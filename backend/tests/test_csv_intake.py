import unittest
import os
from unittest.mock import patch
from types import SimpleNamespace
from uuid import uuid4
from backend.app.commands import DomainError
from backend.app.services import csv_intake


class CsvParserTests(unittest.TestCase):
    def setUp(self):
        self.barangay = uuid4()
        self.context = SimpleNamespace(role='dswd', barangay_id=None, actor_id=uuid4(), household_id=None)
        self.header = ','.join(csv_intake.COLUMNS) + '\n'

    def text(self, name='Invented Tala', birth='1980-01-02'):
        return self.header + f'{name},{birth},"Invented Street, 4",Zone A,{self.barangay}\n'

    def parse(self, content):
        return csv_intake.parse(content, self.context, {self.barangay})

    def test_utf8_bom_quotes_and_line_endings(self):
        rows, digest = self.parse('\ufeff' + self.text('Invented Mañana').replace('\n', '\r\n'))
        self.assertEqual(rows[0]['values']['address'], 'Invented Street, 4')
        self.assertEqual(rows[0]['values']['name'], 'Invented Mañana')
        self.assertEqual(digest, self.parse(self.text('Invented Mañana'))[1])

    def test_private_duplicate_unknown_and_malformed_headers_refused(self):
        for content in [self.header.strip()+',phone\n', 'name,name\n', 'unexpected\n', self.header+'"unclosed']:
            with self.subTest(content=content), self.assertRaises(DomainError): self.parse(content)

    def test_partial_validation_missing_birth_and_repeated_rows(self):
        content=self.text(birth='')+f'Invented Other,not-a-date,Street,Zone,{self.barangay}\n'+self.text(birth='').split('\n')[1]+'\n'
        rows,_=self.parse(content)
        self.assertEqual([r['status'] for r in rows], ['valid','invalid','skipped'])
        self.assertIn('birth_date_missing',rows[0]['warnings'])

    def test_scoped_barangay_and_single_beneficiary(self):
        self.context.role='barangay';self.context.barangay_id=uuid4()
        self.assertIn('own_barangay_only',self.parse(self.text())[0][0]['errors'])
        self.context.role='beneficiary'
        with self.assertRaises(DomainError):self.parse(self.text()+self.text().split('\n')[1]+'\n')

    def test_limits_and_controls(self):
        for content in ['x'*(csv_intake.MAX_BYTES+1),self.text('Invented\x00Tala')]:
            with self.subTest(content=content[:20]):
                if len(content)>csv_intake.MAX_BYTES:
                    with self.assertRaises(DomainError):self.parse(content)
                else:self.assertEqual(self.parse(content)[0][0]['status'],'invalid')
        with self.assertRaises(DomainError):self.parse(self.text('Invented\ud800Name'))
        with self.assertRaises(DomainError):self.parse(self.header+('\n'.join(self.text().split('\n')[1:2])+'\n')*(csv_intake.MAX_ROWS+1))

    def test_duplicate_scores_and_missing_birth_are_explained(self):
        values=self.parse(self.text())[0][0]['values']
        match=dict(values, name='Invented Tala', birth_date=None, household_id=uuid4(), display_id='DFC-2026-ABCD')
        evidence=csv_intake.matches(values,[match])[0]
        self.assertFalse(evidence['birth_date_match'])
        self.assertEqual(evidence['birth_date_comparison'],'unknown')
        self.assertEqual(evidence['name_similarity'],'1.0000')
        self.assertEqual(csv_intake.matches(dict(values,name='Invented Unrelated'),[match]),[])

    def test_key_is_stable_actor_bound_and_row_bound(self):
        _,digest=self.parse(self.text())
        key=csv_intake.row_key(self.context.actor_id,digest,1)
        self.assertEqual(key,csv_intake.row_key(self.context.actor_id,self.parse(self.text())[1],1))
        self.assertNotEqual(key,csv_intake.row_key(uuid4(),digest,1))
        self.assertNotEqual(key,csv_intake.row_key(self.context.actor_id,digest,2))


class CsvPersistenceTests(unittest.TestCase):
    def setUp(self):
        timeout=patch.dict(os.environ,{'PGCONNECT_TIMEOUT':'5'})
        timeout.start();self.addCleanup(timeout.stop)

    def test_read_only_preview_partial_success_replay_and_normal_audit(self):
        from backend.tests.support import Harness
        from backend.app.actor import resolve_identity
        with Harness() as h:
            with h.connection() as db:c=resolve_identity(db,h.actors['dswd'])
            text=','.join(csv_intake.COLUMNS)+f'\nInvented Csv One,1980-01-02,"Invented street, 1",Zone A,{h.barangays[0]}\nInvented Csv Two,bad,Street B,Zone B,{h.barangays[0]}\n'
            with h.connection() as db:
                before=db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            preview=csv_intake.preview(text,c)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'],before)
                self.assertEqual(db.execute('SELECT count(*) n FROM households').fetchone()['n'],0)
            first=csv_intake.confirm(text,preview['digest'],[1,2],c)
            self.assertEqual([v['status'] for v in first['outcomes']],['saved','invalid'])
            second=csv_intake.confirm(text,preview['digest'],[1],c)
            self.assertTrue(second['outcomes'][0]['replayed'])
            self.assertEqual(first['outcomes'][0]['resources'],second['outcomes'][0]['resources'])
            repeated=csv_intake.preview(text,c)
            self.assertEqual(repeated['rows'][0]['status'],'saved')
            self.assertEqual(repeated['rows'][0]['resources'],first['outcomes'][0]['resources'])
            with h.connection() as db:other=resolve_identity(db,h.actors['dswd2'])
            self.assertEqual(csv_intake.confirm(text,preview['digest'],[1],other)['outcomes'][0]['status'],'needs_review')
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM households').fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='registry.register'").fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT residence_state,identity_state FROM household_versions').fetchone(),dict(residence_state='unconfirmed',identity_state='pending_field_check'))

    def test_duplicate_rechecked_at_commit_and_scope_private_headers(self):
        from backend.tests.support import Harness
        from backend.app.actor import resolve_identity
        from backend.app.services import registry
        from backend.app.commands import execute_command
        with Harness() as h:
            with h.connection() as db:c=resolve_identity(db,h.actors['dswd'])
            text=','.join(csv_intake.COLUMNS)+f'\nInvented Csv Tala,1980-01-02,Invented street 4,Zone A,{h.barangays[0]}\n'
            p=csv_intake.preview(text,c)
            req=csv_intake.registration(p['rows'][0]['values'])
            execute_command(c.actor_id,'registry.register','manual-before-confirm',req,lambda tx:registry.register(tx,req))
            outcome=csv_intake.confirm(text,p['digest'],[1],c)['outcomes'][0]
            self.assertEqual(outcome['status'],'needs_review')
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM households').fetchone()['n'],1)
                bc=resolve_identity(db,h.actors['barangay'])
            with self.assertRaises(DomainError):csv_intake.preview(text.replace('name,','phone,'),bc)


if __name__=='__main__':unittest.main()
