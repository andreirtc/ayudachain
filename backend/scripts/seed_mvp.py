"""Explicit idempotent reference bootstrap, without claims/funds/ready payouts."""
import secrets
import os
from uuid import uuid4
from backend.app.database import connection
from backend.app.commands import Transaction
from backend.app.actor import ActorContext
from backend.app.config import ROOT
from backend.scripts.register_deployment import register
from backend.scripts.synthetic_evidence import synthetic_pdf
from backend.app.services.evidence import prepare_upload,save_upload,link_evidence


# Reference records for a local evaluation of a single disaster response. All people are fictional.
FIELD_OFFICE='DSWD Field Office'
BARANGAYS=['Silong','Sapa']
DISASTERS=['Typhoon Luntian']
DAMAGE_CATEGORIES=[('totally_damaged','Totally damaged'),('partially_damaged','Partially damaged')]
# Barangay officers alternate Punong Barangay / Barangay Secretary, two per barangay in BARANGAYS order.
NOMINATORS=['Pedro Alvarez','Rosario Cruz']
ACTORS=[
    ('system',['Local scheduler']),
    ('dswd',['Lourdes Villanueva','Ricardo Navarro']),
    ('beneficiary',['Marites Dalisay','Rogelio Bautista','Josefina Manalo','Erlinda Pascual','Ramon Evangelista','Cecilia Agbayani']),
    ('disbursing',['Benito Castillo','Dolores Mercado','Arnel Soriano']),
    ('auditor',['Carmela Aquino','Victor Estrada']),
    ('barangay',['Eduardo Salazar','Felicidad Ramos','Nestor Ocampo','Gloria Tolentino']),
]


def seed():
    with connection(purpose='owner') as db:
        db.execute("SELECT pg_advisory_xact_lock(74632519)")
        if db.execute("SELECT 1 FROM evaluation_runs WHERE state='active'").fetchone():return False
        office,run,system=uuid4(),uuid4(),uuid4()
        db.execute('INSERT INTO field_offices(id,name,revision,check_data_revision) VALUES(%s,%s,0,0)',(office,FIELD_OFFICE))
        db.execute("INSERT INTO evaluation_runs(id,office_id,namespace,state,clock_mode,clock_offset,created_at) VALUES(%s,%s,%s,'active','wall_clock',interval '0',clock_timestamp())",(run,office,secrets.token_bytes(32)))
        tx=Transaction(db,ActorContext(system,run,office,'system','Local scheduler',None,None,None,None,'system'),uuid4())
        barangays=[tx.insert('barangays',{'name':n,'zone_description':None})['id'] for n in BARANGAYS]
        for name in DISASTERS:tx.insert('disasters',{'name':name,'external_reference':None,'current_input_version_id':None,'inputs_locked_at':None,'revision':0})
        for code,label in DAMAGE_CATEGORIES:tx.insert('damage_categories',{'code':code,'label':label})
        actors=[]
        for role,names in ACTORS:
            for ordinal,name in enumerate(names):
                identity=system if role=='system' else uuid4();version=uuid4()
                tx.insert('actors',{'id':identity,'role':role,'display_name':name,'email':None,'current_version_id':version,'current_member_link_id':None,'revision':0})
                nomination=None
                if role=='barangay':
                    if ordinal==0:register(tx,os.environ.get('MVP_DEPLOYMENT_MANIFEST',str(ROOT/'.runtime/deployment.json')))
                    entrant=next(a for a in actors if a['role']=='dswd')
                    approver=[a for a in actors if a['role']=='dswd'][1]
                    nominated=tx.insert('nominations',{'candidate_actor_id':identity,'barangay_id':barangays[ordinal//2],'position':'Punong Barangay' if ordinal%2==0 else 'Barangay Secretary','nominator_name':NOMINATORS[ordinal//2],'entered_by':entrant['id']})
                    nomination=nominated['id']
                    human=Transaction(db,ActorContext(entrant['id'],run,office,'dswd',entrant['name'],None,None,None,None),uuid4())
                    ref=save_upload(human,prepare_upload(synthetic_pdf(f'NOMINATION\nNominee: {name}\nPosition: {nominated["position"]}\nNominator: {nominated["nominator_name"]}'),'application/pdf'),'nomination')[0][1]
                    link_evidence(human,ref,'nomination_id',nomination,'nomination')
                tx.insert('actor_versions',{'id':version,'actor_id':identity,'predecessor_id':None,'status':'active','barangay_id':barangays[ordinal//2] if role=='barangay' else None,'position':('Punong Barangay' if ordinal%2==0 else 'Barangay Secretary') if role=='barangay' else None,'nomination_id':nomination,'approved_by':approver['id'] if role=='barangay' else None,'reason':'Explicit synthetic reference bootstrap'})
                tx.audit('reference.actor',[('actor_version_id',version)])
                actors.append({'id':identity,'role':role,'name':name})
        register(tx,os.environ.get('MVP_DEPLOYMENT_MANIFEST',str(ROOT/'.runtime/deployment.json')))
        db.execute('SET CONSTRAINTS ALL IMMEDIATE')
        return True


if __name__=='__main__':print('Synthetic reference records created' if seed() else 'Reference records already exist; state preserved')
