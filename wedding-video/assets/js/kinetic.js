/* Kinetic-type engine for the wedding film.
 *
 * Clock: every scene registers a paused GSAP timeline (the HyperFrames contract) and drives one
 * paused anime.js v4 timeline from it with K.bridge(), so anime is seeked in scene-local time.
 * All times passed to presets are scene-local milliseconds. Scene-local time comes from the edit
 * timeline (data.js: window.FILM) minus the scene's start.
 *
 * Grammar (docs/reference-notes.md): A = N pole (groom, cobalt, Black Han Sans, straight expo moves),
 * B = S pole (bride, pink, Jua, springy), AB = both (violet overprint).
 */
(function () {
  const A = window.anime;
  A.engine.useDefaultMainLoop = false;

  const FILM = window.FILM;
  const BEAT = FILM.beatPeriod * 1000; // ms
  const EXPO = A.cubicBezier(0.16, 1, 0.3, 1);
  const QUART = A.cubicBezier(0.25, 1, 0.5, 1);
  const IN3 = A.cubicBezier(0.55, 0, 1, 0.45);
  const INOUT = A.cubicBezier(0.65, 0, 0.35, 1);
  const BACK = A.cubicBezier(0.34, 1.56, 0.64, 1);
  const GLIDE = A.cubicBezier(0.3, 0.12, 0.25, 1); // a camera move that is already travelling and lands softly
  const SETTLE = A.cubicBezier(0.22, 0.45, 0.35, 1); // a pull-back that keeps an even perceived speed

  /** Closed-form damped spring 0->1 as an anime ease; zeta = damping ratio, omega = rad/s scaled to the tween. */
  function springEase(zeta = 0.5, cycles = 2.2) {
    const w = cycles * 2 * Math.PI;
    return (t) => {
      if (t >= 1) return 1;
      if (zeta < 1) {
        const wd = w * Math.sqrt(1 - zeta * zeta);
        return 1 - Math.exp(-zeta * w * t) * (Math.cos(wd * t) + ((zeta * w) / wd) * Math.sin(wd * t));
      }
      return 1 - Math.exp(-w * t) * (1 + w * t);
    };
  }

  const K = {
    A,
    FILM,
    BEAT,
    ease: { expo: EXPO, quart: QUART, in3: IN3, inout: INOUT, back: BACK, glide: GLIDE, settle: SETTLE, spring: springEase, linear: (t) => t },

    /** Scene helper: local-time conversions for scene `id`. */
    scene(id) {
      const s = FILM.scenes[id];
      return {
        start: s.start,
        dur: s.dur,
        /** edit-timeline seconds -> scene-local ms */
        ms: (sec) => Math.round((sec - s.start) * 1000),
        /** beat index (edit timeline) -> scene-local ms */
        beat: (n) => Math.round((FILM.firstBeat + n * FILM.beatPeriod - s.start) * 1000),
        /** first beat index at or after a scene-local ms */
        beatAt: (ms) => Math.ceil((ms / 1000 + s.start - FILM.firstBeat) / FILM.beatPeriod - 1e-6),
        /** snap scene-local ms to the nearest 16th note */
        snap16: (ms) => {
          const t = ms / 1000 + s.start - FILM.firstBeat;
          const q = FILM.beatPeriod / 4;
          return Math.round((Math.round(t / q) * q + FILM.firstBeat - s.start) * 1000);
        },
        // a line can straddle scenes (pickups); each scene gets only its own words
        lines: FILM.lyrics
          .map((l) => ({ ...l, words: l.words.filter((w) => w.scene === id) }))
          .filter((l) => l.words.length),
      };
    },

    /** Drive an anime timeline from the scene's GSAP timeline (scene-local, deterministic). */
    bridge(gtl, atl, durSec) {
      const p = { t: 0 };
      gtl.fromTo(p, { t: 0 }, { t: durSec, duration: durSec, ease: "none", onUpdate: () => atl.seek(p.t * 1000) }, 0);
      atl.seek(0);
    },

    timeline() {
      return A.createTimeline({ autoplay: false, defaults: { ease: EXPO, duration: 400 } });
    },

    /* ---------- DOM helpers ---------- */

    el(tag, cls, parent, text) {
      const e = document.createElement(tag);
      if (cls) e.className = cls;
      if (text != null) e.textContent = text;
      if (parent) parent.appendChild(e);
      return e;
    },

    /** Wrap each syllable/letter of el's text in span.syl (spaces become span.sp). Returns the syllable spans. */
    syllables(el) {
      const text = el.textContent;
      el.textContent = "";
      const out = [];
      for (const ch of Array.from(text)) {
        if (ch === " ") {
          K.el("span", "sp", el, " ");
          continue;
        }
        out.push(K.el("span", "syl", el, ch));
      }
      return out;
    },

    /** Hangul composition states for one syllable: "연" -> ["ㅇ","여","연"]. Non-Hangul -> [ch]. */
    jamoStates(ch) {
      const c = ch.codePointAt(0) - 0xac00;
      if (c < 0 || c > 11171) return [ch];
      const CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ";
      const cho = Math.floor(c / 588);
      const jung = Math.floor((c % 588) / 28);
      const jong = c % 28;
      const open = String.fromCodePoint(0xac00 + (cho * 21 + jung) * 28);
      return jong ? [CHO[cho], open, ch] : [CHO[cho], ch];
    },

    /* ---------- presets (all times scene-local ms) ---------- */

    /** Hide targets until t (set at 0 so seeks back restore it). */
    hideUntil(at, targets, t) {
      at.set(targets, { opacity: 0 }, 0);
      if (t > 0) at.set(targets, { opacity: 0 }, Math.max(0, t - 1));
    },

    /** Cut on at t, cut off at end (hard cuts, no easing: hits are 0 ms sets). */
    window(at, targets, t, end) {
      at.set(targets, { opacity: 0 }, 0);
      at.set(targets, { opacity: 1 }, Math.max(0, t));
      if (end != null) at.set(targets, { opacity: 0 }, end);
    },

    /** Ref #1 slam + creep: scale 1.12->1 in 120 ms expo, then creep to 1.04 until `until`. */
    slam(at, el, t, until, { from = 1.12, creep = 1.04, blur = 10 } = {}) {
      at.set(el, { opacity: 0, scale: from, filter: `blur(${blur}px)` }, 0);
      at.set(el, { opacity: 1 }, t);
      at.add(el, { scale: [from, 1], filter: [`blur(${blur}px)`, "blur(0px)"], duration: 120, ease: EXPO }, t);
      if (until && creep !== 1) at.add(el, { scale: [1, creep], duration: Math.max(1, until - t - 120), ease: "linear" }, t + 120);
    },

    /** Ref #5 drop with stretch, per syllable. */
    drop(at, syls, t, { stagger = 72, dur = 180, dist = "-120%" } = {}) {
      at.set(syls, { opacity: 0, y: dist, scaleY: 1.8 }, 0);
      syls.forEach((s, i) => {
        const ti = t + i * stagger;
        at.set(s, { opacity: 1 }, ti);
        at.add(s, { y: [dist, "0%"], scaleY: [1.8, 1], duration: dur, ease: QUART }, ti);
      });
      return t + (syls.length - 1) * stagger + dur;
    },

    /** B pole: syllables inflate in with a playful spring (damping ~0.5). */
    bloom(at, syls, t, { stagger = 72, dur = 520, zeta = 0.45, rot = 8 } = {}) {
      at.set(syls, { opacity: 0, scale: 0.2, rotate: 0 }, 0);
      syls.forEach((s, i) => {
        const ti = t + i * stagger;
        const r = (i % 2 ? 1 : -1) * rot;
        at.set(s, { opacity: 1 }, ti);
        at.add(s, { scale: [0.2, 1], rotate: [r, 0], duration: dur, ease: springEase(zeta, 2.0) }, ti);
      });
      return t + (syls.length - 1) * stagger + dur;
    },

    /** Ref #3 Hangul IME typing: each syllable steps through its jamo states, one state per `step` ms.
     *  `el` content must be built with K.imeBuild(). Returns end time. */
    imeBuild(el) {
      const text = el.textContent;
      el.textContent = "";
      const cells = [];
      for (const ch of Array.from(text)) {
        if (ch === " ") {
          K.el("span", "sp", el, " ");
          continue;
        }
        const cell = K.el("span", "ime", el);
        const states = K.jamoStates(ch).map((s, i, arr) => K.el("span", i === arr.length - 1 ? "ime-s ime-final" : "ime-s", cell, s));
        cells.push({ cell, states });
      }
      return cells;
    },
    ime(at, cells, t, { step = 72, caret = null } = {}) {
      let ti = t;
      for (const { states } of cells) at.set(states, { opacity: 0 }, 0);
      for (const { cell, states } of cells) {
        states.forEach((s, i) => {
          if (i > 0) at.set(states[i - 1], { opacity: 0 }, ti);
          at.set(s, { opacity: 1 }, ti);
          if (caret) at.set(caret, { x: cell.offsetLeft + cell.offsetWidth, y: cell.offsetTop }, ti);
          ti += step;
        });
      }
      return ti;
    },

    /** Magnet attraction: two elements accelerate toward each other (ease-in), snap together on `t+dur`
     *  with a spring overshoot. dx is the travel of each element in px (A moves +dx, B moves -dx). */
    attract(at, a, b, t, dur, dx, { overshoot = 0.12, settle = 360 } = {}) {
      at.add(a, { x: [0, dx], duration: dur, ease: IN3 }, t);
      at.add(b, { x: [0, -dx], duration: dur, ease: IN3 }, t);
      const o = dx * overshoot;
      at.add(a, { x: [dx, dx], scaleX: [0.9, 1], duration: settle, ease: springEase(0.4, 2) }, t + dur);
      at.add(b, { x: [-dx, -dx], scaleX: [0.9, 1], duration: settle, ease: springEase(0.4, 2) }, t + dur);
      return t + dur;
    },

    /** Magnet repulsion: elements jolt apart, wobble, settle wider. */
    repel(at, a, b, t, dx, { dur = 420 } = {}) {
      at.add(a, { x: [0, -dx], duration: dur, ease: springEase(0.35, 2.5) }, t);
      at.add(b, { x: [0, dx], duration: dur, ease: springEase(0.35, 2.5) }, t);
    },

    /** Ref #7 two-frame flash (inversion layer): opacity 1 for `frames` frames. */
    flash(at, el, t, frames = 2) {
      at.set(el, { opacity: 0 }, 0);
      at.set(el, { opacity: 1 }, t);
      at.set(el, { opacity: 0 }, t + Math.round((frames * 1000) / 30));
    },

    /** Ref #13 circle iris on a wrapper (clip-path). */
    iris(at, el, t, dur, { x = "50%", y = "50%", from = 0, to = 150, ease = INOUT } = {}) {
      at.set(el, { clipPath: `circle(${from}% at ${x} ${y})` }, 0);
      at.add(el, { clipPath: [`circle(${from}% at ${x} ${y})`, `circle(${to}% at ${x} ${y})`], duration: dur, ease }, t);
    },

    /** Ref #13 tracking collapse. */
    track(at, el, t, dur, from = "2em", to = "0.02em") {
      at.add(el, { letterSpacing: [from, to], duration: dur, ease: INOUT }, t);
    },

    /** Ref #9 script write-on: a left-to-right clip wipe with a slight lean. */
    write(at, el, t, dur) {
      at.set(el, { clipPath: "inset(-20% 100% -20% 0%)" }, 0);
      at.add(el, { clipPath: ["inset(-20% 100% -20% 0%)", "inset(-20% 0% -20% 0%)"], duration: dur, ease: A.cubicBezier(0.37, 0, 0.63, 1) }, t);
    },

    /** Ref #11 slot-block reveal: a block per syllable, then the glyph replaces it. */
    slots(at, syls, t, { stagger = 120, color = "rgba(0,0,0,.18)" } = {}) {
      syls.forEach((s, i) => {
        const glyph = s.textContent;
        s.textContent = "";
        const g = K.el("span", "slot-glyph", s, glyph);
        const block = K.el("span", "slot-block", s);
        block.style.background = color;
        const tb = t + i * stagger * 0.5;
        const tg = t + i * stagger + 90;
        at.set(g, { opacity: 0 }, 0);
        at.set(block, { opacity: 0, scaleX: 0 }, 0);
        at.set(block, { opacity: 1 }, tb);
        at.add(block, { scaleX: [0, 1], duration: 90, ease: EXPO }, tb);
        at.set(g, { opacity: 1 }, tg);
        at.set(block, { opacity: 0 }, tg);
      });
    },

    /** Ref #12 repeat multiply: shrink to 1/3 and reveal a prepared 3x3 grid of clones. */
    multiply(at, hero, clones, t, { dur = 144 } = {}) {
      at.add(hero, { scale: [1, 0.333], duration: dur, ease: EXPO }, t);
      at.set(clones, { opacity: 0 }, 0);
      at.set(clones, { opacity: 1 }, t + dur);
    },

    /** Ref #6 zoom out of a letterform: scale from big to 1 around an origin. */
    zoomOut(at, el, t, { from = 15, dur = 160, origin = "50% 50%" } = {}) {
      el.style.transformOrigin = origin;
      at.set(el, { scale: from }, 0);
      at.add(el, { scale: [from, 1], duration: dur, ease: EXPO }, t);
    },

    /** Whip exit: fast horizontal slide with blur. */
    whipOut(at, el, t, { dx = -1400, dur = 220 } = {}) {
      at.add(el, { x: [0, dx], filter: ["blur(0px)", "blur(18px)"], duration: dur, ease: IN3 }, t);
    },

    /** Generic word-per-hit lyric runner: shows each word of `words` in `slot` at its sung time,
     *  using `make(word, i)` to build the element and `enter(at, el, t, next)` to animate it. */
    words(at, words, sceneObj, make, enter, { lead = 40, minHold = 160 } = {}) {
      const els = words.map((w, i) => make(w, i));
      els.forEach((el, i) => {
        const t = sceneObj.ms(words[i].start) - lead;
        const next = i + 1 < words.length ? sceneObj.ms(words[i + 1].start) - lead : null;
        enter(at, el, Math.max(0, t), next != null ? Math.max(t + minHold, next) : null, i);
      });
      return els;
    },

    /** A full-frame shot container visible over [t0, t1) (scene-local ms). */
    shot(parent, at, t0, t1, { bg = null, cls = "" } = {}) {
      const el = K.el("div", "shot " + cls, parent);
      el.style.cssText = "position:absolute;inset:0;overflow:hidden;" + (bg ? `background:${bg};` : "");
      K.window(at, el, t0, t1);
      return el;
    },

    /** Absolutely positioned text block. css is an object of style props (px numbers allowed). */
    txt(parent, text, cls, css = {}) {
      const el = K.el("div", "kt " + (cls || ""), parent, text);
      el.style.position = "absolute";
      el.style.whiteSpace = "nowrap";
      for (const [k, v] of Object.entries(css)) el.style[k] = typeof v === "number" && !/opacity|zIndex|lineHeight|fontWeight/.test(k) ? v + "px" : v;
      return el;
    },

    /** Photo path by key from data/photos.json (w00 wedding, d00 date, x00 misc). */
    photo(key) {
      return FILM.photos[key];
    },

    /** Image layer. */
    img(parent, src, css = {}) {
      const el = K.el("img", "", parent);
      el.src = src;
      el.alt = "";
      el.style.position = "absolute";
      for (const [k, v] of Object.entries(css)) el.style[k] = typeof v === "number" && !/opacity|zIndex/.test(k) ? v + "px" : v;
      return el;
    },

    /** Flat word list of a scene with scene-local ms: [{t, ms, end, line, i}] */
    flat(sceneObj, lead = 60) {
      const out = [];
      sceneObj.lines.forEach((l) =>
        l.words.forEach((w) => out.push({ t: w.t, ms: sceneObj.ms(w.start) - lead, end: sceneObj.ms(w.end), q: w.q != null ? sceneObj.ms(w.q) : null, line: l.line, i: out.length })),
      );
      return out;
    },

    /* ---------- camera language (cinematic pass) ---------- */

    /** A shot with a camera rig inside it: `shot` owns visibility, `cam` owns shake/punch/pulse,
     *  so content inside can keep its own push without fighting over transform properties. */
    rig(parent, at, t0, t1, { bg = null, cls = "" } = {}) {
      const shot = K.shot(parent, at, t0, t1, { bg, cls });
      const cam = K.el("div", "cam", shot);
      cam.style.cssText = "position:absolute;inset:0;transform-origin:50% 50%";
      return { shot, cam };
    },

    /** Handheld hit: seeded jitter that decays to rest over `dur` ms (one set per frame, seek-safe). */
    shake(at, el, t, { dur = 420, amp = 14, rot = 0.5, seed = 1 } = {}) {
      const r = K.rng(seed * 7919 + Math.round(t));
      const n = Math.max(2, Math.round(dur / 33.333));
      at.set(el, { x: 0, y: 0, rotate: 0 }, 0);
      for (let i = 0; i <= n; i++) {
        const d = i === n ? 0 : Math.pow(1 - i / n, 1.6);
        at.set(el, { x: (r() - 0.5) * 2 * amp * d, y: (r() - 0.5) * 2 * amp * 0.7 * d, rotate: (r() - 0.5) * 2 * rot * d }, t + i * 33.333);
      }
    },

    /** Beat punch: the frame lunges in and settles (scale `from` -> 1). */
    punch(at, el, t, { from = 1.06, dur = 380 } = {}) {
      at.add(el, { scale: [from, 1], duration: dur, ease: EXPO }, t);
    },

    /** Pump the frame on every beat in [t0, t1) — a breath of scale on each kick. */
    pulse(at, el, sceneObj, t0, t1, { amp = 0.012, every = 1 } = {}) {
      for (let n = sceneObj.beatAt(t0); ; n += every) {
        const t = sceneObj.beat(n);
        if (t >= t1) break;
        at.add(el, { scale: [1 + amp, 1], duration: Math.min(BEAT * every * 0.9, 420), ease: QUART }, t);
      }
    },

    /** Exposure flash: a full-frame layer that blows out and decays (warm white by default). */
    flashFrame(at, parent, t, { color = "#fffaf0", dur = 300, peak = 1, z = 50 } = {}) {
      const f = K.el("div", "", parent);
      f.style.cssText = `position:absolute;inset:0;background:${color};pointer-events:none;z-index:${z}`;
      at.set(f, { opacity: 0 }, 0);
      at.set(f, { opacity: peak }, t);
      at.add(f, { opacity: [peak, 0], duration: dur, ease: EXPO }, t + 33);
      return f;
    },

    /** Exposure ramp up to white (the wind-up before a drop): eases in and lands at t1 fully white. */
    whiteout(at, parent, t0, t1, { color = "#fffaf0", z = 50 } = {}) {
      const f = K.el("div", "", parent);
      f.style.cssText = `position:absolute;inset:0;background:${color};pointer-events:none;z-index:${z}`;
      at.set(f, { opacity: 0 }, 0);
      at.add(f, { opacity: [0, 1], duration: t1 - t0, ease: IN3 }, t0);
      return f;
    },

    /** Organic light leak (adapted from the registry block organic-light-leak-overlay): three soft
     *  gradient layers drift across the frame in screen blend, finite envelope over `dur` ms. */
    leak(at, parent, t, dur, { peak = 0.8, from = "left", z = 40, tone = "warm" } = {}) {
      const box = K.el("div", "", parent);
      box.style.cssText = `position:absolute;inset:-16%;overflow:hidden;pointer-events:none;mix-blend-mode:screen;z-index:${z}`;
      const pal = tone === "rose"
        ? ["rgb(255 228 214 / 90%)", "rgb(232 120 120 / 70%)", "rgb(255 92 120 / 62%)", "rgb(255 214 190 / 70%)"]
        : ["rgb(255 241 197 / 92%)", "rgb(255 126 57 / 74%)", "rgb(255 79 61 / 60%)", "rgb(255 247 205 / 70%)"];
      const sx = from === "left" ? 1 : -1;
      const L = (css) => {
        const l = K.el("div", "", box);
        l.style.cssText = "position:absolute;inset:-20%;" + css;
        return l;
      };
      const a = L(`background:radial-gradient(ellipse 52% 110% at ${from === "left" ? 10 : 90}% 58%, ${pal[0]}, transparent 45%),radial-gradient(ellipse 72% 120% at ${from === "left" ? 24 : 76}% 54%, ${pal[1]}, transparent 66%);filter:blur(30px)`);
      const b = L(`background:radial-gradient(ellipse 58% 105% at ${from === "left" ? 78 : 22}% 34%, ${pal[2]}, transparent 76%);filter:blur(43px)`);
      const c = L(`background:linear-gradient(${from === "left" ? 104 : 76}deg, transparent 24%, ${pal[1].replace(/\/ \d+%/, "/ 30%")} 40%, ${pal[3]} 51%, transparent 78%);filter:blur(22px)`);
      at.set(box, { opacity: 0 }, 0);
      at.add(box, { opacity: [0, peak], duration: dur * 0.3, ease: A.cubicBezier(0.39, 0.575, 0.565, 1) }, t);
      at.add(box, { opacity: [peak, peak * 0.5], duration: dur * 0.25, ease: INOUT }, t + dur * 0.4);
      at.add(box, { opacity: [peak * 0.5, 0], duration: dur * 0.3, ease: IN3 }, t + dur * 0.7);
      at.add(a, { translateX: [`${-20 * sx}%`, `${18 * sx}%`], scale: [0.92, 1.1], rotate: [-4 * sx, 2 * sx], duration: dur, ease: INOUT }, t);
      at.add(b, { translateX: [`${20 * sx}%`, `${-16 * sx}%`], translateY: ["-8%", "8%"], scale: [1.08, 0.94], duration: dur, ease: INOUT }, t);
      at.add(c, { translateX: [`${-28 * sx}%`, `${24 * sx}%`], rotate: [-6 * sx, 4 * sx], duration: dur, ease: INOUT }, t);
      return box;
    },

    /** Whip pan: outgoing frame streaks off, incoming streaks in, directional blur peaking mid-whip
     *  (stepped SVG filters #hb1..#hb4 declared in index.html). dir 1 = camera pans right. */
    whip(at, outEl, inEl, t, { dir = 1, dur = 330 } = {}) {
      const n = Math.max(4, Math.round(dur / 33.333));
      if (outEl) at.add(outEl, { x: [0, -dir * 1920], duration: dur, ease: A.cubicBezier(0.7, 0, 0.84, 0) }, t);
      if (inEl) {
        at.set(inEl, { x: dir * 1920 }, Math.max(0, t - 1));
        at.add(inEl, { x: [dir * 1920, 0], duration: dur, ease: A.cubicBezier(0.16, 1, 0.3, 1) }, t + dur * 0.35);
      }
      const els = [outEl, inEl].filter(Boolean);
      for (let i = 0; i <= n; i++) {
        const k = Math.sin((Math.PI * i) / n);
        const lvl = i === n ? 0 : Math.min(4, Math.round(k * 4.2));
        at.set(els, { filter: lvl ? `url(#hb${lvl})` : "none" }, t + i * 33.333);
      }
      if (outEl) at.set(outEl, { x: 0, filter: "none" }, t + dur * 1.35 + 34);
    },

    /** Letterbox bars (2.39:1 by default) that slide in over `dur` ms and optionally out again. */
    letterbox(at, parent, t, { h = 138, dur = 900, out = null, z = 45 } = {}) {
      const mk = (top) => {
        const b = K.el("div", "", parent);
        b.style.cssText = `position:absolute;left:0;right:0;${top ? "top" : "bottom"}:0;height:${h}px;background:#0c0b0a;z-index:${z}`;
        at.set(b, { translateY: top ? -h : h }, 0);
        at.add(b, { translateY: [top ? -h : h, 0], duration: dur, ease: INOUT }, t);
        if (out != null) at.add(b, { translateY: [0, top ? -h : h], duration: dur * 0.7, ease: INOUT }, out);
        return b;
      };
      return [mk(true), mk(false)];
    },

    /** Knockout type: a full-frame plate with the word cut out of it, so whatever is behind shows
     *  through the letters. geo comes from scripts/knock_points.py (x, baseline, deep point).
     *  Returns { wrap, plate } — scale `wrap` around geo.deep to fly into the stroke. */
    knock(parent, text, geo, { fill = "#f2ede4", family = "Noto Serif KR", weight = 800, size = 560, z = 20 } = {}) {
      const NS = "http://www.w3.org/2000/svg";
      const id = "kn" + (K._kn = (K._kn || 0) + 1);
      const wrap = K.el("div", "", parent);
      wrap.style.cssText = `position:absolute;inset:0;z-index:${z};transform-origin:${geo.deep[0]}px ${geo.deep[1]}px`;
      const svg = document.createElementNS(NS, "svg");
      svg.setAttribute("width", "1920");
      svg.setAttribute("height", "1080");
      svg.setAttribute("viewBox", "0 0 1920 1080");
      svg.style.cssText = "position:absolute;left:0;top:0;overflow:visible";
      svg.innerHTML =
        `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="-4000" y="-4000" width="9920" height="9080">` +
        `<rect x="-4000" y="-4000" width="9920" height="9080" fill="#fff"/>` +
        `<text x="${geo.x}" y="${geo.baseline}" font-family="${family}" font-weight="${weight}" font-size="${size}" style="font-kerning:none" fill="#000" stroke="#000" stroke-width="0" stroke-linejoin="round">${text}</text>` +
        `</mask></defs><rect x="-4000" y="-4000" width="9920" height="9080" fill="${fill}" mask="url(#${id})"/>`;
      wrap.appendChild(svg);
      return { wrap, plate: svg, glyphs: svg.querySelector("mask text") };
    },

    /** Fly into the knockout's stroke: scale the plate around its deep point until the frame is all media. */
    zoomThrough(at, wrap, t, { dur = 520, to = 34 } = {}) {
      at.add(wrap, { scale: [1, to], duration: dur, ease: A.cubicBezier(0.55, 0, 0.9, 0.3) }, t);
      at.set(wrap, { opacity: 0 }, t + dur);
    },

    /** Seeded PRNG (mulberry32) for any variation. */
    rng(seed) {
      let a = seed >>> 0;
      return () => {
        a |= 0;
        a = (a + 0x6d2b79f5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    },
  };

  window.K = K;
})();
