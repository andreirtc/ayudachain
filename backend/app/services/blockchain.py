"""
AyudaChain Centralized Blockchain Service
Interacts with the AyudaChainRegistry smart contract on Polygon Amoy or Local EVM.
Returns observed results and explicit failures; no simulated blockchain evidence.
"""

import os
import json
import subprocess
import re
from typing import Dict, Any

from app import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONTRACTS_DIR = os.path.join(BASE_DIR, "contracts")
SCRIPT_PATH = os.path.join(CONTRACTS_DIR, "scripts", "blockchain_client.js")

class BlockchainService:
    def __init__(self):
        self.rpc_url = config.RPC_URL
        self.private_key = config.PRIVATE_KEY
        self.contract_address = config.CONTRACT_ADDRESS

    def _execute_cli(self, args: list) -> Dict[str, Any]:
        if not self.contract_address:
            return {"success": False, "error": "No contract address configured."}
        env = os.environ.copy()
        env["CHAIN_ID"] = str(config.CHAIN_ID)
        env["POLYGON_RPC_URL"] = self.rpc_url
        env["POLYGON_PRIVATE_KEY"] = self.private_key
        if self.contract_address:
            env["CONTRACT_ADDRESS"] = self.contract_address

        cmd = ["node", SCRIPT_PATH] + args
        try:
            res = subprocess.run(
                cmd,
                cwd=CONTRACTS_DIR,
                env=env,
                capture_output=True,
                text=True,
                timeout=8
            )
            stdout = res.stdout.strip()
            lines = stdout.splitlines()
            for line in reversed(lines):
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    result = json.loads(line)
                    if res.returncode != 0 or type(result.get("success")) is not bool:
                        return {"success": False, "error": "Blockchain process failed or returned an invalid result."}
                    return result
            
            # Preserve failure instead of inventing transaction or receipt evidence.
            return {
                "success": False,
                "error": f"Blockchain process output: {stdout or res.stderr}"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Blockchain transaction confirmation timed out."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        res = self._execute_cli(["status"])
        return {
            "network": config.NETWORK_NAME,
            "chainId": config.CHAIN_ID,
            "contractAddress": self.contract_address,
            **res,
        }

    def release_fund(self, batch_id: str, amount_centavos: int, calamity_name: str, source_agency: str) -> Dict[str, Any]:
        from app.services.payout_anchors import legacy_signer
        with legacy_signer() as available:
            return self._execute_cli(["releaseFund", batch_id, str(amount_centavos), calamity_name, source_agency]) if available else {"success": False, "error_code": "SIGNER_BUSY"}

    def allocate_fund(self, batch_id: str, allocation_id: str, barangay_id: str, amount_centavos: int) -> Dict[str, Any]:
        from app.services.payout_anchors import legacy_signer
        with legacy_signer() as available:
            return self._execute_cli(["allocateFund", batch_id, allocation_id, barangay_id, str(amount_centavos)]) if available else {"success": False, "error_code": "SIGNER_BUSY"}

    def confirm_distribution(
        self,
        batch_id: str,
        allocation_id: str,
        distribution_id: str,
        beneficiary_id: str,
        amount_centavos: int,
        receipt_hash: str
    ) -> Dict[str, Any]:
        from app.services.payout_anchors import legacy_signer
        with legacy_signer() as available:
            if not available:
                return {"success": False, "error_code": "SIGNER_BUSY"}
            return self._execute_cli([
                "confirmDistribution", batch_id, allocation_id, distribution_id,
                beneficiary_id, str(amount_centavos), receipt_hash
            ])

    def verify_receipt(self, distribution_id: str, receipt_hash: str) -> Dict[str, Any]:
        return self._execute_cli(["verifyReceipt", distribution_id, receipt_hash])

    def payout_anchor(self, action, payload, raw_transaction=None, pin=None, candidate_tx_hash=None):
        """Signed envelopes travel over stdin, never in process arguments or logs."""
        env = os.environ.copy()
        env.update(CHAIN_ID=str(config.CHAIN_ID), POLYGON_RPC_URL=self.rpc_url,
                   POLYGON_PRIVATE_KEY=self.private_key or "", CONTRACT_ADDRESS=self.contract_address or "")
        try:
            result = subprocess.run(
                ["node", os.path.join(CONTRACTS_DIR, "scripts", "payout_anchor.js"), action],
                input=json.dumps({"payload": payload, "raw_transaction": raw_transaction, "pin": pin, "candidate_tx_hash": candidate_tx_hash}),
                cwd=CONTRACTS_DIR, env=env, capture_output=True, text=True, timeout=8,
            )
            if result.returncode != 0:
                return {"success": False, "error_code": "RPC_UNAVAILABLE"}
            return json.loads(result.stdout.strip())
        except (subprocess.SubprocessError, OSError, ValueError):
            return {"success": False, "error_code": "RPC_UNAVAILABLE"}


def is_hex_hash(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"0x[0-9a-fA-F]{64}", value) is not None


def confirmed_transaction_hash(result: Dict[str, Any]):
    """Only persist a valid transaction hash from a successful CLI confirmation."""
    value = result.get("txHash")
    return value if result.get("success") is True and is_hex_hash(value) else None


blockchain_service = BlockchainService()
