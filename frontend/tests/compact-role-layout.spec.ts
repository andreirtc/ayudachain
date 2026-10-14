import {test,expect} from '@playwright/test';
const slugs=['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor'];
test('each role has readable task navigation, four phone shortcuts and reachable complete navigation',async({page})=>{
 for(const slug of slugs){
  await page.setViewportSize({width:1440,height:900});await page.goto('/mvp/'+slug);
  await expect(page.getByRole('heading',{level:1}).first()).toBeVisible();
  expect((await page.locator('.ac-sidebar').boundingBox())!.width).toBeLessThanOrEqual(240);
  await expect(page.locator('.ac-nav-full').first()).toBeVisible();
  await page.setViewportSize({width:390,height:844});
  const quick=page.getByRole('navigation',{name:'Quick navigation'});await expect(quick).toBeVisible();await expect(quick.getByRole('link')).toHaveCount(4);
  expect((await page.locator('.ac-contextbar').boundingBox())!.height).toBeLessThan(80);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.getByRole('button',{name:'Open navigation',exact:true}).click();
  await expect(page.getByRole('navigation',{name:'Workspace navigation'})).toBeVisible();
  await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Open navigation',exact:true})).toBeFocused();
  await quick.getByRole('link').nth(1).click();await expect(page.getByRole('heading',{level:1}).first()).toBeVisible();
 }
});
test('display preferences retain language/theme access and close with Escape and route changes',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/mvp/beneficiary');
 const trigger=page.locator('.ac-display-preferences>summary');await trigger.click();
 await page.getByLabel('Guidance language / Wika ng gabay').selectOption('fil');
 await page.getByRole('button',{name:'Dark',exact:true}).click();await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
 await page.keyboard.press('Escape');await expect(trigger).toBeFocused();await expect(page.getByLabel('Guidance language / Wika ng gabay')).not.toBeVisible();
 await trigger.click();await expect(page.getByLabel('Guidance language / Wika ng gabay')).toHaveValue('fil');
 await page.getByRole('navigation',{name:'Quick navigation'}).getByRole('link').nth(1).click();
 await expect(page.getByLabel('Guidance language / Wika ng gabay')).not.toBeVisible();
});
