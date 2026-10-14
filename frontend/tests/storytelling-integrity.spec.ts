import {test,expect,Page} from '@playwright/test';

// Controlled synthetic presentation only. Matching fixture responses below do
// not establish any real chain verification or workflow success.
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const actor=id(1),other=id(2),disaster=id(20),proof=id(30),second=id(31);
const audit=`/mvp/auditor/audit?account=${actor}&disaster=${disaster}`;
async function fixtures(page:Page,result='match'){
  let checks=0,fail=false;const reads:string[]=[];
  await page.addInitScript(()=>localStorage.setItem('ayudachain.guidance-language','en'));
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(path==='/integrity/check'){
      checks++;if(fail){await route.fulfill({status:503,json:{error:'network_unavailable'}});return;}
      await route.fulfill({json:{data:{result,checked_at:'2026-10-14T03:00:00Z',kind:'handover'}}});return;
    }
    reads.push(path);
    const data:Record<string,unknown>={
      '/actors/catalogue':[{id:actor,role:'auditor',display_name:'Invented Auditor One',status:'active',position:null,barangay_id:null},{id:other,role:'auditor',display_name:'Invented Auditor Two',status:'active',position:null,barangay_id:null}],
      '/disasters':[{id:disaster,name:'Synthetic presentation disaster'}],'/barangays':[], '/context':{run_id:id(21)},
      '/audit/overview':{exceptions:{}}, ['/audit/timeline/evaluation_run_id/'+id(21)]:[],
      '/audit/proofs':[{id:proof,kind:'handover',state:'confirmed',job_id:id(40)},{id:second,kind:'outcome',state:'pending',job_id:id(41)}],
      '/audit/originals':[], '/funds':{entries:[],totals:{}},
      [`/commitments/${proof}/material`]:{kind:'handover',fixture:'presentation-only'},
      [`/commitments/${proof}/summary`]:{id:proof,kind:'handover',created_at:'2026-10-14T02:00:00Z',submission_state:'confirmed',versions:[],originals:[],coverage:'Synthetic presentation fixture; no real verification evidence.'},
    };
    await route.fulfill({json:{data:data[path]??[]}});
  });
  return {fail:()=>{fail=true;},checks:()=>checks,reads};
}
test('Auditor offers all agreed current-result chips and explicit local scope',async({page})=>{
  await fixtures(page);await page.goto(audit);
  const filters=page.getByRole('group',{name:'Current integrity results'});
  for(const name of ['All','Verified','Does not match','Anchor absent','Chain unreachable','Evidence unavailable','Not checked'])await expect(filters.getByRole('button',{name,exact:true})).toBeVisible();
  await expect(page.getByText('Filters cover records loaded and checked in this view; these are not global verified totals.',{exact:true})).toBeVisible();
  await expect(page.locator('#proof-'+proof)).toContainText('Not checked');
  await filters.getByRole('button',{name:'Verified',exact:true}).click();
  await expect(page.locator('.ac-proof-entry')).toHaveCount(0);
});
test('current match has a real word boundary between status and check time',async({page})=>{
  await fixtures(page);await page.goto(audit);
  const row=page.locator('#proof-'+proof);await row.getByRole('button',{name:'Check now',exact:true}).click();
  await expect(row.locator('.ac-integrity-result')).toHaveText(/Verified\s+Checked/);
  await expect(row).toContainText('Committed content matches the chain record.');
  await expect(row).toContainText('Saved submission: Confirmed');
});
test('failed refresh clears a current match while retaining earlier observation',async({page})=>{
  const mock=await fixtures(page);await page.goto(audit);const row=page.locator('#proof-'+proof);
  await row.getByRole('button',{name:'Check now',exact:true}).click();await expect(row.locator('.ac-integrity-result')).toContainText('Verified');
  mock.fail();await row.getByRole('button',{name:'Check now',exact:true}).click();
  await expect(row.locator('.ac-integrity-result')).toContainText('Refresh failed');await expect(row.locator('.ac-integrity-result')).not.toContainText('Verified');
  await expect(row).toContainText('Last match:');await expect(row).toContainText('does not establish the current result');
  await page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'Verified',exact:true}).click();await expect(page.locator('.ac-proof-entry')).toHaveCount(0);
  await page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'All',exact:true}).click();await expect(row).toBeVisible();
});
for(const [result,label] of [['mismatch','Does not match'],['required_anchor_absent','Anchor absent'],['chain_unreachable','Chain unreachable'],['evidence_unavailable','Evidence unavailable']])test(`current ${result} remains distinct from historical confirmation`,async({page})=>{
  await fixtures(page,result);await page.goto(audit);const row=page.locator('#proof-'+proof);await row.getByRole('button',{name:'Check now',exact:true}).click();
  await expect(row.locator('.ac-integrity-result')).toContainText(label);await page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:label,exact:true}).click();
  await expect(page.locator('.ac-proof-entry')).toHaveCount(1);await expect(row).toBeVisible();
  await page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'Verified',exact:true}).click();await expect(page.locator('.ac-proof-entry')).toHaveCount(0);
});
test('proof selection preserves filter and Back without repeating a check',async({page})=>{
  const mock=await fixtures(page);await page.goto(audit);await page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'Not checked',exact:true}).click();
  await page.locator('#proof-'+proof).getByRole('button',{name:'Open exact material',exact:true}).click();
  await expect(page).toHaveURL(/record=00000000-0000-4000-8000-000000000030/);
  await expect(page.getByText('Exact private verification material',{exact:true})).toBeVisible();
  await page.goBack();await expect(page).toHaveURL(/proof_filter=not_checked/);await expect(page).not.toHaveURL(/record=/);
  await expect(page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'Not checked',exact:true})).toHaveAttribute('aria-pressed','true');expect(mock.checks()).toBe(0);
});
test('changing claimed actor discards current checks and private material',async({page})=>{
  await fixtures(page);await page.goto(audit);const row=page.locator('#proof-'+proof);
  await row.getByRole('button',{name:'Check now',exact:true}).click();await expect(row.locator('.ac-integrity-result')).toContainText('Verified');
  await row.getByRole('button',{name:'Open exact material',exact:true}).click();
  // Change actor within the mounted workspace, rather than resetting by reload.
  await page.locator('.ac-account summary').click();await page.getByLabel('Account',{exact:true}).selectOption(other);await expect(page.locator('#proof-'+proof)).toContainText('Not checked');
  await expect(page.getByText('Exact private verification material',{exact:true})).toHaveCount(0);
});
test('checking stays explicit and chips are operable with the keyboard',async({page})=>{
  await fixtures(page);let release!:()=>void;const wait=new Promise<void>(r=>{release=r;});
  await page.route('**/api/v1/integrity/check',async route=>{await wait;await route.fulfill({json:{data:{result:'chain_unreachable',checked_at:'2026-10-14T03:00:00Z'}}});});
  await page.goto(audit);const row=page.locator('#proof-'+proof);
  try{
    await row.getByRole('button',{name:'Check now',exact:true}).click();await expect(row.locator('.ac-integrity-result')).toContainText('Checking');
    const chip=page.getByRole('group',{name:'Current integrity results'}).getByRole('button',{name:'Not checked',exact:true});await chip.focus();await page.keyboard.press('Enter');
    await expect(chip).toBeFocused();await expect(chip).toHaveAttribute('aria-pressed','true');await expect(row).toHaveCount(0);
  }finally{release();}
});

test('proof list spans its container as table-like rows, then sits beside the detail once a proof is selected',async({page})=>{
  await page.setViewportSize({width:1440,height:900});await fixtures(page);await page.goto(audit);
  const box=(selector:string)=>page.locator(selector).first().evaluate(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};});
  const layout=await box('.ac-proof-layout'),list=await box('.ac-proof-list');
  expect(list.w,'list uses the full container width while nothing is selected').toBeGreaterThanOrEqual(layout.w*0.95);
  const row='#proof-'+proof,title=await box(row+' h3'),status=await box(row+' .ac-proof-status'),actions=await box(row+' .mvp-actions');
  expect(status.x,'status is in its own column right of the title').toBeGreaterThan(title.x+150);
  expect(actions.x,'actions are in a column right of the status').toBeGreaterThan(status.x+150);
  await page.locator(row).getByRole('button',{name:'Open exact material',exact:true}).click();
  await expect(page.locator('.ac-proof-detail')).toBeVisible();
  const split=await box('.ac-proof-list'),detail=await box('.ac-proof-detail');
  expect(detail.x,'detail sits beside the list on desktop').toBeGreaterThan(split.x+split.w-1);
  expect(split.w).toBeGreaterThanOrEqual(320);expect(detail.w).toBeGreaterThanOrEqual(split.w);
  await page.setViewportSize({width:390,height:844});
  const phoneList=await box('.ac-proof-list'),phoneLayout=await box('.ac-proof-layout'),phoneDetail=await box('.ac-proof-detail');
  expect(phoneList.w).toBeGreaterThanOrEqual(phoneLayout.w*0.95);expect(phoneDetail.y,'detail stacks below the list on a phone').toBeGreaterThan(phoneList.y+phoneList.h-1);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
