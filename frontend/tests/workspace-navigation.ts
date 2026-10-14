const slugs:Record<string,string>={beneficiary:'beneficiary',barangay:'barangay-officer',dswd:'dswd-officer',disbursing:'disbursing-officer',auditor:'auditor'};
export function workspacePath(role:string,account:string,section='overview',disaster?:string){const query=new URLSearchParams({account,...(disaster?{disaster}:{})});return '/mvp/'+slugs[role]+(section==='overview'?'':'/'+section)+'?'+query.toString();}

// Real synthetic setup for live lookup regressions after the cash journey has
// closed its paid sessions. Never reopen or repay an existing handover.
export async function prepareLookupSession(request:import('@playwright/test').APIRequestContext){
 const {expect}=await import('@playwright/test'),{execFileSync}=await import('node:child_process'),path=await import('node:path');
 const root=path.resolve(__dirname,'../..'),api='http://127.0.0.1:8000/api/v1';
 async function get(route:string,actor?:string){const r=await request.get(api+route,{headers:actor?{'X-Demo-Actor-ID':actor}:{}});expect(r.ok()).toBeTruthy();return(await r.json()).data;}
 async function post(route:string,actor:string,data:object){const r=await request.post(api+route,{headers:{'X-Demo-Actor-ID':actor,'Idempotency-Key':crypto.randomUUID()},data});expect(r.ok(),await r.text()).toBeTruthy();return(await r.json()).data;}
 async function original(purpose:string,actor:string){
  const buffer=execFileSync(path.join(root,'.venv/Scripts/python.exe'),['-c','from backend.scripts.synthetic_evidence import synthetic_pdf; import sys; sys.stdout.buffer.write(synthetic_pdf(sys.argv[1]))','Invented lookup '+purpose+' '+Date.now()],{cwd:root});
  const r=await request.post(api+'/evidence',{headers:{'X-Demo-Actor-ID':actor,'Idempotency-Key':crypto.randomUUID()},multipart:{purpose,file:{name:'invented-lookup.pdf',mimeType:'application/pdf',buffer}}});expect(r.ok()).toBeTruthy();return(await r.json()).data.resources[0].id;
 }
 const actors=await get('/actors/catalogue'),dswd=actors.find((a:any)=>a.role==='dswd'),recipient=actors.filter((a:any)=>a.role==='beneficiary')[2],punong=actors.find((a:any)=>a.position==='Punong Barangay'),officers=actors.filter((a:any)=>a.role==='barangay'&&a.barangay_id===punong.barangay_id),cash=actors.filter((a:any)=>a.role==='disbursing');
 const disaster=(await get('/disasters'))[0],category=(await get('/categories')).find((c:any)=>c.name==='Totally damaged');
 let household=(await get('/registry',recipient.id)).households[0];
 if(!household){const ack=await post('/registry',recipient.id,{beneficiary_actor_id:recipient.id,declared_barangay_id:punong.barangay_id,address:'Invented lookup lane 73',zone:'8',members:[{name:'Invented Lookup Sinta '+Date.now(),birth_date:null,relationship:'head',is_head:true}]});household=await get('/registry/'+ack.resources[0].id,recipient.id);}
 const submitted=await post('/claims',recipient.id,{household_id:household.id,disaster_id:disaster.id,stated_category_id:category.id,damage_description:'Invented lookup-session synthetic damage',evidence_ids:[await original('damage',recipient.id)]});
 let claim=await get('/claims/'+submitted.resources[0].id,dswd.id),round=claim.rounds.at(-1);
 for(const officer of officers.slice(0,2))await post('/claim-rounds/'+round.id+'/responses',officer.id,{kind:'endorse',residence_attested:true,affected_attested:true});
 await post('/claims/submissions',punong.id,{disaster_id:disaster.id,barangay_id:punong.barangay_id,round_ids:[round.id],resolution_evidence_id:await original('council_resolution',punong.id)});
 claim=await get('/claims/'+claim.id,dswd.id);
 await post('/claims/'+claim.id+'/decisions',dswd.id,{expected_revision:claim.revision,reviewed_check_id:claim.latest_check.id,action:'approve',category_id:category.id,reason:'Synthetic test operator inspected current flags and endorsements for the unpaid lookup fixture'});
 const publication=await post('/lists',dswd.id,{disaster_id:disaster.id,barangay_id:punong.barangay_id});
 let list:any;await expect.poll(async()=>{list=(await get('/lists?disaster_id='+disaster.id,dswd.id)).find((l:any)=>l.id===publication.resources[0].id);return list?.business_status;},{timeout:40000}).toBe('published');
 const entry=list.entries.find((e:any)=>e.name===household.members.find((m:any)=>m.is_head).name),clock=await get('/evaluation/status',dswd.id);
 await post('/sessions',dswd.id,{disaster_id:disaster.id,barangay_id:punong.barangay_id,list_version_id:list.id,list_entry_ids:[entry.id],date:new Date(new Date(clock.business_utc).getTime()+8*3600*1000).toISOString().slice(0,10),site:'Invented unpaid lookup test hall',cash_actor_ids:cash.slice(0,2).map((a:any)=>a.id)});
}
