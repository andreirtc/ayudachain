import {test,expect} from '@playwright/test';

test('beneficiary starts in Filipino with four phone destinations and preserves English choice',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('/mvp/beneficiary');
  await expect(page.getByRole('heading',{name:'Ayuda ko',exact:true})).toBeVisible();
  const nav=page.getByRole('navigation',{name:'Mga pangunahing destinasyon'});
  await expect(nav).toBeVisible();
  await expect(nav.getByRole('link')).toHaveCount(4);
  for(const label of ['Ayuda ko','Impormasyon namin','Mga tala','Humingi ng tulong'])await expect(nav.getByRole('link',{name:label,exact:true})).toBeVisible();
  await page.getByLabel('Guidance language / Wika ng gabay').selectOption('en');
  await expect(page.getByRole('heading',{name:'My assistance',exact:true})).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading',{name:'My assistance',exact:true})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.setViewportSize({width:1440,height:900});
  await expect(page.getByRole('navigation',{name:'Workspace navigation'})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Primary destinations'})).not.toBeVisible();
});

test('intermediate drawer supports keyboard and labelled grouped destinations',async({page})=>{
  await page.setViewportSize({width:800,height:900});
  await page.goto('/mvp/beneficiary');
  const trigger=page.getByRole('button',{name:'Buksan ang nabigasyon'});
  await trigger.click();
  await expect(page.getByRole('navigation',{name:'Workspace navigation'}).getByRole('link').first()).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(trigger).toBeFocused();
});

test('a saved English choice hydrates the Filipino-first server render without a mismatch error',async({page})=>{
  const errors:string[]=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.addInitScript(()=>localStorage.setItem('ayudachain.guidance-language','en'));
  await page.goto('/mvp/beneficiary/registry');
  await expect(page.locator('.ac-app')).toHaveAttribute('lang','en');
  expect(errors.filter(e=>/hydrat/i.test(e))).toEqual([]);
});
