"""Private post-handover answers and human case/challenge histories."""
from datetime import timedelta
from ..actor import require_role,require_independent
from ..commands import DomainError
from .payouts import can_read,assigned
from .evidence import link_evidence
from .commitments import freeze_commitment

ANSWERS={'received_full','received_less','not_received'}


def receipt(tx,transaction):
    t=tx.get('payout_transactions',transaction);e=tx.get('entitlements',t['entitlement_id'])
    r=tx.db.execute('SELECT * FROM recorded_handovers WHERE transaction_id=%s',(transaction,)).fetchone()
    if not r:raise DomainError(409,'recorded_handover_required_before_answer')
    return t,e,r


def may_answer(tx,e,r):
    c=tx.context
    if c.role=='beneficiary' and c.household_id==e['household_id']:return
    if c.role=='disbursing' and r['path']=='assisted':
        if c.actor_id==r['payer_id']:raise DomainError(403,'actual_payer_permanently_barred_from_exit_answer')
        require_independent(c,e['household_id'])
        session=tx.get('session_versions',r['session_version_id']);root=tx.get('payout_sessions',session['session_id'])
        assigned(tx,c,root['current_version_id'],e['household_id'],followup=True);return
    raise DomainError(403,'recipient_or_independent_assisted_checker_required')


def case_event(tx,case,kind,text=None,outcome=None):
    predecessor=tx.db.execute('SELECT id FROM grievance_events WHERE grievance_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(case['id'],)).fetchone()
    event=tx.insert('grievance_events',{'grievance_id':case['id'],'predecessor_id':predecessor['id'] if predecessor else None,'kind':kind,'outcome_version_id':outcome,'report_text':text if kind!='resolve' else None,'resolution':text if kind=='resolve' else None})
    tx.audit('grievance.'+kind,[('grievance_event_id',event['id'])],text if kind=='resolve' else None)
    return event


def adverse(tx,t,e,outcome=None,text=None):
    case=tx.db.execute('SELECT * FROM grievances WHERE transaction_id=%s',(t['id'],)).fetchone()
    if not case:
        case=tx.insert('grievances',{'transaction_id':t['id'],'household_id':e['household_id'],'business_status':'open','revision':0});kind='open'
    elif case['business_status']=='closed':
        tx.update('grievances',case['id'],{'business_status':'open','revision':case['revision']+1});kind='reopen'
    else:kind='report'
    return case_event(tx,case,kind,text,outcome)


def save_answer(tx,t,e,r,answer,supplied):
    previous=tx.get('outcome_versions',t['current_outcome_id']) if t['current_outcome_id'] else None
    row=tx.insert('outcome_versions',{'transaction_id':t['id'],'handover_id':r['id'],'predecessor_id':previous['id'] if previous else None,'answer':answer,'recorder_actor_id':tx.context.actor_id,'supplied_by_household':supplied,'effective_at':tx.now,'late':tx.now>=r['handed_at']+timedelta(hours=72)})
    # Keep cash-facing revision/state unchanged; no private-answer signal to payer.
    tx.update('payout_transactions',t['id'],{'current_outcome_id':row['id']});tx.audit('outcome.record',[('outcome_version_id',row['id'])])
    if answer in {'received_less','not_received'}:adverse(tx,t,e,row['id'])
    hand=tx.db.execute('SELECT * FROM commitments WHERE handover_id=%s',(r['id'],)).fetchone()
    prior=tx.db.execute('SELECT id FROM commitments WHERE outcome_version_id=%s',(previous['id'],)).fetchone() if previous else None
    freeze_commitment(tx,'outcome_version_id',row['id'],'outcome',{'outcome':row},context=hand['public_context'],predecessor=prior['id'] if prior else None,related=hand['id'])
    return [('outcome_version_id',row['id'])]


def answer(tx,transaction,req):
    t,e,r=receipt(tx,transaction);may_answer(tx,e,r)
    if req['answer'] not in ANSWERS:raise DomainError(422,'human_answer_required')
    if tx.context.role!='disbursing' and req.get('expected_latest_id')!=t['current_outcome_id']:raise DomainError(409,'latest_private_answer_changed_refresh')
    return save_answer(tx,t,e,r,req['answer'],True)


def timeout(tx,transaction):
    require_role(tx.context,'system');t,e,r=receipt(tx,transaction)
    if t['current_outcome_id']:raise DomainError(409,'answer_already_recorded')
    if tx.now<r['handed_at']+timedelta(hours=72):raise DomainError(409,'outcome_deadline_not_due')
    return save_answer(tx,t,e,r,'unconfirmed',False)


def report(tx,transaction,req):
    require_role(tx.context,'beneficiary');t=tx.get('payout_transactions',transaction);e=tx.get('entitlements',t['entitlement_id'])
    if tx.context.household_id!=e['household_id']:raise DomainError(403,'own_household_only')
    if not req['text'].strip():raise DomainError(422,'private_report_required')
    event=adverse(tx,t,e,text=req['text'])
    for evidence in req.get('evidence_ids',[]):link_evidence(tx,evidence,'grievance_event_id',event['id'],'private_report')
    return [('grievance_event_id',event['id'])]


def case_action(tx,identity,req):
    require_role(tx.context,'dswd');case=tx.get('grievances',identity);require_independent(tx.context,case['household_id']);tx.revision(case,req['expected_revision'])
    if not req['text'].strip():raise DomainError(422,'human_case_action_text_required')
    action=req['action']
    if action=='review' and case['business_status']=='open':state='under_review'
    elif action=='resolve' and case['business_status']=='under_review':state='closed'
    elif action=='note' and case['business_status'] in {'open','under_review'}:state=case['business_status']
    else:raise DomainError(409,'invalid_private_case_transition')
    event=case_event(tx,case,action,req['text']);tx.update('grievances',case['id'],{'business_status':state,'revision':case['revision']+1})
    return [('grievance_event_id',event['id'])]


def private_view(db,c,transaction):
    t,e=can_read(db,c,transaction)
    if c.role not in {'dswd','auditor'} and not(c.role=='beneficiary' and c.household_id==e['household_id']):raise DomainError(404,'record_unavailable')
    answers=db.execute('SELECT id,predecessor_id,answer,recorder_actor_id,supplied_by_household,effective_at,late FROM outcome_versions WHERE transaction_id=%s ORDER BY created_at,id',(transaction,)).fetchall()
    for row in answers:row['proofs']=db.execute('SELECT c.id,j.state FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id WHERE c.outcome_version_id=%s',(row['id'],)).fetchall()
    case=db.execute('SELECT id,business_status,revision FROM grievances WHERE transaction_id=%s',(transaction,)).fetchone()
    if case:case['history']=db.execute('SELECT id,predecessor_id,kind,outcome_version_id,report_text,resolution,created_at FROM grievance_events WHERE grievance_id=%s ORDER BY created_at,id',(case['id'],)).fetchall()
    return {'transaction_id':transaction,'latest_outcome_id':t['current_outcome_id'],'answers':answers,'grievance':case}


def challenge(tx,entry_id,req):
    require_role(tx.context,'beneficiary')
    from .registry import household
    if not tx.context.household_id:raise DomainError(403,'linked_resident_required')
    h=household(tx.db,tx.context,tx.context.household_id);entry=tx.get('approved_list_entries',entry_id);v=tx.get('approved_list_versions',entry['list_version_id']);head=tx.get('list_heads',v['list_head_id'])
    if h['residence_state']!='confirmed' or head['barangay_id']!=h['declared_barangay_id'] or head['current_published_id']!=v['id']:raise DomainError(403,'current_own_barangay_resident_list_required')
    if not req['text'].strip():raise DomainError(422,'private_challenge_reason_required')
    case=tx.insert('list_challenges',{'list_entry_id':entry['id'],'reporting_household_id':h['id'],'business_status':'open','revision':0})
    event=tx.insert('challenge_events',{'challenge_id':case['id'],'predecessor_id':None,'action':'report','reason':req['text'],'decision_id':None});tx.audit('challenge.report',[('challenge_event_id',event['id'])])
    for file in req.get('evidence_ids',[]):link_evidence(tx,file,'challenge_event_id',event['id'],'private_report')
    return [('challenge_event_id',event['id'])]


def challenge_action(tx,identity,req):
    require_role(tx.context,'dswd');case=tx.get('list_challenges',identity);tx.revision(case,req['expected_revision']);entry=tx.get('approved_list_entries',case['list_entry_id']);e=tx.get('entitlements',entry['entitlement_id']);require_independent(tx.context,e['household_id'])
    if not req['text'].strip():raise DomainError(422,'human_challenge_resolution_required')
    action=req['action']
    if action=='review' and case['business_status']=='open':state='under_review'
    elif action in {'substantiate','dismiss'} and case['business_status']=='under_review':state='closed'
    elif action=='note' and case['business_status'] in {'open','under_review'}:state=case['business_status']
    else:raise DomainError(409,'invalid_challenge_transition')
    prior=tx.db.execute('SELECT id FROM challenge_events WHERE challenge_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(case['id'],)).fetchone()
    event=tx.insert('challenge_events',{'challenge_id':case['id'],'predecessor_id':prior['id'],'action':action,'reason':req['text'],'decision_id':None});tx.update('list_challenges',case['id'],{'business_status':state,'revision':case['revision']+1});tx.audit('challenge.'+action,[('challenge_event_id',event['id'])],req['text'])
    if action=='substantiate' and not tx.db.execute('SELECT 1 FROM recorded_handovers WHERE entitlement_id=%s',(e['id'],)).fetchone():
        from . import claims,checks,entitlements,registry
        c=tx.get('claims',e['claim_id'])
        if c['business_status']!='approved':raise DomainError(409,'only_approved_unpaid_challenge_reversal')
        s=tx.get('claim_submissions',c['current_submission_id']);r=claims.latest_round(tx,c);check=checks.run(tx,s,r['id'],'recheck')
        d=tx.insert('claim_decisions',{'claim_id':c['id'],'submission_id':s['id'],'round_id':r['id'],'predecessor_id':c['current_decision_id'],'check_run_id':check['id'],'action':'reverse_approval','category_id':None,'reason':'Approval reversed following a substantiated pre-handover challenge.','question':None,'confirmed_by':None,'bulk_group_id':None,'challenge_event_id':event['id']})
        tx.update('claims',c['id'],{'business_status':'reversed','current_decision_id':d['id'],'revision':c['revision']+1});tx.update('entitlements',e['id'],{'business_status':'cancelled','hold_reasons':[],'revision':e['revision']+1})
        entitlements.expire_attempts(tx,e['id'],'Human approval reversal before recorded cash');tx.audit('claim.reverse_approval',[('decision_id',d['id']),('entitlement_version_id',e['current_version_id']),('challenge_event_id',event['id'])]);registry.changed(tx)
        listhead=tx.get('list_heads',tx.get('approved_list_versions',entry['list_version_id'])['list_head_id']);entitlements.bump_list(tx,c['disaster_id'],listhead['barangay_id'],'Human approval reversal')
        entitlements.request_list(tx,{'disaster_id':c['disaster_id'],'barangay_id':listhead['barangay_id'],'expected_revision':None})
    return [('challenge_event_id',event['id'])]


def totals(db,run,disaster):
    rows=db.execute('''SELECT r.amount_centavos,r.handed_at,o.answer,e.clock_offset FROM recorded_handovers r JOIN entitlements t ON t.id=r.entitlement_id JOIN evaluation_runs e ON e.id=r.run_id LEFT JOIN payout_transactions p ON p.id=r.transaction_id LEFT JOIN outcome_versions o ON o.id=p.current_outcome_id WHERE r.run_id=%s AND t.disaster_id=%s''',(run,disaster)).fetchall()
    now=db.execute('SELECT clock_timestamp() AS now').fetchone()['now']
    counts={'recorded_handover':len(rows),'received_full':0,'adverse':0,'waiting':0,'unconfirmed':0,'overdue_unconfirmed_pending':0}
    for row in rows:
        key='received_full' if row['answer']=='received_full' else 'adverse' if row['answer'] in {'received_less','not_received'} else 'unconfirmed' if row['answer']=='unconfirmed' else 'waiting' if now+row['clock_offset']<row['handed_at']+timedelta(hours=72) else 'overdue_unconfirmed_pending'
        counts[key]+=1
    return {'counts':counts,'recorded_amount_centavos':str(sum(r['amount_centavos'] for r in rows)),'meaning':'Recorded cash evidence and latest answers are separate; no answer awards another payment.'}
