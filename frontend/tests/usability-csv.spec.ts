import {test,expect,Page} from '@playwright/test';
import {workspacePath} from './workspace-navigation';

// UI-only API fixtures. No chain result is generated and no live data is reset.
const actor='00000000-0000-4000-8000-000000000001',barangay='00000000-0000-4000-8000-000000000002',household='00000000-0000-4000-8000-000000000003',disaster='00000000-0000-4000-8000-000000000004';
const header='name,birth_date,address,zone,declared_barangay_id\n';
const content=header+`Invented <b>Tala</b>,1980-01-02,"Invented Street, 4",Zone A,${barangay}\nInvented Invalid,bad,Street B,Zone B,${barangay}\n`;
const resource={type:'household_id',id:household};
const record={id:household,display_id:'DFC-2026-CSV1',revision:0,address:'Invented Street, 4',zone:'Zone A',declared_barangay_id:barangay,residence_state:'unconfirmed',identity_state:'pending_field_check',members:[{member_id:'00000000-0000-4000-8000-000000000005',name:'Invented <b>Tala</b>',birth_date:'1980-01-02',relationship:'head',is_head:true}]};

async function fixture(page:Page,loseAcknowledgement=false){
  const state={saved:false,confirmations:[] as unknown[],details:0};
  await page.route('**/api/v1/**',async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/api/v1','');
    const ok=(data:unknown)=>route.fulfill({json:{data,meta:{identity_assurance:'claimed_unverified',authentication:'pending'}}});
    if(path==='/actors/catalogue')return ok([{id:actor,role:'dswd',display_name:'Invented CSV Officer',status:'active',position:null,barangay_id:null}]);
    if(path==='/disasters')return ok([{id:disaster,name:'Synthetic CSV Typhoon'}]);
    if(path==='/barangays')return ok([{id:barangay,name:'Invented Silong'}]);
    if(path==='/registry')return ok({households:[],limit:200});
    if(path===`/registry/${household}`){state.details++;return ok(record);}
    if(path==='/intake'||path==='/staff')return ok([]);
    if(path==='/registry/csv/template')return ok({content:header,description:'Head-only no-ID declarations.',max_rows:100,max_bytes:262144});
    if(path==='/registry/csv/preview'){
      const body=route.request().postDataJSON();
      if(body.content.startsWith('phone,'))return route.fulfill({status:422,json:{error:'csv_headers_require_name_birth_date_address_zone_declared_barangay_id_only'}});
      return ok({digest:'a'.repeat(64),duplicate_limitations:'Name and address suggestions only; missing birth dates are unknown.',rows:[
        {index:1,values:{name:record.members[0].name,birth_date:'1980-01-02',address:record.address,zone:record.zone,declared_barangay_id:barangay},status:state.saved?'saved':'valid',errors:[],warnings:[],matches:[],...(state.saved?{resources:[resource],replayed:true}:{})},
        {index:2,values:{name:'Invented Invalid',birth_date:'bad',address:'Street B',zone:'Zone B',declared_barangay_id:barangay},status:'invalid',errors:['birth_date_requires_past_YYYY_MM_DD'],warnings:[],matches:[]},
      ]});
    }
    if(path==='/registry/csv/confirm'){
      state.confirmations.push(route.request().postDataJSON());state.saved=true;
      if(loseAcknowledgement&&state.confirmations.length===1)return route.abort('failed');
      return ok({outcomes:[{index:1,status:'saved',resources:[resource],replayed:state.confirmations.length>1}]});
    }
    return route.fulfill({status:404,json:{error:'fixture_route_unavailable'}});
  });
  await page.goto(workspacePath('dswd',actor,'registry',disaster));
  await page.getByRole('heading',{name:'Import household declarations from CSV'}).click();
  await expect(page.getByRole('button',{name:'Download office household template'})).toBeEnabled();
  return state;
}
async function upload(page:Page,text=content){await page.getByLabel('Completed UTF-8 CSV file').setInputFiles({name:'synthetic.csv',mimeType:'text/csv',buffer:Buffer.from(text)});}

test('CSV preview rejects private headers, cancels without writes and confirms only selected valid rows',async({page})=>{
  const state=await fixture(page);
  await upload(page,content.replace('name,','phone,'));
  await expect(page.getByRole('alert').filter({hasText:'csv_headers_require'})).toBeVisible();
  await upload(page);await expect(page.getByRole('heading',{name:'Row 1: Invented <b>Tala</b> · Valid'})).toBeVisible();
  await expect(page.getByText('Birth date requires past YYYY MM DD')).toBeVisible();
  expect(await page.locator('article b').count()).toBe(0);
  for(const viewport of [{width:1280,height:900,name:'desktop'},{width:390,height:844,name:'mobile'}]){
    await page.setViewportSize(viewport);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
    await page.getByRole('heading',{name:'Registry and preparation'}).click();
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:`../.impeccable/review/csv-${viewport.name}.png`,fullPage:true});
  }
  await page.setViewportSize({width:1280,height:900});
  await expect(page.locator('details').filter({has:page.getByRole('heading',{name:'Import household declarations from CSV'})}).getByRole('checkbox')).toHaveCount(1);
  await page.getByRole('button',{name:'Cancel preview'}).click();expect(state.confirmations).toHaveLength(0);
  await upload(page);await page.getByRole('checkbox',{name:'Confirm row 1 as a new household declaration'}).check();
  await page.getByRole('button',{name:'Register 1 confirmed household'}).click();
  await expect(page.getByRole('link',{name:'Open household'})).toBeVisible();
  expect(state.confirmations).toEqual([{content,digest:'a'.repeat(64),rows:[1]}]);
  await page.getByRole('link',{name:'Open household'}).click();
  await expect(page.locator(`#household-${household}`)).toContainText('DFC-2026-CSV1');expect(state.details).toBeGreaterThan(0);
});

test('lost CSV acknowledgement retries identical content and repeat upload recovers saved row',async({page})=>{
  const state=await fixture(page,true);
  await upload(page);await page.getByRole('checkbox',{name:'Confirm row 1 as a new household declaration'}).check();
  await page.getByRole('button',{name:'Register 1 confirmed household'}).click();
  await expect(page.getByRole('alert').filter({hasText:'Some confirmed rows may already be saved'})).toBeVisible();
  await page.getByRole('button',{name:'Retry the same confirmation'}).click();
  await expect(page.getByText('Household already saved; original acknowledgement recovered')).toBeVisible();
  expect(state.confirmations).toHaveLength(2);expect(state.confirmations[1]).toEqual(state.confirmations[0]);
  await page.getByRole('button',{name:'Close import preview'}).click();await upload(page);
  await expect(page.getByRole('link',{name:'Open household'})).toBeVisible();
  await expect(page.locator('details').filter({has:page.getByRole('heading',{name:'Import household declarations from CSV'})}).getByRole('checkbox')).toHaveCount(0);expect(state.confirmations).toHaveLength(2);
});
