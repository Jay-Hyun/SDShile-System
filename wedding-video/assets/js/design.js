/* Design kit for the reference-driven pass (v4): the graphic vocabulary of the four reference films.
 *
 * Actor        cobalt / cream / orange, tone-on-tone oval pattern, scalloped halftone badge, starburst,
 *              checker, icon ring around a black disc, left-aligned neutral-gothic stacks, echo stacks.
 * Love Lee     pastel gradients (periwinkle, lilac, mint, pink), SNS post cards with a soft glow,
 *              circle windows, speech bubbles and pills, phone frames.
 * GODS         black + electric blue, condensed italic Latin, bars that scale from an edge.
 * How It's Done  giant word behind a cutout figure (subject sandwich), outline <-> fill.
 *
 * Illustrated assets come from GPT image generation (scripts/gen_images.py): assets/media/gen/<id>.png,
 * cut-outs in assets/media/gen/cut/<id>.png. Everything here is plain DOM/SVG/CSS, seek-safe.
 */
(function () {
  const PAL = {
    cobalt: "#4554f1",
    cobaltDeep: "#3442d6",
    cream: "#ece7dc",
    paper: "#f3efe6",
    ink: "#232024",
    orange: "#eca039",
    peri: "#6a6ae0",
    lilac: "#bdbcf0",
    mint: "#96e6b7",
    pink: "#e07ab4",
    coral: "#f0899a",
    eblue: "#1a1ae6",
    black: "#0b0b0d",
  };

  const svgURI = (s) => `url("data:image/svg+xml;utf8,${encodeURIComponent(s)}")`;

  const css = `
  .v4 { --cobalt:${PAL.cobalt}; --cream:${PAL.cream}; --ink:${PAL.ink}; --orange:${PAL.orange}; }
  .bg-cobalt { background-color:${PAL.cobalt}; }
  .bg-cream { background-color:${PAL.cream}; }
  .bg-paper { background: radial-gradient(ellipse 80% 90% at 50% 45%, #f6f2ea 0%, ${PAL.cream} 70%, #e2dccf 100%); }
  .bg-orange { background-color:${PAL.orange}; }
  .bg-black { background-color:${PAL.black}; }
  .bg-peri { background: linear-gradient(160deg, #5f5fd8 0%, #8f8ee8 45%, #c9c3f2 80%, #ead8f1 100%); }
  .bg-lilac { background: linear-gradient(180deg, #e9e6fb 0%, #d7d3f7 55%, #f3e3f2 100%); }
  .bg-mint { background: radial-gradient(ellipse 70% 80% at 50% 50%, #c4f3d6 0%, ${PAL.mint} 70%, #7fd9a6 100%); }
  .bg-white { background: radial-gradient(ellipse 80% 80% at 50% 45%, #ffffff 0%, #f1f0f6 100%); }
  .bg-dusk { background: linear-gradient(180deg, #2b2a7a 0%, #6a5fc8 55%, #e3a9c9 100%); }
  .pat-oval { background-image: ${svgURI(
    `<svg xmlns="http://www.w3.org/2000/svg" width="160" height="120"><g fill="#ffffff" fill-opacity="0.075">` +
      `<ellipse cx="40" cy="30" rx="30" ry="12" transform="rotate(-28 40 30)"/>` +
      `<ellipse cx="120" cy="90" rx="30" ry="12" transform="rotate(-28 120 90)"/></g></svg>`,
  )}; background-size: 160px 120px; }
  .pat-thumb { background-image: ${svgURI(
    `<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150"><g fill="#ffffff" fill-opacity="0.09">` +
      `<circle cx="38" cy="38" r="22"/><circle cx="113" cy="113" r="22"/></g></svg>`,
  )}; background-size: 150px 150px; }
  .pat-check { background-color:${PAL.orange}; background-image: conic-gradient(rgba(255,255,255,.16) 25%, transparent 0 50%, rgba(255,255,255,.16) 0 75%, transparent 0); background-size: 120px 120px; }
  .pat-grid { background-image: linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px); background-size: 96px 96px; }
  .fill { position:absolute; inset:0; overflow:hidden; }
  .fill > img.plate, .fill > video { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }
  .k-sans { font-family: "Pretendard"; font-weight: 500; letter-spacing: -0.01em; }
  .k-sansB { font-family: "Pretendard"; font-weight: 800; letter-spacing: -0.03em; }
  .k-sansK { font-family: "Pretendard"; font-weight: 900; letter-spacing: -0.04em; }
  .k-serif { font-family: "Noto Serif KR"; font-weight: 500; letter-spacing: -0.01em; }
  .k-serifB { font-family: "Noto Serif KR"; font-weight: 700; letter-spacing: -0.02em; }
  .k-cond { font-family: "Anton"; letter-spacing: 0.005em; text-transform: uppercase; }
  .k-script { font-family: "Mrs Saint Delafield"; }
  .k-meta { font-family: "Pretendard"; font-weight: 600; font-size: 15px; letter-spacing: 0.22em; text-transform: uppercase; }
  .c-cream { color:${PAL.cream}; } .c-ink { color:${PAL.ink}; } .c-cobalt { color:${PAL.cobalt}; }
  .c-orange { color:${PAL.orange}; } .c-white { color:#fff; } .c-pink { color:${PAL.pink}; } .c-eblue { color:${PAL.eblue}; }
  .c-peri { color:${PAL.peri}; } .c-coral { color:${PAL.coral}; }
  .glow { text-shadow: 0 0 40px rgba(255,255,255,.55); }
  .outline { color: transparent; -webkit-text-stroke: 2px currentColor; }
  .card { position:absolute; background:#fff; border-radius:26px; box-shadow: 0 30px 80px rgba(80,70,200,.28), 0 0 0 1px rgba(0,0,0,.04); overflow:hidden; }
  .card .media { position:absolute; left:18px; right:18px; top:72px; bottom:110px; border-radius:16px; overflow:hidden; background:#eceaf6; }
  .card .media img, .card .media video { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }
  .phone { position:absolute; background:#f6f3ec; border-radius:64px; box-shadow: 0 40px 90px rgba(0,0,0,.35), inset 0 0 0 3px rgba(0,0,0,.08); }
  .phone .screen { position:absolute; left:16px; right:16px; top:16px; bottom:16px; border-radius:50px; overflow:hidden; background:#000; }
  .phone .screen img, .phone .screen video { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }
  .pill { position:absolute; border-radius:999px; padding: 0 1.1em; display:flex; align-items:center; justify-content:center; white-space:nowrap; }
  .meta-row { position:absolute; left:56px; right:56px; display:flex; justify-content:space-between; }
  .kt { line-height: 1.12; will-change: transform, opacity, filter; }
  .kt .syl, .kt .ime { display: inline-block; position: relative; }
  .ime-s { position: absolute; left: 0; top: 0; }
  .ime-final { position: relative; }
  .slot-glyph { position: relative; }
  .slot-block { position: absolute; left: 2%; right: 2%; top: 8%; bottom: 4%; transform-origin: 0 50%; }
  `;
  const st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, cls, parent, text) => K.el(tag, cls, parent, text);
  const place = (e, o) => {
    for (const [k, v] of Object.entries(o)) e.style[k] = typeof v === "number" && !/opacity|zIndex/.test(k) ? v + "px" : v;
    return e;
  };

  const D = {
    PAL,

    /** A full-frame background layer. cls: "bg-cobalt pat-oval" etc. */
    bg(parent, cls) {
      return el("div", "fill " + cls, parent);
    },

    /** GPT-generated image: cut-out (alpha) if `cut`, else the full plate. */
    gen(parent, id, css = {}, { cut = true } = {}) {
      const im = K.img(parent, `assets/media/gen/${cut ? "cut/" : ""}${id}.png`, css);
      if (!cut) im.classList.add("plate");
      return im;
    },

    /** Actor's scalloped halftone badge (the cursor that rides ahead of typing). */
    badge(parent, { size = 120, color = "#e88fb6", dot = "#c4588f", n = 14 } = {}) {
      // returned as a div wrapper: transforms animate reliably on HTML boxes, not on an outer <svg>
      const box = el("div", "", parent);
      box.style.cssText = `position:absolute;width:${size}px;height:${size}px`;
      const s = document.createElementNS(NS, "svg");
      s.setAttribute("viewBox", "-60 -60 120 120");
      s.style.cssText = `position:absolute;left:0;top:0;width:${size}px;height:${size}px;overflow:visible`;
      let d = "";
      for (let i = 0; i < n; i++) {
        const a0 = (i / n) * Math.PI * 2, a1 = ((i + 1) / n) * Math.PI * 2, am = (a0 + a1) / 2;
        const p = (a, r) => `${(Math.cos(a) * r).toFixed(2)} ${(Math.sin(a) * r).toFixed(2)}`;
        d += (i ? " L " : "M ") + p(a0, 46) + ` Q ${p(am, 60)} ${p(a1, 46)}`;
      }
      const id = "dots" + (D._n = (D._n || 0) + 1);
      s.innerHTML =
        `<defs><pattern id="${id}" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.6" fill="${dot}"/></pattern></defs>` +
        `<path d="${d} Z" fill="${color}"/><path d="${d} Z" fill="url(#${id})" opacity=".55"/>`;
      box.appendChild(s);
      return box;
    },

    /** Starburst behind a word (Actor's orange burst). */
    burst(parent, { rays = 16, color = "#f6c27a", inner = 0.55, size = 2400, x = 960, y = 540 } = {}) {
      const box = el("div", "", parent);
      box.style.cssText = `position:absolute;left:${x - size / 2}px;top:${y - size / 2}px;width:${size}px;height:${size}px`;
      const s = document.createElementNS(NS, "svg");
      s.setAttribute("viewBox", "-100 -100 200 200");
      s.style.cssText = `position:absolute;left:0;top:0;width:${size}px;height:${size}px;overflow:visible`;
      let d = "";
      for (let i = 0; i < rays * 2; i++) {
        const a = (i / (rays * 2)) * Math.PI * 2;
        const r = i % 2 ? 100 * inner : 100;
        d += (i ? "L" : "M") + (Math.cos(a) * r).toFixed(2) + " " + (Math.sin(a) * r).toFixed(2);
      }
      s.innerHTML = `<path d="${d}Z" fill="${color}"/>`;
      box.appendChild(s);
      return box;
    },

    /** Items placed evenly on a circle (returns wrapper to rotate and the item elements). */
    ring(parent, n, make, { cx = 960, cy = 540, r = 380, spin = true } = {}) {
      const w = el("div", "", parent);
      w.style.cssText = `position:absolute;left:${cx}px;top:${cy}px;width:0;height:0`;
      const items = [];
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 - Math.PI / 2;
        const holder = el("div", "", w);
        holder.style.cssText = `position:absolute;left:${Math.cos(a) * r}px;top:${Math.sin(a) * r}px;transform:rotate(${spin ? (a * 180) / Math.PI + 90 : 0}deg)`;
        const it = make(holder, i);
        items.push(holder);
      }
      return { wrap: w, items };
    },

    /** Echo stack: the same line repeated, outlined copies around one filled copy (Actor TIME OVER). */
    echo(parent, text, { n = 5, gap = 70, cls = "k-cond", size = 80, color = "#fff", x = 0, y = 540, center = true } = {}) {
      const box = el("div", "", parent);
      box.style.cssText = `position:absolute;left:${x}px;${center ? "right:0" : ""};top:${y - (n * gap) / 2}px;text-align:${center ? "center" : "left"}`;
      const rows = [];
      for (let i = 0; i < n; i++) {
        const r = el("div", "kt " + cls, box, text);
        r.style.cssText += `position:absolute;left:0;right:0;top:${i * gap}px;font-size:${size}px;line-height:1;color:${color};white-space:nowrap`;
        if (i !== Math.floor(n / 2)) {
          r.style.color = "transparent";
          r.style.webkitTextStroke = `1.5px ${color}`;
          r.style.opacity = 0.75;
        }
        rows.push(r);
      }
      return { box, rows, hero: rows[Math.floor(n / 2)] };
    },

    /** SNS post card (Love Lee): header, media slot, action icons, caption lines. Returns { card, media }. */
    card(parent, { x, y, w = 520, h = 680, handle = "", likes = "" } = {}) {
      const c = el("div", "card", parent);
      place(c, { left: x, top: y, width: w, height: h });
      const av = el("div", "", c);
      av.style.cssText = "position:absolute;left:22px;top:20px;width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#8f8ee8,#e07ab4)";
      const hd = el("div", "k-sans", c, handle);
      hd.style.cssText = "position:absolute;left:70px;top:26px;font-size:20px;color:#2a2833";
      const dots = el("div", "", c, "•••");
      dots.style.cssText = "position:absolute;right:24px;top:22px;font-size:18px;color:#9a97b0;letter-spacing:2px";
      const media = el("div", "media", c);
      const icons = document.createElementNS(NS, "svg");
      icons.setAttribute("viewBox", "0 0 160 32");
      icons.style.cssText = `position:absolute;left:22px;bottom:62px;width:150px;height:30px`;
      icons.innerHTML =
        `<path d="M16 28 C 2 18, 2 6, 10 5 C 13 4.5, 15 6, 16 8 C 17 6, 19 4.5, 22 5 C 30 6, 30 18, 16 28 Z" fill="#e8577f"/>` +
        `<path d="M58 6 h 22 a 6 6 0 0 1 6 6 v 9 a 6 6 0 0 1 -6 6 h -14 l -8 6 v -6 a 6 6 0 0 1 -6 -6 v -9 a 6 6 0 0 1 6 -6 z" fill="none" stroke="#2a2833" stroke-width="2.6"/>` +
        `<path d="M110 16 L 136 5 L 128 30 L 122 19 Z" fill="none" stroke="#2a2833" stroke-width="2.6" stroke-linejoin="round"/>`;
      c.appendChild(icons);
      const cap = el("div", "k-sans", c, likes);
      cap.style.cssText = "position:absolute;left:24px;bottom:26px;font-size:19px;color:#2a2833";
      return { card: c, media };
    },

    /** A phone (cream frame) whose screen is a slot. Returns { phone, screen }. */
    phone(parent, { x, y, h = 900 } = {}) {
      const w = Math.round(h * 0.49);
      const p = el("div", "phone", parent);
      place(p, { left: x, top: y, width: w, height: h });
      const screen = el("div", "screen", p);
      const notch = el("div", "", p);
      notch.style.cssText = `position:absolute;left:${w / 2 - 60}px;top:34px;width:120px;height:32px;border-radius:20px;background:#0b0b0d`;
      return { phone: p, screen };
    },

    /** Speech bubble (rounded) with a small tail; text inside. */
    bubble(parent, text, { x, y, cls = "k-sansB", size = 54, bg = "#fff", color = "#5b54d6", tail = "left", pad = 0.9 } = {}) {
      const b = el("div", "pill kt " + cls, parent, text);
      place(b, { left: x, top: y, fontSize: size, height: size * 2, background: bg, color, padding: `0 ${pad}em` });
      b.style.boxShadow = "0 18px 40px rgba(60,40,160,.22)";
      const t = el("div", "", b);
      t.style.cssText = `position:absolute;${tail}:${size * 0.7}px;bottom:-${size * 0.35}px;width:${size * 0.7}px;height:${size * 0.7}px;background:${bg};transform:rotate(45deg);border-radius:4px;z-index:-1`;
      return b;
    },

    /** Small editorial meta text in the corners (Actor/GODS frame furniture). */
    meta(parent, left, right, { y = 1000, color = "rgba(255,255,255,.7)" } = {}) {
      const r = el("div", "meta-row k-meta", parent);
      r.style.top = y + "px";
      r.style.color = color;
      el("span", "", r, left);
      el("span", "", r, right);
      return r;
    },
  };

  window.D = D;
})();
