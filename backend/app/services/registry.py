"""Versioned household facts, separate contacts and explicit human intake."""
import secrets
from uuid import uuid4
from ..actor import require_role,require_independent
from ..commands import DomainError
from .evidence import link_evidence


def changed(tx):
    tx.db.execute('UPDATE field_offices SET check_data_revision=check_data_revision+1 WHERE id=%s',(tx.context.office_id,))


def household(db,c,identity):
    row=db.execute('SELECT h.*,v.declared_barangay_id,v.assister_id,v.residence_state FROM households h JOIN household_versions v ON v.id=h.current_version_id WHERE h.id=%s AND h.run_id=%s AND h.office_id=%s',(identity,c.run_id,c.office_id)).fetchone()
    if not row:raise DomainError(404,'record_unavailable')
    return row


def require_endorser(db,c,identity):
    require_role(c,'barangay');row=household(db,c,identity);require_independent(c,identity)
    if c.barangay_id!=row['declared_barangay_id'] or row['assister_id']==c.actor_id:raise DomainError(403,'independent_endorser_required')
    return row


def members(tx,version,identity,values,*,existing=False):
    if not values or sum(bool(v['is_head']) for v in values)!=1:raise DomainError(422,'exactly_one_household_head_required')
    seen=set()
    for value in values:
        member=value.get('member_id')
        if member:
            stored=tx.get('household_members',member)
            if stored['household_id']!=identity or member in seen:raise DomainError(422,'member_household_mismatch')
        else:member=tx.insert('household_members',{'household_id':identity})['id']
        seen.add(member)
        tx.insert('member_versions',{'household_version_id':version,'member_id':member,**{k:value[k] for k in ['name','birth_date','relationship','is_head']}})


def identity_evidence(tx,req,version,beneficiary):
    for field,role in [('head_photo_evidence_id','identity_photo'),('id_evidence_id','identity_document')]:
        if req.get(field):
            item=tx.get('evidence_versions',req[field])
            if item['prepared_for_actor_id']!=beneficiary:raise DomainError(403,'private_evidence_scope_mismatch')
            link_evidence(tx,item['id'],'household_version_id',version,role)


def register(tx,req):
    require_role(tx.context,'beneficiary','barangay','dswd')
    target=req.get('beneficiary_actor_id')
    if tx.context.role=='beneficiary':
        if target not in {None,tx.context.actor_id}:raise DomainError(403,'own_household_only')
        target=tx.context.actor_id
    if target:
        account=tx.get('actors',target)
        if account['role']!='beneficiary' or tx.db.execute('SELECT 1 FROM household_links WHERE beneficiary_actor_id=%s',(target,)).fetchone():raise DomainError(409,'beneficiary_already_linked_or_invalid')
    tx.get('barangays',req['declared_barangay_id'])
    if tx.context.role=='barangay' and tx.context.barangay_id!=req['declared_barangay_id']:raise DomainError(403,'own_barangay_only')
    has_id=bool(req.get('id_type'))
    if has_id and not req.get('id_evidence_id'):raise DomainError(422,'identity_original_required')
    if not has_id and (req.get('id_number') or req.get('id_evidence_id')):raise DomainError(422,'identity_type_required')
    identity,version=uuid4(),uuid4()
    tx.insert('households',{'id':identity,'display_id':'DFC-2026-'+secrets.token_hex(4).upper(),'current_version_id':version,'current_pin_id':None,'registered_without_id':not has_id,'revision':0})
    tx.insert('household_versions',{'id':version,'household_id':identity,'predecessor_id':None,**{k:req[k] for k in ['declared_barangay_id','address','zone','id_type','id_number','head_photo_evidence_id','id_evidence_id']},'residence_state':'unconfirmed','identity_state':'evidence_recorded' if has_id else 'pending_field_check','assister_id':tx.context.actor_id if tx.context.role!='beneficiary' else None,'registry_review_id':None})
    members(tx,version,identity,req['members']);identity_evidence(tx,req,version,target)
    link=tx.insert('household_link_versions',{'household_id':identity,'predecessor_id':None,'beneficiary_actor_id':target,'phone':req.get('phone'),'basis_review_id':None,'reason':'Initial declared contact'})
    tx.insert('household_links',{'household_id':identity,'link_version_id':link['id'],'beneficiary_actor_id':target})
    tx.audit('registry.register',[('household_version_id',version),('link_version_id',link['id'])]);changed(tx)
    return [('household_id',identity)]


def review(tx,identity,req):
    # A barangay officer may only confirm residence of an own-barangay household they are independent of; DSWD reviews everything.
    barangay=tx.context.role=='barangay'
    if barangay:
        if req['action']!='residence_confirm':raise DomainError(403,'barangay_residence_confirm_only')
        require_endorser(tx.db,tx.context,identity)
    else:require_role(tx.context,'dswd');require_independent(tx.context,identity)
    root=tx.get('households',identity);tx.revision(root,req['expected_revision'])
    prior=tx.get('household_versions',root['current_version_id']);action=req['action']
    if barangay and prior['residence_state']!='unconfirmed':raise DomainError(409,'residence_not_awaiting_confirmation')
    if not req['reason'].strip():raise DomainError(422,'review_reason_required')
    current_link=tx.db.execute('SELECT * FROM household_links WHERE household_id=%s',(identity,)).fetchone()
    event_id=uuid4();version_id=None;link_id=None
    if action=='contact_relink':
        if not req.get('person_photo_compared') or not req.get('accepted_id_type'):raise DomainError(422,'checked_relink_required')
        target=req.get('beneficiary_actor_id')
        if target:
            a=tx.get('actors',target)
            occupied=tx.db.execute('SELECT household_id FROM household_links WHERE beneficiary_actor_id=%s',(target,)).fetchone()
            if a['role']!='beneficiary' or occupied and occupied['household_id']!=identity:raise DomainError(409,'beneficiary_already_linked_or_invalid')
        link_id=uuid4()
        tx.insert('household_link_versions',{'id':link_id,'household_id':identity,'predecessor_id':current_link['link_version_id'],'beneficiary_actor_id':target,'phone':req.get('phone'),'basis_review_id':event_id,'reason':req['reason']})
        tx.db.execute('UPDATE household_links SET link_version_id=%s,beneficiary_actor_id=%s WHERE household_id=%s',(link_id,target,identity))
    else:
        version_id=uuid4()
        fields={k:prior[k] for k in ['declared_barangay_id','address','zone','residence_state','identity_state','id_type','id_number','head_photo_evidence_id','id_evidence_id','assister_id']}
        if action in {'residence_confirm','residence_resolve'}:
            if prior['residence_state']=='disputed' and action!='residence_resolve':raise DomainError(409,'dispute_resolution_required')
            fields['residence_state']='confirmed'
        elif action=='residence_dispute':fields['residence_state']='disputed'
        elif action=='field_check':
            if not req.get('field_evidence_id'):raise DomainError(422,'field_check_original_required')
            for k in ['id_type','id_number','head_photo_evidence_id','id_evidence_id']:fields[k]=req.get(k)
            if not all(fields[k] for k in ['id_type','head_photo_evidence_id','id_evidence_id']):raise DomainError(422,'photo_id_originals_required')
            fields['identity_state']='field_checked_with_photo_id'
            if not req.get('person_photo_compared') or not req.get('accepted_id_type'):raise DomainError(422,'identity_comparison_required')
        elif action=='facts_correct':
            for k in ['declared_barangay_id','address','zone']:fields[k]=req.get(k,fields[k])
        elif action=='id_check':
            if not req.get('person_photo_compared') or not req.get('accepted_id_type'):raise DomainError(422,'identity_comparison_required')
        else:raise DomainError(422,'unknown_registry_action')
        tx.insert('household_versions',dict(fields,id=version_id,household_id=identity,predecessor_id=prior['id'],registry_review_id=event_id))
        values=req.get('members') or [dict(row) for row in tx.db.execute('SELECT * FROM member_versions WHERE household_version_id=%s',(prior['id'],)).fetchall()]
        members(tx,version_id,identity,values,existing=True)
        if action=='field_check':identity_evidence(tx,fields,version_id,current_link['beneficiary_actor_id'])
        tx.update('households',identity,{'current_version_id':version_id})
    tx.insert('registry_reviews',{'id':event_id,'household_id':identity,'prior_version_id':prior['id'],'result_version_id':version_id,'action':action,'reason':req['reason'],'accepted_id_type':req.get('accepted_id_type'),'person_photo_compared':req.get('person_photo_compared'),'prior_link_id':current_link['link_version_id'] if link_id else None,'result_link_id':link_id})
    if req.get('field_evidence_id'):link_evidence(tx,req['field_evidence_id'],'registry_review_id',event_id,'field_check')
    targets=[('registry_review_id',event_id)]
    if version_id:targets.append(('household_version_id',version_id))
    if link_id:targets.append(('link_version_id',link_id))
    tx.update('households',identity,{'revision':root['revision']+1});tx.audit('registry.'+action,targets,req['reason']);changed(tx)
    from .entitlements import registry_changed
    registry_changed(tx,identity,tx.get('registry_reviews',event_id))
    return [('household_id',identity)]


def project(db,c,identity,*,identity_open=False):
    root=household(db,c,identity)
    if c.role not in {'dswd','auditor'} and not (c.role=='beneficiary' and c.household_id==identity) and not (c.role=='barangay' and c.barangay_id==root['declared_barangay_id']):raise DomainError(404,'record_unavailable')
    v=db.execute('SELECT * FROM household_versions WHERE id=%s',(root['current_version_id'],)).fetchone()
    view={k:root[k] for k in ['id','display_id','revision','current_version_id']}
    view.update({k:v[k] for k in ['declared_barangay_id','address','zone','residence_state']})
    view['members']=db.execute('SELECT member_id,name,birth_date,relationship,is_head FROM member_versions WHERE household_version_id=%s ORDER BY is_head DESC,name',(v['id'],)).fetchall()
    if c.role!='barangay':
        link=db.execute('SELECT v.* FROM household_link_versions v JOIN household_links l ON l.link_version_id=v.id WHERE l.household_id=%s',(identity,)).fetchone()
        view.update({k:link[k] for k in ['beneficiary_actor_id','phone']});view['link_version_id']=link['id'];view['identity_state']=v['identity_state'];view['registered_without_id']=root['registered_without_id']
        if c.role!='auditor' or identity_open:view.update({k:v[k] for k in ['id_type','id_number','head_photo_evidence_id','id_evidence_id']})
    return view


def open_intake(tx,req):
    require_role(tx.context,'dswd');tx.get('disasters',req['disaster_id'])
    if tx.db.execute('SELECT 1 FROM claim_operations WHERE disaster_id=%s',(req['disaster_id'],)).fetchone():raise DomainError(409,'intake_already_opened')
    if not req['barangay_ids'] or not 0<req['response_hours']<=720:raise DomainError(422,'coverage_duration_required')
    for b in set(req['barangay_ids']):tx.get('barangays',b)
    operation,version=uuid4(),uuid4()
    tx.insert('claim_operations',{'id':operation,'disaster_id':req['disaster_id'],'current_version_id':version,'business_status':'open','revision':0})
    tx.insert('operation_versions',{'id':version,'operation_id':operation,'predecessor_id':None,'action':'open','response_hours':req['response_hours'],'reason':None})
    for b in set(req['barangay_ids']):tx.insert('operation_barangays',{'operation_version_id':version,'barangay_id':b})
    link_evidence(tx,req['basis_evidence_id'],'operation_version_id',version,'operation_basis');tx.audit('intake.open',[('operation_version_id',version)])
    return [('operation_version_id',version)]


def close_intake(tx,identity,req):
    require_role(tx.context,'dswd')
    # Accept the opening version handle, as returned by the command.
    operation=tx.db.execute('SELECT * FROM claim_operations WHERE id=%s OR current_version_id=%s',(identity,identity)).fetchone()
    if not operation:raise DomainError(404,'record_unavailable')
    tx.revision(operation,req['expected_revision'])
    if operation['business_status']!='open' or not req['reason'].strip():raise DomainError(409,'open_intake_reason_required')
    old=tx.get('operation_versions',operation['current_version_id'])
    v=tx.insert('operation_versions',{'operation_id':operation['id'],'predecessor_id':old['id'],'action':'close','response_hours':old['response_hours'],'reason':req['reason']})
    for b in tx.db.execute('SELECT barangay_id FROM operation_barangays WHERE operation_version_id=%s',(old['id'],)).fetchall():tx.insert('operation_barangays',{'operation_version_id':v['id'],'barangay_id':b['barangay_id']})
    tx.update('claim_operations',operation['id'],{'current_version_id':v['id'],'business_status':'closed','revision':operation['revision']+1});tx.audit('intake.close',[('operation_version_id',v['id'])],req['reason'])
    return [('operation_version_id',v['id'])]


def nominate(tx,req):
    require_role(tx.context,'dswd')
    if req['staff_role'] not in {'barangay','disbursing'}:raise DomainError(403,'staff_roles_only')
    identity,version=uuid4(),uuid4();nomination=None
    tx.insert('actors',{'id':identity,'role':req['staff_role'],'display_name':req['display_name'],'email':req.get('email'),'current_version_id':version,'current_member_link_id':None,'revision':0})
    if req['staff_role']=='barangay':
        if not req.get('barangay_id') or not req.get('position') or not req.get('nominator_name') or not req.get('nomination_evidence_id'):raise DomainError(422,'documented_nomination_required')
        nomination=tx.insert('nominations',{'candidate_actor_id':identity,**{k:req[k] for k in ['barangay_id','position','nominator_name']},'entered_by':tx.context.actor_id})['id']
        link_evidence(tx,req['nomination_evidence_id'],'nomination_id',nomination,'nomination')
    tx.insert('actor_versions',{'id':version,'actor_id':identity,'predecessor_id':None,'status':'pending','barangay_id':req.get('barangay_id') if nomination else None,'position':req.get('position') if nomination else None,'nomination_id':nomination,'approved_by':None,'reason':'Human nomination'})
    tx.audit('staff.nominate',[('actor_version_id',version)])
    return [('actor_version_id',version)]


def staff_decision(tx,identity,req):
    require_role(tx.context,'dswd');row=tx.get('actors',identity);tx.revision(row,req['expected_revision'])
    if row['role'] not in {'barangay','disbursing'}:raise DomainError(403,'staff_roles_only')
    prior=tx.get('actor_versions',row['current_version_id']);status=req['status']
    if (prior['status'],status) not in {('pending','active'),('active','deactivated')}:raise DomainError(409,'invalid_staff_transition')
    v=tx.insert('actor_versions',{'actor_id':identity,'predecessor_id':prior['id'],'status':status,**{k:prior[k] for k in ['barangay_id','position','nomination_id']},'approved_by':tx.context.actor_id if status=='active' else prior['approved_by'],'reason':req['reason']})
    tx.update('actors',identity,{'current_version_id':v['id'],'revision':row['revision']+1});tx.audit('staff.'+status,[('actor_version_id',v['id'])],req['reason']);changed(tx)
    if status=='deactivated':invalidate_staff(tx,identity,req['reason'])
    return [('actor_version_id',v['id'])]


def member_link(tx,identity,req):
    require_role(tx.context,'dswd');a=tx.get('actors',identity);m=tx.get('household_members',req['member_id'])
    tx.revision(a,req['expected_revision'])
    if a['role']=='system':raise DomainError(403,'system_link_forbidden')
    prior=tx.db.execute('SELECT id FROM actor_member_links WHERE actor_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(identity,)).fetchone()
    row=tx.insert('actor_member_links',{'actor_id':identity,'member_id':m['id'],'predecessor_id':prior['id'] if prior else None,'basis_review_id':None,'reason':req['reason']})
    tx.update('actors',identity,{'current_member_link_id':row['id'],'revision':a['revision']+1});tx.audit('staff.member_link',[('actor_version_id',a['current_version_id']),('household_version_id',tx.get('households',m['household_id'])['current_version_id'])],req['reason']);changed(tx)
    invalidate_staff(tx,identity,req['reason'],m['household_id'])
    return [('actor_version_id',a['current_version_id'])]


def invalidate_staff(tx,actor,reason,household=None):
    from .entitlements import expire_attempts
    rows=tx.db.execute('''SELECT DISTINCT e.* FROM entitlements e
      JOIN active_session_memberships m ON m.entitlement_id=e.id
      JOIN payout_sessions s ON s.id=m.session_id
      JOIN session_assignments a ON a.session_version_id=s.current_version_id
      WHERE e.run_id=%s AND a.actor_id=%s AND a.assignment_kind='cash'
      AND e.business_status NOT IN ('handed_over','cancelled')''',(tx.context.run_id,actor)).fetchall()
    for e in rows:
        if household is not None and e['household_id']!=household:continue
        expire_attempts(tx,e['id'],'Staff availability or household recusal changed')
        tx.update('entitlements',e['id'],{'business_status':'held','hold_reasons':['staff_assignment_changed'],'revision':e['revision']+1})
        tx.audit('entitlement.staff_hold',[('entitlement_version_id',e['current_version_id'])],reason)
