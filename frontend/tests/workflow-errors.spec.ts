import {test,expect,Page} from '@playwright/test';
import {request} from '../lib/mvp-client';
import {workflowMessage} from '../lib/workflow-errors';

// Controlled error responses test presentation only; no workflow success or
// blockchain observation is supplied and no live business command is sent.
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const disaster=id(20),barangay=id(21),household=id(22),category=id(23);
const roles=['beneficiary','barangay','dswd','disbursing','auditor'];
const slugs=['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor'];
async function errors(page:Page,role:string,code:string,endpoint:string,method='GET'){
  await page.route('**/api/v1/**',async route=>{
    const req=route.request(),path=new URL(req.url()).pathname.replace('/api/v1','');
    if(path===endpoint&&req.method()===method){await route.fulfill({status:409,json:{error:code}});return;}
    const data:Record<string,unknown>={
      '/actors/catalogue':roles.map((r,i)=>({id:id(i+1),role:r,display_name:`Invented ${r}`,status:'active',position:r==='barangay'?'Punong Barangay':null,barangay_id:r==='barangay'?barangay:null})),
      '/disasters':[{id:disaster,name:'Synthetic test disaster'}],
      '/barangays':[{id:barangay,name:'Invented test barangay'}],
      '/categories':[{id:category,name:'Totally damaged'}],
      '/registry':{households:[{id:household,display_id:'DFC-2026-9001',revision:0,address:'Invented lane',zone:'Invented zone',declared_barangay_id:barangay,residence_state:'unconfirmed',members:[{member_id:id(24),name:'Invented test head',birth_date:null,relationship:'head',is_head:true}]}]},
      '/claims':{claims:[]},'/intake':[],'/staff':[],'/sessions':[], '/transactions':[],
      '/registry/csv/template':{content:'name,birth_date,address,zone,declared_barangay_id\n',description:'Synthetic household declaration template.',max_rows:100,max_bytes:262144},
      '/context':{run_id:id(25)},'/audit/proofs':[],'/audit/originals':[],
      '/funds':{entries:[],totals:{}},
    };
    await route.fulfill({json:{data:data[path]??[]}});
  });
  const i=roles.indexOf(role);
  return `/mvp/${slugs[i]}?account=${id(i+1)}&disaster=${disaster}`;
}

for(const language of ['en','fil'])test(`claim rejection gives the Beneficiary a next step in ${language}`,async({page})=>{
  const url=await errors(page,'beneficiary','intake_closed_or_not_covered','/claims','POST');
  await page.goto(url.replace('?', '/claims?'));
  await page.getByLabel('Guidance language / Wika ng gabay').selectOption(language);
  await page.getByLabel('Household',{exact:true}).selectOption(household);
  await page.getByLabel('Stated damage category',{exact:true}).selectOption(category);
  await page.getByLabel('Damage description',{exact:true}).fill('Invented house damage for a copy regression.');
  await page.getByRole('button',{name:'Submit household claim',exact:true}).click();
  const alert=page.locator('main .mvp-error[role="alert"]').first();
  await expect(alert).toContainText(language==='en'?'Ask your Barangay Officer or DSWD':'Magtanong sa Barangay Officer o DSWD');
  await expect(alert).not.toContainText('intake_closed_or_not_covered');
  await expect(alert).not.toContainText('Your action is not confirmed.');
});

const cases=[
  {role:'barangay',section:'claims',code:'independent_endorser_required',endpoint:'/claims',expected:'another independent Barangay Officer'},
  {role:'dswd',section:'registry',code:'intake_closed_or_not_covered',endpoint:'/intake',expected:'Households & intake'},
  {role:'disbursing',section:'payouts',code:'handover_already_recorded',endpoint:'/transactions',expected:'Do not hand over cash again'},
  {role:'auditor',section:'audit',code:'inspection_logging_unavailable',endpoint:'/audit/overview',expected:'inspection could not be logged'},
];
for(const item of cases)test(`${item.role} sees actionable workflow guidance`,async({page})=>{
  const url=await errors(page,item.role,item.code,item.endpoint);
  await page.goto(url.replace('?',`/${item.section}?`));
  const alert=page.locator('main [role="alert"]').first();
  await expect(alert).toContainText(item.expected);
  await expect(alert).not.toContainText(item.code);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

test('unknown API details are not displayed to the user',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>new Response(JSON.stringify({error:'internal_trace_forbidden'}),{status:403});
    await expect(request('/registry',null)).rejects.toThrow('selected account');
    await expect(request('/registry',null)).rejects.not.toThrow('internal_trace_forbidden');
  }finally{globalThis.fetch=saved;}
});

test('a lost write response does not advise repeating physical cash',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>{throw new TypeError('Failed to fetch');};
    await expect(request('/transactions/example/handover',null,undefined,{},'synthetic-test-key')).rejects.toThrow('Do not hand over cash again');
  }finally{globalThis.fetch=saved;}
});

test('a gateway HTML response gets a recovery message',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>new Response('<html>internal gateway trace</html>',{status:502});
    await expect(request('/claims',null)).rejects.toThrow('service');
    await expect(request('/claims',null)).rejects.not.toThrow('Unexpected token');
  }finally{globalThis.fetch=saved;}
});

test('cancelled requests retain AbortError so old views stay silent',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>{throw new DOMException('Aborted','AbortError');};
    await expect(request('/claims',null)).rejects.toHaveProperty('name','AbortError');
  }finally{globalThis.fetch=saved;}
});

test('error presentation retains the API code and status for diagnostics',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>new Response(JSON.stringify({error:'handover_already_recorded'}),{status:409});
    const error=await request('/transactions/example/handover',null,undefined,{},'synthetic-test-key').catch(e=>e);
    expect(error).toMatchObject({code:'handover_already_recorded',status:409,message:expect.stringContaining('Do not hand over cash again')});
  }finally{globalThis.fetch=saved;}
});

test('private lookup failures do not disclose whether the transaction exists',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>new Response(JSON.stringify({error:'record_unavailable'}),{status:404});
    await expect(request('/sessions/example/lookup',null,undefined,{reference:id(30)})).rejects.toThrow('No permitted transaction was found');
  }finally{globalThis.fetch=saved;}
});

test('lost read-only POST replies do not claim a business action may have saved',async()=>{
  const saved=globalThis.fetch;
  try{
    globalThis.fetch=async()=>{throw new TypeError('Failed to fetch');};
    for(const path of ['/integrity/check','/registry/csv/preview','/queues/search','/sessions/example/lookup']){
      await expect(request(path,null,undefined,{})).rejects.toThrow('try loading the current record');
      await expect(request(path,null,undefined,{})).rejects.not.toThrow('may already be saved');
    }
  }finally{globalThis.fetch=saved;}
});

test('missing ID originals tell a Beneficiary to upload, without assigning officer duties',()=>{
  const message=workflowMessage('identity_original_required',{role:'beneficiary'});
  expect(message).toContain('Upload');
  expect(message).not.toContain('record the actual comparison');
});

test('invalid UTF-8 uploads explain how to correct the CSV',async({page})=>{
  const url=await errors(page,'beneficiary','unused_fixture_error','/never');
  await page.goto(url.replace('?', '/registry?'));
  await page.getByText('Import household declarations from CSV',{exact:true}).click();
  await page.getByLabel('Completed UTF-8 CSV file').setInputFiles({name:'synthetic-invalid-encoding.csv',mimeType:'text/csv',buffer:Buffer.from([0xff,0xfe])});
  await expect(page.locator('main .mvp-error[role="alert"]').last()).toContainText('Save the CSV as UTF-8');
  await expect(page.locator('main .mvp-error[role="alert"]').last()).not.toContainText('encoded data was not valid');
});
