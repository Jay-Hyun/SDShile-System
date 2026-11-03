"""v8 builder — illustration-led, 4 scenes (docs/ads/naver-clip/05-v8-illustration.md).

python3 v8/build.py            -> v8/A30, v8/A15, v8/B30, v8/B15 (HyperFrames projects)

Each project: index.html (root: one film host + one <audio>), compositions/film.html (all scenes, one anime.js
timeline), assets (illustrations hard-linked from _shared/img/ill, font subset, mark, audio).
Layout = advertiser landing grammar (04-v7-visual.md 부록 D): left-aligned on x = 84, eyebrow 30/600 brown-gold
-> lead 64/500 brown-gold -> head 120/700 ink -> body 40/400 grey. Sizes only {30, 40, 64, 120}.
Illustrations were drawn with the top ~46 % empty paper: text sits there, never over the drawing.
Motion: plate push 1.00 -> 1.05 from the bottom edge (whole scene, in-out), words blur in (6 px -> 0, 0.13 s,
67 ms apart). Scene changes are hard cuts on bar downbeats. The end card lands and holds still.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NC = os.path.dirname(HERE)
SH = os.path.join(NC, "_shared")
ILL = os.path.join(SH, "img", "ill")
FPS = 30


def snap(t):
    return round(t * FPS) / FPS


# ---------------------------------------------------------------- music grids (video 0 = a source downbeat)
def bars(beats_json, in_point, n=20):
    d = json.load(open(os.path.join(SH, "beats", beats_json)))
    db = [t for t in d["downbeats"] if t >= in_point - 0.01]
    return [snap(t - in_point) for t in db[:n]]


A_IN, B_IN = 3.239, 1.765
VA = bars("C-alex.json", A_IN)      # 0, 1.846, 3.692, ...
VB = bars("D-nastel.json", B_IN)    # 0, 2.0, 4.0, ...

# ---------------------------------------------------------------- copy (00-brief facts, 03 §4–5, 04 부록 C/D)
CHECK = ('<svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="22" fill="#7d6233"/>'
         '<path d="M13 22.5l6 5.8L31 16" fill="none" stroke="#fbf9f4" stroke-width="3.2" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')
YOU_PATH = ("M 296 214 C 300 176, 352 160, 362 200 C 370 240, 350 300, 380 328 C 410 352, 458 318, 476 262 "
            "C 484 236, 490 206, 498 176 C 494 262, 486 372, 458 432 C 444 462, 404 462, 410 430 "
            "C 418 386, 540 330, 610 300 C 630 290, 640 262, 616 258 C 590 254, 574 290, 584 320 "
            "C 592 344, 628 344, 640 318 C 648 300, 644 280, 634 272 C 650 276, 668 276, 670 292 "
            "C 672 316, 672 338, 692 340 C 716 342, 728 306, 732 278 C 730 310, 734 338, 758 340 "
            "C 800 342, 850 316, 886 266")
YOU_BOX = (296, 176, 886, 454)
YOU_BASE = 341


def eb(t):
    return f'<span class="eb">{t}</span>'


def ld(t):
    return f'<span class="ld">{t}</span>'


def hx(*lines):
    return "".join(f'<span class="hx">{l}</span>' for l in lines)


def bx(t, cls=""):
    return f'<span class="bx {cls}">{t}</span>'


def ck(t):
    return f'<div class="ck">{CHECK}<span>{t}</span></div>'


def end_card(film, cut, lead_eb, footnote):
    """Cream end card under the stairs band. Two phases: slogan (big) -> action block."""
    tel = '전화 <b>070-4006-7128</b> (평일 10–18시)'
    link = ('<b>아래 링크에서 확인하기</b><svg class="arr" viewBox="0 0 36 44"><path d="M18 3V40M6 28L18 40L30 28"/></svg>')
    checks = ck("일하면서도 돼요") + ck("상담만 받아도 돼요")
    return {
        "slogan": eb("그 자리로 가는 첫 계단") + ld("책임지는 자리로,") + hx("지금 있는", "자리에서."),
        "act": [
            ("logo", '<span class="mark"></span><span>경찰복지사이버평생교육원</span>'),
            ("sl", bx("책임지는 자리로, 지금 있는 자리에서.")),
            ("eb2", eb(lead_eb)),
            ("hd", hx("기간·비용부터", "들어 보세요.")),
            ("ck", checks),
            ("link", bx(link, "ink")),
            ("tel", bx(tel)),
        ],
        "foot": footnote,
    }


FOOT_UNIQUE = "*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준"
DISCLAIMER = "로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다."


def foot_line():
    return f'<span class="bx" style="font-size:30px;line-height:42px;margin-top:14px">{FOOT_UNIQUE}</span>'


def ckf(t):
    """Check row whose circle starts as an outline and fills later (A3 accent)."""
    return (f'<div class="ck ckf"><svg viewBox="0 0 44 44"><circle cx="22" cy="22" r="20.5" fill="none" stroke="#7d6233" stroke-width="3"/>'
            f'<circle class="fill" cx="22" cy="22" r="22" fill="#7d6233" style="opacity:0"/>'
            f'<path class="tick" d="M13 22.5l6 5.8L31 16" fill="none" stroke="#7d6233" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
            f'<span>{t}</span></div>')


# image start line (first row where the drawing begins), measured: row std > 12
START = {"A-1-hook.png": 916, "A-2-why.png": 981, "A-3-how.png": 956, "B-1-hook.png": 903, "B-3-how.png": 905, "B-2b-box.png": 990}


def film_spec(film, cut):
    """Scenes: dict(id, t0, img, badge, block, swap=(t, html) | None, accent=(kind, t) | None)."""
    def S(**k):
        k.setdefault("swap", None)
        k.setdefault("accent", None)
        return k
    if film == "A":
        V = VA
        hook = eb("AI에게 물었다") + ld("전문대 나왔는데,") + hx("퇴근하고 법 공부", "할 수 있을까?")
        if cut == 30:
            T = dict(s1=0, s2=V[3], s3=V[7], s4=V[12], act=V[14], end=30)
            sc = [
                S(id="s1", t0=T["s1"], img="A-1-hook.png", badge="", block=hook),
                S(id="s2", t0=T["s2"], img="A-2-why.png", badge="",
                  block=eb("AI 시대, 남는 자리") + ld("AI가 일을 대신할수록,")
                  + hx('<span class="ul">책임지는<i class="bar"></i></span> 사람이', "필요해집니다.")
                  + bx("판단과 책임은 사람의 몫, 법학은 그 기초입니다"),
                  accent=("underline", V[5])),
                S(id="s3", t0=T["s3"], img="A-3-how.png", badge="",
                  block=eb("지금 있는 자리에서") + ld("퇴근 후·주말에,") + hx("100% 온라인으로")
                  + '<div class="cks">' + ckf("전문대 졸업이면 60학점부터") + ckf("교육부장관 명의 법학사")
                  + ckf("이미 딴 학점은 기간·비용 절감") + "</div>",
                  accent=("fill", V[9])),
            ]
        else:
            T = dict(s1=0, s3=V[2], s4=V[5], act=V[6], end=15)
            sc = [
                S(id="s1", t0=T["s1"], img="A-1-hook.png", badge="", block=hook),
                S(id="s3", t0=T["s3"], img="A-3-how.png", badge="",
                  block=eb("지금 있는 자리에서") + ld("퇴근 후·주말에,") + hx("100% 온라인으로")
                  + '<div class="cks">' + ckf("전문대 졸업이면 60학점부터") + ckf("교육부장관 명의 법학사") + "</div>",
                  accent=("fill", V[3])),
            ]
        end = end_card(film, cut, "내 학점이면,", "")
    else:
        V = VB
        if cut == 30:
            T = dict(s1=0, s2=V[3], sign=V[4], swap=V[5], s3=V[6], usp=V[8] + 0.5 * (V[9] - V[8]), s4=V[11], act=V[12], end=30)
        else:
            T = dict(s1=0, s2=V[2], sign=V[2] + 0.5, swap=V[3], s3=V[4], s4=V[5] + 0.5 * (V[6] - V[5]), act=V[5] + 0.5 * (V[6] - V[5]), end=15)
        sc = [S(id="s1", t0=T["s1"], img="B-1-hook.png", badge="가상 인물",
                block=eb("이력서의 첫 줄") + hx("15년 경력.") + ld("이력서 첫 줄에서<br>멈췄습니다.")),
              S(id="s2", t0=T["s2"], img="B-2b-box.png", badge="",
                block=eb("남은 한 칸") + ld("경력은 증명됐습니다.") + hx("학력 칸만", "남았어요."),
                swap=(T["swap"], eb("남은 한 칸") + ld("이 칸의 이름,") + hx('<span class="gold">당신.</span>')),
                accent=("sign", T["sign"]))]
        usp = ld("국내 유일*") + hx("100% 온라인", "법학사") + bx("교육부장관 명의 · '법학 전공' 표기") + foot_line()
        if cut == 30:
            sc.append(S(id="s3", t0=T["s3"], img="B-3-how.png", badge="",
                        block=eb("퇴근 후·주말에, 100% 온라인으로") + ld("이미 딴 학점이 있으면,") + hx("기간·비용을", "줄일 수 있어요.")
                        + bx("학점 기준으로 남은 과정을 1:1로 짚어 드려요"),
                        swap=(T["usp"], eb("퇴근 후·주말에, 100% 온라인으로") + usp)))
        else:
            sc.append(S(id="s3", t0=T["s3"], img="B-3-how.png", badge="",
                        block=eb("퇴근 후·주말에, 100% 온라인으로") + usp))
        end = end_card(film, cut, "비어 있던 학력 칸,", FOOT_UNIQUE)
    return V, T, sc, end


# ---------------------------------------------------------------- measure the empty box in B-2b
def box_rect():
    p = os.path.join(ILL, "B-2b-box.png")
    if not os.path.exists(p):
        return (108, 960, 972, 1152)
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", "scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(1920, 1080).astype(float)
    dark = (g < 160)
    rows = [y for y in range(700, 1400) if dark[y].sum() > 520]
    if len(rows) < 2:
        return (108, 960, 972, 1152)
    y0 = rows[0]
    # bottom line: first long line after y0 + 60
    y1 = next((y for y in rows if y > y0 + 60), y0 + 190)
    band = dark[y0 + 10:y1 - 10]
    cols = [x for x in range(1080) if band[:, x].sum() > (y1 - y0 - 20) * 0.6]
    x0, x1 = (cols[0], cols[-1]) if cols else (108, 972)
    return (x0, y0, x1, y1)


# ---------------------------------------------------------------- HTML
CSS = """
@font-face { font-family: "PretendardGOV"; src: url("assets/fonts/PretendardGOV-subset.woff2") format("woff2"); font-weight: 45 930; }
#root { position: absolute; inset: 0; overflow: hidden; font-family: "PretendardGOV", sans-serif; color: #161616; word-break: keep-all; background: #fbf9f4; }
.sc { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; opacity: 0; }
.plate { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 540px 1920px; }
.plate img { display: block; width: 1080px; height: 1920px; }
.col { position: absolute; left: 84px; width: 912px; }
.badge { position: absolute; left: 84px; top: 140px; font-size: 30px; line-height: 42px; font-weight: 600; color: #6b6660; white-space: nowrap; }
.eb { display: block; font-size: 30px; line-height: 42px; font-weight: 600; letter-spacing: 0.02em; color: #7d6233; margin-bottom: 14px; white-space: nowrap; }
.ld { display: block; font-size: 64px; line-height: 82px; font-weight: 500; letter-spacing: -0.03em; color: #7d6233; white-space: nowrap; }
.hx { display: block; font-size: 120px; line-height: 134px; font-weight: 700; letter-spacing: -0.045em; color: #161616; white-space: nowrap; }
.ld + .hx { margin-top: 10px; }
.hx + .ld { margin-top: 18px; }
.hx + .bx { margin-top: 22px; }
.bx { display: block; font-size: 40px; line-height: 58px; font-weight: 400; letter-spacing: -0.01em; color: #6b6660; white-space: nowrap; }
.bx b { font-weight: 600; color: #161616; }
.bx.ink { color: #161616; }
.ck { display: flex; align-items: center; gap: 20px; font-size: 40px; line-height: 58px; font-weight: 500; letter-spacing: -0.01em; color: #161616; white-space: nowrap; }
.ck svg { width: 44px; height: 44px; flex: none; display: block; }
.ck + .ck { margin-top: 16px; }
.hx + .ck, .blk > .ck:first-child { margin-top: 0; }
.w { display: inline-block; }
.gold { color: #7d6233; }
.arr { display: inline-block; width: 32px; height: 40px; vertical-align: -8px; margin-left: 12px; overflow: visible; }
.arr path { fill: none; stroke: #7d6233; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
#e-logo { display: flex; align-items: center; gap: 18px; font-size: 40px; line-height: 62px; font-weight: 700; letter-spacing: -0.02em; color: #161616; white-space: nowrap; }
.mark { display: block; width: 56px; height: 62px; background: #161616; -webkit-mask: url("assets/img/mark.svg") center / contain no-repeat; mask: url("assets/img/mark.svg") center / contain no-repeat; }
#tk { position: absolute; left: 0; top: 1580px; width: 1080px; height: 340px; background: #0b1a33; overflow: hidden; }
#tk-row { position: absolute; left: 0; top: 76px; white-space: nowrap; font-size: 40px; line-height: 60px; font-weight: 600; letter-spacing: 0.04em; color: #e0c27e; }
#tk-row i { font-style: normal; display: inline-block; margin: 0 28px; font-size: 30px; vertical-align: 4px; }
.small { position: absolute; left: 84px; font-size: 30px; line-height: 42px; font-weight: 400; color: #6b6660; white-space: nowrap; }
.sc { visibility: hidden; }
.mv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
.dial { position: absolute; left: 560px; top: 0; width: 520px; height: 520px; overflow: visible; }
.dial circle { fill: none; stroke: #7d6233; stroke-opacity: 0.35; stroke-width: 1.5; }
.ul { position: relative; display: inline-block; }
.bar { position: absolute; left: 0; right: 0; bottom: 4px; height: 8px; background: #7d6233; transform-origin: 0 50%; transform: scaleX(0); }
.cks { display: block; margin-top: 34px; }
.hx + .bx { margin-top: 26px; }
"""

JS_HEAD = """
(function () {
  const A = window.anime;
  const ms = (t) => Math.round(t * 30) * 1000 / 30;
  const EXPO = A.cubicBezier(0.16, 1, 0.3, 1), INOUT = A.cubicBezier(0.45, 0, 0.55, 1), DRAWE = A.cubicBezier(0.76, 0, 0.24, 1), IN3 = A.cubicBezier(0.55, 0.055, 0.675, 0.19);
  const tl = A.createTimeline({ autoplay: false });
  window.__hfAnime = window.__hfAnime || []; window.__hfAnime.push(tl);
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  // split text nodes into word spans (keeps svg/icons as units)
  function split(root) {
    const out = [];
    const walk = (n) => Array.from(n.childNodes).forEach((c) => {
      if (c.nodeType === 3) {
        const parts = c.textContent.split(/(\\s+)/); const f = document.createDocumentFragment();
        parts.forEach((p) => { if (!p) return; if (/^\\s+$/.test(p)) f.appendChild(document.createTextNode(p)); else { const s = document.createElement("span"); s.className = "w"; s.textContent = p; f.appendChild(s); out.push(s); } });
        n.replaceChild(f, c);
      } else if (c.nodeType === 1 && c.tagName.toLowerCase() === "svg") out.push(c);
      else if (c.nodeType === 1 && !c.classList.contains("w")) walk(c);
    });
    walk(root); return out;
  }
  function words(els, t) { tl.set(els, { opacity: 0 }, 0); els.forEach((el, i) => tl.add(el, { opacity: [0, 1], filter: ["blur(6px)", "blur(0px)"], duration: 130, ease: EXPO }, ms(t + i * 0.067))); }
  function wordsOut(els, t) { els.forEach((el, i) => tl.add(el, { opacity: [1, 0], filter: ["blur(0px)", "blur(6px)"], duration: 180, ease: IN3 }, ms(t + i * 0.03))); }
  function show(sel, t) { tl.set(sel, { opacity: 1, visibility: "visible" }, ms(t)); }
  function hide(sel, t) { tl.set(sel, { opacity: 0, visibility: "hidden" }, ms(t)); }
  function push(sel, t0, t1) { tl.add(sel, { scale: [1, 1.06], duration: ms(t1) - ms(t0), ease: INOUT }, ms(t0)); }
  // scene layout: block bottom = drawing start - 56; the plate rises (<= 260 px) so the block top sits near y 300
  function layout(sid, start, kmax) {
    const b0 = $("#" + sid + "-b0"), b1 = $("#" + sid + "-b1"), mv = $("#" + sid + "-mv");
    const H = Math.max(b0.offsetHeight, b1 ? b1.offsetHeight : 0);
    // grow the drawing from the bottom edge (<= 1.15x) so it starts higher and still fills the bottom
    const want = ($("#" + sid + " .badge") ? 236 : 176) + H + 56;
    const k = Math.max(1, Math.min(kmax, (1920 - want) > 0 ? (1920 - want) / (1920 - start) : kmax));
    // kmax 1 (paper with the empty box): no scaling, slide the sheet up instead; the paper colour fills under it
    const lift = kmax === 1 ? Math.max(0, Math.min(220, start - want)) : 0;
    const w = 1080 * k, h = 1920 * k, l = -(w - 1080) / 2, t = 1920 - h - lift;
    mv.querySelectorAll("img, #sig").forEach((el) => { el.style.position = "absolute"; el.style.left = l + "px"; el.style.top = t + "px"; el.style.width = w + "px"; el.style.height = h + "px"; });
    if (lift) $("#" + sid).style.background = "#fbefe3";
    const bottom = Math.round(1920 - (1920 - start) * k) - lift - 56;
    [b0, b1].forEach((b) => { if (b) b.style.top = (bottom - b.offsetHeight) + "px"; });
  }
  // next scene's drawing rises 120 px into place while fading in (0.5 s expo-out); paper never cuts
  function rise(sel, t) { tl.add(sel, { translateY: [120, 0], opacity: [0, 1], duration: 500, ease: EXPO }, ms(t)); }
  // block lands top-down inside 1 s: eyebrow 0, lead .10, head .20 (+.07 per line), body/checks .45 (+.08 each)
  function land(sel, t) {
    const kids = Array.from($(sel).children); let hxn = 0, bn = 0;
    kids.forEach((c) => {
      let off;
      if (c.classList.contains("eb")) off = 0;
      else if (c.classList.contains("ld")) off = 0.10;
      else if (c.classList.contains("hx")) off = 0.20 + 0.07 * hxn++;
      else off = 0.45 + 0.08 * bn++;
      const units = c.classList.contains("cks") ? Array.from(c.children) : split(c);
      tl.set(units, { opacity: 0 }, 0);
      units.forEach((u, i) => tl.add(u, { opacity: [0, 1], filter: ["blur(6px)", "blur(0px)"], duration: 130, ease: EXPO }, ms(t + off + i * (c.classList.contains("cks") ? 0.08 : 0.04))));
    });
  }
  function leave(sel, t) { tl.add(sel, { opacity: [1, 0], filter: ["blur(0px)", "blur(6px)"], duration: 180, ease: IN3 }, ms(t)); }
"""


def build(film, cut):
    V, T, scenes, end = film_spec(film, cut)
    out = os.path.join(HERE, f"{film}{cut}")
    if os.path.exists(out):
        for d in ("compositions", "assets"):
            shutil.rmtree(os.path.join(out, d), ignore_errors=True)
    for d in ("compositions", "assets/img", "assets/fonts", "assets/audio", "lib"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    # assets
    for sc_ in scenes:
        img = sc_["img"]
        src = os.path.join(ILL, img)
        os.link(src, os.path.join(out, "assets/img", img)) if not os.path.exists(os.path.join(out, "assets/img", img)) else None
    for img in ("A-4-stairs.png",):
        dst = os.path.join(out, "assets/img", img)
        if not os.path.exists(dst):
            os.link(os.path.join(ILL, img), dst)
    open(os.path.join(out, "assets/img/mark.svg"), "w").write(open(os.path.join(SH, "img", "mark-gold.svg")).read())
    shutil.copy(os.path.join(NC, "ask-ai", "lib", "anime.min.js"), os.path.join(out, "lib", "anime.min.js"))

    html, js = [], []
    order = [s["id"] for s in scenes] + ["s4"]
    starts = [s["t0"] for s in scenes] + [T["s4"]]
    nxt = dict(zip(order, starts[1:] + [T["end"]]))
    dial = ('<svg class="dial" viewBox="0 0 520 520" data-layout-ignore>'
            + "".join(f'<circle cx="400" cy="120" r="{r}"/>' for r in (70, 130, 190, 250, 310)) + "</svg>")
    for k, s in enumerate(scenes):
        sid, t0, img = s["id"], s["t0"], s["img"]
        t1 = nxt[sid]
        first = (t0 == 0)
        h = [f'<div id="{sid}" class="sc" data-layout-allow-overflow>', dial,
             f'<div id="{sid}-mv" class="mv" data-layout-allow-overflow>',
             f'<div id="{sid}-pl" class="plate"><img src="assets/img/{img}" alt="" data-fill/>']
        if s["accent"] and s["accent"][0] == "sign":
            h += sign_html(cut)
        h.append("</div></div>")
        if s["badge"]:
            h.append(f'<div class="badge">{s["badge"]}</div>')
        h.append(f'<div id="{sid}-b0" class="col blk">{s["block"]}</div>')
        if s["swap"]:
            h.append(f'<div id="{sid}-b1" class="col blk">{s["swap"][1]}</div>')
        h.append("</div>")
        html.append("\n".join(h))
        # layout: text block sits just above the drawing; the plate rises so the block starts near y 300
        js.append(f'layout("{sid}", {START[img]}, {1.0 if img.startswith("B-2") else 1.2});')
        js.append(f'show("#{sid}", {t0:.3f}); hide("#{sid}", {t1:.3f}); push("#{sid}-pl", {t0:.3f}, {t1:.3f});')
        if not first:
            js.append(f'rise("#{sid}-mv", {t0:.3f});')
            js.append(f'land("#{sid}-b0", {t0 + 0.1:.3f});')
        if t1 < T["end"]:
            js.append(f'leave("#{sid}-b{1 if s["swap"] else 0}", {t1 - 0.2:.3f});')
        if s["swap"]:
            ts = s["swap"][0]
            js.append(f'tl.set("#{sid}-b1", {{ opacity: 0 }}, 0); leave("#{sid}-b0", {ts - 0.25:.3f}); tl.set("#{sid}-b1", {{ opacity: 1 }}, ms({ts:.3f})); land("#{sid}-b1", {ts:.3f});')
        if s["accent"]:
            kind, ta = s["accent"]
            if kind == "underline":
                js.append(f'tl.add("#{sid} .bar", {{ scaleX: [0, 1], duration: 600, ease: DRAWE }}, ms({ta:.3f}));')
            elif kind == "fill":
                js.append(f'$$("#{sid} .ckf").forEach((r, i) => {{ tl.add(r.querySelector(".fill"), {{ opacity: [0, 1], duration: 220, ease: EXPO }}, ms({ta:.3f} + i * 0.2)); tl.add(r.querySelector(".tick"), {{ stroke: ["#7d6233", "#fbf9f4"], duration: 220, ease: EXPO }}, ms({ta:.3f} + i * 0.2)); }});')
            elif kind == "sign":
                js += sign_js(T, cut)

    # ---- end card
    shift = -240
    a = end["act"]
    ec = ['<div id="s4" class="sc" data-layout-allow-overflow style="background:#faf5f3">',
          f'<div id="s4-pl" class="plate" style="top:{shift}px"><img src="assets/img/A-4-stairs.png" alt="" data-fill/></div>',
          f'<div id="s4-slo" class="col" style="top:560px">{end["slogan"]}</div>',
          '<div id="s4-act" class="col" style="top:0">']
    for k, inner in a:
        ec.append(f'<div id="e-{k}" class="blk">{inner}</div>')
    ec.append("</div>")
    if end["foot"]:
        ec.append(f'<div id="e-foot" class="small" style="top:1452px">{end["foot"]}</div>')
    ec.append(f'<div id="e-disc" class="small" style="top:1500px">{DISCLAIMER}</div>')
    tk = "<i>◆</i>".join(["헌법", "민법", "형법", "행정법", "상법", "민사소송법"] * 2)
    ec.append(f'<div id="tk"><div id="tk-row">{tk}</div></div>')
    ec.append("</div>")
    html.append("\n".join(ec))
    S4, ACT, END = T["s4"], T["act"], T["end"]
    short = ACT - S4 < 1.0  # no room for the big slogan phase (B 15 s): the action block opens the card
    slo_in = 'tl.set("#s4-slo", { opacity: 0 }, 0);' if short else f'words(split($("#s4-slo")), {S4 + 0.15:.3f});'
    slo_out = "" if short else f'wordsOut($$("#s4-slo .w"), {ACT - 0.3:.3f});'
    js.append(f"""
  show("#s4", {S4:.3f});
  // end-card action block stacked from y 600 (logo) downward; gaps fixed
  (function () {{
    const gaps = {{ logo: 0, sl: 18, eb2: 46, hd: 0, ck: 34, link: 40, tel: 10 }};
    let y = 500;
    ["logo","sl","eb2","hd","ck","link","tel"].forEach((k) => {{ const el = $("#e-" + k); y += gaps[k]; el.style.position = "absolute"; el.style.left = "0px"; el.style.top = y + "px"; y += el.offsetHeight; }});
  }})();
  tl.set("#s4-act", {{ opacity: 0 }}, 0);
  {slo_in}
  tl.add("#tk-row", {{ translateX: [0, -300], duration: ms({END}) - ms({S4}), ease: "linear" }}, ms({S4}));
  tl.set(["#e-disc"{', "#e-foot"' if end["foot"] else ''}], {{ opacity: 0 }}, 0);
  tl.add(["#e-disc"{', "#e-foot"' if end["foot"] else ''}], {{ opacity: [0, 1], duration: 200 }}, ms({ACT + 0.6:.3f}));
  {slo_out}
  tl.set("#s4-act", {{ opacity: 1 }}, ms({ACT:.3f}));
  // every action block lands within 0.9 s, top to bottom
  {{ const off = {{ logo: 0, sl: 0.08, eb2: 0.16, hd: 0.24, ck: 0.5, link: 0.66, tel: 0.76 }};
    Object.keys(off).forEach((k) => {{ const el = $("#e-" + k); const u = (k === "logo" || k === "ck") ? Array.from(el.children) : split(el);
      tl.set(u, {{ opacity: 0 }}, 0); u.forEach((w, i) => tl.add(w, {{ opacity: [0, 1], filter: ["blur(6px)", "blur(0px)"], duration: 130, ease: EXPO }}, ms({ACT:.3f} + off[k] + i * (k === "ck" ? 0.08 : 0.03)))); }}); }}
  tl.add("#s4-pl", {{ translateY: [-120, 0], opacity: [0, 1], duration: 500, ease: EXPO }}, ms({S4:.3f}));
""")
    js.append(f"tl.set({{ v: 0 }}, {{ v: 1 }}, ms({END}));\n  tl.seek(0);\n}})();")

    film_html = (f'<template>\n<style>{CSS}{SIGN_CSS if film == "B" else ""}</style>\n'
                 f'<div id="root" data-composition-id="film" data-width="1080" data-height="1920">\n'
                 + "\n".join(html) + "\n</div>\n<script>" + JS_HEAD + "\n  " + "\n  ".join(js) + "\n</script>\n</template>\n")
    open(os.path.join(out, "compositions", "film.html"), "w").write(film_html)

    index = f"""<!doctype html>
<html lang="ko" data-resolution="portrait">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="lib/anime.min.js"></script>
<style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #fbf9f4; }}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{cut}" data-fps="30" data-width="1080" data-height="1920">
  <!-- v8 {film} {cut}s — 05-v8-illustration.md. Scenes cut on bar downbeats: {json.dumps({k: round(v, 3) for k, v in T.items()})} -->
  <div id="film" class="clip" data-composition-id="film" data-composition-src="compositions/film.html" data-start="0" data-duration="{cut}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:1"></div>
  <audio id="bgm" class="clip" src="assets/audio/bgm.wav" data-start="0" data-duration="{cut}" data-track-index="2" data-volume="1"></audio>
</div>
<script>window.__timelines = window.__timelines || {{}};</script>
</body>
</html>
"""
    open(os.path.join(out, "index.html"), "w").write(index)
    for f in ("hyperframes.json", "meta.json"):
        src = os.path.join(NC, "ask-ai", f)
        if os.path.exists(src) and not os.path.exists(os.path.join(out, f)):
            shutil.copy(src, os.path.join(out, f))
    json.dump({"film": film, "cut": cut, "T": T, "bars": V[:17]}, open(os.path.join(out, "cues.json"), "w"), indent=1)
    make_audio(film, cut, out)
    subset_font(out)
    print(out, {k: round(v, 3) for k, v in T.items()})


# ---------------------------------------------------------------- B scene 2: gold "You" in the empty box
SIGN_CSS = """
#sig { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
#you { fill: none; stroke: #7d6233; stroke-linecap: round; stroke-linejoin: round; }
"""


def sign_html(cut):
    x0, y0, x1, y1 = box_rect()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w = (x1 - x0) * 0.78
    s = w / (YOU_BOX[2] - YOU_BOX[0])
    bxc, byc = (YOU_BOX[0] + YOU_BOX[2]) / 2, YOU_BASE  # baseline sits a bit under the box centre
    tx, ty = cx - bxc * s, (y1 - 18) - byc * s
    return [f'<svg id="sig" viewBox="0 0 1080 1920" data-layout-ignore><g transform="translate({tx:.1f} {ty:.1f}) scale({s:.4f})">'
            f'<path id="you" d="{YOU_PATH}" stroke-width="{6 / s:.2f}"/></g></svg>']


def sign_js(T, cut):
    return ['{ const d = A.svg.createDrawable("#you"); tl.set(d, { draw: "0 0" }, 0);'
            f' tl.add(d, {{ draw: ["0 0", "0 1"], duration: 1100, ease: DRAWE }}, ms({T["sign"]:.3f})); }}']


# ---------------------------------------------------------------- audio: one continuous excerpt, -15 LUFS
def make_audio(film, cut, out):
    src = os.path.join(SH, "music", "C-alexbesss-news-background-602905.mp3" if film == "A" else "D-nastelbom-news-news-music-629329.mp3")
    start = A_IN if film == "A" else B_IN
    dst = os.path.join(out, "assets", "audio", "bgm.wav")
    tmp = dst + ".tmp.wav"
    fade = f"afade=t=out:st={cut - 0.3}:d=0.3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start}", "-t", f"{cut}", "-i", src, "-af",
                    f"{fade},alimiter=limit=0.89:attack=1:release=50:level=false", "-ar", "48000", "-ac", "2", tmp], check=True)
    # two-pass loudnorm to -15 LUFS, TP -1.5
    m = subprocess.run(["ffmpeg", "-v", "info", "-i", tmp, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    af = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", "48000", "-ac", "2", "-t", f"{cut}", dst], check=True)
    os.remove(tmp)


def subset_font(out):
    chars = set(open(os.path.join(out, "compositions", "film.html"), encoding="utf-8").read())
    chars |= set(" 0123456789…·–※*:'%(),.?!「」◆")
    chars = {c for c in chars if c.isprintable() and ord(c) < 0x1F000}
    subprocess.run([sys.executable, "-m", "fontTools.subset", os.path.join(SH, "fonts", "PretendardGOVVariable.woff2"),
                    "--text=" + "".join(sorted(chars)), "--flavor=woff2", "--layout-features=*",
                    "--output-file=" + os.path.join(out, "assets", "fonts", "PretendardGOV-subset.woff2")], check=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["A30", "A15", "B30", "B15"]
    for w in which:
        build(w[0], int(w[1:]))
