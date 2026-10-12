"""Persisted linkless notices; the SMS adapter is explicitly simulated."""


def deliver(tx,notification):
    n=notification
    if n['state']!='pending':return
    link=tx.get('household_link_versions',n['link_version_id']) if n['link_version_id'] else None
    sms=n['channel']=='simulated_notice_sms'
    if not sms:state='delivered'
    elif not link or not link['phone']:state='no_contact'
    elif link['phone'].endswith('999'):state='failed'
    else:state='delivered'
    # A deterministic named evaluation adapter, never a claim of handset delivery.
    attempt=tx.insert('notification_attempts',{'notification_id':n['id'],'attempt_number':1,'adapter':'Simulated notice SMS' if sms else 'persisted_in_app_notice','simulated':sms,'result':state,'safe_failure':'simulated_delivery_failure' if state=='failed' else 'no_recorded_contact' if state=='no_contact' else None,'attempted_at':tx.now})
    tx.update('notifications',n['id'],{'state':state});tx.audit('notice.result',[('notification_id',n['id'])],details={'simulated':sms,'result':state,'attempt_id':str(attempt['id'])})


def session_notice(tx,session,version,household,purpose):
    link=tx.db.execute('SELECT link_version_id FROM household_links WHERE household_id=%s',(household,)).fetchone()
    for channel in ['in_app','simulated_notice_sms']:
        n=tx.insert('notifications',{'household_id':household,'link_version_id':link['link_version_id'] if link else None,'purpose':purpose,'channel':channel,'content':{'kind':purpose,'date':version['date'].isoformat(),'site':version['site'],'message':'Check your current session after any change. Cash remains an outside physical operation.','disaster_id':str(session['disaster_id'])},'simulated':channel=='simulated_notice_sms','state':'pending','session_version_id':version['id']})
        tx.audit('notice.intent',[('notification_id',n['id']),('session_version_id',version['id'])]);deliver(tx,n)


def due(tx):
    count=0
    for row in tx.db.execute("SELECT * FROM notifications WHERE run_id=%s AND state='pending' ORDER BY created_at,id LIMIT 100",(tx.context.run_id,)).fetchall():deliver(tx,row);count+=1
    return count
