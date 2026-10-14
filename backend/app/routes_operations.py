"""Current-record denominators; locked handovers and latest answers stay separate."""
from uuid import UUID
from fastapi import APIRouter,Depends
from .main import actor,result
from .database import connection
from .actor import require_role
from .commands import DomainError
from .services.access import log_access

router=APIRouter(prefix='/api/v1')

@router.get('/operations')
def operations(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor','barangay')
    with connection() as db:
        if not db.execute('SELECT 1 FROM disasters WHERE id=%s AND run_id=%s AND office_id=%s',(disaster_id,c.run_id,c.office_id)).fetchone():raise DomainError(404,'record_unavailable')
        places=db.execute('SELECT id,name FROM barangays WHERE run_id=%s AND office_id=%s AND (%s OR id=%s) ORDER BY name,id',(c.run_id,c.office_id,c.role!='barangay',c.barangay_id)).fetchall()
        rows=[]
        for place in places:
            counts=db.execute('''SELECT count(*) approved,count(r.id) recorded_handover,
                count(*) FILTER(WHERE r.id IS NULL) remaining FROM entitlements e
                JOIN entitlement_versions ev ON ev.id=e.current_version_id
                JOIN household_versions h ON h.id=ev.registry_version_id
                LEFT JOIN recorded_handovers r ON r.entitlement_id=e.id
                WHERE e.run_id=%s AND e.disaster_id=%s AND h.declared_barangay_id=%s AND e.business_status!='cancelled' ''',
                (c.run_id,disaster_id,place['id'])).fetchone()
            row={'barangay_id':place['id'],'name':place['name'],**counts}
            if c.role!='barangay':
                claim_counts=db.execute('''SELECT count(*) claims,count(*) FILTER(WHERE q.business_status='waiting_barangay') waiting_barangay,
                    count(*) FILTER(WHERE q.business_status='awaiting_dswd') awaiting_dswd FROM claims q
                    JOIN claim_submissions s ON s.id=q.current_submission_id JOIN household_versions h ON h.id=s.registry_version_id
                    WHERE q.run_id=%s AND q.disaster_id=%s AND h.declared_barangay_id=%s''',(c.run_id,disaster_id,place['id'])).fetchone()
                details=db.execute('''SELECT count(*) FILTER(WHERE ev.amount_centavos IS NULL) awaiting_amount,
                    count(*) FILTER(WHERE e.business_status='awaiting_publication') awaiting_publication,
                    count(*) FILTER(WHERE e.business_status='available' AND a.entitlement_id IS NULL) ready_scheduling,
                    count(*) FILTER(WHERE a.entitlement_id IS NOT NULL AND r.id IS NULL) assigned,
                    count(*) FILTER(WHERE o.answer='received_full') received_full,
                    count(*) FILTER(WHERE o.answer='received_less') received_less,
                    count(*) FILTER(WHERE o.answer='not_received') not_received,
                    count(*) FILTER(WHERE o.answer='unconfirmed') unconfirmed,
                    count(*) FILTER(WHERE r.id IS NOT NULL AND o.id IS NULL) waiting_answer,
                    coalesce(sum(CASE WHEN r.id IS NOT NULL THEN r.amount_centavos ELSE ev.amount_centavos END),0) known_approved_centavos,
                    coalesce(sum(r.amount_centavos),0) recorded_centavos
                    FROM entitlements e JOIN entitlement_versions ev ON ev.id=e.current_version_id
                    JOIN household_versions h ON h.id=ev.registry_version_id
                    JOIN payout_transactions t ON t.entitlement_id=e.id
                    LEFT JOIN recorded_handovers r ON r.entitlement_id=e.id
                    LEFT JOIN outcome_versions o ON o.id=t.current_outcome_id
                    LEFT JOIN active_session_memberships a ON a.entitlement_id=e.id AND a.entitlement_version_id=e.current_version_id
                    AND EXISTS(SELECT 1 FROM payout_sessions ps JOIN session_entries se ON se.session_version_id=ps.current_version_id
                        WHERE ps.id=a.session_id AND se.entitlement_id=a.entitlement_id AND se.entitlement_version_id=a.entitlement_version_id
                        AND ps.business_status IN ('scheduled','open'))
                    WHERE e.run_id=%s AND e.disaster_id=%s AND h.declared_barangay_id=%s AND e.business_status!='cancelled' ''',
                    (c.run_id,disaster_id,place['id'])).fetchone()
                row.update(claim_counts);row.update(details)
                for key in ['known_approved_centavos','recorded_centavos']:row[key]=str(row[key])
            rows.append(row)
    log_access(c,'browse','disaster_id',disaster_id,['permitted_operations_aggregates'])
    return result({'rows':rows,'denominators':'Current claims and non-cancelled entitlements, one per household/disaster. Handover amounts are locked; answers use latest revision only. Awaiting response is separate from recorded unconfirmed outcomes.'})
