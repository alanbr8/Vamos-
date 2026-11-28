import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from signing_crypto import seal, unseal

class PhoneSigning(unittest.TestCase):
    password='Only-test-fixture-password-28-11'
    def test_encrypted_backup_recovers_original(self):
        raw=os.urandom(2048)
        encrypted=seal(raw,self.password)
        self.assertNotIn(self.password,encrypted)
        self.assertEqual(unseal(encrypted,self.password),raw)
    def test_wrong_password_rejected(self):
        encrypted=seal(b'private test fixture',self.password)
        with self.assertRaises(ValueError):unseal(encrypted,'Different-test-fixture-password')
    def test_tampered_backup_rejected(self):
        encrypted=seal(os.urandom(2048),self.password)
        replacement='A' if encrypted[-12]!='A' else 'B'
        damaged=encrypted[:-12]+replacement+encrypted[-11:]
        with self.assertRaises(ValueError):unseal(damaged,self.password)
    def test_short_password_rejected(self):
        with self.assertRaises(ValueError):seal(b'test','short')
    def test_existing_identity_is_not_overwritten(self):
        result=subprocess.run([sys.executable,str(Path(__file__).with_name('create_cloud_signing.py')),'unused'],env={**os.environ,'VAMOS_RELEASE_KEYSTORE':'existing-identity'},capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('No se reemplazará',result.stderr)
    def test_generate_and_prepare_with_real_tools(self):
        # Disposable test identity: never stored in GitHub or distributed as a release key.
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);out=root/'encrypted'
            env={**os.environ,'VAMOS_RELEASE_KEYSTORE':'','VAMOS_RELEASE_STORE_PASSWORD':self.password,'CONFIRM_FIRST_KEY':'CREAR PRIMERA FIRMA','GITHUB_STEP_SUMMARY':''}
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('create_cloud_signing.py')),str(out)],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(sorted(p.name for p in out.iterdir()),['LEEME.txt','VAMOS_RELEASE_KEYSTORE.txt','certificado-publico.pem'])
            env.update({'VAMOS_RELEASE_KEYSTORE':(out/'VAMOS_RELEASE_KEYSTORE.txt').read_text(),'RUNNER_TEMP':folder,'GITHUB_ENV':str(root/'env'),'VAMOS_RELEASE_KEY_PASSWORD':'','VAMOS_RELEASE_KEY_ALIAS':''})
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('prepare_signing.py'))],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertNotIn(self.password,result.stdout+result.stderr)
            self.assertTrue((root/'vamos-production.jks').is_file())

if __name__=='__main__':unittest.main()
