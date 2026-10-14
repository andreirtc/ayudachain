"""Opaque lookup only: recipient authorization and handover stay separate commands."""
import re
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import Field
from .main import actor, result
from .actor import require_role
from .commands import DomainError
from .database import connection
from .schemas.mvp import StrictModel
from .services.access import log_access

router = APIRouter(prefix='/api/v1')
REFERENCE = re.compile(r'^(?:ayudachain:transaction:)?([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$', re.IGNORECASE)

class Lookup(StrictModel):
    reference: str = Field(min_length=1, max_length=100)

@router.post('/sessions/{identity}/lookup')
def lookup(identity: UUID, body: Lookup, c=Depends(actor)):
    require_role(c, 'disbursing')
    match = REFERENCE.fullmatch(body.reference.strip())
    if not match:
        raise DomainError(422, 'malformed_transaction_reference')
    transaction = UUID(match.group(1))
    with connection() as db:
        row = db.execute('''SELECT t.id FROM payout_sessions s
            JOIN disasters d ON d.id=s.disaster_id AND d.run_id=s.run_id AND d.office_id=s.office_id
            JOIN session_versions sv ON sv.id=s.current_version_id
            JOIN session_assignments a ON a.session_version_id=sv.id AND a.actor_id=%s
            JOIN session_entries se ON se.session_version_id=sv.id
            JOIN active_session_memberships m ON m.session_id=s.id AND m.entitlement_id=se.entitlement_id
                AND m.entitlement_version_id=se.entitlement_version_id
            JOIN entitlements e ON e.id=se.entitlement_id AND e.current_version_id=se.entitlement_version_id
            JOIN payout_transactions t ON t.entitlement_id=e.id
            WHERE s.id=%s AND t.id=%s AND s.run_id=%s AND s.office_id=%s
            AND e.run_id=s.run_id AND e.office_id=s.office_id AND e.disaster_id=s.disaster_id
            AND t.run_id=s.run_id AND t.office_id=s.office_id
            AND s.business_status IN ('scheduled','open') AND e.business_status!='cancelled'
            LIMIT 1''', (c.actor_id, identity, transaction, c.run_id, c.office_id)).fetchone()
        if not row:
            # Unknown, wrong-session and unassigned references are indistinguishable.
            raise DomainError(404, 'record_unavailable')
    log_access(c, 'open', 'transaction_id', row['id'], ['opaque_transaction_lookup'])
    return result({'transaction_id': row['id']})
