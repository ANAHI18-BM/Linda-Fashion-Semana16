# Actualización de la colección y el carrito

1. Detén Flask con Ctrl+C. Conserva tu carpeta actual como respaldo.
2. Copia los archivos de esta versión sobre tu proyecto. Conserva tu archivo `.env` y tu entorno `.venv`; el ZIP no contiene credenciales.
3. En la terminal del proyecto ejecuta:

```powershell
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe app.py
```

No ejecutes de nuevo el importador de SQLite. La actualización agrega la tabla ventas y una relación en facturación, sin borrar tus registros.

## Fotografías

Guarda las fotos reales en `static/img` con nombres sencillos, por ejemplo `vestido_brown.jpg`. En Productos → Modificar, selecciona la foto de esa prenda y guarda. Si no tienes su fotografía, elige “Sin fotografía”. No asignes una foto de otra prenda. Para Render, incorpora las imágenes a GitHub junto con el código.

Los productos anteriores conservan su imagen. La actualización no inventa fotografías ni cambia automáticamente tus datos. Puedes añadir tantas imágenes propias como necesites y seleccionarlas en cada producto.

## Prueba de la tienda

Colección → buscar o filtrar categoría → agregar dos prendas al carrito → cambiar cantidades → quitar una prenda con cantidad 0 → iniciar sesión → seleccionar un cliente existente → confirmar venta → revisar detalle → imprimir o guardar PDF → revisar Ventas y Facturación.

Los precios se consultan nuevamente al confirmar. Si un producto se elimina o deja de estar disponible, la venta no se registra. Cada venta y todos sus detalles se guardan juntos. Una confirmación repetida no genera otra venta.

## Alcance

El carrito funciona y guarda ventas en PostgreSQL. El comprobante es un registro interno, no una factura electrónica del SRI. No procesa tarjetas, no confirma pagos, no calcula impuestos y no lleva cantidades de inventario. “Disponible” es el estado registrado por el administrador. La confirmación de ventas está reservada al personal que inicia sesión; no se ha añadido una cuenta de comprador independiente.

El CRUD original de proveedores, productos, clientes y facturación individual se conserva. Los detalles de una venta del carrito no se editan ni se eliminan por separado, para mantener consistente el total del comprobante. Las ventas pueden consultarse e imprimirse.

## Requisitos académicos

Se mantienen Flask, PostgreSQL, login, rutas administrativas protegidas, formularios, SQL parametrizado, claves foráneas y JOIN. Las instrucciones de semanas 13 y 14 deben contrastarse cuando estén disponibles. GitHub y Render siguen requiriendo publicación y prueba en el entorno de la estudiante.

## Verificación de esta actualización

`python -m pytest tests/test_tienda.py`: pruebas de carrito, cantidades, precios calculados en servidor, detalle de venta, CSRF, autenticación y compilación de plantillas con conexión simulada. Para probar con PostgreSQL real, usar una base exclusiva de pruebas según `tests/test_integracion.py`. Esas pruebas eliminan los datos de la base de pruebas: nunca usar la base de trabajo.

## Ícono, fotos nuevas y WhatsApp

El carrito tiene ahora un botón flotante en la esquina inferior derecha. En Productos → Modificar puedes subir la foto real de cada prenda desde tu computadora. La foto nueva reemplaza la selección anterior de ese producto; no altera los demás. Usa JPG, PNG o WebP de hasta 5 MB.

Antes de iniciar esta versión, instala nuevamente requirements.txt para añadir Pillow. Conserva `.env`, `.venv` y las fotografías que añadiste a `static/img`. Para publicar en Render, guarda las fotografías locales en GitHub; las subidas realizadas directamente en un servicio sin almacenamiento persistente pueden perderse al desplegar otra vez.

Añade a tu `.env` BOUTIQUE_WHATSAPP con tu número real (por ejemplo, formato 593 seguido del número sin cero inicial), BOUTIQUE_DIRECCION y, si tienes, BOUTIQUE_RUC. No inventes un RUC. Reinicia Flask. El comprobante mostrará esos datos y el botón de WhatsApp cuando configures un número válido. El botón abre una consulta y no envía mensajes automáticamente.

Esta actualización no trae nuevas fotografías comerciales sin verificar: debes subir las fotos de las prendas de tu catálogo. Sigue siendo un comprobante de venta interno, sin integración fiscal ni pasarela de pago.
