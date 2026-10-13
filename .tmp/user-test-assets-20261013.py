"""Create synthetic upload files only; never seed or reset business records."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.scripts.synthetic_evidence import synthetic_pdf, synthetic_portrait

directory = ROOT / '.runtime/user-tests/2026-10-13'
directory.mkdir(parents=True, exist_ok=True)
samples = {
    '01-fund-release.pdf': 'SYNTHETIC USER TEST - NOT AN ACTUAL RELEASE\nReference: DFC-2026-7313\nInvented Relief Office\nAmount: PHP 100,000.00\nAmount in words: ONE HUNDRED THOUSAND PESOS\nPrinted signatory: Invented Ana Verde',
    '02-intake-basis.pdf': 'SYNTHETIC USER TEST - NOT AN OFFICIAL ORDER\nReference: DFC-2026-7313\nSelected synthetic barangay\nResponse duration: 48 hours\nPrinted signatory: Invented Ana Verde',
    '03-invented-id.pdf': 'SYNTHETIC ID FOR TESTING ONLY - NOT A VALID GOVERNMENT ID\nIdentifier: DFC-2026-7313\nInvented Maya Luntian\nAddress: 13 Invented Lane, Invented Silong\nUse the separate invented portrait as photo original.',
    '04-damage-evidence.pdf': 'SYNTHETIC USER TEST DAMAGE EVIDENCE\nHousehold identifier: DFC-2026-7313\nInvented Maya Luntian\nDamage category: Totally damaged\nThis document does not prove actual damage.',
    '05-council-resolution.pdf': 'SYNTHETIC USER TEST RESOLUTION - NOT AN OFFICIAL ENDORSEMENT\nHousehold identifier: DFC-2026-7313\nInvented Maya Luntian\nIndependent officers record their own test responses.\nPrinted signatory: Invented Punong Silong',
    '06-wage-basis.pdf': 'SYNTHETIC USER TEST WAGE BASIS - NOT AN OFFICIAL RATE\nReference: DFC-2026-7313\nDaily wage: PHP 435.00\nAmount in words: FOUR HUNDRED THIRTY FIVE PESOS',
    '07-category-days.pdf': 'SYNTHETIC USER TEST CATEGORY BASIS - NOT AN OFFICIAL POLICY\nReference: DFC-2026-7313\nDamage category: Totally damaged\nCategory days: 15',
}
for name, content in samples.items():
    with (directory / name).open('xb') as stream:
        stream.write(synthetic_pdf(content))
with (directory / '08-invented-portrait.png').open('xb') as stream:
    stream.write(synthetic_portrait())
print('Created 8 synthetic upload files; no business records or chain state changed.')
