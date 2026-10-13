import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';

test('self registry persists absence and scoped staff view omits private contact',async({page,request})=>{
  const actors=(await (await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data as {id:string;role:string;display_name:string}[];
  const recipient=actors.filter(a=>a.role==='beneficiary')[2],officer=actors.find(a=>a.role==='barangay')!;
  const existing=(await(await request.get('http://127.0.0.1:8000/api/v1/registry',{headers:{'X-Demo-Actor-ID':recipient.id}})).json()).data.households;
  await page.goto(workspacePath(recipient.role,recipient.id,'registry'));
  let head=existing[0]?.members.find((m:{is_head:boolean})=>m.is_head)?.name;
  if(!existing.length){
  const registration=page.locator('details').filter({has:page.getByRole('heading',{name:'Register your household',exact:true})});
  await expect(registration).toBeVisible();
  if(await registration.getAttribute('open')===null)await registration.locator('summary').click();
  head=`Invented Browser Head ${Date.now()}`;
  const barangays=(await(await request.get('http://127.0.0.1:8000/api/v1/barangays')).json()).data as {id:string}[];
  await page.getByRole('combobox',{name:'Declared barangay',exact:true}).selectOption(barangays[0].id);
  await page.getByLabel('Head name',{exact:true}).fill(head);await page.getByLabel('Address',{exact:true}).fill('Invented Lane 27');await page.getByLabel('Zone',{exact:true}).fill('9');
  await page.getByRole('button',{name:'Open recipient panel for private details'}).click();await page.getByLabel('Contact phone (optional)',{exact:true}).fill('09990000009');
  await page.getByRole('button',{name:'Register household',exact:true}).click();await expect(page.getByRole('status').filter({hasText:'Household registered'})).toBeVisible();
  }
  await expect(page.getByText('Identity evidence: pending_field_check')).toBeVisible();
  await page.reload();await expect(page.getByRole('heading',{name:new RegExp(head)})).toBeVisible();
  await page.goto(workspacePath(officer.role,officer.id,'registry'));await expect(page.locator('body')).not.toContainText('09990000009');
});
