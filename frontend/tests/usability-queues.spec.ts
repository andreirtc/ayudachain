import {test,expect,Page} from '@playwright/test';
const office={id:'00000000-0000-4000-8000-000000000001',role:'dswd',display_name:'Invented Queue Officer',status:'active',barangay_id:null,position:null};
const disaster='00000000-0000-4000-8000-000000000002',place='00000000-0000-4000-8000-000000000003';
async function fixture(page:Page){
 await page.route('**/api/v1/**',async route=>{const path=new URL(route.request().url()).pathname;let data:unknown=[];
 if(path.endsWith('/actors/catalogue'))data=[office];
 if(path.endsWith('/disasters'))data=[{id:disaster,name:'Invented queue flood'}];
 if(path.endsWith('/barangays'))data=[{id:place,name:'Invented Queue Barangay'}];
 if(path.endsWith('/queues/search')){const body=route.request().postDataJSON();data={rows:[],total:0,offset:body.offset,limit:25,kinds:['claims','registry','entitlements','transactions','proofs'],states:['awaiting_dswd','flagged'],scope:'selected actor permitted records'};}
 await route.fulfill({json:{data,meta:{identity_assurance:'claimed_unverified'}}});});
}
test('queue filters navigate without putting household search text in URLs',async({page})=>{
 await fixture(page);await page.goto(`/mvp/dswd-officer/queues?account=${office.id}&disaster=${disaster}`);
 await expect(page.getByText('0 results',{exact:false})).toBeVisible();
 await page.getByLabel('Search names, household reference or zone').fill('Invented Household Private Text');
 const sent=page.waitForRequest(r=>r.url().endsWith('/queues/search')&&r.postDataJSON().query==='Invented Household Private Text');
 await page.getByRole('button',{name:'Search',exact:true}).click();await sent;
 expect(page.url()).not.toContain('Private');
 await page.getByLabel('Workflow state',{exact:true}).selectOption('flagged');
 await expect(page).toHaveURL(/state=flagged/);await expect(page.getByText('No records match these filters.',{exact:false})).toBeVisible();
 await page.reload();await expect(page.getByLabel('Workflow state',{exact:true})).toHaveValue('flagged');
 await page.getByRole('button',{name:'Clear all',exact:true}).click();await expect(page.getByLabel('Workflow state',{exact:true})).toHaveValue('all');
 await page.goBack();await expect(page.getByLabel('Workflow state',{exact:true})).toHaveValue('flagged');
 for(const width of [390,1440]){await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();}
});
test('queue errors are recoverable and do not show previous counts',async({page})=>{
 await fixture(page);let fail=true;await page.route('**/api/v1/queues/search',async route=>{if(fail)await route.fulfill({status:503,json:{error:'database_unavailable'}});else await route.fulfill({json:{data:{rows:[],total:0,offset:0,limit:25,kinds:['claims'],states:[],scope:'permitted'}}});});
 await page.goto(`/mvp/dswd-officer/queues?account=${office.id}&disaster=${disaster}`);await expect(page.getByRole('alert').filter({hasText:'database service is unavailable'})).toContainText('Ask the evaluation operator');
 fail=false;await page.getByRole('button',{name:'Retry search'}).click();await expect(page.getByText('0 results',{exact:false})).toBeVisible();
});
