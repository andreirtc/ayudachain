/* Read-only actual local UI captures. No fixtures, business writes or fake proofs.
 * Requires a completed isolated journey and installed repository Playwright.
 * Auditor reads/checks create their normal private inspection logs.
 */
const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const {chromium}=require(path.join(root,'frontend/node_modules/@playwright/test'));
const api='http://127.0.0.1:8000/api/v1';
async function read(route,actor){const r=await fetch(api+route,{headers:actor?{'X-Demo-Actor-ID':actor}:{}});if(!r.ok)throw new Error('Actual API unavailable: '+route);return(await r.json()).data;}
let browser;
(async()=>{
 const actors=await read('/actors/catalogue'),disasters=await read('/disasters');
 const dswd=actors.find(a=>a.role==='dswd'),auditor=actors.find(a=>a.role==='auditor');
 let disaster,rows;
 for(const d of disasters){const found=await read('/transactions?disaster_id='+d.id,dswd.id);if(found.filter(t=>t.business_status==='handed_over').length>=2){disaster=d;rows=found;break;}}
 if(!disaster)throw new Error('Complete both actual journey handovers before capturing');
 const registry=(await read('/registry',dswd.id)).households;
 const summary=rows.find(t=>t.household_name.includes('Maria Santos'))||rows.find(t=>t.household_name.includes('Own'))||rows[0];
 const own=await read('/transactions/'+summary.id,dswd.id);
 const recipient=actors.find(a=>a.id===registry.find(h=>h.id===own.household_id)?.beneficiary_actor_id);
 if(!recipient)throw new Error('Actual recipient linkage unavailable');
 const transaction=own,payer=actors.find(a=>a.id===transaction.receipt.payer_id);
 const barangay=actors.find(a=>a.role==='barangay'&&a.barangay_id===registry.find(h=>h.id===own.household_id)?.declared_barangay_id);
 const stamp=new Date().toISOString().replace(/[:.]/g,'-'),folder='captures-'+stamp;
 const out=path.join(__dirname,'evidence',folder);fs.mkdirSync(out);
 browser=await chromium.launch();const context=await browser.newContext();const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const route=(slug,actor,section='',record='')=>`/mvp/${slug}${section?'/'+section:''}?account=${actor.id}&disaster=${disaster.id}${record?'&record='+record:''}`;
 const stages=[
 ['directory','/mvp'],['dswd-overview',route('dswd-officer',dswd)],['dswd-funds',route('dswd-officer',dswd,'funds')],['dswd-registry',route('dswd-officer',dswd,'registry')],['dswd-claims',route('dswd-officer',dswd,'claims')],['dswd-lists',route('dswd-officer',dswd,'lists')],['dswd-sessions',route('dswd-officer',dswd,'sessions')],
 ['barangay-overview',route('barangay-officer',barangay)],['beneficiary-overview',route('beneficiary',recipient)],['beneficiary-receipt',route('beneficiary',recipient,'payouts',own.id)],['beneficiary-outcomes',route('beneficiary',recipient,'outcomes',own.id)],['disbursing-overview',route('disbursing-officer',payer)],['disbursing-receipt',route('disbursing-officer',payer,'payouts',own.id)],['auditor-overview',route('auditor',auditor)],['auditor-integrity',route('auditor',auditor,'audit')]
 ];
 const bilingual=stages.map(([name,url])=>[name,url,'en']).concat(stages.filter(([name])=>['directory','dswd-registry','barangay-overview','beneficiary-overview','disbursing-overview','auditor-integrity'].includes(name)).map(([name,url])=>[name,url,'fil']));
 const records=[];
 for(const theme of ['light','dark'])for(const width of [1440,390])for(const [name,url,language] of bilingual){
  if(language==='fil'&&theme==='dark')continue;
  if(theme==='dark'&&!['dswd-overview','beneficiary-receipt','auditor-integrity'].includes(name))continue;
  await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:3000'+url+(url.includes('?')?'&':'?')+'lang='+language);
  await page.evaluate(value=>{localStorage.setItem('ayudachain:theme',value);document.documentElement.setAttribute('data-theme',value);},theme);
  await page.getByRole('heading',{level:1}).first().waitFor();await page.waitForLoadState('networkidle');
  let checked;
  if(name==='auditor-integrity'){
   await page.getByLabel(language==='fil'?'Hanapin ang record':'Search proofs',{exact:true}).fill('handover');
   const block=page.locator('.ac-proof-entry').first();const check=block.getByRole('button',{name:language==='fil'?'I-check ngayon':'Check now',exact:true});await check.waitFor();
   const response=page.waitForResponse(r=>r.url().endsWith('/integrity/check')&&r.request().method()==='POST');await check.click();
   checked=(await(await response).json()).data;
   if(checked.result!=='match')throw new Error('Actual current check failed; no green capture inferred');
   await block.getByText(language==='fil'?'Match ang record sa blockchain':'Verified',{exact:true}).waitFor();await block.getByText(language==='fil'?'Detalye ng blockchain check':'Observed block and proof details',{exact:true}).click();await block.scrollIntoViewIfNeeded();
  }else if(name==='beneficiary-receipt'){
   await page.getByRole('heading',{name:/Handover recorded once/}).waitFor();
  }
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  if(overflow)throw new Error('Horizontal overflow in '+name+'/'+width+'/'+theme);
  const file=`${name}-${width}-${theme}${language==='fil'?'-taglish':''}.png`;await page.screenshot({path:path.join(out,file),fullPage:false});
  records.push({file,url,language,viewport:{width,height:900},theme,captured_at:new Date().toISOString(),horizontal_overflow:overflow,...(checked?{actual_integrity:checked}:{})});
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'provenance.json'),JSON.stringify({baseline:'4377db1 plus local finals changes',data:'invented local application records',blockchain:'actual loopback EVM, chain ID 31337',business_clock:'labelled accelerated synthetic clock may differ from wall time',page_errors:errors,records},null,2));
 if(errors.length)throw new Error('Page errors captured; inspect provenance before delivery');
 const lines=['# Actual application screenshots','','Captured from the running local finals lab on 14 October 2026. Invented records only; no mockups or synthetic chain results. Phone images are viewport emulation, not physical-device tests. Light/dark captures use actual application theme controls/state. Full provenance and current observed checks accompany the images.','',`[Capture metadata](evidence/${folder}/provenance.json)`,''];
 for(const r of records)lines.push(`- [${r.file}](evidence/${folder}/${r.file})`);
 fs.writeFileSync(path.join(__dirname,'SCREENSHOTS.md'),lines.join('\n')+'\n');
 console.log(JSON.stringify({directory:out,captures:records.length,page_errors:errors.length}));
})().catch(async e=>{if(browser)await browser.close();console.error(e.message);process.exitCode=1;});
