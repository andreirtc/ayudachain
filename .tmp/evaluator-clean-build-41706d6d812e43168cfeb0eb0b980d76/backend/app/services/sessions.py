"""Immutable session memberships/assignments, with mutable current pointers only."""
from datetime import timedelta,timezone
from uuid import uuid4
from ..actor import require_role,resolve_identity
from ..commands import DomainError
from .entitlements import expire_attempts
from .notifications import session_notice

MANILA=timezone(timedelta(hours=8))


def root(tx,identity):
    row=tx.db.execute('SELECT s.* FROM payout_sessions s LEFT JOIN session_versions v ON v.session_id=s.id WHERE (s.id=%s OR v.id=%s) AND s.run_id=%s LIMIT 1',(identity,identity,tx.context.run_id)).fetchone()
    if not row:raise DomainError(404,'record_unavailable')
    return row


def assignments(tx,values):
    if len(set(values))!=len(values):raise DomainError(422,'distinct_assigned_staff_required')
    for identity in values:
        c=resolve_identity(tx.db,identity)
        if c.run_id!=tx.context.run_id or c.role!='disbursing':raise DomainError(422,'active_disbursing_staff_required')


def publishable_members(tx,list_version,ids,session=None):
    v=tx.get('approved_list_versions',list_version);head=tx.get('list_heads',v['list_head_id'])
    if v['business_status']!='published' or head['current_published_id']!=v['id']:raise DomainError(409,'current_published_list_required')
    if not ids or len(ids)!=len(set(ids)):raise DomainError(422,'distinct_payable_members_required')
    rows=[]
    for identity in ids:
        row=tx.get('approved_list_entries',identity);e=tx.get('entitlements',row['entitlement_id'])
        if row['list_version_id']!=v['id'] or row['entitlement_version_id']!=e['current_version_id'] or e['business_status'] in {'handed_over','cancelled','awaiting_amount'}:raise DomainError(409,'current_unpaid_member_required')
        active=tx.db.execute('SELECT m.*,s.business_status FROM active_session_memberships m JOIN payout_sessions s ON s.id=m.session_id WHERE m.entitlement_id=%s',(e['id'],)).fetchone()
        if active and active['session_id']!=session and active['business_status'] in {'scheduled','open'}:
            cleared=tx.db.execute('''SELECT c.id FROM transaction_clearances c JOIN payout_attempts a ON a.id=c.stopped_attempt_id JOIN payout_transactions t ON t.id=c.transaction_id WHERE t.entitlement_id=%s AND a.id=t.current_attempt_id''',(e['id'],)).fetchone()
            if not cleared:raise DomainError(409,'already_assigned_payable_session')
        rows.append(row)
    return v,head,rows


def create_version(tx,s,action,date,site,list_version,entries,cash,followup,reason):
    if not site.strip():raise DomainError(422,'session_site_required')
    if action not in {'close','cancel','followup_assign'}:assignments(tx,cash)
    if action not in {'close','cancel'}:assignments(tx,followup)
    v=tx.insert('session_versions',{'session_id':s['id'],'predecessor_id':s.get('current_version_id'),'action':action,'date':date,'site':site,'original_list_version_id':list_version,'reason':reason})
    for kind,values in [('cash',cash),('followup',followup)]:
        for identity in values:tx.insert('session_assignments',{'session_version_id':v['id'],'actor_id':identity,'assignment_kind':kind})
    for entry in entries:
        row=tx.insert('session_entries',{'session_version_id':v['id'],'list_entry_id':entry['id'],'entitlement_id':entry['entitlement_id'],'entitlement_version_id':entry['entitlement_version_id']})
        if action not in {'close','cancel','followup_assign'}:
            active=tx.db.execute('SELECT * FROM active_session_memberships WHERE entitlement_id=%s',(entry['entitlement_id'],)).fetchone()
            values={'session_id':s['id'],'session_entry_id':row['id'],'entitlement_version_id':row['entitlement_version_id']}
            if active:
                tx.db.execute('UPDATE active_session_memberships SET session_id=%s,session_entry_id=%s,entitlement_version_id=%s WHERE entitlement_id=%s',(s['id'],row['id'],row['entitlement_version_id'],row['entitlement_id']))
            else:tx.insert('active_session_memberships',dict(values,entitlement_id=row['entitlement_id']))
            e=tx.get('entitlements',row['entitlement_id'])
            stopped=tx.db.execute("SELECT a.id FROM payout_transactions t JOIN payout_attempts a ON a.id=t.current_attempt_id LEFT JOIN transaction_clearances c ON c.stopped_attempt_id=a.id WHERE t.entitlement_id=%s AND a.business_status='stopped' AND c.id IS NULL",(e['id'],)).fetchone()
            cleared_later=tx.db.execute('''SELECT 1 FROM payout_transactions t JOIN payout_attempts a ON a.id=t.current_attempt_id
              JOIN transaction_clearances c ON c.stopped_attempt_id=a.id JOIN session_entries old ON old.id=a.session_entry_id
              JOIN session_versions sv ON sv.id=old.session_version_id
              WHERE t.entitlement_id=%s AND sv.session_id!=%s AND c.created_at<%s''',(e['id'],s['id'],s['created_at'])).fetchone()
            if not stopped and ('identity_check_failed' not in e['hold_reasons'] or cleared_later) and e['current_version_id']==row['entitlement_version_id'] and e['business_status']=='held':
                tx.update('entitlements',e['id'],{'business_status':'available','hold_reasons':[],'revision':e['revision']+1});tx.audit('entitlement.session_updated',[('entitlement_version_id',e['current_version_id']),('session_version_id',v['id'])])
    tx.audit('session.'+action,[('session_version_id',v['id'])],reason)
    return v


def schedule(tx,req):
    require_role(tx.context,'dswd');v,head,entries=publishable_members(tx,req['list_version_id'],req['list_entry_ids'])
    if head['disaster_id']!=req['disaster_id'] or head['barangay_id']!=req['barangay_id']:raise DomainError(422,'session_scope_mismatch')
    identity=uuid4()
    # Deferred root pointer permits the initial immutable version in this transaction.
    version_id=uuid4()
    s=tx.insert('payout_sessions',{'id':identity,'disaster_id':req['disaster_id'],'barangay_id':req['barangay_id'],'current_version_id':version_id,'business_status':'scheduled','revision':0})
    initial=dict(s,current_version_id=None)
    version=create_version(tx,initial,'schedule',req['date'],req['site'],v['id'],entries,req['cash_actor_ids'],req.get('followup_actor_ids',[]),None)
    tx.update('payout_sessions',s['id'],{'current_version_id':version['id']})
    for e in entries:session_notice(tx,s,version,tx.get('entitlements',e['entitlement_id'])['household_id'],'session_scheduled')
    return [('session_version_id',version['id'])]


def change(tx,identity,req):
    require_role(tx.context,'dswd');s=root(tx,identity);tx.revision(s,req['expected_revision']);old=tx.get('session_versions',s['current_version_id']);action=req['action']
    allowed={'scheduled':{'open','cancel','amend','followup_assign'},'open':{'close','cancel','amend','followup_assign'},'closed':{'followup_assign'},'cancelled':{'followup_assign'}}
    if action not in allowed[s['business_status']]:raise DomainError(409,'invalid_session_transition')
    if action not in {'amend','followup_assign'} and any(req.get(k) is not None for k in ['date','site','list_version_id','list_entry_ids','cash_actor_ids','followup_actor_ids']):raise DomainError(422,'amendment_requires_amend_action')
    if action=='followup_assign' and any(req.get(k) is not None for k in ['date','site','list_version_id','list_entry_ids','cash_actor_ids']):raise DomainError(422,'followup_cannot_change_cash_authority')
    if action in {'cancel','amend','followup_assign'} and not (req.get('reason') or '').strip():raise DomainError(422,'session_change_reason_required')
    date=req.get('date') or old['date'];site=req.get('site') or old['site']
    if action=='open' and date!=tx.now.astimezone(MANILA).date():raise DomainError(409,'session_manila_date_required')
    old_entries=tx.db.execute('SELECT l.* FROM session_entries e JOIN approved_list_entries l ON l.id=e.list_entry_id WHERE e.session_version_id=%s ORDER BY e.id',(old['id'],)).fetchall()
    old_cash=[v['actor_id'] for v in tx.db.execute("SELECT actor_id FROM session_assignments WHERE session_version_id=%s AND assignment_kind='cash'",(old['id'],)).fetchall()]
    old_followup=[v['actor_id'] for v in tx.db.execute("SELECT actor_id FROM session_assignments WHERE session_version_id=%s AND assignment_kind='followup'",(old['id'],)).fetchall()]
    cash=req.get('cash_actor_ids') if req.get('cash_actor_ids') is not None else old_cash
    followup=req.get('followup_actor_ids') if req.get('followup_actor_ids') is not None else old_followup
    if action=='followup_assign':cash=old_cash
    list_version=req.get('list_version_id') or old['original_list_version_id'];entries=old_entries
    if action=='amend':
        _,head,entries=publishable_members(tx,list_version,req.get('list_entry_ids') or [e['id'] for e in old_entries],s['id'])
        if head['disaster_id']!=s['disaster_id'] or head['barangay_id']!=s['barangay_id']:raise DomainError(422,'session_scope_mismatch')
    if action!='followup_assign':
        new_by={e['entitlement_id']:e for e in entries}
        for e in old_entries:
            if action in {'close','cancel'} or date!=old['date'] or site!=old['site'] or e['entitlement_id'] not in new_by or new_by[e['entitlement_id']]['entitlement_version_id']!=e['entitlement_version_id']:
                expire_attempts(tx,e['entitlement_id'],'Session closed, cancelled, or affected authority changed')
            elif set(old_cash)-set(cash):
                affected=tx.db.execute('''SELECT 1 FROM payout_attempts a JOIN payout_transactions t ON t.id=a.transaction_id JOIN identity_checks i ON i.id=a.current_id_check_id WHERE t.entitlement_id=%s AND i.checked_by=ANY(%s) AND a.business_status IN ('open','presented')''',(e['entitlement_id'],list(set(old_cash)-set(cash)))).fetchone()
                if affected:expire_attempts(tx,e['entitlement_id'],'Checking officer assignment removed')
    version=create_version(tx,s,action,date,site,list_version,entries,cash,followup,req.get('reason'))
    status={'open':'open','close':'closed','cancel':'cancelled'}.get(action,s['business_status'])
    tx.update('payout_sessions',s['id'],{'current_version_id':version['id'],'business_status':status,'revision':s['revision']+1})
    if action!='open':
        affected={e['entitlement_id'] for e in old_entries+entries}
        for e in affected:session_notice(tx,s,version,tx.get('entitlements',e)['household_id'],'session_'+action)
    return [('session_version_id',version['id'])]
