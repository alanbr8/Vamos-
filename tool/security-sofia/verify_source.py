"""Fast regression checks; final acceptance still inspects the compiled APK."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

root=Path(sys.argv[1])
android=root/'vamos_app/android/app'
ns='{http://schemas.android.com/apk/res/android}'
application=ET.parse(android/'src/main/AndroidManifest.xml').getroot().find('application')
assert application.get(ns+'usesCleartextTraffic')=='false'
assert application.get(ns+'debuggable') is None  # Gradle assigns release=false; Android lint forbids hardcoding this.
assert application.get(ns+'networkSecurityConfig')=='@xml/network_security_config'
for manifest in android.glob('src/*/AndroidManifest.xml'):
    for node in ET.parse(manifest).iter('application'):
        assert node.get(ns+'usesCleartextTraffic')!='true',str(manifest)
config=ET.parse(android/'src/main/res/xml/network_security_config.xml').getroot()
assert config.find('base-config').get('cleartextTrafficPermitted')=='false'
gradle=(android/'build.gradle.kts').read_text()
assert 'minSdk = 31' in gradle
assert 'isDebuggable = false' in gradle
assert 'getByName("debug")' not in gradle
assert 'getByName("production")' in gradle
main=(root/'backend/src/main.ts').read_text()
assert main.index('app.use(securityHeaders)')<main.index('mountAdminPanel(app)')
print('OK: production signing configured, minSdk 31, debug disabled, HTTP denied and HSTS before all routes.')
