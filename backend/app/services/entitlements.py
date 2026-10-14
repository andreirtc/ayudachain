"""Calculated assistance amounts: approved damage claims priced by the batch's current amount rules."""
import json
from app.models.entities import AmountRuleVersion, ClaimRevision, DamageClaim

CATEGORIES = {"TOTALLY_DAMAGED": "Totally damaged house", "PARTIALLY_DAMAGED": "Partially damaged house"}
PENDING_CLAIM = {"SUBMITTED", "ENDORSED", "NOT_ENDORSED", "NEEDS_INFO"}


def current_rules(db, batch_id):
    return db.query(AmountRuleVersion).filter_by(batch_id=batch_id).order_by(AmountRuleVersion.version.desc()).first()


def latest_revision(db, claim_id):
    return db.query(ClaimRevision).filter_by(claim_id=claim_id).order_by(ClaimRevision.revision.desc()).first()


def entitlement(db, ben, batch, rules=None):
    """`blocked` is a reason no payout amount can be determined yet."""
    claim = db.query(DamageClaim).filter_by(beneficiary_id=ben.beneficiary_id, batch_id=ben.batch_id).first()
    standard = {"basis": "STANDARD", "category": None, "amount_centavos": batch.standard_grant_centavos, "rule_version": None, "claim_id": None, "claim_status": None, "blocked": None}
    if not claim:
        return standard
    rev = latest_revision(db, claim.claim_id)
    standard.update(claim_id=claim.claim_id, claim_status=rev.status)
    if rev.status == "DECLINED":
        return standard
    if rev.status in PENDING_CLAIM:
        return {**standard, "basis": "PENDING", "amount_centavos": None, "category": rev.category, "blocked": "Damage claim awaiting decision"}
    rules = rules or current_rules(db, ben.batch_id)
    amount = json.loads(rules.rules_json).get(rev.category, {}).get("amount_centavos") if rules else None
    if amount is None:
        return {**standard, "basis": "PENDING", "amount_centavos": None, "category": rev.category, "blocked": "No amount rule for the approved damage category"}
    return {**standard, "basis": "CLAIM", "category": rev.category, "amount_centavos": amount, "rule_version": rules.version}
