import {test,expect,Page,APIRequestContext} from '@playwright/test';
import {workspacePath,prepareLookupSession} from './workspace-navigation';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

const capabilityActor={id:'00000000-0000-4000-8000-000000000001',role:'disbursing',display_name:'Invented capability tester',status:'active',position:null,barangay_id:null};
const capabilityDisaster='00000000-0000-4000-8000-000000000002',capabilityTransaction='00000000-0000-4000-8000-000000000003',capabilitySession='00000000-0000-4000-8000-000000000004';
async function capabilityFixture(page:Page){
  // Only UI capability/projection fixtures; no integrity result or chain reference is supplied.
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');
    let data:unknown=[];
    if(path==='/actors/catalogue')data=[capabilityActor];
    else if(path==='/disasters')data=[{id:capabilityDisaster,name:'Invented capability flood'}];
    else if(path==='/sessions')data=[{id:capabilitySession,business_status:'open',revision:0,date:'2026-10-12',site:'Invented test hall',assignments:[{id:'assignment',actor_id:capabilityActor.id,assignment_kind:'cash',display_name:capabilityActor.display_name}],entries:[{entitlement_id:capabilityTransaction,transaction_id:capabilityTransaction,name:'Invented Test Household'}]}];
    else if(path===`/sessions/${capabilitySession}/lookup`)data={transaction_id:capabilityTransaction};
    else if(path===`/transactions/${capabilityTransaction}`)data={id:capabilityTransaction,disaster_id:capabilityDisaster,household_name:'Invented Test Household',household_id:capabilityTransaction,entitlement_id:capabilityTransaction,business_status:'available',amount_centavos:'495000',revision:0,photo_evidence_id:null,accepted_id_type:null,current_attempt:null,identity_checks:[],receipt:null};
    else if(path.startsWith('/transactions/')){await route.fulfill({status:404,json:{error:'record_unavailable'}});return;}
    await route.fulfill({json:{data,meta:{identity_assurance:'claimed_unverified',authentication:'pending'}}});
  });
  await page.goto(workspacePath('disbursing',capabilityActor.id,'payouts',capabilityDisaster));
  await page.getByLabel('Assigned payout session',{exact:true}).selectOption(capabilitySession);
}

test('camera capability fixture: unsupported browser keeps manual lookup available',async({page})=>{
  await page.addInitScript(()=>Object.defineProperty(window,'BarcodeDetector',{value:undefined,configurable:true}));
  await capabilityFixture(page);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('unavailable in this browser');
  await expect(page.getByLabel('Transaction reference',{exact:true})).toBeEditable();
});

test('camera capability fixture: cancel releases a stream granted after cancellation',async({page})=>{
  await page.addInitScript(()=>{
    const state={requests:0,stops:0};Object.assign(window,{cameraCapability:state});
    Object.defineProperty(window,'BarcodeDetector',{value:class{static async getSupportedFormats(){return ['qr_code'];}async detect(){return [];}}});
    Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>{state.requests++;await new Promise(resolve=>setTimeout(resolve,500));return {getTracks:()=>[{stop:()=>state.stops++}]};}}});
  });
  await capabilityFixture(page);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect.poll(()=>page.evaluate(()=>(window as unknown as {cameraCapability:{requests:number}}).cameraCapability.requests)).toBe(1);
  await page.getByRole('button',{name:'Cancel scanning'}).click();
  await expect.poll(()=>page.evaluate(()=>(window as unknown as {cameraCapability:{stops:number}}).cameraCapability.stops)).toBe(1);
  await expect(page.getByRole('status').filter({hasText:'Scanning cancelled'})).toBeVisible();
});

test('camera capability fixture: mocked decoder opens a reference once without payout mutations',async({page})=>{
  await page.addInitScript(reference=>{
    const state={stops:0};Object.assign(window,{mockDecoder:state});
    Object.defineProperty(window,'BarcodeDetector',{value:class{static async getSupportedFormats(){return ['qr_code'];}async detect(){return [{rawValue:reference}];}}});
    Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>({getTracks:()=>[{stop:()=>state.stops++}]})}});
    HTMLMediaElement.prototype.play=async()=>{};
    Object.defineProperty(HTMLMediaElement.prototype,'srcObject',{get(){return null;},set(){}});
  },`ayudachain:transaction:${capabilityTransaction}`);
  const posts:string[]=[];page.on('request',request=>{if(request.method()==='POST')posts.push(new URL(request.url()).pathname);});
  await capabilityFixture(page);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.getByRole('status').filter({hasText:'Transaction found'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Invented Test Household',exact:true})).toBeVisible();
  await expect.poll(()=>page.evaluate(()=>(window as unknown as {mockDecoder:{stops:number}}).mockDecoder.stops)).toBe(1);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.getByRole('status').filter({hasText:'already open'})).toBeVisible();
  expect(posts).toEqual([`/api/v1/sessions/${capabilitySession}/lookup`]);
  await expect(page.getByRole('button',{name:'Record cash handover',exact:true})).toHaveCount(0);
});

test('projection fixture: direct reference outside catalogue loads and failure clears identity controls',async({page})=>{
  await capabilityFixture(page);
  await page.evaluate(id=>{const url=new URL(location.href);url.searchParams.set('record',id);history.pushState(null,'',url);},capabilityTransaction);
  await expect(page.getByRole('heading',{name:'Invented Test Household',exact:true})).toBeVisible();
  await page.getByLabel('Accepted photo ID type',{exact:true}).fill('Invented photo ID');
  await page.getByLabel('I compared the person with the accepted photo ID').check();
  await page.evaluate(()=>{const url=new URL(location.href);url.searchParams.set('record','00000000-0000-4000-8000-000000000099');history.pushState(null,'',url);});
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('This record is unavailable for the selected account');await expect(page.locator('main .mvp-error[role="alert"]')).not.toContainText('record_unavailable');
  await expect(page.getByRole('heading',{name:'Invented Test Household',exact:true})).toHaveCount(0);
  await page.evaluate(id=>{const url=new URL(location.href);url.searchParams.set('record',id);history.pushState(null,'',url);},capabilityTransaction);
  await expect(page.getByLabel('Accepted photo ID type',{exact:true})).toHaveValue('');
  await expect(page.getByLabel('I compared the person with the accepted photo ID')).not.toBeChecked();
});

test('projection fixture: a direct record from another disaster cannot display payout controls',async({page})=>{
  await capabilityFixture(page);
  await page.route(`**/api/v1/transactions/${capabilityTransaction}`,route=>route.fulfill({json:{data:{id:capabilityTransaction,disaster_id:'00000000-0000-4000-8000-000000000088',household_name:'Invented other-disaster household'},meta:{identity_assurance:'claimed_unverified'}}}));
  await page.evaluate(id=>{const url=new URL(location.href);url.searchParams.set('record',id);history.pushState(null,'',url);},capabilityTransaction);
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('belongs to a different disaster');
  await expect(page.getByRole('heading',{name:'Invented other-disaster household'})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Save ID comparison'})).toHaveCount(0);
});

async function assigned(request:APIRequestContext,prepare=true){
  const api='http://127.0.0.1:8000/api/v1';
  const catalogue=(await(await request.get(`${api}/actors/catalogue`)).json()).data;
  const disasters=(await(await request.get(`${api}/disasters`)).json()).data;
  for(const actor of catalogue.filter((a:{role:string;status:string})=>a.role==='disbursing'&&a.status==='active')){
    for(const disaster of disasters){
      const response=await request.get(`${api}/sessions?disaster_id=${disaster.id}`,{headers:{'X-Demo-Actor-ID':actor.id}});
      if(!response.ok())continue;
      const session=(await response.json()).data.find((s:{business_status:string;entries:unknown[]})=>['scheduled','open'].includes(s.business_status)&&s.entries.length);
      if(session)return {actor,disaster,session,transaction:session.entries[0].transaction_id};
    }
  }
  if(prepare){await prepareLookupSession(request);return assigned(request,false);}
  throw new Error('Actual published, assigned lookup session preparation did not produce a current session.');
}
async function openLookup(page:Page,request:APIRequestContext){
  const data=await assigned(request);
  await page.goto(`${workspacePath('disbursing',data.actor.id,'payouts')}&disaster=${data.disaster.id}`);
  await page.getByLabel('Assigned payout session',{exact:true}).selectOption(data.session.id);
  return data;
}

test('Filipino guidance persists navigation and reload with language metadata',async({page,request})=>{
  const actors=(await(await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data;
  const actor=actors.find((a:{role:string;status:string})=>a.role==='beneficiary'&&a.status==='active');
  await page.goto(workspacePath('beneficiary',actor.id,'registry'));
  await page.getByLabel('Guidance language / Wika ng gabay').selectOption('fil');
  await expect(page.getByRole('heading',{name:'Irehistro ang inyong sambahayan'})).toBeVisible();
  await expect(page.locator('aside[lang="fil"]')).toContainText('Hindi beripikado');
  await page.reload();await expect(page.getByLabel('Guidance language / Wika ng gabay')).toHaveValue('fil');
  await page.goto(workspacePath('beneficiary',actor.id,'payouts'));
  await expect(page.getByRole('heading',{name:'Panatilihing pribado ang code at PIN'})).toBeVisible();
  await page.getByLabel('Guidance language / Wika ng gabay').selectOption('en');
  await expect(page.getByRole('heading',{name:'Keep your code and PIN private'})).toBeVisible();
});

test('manual lookup rejects malformed and unknown references then opens current transaction without authorization',async({page,request})=>{
  const data=await openLookup(page,request);
  await page.getByLabel('Transaction reference',{exact:true}).fill('DFC-2026-0001');
  await page.getByRole('button',{name:'Open transaction reference'}).click();
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('transaction UUID');
  await page.getByLabel('Transaction reference',{exact:true}).fill('00000000-0000-0000-0000-000000000000');
  await page.getByRole('button',{name:'Open transaction reference'}).click();
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('No permitted transaction');
  const before=(await(await request.get(`http://127.0.0.1:8000/api/v1/transactions/${data.transaction}`,{headers:{'X-Demo-Actor-ID':data.actor.id}})).json()).data;
  await page.getByLabel('Transaction reference',{exact:true}).fill(data.transaction);
  await page.getByRole('button',{name:'Open transaction reference'}).click();
  await expect(page.getByRole('status').filter({hasText:'Transaction found'})).toBeVisible();
  await expect(page).toHaveURL(new RegExp('record='+data.transaction));
  await page.getByRole('button',{name:'Open transaction reference'}).click();
  await expect(page.getByRole('status').filter({hasText:'already open'})).toBeVisible();
  const after=(await(await request.get(`http://127.0.0.1:8000/api/v1/transactions/${data.transaction}`,{headers:{'X-Demo-Actor-ID':data.actor.id}})).json()).data;
  expect(after.current_attempt).toEqual(before.current_attempt);expect(after.receipt).toEqual(before.receipt);
});

test('camera decode uses the scoped live lookup and releases tracks on result, cancel and late permission',async({page,request})=>{
  const data=await assigned(request);
  await page.addInitScript(({reference})=>{
    const state={stops:0,requests:0,value:reference,delay:0};Object.assign(window,{scanTest:state});
    Object.defineProperty(window,'BarcodeDetector',{value:class{static async getSupportedFormats(){return ['qr_code'];}async detect(){return state.value?[{rawValue:state.value}]:[];}}});
    Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>{state.requests++;await new Promise(resolve=>setTimeout(resolve,state.delay));return {getTracks:()=>[{stop:()=>state.stops++}]};}}});
    HTMLMediaElement.prototype.play=async()=>{};
    Object.defineProperty(HTMLMediaElement.prototype,'srcObject',{get(){return null;},set(){}});
  },{reference:`ayudachain:transaction:${data.transaction}`});
  await page.goto(`${workspacePath('disbursing',data.actor.id,'payouts')}&disaster=${data.disaster.id}`);
  await page.getByLabel('Assigned payout session',{exact:true}).selectOption(data.session.id);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.getByRole('status').filter({hasText:'Transaction found'})).toBeVisible();
  expect(await page.evaluate(()=>(window as unknown as {scanTest:{stops:number}}).scanTest.stops)).toBe(1);
  await page.evaluate(()=>{(window as unknown as {scanTest:{value:string;delay:number}}).scanTest.value='';});
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.getByLabel('QR camera preview')).toBeVisible();
  await page.getByRole('button',{name:'Cancel scanning'}).click();
  await expect(page.getByRole('status').filter({hasText:'Scanning cancelled'})).toBeVisible();
  await page.evaluate(()=>{(window as unknown as {scanTest:{delay:number}}).scanTest.delay=600;});
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect.poll(()=>page.evaluate(()=>(window as unknown as {scanTest:{requests:number}}).scanTest.requests)).toBe(3);
  await page.getByRole('button',{name:'Cancel scanning'}).click();
  await expect.poll(()=>page.evaluate(()=>(window as unknown as {scanTest:{stops:number}}).scanTest.stops)).toBe(3);
});

test('unsupported camera and denied permission retain equal manual fallback',async({page,request})=>{
  await page.addInitScript(()=>Object.defineProperty(window,'BarcodeDetector',{value:undefined,configurable:true}));
  await openLookup(page,request);
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('unavailable in this browser');
  await page.evaluate(()=>{
    Object.defineProperty(window,'BarcodeDetector',{value:class{static async getSupportedFormats(){return ['qr_code'];}},configurable:true});
    Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>{throw new DOMException('Denied','NotAllowedError');}},configurable:true});
  });
  await page.getByRole('button',{name:'Scan QR with camera'}).click();
  await expect(page.locator('main .mvp-error[role="alert"]')).toContainText('permission was denied');
  await expect(page.getByLabel('Transaction reference',{exact:true})).toBeEditable();
});
