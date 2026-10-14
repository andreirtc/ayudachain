import importlib.util
import unittest
from uuid import uuid4
from datetime import date
from backend.tests.support import Harness,synthetic_pdf
from backend.app.commands import execute_command,DomainError


class FundsTests(unittest.TestCase):
    def test_ledger_identifies_primary_source_even_when_support_was_uploaded_first(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        funds=self.service()
        with Harness() as h,TestClient(app) as client:
            h.register_chain()
            support=h.upload('supporting')
            primary=h.upload('release_source')
            req=self.request(h,primary);req['supporting_evidence_ids']=[support]
            execute_command(h.actors['dswd'],'fund.release','support-first',req,lambda tx:funds.release(tx,req))
            response=client.get('/api/v1/funds',params={'disaster_id':str(h.disasters[0])},headers={'X-Demo-Actor-ID':str(h.actors['dswd'])})
            self.assertEqual(response.status_code,200)
            evidence=response.json()['data']['entries'][0]['evidence']
            self.assertEqual(evidence[0]['id'],str(support))
            self.assertEqual({e['id']:e.get('attachment_role') for e in evidence},{str(support):'supporting',str(primary):'release_source'})

    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.funds'),'Document-backed funding service missing')
        from backend.app.services import funds
        return funds

    def request(self,h,evidence,amount='10000000'):
        return {'disaster_id':h.disasters[0],'source_evidence_id':evidence,'supporting_evidence_ids':[],
                'document_type':'Sub-ARO','reference_number':'SYNTHETIC-2026-1','issued_date':date(2026,10,10),'amount_centavos':amount,
                'purpose':'Invented cash assistance','covered_area':'Invented Silong','signatories':[{'printed_name':'Invented Lira Sayo','printed_role':'Printed approver'}],'area_lines':[],'document_words':None,'document_figures_centavos':None}

    def test_actual_extraction_override_warning_and_duplicate_refusal(self):
        funds=self.service()
        with Harness() as h:
            h.register_chain()
            evidence=h.upload('release_source',synthetic_pdf('Invented release\nAmount: PHP 100,000.00\nIn words: ninety thousand pesos'))
            req=self.request(h,evidence,'11000000')
            ack=execute_command(h.actors['dswd'],'fund.release',str(uuid4()),req,lambda tx:funds.release(tx,req))
            with h.connection() as db:
                row=db.execute('SELECT * FROM fund_entries').fetchone()
                self.assertEqual(row['amount_review']['machine_amount_centavos'],'10000000')
                self.assertTrue(row['amount_review']['amount_overridden'])
                self.assertEqual(row['amount_review']['words_figures_state'],'disagree')
                self.assertIsNone(row['approved_by'])
                self.assertEqual(funds.totals(db,h.run,h.disasters[0])['remaining_centavos'],'11000000')
            with self.assertRaises(DomainError): execute_command(h.actors['dswd'],'fund.release',str(uuid4()),req,lambda tx:funds.release(tx,req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM fund_entries').fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='fund.duplicate_refused'").fetchone()['n'],1)

    def test_concurrent_correction_has_one_complete_successor(self):
        funds=self.service()
        with Harness() as h:
            h.register_chain(); req=self.request(h,h.upload('release_source'))
            ack=execute_command(h.actors['dswd'],'fund.release',str(uuid4()),req,lambda tx:funds.release(tx,req))
            original=__import__('uuid').UUID(ack['resources'][0]['id'])
            correction=dict(req,expected_revision=0,reason='Invented transcription correction',correction_kind='transcription',amount_centavos='12000000')
            from concurrent.futures import ThreadPoolExecutor
            def run(_):
                try: execute_command(h.actors['dswd'],'fund.correct',str(uuid4()),correction,lambda tx:funds.correct(tx,original,correction));return 'saved'
                except DomainError:return 'conflict'
            with ThreadPoolExecutor(max_workers=2) as pool: self.assertCountEqual(list(pool.map(run,[0,1])),['saved','conflict'])
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM fund_entries').fetchone()['n'],3)
                original_row=db.execute('SELECT * FROM fund_entries WHERE id=%s',(original,)).fetchone()
                reversal=db.execute("SELECT * FROM fund_entries WHERE kind='reversal'").fetchone()
                self.assertEqual(reversal['amount_review'],original_row['amount_review'])
                self.assertEqual(reversal['confirmed_fields'],original_row['confirmed_fields'])
                self.assertEqual(db.execute('SELECT count(*) n FROM fund_correction_sets').fetchone()['n'],1)
                self.assertEqual(funds.totals(db,h.run,h.disasters[0])['received_centavos'],'12000000')
                self.assertEqual(db.execute('SELECT count(*) n FROM commitments WHERE kind IN (%s,%s)',('fund_reversal','fund_replacement')).fetchone()['n'],2)
