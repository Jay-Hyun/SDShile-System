/* Design kit v5: "두 개의 방, 하나의 집" — one premium miniature world, one motion language.
 *
 * Plates     GPT-generated miniature sets (scripts/gen_v5.py -> assets/media/gen5/<id>.png). Most become
 *            depth-parallax camera moves (assets/media/living5/<id>.mp4); plates with a chroma-green frame,
 *            mirror or screen are keyed (scripts/key_green.py) and the real footage sits inside the hole.
 * Type       the whole line is set first in a quiet tone; each word lights at its sung onset (two-tone colour per
 *            background: warm grey -> ink on light sets, grey-white -> ivory on dark sets; never opacity alone).
 *            SING = Noto Serif KR, RAP = Pretendard (row stack, the active row bright, older rows recede),
 *            meta = Cormorant italic. Heroes enter with blur + opacity, never scale or bounce.
 * Camera     slow dolly/truck in the clips, hard cuts on the beat, no shakes, no flashes, no springs.
 * Everything is seek-safe: one paused anime timeline per scene, bridged from GSAP (K.bridge).
 */
(function () {
  const PAL = {
    cream: "#F1ECE2",
    paper: "#F7F2E8",
    cobalt: "#2B3BCF",
    coral: "#F08C8C",
    coralD: "#C24F5C",
    lilac: "#B8B2EA",
    ink: "#232024",
    brass: "#B08D57",
    brassL: "#D2B27A",
    night: "#0E1022",
  };

  const css = `
  .v5-shot { position:absolute; inset:0; overflow:hidden; isolation:isolate; background:#0c0b0a; }
  .v5-cam { position:absolute; inset:0; transform-origin:50% 50%; }
  .v5-cover { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; display:block; }
  .v5-win { position:absolute; overflow:hidden; background:#1b1917; }
  .v5-glass { position:absolute; inset:0; pointer-events:none;
    background: linear-gradient(128deg, rgba(255,250,240,.16) 0%, rgba(255,250,240,.05) 26%, rgba(255,250,240,0) 46%),
                radial-gradient(ellipse 120% 120% at 50% 50%, rgba(0,0,0,0) 62%, rgba(10,8,6,.34) 100%);
    box-shadow: inset 0 3px 12px rgba(20,14,8,.32), inset 0 0 2px rgba(20,14,8,.4); }
  .v5-line { position:absolute; white-space:nowrap; }
  .v5-row { display:block; }
  .v5-w { display:inline-block; }
  .v5-serif { font-family:"Noto Serif KR"; font-weight:600; letter-spacing:-0.01em; line-height:1.34; }
  .v5-serifL { font-family:"Noto Serif KR"; font-weight:500; letter-spacing:0; line-height:1.34; }
  .v5-serifB { font-family:"Noto Serif KR"; font-weight:700; letter-spacing:-0.02em; line-height:1.2; }
  .v5-sans { font-family:"Pretendard"; font-weight:700; letter-spacing:-0.02em; line-height:1.28; }
  .v5-sansB { font-family:"Pretendard"; font-weight:800; letter-spacing:-0.035em; line-height:1.1; }
  .v5-sansK { font-family:"Pretendard"; font-weight:900; letter-spacing:-0.045em; line-height:1.0; }
  .v5-meta { font-family:"Cormorant"; font-style:italic; letter-spacing:0.04em; font-variant-numeric:lining-nums; }
  .c-ink { color:${PAL.ink}; text-shadow: 0 1px 10px rgba(250,246,238,.42); }
  .c-cream { color:#F8F3EA; text-shadow: 0 2px 8px rgba(18,14,22,.46), 0 0 2px rgba(18,14,22,.30); }
  .c-coral { color:${PAL.coral}; text-shadow: 0 2px 8px rgba(18,14,22,.46), 0 0 2px rgba(18,14,22,.30); }
  .c-brass { color:${PAL.brassL}; text-shadow: 0 2px 8px rgba(18,14,22,.40); }
  .c-ink .love { color:${PAL.coralD}; }
  .c-cream .love { color:${PAL.coral}; }
  .v5-rule { position:absolute; height:2px; background:${PAL.brass}; transform-origin:0 50%; }
  .v5-scrim { position:absolute; pointer-events:none; }
  `;
  const st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  const E = K.ease;
  const px = (v) => (typeof v === "number" ? v + "px" : v);
  // unlit / lit / lit-love colours per background tone (the line must read before it is sung)
  const TONE = {
    ink: { dim: "#665d56", lit: "#232024", love: "#c24f5c" },
    cream: { dim: "#b9b1a6", lit: "#fbf6ec", love: "#f49a9a" },
  };
  const tone = (c) => TONE[c] || TONE.cream;

  /** CSS matrix3d that maps a w x h box (origin 0 0) onto quad q = [TL, TR, BR, BL] (perspective-correct). */
  function quadMatrix(w, h, q) {
    const src = [[0, 0], [w, 0], [w, h], [0, h]];
    const A = [];
    src.forEach(([x, y], i) => {
      const [u, v] = q[i];
      A.push([x, y, 1, 0, 0, 0, -u * x, -u * y, u]);
      A.push([0, 0, 0, x, y, 1, -v * x, -v * y, v]);
    });
    for (let c = 0; c < 8; c++) {
      let p = c;
      for (let r = c + 1; r < 8; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]];
      for (let r = 0; r < 8; r++) {
        if (r === c) continue;
        const f = A[r][c] / A[c][c];
        for (let k = c; k < 9; k++) A[r][k] -= f * A[c][k];
      }
    }
    const [a, b, c, d, e, f, g, hh] = A.map((r, i) => r[8] / r[i]);
    return `matrix3d(${a},${d},0,${g},${b},${e},0,${hh},0,0,1,0,${c},${f},0,1)`;
  }

  const D = {
    PAL,

    /** Scene context: the paused timelines, flat word list W, word time T(i), and the stage element. */
    scene(id, { lead = 60 } = {}) {
      const S = K.scene(id);
      const at = K.timeline();
      const gtl = gsap.timeline({ paused: true });
      const W = K.flat(S, lead);
      const END = Math.round(S.dur * 1000);
      const T = (i) => (W[i] ? W[i].ms : END);
      // Q(i): the beat-grid cut for a shot that opens on word i (scripts/build_data.py); B(n): beat n, scene-local ms
      const Q = (i) => (i === 0 ? 0 : W[i] ? (W[i].q != null ? W[i].q : W[i].ms) : END);
      const B = (n) => S.beat(n);
      const stage = document.getElementById(id + "-stage");
      return { id, S, at, gtl, W, T, Q, B, END, stage };
    },

    finish(ctx) {
      K.bridge(ctx.gtl, ctx.at, ctx.S.dur);
      window.__timelines[ctx.id] = ctx.gtl;
    },

    /** Beat time (scene-local ms) nearest to ms. */
    onBeat(ctx, ms) {
      const n = Math.round((ms / 1000 + ctx.S.start - K.FILM.firstBeat) / K.FILM.beatPeriod);
      return ctx.S.beat(n);
    },

    /** A full-frame shot visible over [t0, t1): `shot` owns visibility, `cam` the camera move. */
    shot(ctx, t0, t1, { bg = null } = {}) {
      const shot = K.el("div", "v5-shot", ctx.stage);
      if (bg) shot.style.background = bg;
      K.window(ctx.at, shot, Math.max(0, t0), t1);
      const cam = K.el("div", "v5-cam", shot);
      return { shot, cam, t0, t1 };
    },

    /** A transparent overlay over [t0, t1) that sits above the shots (lyrics that run across cuts). */
    layer(ctx, t0, t1, { z = 40 } = {}) {
      const l = K.el("div", "", ctx.stage);
      l.style.cssText = `position:absolute;inset:0;pointer-events:none;z-index:${z}`;
      K.window(ctx.at, l, Math.max(0, t0), t1);
      return l;
    },

    /** Move a declared <video> (a depth-parallax plate or real footage) into parent as a cover layer. */
    take(id, parent, { pos = null, grade = null } = {}) {
      const v = document.getElementById(id);
      v.classList.add("v5-cover");
      if (pos) v.style.objectPosition = pos;
      if (grade) v.style.filter = grade;
      parent.appendChild(v);
      return v;
    },

    /** Camera move on any layer: from/to = {x, y, s, r}. */
    move(ctx, el, t0, t1, { from = {}, to = {}, ease = "linear", origin = null } = {}) {
      const f = { x: 0, y: 0, s: 1, r: 0, ...from };
      const g = { x: 0, y: 0, s: 1, r: 0, ...to };
      if (origin) el.style.transformOrigin = origin;
      ctx.at.set(el, { x: f.x, y: f.y, scale: f.s, rotate: f.r }, 0);
      ctx.at.add(el, { x: [f.x, g.x], y: [f.y, g.y], scale: [f.s, g.s], rotate: [f.r, g.r], duration: Math.max(1, t1 - t0), ease: E[ease] || ease }, t0);
      return el;
    },

    /** A still plate (cover) with a slow camera move. */
    still(ctx, parent, src, t0, t1, opts = {}) {
      const img = K.el("img", "v5-cover", parent);
      img.src = src;
      img.alt = "";
      if (opts.pos) img.style.objectPosition = opts.pos;
      D.move(ctx, img, t0, t1, opts);
      return img;
    },

    /** Green-key composite. The keyed plate (with transparent holes) sits on top; under each hole a window
     *  holds media: { video: id } | { src } | { build(win) }. `window.GREEN[id]` = {W, H, holes:[{x,y,w,h}]}.
     *  The plate is fitted to 1920 wide (centred vertically); move it with opts.from/to like D.move. */
    keyed(ctx, parent, id, media, t0, t1, opts = {}) {
      const R = window.GREEN[id];
      const k = 1920 / R.W;
      const H = R.H * k;
      const box = K.el("div", "", parent);
      box.style.cssText = `position:absolute;left:0;top:${(1080 - H) / 2 + (opts.dy || 0)}px;width:1920px;height:${H}px;transform-origin:50% 50%`;
      const wins = R.holes.map((h, j) => {
        const m = media[j];
        if (!m) return null;
        const pad = 6;
        const win = K.el("div", "v5-win", box);
        if (h.quad) {
          // the picture lies in the plane of the frame: warp the window onto the frame's quad
          const cx = h.quad.reduce((s, p) => s + p[0], 0) / 4;
          const cy = h.quad.reduce((s, p) => s + p[1], 0) / 4;
          const q = h.quad.map(([x, y]) => {
            const L = Math.hypot(x - cx, y - cy) || 1;
            return [(x + ((x - cx) / L) * pad) * k, (y + ((y - cy) / L) * pad) * k];
          });
          const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
          const ww = (dist(q[0], q[1]) + dist(q[3], q[2])) / 2;
          const hh = (dist(q[0], q[3]) + dist(q[1], q[2])) / 2;
          win.style.cssText += `;left:0;top:0;width:${ww}px;height:${hh}px;transform-origin:0 0;transform:${quadMatrix(ww, hh, q)}`;
        } else {
          win.style.left = (h.x - pad) * k + "px";
          win.style.top = (h.y - pad) * k + "px";
          win.style.width = (h.w + 2 * pad) * k + "px";
          win.style.height = (h.h + 2 * pad) * k + "px";
        }
        const grade = m.grade || "saturate(.9) contrast(.95) brightness(.94) sepia(.1)";
        if (m.video) D.take(m.video, win, { pos: m.pos, grade });
        else if (m.src) {
          const img = K.el("img", "v5-cover", win);
          img.src = m.src;
          img.alt = "";
          if (m.pos) img.style.objectPosition = m.pos;
          img.style.filter = grade;
        }
        if (m.build) m.build(win, grade);
        K.el("div", "v5-glass", win);
        return win;
      });
      const plate = K.el("img", "", box);
      plate.src = `assets/media/gen5/${id}_keyed.png`;
      plate.alt = "";
      plate.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%";
      if (opts.manual) {
        if (opts.origin) box.style.transformOrigin = opts.origin;
      } else D.move(ctx, box, t0, t1, opts);
      return { box, wins, k };
    },

    /** Lyric line(s), karaoke style: the line is set first (dim), each word lights at its onset.
     *  idx = [i, ...] or [[row1...], [row2...]]. align: left | center | right (x is the anchor). */
    line(ctx, parent, idx, o = {}) {
      const { x = 960, y = 140, align = "center", size = 64, font = "serif", color = "ink", love = [], lead = 300, enter = 560, end = null, out = 300, gap = 1.34, z = 30, drift = 10 } = o;
      const rows = Array.isArray(idx[0]) ? idx : [idx];
      const box = K.el("div", `v5-line v5-${font} c-${color}`, parent);
      box.style.fontSize = size + "px";
      box.style.top = px(y);
      box.style.zIndex = z;
      box.style.lineHeight = String(gap);
      if (align === "center") {
        box.style.left = "0px";
        box.style.right = "0px";
        box.style.textAlign = "center";
      } else if (align === "left") {
        box.style.left = px(x);
      } else {
        box.style.right = px(1920 - x);
        box.style.textAlign = "right";
      }
      const words = [];
      rows.forEach((r) => {
        const row = K.el("div", "v5-row", box);
        r.forEach((i, k) => {
          const sp = K.el("span", "v5-w" + (love.includes(i) ? " love" : ""), row, o.text && o.text[i] != null ? o.text[i] : ctx.W[i].t);
          if (k < r.length - 1) row.appendChild(document.createTextNode(" "));
          words.push({ sp, i });
        });
      });
      const at = ctx.at;
      const tIn = Math.max(0, ctx.T(rows[0][0]) - lead);
      at.set(box, { opacity: 0 }, 0);
      at.add(box, { opacity: [0, 1], filter: ["blur(8px)", "blur(0px)"], duration: enter, ease: E.expo }, tIn);
      // the type floats up a few pixels while it is on screen, so it never sits dead on a moving plate
      if (drift) at.add(box, { y: [drift / 2, -drift / 2], duration: 4000, ease: "linear" }, tIn);
      words.forEach(({ sp, i }) => {
        const c = tone(color);
        const lit = sp.classList.contains("love") ? c.love : c.lit;
        at.set(sp, { color: c.dim }, 0);
        at.add(sp, { color: [c.dim, lit], duration: 170, ease: E.quart }, Math.max(tIn + 1, ctx.T(i)));
      });
      if (end != null) D.out(ctx, box, end - out, out);
      return box;
    },

    /** Rap stack: rows enter at their first word, words light at onset, the active row is bright and
     *  older rows recede. rows = [[i...], ...]. */
    rap(ctx, parent, rows, o = {}) {
      const { x = 120, y = 300, size = 64, color = "cream", font = "sans", love = [], recede = 0.5, gap = 1.3, end = null, out = 260, lead = 160, z = 30, align = "left", rot = 0, drift = 8 } = o;
      const at = ctx.at;
      const box = K.el("div", `v5-line v5-${font} c-${color}`, parent);
      const anchor = align === "right" ? `right:${1920 - x}px;text-align:right` : `left:${x}px`;
      box.style.cssText += `;${anchor};top:${y}px;font-size:${size}px;line-height:${gap};z-index:${z};transform-origin:0 0`;
      at.set(box, { rotate: rot, y: drift / 2 }, 0);
      if (drift) at.add(box, { y: [drift / 2, -drift / 2], duration: 5000, ease: "linear" }, Math.max(0, ctx.T(rows[0][0]) - lead));
      const rowEls = rows.map((r) => {
        const row = K.el("div", "v5-row", box);
        r.forEach((i, k) => {
          const sp = K.el("span", "v5-w" + (love.includes(i) ? " love" : ""), row, ctx.W[i].t);
          if (k < r.length - 1) row.appendChild(document.createTextNode(" "));
          const c = tone(color);
          const lit = love.includes(i) ? c.love : c.lit;
          at.set(sp, { color: c.dim }, 0);
          at.add(sp, { color: [c.dim, lit], duration: 120, ease: E.quart }, Math.max(1, ctx.T(i)));
        });
        return row;
      });
      rowEls.forEach((row, k) => {
        const t = Math.max(0, ctx.T(rows[k][0]) - lead);
        at.set(row, { opacity: 0 }, 0);
        at.add(row, { opacity: [0, 1], filter: ["blur(6px)", "blur(0px)"], duration: 380, ease: E.expo }, t);
        if (k + 1 < rows.length) {
          const tn = Math.max(t + 400, ctx.T(rows[k + 1][0]) - lead);
          at.add(row, { opacity: [1, recede], duration: 260, ease: E.quart }, tn);
        }
      });
      if (end != null) D.out(ctx, box, end - out, out);
      return box;
    },

    /** A hero word: blur + opacity in, optional slow creep; never scale-pops. */
    hero(ctx, parent, text, t, o = {}) {
      const { x = 120, y = 200, size = 160, font = "sansK", color = "cream", align = "left", end = null, enter = 520, blur = 12, creep = 0, out = 300, z = 31, spacing = null } = o;
      const css = { top: y, fontSize: size, zIndex: z };
      if (align === "center") Object.assign(css, { left: 0, right: 0, textAlign: "center" });
      else if (align === "left") css.left = x;
      else Object.assign(css, { right: 1920 - x, textAlign: "right" });
      const el = K.txt(parent, text, `v5-hero v5-${font} c-${color}`, css);
      if (spacing) el.style.letterSpacing = spacing;
      const at = ctx.at;
      at.set(el, { opacity: 0 }, 0);
      at.add(el, { opacity: [0, 1], filter: [`blur(${blur}px)`, "blur(0px)"], duration: enter, ease: E.expo }, Math.max(0, t));
      if (creep) at.add(el, { scale: [1, 1 + creep], duration: Math.max(1, (end || ctx.END) - t), ease: "linear" }, Math.max(0, t));
      if (end != null) D.out(ctx, el, end - out, out);
      return el;
    },

    /** Soft exit: opacity to 0 with a little blur. */
    out(ctx, els, t, dur = 300) {
      ctx.at.add(els, { opacity: [1, 0], filter: ["blur(0px)", "blur(6px)"], duration: dur, ease: E.in3 }, Math.max(0, t));
    },

    /** Brushed-brass rule that draws from its origin. */
    rule(ctx, parent, { x, y, w, t, dur = 1000, color = null, origin = "left", z = 30, end = null } = {}) {
      const r = K.el("div", "v5-rule", parent);
      r.style.cssText += `;left:${x}px;top:${y}px;width:${w}px;z-index:${z};transform-origin:${origin === "center" ? "50% 50%" : origin === "right" ? "100% 50%" : "0 50%"}`;
      if (color) r.style.background = color;
      ctx.at.set(r, { scaleX: 0 }, 0);
      ctx.at.add(r, { scaleX: [0, 1], duration: dur, ease: E.expo }, t);
      if (end != null) D.out(ctx, r, end - 300, 300);
      return r;
    },

    /** Legibility scrim along an edge: zone top | bottom | left | right; tone dark | light. */
    scrim(parent, zone, { tone = "dark", a = 0.42, reach = 46, z = 20 } = {}) {
      const s = K.el("div", "v5-scrim", parent);
      const c = tone === "dark" ? "16,13,20" : "246,241,232";
      const dir = { top: "180deg", bottom: "0deg", left: "90deg", right: "270deg" }[zone];
      s.style.cssText += `;inset:0;z-index:${z};background:linear-gradient(${dir}, rgba(${c},${a}) 0%, rgba(${c},${a * 0.55}) ${reach * 0.45}%, rgba(${c},0) ${reach}%)`;
      return s;
    },

    /** Full-frame colour layer that fades in (dir "in": colour -> clear) or out (clear -> colour). */
    fade(ctx, parent, t, dur, { color = "#000", dir = "in", z = 60, ease = null } = {}) {
      const f = K.el("div", "", parent);
      f.style.cssText = `position:absolute;inset:0;background:${color};pointer-events:none;z-index:${z}`;
      const a = dir === "in" ? [1, 0] : [0, 1];
      ctx.at.set(f, { opacity: a[0] }, 0);
      ctx.at.add(f, { opacity: a, duration: dur, ease: E[ease] || (dir === "in" ? E.quart : E.in3) }, t);
      return f;
    },

    /** Warm light bloom: a soft radial glow that swells to full (the bridge -> final chorus wind-up). */
    bloom(ctx, parent, t0, t1, { color = "255,246,226", x = "50%", y = "48%", z = 58 } = {}) {
      const b = K.el("div", "", parent);
      b.style.cssText = `position:absolute;inset:-10%;pointer-events:none;mix-blend-mode:screen;z-index:${z};background:radial-gradient(ellipse 60% 60% at ${x} ${y}, rgba(${color},1) 0%, rgba(${color},.85) 40%, rgba(${color},.6) 100%)`;
      ctx.at.set(b, { opacity: 0 }, 0);
      ctx.at.add(b, { opacity: [0, 1], duration: t1 - t0, ease: E.in3 }, t0);
      return b;
    },
  };

  window.D = D;
})();
