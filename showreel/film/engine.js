// A small deterministic animation engine: every style is a pure function of time,
// so the film can be scrubbed, played live, or rendered frame by frame.
(() => {
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = t => ((ax * t + bx) * t + cx) * t;
    const sy = t => ((ay * t + by) * t + cy) * t;
    const dx = t => (3 * ax * t + 2 * bx) * t + cx;
    return x => {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 10; i++) {
        const e = sx(t) - x;
        if (Math.abs(e) < 1e-6) break;
        const d = dx(t);
        if (Math.abs(d) < 1e-6) break;
        t = clamp(t - e / d);
      }
      return sy(t);
    };
  }

  const ease = {
    linear: t => t,
    out: bezier(0.16, 1, 0.3, 1),        // long, confident settle
    outSoft: bezier(0.22, 0.61, 0.36, 1),
    inOut: bezier(0.65, 0, 0.35, 1),
    swift: bezier(0.83, 0, 0.17, 1),     // whip moves
    in: bezier(0.7, 0, 0.84, 0),
    back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    spring: t => (t >= 1 ? 1 : 1 - Math.exp(-6.5 * t) * Math.cos(10.5 * t)),
    springSoft: t => (t >= 1 ? 1 : 1 - Math.exp(-5.2 * t) * Math.cos(6.2 * t)),
  };

  // Seeded noise so "random" motion is identical on every render.
  function rng(seed) {
    let a = seed >>> 0;
    return () => {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const hash = (a, b = 0) => {
    let h = Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  };

  const DEFAULTS = { x: 0, y: 0, z: 0, xp: 0, yp: 0, s: 1, sx: 1, sy: 1, r: 0, rx: 0, ry: 0, o: 1, blur: 0, ct: 0, cr: 0, cb: 0, cl: 0, circ: 0, ox: 0, oy: 0, w: 0, h: 0, dash: 0 };
  const TRANSFORM = ['x', 'y', 'z', 'xp', 'yp', 's', 'sx', 'sy', 'r', 'rx', 'ry'];
  const tracks = new Map();
  const scenes = [];
  let sorted = false;

  function list(target) {
    if (!target) return [];
    if (target instanceof Element) return [target];
    return Array.from(target);
  }

  // tw(el, start, duration, {prop: to | [from, to]}, easing)
  function tw(target, t0, dur, props, e = 'out') {
    for (const el of list(target)) {
      let track = tracks.get(el);
      if (!track) tracks.set(el, (track = {}));
      for (const [prop, value] of Object.entries(props)) {
        const items = track[prop] || (track[prop] = []);
        const last = items[items.length - 1];
        const base = last ? last.to : (prop in DEFAULTS ? DEFAULTS[prop] : 0);
        const [from, to] = Array.isArray(value) ? value : [base, value];
        items.push({ t0, dur: Math.max(dur, 1e-4), from, to, e: typeof e === 'function' ? e : ease[e] });
      }
    }
    sorted = false;
  }
  function stagger(target, t0, dur, props, e = 'out', each = 0.05) {
    list(target).forEach((el, i) => tw(el, t0 + i * each, dur, props, e));
  }
  const set = (target, t, props) => tw(target, t, 1e-4, props, 'linear');

  function valueAt(items, T) {
    let current = null;
    for (const item of items) { if (item.t0 <= T) current = item; else break; }
    if (!current) return items[0].from;
    return lerp(current.from, current.to, current.e(clamp((T - current.t0) / current.dur)));
  }

  function apply(el, track, T) {
    const v = {};
    for (const prop in track) v[prop] = valueAt(track[prop], T);
    const style = el.style;
    if ('o' in v) {
      style.opacity = v.o.toFixed(4);
      style.visibility = v.o <= 0.001 ? 'hidden' : 'visible';
    }
    if (TRANSFORM.some(p => p in v)) {
      const g = p => (p in v ? v[p] : DEFAULTS[p]);
      let t = `translate3d(${g('x').toFixed(3)}px,${g('y').toFixed(3)}px,${g('z').toFixed(3)}px)`;
      if ('xp' in v || 'yp' in v) t += ` translate(${g('xp').toFixed(3)}%,${g('yp').toFixed(3)}%)`;
      if ('rx' in v) t += ` rotateX(${v.rx.toFixed(4)}deg)`;
      if ('ry' in v) t += ` rotateY(${v.ry.toFixed(4)}deg)`;
      if ('r' in v) t += ` rotate(${v.r.toFixed(4)}deg)`;
      const sx = g('s') * g('sx'), sy = g('s') * g('sy');
      if (sx !== 1 || sy !== 1) t += ` scale(${sx.toFixed(5)},${sy.toFixed(5)})`;
      style.transform = t;
    }
    if ('ox' in v || 'oy' in v) style.transformOrigin = `${(v.ox || 0).toFixed(2)}px ${(v.oy || 0).toFixed(2)}px`;
    if ('blur' in v) style.filter = v.blur > 0.05 ? `blur(${v.blur.toFixed(2)}px)` : 'none';
    if ('ct' in v || 'cr' in v || 'cb' in v || 'cl' in v) {
      const g = p => (p in v ? v[p] : 0).toFixed(3);
      style.clipPath = `inset(${g('ct')}% ${g('cr')}% ${g('cb')}% ${g('cl')}%)`;
    }
    if ('circ' in v) style.clipPath = `circle(${Math.max(0, v.circ).toFixed(2)}px at ${el.dataset.cx || 960}px ${el.dataset.cy || 540}px)`;
    if ('w' in v) style.width = `${v.w.toFixed(2)}px`;
    if ('h' in v) style.height = `${v.h.toFixed(2)}px`;
    if ('dash' in v) style.strokeDashoffset = v.dash.toFixed(3);
    for (const prop in v) if (prop.startsWith('--')) style.setProperty(prop, v[prop].toFixed(4));
  }

  function scene(el, start, end, frame) {
    scenes.push({ el, start, end, frame });
    return el;
  }

  function seek(T) {
    if (!sorted) {
      for (const track of tracks.values()) for (const prop in track) track[prop].sort((a, b) => a.t0 - b.t0);
      sorted = true;
    }
    for (const s of scenes) {
      const active = T >= s.start && T < s.end;
      s.el.style.display = active ? 'block' : 'none';
      s.active = active;
    }
    for (const [el, track] of tracks) apply(el, track, T);
    for (const s of scenes) if (s.active && s.frame) s.frame(T - s.start, T);
  }

  function h(tag, attrs = {}, ...children) {
    const svg = ['svg', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'g', 'defs', 'linearGradient', 'stop'].includes(tag);
    const el = svg ? document.createElementNS('http://www.w3.org/2000/svg', tag) : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
      else if (k === 'text') el.textContent = v;
      else if (k === 'html') el.innerHTML = v;
      else el.setAttribute(k, v);
    }
    for (const child of children.flat()) if (child != null) el.append(child);
    return el;
  }

  // Wraps words or characters in clipping masks for line-reveal typography.
  function split(el, mode = 'words') {
    const text = el.textContent;
    el.textContent = '';
    const parts = mode === 'chars' ? [...text] : text.split(' ');
    return parts.map((part, i) => {
      const inner = h('span', { class: 'i', text: part === ' ' ? ' ' : part });
      el.append(h('span', { class: 'm' }, inner));
      if (mode === 'words' && i < parts.length - 1) el.append(' ');
      return inner;
    });
  }

  window.FX = { clamp, lerp, bezier, ease, rng, hash, tw, stagger, set, scene, seek, h, split };
})();
