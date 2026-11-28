import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class FinalApkGate(unittest.TestCase):
    def check_gate(self, *, debug='false', minimum='31', cleartext='false', signer='INGENIX Vamos', signature_ok=True):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);tools=root/'bin';tools.mkdir()
            manifest=f'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.vamoscarpool.app"><uses-sdk android:minSdkVersion="{minimum}"/><application android:debuggable="{debug}" android:usesCleartextTraffic="{cleartext}"/></manifest>'
            for name,output,code in [('apkanalyzer',manifest,0),('apksigner',f'Signer #1 certificate DN: CN={signer}, O=INGENIX',0 if signature_ok else 1)]:
                tool=tools/name
                tool.write_text('#!'+sys.executable+'\nimport sys\nprint('+repr(output)+')\nsys.exit('+str(code)+')\n')
                tool.chmod(0o700)
            apk=root/'fixture.apk';apk.write_bytes(b'test fixture; not a distributable APK')
            env={**os.environ,'PATH':str(tools)+os.pathsep+os.environ['PATH']}
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('verify_apk.py')),str(apk),str(root/'evidence')],env=env,capture_output=True,text=True)
            return result.returncode
    def test_production_configuration_passes(self):self.assertEqual(self.check_gate(),0)
    def test_debug_is_rejected(self):self.assertNotEqual(self.check_gate(debug='true'),0)
    def test_old_android_is_rejected(self):self.assertNotEqual(self.check_gate(minimum='24'),0)
    def test_cleartext_is_rejected(self):self.assertNotEqual(self.check_gate(cleartext='true'),0)
    def test_debug_certificate_is_rejected(self):self.assertNotEqual(self.check_gate(signer='Android Debug'),0)
    def test_invalid_signature_is_rejected(self):self.assertNotEqual(self.check_gate(signature_ok=False),0)

if __name__=='__main__':unittest.main()
