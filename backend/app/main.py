"""Authoritative synthetic-evaluation FastAPI API. No automatic schema or seeds."""
from dataclasses import asdict
from fastapi import FastAPI, Header, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from .database import connection
from .actor import resolve_identity
from .commands import DomainError
from .schemas.mvp import ContextResponse, ActorsResponse, ReferenceResponse

app=FastAPI(title='AyudaChain local synthetic MVP',version='2.0.0',description='Claimed unverified actors. Authentication Pending. No operational privacy or authenticated accountability.')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000','http://localhost:3001','http://127.0.0.1:3001'],allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Demo-Actor-ID','Idempotency-Key'])


def meta():
    clock='unavailable'
    try:
        with connection() as db:
            modes=db.execute("SELECT DISTINCT clock_mode FROM evaluation_runs WHERE state='active'").fetchall()
            clock=modes[0]['clock_mode'] if len(modes)==1 else 'mixed' if modes else 'not_provisioned'
    except (psycopg.Error,RuntimeError):pass
    return dict(mode='local_synthetic_evaluation',identity_assurance='claimed_unverified',authentication='pending',impersonation_possible=True,blockchain_simulated=False,chain_time='actual',business_clock=clock,simulated_services=['Simulated National ID check','Simulated notice SMS'],digital_signatures='not_validated',real_data_ready=False)


def result(data):
    # PostgreSQL bigint amounts exceed JavaScript's exact integer range.
    # Preserve cents on every projection, including informational differences.
    def exact(value):
        if isinstance(value,dict):return {k:str(v) if k.endswith('_centavos') and isinstance(v,int) and not isinstance(v,bool) else exact(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [exact(v) for v in value]
        return value
    return {'data':exact(data),'meta':meta()}


def actor(x_demo_actor_id: str | None=Header(default=None)):
    with connection() as db: return resolve_identity(db,x_demo_actor_id)


@app.middleware('http')
async def no_store(request:Request,call_next):
    response=await call_next(request)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Identity-Assurance']='claimed_unverified'
    response.headers['X-Authentication']='pending'
    return response


@app.exception_handler(DomainError)
async def domain_error(request,exc): return JSONResponse({'error':exc.code,'meta':meta()},status_code=exc.status)


@app.exception_handler(RequestValidationError)
async def invalid_request(request,exc):
    # Pydantic inputs may contain a PIN/code/private file selector. Never echo them.
    return JSONResponse({'error':'invalid_input','fields':[{'path':list(e['loc']),'type':e['type']} for e in exc.errors()],'meta':meta()},status_code=422)


@app.exception_handler(psycopg.Error)
async def database_error(request,exc):
    status=409 if isinstance(exc,psycopg.IntegrityError) else 503
    return JSONResponse({'error':'database_conflict' if status==409 else 'database_unavailable','meta':meta()},status_code=status)


@app.get('/api/v1/health')
def health():
    try:
        with connection() as db:
            ready=bool(db.execute("SELECT 1 FROM mvp_migrations WHERE version='0001'").fetchone())
        return result({'database':'ready' if ready else 'migration_required','chain':'not_checked','storage':'not_checked'})
    except (psycopg.Error,RuntimeError):
        return JSONResponse(result({'database':'unavailable','chain':'not_checked','storage':'not_checked'}),status_code=503)


@app.get('/api/v1/context',response_model=ContextResponse)
def context(c=Depends(actor)): return result(asdict(c))


@app.get('/api/v1/actors/catalogue',response_model=ActorsResponse)
def catalogue():
    with connection() as db:
        rows=db.execute("""SELECT a.id,a.role,a.display_name,v.status,v.position,v.barangay_id FROM actors a
            JOIN actor_versions v ON v.id=a.current_version_id JOIN evaluation_runs r ON r.id=a.run_id
            WHERE r.state='active' AND a.role!='system' ORDER BY a.role,a.display_name,a.id""").fetchall()
    return result(rows)


@app.get('/api/v1/disasters',response_model=ReferenceResponse)
def disasters():
    with connection() as db:
        rows=db.execute("SELECT d.id,d.name FROM disasters d JOIN evaluation_runs r ON r.id=d.run_id WHERE r.state='active' ORDER BY d.name,d.id").fetchall()
    return result(rows)


@app.get('/api/v1/barangays',response_model=ReferenceResponse)
def barangays():
    with connection() as db:
        rows=db.execute("SELECT b.id,b.name FROM barangays b JOIN evaluation_runs r ON r.id=b.run_id WHERE r.state='active' ORDER BY b.name,b.id").fetchall()
    return result(rows)


@app.get('/api/v1/categories',response_model=ReferenceResponse)
def categories():
    with connection() as db:
        rows=db.execute("SELECT b.id,b.label name FROM damage_categories b JOIN evaluation_runs r ON r.id=b.run_id WHERE r.state='active' ORDER BY b.code,b.id").fetchall()
    return result(rows)


from .routes_evidence import router as evidence_router
app.include_router(evidence_router)
from .routes_integrity import router as integrity_router
app.include_router(integrity_router)
from .routes_funds import router as funds_router
app.include_router(funds_router)
from .routes_csv import router as csv_router
app.include_router(csv_router)
from .routes_queues import router as queues_router
app.include_router(queues_router)
from .routes_operations import router as operations_router
app.include_router(operations_router)
from .routes_lookup import router as lookup_router
app.include_router(lookup_router)
from .routes_registry import router as registry_router
app.include_router(registry_router)
from .routes_claims import router as claims_router
app.include_router(claims_router)
from .routes_entitlements import router as entitlements_router
app.include_router(entitlements_router)
from .routes_sessions import router as sessions_router
app.include_router(sessions_router)
from .routes_payouts import router as payouts_router
app.include_router(payouts_router)
from .routes_outcomes import router as outcomes_router
app.include_router(outcomes_router)
from .routes_audit import router as audit_router
app.include_router(audit_router)
from .routes_evaluation import router as evaluation_router
app.include_router(evaluation_router)
