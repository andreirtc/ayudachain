'use client';
import {useInterfaceText} from "./Language";

import {useEffect,useRef} from 'react';
import {Settings2} from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import {LanguageSelector} from './Language';

export default function DisplayPreferences({context,includeLanguage=true}:{context:string;includeLanguage?:boolean}){
  const ui=useInterfaceText();

  const panel=useRef<HTMLDetailsElement>(null);
  useEffect(()=>{if(panel.current)panel.current.open=false;},[context]);
  useEffect(()=>{
    const outside=(event:Event)=>{if(event.target instanceof Node&&!panel.current?.contains(event.target)&&panel.current)panel.current.open=false;};
    const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'&&panel.current?.open){panel.current.open=false;panel.current.querySelector('summary')?.focus();}};
    document.addEventListener('pointerdown',outside);document.addEventListener('focusin',outside);document.addEventListener('keydown',escape);
    return()=>{document.removeEventListener('pointerdown',outside);document.removeEventListener('focusin',outside);document.removeEventListener('keydown',escape);};
  },[]);
  return <details ref={panel} className="ac-display-preferences"><summary aria-label={ui("Display preferences")} title={ui("Display preferences")}><Settings2 size={20}/></summary><div className="ac-display-panel"><strong>{ui("Display preferences")}</strong><p>{ui("Appearance")}</p><ThemeToggle/>{includeLanguage&&<LanguageSelector/>}</div></details>;
}
