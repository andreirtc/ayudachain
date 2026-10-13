// Renders the showreel frame by frame with Playwright, then encodes MP4 and WebM.
//
//   node showreel/render.mjs --stills 1,9.5,20      write PNG stills to showreel/out/stills
//   node showreel/render.mjs                        full render (needs FFMPEG, and score.wav for sound)
//
// FFMPEG must point at a full ffmpeg binary (libx264 + libvpx). Frames go to SHOWREEL_TMP or the OS temp dir.
import { chromium } from '../frontend/node_modules/playwright/index.mjs';
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { existsSync, mkdirSync, rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = fileURLToPath(new URL('.', import.meta.url));
const film = join(here, 'film');
const out = join(here, 'out');
const args = process.argv.slice(2);
const flag = name => { const i = args.indexOf(name); return i < 0 ? null : args[i + 1] ?? ''; };
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.wav': 'audio/wav', '.json': 'application/json' };

export async function serve() {
  const server = createServer(async (request, response) => {
    const path = normalize(decodeURIComponent(new URL(request.url, 'http://x').pathname)).replace(/^([\\/])+/, '');
    const file = join(film, path || 'index.html');
    if (!file.startsWith(film) || !existsSync(file)) { response.writeHead(404).end(); return; }
    response.writeHead(200, { 'content-type': TYPES[extname(file)] || 'application/octet-stream' }).end(await readFile(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return { server, url: `http://127.0.0.1:${server.address().port}/index.html?render=1` };
}

async function openPage(browser, url) {
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => { console.error('page error:', error.message); process.exitCode = 1; });
  await page.goto(url);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
  return page;
}

async function main() {
  const { server, url } = await serve();
  const browser = await chromium.launch();
  try {
    const first = await openPage(browser, url);
    // The digests on screen must be the real SHA-256 of the payloads they claim to fingerprint.
    const record = await first.evaluate(() => window.RECORD);
    const sha = text => createHash('sha256').update(text).digest('hex');
    if (sha(record.payload) !== record.digest || sha(record.alteredPayload) !== record.alteredDigest) throw new Error('RECORD digests do not match their payloads; refusing to render.');
    const cues = await first.evaluate(() => window.CUES);

    const stills = flag('--stills');
    if (stills !== null) {
      const dir = join(out, 'stills');
      mkdirSync(dir, { recursive: true });
      for (const t of stills.split(',').map(Number)) {
        await first.evaluate(time => window.__seek(time), t);
        await first.screenshot({ path: join(dir, `t${t.toFixed(2).padStart(5, '0')}.png`) });
        console.log('still', t);
      }
      return;
    }

    const ffmpeg = process.env.FFMPEG;
    if (!ffmpeg || !existsSync(ffmpeg)) throw new Error('Set FFMPEG to a full ffmpeg binary before a full render.');
    const frames = join(process.env.SHOWREEL_TMP || tmpdir(), 'ayudachain-showreel-frames');
    rmSync(frames, { recursive: true, force: true });
    mkdirSync(frames, { recursive: true });
    mkdirSync(out, { recursive: true });
    const total = Math.round(cues.duration * cues.fps);
    const workers = Number(flag('--workers') || 4);
    const pages = [first, ...(await Promise.all(Array.from({ length: workers - 1 }, () => openPage(browser, url))))];
    let next = 0, done = 0;
    const started = Date.now();
    await Promise.all(pages.map(async page => {
      for (;;) {
        const frame = next++;
        if (frame >= total) return;
        await page.evaluate(time => window.__seek(time), frame / cues.fps);
        await page.screenshot({ path: join(frames, `f${String(frame).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 96 });
        if (++done % 300 === 0) console.log(`frames ${done}/${total} (${((Date.now() - started) / 1000).toFixed(0)}s)`);
      }
    }));
    console.log(`frames ${total}/${total} rendered in ${((Date.now() - started) / 1000).toFixed(0)}s`);

    const score = join(film, 'score.wav');
    const sound = existsSync(score);
    if (!sound) console.warn('score.wav not found: encoding picture only. Run node showreel/score.mjs first for sound.');
    const input = ['-y', '-framerate', String(cues.fps), '-i', join(frames, 'f%05d.jpg'), ...(sound ? ['-i', score] : [])];
    const run = (label, extra) => {
      const result = spawnSync(ffmpeg, [...input, ...extra], { stdio: ['ignore', 'ignore', 'pipe'] });
      if (result.status !== 0) throw new Error(`${label} encode failed:\n${String(result.stderr).slice(-1500)}`);
      console.log('encoded', label);
    };
    run('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709', ...(sound ? ['-c:a', 'aac', '-b:a', '256k'] : []), '-movflags', '+faststart', '-shortest', join(out, 'ayudachain-showreel.mp4')]);
    run('webm', ['-c:v', 'libvpx-vp9', '-crf', '24', '-b:v', '0', '-row-mt', '1', '-cpu-used', '2', '-pix_fmt', 'yuv420p', '-vf', 'scale=in_range=full:out_range=tv:out_color_matrix=bt709', ...(sound ? ['-c:a', 'libopus', '-b:a', '192k'] : []), '-shortest', join(out, 'ayudachain-showreel.webm')]);
    if (!flag('--keep-frames') && !args.includes('--keep-frames')) rmSync(frames, { recursive: true, force: true });
  } finally {
    await browser.close();
    server.close();
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === normalize(process.argv[1])) main().catch(error => { console.error(error.message || error); process.exit(1); });
