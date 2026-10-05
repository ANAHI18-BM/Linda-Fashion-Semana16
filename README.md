# Linda Fashion Boutique · Proyecto final

Aplicación Flask que continúa el Avance 12. Mantiene la portada, imágenes, video y temática de la boutique. La persistencia activa es exclusivamente PostgreSQL.

## Funciones incorporadas

- Registro, login y logout con Flask-Login y hashes de Werkzeug.
- Formularios Flask-WTF con validación y protección CSRF.
- CRUD completo de proveedores, productos, clientes y facturación.
- Relaciones proveedor → productos; cliente → facturas; producto → facturas.
- JOIN en productos (proveedor) y facturación (cliente y prenda).
- Rutas administrativas protegidas, incluida cada operación de escritura.
- Precios y totales decimales; total de factura calculado en el servidor.
- Eliminación mediante POST y confirmación. Las claves foráneas impiden borrar registros utilizados.
- Búsqueda en tablas, panel con conteos y mensajes de contacto guardados.

## 1. Ejecutar en Windows

Necesitas Python y PostgreSQL instalados y el servicio de PostgreSQL encendido.
Extrae el ZIP. Abre una terminal dentro de la carpeta que contiene `app.py`.

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En pgAdmin, crea una base llamada `linda_fashion`: clic derecho en Databases → Create → Database.
Abre `.env` y cambia `TU_CLAVE` por la contraseña de tu usuario PostgreSQL.
Si tu usuario, puerto o nombre de base son distintos, adapta la URL.
Los símbolos especiales de la contraseña deben codificarse para una URL (por ejemplo `@` → `%40`).
Genera una clave para SECRET_KEY:

```powershell
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado a `SECRET_KEY` en `.env`. Después:

```powershell
.venv\Scripts\python.exe -m flask --app app init-db
.venv\Scripts\python.exe app.py
```

Abre http://127.0.0.1:5000. En «Iniciar sesión» → «Crear cuenta», registra tu usuario y una contraseña de mínimo ocho caracteres. No hay una contraseña predefinida.

`init-db` crea las tablas si faltan; no borra ni reinicia los datos al arrancar. Debe ejecutarse antes del primer uso.

## 2. Recuperar los datos del Avance 12

El ZIP conserva las dos bases originales en `respaldo_avance12/`.
`linda_fashion.db` contiene tres prendas, tres clientes, un proveedor y tres facturas.
`ferreterialinda_fashion.db` contiene tres prendas, sin clientes ni facturas.
La aplicación original apuntaba a la segunda. Elige cuál deseas importar.

Para recuperar el conjunto con más registros, después de crear las tablas y ANTES de agregar registros de negocio:

```powershell
.venv\Scripts\python.exe migrar_sqlite.py respaldo_avance12/linda_fashion.db
```

La importación es una transacción: si falla, no queda un conjunto parcial.
Se bloquea cuando la base de destino ya tiene datos de negocio para evitar duplicados.
No modifica los archivos originales. Como SQLite no vinculaba productos con proveedores,
la importación los asigna provisionalmente al primer proveedor; comprueba esa asignación en Productos → Modificar.
Si importas el archivo sin proveedores, crea un proveedor pendiente de confirmar.
Los archivos SQLite son respaldos; no se utilizan para ejecutar el sistema y están excluidos de GitHub.

## 3. Orden de uso y defensa

1. Crear cuenta e iniciar sesión.
2. Agregar un proveedor.
3. Agregar una prenda seleccionando ese proveedor.
4. Agregar un cliente.
5. Agregar una factura seleccionando el cliente y la prenda. Escribir cantidad y precio unitario de venta; el servidor calcula el total.
6. Mostrar los nombres relacionados en Facturación y el proveedor en Productos.
7. Modificar y guardar un registro de cada uno de los cuatro módulos.
8. Intentar eliminar un cliente con factura: el sistema debe explicar por qué está bloqueado.
9. Para demostrar DELETE, borrar primero la factura de prueba, después la prenda, el cliente y el proveedor de prueba.
10. Cerrar sesión e intentar abrir `/productos`: debe redirigir al login.

No uses tus registros originales para demostrar eliminación; crea registros de prueba.
La facturación es un registro académico de ventas, no una factura electrónica autorizada por el SRI.
El formulario de contacto guarda consultas en PostgreSQL; no envía correos.
Revisa los datos de contacto heredados de la portada antes de presentarlos como datos reales.

## 4. Subir a GitHub

El proyecto adjunto identifica este repositorio de origen: https://github.com/ANAHI18-BM/DESAROLLO_WEB. Su estado público actual no se ha comprobado.

Utiliza el repositorio que ya venías trabajando. Sustituye los archivos de la aplicación por esta versión y conserva el historial de Git del repositorio.
No subas `.env`, `.venv`, contraseñas, respaldos privados ni archivos temporales.
Incluye `app.py`, `models.py`, `forms/`, `conexion/`, `sql/`, `templates/`, `static/`, `tests/`, `requirements.txt`, `.env.example`, `.gitignore`, `render.yaml`, `README.md`, `GUIA_DEFENSA.md`, `VERIFICACION.md` y `migrar_sqlite.py`.

Si usas Git desde una copia ya vinculada:

```bash
git add .
git commit -m "Completar PostgreSQL, autenticacion y CRUD del proyecto final"
git push
```

GitHub Pages solo admite la parte estática: no ejecuta este Flask ni el login.
El enlace para comprobar todas las funciones debe ser el servicio web en Render.

## 5. Publicar en Render

Opción guiada: crea primero PostgreSQL desde el panel de Render. Elige conscientemente el plan mostrado antes de crear recursos.
Después crea un Web Service, conecta tu repositorio de GitHub y configura:

| Campo | Valor |
| --- | --- |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python -m flask --app app init-db && gunicorn app:app` |
| DATABASE_URL | Internal Database URL del PostgreSQL de Render |
| SECRET_KEY | Clave aleatoria larga generada por ti |

Usa la misma región para la base y el servicio. Si `app.py` está en una subcarpeta del repositorio, indica esa carpeta en Root Directory.
También se incluye `render.yaml` para la alternativa New → Blueprint; revisa los planes y disponibilidad del panel antes de confirmarlo.
No se garantiza que los planes gratuitos estén disponibles ni que la base dure indefinidamente.

Abre la URL pública que Render te asigne. Crea una cuenta y prueba el flujo completo desde esa URL.
La base de Render es diferente de la local: los datos locales no aparecen automáticamente allí.
Puedes cargar los datos desde los formularios o importar el respaldo desde tu PC usando temporalmente la External Database URL de Render y SSL (`sslmode=require`), en una base de destino vacía.
No publiques ninguna URL que contenga la contraseña de la base.

Documentación oficial: https://render.com/docs/deploy-flask y https://render.com/docs/postgresql-creating-connecting.

## 6. Pruebas automatizadas

Las pruebas necesitan PostgreSQL real y una BASE EXCLUSIVA PARA PRUEBAS.
Vacían sus tablas; nunca configures una base con información que quieras conservar.

```powershell
.venv\Scripts\python.exe -m pip install pytest
$env:TEST_DATABASE_URL = "postgresql://postgres:TU_CLAVE@localhost:5432/linda_fashion_test"
.venv\Scripts\python.exe -m pytest -q
```

Si no se configura TEST_DATABASE_URL, las pruebas se omiten. pytest es una dependencia de desarrollo, no de despliegue.

## Alcance de acceso

Para cumplir la demostración de registro de la Semana 14, una cuenta nueva recibe acceso al panel completo.
Es un sistema académico de administración; antes de usarlo como negocio abierto al público, restringe el registro de administradores y añade roles.
No contiene pasarela de pago, carrito ni facturación tributaria, pues no forman parte de estas actividades.
