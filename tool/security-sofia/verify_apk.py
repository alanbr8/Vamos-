"""Verify the final APK and write public, reproducible audit evidence."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

apk=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
sdk=Path(os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT') or '/opt/android-sdk')

def tool(name):
    found=shutil.which(name)
    if found:return found
    options=list(sdk.glob(f'cmdline-tools/*/bin/{name}'))+list(sdk.glob(f'build-tools/*/{name}'))
    if not options:raise SystemExit(f'Falta la herramienta Android SDK: {name}')
    return str(sorted(options,key=lambda p:[int(x) for x in re.findall(r'\d+',str(p))])[-1])

def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True).stdout

analyzer=tool('apkanalyzer')
signer=tool('apksigner')
manifest=run([analyzer,'manifest','print',str(apk)])
signature=subprocess.run([signer,'verify','--verbose','--print-certs',str(apk)],check=True,capture_output=True,text=True)
certificate=signature.stdout+'\n'+signature.stderr
expected=re.sub(r'[^0-9a-f]','',os.environ.get('VAMOS_RELEASE_CERT_SHA256','').lower())
fingerprints={value.replace(':','').lower() for value in re.findall(r'certificate SHA-256 digest:\s*([0-9a-fA-F:]+)',certificate,re.I)}
print('Certificados públicos detectados:')
for line in certificate.splitlines():
    if 'certificate' in line.lower() and ('dn:' in line.lower() or 'sha-256' in line.lower()): print(line)
(out/'03-05-manifest-final.xml').write_text(manifest)
(out/'02-firma-produccion.txt').write_text(certificate)
ns='{http://schemas.android.com/apk/res/android}'
root=ET.fromstring(manifest)
application=root.find('application')
minimum=int(root.find('uses-sdk').get(ns+'minSdkVersion','0'))
checks={
    '02_signature_is_not_android_debug':len(expected)==64 and fingerprints=={expected} and not bool(re.search(r'CN\s*=\s*Android Debug',certificate,re.I)),
    '03_debuggable_false':application.get(ns+'debuggable','false')=='false',
    '04_min_sdk_at_least_31':minimum>=31,
    '05_cleartext_false':application.get(ns+'usesCleartextTraffic')=='false',
}
result={
    'generatedAtUtc':datetime.now(timezone.utc).isoformat(),
    'commit':os.environ.get('GITHUB_SHA'),
    'workflow':os.environ.get('GITHUB_RUN_ID'),
    'apk':apk.name,'sha256':hashlib.file_digest(apk.open('rb'),'sha256').hexdigest(),
    'package':root.get('package'),'versionName':root.get(ns+'versionName'),'versionCode':root.get(ns+'versionCode'),
    'minSdkVersion':minimum,'expectedSignerSha256':expected,'actualSignerSha256':sorted(fingerprints),'checks':checks,
    'scope':'Verificación estática del APK final. Pendientes pruebas funcionales, prueba dinámica de HTTP y validación de Sofía.',
}
(out/'resultado-apk.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(out/'SHA256SUMS.txt').write_text(f"{result['sha256']}  {apk.name}\n")
print(json.dumps(result,ensure_ascii=False,indent=2))
if not all(checks.values()):raise SystemExit('APK rechazado: no cumple los controles de Sofía')
