"""Frozen submissions, append-only response threads and once-only routing."""
from datetime import timedelta
from uuid import uuid4
from ..actor import require_role,resolve_identity
from ..commands import DomainError,RecordedRefusal,Transaction
from . import registry,checks
from .evidence import link_evidence
from .commitments import freeze_commitment,document_commitment


def latest_round(tx,claim):
    return tx.db.execute('SELECT * FROM claim_rounds WHERE submission_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(claim['current_submission_id'],)).fetchone()


def eligible_endorsers(tx,identity,barangay):
    candidates=tx.db.execute("SELECT a.id FROM actors a JOIN actor_versions v ON v.id=a.current_version_id WHERE a.run_id=%s AND a.role='barangay' AND v.status='active' AND v.barangay_id=%s",(tx.context.run_id,barangay)).fetchall()
    eligible=[]
    for actor in candidates:
        try:registry.require_endorser(tx.db,resolve_identity(tx.db,actor['id']),identity);eligible.append(actor['id'])
        except DomainError:pass
    return candidates,eligible


def submit(tx,req):
    require_role(tx.context,'beneficiary')
    h=registry.household(tx.db,tx.context,req['household_id'])
    if tx.context.household_id!=h['id']:raise DomainError(403,'own_household_only')
    operation=tx.db.execute("SELECT o.*,v.response_hours FROM claim_operations o JOIN operation_versions v ON v.id=o.current_version_id WHERE o.disaster_id=%s AND o.run_id=%s AND o.business_status='open'",(req['disaster_id'],tx.context.run_id)).fetchone()
    if not operation or not tx.db.execute('SELECT 1 FROM operation_barangays WHERE operation_version_id=%s AND barangay_id=%s',(operation['current_version_id'],h['declared_barangay_id'])).fetchone():raise DomainError(409,'intake_closed_or_not_covered')
    tx.get('damage_categories',req['stated_category_id'])
    existing=tx.db.execute('SELECT * FROM claims WHERE household_id=%s AND disaster_id=%s',(h['id'],req['disaster_id'])).fetchone()
    predecessor=None;identity=uuid4();submission_id=uuid4()
    if existing:
        if existing['business_status']!='declined' or existing['resubmissions'] or not (req.get('new_information') or '').strip():
            round=latest_round(tx,existing);checks.run(tx,tx.get('claim_submissions',existing['current_submission_id']),round['id'],'duplicate_attempt')
            tx.audit('claim.duplicate_refused',[('submission_id',existing['current_submission_id'])])
            raise RecordedRefusal(409,'existing_claim_use_current_thread',[('claim_id',existing['id'])])
        identity=existing['id'];predecessor=existing['current_submission_id']
        tx.update('claims',identity,{'current_submission_id':submission_id,'business_status':'waiting_barangay','resubmissions':1,'revision':existing['revision']+1})
    else:tx.insert('claims',{'id':identity,'household_id':h['id'],'disaster_id':req['disaster_id'],'operation_id':operation['id'],'current_submission_id':submission_id,'current_decision_id':None,'business_status':'waiting_barangay','revision':0,'resubmissions':0})
    link=tx.db.execute('SELECT link_version_id FROM household_links WHERE household_id=%s',(h['id'],)).fetchone()
    s=tx.insert('claim_submissions',{'id':submission_id,'claim_id':identity,'registry_version_id':h['current_version_id'],'link_version_id':link['link_version_id'] if link else None,'predecessor_id':predecessor,'stated_category_id':req['stated_category_id'],'damage_description':req['damage_description'],'new_information':req.get('new_information'),'submitted_at':tx.now})
    for e in req.get('evidence_ids',[]):link_evidence(tx,e,'submission_id',s['id'],'damage')
    r=tx.insert('claim_rounds',{'submission_id':s['id'],'referral_decision_id':None,'response_hours':operation['response_hours'],'deadline_at':tx.now+timedelta(hours=operation['response_hours']),'state':'waiting','route_kind':None,'primary_snapshot_id':None,'routed_response_id':None,'revision':0})
    tx.audit('claim.submit',[('submission_id',s['id']),('round_id',r['id'])]);registry.changed(tx)
    checks.run(tx,s,r['id'],'intake')
    candidates,eligible=eligible_endorsers(tx,h['id'],h['declared_barangay_id'])
    if len(candidates)<2 or not eligible:fallback(tx,r['id'],staffing=True)
    return [('claim_id',identity),('submission_id',s['id'])]


def respond(tx,round_id,req):
    require_role(tx.context,'barangay');r=tx.get('claim_rounds',round_id);s=tx.get('claim_submissions',r['submission_id']);claim=tx.get('claims',s['claim_id'])
    if claim['current_submission_id']!=s['id'] or claim['business_status'] in {'approved','declined','reversed'} or r['state']=='closed':raise DomainError(409,'thread_final')
    # Frozen submission's barangay determines thread scope, not a later profile move.
    frozen=tx.get('household_versions',s['registry_version_id'])
    if tx.context.barangay_id!=frozen['declared_barangay_id']:raise DomainError(403,'own_barangay_only')
    registry.require_endorser(tx.db,tx.context,claim['household_id'])
    candidates,_=eligible_endorsers(tx,claim['household_id'],frozen['declared_barangay_id'])
    if len(candidates)<2:raise DomainError(409,'fewer_than_two_active_officers')
    kind=req['kind']
    if kind=='endorse' and not (req.get('residence_attested') and req.get('affected_attested')):raise DomainError(422,'fixed_attestation_required')
    if (kind!='endorse' or req['category_disputed']) and not (req.get('reason') or '').strip():raise DomainError(422,'response_reason_required')
    parent=req.get('parent_response_id')
    if kind in {'withdraw','reverse'}:
        old=tx.get('claim_responses',parent) if parent else None
        if not old or old['actor_id']!=tx.context.actor_id or old['round_id']!=r['id']:raise DomainError(403,'own_response_reply_required')
    if r['referral_decision_id'] and kind!='referral_answer':raise DomainError(422,'referral_answer_required')
    if req.get('category_opinion_id'):tx.get('damage_categories',req['category_opinion_id'])
    row=tx.insert('claim_responses',{'round_id':r['id'],'parent_response_id':parent,'actor_id':tx.context.actor_id,**{k:req.get(k) for k in ['kind','residence_attested','affected_attested','category_opinion_id','category_disputed','related_declared','reason']}})
    for e in req.get('evidence_ids',[]):link_evidence(tx,e,'response_id',row['id'],'damage')
    tx.audit('claim.respond',[('response_id',row['id'])],req.get('reason'));registry.changed(tx)
    if kind=='endorse' and frozen['residence_state']=='unconfirmed':
        # A fixed residence attestation creates a new current registry version.
        current=tx.get('households',claim['household_id']);v=tx.get('household_versions',current['current_version_id'])
        if v['residence_state']=='unconfirmed':
            review=uuid4();version=uuid4()
            tx.insert('registry_reviews',{'id':review,'household_id':current['id'],'prior_version_id':v['id'],'result_version_id':version,'action':'residence_confirm','reason':'Fixed barangay residence attestation','accepted_id_type':None,'person_photo_compared':None,'prior_link_id':None,'result_link_id':None})
            tx.insert('household_versions',{k:v[k] for k in ['household_id','declared_barangay_id','address','zone','identity_state','id_type','id_number','head_photo_evidence_id','id_evidence_id','assister_id']}|{'id':version,'predecessor_id':v['id'],'residence_state':'confirmed','registry_review_id':review})
            for m in tx.db.execute('SELECT * FROM member_versions WHERE household_version_id=%s',(v['id'],)).fetchall():tx.insert('member_versions',{k:m[k] for k in ['member_id','name','birth_date','relationship','is_head']}|{'household_version_id':version})
            tx.update('households',current['id'],{'current_version_id':version,'revision':current['revision']+1});tx.audit('registry.attested',[('registry_review_id',review),('household_version_id',version),('response_id',row['id'])])
    if r['referral_decision_id'] and r['state']=='waiting':
        tx.update('claim_rounds',r['id'],{'state':'routed','route_kind':'referral_answer','routed_response_id':row['id'],'revision':r['revision']+1})
        tx.update('claims',claim['id'],{'business_status':'awaiting_dswd','revision':claim['revision']+1});tx.audit('claim.referral_answer',[('round_id',r['id']),('response_id',row['id'])])
    if r['state']=='routed' or r['referral_decision_id']:checks.run(tx,s,r['id'],'recheck')
    return [('response_id',row['id'])]


def snapshot(tx,rounds,disaster,barangay,kind,resolution=None,reason=None):
    if kind=='system_fallback':
        system=tx.db.execute("SELECT id FROM actors WHERE run_id=%s AND role='system'",(tx.context.run_id,)).fetchone()['id']
        tx=Transaction(tx.db,resolve_identity(tx.db,system,system=True),tx.request_id)
    snap=tx.insert('submission_snapshots',{'disaster_id':disaster,'barangay_id':barangay,'kind':kind,'sender_id':tx.context.actor_id if kind=='barangay_submission' else None,'resolution_evidence_id':resolution,'fallback_reason':reason,'fallback_details':{'reason':reason,'round_count':len(rounds)} if reason else {},'submitted_at':tx.now})
    payload={'snapshot':dict(snap),'items':[]};files=[]
    if resolution:files.append(link_evidence(tx,resolution,'snapshot_id',snap['id'],'council_resolution'))
    for r in rounds:
        s=tx.get('claim_submissions',r['submission_id']);c=tx.get('claims',s['claim_id']);v=tx.get('household_versions',s['registry_version_id'])
        tx.insert('snapshot_items',{'snapshot_id':snap['id'],'round_id':r['id'],'submission_id':s['id'],'registry_version_id':v['id']})
        responses=tx.db.execute('SELECT * FROM claim_responses WHERE round_id=%s ORDER BY created_at,id',(r['id'],)).fetchall()
        for response in responses:tx.insert('snapshot_response_refs',{'snapshot_id':snap['id'],'response_id':response['id']})
        payload['items'].append({'submission':dict(s),'registry':dict(v),'members':tx.db.execute('SELECT * FROM member_versions WHERE household_version_id=%s ORDER BY member_id',(v['id'],)).fetchall(),'responses':responses})
        files.extend(tx.db.execute('SELECT e.* FROM evidence_versions e JOIN evidence_links l ON l.evidence_version_id=e.id WHERE l.submission_id=%s OR l.response_id=ANY(%s)',(s['id'],[v['id'] for v in responses])).fetchall())
        tx.update('claim_rounds',r['id'],{'state':'routed','route_kind':kind,'primary_snapshot_id':snap['id'],'revision':r['revision']+1})
        tx.update('claims',c['id'],{'business_status':'awaiting_dswd','revision':c['revision']+1});tx.audit('claim.route',[('round_id',r['id']),('snapshot_id',snap['id'])]);checks.run(tx,s,r['id'],'review')
    tx.audit('claim.snapshot',[('snapshot_id',snap['id'])])
    files=list({f['id']:f for f in files}.values())
    for f in files:document_commitment(tx,f)
    freeze_commitment(tx,'snapshot_id',snap['id'],kind,payload,evidence=files)
    return snap


def send(tx,req):
    require_role(tx.context,'barangay')
    if tx.context.position!='Punong Barangay' or tx.context.barangay_id!=req['barangay_id']:raise DomainError(403,'active_punong_required')
    if not req['round_ids']:raise DomainError(422,'responded_rounds_required')
    rounds=[]
    for identity in set(req['round_ids']):
        r=tx.get('claim_rounds',identity);s=tx.get('claim_submissions',r['submission_id']);c=tx.get('claims',s['claim_id']);v=tx.get('household_versions',s['registry_version_id'])
        if r['state']!='waiting' or r['referral_decision_id'] or c['disaster_id']!=req['disaster_id'] or v['declared_barangay_id']!=req['barangay_id']:raise DomainError(409,'round_already_routed_or_scope_changed')
        registry.require_endorser(tx.db,tx.context,c['household_id'])
        if not tx.db.execute('SELECT 1 FROM claim_responses WHERE round_id=%s',(r['id'],)).fetchone():raise DomainError(422,'response_required_for_signed_submission')
        rounds.append(r)
    snap=snapshot(tx,rounds,req['disaster_id'],req['barangay_id'],'barangay_submission',req['resolution_evidence_id'])
    return [('snapshot_id',snap['id'])]


def fallback(tx,round_id,*,staffing=False):
    r=tx.get('claim_rounds',round_id);s=tx.get('claim_submissions',r['submission_id']);c=tx.get('claims',s['claim_id']);v=tx.get('household_versions',s['registry_version_id'])
    if r['state']!='waiting':raise DomainError(409,'round_already_routed')
    if not staffing and tx.now<r['deadline_at']:raise DomainError(409,'deadline_not_due')
    if r['referral_decision_id']:
        tx.update('claim_rounds',r['id'],{'state':'routed','route_kind':'referral_timeout','revision':r['revision']+1});tx.update('claims',c['id'],{'business_status':'awaiting_dswd','revision':c['revision']+1});tx.audit('claim.referral_timeout',[('round_id',r['id'])],reason='No answer before fixed referral deadline');checks.run(tx,s,r['id'],'recheck');return [('round_id',r['id'])]
    reason='no_eligible_endorser' if staffing else 'no_barangay_submission' if tx.db.execute('SELECT 1 FROM claim_responses WHERE round_id=%s',(r['id'],)).fetchone() else 'no_barangay_response'
    snap=snapshot(tx,[r],c['disaster_id'],v['declared_barangay_id'],'system_fallback',reason=reason)
    return [('snapshot_id',snap['id'])]
