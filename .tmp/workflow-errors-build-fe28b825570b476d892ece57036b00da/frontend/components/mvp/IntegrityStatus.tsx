"use client";
import {useErrorMessage} from './Language';
import {RefObject,useRef,useState} from 'react';
import {request} from '@/lib/mvp-client';
import {Status,manila} from './UI';

type IntegrityResult={result:string;checked_at?:string;last_confirmed_observation?:{checked_at:string;observed_tx_hash:string|null};[field:string]:unknown};
type Check={status:'checking'|'complete'|'failed';value?:IntegrityResult;checkedAt?:string;lastMatchAt?:string};
const explanations:Record<string,string>={match:'Committed content matches the chain record.',mismatch:'Committed content does not match.',required_anchor_absent:'Required anchor not found.',chain_unreachable:'Chain could not be read; not verified.',evidence_unavailable:'Required evidence unavailable; not verified.'};

export function useIntegrityChecks(actor:string,control:RefObject<AbortController|null>,onError:(error:string)=>void){
  const explainError=useErrorMessage();
  const [checks,setChecks]=useState<Record<string,Check>>({});
  const pending=useRef(new Set<string>());
  async function check(id:string,path='/integrity/check',readOnly=false){
    if(pending.current.has(id))return;
    const signal=control.current?.signal;
    pending.current.add(id);onError('');
    setChecks(previous=>({...previous,[id]:{status:'checking',lastMatchAt:previous[id]?.lastMatchAt}}));
    try{
      const value=await request<IntegrityResult>(path,actor,signal,readOnly?undefined:{commitment_id:id});
      if(signal?.aborted)return;
      const checkedAt=value.checked_at||new Date().toISOString();
      setChecks(previous=>({...previous,[id]:{status:'complete',value,checkedAt,lastMatchAt:value.result==='match'?checkedAt:previous[id]?.lastMatchAt||value.last_confirmed_observation?.checked_at}}));
    }catch(error){
      if(signal?.aborted||error instanceof Error&&error.name==='AbortError')return;
      setChecks(previous=>({...previous,[id]:{status:'failed',lastMatchAt:previous[id]?.lastMatchAt}}));
      onError(explainError(error));
    }finally{pending.current.delete(id);}
  }
  return {checks,check};
}

export default function IntegrityStatus({check,details=false}:{check?:Check;details?:boolean}){
  const current=check?.status==='complete'?check.value?.result:check?.status==='checking'?'checking…':check?.status==='failed'?'unavailable · refresh failed':'not checked';
  return <div role={check?'status':undefined} aria-live={check?'polite':undefined} aria-atomic="true">
    <div className="ac-integrity-result"><Status value={String(current)}/>{check?.status==='complete'&&check.checkedAt&&<span>Checked {manila(check.checkedAt)} Manila</span>}</div>
    {check?.status==='complete'&&check.value&&<p>{explanations[check.value.result]}</p>}
    {check?.lastMatchAt&&check.value?.result!=='match'&&<p className="mvp-note">Last match: {manila(check.lastMatchAt)} Manila. This earlier check does not establish the current result.</p>}
    {check?.status==='complete'&&check.value&&<><dl className="ac-data-fields"><div><dt>Recorded evidence</dt><dd>Saved canonical version and listed original bytes</dd></div><div><dt>Chain commitment</dt><dd>{check.value.result==='match'?'Matches recorded evidence':check.value.result==='mismatch'?'Different committed content':check.value.result==='required_anchor_absent'?'No commitment found at the pinned deployment':'Unavailable for comparison'}</dd></div>{check.value.kind!==undefined&&<div><dt>Evidence kind</dt><dd>{String(check.value.kind).replaceAll('_',' ')}</dd></div>}{check.value.block_number!==undefined&&<div><dt>Observed block</dt><dd>{String(check.value.block_number)}</dd></div>}{check.value.contract_address!==undefined&&<div><dt>Pinned chain reference</dt><dd>Chain {String(check.value.chain_id)} · {String(check.value.contract_address)}</dd></div>}</dl><details><summary>Raw hashes and observed check details</summary><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{JSON.stringify(check.value,null,2)}</pre></details></>}
  </div>;
}
