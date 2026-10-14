import {workspacePath} from './workspace-navigation';
import {test,expect} from '@playwright/test';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

test('amount inputs cannot submit the initial revision while saved input history is loading',async({page,request})=>{
  const base='http://127.0.0.1:8000/api/v1';
  const actors=(await(await request.get(base+'/actors/catalogue')).json()).data as {id:string;role:string}[];
  const dswd=actors.find(a=>a.role==='dswd')!;
  let release!:()=>void,started!:()=>void;
  const held=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>started=r);
  await page.route('**/api/v1/amount-inputs?*',async route=>{
    const response=await route.fetch();started();await held;await route.fulfill({response});
  });
  try{
    await page.goto(workspacePath(dswd.role,dswd.id,'lists'));await ready;
    await expect(page.getByRole('button',{name:'Save immutable input version',exact:true})).toBeDisabled();
    release();
    if(!(await page.getByLabel('Documented daily wage (PHP)',{exact:true}).isVisible()))await page.getByText('Record an amount basis',{exact:true}).click();
    await expect(page.getByRole('button',{name:'Save immutable input version',exact:true})).toBeEnabled();
  }finally{release();await page.unrouteAll({behavior:'wait'});}
});
