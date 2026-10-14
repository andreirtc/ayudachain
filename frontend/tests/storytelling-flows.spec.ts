import {test,expect,Page} from '@playwright/test';

// Synthetic presentation fixtures never establish payment or chain verification.
const id=(n:number)=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const actor=id(1),disaster=id(2),otherDisaster=id(3),household=id(4),category=id(5),transaction=id(6),second=id(7);
async function fixture(page:Page,{wrongDisaster=false,emptyHousehold=false,saveHousehold=false,lostClaim=false,failedRead=''}={}){
  let writes=0,registered=false;
  await page.addInitScript(()=>localStorage.setItem('ayudachain.guidance-language','en'));
  await page.route('**/api/v1/**',async route=>{
    const path=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(route.request().method()==='GET'&&path===failedRead){await route.fulfill({status:503,json:{error:'request_failed'}});return;}
    if(route.request().method()==='POST'){writes++;if(lostClaim&&path==='/claims'){await route.abort('failed');return;}if(saveHousehold&&path==='/registry'){registered=true;await route.fulfill({json:{data:{resources:[{type:'household_id',id:household}],replayed:false}}});return;}await route.fulfill({status:409,json:{error:'intake_closed_or_not_covered'}});return;}
    const details={id:transaction,disaster_id:wrongDisaster?otherDisaster:disaster,household_id:household,household_name:'Invented Talang household',business_status:'awaiting_amount',amount_centavos:null,current_attempt:null,receipt:null,identity_checks:[]};
    const data:Record<string,unknown>={
      '/actors/catalogue':[{id:actor,role:'beneficiary',display_name:'Invented Tala',status:'active',barangay_id:null}],
      '/disasters':[{id:disaster,name:'Synthetic storytelling disaster'},{id:otherDisaster,name:'Other synthetic disaster'}],
      '/barangays':[{id:id(8),name:'Invented Sapa'}],'/categories':[{id:category,name:'Totally damaged'}],
      '/registry':{households:emptyHousehold&&!registered?[]:[{id:household,display_id:'DFC-2026-9002',revision:0,address:'Invented road',zone:'2',declared_barangay_id:id(8),residence_state:'unconfirmed',members:[{member_id:id(9),name:'Invented Tala',is_head:true,relationship:'head',birth_date:null}]}]},
      '/claims':{claims:[]},'/intake':[], '/sessions':[], '/notifications':[], '/lists':[], '/entitlements':[], '/grievances':[], '/challenges':[],
      '/transactions':[{id:second,household_name:'Earlier synthetic record',business_status:'awaiting_amount'},{id:transaction,household_name:details.household_name,business_status:details.business_status}],
      [`/transactions/${transaction}`]:details,[`/transactions/${second}`]:{...details,id:second,household_name:'Earlier synthetic record'},
      [`/transactions/${transaction}/private-outcomes`]:{latest_outcome_id:null,answers:[],grievance:null},
      [`/transactions/${second}/private-outcomes`]:{latest_outcome_id:null,answers:[],grievance:null},
      '/registry/csv/template':{content:'name,birth_date,address,zone,declared_barangay_id\n',description:'Synthetic declaration template',max_rows:100,max_bytes:262144},
    };
    await route.fulfill({json:{data:data[path]??[]}});
  });
  return {url:(section:string,record='')=>`/mvp/beneficiary/${section}?account=${actor}&disaster=${disaster}${record?'&record='+record:''}`,writes:()=>writes};
}

test('concern deep link opens the selected permitted transaction and Back restores it',async({page})=>{
  const f=await fixture(page);await page.goto(f.url('outcomes',transaction));
  await expect(page.getByRole('heading',{name:'Invented Talang household',exact:true})).toBeVisible();
  await page.getByLabel('Transaction',{exact:true}).selectOption(second);
  await expect(page.getByRole('heading',{name:'Earlier synthetic record',exact:true})).toBeVisible();
  await page.goBack();
  await expect(page.getByRole('heading',{name:'Invented Talang household',exact:true})).toBeVisible();
});

for(const item of [{section:'registry',path:'/registry',empty:'No household in your current scope.'},{section:'claims',path:'/claims',empty:'No claims in your scope for this disaster.'},{section:'lists',path:'/lists',empty:'No published list available in your current scope.'},{section:'sessions',path:'/sessions',empty:'No session in your current scope.'}])test(`failed ${item.section} read stays unavailable rather than empty`,async({page})=>{
  const f=await fixture(page,{failedRead:item.path});await page.goto(f.url(item.section));
  await expect(page.locator('main [role="alert"]').first()).toBeVisible();
  await expect(page.getByText(item.empty,{exact:true})).toHaveCount(0);
});

test('lost claim acknowledgement requires a successful current read before another submit',async({page})=>{
  const f=await fixture(page,{lostClaim:true});await page.goto(f.url('claims'));
  await page.getByLabel('Stated damage category',{exact:true}).selectOption(category);
  await page.getByLabel('Damage description',{exact:true}).fill('Invented interrupted claim');
  await page.getByRole('button',{name:'Review household claim',exact:true}).click();
  await page.getByRole('dialog').getByRole('button',{name:'Submit household claim',exact:true}).click();
  await expect(page.locator('main .mvp-error').first()).toContainText('read');
  await expect(page.getByRole('button',{name:'Review household claim',exact:true})).toBeDisabled();
  expect(f.writes()).toBe(1);
  await page.getByRole('button',{name:'Refresh claims',exact:true}).click();
  await expect(page.getByRole('button',{name:'Review household claim',exact:true})).toBeEnabled();
  await expect(page.getByLabel('Damage description',{exact:true})).toHaveValue('Invented interrupted claim');
  expect(f.writes()).toBe(1);
});

test('registration review uses keyboard cancellation and its confirmed result persists after dismissing feedback',async({page})=>{
  const f=await fixture(page,{emptyHousehold:true,saveHousehold:true});await page.goto(f.url('registry'));
  await page.getByLabel('Head name',{exact:true}).fill('Invented Tala');
  await page.getByLabel('Address',{exact:true}).fill('Invented road');
  await page.getByLabel('Zone',{exact:true}).fill('2');
  await page.getByLabel('Head birth date (optional)',{exact:true}).fill('1980-01-02');
  await page.getByLabel('Other members (one name | YYYY-MM-DD or blank | relationship per line)',{exact:true}).fill('Invented Buwan | 2000-03-04 | child');
  await page.getByRole('button',{name:'Open recipient panel for private details',exact:true}).click();
  await page.getByLabel('Contact phone (optional)',{exact:true}).fill('09990000042');
  await page.getByLabel('Photo ID type (optional at registration)',{exact:true}).fill('Invented government photo ID');
  await page.getByLabel('ID number (optional)',{exact:true}).fill('DFC-2026-9002');
  const trigger=page.getByRole('button',{name:'Review household registration',exact:true});
  await trigger.click();await expect(page.getByRole('dialog')).toContainText('Invented Tala');
  await expect(page.getByRole('dialog')).toContainText('1980-01-02');await expect(page.getByRole('dialog')).toContainText('Invented Buwan | 2000-03-04 | child');
  await expect(page.getByRole('dialog')).toContainText('09990000042');await expect(page.getByRole('dialog')).toContainText('Invented government photo ID');
  await expect(page.getByRole('dialog')).toContainText('DFC-2026-9002');await expect(page.getByRole('dialog')).toContainText('No original uploaded');
  await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
  await expect(trigger).toBeFocused();expect(f.writes()).toBe(0);
  await expect(page.getByLabel('Contact phone (optional)',{exact:true})).toHaveValue('09990000042');
  await expect(page.getByLabel('ID number (optional)',{exact:true})).toHaveValue('DFC-2026-9002');
  await trigger.click();await page.getByRole('dialog').getByRole('button',{name:'Register household',exact:true}).click();
  await expect(page.locator('.ac-saved-result')).toContainText('Household registered for Invented Tala');
  await page.locator('.ac-snackbar').getByRole('button',{name:'Dismiss',exact:true}).click();
  await expect(page.locator('.ac-snackbar')).toHaveCount(0);
  await expect(page.locator('.ac-saved-result')).toContainText('Registration itself is not an aid application');
  await expect(page.locator('.ac-saved-result a')).toHaveAttribute('href',new RegExp(`account=${actor}.*disaster=${disaster}`));
  expect(f.writes()).toBe(1);
});

for(const language of ['en','fil'])test(`essential beneficiary task controls fit phone and desktop in ${language}`,async({page})=>{
  const f=await fixture(page,{emptyHousehold:true});
  for(const width of [390,1440])for(const section of ['registry','claims','lists','sessions','outcomes']){
    await page.setViewportSize({width,height:844});await page.goto(f.url(section));
    await page.getByLabel('Guidance language / Wika ng gabay').selectOption(language);
    await expect(page.locator('main h1')).toHaveText(language==='fil'?({registry:'Impormasyon namin',claims:'Aplikasyon at pagsusuri',lists:'Halaga ng ayuda at mga listahan',sessions:'Appointment ng ayuda',outcomes:'Sabihin ang natanggap mo at humingi ng tulong'}[section]!):({registry:'Registry and preparation',claims:'Claims and review',lists:'Amounts and approved lists',sessions:'Payout sessions',outcomes:'Tell us what you received and ask for help'}[section]!));
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  }
});

test('a concern from another disaster cannot open a report form',async({page})=>{
  const f=await fixture(page,{wrongDisaster:true});await page.goto(f.url('outcomes',transaction));
  await expect(page.locator('main [role="alert"]').first()).toContainText('another disaster');
  await expect(page.getByLabel('Private report',{exact:true})).toHaveCount(0);
  expect(f.writes()).toBe(0);
});

test('claim review cancels without writing and failed save preserves input across language changes',async({page})=>{
  const f=await fixture(page);await page.goto(f.url('claims'));
  await page.getByLabel('Stated damage category',{exact:true}).selectOption(category);
  await page.getByLabel('Damage description',{exact:true}).fill('Invented roof damage');
  await page.getByRole('button',{name:'Review household claim',exact:true}).click();
  await expect(page.getByRole('dialog')).toContainText('Invented roof damage');
  await page.getByRole('button',{name:'Cancel',exact:true}).click();expect(f.writes()).toBe(0);
  await page.getByRole('button',{name:'Review household claim',exact:true}).click();
  await page.getByRole('dialog').getByRole('button',{name:'Submit household claim',exact:true}).click();
  await expect(page.locator('main .mvp-error').first()).toBeVisible();
  await expect(page.getByLabel('Damage description',{exact:true})).toHaveValue('Invented roof damage');
  await page.getByLabel('Guidance language / Wika ng gabay').selectOption('fil');
  await expect(page.getByLabel('Paglalarawan ng pinsala',{exact:true})).toHaveValue('Invented roof damage');
});

test('beneficiary registers through the form only: no CSV import is offered or requested',async({page})=>{
  const f=await fixture(page,{emptyHousehold:true});
  const templateReads:string[]=[];
  page.on('request',r=>{if(r.url().includes('/registry/csv'))templateReads.push(r.url());});
  await page.goto(f.url('registry'));
  await expect(page.getByLabel('Head name',{exact:true})).toBeVisible();
  await expect(page.getByText('Import household declarations from CSV',{exact:false})).toHaveCount(0);
  await expect(page.getByLabel('Completed UTF-8 CSV file')).toHaveCount(0);
  await page.waitForLoadState('networkidle');
  expect(templateReads).toEqual([]);
});
