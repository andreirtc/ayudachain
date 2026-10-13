import { API, BASE_URL } from "./support";
import { test, expect, Page } from "./support";

const client = { "X-AyudaChain-Client": "web", Origin: BASE_URL };
test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, r => {
    const url = new URL(r.request().url()); url.hostname = "127.0.0.1"; url.port = new URL(API).port;
    return r.continue({url:url.toString()});
  });
});
async function apiLogin(page:Page, username:string) {
  expect((await page.context().request.post(API+"/api/auth/login", {headers:client,data:{username,password:"synthetic-test-password-only"}})).ok()).toBe(true);
  return {...client,"X-CSRF-Token":(await (await page.context().request.get(API+"/api/auth/session")).json()).csrf_token};
}
async function prepare(page:Page,state:string,viewport:string) {
  const id=`BEN-HOME-${state}-${viewport}`, api=page.context().request;
  let headers=await apiLogin(page,"demo-officer-01");
  const row=await api.get(API+"/api/beneficiaries/"+id);
  if(row.status()===404) expect((await api.post(API+"/api/beneficiaries",{headers,data:{beneficiary_id:id,household_name:`Synthetic ${state} home ${viewport}`,barangay_id:"BRGY-001",barangay_name:"San Isidro",batch_id:"RELIEF-2026-001"}})).status()).toBe(201);
  expect((await api.post(API+"/api/beneficiaries/"+id+"/verify",{headers,data:{status:state==="pending"?"FLAGGED_FOR_REVIEW":state==="rejected"?"REJECTED":"VERIFIED",review_notes:"Synthetic household starting-point QA"}})).ok()).toBe(true);
  let payout;
  if(state==="historical") {
    headers=await apiLogin(page,"demo-disbursing-001");
    const saved=await api.post(API+"/api/distributions/confirm",{headers:{...headers,"Idempotency-Key":"home-history-"+viewport},data:{beneficiary_id:id,batch_id:"RELIEF-2026-001",amount:"100.25"}});
    expect(saved.status()).toBe(201); payout=await saved.json();
    headers=await apiLogin(page,"demo-officer-01");
    const survivor=id+"-SURVIVOR";
    expect((await api.post(API+"/api/beneficiaries",{headers,data:{beneficiary_id:survivor,household_name:`Synthetic retained survivor ${viewport}`,barangay_id:"BRGY-001",barangay_name:"San Isidro",batch_id:"RELIEF-2026-001"}})).status()).toBe(201);
    expect((await api.post(API+"/api/beneficiaries/"+id+"/resolve-duplicate",{headers,data:{canonical_beneficiary_id:survivor,review_notes:"Retain the original synthetic household and receipt"}})).ok()).toBe(true);
  }
  expect((await api.post(API+"/api/auth/logout",{headers})).ok()).toBe(true);
  return {id,payout};
}
async function home(page:Page,state:string,viewport:string) {
  await page.goto("/sign-in");
  await page.getByRole("textbox",{name:"Account",exact:true}).fill(`synthetic-home-${state}-${viewport}`);
  await page.getByLabel("Password",{exact:true}).fill("synthetic-test-password-only");
  await page.getByRole("button",{name:"Sign in",exact:true}).click();
  await expect(page).toHaveURL(/\/household$/);
  await expect(page.getByRole("heading",{name:"My household",exact:true})).toBeVisible();
  await expect(page.getByRole("status")).toHaveCount(0);
}
for(const state of ["pending","approved","rejected","historical"]) {
  test(`own home keeps ${state} status and a grounded next step`,async({page},info)=>{
    const {id,payout}=await prepare(page,state,info.project.name);
    await page.emulateMedia({colorScheme:state==="rejected"||state==="historical"?"dark":"light"});
    await home(page,state,info.project.name);
    await expect(page.getByRole("heading",{name:{pending:"Awaiting staff review",approved:"Eligibility approved; no payout recorded",rejected:"Review the recorded decision",historical:"Historical household record"}[state],exact:true})).toBeVisible();
    await expect(page.getByRole("main").getByText(`Synthetic ${state} home ${info.project.name}`,{exact:true})).toBeVisible();
    await expect(page.getByRole("region",{name:"Household status"})).toContainText({pending:"Pending review",approved:"Approved",rejected:"Rejected",historical:"Retained duplicate"}[state]!);
    await expect(page.getByText("Juan Dela Cruz",{exact:true})).toHaveCount(0);
    await expect(page.getByText(payout?"A saved receipt is not a new appointment.":"Staff have not published a collection date, site or requirements",{exact:false})).toBeVisible();
    await expect(page.getByLabel("Collection instructions")).toHaveCount(0);
    if(payout) {
      await expect(page.getByRole("region",{name:"Payout and instructions"})).toContainText("₱100.25");
      await page.getByRole("link",{name:"Open saved receipt",exact:true}).click();
      await expect(page.getByLabel("Receipt",{exact:true})).toHaveValue(payout.distribution_id);
      await expect(page.getByRole("heading",{name:"Verification unavailable",exact:true})).toBeVisible();
      await page.goto("/household");
      await expect(page.getByRole("heading",{name:"Historical household record",exact:true})).toBeVisible();
    } else {
      await page.getByRole("button",{name:"Review household details",exact:true}).click();
      await expect(page.getByText(id,{exact:true})).toBeVisible();
      await expect(page.getByText("Household details and review history",{exact:true})).toBeFocused();
    }
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:info.outputPath("home-"+state+".png"),fullPage:true});
  });
}
test("failed reads clear prior context and never infer no payout; retry and revocation remain scoped",async({page},info)=>{
  await prepare(page,"approved",info.project.name); await home(page,"approved",info.project.name);
  await page.route(/8000\/api\/distributions$/,r=>r.abort(),{times:1});
  await page.getByRole("button",{name:"Refresh household",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Payout records unavailable",exact:true})).toBeVisible();
  await expect(page.getByText("Eligibility approved; no payout recorded",{exact:true})).toHaveCount(0);
  await page.getByRole("button",{name:"Retry payout records",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Eligibility approved; no payout recorded",exact:true})).toBeVisible();
  await page.route(/8000\/api\/beneficiaries\?/,r=>r.abort(),{times:1});
  await page.getByRole("button",{name:"Refresh household",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Household status unavailable",exact:true})).toBeVisible();
  await expect(page.getByRole("region",{name:"Household status"})).toHaveCount(0);
  await page.getByRole("button",{name:"Retry household",exact:true}).click();
  await expect(page.getByRole("region",{name:"Household status"})).toBeVisible();
  const session=await(await page.context().request.get(API+"/api/auth/session")).json();
  expect((await page.context().request.post(API+"/api/auth/logout",{headers:{...client,"X-CSRF-Token":session.csrf_token}})).ok()).toBe(true);
  await page.getByRole("button",{name:"Refresh household",exact:true}).click();
  await expect(page.getByRole("heading",{name:"Sign in to continue",exact:true})).toBeVisible();
  await expect(page.getByRole("region",{name:"Household status"})).toHaveCount(0);
  const target=new URL((await page.getByRole("main").getByRole("link",{name:"Sign in",exact:true}).getAttribute("href"))!,page.url());
  expect(target.searchParams.get("returnTo")).toBe("/household");
});
test("missing linked record and staff home cannot substitute another household",async({page},info)=>{
  await home(page,"missing",info.project.name);
  await expect(page.getByRole("heading",{name:"Linked household not found",exact:true})).toBeVisible();
  await expect(page.getByText("Juan Dela Cruz",{exact:true})).toHaveCount(0);
  await page.getByRole("button",{name:"Sign out",exact:true}).click();
  await apiLogin(page,"demo-auditor-01"); await page.goto("/household");
  await expect(page.getByRole("heading",{name:"Household home is for linked household accounts",exact:true})).toBeVisible();
  await expect(page.getByRole("region",{name:"Household status"})).toHaveCount(0);
});
