"""
AI Entity Resolution & Duplicate Beneficiary Detection Engine.
Deterministic, fuzzy matching for Philippine names and household identities.
Flags potential duplicates for human review without automated denial.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

PHILIPPINE_ABBREVIATIONS = {
    "ma": "maria",
    "ma.": "maria",
    "jr": "junior",
    "jr.": "junior",
    "sr": "senior",
    "sr.": "senior",
    "ii": "two",
    "iii": "three",
    "iv": "four",
    "d": "dela",
    "d.": "dela",
    "del": "dela",
    "sta": "santa",
    "sta.": "santa",
    "sto": "santo",
    "sto.": "santo",
    "san": "san",
}

def normalize_name(name: str) -> str:
    """
    Normalizes a name string:
    - Lowercase
    - Unicode NFKD normalization (strip accents)
    - Strip punctuation and commas
    - Expand common Filipino abbreviations
    - Sort name tokens to handle "Last, First" vs "First Last"
    """
    if not name:
        return ""
    
    # Unicode normalize
    name = unicodedata.normalize('NFKD', name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()

    # Handle "Last, First Middle" -> tokens
    # Replace punctuation with spaces
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    tokens = [t.strip() for t in name.split() if t.strip()]

    # Normalize abbreviations
    normalized_tokens = [PHILIPPINE_ABBREVIATIONS.get(t, t) for t in tokens]
    
    return " ".join(normalized_tokens)

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def token_similarity(name1: str, name2: str) -> float:
    """
    Token-set Jaccard + Levenshtein hybrid similarity score [0.0 - 1.0].
    """
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 1.0

    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())

    # Token overlap (Jaccard)
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / max(len(union), 1)

    # Token-sort Levenshtein similarity (matches fuzz.token_sort_ratio)
    s_norm1 = " ".join(sorted(norm1.split()))
    s_norm2 = " ".join(sorted(norm2.split()))
    s_max_len = max(len(s_norm1), len(s_norm2))
    s_dist = levenshtein_distance(s_norm1, s_norm2)
    token_sort_sim = 1.0 - (s_dist / s_max_len)

    # Raw string edit similarity
    max_len = max(len(norm1), len(norm2))
    dist = levenshtein_distance(norm1, norm2)
    edit_sim = 1.0 - (dist / max_len)

    # Best of token sort similarity or hybrid
    score = max(token_sort_sim, (0.5 * jaccard) + (0.5 * edit_sim))

    # Bonus: if all tokens of one are in the other (e.g. "Juan Dela Cruz" vs "Juan Cruz")
    if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
        score = max(score, 0.88)

    return round(min(max(score, 0.0), 1.0), 4)

class EntityResolutionEngine:
    """
    Engine for scanning existing beneficiary records to detect possible duplicates.
    """

    def __init__(self, confidence_threshold: float = 0.78):
        self.confidence_threshold = confidence_threshold

    def evaluate_duplicate(
        self,
        candidate_name: str,
        candidate_barangay: str,
        existing_records: List[Dict]
    ) -> Dict:
        """
        Compares candidate against a list of existing records:
        [{'beneficiary_id': 'BEN-0001', 'household_name': '...', 'barangay_id': '...'}]

        Returns:
            {
                "is_duplicate": bool,
                "confidence": float,
                "matched_id": Optional[str],
                "matched_name": Optional[str],
                "similarity_reasons": List[str],
                "status": "NORMAL" | "FLAGGED_FOR_HUMAN_REVIEW"
            }
        """
        best_match = None
        best_score = 0.0
        best_reasons = []

        for record in existing_records:
            rec_id = record.get("beneficiary_id")
            rec_name = record.get("household_name", "")
            rec_brgy = record.get("barangay_id", "")

            sim = token_similarity(candidate_name, rec_name)
            reasons = []

            # Check if same barangay
            same_barangay = (candidate_barangay == rec_brgy) and bool(candidate_barangay)
            if same_barangay:
                # Boost confidence slightly if same locality
                effective_score = min(sim * 1.08, 1.0)
                reasons.append("Identical Barangay locality match")
            else:
                effective_score = sim

            if effective_score > best_score:
                best_score = effective_score
                best_match = record
                if sim >= 0.90:
                    reasons.append(f"High fuzzy name match ({int(sim*100)}%) with {rec_name}")
                elif sim >= self.confidence_threshold:
                    reasons.append(f"Moderate name variation ({int(sim*100)}%) with {rec_name}")
                best_reasons = reasons

        is_dup = best_score >= self.confidence_threshold

        return {
            "is_duplicate": is_dup,
            "confidence": round(best_score, 2),
            "matched_id": best_match.get("beneficiary_id") if (is_dup and best_match) else None,
            "matched_name": best_match.get("household_name") if (is_dup and best_match) else None,
            "similarity_reasons": best_reasons if is_dup else [],
            "status": "FLAGGED_FOR_HUMAN_REVIEW" if is_dup else "NORMAL",
            "disclaimer": "AI-assisted flag for human review only. Does not deny beneficiary aid."
        }

def process_csv_batch(csv_text: str) -> dict:
    """
    Parses CSV of beneficiaries (e.g. seed_beneficiaries.csv) and runs pairwise
    fuzzy entity resolution. Matches Section 3 of Hackathon architecture plan.
    """
    import csv, io, itertools
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    flagged_records = []
    
    for row1, row2 in itertools.combinations(rows, 2):
        name1 = f"{row1.get('first_name', '')} {row1.get('last_name', '')}".strip() or row1.get('household_name', '')
        name2 = f"{row2.get('first_name', '')} {row2.get('last_name', '')}".strip() or row2.get('household_name', '')
        
        name_score = int(token_similarity(name1, name2) * 100)
        
        addr1 = f"{row1.get('address_street', '')} {row1.get('barangay', '')} {row1.get('city', '')}".strip()
        addr2 = f"{row2.get('address_street', '')} {row2.get('barangay', '')} {row2.get('city', '')}".strip()
        addr_score = int(token_similarity(addr1, addr2) * 100) if (addr1 and addr2) else 50
        
        dafac1 = row1.get('dafac_id', '')
        dafac2 = row2.get('dafac_id', '')
        dafac_match = bool(dafac1 and dafac2 and dafac1.strip().upper() == dafac2.strip().upper())
        
        overall_score = (name_score * 0.6) + (addr_score * 0.4)
        if dafac_match and overall_score > 60:
            overall_score = max(overall_score, 95.0)
            
        anomaly_type = "Potential Duplicate"
        if dafac_match and name_score < 95:
            anomaly_type = "Clerical Typo / Formatting Variation"
        elif " " in name1 and " " in name2 and sorted(name1.lower().split()) == sorted(name2.lower().split()):
            anomaly_type = "Swapped First/Last Name Fields"
        elif dafac1 != dafac2 and row1.get('barangay') != row2.get('barangay') and name_score >= 85:
            anomaly_type = "Cross-Barangay Duplicate Claim"
        elif name_score >= 95:
            anomaly_type = "Exact Duplicate Record"

        if overall_score >= 80:
            flagged_records.append({
                "record_a": {
                    "id": row1.get('beneficiary_id', ''),
                    "name": name1.title(),
                    "address": addr1.title(),
                    "barangay": row1.get('barangay', ''),
                    "dafac_id": dafac1
                },
                "record_b": {
                    "id": row2.get('beneficiary_id', ''),
                    "name": name2.title(),
                    "address": addr2.title(),
                    "barangay": row2.get('barangay', ''),
                    "dafac_id": dafac2
                },
                "anomaly_type": anomaly_type,
                "match_metrics": {
                    "overall_score": round(overall_score, 1),
                    "name_score": name_score,
                    "address_score": addr_score,
                    "dafac_match": dafac_match
                },
                "requires_human_review": True
            })
            
    return {
        "status": "success",
        "total_records_processed": len(rows),
        "flagged_duplicates_count": len(flagged_records),
        "flagged_records": flagged_records
    }

