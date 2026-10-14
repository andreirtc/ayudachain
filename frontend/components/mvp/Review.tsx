'use client';
import {useEffect,useId,useRef,useState} from 'react';
import Link from 'next/link';
import {useLanguage} from './Language';

export type Review={title:string;record:string;choice:string;effect:string};
export function ReviewDialog({review,onConfirm,onCancel,busy=false,confirmLabel}:{review:Review|null;onConfirm:()=>void;onCancel:()=>void;busy?:boolean;confirmLabel?:string}){
  const {t}=useLanguage(),dialog=useRef<HTMLDialogElement>(null),trigger=useRef<HTMLElement|null>(null),title=useId();
  useEffect(()=>{
    if(review){trigger.current=document.activeElement as HTMLElement;dialog.current?.showModal();}
    else if(dialog.current?.open){dialog.current.close();trigger.current?.focus();}
  },[!!review]);
  useEffect(()=>()=>{trigger.current?.focus();},[]);
  return <dialog ref={dialog} className="ac-review-dialog" aria-labelledby={title} onCancel={e=>{e.preventDefault();if(!busy)onCancel();}} onClose={()=>{trigger.current?.focus();}} onKeyDown={e=>{
    if(e.key!=='Tab')return;
    const items=Array.from(dialog.current?.querySelectorAll<HTMLElement>('button:not(:disabled),a[href],input:not(:disabled)')||[]),first=items[0],last=items.at(-1);
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
  }}>{review&&<><h2 id={title}>{review.title}</h2><dl className="ac-data-fields"><div><dt>{t('Selected record','Napiling tala')}</dt><dd>{review.record}</dd></div><div><dt>{t('Your choice','Iyong pinili')}</dt><dd>{review.choice}</dd></div></dl><p>{review.effect}</p><p className="mvp-note">{t('The saved event remains in history. Where permitted, corrections are new events. Cancelling this review sends no command.','Mananatili sa kasaysayan ang naitalang pangyayari. Kung pinahihintulutan, bagong tala ang pagwawasto. Walang ipapadalang utos kapag kinansela ang pagsusuring ito.')}</p><div className="mvp-actions"><button autoFocus type="button" disabled={busy} onClick={onCancel}>{t('Cancel','Kanselahin')}</button><button className="primary" type="button" disabled={busy} onClick={onConfirm}>{confirmLabel||t('Confirm','Ituloy')}</button></div></>}</dialog>;
}

// Native radios supply arrow-key selection and form/assistive semantics.
export function Segmented({label,name,value,onChange,options,disabled=false}:{label:string;name:string;value:string;onChange:(value:string)=>void;options:{value:string;label:string;danger?:boolean}[];disabled?:boolean}){
  return <fieldset className="ac-segmented" disabled={disabled}><legend>{label}</legend><div>{options.map(option=><label key={option.value} className={option.danger?'is-danger':undefined}><input type="radio" aria-label={option.label} name={name} value={option.value} checked={value===option.value} onChange={()=>onChange(option.value)}/><span>{option.label}</span></label>)}</div></fieldset>;
}
export function SavedResult({message,href,action}:{message:string;href?:string;action?:string}){
  const {t}=useLanguage(),[visible,setVisible]=useState(false);
  useEffect(()=>{if(!message){setVisible(false);return;}setVisible(true);const timeout=setTimeout(()=>setVisible(false),5000);return()=>clearTimeout(timeout);},[message]);
  if(!message)return null;
  return <><div className="mvp-success ac-saved-result"><p>{message}</p>{href&&<Link href={href}>{action||t('View saved record','Tingnan ang naitalang resulta')}</Link>}</div>{visible&&<aside className="ac-snackbar" role="status" aria-live="polite"><span>{message}</span>{href&&<Link href={href}>{action||t('View','Tingnan')}</Link>}<button type="button" onClick={()=>setVisible(false)}>{t('Dismiss','Isara')}</button></aside>}</>;
}
