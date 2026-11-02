import {getApiBase} from "./api";
import {WorkflowError} from './workflow-errors';
export type Ref={id:string;name:string};
export type Actor={id:string;role:string;display_name:string;status:string;position:string|null;barangay_id:string|null};
export type Ack={resources:{type:string;id:string}[];replayed:boolean;code?:string};
export type Envelope<T>={data:T;meta:{identity_assurance:string;authentication:string}};
export async function request<T>(path:string,actor:string|null,signal?:AbortSignal,body?:object|FormData,key?:string):Promise<T>{
  const headers:Record<string,string>={};
  if(actor)headers["X-Demo-Actor-ID"]=actor;
  if(key)headers["Idempotency-Key"]=key;
  if(body && !(body instanceof FormData))headers["Content-Type"]="application/json";
  const readOnly=path==='/integrity/check'||path==='/registry/csv/preview'||path==='/queues/search'||/^\/sessions\/[^/]+\/lookup$/.test(path);
  const mutation=!!body&&!readOnly;let response:Response;
  try{response=await fetch(`${getApiBase()}/api/v1${path}`,{method:body?"POST":"GET",headers,body:body instanceof FormData?body:body?JSON.stringify(body):undefined,signal,cache:"no-store"});}
  catch(error){if(error instanceof Error&&error.name==='AbortError')throw error;throw new WorkflowError('network_unavailable',0,path,mutation);}
  if(!response.ok)await rejectResponse(response,path,mutation);
  let result:Record<string,unknown>;
  try{result=await response.json();if(!result||typeof result!=='object')throw new Error('Invalid envelope');}
  catch(error){if(error instanceof Error&&error.name==='AbortError')throw error;throw new WorkflowError('invalid_response',response.status,path,mutation);}
  if(!Object.prototype.hasOwnProperty.call(result,'data'))throw new WorkflowError('invalid_response',response.status,path,mutation);
  return (result as Envelope<T>).data;
}
export async function rejectResponse(response:Response,path:string,mutation=false):Promise<never>{
  let result:{error?:unknown}|null;
  try{result=await response.json();}
  catch(error){if(error instanceof Error&&error.name==='AbortError')throw error;throw new WorkflowError('invalid_response',response.status,path,mutation);}
  throw new WorkflowError(typeof result?.error==='string'?result.error:'request_failed',response.status,path,mutation);
}
export const pesos=(v:string)=>{const n=BigInt(v),absolute=n<0?-n:n;return `${n<0?'−':''}₱${(absolute/BigInt(100)).toLocaleString('en-PH')}.${(absolute%BigInt(100)).toString().padStart(2,'0')}`;};
export const pesoInput=(v:string)=>{const n=BigInt(v),absolute=n<0?-n:n;return `${n<0?'-':''}${absolute/BigInt(100)}.${(absolute%BigInt(100)).toString().padStart(2,'0')}`;};
export function centavos(v:string){
  if(!/^[0-9]+(?:\.[0-9]{1,2})?$/.test(v))throw new Error("Enter a peso amount with at most two decimal places.");
  const [whole,fraction=""]=v.split(".");return (BigInt(whole)*BigInt(100)+BigInt(fraction.padEnd(2,"0"))).toString();
}
