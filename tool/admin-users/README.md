# Administración: identidad y actividad de usuarios

Se aplica sobre el ZIP extraído con `python3 tool/admin-users/apply.py proyecto`.
El build de la API en Render lo aplica después de preparar la revisión Sofía y el cierre del chat.
No requiere migraciones ni cambios en Flutter.

- Usuarios: hasta 100 cuentas recientes, fecha de creación en America/La_Paz, viajes finalizados como conductor y pasajero, y cancelaciones propias por rol.
- Viajes del conductor: hasta 200 viajes recientes, reservas aceptadas/completadas, cuentas con encuentro verificado y suma de sus asientos. Verificar una reserva de dos asientos confirma una cuenta; no demuestra la identidad de sus acompañantes.
- Cancelaciones del conductor: viajes cuyo estado es CANCELLED. Cancelaciones del pasajero: eventos BOOKING_CANCELLED, que se conservan aunque vuelva a solicitar la misma reserva. Se incluyen reservas canceladas con motivo propio sin evento conservado como respaldo. Una cancelación del viaje por el conductor genera TRIP_CANCELLED y no se carga al pasajero. Los datos históricos eliminados o nunca registrados no pueden reconstruirse; no se cuentan ausencias ni rechazos como cancelaciones.
- Edición de nombres/apellidos: solo administradores activos; validación de 2 a 80 caracteres tras quitar espacios externos. Cambio y auditoría son atómicos; se conserva el antes y después. No se modifica la fecha de registro.
- La vista temporal de Sofía se genera antes y conserva sus datos ficticios y solo consulta.

Validación: `npm run build` y `npm test -- --runInBand` en backend.
Para comprobar SQL PostgreSQL y la interfaz con datos ficticios, sin tocar producción:

```sh
npm install --prefix /tmp/vamos-admin-qa @electric-sql/pglite jsdom
NODE_PATH=/tmp/vamos-admin-qa/node_modules node tool/admin-users/verify.cjs /ruta/absoluta/proyecto
```

La comprobación incluye usuarios sin viajes, separación de roles, cancelación repetida/re-reserva, cancelación en cascada por conductor, cancelación histórica con motivo, asientos múltiples, fecha en Bolivia, validación y edición en el diálogo.
