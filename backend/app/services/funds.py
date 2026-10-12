"""Funding authority ledger, independent of physical cash and handover totals."""
import re
import secrets
from uuid import uuid4
from ..actor import require_role
from ..commands import DomainError,RecordedRefusal
from .evidence import link_evidence,original_bytes
from .commitments import document_commitment,freeze_commitment

MAX=9000000000000000000


def money(value,*,zero=False):
    if not isinstance(value,str) or not re.fullmatch(r'0|[1-9][0-9]*',value): raise DomainError(422,'centavo_decimal_string_required')
    n=int(value)
    if n>MAX or (n==0 and not zero): raise DomainError(422,'amount_out_of_range')
    return n


def parse_words(words):
    if not words: return None
    small=dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(),range(20)))
    small.update(dict(zip('twenty thirty forty fifty sixty seventy eighty ninety'.split(),range(20,100,10))))
    tokens=re.findall('[a-z]+',words.lower().replace('-',' '))
    if not tokens or any(t not in small and t not in {'hundred','thousand','million','billion','pesos','peso','only','and'} for t in tokens):return None
    if not any(t in small for t in tokens): return None
    total=chunk=0
    for token in tokens:
        if token in small: chunk+=small[token]
        elif token=='hundred': chunk=(chunk or 1)*100
        elif token in {'thousand','million','billion'}: total+=(chunk or 1)*{'thousand':1000,'million':1000000,'billion':1000000000}[token];chunk=0
    value=(total+chunk)*100
    return str(value) if value<=MAX else None


def review(req,source):
    extracted=source['extracted_fields'] or {}
    machine=extracted.get('amount_centavos')
    words=req.get('document_words') or extracted.get('document_words')
    parsed=parse_words(words)
    figures=req.get('document_figures_centavos') or machine
    state='unknown' if parsed is None or figures is None else 'consistent' if parsed==figures else 'disagree'
    return {'machine_amount_centavos':machine,'document_words':words,'parsed_words_centavos':parsed,'document_figures_centavos':figures,
            'words_value_source':'manual' if req.get('document_words') else 'machine','words_figures_state':state,
            'amount_overridden':machine is not None and machine!=req['amount_centavos']}


def context_for(tx,disaster):
    row=tx.db.execute('SELECT c.public_context FROM commitments c JOIN fund_entries f ON f.id=c.fund_entry_id WHERE f.disaster_id=%s ORDER BY f.created_at,f.id LIMIT 1',(disaster,)).fetchone()
    return row['public_context'] if row else secrets.token_bytes(32)


def validate(tx,req,root=None):
    require_role(tx.context,'dswd')
    tx.get('disasters',req['disaster_id'])
    amount=money(req['amount_centavos'])
    if req['document_type'].strip().lower() in {'nta','notice of transfer of allocation'}:raise DomainError(422,'supporting_document_is_not_release')
    for field in ['document_type','reference_number','purpose','covered_area']:
        if not str(req[field]).strip(): raise DomainError(422,'release_fields_required')
    if not req['signatories']: raise DomainError(422,'printed_signatory_required')
    if req.get('document_figures_centavos') is not None: money(req['document_figures_centavos'],zero=True)
    if req.get('area_lines') and sum(money(v['amount_centavos'],zero=True) for v in req['area_lines'])!=amount: raise DomainError(422,'area_breakdown_must_equal_amount')
    evidence=[tx.get('evidence_versions',i) for i in [req['source_evidence_id'],*req['supporting_evidence_ids']]]
    if len({r['byte_sha256'] for r in evidence})!=len(evidence): raise DomainError(422,'repeated_document_in_entry')
    for item in evidence:
        original_bytes(item)
        use=tx.db.execute('SELECT * FROM release_document_uses WHERE run_id=%s AND byte_sha256=%s',(tx.context.run_id,item['byte_sha256'])).fetchone()
        if use and use['source_root_id']!=root:
            targets=[('fund_entry_id',use['source_root_id']),('evidence_version_id',item['id'])]
            tx.audit('fund.duplicate_refused',targets,reason='Document already backs an independent release')
            raise RecordedRefusal(409,'duplicate_release_document',targets)
    return amount,evidence


def entry(tx,req,kind,delta,identity,root,original=None,correction=None,evidence=(),provenance=None):
    row=tx.insert('fund_entries',{'id':identity,'disaster_id':req['disaster_id'],'kind':kind,'delta_centavos':delta,'source_root_id':root,
        'original_entry_id':original,'correction_set_id':correction,'document_type':req['document_type'],'reference_number':req['reference_number'],
        'issued_date':req['issued_date'],'purpose':req['purpose'],'covered_area':req['covered_area'],'extracted_fields':evidence[0]['extracted_fields'],
        'confirmed_fields':provenance['confirmed_fields'] if provenance else {'amount_centavos':str(abs(delta)),'human_confirmed':True},'amount_review':provenance['amount_review'] if provenance else review(dict(req,amount_centavos=str(abs(delta))),evidence[0]),'entered_by':tx.context.actor_id,'approved_by':None})
    for ordinal,s in enumerate(req['signatories']):
        tx.insert('fund_signatories',{'entry_id':identity,'ordinal':ordinal,'printed_name':s['printed_name'],'printed_role':s['printed_role'],'signature_state':'not_validated','validation_evidence_id':None})
    for ordinal,line in enumerate(req['area_lines']): tx.insert('fund_area_lines',dict(line,entry_id=identity,ordinal=ordinal,amount_centavos=money(line['amount_centavos'],zero=True)))
    for ordinal,item in enumerate(evidence):
        role='release_source' if ordinal==0 else 'supporting'
        link_evidence(tx,item['id'],'fund_entry_id',identity,role)
        if not tx.db.execute('SELECT 1 FROM release_document_uses WHERE run_id=%s AND byte_sha256=%s',(tx.context.run_id,item['byte_sha256'])).fetchone():
            tx.insert('release_document_uses',{'byte_sha256':item['byte_sha256'],'source_root_id':root,'evidence_version_id':item['id'],'role':'primary' if ordinal==0 else 'supporting'})
        document_commitment(tx,item)
    tx.audit('fund.'+kind,[('fund_entry_id',identity)],req.get('reason'))
    return row


def proof_payload(row,req):
    return {k:row[k] for k in ['id','disaster_id','kind','delta_centavos','source_root_id','original_entry_id','correction_set_id','document_type','reference_number','issued_date','purpose','covered_area','confirmed_fields','amount_review','entered_by','approved_by']} | {'signatories':req['signatories'],'area_lines':req['area_lines']}


def release(tx,req):
    amount,evidence=validate(tx,req)
    identity=uuid4();row=entry(tx,req,'release',amount,identity,identity,evidence=evidence)
    tx.insert('fund_heads',{'source_root_id':identity,'current_entry_id':identity,'revision':0})
    freeze_commitment(tx,'fund_entry_id',identity,'fund_release',proof_payload(row,req),context=context_for(tx,req['disaster_id']),evidence=evidence)
    return [('fund_entry_id',identity)]


def correct(tx,original_id,req):
    require_role(tx.context,'dswd')
    original=tx.get('fund_entries',original_id)
    head=tx.db.execute('SELECT * FROM fund_heads WHERE source_root_id=%s',(original['source_root_id'],)).fetchone()
    tx.revision(head,req['expected_revision'])
    if head['current_entry_id']!=original_id or original['kind']=='reversal': raise DomainError(409,'live_original_required')
    if not req['reason'].strip() or req['disaster_id']!=original['disaster_id']: raise DomainError(422,'correction_reason_scope_required')
    amount,evidence=validate(tx,req,original['source_root_id'])
    old_source=tx.db.execute("SELECT e.* FROM evidence_versions e JOIN evidence_links l ON l.evidence_version_id=e.id WHERE l.fund_entry_id=%s AND l.attachment_role='release_source'",(original_id,)).fetchone()
    if req['correction_kind']=='source_amendment' and evidence[0]['byte_sha256']==old_source['byte_sha256']: raise DomainError(422,'amended_source_required')
    if req['correction_kind']=='transcription' and evidence[0]['byte_sha256']!=old_source['byte_sha256']: raise DomainError(422,'transcription_retains_source')
    set_id,reversal_id,replacement_id=uuid4(),uuid4(),uuid4()
    tx.insert('fund_correction_sets',{'id':set_id,'original_entry_id':original_id,'reversal_entry_id':reversal_id,'replacement_entry_id':replacement_id,'correction_kind':req['correction_kind'],'reason':req['reason']})
    old_req=dict(req,amount_centavos=str(original['delta_centavos']),document_type=original['document_type'],reference_number=original['reference_number'],issued_date=original['issued_date'],purpose=original['purpose'],covered_area=original['covered_area'])
    old_req['signatories']=[{k:s[k] for k in ['printed_name','printed_role']} for s in tx.db.execute('SELECT * FROM fund_signatories WHERE entry_id=%s ORDER BY ordinal',(original_id,)).fetchall()]
    old_req['area_lines']=[{k:str(v[k]) if k=='amount_centavos' else v[k] for k in ['area_code','area_name','amount_centavos']} for v in tx.db.execute('SELECT * FROM fund_area_lines WHERE entry_id=%s ORDER BY ordinal',(original_id,)).fetchall()]
    old_evidence=tx.db.execute('SELECT e.* FROM evidence_versions e JOIN evidence_links l ON l.evidence_version_id=e.id WHERE l.fund_entry_id=%s ORDER BY CASE WHEN l.attachment_role=\'release_source\' THEN 0 ELSE 1 END,e.id',(original_id,)).fetchall()
    reversal=entry(tx,old_req,'reversal',-original['delta_centavos'],reversal_id,original['source_root_id'],original_id,set_id,old_evidence,provenance=original)
    replacement=entry(tx,req,'replacement',amount,replacement_id,original['source_root_id'],original_id,set_id,evidence)
    tx.db.execute('UPDATE fund_heads SET current_entry_id=%s,revision=revision+1 WHERE source_root_id=%s',(replacement_id,original['source_root_id']))
    job=tx.insert('anchor_jobs',{'deployment_id':tx.db.execute('SELECT deployment_id FROM commitments WHERE fund_entry_id=%s',(original_id,)).fetchone()['deployment_id'],'operation':'fund_correction','state':'pending','next_attempt_at':tx.wall_now})
    tx.audit('fund.correction',[('correction_set_id',set_id),('anchor_job_id',job['id'])],req['reason'])
    prior=tx.db.execute('SELECT * FROM commitments WHERE fund_entry_id=%s',(original_id,)).fetchone()
    public_set='0x'+secrets.token_bytes(32).hex()
    for ordinal,row,request,files in [(0,reversal,old_req,old_evidence),(1,replacement,req,evidence)]:
        freeze_commitment(tx,'fund_entry_id',row['id'],'fund_'+row['kind'],dict(proof_payload(row,request),correction_public_id=public_set,correction_kind=req['correction_kind'],reason=req['reason']),context=prior['public_context'],predecessor=prior['id'],evidence=files,job_id=job['id'],ordinal=ordinal)
    return [('correction_set_id',set_id),('fund_entry_id',replacement_id)]


def totals(db,run,disaster):
    received=db.execute('SELECT COALESCE(SUM(delta_centavos),0) n FROM fund_entries WHERE run_id=%s AND disaster_id=%s',(run,disaster)).fetchone()['n']
    approved=db.execute("SELECT COALESCE(SUM(v.amount_centavos),0) n,COUNT(*) FILTER(WHERE v.amount_centavos IS NULL) awaiting FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id WHERE e.run_id=%s AND e.disaster_id=%s AND e.business_status!='cancelled'",(run,disaster)).fetchone()
    return {'received_centavos':str(received),'advanced_centavos':'0','returns_centavos':'0','remaining_centavos':str(received),
            'advanced_returns':'deferred_no_feeding_events','approved_known_subtotal_centavos':str(approved['n']),'awaiting_amount_count':approved['awaiting'],
            'approved_total_complete':approved['awaiting']==0,'approved_exceeds_recorded_authority':approved['n']>received,'cash_certification':'not_implemented'}
