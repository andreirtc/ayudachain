"""Real PostgreSQL boundaries: no SQLite or chain success double."""
import importlib.util
import unittest
from uuid import uuid4


class FoundationTests(unittest.TestCase):
    def foundation(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.models.mvp'), 'Typed MVP relational model is missing')
        from backend.tests.support import Harness
        return Harness()

    def test_stored_actor_scope_and_inactive_system_denial(self):
        with self.foundation() as h:
            from backend.app.actor import resolve_identity
            from backend.app.commands import DomainError
            with h.connection() as db:
                c = resolve_identity(db, h.actors['dswd'])
                self.assertEqual(c.role, 'dswd')
                self.assertEqual(c.identity_assurance, 'claimed_unverified')
                for actor in [uuid4(), h.actors['system'], h.actors['pending']]:
                    with self.assertRaises(DomainError): resolve_identity(db, actor)

    def test_cross_run_foreign_key_is_rejected(self):
        with self.foundation() as h:
            import psycopg
            with self.assertRaises(psycopg.errors.ForeignKeyViolation):
                with h.connection() as db:
                    db.execute('SET CONSTRAINTS ALL IMMEDIATE')
                    db.execute('INSERT INTO actors(id,run_id,office_id,role,display_name,current_version_id,revision,created_by) VALUES(%s,%s,%s,%s,%s,%s,0,%s)',
                               (uuid4(),uuid4(),h.office,'dswd','Invented actor',uuid4(),h.actors['system']))

    def test_separate_connections_serialize_stale_edits(self):
        with self.foundation() as h:
            from concurrent.futures import ThreadPoolExecutor
            from backend.app.commands import execute_command,DomainError
            def attempt(_):
                try:
                    execute_command(h.actors['dswd'],'deactivate',str(uuid4()),{'revision':0},lambda tx:h.deactivate(tx,h.actors['disbursing']))
                    return 'saved'
                except DomainError as e: return e.code
            with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(attempt,[0,1]))
            self.assertCountEqual(results,['saved','stale_revision'])

    def test_missing_audit_rolls_back_new_version(self):
        with self.foundation() as h:
            import psycopg
            from backend.app.commands import execute_command
            def unlogged(tx):
                actor=tx.get('actors',h.actors['disbursing'])
                v=tx.insert('actor_versions',dict(actor_id=actor['id'],predecessor_id=actor['current_version_id'],status='deactivated'))
                tx.update('actors',actor['id'],{'current_version_id':v['id'],'revision':1})
                return [('actor_version_id',v['id'])]
            with self.assertRaises(psycopg.errors.CheckViolation):
                execute_command(h.actors['dswd'],'unlogged',str(uuid4()),{},unlogged)

    def test_atomic_action_audit_and_replay_current_ack(self):
        with self.foundation() as h:
            from backend.app.commands import execute_command, DomainError
            def change(tx):
                return h.deactivate(tx, h.actors['disbursing'])
            key = str(uuid4())
            first = execute_command(h.actors['dswd'], 'deactivate', key, {'revision': 0}, change)
            second = execute_command(h.actors['dswd'], 'deactivate', key, {'revision': 0}, change)
            self.assertEqual(first['resources'], second['resources'])
            self.assertTrue(second['replayed'])
            with self.assertRaises(DomainError):
                execute_command(h.actors['dswd'], 'deactivate', key, {'revision': 1}, change)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) FROM actor_versions WHERE actor_id=%s', (h.actors['disbursing'],)).fetchone()['count'], 2)
                self.assertEqual(db.execute("SELECT count(*) FROM audit_events WHERE action='actor.deactivate'").fetchone()['count'], 1)

    def test_late_failure_rolls_back_action_and_audit(self):
        with self.foundation() as h:
            from backend.app.commands import execute_command
            def broken(tx):
                h.deactivate(tx, h.actors['disbursing'])
                raise RuntimeError('injected after audit')
            with self.assertRaises(RuntimeError):
                execute_command(h.actors['dswd'], 'deactivate', str(uuid4()), {}, broken)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) FROM actor_versions WHERE actor_id=%s', (h.actors['disbursing'],)).fetchone()['count'], 1)
                self.assertEqual(db.execute("SELECT count(*) FROM audit_events WHERE action='actor.deactivate'").fetchone()['count'], 0)

    def test_append_only_runtime_cannot_edit_history(self):
        with self.foundation() as h:
            import psycopg
            with self.assertRaises(psycopg.Error):
                with h.connection() as db:
                    db.execute("UPDATE actor_versions SET reason='changed' WHERE actor_id=%s", (h.actors['dswd'],))


if __name__ == '__main__': unittest.main()
