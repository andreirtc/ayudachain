import {test,expect,Page} from '@playwright/test';

// Controlled synthetic presentation only. Fixture responses do not establish
// any real chain verification, funding exception or workflow result.
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const auditor=id(1),dswd=id(2),disaster=id(20),fund=id(30),proof=id(31);
const query=(account:string)=>`account=${account}&disaster=${disaster}`;
async function fixtures(page:Page){
  const reads:string[]=[];
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');reads.push(path);
    const data:Record<string,unknown>={
      '/actors/catalogue':[{id:auditor,role:'auditor',display_name:'Invented Auditor One',status:'active',position:null,barangay_id:null},{id:dswd,role:'dswd',display_name:'Invented DSWD One',status:'active',position:null,barangay_id:null}],
      '/disasters':[{id:disaster,name:'Synthetic presentation disaster'}],'/barangays':[],'/context':{run_id:id(21)},
      '/claims':{claims:[]},'/audit/overview':{population:{claims:0,entitlements:0},financial:{received_centavos:'0',approved_known_subtotal_centavos:'0',awaiting_amount_count:0},outcomes:{counts:{recorded_handover:0,received_full:0,adverse:0,waiting:0,unconfirmed:0,overdue_unconfirmed_pending:0},recorded_amount_centavos:'0'},exceptions:{grievances:[]}},
      '/funds':{entries:[{id:fund,reference_number:'DFC-2026-0001',exceptions:['document_mismatch']}],totals:{}},
      '/audit/proofs':[{id:proof,kind:'handover',state:'confirmed',job_id:id(40)}],'/audit/originals':[],
      ['/audit/timeline/fund_entry_id/'+fund]:[{id:id(50),sequence:1,action:'fund.record',actor_id:dswd,effective_at:'2026-10-14T02:00:00Z',reason:'Invented release order',exact_versions:[]}],
      '/operations':{rows:[],denominators:'Synthetic presentation fixture'},
      '/queues/search':{rows:[],total:0,offset:0,limit:25,kinds:['claims'],states:[],scope:'selected actor permitted records'},
    };
    await route.fulfill({json:{data:data[path]??[]}});
  });
  return reads;
}

test('Auditor navigation shows only Inspect, Records and Verify',async({page})=>{
  await fixtures(page);await page.goto(`/mvp/auditor?${query(auditor)}`);
  const sidebar=page.getByRole('navigation',{name:'Workspace navigation'});
  await expect(sidebar.getByRole('link')).toHaveText(['Inspect','Records','Verify']);
  await page.setViewportSize({width:390,height:844});
  await expect(page.getByRole('navigation',{name:'Primary destinations'}).getByRole('link')).toHaveText(['Inspect','Records','Verify']);
});

test('a record page outside the menu stays reachable and returns to Records',async({page})=>{
  await fixtures(page);await page.goto(`/mvp/auditor/claims?${query(auditor)}`);
  await expect(page.getByRole('heading',{name:'Page unavailable'})).toHaveCount(0);
  await expect(page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link',{name:'Records',exact:true})).toHaveAttribute('aria-current','page');
  await page.getByRole('link',{name:'Back to Records',exact:true}).click();
  await expect(page).toHaveURL(/\/mvp\/auditor\/queues\?/);
  await expect(page.getByRole('heading',{name:'Records',exact:true})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Other records'}).getByRole('link',{name:'Funding ledger',exact:true})).toHaveAttribute('href',/\/mvp\/auditor\/funds\?/);
  await expect(page.getByText('Office totals by barangay',{exact:true})).toBeVisible();
});

test('funding exceptions appear on Inspect and open their history on Verify',async({page})=>{
  await fixtures(page);await page.goto(`/mvp/auditor?${query(auditor)}`);
  const row=page.getByRole('link',{name:/Funding entry DFC-2026-0001/});
  await expect(row).toContainText('Document mismatch');
  await row.click();
  await expect(page).toHaveURL(new RegExp(`record=${fund}&history=fund_entry_id`));
  await expect(page.getByRole('region',{name:'Supporting record history'})).toContainText('Invented release order');
});

test('Verify shows one view at a time without exceptions, and Back restores the view',async({page})=>{
  const reads=await fixtures(page);await page.goto(`/mvp/auditor/audit?${query(auditor)}`);
  await expect(page.getByRole('heading',{name:'Verify',exact:true})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Exceptions and supporting records'})).toHaveCount(0);
  const views=page.getByRole('group',{name:'Verify views'});
  await expect(page.getByRole('heading',{name:'Chain integrity checks'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Original evidence'})).toHaveCount(0);
  await views.getByRole('button',{name:'Original files',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Original evidence'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Chain integrity checks'})).toHaveCount(0);
  await views.getByRole('button',{name:'Event history',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Append-only business history'})).toBeVisible();
  await page.goBack();
  await expect(page).toHaveURL(/view=originals/);
  await expect(page.getByRole('heading',{name:'Original evidence'})).toBeVisible();
  expect(reads.filter(p=>p==='/integrity/check')).toHaveLength(0);
  expect(reads).not.toContain('/audit/overview');
});

test('DSWD evidence page keeps its combined layout and exceptions',async({page})=>{
  await fixtures(page);await page.goto(`/mvp/dswd-officer/audit?${query(dswd)}`);
  await expect(page.getByRole('heading',{name:'Evidence and integrity',exact:true})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Exceptions and supporting records'})).toBeVisible();
  await expect(page.getByRole('group',{name:'Verify views'})).toHaveCount(0);
  await expect(page.getByRole('heading',{name:'Original evidence'})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link',{name:'Evidence & history',exact:true})).toHaveAttribute('aria-current','page');
});
