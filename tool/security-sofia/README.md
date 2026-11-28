# Subsanación de seguridad — Piloto Sofía — Vamos 1.10.1

Estado: correcciones de código preparadas; el cierre depende del despliegue y de las evidencias del APK final. No se debe presentar esta documentación como prueba de una compilación todavía no generada.

## Correcciones

1. HSTS: middleware global previo a todas las rutas: `Strict-Transport-Security: max-age=31536000`. Cubre la API, /admin y /admin/revision-sofia, incluso sus errores. Se limita al hostname administrado; no se incluye includeSubDomains ni preload sin validar primero servicios adicionales. Render conserva su redirección HTTP a HTTPS. La cabecera no reactiva el acceso temporal de revisión si ya venció.
2. Firma: Android release usa exclusivamente una clave privada de producción del custodio INGENIX; la configuración y el preflight rechazan usar Android Debug. No hay sustitución automática por una clave de pruebas. El certificado Android puede ser autofirmado por INGENIX; no necesita comprarse un certificado TLS.
3. Depuración: workflow cambia `flutter build apk --debug` por `--release`; Gradle fija `isDebuggable=false` y el manifiesto principal fija `android:debuggable=false`.
4. Compatibilidad: `minSdk=31` (Android 12), sujeto al parque aprobado para el piloto. El mínimo no garantiza que un teléfono tenga parches actuales.
5. Tráfico: `usesCleartextTraffic=false` en el manifiesto principal y en las variantes existentes; Network Security Config deniega HTTP y usa certificados del sistema. La configuración de la API usa HTTPS por defecto y rechaza una API HTTP en release.

Se aplica después de generar los archivos Android porque ese paso sobrescribía app/build.gradle.kts. Se mantienen las mejoras de chat, administración y Solo mujeres.

## Desde un celular Android

Ya puedes generar la primera firma desde GitHub, sin instalar herramientas en el teléfono. Sigue [ANDROID.md](ANDROID.md): se usa una contraseña privada, se descarga solo una copia cifrada y se guardan dos secretos. La creación requiere ejecución manual del propietario; no se ha generado automáticamente una clave de producción por añadir este código.

## Único requisito privado: firma de producción

Este repositorio no contiene la clave ni sus contraseñas. Conserva una copia privada del keystore y de las contraseñas: las futuras actualizaciones deben usar la misma identidad de firma. No reutilices el antiguo VAMOS_ANDROID_KEYSTORE de pruebas.

En un equipo del custodio con Java/keytool (incluido con Android Studio):

1. Descarga `crear-clave-produccion.ps1` y ejecútalo en PowerShell. Se creará `Documentos/INGENIX-Vamos-Firma/vamos-production.jks`, sin sobrescribir una clave existente. keytool solicita las contraseñas de forma interactiva. También se genera un archivo Base64 privado para cargar el secreto.
2. Guarda una copia privada del keystore y las contraseñas en el sistema de custodia de INGENIX.
3. En GitHub → alanbr8/Vamos- → Settings → Secrets and variables → Actions → New repository secret, agrega:

| Nombre | Valor |
|---|---|
| VAMOS_RELEASE_KEYSTORE | Contenido completo de VAMOS_RELEASE_KEYSTORE.txt (Base64) |
| VAMOS_RELEASE_STORE_PASSWORD | Contraseña del almacén elegida en keytool |
| VAMOS_RELEASE_KEY_PASSWORD | Contraseña de la clave; si pulsaste Enter para usar la del almacén, repite esa contraseña |
| VAMOS_RELEASE_KEY_ALIAS | vamos-production |

4. En Actions, ejecuta **Compilar Vamos Android → Run workflow**. Si la ejecución anterior se detuvo por secretos faltantes, vuelve a ejecutar el workflow completo tras guardarlos.

No pegues claves ni contraseñas en chats, incidencias, archivos del repositorio o evidencias enviadas a Sofía. Los secretos llegan al runner temporal por variables, y el keystore se retira al finalizar el job. La herramienta de firma no imprime sus contenidos.

## Evidencias reales

- `Vamos-Produccion-Sofia`: APK release, manifiesto fusionado final, verificación apksigner, huella SHA-256 del APK y resultado JSON por observación. Solo se publica el artefacto si todas las comprobaciones estáticas pasan.
- `Evidencia-HSTS-Sofia`: respuestas públicas de las rutas evaluadas y redirección HTTP a HTTPS, con fecha UTC y resultado. Un resultado false es pendiente, no cerrado.
- Las ejecuciones y commits permiten identificar la versión exacta. Las evidencias no incluyen contraseñas, tokens, documentos ni datos de usuarios.

Comprobación manual de HSTS: `python3 tool/security-sofia/verify_web.py evidencias/web`.

## Antes de solicitar el visto bueno

1. Comprobar que la versión desplegada responde con HSTS.
2. Cargar firma y generar la APK de producción, descargar ambos artefactos de Actions y conservarlos en el expediente privado.
3. Probar instalación y funcionamiento en Android 12 o superior: registro/login, recuperación, fotos/documentos, publicación/búsqueda, reserva/aceptación y chat. Confirmar bloqueo de HTTP mediante prueba dinámica controlada con datos ficticios. Revisar especialmente Firebase/push al cambiar la firma y registrar su SHA-256 donde corresponda.
4. La APK antigua firmada con debug no recibe cambios retroactivos. No usar Vamos.version.1.9.9.apk como evidencia de esta subsanación. Una instalación con otra firma puede requerir desinstalar la anterior; revisar primero los datos locales y probar el procedimiento.
5. Entregar a Sofía la nueva APK y las evidencias de esa misma huella. Marcar cada observación como Corregida, pendiente de validación de Sofía solo tras obtener el resultado correspondiente. Sofía decide el cierre y el inicio del piloto.

Los ZIP originales se conservan como fuente histórica; los scripts de construcción aplican la corrección. No construir esos ZIP directamente para distribuir una APK sin aplicar las correcciones.
