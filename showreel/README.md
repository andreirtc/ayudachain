# AyudaChain showreel

A 66-second, 1920x1080, 60fps motion piece about the five-role MVP. It is promotional material, not product code, and nothing here is imported by the frontend or backend.

## What is real and what is illustrated

- **Product screens are real.** `capture.mjs` screenshots the running local `/mvp` workspaces by navigation only. No form is submitted and no action button is pressed. Every name and figure on them is the MVP's synthetic evaluation data.
- **The integrity sequence (0:40 to 1:00) is an illustration.** It rebuilds a payout record and a chain in the product's visual style to explain the check. Its status chips and explanations use the product's own wording from `frontend/components/mvp/UI.tsx` and `IntegrityStatus.tsx`. It is labelled as an illustration on screen.
- **The digests are real SHA-256.** They are the digests of the two payload strings in `film/timeline.js`. `render.mjs` recomputes both and refuses to render if they differ. They are not the MVP's evidence-protocol commitments and no chain was read to make the film.
- **The score is synthesized** in `score.mjs` with the Web Audio API. It uses no samples.

The film makes no claim of sign-in, offline payout or fraud detection, and its end card says the MVP is for local evaluation with synthetic records.

## Preview

Serve `film/` over HTTP and open it, for example `npx serve showreel/film`. Space plays and pauses; the slider scrubs. The page needs `film/score.wav` for sound.

## Rebuild

```
node showreel/capture.mjs      # optional: recapture plates (needs the frontend on :3000 and the API on :8000)
node showreel/score.mjs        # writes film/score.wav
FFMPEG=/path/to/ffmpeg node showreel/render.mjs
```

`render.mjs` uses the Playwright already installed in `frontend/` and needs a full ffmpeg build (libx264 and libvpx-vp9) named by `FFMPEG`. Output goes to `showreel/out/`. `--stills 12,30.5` writes PNG stills instead of a full render.

All timing lives in `film/timeline.js`; picture and sound both read it.
