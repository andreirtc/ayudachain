"""
Generates fictional official disaster relief voucher receipts for the demo.
Creates both the SVG/image representation and canonical OCR extracted text.
"""

import os
from datetime import datetime

DEMO_OCR_TEXT = """REPUBLIC OF THE PHILIPPINES
DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT
TYPHOON SALINLAHI EMERGENCY ASSISTANCE (2026)
--------------------------------------------------
OFFICIAL RELIEF DISBURSEMENT ACKNOWLEDGEMENT RECEIPT
BATCH REFERENCE      : RELIEF-2026-001
DISTRIBUTION ID      : DIST-0001
BENEFICIARY ID       : BEN-0001
HOUSEHOLD HEAD       : JUAN DELA CRUZ
MUNICIPALITY / LGU   : ALBAY DISASTER RESPONSE CENTER
BARANGAY             : SAN ISIDRO
DISBURSEMENT TYPE    : EMERGENCY CASH & RELIEF PACK (ECRP)
GRANT AMOUNT         : PHP 5,000.00
VERIFICATION METHOD  : QR VOUCHER & BIOMETRIC CONFIRMATION
STATUS               : CLAIMED & CONFIRMED
DISBURSING OFFICER   : MARIA SANTOS, DSWD FIELD OFFICER #4412
ISSUED TIMESTAMP     : 2026-09-01 09:41:22 UTC
--------------------------------------------------
INTEGRITY NOTICE:
This digital record is protected under AyudaChain.
Any alteration to name, amount, or reference will invalidate the cryptographic blockchain proof.
"""

def generate_svg_receipt(
    distribution_id: str,
    beneficiary_id: str,
    household_name: str,
    barangay_name: str,
    amount: float,
    batch_id: str = "RELIEF-2026-001"
) -> str:
    """Returns SVG markup for a high-fidelity Philippine relief receipt."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800" width="600" height="800">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Background Canvas -->
  <rect width="600" height="800" fill="#f8fafc" rx="16"/>
  <rect x="20" y="20" width="560" height="760" fill="#ffffff" rx="12" stroke="#e2e8f0" stroke-width="2" filter="url(#cardShadow)"/>

  <!-- Official Header Banner -->
  <path d="M 20 32 Q 20 20 32 20 L 568 20 Q 580 20 580 32 L 580 130 L 20 130 Z" fill="url(#headerGrad)" />
  
  <text x="300" y="55" fill="#fef08a" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="2">REPUBLIC OF THE PHILIPPINES</text>
  <text x="300" y="78" fill="#ffffff" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">DEPARTMENT OF SOCIAL WELFARE &amp; DEVELOPMENT</text>
  <text x="300" y="102" fill="#93c5fd" font-family="system-ui, sans-serif" font-size="13" font-weight="600" text-anchor="middle">TYPHOON SALINLAHI EMERGENCY AID VOUCHER</text>

  <!-- Document Title -->
  <rect x="140" y="150" width="320" height="32" fill="#f1f5f9" rx="16" stroke="#cbd5e1" stroke-width="1"/>
  <text x="300" y="171" fill="#334155" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1">OFFICIAL DISBURSEMENT RECEIPT</text>

  <!-- Key Value Grid -->
  <!-- Batch ID -->
  <text x="60" y="225" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">BATCH REFERENCE</text>
  <text x="60" y="248" fill="#0f172a" font-family="monospace" font-size="15" font-weight="700">{batch_id}</text>

  <!-- Distribution ID -->
  <text x="320" y="225" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">DISTRIBUTION ID</text>
  <text x="320" y="248" fill="#0f172a" font-family="monospace" font-size="15" font-weight="700">{distribution_id}</text>

  <line x1="60" y1="270" x2="540" y2="270" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4 4"/>

  <!-- Beneficiary Info -->
  <text x="60" y="305" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">BENEFICIARY ID</text>
  <text x="60" y="328" fill="#0f172a" font-family="monospace" font-size="14" font-weight="700">{beneficiary_id}</text>

  <text x="320" y="305" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">HOUSEHOLD HEAD</text>
  <text x="320" y="328" fill="#0f172a" font-family="system-ui, sans-serif" font-size="15" font-weight="700">{household_name}</text>

  <!-- Barangay & LGU -->
  <text x="60" y="375" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">BARANGAY LOCALITY</text>
  <text x="60" y="398" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="600">{barangay_name}</text>

  <text x="320" y="375" fill="#64748b" font-family="system-ui, sans-serif" font-size="12">RECIPIENT LGU</text>
  <text x="320" y="398" fill="#0f172a" font-family="system-ui, sans-serif" font-size="14" font-weight="600">Province of Albay</text>

  <line x1="60" y1="430" x2="540" y2="430" stroke="#e2e8f0" stroke-width="1"/>

  <!-- Amount Highlight Card -->
  <rect x="60" y="450" width="480" height="90" fill="#ecfdf5" rx="10" stroke="#a7f3d0" stroke-width="1.5"/>
  <text x="90" y="485" fill="#065f46" font-family="system-ui, sans-serif" font-size="12" font-weight="700">CONFIRMED AID DISBURSEMENT AMOUNT</text>
  <text x="90" y="525" fill="#047857" font-family="system-ui, sans-serif" font-size="32" font-weight="900">₱{amount:,.2f}</text>
  <text x="400" y="515" fill="#059669" font-family="system-ui, sans-serif" font-size="13" font-weight="700">✓ CLAIMED</text>

  <!-- Simulated QR Code -->
  <g transform="translate(60, 565)">
    <rect width="110" height="110" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="6"/>
    <!-- Simulated QR Finder Patterns -->
    <rect x="10" y="10" width="28" height="28" fill="#0f172a" rx="3"/>
    <rect x="15" y="15" width="18" height="18" fill="#ffffff" rx="2"/>
    <rect x="19" y="19" width="10" height="10" fill="#0f172a"/>
    
    <rect x="72" y="10" width="28" height="28" fill="#0f172a" rx="3"/>
    <rect x="77" y="15" width="18" height="18" fill="#ffffff" rx="2"/>
    <rect x="81" y="19" width="10" height="10" fill="#0f172a"/>
    
    <rect x="10" y="72" width="28" height="28" fill="#0f172a" rx="3"/>
    <rect x="15" y="77" width="18" height="18" fill="#ffffff" rx="2"/>
    <rect x="19" y="81" width="10" height="10" fill="#0f172a"/>
    
    <!-- Dots -->
    <rect x="45" y="15" width="6" height="6" fill="#0f172a"/>
    <rect x="55" y="25" width="6" height="6" fill="#0f172a"/>
    <rect x="45" y="45" width="16" height="16" fill="#0f172a" rx="2"/>
    <rect x="72" y="55" width="8" height="8" fill="#0f172a"/>
    <rect x="85" y="75" width="12" height="12" fill="#0f172a"/>
    <rect x="50" y="75" width="8" height="8" fill="#0f172a"/>
    <rect x="25" y="50" width="8" height="8" fill="#0f172a"/>
  </g>

  <!-- Blockchain Seal and Disclaimer -->
  <text x="190" y="590" fill="#0f172a" font-family="system-ui, sans-serif" font-size="13" font-weight="700">AYUDACHAIN DIGITAL INTEGRITY SEAL</text>
  <text x="190" y="612" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Off-chain canonical document hash is anchored on Polygon.</text>
  <text x="190" y="630" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Verify on-chain via AyudaChain Public Transparency Portal.</text>
  <text x="190" y="655" fill="#2563eb" font-family="monospace" font-size="11" font-weight="600">Proof: SHA-256 Digest Anchored</text>

  <!-- Footer -->
  <line x1="60" y1="700" x2="540" y2="700" stroke="#e2e8f0" stroke-width="1"/>
  <text x="300" y="730" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" text-anchor="middle">FICTIONAL DEMONSTRATION RECORD — TYPHOON SALINLAHI CALAMITY RELIEF</text>
</svg>"""

def save_sample_receipt(output_dir: str):
    """Generates the primary sample receipt SVG file for the demo."""
    os.makedirs(output_dir, exist_ok=True)
    svg_path = os.path.join(output_dir, "sample_relief_receipt.svg")
    svg_content = generate_svg_receipt(
        distribution_id="DIST-0001",
        beneficiary_id="BEN-0001",
        household_name="JUAN DELA CRUZ",
        barangay_name="San Isidro",
        amount=5000.0,
        batch_id="RELIEF-2026-001"
    )
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return svg_path
