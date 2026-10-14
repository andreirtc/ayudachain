"""Stopping an owned supervisor releases its whole tree and preserves others."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(os.name == 'nt', 'Windows process-tree regression')
class LocalSupervisorTests(unittest.TestCase):
    def test_owned_stop_releases_descendants_and_preserves_unrelated_process(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'child.json'
            source = ('import subprocess,sys,time,json; '
                      'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(90)"]); '
                      'open(sys.argv[1],"w").write(json.dumps({"pid":p.pid})); time.sleep(90)')
            owned = subprocess.Popen([sys.executable, '-c', source, str(marker)],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            other = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(90)'],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            child_pid = None
            try:
                for _ in range(100):
                    if marker.exists():
                        try: child_pid = json.loads(marker.read_text())['pid']; break
                        except (ValueError, KeyError): pass
                    time.sleep(.05)
                self.assertIsNotNone(child_pid)
                from backend.scripts.local_mvp import stop_owned
                stop_owned([('test', owned, [], Path(directory), None)])
                self.assertIsNotNone(owned.poll())
                result = subprocess.run(['tasklist', '/FI', f'PID eq {child_pid}', '/FO', 'CSV', '/NH'],
                                        capture_output=True, text=True, timeout=5)
                self.assertNotIn(str(child_pid), result.stdout)
                self.assertIsNone(other.poll())
            finally:
                for process in (owned, other):
                    if process.poll() is None:
                        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                       capture_output=True, timeout=10)
                    process.wait(timeout=5)
                if child_pid:
                    subprocess.run(['taskkill', '/PID', str(child_pid), '/T', '/F'],
                                   capture_output=True, timeout=5)
