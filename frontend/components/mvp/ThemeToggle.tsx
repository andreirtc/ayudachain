'use client';
import {useInterfaceText} from "./Language";

import {useEffect,useState} from 'react';
import {Sun,Moon,Monitor} from 'lucide-react';

type Theme='light'|'dark'|'system';
const KEY='ayudachain:theme';
const options:{value:Theme;label:string;Icon:typeof Sun}[]=[{value:'light',label:'Light theme',Icon:Sun},{value:'dark',label:'Dark theme',Icon:Moon},{value:'system',label:'Use device theme',Icon:Monitor}];

/* Light, Dark or System. The choice is a per-browser convenience; "system" removes data-theme so prefers-color-scheme decides. */
function applyTheme(theme:Theme){const root=document.documentElement;if(theme==='system')root.removeAttribute('data-theme');else root.setAttribute('data-theme',theme);}

export default function ThemeToggle(){
  const ui=useInterfaceText();

  const [theme,setTheme]=useState<Theme>('system');
  useEffect(()=>{let saved:Theme='system';try{const v=localStorage.getItem(KEY);if(v==='light'||v==='dark')saved=v;}catch{}setTheme(saved);},[]);
  const choose=(next:Theme)=>{setTheme(next);applyTheme(next);try{if(next==='system')localStorage.removeItem(KEY);else localStorage.setItem(KEY,next);}catch{}};
  return <div className="ac-theme-toggle" role="group" aria-label={ui("Colour theme")}>
    {options.map(({value,label,Icon})=><button key={value} type="button" aria-label={ui(label)} title={ui(label)} aria-pressed={theme===value} onClick={()=>choose(value)}><Icon size={18} aria-hidden="true"/></button>)}
  </div>;
}
