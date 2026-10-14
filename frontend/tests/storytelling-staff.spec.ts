import {test,expect,Page} from '@playwright/test';
// Synthetic response fixtures exercise UI safeguards only. They do not establish
// real workflow eligibility, physical cash or blockchain verification.
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const account=id(51),disaster=id(52),claimID=id(53),category=id(54),barangay=id(55),round=id(56),caseID=id(60);
async function fixture(page:Page,role:'dswd'|'barangay'){
 const writes:{path:string;body:Record<string,unknown>}[]=[];
 await page.addInitScript(()=>localStorage.setItem('ayudachain.guidance-language','en'));
 const claim={id:claimID,household_id:id(57),disaster_id:disaster,business_status:role==='dswd'?'awaiting_dswd':'waiting_barangay',revision:2,current_submission_id:id(58),submission:{stated_category_id:category,damage_description:'Synthetic roof damage',new_information:null},household:{name:'Invented Tala Salonga',address:'Invented street',zone:'2',barangay_id:barangay},rounds:[{id:round,state:'waiting',deadline_at:'2026-10-20T08:00:00Z',route_kind:null,referral_decision_id:null,responses:[]}],decisions:[],latest_check:{id:id(59),risk_score:3,algorithm_version:'fixture',created_at:'2026-10-14T08:00:00Z',compared_data_revision:1,current_data_revision:1,stale:false,simulation_adapter:'Simulated National ID check',simulation_result:{simulated:true},flags:[{code:'person_in_two_households',weight:3,comparison_available:false,scores:{name_similarity:'0.9'},comparison_unavailable_reason:'No full comparison in this presentation fixture'}]}};
 await page.route('**/api/v1/**',async route=>{
   const req=route.request(),path=new URL(req.url()).pathname.replace('/api/v1','');
   if(req.method()==='POST'){writes.push({path,body:req.postDataJSON()});await route.fulfill({json:{data:{resources:[{type:'test_record',id:claimID}],replayed:false}}});return;}
   const data:Record<string,unknown>={
    '/actors/catalogue':[{id:account,role,display_name:'Invented Review Officer',status:'active',position:role==='barangay'?'Council Member':null,barangay_id:barangay}],
    '/disasters':[{id:disaster,name:'Synthetic decision disaster'}],'/barangays':[{id:barangay,name:'Invented Sapa'}],'/categories':[{id:category,name:'Totally damaged'}],
    '/claims':{claims:[claim]},[`/claims/${claimID}`]:claim,'/registry':{households:[]},'/intake':[], '/lists':[], '/entitlements':[], '/amount-inputs':{disaster:{revision:1},versions:[]},
    '/transactions':[],'/grievances':[{id:caseID,transaction_id:id(61),business_status:'open',revision:4,history:[]}],'/challenges':[], '/outcome-totals':{},
   };await route.fulfill({json:{data:data[path]??[]}});
 });
 return {writes,url:(section:string,record='')=>`/mvp/${role==='dswd'?'dswd-officer':'barangay-officer'}/${section}?account=${account}&disaster=${disaster}${record?'&record='+record:''}`};
}

test('DSWD segmented decision review names record and consequence; cancellation sends no command',async({page})=>{
 const f=await fixture(page,'dswd');await page.goto(f.url('claims',claimID));
 await page.getByRole('radio',{name:'Decline',exact:true}).check();
 await page.getByLabel('Decision reason',{exact:true}).fill('Invented evidence reason');
 await page.getByLabel('I reviewed this current check and its flags, the response thread and available evidence.',{exact:true}).check();
 await page.getByRole('button',{name:'Save human decision',exact:true}).click();
 const dialog=page.getByRole('dialog');await expect(dialog).toContainText('Invented Tala Salonga');await expect(dialog).toContainText('Decline');await expect(dialog).toContainText('Invented evidence reason');
 await page.keyboard.press('Escape');expect(f.writes).toHaveLength(0);
 await page.getByRole('button',{name:'Save human decision',exact:true}).click();await dialog.getByRole('button',{name:'Record decision',exact:true}).click();
 await expect.poll(()=>f.writes.length).toBe(1);expect(f.writes[0].body).toMatchObject({expected_revision:2,action:'decline',reason:'Invented evidence reason'});
 await expect(page.locator('.ac-saved-result')).toContainText('Invented Tala Salonga');
});

test('private case review identifies the case and records a specific append-only action',async({page})=>{
 const f=await fixture(page,'dswd');await page.goto(f.url('outcomes'));
 await page.getByLabel('Private review, resolution or note',{exact:true}).fill('Invented follow-up review');
 await page.getByRole('button',{name:'Append human case action',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText(caseID);await expect(page.getByRole('dialog')).toContainText('Invented follow-up review');
 await page.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();expect(f.writes).toHaveLength(0);
 await page.getByRole('button',{name:'Append human case action',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Record case action',exact:true}).click();
 await expect.poll(()=>f.writes.length).toBe(1);expect(f.writes[0]).toMatchObject({path:`/grievances/${caseID}/actions`,body:{expected_revision:4,action:'review',text:'Invented follow-up review'}});
 await expect(page.locator('.ac-saved-result')).toContainText(`Case action Review recorded for ${caseID}`);
});

test('lost publication acknowledgement remains blocked until its current list read succeeds',async({page})=>{
 const f=await fixture(page,'dswd');let unavailable=false,commands=0;
 await page.route('**/api/v1/lists*',async route=>{
  if(route.request().method()==='POST'){commands++;await route.abort('failed');return;}
  await route.fulfill(unavailable?{status:503,json:{error:'request_failed'}}:{json:{data:[]}});
 });
 await page.goto(f.url('lists'));const prepare=page.getByRole('button',{name:'Prepare list for publication',exact:true});
 await prepare.click();await page.getByRole('dialog').getByRole('button',{name:'Prepare publication request',exact:true}).click();
 await expect(prepare).toBeDisabled();expect(commands).toBe(1);
 unavailable=true;await page.getByRole('button',{name:'Refresh publication',exact:true}).click();await expect(page.locator('main [role="alert"]').first()).toBeVisible();
 await expect(prepare).toBeDisabled();expect(commands).toBe(1);
 unavailable=false;await page.getByRole('button',{name:'Refresh publication',exact:true}).click();await expect(prepare).toBeEnabled();expect(commands).toBe(1);
});

test('record flags stay visible above evidence and describe inspection rather than a fraud finding',async({page})=>{
 const f=await fixture(page,'dswd');await page.goto(f.url('claims',claimID));
 const banner=page.locator('.ac-case-flag').first();
 await expect(banner).toBeVisible();await expect(banner).toContainText('human');await expect(banner).toContainText('not a fraud');
 await expect(banner.getByRole('button',{name:'Compare records',exact:true})).toBeVisible();
 await expect(banner.locator('[aria-hidden="true"]').first()).toBeVisible();
 await expect(banner).toHaveCSS('border-bottom-style','solid');
});

test('Barangay segmented response has keyboard choices and a record-specific review',async({page})=>{
 const f=await fixture(page,'barangay');await page.goto(f.url('claims',claimID));
 const endorse=page.getByRole('radio',{name:'Endorse',exact:true});await endorse.focus();await page.keyboard.press('ArrowRight');
 await expect(page.getByRole('radio',{name:'Not endorse',exact:true})).toBeChecked();
 await page.getByLabel('Reason or referral answer',{exact:true}).fill('Invented residence mismatch');
 await page.getByRole('button',{name:'Append response',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Invented Tala Salonga');
 await page.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();expect(f.writes).toHaveLength(0);
});

test('publication review describes a queued request without claiming published or verified',async({page})=>{
 const f=await fixture(page,'dswd');await page.goto(f.url('lists'));
 await page.getByRole('button',{name:'Prepare list for publication',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('Invented Sapa');await expect(page.getByRole('dialog')).toContainText('matching');expect(f.writes).toHaveLength(0);
 await page.getByRole('dialog').getByRole('button',{name:'Prepare publication request',exact:true}).click();
 await expect.poll(()=>f.writes.length).toBe(1);await expect(page.locator('.ac-saved-result')).toContainText('request');
 await expect(page.locator('.ac-saved-result')).not.toContainText('Verified');
});
