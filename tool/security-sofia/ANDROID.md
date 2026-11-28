# Crear la primera firma desde Android — sin instalar herramientas

Usa Chrome y activa **Sitio para computadoras** en su menú si GitHub no muestra Settings, Actions o Run workflow. Inicia sesión como propietario de alanbr8/Vamos-.

La generación se hace en un runner temporal de GitHub, no en el teléfono. La clave privada existe allí mientras se genera y se cifra. Solo se entrega una copia cifrada con GnuPG/AES-256 y un certificado público; no se exporta la contraseña ni la clave sin cifrar. La automatización no administra tus secretos ni necesita un token administrador adicional.

## 1. Guarda tu contraseña privada

Abre el repositorio → **Settings → Secrets and variables → Actions → New repository secret**.

- **Name:** `VAMOS_RELEASE_STORE_PASSWORD`
- **Secret:** una contraseña exclusiva generada por tu gestor de contraseñas, preferiblemente 24 caracteres o más; mínimo 20. Sin saltos de línea ni espacios al principio o final. No reutilices la de GitHub.

Pulsa **Add secret** y guarda esa misma contraseña en tu gestor. No la envíes por chat: no podremos recuperarla si la pierdes.

## 2. Genera UNA primera firma

En **Actions**, elige **Crear primera firma INGENIX desde celular** → **Run workflow**.

- Selecciona la rama **main**.
- En Confirmación escribe exactamente: `CREAR PRIMERA FIRMA`.
- Ejecuta el workflow y espera que termine en verde.

Esta operación se detiene si ya existe VAMOS_RELEASE_KEYSTORE. No la uses para cambiar una firma que ya se haya distribuido. Después de crear la primera, completa los siguientes pasos antes de ejecutar otra creación. Las actualizaciones siempre usan la misma firma.

## 3. Conserva la copia cifrada y guárdala como secreto

En la ejecución terminada, baja hasta **Artifacts** y descarga **Firma-INGENIX-Cifrada**.

1. Abre el ZIP desde **Archivos** de Android y extrae su contenido.
2. Abre **VAMOS_RELEASE_KEYSTORE.txt** con un visor de texto que permita **Seleccionar todo → Copiar**. Empieza por `VAMOS-GPG-V1:`. No lo edites ni borres caracteres.
3. Conserva una copia privada del ZIP fuera de los artefactos temporales de GitHub y por separado de la contraseña. El artefacto caduca a los 90 días; no es un archivo permanente de custodia.
4. Vuelve a **Settings → Secrets and variables → Actions → New repository secret**:
   - **Name:** `VAMOS_RELEASE_KEYSTORE`
   - **Secret:** pega TODO el contenido del archivo de texto cifrado.
5. Pulsa **Add secret**.

No subas estos archivos al repositorio ni publiques la contraseña. La copia está cifrada, pero debe conservarse como material privado de INGENIX.

En esta ruta no hacen falta dos secretos adicionales: el alias predeterminado es `vamos-production` y la contraseña de la clave es la misma que la del almacén. El proceso sigue admitiendo los cuatro secretos anteriores para quien ya tenga un keystore propio.

## 4. Genera la APK y las evidencias

En **Actions → Compilar Vamos Android → Run workflow**, ejecuta la rama **main**.

Cuando termine en verde, descarga **Vamos-Produccion-Sofia**. Contendrá la APK release, el manifiesto final, verificación de firma, resultados de controles y SHA-256. La evidencia HSTS aparece en **Evidencia-HSTS-Sofia**.

La generación de la firma NO es todavía la generación ni validación del APK. No dar por cerradas las observaciones móviles hasta obtener y comprobar ese APK; después siguen las pruebas funcionales y la validación de Sofía.

## Recuperación futura

Para recuperar una firma existente conserva la copia cifrada y la contraseña, y vuelve a cargar esos mismos dos secretos. No ejecutes Crear primera firma para sustituir una clave perdida: otra clave no equivale a la identidad anterior y puede impedir las actualizaciones de instalaciones existentes.
