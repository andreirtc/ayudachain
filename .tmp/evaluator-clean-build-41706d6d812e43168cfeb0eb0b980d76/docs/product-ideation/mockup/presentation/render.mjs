// Renders presentation.html to presentation.mp4.
//
//   npm run render             extract mockup screens, render every frame, encode, probe
//   npm run stills             write one PNG per checkpoint straight from the HTML (fast design check)
//   node render.mjs --verify   probe presentation.mp4 and pull the checkpoint frames out of the mp4 itself
//
// Options: --workers=4  --keep-frames  --no-extract  --from=SECONDS --to=SECONDS (partial render, no encode)
//
// The page draws the frame for a given time; this script steps time by 1/fps, saves each
// frame as a PNG, then encodes the PNGs with ffmpeg. Nothing is captured in real time.
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { cpus } from "node:os";
import { join } from "node:path";
import ffprobeInstaller from "@ffprobe-installer/ffprobe";
import ffmpegPath from "ffmpeg-static";
import { extract } from "./extract-screens.mjs";
import { HERE, fileUrl, launch } from "./tools.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const [k, v] = a.replace(/^--/, "").split("="); return [k, v ?? true]; }));
const FFMPEG = process.env.FFMPEG_PATH || ffmpegPath;
const FFPROBE = process.env.FFPROBE_PATH || ffprobeInstaller.path;
const OUT = join(HERE, "presentation.mp4");
const FRAMES = join(HERE, "frames");
const STILLS = join(HERE, "stills");
const WIDTH = 1920, HEIGHT = 1080;
const pad = (n) => String(n).padStart(6, "0");

async function openPage(browser) {
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(fileUrl(join(HERE, "presentation.html")) + "?capture=1", { waitUntil: "load" });
  await page.waitForFunction("window.READY === true", { timeout: 15000 }).catch(() => {});
  if (errors.length) throw new Error("presentation.html raised errors:\n  " + errors.join("\n  "));
  return page;
}
const shoot = async (page, t, path) => {
  await page.evaluate((time) => window.renderAt(time), t);
  await page.screenshot({ path, type: "png", optimizeForSpeed: true, captureBeyondViewport: false });
};
const meta = (page) => page.evaluate(() => ({ total: window.TOTAL, fps: window.FPS, beats: window.BEATS, checkpoints: window.CHECKPOINTS }));

function readingReport(beats) { // hold rule: reading time (3 words a second) plus 3 seconds
  const short = [];
  for (const b of beats) {
    const words = b.caption.trim().split(/\s+/).length, need = words / 3 + 3;
    if (b.dur + 1e-6 < need) short.push(`  beat ${b.n} "${b.id}": caption needs ${need.toFixed(1)} s, beat lasts ${b.dur.toFixed(1)} s`);
    if (b.capSize < 40) short.push(`  beat ${b.n} "${b.id}": caption shrunk to ${b.capSize}px to fit one line; consider shortening it`);
  }
  if (short.length) console.log("Caption warnings:\n" + short.join("\n"));
}

function probe() {
  const r = spawnSync(FFPROBE, ["-v", "error", "-show_entries", "stream=index,codec_type,codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,nb_frames,duration:format=duration,size,format_name", "-of", "json", OUT], { encoding: "utf8" });
  if (r.status !== 0) throw new Error("ffprobe failed: " + r.stderr);
  return JSON.parse(r.stdout);
}
function printProbe() {
  const info = probe(), v = info.streams.find((s) => s.codec_type === "video"), audio = info.streams.filter((s) => s.codec_type === "audio");
  const size = statSync(OUT).size;
  console.log(`presentation.mp4: ${v.width}x${v.height}, ${v.codec_name} (${v.profile}), ${v.pix_fmt}, ${v.r_frame_rate} fps, ${v.nb_frames} frames, ${Number(info.format.duration).toFixed(3)} s, ` +
    `${audio.length} audio streams, ${(size / 1048576).toFixed(2)} MB (${size} bytes)`);
  return { info, size };
}

async function main() {
  if (args.verify) {
    if (!existsSync(OUT)) throw new Error("presentation.mp4 does not exist yet. Run npm run render first.");
    const browser = await launch();
    let m;
    try { m = await meta(await openPage(browser)); } finally { await browser.close(); }
    const { info } = printProbe();
    rmSync(STILLS, { recursive: true, force: true }); mkdirSync(STILLS, { recursive: true });
    for (const c of m.checkpoints) {
      const frame = Math.round(c.t * m.fps);
      // seek to half a frame before the wanted frame, so the first frame decoded is exactly that one
      const at = Math.max(0, (frame - 0.5) / m.fps).toFixed(4);
      const r = spawnSync(FFMPEG, ["-v", "error", "-y", "-ss", at, "-i", OUT, "-frames:v", "1", join(STILLS, `mp4-${c.name}.png`)], { encoding: "utf8" });
      if (r.status !== 0) throw new Error(`Could not extract frame ${frame}: ${r.stderr}`);
    }
    writeFileSync(join(STILLS, "probe.json"), JSON.stringify(info, null, 2));
    console.log(`${m.checkpoints.length} frames pulled from the mp4 into stills/ (mp4-*.png), probe.json alongside.`);
    return;
  }

  if (!args["no-extract"]) {
    const e = await extract();
    console.log(`Extracted ${e.screens} screens from ../index.html`);
  }
  const browser = await launch(), extras = [];
  try {
    const first = await openPage(browser);
    const m = await meta(first);
    readingReport(m.beats);

    if (args.stills) {
      rmSync(STILLS, { recursive: true, force: true }); mkdirSync(STILLS, { recursive: true });
      const only = typeof args.stills === "string" ? args.stills.split(",") : null;
      const list = m.checkpoints.filter((c) => !only || only.some((o) => c.name.includes(o)));
      for (const c of list) await shoot(first, c.t, join(STILLS, `html-${c.name}.png`));
      console.log(`${list.length} stills written to stills/ (html-*.png). Total ${m.total.toFixed(1)} s.`);
      return;
    }

    const fps = m.fps, totalFrames = Math.round(m.total * fps);
    const from = args.from ? Math.round(Number(args.from) * fps) : 0, to = args.to ? Math.round(Number(args.to) * fps) : totalFrames;
    const partial = from !== 0 || to !== totalFrames;
    if (!partial) rmSync(FRAMES, { recursive: true, force: true });
    mkdirSync(FRAMES, { recursive: true });
    const workers = Math.max(1, Math.min(Number(args.workers) || Math.min(6, Math.ceil(cpus().length / 2)), 8));
    // One browser per worker: a headless browser only paints its front tab, so extra tabs would stall.
    const pages = [first];
    while (pages.length < workers) { const extra = await launch(); extras.push(extra); pages.push(await openPage(extra)); }
    console.log(`Rendering frames ${from}-${to - 1} of ${totalFrames} (${m.total.toFixed(2)} s at ${fps} fps) with ${workers} browsers...`);
    let next = from, done = 0;
    const started = Date.now();
    await Promise.all(pages.map(async (page) => {
      for (;;) {
        const f = next++;
        if (f >= to) return;
        await shoot(page, f / fps, join(FRAMES, `f_${pad(f)}.png`));
        if (++done % 300 === 0) console.log(`  ${done}/${to - from} frames, ${((Date.now() - started) / 1000).toFixed(0)} s`);
      }
    }));
    console.log(`Frames done in ${((Date.now() - started) / 1000).toFixed(0)} s.`);
    if (partial) { console.log("Partial render: frames kept in frames/, nothing encoded."); return; }

    const have = readdirSync(FRAMES).filter((n) => /^f_\d{6}\.png$/.test(n)).length;
    if (have !== totalFrames) throw new Error(`Expected ${totalFrames} frames, found ${have}.`);
    await new Promise((resolve, reject) => {
      const ff = spawn(FFMPEG, [
        "-v", "error", "-y", "-framerate", String(fps), "-i", join(FRAMES, "f_%06d.png"),
        // bt709 so colours match in browsers and PowerPoint; yuv420p for broad playback
        "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1", "-preset", "slow", "-crf", "17", "-tune", "animation",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-r", String(fps), "-an", "-movflags", "+faststart", OUT,
      ], { stdio: ["ignore", "inherit", "inherit"] });
      ff.on("error", reject);
      ff.on("close", (code) => (code === 0 ? resolve() : reject(new Error("ffmpeg exited with code " + code))));
    });
    printProbe();
    if (!args["keep-frames"]) rmSync(FRAMES, { recursive: true, force: true });
  } finally {
    await Promise.all([browser, ...extras].map((b) => b.close().catch(() => {})));
  }
}

main().catch((e) => { console.error(e.message || e); process.exit(1); });
