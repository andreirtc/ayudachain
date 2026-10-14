import {test,expect} from '@playwright/test';
test.beforeEach(async({page})=>{await page.addInitScript(()=>{if(!localStorage.getItem('ayudachain.guidance-language'))localStorage.setItem('ayudachain.guidance-language','en');});});

test('theme choice survives refresh and device mode follows the browser on phone and desktop',async({page})=>{
  await page.emulateMedia({colorScheme:'light'});
  await page.goto('/mvp');
  const theme=page.getByRole('group',{name:'Colour theme'});
  await expect(theme).toBeVisible();
  const surface=()=>page.locator('.ac-entry').evaluate(el=>getComputedStyle(el).backgroundColor);
  const light=await surface();
  await theme.getByRole('button',{name:'Dark theme',exact:true}).click();
  const dark=await surface();
  expect(dark).not.toBe(light);
  await page.reload();
  await expect(theme.getByRole('button',{name:'Dark theme',exact:true})).toHaveAttribute('aria-pressed','true');
  expect(await surface()).toBe(dark);
  await page.emulateMedia({colorScheme:'dark'});
  await theme.getByRole('button',{name:'Light theme',exact:true}).click();
  expect(await surface()).toBe(light);
  await theme.getByRole('button',{name:'Use device theme',exact:true}).click();
  expect(await surface()).toBe(dark);
  await page.emulateMedia({colorScheme:'light'});
  expect(await surface()).toBe(light);
  await page.reload();
  await expect(theme.getByRole('button',{name:'Use device theme',exact:true})).toHaveAttribute('aria-pressed','true');
  for(const width of [390,1440]){
    await page.setViewportSize({width,height:900});
    await expect(theme).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  }
});

test('workspace retains theme and directory links even when records are unavailable',async({page})=>{
  // Fail catalogue reads explicitly; this test supplies no business or chain success.
  await page.route('**/api/v1/**',route=>route.fulfill({status:503,json:{error:'network_unavailable'}}));
  await page.goto('/mvp');
  await page.getByRole('button',{name:'Dark theme',exact:true}).click();
  await page.goto('/mvp/auditor');
  await expect(page.getByRole('button',{name:'Dark theme',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('heading',{name:'Connection unavailable',exact:true})).toBeVisible();
  await expect(page.getByRole('link',{name:'All workspaces',exact:true})).toHaveAttribute('href','/mvp');
  await page.getByRole('link',{name:'AyudaChain, all workspaces',exact:true}).click();
  await expect(page).toHaveURL(/\/mvp$/);
  await page.goto('/mvp/auditor');
  await page.setViewportSize({width:390,height:900});
  await page.getByRole('button',{name:'Open navigation',exact:true}).click();
  await page.getByRole('link',{name:'All workspaces',exact:true}).click();
  await expect(page).toHaveURL(/\/mvp$/);
  await expect(page.getByRole('button',{name:'Dark theme',exact:true})).toHaveAttribute('aria-pressed','true');
});
