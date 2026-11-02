import {test,expect} from '@playwright/test';

test('assisted registration stays open while choosing a recipient and editing',async({page})=>{
  const actor='00000000-0000-4000-8000-000000000011',recipient='00000000-0000-4000-8000-000000000012';
  const barangay='00000000-0000-4000-8000-000000000013';
  let release!:()=>void,started!:()=>void;const held=new Promise<void>(r=>release=r),ready=new Promise<void>(r=>started=r);
  await page.route('**/api/v1/**',async route=>{
    const p=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(p==='/registry'){started();await held;}
    const data:Record<string,unknown>={
      '/actors/catalogue':[{id:actor,role:'barangay',display_name:'Invented helper',status:'active',barangay_id:barangay,position:'Punong Barangay'},{id:recipient,role:'beneficiary',display_name:'Invented recipient',status:'active',barangay_id:null,position:null}],
      '/disasters':[{id:barangay,name:'Synthetic UI flood'}],'/barangays':[{id:barangay,name:'Invented UI barangay'}],
      '/registry':{households:[{id:barangay,display_id:'DFC-2026-9011',revision:0,address:'Invented old lane',zone:'1',declared_barangay_id:barangay,residence_state:'unconfirmed',members:[{member_id:barangay,name:'Invented existing household',relationship:'head',is_head:true}]}]},
      '/intake':[],
    };await route.fulfill({json:{data:data[p]??[]}});
  });
  await page.goto(`/mvp/barangay-officer/registry?account=${actor}`);
  await ready;try{await expect(page.getByLabel('Head name',{exact:true})).toHaveCount(0);await expect(page.locator('main')).not.toContainText('No household in your current scope.');}finally{release();}
  await expect(page.getByRole('heading',{name:/DFC-2026-9011/})).toBeVisible();
  const registration=page.locator('details').filter({has:page.getByRole('heading',{name:'Assist household registration',exact:true})});
  if(await registration.getAttribute('open')===null)await registration.locator(':scope > summary').click();
  await page.getByLabel('Claimed beneficiary account (optional for no-account household)',{exact:true}).selectOption(recipient);
  await expect(page.getByLabel('Head name',{exact:true})).toBeVisible();
  await page.getByLabel('Head name',{exact:true}).fill('Invented new household');
  await expect(page.getByLabel('Head name',{exact:true})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Before you register',exact:true})).toBeVisible();
  await expect(page.locator('main')).toContainText('A contact phone is optional');
});

// UI-only synthetic fixture. No cash, chain observation or successful business
// result is supplied. Confirming receives a real-looking refusal, never success.
test('handover review supports cancel, Escape and one explicit confirmation',async({page})=>{
  const actor='00000000-0000-4000-8000-000000000001',disaster='00000000-0000-4000-8000-000000000002';
  const tx='00000000-0000-4000-8000-000000000003',session='00000000-0000-4000-8000-000000000004';
  const posts:string[]=[];
  await page.route('**/api/v1/**',async route=>{
    const p=new URL(route.request().url()).pathname.replace('/api/v1','');
    if(p.endsWith('/handover')){posts.push(p);await route.fulfill({status:409,json:{error:'current_presented_authorization_required'}});return;}
    const data:Record<string,unknown>={
      '/actors/catalogue':[{id:actor,role:'disbursing',display_name:'Invented UI payer',status:'active',barangay_id:null,position:null}],
      '/disasters':[{id:disaster,name:'Synthetic UI flood'}],'/barangays':[],
      '/sessions':[{id:session,date:'2026-10-14',site:'Invented UI hall',business_status:'open',assignments:[{id:actor,actor_id:actor,assignment_kind:'cash',display_name:'Invented UI payer'}],entries:[{entitlement_id:tx,transaction_id:tx,name:'Invented UI household'}]}],
      '/transactions':[{id:tx,household_name:'Invented UI household',business_status:'in_transaction',amount_centavos:'495000'}],
      [`/transactions/${tx}`]:{id:tx,disaster_id:disaster,entitlement_id:tx,household_id:tx,household_name:'Invented UI household',business_status:'in_transaction',amount_centavos:'495000',revision:1,photo_evidence_id:null,accepted_id_type:'Synthetic photo ID',identity_checks:[],receipt:null,current_attempt:{id:tx,attempt_number:1,path:'own_device',business_status:'presented',expires_at:'2026-10-14T00:00:00Z',current_id_check_id:tx}},
    };
    await route.fulfill({json:{data:data[p]??[]}});
  });
  await page.goto(`/mvp/disbursing-officer/payouts?account=${actor}&disaster=${disaster}&record=${tx}`);
  await page.getByLabel('Recipient payout code',{exact:true}).fill('123456');
  await page.getByLabel('Transaction',{exact:true}).selectOption(tx);
  await expect(page.getByLabel('Recipient payout code',{exact:true})).toBeVisible();
  await page.getByLabel('Recipient payout code',{exact:true}).fill('123456');
  const trigger=page.getByRole('button',{name:'Record cash handover',exact:true});
  await trigger.click();
  const dialog=page.getByRole('dialog',{name:'Record this cash handover?'});
  await expect(dialog).toBeVisible();await expect(dialog).toContainText('Invented UI household');await expect(dialog).toContainText('₱4,950.00');
  expect(posts).toHaveLength(0);
  await dialog.getByRole('button',{name:'Go back',exact:true}).click();
  await expect(dialog).not.toBeVisible();await expect(trigger).toBeFocused();expect(posts).toHaveLength(0);
  await trigger.click();await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();expect(posts).toHaveLength(0);
  await page.setViewportSize({width:390,height:844});await trigger.click();
  expect(await dialog.evaluate(e=>e.getBoundingClientRect().width<=innerWidth)).toBeTruthy();
  expect(await dialog.getByRole('button',{name:'Go back',exact:true}).evaluate(e=>e.getBoundingClientRect().height)).toBeGreaterThanOrEqual(44);
  await dialog.getByRole('button',{name:'Confirm recorded handover',exact:true}).click();
  await expect.poll(()=>posts.length).toBe(1);
  await expect(page.locator('main [role="alert"]').first()).toContainText('recipient');
  await expect(page.getByRole('heading',{name:/Handover recorded once/})).toHaveCount(0);
});
