import {test,expect} from '@playwright/test';
import {beneficiaryStory,currentIntegrity,integrityFilter,storyHref,StoryInput} from '../components/mvp/Storytelling';

// Presentation-only synthetic projections: these never establish chain evidence.
const base:StoryInput={disaster:'d',today:'2026-10-14',households:[{id:'h',declared_barangay_id:'b'}],claims:[],entitlements:[],transactions:[],sessions:[],intake:[{id:'i',disaster_id:'d',business_status:'open',barangay_ids:['b']}]};
const entitlement={id:'e',household_id:'h',current_version_id:'v',transaction_id:'t',business_status:'available',amount_centavos:'125000',hold_reasons:[]};
const session={id:'s',business_status:'open',date:'2026-10-14',site:'Invented site',entries:[{entitlement_id:'e',entitlement_version_id:'v',transaction_id:'t'}]};
const transaction={id:'t',entitlement_id:'e',household_id:'h',business_status:'available',amount_centavos:'125000',current_attempt:null,receipt:null};
const payout:StoryInput={...base,claims:[{id:'c',household_id:'h',business_status:'approved'}],entitlements:[entitlement],transactions:[transaction],sessions:[session]};
test('no household offers registration, known open coverage offers application',()=>{
  expect(beneficiaryStory({...base,households:[]}).state).toBe('no_household');
  expect(beneficiaryStory(base).state).toBe('ready_to_apply');
});
test('missing reads never become empty success',()=>{
  expect(beneficiaryStory({...base,households:[],unavailable:true})).toMatchObject({state:'unavailable',action:{kind:'refresh'}});
});
test('ambiguous intake does not invent coverage or permit submission',()=>{
  for(const intake of [undefined,[],[{id:'i',business_status:'open',disaster_id:'d',barangay_ids:['other']}],[...base.intake!,...base.intake!]]){
    const result=beneficiaryStory({...base,intake});
    expect(result.state).toBe('intake_unavailable');expect(result.action.section).toBe('outcomes');
  }
});
test('known closed intake says closed, never guesses an ambiguous cause',()=>{
  expect(beneficiaryStory({...base,intake:[{...base.intake![0],business_status:'closed'}]}).message.en).toContain('closed');
  expect(beneficiaryStory({...base,intake:undefined}).message.en).toContain('cannot confirm');
});
test('under review identifies next responsible role and exact claim',()=>{
  for(const [business_status,owner] of [['waiting_barangay','barangay'],['awaiting_dswd','dswd'],['referred','barangay']]){
    expect(beneficiaryStory({...base,claims:[{id:'c',household_id:'h',business_status}]})).toMatchObject({state:'under_review',owner,action:{section:'claims',record:'c'}});
  }
});
test('decline names reason and resubmission requires known unused allowance and open coverage',()=>{
  const claim={id:'c',household_id:'h',business_status:'declined',resubmissions:0,current_decision_id:'q',decisions:[{id:'q',action:'decline',reason:'Invented missing damage evidence'}]};
  const result=beneficiaryStory({...base,claims:[claim]});
  expect(result).toMatchObject({state:'declined',reason:'Invented missing damage evidence',action:{section:'claims',record:'c'}});
  expect(result.action.label.en).toContain('new information');
  for(const input of [{...base,claims:[{...claim,resubmissions:1}]},{...base,claims:[{...claim,resubmissions:undefined}]},{...base,intake:[],claims:[claim]}])expect(beneficiaryStory(input).action.label.en).toBe('View decision');
});
test('an unknown amount is never presented as zero or payout availability',()=>{
  expect(beneficiaryStory({...payout,entitlements:[{...entitlement,amount_centavos:null}]})).toMatchObject({state:'amount_pending',amount:null,owner:'dswd'});
});
test('publication and appointment waiting remain distinct',()=>{
  expect(beneficiaryStory({...payout,entitlements:[{...entitlement,business_status:'awaiting_publication'}],transactions:[{...transaction,business_status:'awaiting_publication'}]}).state).toBe('awaiting_publication');
  expect(beneficiaryStory({...payout,sessions:[]}).state).toBe('awaiting_appointment');
});
test('scheduled appointment never implies available authorization',()=>{
  expect(beneficiaryStory({...payout,sessions:[{...session,business_status:'scheduled',date:'2026-10-15'}]})).toMatchObject({state:'appointment_scheduled',action:{section:'sessions',record:'s'}});
});
test('exact current version and open Manila date provide a guarded record destination',()=>{
  expect(beneficiaryStory(payout)).toMatchObject({state:'payout_available',action:{section:'payouts',record:'t'}});
  expect(beneficiaryStory(payout).message.en).toContain('checked again');
});
test('closed, cancelled, past open and stale version sessions never offer a code',()=>{
  for(const changed of [{business_status:'closed'},{business_status:'cancelled'},{date:'2026-10-13'},{entries:[{...session.entries[0],entitlement_version_id:'old'}]}])expect(beneficiaryStory({...payout,sessions:[{...session,...changed}]}).state).not.toBe('payout_available');
});
test('session array order and historical appointments do not select the wrong task',()=>{
  const history={...session,id:'old',business_status:'closed',date:'2026-10-13'};
  for(const sessions of [[history,session],[session,history]])expect(beneficiaryStory({...payout,sessions}).session?.id).toBe('s');
});
test('two live assignments, missing version and conflicting amounts fail conservatively',()=>{
  const inputs=[{...payout,sessions:[session,{...session,id:'s2'}]},{...payout,entitlements:[{...entitlement,current_version_id:undefined}]},{...payout,transactions:[{...transaction,amount_centavos:'100'}]}];
  for(const input of inputs)expect(beneficiaryStory(input).state).toBe('unavailable');
});
test('summary-only transaction, malformed amount and conflicting state cannot establish authorization readiness',()=>{
  const {current_attempt,receipt,...summary}=transaction;
  for(const input of [{...payout,transactions:[summary]},{...payout,transactions:[{...transaction,business_status:'in_transaction'}]}])expect(beneficiaryStory(input).state).toBe('unavailable');
  for(const amount_centavos of ['0','-1','unknown'])expect(beneficiaryStory({...payout,entitlements:[{...entitlement,amount_centavos}],transactions:[{...transaction,amount_centavos}]}).state).toBe('unavailable');
  expect(beneficiaryStory({...payout,transactions:[{...transaction,business_status:'held'}]}).state).toBe('held');
});
test('holds and stopped comparisons outrank an open session',()=>{
  expect(beneficiaryStory({...payout,entitlements:[{...entitlement,business_status:'held',hold_reasons:['identity_check_failed']}]})).toMatchObject({state:'held',owner:'dswd'});
  expect(beneficiaryStory({...payout,transactions:[{...transaction,current_attempt:{business_status:'stopped'}}]})).toMatchObject({state:'stopped',owner:'dswd'});
});
test('ordinary expired code differs from stopped ID comparison',()=>{
  expect(beneficiaryStory({...payout,transactions:[{...transaction,current_attempt:{business_status:'expired'}}]})).toMatchObject({state:'code_expired',action:{section:'payouts',record:'t'}});
});
test('already-open authorization guides cash counting without generating another code',()=>{
  expect(beneficiaryStory({...payout,entitlements:[{...entitlement,business_status:'in_transaction'}],transactions:[{...transaction,business_status:'in_transaction',current_attempt:{business_status:'presented'}}]}).state).toBe('authorization_open');
});
test('handover wins over conflicting current payable or held projections',()=>{
  for(const business_status of ['available','held']){
    const result=beneficiaryStory({...payout,entitlements:[{...entitlement,business_status}],transactions:[{...transaction,receipt:{id:'r',amount_centavos:'125000'}}]});
    expect(result).toMatchObject({state:'handover_recorded',action:{section:'outcomes',record:'t'}});
    expect(result.message.en).toContain('Do not repeat');
  }
});
test('transaction, entitlement or attempt handed-over status each blocks another payout',()=>{
  for(const input of [{...payout,transactions:[{...transaction,business_status:'handed_over'}]},{...payout,entitlements:[{...entitlement,business_status:'handed_over'}]},{...payout,transactions:[{...transaction,current_attempt:{business_status:'handed_over'}}]}])expect(beneficiaryStory(input).state).toBe('handover_recorded');
});
test('a full answer never closes an open separate case',()=>{
  const result=beneficiaryStory({...payout,transactions:[{...transaction,business_status:'handed_over'}],answer:'received_full',caseStatus:'open'});
  expect(result.state).toBe('answer_recorded');expect(result.message.en).toContain('open');expect(result.message.en).toContain('does not close');
});
test('unknown answer context never implies that cash was handed over',()=>{
  expect(beneficiaryStory({...payout,answer:'received_full'}).state).toBe('unavailable');
});
test('lost write response prioritizes reading saved transaction before any retry',()=>{
  expect(beneficiaryStory({...payout,uncertainWrite:true})).toMatchObject({state:'interrupted',action:{kind:'refresh',section:'payouts',record:'t'}});
});
test('record href preserves context and encodes only opaque record identity',()=>{
  const link=storyHref(section=>`/mvp/beneficiary/${section}?account=actor&disaster=d#old`,{section:'claims',record:'opaque / record',kind:'navigate',label:{en:'View',fil:'Tingnan'}});
  expect(link).toBe('/mvp/beneficiary/claims?account=actor&disaster=d&record=opaque+%2F+record#old');
});
test('unrecognized records and multiple own household records do not infer readiness',()=>{
  expect(beneficiaryStory({...base,households:[...base.households,{id:'h2'}]}).state).toBe('unavailable');
  expect(beneficiaryStory({...payout,entitlements:[{...entitlement,business_status:'unexpected'}]}).state).toBe('unavailable');
});
test('integrity only regards an actual current matching response as a current match',()=>{
  expect(currentIntegrity(undefined).state).toBe('not_checked');
  expect(currentIntegrity({status:'complete',value:{result:'match'},checkedAt:'now'})).toMatchObject({state:'match',verified:true});
  for(const status of ['checking','failed'] as const)expect(currentIntegrity({status,lastMatchAt:'earlier'})).toMatchObject({verified:false,earlierMatchAt:'earlier'});
  expect(currentIntegrity({status:'complete',value:{result:'chain_unreachable'},lastMatchAt:'earlier'})).toMatchObject({state:'chain_unreachable',verified:false,earlierMatchAt:'earlier'});
});
test('proof filter semantics keep all unresolved states separate',()=>{
  for(const state of ['match','mismatch','required_anchor_absent','chain_unreachable','evidence_unavailable','not_checked','checking','refresh_failed']){
    expect(integrityFilter(state,'all')).toBe(true);expect(integrityFilter(state,'match')).toBe(state==='match');
  }
  expect(integrityFilter('refresh_failed','evidence_unavailable')).toBe(false);
  expect(currentIntegrity({status:'complete',value:{result:'unexpected'}}).verified).toBe(false);
});
