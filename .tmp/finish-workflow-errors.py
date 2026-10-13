from pathlib import Path

root=Path(__file__).resolve().parents[1]/'frontend/components/mvp'
replacements={
 'DuplicateComparison':[("setError(e instanceof Error?e.message:'Identity inspection unavailable')",'setError(explainError(e))')],
 'Registry':[("{error} {t('Could not confirm this action. Read the current record before retrying.','Hindi kumpirmado ang ginawa. Basahin muna ang kasalukuyang tala bago subukang muli.')}",'{error}')],
 'Payouts':[("if(!r.ok)throw new Error(translate('Photo unavailable','Hindi makuha ang larawan'))","if(!r.ok)await rejectResponse(r,`/evidence/${t.photo_evidence_id}/content`)")],
 'Audit':[("if(!r.ok)throw new Error('The original file could not be opened. Try again after checking your connection.')","if(!r.ok)await rejectResponse(r,'/evidence/'+item.id+'/content')")],
 'Funds':[("if(!r.ok)throw new Error(\"Original unavailable\")","if(!r.ok)await rejectResponse(r,`/evidence/${source.id}/content`)")],
 'CsvIntake':[("{readable(outcome.error)}. Inspect Household records before changing this row.","{workflowMessage(outcome.error,{role:actor.role,language})}"),("{readable(v)}","{workflowMessage(v,{role:actor.role,language})}")],
}
for name,items in replacements.items():
    file=root/(name+'.tsx')
    source=file.read_bytes().decode('utf-8')
    for old,new in items:
        assert old in source,(name,old)
        source=source.replace(old,new)
    if name in {'Payouts','Audit','Funds'}:
        source=source.replace(',request}',',request,rejectResponse}')
    file.write_bytes(source.encode('utf-8'))
print('Finished original-file, comparison, registry and CSV message handling.')
