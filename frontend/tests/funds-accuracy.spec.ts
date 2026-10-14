import {workspacePath} from './workspace-navigation';
import {test,expect,Page} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

const root=path.resolve(__dirname,'../..'),exactAmount='90071992547409.93';
function original(amount:string,reference:string){
  return {name:'invented-release.pdf',mimeType:'application/pdf',buffer:execFileSync(path.join(root,'.venv/Scripts/python.exe'),['-c','from backend.scripts.synthetic_evidence import synthetic_pdf; import sys; sys.stdout.buffer.write(synthetic_pdf(sys.argv[1]))',`Invented accuracy original ${reference}\nAmount: PHP ${amount}`],{cwd:root})};
}
async function record(page:Page,reference:string,amount:string){
  await page.getByLabel('Confirmed amount (PHP)',{exact:true}).fill(amount);
  await page.getByLabel('Reference number',{exact:true}).fill(reference);
  await page.getByLabel('Covered area',{exact:true}).fill('Invented Silong');
  await page.getByLabel('Printed signatory name',{exact:true}).fill('Invented Accuracy Tala');
  await page.getByLabel('Printed signatory role',{exact:true}).fill('Synthetic Director');
  await page.getByLabel('Purpose',{exact:true}).fill('Invented exact amount regression');
  await page.getByRole('button',{name:'Confirm and record',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('Saved to the ledger');
}

test.beforeEach(async({page,request})=>{
  const actors=(await(await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data as {id:string;role:string}[];
  await page.goto(workspacePath('dswd',actors.find(a=>a.role==='dswd')!.id,'funds'));
  await page.getByRole('button',{name:'Record a release',exact:true}).click();
});

test('extracted centavos beyond the safe Number range prefill without losing a cent',async({page})=>{
  await page.getByLabel('Release original',{exact:true}).setInputFiles(original(exactAmount,'EXTRACT-'+Date.now()));
  await expect(page.getByLabel('Confirmed amount (PHP)',{exact:true})).toHaveValue(exactAmount);
});

test('a saved large-centavo correction prefills the exact recorded amount',async({page})=>{
  const reference='DFC-2026-'+Date.now();
  await page.getByLabel('Release original',{exact:true}).setInputFiles(original(exactAmount,reference));
  await expect(page.getByRole('button',{name:'Confirm and record',exact:true})).toBeEnabled();
  await record(page,reference,exactAmount);
  await page.locator('article').filter({has:page.getByRole('heading',{name:reference+' · Release',exact:true})}).getByRole('button',{name:'Append correction',exact:true}).click();
  await expect(page.getByLabel('Confirmed amount (PHP)',{exact:true})).toHaveValue(exactAmount);
  await page.setViewportSize({width:390,height:900});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.getByLabel('Confirmed amount (PHP)',{exact:true}).fill('120000.00');
  await page.getByLabel('Reason',{exact:true}).fill('Invented test correction after checking exact large-centavo prefill');
  await page.getByRole('button',{name:'Save reversal and replacement',exact:true}).click();
  await expect(page.getByRole('heading',{name:reference+' · Replacement',exact:true})).toBeVisible();
});

test('transcription correction retains the primary source when supporting evidence was uploaded first',async({page})=>{
  const reference='DFC-2026-'+Date.now();
  await page.getByLabel('Supporting originals (NTA alone is not a release)',{exact:true}).setInputFiles(original('111.00',reference+'-support'));
  await expect(page.getByText('1 supporting file(s) attached.',{exact:true})).toBeVisible();
  await page.getByLabel('Release original',{exact:true}).setInputFiles(original('222.00',reference+'-source'));
  await expect(page.getByLabel('Confirmed amount (PHP)',{exact:true})).toHaveValue('222.00');
  await record(page,reference,'222.00');
  await page.locator('article').filter({has:page.getByRole('heading',{name:reference+' · Release',exact:true})}).getByRole('button',{name:'Append correction',exact:true}).click();
  await expect(page.getByRole('button',{name:'Save reversal and replacement',exact:true})).toBeEnabled();
  await page.getByLabel('Confirmed amount (PHP)',{exact:true}).fill('223.00');
  await page.getByLabel('Reason',{exact:true}).fill('Invented transcription correction preserving the original source');
  const saved=page.waitForResponse(r=>r.url().includes('/corrections')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Save reversal and replacement',exact:true}).click();
  expect((await saved).status()).toBe(200);
  await expect(page.getByRole('heading',{name:reference+' · Replacement',exact:true})).toBeVisible();
});
