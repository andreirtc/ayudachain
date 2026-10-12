"""Read-only business history. Inspection selectors use the separate DB role."""
from psycopg import sql
from ..database import connection
from ..actor import require_role
from ..commands import DomainError
from ..projections import authorize_reference
from ..models.mvp import ACCESS_TARGETS
from .access import log_access


def timeline(c,slot,identity):
    require_role(c,'dswd','auditor')
    if slot not in ACCESS_TARGETS:raise DomainError(404,'record_unavailable')
    with connection() as db:
        authorize_reference(db,c,slot,identity)
        if slot=='evaluation_run_id':
            rows=db.execute('SELECT id,sequence,actor_id,action,reason,effective_at,safe_details FROM audit_events WHERE run_id=%s ORDER BY sequence',(c.run_id,)).fetchall()
        else:
            rows=db.execute(sql.SQL('SELECT a.id,a.sequence,a.actor_id,a.action,a.reason,a.effective_at,a.safe_details FROM audit_events a JOIN audit_targets t ON t.audit_event_id=a.id WHERE t.{}=%s AND a.run_id=%s ORDER BY a.sequence').format(sql.Identifier(slot)),(identity,c.run_id)).fetchall()
        for row in rows:
            targets=db.execute('SELECT * FROM audit_targets WHERE audit_event_id=%s',(row['id'],)).fetchall()
            row['exact_versions']=[{'type':key,'id':target[key]} for target in targets for key in ACCESS_TARGETS if target.get(key)]
    log_access(c,'open',slot,identity,['append_only_business_history','exact_version_references'])
    return rows


def inspection_history(c):
    require_role(c,'auditor')
    log_access(c,'browse','evaluation_run_id',c.run_id,['own_private_inspection_history'])
    with connection(purpose='inspection') as db:
        rows=db.execute('SELECT id,action,fields_opened,checked_at,integrity_result FROM auditor_access_events WHERE run_id=%s AND auditor_actor_id=%s ORDER BY checked_at,id',(c.run_id,c.actor_id)).fetchall()
        for row in rows:
            refs=db.execute('SELECT * FROM auditor_access_targets WHERE access_event_id=%s',(row['id'],)).fetchall()
            row['targets']=[{'type':key,'id':ref[key]} for ref in refs for key in ACCESS_TARGETS if ref.get(key)]
    return rows


def overview(c,disaster):
    require_role(c,'dswd','auditor')
    with connection() as db:
        authorize_reference(db,c,'disaster_id',disaster)
        def query(statement):return db.execute(statement,(c.run_id,disaster)).fetchall()
        claims=query('SELECT id,business_status FROM claims WHERE run_id=%s AND disaster_id=%s')
        ent=query('SELECT e.id,e.business_status,e.hold_reasons,v.amount_centavos FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id WHERE e.run_id=%s AND e.disaster_id=%s')
        snapshots=query('SELECT id,kind,fallback_reason,submitted_at FROM submission_snapshots WHERE run_id=%s AND disaster_id=%s')
        lists=query("SELECT v.id,v.business_status FROM approved_list_versions v JOIN list_heads h ON h.id=v.list_head_id WHERE v.run_id=%s AND h.disaster_id=%s AND v.business_status IN ('pending_publication','stale')")
        decisions=query("SELECT d.id,d.action,d.bulk_group_id,d.created_by FROM claim_decisions d JOIN claims c ON c.id=d.claim_id WHERE d.run_id=%s AND c.disaster_id=%s AND (d.bulk_group_id IS NOT NULL OR d.action='category_change')")
        attempts=query("SELECT p.id,p.path,p.business_status FROM payout_attempts p JOIN payout_transactions t ON t.id=p.transaction_id JOIN entitlements e ON e.id=t.entitlement_id WHERE p.run_id=%s AND e.disaster_id=%s")
        differences=query('SELECT p.id,p.handover_id,p.hypothetical_centavos,p.locked_centavos,p.delta_centavos FROM paid_difference_events p JOIN recorded_handovers r ON r.id=p.handover_id JOIN entitlements e ON e.id=r.entitlement_id WHERE p.run_id=%s AND e.disaster_id=%s')
        input_history=query('SELECT id,predecessor_id,mode,reason FROM amount_input_versions WHERE run_id=%s AND disaster_id=%s')
        cases=query('SELECT g.id,g.transaction_id,g.business_status FROM grievances g JOIN payout_transactions t ON t.id=g.transaction_id JOIN entitlements e ON e.id=t.entitlement_id WHERE g.run_id=%s AND e.disaster_id=%s')
        challenges=query('SELECT c.id,c.business_status,c.list_entry_id,r.id handover_id FROM list_challenges c JOIN approved_list_entries l ON l.id=c.list_entry_id JOIN entitlements e ON e.id=l.entitlement_id LEFT JOIN recorded_handovers r ON r.entitlement_id=e.id WHERE c.run_id=%s AND e.disaster_id=%s')
        # Use the recorded response's business time, rather than wall-clock row
        # creation or today's offset. Other audit targets must not multiply rows.
        responses=query("""SELECT r.actor_id,r.kind,r.category_opinion_id,r.related_declared,s.stated_category_id,
            EXISTS(SELECT 1 FROM audit_targets t JOIN audit_events a ON a.id=t.audit_event_id
                WHERE t.response_id=r.id AND a.action='claim.respond'
                AND a.run_id=r.run_id AND a.office_id=r.office_id AND a.effective_at>q.deadline_at) after_deadline
            FROM claim_responses r JOIN claim_rounds q ON q.id=r.round_id
            JOIN claim_submissions s ON s.id=q.submission_id JOIN claims c ON c.id=s.claim_id
            WHERE r.run_id=%s AND c.disaster_id=%s""")
        assisted=query('SELECT s.id,v.assister_id FROM claim_submissions s JOIN household_versions v ON v.id=s.registry_version_id JOIN claims c ON c.id=s.claim_id WHERE s.run_id=%s AND c.disaster_id=%s AND v.assister_id IS NOT NULL')
        from .funds import totals
        financial=totals(db,c.run_id,disaster)
        from .outcomes import totals as outcome_totals
        outcomes=outcome_totals(db,c.run_id,disaster)
        staff=db.execute("SELECT a.id,a.display_name FROM actors a WHERE a.run_id=%s AND a.role='barangay' ORDER BY a.display_name",(c.run_id,)).fetchall()
        for officer in staff:
            rows=[r for r in responses if r['actor_id']==officer['id']]
            officer.update(response_count=len(rows),endorsements=sum(r['kind']=='endorse' for r in rows),relative_declarations=sum(r['related_declared'] for r in rows),category_differences=sum(r['category_opinion_id'] is not None and r['category_opinion_id']!=r['stated_category_id'] for r in rows),after_deadline=sum(r['after_deadline'] for r in rows),assisted_submissions=sum(r['assister_id']==officer['id'] for r in assisted),denominator='recorded responses; assisted count uses submitted registry versions')
    log_access(c,'browse','disaster_id',disaster,['workflow_exceptions','private_case_and_outcome_totals','officer_response_denominators'])
    return {'interpretation':'Review flags and evidence; not a fraud finding. No automatic decision.',
        'population':{'claims':len(claims),'entitlements':len(ent),'attempts':len(attempts),'responses':len(responses)},
        'denominators':{'outcomes':'recorded handovers, partitioned by latest answer and elapsed business time','officers':'actual append-only responses and submitted assisted registry versions','financial':'signed fund ledger and distinct current approved or locked paid entitlements'},
        'financial':financial,'outcomes':outcomes,'officers':staff,'exceptions':{'fallback_snapshots':[r for r in snapshots if r['kind']=='system_fallback'],'pending_or_stale_publication':lists,'bulk_or_category_decisions':decisions,'changed_inputs':[r for r in input_history if r['predecessor_id']], 'stopped_attempts':[r for r in attempts if r['business_status']=='stopped'],'assisted_attempts':[r for r in attempts if r['path']=='assisted'],'stale_authorizations':[r for r in attempts if r['business_status']=='expired'],'held_entitlements':[r for r in ent if r['hold_reasons']], 'paid_differences':differences,'grievances':cases,'resident_challenges':challenges}}
