'use client';
import {useEffect,useState} from 'react';
import {Sun,Moon,Monitor} from 'lucide-react';
import {useLanguage} from './Language';

type Theme='light'|'dark'|'system';
const KEY='ayudachain:theme';
const options:{value:Theme;label:string;Icon:typeof Sun}[]=[{value:'light',label:'Light theme',Icon:Sun},{value:'dark',label:'Dark theme',Icon:Moon},{value:'system',label:'Use device theme',Icon:Monitor}];

/* Light, Dark or System. The choice is a per-browser convenience; "system" removes data-theme so prefers-color-scheme decides. */
function applyTheme(theme:Theme){const root=document.documentElement;if(theme==='system')root.removeAttribute('data-theme');else root.setAttribute('data-theme',theme);}

export default function ThemeToggle(){
  const {t}=useLanguage();
  const [theme,setTheme]=useState<Theme>('system');
  useEffect(()=>{let saved:Theme='system';try{const v=localStorage.getItem(KEY);if(v==='light'||v==='dark')saved=v;}catch{}setTheme(saved);},[]);
  const choose=(next:Theme)=>{setTheme(next);applyTheme(next);try{if(next==='system')localStorage.removeItem(KEY);else localStorage.setItem(KEY,next);}catch{}};
  return <div className="ac-theme-toggle" role="group" aria-label={t('Colour theme','Kulay ng tema')}>
    {options.map(({value,label,Icon})=><button key={value} type="button" aria-label={t(label,({light:'Maliwanag na tema',dark:'Madilim na tema',system:'Tema ng device'})[value])} title={t(label,({light:'Maliwanag na tema',dark:'Madilim na tema',system:'Tema ng device'})[value])} aria-pressed={theme===value} onClick={()=>choose(value)}><Icon size={18} aria-hidden="true"/></button>)}
  </div>;
}
