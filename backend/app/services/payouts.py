"""Online recipient authorization and once-only recorded cash handover."""
import hashlib
import hmac
import re
import secrets
from datetime import timedelta
from uuid import uuid4
from ..actor import require_role,require_independent,resolve_identity
from ..commands import DomainError,RecordedRefusal
from .sessions import MANILA,root as session_root
from .evidence import original_bytes
from .commitments import freeze_commitment

ALGORITHM='scrypt-n16384-r8-p1-v1'


def verifier(value,salt):return hashlib.scrypt(value.encode(),salt=salt,n=16384,r=8,p=1,dklen=32)


def authority(tx,entitlement):
    e=tx.get('entitlements',entitlement)
    if e['business_status'] in {'handed_over','cancelled','awaiting_amount','awaiting_publication'}:raise DomainError(409,'entitlement_not_payable')
    v=tx.get('entitlement_versions',e['current_version_id']);m=tx.db.execute('SELECT * FROM active_session_memberships WHERE entitlement_id=%s',(e['id'],)).fetchone()
    if not m or m['entitlement_version_id']!=v['id'] or v['amount_centavos'] is None:raise DomainError(409,'current_session_update_required')
    s=tx.get('payout_sessions',m['session_id']);sv=tx.get('session_versions',s['current_version_id']);se=tx.get('session_entries',m['session_entry_id'])
    if s['business_status']!='open' or sv['date']!=tx.now.astimezone(MANILA).date() or se['session_version_id']!=sv['id']:raise DomainError(409,'open_current_manila_session_required')
    d=tx.get('disasters',e['disaster_id'])
    if d['current_input_version_id']!=v['input_version_id']:raise DomainError(409,'current_input_required')
    registry=tx.get('household_versions',v['registry_version_id']);h=tx.get('households',e['household_id'])
    if not registry['head_photo_evidence_id'] or not registry['id_evidence_id'] or not registry['id_type'] or h['registered_without_id'] and registry['identity_state']!='field_checked_with_photo_id':raise DomainError(409,'accepted_photo_id_and_field_check_required')
    head=tx.db.execute('SELECT * FROM list_heads WHERE disaster_id=%s AND barangay_id=%s',(e['disaster_id'],s['barangay_id'])).fetchone()
    entry=tx.db.execute('SELECT * FROM approved_list_entries WHERE list_version_id=%s AND entitlement_id=%s AND entitlement_version_id=%s',(head['current_published_id'] if head else None,e['id'],v['id'])).fetchone()
    if not entry:raise DomainError(409,'current_confirmed_list_entry_required')
    return e,v,m,s,sv,se,entry,registry


def assigned(tx,c,session_version,household,*,followup=False):
    require_role(c,'disbursing');require_independent(c,household)
    row=tx.db.execute('SELECT * FROM session_assignments WHERE session_version_id=%s AND actor_id=%s AND (%s OR assignment_kind=%s) ORDER BY assignment_kind LIMIT 1',(session_version,c.actor_id,followup,'cash')).fetchone()
    if not row:raise DomainError(403,'current_assignment_required')
    return row


def attempt_event(tx,attempt,action,reason=None,check=None):
    event=tx.insert('attempt_events',{'attempt_id':attempt['id'],'action':action,'identity_check_id':check,'reason':reason})
    tx.audit('attempt.'+action,[('attempt_event_id',event['id'])],reason);return event


def expire(tx,attempt,reason):
    if attempt['business_status'] not in {'open','presented'}:return
    tx.update('payout_attempts',attempt['id'],{'business_status':'expired'});attempt_event(tx,attempt,'expire',reason)
    t=tx.get('payout_transactions',attempt['transaction_id']);e=tx.get('entitlements',t['entitlement_id'])
    if e['business_status']=='in_transaction':
        tx.update('entitlements',e['id'],{'business_status':'available','revision':e['revision']+1});tx.audit('entitlement.unused_expiry',[('entitlement_version_id',e['current_version_id'])],reason)
    tx.update('payout_transactions',t['id'],{'revision':t['revision']+1})


def checked_photo(tx,registry):
    files=[tx.get('evidence_versions',registry[k]) for k in ['head_photo_evidence_id','id_evidence_id']]
    for f in files:original_bytes(f)
    return files


def require_stop_clearance(tx,attempt,session):
    clear=tx.db.execute('SELECT * FROM transaction_clearances WHERE stopped_attempt_id=%s',(attempt['id'],)).fetchone()
    opening=tx.get('session_entries',attempt['session_entry_id']);old=tx.get('session_versions',opening['session_version_id'])
    if not clear or old['session_id']==session['id'] or session['created_at']<=clear['created_at']:
        raise DomainError(409,'clearance_and_distinct_later_session_required')


def id_check(tx,session_id,req):
    require_role(tx.context,'disbursing');s=session_root(tx,session_id)
    membership=tx.db.execute('SELECT e.id FROM entitlements e JOIN active_session_memberships m ON m.entitlement_id=e.id WHERE e.household_id=%s AND m.session_id=%s',(req['household_id'],s['id'])).fetchone()
    if not membership:raise DomainError(404,'record_unavailable')
    e,v,m,s,sv,se,list_entry,registry=authority(tx,membership['id']);assigned(tx,tx.context,sv['id'],e['household_id']);checked_photo(tx,registry)
    if req['result']=='pass' and (not req.get('accepted_id_type') or not req['person_photo_compared']):raise DomainError(422,'photo_comparison_required')
    if req['result']=='fail' and not (req.get('reason') or '').strip():raise DomainError(422,'failed_comparison_reason_required')
    t=tx.db.execute('SELECT * FROM payout_transactions WHERE entitlement_id=%s',(e['id'],)).fetchone()
    previous=tx.get('payout_attempts',t['current_attempt_id']) if t['current_attempt_id'] else None
    if previous and previous['business_status']=='stopped':require_stop_clearance(tx,previous,s)
    attempt=tx.get('payout_attempts',req['attempt_id']) if req.get('attempt_id') else None
    if req['result']=='fail' and not attempt and previous and previous['business_status'] in {'open','presented'}:
        attempt=previous
    if attempt:
        if attempt['transaction_id']!=t['id'] or attempt['id']!=t['current_attempt_id'] or attempt['entitlement_version_id']!=v['id'] or attempt['business_status'] not in {'open','presented'}:raise DomainError(409,'current_open_attempt_required')
        if tx.now>=attempt['expires_at']:raise DomainError(409,'attempt_expired_refresh_state')
    check=tx.insert('identity_checks',{'session_id':s['id'],'household_version_id':registry['id'],'checked_by':tx.context.actor_id,'result':req['result'],'accepted_id_type':req.get('accepted_id_type'),'person_photo_compared':req['person_photo_compared'],'reason':req.get('reason')})
    tx.audit('identity.compare',[('entitlement_version_id',v['id']),('household_version_id',registry['id'])],req.get('reason'),{'identity_check_id':str(check['id']),'result':check['result']})
    if req['result']=='fail' and not attempt:
        link=tx.db.execute('SELECT l.beneficiary_actor_id,v.phone FROM household_links l JOIN household_link_versions v ON v.id=l.link_version_id WHERE l.household_id=%s',(e['household_id'],)).fetchone()
        if not link or not link['beneficiary_actor_id']:raise DomainError(409,'current_recipient_linkage_required')
        # Terminal refusal only: no recipient authorization, open event or code.
        attempt=tx.insert('payout_attempts',{'transaction_id':t['id'],'attempt_number':(previous['attempt_number'] if previous else 0)+1,'session_entry_id':se['id'],'entitlement_version_id':v['id'],'path':'own_device' if link['phone'] else 'assisted','recipient_actor_id':link['beneficiary_actor_id'],'opened_at':tx.now,'expires_at':tx.now+timedelta(minutes=10),'business_status':'stopped','current_id_check_id':check['id'],'bad_code_count':0})
        tx.update('payout_transactions',t['id'],{'current_attempt_id':attempt['id']})
    if attempt:
        state='presented' if req['result']=='pass' else 'stopped'
        tx.update('payout_attempts',attempt['id'],{'business_status':state,'current_id_check_id':check['id']});event=attempt_event(tx,attempt,'present' if state=='presented' else 'stop',req.get('reason'),check['id'])
        tx.update('payout_transactions',t['id'],{'revision':t['revision']+1})
    if req['result']=='fail':
        tx.update('entitlements',e['id'],{'business_status':'held','hold_reasons':['identity_check_failed'],'revision':e['revision']+1});tx.audit('entitlement.identity_hold',[('entitlement_version_id',v['id'])],req['reason'])
    return [('entitlement_version_id',v['id'])]


def establish_pin(tx,household,req):
    require_role(tx.context,'beneficiary')
    if tx.context.household_id!=household:raise DomainError(403,'own_household_only')
    h=tx.get('households',household)
    if h['current_pin_id']:raise DomainError(409,'pin_already_established_recovery_pending')
    if not re.fullmatch(r'[0-9]{6,12}',req['pin']):raise DomainError(422,'private_pin_six_to_twelve_digits')
    check=tx.get('identity_checks',req['identity_check_id']);s=tx.get('payout_sessions',check['session_id'])
    e=tx.db.execute('SELECT id FROM entitlements WHERE household_id=%s AND disaster_id=%s',(household,s['disaster_id'])).fetchone()
    if not e:raise DomainError(404,'record_unavailable')
    e,v,m,s,sv,se,le,registry=authority(tx,e['id'])
    if check['result']!='pass' or check['household_version_id']!=registry['id']:raise DomainError(409,'current_prior_identity_check_required')
    assigned(tx,resolve_identity(tx.db,check['checked_by']),sv['id'],household)
    salt=secrets.token_bytes(32);pin=tx.insert('assisted_pins',{'household_id':household,'established_after_check_id':check['id'],'salt':salt,'digest':verifier(req['pin'],salt),'algorithm':ALGORITHM})
    tx.insert('credential_counters',{'pin_id':pin['id'],'failed_count':0,'window_start':None,'locked_until':None})
    tx.update('households',household,{'current_pin_id':pin['id'],'revision':h['revision']+1});tx.audit('recipient.pin_established',[('household_version_id',h['current_version_id'])],details={'pin_not_disclosed':True})
    return [('household_id',household)]


def verify_pin(tx,e,registry,value):
    h=tx.get('households',e['household_id'])
    if not h['current_pin_id']:raise DomainError(409,'prior_private_pin_required')
    p=tx.get('assisted_pins',h['current_pin_id']);counter=tx.db.execute('SELECT * FROM credential_counters WHERE pin_id=%s',(p['id'],)).fetchone()
    if counter['locked_until'] and counter['locked_until']>tx.now:raise DomainError(429,'private_pin_temporarily_locked')
    if not value or not hmac.compare_digest(verifier(value,p['salt']),p['digest']):
        count=counter['failed_count']+1 if counter['window_start'] and tx.now<counter['window_start']+timedelta(minutes=15) else 1
        tx.db.execute('UPDATE credential_counters SET failed_count=%s,window_start=%s,locked_until=%s WHERE pin_id=%s',(count,counter['window_start'] if count>1 else tx.now,tx.now+timedelta(minutes=15) if count>=5 else None,p['id']))
        tx.audit('recipient.pin_refused',[('household_version_id',registry['id'])],details={'failure_count':count})
        raise RecordedRefusal(403,'private_pin_incorrect',[('household_id',h['id'])])
    tx.db.execute('UPDATE credential_counters SET failed_count=0,window_start=NULL,locked_until=NULL WHERE pin_id=%s',(p['id'],))
    check=tx.db.execute('SELECT * FROM identity_checks WHERE session_id=%s AND household_version_id=%s AND result=%s ORDER BY created_at DESC,id DESC LIMIT 1',(tx.db.execute('SELECT session_id FROM active_session_memberships WHERE entitlement_id=%s',(e['id'],)).fetchone()['session_id'],registry['id'],'pass')).fetchone()
    if not check:raise DomainError(409,'current_prior_identity_check_required')
    return check


def open_attempt(tx,entitlement,req):
    require_role(tx.context,'beneficiary');e,v,m,s,sv,se,le,registry=authority(tx,entitlement)
    if tx.context.household_id!=e['household_id']:raise DomainError(403,'own_household_only')
    if e['business_status']=='held':raise DomainError(409,'held_entitlement_requires_clearance_or_session_update')
    t=tx.db.execute('SELECT * FROM payout_transactions WHERE entitlement_id=%s',(e['id'],)).fetchone();tx.revision(t,req['expected_revision'])
    previous=tx.get('payout_attempts',t['current_attempt_id']) if t['current_attempt_id'] else None
    if previous:
        if previous['business_status'] in {'open','presented'}:
            if tx.now<previous['expires_at']:raise DomainError(409,'attempt_already_open_read_current_state')
            expire(tx,previous,'Unused ten-minute authorization expired')
        elif previous['business_status']=='handed_over':raise DomainError(409,'handover_already_recorded')
        elif previous['business_status']=='stopped':
            require_stop_clearance(tx,previous,s)
        elif previous['bad_code_count']>=5 and tx.now<previous['expires_at']:raise DomainError(429,'authorization_retry_after_expiry')
    check=None
    if req['path']=='assisted':
        link=tx.db.execute('SELECT v.phone FROM household_links l JOIN household_link_versions v ON v.id=l.link_version_id WHERE l.household_id=%s',(e['household_id'],)).fetchone()
        if link and link['phone']:raise DomainError(409,'registered_phone_assisted_path_deferred')
        check=verify_pin(tx,e,registry,req.get('pin'))
        assigned(tx,resolve_identity(tx.db,check['checked_by']),sv['id'],e['household_id'])
    elif req['path']!='own_device' or req.get('pin') is not None:raise DomainError(422,'valid_recipient_path_required')
    a=tx.insert('payout_attempts',{'transaction_id':t['id'],'attempt_number':(previous['attempt_number'] if previous else 0)+1,'session_entry_id':se['id'],'entitlement_version_id':v['id'],'path':req['path'],'recipient_actor_id':tx.context.actor_id,'opened_at':tx.now,'expires_at':tx.now+timedelta(minutes=10),'business_status':'open','current_id_check_id':check['id'] if check else None,'bad_code_count':0})
    code=f'{secrets.randbelow(1000000):06d}';salt=secrets.token_bytes(32)
    tx.insert('payout_codes',{'attempt_id':a['id'],'salt':salt,'digest':verifier(code,salt),'algorithm':ALGORITHM,'expires_at':a['expires_at'],'consumed_at':None})
    event=attempt_event(tx,a,'open',check=check['id'] if check else None)
    tx.update('payout_transactions',t['id'],{'current_attempt_id':a['id'],'revision':t['revision']+1+(1 if previous and previous['business_status'] in {'open','presented'} else 0)})
    tx.update('entitlements',e['id'],{'business_status':'in_transaction','revision':e['revision']+1});tx.audit('entitlement.authorized',[('entitlement_version_id',v['id']),('attempt_event_id',event['id'])])
    tx.secret_response={'code':code,'code_revealed_once':True,'expires_at':a['expires_at'].isoformat()}
    return [('transaction_id',t['id']),('attempt_event_id',event['id'])]


def handover(tx,transaction,req):
    require_role(tx.context,'disbursing');t=tx.get('payout_transactions',transaction);tx.revision(t,req['expected_revision'])
    if tx.db.execute('SELECT 1 FROM recorded_handovers WHERE transaction_id=%s',(transaction,)).fetchone():raise DomainError(409,'handover_already_recorded')
    e,v,m,s,sv,se,list_entry,registry=authority(tx,t['entitlement_id']);payer=assigned(tx,tx.context,sv['id'],e['household_id'])
    if e['business_status']=='held':raise DomainError(409,'held_entitlement_requires_clearance_or_session_update')
    a=tx.get('payout_attempts',req['attempt_id'])
    if a['transaction_id']!=t['id'] or t['current_attempt_id']!=a['id'] or a['business_status']!='presented' or a['entitlement_version_id']!=v['id']:raise DomainError(409,'current_presented_authorization_required')
    link=tx.db.execute('SELECT beneficiary_actor_id FROM household_links WHERE household_id=%s',(e['household_id'],)).fetchone()
    if not link or link['beneficiary_actor_id']!=a['recipient_actor_id']:raise DomainError(409,'recipient_linkage_changed')
    recipient=resolve_identity(tx.db,a['recipient_actor_id'])
    if recipient.role!='beneficiary' or recipient.actor_id==tx.context.actor_id:raise DomainError(403,'recipient_authorization_required')
    code=tx.db.execute('SELECT * FROM payout_codes WHERE attempt_id=%s',(a['id'],)).fetchone()
    if code['consumed_at'] or tx.now>=code['expires_at'] or tx.now>=a['expires_at']:raise DomainError(409,'unused_unexpired_code_required')
    check=tx.get('identity_checks',a['current_id_check_id']) if a['current_id_check_id'] else None
    if not check or check['result']!='pass' or check['session_id']!=s['id'] or check['household_version_id']!=registry['id'] or check['checked_by']!=tx.context.actor_id:raise DomainError(409,'payer_photo_comparison_required')
    checker=None
    if a['path']=='assisted':
        try:
            if not req.get('checker_actor_id') or req['checker_actor_id']==tx.context.actor_id:raise DomainError(409,'independent_assisted_checker_required')
            checker_context=resolve_identity(tx.db,req['checker_actor_id']);checker=assigned(tx,checker_context,sv['id'],e['household_id'])
        except DomainError:
            tx.update('entitlements',e['id'],{'business_status':'held','hold_reasons':['independent_checker_unavailable'],'revision':e['revision']+1})
            tx.audit('entitlement.checker_unavailable',[('entitlement_version_id',v['id'])], 'Assisted cash requires an eligible independent checking officer; DSWD session review required.')
            raise RecordedRefusal(409,'independent_assisted_checker_required',[('transaction_id',t['id'])]) from None
    elif req.get('checker_actor_id') is not None:raise DomainError(422,'checker_only_for_assisted_handover')
    if not re.fullmatch(r'[0-9]{6}',req['code']) or not hmac.compare_digest(verifier(req['code'],code['salt']),code['digest']):
        count=a['bad_code_count']+1;tx.update('payout_attempts',a['id'],{'bad_code_count':count})
        event=tx.db.execute("SELECT id FROM attempt_events WHERE attempt_id=%s AND action='open'",(a['id'],)).fetchone()
        tx.audit('attempt.code_refused',[('attempt_event_id',event['id'])],details={'failure_count':count})
        if count>=5:expire(tx,a,'Five incorrect authorization checks')
        raise RecordedRefusal(403,'payout_code_incorrect',[('transaction_id',t['id'])])
    files=checked_photo(tx,registry)
    receipt=tx.insert('recorded_handovers',{'transaction_id':t['id'],'entitlement_id':e['id'],'attempt_id':a['id'],'entitlement_version_id':v['id'],'input_version_id':v['input_version_id'],'session_entry_id':a['session_entry_id'],'current_session_entry_id':se['id'],'session_version_id':sv['id'],'current_list_entry_id':list_entry['id'],'identity_check_id':check['id'],'payer_id':tx.context.actor_id,'recipient_actor_id':a['recipient_actor_id'],'checker_assignment_id':checker['id'] if checker else None,'path':a['path'],'amount_centavos':v['amount_centavos'],'handed_at':tx.now,'authorization_result':{'recipient_authorized':True,'code_matched':True,'photo_compared':True,'current_versions_checked':True,'assisted_independence_checked':a['path']=='assisted','identity_assurance':'claimed_unverified'}})
    tx.db.execute('UPDATE payout_codes SET consumed_at=%s WHERE attempt_id=%s',(tx.now,a['id']));tx.update('payout_attempts',a['id'],{'business_status':'handed_over'});event=attempt_event(tx,a,'handover',check=check['id'])
    tx.update('entitlements',e['id'],{'business_status':'handed_over','hold_reasons':[],'revision':e['revision']+1});tx.update('payout_transactions',t['id'],{'revision':t['revision']+1})
    tx.audit('payout.recorded_handover',[('handover_id',receipt['id']),('attempt_event_id',event['id'])])
    freeze_commitment(tx,'handover_id',receipt['id'],'handover',{'receipt':receipt,'entitlement_version':v,'identity_check':check,'session_version':sv,'current_list_entry':list_entry},evidence=[files[0]])
    return [('handover_id',receipt['id']),('transaction_id',t['id'])]


def clearance(tx,transaction,req):
    require_role(tx.context,'dswd');t=tx.get('payout_transactions',transaction);tx.revision(t,req['expected_revision']);e=tx.get('entitlements',t['entitlement_id']);require_independent(tx.context,e['household_id'])
    a=tx.get('payout_attempts',t['current_attempt_id']) if t['current_attempt_id'] else None
    if not a or a['business_status']!='stopped' or not req['reason'].strip() or tx.db.execute('SELECT 1 FROM transaction_clearances WHERE stopped_attempt_id=%s',(a['id'],)).fetchone():raise DomainError(409,'uncleared_stopped_attempt_required')
    clear=tx.insert('transaction_clearances',{'transaction_id':t['id'],'stopped_attempt_id':a['id'],'reason':req['reason'],'cleared_at':tx.now})
    if req.get('evidence_id'):
        from .evidence import link_evidence
        link_evidence(tx,req['evidence_id'],'clearance_id',clear['id'],'clearance')
    tx.update('payout_transactions',t['id'],{'revision':t['revision']+1});tx.audit('attempt.clearance',[('attempt_event_id',tx.db.execute("SELECT id FROM attempt_events WHERE attempt_id=%s AND action='stop' ORDER BY created_at DESC,id DESC LIMIT 1",(a['id'],)).fetchone()['id'])],req['reason'],{'clearance_id':str(clear['id']),'distinct_later_session_required':True})
    return [('transaction_id',t['id'])]


def expire_due(tx):
    for a in tx.db.execute("SELECT * FROM payout_attempts WHERE run_id=%s AND business_status IN ('open','presented') AND expires_at<=%s ORDER BY expires_at,id",(tx.context.run_id,tx.now)).fetchall():expire(tx,a,'Unused authorization reached its fixed expiry')


def can_read(db,c,transaction):
    t=db.execute('SELECT * FROM payout_transactions WHERE id=%s AND run_id=%s',(transaction,c.run_id)).fetchone()
    if not t:raise DomainError(404,'record_unavailable')
    e=db.execute('SELECT * FROM entitlements WHERE id=%s',(t['entitlement_id'],)).fetchone()
    if c.role in {'dswd','auditor'} or c.role=='beneficiary' and c.household_id==e['household_id']:return t,e
    if c.role=='disbursing':
        permitted=db.execute('''SELECT 1 FROM session_entries se JOIN session_versions sv ON sv.id=se.session_version_id JOIN payout_sessions s ON s.current_version_id=sv.id JOIN session_assignments a ON a.session_version_id=sv.id WHERE se.entitlement_id=%s AND a.actor_id=%s UNION ALL SELECT 1 FROM recorded_handovers WHERE transaction_id=%s AND payer_id=%s LIMIT 1''',(e['id'],c.actor_id,t['id'],c.actor_id)).fetchone()
        if permitted:return t,e
    raise DomainError(404,'record_unavailable')


def project(db,c,transaction):
    t,e=can_read(db,c,transaction);v=db.execute('SELECT * FROM entitlement_versions WHERE id=%s',(e['current_version_id'],)).fetchone()
    profile=db.execute('SELECT * FROM household_versions WHERE id=%s',(v['registry_version_id'],)).fetchone()
    head=db.execute('SELECT name FROM member_versions WHERE household_version_id=%s AND is_head',(profile['id'],)).fetchone()['name']
    view={'id':t['id'],'disaster_id':e['disaster_id'],'entitlement_id':e['id'],'household_id':e['household_id'],'household_name':head,'business_status':e['business_status'],'amount_centavos':str(v['amount_centavos']) if v['amount_centavos'] is not None else None,'photo_evidence_id':profile['head_photo_evidence_id'],'accepted_id_type':profile['id_type'],'current_attempt':None,'receipt':None}
    receipt=db.execute('SELECT * FROM recorded_handovers WHERE transaction_id=%s',(t['id'],)).fetchone()
    if not receipt:view['revision']=t['revision']
    elif c.role!='disbursing':view['revision']=t['revision']
    if c.role=='beneficiary':view['assisted_pin_established']=bool(db.execute('SELECT current_pin_id FROM households WHERE id=%s',(e['household_id'],)).fetchone()['current_pin_id'])
    if t['current_attempt_id']:
        a=db.execute('SELECT * FROM payout_attempts WHERE id=%s',(t['current_attempt_id'],)).fetchone()
        view['current_attempt']={k:a[k] for k in ['id','attempt_number','path','business_status','opened_at','expires_at','current_id_check_id']}
        view['attempt_events']=db.execute('SELECT id,action,reason,created_at FROM attempt_events WHERE attempt_id=%s ORDER BY created_at,id',(a['id'],)).fetchall()
    checks=db.execute('SELECT i.id,i.result,i.accepted_id_type,i.person_photo_compared,i.checked_by,i.created_at FROM identity_checks i JOIN session_entries se ON se.entitlement_id=%s JOIN session_versions sv ON sv.id=se.session_version_id WHERE i.session_id=sv.session_id AND i.household_version_id=%s ORDER BY i.created_at DESC,i.id DESC',(e['id'],v['registry_version_id'])).fetchall()
    view['identity_checks']=list({r['id']:r for r in checks}.values())
    if receipt:
        view['receipt']={k:receipt[k] for k in ['id','amount_centavos','handed_at','payer_id','recipient_actor_id','path','entitlement_version_id','input_version_id']};view['receipt']['amount_centavos']=str(receipt['amount_centavos'])
        view['receipt']['proofs']=db.execute('SELECT c.id,j.state FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id WHERE c.handover_id=%s',(receipt['id'],)).fetchall()
    return view
