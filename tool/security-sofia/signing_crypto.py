"""GnuPG symmetric encryption for the phone-assisted signing backup."""
import base64
from pathlib import Path
import subprocess
import tempfile

PREFIX='VAMOS-GPG-V1:'

def validate_password(password):
    if len(password)<20 or '\n' in password or '\r' in password or password!=password.strip():
        raise ValueError('Usa una contraseña exclusiva de al menos 20 caracteres, sin saltos de línea ni espacios al inicio o al final.')

def transform(payload: bytes, password: str, *, decrypt=False):
    validate_password(password)
    with tempfile.TemporaryDirectory(prefix='vamos-signing-') as folder:
        root=Path(folder);root.chmod(0o700)
        source=root/'input';source.write_bytes(payload);source.chmod(0o600)
        command=['gpg','--no-options','--homedir',folder,'--batch','--yes','--pinentry-mode','loopback','--no-symkey-cache','--passphrase-fd','0','--output','-']
        if decrypt:command+=['--decrypt']
        else:command+=['--symmetric','--cipher-algo','AES256','--s2k-mode','3','--s2k-digest-algo','SHA512','--s2k-count','65011712','--compress-algo','none']
        result=subprocess.run(command+[str(source)],input=(password+'\n').encode(),capture_output=True)
        if result.returncode:raise ValueError('No se pudo cifrar o abrir la copia de firma. Comprueba la contraseña y que el contenido esté completo.')
        return result.stdout

def seal(payload: bytes,password: str):
    return PREFIX+base64.b64encode(transform(payload,password)).decode('ascii')

def unseal(value: str,password: str):
    if not value.startswith(PREFIX):raise ValueError('Formato de copia de firma no válido')
    encrypted=base64.b64decode(''.join(value[len(PREFIX):].split()),validate=True)
    return transform(encrypted,password,decrypt=True)
