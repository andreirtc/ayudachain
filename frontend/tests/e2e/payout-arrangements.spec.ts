import {test,expect,Page} from "@playwright/test";
const API="http://127.0.0.1:8101";
test.beforeEach(async({page})=>{await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//,r=>{const u=new URL(r.request().url());u.hostname="127.0.0.1";u.port="8101";return r.continue({url:u.toString()});});});
async function login(page:Page,id="demo-officer-01"){await page.goto("/sign-in");await page.getByRole("textbox",{name:"Account",exact:true}).fill(id);await page.getByLabel("Password",{exact:true}).fill("synthetic-test-password-only");await page.getByRole("button",{name:"Sign in",exact:true}).click();await expect(page.getByText("Authenticated synthetic account.",{exact:false})).toBeVisible();}
async function signOut(page:Page){await page.getByRole("button",{name:"Sign out",exact:true}).click();}
async function headers(page:Page){const s=await(await page.context().request.get(API+"/api/auth/session")).json();return {"X-AyudaChain-Client":"web","X-CSRF-Token":s.csrf_token,Origin:"http://127.0.0.1:3101"};}
const soon=new Date(Date.now()+7*864e5).toISOString().slice(0,10);

test("staff publish, edit and cancel instructions that the included household reads without staff notes",async({page},info)=>{
 await login(page);const h=await headers(page),request=page.context().request;
 expect((await request.post(API+"/api/beneficiaries/BEN-0004/verify",{headers:h,data:{status:"VERIFIED",review_notes:"Inspected synthetic household for arrangement"}})).ok()).toBe(true);
 const list=await(await request.post(API+"/api/validated-lists/prepare",{headers:h,data:{batch_id:"RELIEF-2026-001",barangay_id:"BRGY-001",request_id:crypto.randomUUID()}})).json();
 expect((await request.post(API+"/api/validated-lists/"+list.list_id+"/finalize",{headers:h,data:{confirm:true,reason:"Inspected synthetic list"}})).status()).toBe(201);
 await page.goto("/lists?list_id="+list.list_id);await page.getByRole("link",{name:"Payout arrangement",exact:true}).click();await expect(page).toHaveURL(new RegExp("/arrangements\\?list_id="+list.list_id));
 await expect(page.getByLabel("Finalized list version")).toHaveValue(list.list_id);
 await page.getByLabel("Collection date").fill(soon);await page.getByLabel("Time window").fill("8:00 AM - 12:00 NN");await page.getByLabel("Collection site").fill("San Isidro covered court "+info.project.name);
 await page.getByLabel("Requirements to bring (one per line)").fill("Any government ID\nHousehold reference");await page.getByLabel("Responsible staff shown to households").fill("Synthetic payout team lead");
 const publish=page.getByRole("button",{name:"Publish arrangement",exact:true});await publish.evaluate((b:HTMLButtonElement)=>{b.click();b.click();});
 await expect(page.getByText("Arrangement published to included households.",{exact:true})).toBeVisible();
 const selected=page.getByRole("region",{name:"Selected arrangement"});await expect(selected).toContainText("San Isidro covered court "+info.project.name);await expect(selected).toContainText("Scheduled · revision 1");
 expect((await(await request.get(API+"/api/arrangements")).json()).filter((a:{list_id:string})=>a.list_id===list.list_id)).toHaveLength(1);
 await selected.getByRole("button",{name:"Edit arrangement",exact:true}).click();await selected.getByLabel("Collection site").fill("Barangay hall "+info.project.name);await selected.getByLabel("Reason (staff only)").fill("Private venue note for staff");
 await selected.getByRole("button",{name:"Save new revision",exact:true}).click();await expect(page.getByText("Updated arrangement saved; earlier revisions stay retained.",{exact:true})).toBeVisible();await expect(selected).toContainText("Scheduled · revision 2");
 await selected.getByText("Revision history (2)",{exact:true}).click();await expect(selected).toContainText("San Isidro covered court "+info.project.name);
 await page.emulateMedia({colorScheme:info.project.name==="phone"?"dark":"light"});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:info.outputPath("staff-arrangement.png"),fullPage:true});
 await signOut(page);await login(page,"demo-beneficiary-01");await page.goto("/household");
 await expect(page.getByRole("region",{name:"Next step"})).toContainText("Collect your payout on");
 const instructions=page.getByLabel("Collection instructions");await expect(instructions).toContainText("Barangay hall "+info.project.name);await expect(instructions).toContainText("Any government ID");await expect(instructions).toContainText("(updated)");
 await expect(page.getByText("Private venue note for staff")).toHaveCount(0);await page.screenshot({path:info.outputPath("household-instructions.png"),fullPage:true});
 await signOut(page);await login(page);await page.goto("/arrangements?list_id="+list.list_id);
 await selected.getByRole("button",{name:"Cancel arrangement",exact:true}).click();await selected.getByLabel("Reason (staff only)").fill("Typhoon signal raised");await selected.getByRole("button",{name:"Confirm cancellation",exact:true}).click();
 await expect(selected).toContainText("Cancelled · revision 3");await expect(selected.getByRole("button",{name:"Edit arrangement",exact:true})).toHaveCount(0);
 await signOut(page);await login(page,"demo-beneficiary-01");await page.goto("/household");
 await expect(page.getByRole("main").getByRole("alert")).toContainText("was cancelled by staff");await expect(page.getByLabel("Collection instructions")).toHaveCount(0);
});

test("household and read-only staff cannot change arrangements; missing links substitute nothing",async({page})=>{
 await login(page,"demo-beneficiary-01");await page.goto("/arrangements");await expect(page.getByRole("heading",{name:"Payout arrangements are a staff task",exact:true})).toBeVisible();
 expect((await page.context().request.get(API+"/api/arrangements")).status()).toBe(403);
 await signOut(page);await login(page,"demo-auditor-01");await page.goto("/arrangements?list_id=LIST-MISSING");
 await expect(page.getByRole("heading",{name:"Arrangement unavailable",exact:true})).toBeVisible();await expect(page.getByRole("button",{name:"Publish arrangement",exact:true})).toHaveCount(0);
 expect((await page.context().request.post(API+"/api/arrangements",{headers:await headers(page),data:{list_id:"LIST-MISSING",request_id:crypto.randomUUID(),collection_date:soon,time_window:"AM",site:"Hall",requirements:["ID"],responsible_staff:"Lead"}})).status()).toBe(403);
});
