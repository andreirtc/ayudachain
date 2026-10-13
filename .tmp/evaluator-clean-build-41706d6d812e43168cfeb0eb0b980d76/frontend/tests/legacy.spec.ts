import {test,expect} from '@playwright/test';
test('legacy verification has explicit coverage and no fabricated fraud controls',async({page})=>{
  await page.goto('/verify');
  await expect(page.getByRole('heading',{name:'Legacy receipt verification',exact:true})).toBeVisible();
  await expect(page.getByText('Original normalized receipt text and distribution fields only.',{exact:true})).toBeVisible();
  await expect(page.getByText('Pitch Demonstration:',{exact:false})).toHaveCount(0);
});
