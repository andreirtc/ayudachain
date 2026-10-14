/** Presentation of scoped saved records. Commands and their guards remain server-owned. */
export type StoryCopy={en:string;fil:string};
export type StoryAction={section:string;record?:string;kind:'navigate'|'refresh';label:StoryCopy};
export type StoryHousehold={id:string;declared_barangay_id?:string};
export type StoryClaim={id:string;household_id?:string;disaster_id?:string;business_status:string;resubmissions?:number;current_decision_id?:string|null;decisions?:{id:string;action:string;reason:string|null}[]};
export type StoryEntitlement={id:string;household_id?:string;current_version_id?:string;transaction_id?:string;business_status:string;amount_centavos:string|null;hold_reasons?:string[]};
export type StoryTransaction={id:string;entitlement_id?:string;household_id?:string;business_status:string;amount_centavos:string|null;current_attempt?:{business_status:string;expires_at?:string}|null;receipt?:{id:string;amount_centavos?:string}|null};
export type StorySession={id:string;business_status:string;date:string;site:string;entries:{entitlement_id:string;entitlement_version_id?:string;transaction_id?:string}[]};
export type StoryIntake={id:string;disaster_id?:string;business_status:string;barangay_ids?:string[]};
export type StoryInput={disaster?:string;today?:string;households:StoryHousehold[];claims:StoryClaim[];entitlements:StoryEntitlement[];sessions:StorySession[];transactions:StoryTransaction[];intake?:StoryIntake[];answer?:string;caseStatus?:string;unavailable?:boolean;uncertainWrite?:boolean};
export type StoryState='no_household'|'ready_to_apply'|'intake_unavailable'|'under_review'|'declined'|'amount_pending'|'awaiting_publication'|'awaiting_appointment'|'appointment_scheduled'|'payout_available'|'authorization_open'|'code_expired'|'held'|'stopped'|'handover_recorded'|'answer_recorded'|'interrupted'|'unavailable';
export type BeneficiaryStory={state:StoryState;owner:'beneficiary'|'barangay'|'dswd'|'disbursing'|'system';title:StoryCopy;message:StoryCopy;action:StoryAction;amount:string|null;session?:StorySession;reason?:string};
const copy=(en:string,fil:string):StoryCopy=>({en,fil});
const action=(section:string,en:string,fil:string,record?:string,kind:StoryAction['kind']='navigate'):StoryAction=>({section,record,kind,label:copy(en,fil)});
const unavailable=():BeneficiaryStory=>({state:'unavailable',owner:'system',title:copy('Current records unavailable','Hindi makuha ang kasalukuyang mga tala'),message:copy('We cannot safely identify the next step. Refresh the saved records before proceeding.','Hindi matiyak ang ligtas na susunod na hakbang. I-refresh muna ang mga naitalang rekord.'),action:action('overview','Refresh records','I-refresh ang mga tala',undefined,'refresh'),amount:null});

export function beneficiaryStory(input:StoryInput):BeneficiaryStory{
  // Never turn a failed required read or ambiguous own-record selection into an empty state.
  if(input.unavailable||input.households.length>1)return unavailable();
  const h=input.households[0];
  const claims=input.claims.filter(c=>(!input.disaster||!c.disaster_id||c.disaster_id===input.disaster)&&(!h||!c.household_id||c.household_id===h.id));
  const entitlements=input.entitlements.filter(e=>!h||!e.household_id||e.household_id===h.id);
  const transactions=input.transactions.filter(t=>!h||!t.household_id||t.household_id===h.id);
  if(claims.length>1||entitlements.length>1||transactions.length>1)return unavailable();
  const claim=claims[0],e=entitlements[0],transaction=transactions[0];
  if(!h&&(claim||e||transaction))return unavailable();
  if(e&&transaction&&(transaction.entitlement_id&&transaction.entitlement_id!==e.id||e.transaction_id&&e.transaction_id!==transaction.id))return unavailable();
  const record=transaction?.id||e?.transaction_id;
  const amount=e?.amount_centavos??transaction?.amount_centavos??null;
  const result=(state:StoryState,owner:BeneficiaryStory['owner'],title:StoryCopy,message:StoryCopy,next:StoryAction,extra:Partial<BeneficiaryStory>={}):BeneficiaryStory=>({state,owner,title,message,action:next,amount,...extra});
  const paid=!!transaction?.receipt||transaction?.business_status==='handed_over'||transaction?.current_attempt?.business_status==='handed_over'||e?.business_status==='handed_over';
  // Any recorded handover signal blocks another payout, including conflicting projections.
  if(paid){
    if(!record)return unavailable();
    if(input.answer)return result('answer_recorded','dswd',copy('Your receipt answer is recorded','Naitala ang sagot mo tungkol sa natanggap'),copy(`Your answer: ${answerLabel(input.answer,'en')}. ${input.caseStatus?`Separate case status: ${input.caseStatus}. `:''}A full answer does not close a case automatically. Do not repeat cash.`,`Sagot mo: ${answerLabel(input.answer,'fil')}. ${input.caseStatus?`Hiwalay na katayuan ng concern: ${caseLabel(input.caseStatus)}. `:''}Hindi awtomatikong nagsasara ng concern ang sagot na buo ang natanggap. Huwag ulitin ang pag-abot ng pera.`),action('outcomes','View answer and concern','Tingnan ang sagot at concern',record),{amount:transaction?.receipt?.amount_centavos??amount});
    return result('handover_recorded','beneficiary',copy('Handover recorded once','Naitala na ang pag-abot ng pera'),copy('Tell us privately what you actually received. The paying officer cannot see your answer. Do not repeat cash; chain status cannot restore payment.','Sabihin nang pribado ang talagang natanggap mo. Hindi makikita ng nagbayad na opisyal ang sagot. Huwag ulitin ang pag-abot ng pera; hindi nagbabalik ng bayad ang katayuan sa chain.'),action('outcomes','Tell us what you received','Sabihin ang natanggap mo',record),{amount:transaction?.receipt?.amount_centavos??amount});
  }
  if(input.answer)return unavailable();
  if(input.uncertainWrite)return result('interrupted','system',copy('Read the saved record first','Basahin muna ang naitalang rekord'),copy('The last response was interrupted. Read the same transaction before retrying. Do not repeat any physical cash handover.','Naputol ang huling tugon. Basahin ang parehong transaksiyon bago subukang muli. Huwag ulitin ang pisikal na pag-abot ng pera.'),action(record?'payouts':'overview','Read saved records','Basahin ang mga naitalang rekord',record,'refresh'));
  if(!h)return result('no_household','beneficiary',copy('Start with your household','Magsimula sa inyong sambahayan'),copy('Register your household first. Registration is separate from an application for aid.','Irehistro muna ang inyong sambahayan. Hiwalay ang pagpaparehistro sa pag-apply para sa ayuda.'),action('registry','Register my household','Irehistro ang sambahayan'));
  const operations=input.intake?.filter(i=>!input.disaster||i.disaster_id===input.disaster);
  const intake=operations?.length===1?operations[0]:undefined;
  const covered=!!h.declared_barangay_id&&intake?.barangay_ids?.includes(h.declared_barangay_id)===true;
  const mayApply=intake?.business_status==='open'&&covered;
  if(!claim&&!e){
    if(mayApply)return result('ready_to_apply','beneficiary',copy('Apply for assistance','Mag-apply para sa ayuda'),copy('Your household is registered and intake covers your barangay. Describe the damage and submit evidence for human review.','Nakaparehistro na ang sambahayan at sakop ng pagtanggap ng aplikasyon ang inyong barangay. Ilarawan ang pinsala at magbigay ng katibayan para sa pagsusuri.'),action('claims','Apply for assistance','Mag-apply para sa ayuda'));
    const message=intake?.business_status==='closed'?copy('Intake is closed for this disaster. DSWD can explain your available help options.','Sarado na ang pagtanggap ng aplikasyon para sa sakunang ito. Maipapaliwanag ng DSWD ang maaaring tulong.'):intake?.business_status==='open'&&intake.barangay_ids&&h.declared_barangay_id?copy('The saved intake does not cover your declared barangay. Ask DSWD about coverage.','Hindi sakop ng naitalang pagtanggap ng aplikasyon ang idineklarang barangay. Magtanong sa DSWD tungkol sa saklaw.'):copy('We cannot confirm open intake and coverage for your household. Ask DSWD; no application has been submitted.','Hindi matiyak kung bukas at sakop ang inyong sambahayan. Magtanong sa DSWD; wala pang naipapasang aplikasyon.');
    return result('intake_unavailable','dswd',copy('Application intake unavailable','Hindi pa maaaring mag-apply'),message,action('outcomes','Ask for help','Humingi ng tulong'));
  }
  if(claim&&['waiting_barangay','awaiting_dswd','referred'].includes(claim.business_status)){
    if(e)return unavailable();
    const owner=claim.business_status==='awaiting_dswd'?'dswd':'barangay';
    return result('under_review',owner,owner==='dswd'?copy('DSWD is reviewing your application','Sinusuri ng DSWD ang inyong aplikasyon'):claim.business_status==='referred'?copy('Barangay response requested','Hinihintay ang tugon ng Barangay'):copy('Your barangay is reviewing your application','Sinusuri ng Barangay ang inyong aplikasyon'),owner==='dswd'?copy('Your application is saved. DSWD acts next. You do not need to submit it again.','Naitala ang inyong aplikasyon. DSWD ang susunod na kikilos. Hindi kailangang ipasa itong muli.'):copy('Your saved application needs a barangay response. Read the saved progress; DSWD makes the decision afterward.','Kailangan ng tugon ng Barangay ang naitalang aplikasyon. Basahin ang progreso; DSWD ang magpapasya pagkatapos.'),action('claims','View application','Tingnan ang aplikasyon',claim.id));
  }
  if(claim?.business_status==='declined'){
    if(e)return unavailable();
    const decision=claim.current_decision_id?claim.decisions?.find(d=>d.id===claim.current_decision_id):undefined;
    const reason=decision?.action==='decline'?decision.reason||undefined:undefined;
    const resubmit=mayApply&&claim.resubmissions===0;
    return result('declined',resubmit?'beneficiary':'dswd',copy('Your application was declined','Hindi naaprubahan ang inyong aplikasyon'),copy(`${reason?`Reason: ${reason}. `:'Read the saved decision for the recorded reason. '}${resubmit?'You may submit new information once while intake remains open.':'Read the decision or ask DSWD for help. No new submission is currently confirmed as available.'}`,`${reason?`Dahilan: ${reason}. `:'Basahin ang naitalang pasya para sa dahilan. '}${resubmit?'Maaari kayong magpasa ng bagong impormasyon nang isang beses habang bukas ang pagtanggap.':'Basahin ang pasya o humingi ng tulong sa DSWD. Hindi pa matiyak kung maaari ang bagong pagpapasa.'}`),action('claims',resubmit?'Submit new information':'View decision',resubmit?'Magpasa ng bagong impormasyon':'Tingnan ang pasya',claim.id),{reason});
  }
  if(claim&&claim.business_status!=='approved'&&claim.business_status!=='reversed')return unavailable();
  if(claim?.business_status==='reversed'||e?.business_status==='cancelled'||transaction?.business_status==='cancelled')return result('held','dswd',copy('Payout stopped','Itinigil ang payout'),copy('The saved approval or entitlement was cancelled. DSWD must explain the recorded decision. No payout is available.','Kinansela ang naitalang pag-apruba o ayuda. DSWD ang magpapaliwanag ng pasya. Hindi maaaring mag-payout.'),action(claim?'claims':'lists','View recorded decision','Tingnan ang naitalang pasya',claim?.id||e?.id));
  if(e&&!['awaiting_amount','awaiting_publication','available','held','in_transaction'].includes(e.business_status))return unavailable();
  const attempt=transaction?.current_attempt;
  if(attempt?.business_status==='stopped')return result('stopped','dswd',copy('Identity comparison stopped','Itinigil ang paghahambing ng pagkakakilanlan'),copy('DSWD must review the saved stop. Clearance and a distinct later session are required before a fresh attempt. An unused expired code is a different state.','Kailangang suriin ng DSWD ang naitalang paghinto. Kailangan ng clearance at ibang session na ginawa pagkatapos nito bago ang bagong pagtatangka. Iba ito sa nag-expire na hindi nagamit na code.'),action('payouts','View stop and recovery','Tingnan ang paghinto at susunod na hakbang',record));
  if(e?.business_status==='held'||transaction?.business_status==='held'||e?.hold_reasons?.length)return result('held','dswd',copy('Your payout is on hold','Naka-hold ang inyong payout'),copy('DSWD must review the recorded hold and current session or amount versions. Do not generate a code or repeat cash while held.','Kailangang suriin ng DSWD ang naitalang hold at kasalukuyang session o halaga. Huwag gumawa ng code o ulitin ang pag-abot ng pera habang naka-hold.'),action('lists','View hold and amount record','Tingnan ang hold at halaga',e?.id),{reason:e?.hold_reasons?.join(', ')});
  // Missing means unknown even if another projection happens to carry an older amount.
  if(!e||e.amount_centavos===null||e.business_status==='awaiting_amount')return result('amount_pending','dswd',copy('Approved; amount pending','Naaprubahan; hinihintay ang halaga'),copy('DSWD is completing the documented amount calculation. An unknown amount is not zero. No payout is available yet.','Kinukumpleto ng DSWD ang pagkukuwenta na may katibayan. Ang hindi pa alam na halaga ay hindi zero. Hindi pa maaaring mag-payout.'),action('lists','View amount progress','Tingnan ang progreso ng halaga',e?.id),{amount:null});
  if(!/^[1-9][0-9]*$/.test(e.amount_centavos))return unavailable();
  if(transaction&&transaction.amount_centavos!==e.amount_centavos)return unavailable();
  if(transaction&&transaction.business_status!==e.business_status)return unavailable();
  if(e.business_status==='awaiting_publication')return result('awaiting_publication','dswd',copy('Amount recorded; list pending','Naitala ang halaga; hinihintay ang listahan'),copy('DSWD must publish the current approved list with its confirmed anchor. A saved publication request is not a published list.','Kailangang ilathala ng DSWD ang kasalukuyang aprubadong listahan na may nakumpirmang anchor. Ang kahilingan para sa publikasyon ay hindi pa nailathalang listahan.'),action('lists','View amount and list','Tingnan ang halaga at listahan',e.id));
  const candidates=input.sessions.filter(s=>['scheduled','open'].includes(s.business_status)&&s.entries.some(entry=>entry.entitlement_id===e.id));
  if(candidates.length>1)return unavailable();
  const session=candidates[0];
  if(!session)return result('awaiting_appointment','dswd',copy('Waiting for your appointment','Hinihintay ang inyong appointment'),copy('Your amount is recorded. DSWD must schedule a current appointment. Completed or cancelled sessions remain history, not another payout.','Naitala ang halaga. DSWD ang magtatakda ng kasalukuyang appointment. Kasaysayan ang tapos o kanseladong session, hindi panibagong payout.'),action('sessions','View appointments','Tingnan ang mga appointment'));
  const entry=session.entries.find(entry=>entry.entitlement_id===e.id);
  if(!e.current_version_id||!entry?.entitlement_version_id)return unavailable();
  if(entry.entitlement_version_id!==e.current_version_id)return result('held','dswd',copy('Appointment needs an update','Kailangang baguhin ang appointment'),copy('The appointment references an earlier amount version. DSWD must update the session before authorization.','Naunang bersiyon ng halaga ang gamit ng appointment. Kailangang baguhin ng DSWD ang session bago ang pahintulot.'),action('sessions','View appointment','Tingnan ang appointment',session.id));
  const today=input.today||new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Manila',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  if(session.date<today)return result('awaiting_appointment','dswd',copy('Your appointment date has passed','Lumipas na ang petsa ng appointment'),copy('DSWD must review the past appointment. It is not a current authorization to collect cash.','Kailangang suriin ng DSWD ang lumipas na appointment. Hindi ito kasalukuyang pahintulot para tumanggap ng pera.'),action('sessions','View past appointment','Tingnan ang lumipas na appointment',session.id));
  if(session.business_status==='scheduled'||session.date!==today)return result('appointment_scheduled','dswd',copy('Your payout appointment is scheduled','Nakatakda ang inyong payout appointment'),copy(`${session.date} · ${session.site}. Bring your accepted photo ID. Wait until DSWD opens the session on its date; do not generate a code yet.`,`${session.date} · ${session.site}. Dalhin ang tinatanggap na photo ID. Hintaying buksan ng DSWD ang session sa takdang petsa; huwag munang gumawa ng code.`),action('sessions','View appointment and preparation','Tingnan ang appointment at paghahanda',session.id),{session});
  if(!record||!transaction||!('current_attempt' in transaction)||!('receipt' in transaction))return unavailable();
  if(attempt&&!['open','presented','expired'].includes(attempt.business_status))return unavailable();
  if(e.business_status==='in_transaction'&&!attempt)return unavailable();
  if(attempt&&['open','presented'].includes(attempt.business_status))return result('authorization_open','disbursing',copy('Your authorization is already open','Bukas na ang inyong pahintulot'),copy('Keep the active code private. Compare identity and count the cash before sharing the payout code. Refreshing cannot reveal a lost code; read the attempt before any retry.','Panatilihing pribado ang aktibong code. Ihambing ang pagkakakilanlan at bilangin ang pera bago ibahagi ang payout code. Hindi ibinabalik ng refresh ang nawalang code; basahin ang pagtatangka bago subukang muli.'),action('payouts','View current authorization','Tingnan ang kasalukuyang pahintulot',record),{session});
  if(attempt?.business_status==='expired')return result('code_expired','beneficiary',copy('Your unused code expired','Nag-expire ang hindi nagamit na code'),copy('The saved unused authorization expired. Review the current transaction; a fresh attempt requires the same current eligibility and open session checks. No cash handover is implied.','Nag-expire ang naitalang hindi nagamit na pahintulot. Basahin ang kasalukuyang transaksiyon; kailangan pa rin ng bagong pagtatangka ang kasalukuyang pagsusuri sa karapatan at bukas na session. Hindi ito nangangahulugang naiabot na ang pera.'),action('payouts','Review a fresh authorization','Suriin ang bagong pahintulot',record),{session});
  return result('payout_available','beneficiary',copy('Review your payout authorization','Suriin ang inyong payout code'),copy('Your current amount is assigned to today’s open session. Open the authorization task at the site; eligibility, identity evidence and current versions are checked again by the server. Count cash before sharing the code.','Nakatakda ang kasalukuyang halaga sa bukas na session ngayon. Buksan ang gawain para sa pahintulot sa payout site; susuriin muli ng server ang karapatan, katibayan ng pagkakakilanlan at mga bersiyon. Bilangin ang pera bago ibahagi ang code.'),action('payouts','Open payout authorization','Kumuha ng payout code',record),{session});
}

function answerLabel(value:string,language:'en'|'fil'){
  const labels:Record<string,StoryCopy>={received_full:copy('received in full','buo ang natanggap'),received_less:copy('received less','kulang ang natanggap'),not_received:copy('no cash received','walang natanggap na pera'),unconfirmed:copy('not confirmed','hindi pa nakumpirma')};
  return labels[value]?.[language]||value;
}
function caseLabel(value:string){return ({open:'bukas',closed:'sarado',under_review:'sinusuri',reopened:'muling binuksan'} as Record<string,string>)[value]||value;}

/** Preserve actor/disaster/filters and use only opaque, non-secret record context. */
export function storyHref(href:(section:string)=>string,next:StoryAction){
  const path=href(next.section);if(!next.record)return path;
  const hashAt=path.indexOf('#'),hash=hashAt>=0?path.slice(hashAt):'',withoutHash=hashAt>=0?path.slice(0,hashAt):path;
  const queryAt=withoutHash.indexOf('?'),base=queryAt>=0?withoutHash.slice(0,queryAt):withoutHash;
  const query=new URLSearchParams(queryAt>=0?withoutHash.slice(queryAt+1):'');query.set('record',next.record);
  return `${base}?${query}${hash}`;
}

export type IntegrityState='not_checked'|'checking'|'match'|'mismatch'|'required_anchor_absent'|'chain_unreachable'|'evidence_unavailable'|'refresh_failed';
export type StoryIntegrityCheck={status:'checking'|'complete'|'failed';value?:{result:string;checked_at?:string;last_confirmed_observation?:{checked_at:string}};checkedAt?:string;lastMatchAt?:string};
export function currentIntegrity(check?:StoryIntegrityCheck):{state:IntegrityState;verified:boolean;checkedAt?:string;earlierMatchAt?:string;explanation:string}{
  const states:IntegrityState[]=['match','mismatch','required_anchor_absent','chain_unreachable','evidence_unavailable'];
  const raw=check?.value?.result;
  const state:IntegrityState=!check?'not_checked':check.status==='checking'?'checking':check.status==='failed'?'refresh_failed':states.includes(raw as IntegrityState)?raw as IntegrityState:'evidence_unavailable';
  const explanations:Record<IntegrityState,string>={not_checked:'No current integrity read has been made.',checking:'Reading the current chain record; not yet verified.',match:'Committed content matches the chain record.',mismatch:'Committed content does not match.',required_anchor_absent:'Required anchor not found.',chain_unreachable:'Chain could not be read; not verified.',evidence_unavailable:'Required evidence unavailable; not verified.',refresh_failed:'The current refresh failed; not verified. Read again.'};
  return {state,verified:state==='match',checkedAt:check?.status==='complete'?check.checkedAt||check.value?.checked_at:undefined,earlierMatchAt:state!=='match'?check?.lastMatchAt||check?.value?.last_confirmed_observation?.checked_at:undefined,explanation:explanations[state]};
}
/** Filters describe only loaded/check results in this view, never global proof totals. */
export function integrityFilter(state:string,filter:string):boolean{return filter==='all'||state===filter;}
