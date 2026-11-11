// Small helpers for authoring Lottie (Bodymovin) JSON for Skia Skottie.
export const W = 1920, H = 1080, FR = 30;

export const C = {
  ink: '#0a0b10', black: '#000000', gold: '#e8c170', goldHi: '#fff0c4', goldDim: '#a8894a',
  white: '#f4efe4', crimson: '#8e1b1b', parchment: '#d8c79c', halo: '#4a3a1e', night: '#101524',
};

export const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);

// cubic-bezier presets, chosen per motion behaviour
export const E = {
  out: [0.16, 1, 0.3, 1], inOut: [0.65, 0, 0.35, 1], in: [0.55, 0, 0.9, 0.5],
  lin: [0.3, 0.3, 0.7, 0.7], soft: [0.4, 0, 0.2, 1],
};

const K = v => ({ a: 0, k: v });
const P = v => (v && typeof v === 'object' && !Array.isArray(v) && 'a' in v ? v : K(v));

/** Keyframes: A([[t, value, ease?], ...]) — ease applies to the segment leaving that key. */
export function A(frames) {
  if (frames.length === 1) return K(frames[0][1]);
  return {
    a: 1,
    k: frames.map(([t, v, e], i) => {
      const s = Array.isArray(v) ? v : [v];
      if (i === frames.length - 1) return { t, s };
      const [x1, y1, x2, y2] = e || E.inOut;
      return { t, s, o: { x: [x1], y: [y1] }, i: { x: [x2], y: [y2] } };
    }),
  };
}

export const tf = ({ p = [0, 0], a = [0, 0], s = [100, 100], r = 0, o = 100 } = {}) =>
  ({ p: P(p), a: P(a), s: P(s), r: P(r), o: P(o) });

// ---- shape items -------------------------------------------------------
export const fill = (c, o = 100) => ({ ty: 'fl', c: K([...hex(c), 1]), o: P(o), r: 1 });
export const stroke = (c, w, o = 100) => ({ ty: 'st', c: K([...hex(c), 1]), o: P(o), w: P(w), lc: 2, lj: 2 });
export const trim = (s, e) => ({ ty: 'tm', s: P(s), e: P(e), o: K(0), m: 1 });
export const ellipse = (x, y, w, h = w) => ({ ty: 'el', p: K([x, y]), s: K([w, h]) });
export const rect = (x, y, w, h, r = 0) => ({ ty: 'rc', p: K([x + w / 2, y + h / 2]), s: K([w, h]), r: K(r) });

/** Radial gradient that fades `c` from alpha a0 at centre to a1 at radius r. */
export const radial = (c, r, a0 = 1, a1 = 0, o = 100) => {
  const [R, G, B] = hex(c);
  return { ty: 'gf', t: 2, o: P(o), r: 1, s: K([0, 0]), e: K([r, 0]),
    g: { p: 3, k: K([0, R, G, B, 0.45, R, G, B, 1, R, G, B, 0, a0, 0.45, a0 * 0.28 + a1 * 0.72, 1, a1]) } };
};
/** Linear vertical gradient through colour stops [[pos, hex], ...]. */
export const linear = (y0, y1, stops) => ({ ty: 'gf', t: 1, o: K(100), r: 1, s: K([0, y0]), e: K([0, y1]),
  g: { p: stops.length, k: K(stops.flatMap(([p, c]) => [p, ...hex(c)])) } });

/** Vertical gradient of one colour whose alpha runs a0 -> a1 (for scrims). */
export const linearA = (y0, y1, c, a0, a1) => {
  const [R, G, B] = hex(c);
  return { ty: 'gf', t: 1, o: K(100), r: 1, s: K([0, y0]), e: K([0, y1]), g: { p: 2, k: K([0, R, G, B, 1, R, G, B, 0, a0, 1, a1]) } };
};

/** Polygon / smooth path. Points: [x, y] smooth (when smooth=true) or [x, y, 'c'] corner. */
export function path(pts, { closed = true, smooth = false, tension = 1 } = {}) {
  const n = pts.length, v = [], i = [], o = [];
  for (let k = 0; k < n; k++) {
    const [x, y, flag] = pts[k];
    v.push([x, y]);
    const prev = pts[closed ? (k - 1 + n) % n : Math.max(k - 1, 0)];
    const next = pts[closed ? (k + 1) % n : Math.min(k + 1, n - 1)];
    if (!smooth || flag === 'c') { i.push([0, 0]); o.push([0, 0]); continue; }
    const tx = ((next[0] - prev[0]) / 6) * tension, ty = ((next[1] - prev[1]) / 6) * tension;
    i.push([-tx, -ty]); o.push([tx, ty]);
  }
  return { ty: 'sh', ks: K({ c: closed, v, i, o }) };
}

export const group = (items, t = {}, nm = 'g') => ({ ty: 'gr', nm, it: [...items, { ty: 'tr', ...tf(t) }] });

// ---- layers ------------------------------------------------------------
export const shape = (nm, shapes, t = {}, extra = {}) => ({ ty: 4, nm, ks: tf(t), shapes, ...extra });
export const nul = (nm, t = {}) => ({ ty: 3, nm, ks: tf(t) });
/** Still image layer; `file` sits next to lottie.json. Anchor is the image centre. */
export const image = (nm, file, w, h, t = {}) => ({ ty: 2, nm, refId: file, ks: tf({ a: [w / 2, h / 2], ...t }), _asset: { id: file, w, h, u: '', p: file, e: 0 } });

export const FONTS = {
  R: { fName: 'NotoSerifKR-Regular', fFamily: 'Noto Serif KR', fStyle: 'Regular', ascent: 75 },
  B: { fName: 'NotoSerifKR-Bold', fFamily: 'Noto Serif KR', fStyle: 'Bold', ascent: 75 },
};

export function text(nm, str, { x = W / 2, y, size, font = 'R', color = C.white, track = 0, o = 100, s = [100, 100], animators = [], sid } = {}) {
  const doc = { s: size, f: FONTS[font].fName, t: str, j: 2, tr: track, lh: size * 1.35, ls: 0, fc: hex(color) };
  const d = { k: [{ t: 0, s: doc }] };
  if (sid) d.sid = sid;
  return { ty: 5, nm, ks: tf({ p: [x, y], o, s }), _slot: sid ? { sid, doc } : null,
    t: { d, p: {}, m: { g: 1, a: K([0, 0]) }, a: animators } };
}

/** Fade-in / hold / fade-out opacity track. */
export const fade = (tIn, tOut, max = 100, dIn = 22, dOut = 16) =>
  A([[tIn, 0, E.out], [tIn + dIn, max, E.lin], [tOut - dOut, max, E.in], [tOut, 0]]);

/** Layers are authored bottom-to-top; Lottie wants top-first. */
export function comp(nm, op, layers, { bg = C.ink } = {}) {
  const assets = [];
  const slots = { bgColor: { p: K([...hex(bg), 1]) } };
  const bgLayer = shape('background', [rect(0, 0, W, H), { ty: 'fl', c: { a: 0, k: [...hex(bg), 1], sid: 'bgColor' }, o: K(100), r: 1 }]);
  const all = [bgLayer, ...layers.flat(Infinity).filter(Boolean)];
  const names = new Map(all.map((l, i) => [l.nm, i + 1]));
  const out = all.map((l, i) => {
    const { _slot, _asset, parent, ...rest } = l;
    if (_asset && !assets.some(a => a.id === _asset.id)) assets.push(_asset);
    if (_slot) slots[_slot.sid] = { p: { a: 1, k: [{ t: 0, s: _slot.doc }] } };
    const base = { ddd: 0, ind: i + 1, ip: 0, op, st: 0, sr: 1, ao: 0, bm: 0, ...rest };
    if (parent) {
      if (!names.has(parent)) throw new Error(`${nm}: unknown parent ${parent}`);
      base.parent = names.get(parent);
    }
    return base;
  }).reverse();
  return { v: '5.7.0', fr: FR, ip: 0, op, w: W, h: H, nm, ddd: 0, assets, fonts: { list: [FONTS.R, FONTS.B] }, slots, layers: out };
}
