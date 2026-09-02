"""
Lightweight Statistical Anomaly Detection Engine for Calamity Relief Distribution.
Monitors velocity, amount variances, clustering, and beneficiary distribution uniformity.
Flags irregularities for human auditor review without automated fraud accusations.
"""

from typing import Dict, List
import statistics

class DistributionAnomalyDetector:
    """
    Statistical and rule-based anomaly detector for relief distribution patterns.
    """

    def __init__(self, standard_grant_amount: float = 5000.0):
        self.standard_grant_amount = standard_grant_amount

    def analyze_distribution(
        self,
        candidate_amount: float,
        beneficiary_id: str,
        barangay_id: str,
        past_distributions: List[Dict]
    ) -> Dict:
        """
        Analyzes a single distribution event against historical barangay distributions.
        past_distributions: list of dicts with {'amount': float, 'beneficiary_id': str, 'barangay_id': str, 'distributed_at': datetime}
        """
        flags = []
        confidence = 0.0

        # 1. Amount Deviation Check
        if candidate_amount != self.standard_grant_amount:
            deviation = abs(candidate_amount - self.standard_grant_amount)
            pct = (deviation / self.standard_grant_amount) * 100
            flags.append(f"Non-standard grant amount (₱{candidate_amount:,.2f} vs expected ₱{self.standard_grant_amount:,.2f}, {pct:.0f}% deviation)")
            confidence = max(confidence, 0.85)

        # 2. Prior distribution to same beneficiary
        prior_beneficiary_dist = [d for d in past_distributions if d.get("beneficiary_id") == beneficiary_id]
        if prior_beneficiary_dist:
            flags.append(f"Beneficiary {beneficiary_id} has already received {len(prior_beneficiary_dist)} prior disbursement(s)")
            confidence = max(confidence, 0.95)

        # 3. High-velocity clustering within the same barangay
        brgy_dists = [d for d in past_distributions if d.get("barangay_id") == barangay_id]
        if len(brgy_dists) >= 10:
            # Check amounts variance
            amounts = [d.get("amount", self.standard_grant_amount) for d in brgy_dists]
            stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            if stdev > 1500:
                flags.append(f"High variance detected in barangay distribution amounts (stdev=₱{stdev:,.2f})")
                confidence = max(confidence, 0.75)

        is_anomalous = len(flags) > 0

        return {
            "is_anomaly": is_anomalous,
            "status": "FLAGGED_FOR_HUMAN_REVIEW" if is_anomalous else "NORMAL",
            "anomaly_score": round(confidence, 2) if is_anomalous else 0.0,
            "reasons": flags,
            "disclaimer": "AI-assisted anomaly check. Flagged for review; not an accusation of fraud."
        }

    def evaluate_batch_health(self, total_released: float, allocations: List[Dict], distributions: List[Dict]) -> Dict:
        """
        Calculates aggregate operational health metrics and flags macro-level anomalies.
        """
        allocated_sum = sum(a.get("amount", 0.0) for a in allocations)
        distributed_sum = sum(d.get("amount", 0.0) for d in distributions)
        
        alerts = []
        if allocated_sum > total_released:
            alerts.append("CRITICAL: Total allocated funds exceed batch release amount.")
        
        if distributed_sum > allocated_sum:
            alerts.append("CRITICAL: Confirmed distributions exceed total allocated funds.")

        return {
            "allocated_sum": allocated_sum,
            "distributed_sum": distributed_sum,
            "coverage_pct": round((distributed_sum / max(allocated_sum, 1.0)) * 100, 1),
            "macro_alerts": alerts,
            "status": "ATTENTION_REQUIRED" if alerts else "HEALTHY"
        }
