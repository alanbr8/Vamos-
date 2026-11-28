"""Publish only the previously verified production APK, without rebuilding or signing."""
from pathlib import Path
import hashlib
import json
import subprocess

EXPECTED_SHA='f995f6516bea76bd51e0f218869cf7886b048cbf5f41df919afd0774a208cf95'
SOURCE_COMMIT='f8739cc6bb95109bd8284116c3ee5d657ce9b4b3'
CERT='94c715a00601a7cd40e064133fca8eeee38be6949217c4b2e373c15c7775d980'
TAG='v1.10.1'
NAME='Vamos.version.1.10.1.apk'
root=Path('verified-artifact')
apks=list(root.rglob('app-release.apk'))
reports=list(root.rglob('resultado-apk.json'))
if len(apks)!=1 or len(reports)!=1:raise SystemExit('El artefacto debe contener exactamente una APK y su informe')
apk=apks[0]
report=json.loads(reports[0].read_text())
actual=hashlib.file_digest(apk.open('rb'),'sha256').hexdigest()
checks=['02_signature_is_not_android_debug','03_debuggable_false','04_min_sdk_at_least_31','05_cleartext_false']
if actual!=EXPECTED_SHA or report.get('sha256')!=EXPECTED_SHA:raise SystemExit('La APK no corresponde al archivo verificado')
if report.get('commit')!=SOURCE_COMMIT or report.get('versionName')!='1.10.1':raise SystemExit('Versión o commit de origen inesperado')
if report.get('expectedSignerSha256')!=CERT or report.get('actualSignerSha256')!=[CERT]:raise SystemExit('El certificado de producción no corresponde')
if any(report.get('checks',{}).get(key) is not True for key in checks):raise SystemExit('Falta una comprobación de seguridad aprobada')

out=Path('public-download');out.mkdir(exist_ok=True)
published=out/NAME
published.write_bytes(apk.read_bytes())
checksum=out/'SHA256SUMS.txt'
checksum.write_text(f'{EXPECTED_SHA}  {NAME}\n')
notes=out/'release-notes.md'
notes.write_text('Vamos!! 1.10.1 — APK de producción para Android 12 o superior.\n\nFirma de INGENIX comprobada por huella SHA-256; depuración deshabilitada y tráfico HTTP deshabilitado. Este archivo es idéntico a la APK verificada en la ejecución 46146563280.\n\nLas comprobaciones automáticas no sustituyen las pruebas funcionales ni el visto bueno del área de Seguridad de Sofía. La nueva firma puede requerir reinstalación respecto de la APK antigua de pruebas; revise antes sus datos locales.\n\nSHA-256 del APK: '+EXPECTED_SHA+'\n')

def gh(*args,check=True):
    return subprocess.run(['gh',*args],check=check,capture_output=True,text=True)

existing=gh('release','view',TAG,'--json','isDraft',check=False)
if existing.returncode==0:
    draft=json.loads(existing.stdout)['isDraft']
    if not draft:
        verification=Path('existing-release');verification.mkdir(exist_ok=True)
        gh('release','download',TAG,'--pattern',NAME,'--dir',str(verification),'--clobber')
        digest=hashlib.file_digest((verification/NAME).open('rb'),'sha256').hexdigest()
        if digest!=EXPECTED_SHA:raise SystemExit('Ya existe una publicación diferente; no se reemplazará')
        print('La APK verificada ya está publicada. No se modificó el archivo existente.')
        raise SystemExit(0)
else:
    gh('release','create',TAG,'--target',SOURCE_COMMIT,'--title','Vamos!! 1.10.1 — Android','--notes-file',str(notes),'--draft')

# Only a draft can receive these exact files. No clobber of published assets.
gh('release','upload',TAG,str(published),str(checksum),'--clobber')
verification=Path('uploaded-verification');verification.mkdir(exist_ok=True)
gh('release','download',TAG,'--pattern',NAME,'--dir',str(verification),'--clobber')
if hashlib.file_digest((verification/NAME).open('rb'),'sha256').hexdigest()!=EXPECTED_SHA:
    raise SystemExit('La descarga no coincide; la publicación permanece como borrador')
gh('release','edit',TAG,'--draft=false','--latest')
print('Publicada la APK 1.10.1; la descarga conserva el SHA-256 del archivo verificado.')
