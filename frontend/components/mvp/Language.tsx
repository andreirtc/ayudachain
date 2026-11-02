"use client";
import {createContext,useContext,useEffect,useState,ReactNode,startTransition} from 'react';
import {errorMessage} from '@/lib/workflow-errors';
import {filipinoInterface} from '@/lib/interface-copy';

export type Language='en'|'fil';
const preferenceKey='ayudachain.guidance-language';
const LanguageContext=createContext({language:'en' as Language,setLanguage:(_language:Language)=>{},t:(english:string,_filipino:string)=>english});

export function LanguageProvider({children}:{children:ReactNode}){
  const [language,setLanguage]=useState<Language>('fil');
  useEffect(()=>{const query=new URL(window.location.href).searchParams.get('lang');let saved:Language='fil';try{const cached=localStorage.getItem(preferenceKey);if(cached==='en'||cached==='fil')saved=cached;}catch{}const selected=query==='fil'||query==='en'?query:saved;startTransition(()=>setLanguage(selected));if(query==='fil'||query==='en')try{localStorage.setItem(preferenceKey,selected);}catch{}},[]);
  function choose(value:Language){setLanguage(value);const url=new URL(window.location.href);url.searchParams.set('lang',value);window.history.replaceState(null,'',url.pathname+url.search+url.hash);try{localStorage.setItem(preferenceKey,value);}catch{/* This visit still uses the selected language. */}}
  return <LanguageContext.Provider value={{language,setLanguage:choose,t:(en,fil)=>language==='fil'&&fil?fil:en}}>{children}</LanguageContext.Provider>;
}
export const useLanguage=()=>useContext(LanguageContext);
export function useErrorMessage(role?:string){
  const {language}=useLanguage();
  return (error:unknown)=>errorMessage(error,role,language);
}
export function LanguageSelector(){
  const {language,setLanguage}=useLanguage();
  return <label lang={language}>Language / Wika<select aria-label="Guidance language / Wika ng gabay" value={language} onChange={e=>setLanguage(e.target.value as Language)}><option value="en" lang="en">English</option><option value="fil" lang="fil">Taglish</option></select></label>;
}

const normalizedCopy=new Map(Object.entries(filipinoInterface).map(([key,value])=>[key.toLocaleLowerCase(),value]));
export function useInterfaceText(){const {language}=useLanguage();return (value:string|number|undefined)=>{const english=value===undefined?'':String(value);return language==='fil'?(filipinoInterface[english]||normalizedCopy.get(english.toLocaleLowerCase())||english):english;};}
