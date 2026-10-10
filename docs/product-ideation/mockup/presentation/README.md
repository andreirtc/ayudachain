# Redesign walkthrough video

`presentation.mp4` walks a non-technical audience through the AyudaChain redesign mockup: who uses it, which screens each role gets, and how one payout record travels from a fund release to the Auditor. It is a video of [the mockup](../index.html), which is still ideation. Nothing in it is working software, and every frame says so.

The mp4 is not kept in git (about 16 MB per render). Build it with the commands below.

## Re-render

From this folder, once:

```
npm install
```

Then, after any change:

```
npm run render
```

This rewrites `presentation.mp4` (1920x1080, 30 fps, H.264, yuv420p, no audio). It needs Node and an installed Chrome or Edge; set `CHROME_PATH` if neither is in a standard location. ffmpeg and ffprobe come from this folder's own `node_modules`.

## Change a caption or a timing

Edit [storyboard.js](storyboard.js). Each beat has a `caption` and a `dur` in seconds. Run `npm run render`. The render prints a warning when a caption is longer than its beat allows (reading time at three words a second, plus three seconds).

To preview without rendering, open [presentation.html](presentation.html) in a browser and drag the slider. Add `?t=75` to the address to open at 75 seconds.

## Files

| File | What it is |
|---|---|
| `storyboard.js` | The beats: order, duration, caption, which mockup screen and which guided steps |
| `presentation.html` | The scene. `renderAt(t)` draws the frame for time `t`; there are no timers or CSS animations |
| `extract-screens.mjs` | Reads `../index.html` and copies out its stylesheet, role and screen names, and each needed screen's markup. Read-only on the mockup |
| `screens.generated.js` | Output of the extraction. Regenerated on every render; do not edit |
| `render.mjs` | Steps time one frame at a time in headless Chrome, saves PNG frames, encodes them with ffmpeg, then probes the result |
| `tools.mjs` | Shared helpers: browser lookup and storyboard loading |

`frames/`, `stills/` and `node_modules/` are ignored by git.

## Checking a render

```
npm run stills            # one PNG per checkpoint, straight from the HTML (fast)
npm run verify            # ffprobe the mp4, then pull the same checkpoint frames out of the mp4
```

Checkpoints are the middle of every beat and of every transition. Both commands write to `stills/`.

## Where the content comes from

- Screens, role names, screen names, people and identifiers are taken from the mockup at render time. If the mockup changes, the next render picks it up. If a screen or section the storyboard names no longer exists, the render stops and says which.
- The journey is the mockup's scenario 1, "From funding to full receipt". A screen is shown as the mockup renders it at one guided step, the role's own button is pressed, and the screen changes to how the mockup renders it at the next step.
- The "today" beat is written by hand from [the current sitemap](../../../product/sitemap.md).
- The "before AyudaChain" beat is written by hand from DSWD Memorandum Circular No. 24, s. 2025, which amends MC No. 11, s. 2025. It shows the real steps that come before the software: a state of calamity, the barangay's or LGU's request and project proposal, Field Office validation and the Secretary's activation, then the release of funds. Under that circular the beneficiary masterlist follows the release of funds, which is the order the journey then takes. None of those earlier steps is a mockup screen; the redesign treats them as outside the software.
- Captions and the short labels on each handoff are written by hand in `storyboard.js`.

## What the video leaves out of the mockup

- Presenter controls: the scenario picker, the presenter guide and the "resume guided step" strip. The role picker and each role's navigation are kept.
- The sidebar is drawn 220 pixels wide instead of the mockup's 190, so the account picker and the longest navigation label are not cut off.
- Seven of the eight scenarios. Only scenario 1 is shown.

## Labels

Every frame carries two labels in its top strip: "Redesign mockup · not working software" and "Simulated demo data · no chain was read". No hash is shown anywhere, because the mockup shows none. The one integrity result shown is the mockup's default, "SIMULATED result: Chain unreachable. Not verified."
