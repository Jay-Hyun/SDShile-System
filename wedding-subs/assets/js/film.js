/* The overlay: basic lyric subtitles (Korean + English), Reels UI on the vertical clips,
 * boxed messages, and the handwritten outro card. Data: window.SUBS (scripts/build_subs.py), window.CALLI
 * (scripts/calligraphy.py). One paused GSAP timeline; text cuts in and out with no motion (only the pen writes). */
(function () {
  const S = window.SUBS;
  const root = document.getElementById("overlay");
  const tl = gsap.timeline({ paused: true });
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    (parent || root).appendChild(e);
    return e;
  };
  // visible over [s, e): instant cuts, seek-safe
  const span = (e, s, t1) => {
    tl.set(e, { autoAlpha: 0 }, 0);
    tl.set(e, { autoAlpha: 1 }, Math.max(0.001, s));
    if (t1 != null) tl.set(e, { autoAlpha: 0 }, t1);
  };
  const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");

  // ---- lyrics: basic subtitle --------------------------------------------------------------
  {
    // a faint dark floor under the lyrics so the gold English reads on bright footage
    const floor = el("div", "", root);
    floor.style.cssText = "position:absolute;left:0;right:0;bottom:0;height:300px;z-index:20;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.42))";
    span(floor, S.lyrics[0].s, S.lyrics[S.lyrics.length - 1].e);
  }
  // inside a Reels span the lyric moves up top (the account and caption sit at the bottom there)
  const inReels = (t) => S.reels.some((r) => t >= r.s && t < r.e);
  const cuts = (s, e) => {
    const pts = [s, ...S.reels.flatMap((r) => [r.s, r.e]).filter((t) => t > s && t < e), e];
    return pts.slice(0, -1).map((t, i) => [t, pts[i + 1]]);
  };
  S.lyrics.forEach((l) => {
    cuts(l.s, l.e).forEach(([a, b]) => {
      const r = S.reels.find((x) => (a + b) / 2 >= x.s && (a + b) / 2 < x.e);
      if (r && r.side) {
        // the photo-booth reel: Korean in the left bar, English in the right bar
        const ko = el("div", "flank", root, `<div class="ko">${esc(l.ko)}</div>`);
        const en = el("div", "flank", root, `<div class="en">${esc(l.en)}</div>`);
        ko.style.cssText = `left:40px;width:${r.x0 - 80}px`;
        en.style.cssText = `left:${r.x0 + r.w + 40}px;width:${1920 - r.x0 - r.w - 80}px`;
        span(ko, a, b);
        span(en, a, b);
        return;
      }
      const sub = el("div", "sub" + (r ? " top" : ""), root, `<div class="ko">${esc(l.ko)}</div><div class="en">${esc(l.en)}</div>`);
      if (r) {
        // on a vertical clip the lyric wraps inside the clip
        sub.style.left = r.x0 + 40 + "px";
        sub.style.right = 1920 - r.x0 - r.w + 40 + "px";
      }
      span(sub, a, b);
    });
  });

  // ---- Reels UI on the vertical clips ----------------------------------------------------------------------------
  const ICON = {
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 8 3.4 4.6 6.8 4.6c2.1 0 3.6 1.2 4.2 2.4h2c.6-1.2 2.1-2.4 4.2-2.4 3.4 0 5.4 3.4 4.1 6.7-1.8 4.6-9.3 9.2-9.3 9.2z"/></svg>',
    heartRed: '<svg viewBox="0 0 24 24" fill="#ff3040" stroke="#ff3040" stroke-width="1.9"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 8 3.4 4.6 6.8 4.6c2.1 0 3.6 1.2 4.2 2.4h2c.6-1.2 2.1-2.4 4.2-2.4 3.4 0 5.4 3.4 4.1 6.7-1.8 4.6-9.3 9.2-9.3 9.2z"/></svg>',
    comment: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linejoin="round"><path d="M20.6 16.6A9 9 0 1 0 17 20l3.9 1-1-3.9z"/></svg>',
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linejoin="round"><path d="M22 3 9.2 10.1M22 3l-7 18-4.6-8.8L2 9.3z"/></svg>',
    more: '<svg viewBox="0 0 24 24" fill="#fff"><circle cx="5" cy="12" r="1.9"/><circle cx="12" cy="12" r="1.9"/><circle cx="19" cy="12" r="1.9"/></svg>',
    cam: '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#fff" stroke-width="1.9" stroke-linejoin="round"><path d="M3 8h4l2-3h6l2 3h4v12H3z"/><circle cx="12" cy="13.5" r="3.8"/></svg>',
  };
  S.reels.forEach((r, i) => {
    const box = el("div", "reels", root);
    box.style.left = r.x0 + "px";
    box.style.width = r.w + "px";
    box.innerHTML = `<div class="shade"></div>
      <div class="head"><span>릴스</span>${ICON.cam}</div>
      <div class="side">
        <div>${i === 0 ? ICON.heartRed : ICON.heart}<span>${i === 0 ? "1,107" : "2,024"}</span></div>
        <div>${ICON.comment}<span>${i === 0 ? "86" : "131"}</span></div>
        <div>${ICON.share}<span>${i === 0 ? "52" : "77"}</span></div>
        <div>${ICON.more}</div>
      </div>
      <div class="acct"><div class="avatar"><span>♥</span></div>준익 ♥ 명지<span class="follow">팔로우</span></div>
      <div class="cap">${i === 0 ? "비 오는 날에도 같이 ☂" : "우리 결혼합니다"}</div>
      <div class="music">♫ god · 반대가 끌리는 이유</div>
      <div class="bar"><i></i></div>`;
    span(box, r.s, r.e);
    tl.fromTo(box.querySelector(".bar i"), { scaleX: 0 }, { scaleX: 1, duration: r.e - r.s, ease: "none" }, r.s);
  });

  // ---- friends' messages ------------------------------------------------------------------------------------------
  S.msgs.forEach((m) => {
    const box = el("div", "msg" + (m.group ? " group" : ""), root,
      `<div class="bar"><div class="tag">${esc(m.who)}</div><div class="box">${esc(m.ko)}</div></div>`);
    span(box, m.s, m.e);
  });

  // ---- outro: Happy Wedding Day written by a pen, then their names --------------------------------------------------
  {
    const O = S.outro;
    const card = el("div", "outro", root);
    span(card, O.s, null);
    const CA = window.CALLI;
    const [VW, VH] = CA.vb;
    const NS = "http://www.w3.org/2000/svg";
    const pen = el("div", "pen", card);
    const txt = `x="${CA.x}" y="${CA.y}" text-anchor="middle" font-family="${CA.font}" font-size="${CA.size}" word-spacing="${CA.ws}" fill="#F4E6C8"`;
    pen.innerHTML = `<svg xmlns="${NS}" viewBox="0 0 ${VW} ${VH}" width="1400" height="${(1400 * VH) / VW}" style="overflow:visible">
      <defs><filter id="pen-soft"><feGaussianBlur stdDeviation="1"/></filter>
      <mask id="pen-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="${VW}" height="${VH}">
      <g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" filter="url(#pen-soft)"></g></mask></defs>
      <text ${txt} mask="url(#pen-mask)">${CA.text}</text><text ${txt} opacity="0">${CA.text}</text></svg>`;
    const g = pen.querySelector("g");
    const full = pen.querySelectorAll("text")[1];
    const t0 = O.s + 0.25;
    CA.strokes.forEach((s) => {
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", s.d);
      p.setAttribute("stroke-width", s.w);
      p.setAttribute("pathLength", "1");
      p.setAttribute("stroke-dasharray", "1 1");
      g.appendChild(p);
      tl.set(p, { opacity: 0, attr: { "stroke-dashoffset": 1 } }, 0);
      tl.set(p, { opacity: 1 }, t0 + s.t / 1000);
      tl.fromTo(p, { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: Math.max(s.dur, 6) / 1000, ease: "none", immediateRender: false }, t0 + s.t / 1000);
    });
    const tDone = t0 + CA.total / 1000;
    tl.fromTo(full, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "sine.inOut", immediateRender: false }, tDone + 0.05);
    const rule = el("div", "rule", card);
    const names = el("div", "names", card, "박준익 &nbsp;·&nbsp; 김명지");
    const date = el("div", "date", card, "2026. 11. 07 SAT");
    [rule, names, date].forEach((x, i) => {
      tl.set(x, { opacity: 0 }, 0);
      tl.fromTo(x, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }, tDone + 0.25 + i * 0.15);
    });
    const black = el("div", "", card);
    black.style.cssText = "position:absolute;inset:0;background:#000";
    tl.set(black, { opacity: 0 }, 0);
    // let it linger: the card holds after the music, then dims slowly
    tl.fromTo(black, { opacity: 0 }, { opacity: 1, duration: 3.2, ease: "sine.inOut", immediateRender: false }, S.dur - 3.4);
  }

  tl.set({}, {}, S.dur);
  window.FILM_TL = tl;
})();
