"""Catálogo y carrito; precios y transacciones se validan en PostgreSQL."""
import secrets
import os
from decimal import Decimal
from flask import render_template, request, session, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from conexion.conexion import query, get_connection

def registrar_tienda(app):
    def contenido():
        cesta = session.get('carrito', {})
        ids = [int(k) for k in cesta if k.isdigit()]
        filas = query('SELECT * FROM productos WHERE id = ANY(%s) ORDER BY nombre', (ids,)) if ids else []
        for fila in filas:
            fila['cantidad'] = cesta[str(fila['id'])]
            fila['subtotal'] = fila['precio'] * fila['cantidad']
        return filas

    @app.context_processor
    def contador():
        numero = os.getenv('BOUTIQUE_WHATSAPP', '').strip()
        valido = numero.isdigit() and 8 <= len(numero) <= 15
        return {'carrito_cantidad': sum(session.get('carrito', {}).values()),
                'boutique_direccion': os.getenv('BOUTIQUE_DIRECCION',''),
                'boutique_ruc': os.getenv('BOUTIQUE_RUC',''),
                'boutique_whatsapp': numero if valido else '',
                'boutique_whatsapp_url': 'https://wa.me/' + numero if valido else ''}

    @app.get('/coleccion')
    def catalogo():
        categoria = request.args.get('categoria', '')
        buscar = request.args.get('buscar', '').strip()[:150]
        prendas = query("SELECT p.*, v.nombre AS proveedor FROM productos p JOIN proveedores v ON v.id=p.proveedor_id WHERE (%s='' OR p.categoria=%s) AND p.nombre ILIKE %s ORDER BY p.id DESC", (categoria, categoria, '%' + buscar + '%'))
        categorias = query('SELECT DISTINCT categoria FROM productos ORDER BY categoria')
        return render_template('catalogo.html', prendas=prendas, categorias=categorias, categoria=categoria, buscar=buscar)

    @app.post('/carrito/agregar/<int:id>')
    def agregar_carrito(id):
        fila = query('SELECT id,estado FROM productos WHERE id=%s', (id,), one=True)
        if not fila: abort(404)
        cesta = dict(session.get('carrito', {}))
        if fila['estado'] != 'Disponible':
            flash('Esta prenda no está disponible.', 'warning')
        elif len(cesta) >= 50 and str(id) not in cesta:
            flash('El carrito admite hasta 50 prendas distintas.', 'warning')
        else:
            cesta[str(id)] = min(cesta.get(str(id), 0) + 1, 100)
            session['carrito'] = cesta
            session.pop('venta_token', None)
            flash('Prenda agregada al carrito.', 'success')
        return redirect(url_for('carrito'))

    @app.route('/carrito', methods=['GET', 'POST'])
    def carrito():
        if request.method == 'POST':
            cesta = dict(session.get('carrito', {}))
            id = request.form.get('producto_id', '')
            try: cantidad = int(request.form.get('cantidad', ''))
            except ValueError: cantidad = -1
            if id not in cesta or not 0 <= cantidad <= 100:
                flash('Selecciona una cantidad entre 0 y 100.', 'warning')
            else:
                if cantidad == 0: cesta.pop(id)
                else: cesta[id] = cantidad
                session['carrito'] = cesta
                session.pop('venta_token', None)
            return redirect(url_for('carrito'))
        filas = contenido()
        session.setdefault('venta_token', secrets.token_hex(24))
        clientes = query('SELECT id,nombre FROM clientes ORDER BY nombre') if current_user.is_authenticated else []
        return render_template('carrito.html', filas=filas, total=sum((r['subtotal'] for r in filas), Decimal('0')), clientes=clientes)

    @app.post('/carrito/confirmar')
    @login_required
    def confirmar_venta():
        token = request.form.get('token', '')
        if not token or token != session.get('venta_token'):
            flash('La solicitud venció. Revisa tu carrito.', 'warning')
            return redirect(url_for('carrito'))
        existente = query('SELECT id FROM ventas WHERE token=%s', (token,), one=True)
        if existente: return redirect(url_for('comprobante', id=existente['id']))
        try:
            cliente = int(request.form.get('cliente_id', ''))
        except ValueError:
            flash('Selecciona el cliente de la venta.', 'warning')
            return redirect(url_for('carrito'))
        cesta = session.get('carrito', {})
        if not cesta:
            flash('Agrega prendas antes de registrar una venta.', 'warning')
            return redirect(url_for('carrito'))
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Serializa confirmaciones de una misma sesión para evitar ventas duplicadas.
                cur.execute('SELECT pg_advisory_xact_lock(hashtext(%s))', (token,))
                cur.execute('SELECT id FROM ventas WHERE token=%s', (token,))
                anterior = cur.fetchone()
                if anterior: return redirect(url_for('comprobante', id=anterior['id']))
                cur.execute('SELECT id FROM clientes WHERE id=%s FOR KEY SHARE', (cliente,))
                if not cur.fetchone():
                    flash('El cliente ya no existe.', 'warning')
                    return redirect(url_for('carrito'))
                ids = [int(k) for k in cesta]
                cur.execute('SELECT * FROM productos WHERE id = ANY(%s) ORDER BY id FOR SHARE', (ids,))
                filas = cur.fetchall()
                if len(filas) != len(ids) or any(r['estado'] != 'Disponible' for r in filas):
                    flash('Una prenda ya no está disponible. Revisa tu carrito.', 'warning')
                    return redirect(url_for('carrito'))
                total = sum((r['precio'] * cesta[str(r['id'])] for r in filas), Decimal('0'))
                cur.execute('INSERT INTO ventas(cliente_id,usuario_id,token,total) VALUES(%s,%s,%s,%s) RETURNING id', (cliente, int(current_user.get_id()), token, total))
                venta = cur.fetchone()['id']
                for r in filas:
                    cantidad = cesta[str(r['id'])]
                    cur.execute('INSERT INTO facturacion(cliente_id,producto_id,cantidad,precio_unitario,total,venta_id) VALUES(%s,%s,%s,%s,%s,%s)', (cliente,r['id'],cantidad,r['precio'],r['precio']*cantidad,venta))
        session['carrito'] = {}
        flash('Venta registrada correctamente. No se ha procesado un pago en línea.', 'success')
        return redirect(url_for('comprobante', id=venta))

    @app.get('/ventas')
    @login_required
    def ventas():
        filas = query('SELECT v.*,c.nombre AS cliente FROM ventas v JOIN clientes c ON c.id=v.cliente_id ORDER BY v.id DESC')
        return render_template('ventas.html', filas=filas)

    @app.get('/ventas/<int:id>')
    @login_required
    def comprobante(id):
        venta = query('SELECT v.*,c.nombre,c.correo,c.direccion FROM ventas v JOIN clientes c ON c.id=v.cliente_id WHERE v.id=%s', (id,), one=True)
        if not venta: abort(404)
        detalles = query('SELECT f.*,p.nombre,p.talla FROM facturacion f JOIN productos p ON p.id=f.producto_id WHERE f.venta_id=%s ORDER BY f.id', (id,))
        return render_template('comprobante.html', venta=venta, detalles=detalles)
