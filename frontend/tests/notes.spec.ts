import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';
import path from 'node:path';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

test('closed-transaction DSWD notes persist and remain absent from payer and Auditor write controls',async({page,request})=>{
 const base='http://127.0.0.1:8000/api/v1';
 const actors=(await(await request.get(base+'/actors/catalogue')).json()).data as {id:string;role:string}[];
 const dswd=actors.find(a=>a.role==='dswd')!,aud=actors.find(a=>a.role==='auditor')!;
 const disaster=(await(await request.get(base+'/disasters')).json()).data[0].id;
 const transactions=(await(await request.get(base+'/transactions?disaster_id='+disaster,{headers:{'X-Demo-Actor-ID':dswd.id}})).json()).data as {id:string}[];
 expect(transactions.length).toBeGreaterThan(0);
 const id=transactions[0].id;
 const transaction=(await(await request.get(base+'/transactions/'+id,{headers:{'X-Demo-Actor-ID':dswd.id}})).json()).data;
 expect(transaction.receipt).toBeTruthy();
 async function select(actor:string){await page.goto(workspacePath(actors.find(a=>a.id===actor)!.role,actor,'outcomes',disaster)+'&record='+id);}
 await select(dswd.id);
 const text='Invented office follow-up '+Date.now();
 await page.getByLabel('Operational transaction note (not a recipient answer)',{exact:true}).fill(text);
 await page.getByRole('button',{name:'Append operational note',exact:true}).click();
 await expect(page.locator('.ac-saved-result')).toContainText('Operational note recorded for');
 await page.reload();await select(dswd.id);await page.getByText('Permitted operational note history',{exact:true}).click();await expect(page.getByText(text,{exact:false})).toBeVisible();
 await select(transaction.receipt.payer_id);await expect(page.locator('body')).not.toContainText(text);
 await select(aud.id);await expect(page.getByRole('button',{name:'Append operational note',exact:true})).toHaveCount(0);
 await page.getByText('Permitted operational note history',{exact:true}).click();await expect(page.getByText(text,{exact:false})).toBeVisible();
 for(const width of [390,1440]){await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:path.resolve(__dirname,'../../.runtime',`follow-up-viewport-${width}.png`),fullPage:false});}
});
