import {test,expect,Page} from '@playwright/test';
test.use({actionTimeout:5000});
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const household=(n:number)=>({id:id(n),display_id:`DFC-2026-UX0${n}`,revision:0,address:'Invented Street '+n,zone:String(n),declared_barangay_id:id(3),residence_state:'unconfirmed',identity_state:'pending_field_check',members:[{member_id:id(n+20),name:'Invented Household '+n,birth_date:null,relationship:'head',is_head:true}]});
async function setup(page:Page,role='dswd'){
 const actor={id:id(1),display_name:'Invented Layout Officer',role,status:'active',barangay_id:role==='barangay'?id(3):null,position:null};
 await page.route('**/api/v1/**',async route=>{const p=new URL(route.request().url()).pathname.replace('/api/v1','');let data:unknown=[];
 if(p==='/actors/catalogue')data=[actor];else if(p==='/disasters')data=[{id:id(2),name:'Invented layout flood'}];else if(p==='/barangays')data=[{id:id(3),name:'Invented Layout Barangay'}];else if(p==='/registry')data={households:[household(4),household(5)]};else if(p.startsWith('/registry/'))data=household(5);
 await route.fulfill({json:{data,meta:{mode:'local_synthetic_evaluation'}}});});
 await page.goto('/mvp/'+(role==='dswd'?'dswd-officer':'barangay-officer')+'/registry');
 await expect(page.getByRole('heading',{name:'Registry and preparation'})).toBeVisible();
}
test('staff search and inspect one household inline without exposing the whole registry',async({page})=>{
 await setup(page);await page.getByRole('searchbox',{name:'Search households',exact:true}).fill('Household 5');
 await expect(page.getByRole('status').filter({hasText:'1 of 2 households'})).toBeVisible();
 await page.getByRole('button',{name:'Open household DFC-2026-UX05 · Invented Household 5',exact:true}).click();
 const detail=page.getByRole('region',{name:'Selected household',exact:true});await expect(detail).toContainText('Invented Street 5');await expect(detail).not.toContainText('Invented Street 4');
 await detail.getByRole('button',{name:'Review registry or linkage'}).click();await expect(detail.getByLabel('Review action',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Clear household search'}).click();await expect(page.getByRole('button',{name:/Open household DFC/})).toHaveCount(2);
});
test('phone list/detail returns focus and keeps private actions out of Barangay views',async({page})=>{
 await page.setViewportSize({width:390,height:844});await setup(page,'barangay');
 const row=page.getByRole('button',{name:'Open household DFC-2026-UX05 · Invented Household 5',exact:true});await row.click();
 await expect(page.getByRole('region',{name:'Selected household',exact:true})).toBeVisible();await expect(page.getByRole('region',{name:'Household selection',exact:true})).not.toBeVisible();
 await expect(page.getByRole('button',{name:'Review registry or linkage'})).toHaveCount(0);await expect(page.locator('main')).not.toContainText('Contact:');
 await page.getByRole('button',{name:'Back to households',exact:true}).click();await expect(row).toBeFocused();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
