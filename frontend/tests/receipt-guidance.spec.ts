import {test,expect} from '@playwright/test';
import {workspacePath} from './workspace-navigation';

test('a recorded beneficiary receipt leads to private follow-up without obsolete code instructions',async({page,request})=>{
  const base='http://127.0.0.1:8000/api/v1';
  const read=async(path:string,actor?:string)=>(await(await request.get(base+path,{headers:actor?{'X-Demo-Actor-ID':actor}:{}})).json()).data;
  const actors=await read('/actors/catalogue'),dswd=actors.find((a:{role:string})=>a.role==='dswd');
  const disaster=(await read('/disasters'))[0].id;
  const row=(await read('/transactions?disaster_id='+disaster,dswd.id)).find((t:{business_status:string})=>t.business_status==='handed_over');
  expect(row,'Run the actual journey before the receipt regression').toBeTruthy();
  const tx=await read('/transactions/'+row.id,dswd.id),households=(await read('/registry',dswd.id)).households;
  const recipient=households.find((h:{id:string})=>h.id===tx.household_id).beneficiary_actor_id;
  await page.setViewportSize({width:390,height:900});
  await page.goto(workspacePath('beneficiary',recipient,'payouts',disaster)+'&record='+tx.id);
  await expect(page.getByRole('heading',{name:/Handover recorded once/})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Keep your code and PIN private',exact:true})).toHaveCount(0);
  const next=page.getByRole('link',{name:'Tell us what you received',exact:true});
  await expect(next).toHaveAttribute('href',workspacePath('beneficiary',recipient,'outcomes',disaster)+'&record='+tx.id);
  await next.click();await expect(page.getByLabel('Recipient’s private answer',{exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Open payout authorization'})).toHaveCount(0);
});
