import {test,expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
// User-facing copy must not use these words. The X-Demo-Actor-ID request header and the legacy /api/demo/ route are
// API contract names, not copy,
// and CSS `position: static` is not text, so neither is flagged.
const banned=/(?<!X-)\b(invented|demonstration|demo|static|synthetic|kathang-isip)\b/i;
function files(dir:string):string[]{return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?(e.name==='node_modules'||e.name==='.next'?[]:files(p)):/\.(tsx|ts)$/.test(e.name)&&!/generated/.test(e.name)?[p]:[];});}
test('app copy never uses the words invented, static, demo, demonstration or synthetic',()=>{
  const root=path.resolve(__dirname,'..');
  const hits:string[]=[];
  for(const dir of ['app','components','lib'])for(const file of files(path.join(root,dir)))fs.readFileSync(file,'utf8').split('\n').forEach((line,i)=>{
    // The legacy backend route path is an endpoint, not copy.
    const code=line.replace(/\/api\/demo\//g,'/api/legacy-reset/').replace(/\/\/.*$/,'').replace(/\/\*.*?\*\//g,'');
    const match=code.match(banned);if(match)hits.push(`${path.relative(root,file)}:${i+1}: ${match[0]}`);
  });
  expect(hits,'banned words in app source').toEqual([]);
});
