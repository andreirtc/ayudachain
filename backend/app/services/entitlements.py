"""Human eligibility, exact documented calculations and immutable list candidates."""
from datetime import timedelta
from uuid import uuid4
from ..actor import require_role,require_independent
from ..commands import DomainError,RecordedRefusal
from . import registry,claims,checks
from .funds import money,MAX
from .evidence import link_evidence
from .commitments import freeze_commitment,document_commitment


def calculate(mode,wage,days,fixed):
    if mode=='wage_formula':
        if not isinstance(wage,int) or wage<=0 or not isinstance(days,int) or days<=0 or fixed is not None:raise DomainError(422,'documented_wage_and_days_required')
        daily=((wage*75+99999)//100000)*1000
        amount=daily*days
        calculation={'formula':'ceil((0.75 * wage_centavos) / 1000) * 1000 * days','wage_centavos':str(wage),'rounded_daily_centavos':str(daily),'days':str(days)}
    elif mode=='fixed_category':
        if wage is not None or days is not None or not isinstance(fixed,int) or fixed<=0:raise DomainError(422,'documented_fixed_amount_required')
        amount=fixed;calculation={'formula':'documented_fixed_category','fixed_centavos':str(fixed)}
    else:raise DomainError(422,'unknown_amount_mode')
    if not 0<amount<=MAX:raise DomainError(422,'calculated_amount_overflow')
    return amount,calculation


def basis(tx,disaster,category):
    d=tx.get('disasters',disaster)
    if not d['current_input_version_id']:return None,None,{'state':'awaiting_documented_inputs'}
    v=tx.get('amount_input_versions',d['current_input_version_id'])
    r=tx.db.execute('SELECT * FROM amount_rules WHERE input_version_id=%s AND category_id=%s',(v['id'],category)).fetchone()
    if not r:return None,None,{'state':'awaiting_documented_category_rule'}
    amount,calculation=calculate(v['mode'],v['wage_centavos'],r['day_count'],r['fixed_centavos'])
    return v['id'],amount,calculation


def expire_attempts(tx,entitlement,reason):
    for a in tx.db.execute("SELECT a.* FROM payout_attempts a JOIN payout_transactions t ON t.id=a.transaction_id WHERE t.entitlement_id=%s AND a.business_status IN ('open','presented')",(entitlement,)).fetchall():
        tx.update('payout_attempts',a['id'],{'business_status':'expired'})
        event=tx.insert('attempt_events',{'attempt_id':a['id'],'action':'expire','identity_check_id':None,'reason':reason})
        tx.audit('attempt.invalidate',[('attempt_event_id',event['id'])],reason)


def notify_change(tx,root,version,old_amount,new_amount):
    link=tx.db.execute('SELECT link_version_id FROM household_links WHERE household_id=%s',(root['household_id'],)).fetchone()
    for channel in ['in_app','simulated_notice_sms']:
        n=tx.insert('notifications',{'household_id':root['household_id'],'link_version_id':link['link_version_id'] if link else None,'purpose':'amount_basis_changed','channel':channel,'content':{'kind':'amount_basis_changed','old_amount_centavos':str(old_amount) if old_amount is not None else None,'new_amount_centavos':str(new_amount) if new_amount is not None else None,'message':'Changed basis requires current publication and affected session update.'},'simulated':channel=='simulated_notice_sms','state':'pending','entitlement_version_id':version})
        tx.audit('notice.intent',[('notification_id',n['id'])])


def bump_list(tx,disaster,barangay,reason):
    head=tx.db.execute('SELECT * FROM list_heads WHERE disaster_id=%s AND barangay_id=%s',(disaster,barangay)).fetchone()
    if head:
        if head['newest_requested_id']:
            candidate=tx.get('approved_list_versions',head['newest_requested_id'])
            if candidate['business_status']=='pending_publication':
                tx.update('approved_list_versions',candidate['id'],{'business_status':'stale'});tx.audit('list.stale',[('list_version_id',candidate['id'])],reason)
        tx.update('list_heads',head['id'],{'eligibility_revision':head['eligibility_revision']+1})


def version_entitlement(tx,root,decision,*,initial=False,review=None):
    s=tx.get('claim_submissions',decision['submission_id'])
    old=tx.get('entitlement_versions',root['current_version_id']) if not initial else None
    registry_id=review['result_version_id'] if review and review['result_version_id'] else old['registry_version_id'] if old else s['registry_version_id']
    category=decision['category_id'];input_id,amount,calculation=basis(tx,root['disaster_id'],category)
    handover=tx.db.execute('SELECT * FROM recorded_handovers WHERE entitlement_id=%s',(root['id'],)).fetchone()
    if handover:
        if amount is not None:
            diff=tx.insert('paid_difference_events',{'handover_id':handover['id'],'new_input_version_id':input_id,'new_decision_id':decision['id'] if decision['id']!=old['decision_id'] else None,'hypothetical_centavos':amount,'locked_centavos':handover['amount_centavos'],'delta_centavos':amount-handover['amount_centavos']})
            tx.audit('entitlement.paid_difference',[('handover_id',handover['id'])],details={'difference_id':str(diff['id']),'no_payment_or_recovery':True})
        profile=tx.get('household_versions',old['registry_version_id'])
        bump_list(tx,root['disaster_id'],profile['declared_barangay_id'],'Paid display category or current documentary basis changed; recorded payment remains locked')
        return old
    identity=root['current_version_id'] if initial else uuid4()
    v=tx.insert('entitlement_versions',{'id':identity,'entitlement_id':root['id'],'predecessor_id':old['id'] if old else None,'decision_id':decision['id'],'registry_version_id':registry_id,'registry_review_id':review['id'] if review else old['registry_review_id'] if old else None,'category_id':category,'input_version_id':input_id,'amount_centavos':amount,'calculation':calculation})
    membership=tx.db.execute('SELECT 1 FROM active_session_memberships WHERE entitlement_id=%s',(root['id'],)).fetchone()
    tx.update('entitlements',root['id'],{'current_version_id':identity,'business_status':'awaiting_amount' if amount is None else 'held' if membership else 'awaiting_publication','hold_reasons':['basis_changed','session_update_required'] if membership else [],'revision':root['revision']+(0 if initial else 1)})
    tx.audit('entitlement.version',[('entitlement_version_id',identity)])
    if old:
        expire_attempts(tx,root['id'],'Current eligibility, registry or amount basis changed')
        notify_change(tx,root,identity,old['amount_centavos'],amount)
    vregistry=tx.get('household_versions',registry_id);bump_list(tx,root['disaster_id'],vregistry['declared_barangay_id'],'Eligibility or basis changed')
    if old:
        old_registry=tx.get('household_versions',old['registry_version_id'])
        if old_registry['declared_barangay_id']!=vregistry['declared_barangay_id']:
            bump_list(tx,root['disaster_id'],old_registry['declared_barangay_id'],'Reviewed residence moved to another barangay; old membership is stale')
    return v


def reviewed(tx,claim,req):
    r=claims.latest_round(tx,claim);s=tx.get('claim_submissions',claim['current_submission_id'])
    latest=tx.db.execute('SELECT * FROM check_runs WHERE submission_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(s['id'],)).fetchone()
    data_revision=tx.db.execute('SELECT check_data_revision FROM field_offices WHERE id=%s',(tx.context.office_id,)).fetchone()['check_data_revision']
    if not latest or latest['compared_data_revision']!=data_revision:
        latest=checks.run(tx,s,r['id'],'recheck');tx.audit('claim.review_changed',[('check_run_id',latest['id'])])
        raise RecordedRefusal(409,'review_changed_refresh_and_review_new_flags',[('check_run_id',latest['id'])])
    if req.get('reviewed_check_id')!=latest['id']:raise DomainError(409,'latest_check_must_be_reviewed')
    return r,s,latest


def decide(tx,identity,req,*,bulk_group=None):
    require_role(tx.context,'dswd');c=tx.get('claims',identity);require_independent(tx.context,c['household_id']);tx.revision(c,req['expected_revision'])
    action=req['action']
    if c['business_status']!='awaiting_dswd' and not (action=='category_change' and c['business_status']=='approved'):raise DomainError(409,'claim_not_ready_for_decision')
    r,s,check=reviewed(tx,c,req)
    if action in {'approve','category_change'}:
        if not req.get('category_id'):raise DomainError(422,'human_category_required')
        tx.get('damage_categories',req['category_id'])
    if action in {'decline','category_change'} and not (req.get('reason') or '').strip():raise DomainError(422,'decision_reason_required')
    if action=='refer' and not (req.get('question') or '').strip():raise DomainError(422,'referral_question_required')
    if action not in {'approve','decline','refer','category_change'}:raise DomainError(422,'unsupported_human_decision')
    d=tx.insert('claim_decisions',{'claim_id':c['id'],'submission_id':s['id'],'round_id':r['id'],'predecessor_id':c['current_decision_id'],'check_run_id':check['id'],'action':action,'category_id':req.get('category_id') if action in {'approve','category_change'} else None,'reason':req.get('reason'),'question':req.get('question'),'confirmed_by':None,'bulk_group_id':bulk_group,'challenge_event_id':None})
    status={'approve':'approved','decline':'declined','refer':'referred','category_change':'approved'}[action]
    tx.update('claims',c['id'],{'business_status':status,'current_decision_id':d['id'],'revision':c['revision']+1});tx.audit('claim.'+action,[('decision_id',d['id'])],req.get('reason'))
    if action=='refer':
        duration=req.get('response_hours') or r['response_hours']
        if not 0<duration<=720:raise DomainError(422,'referral_duration_required')
        nr=tx.insert('claim_rounds',{'submission_id':s['id'],'referral_decision_id':d['id'],'response_hours':duration,'deadline_at':tx.now+timedelta(hours=duration),'state':'waiting','route_kind':None,'primary_snapshot_id':None,'routed_response_id':None,'revision':0});tx.audit('claim.referral',[('round_id',nr['id']),('decision_id',d['id'])])
    elif action in {'approve','decline'}:
        for old in tx.db.execute("SELECT * FROM claim_rounds WHERE submission_id=%s AND state!='closed'",(s['id'],)).fetchall():tx.update('claim_rounds',old['id'],{'state':'closed','revision':old['revision']+1});tx.audit('claim.thread_final',[('round_id',old['id']),('decision_id',d['id'])])
    if action=='approve':
        entitlement,version=uuid4(),uuid4()
        e=tx.insert('entitlements',{'id':entitlement,'claim_id':c['id'],'household_id':c['household_id'],'disaster_id':c['disaster_id'],'current_version_id':version,'business_status':'awaiting_amount','hold_reasons':[],'revision':0})
        version_entitlement(tx,e,d,initial=True)
        tx.insert('payout_transactions',{'entitlement_id':e['id'],'current_attempt_id':None,'current_outcome_id':None,'revision':0})
    elif action=='category_change':
        e=tx.db.execute('SELECT * FROM entitlements WHERE claim_id=%s',(c['id'],)).fetchone();version_entitlement(tx,e,d)
    registry.changed(tx)
    return [('decision_id',d['id'])]


def bulk_approve(tx,req):
    require_role(tx.context,'dswd');group=uuid4()
    if not req['claims'] or len({r['claim_id'] for r in req['claims']})!=len(req['claims']):raise DomainError(422,'distinct_claims_required')
    # Validate the entire set before any human decision/check-data change.
    for item in req['claims']:
        c=tx.get('claims',item['claim_id']);require_independent(tx.context,c['household_id']);r,s,check=reviewed(tx,c,item)
        responses=tx.db.execute('SELECT * FROM claim_responses WHERE round_id=%s ORDER BY created_at,id',(r['id'],)).fetchall();latest={v['actor_id']:v for v in responses}
        if check['risk_score'] or not any(v['kind']=='endorse' for v in latest.values()) or any(v['category_disputed'] for v in latest.values()):raise DomainError(409,'bulk_requires_endorsed_unflagged_undisputed')
    refs=[]
    # Keep already-reviewed check-data revision stable within this atomic group.
    revision=tx.db.execute('SELECT check_data_revision FROM field_offices WHERE id=%s',(tx.context.office_id,)).fetchone()['check_data_revision']
    for item in req['claims']:
        tx.db.execute('UPDATE field_offices SET check_data_revision=%s WHERE id=%s',(revision,tx.context.office_id))
        refs.extend(decide(tx,item['claim_id'],dict(item,action='approve',reason=req.get('reason'),question=None,response_hours=None),bulk_group=group))
    tx.db.execute('UPDATE field_offices SET check_data_revision=%s WHERE id=%s',(revision+1,tx.context.office_id));return refs


def save_inputs(tx,req):
    require_role(tx.context,'dswd');d=tx.get('disasters',req['disaster_id']);tx.revision(d,req['expected_revision'])
    if not req['rules'] or len({r['category_id'] for r in req['rules']})!=len(req['rules']):raise DomainError(422,'distinct_documented_rules_required')
    if d['current_input_version_id'] and not (req.get('reason') or '').strip():raise DomainError(422,'changed_basis_reason_required')
    wage=money(req['wage_centavos']) if req['mode']=='wage_formula' and req.get('wage_centavos') else None
    if req['mode']=='fixed_category' and (req.get('wage_centavos') is not None or req.get('wage_evidence_id')):raise DomainError(422,'whole_version_mode_required')
    version=tx.insert('amount_input_versions',{'disaster_id':d['id'],'predecessor_id':d['current_input_version_id'],'mode':req['mode'],'wage_centavos':wage,'reason':req.get('reason')});files=[]
    if req['mode']=='wage_formula':
        if not wage or not req.get('wage_evidence_id'):raise DomainError(422,'wage_original_required')
        files.append(link_evidence(tx,req['wage_evidence_id'],'input_version_id',version['id'],'wage','wage_centavos'))
    rules=[]
    for value in req['rules']:
        tx.get('damage_categories',value['category_id']);fixed=money(value['fixed_centavos']) if value.get('fixed_centavos') else None
        calculate(req['mode'],wage,value.get('day_count'),fixed)
        rule=tx.insert('amount_rules',{'input_version_id':version['id'],'category_id':value['category_id'],'day_count':value.get('day_count'),'fixed_centavos':fixed});rules.append(rule)
        files.append(link_evidence(tx,value['evidence_id'],'amount_rule_id',rule['id'],'days' if req['mode']=='wage_formula' else 'fixed_amount','day_count' if req['mode']=='wage_formula' else 'fixed_centavos'))
    tx.update('disasters',d['id'],{'current_input_version_id':version['id'],'revision':d['revision']+1});tx.audit('inputs.save',[('input_version_id',version['id'])],req.get('reason'))
    previous=tx.db.execute('SELECT id,public_context FROM commitments WHERE input_version_id=%s',(d['current_input_version_id'],)).fetchone() if d['current_input_version_id'] else None
    for file in files:document_commitment(tx,file)
    freeze_commitment(tx,'input_version_id',version['id'],'amount_input',{'version':version,'rules':rules},context=previous['public_context'] if previous else None,predecessor=previous['id'] if previous else None,evidence=files)
    for root in tx.db.execute("SELECT * FROM entitlements WHERE disaster_id=%s AND business_status!='cancelled'",(d['id'],)).fetchall():
        decision=tx.db.execute('SELECT d.* FROM claim_decisions d JOIN claims c ON c.current_decision_id=d.id WHERE c.id=%s',(root['claim_id'],)).fetchone();version_entitlement(tx,root,decision)
    return [('input_version_id',version['id'])]


def request_list(tx,req):
    require_role(tx.context,'dswd');d=tx.get('disasters',req['disaster_id']);tx.get('barangays',req['barangay_id'])
    if not d['current_input_version_id']:raise DomainError(409,'documented_inputs_required')
    head=tx.db.execute('SELECT * FROM list_heads WHERE disaster_id=%s AND barangay_id=%s',(d['id'],req['barangay_id'])).fetchone()
    if not head:head=tx.insert('list_heads',{'disaster_id':d['id'],'barangay_id':req['barangay_id'],'eligibility_revision':0,'newest_requested_id':None,'current_published_id':None})
    if req.get('expected_revision') is not None and head['eligibility_revision']!=req['expected_revision']:raise DomainError(409,'stale_list_revision')
    roots=tx.db.execute("SELECT e.* FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id JOIN household_versions h ON h.id=v.registry_version_id WHERE e.disaster_id=%s AND h.declared_barangay_id=%s AND e.business_status!='cancelled' ORDER BY e.created_at,e.id",(d['id'],req['barangay_id'])).fetchall()
    if not roots and not head['current_published_id']:raise DomainError(409,'no_approved_entries')
    if any(tx.get('entitlement_versions',r['current_version_id'])['amount_centavos'] is None for r in roots):raise DomainError(409,'list_has_awaiting_amounts')
    if head['newest_requested_id']:
        old=tx.get('approved_list_versions',head['newest_requested_id'])
        if old['business_status']=='pending_publication':tx.update('approved_list_versions',old['id'],{'business_status':'stale'});tx.audit('list.superseded_request',[('list_version_id',old['id'])])
    version=tx.insert('approved_list_versions',{'list_head_id':head['id'],'predecessor_published_id':head['current_published_id'],'based_on_revision':head['eligibility_revision'],'basis_input_version_id':d['current_input_version_id'],'requested_at':tx.now,'business_status':'pending_publication','published_at':None});entries=[];files={}
    for root in roots:
        v=tx.get('entitlement_versions',root['current_version_id']);c=tx.get('claims',root['claim_id']);display=tx.get('claim_decisions',c['current_decision_id']);profile=tx.get('household_versions',v['registry_version_id'])
        name=tx.db.execute('SELECT name FROM member_versions WHERE household_version_id=%s AND is_head',(profile['id'],)).fetchone()['name']
        for key in ['head_photo_evidence_id','id_evidence_id']:
            if profile[key]:files[profile[key]]=tx.get('evidence_versions',profile[key])
        row=tx.insert('approved_list_entries',{'list_version_id':version['id'],'entitlement_id':root['id'],'entitlement_version_id':v['id'],'submission_id':c['current_submission_id'],'display_decision_id':display['id'],'registry_version_id':profile['id'],'registry_review_id':v['registry_review_id'],'frozen_name':name,'frozen_zone':profile['zone'],'display_category_id':display['category_id']});entries.append({'entry':row,'entitlement_version':v,'registry':profile})
    tx.update('list_heads',head['id'],{'newest_requested_id':version['id']});tx.audit('list.request',[('list_version_id',version['id'])])
    previous=tx.db.execute('SELECT id,public_context FROM commitments WHERE list_version_id=%s',(head['current_published_id'],)).fetchone() if head['current_published_id'] else None
    freeze_commitment(tx,'list_version_id',version['id'],'approved_list',{'version':version,'disaster_id':d['id'],'barangay_id':req['barangay_id'],'entries':entries},context=previous['public_context'] if previous else None,predecessor=previous['id'] if previous else None,evidence=list(files.values()))
    return [('list_version_id',version['id'])]


def publish_confirmed(tx,version_id):
    version=tx.get('approved_list_versions',version_id);head=tx.get('list_heads',version['list_head_id']);d=tx.get('disasters',head['disaster_id'])
    if version['business_status']!='pending_publication':return
    if head['newest_requested_id']!=version_id or head['eligibility_revision']!=version['based_on_revision'] or d['current_input_version_id']!=version['basis_input_version_id']:
        tx.update('approved_list_versions',version_id,{'business_status':'stale'});tx.audit('list.stale',[('list_version_id',version_id)]);return
    if head['current_published_id']:
        tx.update('approved_list_versions',head['current_published_id'],{'business_status':'historical'});tx.audit('list.historical',[('list_version_id',head['current_published_id'])])
    tx.update('approved_list_versions',version_id,{'business_status':'published','published_at':tx.now});tx.update('list_heads',head['id'],{'current_published_id':version_id})
    tx.update('disasters',d['id'],{'inputs_locked_at':d['inputs_locked_at'] or tx.now})
    for row in tx.db.execute('SELECT * FROM approved_list_entries WHERE list_version_id=%s',(version_id,)).fetchall():
        root=tx.get('entitlements',row['entitlement_id'])
        if root['current_version_id']==row['entitlement_version_id'] and root['business_status']=='awaiting_publication':tx.update('entitlements',root['id'],{'business_status':'available','revision':root['revision']+1});tx.audit('entitlement.published',[('entitlement_version_id',root['current_version_id']),('list_version_id',version_id)])
    tx.audit('list.publish',[('list_version_id',version_id)])


def registry_changed(tx,identity,review):
    for root in tx.db.execute("SELECT * FROM entitlements WHERE household_id=%s AND business_status NOT IN ('cancelled','handed_over')",(identity,)).fetchall():
        if review['action']=='contact_relink':expire_attempts(tx,root['id'],'Household account linkage changed')
        elif review['action'] in {'field_check','facts_correct'} or review['action']=='id_check' and 'identity_check_failed' in root['hold_reasons']:
            d=tx.get('claims',root['claim_id']);version_entitlement(tx,root,tx.get('claim_decisions',d['current_decision_id']),review=review)
