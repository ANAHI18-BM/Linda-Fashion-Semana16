"""Añade catálogo documentado sin borrar ni sobrescribir registros existentes."""
import json
from pathlib import Path
from dotenv import load_dotenv
from conexion.conexion import get_connection

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

def importar():
    datos = json.loads((ROOT / 'catalogo_real.json').read_text(encoding='utf-8'))
    for p in datos:
        if not (ROOT / 'static' / 'img' / p['imagen']).is_file():
            raise RuntimeError('Falta la fotografía: ' + p['imagen'])
    agregados = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_xact_lock(%s)', (1571604,))
            cur.execute("ALTER TABLE productos ADD COLUMN IF NOT EXISTS fuente_url TEXT NOT NULL DEFAULT ''")
            cur.execute('SELECT id FROM proveedores WHERE LOWER(correo)=LOWER(%s) ORDER BY id LIMIT 1', ('ropalissey@gmail.com',))
            proveedor = cur.fetchone()
            if proveedor:
                proveedor_id = proveedor['id']
            else:
                cur.execute('INSERT INTO proveedores(nombre,correo,telefono,producto) VALUES (%s,%s,%s,%s) RETURNING id', ('Ropa Lissey','ropalissey@gmail.com','+593990506409','Ropa femenina al por mayor y menor'))
                proveedor_id = cur.fetchone()['id']
            for p in datos:
                cur.execute('SELECT id FROM productos WHERE fuente_url=%s OR (nombre=%s AND proveedor_id=%s) LIMIT 1', (p['fuente_url'],p['nombre'],proveedor_id))
                if cur.fetchone():
                    continue
                cur.execute('INSERT INTO productos(nombre,categoria,descripcion,talla,precio,estado,imagen,proveedor_id,fuente_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', (p['nombre'],p['categoria'],p['descripcion'],p['talla'],p['precio'],'Disponible',p['imagen'],proveedor_id,p['fuente_url']))
                agregados += 1
    print(f'Catálogo listo: {agregados} prendas nuevas. No se borraron registros.')

if __name__ == '__main__':
    importar()
