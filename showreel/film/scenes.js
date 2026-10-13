// AyudaChain showreel: scene construction. All timing comes from CUES (timeline.js).
// Product screens are captured plates of the running local MVP (see ../capture.mjs).
// The integrity sequence is an illustration that uses the product's own status wording.
window.buildFilm = async function buildFilm() {
  const { tw, stagger, set, scene, h, split, ease, clamp, lerp, hash } = FX;
  const C = CUES, R = RECORD;
  const stage = document.getElementById('stage');

  const PLATES = ['directory', 'beneficiary-overview', 'beneficiary-overview-tall', 'barangay-overview', 'dswd-overview', 'dswd-funds', 'dswd-claims', 'disbursing-overview', 'disbursing-overview-tall', 'auditor-overview', 'auditor-overview-tall'];
  await Promise.all(PLATES.map(name => { const image = new Image(); image.src = `plates/${name}.png`; return image.decode().catch(() => {}); }));

  // ---------- shared pieces ----------
  const ICONS = {
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    alert: '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16.5 12"/>',
    lock: '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    house: '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    landmark: '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/><polygon points="12 2 20 7 4 7"/>',
    banknote: '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    scan: '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
    link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  };
  const icon = (name, size = 24, sw = 2) => h('svg', { viewBox: '0 0 24 24', width: size, height: size, fill: 'none', stroke: 'currentColor', 'stroke-width': sw, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', html: ICONS[name] });

  // The in-app brand mark: a teal tile with the shield-check, drawn as two strokes so it can animate on.
  function brandMark(height) {
    const k = height / 39;
    const size = 23 * k;
    const svg = h('svg', { viewBox: '0 0 24 24', width: size, height: size, fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
    const body = h('path', { pathLength: 1, d: 'M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z', style: { strokeDasharray: 1 } });
    const tick = h('path', { pathLength: 1, d: 'm9 12 2 2 4-4', style: { strokeDasharray: 1 } });
    svg.append(body, tick);
    const el = h('div', { class: 'mark', style: { width: `${35 * k}px`, height: `${height}px`, borderRadius: `${9 * k}px ${9 * k}px ${15 * k}px ${15 * k}px` } }, svg);
    return { el, body, tick, width: 35 * k };
  }

  // Mark, wordmark and tagline, centred on the stage. Returns handles for animation.
  function lockup(parent, cy) {
    const group = h('div', { class: 'abs', style: { width: '1920px', height: '1080px', transformOrigin: `960px ${cy}px` } });
    parent.append(group);
    const mark = brandMark(196);
    const word = h('div', { class: 'wordmark', text: 'AyudaChain' });
    group.append(mark.el, word);
    const total = mark.width + 46 + word.offsetWidth;
    const left = (1920 - total) / 2;
    Object.assign(mark.el.style, { left: `${left}px`, top: `${cy - 98}px` });
    Object.assign(word.style, { left: `${left + mark.width + 46}px`, top: `${cy - 78}px` });
    const chars = split(word, 'chars');
    const tagline = h('div', { class: 'tagline', text: 'Relief you can follow.', style: { top: `${cy + 150}px` } });
    group.append(tagline);
    return { group, mark, chars, tagline, left, centreOffset: 960 - mark.width / 2 - left, markCx: left + mark.width / 2 };
  }

  // A browser window holding a captured plate. Tall plates scroll under the app's fixed rail.
  function plateWin(parent, { name, url, tall }) {
    const src = `plates/${name}.png`;
    const tallSrc = `plates/${name}-tall.png`;
    const scroll = h('div', { class: 'abs' }, h('img', { class: 'plate-img', src: tall ? tallSrc : src, alt: '' }));
    const view = h('div', { class: 'win-view' }, scroll);
    if (tall) view.append(h('img', { class: 'plate-img rail', src, alt: '' }));
    const dim = h('div', { class: 'win-dim' });
    const bar = h('div', { class: 'win-bar' }, h('i'), h('i'), h('i'), h('div', { class: 'win-url', text: url }));
    const win = h('div', { class: 'win' }, bar, view, dim);
    const tilt = h('div', { class: 'tilt' }, win);
    const cam = h('div', { class: 'cam' }, tilt);
    parent.append(cam);
    return { cam, tilt, win, view, scroll, dim, src, tallSrc, tall };
  }
  // Camera state that centres a plate region on a point at a scale.
  const camState = (r, s, cx, cy) => ({ x: cx - s * (r.x + r.w / 2), y: cy - s * (40 + r.y + r.h / 2), s, ox: r.x + r.w / 2, oy: 40 + r.y + r.h / 2 });
  const FULL = { x: 0, y: 0, w: 1600, h: 1000 };

  // Lifts a region of the plate off the screen: same pixels, raised and enlarged.
  function lift(P, r, tIn, tOut, k, scrollY = 0) {
    const el = h('div', { class: 'lift', style: { left: `${r.x}px`, top: `${40 + r.y}px`, width: `${r.w}px`, height: `${r.h}px`, backgroundImage: `url(${scrollY ? P.tallSrc : P.src})`, backgroundSize: '1600px auto', backgroundPosition: `${-r.x}px ${-(r.y + scrollY)}px` } });
    P.tilt.append(el);
    tw(el, tIn, 0.1, { o: [0, 1] }, 'linear');
    tw(el, tIn, 0.8, { s: [1, k] }, 'spring');
    tw(el, tOut - 0.34, 0.3, { s: 1 }, 'inOut');
    tw(el, tOut - 0.05, 0.05, { o: 0 }, 'linear');
    return el;
  }

  const lines = (el, texts) => texts.map(text => { const line = h('div', { text }); el.append(line); return split(line, 'words'); }).flat();
  const lightBackdrop = el => { const glow = h('div', { class: 'bg-glow' }), dots = h('div', { class: 'bg-dots' }); el.append(glow, dots); return { glow, dots }; };

  // ---------- 1. cold open ----------
  (function open() {
    const el = h('section', { class: 'scene dark' });
    stage.append(el);
    const canvas = h('canvas', { width: 1920, height: 1080 });
    const g = canvas.getContext('2d');
    const line = h('div', { class: 'o-line', text: 'After the flood, relief funding is released.' });
    const num = h('div', { class: 'o-num', text: '₱0.00' });
    const label = h('div', { class: 'o-label', text: 'Recorded funding authority · Synthetic Flood Talim' });
    el.append(canvas, line, num, label, h('div', { class: 'slate', text: 'Figure from the local MVP ledger · synthetic records only' }));

    stagger(split(line), 0.35, 0.9, { yp: [130, 0] }, 'out', 0.07);
    tw(line, 3.55, 0.45, { o: [1, 0], y: [0, -24] }, 'in');
    tw(num, 1.45, 0.5, { o: [0, 1] }, 'outSoft');
    tw(num, 1.45, 2.3, { s: [0.9, 1] }, 'out');
    tw(num, C.disperse, 0.55, { s: 0.5, o: 0, blur: [0, 18] }, 'in');
    tw(label, 2.3, 0.6, { o: [0, 1], y: [14, 0] });
    tw(label, 3.55, 0.4, { o: 0 }, 'in');

    ['Who approved it?', 'Who received it?', 'Can anyone prove it?'].forEach((text, i) => {
      const q = h('div', { class: 'o-q', text });
      el.append(q);
      const parts = split(q);
      stagger(parts, C.questions[i], 0.6, { yp: [130, 0] }, 'out', 0.06);
      if (i < 2) tw(parts, C.questions[i] + 0.82, 0.18, { yp: -130 }, 'in');
      else { tw(q, C.questions[i], 1.2, { s: [1, 1.05] }, 'linear'); parts.find(p => p.textContent === 'prove').style.color = 'var(--teal-bright)'; }
    });

    const money = new Intl.NumberFormat('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const TOTAL = 1270952.75; // "Recorded releases" on the DSWD funding ledger plate
    const drops = Array.from({ length: 170 }, (_, i) => ({ x: hash(i, 11) * 2500 - 200, y: hash(i, 12) * 1300, len: 40 + hash(i, 13) * 90, v: 900 + hash(i, 14) * 900, a: 0.04 + hash(i, 15) * 0.1 }));
    const targets = Array.from({ length: 48 }, (_, i) => {
      const a = (i / 48) * Math.PI * 2 + (hash(i, 21) - 0.5) * 0.2;
      const rx = 500 + hash(i, 22) * 420, ry = 250 + hash(i, 23) * 250;
      return { x: 960 + Math.cos(a) * rx, y: 500 + Math.sin(a) * ry, bend: (hash(i, 24) - 0.5) * 260, delay: hash(i, 25) * 0.7, fade: hash(i, 26) * 1.1, cold: hash(i, 27) * 2 };
    });
    const SRC = { x: 960, y: 470 };

    function draw(t) {
      g.clearRect(0, 0, 1920, 1080);
      // rain
      const rain = clamp(t / 0.6) * (1 - clamp((t - 3.1) / 1.3));
      if (rain > 0) {
        g.lineWidth = 1.4;
        for (const d of drops) {
          const y = ((d.y + d.v * t) % 1400) - 150;
          const x = d.x - y * 0.22;
          g.strokeStyle = `rgba(190,220,228,${(d.a * rain).toFixed(3)})`;
          g.beginPath(); g.moveTo(x, y); g.lineTo(x - d.len * 0.22, y + d.len); g.stroke();
        }
      }
      // rising water contours
      const rise = 46 * ease.out(clamp(t / 5));
      for (let i = 0; i < 6; i++) {
        g.beginPath();
        for (let x = -20; x <= 1940; x += 20) {
          const y = 800 + i * 52 - rise + Math.sin(x * 0.004 + t * 0.55 + i) * 15 + Math.sin(x * 0.011 - t * 0.8 + i * 2) * 6;
          x < 0 ? g.moveTo(x, y) : g.lineTo(x, y);
        }
        g.strokeStyle = `rgba(79,196,174,${0.05 + i * 0.022})`;
        g.lineWidth = 1.5; g.stroke();
      }
      // the release spreads out to households, then the trail goes cold
      if (t > C.disperse - 0.1) {
        for (const p of targets) {
          const grow = ease.out(clamp((t - C.disperse - p.delay) / 0.9));
          if (grow <= 0) continue;
          const alive = 1 - clamp((t - 4.9 - p.fade) / 0.8);
          const mx = (SRC.x + p.x) / 2 - (p.y - SRC.y) / 600 * p.bend, my = (SRC.y + p.y) / 2 + (p.x - SRC.x) / 900 * p.bend;
          const at = u => ({ x: (1 - u) * (1 - u) * SRC.x + 2 * (1 - u) * u * mx + u * u * p.x, y: (1 - u) * (1 - u) * SRC.y + 2 * (1 - u) * u * my + u * u * p.y });
          if (alive > 0) {
            g.beginPath();
            for (let k = 0; k <= 26; k++) { const q = at((k / 26) * grow); k ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y); }
            g.strokeStyle = `rgba(79,196,174,${(0.55 * alive).toFixed(3)})`;
            g.lineWidth = 1.6; g.stroke();
          }
          const head = at(grow);
          if (grow < 1) { g.fillStyle = 'rgba(216,255,245,.95)'; g.beginPath(); g.arc(head.x, head.y, 3.4, 0, 7); g.fill(); }
          else {
            const cold = clamp((t - 5.3 - p.cold) / 0.6);
            g.fillStyle = `rgba(${Math.round(lerp(79, 150, cold))},${Math.round(lerp(196, 170, cold))},${Math.round(lerp(174, 180, cold))},${lerp(0.95, 0.28, cold).toFixed(3)})`;
            g.beginPath(); g.arc(p.x, p.y, lerp(5.5, 3.6, cold), 0, 7); g.fill();
          }
        }
      }
    }
    scene(el, 0, C.logo, t => {
      num.textContent = '₱' + money.format(TOTAL * ease.out(clamp((t - C.count) / 1.7)));
      draw(t);
    });
  })();

  // ---------- 2. mark ----------
  (function logo() {
    const el = h('section', { class: 'scene dark', style: { zIndex: 5 } });
    stage.append(el);
    const L = lockup(el, 470);
    const ring = h('div', { class: 'ring', style: { left: '840px', top: '350px', width: '240px', height: '240px' } });
    const flash = h('div', { class: 'flash' });
    const wipe = h('div', { class: 'wipe' });
    wipe.dataset.cx = L.markCx; wipe.dataset.cy = 470;
    el.append(ring, flash, wipe);
    const mask = `radial-gradient(circle at ${L.markCx}px 470px, transparent calc(var(--hole) * 1px - 2px), #000 calc(var(--hole) * 1px))`;
    el.style.setProperty('--hole', 0);
    el.style.webkitMaskImage = mask; el.style.maskImage = mask;

    const t = C.logo;
    tw(flash, t, 0.6, { o: [0.9, 0] }, 'outSoft');
    tw(ring, t, 1.2, { s: [0.3, 4.2], o: [0.9, 0] }, 'out');
    tw(L.mark.el, t, 0.12, { o: [0, 1] }, 'linear');
    tw(L.mark.el, t, 1.0, { s: [0.2, 1] }, 'spring');
    set(L.mark.el, 0, { x: L.centreOffset });
    tw(L.mark.el, t + 0.95, 0.8, { x: [L.centreOffset, 0] }, 'swift');
    tw(L.mark.body, t + 0.1, 0.85, { dash: [1, 0] }, 'inOut');
    tw(L.mark.tick, t + 0.7, 0.4, { dash: [1, 0] }, 'out');
    stagger(L.chars, t + 1.2, 0.75, { yp: [130, 0] }, 'out', 0.035);
    stagger(split(L.tagline), t + 1.95, 0.8, { yp: [130, 0] }, 'out', 0.07);
    tw(L.group, t, 3.2, { s: [1, 1.035] }, 'linear');
    tw(wipe, t + 3.1, 0.75, { circ: [0, 2500] }, 'swift');
    tw(el, t + 3.45, 0.72, { '--hole': [0, 2500] }, 'swift');
    scene(el, C.logo, C.directory + 0.2);
  })();

  // ---------- 3. the real directory, and the five workspaces behind it ----------
  (function directory() {
    const el = h('section', { class: 'scene light' });
    stage.append(el);
    lightBackdrop(el);
    const rig = h('div', { class: 'abs', style: { width: '1920px', height: '1080px', perspective: '2400px' } });
    el.append(rig);
    const D = plateWin(rig, { name: 'directory', url: 'localhost:3000/mvp' });
    const scrim = h('div', { class: 'scrim' }, h('div', { class: 'bg-glow' }), h('div', { class: 'bg-dots' }));
    rig.append(scrim);
    tw(scrim, 13.55, 0.7, { o: [0, 1] }, 'inOut');
    tw(scrim, 17.5, 0.4, { o: 0 }, 'in');
    const a0 = camState(FULL, 0.74, 960, 700), a1 = camState(FULL, 0.8, 960, 548), a2 = camState(FULL, 0.83, 960, 548);
    const LIST = { x: 800, y: 160, w: 600, h: 600 };
    const b1 = camState(LIST, 1.16, 1390, 540), b2 = camState(LIST, 1.21, 1390, 540);
    tw(D.cam, 11.7, 0.3, { o: [0, 1] }, 'linear');
    tw(D.cam, 11.7, 1.05, { x: [a0.x, a1.x], y: [a0.y, a1.y], s: [a0.s, a1.s] }, 'out');
    tw(D.tilt, 11.7, 1.05, { rx: [18, 5], ry: [-7, -3], ox: [800, 800], oy: [520, 520] }, 'out');
    tw(D.cam, 12.75, 0.8, { x: a2.x, y: a2.y, s: a2.s }, 'linear');
    tw(D.cam, 13.5, 0.8, { x: b1.x, y: b1.y, s: b1.s }, 'inOut');
    tw(D.tilt, 13.5, 0.8, { rx: 3, ry: -9, ox: b1.ox, oy: b1.oy }, 'inOut');
    tw(D.cam, 14.3, 3.2, { x: b2.x, y: b2.y, s: b2.s }, 'linear');
    tw(D.cam, 17.5, 0.45, { x: b2.x + 1100, o: 0 }, 'in');

    const roles = [['beneficiary-overview', 'Beneficiary', '/mvp/beneficiary'], ['barangay-overview', 'Barangay Officer', '/mvp/barangay-officer'], ['dswd-overview', 'DSWD Officer', '/mvp/dswd-officer'], ['disbursing-overview', 'Disbursing Officer', '/mvp/disbursing-officer'], ['auditor-overview', 'Auditor', '/mvp/auditor']];
    roles.forEach(([name, label, path], i) => {
      const hl = h('div', { class: 'hl', style: { left: '812px', top: `${40 + 274 + 91 * i}px`, width: '568px', height: '83px' } });
      D.tilt.append(hl);
      tw(hl, C.roles[i], 0.35, { o: [0, 1], sx: [0, 1] }, 'out');
      tw(hl, C.roles[i] + 0.5, 0.5, { o: 0.4 }, 'outSoft');

      const T = plateWin(rig, { name, url: `localhost:3000${path}` });
      T.tilt.append(h('div', { class: 'tag', text: label }));
      const t0 = C.roles[i], sx = 84 + 84 * i, sy = 118 + 80 * i, rowY = 540 + 1.16 * (91 * i - 145);
      tw(T.cam, t0, 0.14, { o: [0, 1] }, 'linear');
      tw(T.cam, t0, 0.95, { x: [1340, sx], y: [rowY, sy] }, 'out');
      tw(T.cam, t0, 1.0, { s: [0.03, 0.36] }, 'spring');
      tw(T.tilt, t0, 1.1, { ry: [-46, -7], rx: [14, 3], r: [9, (i - 2) * 1.1], ox: [800, 800], oy: [520, 520] }, 'out');
      tw(T.cam, 16.6, 0.9, { y: sy - 12 }, 'linear');
      tw(T.cam, 17.5 + i * 0.035, 0.42, { x: sx - 1300, o: 0 }, 'in');
    });

    const cap = h('div', { class: 'big-cap', text: 'Five roles. One record.' });
    el.append(cap);
    const parts = split(cap);
    parts[2].style.color = parts[3].style.color = 'var(--teal)';
    stagger(parts, 14.35, 0.85, { yp: [130, 0] }, 'out', 0.07);
    stagger(parts, 17.5, 0.3, { yp: -130 }, 'in', 0.02);
    const slate = h('div', { class: 'slate', text: 'Product screens captured from the running local MVP · synthetic records · no sign-in', style: { left: 'auto', right: '96px' } });
    el.append(slate);
    scene(el, 11.4, C.trail[0]);
  })();

  // ---------- 4. the trail: five stations, each on its own real screen ----------
  (function trail() {
    const el = h('section', { class: 'scene light' });
    stage.append(el);
    lightBackdrop(el);
    const zone = h('div', { class: 'uizone' });
    el.append(zone);
    const FX_ = 640, FY = 548;

    const stations = [
      { name: 'Funding', role: 'DSWD Officer', icon: 'landmark', plate: 'dswd-funds', path: '/mvp/dswd-officer/funds',
        title: ['Every release,', 'on the ledger.'], sub: 'Funding authority is recorded against its release document.',
        moves: [{ at: 0.95, dur: 0.95, r: { x: 250, y: 270, w: 800, h: 540 }, s: 1.3 }, { at: 1.9, dur: 2.1, r: { x: 250, y: 270, w: 800, h: 540 }, s: 1.37, e: 'linear' }],
        lifts: [{ r: { x: 262, y: 304, w: 340, h: 66 }, in: 1.6, out: 3.6, k: 1.42 }, { r: { x: 287, y: 514, w: 470, h: 56 }, in: 2.35, out: 3.6, k: 1.2 }],
        dims: [[1.6, 3.6]] },
      { name: 'Claim & review', role: 'DSWD Officer', icon: 'users', plate: 'dswd-claims', path: '/mvp/dswd-officer/claims',
        title: ['Flags inform.', 'People decide.'], sub: 'Barangay responses and review flags go to a human DSWD decision.',
        moves: [{ at: 0.95, dur: 0.95, r: { x: 236, y: 170, w: 820, h: 500 }, s: 1.28 }, { at: 1.9, dur: 2.1, r: { x: 236, y: 170, w: 820, h: 500 }, s: 1.35, e: 'linear' }],
        lifts: [{ r: { x: 262, y: 233, w: 420, h: 30 }, in: 1.6, out: 3.6, k: 1.38 }, { r: { x: 287, y: 546, w: 500, h: 52 }, in: 2.35, out: 3.6, k: 1.26 }],
        dims: [[1.6, 3.6]] },
      { name: 'Payout', role: 'Disbursing Officer', icon: 'banknote', plate: 'disbursing-overview', tall: true, path: '/mvp/disbursing-officer',
        title: ['One handover.', 'Recorded once.'], sub: 'Compare identity, present the amount, record authorization.',
        moves: [{ at: 0.95, dur: 0.85, r: { x: 252, y: 180, w: 900, h: 230 }, s: 1.16 }, { at: 2.35, dur: 0.75, r: { x: 790, y: 470, w: 470, h: 180 }, s: 1.72, scroll: 330 }, { at: 3.1, dur: 0.9, r: { x: 790, y: 470, w: 470, h: 180 }, s: 1.78, e: 'linear' }],
        lifts: [{ r: { x: 262, y: 298, w: 880, h: 78 }, in: 1.5, out: 2.4, k: 1.03 }, { r: { x: 826, y: 534, w: 404, h: 54 }, in: 2.95, out: 3.62, k: 1.12, scroll: 330 }],
        dims: [[1.5, 2.4], [2.95, 3.62]] },
      { name: 'Private confirmation', role: 'Beneficiary', icon: 'house', plate: 'beneficiary-overview', tall: true, path: '/mvp/beneficiary',
        title: ['The household', 'sees it too.'], sub: 'The amount, how it was worked out, and a private receipt answer.',
        moves: [{ at: 0.95, dur: 0.9, r: { x: 380, y: 270, w: 1060, h: 400 }, s: 1.08 }, { at: 2.75, dur: 0.8, r: { x: 262, y: 296, w: 640, h: 490 }, s: 1.34, scroll: 236 }, { at: 3.55, dur: 1.45, r: { x: 262, y: 296, w: 640, h: 490 }, s: 1.39, e: 'linear' }],
        lifts: [{ r: { x: 902, y: 289, w: 402, h: 360 }, in: 1.5, out: 2.75, k: 1.2 }],
        dims: [[1.5, 2.75]], journey: 3.0 },
      { name: 'Independent audit', role: 'Auditor', icon: 'scan', plate: 'auditor-overview', tall: true, path: '/mvp/auditor',
        title: ['Auditors read', 'everything.'], sub: 'Read-only. A flag is a reason to inspect, never a finding of fraud.',
        moves: [{ at: 0.95, dur: 0.9, r: { x: 248, y: 170, w: 860, h: 470 }, s: 1.28 }, { at: 2.7, dur: 0.85, r: { x: 1100, y: 402, w: 484, h: 276 }, s: 1.62, scroll: 420 }, { at: 3.55, dur: 1.45, r: { x: 1100, y: 402, w: 484, h: 276 }, s: 1.68, e: 'linear' }],
        lifts: [{ r: { x: 262, y: 236, w: 700, h: 28 }, in: 1.5, out: 2.7, k: 1.22 }, { r: { x: 1120, y: 420, w: 444, h: 240 }, in: 3.4, out: 4.62, k: 1.1, scroll: 420 }],
        dims: [[1.5, 2.7], [3.4, 4.62]] },
    ];

    // progress strip uses the product's own five journey labels from the directory page
    const steps = h('div', { class: 'steps' });
    const labelBox = h('div', { class: 'steps-label' });
    const fill = h('div', { class: 'fill' });
    const track = h('div', { class: 'steps-track' }, h('div', { class: 'base' }), fill);
    steps.append(labelBox, track);
    el.append(steps);
    tw(steps, C.trail[0] + 0.1, 0.6, { o: [0, 1], y: [20, 0] }, 'out');
    tw(steps, C.concept - 0.5, 0.3, { o: 0 }, 'in');

    stations.forEach((st, i) => {
      const t0 = C.trail[i], t1 = C.trail[i + 1] ?? C.concept;
      const P = plateWin(zone, { name: st.plate, tall: st.tall, url: `localhost:3000${st.path}` });
      const est = camState(FULL, 0.64, FX_ - 20, FY);
      tw(P.cam, t0, 0.22, { o: [0, 1] }, 'linear');
      tw(P.cam, t0, 0.95, { x: [est.x + 1250, est.x], y: [est.y + 26, est.y], s: [est.s, est.s] }, 'out');
      tw(P.cam, t0, 0.6, { blur: [14, 0] }, 'out');
      tw(P.tilt, t0, 1.05, { ry: [-36, -10], rx: [7, 4], ox: [800, 800], oy: [520, 520] }, 'out');
      let cur = est;
      st.moves.forEach(m => {
        cur = camState(m.r, m.s, FX_, FY);
        const e = m.e || 'inOut';
        tw(P.cam, t0 + m.at, m.dur, { x: cur.x, y: cur.y, s: cur.s }, e);
        tw(P.tilt, t0 + m.at, m.dur, { rx: m.e ? 1.2 : 2, ry: m.e ? -2.5 : -4.5, ox: cur.ox, oy: cur.oy }, e);
        if (m.scroll != null) tw(P.scroll, t0 + m.at, m.dur, { y: -m.scroll }, e);
      });
      st.lifts.forEach(L => lift(P, L.r, t0 + L.in, t0 + L.out, L.k, L.scroll || 0));
      st.dims.forEach(([a, b]) => { tw(P.dim, t0 + a, 0.4, { o: [0, 0.3] }, 'outSoft'); tw(P.dim, t0 + b - 0.3, 0.3, { o: 0 }, 'inOut'); });
      if (st.journey) {
        // the five journey rows of the real screen wipe on, one per step
        for (let k = 0; k < 6; k++) {
          const cover = h('div', { class: 'cover', style: { left: '290px', top: `${596 + 70 * k}px`, width: '580px', height: `${k === 5 ? 44 : 70}px` } });
          P.scroll.append(cover);
          tw(cover, t0 + st.journey + k * 0.2, 0.42, { cl: [0, 100] }, 'inOut');
        }
      }
      if (i < stations.length - 1) tw(P.cam, t1 - 0.36, 0.36, { x: cur.x - 340, o: 0, blur: [0, 12] }, 'in');

      // caption
      const role = h('div', { class: 'cap-role' }, h('span', { class: 'av' }, icon(st.icon, 22)), h('span', { text: `${st.role} workspace` }));
      const title = h('h2');
      const sub = h('p', { text: st.sub });
      el.append(h('div', { class: 'cap' }, role, title, sub));
      const words = lines(title, st.title);
      tw(role, t0 + 0.1, 0.55, { o: [0, 1], x: [-18, 0] }, 'out');
      stagger(words, t0 + 0.16, 0.85, { yp: [130, 0] }, 'out', 0.065);
      tw(sub, t0 + 0.52, 0.7, { o: [0, 1], y: [18, 0] }, 'out');
      tw(role, t1 - 0.44, 0.24, { o: 0 }, 'in');
      stagger(words, t1 - 0.46, 0.3, { yp: -130 }, 'in', 0.02);
      tw(sub, t1 - 0.46, 0.24, { o: 0 }, 'in');

      // progress node and label
      const dot = h('span', { style: { width: '8px', height: '8px', borderRadius: '50%', background: '#fff' } });
      const tick = h('span', { class: 'abs', style: { inset: 0, display: 'grid', placeItems: 'center' } }, icon('check', 14, 3));
      const on = h('div', { class: 'on' }, dot, tick);
      track.append(h('div', { class: 'node', style: { left: `${i * 130}px` } }, on));
      tw(fill, t0 + 0.1, 0.7, { w: i * 130 }, 'inOut');
      tw(on, t0 + 0.45, 0.7, { s: [0, 1] }, 'spring');
      tw(tick, t1, 0.3, { o: [0, 1] }, 'out');
      if (i < stations.length - 1) tw(dot, t1, 0.15, { o: [1, 0] }, 'linear');
      const label = h('div', { html: `<b>${i + 1} / 5</b>${st.name.replace('&', '&amp;')}` });
      labelBox.append(label);
      tw(label, t0 + 0.14, 0.5, { o: [0, 1], y: [16, 0] }, 'out');
      tw(label, t1 - 0.36, 0.22, { o: 0, y: -14 }, 'in');
    });

    el.append(h('div', { class: 'slate', text: 'Product screens captured from the running local MVP · synthetic records', style: { bottom: '28px' } }));
    // curtain down into the integrity sequence
    for (let i = 0; i < 6; i++) {
      const band = h('div', { class: 'band', style: { left: `${i * 320}px`, width: '321px' } });
      el.append(band);
      tw(band, C.concept - 0.56 + i * 0.03, 0.38, { sy: [0, 1] }, 'swift');
    }
    scene(el, C.trail[0], C.concept);
  })();

  // ---------- 5. how the check works: private record, public digest, and three honest answers ----------
  (function concept() {
    const el = h('section', { class: 'scene dark' });
    stage.append(el);
    const canvas = h('canvas', { width: 1920, height: 1080 });
    const g = canvas.getContext('2d');
    const glowTeal = h('div', { class: 'glow teal' }), glowAmber = h('div', { class: 'glow amber' }), glowGreen = h('div', { class: 'glow green' });
    const all = h('div', { class: 'abs', style: { width: '1920px', height: '1080px', transformOrigin: '960px 540px' } });
    el.append(glowTeal, glowAmber, glowGreen, canvas, all);
    tw(glowTeal, C.concept, 1, { o: [0, 1] }, 'outSoft');
    tw(glowAmber, C.tamper, 0.6, { o: [0, 1] }, 'outSoft');
    tw(glowTeal, C.powerDown, 0.5, { o: 0.2 }, 'inOut');
    tw(glowAmber, C.powerDown, 0.5, { o: 0.55 }, 'inOut');
    tw(glowAmber, C.restore, 0.5, { o: 0 }, 'inOut');
    tw(glowTeal, C.restore, 0.6, { o: 1 }, 'inOut');
    tw(glowGreen, C.verified, 0.25, { o: [0, 1] }, 'out');
    tw(glowGreen, C.verified + 0.3, 1.2, { o: 0.6 }, 'outSoft');

    // captions
    const caps = [
      [40.35, 43.5, 'Personal details stay private.', 'Names, contact details and receipt contents never leave the database.'],
      [43.7, 47.7, 'Only a fingerprint goes on-chain.', 'An opaque ID, the amount and a SHA-256 digest. Nothing else.'],
      [48.15, 51.85, 'Change one figure, and the check says so.', 'The altered record no longer matches its commitment.'],
      [52.25, 55.8, 'No chain read. No “Verified”.', 'If the chain cannot be read, the answer is “Chain unreachable”, never a guess.'],
      [56.15, 57.85, 'Every check reads the chain again.', 'An earlier match does not establish the current result.'],
      [58.0, 59.7, 'Verified is earned. Every time.', 'A matching hash proves the committed content is unchanged.'],
    ];
    caps.forEach(([a, b, title, subText]) => {
      const cap = h('div', { class: 'c-cap', text: title }), sub = h('div', { class: 'c-sub', text: subText });
      all.append(cap, sub);
      const words = split(cap);
      stagger(words, a, 0.7, { yp: [130, 0] }, 'out', 0.045);
      stagger(words, b - 0.3, 0.26, { yp: -130 }, 'in', 0.012);
      tw(sub, a + 0.3, 0.6, { o: [0, 1], y: [12, 0] }, 'out');
      tw(sub, b - 0.3, 0.22, { o: 0 }, 'in');
    });

    // columns
    const leftLabel = h('div', { class: 'col-label', style: { left: '120px' } }, icon('lock', 20), h('span', { text: 'Off-chain · private database' }));
    const rightLabel = h('div', { class: 'col-label', style: { left: '1020px' } }, icon('link', 20), h('span', { text: 'On-chain · public commitments' }));
    const divider = h('div', { class: 'divider' });
    all.append(leftLabel, rightLabel, divider);
    tw(divider, 40.15, 0.9, { sy: [0, 1] }, 'inOut');
    tw(leftLabel, 40.35, 0.6, { o: [0, 1], y: [10, 0] });
    tw(rightLabel, 40.5, 0.6, { o: [0, 1], y: [10, 0] });

    // record card, in the product's panel and chip styles
    const row = (label, value, extra) => h('div', { class: 'rc-row' }, h('dt', { text: label }), value, extra || h('span'));
    const offtag = () => h('span', { class: 'offtag' }, icon('lock', 14), h('span', { text: 'stays off-chain' }));
    const amount = h('dd', { class: 'amt', text: '₱4,950.00' });
    const flag = h('div', { class: 'rc-flag' });
    const tagA = offtag(), tagB = offtag();
    const rows = [
      row('Household', h('dd', { text: 'DFC-2026-33757601' })),
      row('Head of household', h('dd', { text: 'Invented Amihan Malaya' }), tagA),
      row('Amount', amount),
      row('Basis', h('dd', { text: '₱330.00 per day × 15 documented days' })),
      row('Handover', h('dd', { text: 'Oct 11, 2026 · Invented browser hall' }), tagB),
    ];
    rows[2].append(flag);
    const card = h('div', { class: 'rc' }, h('div', { class: 'rc-head' }, h('h3', { text: 'Payout record' }), h('span', { class: 'chip pos' }, icon('check', 15, 2.4), h('span', { text: 'Handover recorded' }))), rows);
    all.append(card);
    tw(card, 40.25, 0.3, { o: [0, 1] }, 'linear');
    tw(card, 40.25, 1.0, { y: [80, 0] }, 'springSoft');
    stagger(rows, 40.5, 0.6, { o: [0, 1], x: [-14, 0] }, 'out', 0.07);
    tw(tagA, 41.5, 0.5, { o: [0, 1], x: [16, 0] }, 'out');
    tw(tagB, 41.66, 0.5, { o: [0, 1], x: [16, 0] }, 'out');
    tw(flag, C.edit + 0.05, 0.25, { o: [0, 1] }, 'out');
    tw(flag, C.unreachable, 0.3, { o: 0 }, 'in');
    const cardH = card.offsetHeight;
    const scan = h('div', { class: 'scanline' });
    all.append(scan);
    tw(scan, C.scan, 0.15, { o: [0, 1] }, 'linear');
    tw(scan, C.scan, 1.25, { y: [0, cardH] }, 'inOut');
    tw(scan, C.scan + 1.15, 0.15, { o: 0 }, 'linear');

    // digests
    function digest(left, labelText) {
      const hex = h('div', { class: 'dg-hex' });
      const spans = Array.from({ length: 64 }, () => h('span', { class: 'ph', text: '·' }));
      hex.append(h('div', {}, spans.slice(0, 32)), h('div', {}, spans.slice(32)));
      const box = h('div', { class: 'dg', style: { left: `${left}px` } }, h('div', { class: 'dg-label' }, h('span', { text: labelText }), h('span', { text: 'SHA-256' })), hex);
      all.append(box);
      const state = spans.map(() => '');
      return { box, paint(i, ch, cls) { const key = ch + cls; if (state[i] !== key) { state[i] = key; spans[i].textContent = ch; spans[i].className = cls; } } };
    }
    const dgL = digest(120, 'Record digest'), dgR = digest(1020, 'Chain commitment');
    tw(dgL.box, 41.2, 0.6, { o: [0, 1], y: [16, 0] });
    tw(dgR.box, 41.35, 0.6, { o: [0, 1], y: [16, 0] });

    // chain
    const blocks = [0, 1, 2, 3].map(i => {
      const power = h('div');
      const solid = h('div', { class: 'solid', html: `#${1041 + i}<u style="width:82%"></u><u style="width:58%"></u><u style="width:70%"></u><u style="width:40%"></u>` });
      const dashed = h('div', { class: 'dashed' });
      const lit = h('div', { class: 'lit' }, icon('shield', 58, 1.8));
      power.append(solid, dashed, lit);
      const el2 = h('div', { class: 'block', style: { left: `${1020 + 173 * i}px` } }, power);
      all.append(el2);
      return { el: el2, power, solid, dashed, lit };
    });
    const links = [0, 1, 2].map(i => {
      const a = h('div', { class: 'link', style: { left: `${1160 + 173 * i}px` } }), b = h('div', { class: 'link dead', style: { left: `${1160 + 173 * i}px` } });
      all.append(a, b);
      tw(b, C.powerDown + 0.1, 0.2, { o: [0, 1] }, 'linear');
      tw(b, C.restore + 0.1 + i * 0.14, 0.2, { o: 0 }, 'linear');
      return a;
    });
    blocks.forEach((b, i) => {
      set(b.lit, 0, { o: 0 });
      if (i < 2) { set(b.dashed, 0, { o: 0 }); tw(b.el, 40.6 + i * 0.13, 0.9, { s: [0, 1] }, 'spring'); tw(b.el, 40.6 + i * 0.13, 0.15, { o: [0, 1] }, 'linear'); }
    });
    tw(links[0], 40.85, 0.4, { sx: [0, 1] }, 'out');
    // slot 2 waits as a dashed outline, then takes the commitment
    const B2 = blocks[2], B3 = blocks[3];
    set(B2.solid, 0, { o: 0 }); set(B3.solid, 0, { o: 0 });
    tw(B2.el, 40.95, 0.5, { o: [0, 1], s: [0.7, 1] }, 'out');
    tw(links[1], C.stamp + 0.05, 0.35, { sx: [0, 1] }, 'out');
    tw(B2.dashed, C.stamp, 0.1, { o: [1, 0] }, 'linear');
    tw(B2.solid, C.stamp, 0.1, { o: [0, 1] }, 'linear');
    tw(B2.lit, C.stamp, 0.1, { o: [0, 1] }, 'linear');
    tw(B2.el, C.stamp, 0.9, { s: [1.4, 1] }, 'spring');
    tw(B3.el, C.stamp + 0.5, 0.5, { o: [0, 1], s: [0.7, 1] }, 'out');
    set(links[2], 0, { o: 0 });
    const stampRing = h('div', { class: 'ring', style: { left: '1336px', top: '365px', width: '200px', height: '200px' } });
    all.append(stampRing);
    set(stampRing, 0, { o: 0 });
    tw(stampRing, C.stamp, 0.9, { s: [0.5, 2.6], o: [0.9, 0] }, 'out');
    tw(links, C.powerDown + 0.1, 0.2, { o: 0 }, 'linear');
    links.slice(0, 2).forEach((l, i) => tw(l, C.restore + 0.1 + i * 0.14, 0.2, { o: 1 }, 'linear'));
    const note = h('div', { class: 'chain-note', text: 'No response from the chain' });
    all.append(note);
    tw(note, C.powerDown + 0.5, 0.4, { o: [0, 1], y: [8, 0] });
    tw(note, C.restore, 0.2, { o: 0 }, 'in');

    // the travelling commitment
    const packet = h('div', { class: 'packet', text: `${R.digest.slice(0, 8)}…${R.digest.slice(-4)}` });
    all.append(packet);
    tw(packet, C.send, 0.15, { o: [0, 1] }, 'linear');
    tw(packet, C.stamp - 0.04, 0.08, { o: 0 }, 'linear');
    const PATH = [{ x: 450, y: 771 }, { x: 900, y: 150 }, { x: 1436, y: 465 }];
    const onPath = u => ({ x: (1 - u) * (1 - u) * PATH[0].x + 2 * (1 - u) * u * PATH[1].x + u * u * PATH[2].x, y: (1 - u) * (1 - u) * PATH[0].y + 2 * (1 - u) * u * PATH[1].y + u * u * PATH[2].y });

    // comparison beam between the two digests
    const beamOk = h('div', { class: 'beam' }), beamBad = h('div', { class: 'beam bad' }), beamCut = h('div', { class: 'beam cut' });
    const eqOk = h('div', { class: 'eqnode ok', text: '=' }), eqBad = h('div', { class: 'eqnode bad', text: '≠' }), eqOff = h('div', { class: 'eqnode off', text: '?' });
    all.append(beamOk, beamBad, beamCut, eqOk, eqBad, eqOff);
    tw(beamOk, 45.4, 0.5, { sx: [0, 1], o: [1, 1] }, 'out'); set(beamOk, 0, { o: 0 });
    tw(eqOk, 45.75, 0.7, { s: [0, 1], o: [1, 1] }, 'spring');
    tw([beamOk, eqOk], C.compare, 0.2, { o: 0 }, 'linear');
    tw(beamBad, C.mismatch, 0.3, { o: [0, 1], sx: [0, 1] }, 'out');
    tw(eqBad, C.mismatch, 0.6, { o: [0, 1], s: [0, 1] }, 'spring');
    tw([beamBad, eqBad], C.unreachable - 0.2, 0.2, { o: 0 }, 'linear');
    tw([beamCut, eqOff], C.powerDown + 0.4, 0.3, { o: [0, 1] }, 'linear');
    tw([beamCut, eqOff], C.verified - 0.05, 0.05, { o: 0 }, 'linear');
    tw(beamOk, C.verified, 0.3, { sx: [0, 1], o: [1, 1] }, 'out');
    tw(eqOk, C.verified, 0.7, { s: [0, 1], o: [1, 1] }, 'spring');
    const okRing = h('div', { class: 'ring', style: { left: '860px', top: '732px', width: '80px', height: '80px', borderColor: '#8ff0c2' } });
    all.append(okRing);
    set(okRing, 0, { o: 0 });
    tw(okRing, C.verified, 1.1, { s: [0.5, 9], o: [0.9, 0] }, 'out');

    // verdicts, in the product's status vocabulary (frontend/components/mvp/UI.tsx, IntegrityStatus.tsx)
    const verdict = (kind, iconName, labelText, text, extra) => {
      const v = h('div', { class: 'verdict' }, h('span', { class: `chip xl ${kind}` }, icon(iconName, 30, 2.2), h('span', { text: labelText })), text ? h('span', { text }) : null, extra);
      all.append(v);
      return v;
    };
    const slam = (v, a, b) => { tw(v, a, 0.1, { o: [0, 1] }, 'linear'); tw(v, a, 0.55, { s: [1.3, 1] }, 'out'); if (b) tw(v, b, 0.2, { o: 0, y: -14 }, 'in'); };
    slam(verdict('att', 'alert', 'Does not match', 'Committed content does not match.'), C.mismatch, C.unreachable - 0.25);
    slam(verdict('att', 'alert', 'Chain unreachable', 'Chain could not be read; not verified.'), C.unreachableChip, C.restore - 0.25);
    const button = h('span', { class: 'btn', text: 'Check now' });
    const vIdle = verdict('neu', 'clock', 'Not checked', null, button);
    tw(vIdle, C.restore + 0.1, 0.45, { o: [0, 1], y: [14, 0] }, 'out');
    tw(vIdle, C.click + 0.12, 0.06, { o: 0 }, 'linear');
    tw(button, C.click - 0.04, 0.08, { s: [1, 0.94] }, 'out');
    tw(button, C.click + 0.04, 0.1, { s: 1 }, 'out');
    const vBusy = verdict('neu', 'clock', 'Checking…', 'Reading the chain commitment');
    tw(vBusy, C.click + 0.12, 0.1, { o: [0, 1] }, 'linear');
    tw(vBusy, C.verified - 0.04, 0.04, { o: 0 }, 'linear');
    slam(verdict('pos', 'check', 'Verified', 'Committed content matches the chain record.'), C.verified);

    // cursor
    const at = node => { let x = 0, y = 0; for (let n = node; n && n !== all; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; } return { x: x + node.offsetWidth / 2, y: y + node.offsetHeight / 2 }; };
    const cursor = h('svg', { class: 'cursor', viewBox: '0 0 24 24', html: '<path d="M4 2.5 4 20l4.6-4.3 3 6.6 3-1.4-3-6.4 6.4-.3z" fill="#fff" stroke="#0c1f28" stroke-width="1.4" stroke-linejoin="round"/>' });
    const ripple = h('div', { class: 'ripple' });
    all.append(ripple, cursor);
    const amountAt = at(amount), buttonAt = at(button);
    const aim = { x: amountAt.x - 60, y: amountAt.y + 8 };
    tw(cursor, C.tamper + 0.15, 0.15, { o: [0, 1] }, 'linear');
    tw(cursor, C.tamper + 0.15, 0.7, { x: [760, aim.x], y: [900, aim.y] }, 'inOut');
    tw(cursor, C.edit - 0.03, 0.07, { s: [1, 0.84] }, 'out');
    tw(cursor, C.edit + 0.05, 0.12, { s: 1 }, 'out');
    tw(cursor, C.edit + 0.7, 0.5, { x: aim.x + 120, y: aim.y + 170, o: 0 }, 'in');
    tw(cursor, C.restore + 0.3, 0.12, { o: 1 }, 'linear');
    tw(cursor, C.restore + 0.3, 0.6, { x: [buttonAt.x + 260, buttonAt.x + 6], y: [buttonAt.y + 130, buttonAt.y + 8] }, 'inOut');
    tw(cursor, C.click - 0.04, 0.07, { s: 0.84 }, 'out');
    tw(cursor, C.click + 0.04, 0.12, { s: 1 }, 'out');
    tw(cursor, C.click + 0.4, 0.4, { o: 0 }, 'in');
    set(ripple, 0, { o: 0, x: aim.x, y: aim.y });
    tw(ripple, C.edit, 0.5, { s: [0.2, 1.3], o: [0.9, 0] }, 'out');
    set(ripple, C.click - 0.01, { x: buttonAt.x, y: buttonAt.y });
    tw(ripple, C.click, 0.5, { s: [0.2, 1.5], o: [0.9, 0] }, 'out');

    all.append(h('div', { class: 'slate', text: 'Illustration of the integrity check · synthetic record · digests are the real SHA-256 of the fields shown' }));
    // curtain lifts in, whole layout recedes out
    for (let i = 0; i < 6; i++) {
      const band = h('div', { class: 'band', style: { left: `${i * 320}px`, width: '321px' } });
      el.append(band);
      tw(band, C.concept, 0.4, { o: [1, 0] }, 'outSoft');
    }
    tw(all, C.end - 0.34, 0.34, { o: [1, 0], s: [1, 0.965] }, 'in');

    // per-frame procedural parts: digest characters, amount digits, block power, packet flight, dust
    const HEX = '0123456789abcdef', H0 = R.digest, H1 = R.alteredDigest;
    const dust = Array.from({ length: 80 }, (_, i) => ({ x: hash(i, 31) * 1920, y: hash(i, 32) * 1080, v: 8 + hash(i, 33) * 22, r: 0.8 + hash(i, 34) * 1.6, a: 0.06 + hash(i, 35) * 0.14 }));
    function frame(_, T) {
      const f = Math.floor(T * 30);
      const rnd = i => HEX[Math.floor(hash(i * 7 + 3, f) * 16)];
      const settled = (i, t0, dur) => T >= t0 + dur * (0.15 + 0.85 * i / 63);
      const sweep = (t0, dur) => ((T - t0) / dur) * 64;
      for (let i = 0; i < 64; i++) {
        // record digest
        if (T < C.scan + 0.2) dgL.paint(i, '·', 'ph');
        else if (T < C.scan + 1.4) settled(i, C.scan + 0.2, 1.2) ? dgL.paint(i, H0[i], '') : dgL.paint(i, rnd(i), 'rnd');
        else if (T < C.edit + 0.7) dgL.paint(i, H0[i], T >= 45.4 && T < C.tamper ? 'eq' : '');
        else if (T < C.compare) settled(i, C.edit + 0.7, 0.75) ? dgL.paint(i, H1[i], '') : dgL.paint(i, rnd(i), 'rnd');
        else if (T < C.unreachable) { const head = sweep(C.compare, 0.6); dgL.paint(i, H1[i], i < head - 1 ? (H1[i] !== H0[i] ? 'bad' : 'same') : i < head + 1 ? 'head' : ''); }
        else if (T < C.unreachable + 0.5) settled(i, C.unreachable, 0.5) ? dgL.paint(i, H0[i], '') : dgL.paint(i, rnd(i + 64), 'rnd');
        else if (T < C.click) dgL.paint(i, H0[i], '');
        else { const head = sweep(C.click + 0.15, 0.8); dgL.paint(i, H0[i], i < head - 1 ? 'ok' : i < head + 1 ? 'head' : ''); }
        // chain commitment
        if (T < C.stamp) dgR.paint(i, '·', 'ph');
        else if (T < C.stamp + 0.6) settled(i, C.stamp, 0.6) ? dgR.paint(i, H0[i], '') : dgR.paint(i, rnd(i + 128), 'rnd');
        else if (T < C.compare) dgR.paint(i, H0[i], T >= 45.4 && T < C.tamper ? 'eq' : '');
        else if (T < C.unreachable) { const head = sweep(C.compare, 0.6); dgR.paint(i, H0[i], i < head - 1 ? (H1[i] !== H0[i] ? 'bad' : 'same') : i < head + 1 ? 'head' : ''); }
        else if (T < C.powerDown + 0.2) dgR.paint(i, H0[i], '');
        else if (T < C.restore) i < sweep(C.powerDown + 0.2, 0.6) ? dgR.paint(i, '·', 'dead') : dgR.paint(i, H0[i], 'same');
        else if (T < C.restore + 0.6) settled(i, C.restore, 0.6) ? dgR.paint(i, H0[i], '') : dgR.paint(i, rnd(i + 128), 'rnd');
        else if (T < C.click) dgR.paint(i, H0[i], '');
        else { const head = sweep(C.click + 0.15, 0.8); dgR.paint(i, H0[i], i < head - 1 ? 'ok' : i < head + 1 ? 'head' : ''); }
      }
      // amount digits
      const A = '4,950.00', B = '9,450.00';
      const roll = (to, t0, dur) => [...to].map((ch, i) => (!/\d/.test(ch) || T >= t0 + dur * (0.3 + 0.7 * i / (to.length - 1)) ? ch : String(Math.floor(hash(i * 13 + 1, f) * 10)))).join('');
      let text = A, altered = false;
      if (T >= C.edit && T < C.edit + 0.6) { text = roll(B, C.edit, 0.6); altered = true; }
      else if (T >= C.edit + 0.6 && T < C.unreachable) { text = B; altered = true; }
      else if (T >= C.unreachable && T < C.unreachable + 0.4) text = roll(A, C.unreachable, 0.4);
      amount.textContent = '₱' + text;
      amount.classList.toggle('bad', altered);
      // chain power
      blocks.forEach((b, i) => {
        const down = C.powerDown + i * 0.12, up = C.restore + i * 0.14;
        let p = 1;
        if (T >= down && T < down + 0.45) p = hash(f, i + 40) > 0.5 ? 1 : 0.3;
        else if (T >= down + 0.45 && T < up) p = 0.26;
        else if (T >= up && T < up + 0.35) p = hash(f, i + 50) > 0.45 ? 1 : 0.3;
        b.power.style.opacity = p;
      });
      // dust and the packet's trail
      g.clearRect(0, 0, 1920, 1080);
      for (const d of dust) {
        const y = (((d.y - d.v * T) % 1080) + 1080) % 1080;
        g.fillStyle = `rgba(190,225,220,${d.a})`;
        g.beginPath(); g.arc(d.x + Math.sin(T * 0.4 + d.y) * 12, y, d.r, 0, 7); g.fill();
      }
      if (T >= C.send && T < C.stamp + 0.5) {
        const u = ease.inOut(clamp((T - C.send) / (C.stamp - C.send)));
        const p = onPath(u);
        packet.style.transform = `translate3d(${p.x.toFixed(2)}px,${p.y.toFixed(2)}px,0) scale(${lerp(0.7, 1, clamp((T - C.send) / 0.3)).toFixed(3)})`;
        const fade = 1 - clamp((T - C.stamp) / 0.5);
        for (let k = 1; k < 34; k++) {
          const q = onPath(Math.max(0, u - k * 0.012));
          g.fillStyle = `rgba(143,240,214,${(0.5 * (1 - k / 34) * fade).toFixed(3)})`;
          g.beginPath(); g.arc(q.x, q.y, 7 * (1 - k / 34) + 1, 0, 7); g.fill();
        }
      }
    }
    scene(el, C.concept, C.end, frame);
  })();

  // ---------- 6. end card ----------
  (function end() {
    const el = h('section', { class: 'scene dark' });
    stage.append(el);
    const glow = h('div', { class: 'glow teal', style: { background: 'radial-gradient(1100px 700px at 50% 42%,#1f6b6170,transparent 70%)' } });
    el.append(glow);
    const L = lockup(el, 420);
    const t = C.end;
    tw(glow, t, 1.2, { o: [0, 1] }, 'outSoft');
    tw(L.mark.el, t + 0.05, 0.12, { o: [0, 1] }, 'linear');
    tw(L.mark.el, t + 0.05, 1.0, { s: [0.2, 1] }, 'spring');
    tw(L.mark.body, t + 0.1, 0.8, { dash: [1, 0] }, 'inOut');
    tw(L.mark.tick, t + 0.6, 0.4, { dash: [1, 0] }, 'out');
    stagger(L.chars, t + 0.3, 0.75, { yp: [130, 0] }, 'out', 0.035);
    stagger(split(L.tagline), t + 0.95, 0.8, { yp: [130, 0] }, 'out', 0.07);
    tw(L.group, t, 6, { s: [1, 1.04] }, 'linear');
    const roles = [['house', 'Beneficiary'], ['users', 'Barangay Officer'], ['landmark', 'DSWD Officer'], ['banknote', 'Disbursing Officer'], ['scan', 'Auditor']].map(([i, text]) => h('div', {}, icon(i, 22), h('span', { text })));
    el.append(h('div', { class: 'roles' }, roles));
    stagger(roles, t + 1.6, 0.6, { o: [0, 1], y: [14, 0] }, 'out', 0.08);
    const foot = h('div', { class: 'foot', html: 'Five-role MVP for local evaluation · synthetic records only · chain checks use actual reads<br>There is no sign-in yet. National ID checks and SMS notices are simulated.' });
    el.append(foot);
    tw(foot, t + 2.4, 0.8, { o: [0, 1] }, 'outSoft');
    const black = h('div', { class: 'black' });
    el.append(black);
    tw(black, C.fade, 0.9, { o: [0, 1] }, 'inOut');
    scene(el, C.end, C.duration + 0.5);
  })();
};
