# Connected receipt details

Bounded frontend follow-up to [PR #22](https://github.com/andreirtc/ayudachain/pull/22). A shared `ReceiptDetails` component presents the exact payout in the payout preview and selected verification view. It reads existing API fields; no receipts, hashes or identity evidence are fabricated.

Authorized readers see the current household label, amount, recorded time, batch and receipt reference. The UI states that registry labels can change and that a receipt check does not establish identity or cash delivery. Office readers may expand the protected saved image and extracted text. The shared SVG is explicitly labeled as a demo template that can contain another fictional household's details. Scoped accounts continue to receive no shared image/OCR, and public viewers receive reference-only representations.

Images have loading, failure and retry feedback. An image failure preserves the reference and hash context. Hashes and stored transaction references are expandable and are not presented as a current proof result. The payout preview uses a native modal with initial focus, Tab/Shift+Tab wrapping, Escape and return focus; its heading/close control stays visible while scrolling.

Existing exact receipt navigation and not-found behavior remain intact. This task does not implement household-specific uploads, generated identity snapshots or a new receipt protocol. Verification outcome presentation is the next bounded PR.

Validation on 2026-10-13: all 40 isolated Edge desktop/phone cases passed. The six receipt cases were rerun successfully after simplifying the final limitation wording. Tests use the actual API, protected file endpoint and authenticated roles, covering exact-record links, dialog focus, an aborted image request followed by a real successful retry, public file denial and beneficiary denial of another household's receipt. Independent TypeScript, production build and diff checks passed. Desktop and phone screenshots were inspected. Chain unavailability in the ordinary browser fixture is stated explicitly.
