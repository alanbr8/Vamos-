"""Apply the five Sofia remediation controls to the extracted application."""
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET

root=Path(sys.argv[1])
source=Path(__file__).resolve().parent
backend=root/'backend/src'
for name in ['security-headers.ts','security-headers.spec.ts']:
    shutil.copyfile(source/name,backend/name)
main=backend/'main.ts'
text=main.read_text()
if "from './security-headers'" not in text:
    text="import { securityHeaders } from './security-headers';\n"+text
if '  app.use(securityHeaders);' not in text:
    anchor="  app.useBodyParser('json', { limit: '2mb' });"
    if anchor not in text:raise SystemExit('No se encontró el punto de instalación de cabeceras')
    text=text.replace(anchor,"  app.use(securityHeaders);\n"+anchor)
main.write_text(text)
app=root/'vamos_app'
android=app/'android/app'
shutil.copyfile(source/'build.gradle.kts',android/'build.gradle.kts')
manifest=android/'src/main/AndroidManifest.xml'
text=manifest.read_text()
for attr,value in [('usesCleartextTraffic','false'),('debuggable','false'),('networkSecurityConfig','@xml/network_security_config')]:
    pattern=rf'android:{attr}="[^"]*"'
    if re.search(pattern,text):text=re.sub(pattern,f'android:{attr}="{value}"',text)
    else:text=text.replace('<application',f'<application\n        android:{attr}="{value}"',1)
manifest.write_text(text)
# Cleartext cannot be reenabled by the debug/profile manifest merge.
for variant in ['debug','profile']:
    variant_file=android/f'src/{variant}/AndroidManifest.xml'
    if variant_file.exists():
        text=variant_file.read_text().replace('android:usesCleartextTraffic="true"','android:usesCleartextTraffic="false"').replace('android:debuggable="true"','android:debuggable="false"')
        variant_file.write_text(text)
resources=android/'src/main/res/xml'
resources.mkdir(parents=True,exist_ok=True)
shutil.copyfile(source/'network_security_config.xml',resources/'network_security_config.xml')
shutil.copyfile(source/'app_config.dart',app/'lib/core/config/app_config.dart')
pubspec=app/'pubspec.yaml'
pubspec.write_text(re.sub(r'^version:.*$', 'version: 1.10.1+40',pubspec.read_text(),flags=re.M))
assert 'android:usesCleartextTraffic="true"' not in manifest.read_text()
ET.parse(manifest)
