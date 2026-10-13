import {test,expect,Page} from '@playwright/test';
import {workspacePath} from './workspace-navigation';
import type {Claim} from '../components/mvp/Claims';

const disaster='00000000-0000-4000-8000-000000000002';
const claimID='00000000-0000-4000-8000-000000000003';
const category='00000000-0000-4000-8000-000000000004';
const account='00000000-0000-4000-8000-000000000005';
const candidate='00000000-0000-4000-8000-000000000006';

function claimFixture():Claim{
 const compared={household_id:account,display_id:'DFC-2026-0001',registry_version_id:'00000000-0000-4000-8000-000000000007',household_revision:0,current_registry_version_id:'00000000-0000-4000-8000-000000000007',current_household_revision:0,version_changed:false,address:'Invented street 12',barangay_id:'00000000-0000-4000-8000-000000000008',members:[{member_id:account,name:'Invented Tala Salonga',birth_date:'1980-01-02',is_head:true}]};
 return {id:claimID,household_id:account,disaster_id:disaster,business_status:'awaiting_dswd',revision:0,current_submission_id:'submission',submission:{stated_category_id:category,damage_description:'Invented damaged roof',new_information:null},household:{name:'Invented Tala Salonga',address:'Invented street 12',zone:'7',barangay_id:compared.barangay_id},rounds:[],decisions:[],latest_check:{id:'check-one',risk_score:3,algorithm_version:'local.flags.v1:fixture',created_at:'2026-10-12T00:00:00Z',compared_data_revision:5,current_data_revision:5,stale:false,simulation_adapter:'Simulated National ID check',simulation_result:{simulated:true,identity_verified:false},flags:[{code:'person_in_two_households',weight:3,matched_household_id:candidate,comparison_available:true,scores:{name_similarity:'0.9500',birth_date_match:true},comparison:{source:compared,candidate:{...compared,household_id:candidate,display_id:'DFC-2026-0002',members:[{...compared.members[0],member_id:candidate,name:'Invented Tala Salunga'}]}}}]}};
}

async function fixture(page:Page,role:'dswd'|'auditor'){
 const claim=claimFixture(),decisions:Record<string,unknown>[]=[],opened:string[]=[];
 // Synthetic projection and review-state fixtures only. No chain result or fabricated verification is provided.
 await page.route('**/api/v1/**',async route=>{
  const path=new URL(route.request().url()).pathname.replace('/api/v1','');
  let data:unknown=[];
  if(path==='/actors/catalogue')data=[{id:account,role,display_name:'Invented Review Officer',status:'active',position:null,barangay_id:null}];
  else if(path==='/disasters')data=[{id:disaster,name:'Invented review flood'}];
  else if(path==='/categories')data=[{id:category,name:'Invented damaged roof'}];
  else if(path===`/claims/${claimID}`){opened.push(path);data=claim;}
  else if(path===`/claims/${claimID}/decisions`){decisions.push(route.request().postDataJSON());data={resources:[]};}
  else if(path==='/claims'){throw new Error('A direct claim link must fetch the record rather than relying on a truncated queue.');}
  await route.fulfill({json:{data,meta:{identity_assurance:'claimed_unverified',authentication:'pending'}}});
 });
 await page.goto(workspacePath(role,account,'claims',disaster)+'&record='+claimID);
 return {claim,decisions,opened};
}

test('review projection fixture: acknowledgment resets for changed check, claim revision and comparison data',async({page})=>{
 const {claim,decisions,opened}=await fixture(page,'dswd');
 const acknowledged=page.getByLabel('I reviewed this current check and its flags, the response thread and available evidence.',{exact:true});
 const decide=page.getByRole('button',{name:'Save human decision',exact:true});
 await expect(page.getByRole('heading',{name:'Review and decide',exact:true})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Candidate household: DFC-2026-0002',exact:true})).toBeVisible();
 await expect(page.getByText('Birth dates matched.',{exact:true}).filter({visible:true})).toHaveCount(1);
 await page.getByLabel('Final category',{exact:true}).selectOption(category);
 await expect(decide).toBeDisabled();
 for(const change of [()=>{claim.latest_check!.id='check-two';},()=>{claim.revision++;},()=>{claim.latest_check!.current_data_revision++;claim.latest_check!.stale=true;}]){
  await acknowledged.check();change();await page.getByRole('button',{name:'Refresh claims',exact:true}).click();
  await expect(acknowledged).not.toBeChecked();await expect(decide).toBeDisabled();
 }
 await acknowledged.check();await expect(decide).toBeDisabled();
 await expect(page.getByRole('status').filter({hasText:'This check is stale.'}).filter({visible:true})).toHaveCount(1);
 expect(decisions).toHaveLength(0);
 claim.latest_check!.id='check-three';claim.latest_check!.compared_data_revision=claim.latest_check!.current_data_revision;claim.latest_check!.stale=false;
 await page.getByRole('button',{name:'Refresh claims',exact:true}).click();
 await expect(acknowledged).not.toBeChecked();await acknowledged.check();await expect(decide).toBeEnabled();
 await decide.click();await expect.poll(()=>decisions.length).toBe(1);
 expect(decisions[0]).toMatchObject({expected_revision:1,reviewed_check_id:'check-three',action:'approve',category_id:category});
 expect(opened.length).toBeGreaterThan(3);
});

test('review projection fixture: Auditor inspects frozen comparisons without decision or recheck controls',async({page})=>{
 const {decisions}=await fixture(page,'auditor');
 await page.getByText('Review flags - weighted priority 3',{exact:true}).click();
 await expect(page.getByRole('heading',{name:'Candidate household: DFC-2026-0002',exact:true})).toBeVisible();
 await expect(page.getByText('Weighted review priority: 3. This is not a fraud probability or an eligibility decision.',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Save human decision'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'Refresh comparison'})).toHaveCount(0);
 await expect(page.getByRole('checkbox')).toHaveCount(0);
 expect(decisions).toHaveLength(0);
});
