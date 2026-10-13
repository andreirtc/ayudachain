"""Allowlisted projections; no arbitrary row dumps from read endpoints."""
from .commands import DomainError
from .models.mvp import ACCESS_TARGETS
from psycopg import sql


def authorize_reference(db,context,slot,identity):
    name=ACCESS_TARGETS.get(slot)
    if not name: raise DomainError(404,'record_unavailable')
    if name=='evaluation_runs':
        row=db.execute('SELECT id FROM evaluation_runs WHERE id=%s AND office_id=%s',(identity,context.office_id)).fetchone()
    else:
        row=db.execute(sql.SQL('SELECT * FROM {} WHERE id=%s AND run_id=%s AND office_id=%s').format(sql.Identifier(name)),(identity,context.run_id,context.office_id)).fetchone()
    if not row: raise DomainError(404,'record_unavailable')
    if context.role in {'dswd','auditor','system'}: return row
    if slot=='actor_version_id' and row['actor_id']==context.actor_id: return row
    if slot=='household_id':
        from .services.registry import project
        project(db,context,identity)
        return row
    if slot in {'household_version_id','link_version_id','registry_review_id'}:
        if slot=='household_version_id' and context.role=='disbursing':
            from .services.payouts import can_read
            candidates=db.execute('SELECT t.id FROM payout_transactions t JOIN entitlement_versions v ON v.entitlement_id=t.entitlement_id WHERE v.registry_version_id=%s',(identity,)).fetchall()
            for candidate in candidates:
                try:can_read(db,context,candidate['id']);return row
                except DomainError:pass
        from .services.registry import project
        project(db,context,row['household_id'])
        return row
    if slot=='operation_version_id':return row
    if slot in {'claim_id','submission_id','round_id','response_id','decision_id','check_run_id'}:
        from .routes_claims import project_claim
        if slot=='claim_id':claim_id=identity
        elif slot in {'submission_id','decision_id'}:claim_id=row['claim_id']
        else:
            submission_id=row.get('submission_id')
            if slot=='response_id':submission_id=db.execute('SELECT submission_id FROM claim_rounds WHERE id=%s',(row['round_id'],)).fetchone()['submission_id']
            claim_id=db.execute('SELECT claim_id FROM claim_submissions WHERE id=%s',(submission_id,)).fetchone()['claim_id']
        project_claim(db,context,claim_id)
        return row
    if slot=='snapshot_id' and context.role=='barangay' and row['barangay_id']==context.barangay_id:return row
    if slot=='outcome_version_id':
        from .services.payouts import can_read
        _,e=can_read(db,context,row['transaction_id'])
        if context.role=='beneficiary' and context.household_id==e['household_id']:return row
        if context.role=='disbursing' and row['recorder_actor_id']==context.actor_id:return row # safe acknowledgement only
    if slot=='grievance_event_id':
        case=db.execute('SELECT household_id FROM grievances WHERE id=%s',(row['grievance_id'],)).fetchone()
        if context.role=='beneficiary' and context.household_id==case['household_id']:return row
    if slot=='challenge_event_id':
        case=db.execute('SELECT reporting_household_id FROM list_challenges WHERE id=%s',(row['challenge_id'],)).fetchone()
        if context.role=='beneficiary' and context.household_id==case['reporting_household_id']:return row
    if slot in {'transaction_id','handover_id','attempt_event_id','entitlement_version_id'}:
        from .services.payouts import can_read
        if slot=='transaction_id':transaction=identity
        elif slot=='handover_id':transaction=row['transaction_id']
        elif slot=='attempt_event_id':transaction=db.execute('SELECT transaction_id FROM payout_attempts WHERE id=%s',(row['attempt_id'],)).fetchone()['transaction_id']
        else:transaction=db.execute('SELECT id FROM payout_transactions WHERE entitlement_id=%s',(row['entitlement_id'],)).fetchone()['id']
        can_read(db,context,transaction);return row
    if slot=='evidence_version_id':
        if row['uploaded_by']==context.actor_id and row['purpose'] not in {'identity_photo','identity_document'}:return row
        if row['prepared_for_actor_id']==context.actor_id:return row
        # A helper gets only the original safe acknowledgement, never the file.
        if row['uploaded_by']==context.actor_id:return row
    raise DomainError(404,'record_unavailable')
