"""Staged CSV intake endpoints. Preview never writes business records."""
from fastapi import APIRouter,Depends
from pydantic import Field
from .main import actor,result
from .actor import require_role
from .schemas.mvp import StrictModel
from .services import csv_intake

router=APIRouter(prefix='/api/v1/registry/csv')


class Preview(StrictModel):
    content:str=Field(max_length=csv_intake.MAX_BYTES)


class Confirm(Preview):
    digest:str=Field(pattern='^[a-f0-9]{64}$')
    rows:list[int]=Field(min_length=1,max_length=csv_intake.MAX_ROWS)


@router.get('/template')
def template(c=Depends(actor)):
    require_role(c,'beneficiary','barangay','dswd')
    return result(dict(columns=csv_intake.COLUMNS,required=['name','address','zone','declared_barangay_id'],
        content=','.join(csv_intake.COLUMNS)+'\n',max_bytes=csv_intake.MAX_BYTES,max_rows=1 if c.role=='beneficiary' else csv_intake.MAX_ROWS,
        description='One household head per row; birth_date optional (YYYY-MM-DD). No private contact, ID, evidence or account columns. Complete other members/private facts through normal registry forms.'))


@router.post('/preview')
def preview(body:Preview,c=Depends(actor)):
    return result(csv_intake.preview(body.content,c))


@router.post('/confirm')
def confirm(body:Confirm,c=Depends(actor)):
    return result(csv_intake.confirm(body.content,body.digest,body.rows,c))
