"""Materialize production signing only inside the ephemeral runner."""
import base64
import os
from pathlib import Path
import subprocess
from signing_crypto import PREFIX, unseal

store_password=os.environ.get('VAMOS_RELEASE_STORE_PASSWORD','')
value=os.environ.get('VAMOS_RELEASE_KEYSTORE','').strip()
missing=[name for name,content in [('VAMOS_RELEASE_KEYSTORE',value),('VAMOS_RELEASE_STORE_PASSWORD',store_password)] if not content]
if missing:raise SystemExit('Faltan secretos de firma de producción: '+', '.join(missing)+'. Sigue tool/security-sofia/ANDROID.md; no se generará una APK debug como alternativa.')
key_password=os.environ.get('VAMOS_RELEASE_KEY_PASSWORD') or store_password
alias=os.environ.get('VAMOS_RELEASE_KEY_ALIAS') or 'vamos-production'
if any('\n' in v or '\r' in v for v in [store_password,key_password,alias]):raise SystemExit('Los secretos de firma no pueden contener saltos de línea')
try:
    content=unseal(value,store_password) if value.startswith(PREFIX) else base64.b64decode(''.join(value.split()),validate=True)
except Exception:
    raise SystemExit('No se pudo abrir la copia de firma. Revisa la contraseña y el contenido completo del secreto.') from None
file=Path(os.environ['RUNNER_TEMP'])/'vamos-production.jks'
file.write_bytes(content);file.chmod(0o600)
certificate=subprocess.run(['keytool','-list','-v','-keystore',str(file),'-storepass:env','VAMOS_RELEASE_STORE_PASSWORD','-alias',alias],capture_output=True,text=True)
if certificate.returncode:
    file.unlink(missing_ok=True)
    raise SystemExit('No se pudo abrir la clave de producción. Comprueba los secretos; no se muestran sus valores.')
if 'android debug' in certificate.stdout.lower():
    file.unlink(missing_ok=True)
    raise SystemExit('La clave corresponde a Android Debug y no sirve para el piloto')
with open(os.environ['GITHUB_ENV'],'a') as env:
    env.write(f'VAMOS_RELEASE_KEYSTORE_PATH={file}\nVAMOS_RELEASE_KEY_PASSWORD={key_password}\nVAMOS_RELEASE_KEY_ALIAS={alias}\n')
print('Firma de producción preparada sin exponer la clave ni sus contraseñas.')
