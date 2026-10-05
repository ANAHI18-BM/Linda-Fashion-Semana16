import os
import secrets
from pathlib import Path
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from types import SimpleNamespace
from urllib.parse import urlsplit
from decimal import Decimal
import click
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from conexion.conexion import query, get_connection
from models import Usuario
from forms import ProductoForm, ClienteForm, ProveedorForm, FacturacionForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm
from forms.contacto_form import ContactoForm

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
app = Flask(__name__)
secret = os.getenv('SECRET_KEY')
if os.getenv('RENDER') and not secret:
    raise RuntimeError('Configure SECRET_KEY en Render.')
app.config.update(SECRET_KEY=secret or secrets.token_hex(32), SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=bool(os.getenv('RENDER')))
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Inicia sesión para acceder a la administración.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    if not user_id.isdigit():
        return None
    row = query('SELECT id, usuario FROM usuarios WHERE id=%s', (int(user_id),), one=True)
    return Usuario(row) if row else None

@app.cli.command('init-db')
def init_db():
    """Crea las tablas sin borrar los datos existentes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute((BASE_DIR / 'sql/esquema.sql').read_text())
    click.echo('Tablas de PostgreSQL listas. No se borraron registros.')

@app.route('/', methods=['GET', 'POST'])
def index():
    contacto = ContactoForm()
    if contacto.validate_on_submit():
        query('INSERT INTO mensajes(nombre,correo,mensaje) VALUES(%s,%s,%s)',
              (contacto.nombre.data.strip(), contacto.correo.data.strip(), contacto.mensaje.data.strip()))
        flash('Tu mensaje se guardó correctamente. Gracias por contactarnos.', 'success')
        return redirect(url_for('index', _anchor='contacto'))
    prendas = query("SELECT * FROM productos WHERE estado='Disponible' ORDER BY id DESC LIMIT 3")
    return render_template('index.html', productos=prendas, contacto=contacto)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = UsuarioForm()
    if form.validate_on_submit():
        try:
            # El proyecto académico permite crear cuentas administrativas para demostrar el registro.
            query('INSERT INTO usuarios(usuario,password) VALUES(%s,%s)',
                  (form.usuario.data.strip().lower(), generate_password_hash(form.password.data)))
        except psycopg2.errors.UniqueViolation:
            form.usuario.errors.append('Ese usuario ya está registrado.')
        else:
            flash('Cuenta creada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    return render_template('formulario.html', form=form, titulo='Crear cuenta', volver='login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        row = query('SELECT * FROM usuarios WHERE usuario=%s', (form.usuario.data.strip().lower(),), one=True)
        if row and check_password_hash(row['password'], form.password.data):
            login_user(Usuario(row))
            dest = request.args.get('next', '')
            parts = urlsplit(dest)
            if not dest.startswith('/') or dest.startswith('//') or parts.netloc or parts.scheme or '\\' in dest:
                dest = url_for('dashboard')
            return redirect(dest)
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('formulario.html', form=form, titulo='Iniciar sesión', volver='index')

@app.post('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))

# Únicamente estos nombres internos se interpolan en SQL. Los datos del usuario usan %s.
MODULOS = {
 'productos': (ProductoForm, ['nombre','categoria','descripcion','talla','precio','estado','proveedor_id','imagen']),
 'clientes': (ClienteForm, ['nombre','correo','telefono','direccion']),
 'proveedores': (ProveedorForm, ['nombre','correo','telefono','producto']),
 'facturacion': (FacturacionForm, ['cliente_id','producto_id','cantidad','precio_unitario']),
}
LISTAS = {
 'productos': 'SELECT p.*, v.nombre AS proveedor FROM productos p JOIN proveedores v ON v.id=p.proveedor_id ORDER BY p.id DESC',
 'clientes': 'SELECT * FROM clientes ORDER BY id DESC',
 'proveedores': 'SELECT * FROM proveedores ORDER BY id DESC',
 'facturacion': 'SELECT f.*, c.nombre AS cliente, p.nombre AS producto FROM facturacion f JOIN clientes c ON c.id=f.cliente_id JOIN productos p ON p.id=f.producto_id ORDER BY f.id DESC',
}
COLUMNAS = {
 'productos': [('id','ID'),('nombre','Prenda'),('categoria','Categoría'),('talla','Talla'),('precio','Precio ($)'),('estado','Estado'),('proveedor','Proveedor')],
 'clientes': [('id','ID'),('nombre','Nombre'),('correo','Correo'),('telefono','Teléfono'),('direccion','Dirección')],
 'proveedores': [('id','ID'),('nombre','Nombre'),('correo','Correo'),('telefono','Teléfono'),('producto','Suministro')],
 'facturacion': [('id','ID'),('cliente','Cliente'),('producto','Prenda'),('cantidad','Cantidad'),('precio_unitario','Precio ($)'),('total','Total ($)'),('fecha','Fecha')],
}

def listar(modulo):
    return render_template('lista.html', modulo=modulo, registros=query(LISTAS[modulo]), columnas=COLUMNAS[modulo])

def editar(modulo, id=None):
    row = query(f'SELECT * FROM {modulo} WHERE id=%s', (id,), one=True) if id else None
    if id and not row:
        abort(404)
    if modulo == 'facturacion' and row and row.get('venta_id'):
        flash('Este detalle pertenece a una venta. Consulta su comprobante desde Ventas.', 'warning')
        return redirect(url_for('ventas'))
    cls, campos = MODULOS[modulo]
    form = cls(obj=SimpleNamespace(**row) if row else None)
    if modulo == 'productos':
        form.imagen.choices = [('', 'Sin fotografía')] + [(x.name, x.name) for x in sorted((BASE_DIR / 'static/img').iterdir()) if x.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.avif'}]
        form.proveedor_id.choices = [(r['id'], r['nombre']) for r in query('SELECT id,nombre FROM proveedores ORDER BY nombre')]
    if modulo == 'facturacion':
        form.cliente_id.choices = [(r['id'], r['nombre']) for r in query('SELECT id,nombre FROM clientes ORDER BY nombre')]
        form.producto_id.choices = [(r['id'], r['nombre']) for r in query('SELECT id,nombre FROM productos ORDER BY nombre')]
    if form.validate_on_submit():
        if modulo == 'productos' and form.foto.data:
            try:
                raw = form.foto.data.read(5 * 1024 * 1024 + 1)
                if len(raw) > 5 * 1024 * 1024:
                    raise ValueError('La fotografía debe pesar menos de 5 MB.')
                with Image.open(BytesIO(raw)) as foto:
                    if foto.width * foto.height > 20000000:
                        raise ValueError('La fotografía es demasiado grande.')
                    foto.load()
                    foto.thumbnail((1600,1600))
                    nombre = 'prenda_' + secrets.token_hex(12) + '.jpg'
                    foto.convert('RGB').save(BASE_DIR / 'static/img' / nombre, quality=90)
                form.imagen.data = nombre
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
                form.foto.errors.append('Usa una fotografía JPG, PNG o WebP válida de hasta 5 MB.')
                return render_template('formulario.html', form=form, titulo=('Modificar ' if id else 'Registrar ') + modulo, volver=modulo)
        valores = [getattr(form,c).data.strip() if isinstance(getattr(form,c).data,str) else getattr(form,c).data for c in campos]
        columnas = list(campos)
        if modulo == 'facturacion':
            columnas.append('total')
            valores.append(form.cantidad.data * form.precio_unitario.data)
        try:
            if id:
                query(f"UPDATE {modulo} SET " + ','.join(c+'=%s' for c in columnas) + ' WHERE id=%s', tuple(valores+[id]))
            else:
                query(f"INSERT INTO {modulo} (" + ','.join(columnas) + ') VALUES (' + ','.join(['%s']*len(columnas)) + ')', tuple(valores))
        except psycopg2.errors.ForeignKeyViolation:
            flash('La relación seleccionada ya no existe. Actualiza el formulario.', 'danger')
        else:
            flash('Registro actualizado.' if id else 'Registro creado.', 'success')
            return redirect(url_for(modulo))
    return render_template('formulario.html', form=form, titulo=('Modificar ' if id else 'Registrar ') + modulo, volver=modulo)

def eliminar(modulo, id):
    if modulo == 'facturacion':
        row = query('SELECT venta_id FROM facturacion WHERE id=%s', (id,), one=True)
        if row and row.get('venta_id'):
            flash('El detalle pertenece a una venta y debe conservarse con su comprobante.', 'warning')
            return redirect(url_for('ventas'))
    try:
        n = query(f'DELETE FROM {modulo} WHERE id=%s', (id,))
    except psycopg2.errors.ForeignKeyViolation:
        flash('No puedes eliminar este registro porque está relacionado con productos o facturas. Revisa primero esos registros.', 'warning')
    else:
        if not n: abort(404)
        flash('Registro eliminado correctamente.', 'success')
    return redirect(url_for(modulo))

# Registra rutas explícitas para los cuatro módulos; cada operación requiere autenticación.
for modulo in MODULOS:
    app.add_url_rule('/'+modulo, endpoint=modulo, view_func=login_required(lambda m=modulo: listar(m)))
    nuevo = {'productos':'formulario_producto','clientes':'formulario_cliente','proveedores':'formulario_proveedor','facturacion':'formulario_facturacion'}[modulo]
    sufijo = '/nueva' if modulo == 'facturacion' else '/nuevo'
    app.add_url_rule('/'+modulo+sufijo, endpoint=nuevo, view_func=login_required(lambda m=modulo: editar(m)), methods=['GET','POST'])
    app.add_url_rule('/'+modulo+'/<int:id>/editar', endpoint='editar_'+modulo, view_func=login_required(lambda id,m=modulo: editar(m,id)), methods=['GET','POST'])
    app.add_url_rule('/'+modulo+'/<int:id>/eliminar', endpoint='eliminar_'+modulo, view_func=login_required(lambda id,m=modulo: eliminar(m,id)), methods=['POST'])

@app.get('/dashboard')
@login_required
def dashboard():
    conteos = {m:query(f'SELECT COUNT(*) AS n FROM {m}', one=True)['n'] for m in MODULOS}
    return render_template('dashboard.html', conteos=conteos)

@app.get('/mensajes')
@login_required
def mensajes():
    return render_template('mensajes.html', registros=query('SELECT * FROM mensajes ORDER BY id DESC'))

@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template('error.html', titulo='Formulario vencido', mensaje='Vuelve a abrir el formulario e inténtalo de nuevo.'), 400

@app.errorhandler(413)
def archivo_grande(error):
    return render_template('error.html', titulo='Archivo demasiado grande', mensaje='Selecciona una fotografía de hasta 5 MB.'), 413

@app.errorhandler(404)
def no_encontrado(error):
    return render_template('error.html', titulo='Página no encontrada', mensaje='El registro o la página solicitada no existe.'), 404

@app.errorhandler(psycopg2.OperationalError)
def conexion_error(error):
    app.logger.error('No se pudo conectar a PostgreSQL.')
    return render_template('error.html', titulo='Base de datos no disponible', mensaje='Revisa la conexión a PostgreSQL y la configuración de DATABASE_URL.'), 503

@app.after_request
def headers(response):
    if current_user.is_authenticated:
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

from tienda import registrar_tienda
registrar_tienda(app)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
