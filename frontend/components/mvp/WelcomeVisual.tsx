import {LogoMark} from './Logo';

/* Brand illustration only: no fabricated amounts, transactions or verification results. */
export default function WelcomeVisual(){
 return <svg className="ac-welcome-visual" viewBox="0 0 440 320" fill="none" aria-hidden="true" focusable="false">
  <ellipse cx="239" cy="162" rx="158" ry="137" fill="var(--md-primary-container)"/>
  <circle cx="360" cy="54" r="28" fill="var(--md-tertiary-container)"/>
  <path d="M61 158H132M285 158H366M214 240V278H115" stroke="var(--md-primary)" strokeWidth="2" strokeDasharray="5 6"/>
  <circle cx="130" cy="158" r="4" fill="var(--md-primary)"/><circle cx="286" cy="158" r="4" fill="var(--md-primary)"/>
  <g transform="translate(144 55)"><LogoMark size={164}/></g>
  <path d="M23 145L65 111L107 145M33 140V190H97V140" stroke="var(--md-primary)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
  <path d="M57 190V161H75V190" fill="var(--md-tertiary-container)" stroke="var(--md-primary)" strokeWidth="3"/>
  <path d="M345 111H395L415 131V196H345V111Z" fill="var(--md-surface-container-lowest)" stroke="var(--md-primary)" strokeWidth="3" strokeLinejoin="round"/>
  <path d="M395 111V131H415M359 146H399M359 157H392M359 168H383" stroke="var(--md-primary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
  <path d="M87 294V284C87 271 98 261 111 261C124 261 135 271 135 284V294M150 294V286C150 276 143 268 135 265" stroke="var(--md-primary)" strokeWidth="3" strokeLinecap="round"/>
  <circle cx="111" cy="244" r="12" fill="var(--md-tertiary-container)" stroke="var(--md-primary)" strokeWidth="3"/>
  <path d="M131 235A10 10 0 0 1 131 254" stroke="var(--md-primary)" strokeWidth="3" strokeLinecap="round"/>
  <path d="M314 261H375M326 275H385M314 289H363" stroke="var(--md-primary)" strokeWidth="3" strokeLinecap="round" opacity=".45"/>
 </svg>;
}
