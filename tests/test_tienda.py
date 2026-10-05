"""Pruebas del carrito con una conexión simulada; no requieren vaciar una base real."""
import sys
from pathlib import Path
from decimal import Decimal
from contextlib import contextmanager
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import app as principal
import tienda

@pytest.fixture
def cliente(monkeypatch):
    principal.app.config.update(TESTING=True,WTF_CSRF_ENABLED=False)
    monkeypatch.setattr(principal,'query',lambda *a,**kw: {'id':1,'usuario':'bella'} if 'FROM usuarios' in a[0] else [])
    return principal.app.test_client()

def producto():
    return dict(id=4,nombre='Vestido',categoria='Vestidos',descripcion='Vestido largo',talla='M',precio=Decimal('110.50'),estado='Disponible',imagen='',proveedor='Proveedor')

def test_carrito_cantidad_y_precio_servidor(cliente,monkeypatch):
    monkeypatch.setattr(tienda,'query',lambda *a,**k: producto() if k.get('one') else [producto()])
    assert cliente.post('/carrito/agregar/4').status_code==302
    assert cliente.post('/carrito',data={'producto_id':'4','cantidad':'2','precio':'0.01'}).status_code==302
    texto=cliente.get('/carrito').get_data(as_text=True)
    assert '221.00' in texto
    cliente.post('/carrito',data={'producto_id':'4','cantidad':'-1'})
    with cliente.session_transaction() as ses: assert ses['carrito']=={'4':2}
    cliente.post('/carrito',data={'producto_id':'4','cantidad':'0'})
    with cliente.session_transaction() as ses: assert ses['carrito']=={}

def test_agotado_y_rutas_protegidas(cliente,monkeypatch):
    monkeypatch.setattr(tienda,'query',lambda *a,**k:{**producto(),'estado':'Agotado'})
    cliente.post('/carrito/agregar/4')
    with cliente.session_transaction() as ses: assert not ses.get('carrito')
    for ruta in ['/ventas','/ventas/1']: assert cliente.get(ruta).status_code==302
    assert cliente.post('/carrito/confirmar').status_code==302

def test_venta_guarda_total_y_detalle(cliente,monkeypatch):
    llamadas=[]
    class Cursor:
        def execute(self,sql,params=()): self.sql=sql; llamadas.append((sql,params))
        def fetchone(self):
            if 'FROM ventas' in self.sql: return None
            if 'FROM clientes' in self.sql: return {'id':1}
            return {'id':8}
        def fetchall(self): return [producto()]
        def __enter__(self): return self
        def __exit__(self,*a): pass
    class Conexion:
        def cursor(self): return Cursor()
    @contextmanager
    def conexion(): yield Conexion()
    monkeypatch.setattr(tienda,'get_connection',conexion)
    monkeypatch.setattr(tienda,'query',lambda *a,**k:None)
    with cliente.session_transaction() as ses:
        ses['_user_id']='1';ses['_fresh']=True;ses['carrito']={'4':2};ses['venta_token']='abc'
    r=cliente.post('/carrito/confirmar',data={'token':'abc','cliente_id':'1','total':'0.01'})
    assert r.status_code==302 and r.location.endswith('/ventas/8')
    inserciones=[p for sql,p in llamadas if sql.startswith('INSERT')]
    assert inserciones[0][-1]==Decimal('221.00')
    assert inserciones[1]==(1,4,2,Decimal('110.50'),Decimal('221.00'),8)
    with cliente.session_transaction() as ses: assert ses['carrito']=={}

def test_plantillas_compilan(cliente):
    for nombre in principal.app.jinja_env.list_templates(): principal.app.jinja_env.get_template(nombre)

def test_csrf_carrito(cliente):
    principal.app.config['WTF_CSRF_ENABLED']=True
    try: assert cliente.post('/carrito/agregar/4').status_code==400
    finally: principal.app.config['WTF_CSRF_ENABLED']=False

def test_subir_fotografia_valida_e_invalida(cliente,monkeypatch):
    from io import BytesIO
    from PIL import Image
    escritos=[]
    def consultas(sql,params=(),one=False):
        if 'FROM usuarios' in sql: return {'id':1,'usuario':'bella'}
        if 'FROM proveedores' in sql: return [{'id':1,'nombre':'Proveedor'}]
        if sql.startswith('INSERT INTO productos'): escritos.append(params);return 1
        return []
    monkeypatch.setattr(principal,'query',consultas)
    with cliente.session_transaction() as ses: ses['_user_id']='1';ses['_fresh']=True
    datos=dict(nombre='Vestido Test',categoria='Vestidos',descripcion='Vestido largo de prueba',talla='M',precio='25.00',estado='Disponible',proveedor_id='1',imagen='')
    r=cliente.post('/productos/nuevo',data={**datos,'foto':(BytesIO(b'no es imagen'),'foto.jpg')})
    assert r.status_code==200 and b'Usa una fotograf' in r.data and not escritos
    raw=BytesIO();Image.new('RGB',(20,20),'pink').save(raw,format='PNG');raw.seek(0)
    r=cliente.post('/productos/nuevo',data={**datos,'foto':(raw,'foto.png')})
    assert r.status_code==302
    ruta=principal.BASE_DIR/'static/img'/escritos[0][-1]
    try:
        with Image.open(ruta) as foto: assert foto.format=='JPEG'
    finally: ruta.unlink(missing_ok=True)

def test_whatsapp_configurable(cliente,monkeypatch):
    monkeypatch.setenv('BOUTIQUE_WHATSAPP','593991234567')
    with principal.app.test_request_context():
        datos=principal.app.template_context_processors[None][-1]()
        assert datos['boutique_whatsapp_url']=='https://wa.me/593991234567'
