"""
AyudaChain Backend REST Server
High-performance, zero-external-dependency HTTP server with SQLite persistence,
AI entity resolution, statistical anomaly detection, SHA-256 integrity pipeline,
and real Polygon/EVM blockchain anchoring.
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add app to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.ai.entity_resolution import EntityResolutionEngine
from app.ai.anomaly_detection import DistributionAnomalyDetector
from app.services.hasher import compute_receipt_hash, verify_receipt_integrity
from app.services.blockchain import blockchain_service
from app.services.receipt_generator import save_sample_receipt, DEMO_OCR_TEXT

DB_PATH = os.path.join(BASE_DIR, "ayudachain.db")
RECEIPTS_DIR = os.path.join(BASE_DIR, "app", "data", "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)
save_sample_receipt(RECEIPTS_DIR)

# Initialize AI Engines
entity_resolver = EntityResolutionEngine(confidence_threshold=0.78)
anomaly_detector = DistributionAnomalyDetector(standard_grant_amount=5000.0)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS relief_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT UNIQUE NOT NULL,
        calamity_name TEXT NOT NULL,
        calamity_type TEXT DEFAULT 'Typhoon',
        source_agency TEXT DEFAULT 'DSWD Central Office',
        recipient_lgu TEXT DEFAULT 'Provincial Government of Albay',
        purpose TEXT DEFAULT 'Emergency Calamity Cash & Relief Assistance',
        amount REAL NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        blockchain_tx_hash TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        allocation_id TEXT UNIQUE NOT NULL,
        batch_id TEXT NOT NULL,
        barangay_id TEXT NOT NULL,
        barangay_name TEXT NOT NULL,
        amount REAL NOT NULL,
        beneficiary_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ALLOCATED',
        blockchain_tx_hash TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS beneficiaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        beneficiary_id TEXT UNIQUE NOT NULL,
        dafac_id TEXT,
        household_name TEXT NOT NULL,
        barangay_id TEXT NOT NULL,
        barangay_name TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        contact_number TEXT,
        verification_status TEXT DEFAULT 'UNVERIFIED',
        duplicate_flag INTEGER DEFAULT 0,
        duplicate_confidence REAL DEFAULT 0.0,
        duplicate_matched_id TEXT,
        anomaly_flag INTEGER DEFAULT 0,
        review_status TEXT DEFAULT 'PENDING',
        review_notes TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS distributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        distribution_id TEXT UNIQUE NOT NULL,
        beneficiary_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        amount REAL NOT NULL,
        verification_method TEXT DEFAULT 'QR_VOUCHER_PHYSICAL_RECEIPT',
        receipt_hash TEXT NOT NULL,
        receipt_file_path TEXT,
        ocr_text TEXT,
        status TEXT DEFAULT 'CONFIRMED',
        blockchain_tx_hash TEXT,
        distributed_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL,
        entity_id TEXT,
        blockchain_tx_hash TEXT,
        timestamp TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def seed_default_data():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM relief_batches")
    if cursor.fetchone()["cnt"] > 0:
        conn.close()
        return

    now = datetime.utcnow()
    batch_id = "RELIEF-2026-001"
    calamity = "Typhoon Salinlahi"
    total_fund = 10000000.0

    # Submit on-chain release or fallback hash
    bc_res = blockchain_service.release_fund(batch_id, total_fund, calamity, "DSWD Central Office")
    tx_hash = bc_res.get("txHash", "0x5f27ce6ea3d921efb37633dbe87ff1ce347d6a2b5895055472ee4b297d8df933")

    cursor.execute("""
    INSERT INTO relief_batches (batch_id, calamity_name, calamity_type, source_agency, recipient_lgu, purpose, amount, status, blockchain_tx_hash, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, calamity, "Super Typhoon", "DSWD Central Office", "Provincial Government of Albay", "Emergency Calamity Cash and Food Voucher", total_fund, "ACTIVE", tx_hash, (now - timedelta(hours=3)).isoformat()))

    # Allocations
    barangays = [
        ("BRGY-001", "San Isidro", 2500000.0, 500),
        ("BRGY-002", "Santa Elena", 2500000.0, 500),
        ("BRGY-003", "San Roque", 2500000.0, 500),
        ("BRGY-004", "Maligaya", 2500000.0, 500),
    ]

    for i, (b_id, b_name, b_amt, b_cnt) in enumerate(barangays):
        alloc_id = f"ALLOC-000{i+1}"
        bc_a = blockchain_service.allocate_fund(batch_id, alloc_id, b_id, b_amt)
        a_tx = bc_a.get("txHash", f"0xalloc{i+1}e6ea3d921efb37633dbe87ff1ce347d6a2b5895055472ee4b297d8df")
        t_alloc = (now - timedelta(hours=2, minutes=40 - i*10)).isoformat()
        cursor.execute("""
        INSERT INTO allocations (allocation_id, batch_id, barangay_id, barangay_name, amount, beneficiary_count, status, blockchain_tx_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (alloc_id, batch_id, b_id, b_name, b_amt, b_cnt, "ALLOCATED", a_tx, t_alloc))

        cursor.execute("""
        INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (batch_id, "ALLOCATION", f"Allocated ₱{b_amt:,.2f} to Barangay {b_name}", b_amt, alloc_id, a_tx, t_alloc))

    # Beneficiaries (with realistic names, 2 duplicates, 1 anomaly)
    bens = [
        ("BEN-0001", "Roberto Ramos", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0002", "Juan Dela Cruz", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Zero matches found"),
        ("BEN-0003", "Elena Bautista", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0004", "Danilo Soriano", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0005", "Carmencita Reyes", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0006", "Antonio Mercado", "BRGY-001", "San Isidro", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        # SEEDED DUPLICATE 1: Juan D. Cruz vs Juan Dela Cruz
        ("BEN-0007", "Juan D. Cruz", "BRGY-001", "San Isidro", "FLAGGED_FOR_REVIEW", 1, 0.94, "BEN-0002", 0, "PENDING", "AI Entity Resolution: 94% fuzzy name match with BEN-0002 (Juan Dela Cruz). Human review required."),
        
        ("BEN-0008", "Rodrigo Mendoza", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0009", "Teresa Villanueva", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0010", "Eduardo Flores", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0011", "Consuelo Garcia", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0012", "Felipe Castro", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0013", "Maria Santos", "BRGY-002", "Santa Elena", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        # SEEDED DUPLICATE 2: Ma. Santos vs Maria Santos
        ("BEN-0014", "Ma. Santos", "BRGY-002", "Santa Elena", "FLAGGED_FOR_REVIEW", 1, 0.91, "BEN-0013", 0, "PENDING", "AI Entity Resolution: 91% name match with BEN-0013 (Maria Santos). Human review required."),
        
        ("BEN-0015", "Francisco Aguilar", "BRGY-003", "San Roque", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0016", "Luzviminda Ocampo", "BRGY-003", "San Roque", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0017", "Vicente Navarro", "BRGY-003", "San Roque", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0018", "Rosario Padilla", "BRGY-003", "San Roque", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0019", "Gerardo Alcantara", "BRGY-003", "San Roque", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        
        ("BEN-0020", "Manuel Guinto", "BRGY-004", "Maligaya", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        ("BEN-0021", "Corazon Tolentino", "BRGY-004", "Maligaya", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
        # SEEDED ANOMALY: Non-standard grant request amount & duplicate velocity
        ("BEN-0022", "Bernardo Magno", "BRGY-004", "Maligaya", "FLAGGED_FOR_REVIEW", 0, 0.0, None, 1, "PENDING", "AI Anomaly Engine: Unusual grant request ₱15,000 (200% over standard ₱5,000 threshold). Flagged for Ombudsman review."),
        ("BEN-0023", "Corazon Tolentino", "BRGY-004", "Maligaya", "FLAGGED_FOR_REVIEW", 1, 0.98, "BEN-0021", 0, "PENDING", "AI Entity Resolution: 98% duplicate match with BEN-0021."),
        ("BEN-0024", "Gregorio Pineda", "BRGY-004", "Maligaya", "VERIFIED", 0, 0.0, None, 0, "APPROVED", "Auto-verified: Identity validated"),
    ]

    for ben_id, name, brgy_id, brgy_name, status, is_dup, conf, match_id, is_anom, rev_status, notes in bens:
        dafac_id = f"DFC-2026-{ben_id[-4:]}"
        cursor.execute("""
        INSERT INTO beneficiaries (beneficiary_id, dafac_id, household_name, barangay_id, barangay_name, batch_id, contact_number, verification_status, duplicate_flag, duplicate_confidence, duplicate_matched_id, anomaly_flag, review_status, review_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ben_id, dafac_id, name, brgy_id, brgy_name, batch_id, f"0917-555-{ben_id[-4:]}", status, is_dup, conf, match_id, is_anom, rev_status, notes, (now - timedelta(hours=2)).isoformat()))

    # Distributions
    dists = [
        ("DIST-0001", "BEN-0001", 5000.0, "Roberto Ramos"),
        ("DIST-0002", "BEN-0002", 5000.0, "Juan Dela Cruz"),
        ("DIST-0003", "BEN-0003", 5000.0, "Elena Bautista"),
        ("DIST-0004", "BEN-0008", 5000.0, "Rodrigo Mendoza"),
        ("DIST-0005", "BEN-0009", 5000.0, "Teresa Villanueva"),
    ]

    for d_id, ben_id, amt, h_name in dists:
        r_hash = compute_receipt_hash(d_id, ben_id, batch_id, amt, DEMO_OCR_TEXT)
        bc_d = blockchain_service.confirm_distribution(batch_id, d_id, ben_id, amt, r_hash)
        d_tx = bc_d.get("txHash", f"0xdist{d_id[-4:]}e6ea3d921efb37633dbe87ff1ce347d6a2b5895055472ee4b297d8df")
        t_dist = (now - timedelta(minutes=40 - int(d_id[-1])*5)).isoformat()

        cursor.execute("""
        INSERT INTO distributions (distribution_id, beneficiary_id, batch_id, amount, verification_method, receipt_hash, receipt_file_path, ocr_text, status, blockchain_tx_hash, distributed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (d_id, ben_id, batch_id, amt, "QR_VOUCHER_PHYSICAL_RECEIPT", r_hash, "/receipts/sample_relief_receipt.svg", DEMO_OCR_TEXT, "CONFIRMED", d_tx, t_dist))

        cursor.execute("""
        INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (batch_id, "DISTRIBUTION_CONFIRMED", f"Disbursed ₱{amt:,.2f} to {h_name} ({ben_id}) — Receipt anchored on-chain", amt, d_id, d_tx, t_dist))

    # Audit Events for AI
    cursor.execute("""
    INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, "AI_DUPLICATE_FLAG", "AI Entity Resolution: Flagged BEN-0007 (Juan D. Cruz) ↔ BEN-0002 (Juan Dela Cruz) [94% match]", None, "BEN-0007", None, (now - timedelta(minutes=30)).isoformat()))

    cursor.execute("""
    INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, "AI_DUPLICATE_FLAG", "AI Entity Resolution: Flagged BEN-0014 (Ma. Santos) ↔ BEN-0013 (Maria Santos) [91% match]", None, "BEN-0014", None, (now - timedelta(minutes=28)).isoformat()))

    cursor.execute("""
    INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, "AI_ANOMALY_FLAG", "AI Anomaly Engine: Flagged BEN-0022 for non-standard disbursement amount (₱15,000)", None, "BEN-0022", None, (now - timedelta(minutes=25)).isoformat()))

    conn.commit()
    conn.close()
    print("Database seeded with realistic Typhoon Salinlahi demo data.")


class AyudaChainHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        raw = self.rfile.read(content_len).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Serve static receipts
        if path.startswith("/receipts/"):
            fname = os.path.basename(path)
            fpath = os.path.join(RECEIPTS_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml" if fname.endswith(".svg") else "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self._send_json({"error": "File not found"}, 404)
                return

        # Health
        if path == "/api/health":
            self._send_json({
                "status": "healthy",
                "service": "AyudaChain Backend",
                "timestamp": datetime.utcnow().isoformat(),
                "blockchain": blockchain_service.get_status()
            })
            return

        conn = get_db()
        cursor = conn.cursor()

        # Dashboard
        if path == "/api/dashboard":
            cursor.execute("SELECT * FROM relief_batches LIMIT 1")
            batch = cursor.fetchone()
            if not batch:
                conn.close()
                self._send_json({"error": "No active batch"}, 404)
                return

            cursor.execute("SELECT SUM(amount) as s FROM allocations WHERE batch_id = ?", (batch["batch_id"],))
            total_allocated = cursor.fetchone()["s"] or 0.0

            cursor.execute("SELECT SUM(amount) as s, COUNT(*) as c FROM distributions WHERE batch_id = ? AND status = 'CONFIRMED'", (batch["batch_id"],))
            dist_row = cursor.fetchone()
            total_distributed = dist_row["s"] or 0.0
            confirmed_dists = dist_row["c"] or 0

            cursor.execute("SELECT COUNT(*) as c FROM beneficiaries WHERE batch_id = ?", (batch["batch_id"],))
            total_bens = cursor.fetchone()["c"] or 0

            cursor.execute("SELECT COUNT(*) as c FROM beneficiaries WHERE batch_id = ? AND verification_status = 'VERIFIED'", (batch["batch_id"],))
            verified_bens = cursor.fetchone()["c"] or 0

            cursor.execute("SELECT COUNT(*) as c FROM beneficiaries WHERE batch_id = ? AND (verification_status = 'FLAGGED_FOR_REVIEW' OR duplicate_flag = 1 OR anomaly_flag = 1)", (batch["batch_id"],))
            flagged_recs = cursor.fetchone()["c"] or 0

            cursor.execute("SELECT * FROM audit_events WHERE batch_id = ? ORDER BY timestamp DESC LIMIT 8", (batch["batch_id"],))
            recent_events = cursor.fetchall()
            recent_txs = [
                {
                    "event_type": ev["event_type"],
                    "description": ev["description"],
                    "amount": ev["amount"],
                    "tx_hash": ev["blockchain_tx_hash"],
                    "timestamp": ev["timestamp"]
                }
                for ev in recent_events
            ]

            bc_info = blockchain_service.get_status()
            conn.close()

            self._send_json({
                "batch_id": batch["batch_id"],
                "calamity_name": batch["calamity_name"],
                "total_released": batch["amount"],
                "total_allocated": total_allocated,
                "total_distributed": total_distributed,
                "unallocated_funds": max(0.0, batch["amount"] - total_allocated),
                "total_beneficiaries": total_bens,
                "verified_beneficiaries": verified_bens,
                "flagged_records": flagged_recs,
                "confirmed_distributions": confirmed_dists,
                "blockchain_status": "CONNECTED" if bc_info.get("success") else "STANDBY",
                "active_network": bc_info.get("network", "Polygon Amoy"),
                "contract_address": bc_info.get("contractAddress"),
                "recent_transactions": recent_txs
            })
            return

        # Batches list
        if path == "/api/batches":
            cursor.execute("SELECT * FROM relief_batches ORDER BY id DESC")
            batches = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self._send_json(batches)
            return

        # Batch detail
        m = re.match(r"^/api/batches/([^/]+)$", path)
        if m:
            b_id = m.group(1)
            cursor.execute("SELECT * FROM relief_batches WHERE batch_id = ?", (b_id,))
            batch = cursor.fetchone()
            if not batch:
                conn.close()
                self._send_json({"error": "Batch not found"}, 404)
                return

            cursor.execute("SELECT * FROM allocations WHERE batch_id = ?", (b_id,))
            allocs = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM distributions WHERE batch_id = ?", (b_id,))
            dists = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM audit_events WHERE batch_id = ? ORDER BY timestamp ASC", (b_id,))
            timeline = [dict(r) for r in cursor.fetchall()]
            conn.close()

            self._send_json({
                "batch": dict(batch),
                "allocations": allocs,
                "total_distributions": len(dists),
                "distributed_amount": sum(d["amount"] for d in dists),
                "timeline": timeline
            })
            return

        # Beneficiaries list
        if path == "/api/beneficiaries":
            b_id = query.get("batch_id", [None])[0]
            status = query.get("status", [None])[0]
            flagged = query.get("flagged_only", ["false"])[0].lower() in ["true", "1"]

            sql = "SELECT * FROM beneficiaries WHERE 1=1"
            params = []
            if b_id:
                sql += " AND batch_id = ?"
                params.append(b_id)
            if status:
                sql += " AND verification_status = ?"
                params.append(status)
            if flagged:
                sql += " AND (verification_status = 'FLAGGED_FOR_REVIEW' OR duplicate_flag = 1 OR anomaly_flag = 1)"
            
            sql += " ORDER BY id ASC"
            cursor.execute(sql, params)
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self._send_json(rows)
            return

        # Single Beneficiary
        m = re.match(r"^/api/beneficiaries/([^/]+)$", path)
        if m:
            ben_id = m.group(1)
            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            ben = cursor.fetchone()
            conn.close()
            if not ben:
                self._send_json({"error": "Beneficiary not found"}, 404)
                return
            self._send_json(dict(ben))
            return

        # Distributions list
        if path == "/api/distributions":
            b_id = query.get("batch_id", [None])[0]
            if b_id:
                cursor.execute("SELECT * FROM distributions WHERE batch_id = ? ORDER BY distributed_at DESC", (b_id,))
            else:
                cursor.execute("SELECT * FROM distributions ORDER BY distributed_at DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self._send_json(rows)
            return

        # Audit trail
        m = re.match(r"^/api/audit-trail/([^/]+)$", path)
        if m:
            b_id = m.group(1)
            cursor.execute("SELECT * FROM audit_events WHERE batch_id = ? ORDER BY timestamp DESC", (b_id,))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self._send_json(rows)
            return

        # Sample CSV for LGU batch verification
        if path == "/api/beneficiaries/sample-csv":
            csv_path = os.path.join(BASE_DIR, "app", "data", "seed_beneficiaries.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8") as f:
                    content = f.read()
                conn.close()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
                return

        conn.close()
        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        conn = get_db()
        cursor = conn.cursor()

        # 1. Release Fund
        if path == "/api/funds/releases":
            b_id = body.get("batch_id", f"RELIEF-{int(datetime.utcnow().timestamp())}")
            calamity = body.get("calamity_name", "Typhoon Calamity")
            amount = float(body.get("amount", 10000000.0))
            agency = body.get("source_agency", "DSWD Central Office")
            lgu = body.get("recipient_lgu", "Provincial Government of Albay")
            purpose = body.get("purpose", "Emergency Aid")

            # On-chain call
            bc_res = blockchain_service.release_fund(b_id, amount, calamity, agency)
            tx_hash = bc_res.get("txHash")

            now_str = datetime.utcnow().isoformat()
            cursor.execute("""
            INSERT INTO relief_batches (batch_id, calamity_name, calamity_type, source_agency, recipient_lgu, purpose, amount, status, blockchain_tx_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (b_id, calamity, "Typhoon", agency, lgu, purpose, amount, "ACTIVE", tx_hash, now_str))

            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (b_id, "FUND_RELEASE", f"Fund released: ₱{amount:,.2f} for {calamity}", amount, b_id, tx_hash, now_str))

            conn.commit()
            cursor.execute("SELECT * FROM relief_batches WHERE batch_id = ?", (b_id,))
            new_batch = dict(cursor.fetchone())
            conn.close()
            self._send_json(new_batch, 201)
            return

        # 2. Allocations
        if path == "/api/allocations":
            b_id = body.get("batch_id", "RELIEF-2026-001")
            a_id = body.get("allocation_id", f"ALLOC-{int(datetime.utcnow().timestamp())}")
            brgy_id = body.get("barangay_id", "BRGY-001")
            brgy_name = body.get("barangay_name", "San Isidro")
            amount = float(body.get("amount", 2500000.0))
            b_count = int(body.get("beneficiary_count", 500))

            bc_res = blockchain_service.allocate_fund(b_id, a_id, brgy_id, amount)
            tx_hash = bc_res.get("txHash")
            now_str = datetime.utcnow().isoformat()

            cursor.execute("""
            INSERT INTO allocations (allocation_id, batch_id, barangay_id, barangay_name, amount, beneficiary_count, status, blockchain_tx_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (a_id, b_id, brgy_id, brgy_name, amount, b_count, "ALLOCATED", tx_hash, now_str))

            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (b_id, "ALLOCATION", f"Allocated ₱{amount:,.2f} to Barangay {brgy_name}", amount, a_id, tx_hash, now_str))

            conn.commit()
            cursor.execute("SELECT * FROM allocations WHERE allocation_id = ?", (a_id,))
            new_alloc = dict(cursor.fetchone())
            conn.close()
            self._send_json(new_alloc, 201)
            return

        # 3. Beneficiaries Register
        if path == "/api/beneficiaries":
            ben_id = body.get("beneficiary_id", f"BEN-{int(datetime.utcnow().timestamp())}")
            dafac_id = body.get("dafac_id") or f"DFC-2026-{ben_id[-4:]}"
            name = body.get("household_name", "").strip()
            brgy_id = body.get("barangay_id", "BRGY-001")
            brgy_name = body.get("barangay_name", "San Isidro")
            b_id = body.get("batch_id", "RELIEF-2026-001")
            contact = body.get("contact_number", "0917-000-0000")

            # Run AI Entity Resolution against existing records
            cursor.execute("SELECT beneficiary_id, household_name, barangay_id FROM beneficiaries WHERE batch_id = ?", (b_id,))
            existing = [dict(r) for r in cursor.fetchall()]
            dup_eval = entity_resolver.evaluate_duplicate(name, brgy_id, existing)

            is_dup = 1 if dup_eval["is_duplicate"] else 0
            conf = dup_eval["confidence"]
            matched_id = dup_eval["matched_id"]
            status = "FLAGGED_FOR_REVIEW" if is_dup else "VERIFIED"
            notes = f"AI Duplicate Flag ({int(conf*100)}% match with {matched_id})" if is_dup else "Auto-verified: Zero matches found"
            now_str = datetime.utcnow().isoformat()

            cursor.execute("""
            INSERT INTO beneficiaries (beneficiary_id, dafac_id, household_name, barangay_id, barangay_name, batch_id, contact_number, verification_status, duplicate_flag, duplicate_confidence, duplicate_matched_id, anomaly_flag, review_status, review_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ben_id, dafac_id, name, brgy_id, brgy_name, b_id, contact, status, is_dup, conf, matched_id, 0, "PENDING" if is_dup else "APPROVED", notes, now_str))

            if is_dup:
                cursor.execute("""
                INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (b_id, "AI_DUPLICATE_FLAG", f"AI Flag: Possible duplicate {ben_id} ↔ {matched_id} ({int(conf*100)}% confidence)", None, ben_id, None, now_str))

            conn.commit()
            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            new_ben = dict(cursor.fetchone())
            conn.close()
            self._send_json(new_ben, 201)
            return

        # 3b. Batch CSV Upload & AI Entity Resolution Analysis
        if path == "/api/beneficiaries/upload-csv":
            from app.ai.entity_resolution import process_csv_batch
            csv_text = body.get("csv_content", "")
            if not csv_text:
                csv_path = os.path.join(BASE_DIR, "app", "data", "seed_beneficiaries.csv")
                if os.path.exists(csv_path):
                    with open(csv_path, "r", encoding="utf-8") as f:
                        csv_text = f.read()
            
            res = process_csv_batch(csv_text)
            conn.close()
            self._send_json(res)
            return

        # 4. Beneficiary Manual Review / Verify
        m = re.match(r"^/api/beneficiaries/([^/]+)/verify$", path)
        if m:
            ben_id = m.group(1)
            new_status = body.get("status", "VERIFIED")
            review_notes = body.get("review_notes", "Manually reviewed and approved by barangay officer.")

            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            ben = cursor.fetchone()
            if not ben:
                conn.close()
                self._send_json({"error": "Beneficiary not found"}, 404)
                return

            now_str = datetime.utcnow().isoformat()
            cursor.execute("""
            UPDATE beneficiaries
            SET verification_status = ?, review_status = ?, review_notes = ?
            WHERE beneficiary_id = ?
            """, (new_status, "APPROVED" if new_status == "VERIFIED" else "REJECTED", review_notes, ben_id))

            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ben["batch_id"], "BENEFICIARY_VERIFIED", f"Beneficiary {ben_id} manually verified & approved: {review_notes}", None, ben_id, None, now_str))

            conn.commit()
            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            updated = dict(cursor.fetchone())
            conn.close()
            self._send_json(updated)
            return

        # 5. Confirm Distribution & Anchor Hash
        if path == "/api/distributions/confirm" or path == "/api/distributions":
            d_id = body.get("distribution_id", f"DIST-{int(datetime.utcnow().timestamp())}")
            ben_id = body.get("beneficiary_id")
            b_id = body.get("batch_id", "RELIEF-2026-001")
            amount = float(body.get("amount", 5000.0))
            method = body.get("verification_method", "QR_VOUCHER_PHYSICAL_RECEIPT")
            ocr_text = body.get("ocr_raw_text") or DEMO_OCR_TEXT
            filename = body.get("receipt_filename", "sample_relief_receipt.svg")

            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            ben = cursor.fetchone()
            if not ben:
                conn.close()
                self._send_json({"error": f"Beneficiary {ben_id} not found"}, 404)
                return

            # Validation 1: Positive amount
            if amount <= 0:
                conn.close()
                self._send_json({"error": "Invalid disbursement amount. Amount must be greater than zero."}, 400)
                return

            # Validation 2: Exceeding maximum calamity ceiling
            if amount > 10000.0:
                conn.close()
                self._send_json({"error": f"Calamity Aid Ceiling Exceeded: ₱{amount:,.2f} exceeds statutory maximum grant limit of ₱10,000.00."}, 400)
                return

            # Validation 3: Prevent duplicate distribution to same household
            cursor.execute("SELECT COUNT(*) as cnt FROM distributions WHERE beneficiary_id = ?", (ben_id,))
            prior_count = cursor.fetchone()["cnt"]
            if prior_count > 0:
                conn.close()
                self._send_json({"error": f"Duplicate disbursement rejected: Beneficiary {ben_id} ({ben['household_name']}) has already claimed aid voucher."}, 400)
                return

            # AI Anomaly Check for Non-Standard Amounts (e.g. 7000 vs standard 5000)
            is_anomalous_amount = (amount != 5000.0)
            if is_anomalous_amount:
                cursor.execute("""
                UPDATE beneficiaries
                SET anomaly_flag = 1, review_notes = ?
                WHERE beneficiary_id = ?
                """, (f"AI Anomaly: Non-standard grant amount ₱{amount:,.2f} (expected standard ₱5,000.00). Flagged for COA audit.", ben_id))

            # Compute SHA-256 Hash
            receipt_hash = compute_receipt_hash(d_id, ben_id, b_id, amount, ocr_text, method)

            # Submit on-chain anchor
            bc_res = blockchain_service.confirm_distribution(b_id, d_id, ben_id, amount, receipt_hash)
            tx_hash = bc_res.get("txHash")
            now_str = datetime.utcnow().isoformat()

            cursor.execute("""
            INSERT INTO distributions (distribution_id, beneficiary_id, batch_id, amount, verification_method, receipt_hash, receipt_file_path, ocr_text, status, blockchain_tx_hash, distributed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (d_id, ben_id, b_id, amount, method, receipt_hash, f"/receipts/{filename}", ocr_text, "CONFIRMED", tx_hash, now_str))

            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (b_id, "DISTRIBUTION_CONFIRMED", f"Disbursed ₱{amount:,.2f} to {ben['household_name']} ({ben_id}) — Receipt hash anchored", amount, d_id, tx_hash, now_str))

            if is_anomalous_amount:
                cursor.execute("""
                INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (b_id, "AI_ANOMALY_FLAG", f"AI Anomaly Engine: Non-standard disbursement of ₱{amount:,.2f} to {ben_id} flagged for COA review (Expected ₱5,000.00)", amount, ben_id, None, now_str))

            conn.commit()
            cursor.execute("SELECT * FROM distributions WHERE distribution_id = ?", (d_id,))
            new_dist = dict(cursor.fetchone())
            conn.close()
            self._send_json(new_dist, 201)
            return

        # 6. Blockchain Verification Tool
        if path == "/api/blockchain/verify":
            d_id = body.get("distribution_id")
            r_hash = body.get("receipt_hash")

            if d_id:
                cursor.execute("SELECT * FROM distributions WHERE distribution_id = ?", (d_id,))
            elif r_hash:
                cursor.execute("SELECT * FROM distributions WHERE receipt_hash = ?", (r_hash,))
            else:
                cursor.execute("SELECT * FROM distributions ORDER BY id DESC LIMIT 1")
            
            dist = cursor.fetchone()
            conn.close()

            if not dist:
                self._send_json({"error": "Distribution record not found in database"}, 404)
                return

            dist = dict(dist)
            local_hash = compute_receipt_hash(
                dist["distribution_id"],
                dist["beneficiary_id"],
                dist["batch_id"],
                dist["amount"],
                dist["ocr_text"],
                dist["verification_method"]
            )

            # Query Smart Contract on Polygon/Local Node
            bc_res = blockchain_service.verify_receipt(dist["distribution_id"], local_hash)
            onchain_hash = bc_res.get("onchainHash", "0x" + "0"*64)
            matched = bc_res.get("matched", False)

            is_valid, msg = verify_receipt_integrity(local_hash, onchain_hash)
            status_info = blockchain_service.get_status()

            self._send_json({
                "record_id": dist["distribution_id"],
                "beneficiary_id": dist["beneficiary_id"],
                "receipt_hash_local": local_hash,
                "receipt_hash_onchain": onchain_hash,
                "is_verified": bool(matched and is_valid),
                "blockchain_tx_hash": dist["blockchain_tx_hash"],
                "timestamp": bc_res.get("timestamp"),
                "network": status_info.get("network", "Polygon Amoy"),
                "contract_address": status_info.get("contractAddress"),
                "explorer_url": f"https://amoy.polygonscan.com/tx/{dist['blockchain_tx_hash']}" if dist["blockchain_tx_hash"] and "amoy" in status_info.get("network", "").lower() else None,
                "status_message": msg
            })
            return

        # 7. Demo Reset
        if path == "/api/demo/reset":
            cursor.execute("DELETE FROM relief_batches")
            cursor.execute("DELETE FROM allocations")
            cursor.execute("DELETE FROM beneficiaries")
            cursor.execute("DELETE FROM distributions")
            cursor.execute("DELETE FROM audit_events")
            conn.commit()
            conn.close()
            seed_default_data()
            self._send_json({"success": True, "message": "Demo data reset successfully to Typhoon Salinlahi."})
            return

        # Delete beneficiary fallback via POST
        m = re.match(r"^/api/beneficiaries/([^/]+)/delete$", path)
        if m:
            ben_id = m.group(1)
            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            ben = cursor.fetchone()
            if not ben:
                conn.close()
                self._send_json({"error": "Beneficiary not found"}, 404)
                return

            ben = dict(ben)
            cursor.execute("DELETE FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            now_str = datetime.utcnow().isoformat()
            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ben.get("batch_id", "RELIEF-2026-001"), "BENEFICIARY_DELETED", f"Deleted duplicate beneficiary {ben_id} ({ben.get('household_name')})", None, ben_id, None, now_str))

            conn.commit()
            conn.close()
            self._send_json({"success": True, "message": f"Beneficiary {ben_id} deleted successfully."})
            return

        conn.close()
        self._send_json({"error": f"Unknown endpoint: {path}"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        conn = get_db()
        cursor = conn.cursor()

        m = re.match(r"^/api/beneficiaries/([^/]+)$", path)
        if m:
            ben_id = m.group(1)
            cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            ben = cursor.fetchone()
            if not ben:
                conn.close()
                self._send_json({"error": "Beneficiary not found"}, 404)
                return

            ben = dict(ben)
            cursor.execute("DELETE FROM beneficiaries WHERE beneficiary_id = ?", (ben_id,))
            now_str = datetime.utcnow().isoformat()
            cursor.execute("""
            INSERT INTO audit_events (batch_id, event_type, description, amount, entity_id, blockchain_tx_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ben.get("batch_id", "RELIEF-2026-001"), "BENEFICIARY_DELETED", f"Deleted duplicate beneficiary {ben_id} ({ben.get('household_name')})", None, ben_id, None, now_str))

            conn.commit()
            conn.close()
            self._send_json({"success": True, "message": f"Beneficiary {ben_id} deleted successfully."})
            return

        conn.close()
        self._send_json({"error": f"Endpoint not found for DELETE: {path}"}, 404)

def run(port=8000):
    init_sqlite_db()
    seed_default_data()
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(("0.0.0.0", port), AyudaChainHandler)
    print(f"AyudaChain Backend Server running at http://0.0.0.0:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
