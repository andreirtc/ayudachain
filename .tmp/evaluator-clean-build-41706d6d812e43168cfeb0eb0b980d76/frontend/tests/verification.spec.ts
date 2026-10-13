import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';

const currentMatch=/\bVerified\b/;
for(const screen of ['Funds','Amounts and lists','Authorization and handover','Evidence and review']){
  test(`${screen} clears the current match when a later verification request fails`,async({page,request})=>{
    const base='http://127.0.0.1:8000/api/v1';
    const actors=(await(await request.get(base+'/actors/catalogue')).json()).data as {id:string;role:string}[];
    const dswd=actors.find(a=>a.role==='dswd')!;
    const disaster=(await(await request.get(base+'/disasters')).json()).data[0].id;
    await page.goto(workspacePath(dswd.role,dswd.id,({'Funds':'funds','Amounts and lists':'lists','Authorization and handover':'payouts','Evidence and review':'audit'} as Record<string,string>)[screen],disaster));
    if(screen==='Funds')await page.getByText('Evidence, amount review and chain proofs',{exact:true}).first().click();
    if(screen==='Authorization and handover'){
      const rows=(await(await request.get(base+'/transactions?disaster_id='+disaster,{headers:{'X-Demo-Actor-ID':dswd.id}})).json()).data as {id:string;business_status:string}[];
      const paid=rows.find(t=>t.business_status==='handed_over')!;
      expect(paid).toBeTruthy();await page.getByLabel('Transaction',{exact:true}).selectOption(paid.id);
    }
    const block=screen==='Evidence and review'?page.locator('.mvp-entry').filter({has:page.getByRole('button',{name:'Check now',exact:true})}).filter({hasText:'confirmed'}).first():page.locator('.mvp-proof').filter({hasText:'confirmed'}).first();
    const button=block.getByRole('button',{name:screen==='Evidence and review'?'Check now':screen==='Authorization and handover'?'Check receipt chain record':'Check chain now',exact:true});
    const real=page.waitForResponse(r=>r.url().endsWith('/integrity/check')&&r.request().method()==='POST');
    await button.click();expect((await(await real).json()).data.result).toBe('match');
    await expect(block).toContainText(currentMatch);
    let release!:()=>void,started!:()=>void;
    const held=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>started=r);
    await page.route('**/api/v1/integrity/check',async route=>{started();await held;await route.abort('connectionfailed');});
    try{
      await button.click();await ready;
      await expect(block).not.toContainText(currentMatch);
      await expect(block).toContainText(/checking/i);
    }finally{release();}
    await expect(page.getByRole('alert').filter({hasText:/fetch|connection|unavailable|failed/i})).toBeVisible();
    await expect(block).not.toContainText(currentMatch);
    await expect(block).toContainText(/Last match/i);
    await expect(block).toContainText(/refresh failed/i);
    const auditor=actors.find(a=>a.role==='auditor')!;
    await page.goto(workspacePath(auditor.role,auditor.id,({'Funds':'funds','Amounts and lists':'lists','Authorization and handover':'payouts','Evidence and review':'audit'} as Record<string,string>)[screen],disaster));
    await expect(page.locator('body')).not.toContainText(/Last match|refresh failed/i);
    await expect(page.locator('body')).not.toContainText(currentMatch);
  });
}

test('a delayed real chain result cannot populate a newly selected actor view',async({page,request})=>{
  const base='http://127.0.0.1:8000/api/v1';
  const actors=(await(await request.get(base+'/actors/catalogue')).json()).data as {id:string;role:string}[];
  const dswd=actors.find(a=>a.role==='dswd')!,auditor=actors.find(a=>a.role==='auditor')!;
  let release!:()=>void,started!:()=>void;
  const held=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>started=r);
  await page.route('**/api/v1/integrity/check',async route=>{
    const response=await route.fetch();expect(typeof (await response.json()).data.result).toBe('string');
    started();await held;
    try{await route.fulfill({response});}catch{} // The former actor request can already be aborted.
  });
  try{
    await page.goto(workspacePath(dswd.role,dswd.id,'audit'));
    await page.locator('.mvp-entry').filter({hasText:'confirmed'}).filter({has:page.getByRole('button',{name:'Check now',exact:true})}).first().getByRole('button',{name:'Check now',exact:true}).click();
    await ready;await page.goto(workspacePath(auditor.role,auditor.id,'audit'));release();
    await expect(page.getByRole('heading',{name:'Evidence and integrity',exact:true})).toBeVisible();
    await expect(page.getByRole('button',{name:'Check now',exact:true}).first()).toBeEnabled();
    await expect(page.locator('body')).not.toContainText(currentMatch);
    await expect(page.locator('body')).not.toContainText(/Last match/i);
  }finally{release();await page.unrouteAll({behavior:'wait'});}
});
