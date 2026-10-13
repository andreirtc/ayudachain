"""Fresh edited own-device + assisted journeys through an ACTUAL restarted API."""
import unittest
import json
from datetime import datetime
from uuid import uuid4
from backend.tests.support import Harness
from backend.tests.api_process import ActualAPI


class JourneyTests(unittest.TestCase):
    def test_five_roles_fresh_uploads_all_ten_commitments_restart_and_paid_lock(self):
        from backend.scripts.synthetic_evidence import synthetic_pdf,synthetic_portrait
        from backend.app.services.integrity import check_saved
        with Harness() as h:
            h.register_chain()
            with ActualAPI() as api:
                def headers(role,key=None):return {'X-Demo-Actor-ID':str(h.actors[role]),**({'Idempotency-Key':key or str(uuid4())} if key is not None else {})}
                def get(path,role='dswd'):
                    response=api.client.get(path,headers=headers(role));self.assertEqual(response.status_code,200,response.text);return response.json()['data']
                def post(path,data,role='dswd',key=''):
                    response=api.client.post(path,headers=headers(role,key or str(uuid4())),json=json.loads(json.dumps(data,default=str)));self.assertEqual(response.status_code,200,response.text);return response.json()['data']
                def upload(purpose,text='Invented fresh evidence',role='dswd',prepared=None):
                    raw=synthetic_portrait() if purpose=='identity_photo' else synthetic_pdf(text+' '+uuid4().hex)
                    response=api.client.post('/evidence',headers=headers(role,str(uuid4())),data={'purpose':purpose,**({'prepared_for_actor_id':str(prepared)} if prepared else {})},files={'file':('synthetic-original.png' if purpose=='identity_photo' else 'synthetic-original.pdf',raw,'image/png' if purpose=='identity_photo' else 'application/pdf')});self.assertEqual(response.status_code,200,response.text);return response.json()['data']['resources'][0]['id']
                def resource(ack):return ack['resources'][0]['id']
                from backend.tests.test_funds import FundsTests
                release=FundsTests().request(h,upload('release_source','Amount: PHP 200,000.00'),'20123456')
                source=resource(post('/funds/releases',release))
                correction=dict(release,expected_revision=0,reason='Fresh invented transcription adjustment',correction_kind='transcription',amount_centavos='20234567')
                post('/funds/'+source+'/corrections',correction)
                before=get('/intake');self.assertEqual(before,[])
                post('/intake/open',{'disaster_id':h.disasters[0],'barangay_ids':[h.barangays[0]],'response_hours':48,'basis_evidence_id':upload('operation_basis')})
                paid=None
                for assisted in [False,True]:
                    role='beneficiary2' if assisted else 'beneficiary';entrant='barangay' if assisted else role
                    from backend.tests.test_registry import RegistryTests
                    req=RegistryTests().request(h,beneficiary_actor_id=h.actors[role],address='Invented edited site '+('74' if assisted else '39'),zone='9' if assisted else '4',members=[{'name':'Invented Mayumi Sayo' if assisted else 'Invented Lira Agila','birth_date':'1982-04-19' if assisted else '1989-11-07','relationship':'head','is_head':True}])
                    if not assisted:req.update(id_type='Synthetic photo ID',id_number='DFC-2026-ID91',head_photo_evidence_id=upload('identity_photo',role=role,prepared=h.actors[role]),id_evidence_id=upload('identity_document',role=role,prepared=h.actors[role]))
                    household=resource(post('/registry',req,entrant))
                    if assisted:
                        post('/registry/'+household+'/reviews',{'expected_revision':0,'action':'field_check','reason':'Fresh invented documented field comparison','id_type':'Synthetic accepted photo ID','head_photo_evidence_id':upload('identity_photo',prepared=h.actors[role]),'id_evidence_id':upload('identity_document',prepared=h.actors[role]),'field_evidence_id':upload('field_check'),'accepted_id_type':'Synthetic photo ID','person_photo_compared':True})
                        post('/registry/'+household+'/reviews',{'expected_revision':1,'action':'residence_confirm','reason':'Invented independent residence observation'})
                    submission={'household_id':household,'disaster_id':h.disasters[0],'stated_category_id':h.categories[0],'damage_description':'Fresh edited invented damage '+str(assisted),'evidence_ids':[upload('damage',role=entrant)]}
                    post('/claims',submission,entrant)
                    claims=get('/claims?disaster_id='+str(h.disasters[0]))['claims'];claim=next(c for c in claims if c['household_id']==household)
                    round_=claim['rounds'][-1]
                    if not assisted:
                        for responder in ['barangay','barangay2']:post('/claim-rounds/'+round_['id']+'/responses',{'kind':'endorse','residence_attested':True,'affected_attested':True,'category_opinion_id':h.categories[0]},responder)
                        post('/claims/submissions',{'disaster_id':h.disasters[0],'barangay_id':h.barangays[0],'round_ids':[round_['id']],'resolution_evidence_id':upload('council_resolution',role='barangay')},'barangay')
                    if assisted:
                        post('/claim-rounds/'+round_['id']+'/responses',{'kind':'not_endorse','reason':'Invented negative opinion retained for human review'},'barangay2')
                        post('/evaluation/clock',{'advance_hours':48})
                        from backend.app.scheduler import route_overdue
                        route_overdue()
                    claim=get('/claims/'+claim['id'])
                    post('/claims/'+claim['id']+'/decisions',{'expected_revision':claim['revision'],'reviewed_check_id':claim['latest_check']['id'],'action':'approve','category_id':h.categories[0],'reason':'Fresh human review of recorded synthetic flags'})
                    basis={'disaster_id':h.disasters[0],'expected_revision':1 if assisted else 0,'mode':'fixed_category' if assisted else 'wage_formula','wage_centavos':None if assisted else '43500','wage_evidence_id':None if assisted else upload('wage'),'rules':[{'category_id':category,'day_count':None if assisted else 15,'fixed_centavos':'723400' if assisted else None,'evidence_id':upload('fixed_amount' if assisted else 'days')} for category in h.categories],'reason':'Fresh edited documented category basis' if assisted else None}
                    post('/amount-inputs',basis)
                    ent=next(e for e in get('/entitlements?disaster_id='+str(h.disasters[0])) if e['household_id']==household)
                    self.assertEqual(ent['amount_centavos'],'723400' if assisted else '495000')
                    listed=resource(post('/lists',{'disaster_id':h.disasters[0],'barangay_id':h.barangays[0]}));h.drain_anchors()
                    lists=get('/lists?disaster_id='+str(h.disasters[0]));version=next(v for v in lists if v['id']==listed);self.assertEqual(version['business_status'],'published');entry=next(e for e in version['entries'] if e['entitlement_id']==ent['id'])
                    if assisted:self.assertEqual(len(version['entries']),2)
                    from zoneinfo import ZoneInfo
                    session=resource(post('/sessions',{'disaster_id':h.disasters[0],'barangay_id':h.barangays[0],'list_version_id':listed,'list_entry_ids':[entry['id']],'date':datetime.fromisoformat(get('/evaluation/status')['business_utc']).astimezone(ZoneInfo('Asia/Manila')).date(),'site':'Invented edited payout site '+str(assisted),'cash_actor_ids':[h.actors['disbursing'],h.actors['disbursing2']]}))
                    post('/sessions/'+session+'/changes',{'expected_revision':0,'action':'open','reason':'Human opened the invented session'})
                    transaction=get('/transactions/'+ent['transaction_id'],role)
                    if assisted:
                        post('/sessions/'+session+'/id-checks',{'household_id':household,'result':'pass','accepted_id_type':'Synthetic photo ID','person_photo_compared':True},'disbursing')
                        transaction=get('/transactions/'+transaction['id'],role);identity=transaction['identity_checks'][-1]['id']
                        post('/households/'+household+'/assisted-pin',{'identity_check_id':identity,'pin':'592831'},role)
                    opened=post('/entitlements/'+ent['id']+'/attempts',{'expected_revision':transaction['revision'],'path':'assisted' if assisted else 'own_device','pin':'592831' if assisted else None},role,key='opening-'+str(assisted))
                    code=opened['code'];transaction=get('/transactions/'+transaction['id'],role)
                    post('/sessions/'+session+'/id-checks',{'household_id':household,'attempt_id':transaction['current_attempt']['id'],'result':'pass','accepted_id_type':'Synthetic photo ID','person_photo_compared':True},'disbursing')
                    transaction=get('/transactions/'+transaction['id'],'disbursing')
                    handover={'expected_revision':transaction['revision'],'attempt_id':transaction['current_attempt']['id'],'code':code,'checker_actor_id':h.actors['disbursing2'] if assisted else None}
                    with api.client.stream('POST','/transactions/'+transaction['id']+'/handover',headers=headers('disbursing','cash-'+str(assisted)),json=json.loads(json.dumps(handover,default=str))) as dropped_ack:self.assertEqual(dropped_ack.status_code,200)
                    # The committed response body is deliberately not read.
                    api.restart()
                    replay=post('/transactions/'+transaction['id']+'/handover',handover,'disbursing',key='cash-'+str(assisted));self.assertTrue(replay['replayed'])
                    saved=get('/transactions/'+transaction['id'],role);self.assertEqual(saved['receipt']['amount_centavos'],'723400' if assisted else '495000')
                    post('/sessions/'+session+'/changes',{'expected_revision':1,'action':'close','reason':'Human closed cash before private follow-up'})
                    post('/transactions/'+transaction['id']+'/outcomes',{'answer':'received_less' if assisted else 'received_full','expected_latest_id':None},'disbursing2' if assisted else role)
                    if not assisted:paid=saved
                h.drain_anchors()
                history=get('/transactions/'+paid['id'],'beneficiary');self.assertEqual({k:v for k,v in history['receipt'].items() if k!='proofs'},{k:v for k,v in paid['receipt'].items() if k!='proofs'})
                auditor=get('/audit/overview?disaster_id='+str(h.disasters[0]),'auditor');self.assertEqual(auditor['population']['claims'],2)
                self.assertEqual(len(auditor['exceptions']['paid_differences']),1)
                self.assertEqual(len(get('/grievances','auditor')),1)
                with h.connection() as db:
                    kinds=set()
                    for proof in db.execute('SELECT * FROM commitments').fetchall():kinds.add(proof['kind']);self.assertEqual(check_saved(db,proof)['result'],'match',proof['kind'])
                    self.assertEqual(kinds,{'document','amount_input','barangay_submission','system_fallback','approved_list','handover','outcome','fund_release','fund_reversal','fund_replacement'})
                    # The independent verifier has no DB connection or signing key.
                    import os,subprocess
                    from backend.app.services.integrity import manifest_for
                    from backend.app.services.evidence import storage_root
                    from backend.app.config import ROOT
                    verified=set()
                    for proof in db.execute('SELECT * FROM commitments ORDER BY created_at,id').fetchall():
                        if proof['kind'] in verified:continue
                        envelope=json.loads(bytes(proof['canonical_bytes']))
                        originals=[]
                        for d in envelope['evidence']:
                            file=db.execute('SELECT storage_key FROM evidence_versions WHERE id=%s',(d['id'],)).fetchone()
                            originals.append({'id':d['id'],'path':str(storage_root()/file['storage_key'])})
                        material={'canonical_utf8':bytes(proof['canonical_bytes']).decode(),'content_hash':'0x'+proof['content_hash'].hex(),'deployment':manifest_for(db.execute('SELECT * FROM deployments WHERE id=%s',(proof['deployment_id'],)).fetchone()),'originals':originals}
                        env=os.environ.copy();env.pop('MVP_PRIVATE_KEY',None)
                        run=subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/verify_evidence.js')],input=json.dumps(material),capture_output=True,text=True,env=env,timeout=20)
                        self.assertEqual(run.returncode,0,proof['kind']);self.assertEqual(json.loads(run.stdout)['result'],'match',proof['kind']);verified.add(proof['kind'])
