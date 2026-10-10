// Storyboard for presentation.mp4. Edit captions and durations here, then run:
//   npm run render
// Every label, screen name, person and identifier on a mockup screen comes from
// ../index.html through extract-screens.mjs. Only the captions, the "today" beat and
// the short handoff labels below are written here.
//
// Screen beats use the mockup's scenario 1, "From funding to full receipt".
// `steps` are the mockup's guided step numbers (1-based): the screen is shown as the
// mockup renders it at the first step, the role's own button is pressed, and the
// screen changes to how the mockup renders it at the next step.
globalThis.STORYBOARD = {
  fps: 30,
  scenario: "normal",
  record: { id: "DFC-2026-0101", name: "Lina Mercado" },
  labels: {
    mockup: "Redesign mockup",
    mockupNote: "not working software",
    simulated: "Simulated demo data",
    simulatedNote: "no chain was read",
  },
  sections: [
    { id: "map", label: "The map" },
    { id: "role", label: "One role" },
    { id: "payout", label: "One payout" },
    { id: "path", label: "The path" },
  ],
  // Source: docs/product/sitemap.md (the product as built). Contrast only.
  today: {
    tag: "Current product, as built",
    roles: ["Public Citizen", "Barangay Officer", "Auditor / COA"],
    pages: [
      ["/", "Dashboard"],
      ["/batch/[id]", "Relief batch"],
      ["/beneficiaries", "Beneficiaries"],
      ["/distributions", "Distributions"],
      ["/verify", "Verify"],
    ],
    note: "No login page. No route guards.",
  },
  // What happens before the software, in the real procedure. Context only: none of these steps is
  // an AyudaChain screen. Source: DSWD Memorandum Circular No. 24, s. 2025 (amending MC No. 11,
  // s. 2025): triggers for activation, funding requirements, and implementation procedures.
  lead: {
    tag: "Before AyudaChain: the real procedure",
    outside: "OUTSIDE THE SOFTWARE",
    inside: "IN AYUDACHAIN",
    steps: [
      ["State of calamity", "is declared for the area"],
      ["Barangay or LGU", "sends a request and a project proposal"],
      ["DSWD Field Office", "validates it; the Secretary activates cash aid"],
      ["Central Office", "releases funds to the Field Office"],
    ],
    enter: ["DSWD Officer", "records the release document"],
    source: "Source: DSWD Memorandum Circular No. 24, series of 2025",
  },
  beats: [
    // ---- Section 1: the problem and the map ----
    { id: "problem", section: "map", kind: "title", dur: 7.5,
      caption: "Disaster cash aid passes through many hands. Each handoff should leave a record." },
    { id: "today", section: "map", kind: "today", dur: 7.5,
      caption: "Today: five pages, three roles, and every page is open to everyone." },
    { id: "map-dswd", section: "map", kind: "map", role: "dswd", dur: 6.0,
      caption: "DSWD Officer: records funds, decides claims, runs payout sessions." },
    { id: "map-barangay", section: "map", kind: "map", role: "barangay", dur: 6.7,
      caption: "Barangay Officer: vouches that a household lives here and was affected." },
    { id: "map-beneficiary", section: "map", kind: "map", role: "beneficiary", dur: 6.5,
      caption: "Beneficiary: registers a household, claims, and confirms what was received." },
    { id: "map-disbursing", section: "map", kind: "map", role: "disbursing", dur: 6.0,
      caption: "Disbursing Officer: checks ID and hands over the cash." },
    { id: "map-auditor", section: "map", kind: "map", role: "auditor", dur: 5.5,
      caption: "Auditor: reads everything, changes nothing." },
    { id: "map-all", section: "map", kind: "map-hold", dur: 6.7,
      caption: "Five roles, 27 proposed screens. Each role sees only its own." },

    // ---- Section 2: inside one role ----
    { id: "grid", section: "role", kind: "grid", role: "dswd", step: 2, dur: 7.5,
      caption: "Each node opens a proposed screen. The DSWD Officer has nine." },
    { id: "grid-limit", section: "role", kind: "grid-limit", role: "dswd", dur: 7.0,
      caption: "It decides claims and runs payout sessions. It cannot hand over cash." },

    // ---- Section 3: one payout, end to end ----
    { id: "before", section: "payout", kind: "lead", dur: 9.5,
      caption: "First a request goes up and is approved. Then the funds come down." },
    { id: "funds", section: "payout", kind: "screen", arrive: "grow", dur: 8.0,
      role: "dswd", page: "funds", steps: [2, 3],
      scroll: [{ focus: null }, { at: 1.5, dur: 1.0, focus: "Recorded funding authority" }], press: [3.3],
      caption: "Funds reach the Field Office. DSWD records the release: ₱500,000." },
    { id: "claim", section: "payout", kind: "screen", arrive: "handoff", carry: "Claim intake opened", dur: 9.0,
      role: "beneficiary", page: "claim", steps: [5, 6], focus: "Submitted claim",
      caption: "With funds released, the list is built. Lina’s household claims." },
    { id: "attest", section: "payout", kind: "screen", arrive: "handoff", carry: "Claim, version 1", dur: 9.0,
      role: "barangay", page: "claims", steps: [6, 7], focus: "Submitted claim",
      caption: "A named Barangay Officer vouches: lives here, was affected." },
    { id: "batch", section: "payout", kind: "screen", arrive: "nav", dur: 7.0,
      role: "barangay", page: "batches", steps: [7, 8], focus: null,
      caption: "The Punong Barangay sends the signed batch to DSWD." },
    { id: "review", section: "payout", kind: "screen", arrive: "handoff", carry: "Signed barangay snapshot", dur: 9.0,
      role: "dswd", page: "review", steps: [8, 9], focus: "Shared Field Office review",
      caption: "Automatic checks only raise flags. A DSWD Officer decides." },
    { id: "amount", section: "payout", kind: "screen", arrive: "nav", dur: 7.5,
      role: "dswd", page: "amounts", steps: [9, 10], focus: "Documented basis per disaster",
      caption: "Nobody types an amount. ₱4,950 is computed from documented inputs." },
    { id: "list", section: "payout", kind: "screen", arrive: "nav", dur: 8.5,
      role: "dswd", page: "lists", steps: [10, 11, 12], focus: null, press: [2.3, 4.9],
      caption: "The approved list is published only once its anchor is confirmed." },
    { id: "session", section: "payout", kind: "screen", arrive: "nav", dur: 7.5,
      role: "dswd", page: "sessions", steps: [12, 13],
      scroll: [{ focus: "DSWD-controlled payout session" }, { at: 4.2, dur: 1.0, focus: "Notice delivery" }], press: [2.2],
      caption: "DSWD schedules the payout. Lina is sent the date and site." },
    { id: "open", section: "payout", kind: "screen", arrive: "handoff", carry: "Payout notice", dur: 9.0,
      role: "beneficiary", page: "payout", steps: [14, 15], focus: "Your transaction",
      caption: "Lina opens her payout and receives a one-time code." },
    { id: "idcheck", section: "payout", kind: "screen", arrive: "handoff", carry: "Opened attempt 1", dur: 9.0,
      role: "disbursing", page: "payment", steps: [15, 16], focus: "Assigned recipient",
      caption: "The Disbursing Officer checks Lina’s ID against her photo." },
    { id: "handover", section: "payout", kind: "screen", arrive: "state", dur: 7.5,
      role: "disbursing", page: "payment", steps: [16, 17], focus: "Assigned recipient",
      caption: "She counts the cash, then gives her code. Handover recorded once." },
    { id: "answer", section: "payout", kind: "screen", arrive: "handoff", carry: "Recorded handover", dur: 9.0,
      role: "beneficiary", page: "payout", steps: [17, 18], focus: "Your transaction",
      caption: "Lina answers privately: received in full. The payer cannot see it." },
    { id: "audit", section: "payout", kind: "screen", arrive: "handoff", carry: "Evidence trail", dur: 9.0,
      role: "auditor", page: "evidence", steps: [18],
      scroll: [{ focus: null }, { at: 3.6, dur: 4.6, focus: "Versioned evidence trail", align: "end" }],
      caption: "The Auditor reads the whole trail and changes nothing." },
    { id: "recheck", section: "payout", kind: "screen", arrive: "scroll", dur: 7.5,
      role: "auditor", page: "evidence", steps: [18],
      scroll: [{ focus: "Versioned evidence trail", align: "end" }, { at: 0, dur: 1.2, focus: "Integrity re-check — simulation only" }],
      spot: "#integrity-result",
      caption: "Re-checking a record. Chain unreachable means not verified, never assumed." },

    // ---- Section 4: the path ----
    { id: "path", section: "path", kind: "path", dur: 9.0,
      caption: "One payout, seven handoffs, five roles. Every step left a record." },
    { id: "close", section: "path", kind: "close", dur: 7.5,
      caption: "Redesign mockup: proposed screens, invented people, simulated results. Not built yet." },
  ],
};
