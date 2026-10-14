import {test,expect} from '@playwright/test';
test('staff phone destinations are deliberate and every secondary route remains reachable',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  const roles:Record<string,string[]>={'barangay-officer':['Barangay overview','Claim responses','Households','Approved list'],'dswd-officer':['Operations overview','Claim review','Payout sessions','Private cases'],'disbursing-officer':['My work today','Cash handover','Assigned sessions','Exit checks & notes'],auditor:['Inspect','Records','Verify']};
  for(const [role,labels] of Object.entries(roles)){
    await page.goto('/mvp/'+role);const nav=page.getByRole('navigation',{name:'Primary destinations'});await expect(nav).toBeVisible();await expect(nav.getByRole('link')).toHaveCount(labels.length);
    for(const label of labels)await expect(nav.getByRole('link',{name:label,exact:true})).toBeVisible();
    await page.getByRole('button',{name:'Open navigation'}).click();
    await expect(page.getByRole('navigation',{name:'Workspace navigation'})).toBeVisible();
    await page.keyboard.press('Escape');
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
    if(role==='auditor')await expect(page.getByRole('link',{name:'Assisted registration',exact:true})).toHaveCount(0);
  }
});
test('staff dashboards are task-first and Barangay creation stays secondary',async({page})=>{
  await page.goto('/mvp/barangay-officer');
  await expect(page.getByRole('heading',{name:'Claims needing your response.',exact:true})).toBeVisible();
  await expect(page.getByRole('link',{name:'Assisted registration',exact:true})).toHaveAttribute('href',/\/registry\?/);
  await page.goto('/mvp/dswd-officer');await expect(page.getByRole('heading',{name:'Work needing your decision.',exact:true})).toBeVisible();
  await page.goto('/mvp/disbursing-officer');await expect(page.getByRole('heading',{name:'Find recipient.',exact:true})).toBeVisible();
  await page.goto('/mvp/auditor');await expect(page.getByRole('heading',{name:'Records needing inspection.',exact:true})).toBeVisible();
});
