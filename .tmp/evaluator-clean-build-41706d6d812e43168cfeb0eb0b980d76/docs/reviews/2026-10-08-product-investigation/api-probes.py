"""Synthetic investigation scenarios. Refuses to run outside the disposable snapshot."""
import concurrent.futures, json, pathlib, sqlite3, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
review = pathlib.Path(__file__).resolve().parent
lab = pathlib.Path(json.loads((review / "initial-state.json").read_text())["snapshot"])
assert lab.name.startswith("ayudachain-investigation-") and "Temp" in lab.parts
db = lab / "backend/ayudachain.db"
results = []

def req(label, path, body=None, method=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    request = urllib.request.Request("http://127.0.0.1:8000" + path, data=data, method=method or ("POST" if data is not None else "GET"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            text = response.read().decode()
            try: value = json.loads(text)
            except ValueError: value = text
            out = {"status": response.status, "body": value, "cors": response.headers.get("Access-Control-Allow-Origin")}
    except urllib.error.HTTPError as error:
        out = {"status": error.code, "body": json.loads(error.read())}
    except Exception as error:
        out = {"status": "connection failure", "error": repr(error)}
    row = {"scenario": label, "method": request.method, "path": path, "request": body if raw is None else repr(raw), "response": out, "auth": "none"}
    results.append(row)
    (review / "api-probes.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"scenario": label, "status": out["status"], "summary": str(out.get("body", out.get("error")))[:350]}, ensure_ascii=False))
    return out.get("body")

def sql(query, args=()):
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        return [dict(row) for row in cur.fetchall()]

def register(n, name, batch="RELIEF-2026-001"):
    return req("register-"+str(n), "/api/beneficiaries", {"beneficiary_id": f"BEN-{n}", "dafac_id": f"DFC-2026-{n}", "household_name": name, "barangay_id": "BRGY-001", "barangay_name": "Synthetic Islet", "batch_id": batch})

def payout(label, d, ben, amount=5000, batch="RELIEF-2026-001"):
    return req(label, "/api/distributions/confirm", {"distribution_id": d, "beneficiary_id": ben, "amount": amount, "batch_id": batch})

mode = sys.argv[1]
if mode == "baseline":
    req("public-entire-registry", "/api/beneficiaries")
    req("single-public-household", "/api/beneficiaries/BEN-0001")
    req("sample-csv-route-shadow", "/api/beneficiaries/sample-csv")
    req("missing-distribution", "/api/blockchain/verify", {"distribution_id": "DIST-MISSING"})
    req("blank-verification-selects-last", "/api/blockchain/verify", {})
    req("normal-local-verification", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
    before = sql("SELECT COUNT(*) AS n FROM audit_events")[0]["n"]
    register(9901, "Lino Bituan")
    after = sql("SELECT COUNT(*) AS n FROM audit_events")[0]["n"]
    results.append({"scenario": "nonduplicate-registration-audit", "before": before, "after": after, "source": "isolated database query"})
    register(9902, "")
    register(9903, "Sela Maligaya")
    req("arbitrary-review-status", "/api/beneficiaries/BEN-9903/verify", {"status": "MADE_UP", "review_notes": "Synthetic API probe"})
    register(9904, "Tala Cabintuan")
    register(9905, "Nilo Amihan")
    register(9906, "Vela Dapilan")
    register(9907, "Amaya Sinagtala")
    payout("zero-amount", "DIST-ZERO", "BEN-9901", 0)
    payout("over-ceiling", "DIST-OVER", "BEN-9901", 10001)
    payout("missing-household", "DIST-MISSINGBEN", "BEN-NONE")
    payout("pay-rejected-household", "DIST-REJECTED", "BEN-0007", 2000)
    payout("retry-rejected-payout", "DIST-REJECTED", "BEN-0007", 2000)
    payout("pay-flagged-household", "DIST-FLAGGED", "BEN-0014")
    req("tiny-program-release", "/api/funds/releases", {"batch_id": "RELIEF-LAB-002", "calamity_name": "Synthetic drill", "amount": 10})
    req("over-allocation", "/api/allocations", {"allocation_id": "ALLOC-LAB-001", "batch_id": "RELIEF-LAB-002", "amount": 1000000, "barangay_id": "BRGY-001", "barangay_name": "Synthetic Islet"})
    payout("cross-batch-over-budget", "DIST-LAB-BUDGET", "BEN-9901", 5000, "RELIEF-LAB-002")
    payout("unknown-batch-chain-rejected-db-saved", "DIST-LAB-ABSENT", "BEN-9903", 5000, "RELIEF-NOT-ONCHAIN")
    req("absent-anchor-false-verification", "/api/blockchain/verify", {"distribution_id": "DIST-LAB-ABSENT"})
    req("negative-release-chain-rejected-db-saved", "/api/funds/releases", {"batch_id": "RELIEF-LAB-NEGATIVE", "amount": -10})
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(payout, "concurrent-same-household-"+str(i), f"DIST-RACE-{i}", "BEN-9904") for i in (1,2)]
        for job in jobs: job.result()
    results.append({"scenario": "concurrent-db-result", "rows": sql("SELECT distribution_id,beneficiary_id,amount,blockchain_tx_hash FROM distributions WHERE beneficiary_id='BEN-9904'")})
    req("malformed-json", "/api/beneficiaries", raw=b"{")
    req("non-numeric-amount", "/api/distributions/confirm", {"beneficiary_id": "BEN-9905", "amount": "invalid"})
    req("health-after-invalid-requests", "/api/health")
elif mode == "tamper":
    original = sql("SELECT household_name FROM beneficiaries WHERE beneficiary_id='BEN-0001'")[0]["household_name"]
    sql("UPDATE beneficiaries SET household_name='Synthetic Renamed Household' WHERE beneficiary_id='BEN-0001'")
    req("real-name-change-not-detected", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
    sql("UPDATE beneficiaries SET household_name=? WHERE beneficiary_id='BEN-0001'", (original,))
    receipt = lab / "backend/app/data/receipts/sample_relief_receipt.svg"
    old = receipt.read_bytes()
    receipt.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Synthetic replaced receipt DFC-2026-9901</text></svg>', encoding="utf-8")
    req("real-file-change-not-detected", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
    receipt.write_bytes(old)
    sql("UPDATE distributions SET amount=2000 WHERE distribution_id='DIST-0001'")
    req("real-amount-mismatch-detected", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
    sql("UPDATE distributions SET amount=5000 WHERE distribution_id='DIST-0001'")
    req("restored-amount-matches", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
elif mode == "reverse":
    sql("INSERT INTO distributions (distribution_id,beneficiary_id,batch_id,amount,receipt_hash,ocr_text,verification_method,status,distributed_at) SELECT 'DIST-DB-ONLY',beneficiary_id,batch_id,amount,receipt_hash,ocr_text,verification_method,status,distributed_at FROM distributions WHERE distribution_id='DIST-0001'")
    payout("chain-success-db-id-collision", "DIST-DB-ONLY", "BEN-9905")
    results.append({"scenario": "db-collision-existing-row", "rows": sql("SELECT distribution_id,beneficiary_id,receipt_hash FROM distributions WHERE distribution_id='DIST-DB-ONLY'")})
elif mode == "outage":
    req("outage-dashboard", "/api/dashboard")
    payout("outage-payout-db-success", "DIST-OUTAGE", "BEN-9906")
    req("outage-false-verification", "/api/blockchain/verify", {"distribution_id": "DIST-OUTAGE"})
elif mode == "delete":
    req("unauthorized-delete-paid-household", "/api/beneficiaries/BEN-0001", method="DELETE")
    results.append({"scenario": "orphan-distribution-count", "rows": sql("SELECT COUNT(*) AS n FROM distributions WHERE beneficiary_id='BEN-0001'")})
    req("orphan-payout-still-verified", "/api/blockchain/verify", {"distribution_id": "DIST-0001"})
else:
    raise SystemExit("Unknown mode")
(review / ("api-probes-" + mode + ".json")).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
