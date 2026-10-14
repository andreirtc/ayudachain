"""Private, frozen synthetic list versions; no approval or receipt backfill."""
import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import require_actor
from app.database import get_db
from app.models.entities import ValidatedList, ListFinalization, ReliefBatch, Beneficiary, BeneficiaryReview, Distribution, AuditEvent
from app.barangays import DEMO_BARANGAYS as BARANGAYS
from app.services.entitlements import current_rules, entitlement

router = APIRouter(prefix="/api/validated-lists")

def now(): return datetime.now(timezone.utc).isoformat()
def encoded(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def digest(value): return hashlib.sha256(encoded(value).encode()).hexdigest()
def write_lock(db):
    if db.bind.dialect.name == "sqlite": db.connection().exec_driver_sql("BEGIN IMMEDIATE")

def area_scope(actor, area):
    if area not in BARANGAYS: raise HTTPException(422, "Select a supported barangay.")
    if actor.role == "BENEFICIARY": raise HTTPException(403, "Staff access required.")
    if actor.role in {"BARANGAY", "DISBURSING"} and actor.barangay_id != area: raise HTTPException(404, "List not available to this account.")

class Prepare(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batch_id: str = Field(min_length=1, max_length=64)
    barangay_id: str = Field(min_length=1, max_length=32)
    request_id: UUID
    exclusions: dict[str, str] = Field(default_factory=dict, max_length=200)

class Finalize(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(min_length=1, max_length=512)
    confirm: bool

def snapshot(db, batch_id, area, exclusions):
    batch = db.query(ReliefBatch).filter_by(batch_id=batch_id).first()
    if not batch: raise HTTPException(404, "Batch not found.")
    records = db.query(Beneficiary).filter_by(batch_id=batch_id, barangay_id=area).order_by(Beneficiary.beneficiary_id).all()
    if len(records) > 2000: raise HTTPException(422, "This prototype supports at most 2000 records per area version.")
    if any(key not in {r.beneficiary_id for r in records} for key in exclusions): raise HTTPException(422, "An exclusion is outside the selected batch and area.")
    rows = []
    registry = db.query(Beneficiary).filter_by(batch_id=batch_id).all()
    roots = {b.beneficiary_id:b.canonical_beneficiary_id or b.beneficiary_id for b in registry}
    paid = db.query(Distribution).filter_by(batch_id=batch_id).all()
    rules = current_rules(db, batch_id)
    for ben in records:
        amount = entitlement(db, ben, batch, rules)
        review = db.query(BeneficiaryReview).filter_by(beneficiary_id=ben.beneficiary_id).order_by(BeneficiaryReview.id.desc()).first()
        reasons = []
        if ben.record_status != "ACTIVE": reasons.append("Historical record; retain earlier evidence")
        if ben.verification_status != "VERIFIED" or ben.review_status != "APPROVED": reasons.append("Eligibility not approved")
        if ben.duplicate_flag or ben.anomaly_flag: reasons.append("Unresolved review flag")
        if not review or review.decision != "VERIFIED": reasons.append("No retained approval decision")
        if not ben.household_name.strip() or ben.barangay_name != BARANGAYS[area]: reasons.append("Incomplete or inconsistent locality")
        prior_payouts = sorted(d.distribution_id for d in paid if roots.get(d.beneficiary_id,d.beneficiary_id)==roots[ben.beneficiary_id])
        if prior_payouts: reasons.append("Payout already recorded for linked household; this is not ineligibility")
        if amount["blocked"]: reasons.append(amount["blocked"])
        if ben.beneficiary_id in exclusions: reasons.append("Staff exclusion: " + exclusions[ben.beneficiary_id])
        rows.append({"beneficiary_id":ben.beneficiary_id,"household_name":ben.household_name,"dafac_id":ben.dafac_id,"record_status":ben.record_status,"canonical_beneficiary_id":ben.canonical_beneficiary_id,"verification_status":ben.verification_status,"review_status":ben.review_status,"duplicate_flag":bool(ben.duplicate_flag),"anomaly_flag":bool(ben.anomaly_flag),"included":not reasons,"exclusion_reasons":reasons,"decision":None if not review else {"review_id":review.review_id,"decision":review.decision,"actor":review.reviewed_by,"at":review.reviewed_at,"reason":review.reason}})
        rows[-1]["recorded_payout_references"] = prior_payouts
        rows[-1]["entitlement"] = {key: amount[key] for key in ("basis", "category", "amount_centavos", "rule_version")}
        if review:
            rows[-1]["decision"]["evidence"] = {key:getattr(review,key) for key in ("previous_verification_status","previous_review_status","previous_review_notes","duplicate_flag_before","anomaly_flag_before","duplicate_flag_after","anomaly_flag_after","linked_beneficiary_id","matched_beneficiary_id","duplicate_confidence")}
    return {"format":"ayudachain.validated-list","version":1,"batch_id":batch_id,"batch_name":batch.calamity_name,"batch_status":batch.status,"barangay_id":area,"barangay_name":BARANGAYS[area],"standard_grant_centavos":batch.standard_grant_centavos,"max_grant_centavos":batch.max_grant_centavos,"exclusions":exclusions,"rows":rows}

def view(db, row, actor):
    area_scope(actor, row.barangay_id)
    frozen = json.loads(row.snapshot_json)
    try:
        current = snapshot(db,row.batch_id,row.barangay_id,frozen["exclusions"])
        stale = digest(current)!=row.revision_hash
        current_check = "CURRENT" if not stale else "CHANGED"
    except HTTPException:
        stale = True
        current_check = "UNAVAILABLE"
    final = db.get(ListFinalization,row.list_id)
    if actor.role in {"BARANGAY","DISBURSING"}:
        for item in frozen["rows"]:
            item.pop("recorded_payout_references",None)
            if item["decision"]: item["decision"].pop("reason",None); item["decision"].pop("actor",None); item["decision"].pop("evidence",None)
            item["exclusion_reasons"]=["Staff exclusion (reason restricted)" if reason.startswith("Staff exclusion:") else reason for reason in item["exclusion_reasons"]]
        frozen["exclusions"]={key:"Reason restricted" for key in frozen["exclusions"]}
    return {"list_id":row.list_id,"version":row.version,"prepared_by":row.prepared_by,"prepared_at":row.prepared_at,"revision_hash":row.revision_hash,"state":"FINALIZED" if final else "PREPARED","stale":stale,"current_check":current_check,"snapshot":frozen,"finalization":None if not final else {"actor":final.finalized_by,"name":final.finalized_name,"at":final.finalized_at,"reason":final.reason if actor.role in {"DSWD","AUDITOR"} else None}}

@router.get("")
def versions(request:Request, batch_id:str|None=None, db:Session=Depends(get_db)):
    actor=require_actor(request)
    if actor.role=="BENEFICIARY": raise HTTPException(403,"Staff access required.")
    query=db.query(ValidatedList)
    if actor.role in {"BARANGAY","DISBURSING"}: query=query.filter_by(barangay_id=actor.barangay_id)
    if batch_id: query=query.filter_by(batch_id=batch_id)
    return [view(db,row,actor) for row in query.order_by(ValidatedList.prepared_at.desc()).all()]

@router.get("/{list_id}")
def detail(list_id:str,request:Request,db:Session=Depends(get_db)):
    row=db.get(ValidatedList,list_id)
    if not row: raise HTTPException(404,"List not available.")
    return view(db,row,require_actor(request))

@router.post("/prepare")
def prepare(payload:Prepare,request:Request,response:Response,db:Session=Depends(get_db)):
    actor=require_actor(request); area_scope(actor,payload.barangay_id)
    if actor.role not in {"DSWD","BARANGAY"}: raise HTTPException(403,"Preparation belongs to DSWD or the assigned barangay.")
    exclusions={key:reason.strip() for key,reason in payload.exclusions.items()}
    if any(not reason or len(reason)>512 or any(ord(c)<32 and c not in "\n\t" for c in reason) for reason in exclusions.values()): raise HTTPException(422,"Enter a readable reason for every exclusion.")
    fingerprint=digest({"batch_id":payload.batch_id,"area":payload.barangay_id,"exclusions":exclusions})
    write_lock(db)
    prior=db.query(ValidatedList).filter_by(prepared_by=actor.id,request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint!=fingerprint: raise HTTPException(409,"This retry identity belongs to a different preparation.")
        return view(db,prior,actor)
    frozen=snapshot(db,payload.batch_id,payload.barangay_id,exclusions)
    if frozen["batch_status"]!="ACTIVE": raise HTTPException(409,"Prepare a list for an active batch.")
    version=(db.query(func.max(ValidatedList.version)).filter_by(batch_id=payload.batch_id,barangay_id=payload.barangay_id).scalar() or 0)+1
    row=ValidatedList(list_id="LIST-"+str(uuid4()),batch_id=payload.batch_id,barangay_id=payload.barangay_id,version=version,prepared_by=actor.id,prepared_at=now(),request_id=str(payload.request_id),request_fingerprint=fingerprint,snapshot_json=encoded(frozen),revision_hash=digest(frozen))
    db.add(row); db.add(AuditEvent(batch_id=row.batch_id,event_type="LIST_PREPARED",entity_id=row.list_id,description=f"{actor.id} prepared {row.barangay_id} list version {version}")); db.commit()
    response.status_code=201
    return view(db,row,actor)

@router.post("/{list_id}/finalize")
def finalize(list_id:str,payload:Finalize,request:Request,response:Response,db:Session=Depends(get_db)):
    actor=require_actor(request)
    if actor.role!="DSWD": raise HTTPException(403,"Only DSWD can finalize this prototype list.")
    if not payload.confirm or not payload.reason.strip(): raise HTTPException(422,"Confirm the included records and enter a reason.")
    write_lock(db); row=db.get(ValidatedList,list_id)
    if not row: raise HTTPException(404,"List not available.")
    if db.get(ListFinalization,list_id): return view(db,row,actor)
    frozen=json.loads(row.snapshot_json); current=snapshot(db,row.batch_id,row.barangay_id,frozen["exclusions"])
    if digest(current)!=row.revision_hash or current["batch_status"]!="ACTIVE": raise HTTPException(409,"Records changed after preparation. Prepare and inspect a new version.")
    if not any(item["included"] for item in frozen["rows"]): raise HTTPException(409,"No eligible records with retained approval decisions are included.")
    db.add(ListFinalization(list_id=list_id,finalized_by=actor.id,finalized_name=actor.display_name,finalized_at=now(),reason=payload.reason.strip()))
    db.add(AuditEvent(batch_id=row.batch_id,event_type="LIST_FINALIZED",entity_id=list_id,description=f"{actor.id} finalized {row.barangay_id} list version {row.version}")); db.commit(); response.status_code=201
    return view(db,row,actor)
