"""Password-authenticated synthetic accounts and revocable local demo sessions."""
import hashlib
import hmac
import json
import secrets
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer

from app import config
from app.database import SessionLocal
from app.models.entities import Base

COOKIE = "ayudachain_session"
ROLES = {"DSWD", "BARANGAY", "DISBURSING", "BENEFICIARY", "AUDITOR"}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
_attempts = {}
_attempt_lock = threading.Lock()


class DemoSession(Base):
    __tablename__ = "demo_sessions"
    token_hash = Column(String(64), primary_key=True)
    account_id = Column(String(64), nullable=False)
    account_revision = Column(String(64), nullable=False)
    expires_at = Column(Integer, nullable=False, index=True)


@dataclass(frozen=True)
class Actor:
    id: str
    role: str
    display_name: str
    barangay_id: str | None = None
    beneficiary_id: str | None = None


def password_hash(password, salt):
    return hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt), n=16384, r=8, p=1, dklen=32).hex()


def account_revision(account):
    return hashlib.sha256(json.dumps(account, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_accounts():
    try:
        with open(config.DEMO_ACCOUNTS_FILE, encoding="utf-8") as stream:
            document = json.load(stream)
        if document["version"] != 1:
            raise ValueError()
        accounts = document["accounts"]
        if not isinstance(accounts, list):
            raise ValueError()
        by_id = {}
        for account in accounts:
            identity = account["id"]
            if not isinstance(identity, str) or not identity or len(identity) > 64 or identity in by_id:
                raise ValueError()
            if account["role"] not in ROLES or not isinstance(account["display_name"], str) or not isinstance(account["enabled"], bool):
                raise ValueError()
            if len(bytes.fromhex(account["salt"])) != 32 or len(bytes.fromhex(account["password_hash"])) != 32:
                raise ValueError()
            if account["role"] in {"BARANGAY", "DISBURSING"} and account.get("barangay_id") not in {"BRGY-001", "BRGY-002", "BRGY-003", "BRGY-004"}:
                raise ValueError()
            if account["role"] == "BENEFICIARY" and not account.get("beneficiary_id"):
                raise ValueError()
            by_id[identity] = account
        return by_id
    except (OSError, ValueError, TypeError, KeyError):
        raise HTTPException(503, "Demo sign-in is unavailable. Account provisioning is required.") from None


def _digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _csrf(token):
    return hmac.new(token.encode(), b"ayudachain-csrf-v1", hashlib.sha256).hexdigest()


def optional_actor(request):
    token = request.cookies.get(COOKIE)
    if not token or len(token) > 128:
        return None
    with SessionLocal() as db:
        session = db.get(DemoSession, _digest(token))
        if not session or session.expires_at <= int(time.time()):
            return None
        account = load_accounts().get(session.account_id)
        if not account or not account["enabled"] or session.account_revision != account_revision(account):
            return None
        actor = Actor(account["id"], account["role"], account["display_name"], account.get("barangay_id"), account.get("beneficiary_id"))
        request.state.actor = actor
        return actor


def require_actor(request):
    actor = getattr(request.state, "actor", None) or optional_actor(request)
    if actor is None:
        raise HTTPException(401, "Sign in to access this workflow.")
    return actor


def validate_origin(request):
    if request.headers.get("X-AyudaChain-Client") != "web":
        raise HTTPException(403, "A same-site application request is required.")
    origin = request.headers.get("origin")
    if origin and origin not in config.CORS_ORIGINS:
        raise HTTPException(403, "This request origin is not allowed.")
    if not config.SESSION_COOKIE_SECURE and (urlsplit(origin).hostname if origin else request.url.hostname) not in LOCAL_HOSTS:
        raise HTTPException(403, "Non-local sign-in requires HTTPS session cookies.")


def validate_csrf(request):
    validate_origin(request)
    token = request.cookies.get(COOKIE, "")
    if not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), _csrf(token)):
        raise HTTPException(403, "Refresh your session before submitting this request.")


def authorize_request(request: Request):
    path, method = request.url.path, request.method
    if path in {"/api/auth/login", "/api/auth/session", "/api/auth/logout", "/api/health", "/api/dashboard", "/api/blockchain/verify", "/api/public/receipts", "/api/demo/reset"} or (method == "GET" and (path == "/api/batches" or path.startswith("/api/batches/"))):
        return
    if not path.startswith(("/api/", "/receipts/")):
        return
    actor = require_actor(request)
    if method in {"GET", "HEAD"}:
        if (path == "/api/distributions" or path.startswith("/receipts/")) and actor.role == "BARANGAY":
            raise HTTPException(403, "Named payout records are not part of the barangay workflow.")
        if path.endswith("/reviews") and actor.role in {"BARANGAY", "DISBURSING"}:
            raise HTTPException(403, "Review evidence is not part of this account's workflow.")
        if path.startswith("/api/audit-trail/") and actor.role not in {"DSWD", "AUDITOR"}:
            raise HTTPException(403, "This account cannot inspect the office audit trail.")
        if path == "/api/beneficiaries/sample-csv" and actor.role != "DSWD":
            raise HTTPException(403, "This account cannot analyze office CSV data.")
        return
    allowed = {"DSWD"}
    if path == "/api/beneficiaries":
        allowed = {"DSWD", "BARANGAY"}
    elif path == "/api/distributions/confirm":
        allowed = {"DISBURSING"}
    if actor.role not in allowed:
        raise HTTPException(403, "This account cannot perform that action.")
    validate_csrf(request)


def scope_query(query, actor, model):
    if actor.role in {"BARANGAY", "DISBURSING"}:
        query = query.filter(model.barangay_id == actor.barangay_id)
    elif actor.role == "BENEFICIARY":
        query = query.filter(model.beneficiary_id == actor.beneficiary_id)
    return query


def assert_household_scope(actor, beneficiary):
    if not beneficiary or (actor.role in {"BARANGAY", "DISBURSING"} and beneficiary.barangay_id != actor.barangay_id) or (actor.role == "BENEFICIARY" and beneficiary.beneficiary_id != actor.beneficiary_id):
        raise HTTPException(404, "Household record not available to this account.")


def bind_reviewer(request, payload):
    actor = require_actor(request)
    if payload.reviewed_by is not None and payload.reviewed_by != actor.id:
        raise HTTPException(403, "The reviewer must be the signed-in account.")
    payload.reviewed_by = actor.id


router = APIRouter(prefix="/api/auth")


class LoginInput(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


def session_result(actor, token):
    return {"account": {"id": actor.id, "role": actor.role, "display_name": actor.display_name, "barangay_id": actor.barangay_id, "beneficiary_id": actor.beneficiary_id}, "csrf_token": _csrf(token), "synthetic": True}


@router.post("/login")
def login(payload: LoginInput, request: Request, response: Response):
    validate_origin(request)
    key = (request.client.host if request.client else "unknown", payload.username)
    now = int(time.time())
    with _attempt_lock:
        failures = [t for t in _attempts.get(key, []) if t > now - 300]
        if len(failures) >= 5:
            raise HTTPException(429, "Too many sign-in attempts. Try again later.")
    account = load_accounts().get(payload.username)
    salt = account["salt"] if account else "00" * 32
    computed = password_hash(payload.password, salt)
    if not account or not account["enabled"] or not hmac.compare_digest(computed, account["password_hash"]):
        with _attempt_lock:
            if len(_attempts) > 1000:
                for expired_key in [k for k, values in _attempts.items() if not any(t > now - 300 for t in values)]:
                    _attempts.pop(expired_key, None)
                if key not in _attempts and len(_attempts) > 1000:
                    raise HTTPException(429, "Too many sign-in attempts. Try again later.")
            _attempts[key] = [t for t in _attempts.get(key, []) if t > now - 300] + [now]
        raise HTTPException(401, "Incorrect account or password.")
    with _attempt_lock:
        _attempts.pop(key, None)
    token = secrets.token_urlsafe(32)
    with SessionLocal() as db:
        db.query(DemoSession).filter(DemoSession.expires_at <= now).delete()
        old = request.cookies.get(COOKIE)
        if old:
            db.query(DemoSession).filter_by(token_hash=_digest(old)).delete()
        db.add(DemoSession(token_hash=_digest(token), account_id=account["id"], account_revision=account_revision(account), expires_at=now + config.SESSION_TTL_SECONDS))
        db.commit()
    response.set_cookie(COOKIE, token, max_age=config.SESSION_TTL_SECONDS, httponly=True, secure=config.SESSION_COOKIE_SECURE, samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
    actor = Actor(account["id"], account["role"], account["display_name"], account.get("barangay_id"), account.get("beneficiary_id"))
    return session_result(actor, token)


@router.get("/session")
def session(request: Request, response: Response):
    actor = require_actor(request)
    response.headers["Cache-Control"] = "no-store"
    return session_result(actor, request.cookies[COOKIE])


@router.post("/logout")
def logout(request: Request, response: Response):
    require_actor(request)
    validate_csrf(request)
    with SessionLocal() as db:
        db.query(DemoSession).filter_by(token_hash=_digest(request.cookies[COOKIE])).delete()
        db.commit()
    response.delete_cookie(COOKIE, path="/", httponly=True, secure=config.SESSION_COOKIE_SECURE, samesite="strict")
    return {"success": True}
