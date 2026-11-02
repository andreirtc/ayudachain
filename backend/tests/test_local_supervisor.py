"""Stopping an owned supervisor releases its whole tree and preserves others."""
import json
import os
import socket
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


class ParallelDemoTests(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'POSIX socket restart regression')
    def test_recently_stopped_service_port_can_restart_without_taking_a_listener(self):
        from backend.scripts.local_mvp import available
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
            listener.listen()
            self.assertFalse(available(port))
            with socket.create_connection(('127.0.0.1', port)) as client:
                accepted, _ = listener.accept()
                with accepted:
                    accepted.shutdown(socket.SHUT_WR)
                    self.assertEqual(client.recv(1), b'')
        self.assertTrue(available(port))

    def test_alternate_ports_route_frontend_to_its_own_api(self):
        from backend.scripts import local_mvp
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.runtime').mkdir()
            (root / '.runtime/deployment.json').write_text('{}')
            with patch.object(local_mvp, 'ROOT', root), \
                 patch.object(local_mvp, 'environment', return_value=('node', 'python')), \
                 patch.object(local_mvp, 'prepare'), \
                 patch.object(local_mvp, 'available', return_value=True) as available, \
                 patch.object(local_mvp.subprocess, 'Popen', side_effect=lambda *a, **k: Mock(pid=123)) as start, \
                 patch.object(local_mvp, 'stop_owned'), \
                 patch.object(local_mvp.time, 'sleep', side_effect=KeyboardInterrupt):
                local_mvp.serve(api_port=8001, frontend_port=3001)
            self.assertEqual([c.args[0] for c in available.call_args_list], [3001, 8001])
            calls = start.call_args_list
            self.assertEqual(calls[0].args[0][-2:], ['--port', '8001'])
            self.assertEqual(calls[-1].args[0][-2:], ['--port', '3001'])
            self.assertEqual(calls[-1].kwargs['env']['NEXT_PUBLIC_API_URL'], 'http://127.0.0.1:8001')

    def test_port_collision_is_rejected_before_starting_services(self):
        from backend.scripts import local_mvp
        with patch.object(local_mvp, 'environment') as environment:
            with self.assertRaises(ValueError):
                local_mvp.serve(api_port=3001, frontend_port=3001)
            environment.assert_not_called()


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
