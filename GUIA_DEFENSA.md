# Guion para la defensa · Linda Fashion Boutique

Buenos días, ingeniero y compañeros. Soy Bella Anahí Morocho Vite y voy a presentar mi proyecto Linda Fashion Boutique, una aplicación web para gestionar prendas, proveedores, clientes y ventas de una boutique. Continué trabajando sobre la página de las semanas anteriores y mantuve su portada, imágenes y video. En esta etapa integré PostgreSQL, autenticación y las operaciones de crear, consultar, modificar y eliminar.

Primero muestro la página principal y su colección. Los productos disponibles se consultan desde la base de datos. El formulario de contacto también permite registrar una consulta, que luego se puede revisar en el panel.

Ahora ingreso al sistema. Se puede registrar un usuario nuevo y su contraseña se guarda mediante un hash, por lo que no queda almacenada como texto visible. El inicio de sesión valida las credenciales y Flask-Login mantiene la sesión. Las rutas de administración requieren autenticación.

En el panel podemos acceder a proveedores, productos, clientes y facturación. Voy a crear un proveedor de prueba y una prenda relacionada con ese proveedor. Después registraré un cliente y una venta, seleccionando ese cliente y esa prenda. La aplicación calcula el total multiplicando la cantidad por el precio unitario.

Las tablas tienen una clave primaria que identifica cada registro y claves foráneas que conectan la información. Un proveedor puede tener varias prendas, y una factura está relacionada con un cliente y un producto. En Facturación utilizo una consulta JOIN para mostrar sus nombres en lugar de mostrar únicamente sus identificadores.

Voy a modificar un registro en cada módulo para demostrar la actualización. Después eliminaré los datos de prueba. Si intento eliminar una prenda que aparece en una factura, el sistema lo impide para conservar la relación. Primero debo revisar o eliminar la factura de prueba y luego borrar la prenda. Esto demuestra que las relaciones se utilizan realmente.

Los formularios validan los datos antes de guardarlos y las consultas SQL utilizan parámetros. También hay protección CSRF para los envíos. Finalmente cierro sesión y escribo directamente la dirección de una página administrativa; el sistema me devuelve al login porque ya no estoy autenticada.

[Cuando el despliegue esté terminado: mostrar la URL pública de Render, repetir el flujo desde esa aplicación y abrir el repositorio GitHub. No afirmar que está publicado antes de verificarlo.]

## Preguntas que podría hacer el docente

**¿Dónde se guardan los datos?** En PostgreSQL. SQLite se conserva únicamente como respaldo del avance anterior.

**¿Qué significa CRUD?** Crear un registro, consultar lo guardado, actualizarlo y eliminarlo. Se implementa con INSERT, SELECT, UPDATE y DELETE.

**¿Cuáles son las tablas relacionadas?** Proveedores con productos; clientes y productos con facturación. Usuarios almacena las cuentas, y mensajes guarda las consultas.

**¿Por qué no deja eliminar algunos registros?** Porque todavía están referenciados por otra tabla. Las claves foráneas protegen esas relaciones.

**¿Para qué sirve login_required?** Para impedir que una persona sin sesión entre al panel o ejecute operaciones administrativas escribiendo la URL.

**¿Qué diferencia hay entre GitHub y Render?** GitHub almacena el código del proyecto. Render ejecuta la aplicación Flask y permite acceder a ella mediante un enlace público.

**¿Cómo comprobaste que funcionaba?** Se realizaron pruebas con PostgreSQL real para registrar usuarios, rechazar una contraseña incorrecta, proteger rutas, ejecutar CRUD en los cuatro módulos, consultar relaciones y cerrar sesión. La comprobación en Render se hace después de publicar.
