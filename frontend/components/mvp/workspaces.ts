export type NavItem={key:string;label:string;icon:string;hidden?:boolean};
export type WorkspaceConfig={role:string;label:string;description:string;navigation:NavItem[]};
// Group routes without removing deep links or permitted secondary capabilities.
export const beneficiaryDestinations=[
  {key:'overview',label:'My assistance',fil:'Ayuda ko',icon:'house',sections:['overview','sessions','payouts']},
  {key:'registry',label:'Our information',fil:'Impormasyon namin',icon:'users',sections:['registry']},
  {key:'claims',label:'Records',fil:'Mga tala',icon:'clipboard',sections:['claims','lists','queues']},
  {key:'outcomes',label:'Ask for help',fil:'Humingi ng tulong',icon:'message',sections:['outcomes']},
];
export const staffDestinations:Record<string,string[]>={barangay:['overview','claims','registry','lists'],dswd:['overview','claims','sessions','outcomes'],disbursing:['overview','payouts','sessions','outcomes'],auditor:['overview','queues','audit']};
const nav=(key:string,label:string,icon:string,hidden?:boolean):NavItem=>({key,label,icon,...(hidden?{hidden}:{})});
// Auditor record pages stay routable from Records and exception links, outside the menu.
const record=(key:string,label:string,icon:string)=>nav(key,label,icon,true);
export const workspaces:Record<string,WorkspaceConfig>={
  beneficiary:{role:'beneficiary',label:'Beneficiary',description:'Follow your claim, prepare for payout, and confirm what you received.',navigation:[nav('queues','Search & task queues','list'),nav('overview','My assistance','house'),nav('registry','My household','users'),nav('claims','My claim','clipboard'),nav('lists','Entitlement & lists','list'),nav('sessions','Payout appointment','calendar'),nav('payouts','Authorization & receipt','receipt'),nav('outcomes','Private reports','message')]},
  'barangay-officer':{role:'barangay',label:'Barangay Officer',description:'Confirm residence and affectedness, endorse claims, and submit batches.',navigation:[nav('queues','Search & task queues','list'),nav('overview','Barangay overview','house'),nav('claims','Claim responses','clipboard'),nav('registry','Households','users'),nav('lists','Approved list','list')]},
  'dswd-officer':{role:'dswd',label:'DSWD Officer',description:'Connect funding, fair decisions, approved lists, and payout operations.',navigation:[nav('queues','Search & task queues','list'),nav('overview','Operations overview','house'),nav('funds','Funding ledger','landmark'),nav('registry','Households & intake','users'),nav('claims','Claim review','clipboard'),nav('lists','Amounts & approved lists','list'),nav('sessions','Payout sessions','calendar'),nav('payouts','Payout records','receipt'),nav('outcomes','Private cases','message'),nav('audit','Evidence & history','shield')]},
  'disbursing-officer':{role:'disbursing',label:'Disbursing Officer',description:'Work assigned sessions, compare identity, and record authorized handovers.',navigation:[nav('queues','Search & task queues','list'),nav('overview','My work today','house'),nav('sessions','Assigned sessions','calendar'),nav('payouts','Cash handover','hand'),nav('outcomes','Exit checks & notes','clipboard')]},
  auditor:{role:'auditor',label:'Auditor',description:'Follow exceptions to the evidence and independently check record integrity.',navigation:[nav('overview','Inspect','scan'),nav('queues','Records','list'),nav('audit','Verify','shield'),record('funds','Funding ledger','landmark'),record('claims','Claim decisions','clipboard'),record('registry','Household records','users'),record('lists','Amount and list history','list'),record('sessions','Payout sessions','calendar'),record('payouts','Recorded handovers','receipt'),record('outcomes','Recipient outcomes','message')]}
};
