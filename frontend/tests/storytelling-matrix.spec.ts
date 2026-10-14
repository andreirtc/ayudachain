import {test,expect,Page} from '@playwright/test';
// Phase 5 matrix over the live synthetic workspaces. It checks layout, theme, language and shell composition only;
// it does not establish workflow correctness, verification or contrast measurements.
const roles=['beneficiary','barangay-officer','dswd-officer','disbursing-officer','auditor'];
async function open(page:Page,role:string,width:number,theme:'light'|'dark',language:'en'|'fil',height=900){
  await page.addInitScript(([th,lang])=>{localStorage.setItem('ayudachain:theme',th);localStorage.setItem('ayudachain.guidance-language',lang);},[theme,language]);
  await page.setViewportSize({width,height});
  await page.goto('/mvp/'+role);await expect(page.locator('main')).toBeVisible();
  await page.waitForLoadState('networkidle');
}
for(const role of roles)for(const width of [390,1440])for(const theme of ['light','dark'] as const)for(const language of ['en','fil'] as const){
  test(`${role} at ${width}px in ${theme} / ${language} fits, has no page errors and uses the right shell`,async({page})=>{
    const errors:string[]=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error'&&!/Failed to load resource/.test(m.text()))errors.push(m.text());});
    await open(page,role,width,theme,language);
    await expect(page.locator('html')).toHaveAttribute('data-theme',theme);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal page overflow').toBeTruthy();
    const bottom=page.locator('.ac-bottom-nav');
    if(width<760){
      await expect(bottom).toBeVisible();
      const links=bottom.getByRole('link');expect(await links.count()).toBeLessThanOrEqual(4);
      for(const box of await links.evaluateAll(els=>els.map(e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height};})))expect(box.h).toBeGreaterThanOrEqual(44);
      // The bar must not cover the final content: the frame reserves at least the bar's height.
      const reserved=await page.evaluate(()=>{const f=document.querySelector('.ac-main-frame') as HTMLElement,b=document.querySelector('.ac-bottom-nav') as HTMLElement;return parseFloat(getComputedStyle(f).paddingBottom)-b.getBoundingClientRect().height;});
      expect(reserved).toBeGreaterThanOrEqual(0);
    }else await expect(bottom).toBeHidden();
    // Minimum readable text: no visible text node below 13px.
    const small=await page.evaluate(()=>{const out:string[]=[];const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n:Node|null;while((n=walker.nextNode())){const el=n.parentElement;if(!el||!n.textContent?.trim())continue;if(el.closest('script,style,nextjs-portal,[hidden],[aria-hidden="true"]'))continue;const cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden')continue;const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;if(parseFloat(cs.fontSize)<13)out.push(`${el.tagName.toLowerCase()}.${el.className}:${cs.fontSize}:${n.textContent.trim().slice(0,30)}`);}return out.slice(0,8);});
    expect(small,'text smaller than 13px').toEqual([]);
    expect(errors,'page or console errors').toEqual([]);
  });
}
for(const role of ['beneficiary','dswd-officer'])test(`${role} shell changes exactly at the 760px and 1024px breakpoints`,async({page})=>{
  await open(page,role,759,'light','en');
  await expect(page.locator('.ac-bottom-nav')).toBeVisible();
  for(const [width,bottom,menu,sidebar] of [[760,false,true,false],[1023,false,true,false],[1024,false,false,true]] as const){
    await page.setViewportSize({width,height:900});
    if(bottom)await expect(page.locator('.ac-bottom-nav')).toBeVisible();else await expect(page.locator('.ac-bottom-nav')).toBeHidden();
    const menuButton=page.getByRole('button',{name:/Open navigation|Buksan ang nabigasyon/});
    if(menu)await expect(menuButton).toBeVisible();else await expect(menuButton).toBeHidden();
    const nav=page.getByRole('navigation',{name:'Workspace navigation'});
    if(sidebar)await expect(nav).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  }
});

// The desktop navigation must be wide enough that every role's labels stay on one line in both languages.
for(const role of roles)for(const language of ['en','fil'] as const)for(const width of [1024,1280,1440,1920])test(`${role} sidebar at ${width}px in ${language} is wide and no destination label wraps`,async({page})=>{
  await open(page,role,width,'light',language);
  const taskPages=page.locator('.ac-secondary-nav summary');if(await taskPages.count())await taskPages.click();
  const result=await page.evaluate(()=>{
    const sidebar=document.querySelector('.ac-sidebar') as HTMLElement,frame=document.querySelector('.ac-main-frame') as HTMLElement;
    // Count rendered text lines exactly: distinct vertical positions of the text's client rectangles.
    const lines=(el:Element)=>{const tops=new Set<number>(),walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node:Node|null;while((node=walker.nextNode())){if(!node.textContent?.trim())continue;const range=document.createRange();range.selectNodeContents(node);for(const r of range.getClientRects())if(r.width>0)tops.add(Math.round(r.top/6));}return tops.size;};
    const visible=(a:Element)=>(a as HTMLElement).offsetParent!==null;
    const links=[...sidebar.querySelectorAll('nav a')].filter(visible) as HTMLElement[];
    const bottom=[...sidebar.querySelectorAll('.ac-sidebar-bottom a, a.ac-all-workspaces')].filter(visible);
    return {width:Math.round(sidebar.getBoundingClientRect().width),frameLeft:Math.round(frame.getBoundingClientRect().left),count:links.length,wrapped:links.filter(a=>lines(a)>1).map(a=>a.textContent!.trim()),wrappedBottom:bottom.filter(a=>lines(a)>1).map(a=>a.textContent!.trim()),clipped:sidebar.scrollWidth>sidebar.clientWidth+1,rowHeights:links.map(a=>Math.round(a.getBoundingClientRect().height))};
  });
  expect(result.width,'sidebar is at least 280px wide on desktop').toBeGreaterThanOrEqual(280);
  expect(result.frameLeft,'content starts exactly where the sidebar ends').toBe(result.width);
  expect(result.count).toBeGreaterThan(0);
  expect(result.wrapped,'destination labels wrapping onto a second line').toEqual([]);
  expect(result.wrappedBottom,'All workspaces link wrapping').toEqual([]);
  expect(result.clipped,'sidebar content clipped horizontally').toBeFalsy();
  expect(Math.max(...result.rowHeights),'one-line rows, icon beside label').toBeLessThanOrEqual(60);
});
