import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest


class GeneratedCatalogueTests(unittest.TestCase):
    def test_ddl_is_identical_across_fresh_interpreters(self):
        source='from backend.migrations.catalogue import ddl; import hashlib; print(hashlib.sha256(ddl().encode()).hexdigest())'
        hashes=[]
        for seed in ['1','2']:
            env=os.environ.copy();env['PYTHONHASHSEED']=seed
            hashes.append(subprocess.check_output([sys.executable,'-c',source],env=env,text=True,timeout=15).strip())
        self.assertEqual(hashes[0],hashes[1])
        from backend.app.config import ROOT
        self.assertEqual(hashes[0],hashlib.sha256((ROOT/'backend/migrations/0001_catalogue.sql').read_text(encoding='utf-8').encode()).hexdigest())
