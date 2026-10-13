import { API, BASE_URL } from "./support";
import { test, expect, Page } from "./support";

test.beforeEach(async ({page}) => { await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => { const url=new URL(route.request().url()); url.hostname="127.0.0.1"; url.port=new URL(API).port; return route.continue({url:url.toString()}); }); });
async function login(page:Page, name="demo-officer-01") { await page.goto("/sign-in"); await page.getByRole("textbox",{name:"Account",exact:true}).fill(name); await page.getByLabel("Password",{exact:true}).fill("synthetic-test-password-only"); await page.getByRole("button",{name:"Sign in",exact:true}).click(); await expect(page.getByText("Authenticated synthetic account.",{exact:false})).toBeVisible(); }
async function open(page:Page, content:string) { await page.goto("/beneficiaries");  await page.getByRole("button",{name:"Import a CSV",exact:true}).click(); await expect(page.getByRole("heading",{name:"Import a CSV",exact:true})).toBeFocused(); await page.getByLabel("Relief batch",{exact:true}).selectOption("RELIEF-2026-001"); await page.getByLabel("CSV to import",{exact:true}).setInputFiles({name:"synthetic.csv",mimeType:"text/csv",buffer:Buffer.from(content)}); }
function content(id:string) { return "beneficiary_id,household_name,barangay_id,barangay_name,dafac_id\n"+id+",Synthetic CSV Aster,BRGY-001,San Isidro,DFC-CSV-ASTER\n"+id+"-MATCH,Juan Dela Cruz,BRGY-001,San Isidro,DFC-2026-0002\n"; }

test("CSV preview, lost import response and repeated clicks save pending rows once",async({page},info)=>{
 await login(page); const id="BEN-CSV-UI-"+info.project.name;
 const before=await (await page.context().request.get(API+"/api/beneficiaries")).json(); await open(page,content(id));
 await page.context().setOffline(true); await expect(page.getByRole("button",{name:"Preview selected CSV",exact:true})).toBeDisabled(); await page.context().setOffline(false);
 await page.route(/8000\/api\/beneficiaries\/csv\/preview$/,r=>r.abort(),{times:1}); await page.getByRole("button",{name:"Preview selected CSV",exact:true}).click(); await expect(page.getByRole("dialog").getByRole("alert")).toBeVisible();
 await page.getByRole("button",{name:"Preview selected CSV",exact:true}).click(); await expect(page.getByRole("region",{name:"Import preview",exact:true})).toContainText("Ready for explicit import.");
 expect((await (await page.context().request.get(API+"/api/beneficiaries")).json()).length).toBe(before.length);
 await page.getByText(/Possible matches/).last().click(); await expect(page.getByRole("dialog").getByText(/Juan Dela Cruz \(BEN-0002\)/)).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true); await page.screenshot({path:info.outputPath("csv-preview.png"),fullPage:false});
 let calls=0; let importRequests=0; page.on("request", request => { if (/\/csv\/[^/]+\/import$/.test(request.url())) importRequests++; });
 await page.route(/8000\/api\/beneficiaries\/csv\/[^/]+\/import$/,async route=>{calls++; const response=await route.fetch({url:route.request().url().replace(":8000",":" + new URL(API).port)}); expect(response.status()).toBe(201); await route.abort();},{times:1});
 await page.getByRole("button",{name:"Import pending households",exact:true}).click(); await expect(page.getByRole("dialog").getByRole("alert")).toContainText("Retry this preview");
 await page.getByRole("button",{name:"Retry import",exact:true}).evaluate((el:HTMLButtonElement)=>{el.click();el.click();});
 await expect(page.getByRole("heading",{name:"2 households imported for review",exact:true})).toBeVisible(); expect(calls).toBe(1); expect(importRequests).toBe(2);
 const rows=await (await page.context().request.get(API+"/api/beneficiaries")).json(); const imported=rows.filter((r:{beneficiary_id:string})=>r.beneficiary_id===id||r.beneficiary_id===id+"-MATCH"); expect(imported).toHaveLength(2); expect(imported.every((r:{review_status:string;verification_status:string})=>r.review_status==="PENDING"&&r.verification_status==="FLAGGED_FOR_REVIEW")).toBe(true);
 await page.screenshot({path:info.outputPath("csv-imported.png"),fullPage:false}); await page.getByRole("button",{name:"Review "+id,exact:true}).click(); await expect(page.getByRole("button",{name:"Review Synthetic CSV Aster",exact:true})).toBeVisible();
});
test("invalid CSV shows row errors and never permits partial import",async({page},info)=>{
 await login(page); const before=await (await page.context().request.get(API+"/api/beneficiaries")).json(); await open(page,content("BEN-CSV-INVALID-"+info.project.name).replace("San Isidro","Wrong barangay")); await page.getByRole("button",{name:"Preview selected CSV",exact:true}).click(); await expect(page.getByRole("region",{name:"Import preview",exact:true})).toContainText("Correct the row errors"); await expect(page.getByRole("button",{name:"Import pending households",exact:true})).toBeDisabled(); await expect(page.getByRole("dialog")).toContainText("Barangay BRGY-001 is San Isidro"); expect(await (await page.context().request.get(API+"/api/beneficiaries")).json()).toEqual(before); await page.screenshot({path:info.outputPath("csv-errors.png"),fullPage:false});
});
test("registry changes invalidate an import until a fresh preview",async({page},info)=>{
 await login(page); await open(page,content("BEN-CSV-STALE-"+info.project.name)); await page.getByRole("button",{name:"Preview selected CSV",exact:true}).click(); await expect(page.getByRole("button",{name:"Import pending households",exact:true})).toBeEnabled();
 const session=await(await page.context().request.get(API+"/api/auth/session")).json(); const changed=await page.context().request.post(API+"/api/beneficiaries/BEN-0007/verify",{headers:{"X-AyudaChain-Client":"web","X-CSRF-Token":session.csrf_token,Origin:BASE_URL},data:{status:"FLAGGED_FOR_REVIEW",review_notes:"Synthetic change after CSV preview"}}); expect(changed.status()).toBe(200);
 // Change a name used by matching through another authorized registration.
 const created=await page.context().request.post(API+"/api/beneficiaries",{headers:{"X-AyudaChain-Client":"web","X-CSRF-Token":session.csrf_token,Origin:BASE_URL},data:{beneficiary_id:"BEN-CSV-CHANGED-"+info.project.name,household_name:"Synthetic CSV registry change",barangay_id:"BRGY-001",barangay_name:"San Isidro",batch_id:"RELIEF-2026-001"}}); expect(created.status()).toBe(201);
 await page.getByRole("button",{name:"Import pending households",exact:true}).click(); await expect(page.getByRole("dialog").getByRole("alert")).toContainText("Registry changed since preview"); await page.getByRole("button",{name:"Preview selected CSV",exact:true}).click(); await expect(page.getByRole("button",{name:"Import pending households",exact:true})).toBeEnabled();
});
test("other roles cannot import CSV through UI or API",async({page})=>{
 await login(page,"demo-auditor-01"); await page.goto("/beneficiaries");  await expect(page.getByRole("button",{name:"Import a CSV",exact:true})).toHaveCount(0); const response=await page.context().request.post(API+"/api/beneficiaries/csv/preview",{data:{batch_id:"RELIEF-2026-001",csv_content:content("BEN-DENIED")}}); expect(response.status()).toBe(403);
});
