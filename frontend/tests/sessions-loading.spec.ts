import {test,expect} from '@playwright/test';
import {workspacePath} from './workspace-navigation';

test('late saved sessions cannot collapse the session form after editing starts',async({page,request})=>{
  const base='http://127.0.0.1:8000/api/v1';
  const actors=(await(await request.get(base+'/actors/catalogue')).json()).data;
  const dswd=actors.find((a:{role:string})=>a.role==='dswd');
  let release!:()=>void,started!:()=>void;
  const held=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>started=r);
  await page.route('**/api/v1/sessions?*',async route=>{const response=await route.fetch();started();await held;await route.fulfill({response});});
  try{
    await page.goto(workspacePath('dswd',dswd.id,'sessions'));await ready;
    await page.getByLabel('Site',{exact:true}).fill('Invented draft hall');
    release();
    await expect(page.getByLabel('Site',{exact:true})).toBeVisible();
    await expect(page.getByLabel('Site',{exact:true})).toHaveValue('Invented draft hall');
    await expect(page.getByLabel('Current published list',{exact:true}).locator('option')).not.toHaveCount(1);
    await expect(page.getByLabel('Site',{exact:true})).toBeVisible();
  }finally{release();await page.unrouteAll({behavior:'wait'});}
});
