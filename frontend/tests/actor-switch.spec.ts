import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

test('a delayed real former-actor response cannot render after switching role',async({page,request})=>{
 const actors=(await(await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data as {id:string;role:string}[];
 const dswd=actors.find(a=>a.role==='dswd')!,bar=actors.find(a=>a.role==='barangay')!;
 let release!:()=>void,started!:()=>void;
 const ready=new Promise<void>(r=>started=r),held=new Promise<void>(r=>release=r);
 await page.route('**/api/v1/registry',async route=>{
   if(route.request().headers()['x-demo-actor-id']!==dswd.id){await route.continue();return;}
   try{const response=await route.fetch();started();await held;await route.fulfill({response});}catch{} // Former view may already have aborted.
 });
 await page.goto(workspacePath(dswd.role,dswd.id,'registry'));await ready;
 await page.goto(workspacePath(bar.role,bar.id,'registry'));release();
 await expect(page.getByRole('heading',{name:'Households',exact:true})).toBeVisible();
 await expect(page.locator('body')).not.toContainText('Contact:');await expect(page.getByRole('button',{name:'Review registry or linkage'})).toHaveCount(0);
 await page.unrouteAll({behavior:'wait'});
});
