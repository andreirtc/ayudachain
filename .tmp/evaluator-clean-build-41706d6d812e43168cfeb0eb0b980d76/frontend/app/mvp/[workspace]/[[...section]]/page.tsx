import {notFound} from 'next/navigation';
import Workspace from '@/components/mvp/Workspace';
import {workspaces} from '@/components/mvp/workspaces';
export default async function Page({params}:{params:Promise<{workspace:string;section?:string[]}>}){
  const {workspace,section}=await params;
  if(!workspaces[workspace])notFound();
  return <Workspace slug={workspace} section={section?.join('/')||'overview'}/>;
}
