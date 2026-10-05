"""TEST_DATABASE_URL debe apuntar a una base exclusiva de pruebas: se vacían sus tablas."""
import os, re, sys
from pathlib import Path
import pytest
if not os.getenv('TEST_DATABASE_URL'):
    pytest.skip('Configura TEST_DATABASE_URL (base exclusiva de pruebas)',allow_module_level=True)
os.environ['DATABASE_URL']=os.environ['TEST_DATABASE_URL']
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import app
from conexion.conexion import query
from werkzeug.security import check_password_hash

@pytest.fixture
def c():
    app.config['TESTING']=True
    assert app.test_cli_runner().invoke(args=['init-db']).exit_code==0
    query('TRUNCATE usuarios, facturacion, productos, proveedores, clientes, mensajes RESTART IDENTITY CASCADE')
    return app.test_client()

def post(c,page,data,target=None):
    text=c.get(page).get_data(as_text=True)
    token=re.search(r'name="csrf_token"[^>]*value="([^"]+)"',text)
    assert token, page
    return c.post(target or page,data={**data,'csrf_token':token[1]},follow_redirects=True)

def login(c):
    post(c,'/registro',dict(usuario='bella',password='Prueba123!',confirmacion='Prueba123!'))
    row=query('SELECT * FROM usuarios',one=True)
    assert row['password']!='Prueba123!' and check_password_hash(row['password'],'Prueba123!')
    assert 'incorrectos' in post(c,'/login',dict(usuario='bella',password='incorrecta')).get_data(as_text=True)
    assert c.get('/productos').status_code==302
    assert post(c,'/login',dict(usuario='bella',password='Prueba123!')).status_code==200

def test_crud_relaciones_logout(c):
    for page in ['/productos','/clientes','/proveedores','/facturacion','/dashboard','/mensajes','/productos/nuevo','/productos/1/editar']:
        assert c.get(page).status_code==302
    login(c)
    datos={
     'proveedores':dict(nombre='Moda Test',correo='moda@example.com',telefono='0991234567',producto='Vestidos'),
     'clientes':dict(nombre='Cliente Test',correo='cliente@example.com',telefono='0991234567',direccion='Shushufindi Centro'),
     'productos':dict(nombre='Vestido Test',categoria='Vestidos',descripcion='Vestido de prueba completo',talla='M',precio='30.50',estado='Disponible',proveedor_id=1),
     'facturacion':dict(cliente_id=1,producto_id=1,cantidad=2,precio_unitario='30.50')}
    for modulo,data in datos.items():
        ruta='/'+modulo+('/nueva' if modulo=='facturacion' else '/nuevo')
        assert post(c,ruta,data).status_code==200
        assert query(f'SELECT COUNT(*) AS n FROM {modulo}',one=True)['n']==1
    assert query('SELECT total FROM facturacion',one=True)['total']==61
    t=c.get('/facturacion').get_data(as_text=True)
    assert 'Cliente Test' in t and 'Vestido Test' in t
    assert 'Moda Test' in c.get('/productos').get_data(as_text=True)
    for modulo,data in datos.items():
        changed={**data,'cantidad':3} if modulo=='facturacion' else {**data,'nombre':'Registro Editado'}
        assert post(c,f'/{modulo}/1/editar',changed).status_code==200
        row=query(f'SELECT * FROM {modulo}',one=True)
        assert row['cantidad']==3 if modulo=='facturacion' else row['nombre']=='Registro Editado'
    assert query('SELECT total FROM facturacion',one=True)['total']==pytest.approx(91.5)
    assert 'relacionado' in post(c,'/productos',{},'/productos/1/eliminar').get_data(as_text=True)
    assert query('SELECT COUNT(*) AS n FROM productos',one=True)['n']==1
    for modulo in ['facturacion','productos','clientes','proveedores']:
        assert post(c,'/'+modulo,{},f'/{modulo}/1/eliminar').status_code==200
        assert query(f'SELECT COUNT(*) AS n FROM {modulo}',one=True)['n']==0
    assert c.post('/logout').status_code==400
    assert post(c,'/dashboard',{},'/logout').status_code==200
    assert c.get('/productos').status_code==302

def test_validaciones_contacto(c):
    assert c.post('/registro',data={'usuario':'bella'}).status_code==400
    post(c,'/registro',dict(usuario='bella',password='corta',confirmacion='corta'))
    assert query('SELECT COUNT(*) AS n FROM usuarios',one=True)['n']==0
    login(c)
    post(c,'/clientes/nuevo',dict(nombre='Cliente Test',correo='invalido',telefono='0991234567',direccion='Dirección Test'))
    assert query('SELECT COUNT(*) AS n FROM clientes',one=True)['n']==0
    post(c,'/',dict(nombre='Bella Test',correo='bella@example.com',mensaje='Consulta sobre el catálogo.'))
    assert query('SELECT COUNT(*) AS n FROM mensajes',one=True)['n']==1
    assert 'Consulta sobre' in c.get('/mensajes').get_data(as_text=True)
    assert c.get('/clientes/999/editar').status_code==404
    assert c.get('/logout').status_code==405

def test_duplicados_redirect(c):
    login(c)
    post(c,'/dashboard',{},'/logout')
    assert 'ya está registrado' in post(c,'/registro',dict(usuario='BELLA',password='Prueba123!',confirmacion='Prueba123!')).get_data(as_text=True)
    r=post(c,'/login?next=https://example.com',dict(usuario='bella',password='Prueba123!'))
    assert r.request.path=='/dashboard'
