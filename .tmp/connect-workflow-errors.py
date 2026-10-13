"""Apply the same role/language error presenter at existing MVP catch sites."""
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]/'frontend/components/mvp'
names=['Audit','Claims','CsvIntake','Dashboard','DuplicateComparison','EvaluationClock','EvidenceContext','EvidenceUpload','Funds','IntegrityStatus','Lists','Operations','Outcomes','Payouts','Queue','Registry','SessionLookup','Sessions','Workspace']
for name in names:
    path=root/(name+'.tsx')
    source=path.read_bytes().decode('utf-8')
    newline='\r\n' if '\r\n' in source else '\n'
    existing=re.search(r"import \{([^}]+)\} from './Language';",source)
    if existing:
        source=source[:existing.start()]+existing.group(0).replace(existing.group(1),existing.group(1)+',useErrorMessage')+source[existing.end():]
    else:
        index=source.index(newline)+len(newline)
        source=source[:index]+"import {useErrorMessage} from './Language';"+newline+source[index:]
    function='useIntegrityChecks' if name=='IntegrityStatus' else 'WorkspaceBody' if name=='Workspace' else name
    pattern=rf'((?:export (?:default )?)?function {function}\([^\n]+\{{)\r?\n'
    argument='' if name in {'IntegrityStatus','EvidenceUpload'} else 'config?.role' if name=='Workspace' else 'actor.role'
    insertion='  const explainError=useErrorMessage('+argument+');'+newline
    if name=='Workspace':
        needle='  const config=workspaces[slug],search=useSearchParams();'+newline
        assert source.count(needle)==1,name
        source=source.replace(needle,needle+insertion)
    else:
        source,count=re.subn(pattern,lambda m:m.group(1)+newline+insertion,source,count=1)
        assert count==1,name
    if name=='SessionLookup':
        lines=source.splitlines(keepends=True)
        lines=[re.sub(r'setError\(.*\);','setError(explainError(e));',line) if "e.message==='record_unavailable'" in line else line for line in lines]
        source=''.join(lines)
    if name!='CsvIntake':
        source=re.sub(r'setError\(`\$\{e\.message\}[^`]*`\)', 'setError(explainError(e))',source)
    else:
        source=source.replace('${e.message}', '${explainError(e)}')
    source=source.replace('setError(e.message)','setError(explainError(e))')
    source=source.replace('setError((e as Error).message)','setError(explainError(e))')
    source=source.replace('setStatus(error.message)','setStatus(explainError(error))')
    source=source.replace("error instanceof Error?error.message:'Verification refresh failed'",'explainError(error)')
    if name=='Audit':
        source=re.sub(r"setLoadError\('We couldn[^']*read the evidence records\.[^']*'\)",'setLoadError(explainError(e))',source)
    if name=='Workspace':
        source=re.sub(r"setError\('We couldn[^']*load your workspace\.[^']*'\)",'setError(explainError(e))',source)
    if name=='Dashboard':
        needle="if(results.some(r=>r.status==='rejected'))setError('Some records could not be loaded. Refresh to see the latest saved information.');"
        assert needle in source
        source=source.replace(needle,"const failed=results.find(r=>r.status==='rejected');if(failed?.status==='rejected')setError(explainError(failed.reason));")
    if name=='Registry':
        source=re.sub(r"\{error\} \{t\('Could not confirm this action\.[^}]+\}\}",'{error}}',source)
    path.write_bytes(source.encode('utf-8'))
print('Connected the existing error presenter in',len(names),'MVP components/hooks.')
