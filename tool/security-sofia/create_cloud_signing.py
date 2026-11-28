"""Generate the FIRST signing identity only after the owner supplies a private secret."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from signing_crypto import seal, unseal, validate_password

if os.environ.get('VAMOS_RELEASE_KEYSTORE'):
    raise SystemExit('Ya existe VAMOS_RELEASE_KEYSTORE. No se reemplazará la firma instalada.')
if os.environ.get('CONFIRM_FIRST_KEY')!='CREAR PRIMERA FIRMA':
    raise SystemExit('Esta operación requiere confirmar CREAR PRIMERA FIRMA en Run workflow.')
password=os.environ.get('VAMOS_RELEASE_STORE_PASSWORD','')
try:validate_password(password)
except ValueError as error:raise SystemExit(str(error))
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
if any(out.iterdir()):raise SystemExit('La carpeta de salida debe estar vacía; no se reemplazará otra copia de firma.')
with tempfile.TemporaryDirectory(prefix='vamos-keystore-') as folder:
    key=Path(folder)/'vamos-production.jks'
    result=subprocess.run(['keytool','-genkeypair','-keystore',str(key),'-storetype','JKS','-alias','vamos-production','-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=INGENIX Vamos, OU=Desarrollo, O=INGENIX, L=Santa Cruz, C=BO','-storepass:env','VAMOS_RELEASE_STORE_PASSWORD','-keypass:env','VAMOS_RELEASE_STORE_PASSWORD'],capture_output=True,text=True)
    if result.returncode:raise SystemExit('No se pudo generar la firma de producción. No se publicarán archivos privados.')
    key.chmod(0o600)
    original=key.read_bytes()
    protected=seal(original,password)
    if unseal(protected,password)!=original:raise SystemExit('Falló la comprobación de recuperación de la copia cifrada')
    certificate=subprocess.run(['keytool','-exportcert','-rfc','-keystore',str(key),'-alias','vamos-production','-storepass:env','VAMOS_RELEASE_STORE_PASSWORD'],check=True,capture_output=True).stdout
    # These are the only exported files: encrypted key and PUBLIC certificate.
    (out/'VAMOS_RELEASE_KEYSTORE.txt').write_text(protected+'\n')
    (out/'certificado-publico.pem').write_bytes(certificate)
    (out/'LEEME.txt').write_text('Copia cifrada de la primera firma de INGENIX Vamos. Guarda este archivo y tu contraseña por separado. Desde Android abre VAMOS_RELEASE_KEYSTORE.txt, copia TODO su contenido y guárdalo como el secreto VAMOS_RELEASE_KEYSTORE del repositorio. Conserva VAMOS_RELEASE_STORE_PASSWORD con la contraseña original. No generes otra firma para actualizaciones. La misma contraseña abre el almacén y la clave; el alias es vamos-production. Esta copia NO es una APK.\n')
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as file:
            file.write('## Firma creada y copia cifrada verificada\n\nDescarga **Firma-INGENIX-Cifrada** en Artifacts y conserva una copia privada. Guarda la contraseña por separado.\n\nEn Android abre el ZIP y VAMOS_RELEASE_KEYSTORE.txt, copia todo su contenido y crea el secreto **VAMOS_RELEASE_KEYSTORE**. Después ejecuta **Compilar Vamos Android**.\n\nNo vuelvas a generar una firma para actualizar la aplicación. La clave privada no se publica sin cifrar.\n')
print('Primera firma creada. Solo se exportó la copia cifrada y el certificado público; conserva la copia y completa VAMOS_RELEASE_KEYSTORE.')
