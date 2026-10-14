import hashlib
from uuid import UUID
from fastapi import APIRouter,Depends,File,UploadFile,Form,Header
from fastapi.responses import Response
from .main import actor,result
from .database import connection
from .commands import execute_command,DomainError
from .services.evidence import prepare_upload,save_upload,original_bytes
from .services.access import authorize_evidence,log_access

router=APIRouter(prefix='/api/v1')


@router.post('/evidence')
async def upload(file:UploadFile=File(...),purpose:str=Form(...),prepared_for_actor_id:UUID|None=Form(None),predecessor_id:UUID|None=Form(None),idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    raw=await file.read(10485761)
    await file.close()
    item=prepare_upload(raw,file.content_type)
    request={'byte_sha256':hashlib.sha256(raw).hexdigest(),'purpose':purpose,'prepared_for_actor_id':prepared_for_actor_id,'predecessor_id':predecessor_id}
    return result(execute_command(c.actor_id,'evidence.upload',idempotency_key,request,lambda tx:save_upload(tx,item,purpose,prepared_for_actor_id,predecessor_id)))


@router.get('/evidence/{identity}/content')
def content(identity:UUID,c=Depends(actor)):
    with connection() as db: item=authorize_evidence(db,c,identity)
    raw=original_bytes(item)
    log_access(c,'file','evidence_version_id',identity,['original_bytes'],None)
    return Response(raw,media_type=item['mime_type'],headers={'Cache-Control':'no-store','Content-Disposition':'inline; filename="synthetic-original"','X-Content-Type-Options':'nosniff'})


@router.get('/evidence/{identity}')
def evidence_metadata(identity:UUID,c=Depends(actor)):
    with connection() as db: item=authorize_evidence(db,c,identity)
    log_access(c,'open','evidence_version_id',identity,['original_metadata','extracted_fields'])
    return result({k:item[k] for k in ['id','purpose','mime_type','byte_length','extraction_state','extracted_fields','signature_state']})
