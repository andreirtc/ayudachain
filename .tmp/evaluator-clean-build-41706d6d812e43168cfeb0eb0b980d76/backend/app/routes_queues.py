"""Bounded, server-filtered task projections. Search terms never enter URLs."""
from uuid import UUID
from typing import Literal
from fastapi import APIRouter, Depends
from pydantic import Field
from .main import actor, result
from .schemas.mvp import StrictModel
from .database import connection
from .commands import DomainError
from .actor import require_role
from .services.access import log_access

router=APIRouter(prefix='/api/v1')
KINDS={'beneficiary':['registry','claims','entitlements','transactions'],
    'barangay':['registry','claims'],'dswd':['registry','claims','entitlements','transactions','proofs'],
    'auditor':['registry','claims','entitlements','transactions','proofs'],'disbursing':['transactions']}
STATES={'registry':['unconfirmed','confirmed','disputed'],
    'claims':['waiting_barangay','awaiting_dswd','flagged','approved','declined','reversed'],
    'entitlements':['awaiting_amount','awaiting_publication','available','assigned','held','handed_over'],
    'transactions':['available','assigned','held','handed_over','received_full','received_less','not_received','unconfirmed','waiting_answer'],
    'proofs':['pending','prepared','submitted','uncertain','retry_wait','mined_unapplied','confirmed','conflict','deployment_lost']}

class QueueRequest(StrictModel):
    kind:Literal['registry','claims','entitlements','transactions','proofs']
    disaster_id:UUID
    query:str=Field(default='',max_length=200)
    state:str=Field(default='all',max_length=50)
    barangay_id:UUID|None=None
    offset:int=Field(default=0,ge=0,le=100000)
    limit:int=Field(default=25,ge=1,le=50)


def queue_query(c,b):
    if b.kind not in KINDS[c.role]:raise DomainError(403,'queue_not_permitted')
    states=STATES[b.kind]
    if c.role not in {'dswd','auditor'} and b.kind=='claims':states=[s for s in states if s!='flagged']
    if c.role not in {'dswd','auditor'} and b.kind=='transactions':states=states[:4]
    if b.state!='all' and b.state not in states:raise DomainError(422,'queue_filter_not_permitted')
    args=[c.run_id,c.office_id]
    if b.kind=='proofs':
        # Proof catalogue is office-wide; committed kinds carry different context types.
        base='''SELECT c.id,c.kind name,c.id::text reference,NULL::uuid barangay_id,'' zone,
            j.state state,'audit' section,'proof' target FROM commitments c
            JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id
            WHERE c.run_id=%s AND c.office_id=%s'''
    else:
        root={'registry':'h','claims':'q','entitlements':'e','transactions':'t'}[b.kind]
        if b.kind=='registry':
            base="""SELECT h.id,m.name,h.display_id reference,v.declared_barangay_id barangay_id,v.zone,
                v.residence_state state,'registry' section,'household' target FROM households h
                JOIN household_versions v ON v.id=h.current_version_id"""
        elif b.kind=='claims':
            base="""SELECT q.id,m.name,h.display_id reference,v.declared_barangay_id barangay_id,v.zone,
                q.business_status state,'claims' section,'claim' target,
                EXISTS(SELECT 1 FROM check_flags f WHERE f.check_run_id=(SELECT id FROM check_runs
                    WHERE submission_id=q.current_submission_id ORDER BY created_at DESC,id DESC LIMIT 1)) flagged
                FROM claims q JOIN claim_submissions s ON s.id=q.current_submission_id
                JOIN households h ON h.id=q.household_id JOIN household_versions v ON v.id=s.registry_version_id"""
        else:
            base="""SELECT t.id,m.name,h.display_id reference,v.declared_barangay_id barangay_id,v.zone,
                e.business_status state,'payouts' section,'transaction' target,
                CASE WHEN r.id IS NOT NULL THEN r.amount_centavos ELSE ev.amount_centavos END amount_centavos,
                EXISTS(SELECT 1 FROM active_session_memberships a JOIN payout_sessions ps ON ps.id=a.session_id
                    JOIN session_entries se ON se.session_version_id=ps.current_version_id AND se.entitlement_id=a.entitlement_id
                    AND se.entitlement_version_id=a.entitlement_version_id WHERE a.entitlement_id=e.id
                    AND a.entitlement_version_id=e.current_version_id AND ps.business_status IN ('scheduled','open')) assigned"""
            if c.role=='disbursing':base=base.replace('v.zone,',"'' zone,")
            if c.role in {'dswd','auditor'}:
                base+=",o.answer outcome,r.id IS NOT NULL has_handover"
            base+=''' FROM payout_transactions t JOIN entitlements e ON e.id=t.entitlement_id
                JOIN entitlement_versions ev ON ev.id=e.current_version_id JOIN households h ON h.id=e.household_id
                JOIN household_versions v ON v.id=ev.registry_version_id
                LEFT JOIN recorded_handovers r ON r.entitlement_id=e.id'''
            if c.role in {'dswd','auditor'}:base+=' LEFT JOIN outcome_versions o ON o.id=t.current_outcome_id'
        base+=' JOIN member_versions m ON m.household_version_id=v.id AND m.is_head'
        base+=f' WHERE {root}.run_id=%s AND {root}.office_id=%s'
        if b.kind!='registry':base+=' AND '+('q' if b.kind=='claims' else 'e')+'.disaster_id=%s';args.append(b.disaster_id)
        if b.kind in {'entitlements','transactions'}:base+=" AND e.business_status!='cancelled'"
        if c.role=='beneficiary':base+=' AND h.id=%s';args.append(c.household_id)
        if c.role=='barangay':base+=' AND v.declared_barangay_id=%s';args.append(c.barangay_id)
        if c.role=='disbursing':
            base+=''' AND (EXISTS(SELECT 1 FROM session_entries se JOIN payout_sessions ps ON ps.current_version_id=se.session_version_id
                JOIN session_assignments sa ON sa.session_version_id=ps.current_version_id
                WHERE se.entitlement_id=e.id AND sa.actor_id=%s) OR r.payer_id=%s)''';args.extend([c.actor_id,c.actor_id])
    where=[]
    if b.barangay_id:where.append('barangay_id=%s');args.append(b.barangay_id)
    if b.query.strip():
        where.append("(name ILIKE %s ESCAPE '\\' OR reference ILIKE %s ESCAPE '\\' OR zone ILIKE %s ESCAPE '\\')")
        term='%'+b.query.strip().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%';args.extend([term]*3)
    if b.state!='all':
        if b.state=='flagged':where.append('flagged')
        elif b.state=='assigned':where.append("assigned AND state!='handed_over'")
        elif b.state=='available' and b.kind in {'transactions','entitlements'}:where.append("state='available' AND NOT assigned")
        elif b.state in {'received_full','received_less','not_received','unconfirmed'}:where.append('outcome=%s');args.append(b.state)
        elif b.state=='waiting_answer':where.append('has_handover AND outcome IS NULL')
        else:where.append('state=%s');args.append(b.state)
    filtered='SELECT * FROM ('+base+') scoped'+(' WHERE '+' AND '.join(where) if where else '')
    return filtered,args,states


@router.post('/queues/search')
def search(body:QueueRequest,c=Depends(actor)):
    require_role(c,*KINDS)
    with connection() as db:
        if not db.execute('SELECT 1 FROM disasters WHERE id=%s AND run_id=%s AND office_id=%s',(body.disaster_id,c.run_id,c.office_id)).fetchone():raise DomainError(404,'record_unavailable')
        query,args,states=queue_query(c,body)
        total=db.execute('SELECT count(*) n FROM ('+query+') counted',args).fetchone()['n']
        rows=db.execute(query+' ORDER BY name,id LIMIT %s OFFSET %s',(*args,body.limit,body.offset)).fetchall()
        for row in rows:
            if 'amount_centavos' in row and row['amount_centavos'] is not None:row['amount_centavos']=str(row['amount_centavos'])
            if c.role not in {'dswd','auditor'}:row.pop('flagged',None)
            if c.role=='disbursing':row.pop('zone',None)
    log_access(c,'browse','disaster_id',body.disaster_id,['filtered_task_queue'])
    return result({'rows':rows,'total':total,'offset':body.offset,'limit':body.limit,'kinds':KINDS[c.role],'states':states,
        'scope':'Field Office evidence' if body.kind=='proofs' else 'selected actor permitted records'})
