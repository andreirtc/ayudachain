import {test,expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

const spaces=['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor'];
test('dedicated workspaces survive refresh, preserve role and fit both viewports',async({page})=>{
  for(const space of spaces){
    await page.goto(`/mvp/${space}`);
    await expect(page.getByRole('navigation',{name:'Workspace navigation'})).toBeVisible();
    await expect(page.getByLabel('Disaster',{exact:true}).or(page.locator('.ac-context-disaster')).first()).toBeVisible();
    await expect(page.getByLabel('Acting as',{exact:true})).toHaveCount(0);
    await page.reload();
    await expect(page.getByRole('navigation',{name:'Workspace navigation'})).toBeVisible();
    const links=await page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link').evaluateAll(nodes=>nodes.map(n=>(n as HTMLAnchorElement).getAttribute('href')));
    expect(links.every(link=>link?.startsWith(`/mvp/${space}`))).toBeTruthy();
    for(const width of [390,1440]){
      await page.setViewportSize({width,height:900});
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
    }
  }
});
test('entry links lead to five workspaces; unknown sections cannot display another role',async({page})=>{
  await page.goto('/mvp');
  await expect(page.getByRole('heading',{name:'Relief you can follow.'})).toBeVisible();
  for(const space of spaces)await expect(page.locator(`a[href="/mvp/${space}"]`)).toBeVisible();
  await page.goto('/mvp/barangay-officer/funds');
  await expect(page.getByRole('heading',{name:'Page unavailable'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Record a release'})).toHaveCount(0);
});
test('read-only auditor and restricted barangay keep private actions out',async({page})=>{
  await page.goto('/mvp/auditor/funds');
  await expect(page.getByRole('heading',{name:'Disaster funds',exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Record a release'})).toHaveCount(0);
  await page.goto('/mvp/barangay-officer/registry');
  await expect(page.getByRole('heading',{name:'Households',exact:true})).toBeVisible();
  await expect(page.locator('body')).not.toContainText('Contact:');
  await expect(page.getByRole('button',{name:'Review registry or linkage'})).toHaveCount(0);
});

test('keyboard navigation, scoped accounts and nested links retain context',async({page,request})=>{
  const actors=(await (await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data;
  const dswd=actors.find((a:{role:string;status:string})=>a.role==='dswd'&&a.status==='active');
  const d=(await (await request.get('http://127.0.0.1:8000/api/v1/disasters')).json()).data[0];
  let release!:()=>void;const held=new Promise<void>(resolve=>release=resolve);
  await page.route('**/api/v1/actors/catalogue',async route=>{const response=await route.fetch();await held;try{await route.fulfill({response});}catch{}});
  await page.goto(`/mvp/dswd-officer?account=${dswd.id}&disaster=${d.id}`);
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link',{name:'Skip to main content'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
  await page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link',{name:'Funding ledger'}).click();
  await expect(page).toHaveURL(new RegExp(`/mvp/dswd-officer/funds\\?account=${dswd.id}&disaster=${d.id}`));
  release();await page.unrouteAll({behavior:'ignoreErrors'});
  await page.locator('.ac-account > summary').click();
  await expect(page.getByLabel('Account',{exact:true}).locator('option')).toHaveCount(actors.filter((a:{role:string;status:string})=>a.role==='dswd'&&a.status==='active').length);
  const accountIds=await page.getByLabel('Account',{exact:true}).locator('option').evaluateAll(nodes=>nodes.map(n=>(n as HTMLOptionElement).value));
  expect(accountIds.every(id=>actors.some((a:{id:string;role:string})=>a.id===id&&a.role==='dswd'))).toBeTruthy();
  await page.setViewportSize({width:390,height:844});
  await page.getByRole('button',{name:'Open navigation'}).click();
  await expect(page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link').first()).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button',{name:'Open navigation'})).toBeFocused();
  await expect(page.getByRole('navigation',{name:'Workspace navigation'})).not.toBeVisible();
  await page.getByRole('button',{name:'Open navigation'}).click();
  await page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link',{name:'Claim review'}).click();
  await expect(page.getByRole('heading',{name:'Claims and review',exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Open navigation'})).toHaveAttribute('aria-expanded','false');
});

test('edited original-backed release survives refresh and cannot be changed by auditor',async({page,request})=>{
  const root=path.resolve(__dirname,'../..');
  const actors=(await (await request.get('http://127.0.0.1:8000/api/v1/actors/catalogue')).json()).data;
  const dswd=actors.find((a:{role:string})=>a.role==='dswd'),auditor=actors.find((a:{role:string})=>a.role==='auditor');
  const disaster=(await (await request.get('http://127.0.0.1:8000/api/v1/disasters')).json()).data[0].id;
  const reference='DFC-2026-UX'+Date.now();
  await page.goto(`/mvp/dswd-officer/funds?account=${dswd.id}&disaster=${disaster}`);
  await page.getByRole('button',{name:'Record a release'}).click();
  const bytes=execFileSync(path.join(root,'.venv/Scripts/python.exe'),['-c',"from backend.scripts.synthetic_evidence import synthetic_pdf; import sys; sys.stdout.buffer.write(synthetic_pdf('SYNTHETIC RELEASE '+sys.argv[1]+'\\nAmount: PHP 12,345.00'))",reference],{cwd:root});
  await page.getByLabel('Release original',{exact:true}).setInputFiles({name:'synthetic-release.pdf',mimeType:'application/pdf',buffer:bytes});
  await expect(page.getByLabel('Confirmed amount (PHP)',{exact:true})).toHaveValue('12345.00');
  await page.getByLabel('Reference number',{exact:true}).fill(reference);
  await page.getByLabel('Confirmed amount (PHP)',{exact:true}).fill('12350.50');
  await page.getByLabel('Covered area',{exact:true}).fill('Invented Sapa');
  await page.getByLabel('Printed signatory name',{exact:true}).fill('Invented Tala Sinta');
  await page.getByLabel('Printed signatory role',{exact:true}).fill('Synthetic Regional Director');
  await page.getByLabel('Purpose',{exact:true}).fill('Invented disaster cash assistance');
  await page.getByRole('button',{name:'Confirm and record',exact:true}).click();
  await expect(page.getByRole('status').filter({hasText:'Saved to the ledger'})).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading',{name:reference+' · Release',exact:true})).toBeVisible();
  await page.goto(`/mvp/auditor/funds?account=${auditor.id}&disaster=${disaster}`);
  const entry=page.locator('article').filter({has:page.getByRole('heading',{name:reference+' · Release',exact:true})});
  await expect(entry).toContainText('₱12,350.50');
  await expect(entry.getByRole('button',{name:'Append correction'})).toHaveCount(0);
  await entry.getByText('Evidence, amount review and chain proofs',{exact:true}).click();
  // Confirm the actual new release has anchored before asking for a current read.
  await expect.poll(async()=>{
    const r=await request.get(`http://127.0.0.1:8000/api/v1/funds?disaster_id=${disaster}`,{headers:{'X-Demo-Actor-ID':auditor.id}});
    expect(r.ok()).toBeTruthy();const saved=(await r.json()).data.entries.find((e:{reference_number:string})=>e.reference_number===reference);
    return !!saved&&saved.proofs.length>0&&saved.proofs.every((p:{state:string})=>p.state==='confirmed');
  },{timeout:40000}).toBeTruthy();
  const proof=entry.locator('.mvp-proof').first(),currentRead=page.waitForResponse(r=>r.url().endsWith('/integrity/check')&&r.request().method()==='POST');
  await proof.getByRole('button',{name:'Check chain now'}).click();expect((await(await currentRead).json()).data.result).toBe('match');
  await expect(proof.locator('.ac-integrity-result')).toContainText(/\bVerified\b/);
  // A failed subsequent request clears current verification while retaining a labelled earlier match.
  await page.route('**/api/v1/integrity/check',route=>route.abort('connectionfailed'));
  await proof.getByRole('button',{name:'Check chain now'}).click();
  await expect(proof.locator('.ac-integrity-result')).not.toContainText(/\bVerified\b/);
  await expect(proof).toContainText(/Last match/i);await expect(proof).toContainText(/refresh failed/i);
});

test('all principal role sections render without horizontal overflow',async({page})=>{
  const sections:Record<string,string[]>={beneficiary:['registry','claims','lists','sessions','payouts','outcomes'],'barangay-officer':['claims','registry','lists'],'dswd-officer':['funds','registry','claims','lists','sessions','payouts','outcomes','audit'],'disbursing-officer':['sessions','payouts','outcomes'],auditor:['funds','claims','registry','lists','sessions','payouts','outcomes','audit']};
  for(const [role,paths] of Object.entries(sections))for(const section of paths){
    await page.goto(`/mvp/${role}/${section}`);
    await expect(page.locator('#main-content h1')).toBeVisible();
    await page.waitForLoadState('networkidle');
    for(const width of [1440,390]){
      await page.setViewportSize({width,height:900});
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${role}/${section} at ${width}`).toBeTruthy();
    }
  }
});

test('failed dashboard and audit reads stay unavailable until a successful retry',async({page})=>{
  await page.route('**/api/v1/audit/overview?*',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic connection failure'})}));
  await page.goto('/mvp/dswd-officer');
  await expect(page.getByRole('heading',{name:'Records unavailable',exact:true})).toBeVisible();
  await expect(page.getByText('Your response queue is clear')).toHaveCount(0);
  await page.goto('/mvp/dswd-officer/audit');
  await expect(page.getByRole('heading',{name:'Evidence unavailable',exact:true})).toBeVisible();
  await expect(page.getByText('No exceptions recorded. Current chain checks are available below.')).toHaveCount(0);
  await page.unroute('**/api/v1/audit/overview?*');
  await page.getByRole('button',{name:'Try again',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Exceptions and supporting records',exact:true})).toBeVisible();
  // The Auditor's Verify page no longer reads exceptions; its proof read fails closed instead.
  await page.route('**/api/v1/audit/proofs',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic connection failure'})}));
  await page.goto('/mvp/auditor/audit');
  await expect(page.getByRole('heading',{name:'Evidence unavailable',exact:true})).toBeVisible();
  await page.unroute('**/api/v1/audit/proofs');
  await page.getByRole('button',{name:'Try again',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Verify',exact:true})).toBeVisible();
});
