# Modalidad Solo mujeres

Aplicación sobre el proyecto extraído: `python3 tool/women-mode/apply.py proyecto`.
Se integra en los builds API, Web y Android, y en la verificación de GitHub.

## Comportamiento

- El registro nuevo pregunta Hombre/Mujer sin preselección. Se conserva la compatibilidad con APK anteriores: si no envían el dato, la cuenta queda sin completar y no accede a Solo mujeres.
- Las cuentas anteriores completan el dato una vez en Mi perfil, mediante una ruta autenticada. No se deduce por nombre, foto ni documentos. Una corrección posterior requiere soporte.
- Una mujer puede publicar/editar un viaje exclusivo para mujeres. Se utiliza `preferences.womenOnly` booleano. Publicar, buscar, reservar y aceptar comprueban la condición en el servidor.
- El filtro de búsqueda muestra viajes exclusivos de conductoras. En la búsqueda normal los viajes exclusivos tampoco se muestran a hombres o cuentas sin completar.
- Cada pasajera solicita un asiento desde su cuenta en los viajes exclusivos. Las reservas normales mantienen su cantidad habitual de asientos.
- Las alertas de búsquedas guardadas conservan y respetan el filtro; no envían coincidencias incompatibles.
- El dato es declarado y no se muestra a otros como si fuera una verificación independiente de identidad.

## Base de datos

Al arrancar la API, TypeORM ejecuta una migración aditiva en su propia tabla `vamos_feature_migrations`: agrega `users.gender` nullable con valores MALE/FEMALE. Las cuentas anteriores conservan sus datos y quedan con gender NULL. No hay borrado ni reclasificación masiva. La cuenta PostgreSQL de la API debe poder agregar la columna y registrar la migración. No se ejecuta SQL durante el build y no se necesita pegar manualmente la migración en Neon con los permisos habituales del propietario.

## Validación

En backend: `npm run build` y `npm test -- --runInBand`.

Comprobación adicional con PostgreSQL embebido (sin conectarse a producción):

```sh
npm install --prefix /tmp/vamos-women-qa @electric-sql/pglite
NODE_PATH=/tmp/vamos-women-qa/node_modules node tool/women-mode/verify.cjs /ruta/absoluta/proyecto
```

Comprueba migración repetible, conservación de cuentas, valores válidos y filtros SQL de búsqueda y alertas para mujeres, hombres y cuentas sin dato. Las pruebas Jest incluyen intentos de publicación, reserva directa y aceptación incompatibles.
