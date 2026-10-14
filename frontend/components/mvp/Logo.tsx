/* AyudaChain mark: a shield and check (verified) around a house (the household) held by a chain (the anchored record). Drawn in /logo.svg. */
export function LogoMark({size=32}:{size?:number}){
  return <img src="/logo.svg" width={size} height={Math.round(size*105/94)} alt="" aria-hidden="true"/>;
}
