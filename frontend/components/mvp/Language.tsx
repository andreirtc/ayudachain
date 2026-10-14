"use client";
import {createContext,useContext,useEffect,useState,ReactNode} from 'react';
import {errorMessage} from '@/lib/workflow-errors';

export type Language='en'|'fil';
const preferenceKey='ayudachain.guidance-language';
const LanguageContext=createContext({language:'en' as Language,setLanguage:(_language:Language)=>{},t:(english:string,_filipino:string)=>english});

export function LanguageProvider({children,defaultLanguage='en'}:{children:ReactNode;defaultLanguage?:Language}){
  const [language,setLanguage]=useState<Language>(defaultLanguage);
  function choose(value:Language){setLanguage(value);try{localStorage.setItem(preferenceKey,value);}catch{/* This visit still uses the selected language. */}}
  return <LanguageContext.Provider value={{language,setLanguage:choose,t:(en,fil)=>language==='fil'&&fil?fil:en}}>{children}</LanguageContext.Provider>;
}
export const useLanguage=()=>useContext(LanguageContext);
// Render this inside the same Suspense boundary as the localized content. Its effect then runs only after that
// content has hydrated in the server's default language, so a saved choice never causes a hydration mismatch.
export function SavedLanguage(){
  const {setLanguage}=useLanguage();
  useEffect(()=>{try{const saved=localStorage.getItem(preferenceKey);if(saved==='fil'||saved==='en')setLanguage(saved);}catch{/* The default remains available when storage is blocked. */}},[]);
  return null;
}
export function useErrorMessage(role?:string){
  const {language}=useLanguage();
  return (error:unknown)=>errorMessage(error,role,language);
}
export function LanguageSelector(){
  const {language,setLanguage}=useLanguage();
  return <label lang={language}>Guidance language / Wika ng gabay<select aria-label="Guidance language / Wika ng gabay" value={language} onChange={e=>setLanguage(e.target.value as Language)}><option value="en" lang="en">English</option><option value="fil" lang="fil">Filipino</option></select></label>;
}
