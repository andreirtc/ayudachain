import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import path from 'node:path';

test('fresh editable release survives reload and Auditor is read-only',async({page,request})=>{
  const catalogue=(await (await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data as {id:string;role:string;status:string}[];
  const dswd=catalogue.find(a=>a.role==='dswd'&&a.status==='active')!,auditor=catalogue.find(a=>a.role==='auditor')!;
  await page.goto(workspacePath(dswd.role,dswd.id,'funds'));
  await page.getByRole('button',{name:'Record a release'}).click();
  const reference=`DFC-2026-${Date.now()}`;
  const root=path.resolve(__dirname,'../..');
  const bytes=execFileSync(path.join(root,'.venv/Scripts/python.exe'),['-c',"from backend.scripts.synthetic_evidence import synthetic_pdf; import sys; sys.stdout.buffer.write(synthetic_pdf('Invented browser release '+sys.argv[1]+'\\nAmount: PHP 123,456.00'))",reference],{cwd:root});
  await page.getByLabel('Release original',{exact:true}).setInputFiles({name:'invented-release.pdf',mimeType:'application/pdf',buffer:bytes});
  await expect(page.getByLabel('Confirmed amount (PHP)',{exact:true})).toHaveValue('123456.00');
  await page.getByLabel('Reference number',{exact:true}).fill(reference);
  await page.getByLabel('Confirmed amount (PHP)',{exact:true}).fill('123500.50');
  await page.getByLabel('Covered area',{exact:true}).fill('Invented Silong, Zone 7');
  await page.getByLabel('Printed signatory name',{exact:true}).fill('Invented Mayari Tala');
  await page.getByLabel('Printed signatory role',{exact:true}).fill('Synthetic Director');
  await page.getByLabel('Purpose',{exact:true}).fill('Fresh edited synthetic assistance');
  await page.getByRole('button',{name:'Confirm and record'}).click();
  await expect(page.getByRole('status')).toContainText('Saved to the ledger');
  await page.reload();
  await expect(page.getByRole('heading',{name:`${reference} · Release`})).toBeVisible();
  await page.goto(workspacePath(auditor.role,auditor.id,'funds'));
  await expect(page.getByRole('heading',{name:`${reference} · Release`})).toBeVisible();
  await expect(page.getByRole('button',{name:'Record a release'})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Append correction'})).toHaveCount(0);
  for(const width of [390,1440]){await page.setViewportSize({width,height:900});await expect(page.getByRole('heading',{name:'Disaster funds',exact:true})).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:path.join(root,'.runtime',`funds-${width}.png`),fullPage:true});}
});
