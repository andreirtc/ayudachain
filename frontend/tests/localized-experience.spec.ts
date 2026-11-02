import {test,expect} from '@playwright/test';
import {workspacePath} from './workspace-navigation';
test.use({storageState:{cookies:[],origins:[]}});
test('first visit uses Filipino/Taglish, all five roles stay visible and English is available',async({page})=>{
 await page.setViewportSize({width:390,height:900});await page.goto('/mvp');
 await expect(page.getByRole('heading',{level:1})).toHaveText('Welcome sa AyudaChain');
 for(const slug of ['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor'])await expect(page.locator(`a[href="/mvp/${slug}"]`)).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.getByLabel('Guidance language / Wika ng gabay').selectOption('en');await expect(page.getByRole('heading',{level:1})).toHaveText('Welcome to AyudaChain');
 await page.reload();await expect(page.getByRole('heading',{level:1})).toHaveText('Welcome to AyudaChain');
});
test('all five role homes use Filipino controls without horizontal overflow on phones and desktops',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const slug of ['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor']){
  await page.goto('/mvp/'+slug+'?lang=fil');await expect(page.locator('.ac-app')).toHaveAttribute('lang','fil');await expect(page.getByRole('heading',{level:1}).first()).toBeVisible();
  for(const width of [1440,390]){await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();}
  await expect(page.locator('.ac-quick-navigation')).toContainText('Home');
 }
 expect(errors).toEqual([]);
});
test('citizen sees assistance amount first; wage basis is optional detail and changing language changes no business record',async({page,request})=>{
 const base='http://127.0.0.1:8000/api/v1';const actors=(await(await request.get(base+'/actors/catalogue')).json()).data;const actor=actors.find((a:{role:string;display_name:string})=>a.role==='beneficiary'&&a.display_name==='Maria Santos · Demo')||actors.find((a:{role:string})=>a.role==='beneficiary');const d=(await(await request.get(base+'/disasters')).json()).data[0].id;
 const read=async()=>(await(await request.get(base+'/transactions?disaster_id='+d,{headers:{'X-Demo-Actor-ID':actor.id}})).json()).data;const before=await read();expect(before.length).toBeGreaterThan(0);
 await page.goto(workspacePath('beneficiary',actor.id,'overview',d)+'&lang=fil');await expect(page.getByRole('heading',{name:'Halaga ng ayuda',exact:true})).toBeVisible();
 const basis=page.locator('.ac-amount-basis');await expect(basis).not.toBeVisible();await page.getByText('Paano kinuwenta?',{exact:true}).click();await expect(basis).toBeVisible();
 await page.locator('.ac-display-preferences>summary').click();await page.getByLabel('Guidance language / Wika ng gabay').selectOption('en');await page.keyboard.press('Escape');await expect(page.getByRole('heading',{name:'Your assistance amount',exact:true})).toBeVisible();await page.reload();await expect(page.getByRole('heading',{name:'Your assistance amount',exact:true})).toBeVisible();expect(await read()).toEqual(before);
});
