"""Importa una sola vez los datos del Avance 12, sin borrar el original."""
import argparse
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from conexion.conexion import get_connection

load_dotenv(Path(__file__).with_name('.env'))
parser = argparse.ArgumentParser()
parser.add_argument('archivo', help='Ruta del .db original que deseas importar')
args = parser.parse_args()
source = Path(args.archivo).resolve()
if not source.is_file():
    raise SystemExit('No existe el archivo SQLite indicado.')
old = sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)
old.row_factory = sqlite3.Row
try:
    with get_connection() as conn:
        with conn.cursor() as cur:
            for table in ['proveedores','productos','clientes','facturacion']:
                cur.execute(f'SELECT COUNT(*) AS n FROM {table}')
                if cur.fetchone()['n']:
                    raise SystemExit('La base de destino ya contiene datos. Importa únicamente en una base vacía para evitar duplicados.')
            suppliers = list(old.execute('SELECT * FROM proveedores'))
            for r in suppliers:
                cur.execute('INSERT INTO proveedores(id,nombre,correo,telefono,producto) VALUES(%s,%s,%s,%s,%s)', tuple(r[k] for k in ['id','nombre','correo','telefono','producto']))
            if suppliers:
                supplier_id = suppliers[0]['id']
            else:
                cur.execute("INSERT INTO proveedores(nombre,correo,telefono,producto) VALUES('Proveedor por confirmar','pendiente@example.com','0000000','Prendas originales') RETURNING id")
                supplier_id = cur.fetchone()['id']
            for table, cols in [('productos',['id','nombre','categoria','descripcion','talla','precio','estado','imagen']),('clientes',['id','nombre','correo','telefono','direccion']),('facturacion',['id','cliente_id','producto_id','cantidad','precio_unitario','total','fecha'])]:
                for row in old.execute('SELECT * FROM '+table):
                    values = [row[k] for k in cols]
                    target = list(cols)
                    if table == 'productos':
                        target.append('proveedor_id'); values.append(supplier_id)
                    if table == 'facturacion':
                        from decimal import Decimal
                        values[4] = Decimal(str(values[4])).quantize(Decimal('.01'))
                        values[5] = values[3] * values[4]
                    cur.execute(f"INSERT INTO {table} ("+','.join(target)+') VALUES ('+','.join(['%s']*len(values))+')',values)
            for table in ['proveedores','productos','clientes','facturacion']:
                cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}','id'), COALESCE(MAX(id),1), MAX(id) IS NOT NULL) FROM {table}")
    print('Importación completada. Confirma el proveedor real de cada prenda en Productos → Modificar.')
finally:
    old.close()
