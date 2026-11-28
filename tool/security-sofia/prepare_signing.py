"""Materialize GitHub production-signing secrets in the ephemeral runner only."""
import base64
import os
from pathlib import Path
import subprocess
import sys

names=['VAMOS_RELEASE_KEYSTORE','VAMOS_RELEASE_STORE_PASSWORD','VAMOS_RELEASE_KEY_PASSWORD','VAMOS_RELEASE_KEY_ALIAS']
missing=[name for name in names if not os.environ.get(name)]
if missing:raise SystemExit('Faltan secretos de firma de producción: '+', '.join(missing)+'. Sigue tool/security-sofia/README.md; no se generará una APK debug como alternativa.')
file=Path(os.environ['RUNNER_TEMP'])/'vamos-production.jks'
file.write_bytes(base64.b64decode(os.environ['VAMOS_RELEASE_KEYSTORE'],validate=True))
file.chmod(0o600)
# Both passwords are read through the environment, never command-line literals.
certificate=subprocess.run(['keytool','-list','-v','-keystore',str(file),'-storepass:env','VAMOS_RELEASE_STORE_PASSWORD','-alias',os.environ['VAMOS_RELEASE_KEY_ALIAS']],capture_output=True,text=True)
if certificate.returncode:raise SystemExit('No se pudo abrir la clave de producción. Comprueba los secretos; no se muestran los valores.')
if 'android debug' in certificate.stdout.lower():raise SystemExit('La clave corresponde a Android Debug y no sirve para el piloto')
with open(os.environ['GITHUB_ENV'],'a') as env:env.write(f'VAMOS_RELEASE_KEYSTORE_PATH={file}\n')
print('Firma de producción preparada sin exponer la clave ni sus contraseñas.')
