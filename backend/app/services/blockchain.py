"""Legacy transport adapter. Successful verification requires an actual chain read.

The original receipt canonicalization and contract interface are unchanged.
"""
import os
import json
import subprocess
from pathlib import Path

SCRIPT_PATH=Path(__file__).resolve().parents[3]/'contracts/scripts/blockchain_client.js'


class BlockchainService:
    def __init__(self):
        self.rpc_url=os.getenv('POLYGON_RPC_URL','http://127.0.0.1:8545')
        self.private_key=os.getenv('POLYGON_PRIVATE_KEY','')
        self.contract_address=os.getenv('CONTRACT_ADDRESS','')

    def _execute_cli(self,args):
        env=os.environ.copy()
        env['POLYGON_RPC_URL']=self.rpc_url
        if self.private_key:env['POLYGON_PRIVATE_KEY']=self.private_key
        if self.contract_address:env['CONTRACT_ADDRESS']=self.contract_address
        try:
            run=subprocess.run([env.get('MVP_NODE','node'),str(SCRIPT_PATH),*args],env=env,cwd=SCRIPT_PATH.parents[1],capture_output=True,text=True,timeout=12)
            result=json.loads(run.stdout.strip().splitlines()[-1])
            if not result.get('success'):return {'success':False,'error':'chain_unreachable','matched':False}
            return result
        except (OSError,subprocess.SubprocessError,ValueError,IndexError):
            return {'success':False,'error':'chain_unreachable','matched':False}

    def get_status(self):return self._execute_cli(['status'])
    def release_fund(self,batch_id,amount,calamity_name,source_agency):
        return self._execute_cli(['releaseFund',batch_id,str(amount),calamity_name,source_agency])
    def allocate_fund(self,batch_id,allocation_id,barangay_id,amount):
        return self._execute_cli(['allocateFund',batch_id,allocation_id,barangay_id,str(amount)])
    def confirm_distribution(self,batch_id,distribution_id,beneficiary_id,amount,receipt_hash):
        return self._execute_cli(['confirmDistribution',batch_id,distribution_id,beneficiary_id,str(amount),receipt_hash])
    def verify_receipt(self,distribution_id,receipt_hash):
        result=self._execute_cli(['verifyReceipt',distribution_id,receipt_hash])
        if not result.get('success'):return dict(result,matched=False)
        if not result.get('exists'):return dict(result,matched=False,result='required_anchor_absent')
        return result


blockchain_service=BlockchainService()
