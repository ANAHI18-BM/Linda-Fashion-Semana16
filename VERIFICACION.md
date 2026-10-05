# Verificación del proyecto · 30 de septiembre de 2026

Se realizaron pruebas con Flask y PostgreSQL real 16.15 en una base temporal exclusiva. Resultado: **3 pruebas de integración aprobadas**.

| Requisito | Resultado comprobado |
| --- | --- |
| Semana 13: conexión relacional | PostgreSQL con psycopg2 y conexión centralizada |
| Tablas, PK y FK | Proveedores → Productos; Clientes y Productos → Facturación |
| Semana 14: registro | Cuenta almacenada; contraseña con hash comprobado |
| Login | Credenciales correctas aceptadas e incorrectas rechazadas |
| Duplicados | Nombre de usuario repetido rechazado, incluso cambiando mayúsculas |
| Rutas privadas | Listas, panel, formularios y mensajes redirigen al login sin sesión |
| Semana 15: CRUD | Crear, listar, modificar y eliminar en los cuatro módulos |
| JOIN | Lista de productos con proveedor; facturas con cliente y prenda |
| Validaciones | Contraseña corta y correo inválido no se guardan |
| Protección CSRF | POST sin token rechazado, incluido logout |
| Integridad relacional | No se elimina una prenda utilizada en una factura |
| Cálculo | Dos unidades a $30.50 dan $61.00; al modificar a tres, $91.50 |
| Cierre de sesión | Logout finaliza sesión y vuelve a proteger Productos |
| Contacto | Consulta guardada y visible en mensajes administrativos |
| Registro inexistente | Formulario de edición devuelve 404 |
| Redirecciones | El login no redirige a un dominio externo enviado en next |

También se verificó la migración del respaldo `linda_fashion.db`: tres productos, tres clientes, un proveedor y tres facturas importados; una segunda importación se bloquea para evitar duplicados. La portada respondió HTTP 200 y todas las plantillas Jinja se compilaron.

## Comprobaciones pendientes en el equipo y en Render

Estas pruebas se hicieron mediante el cliente de pruebas de Flask contra PostgreSQL real. No sustituyen la revisión visual en un navegador, la conexión a tu PostgreSQL local ni la prueba desde la URL pública de Render.

- Configurar `.env`, crear la base local e iniciar la aplicación.
- Revisar la portada, video y formularios en escritorio y celular.
- Confirmar que los proveedores asignados al importar sean correctos.
- Subir el código al repositorio real de GitHub.
- Configurar el servicio y PostgreSQL de Render.
- Desde la URL pública: Login → Listar → Agregar → Modificar → Eliminar → consultar relaciones → Cerrar sesión.
- Preparar datos de prueba para la defensa de Semana 16 y entregar los enlaces que solicita el docente.

El paquete incluye configuración de despliegue; **todavía no está publicado en GitHub ni Render** y no se han inventado enlaces públicos.
