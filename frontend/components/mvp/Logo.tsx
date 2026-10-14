/* Vector recreation of the maintainer's shield/link mark. Decorative beside the wordmark. */
export function LogoMark({size=32}:{size?:number}){
  return <svg className="ac-logo-mark" width={size} height={size} viewBox="0 0 128 128" fill="none" aria-hidden="true" focusable="false">
    <path d="M20 62C17 51 16 39 18 27C35 25 51 18 64 10C78 18 93 24 110 27L110 44L65 88L52 75M108 61C100 88 85 107 64 119C54 113 45 106 38 98" stroke="var(--ayuda-logo-blue, #477ff5)" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M52 53L63 42C68 37 74 37 79 42L85 48C90 53 90 59 85 64L76 73M48 72L39 81M54 84L45 93C40 98 34 98 29 93L24 88C19 83 19 77 24 72L35 61C40 56 46 56 51 61L58 68" stroke="var(--ayuda-logo-green, #218859)" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M59 62L64 57L71 64L71 70" stroke="var(--ayuda-logo-blue, #477ff5)" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>;
}
