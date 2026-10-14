import {test,expect,Page} from '@playwright/test';
const actor='00000000-0000-4000-8000-000000000101',disaster='00000000-0000-4000-8000-000000000102';
async function fixture(page:Page){
  let attempt=false,writes=0,failWrite=false;
  await page.addInitScript(()=>localStorage.setItem('ayudachain.guidance-language','en'));
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(route.request().method()==='POST'){
      writes++;
      if(failWrite){await route.abort();return;}
      attempt=true;await route.fulfill({json:{data:{resources:[{id:'attempt',type:'attempt'}],replayed:false,code:'123456'}}});return;
    }
    const tx={id:'txn',disaster_id:disaster,entitlement_id:'ent',household_id:'house',household_name:'Invented Sinta',business_status:attempt?'in_transaction':'available',amount_centavos:'125000',revision:1,identity_checks:[],photo_evidence_id:null,accepted_id_type:null,receipt:null,current_attempt:attempt?{id:'attempt',attempt_number:1,path:'own_device',business_status:'open',expires_at:'2099-01-01T00:00:00Z',current_id_check_id:null}:null};
    const data:Record<string,unknown>={'/actors/catalogue':[{id:actor,role:'beneficiary',status:'active',display_name:'Invented Sinta',barangay_id:null}],'/disasters':[{id:disaster,name:'Synthetic disaster'}],'/barangays':[], '/evaluation/status':{business_utc:'2099-01-01T00:00:00Z',clock_mode:'simulated'},'/transactions':[tx],'/transactions/txn':tx,'/sessions':[{id:'session',business_status:'open',date:'2099-01-01',site:'Invented site',entries:[{entitlement_id:'ent',transaction_id:'txn'}],assignments:[]}]};
    await route.fulfill({json:{data:data[path]??[]}});
  });
  return {url:`/mvp/beneficiary/payouts?account=${actor}&disaster=${disaster}&record=txn`,writes:()=>writes,fail:()=>{failWrite=true;}};
}
test('recipient path is keyboard accessible; hiding never stores code and refresh cannot reveal it',async({page})=>{
  const f=await fixture(page);await page.goto(f.url);
  const own=page.getByRole('radio',{name:'Own device',exact:true});
  await own.focus();await page.keyboard.press('ArrowRight');
  await expect(page.getByRole('radio',{name:'No-phone assisted recipient',exact:true})).toBeChecked();
  await page.keyboard.press('ArrowLeft');await expect(own).toBeChecked();
  await page.getByRole('button',{name:'Open payout authorization',exact:true}).click();
  await expect(page.locator('.ac-secret-code')).toHaveText('123 456');
  await page.getByRole('button',{name:'Hide code',exact:true}).click();
  await expect(page.locator('.ac-secret-code')).not.toBeVisible();
  await page.getByRole('button',{name:'Reveal code in this view',exact:true}).click();
  await expect(page.locator('.ac-secret-code')).toBeVisible();
  expect(await page.evaluate(()=>JSON.stringify({...localStorage,...sessionStorage}))).not.toContain('123456');
  expect(page.url()).not.toContain('123456');
  await page.reload();await expect(page.locator('.ac-secret-code')).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Reveal code in this view',exact:true})).toHaveCount(0);
});
test('uncertain opening blocks retry until current record read and retains recovery instructions',async({page})=>{
  const f=await fixture(page);await page.goto(f.url);f.fail();
  await page.getByRole('button',{name:'Open payout authorization',exact:true}).click();
  await expect(page.getByRole('button',{name:'Open payout authorization',exact:true})).toBeDisabled();
  await expect(page.locator('main')).toContainText('Read the saved transaction before retrying');
  await page.getByRole('button',{name:'Read current transaction',exact:true}).click();
  await expect(page.getByRole('button',{name:'Open payout authorization',exact:true})).toBeEnabled();
  expect(f.writes()).toBe(1);
});
test('a beneficiary with one record sees it directly, with no record dropdown',async({page})=>{
  const f=await fixture(page);await page.goto(f.url.replace('&record=txn',''));
  await expect(page.getByRole('radio',{name:'Own device',exact:true})).toBeVisible();
  await expect(page.getByLabel('Transaction',{exact:true})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Open payout authorization',exact:true})).toBeEnabled();
});
test('choosing the already auto-selected record keeps its current detail and adds the record to the URL',async({page})=>{
  const f=await fixture(page);
  await page.route(u=>u.pathname==='/api/v1/transactions',route=>route.fulfill({json:{data:[{id:'txn',household_name:'Invented Sinta',business_status:'available',amount_centavos:'125000'},{id:'txn-2',household_name:'Earlier record',business_status:'handed_over',amount_centavos:'125000'}]}}));
  await page.goto(f.url.replace('&record=txn',''));
  const own=page.getByRole('radio',{name:'Own device',exact:true});await expect(own).toBeVisible();
  await page.getByLabel('Transaction',{exact:true}).selectOption('txn');
  await expect(own).toBeVisible();await expect(page.getByRole('button',{name:'Open payout authorization',exact:true})).toBeEnabled();
  await expect(page).toHaveURL(/record=txn/);
});

test('a single disaster is shown as text, not as a dropdown',async({page})=>{
  const f=await fixture(page);await page.goto(f.url);
  await expect(page.getByLabel('Disaster',{exact:true})).toHaveCount(0);
  await expect(page.locator('.ac-context-disaster')).toHaveText('Synthetic disaster');
});

test('the beneficiary payout page stays short: few words, no long paragraphs',async({page})=>{
  const f=await fixture(page);await page.goto(f.url);
  await expect(page.getByRole('radio',{name:'Own device',exact:true})).toBeVisible();
  const stats=await page.locator('main').evaluate(element=>{const main=element as HTMLElement;return {words:main.innerText.split(/\s+/).filter(Boolean).length,longest:Math.max(0,...[...main.querySelectorAll('p')].map(p=>(p as HTMLElement).innerText.split(/\s+/).filter(Boolean).length))};});
  expect(stats.words,'words in the main area').toBeLessThanOrEqual(140);
  expect(stats.longest,'words in the longest paragraph').toBeLessThanOrEqual(30);
});
