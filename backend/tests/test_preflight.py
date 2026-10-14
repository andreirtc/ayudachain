import importlib.util
import unittest


class PreflightTests(unittest.TestCase):
    def load_config(self):
        spec = importlib.util.find_spec('backend.app.config')
        self.assertIsNotNone(spec, 'MVP local preflight is missing')
        from backend.app.config import validate_environment
        return validate_environment

    def test_public_rpc_is_rejected_even_with_a_key(self):
        check = self.load_config()
        with self.assertRaisesRegex(ValueError, 'loopback'):
            check({'MVP_RPC_URL': 'https://example.org', 'MVP_DATABASE_URL': 'postgresql://localhost/demo'}, node_version='v22.22.0')

    def test_missing_postgres_is_not_replaced_by_sqlite(self):
        check = self.load_config()
        with self.assertRaisesRegex(ValueError, 'PostgreSQL'):
            check({'MVP_RPC_URL': 'http://127.0.0.1:8545', 'MVP_DATABASE_URL': 'sqlite:///demo.db'}, node_version='v22.22.0')

    def test_unsupported_node_fails_explicitly(self):
        check = self.load_config()
        with self.assertRaisesRegex(ValueError, 'Node'):
            check({'MVP_RPC_URL': 'http://127.0.0.1:8545', 'MVP_DATABASE_URL': 'postgresql://localhost/demo'}, node_version='v25.4.0')

    def test_loopback_supported_setup_is_pure_and_repeatable(self):
        check = self.load_config()
        env = {'MVP_RPC_URL': 'http://127.0.0.1:8545', 'MVP_DATABASE_URL': 'postgresql://localhost/demo'}
        self.assertEqual(check(env, node_version='v22.22.0'), check(env, node_version='v22.22.0'))
        self.assertEqual(env['MVP_DATABASE_URL'], 'postgresql://localhost/demo')


if __name__ == '__main__':
    unittest.main()
