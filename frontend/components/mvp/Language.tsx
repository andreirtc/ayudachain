"use client";
import {createContext,useContext,useEffect,useState,ReactNode} from 'react';

export type Language='en'|'fil';
const preferenceKey='ayudachain.guidance-language';
const LanguageContext=createContext({language:'en' as Language,setLanguage:(_language:Language)=>{},t:(english:string,_filipino:string)=>english});

export function LanguageProvider({children}:{children:ReactNode}){
  const [language,setLanguage]=useState<Language>('en');
  useEffect(()=>{try{if(localStorage.getItem(preferenceKey)==='fil')setLanguage('fil');}catch{/* English remains available when storage is blocked. */}},[]);
  function choose(value:Language){setLanguage(value);try{localStorage.setItem(preferenceKey,value);}catch{/* This visit still uses the selected language. */}}
  return <LanguageContext.Provider value={{language,setLanguage:choose,t:(en,fil)=>language==='fil'&&fil?fil:en}}>{children}</LanguageContext.Provider>;
}
export const useLanguage=()=>useContext(LanguageContext);
export function LanguageSelector(){
  const {language,setLanguage}=useLanguage();
  return <label lang={language}>Guidance language / Wika ng gabay<select aria-label="Guidance language / Wika ng gabay" value={language} onChange={e=>setLanguage(e.target.value as Language)}><option value="en" lang="en">English</option><option value="fil" lang="fil">Filipino</option></select></label>;
}
