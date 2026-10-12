"""Versioned local review flags and explicitly simulated National ID adapter."""
import re
import unicodedata
from difflib import SequenceMatcher

VERSION='local.flags.v1:name088-address080-person3-id5-phone1-aid5-other4'


def comparison_snapshot(db, household_id, version_id, member_id=None):
    """Freeze only review facts, never raw identity numbers or contact details."""
    root=db.execute('SELECT display_id,revision FROM households WHERE id=%s',(household_id,)).fetchone()
    version=db.execute('SELECT address,declared_barangay_id FROM household_versions WHERE id=%s',(version_id,)).fetchone()
    members=db.execute('SELECT member_id,name,birth_date,is_head FROM member_versions WHERE household_version_id=%s ORDER BY is_head DESC,name,member_id',(version_id,)).fetchall()
    if member_id:members=[m for m in members if m['member_id']==member_id]
    return {'household_id':str(household_id),'display_id':root['display_id'],'registry_version_id':str(version_id),'household_revision':root['revision'],'address':version['address'],'barangay_id':str(version['declared_barangay_id']),'members':[{k:(str(v) if v is not None and k in {'member_id','birth_date'} else v) for k,v in m.items()} for m in members]}


def normalize(value):return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',value or '').casefold()))
def name_score(a,b):return SequenceMatcher(None,normalize(a),normalize(b)).ratio() if a and b else 0
def address_score(a,b):
    a,b=set(normalize(a).split()),set(normalize(b).split())
    return len(a&b)/len(a|b) if a and b else 0


def phone_key(value):
    digits=''.join(re.findall(r'[0-9]',value or ''))
    if len(digits)==12 and digits.startswith('63'):digits='0'+digits[2:]
    elif len(digits)==10 and digits.startswith('9'):digits='0'+digits
    return digits


def run(tx,submission,round_id,purpose='review'):
    claim=tx.get('claims',submission['claim_id']);registry=tx.get('household_versions',submission['registry_version_id'])
    flags=[];seen=set()
    def flag(code,weight,household=None,member=None,link=None,scores=None,source_member=None,candidate_version=None):
        key=(code,household,member,link)
        if key in seen:return
        evidence=dict(scores or {})
        if household:
            candidate_version=candidate_version or tx.get('households',household)['current_version_id']
            evidence['comparison']={'source':comparison_snapshot(tx.db,claim['household_id'],registry['id'],source_member),'candidate':comparison_snapshot(tx.db,household,candidate_version,member),'source_link_version_id':str(submission['link_version_id']) if code=='phone_shared_over_three' else None,'candidate_link_version_id':str(link) if link else None}
            if code=='reused_id':evidence['id_number_match']=True
            if code=='phone_shared_over_three':evidence['phone_match']=True
        seen.add(key);flags.append({'code':code,'weight':weight,'matched_household_id':household,'matched_member_id':member,'matched_link_version_id':link,'scores':evidence})
    own=tx.db.execute('SELECT * FROM member_versions WHERE household_version_id=%s',(registry['id'],)).fetchall()
    others=tx.db.execute('''SELECT m.*,h.id household_id,v.address,v.id_number,v.declared_barangay_id FROM households h JOIN household_versions v ON v.id=h.current_version_id JOIN member_versions m ON m.household_version_id=v.id WHERE h.run_id=%s AND h.id!=%s''',(tx.context.run_id,claim['household_id'])).fetchall()
    for member in own:
        for other in others:
            score=name_score(member['name'],other['name'])
            if member['birth_date'] and other['birth_date'] and member['birth_date']==other['birth_date'] and score>=.88:
                flag('person_in_two_households',3,other['household_id'],other['member_id'],scores={'name_similarity':format(score,'.4f'),'birth_date_match':True},source_member=member['member_id'])
    if normalize(registry['id_number']):
        for other in others:
            if normalize(other['id_number'])==normalize(registry['id_number']):flag('reused_id',5,other['household_id'])
    link=tx.get('household_link_versions',submission['link_version_id']) if submission['link_version_id'] else None
    if link and phone_key(link['phone']):
        links=tx.db.execute('SELECT v.* FROM household_links l JOIN household_link_versions v ON v.id=l.link_version_id WHERE l.run_id=%s',(tx.context.run_id,)).fetchall()
        shared=[v for v in links if phone_key(v['phone'])==phone_key(link['phone'])]
        if len({v['household_id'] for v in shared})>3:
            for v in shared:
                if v['household_id']!=claim['household_id']:flag('phone_shared_over_three',1,v['household_id'],link=v['id'])
    aided=tx.db.execute("SELECT c.id,c.household_id,v.id registry_version_id,v.declared_barangay_id,v.address,m.name FROM claims c JOIN claim_submissions s ON s.id=c.current_submission_id JOIN household_versions v ON v.id=s.registry_version_id JOIN member_versions m ON m.household_version_id=v.id AND m.is_head WHERE c.run_id=%s AND c.disaster_id=%s AND c.business_status='approved'",(tx.context.run_id,claim['disaster_id'])).fetchall()
    head=next(v for v in own if v['is_head'])
    for row in aided:
        if row['household_id']==claim['household_id']:
            if purpose=='duplicate_attempt':flag('already_approved_or_handed_over',5,row['household_id'],candidate_version=row['registry_version_id'])
        elif row['declared_barangay_id']!=registry['declared_barangay_id']:
            n,a=name_score(head['name'],row['name']),address_score(registry['address'],row['address'])
            if n>=.88 and a>=.80:flag('aid_in_other_barangay',4,row['household_id'],scores={'name_similarity':format(n,'.4f'),'address_similarity':format(a,'.4f')},candidate_version=row['registry_version_id'])
    if registry['assister_id']:flag('assisted_registration',1)
    if registry['identity_state']=='pending_field_check':flag('identity_field_check_pending',1)
    reviewers=tx.db.execute('''SELECT a.id,m.household_id member_household_id,l.household_id linked_household_id
      FROM actors a JOIN actor_versions v ON v.id=a.current_version_id
      LEFT JOIN actor_member_links ml ON ml.id=a.current_member_link_id
      LEFT JOIN household_members m ON m.id=ml.member_id
      LEFT JOIN household_links l ON l.beneficiary_actor_id=a.id
      WHERE a.run_id=%s AND a.role='dswd' AND v.status='active' ''',(tx.context.run_id,)).fetchall()
    if not any(r['member_household_id']!=claim['household_id'] and r['linked_household_id']!=claim['household_id'] for r in reviewers):
        flag('independent_dswd_reviewer_unavailable',1)
    responses=tx.db.execute('SELECT * FROM claim_responses WHERE round_id=%s ORDER BY created_at,id',(round_id,)).fetchall()
    if any(v['related_declared'] for v in responses):flag('relative_declared',1)
    if any(v['category_disputed'] for v in responses):flag('category_disputed',1)
    revision=tx.db.execute('SELECT check_data_revision FROM field_offices WHERE id=%s',(tx.context.office_id,)).fetchone()['check_data_revision']
    row=tx.insert('check_runs',{'submission_id':submission['id'],'round_id':round_id,'purpose':purpose,'algorithm_version':VERSION,'compared_data_revision':revision,'risk_score':sum(v['weight'] for v in flags),'simulation_adapter':'Simulated National ID check','simulation_result':{'simulated':True,'identity_verified':False,'result':'not_connected_to_identity_authority','limitations':'No live identity dataset or authentication.'},'simulated':True})
    for f in flags:tx.insert('check_flags',dict(f,check_run_id=row['id']))
    tx.audit('claim.check',[('check_run_id',row['id'])]);return row
