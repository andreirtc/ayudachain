'use client';
import {useInterfaceText} from "./Language";

import {ReactNode,useEffect,useRef,useState} from 'react';
import {ArrowLeft,ChevronRight,Search} from 'lucide-react';
import {Status} from './UI';

type Record={id:string;display_id:string;zone:string;residence_state:string;members:{name:string;is_head:boolean}[]};
export default function HouseholdBrowser<T extends Record>({records,requested,renderDetail,onSelect,children}:{records:T[];requested:string|null;renderDetail:(record:T)=>ReactNode;onSelect:()=>void;children:ReactNode}){
  const ui=useInterfaceText();

  const [query,setQuery]=useState(''),[selected,setSelected]=useState(requested||'');
  const heading=useRef<HTMLHeadingElement>(null),previous=useRef('');
  const current=records.find(r=>r.id===selected)||records[0];
  useEffect(()=>{setSelected(requested||'');},[requested]);
  const visible=records.filter(r=>(r.display_id+' '+r.zone+' '+r.members.map(m=>m.name).join(' ')).toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
  function choose(id:string){setSelected(id);previous.current=id;onSelect();requestAnimationFrame(()=>heading.current?.focus());}
  function back(){setSelected('');onSelect();requestAnimationFrame(()=>document.getElementById('select-household-'+previous.current)?.focus());}
  return <div className="ac-registry-workspace" data-detail-open={!!selected}>
    <section className="mvp-panel ac-household-list" aria-label={ui("Household selection")}><h2>{ui("Household records")}</h2><label>{ui("Search households")}<div className="ac-search-field"><Search size={18} aria-hidden="true"/><input type="search" placeholder={ui("Name, reference or zone")} value={query} onChange={e=>setQuery(e.target.value)}/></div></label><div className="ac-section-heading"><p role="status">{visible.length}{' '}{ui("of")}{' '}{records.length}{' '}{ui("households")}</p>{query&&<button onClick={()=>setQuery('')}>{ui("Clear household search")}</button>}</div>
      <div className="ac-household-rows">{visible.map(h=><button id={'select-household-'+h.id} key={h.id} className="ac-household-row" aria-label={ui('Open household')+' '+h.display_id+' · '+h.members.find(m=>m.is_head)?.name} aria-current={current?.id===h.id?'true':undefined} onClick={()=>choose(h.id)}><span><strong>{h.members.find(m=>m.is_head)?.name||'Household'}</strong><small>{h.display_id}{' '}{ui("· Zone")}{' '}{h.zone}</small><Status value={h.residence_state}/></span><ChevronRight size={18}/></button>)}</div>
      {!visible.length&&<p>{records.length?ui("No households match this search. Clear the search to see your permitted records."):ui("No household in your current scope.")}</p>}
    </section>
    <section className="mvp-panel ac-household-detail" aria-label={ui("Selected household")}><div className="ac-section-heading"><h2 ref={heading} tabIndex={-1}>{ui("Household details")}</h2><button onClick={back} className="ac-back-to-households"><ArrowLeft size={16}/>{ui("Back to households")}</button></div>{current?<>{renderDetail(current)}{children}</>:<p>{ui("Select a household to inspect its recorded details.")}</p>}</section>
  </div>;
}
