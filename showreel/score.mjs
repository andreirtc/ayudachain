// Synthesizes the showreel score with the Web Audio API in headless Chromium and writes film/score.wav.
// Every note is generated here; no samples or third-party audio are used. Cue times come from film/timeline.js.
//   node showreel/score.mjs
import { chromium } from '../frontend/node_modules/playwright/index.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const film = fileURLToPath(new URL('./film/', import.meta.url));

async function compose() {
  const C = window.CUES;
  const SR = 48000, LENGTH = C.duration + 0.6;
  const ctx = new OfflineAudioContext(2, Math.ceil(SR * LENGTH), SR);

  // deterministic noise
  let seed = 20261013;
  const rand = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const noiseBuffer = ctx.createBuffer(1, SR * 2, SR);
  { const d = noiseBuffer.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rand() * 2 - 1; }
  const impulse = ctx.createBuffer(2, SR * 3.4, SR);
  for (let ch = 0; ch < 2; ch++) { const d = impulse.getChannelData(ch); for (let i = 0; i < d.length; i++) { const x = i / d.length; d[i] = (rand() * 2 - 1) * Math.pow(1 - x, 3.2) * (i < 400 ? i / 400 : 1); } }

  // buses
  const master = ctx.createGain();
  const comp = ctx.createDynamicsCompressor();
  comp.threshold.value = -16; comp.knee.value = 12; comp.ratio.value = 3.2; comp.attack.value = 0.006; comp.release.value = 0.22;
  master.connect(comp); comp.connect(ctx.destination);
  const reverb = ctx.createConvolver(); reverb.buffer = impulse;
  const reverbOut = ctx.createGain(); reverbOut.gain.value = 0.5;
  reverb.connect(reverbOut); reverbOut.connect(master);
  const bus = gain => { const g = ctx.createGain(); g.gain.value = gain; g.connect(master); return g; };
  const padBus = bus(1), bassBus = bus(1), drumBus = bus(1), leadBus = bus(1), fxBus = bus(1);
  master.gain.setValueAtTime(1, 0);
  master.gain.setValueAtTime(1, C.fade);
  master.gain.linearRampToValueAtTime(0, C.duration + 0.4);

  function route(node, { pan = 0, rev = 0, dest = fxBus }) {
    const p = ctx.createStereoPanner(); p.pan.value = pan;
    node.connect(p); p.connect(dest);
    if (rev > 0) { const s = ctx.createGain(); s.gain.value = rev; p.connect(s); s.connect(reverb); }
  }
  function tone({ t, f, f1, dur = 0.3, type = 'sine', gain = 0.1, a = 0.004, tau, lp, pan = 0, rev = 0, dest = leadBus }) {
    const osc = ctx.createOscillator(); osc.type = type;
    osc.frequency.setValueAtTime(f, t);
    if (f1) osc.frequency.exponentialRampToValueAtTime(f1, t + dur);
    const g = ctx.createGain(); const decay = tau ?? dur / 4;
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(gain, t + a); g.gain.setTargetAtTime(0, t + a, decay);
    let node = osc;
    if (lp) { const fl = ctx.createBiquadFilter(); fl.type = 'lowpass'; fl.frequency.value = lp; node.connect(fl); node = fl; }
    node.connect(g); route(g, { pan, rev, dest });
    osc.start(t); osc.stop(t + a + decay * 7 + 0.05);
  }
  function noise({ t, dur, gain, type = 'bandpass', f0, f1, q = 1, a = 0.005, tau, peakAt, pan = 0, pan1, rev = 0, dest = fxBus }) {
    const src = ctx.createBufferSource(); src.buffer = noiseBuffer; src.loop = true;
    const fl = ctx.createBiquadFilter(); fl.type = type; fl.Q.value = q;
    fl.frequency.setValueAtTime(f0, t); if (f1) fl.frequency.exponentialRampToValueAtTime(f1, t + dur);
    const g = ctx.createGain(); g.gain.setValueAtTime(0, t);
    if (peakAt != null) { g.gain.linearRampToValueAtTime(gain, t + dur * peakAt); g.gain.linearRampToValueAtTime(0, t + dur); }
    else { g.gain.linearRampToValueAtTime(gain, t + a); g.gain.setTargetAtTime(0, t + a, tau ?? dur / 4); }
    src.connect(fl); fl.connect(g);
    const p = ctx.createStereoPanner(); p.pan.setValueAtTime(pan, t); if (pan1 != null) p.pan.linearRampToValueAtTime(pan1, t + dur);
    g.connect(p); p.connect(dest);
    if (rev > 0) { const s = ctx.createGain(); s.gain.value = rev; p.connect(s); s.connect(reverb); }
    src.start(t, rand() * 1.5); src.stop(t + dur + (tau ?? 0) * 7 + 0.1);
  }
  function pad(t, dur, freqs, gain, { cut0 = 500, cut1 = 1400, atk = 0.6, rel = 0.8, rev = 0.5 } = {}) {
    const fl = ctx.createBiquadFilter(); fl.type = 'lowpass'; fl.Q.value = 0.6;
    fl.frequency.setValueAtTime(cut0, t); fl.frequency.linearRampToValueAtTime(cut1, t + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(gain, t + atk); g.gain.setValueAtTime(gain, t + dur); g.gain.linearRampToValueAtTime(0, t + dur + rel);
    freqs.forEach((f, i) => [-7, 7].forEach((cents, k) => {
      const osc = ctx.createOscillator(); osc.type = 'sawtooth'; osc.frequency.value = f; osc.detune.value = cents + (i % 2 ? 3 : -3);
      const p = ctx.createStereoPanner(); p.pan.value = k ? 0.5 : -0.5;
      osc.connect(p); p.connect(fl); osc.start(t); osc.stop(t + dur + rel + 0.1);
    }));
    fl.connect(g); route(g, { rev, dest: padBus });
  }
  const duck = t => [padBus, bassBus].forEach(b => { b.gain.setValueAtTime(0.42, t); b.gain.linearRampToValueAtTime(1, t + 0.3); });
  function kick(t, gain = 0.6, sidechain = true) {
    tone({ t, f: 130, f1: 44, dur: 0.11, gain, tau: 0.1, dest: drumBus });
    noise({ t, dur: 0.02, gain: gain * 0.25, type: 'highpass', f0: 3000, tau: 0.006, dest: drumBus });
    if (sidechain) duck(t);
  }
  const clap = (t, gain = 0.22) => [0, 0.011, 0.023].forEach((d, i) => noise({ t: t + d, dur: 0.12, gain: gain * (i === 2 ? 1 : 0.6), f0: 1700, q: 0.9, tau: i === 2 ? 0.07 : 0.012, rev: 0.3, dest: drumBus }));
  const hat = (t, gain = 0.04, pan = 0.2) => noise({ t, dur: 0.05, gain, type: 'highpass', f0: 7500, tau: 0.018, pan, dest: drumBus });
  function bass(t, f, dur, gain = 0.2) {
    tone({ t, f, dur, type: 'sawtooth', gain: gain * 0.7, a: 0.008, tau: dur * 0.5, lp: 340, dest: bassBus });
    tone({ t, f: f / (f > 80 ? 2 : 1), dur, gain, a: 0.008, tau: dur * 0.5, dest: bassBus });
  }
  const pluck = (t, f, gain = 0.07, pan = 0) => { tone({ t, f, dur: 0.4, type: 'triangle', gain, tau: 0.09, lp: 3200, pan, rev: 0.4 }); tone({ t, f: f * 2, dur: 0.2, gain: gain * 0.25, tau: 0.05, pan, rev: 0.4 }); };
  const bell = (t, f, gain = 0.08, pan = 0) => { tone({ t, f, dur: 2, gain, tau: 0.5, pan, rev: 0.7 }); tone({ t, f: f * 2.76, dur: 1, gain: gain * 0.2, tau: 0.2, pan, rev: 0.7 }); };
  const whoosh = (t, dur, gain = 0.12, up = true) => noise({ t, dur, gain, f0: up ? 250 : 5000, f1: up ? 5000 : 180, q: 1.1, peakAt: up ? 0.82 : 0.18, pan: up ? -0.6 : 0.6, pan1: up ? 0.6 : -0.6, rev: 0.35 });
  function riser(t, dur, gain = 0.14) {
    noise({ t, dur, gain, type: 'highpass', f0: 500, f1: 7000, q: 0.7, peakAt: 0.97, rev: 0.3 });
    const osc = ctx.createOscillator(); osc.type = 'sawtooth'; osc.frequency.setValueAtTime(110, t); osc.frequency.exponentialRampToValueAtTime(880, t + dur);
    const fl = ctx.createBiquadFilter(); fl.type = 'lowpass'; fl.frequency.setValueAtTime(300, t); fl.frequency.exponentialRampToValueAtTime(3500, t + dur);
    const g = ctx.createGain(); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(gain * 0.5, t + dur * 0.97); g.gain.linearRampToValueAtTime(0, t + dur);
    osc.connect(fl); fl.connect(g); route(g, { rev: 0.4 }); osc.start(t); osc.stop(t + dur + 0.05);
  }
  function impact(t, gain = 0.7) {
    tone({ t, f: 95, f1: 30, dur: 0.6, gain, tau: 0.32, dest: fxBus });
    noise({ t, dur: 0.6, gain: gain * 0.35, type: 'lowpass', f0: 1400, f1: 200, tau: 0.2, rev: 0.6 });
    noise({ t, dur: 1.6, gain: gain * 0.1, type: 'highpass', f0: 5000, tau: 0.45, rev: 0.7 });
  }
  const tick = (t, f = 2200, gain = 0.035, pan = 0) => tone({ t, f, dur: 0.03, type: 'square', gain, a: 0.001, tau: 0.007, lp: 6000, pan, dest: fxBus });
  const pop = (t, f = 880, gain = 0.09, pan = 0.3) => tone({ t, f, f1: f * 1.5, dur: 0.09, gain, a: 0.002, tau: 0.04, pan, rev: 0.35, dest: fxBus });

  const N = { F1: 43.65, Bb1: 58.27, C2: 65.41, D2: 73.42, Eb2: 77.78, F2: 87.31, Ab2: 103.83, A2: 110, Bb2: 116.54, C3: 130.81, D3: 146.83, Eb3: 155.56, E3: 164.81, F3: 174.61, G3: 196, A3: 220, Bb3: 233.08, C4: 261.63, D4: 293.66, E4: 329.63, F4: 349.23, G4: 392, A4: 440, Bb4: 466.16, C5: 523.25, D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99, A5: 880, C6: 1046.5, D6: 1174.66, F6: 1396.91 };
  const CH = {
    F: { bass: N.F2, pad: [N.F3, N.A3, N.C4, N.G4], arp: [N.F4, N.A4, N.C5, N.G5] },
    C: { bass: N.C2, pad: [N.E3, N.G3, N.C4, N.D4], arp: [N.E4, N.G4, N.C5, N.D5] },
    Dm: { bass: N.D2, pad: [N.D3, N.F3, N.A3, N.C4], arp: [N.D4, N.F4, N.A4, N.C5] },
    Bb: { bass: N.Bb1, pad: [N.Bb2, N.F3, N.A3, N.D4], arp: [N.F4, N.A4, N.Bb4, N.D5] },
  };
  const ARP = [0, 2, 1, 3, 2, 1, 3, 2];

  // ---- 0-8 cold open: rain, a rising drone, the count, three questions ----
  noise({ t: 0, dur: 4.6, gain: 0.05, type: 'highpass', f0: 3800, q: 0.5, peakAt: 0.35, rev: 0.2 }); // rain
  pad(0.1, 7.6, [N.D2, N.A2, N.D3], 0.085, { cut0: 180, cut1: 950, atk: 2.2, rel: 0.25 });
  [[0.35, N.D5], [1.1, N.A4], [2.3, N.F5], [3.3, N.D5], [3.45, N.A5]].forEach(([t, f], i) => bell(t, f, 0.06, i % 2 ? 0.4 : -0.4));
  for (let i = 0, t = C.count; t < C.count + 1.65; i++) { tick(t, 1700 + rand() * 900, 0.03, rand() * 1.2 - 0.6); t += 0.022 + Math.pow(i / 40, 2.2) * 0.2; }
  whoosh(C.disperse - 0.25, 0.9, 0.11, true);
  [N.D5, N.F5, N.A5, N.C6, N.D6, N.F6].forEach((f, i) => pluck(C.disperse + 0.1 + i * 0.09, f, 0.035, i % 2 ? 0.5 : -0.5));
  C.questions.forEach((t, i) => { impact(t, 0.34 + i * 0.12); tone({ t, f: [N.D3, N.Eb3, N.D3][i], dur: 0.9, type: 'sawtooth', gain: 0.07, tau: 0.3, lp: 700, rev: 0.5 }); });
  pad(C.questions[2], 0.9, [N.D3, N.A3, N.E4], 0.07, { cut0: 400, cut1: 2600, atk: 0.7, rel: 0.05 });
  riser(C.logo - 1.5, 1.5, 0.15);

  // ---- 8-12 the mark ----
  impact(C.logo, 0.85);
  pad(C.logo, 3.9, CH.F.pad, 0.12, { cut0: 2400, cut1: 900, atk: 0.02, rel: 0.5 });
  bass(C.logo, N.F1, 3.6, 0.3);
  [N.F5, N.A5, N.C6, N.F6].forEach((f, i) => bell(C.logo + 0.02 + i * 0.03, f, 0.06, (i - 1.5) * 0.4));
  for (let i = 0; i < 16; i++) pluck(C.logo + 1.2 + i * 0.125, [N.F5, N.C6, N.A5, N.G5][i % 4], 0.03 + i * 0.0015, i % 2 ? 0.5 : -0.5);
  whoosh(C.logo + 3.05, 0.95, 0.13, true);

  // ---- 12-40 the product: groove under the directory and the five stations ----
  const chords = ['F', 'C', 'Dm', 'Bb', 'F', 'C', 'Dm'];
  chords.forEach((name, i) => {
    const t = C.directory + i * 4, ch = CH[name];
    pad(t, 3.9, ch.pad, 0.075, { cut0: 700, cut1: 1500, atk: 0.12, rel: 0.25 });
  });
  for (let t = C.directory; t < C.concept - 0.001; t += 0.25) {
    const ch = CH[chords[Math.min(chords.length - 1, Math.floor((t - C.directory) / 4))]];
    const step = Math.round((t - C.directory) / 0.25);
    const onBeat = step % 2 === 0, beat = step / 2;
    const fill = C.trail.some(s => t >= s - 0.5 && t < s) || t >= C.concept - 0.75;
    pluck(t, ch.arp[ARP[step % 8]] * (step % 16 >= 12 ? 2 : 1), 0.05, step % 2 ? 0.45 : -0.45);
    if (t >= C.roles[0] && !fill && onBeat) kick(t, t < C.trail[0] ? 0.42 : 0.6);
    if (t >= C.trail[0] && !fill && onBeat && beat % 2 === 1) clap(t, 0.2);
    if (!onBeat && !fill) hat(t, t < C.trail[0] ? 0.03 : 0.045, step % 4 === 1 ? 0.3 : -0.3);
    if (t >= C.roles[0] && !fill) bass(t, ch.bass * (step % 8 === 6 ? 2 : 1), 0.22, t < C.trail[0] ? 0.14 : 0.2);
  }
  C.roles.forEach((t, i) => { pop(t, [N.F5, N.G5, N.A5, N.C6, N.D6][i], 0.09, -0.4 + i * 0.1); whoosh(t - 0.06, 0.3, 0.05, false); });
  whoosh(13.4, 0.9, 0.08, true);
  C.trail.forEach((t, i) => {
    whoosh(t - 0.5, 0.52, 0.12, true);
    impact(t, 0.4);
    const end = C.trail[i + 1] ?? C.concept;
    [1.55, i === 2 ? 2.95 : i >= 3 ? 3.4 : 2.35].forEach((d, k) => { if (t + d < end - 0.3) pop(t + d, k ? N.C6 : N.A5, 0.07, 0.4); });
  });
  for (let k = 0; k < 6; k++) tick(C.trail[3] + 3.0 + k * 0.2, 2400 + k * 180, 0.03, 0.3); // journey rows wipe on
  whoosh(C.concept - 0.6, 0.6, 0.14, false);

  // ---- 40-48 how the check works: thinner, patient ----
  impact(C.concept, 0.45);
  pad(C.concept, 3.9, CH.Bb.pad, 0.07, { cut0: 500, cut1: 1100, atk: 0.4, rel: 0.4 });
  pad(C.concept + 4, 3.75, CH.C.pad, 0.075, { cut0: 600, cut1: 1900, atk: 0.3, rel: 0.05 });
  bass(C.concept, N.Bb1, 3.8, 0.22); bass(C.concept + 4, N.C2, 3.7, 0.22);
  for (let t = C.concept + 0.5; t < C.tamper - 0.26; t += 0.5) {
    const ch = t < C.concept + 4 ? CH.Bb : CH.C, step = Math.round((t - C.concept) / 0.5);
    pluck(t, ch.arp[ARP[step % 8]], 0.04, step % 2 ? 0.5 : -0.5);
    hat(t + 0.25, 0.022, 0);
  }
  tone({ t: C.scan, f: 320, f1: 1250, dur: 1.2, gain: 0.035, a: 0.2, tau: 0.5, rev: 0.4, dest: fxBus });
  for (let t = C.scan + 0.2; t < C.scan + 1.4; t += 0.045) tick(t, 2600 + rand() * 1600, 0.018, -0.5);
  whoosh(C.send, 1.0, 0.1, true);
  impact(C.stamp, 0.5); bell(C.stamp, N.C6, 0.08, 0.4); bell(C.stamp + 0.02, N.G5, 0.06, 0.2);
  for (let t = C.stamp; t < C.stamp + 0.6; t += 0.04) tick(t, 3000 + rand() * 1200, 0.016, 0.5);
  pop(45.75, N.G5, 0.07, 0); pop(45.87, N.C6, 0.07, 0);
  noise({ t: C.tamper - 0.9, dur: 0.9, gain: 0.12, f0: 300, f1: 4200, q: 1.4, peakAt: 0.98, rev: 0.2 });

  // ---- 48-56 tamper, then a chain that cannot be read: the floor drops out ----
  impact(C.tamper, 0.6);
  pad(C.tamper + 0.05, 7.6, [N.D2, N.Eb3, N.A2], 0.07, { cut0: 260, cut1: 520, atk: 0.5, rel: 0.3, rev: 0.6 });
  for (let t = C.tamper + 1; t < C.restore - 0.1; t += 1) { kick(t, 0.36, false); kick(t + 0.19, 0.24, false); } // heartbeat
  for (let k = 0; k < 14; k++) tick(C.edit + k * 0.042, 900 - k * 30, 0.04, -0.4);
  for (let t = C.edit + 0.7; t < C.compare; t += 0.04) tick(t, 2400 + rand() * 1800, 0.017, -0.5);
  for (let k = 0; k < 24; k++) tick(C.compare + k * 0.025, 700 + k * 55, 0.028, -0.6 + k * 0.05);
  impact(C.mismatch, 0.75);
  [N.D2, N.Ab2, N.D3].forEach(f => tone({ t: C.mismatch, f, dur: 1, type: 'sawtooth', gain: 0.085, a: 0.005, tau: 0.28, lp: 900, rev: 0.5, dest: fxBus }));
  tone({ t: C.powerDown, f: 520, f1: 38, dur: 0.9, type: 'sawtooth', gain: 0.1, a: 0.01, tau: 0.45, lp: 1200, rev: 0.4, dest: fxBus });
  noise({ t: C.powerDown, dur: 1.0, gain: 0.09, type: 'lowpass', f0: 5000, f1: 120, peakAt: 0.05, rev: 0.3 });
  for (let k = 0; k < 16; k++) tick(C.powerDown + 0.05 + rand() * 0.8, 4000 + rand() * 3000, 0.02, 0.5);
  impact(C.unreachableChip, 0.55);
  [N.D2, N.Ab2].forEach(f => tone({ t: C.unreachableChip, f, dur: 1, type: 'sawtooth', gain: 0.07, tau: 0.3, lp: 700, rev: 0.5, dest: fxBus }));

  // ---- 56-58 the chain answers again; 58 resolve ----
  [N.F3, N.A3, N.C4, N.F4, N.A4, N.C5].forEach((f, i) => pluck(C.restore + i * 0.1, f, 0.06, -0.5 + i * 0.2));
  pad(C.restore, 1.95, CH.C.pad, 0.08, { cut0: 350, cut1: 3200, atk: 1.6, rel: 0.04 });
  bass(C.restore, N.C2, 1.9, 0.2);
  riser(C.restore + 0.5, 1.5, 0.15);
  tick(C.click, 1500, 0.08, 0.1);
  for (let k = 0; k < 30; k++) tick(C.click + 0.15 + k * 0.027, 900 + k * 70, 0.022, -0.6 + k * 0.04);
  impact(C.verified, 0.95);
  [N.F5, N.A5, N.C6, N.F6].forEach((f, i) => bell(C.verified + i * 0.035, f, 0.075, (i - 1.5) * 0.4));

  // ---- 58-66 home key, groove returns, long tail ----
  [['F', 58], ['F', 60], ['C', 62]].forEach(([name, t]) => { pad(t, 1.95, CH[name].pad, 0.09, { cut0: 1900, cut1: 1300, atk: 0.03, rel: 0.2 }); });
  for (let t = C.verified; t < 64 - 0.001; t += 0.25) {
    const ch = t < 62 ? CH.F : CH.C, step = Math.round((t - C.verified) / 0.25), onBeat = step % 2 === 0;
    pluck(t, ch.arp[ARP[step % 8]] * (step % 16 >= 12 ? 2 : 1), 0.055, step % 2 ? 0.45 : -0.45);
    if (onBeat) kick(t, 0.6);
    if (onBeat && (step / 2) % 2 === 1) clap(t, 0.2);
    if (!onBeat) hat(t, 0.045, step % 4 === 1 ? 0.3 : -0.3);
    bass(t, ch.bass * (step % 8 === 6 ? 2 : 1), 0.22, 0.2);
  }
  impact(C.end, 0.6);
  whoosh(C.end - 0.4, 0.42, 0.1, true);
  impact(64, 0.55);
  pad(64, 1.6, [N.F2, ...CH.F.pad, N.C5], 0.1, { cut0: 2200, cut1: 500, atk: 0.02, rel: 1.6, rev: 0.8 });
  bass(64, N.F1, 2.2, 0.28);
  [N.F5, N.C6, N.A5, N.F6].forEach((f, i) => bell(64 + i * 0.09, f, 0.06, (i - 1.5) * 0.4));

  const rendered = await ctx.startRendering();
  const L = rendered.getChannelData(0), Rr = rendered.getChannelData(1);
  let peak = 0;
  for (let i = 0; i < L.length; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(Rr[i]));
  const norm = 0.89 / (peak || 1);
  const frames = Math.round(SR * (C.duration + 0.5));
  const pcm = new Int16Array(frames * 2);
  for (let i = 0; i < frames; i++) { pcm[i * 2] = Math.max(-1, Math.min(1, L[i] * norm)) * 32767; pcm[i * 2 + 1] = Math.max(-1, Math.min(1, Rr[i] * norm)) * 32767; }
  const bytes = new Uint8Array(pcm.buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return { base64: btoa(binary), sampleRate: SR, peak };
}

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  page.on('pageerror', error => console.error('page error:', error.message));
  await page.setContent('<!doctype html><title>score</title>');
  await page.addScriptTag({ content: readFileSync(`${film}timeline.js`, 'utf8') });
  const { base64, sampleRate, peak } = await page.evaluate(compose);
  const pcm = Buffer.from(base64, 'base64');
  const header = Buffer.alloc(44);
  header.write('RIFF', 0); header.writeUInt32LE(36 + pcm.length, 4); header.write('WAVEfmt ', 8);
  header.writeUInt32LE(16, 16); header.writeUInt16LE(1, 20); header.writeUInt16LE(2, 22);
  header.writeUInt32LE(sampleRate, 24); header.writeUInt32LE(sampleRate * 4, 28); header.writeUInt16LE(4, 32); header.writeUInt16LE(16, 34);
  header.write('data', 36); header.writeUInt32LE(pcm.length, 40);
  writeFileSync(`${film}score.wav`, Buffer.concat([header, pcm]));
  console.log(`score.wav written: ${(pcm.length / sampleRate / 4).toFixed(2)}s, pre-normalisation peak ${peak.toFixed(3)}`);
} finally {
  await browser.close();
}
