import {test,expect,Page} from '@playwright/test';
test.use({trace:'off'}); // Once-shown codes/PINs must not be written into browser traces.
const account='00000000-0000-4000-8000-000000000201',disaster='00000000-0000-4000-8000-000000000202';
async function fixture(page:Page){
  let writes=0,paid=false;
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(route.request().method()==='POST'){writes++;paid=true;await route.abort();return;}
    const tx={id:'txn',disaster_id:disaster,entitlement_id:'ent',household_id:'house',household_name:'Invented Sinta',business_status:paid?'handed_over':'in_transaction',amount_centavos:'125000',revision:1,identity_checks:[{id:'idcheck',result:'pass',checked_by:account,accepted_id_type:'Synthetic photo ID'}],photo_evidence_id:null,accepted_id_type:'Synthetic photo ID',current_attempt:{id:'attempt',attempt_number:1,path:'own_device',business_status:paid?'handed_over':'presented',expires_at:'2099-01-01T00:00:00Z',current_id_check_id:'idcheck'},receipt:paid?{id:'receipt',amount_centavos:'125000',handed_at:'2026-10-14T00:00:00Z',payer_id:account,proofs:[]}:null};
    const data:Record<string,unknown>={'/actors/catalogue':[{id:account,role:'disbursing',status:'active',display_name:'Invented Payer',barangay_id:null}],'/disasters':[{id:disaster,name:'Synthetic disaster'}],'/barangays':[], '/evaluation/status':{business_utc:'2026-10-14T00:00:00Z',clock_mode:'simulated'},'/transactions':[tx],'/transactions/txn':tx,'/sessions':[{id:'session',business_status:'open',date:'2026-10-14',site:'Invented site',entries:[{entitlement_id:'ent',transaction_id:'txn'}],assignments:[{id:'assignment',actor_id:account,assignment_kind:'cash',display_name:'Invented Payer'}]}]};
    await route.fulfill({json:{data:data[path]??[]}});
  });
  return {url:`/mvp/disbursing-officer/payouts?account=${account}&disaster=${disaster}&record=txn`,writes:()=>writes};
}
test('handover review cancellation sends no command; lost acknowledgement reads receipt before any retry',async({page})=>{
  const f=await fixture(page);await page.goto(f.url);
  await page.getByLabel('Recipient payout code',{exact:true}).fill('654321');
  const trigger=page.getByRole('button',{name:'Record cash handover',exact:true});await trigger.click();
  const dialog=page.getByRole('dialog');await expect(dialog).toContainText('Invented Sinta');await expect(dialog).toContainText('₱1,250.00');await expect(dialog).not.toContainText('654321');
  await page.keyboard.press('Escape');await expect(trigger).toBeFocused();expect(f.writes()).toBe(0);
  await trigger.click();await dialog.getByRole('button',{name:'Record handover once',exact:true}).click();
  await expect(trigger).toBeDisabled();await expect(page.locator('main')).toContainText('Read the saved transaction before retrying');
  await page.getByRole('button',{name:'Read current transaction',exact:true}).click();
  await expect(page.getByRole('heading',{name:/Handover recorded once/})).toBeVisible();
  await expect(trigger).toHaveCount(0);expect(f.writes()).toBe(1);
});
test('failed identity comparison uses explicit stop tone and review; tablet keeps amount visible',async({page})=>{
  const f=await fixture(page);await page.setViewportSize({width:1024,height:900});await page.goto(f.url);
  const fail=page.getByRole('radio',{name:'Fail and hold/stop',exact:true});await fail.check();
  await page.getByLabel('Failed comparison reason (required on failure)',{exact:true}).fill('Invented person differs from photo');
  const trigger=page.getByRole('button',{name:'Save ID comparison',exact:true});await expect(trigger).toHaveClass(/danger/);await trigger.click();
  await expect(page.getByRole('dialog')).toContainText('Fail and hold/stop');await page.keyboard.press('Escape');expect(f.writes()).toBe(0);
  await expect(page.locator('.ac-disbursing-tablet')).toBeVisible();
  await expect(page.locator('.ac-payout-amount')).toContainText('₱1,250.00');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
