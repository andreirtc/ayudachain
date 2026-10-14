"use client";
import {useErrorMessage,useLanguage} from './Language';
import {RefObject,useRef,useState} from 'react';
import {request} from '@/lib/mvp-client';
import {Status,manila} from './UI';
import {currentIntegrity} from './Storytelling';

type IntegrityResult={result:string;checked_at?:string;last_confirmed_observation?:{checked_at:string;observed_tx_hash:string|null};[field:string]:unknown};
type Check={status:'checking'|'complete'|'failed';value?:IntegrityResult;checkedAt?:string;lastMatchAt?:string};
const filipinoExplanations:Record<string,string>={not_checked:'Wala pang kasalukuyang pagsusuri sa chain.',checking:'Binabasa ang kasalukuyang tala sa chain; hindi pa beripikado.',match:'Tumutugma ang nakatalang nilalaman sa tala sa chain.',mismatch:'Hindi tumutugma ang nakatalang nilalaman.',required_anchor_absent:'Hindi natagpuan ang kinakailangang anchor.',chain_unreachable:'Hindi mabasa ang chain; hindi beripikado.',evidence_unavailable:'Hindi makuha ang kinakailangang katibayan; hindi beripikado.',refresh_failed:'Nabigo ang kasalukuyang refresh; hindi beripikado. Basahin itong muli.'};

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
  const {t}=useLanguage(),current=currentIntegrity(check);
  const label=current.state==='not_checked'?'not checked':current.state==='checking'?'checking…':current.state==='refresh_failed'?'refresh failed':current.state;
  return <div className="ac-proof-status" role={check?'status':undefined} aria-live={check?'polite':undefined} aria-atomic="true">
    <div className="ac-integrity-result"><Status value={label}/>{current.checkedAt&&<span>{' '}{t('Checked','Sinuri')} {manila(current.checkedAt)} Manila</span>}</div>
    <p>{t(current.explanation,filipinoExplanations[current.state])}</p>
    {current.earlierMatchAt&&<p className="mvp-note">{t('Last match:','Huling pagtugma:')} {manila(current.earlierMatchAt)} Manila. {t('This earlier check does not establish the current result.','Hindi pinatutunayan ng naunang pagsusuring ito ang kasalukuyang resulta.')}</p>}
    {check?.status==='complete'&&check.value&&<details open={details}><summary>{t('Current check details','Mga detalye ng kasalukuyang pagsusuri')}</summary><dl className="ac-data-fields"><div><dt>{t('Recorded evidence','Naitalang katibayan')}</dt><dd>{t('Saved canonical version and listed original bytes','Naitalang canonical na bersiyon at nakalistang orihinal na bytes')}</dd></div><div><dt>{t('Chain commitment','Commitment sa chain')}</dt><dd>{current.verified?t('Matches recorded evidence','Tumutugma sa naitalang katibayan'):current.state==='mismatch'?t('Different committed content','Iba ang nakatalang nilalaman'):current.state==='required_anchor_absent'?t('No commitment found at the pinned deployment','Walang commitment sa nakatakdang deployment'):t('Unavailable for comparison','Hindi makuha para sa paghahambing')}</dd></div>{check.value.kind!==undefined&&<div><dt>{t('Evidence kind','Uri ng katibayan')}</dt><dd>{String(check.value.kind).replaceAll('_',' ')}</dd></div>}{check.value.block_number!==undefined&&<div><dt>{t('Observed block','Nabasang block')}</dt><dd>{String(check.value.block_number)}</dd></div>}{check.value.contract_address!==undefined&&<div><dt>{t('Pinned chain reference','Nakatakdang chain reference')}</dt><dd>Chain {String(check.value.chain_id)} · {String(check.value.contract_address)}</dd></div>}</dl><details><summary>{t('Raw hashes and observed check details','Mga hash at detalye ng nabasang pagsusuri')}</summary><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{JSON.stringify(check.value,null,2)}</pre></details></details>}
  </div>;
}
