import importlib.util
import unittest
from unittest.mock import patch
from backend.app.services.blockchain import BlockchainService


class LegacyTests(unittest.TestCase):
    def test_transport_or_absent_record_can_never_verify_or_fabricate_reference(self):
        svc=BlockchainService()
        with patch.object(svc,'_execute_cli',return_value={'success':False}):
            result=svc.verify_receipt('DFC-2026-OLD1','0x'+'ab'*32)
            self.assertFalse(result.get('matched'));self.assertFalse(result.get('success'))
            self.assertNotIn('onchainHash',result)
            for result in [svc.release_fund('old',1,'Invented flood','Invented source'),svc.allocate_fund('old','allocation','bar',1),svc.confirm_distribution('old','distribution','beneficiary',1,'0x'+'ab'*32)]:
                self.assertNotIn('txHash',result)
            self.assertFalse(svc.get_status().get('success'))
        with patch.object(svc,'_execute_cli',return_value={'success':True,'exists':False,'matched':False}):
            self.assertFalse(svc.verify_receipt('absent','0x'+'ab'*32)['matched'])

    def test_frozen_legacy_reader_exists_without_pivot_writes(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.legacy'))

    def test_idempotent_import_preserves_exact_fields_without_eligibility(self):
        import sqlite3
        from contextlib import closing
        import tempfile
        from pathlib import Path
        from backend.tests.support import Harness
        from backend.app.commands import execute_command
        from backend.app.services.legacy import import_snapshot,check
        with Harness() as h,tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'invented.sqlite'
            with closing(sqlite3.connect(source)) as old:
                old.execute('CREATE TABLE distributions(id integer,distribution_id text,beneficiary_id text,batch_id text,amount real,ocr_text text,verification_method text,blockchain_tx_hash text)')
                fields=(1,'DFC-2026-OLD1','DFC-2026-BEN1','invented-batch',435.0,'Invented retained receipt','QR_VOUCHER_PHYSICAL_RECEIPT','untrusted-reference')
                old.execute('INSERT INTO distributions VALUES(?,?,?,?,?,?,?,?)',fields)
                old.commit()
            for key in ['first','again']:
                execute_command(h.actors['dswd'],'legacy.import',key,{'path':str(source)},lambda tx:import_snapshot(tx,source))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM legacy_records').fetchone()['n'],1)
                row=db.execute('SELECT * FROM legacy_records').fetchone();self.assertEqual(row['original_fields']['ocr_text'],fields[5])
                self.assertEqual(check(row,None)['result'],'evidence_unavailable')
                for table in ['entitlements','recorded_handovers','claims']:
                    self.assertEqual(db.execute('SELECT count(*) n FROM '+table).fetchone()['n'],0)

    def test_original_protocol_matches_actual_pinned_legacy_getter_without_key(self):
        import os,json,subprocess
        from uuid import uuid4
        from backend.tests.support import Harness
        from backend.app.config import ROOT
        from backend.app.commands import execute_command
        from backend.scripts.import_legacy import register_legacy
        from backend.app.services.legacy import check
        from backend.app.services.hasher import compute_receipt_hash
        with Harness() as h:
            manifest=ROOT/'.runtime'/('legacy-test-'+uuid4().hex+'.json')
            deploy=subprocess.run([os.environ['MVP_NODE'],str(ROOT/'contracts/scripts/deploy_legacy_local.js'),str(manifest)],capture_output=True,text=True,timeout=30)
            self.assertEqual(deploy.returncode,0,deploy.stdout)
            fields={'distribution_id':'DFC-2026-OLD1','beneficiary_id':'DFC-2026-BEN1','batch_id':'invented-batch','amount':435.0,'ocr_text':'Invented retained receipt','verification_method':'QR_VOUCHER_PHYSICAL_RECEIPT'}
            digest=compute_receipt_hash(*(fields[k] for k in ['distribution_id','beneficiary_id','batch_id','amount','ocr_text','verification_method']))
            script="const fs=require('fs'),{ethers}=require('ethers');(async()=>{const r=JSON.parse(fs.readFileSync(0,'utf8')),p=new ethers.JsonRpcProvider(process.env.MVP_RPC_URL),s=await p.getSigner(0),c=new ethers.Contract(r.m.address,r.m.abi,s),b=ethers.encodeBytes32String('invented-batch');await(await c.releaseFund(b,ethers.parseEther('1000'),'Invented flood','Invented source')).wait();await(await c.confirmDistribution(b,ethers.encodeBytes32String('DFC-2026-OLD1'),ethers.encodeBytes32String('DFC-2026-BEN1'),ethers.parseEther('435'),r.hash)).wait();p.destroy();})().catch(()=>process.exit(1));"
            actual=subprocess.run([os.environ['MVP_NODE'],'-e',script],input=json.dumps({'m':json.loads(manifest.read_text()),'hash':digest}),capture_output=True,text=True,cwd=ROOT/'contracts',timeout=30)
            self.assertEqual(actual.returncode,0)
            def register(tx):
                row=register_legacy(tx,manifest);self.deployment=row['id'];return [('evaluation_run_id',h.run)]
            execute_command(h.actors['dswd'],'legacy.register','register',{},register)
            with h.connection() as db:
                deployment=db.execute('SELECT * FROM deployments WHERE id=%s',(self.deployment,)).fetchone()
                self.assertEqual(check({'source_table':'distributions','original_fields':fields},deployment)['result'],'match')
                changed=dict(fields,amount=436.0)
                self.assertEqual(check({'source_table':'distributions','original_fields':changed},deployment)['result'],'mismatch')
