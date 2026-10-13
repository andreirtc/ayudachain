import {test,expect,Page} from '@playwright/test';
const API='http://127.0.0.1:8101';
test.setTimeout(90000);
async function login(page:Page,id:string){await page.goto('/sign-in');await page.getByRole('textbox',{name:'Account',exact:true}).fill(id);await page.getByLabel('Password',{exact:true}).fill('synthetic-test-password-only');await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.getByText('Authenticated synthetic account.',{exact:false})).toBeVisible();}
async function signOut(page:Page){await page.getByRole('button',{name:'Sign out',exact:true}).click();}
async function headers(page:Page){const s=await(await page.context().request.get(API+'/api/auth/session')).json();return {'X-AyudaChain-Client':'web','X-CSRF-Token':s.csrf_token,Origin:'http://127.0.0.1:3101'};}
test.beforeEach(async({page})=>{await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//,r=>{const u=new URL(r.request().url());u.hostname='127.0.0.1';u.port='8101';return r.continue({url:u.toString()});});});
test('demo desk, assisted concern, private reply and read-only audit stay connected',async({page},info)=>{
 await login(page,'demo-officer-01');let h=await headers(page);
 const id='BEN-DEMO-'+info.project.name,request=page.context().request;
 expect((await request.post(API+'/api/beneficiaries',{headers:h,data:{beneficiary_id:id,household_name:'Synthetic desk household '+info.project.name,barangay_id:'BRGY-001',barangay_name:'San Isidro',batch_id:'RELIEF-2026-001'}})).status()).toBe(201);
 expect((await request.post(API+'/api/beneficiaries/'+id+'/verify',{headers:h,data:{status:'VERIFIED',review_notes:'Inspected synthetic demo household'}})).status()).toBe(200);
 await signOut(page);await login(page,'demo-disbursing-001');await page.goto('/distributions?beneficiary_id='+id);
 await expect(page.getByLabel('Desk checks')).toContainText('Ready to record this amount.');
 await page.getByRole('link',{name:'Record an assisted concern',exact:true}).click();
 await page.getByRole('button',{name:'Report a concern',exact:true}).click();await expect(page.getByLabel('Household',{exact:true})).toHaveValue(id);
 await page.getByLabel('Concern about').selectOption('PAYOUT');await page.getByLabel('What needs reviewing?').fill('Please confirm the desk amount for '+info.project.name+'.');
 await page.getByRole('button',{name:'Submit concern',exact:true}).click();await expect(page.getByText('Concern submitted.',{exact:true})).toBeVisible();
 const concern=page.getByRole('region',{name:'Selected concern'});await expect(concern).toContainText('with staff assistance');
 await page.emulateMedia({colorScheme:info.project.name==='phone'?'dark':'light'});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:info.outputPath('assisted-concern.png'),fullPage:true});
 await signOut(page);await login(page,'demo-officer-01');await page.goto('/concerns?beneficiary_id='+id);
 await page.getByLabel('Response shown to household').fill('Your fictional standard grant is 5000 pesos.');await page.getByLabel('Reason (staff only)').fill('Private demo staff reason '+info.project.name);
 await page.getByRole('button',{name:'Save response',exact:true}).click();await expect(page.getByText('Reply saved.',{exact:true})).toBeVisible();await expect(concern).toContainText('In review · revision 2');
 await signOut(page);await login(page,'demo-disbursing-001');await page.goto('/distributions?beneficiary_id='+id);
 await expect(page.getByLabel('Desk checks')).toContainText('Ready to record this amount.');await page.getByRole('button',{name:'Record demo payout',exact:true}).click();await expect(page.getByRole('heading',{name:'Payout recorded',exact:true})).toBeVisible();
 await page.screenshot({path:info.outputPath('recorded-payout.png'),fullPage:true});
 await signOut(page);await login(page,'demo-auditor-01');await page.goto('/audit');await expect(page.getByRole('region',{name:'Recorded funding'})).toContainText('Typhoon Salinlahi');
 const receipts=page.getByRole('region',{name:'Receipt evidence'});await expect(receipts).toContainText(id);await expect(receipts).toContainText('Current proof: not checked in this view.');
 await page.getByText('Local audit history',{exact:false}).click();await expect(page.getByRole('main')).toContainText('concern replied');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:info.outputPath('staff-audit.png'),fullPage:true});
 h=await headers(page);expect((await request.post(API+'/api/concerns',{headers:h,data:{}})).status()).toBe(403);
 await receipts.getByRole('link',{name:'Check receipt',exact:true}).first().click();await expect(page).toHaveURL(/\/verify\?distribution_id=/);await expect(page.getByRole('main')).toContainText('unavailable',{ignoreCase:true});
 await signOut(page);await login(page,'demo-beneficiary-01');await page.goto('/household');await page.getByRole('link',{name:'Report or follow up a concern',exact:true}).click();
 await page.getByRole('button',{name:'Report a concern',exact:true}).click();await page.getByLabel('What needs reviewing?').fill('Please review my own collection instructions '+info.project.name+'.');await page.getByRole('button',{name:'Submit concern',exact:true}).click();await expect(page.getByText('Concern submitted.',{exact:true})).toBeVisible();
 await expect(page.getByRole('main')).not.toContainText('Private demo staff reason');await page.screenshot({path:info.outputPath('household-concern.png'),fullPage:true});
 const own=(await(await request.get(API+'/api/concerns')).json())[0];await signOut(page);await login(page,'demo-officer-01');await page.goto('/concerns?beneficiary_id=BEN-0004');
 await page.getByLabel('Response shown to household').fill('Bring your recorded household reference.');await page.getByLabel('Reason (staff only)').fill('Private household staff note');await page.getByRole('button',{name:'Save response',exact:true}).click();await expect(page.getByText('Reply saved.',{exact:true})).toBeVisible();
 await signOut(page);await login(page,'demo-beneficiary-01');await page.goto('/concerns');await expect(page.getByRole('region',{name:'Selected concern'})).toContainText('Bring your recorded household reference.');await expect(page.getByRole('main')).not.toContainText('Private household staff note');
 const ownRead=await request.get(API+'/api/concerns/'+own.concern_id);expect(ownRead.status()).toBe(200);expect(await ownRead.text()).not.toContain('staff_reason');
});
