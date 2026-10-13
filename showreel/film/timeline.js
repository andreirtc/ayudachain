// Shared cue sheet for picture (scenes.js) and sound (score.mjs).
// 120 BPM: one beat is 0.5s, one bar is 2s. Every cut lands on a bar.
window.CUES = {
  fps: 60,
  duration: 66,
  open: 0,          // cold open on navy
  count: 1.6,       // funding figure counts up
  disperse: 3.8,    // figure breaks into a network
  questions: [5, 6, 7],
  logo: 8,          // mark impact
  directory: 12,    // real directory screen
  roles: [14, 14.5, 15, 15.5, 16], // five workspaces eject
  trail: [18, 22, 26, 30, 35],     // five stations of the assistance journey
  concept: 40,      // off-chain record, on-chain digest
  scan: 42.2,
  send: 43.8,
  stamp: 44.8,
  tamper: 48,
  edit: 48.9,
  compare: 50.4,
  mismatch: 51,
  unreachable: 52,
  powerDown: 52.4,
  unreachableChip: 53.6,
  restore: 56,
  click: 57,
  verified: 58,
  end: 60,
  fade: 65,
};

// Real SHA-256 digests of the illustrative payload shown on the record card.
// render.mjs recomputes both with node:crypto and refuses to render if they differ.
window.RECORD = {
  payload: '{"amount_centavos":495000,"days":15,"household":"DFC-2026-33757601","rounded_daily_centavos":33000,"state":"handed_over"}',
  digest: '88ed6fe8de17a62f34eb963084d545ec89c37291231b0c444ba46f2aacffed51',
  alteredPayload: '{"amount_centavos":945000,"days":15,"household":"DFC-2026-33757601","rounded_daily_centavos":33000,"state":"handed_over"}',
  alteredDigest: '8194516ec89821df727522ffcb5a471b1b0a7d2775e03a86d8ccffc1a57b7243',
};
