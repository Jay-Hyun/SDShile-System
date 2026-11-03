"""「마지막 서명」 편 B 재취업 — v7 scene generator (anime.js v4). 30s at the project root, 15s in v15/.

Usage (from the project root):
  python3 tools/build.py              # compositions/*.html + index.html      (30s)
  python3 tools/build.py --variant 15 # v15/compositions/*.html + v15/index.html (15s)

Direction: docs/ads/naver-clip/04-v7-visual.md §1, §3 (+ 02-art-direction §1-2, §7-2). The world is daylight
paper and ink plus photographs (assets/img/*.jpg, generated, no faces, no text). Navy appears only on the end
card, reached by a colour flood. Gold (#B8955A) is the "You" stroke, the career checks, one word per screen and
the end-card line. Sizes 144 / 88 / 44 / 26 only, every text row centred on x=540.

Transitions (each caused): the résumé's signature box grows into the next world (object -> world), a hard cut on
the pen's touch (30s), dip cuts photo -> photo (3 frames at 40% darker), a paper card revealed by a mask, and a
Navy colour flood into the end card. Text entrances: masked line rise twice (USP display, slogan); otherwise
per-word blur 6px -> 0 (0.13s, 67ms apart), grey -> ink sweeps, or ink "printing" (clip reveal). Landed titles
hold dead still. One hero move per shot (a 1.00 -> 1.06 push or a 50px pan, power2.inOut over the shot).

Engine: anime.js v4 only (lib/anime.umd.min.js). Every scene builds ONE paused timeline and pushes it to
window.__hfAnime; HyperFrames seeks each to the ROOT time in ms, so every position below is absolute video time.
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = open(os.path.join(ROOT, "tools", "common.css"), encoding="utf-8").read()
VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "30"
OUT = ROOT if VARIANT == "30" else os.path.join(ROOT, "v15")
TOTAL = 30.0 if VARIANT == "30" else 15.0
FPS = 30

# ---------------------------------------------------------------- beat grid (NastelBom, 119.97 BPM)
BEATS = json.load(open(os.path.join(ROOT, "beats", "source.json")))
OFFSET = 1.765           # excerpt in-point = the track's first downbeat (music from frame 0)
_i0 = min(range(len(BEATS["beats"])), key=lambda k: abs(BEATS["beats"][k] - OFFSET))
GRID = [round(b - BEATS["beats"][_i0], 3) for b in BEATS["beats"][_i0:]]
DOWN = [round(d - OFFSET, 3) for d in BEATS["downbeats"] if d >= OFFSET - 0.01]


def fr(t):
    """snap to the frame grid"""
    return round(round(t * FPS) / FPS, 4)


def B(k):
    """k-th beat of the excerpt (video seconds, frame-snapped)"""
    return fr(GRID[k])


def D(k):
    """k-th downbeat (bar line) of the excerpt (video seconds, frame-snapped)"""
    return fr(DOWN[k])


def is_down(t):
    return any(abs(t - d) < 0.035 for d in DOWN)


# ---------------------------------------------------------------- html helpers
def words(line):
    """a line as word spans; a word starting with '!' is gold"""
    out = []
    for w in line.split(" "):
        g = w.startswith("!")
        w = w.lstrip("!")
        out.append(f'<span class="w{" au" if g else ""}"{" data-gold" if g else ""}>{w}</span>')
    return " ".join(out)


def text(id_, size, top, lines, tone="ink", mode="", tx=False, style="", cls="", swap=False):
    """centred text block, one block per line. mode: '' (static), 'rise' (masked line), 'wb' (word blur-in),
    'sw' (grey -> ink sweep). tx marks texture (résumé entries in 15s, day labels): skipped by the reading audit."""
    lis = "".join(f'<span class="ln"><span id="{id_}-{i}" class="li">{words(t)}</span></span>' for i, t in enumerate(lines))
    gold = ' data-gold' if tone == "au" else ""
    return (f'<div id="{id_}" class="row t-{size} {tone}{" " + mode if mode else ""}{" " + cls if cls else ""}"{" data-tx" if tx else ""}{" data-layout-allow-overlap" if swap else ""}{gold} '
            f'style="top:{top}px;{style}">{lis}</div>')


def lockup(id_, top):
    return (f'<div id="{id_}" class="row lock later" style="top:{top}px">'
            f'<div class="lockrow" data-lockup><span class="lmark" data-gold></span><span>{BRAND}</span></div></div>')


BRAND = "경찰복지사이버평생교육원"
CHECK_D = "M4.5 12.5l4.6 4.6L19.5 6.8"
PAPER_BOX = "#ebebe8"      # the résumé box's own white (sampled from B-01), the first frame of the grow


# ---------------------------------------------------------------- anime.js helpers (absolute seconds)
HELPERS = r"""
    const tl = anime.createTimeline({ autoplay: false });
    const ms = (s) => Math.round(s * 1000);
    const EXPO = anime.cubicBezier(0.16, 1, 0.3, 1);            // arrivals: long tail
    const INOUT2 = anime.cubicBezier(0.45, 0, 0.55, 1);         // camera, colour flood (power2.inOut)
    const INOUT = anime.cubicBezier(0.76, 0, 0.24, 1);          // object -> world, line drawing
    const IN3 = anime.cubicBezier(0.32, 0, 0.67, 0);            // exits accelerate (power3.in)
    const OUT = anime.cubicBezier(0.22, 1, 0.36, 1);
    function A(t, sel, props, dur, ease) { tl.add(sel, Object.assign({ duration: Math.max(1, ms(dur)), ease: ease || OUT }, props), ms(t)); }
    function S(t, sel, props) { tl.set(sel, props, ms(t)); }
    // masked line rise (800 ms expo-out, 90 ms between lines) -- used twice per film
    function RISE(t, sels) { sels.forEach((s, i) => { S(t + i * 0.09, s, { opacity: 1 }); A(t + i * 0.09, s, { translateY: ["110%", "0%"] }, 0.8, EXPO); }); }
    // per-word blur-in: blur 6px -> 0 and opacity 0 -> 1 in 0.13 s, 67 ms apart, no translate
    function WB(t, sel) { tl.add(sel + " .w", { opacity: [0, 1], filter: ["blur(6px)", "blur(0px)"], duration: 130, delay: anime.stagger(67), ease: OUT }, ms(t)); }
    // per-word exit: blur-out and fade, 0.18 s, 40 ms apart
    function WOUT(t, sel) { tl.add(sel + " .w", { opacity: [1, 0], filter: ["blur(0px)", "blur(6px)"], duration: 180, delay: anime.stagger(40), ease: IN3 }, ms(t)); }
    // grey -> ink sweep, 85 ms apart
    function SW(t, sel, to) { tl.add(sel + " .w", { color: ["#c9c3b6", to], duration: 120, delay: anime.stagger(85), ease: OUT }, ms(t)); }
    // ink printing into a box: a left -> right clip reveal
    function PRINT(t, sel) { S(t, sel, { opacity: 1 }); A(t, sel, { clipPath: ["inset(0px 100% 0px 0px)", "inset(0px 0% 0px 0px)"] }, 0.45, EXPO); }
    function CARET(sel, t0, t1) { let on = true; for (let t = t0; t < t1 - 1e-6; t += 0.5) { S(t, sel, { opacity: on ? 1 : 0 }); on = !on; } }
    function DRAW(t0, t, sel, dur, ease) {
      const d = anime.svg.createDrawable(sel);
      S(t0, d, { draw: "0 0" });
      S(t, sel, { opacity: 1 });
      A(t, d, { draw: ["0 0", "0 1"] }, dur, ease || INOUT);
    }
    // dip cut: the outgoing frame darkens ~40% for its last 3 frames
    function DIP(tEnd, sel) { S(tEnd - 0.1, sel, { opacity: 0.4 }); }
"""


def scene(cid, t0, t1, css, html, js):
    s = f'''<template>
  <style>
{COMMON}
    #root {{ background: transparent; }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{html}
  </div>
  <script>
  (function () {{
{HELPERS}
{js}
    window.__hfAnime = window.__hfAnime || [];
    window.__hfAnime.push(tl);
  }})();
  </script>
</template>
'''
    os.makedirs(os.path.join(OUT, "compositions"), exist_ok=True)
    open(os.path.join(OUT, "compositions", cid + ".html"), "w", encoding="utf-8").write(s)
    return (cid, round(t0, 3), round(t1 - t0, 3))


def J(x):
    return json.dumps(x)


# ============================================================ RÉSUMÉ plate (B-01), measured box rectangles
# B-01 is 1060x1484. Lines measured from its pixels (tools: numpy on the PNG):
#   table 1 rows y 582 / 638 / 691 / 743, columns x 121 | 283 | 930   -> career entries (3)
#   table 2 rows y 770 / 824 / 876 / 929, columns x 116 | 280 | 937   -> 학력 (left empty, caret)
#   big box y 962-1167, x 110-943 (the pen hovers over it)             -> the signature box that becomes the world
# Plate scale 1.34 (1.035x beyond cover). x offset puts the right column's centre (608.5) on x=540.
R_S = 1.34
R_W, R_H = 1060 * R_S, 1484 * R_S
R_LEFT = 540 - 608.5 * R_S
R_TOP = -68
BAND = 640                        # paper band 0..640 carries the captions; the photo shows below it
PUSH_O = (540, BAND)              # push origin: the band's edge stays put, the page grows downwards
PUSH, PAN = 1.06, -50


def r_y(img_y):
    return img_y * R_S + R_TOP


def r_final(x, y):
    """frame position after the push (1.06 about PUSH_O) and the pan (-50px)"""
    return ((x - PUSH_O[0]) * PUSH + PUSH_O[0], (y - PUSH_O[1]) * PUSH + PUSH_O[1] + PAN)


T1 = [(582, 638), (638, 691), (691, 743)]
T2 = [(770, 824), (824, 876), (876, 929)]
SIGBOX = (110, 962, 943, 1167)
_x0, _y0 = r_final(SIGBOX[0] * R_S + R_LEFT, r_y(SIGBOX[1]))
_x1, _y1 = r_final(SIGBOX[2] * R_S + R_LEFT, r_y(SIGBOX[3]))
BOX_INSET = f"inset({max(0, _y0):.1f}px {max(0, 1080 - _x1):.1f}px {max(0, 1920 - _y1):.1f}px {max(0, _x0):.1f}px)"
CAREER = ["영업관리 팀장 · 8년", "현장 운영 총괄 · 5년", "고객 상담 리더 · 2년"]


def build_resume(T, compact=False):
    css = f"""
    #r-band {{ left: 0; top: 0; width: 1080px; height: {BAND}px; }}
    #r-pan {{ position: absolute; inset: 0; }}
    #r-push {{ position: absolute; inset: 0; transform-origin: {PUSH_O[0]}px {PUSH_O[1]}px; }}
    .ent {{ display: inline-block; position: relative; }}
    .ok {{ position: absolute; left: calc(100% + 16px); top: 50%; width: 40px; height: 40px; margin-top: -20px; overflow: visible; }}
    .ok path {{ fill: none; stroke: #b8955a; stroke-width: 2.8; stroke-linecap: square; }}
"""
    ents = []
    for i, ((a, b), t) in enumerate(zip(T1, CAREER)):
        cy = (r_y(a) + r_y(b)) / 2
        ok = f'<svg class="ok" viewBox="0 0 24 24" data-gold><path id="r-k{i}" d="{CHECK_D}" style="opacity:0"/></svg>'
        ents.append(f'<div id="r-e{i}" class="row t-body ink"{" data-tx" if compact else ""} style="top:{cy - 31:.1f}px">'
                    f'<span class="ln" style="overflow:visible"><span class="li"><span id="r-p{i}" class="ent" style="opacity:0">{t}{ok}</span></span></span></div>')
    cy2 = (r_y(T2[0][0]) + r_y(T2[0][1])) / 2
    hook2 = ["이력서 첫 줄에서", "멈췄습니다."]
    html = f'''    <div id="r-cam" data-layout-allow-overflow>
      <div id="r-pan" data-layout-allow-overflow>
        <div id="r-push" data-layout-allow-overflow>
          <img id="r-plate" class="plate" src="assets/img/B-01-resume-desk.jpg" alt="" style="left:{R_LEFT:.1f}px;top:{R_TOP}px;width:{R_W:.1f}px;height:{R_H:.1f}px">
          {"".join(ents)}
          <div id="r-car" class="caret ink" style="left:538px;top:{cy2 - 26:.1f}px;height:52px;opacity:0"></div>
        </div>
      </div>
    </div>
    <div id="r-band" class="paper" data-paper></div>
    {text("r-h1", "display", 215, ["15년 경력."], "ink")}
    {text("r-h2", "head", 390, hook2, "ink", swap=True)}
    {text("r-c1", "head", 303, ["경력은 증명됐습니다."], "ink", "wb", swap=True)}
    {text("r-c2", "head", 404, ["학력 칸만 남았어요."], "ink", "sw", swap=True)}'''
    js = f"""
    const T = {J(T)};
    // hero move 1: push 1.00 -> 1.06 over bar 1; hero move 2: pan 50px down the page over the rest of the shot
    A(0, "#r-push", {{ scale: [1, {PUSH}] }}, T.push1, INOUT2);
    A(T.push1, "#r-pan", {{ translateY: [0, {PAN}] }}, T.end - T.push1, INOUT2);
    T.prints.forEach((t, i) => {{
      if (t > 0) {{ PRINT(t, "#r-p" + i); DRAW(0, t + 0.3, "#r-k" + i, 0.35, OUT); }}
      else {{ S(0, "#r-p" + i, {{ opacity: 1 }}); S(0, "#r-k" + i, {{ opacity: 1 }}); }}   // 15s: already printed at frame 0
    }});
    CARET("#r-car", T.caret, T.end + 0.7);
    WOUT(T.out, "#r-h1"); WOUT(T.out, "#r-h2");
    WB(T.c1, "#r-c1");
    S(T.c2, "#r-c2 .w", {{ opacity: 1 }});
    S(0, "#r-c2", {{ opacity: 0 }}); S(T.c2, "#r-c2", {{ opacity: 1 }});
    SW(T.c2, "#r-c2", "#0e1116");
"""
    return css, html, js


# ============================================================ PEN insert (B-04), 30s only
# The signature box grows past the frame (0.65s in-out) and inside it the close-up of a gold nib resting on a
# blank signature line fades in while it still grows. Cover crop, push 1.00 -> 1.06 about the nib tip.
P_S = 1920 / 1491
P_W = 1055 * P_S
P_LEFT = -(P_W - 1080) / 2
NIB = (597 * P_S + P_LEFT, 1050 * P_S)


def grow_css(sel):
    return f"#{sel} {{ position: absolute; inset: 0; clip-path: {BOX_INSET}; background: {PAPER_BOX}; }}"


def build_pen(T):
    css = f"""
    {grow_css("p-win")}
    #p-push {{ position: absolute; inset: 0; transform-origin: {NIB[0]:.1f}px {NIB[1]:.1f}px; opacity: 0; }}
"""
    html = f'''    <div id="p-win" data-layout-allow-overflow>
      <div id="p-push" data-layout-allow-overflow>
        <img id="p-plate" class="plate" src="assets/img/B-04-pen-line.jpg" alt="" style="left:{P_LEFT:.1f}px;top:0;width:{P_W:.1f}px;height:1920px">
      </div>
    </div>'''
    js = f"""
    const T = {J(T)};
    A(T.c0, "#p-win", {{ clipPath: ["{BOX_INSET}", "inset(0px 0px 0px 0px)"] }}, 0.65, INOUT);
    A(T.c0 + 0.15, "#p-push", {{ opacity: [0, 1] }}, 0.4, OUT);
    A(T.c0, "#p-push", {{ scale: [1, 1.06] }}, T.end - T.c0, INOUT2);
"""
    return css, html, js


# ============================================================ SIGN — the paper world, gold "You"
# One continuous cursive stroke (capital Y, lowercase ou) in a 1080-wide sketch frame (v6 path, kept).
YOU_PATH = ("M 296 214 C 300 176, 352 160, 362 200 C 370 240, 350 300, 380 328 C 410 352, 458 318, 476 262 "
            "C 484 236, 490 206, 498 176 C 494 262, 486 372, 458 432 C 444 462, 404 462, 410 430 "
            "C 418 386, 540 330, 610 300 C 630 290, 640 262, 616 258 C 590 254, 574 290, 584 320 "
            "C 592 344, 628 344, 640 318 C 648 300, 644 280, 634 272 C 650 276, 668 276, 670 292 "
            "C 672 316, 672 338, 692 340 C 716 342, 728 306, 732 278 C 730 310, 734 338, 758 340 "
            "C 800 342, 850 316, 886 266")
YOU_BOX = (296, 176, 886, 454)
YOU_BASE = 341
SIG_S = 1.6
SIG_HEAD_T = 440          # "이 칸의 이름,"
SIG_TOP = 650             # top of the signature's bbox
SIG_CY = SIG_TOP + (YOU_BOX[3] - YOU_BOX[1]) / 2 * SIG_S
SIG_RULE = round(SIG_CY + (YOU_BASE - (YOU_BOX[1] + YOU_BOX[3]) / 2) * SIG_S + 12)
SIG_BOTTOM = SIG_CY + (YOU_BOX[3] - YOU_BOX[1]) / 2 * SIG_S
SIG_YOU_T = round(SIG_BOTTOM + 56)


def you_g(id_, scale, cx, cy):
    bx, by = (YOU_BOX[0] + YOU_BOX[2]) / 2, (YOU_BOX[1] + YOU_BOX[3]) / 2
    return (f'<g transform="translate({cx - bx * scale:.2f} {cy - by * scale:.2f}) scale({scale})">'
            f'<path id="{id_}" d="{YOU_PATH}" stroke="#b8955a" stroke-width="{5 / scale:.3f}" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none" style="opacity:0" data-gold/></g>')


def build_sign(T, grow=False):
    css = f"""
    #s-win {{ position: absolute; inset: 0;{" clip-path: " + BOX_INSET + "; background: " + PAPER_BOX + ";" if grow else ""} }}
    #s-world {{ position: absolute; inset: 0;{" opacity: 0;" if grow else ""} }}
    #s-dock {{ background: #e6dac5; }}
    #s-dip {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
"""
    html = f'''    <div id="s-win" data-layout-allow-overflow>
      <div id="s-world">
        <div class="paper field" data-paper></div>
        <div id="s-dock" class="dock" data-fill data-layout-ignore></div>
        {text("s-h", "head", SIG_HEAD_T, ["이 칸의 이름,"], "ink", "wb")}
        <div id="s-rule" class="rule" style="left:90px;top:{SIG_RULE}px;width:900px;color:#3b3f46"></div>
        <svg class="sv" viewBox="0 0 1080 1920" data-layout-ignore>{you_g("s-ink", SIG_S, 540, SIG_CY)}</svg>
        {text("s-you", "display", SIG_YOU_T, ["!당신."], "ink", "wb")}
      </div>
      <div id="s-dip"></div>
    </div>'''
    js = f"""
    const T = {J(T)};
    if ({str(grow).lower()}) {{
      A(T.c0, "#s-win", {{ clipPath: ["{BOX_INSET}", "inset(0px 0px 0px 0px)"] }}, 0.65, INOUT);
      A(T.c0 + 0.15, "#s-world", {{ opacity: [0, 1] }}, 0.4, OUT);
    }}
    WB(T.head, "#s-h");
    DRAW(T.c0, T.hit, "#s-ink", 1.1, INOUT);
    WB(T.you, "#s-you");
    DIP(T.end, "#s-dip");
"""
    return css, html, js


# ============================================================ BENEFIT — living-room table (B-03) + paper band
# Paper band 0..BENEFIT_BAND carries the week strip (월..일; 토·일 gold) and the line(s); the photo below shows the
# keyboard, the forearm, the plain textbook and the highlighter. Hero move: pan -50px (plate 1129px wide).
L_S = 1.2
L_W, L_H = 941 * L_S, 1672 * L_S
L_TOP = -86
L_BAND = 840
DAYS = ["월", "화", "수", "목", "금", "토", "일"]


def build_benefit(T, compact=False):
    css = f"""
    #b-band {{ left: 0; top: 0; width: 1080px; height: {L_BAND}px; }}
    #b-pan {{ position: absolute; inset: 0; }}
    .dl {{ position: absolute; width: 108px; text-align: center; }}
    .du {{ position: absolute; height: 4px; width: 64px; background: #b8955a; transform-origin: 0 50%; transform: scaleX(0); }}
    #b-dip {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
"""
    week = ""
    for i, d in enumerate(DAYS):
        x = 120 + i * 122
        we = i >= 5
        week += f'<div class="dl t-body sw{" au" if we else ""}"{" data-gold" if we else ""} style="left:{x}px;top:300px"><span class="w">{d}</span></div>'
        if we:
            week += f'<div id="b-u{i}" class="du" data-gold style="left:{x + 22}px;top:372px"></div>'
    l2 = ["이미 딴 학점이 있으면", "기간·비용을", "줄일 수 있어요."]
    html = f'''    <div id="b-pan" data-layout-allow-overflow>
      <img id="b-plate" class="plate" src="assets/img/B-03-living-table.jpg" alt="" style="left:0;top:{L_TOP}px;width:{L_W:.1f}px;height:{L_H:.1f}px">
    </div>
    <div id="b-band" class="paper" data-paper></div>
    <div id="b-week" data-grid data-tx>{week}</div>
    {text("b-l1", "head", 495 if compact else 520, ["퇴근 후·주말에,", "100% 온라인으로."], "ink", swap=True)}
    {"" if compact else text("b-l2", "head", 470, l2, "ink", "wb", swap=True)}
    <div id="b-dip"></div>'''
    js = f"""
    const T = {J(T)};
    A(T.c0, "#b-pan", {{ translateX: [0, -49] }}, T.end - T.c0, INOUT2);
    SW(T.week, "#b-week .dl:nth-child(-n+5)", "#0e1116");
    tl.add("#b-week .dl.au .w", {{ color: ["#c9c3b6", "#b8955a"], duration: 120, delay: anime.stagger(85), ease: OUT }}, ms(T.week + 0.45));
    tl.add("#b-week .du", {{ scaleX: [0, 1], duration: 300, delay: anime.stagger(85), ease: EXPO }}, ms(T.week + 0.6));
    if (!{str(compact).lower()}) {{ WOUT(T.l2 - 0.22, "#b-l1"); WB(T.l2, "#b-l2"); }}
    DIP(T.end, "#b-dip");
"""
    return css, html, js


# ============================================================ USP — stairs (A-04) + paper card, then the flood
# The card is laid at the foot of the stairs (the first step); it carries the claim AND its footnote. On the
# downbeat the ground floods to Navy while the card holds (hero object stays), then the card lifts away as the
# end-card block lands in its place.
CARD_T = 640


def build_usp(T, compact=False):
    card_b = 1260 if compact else 1420
    ins0 = f"inset({CARD_T}px 120px {1920 - CARD_T}px 120px)"
    ins1 = f"inset({CARD_T}px 120px {1920 - card_b}px 120px)"
    css = f"""
    #u-push {{ position: absolute; inset: 0; transform-origin: 540px 560px; }}
    #u-card {{ position: absolute; inset: 0; clip-path: {ins0}; }}
    #u-navy {{ position: absolute; inset: 0; background: #0b1a33; clip-path: inset(100% 0px 0px 0px); }}
    #u-dock {{ background: #102245; clip-path: inset(100% 0px 0px 0px); }}
"""
    body = "" if compact else text("u-3", "body", CARD_T + 540, ["교육부장관 명의 · '법학 전공' 표기"], "ink", "sw", cls="later")
    fn_t = CARD_T + (540 if compact else 660)
    html = f'''    <div id="u-push" data-layout-allow-overflow>
      <img id="u-plate" class="plate" src="assets/img/A-04-stairs.jpg" alt="" style="left:0;top:0;width:1080px;height:1920px">
    </div>
    <div id="u-navy"></div>
    <div id="u-dock" class="dock" data-fill data-layout-ignore></div>
    <div id="u-card" data-layout-allow-overflow>
      <div class="paper field" data-paper></div>
      {text("u-1", "head", CARD_T + 52, ["!국내 !유일*"], "ink", "wb")}
      {text("u-2", "display", CARD_T + 178, ["100% 온라인", "법학사"], "ink", "rise")}
      {body}
      {text("u-fn", "small", fn_t, ["*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준"], "m-l", tx=True)}
    </div>'''
    js = f"""
    const T = {J(T)};
    A(T.c0, "#u-push", {{ scale: [1, 1.06] }}, T.flood - T.c0, INOUT2);
    // the paper card is laid down from its top edge (mask reveal)
    A(T.card, "#u-card", {{ clipPath: ["{ins0}", "{ins1}"] }}, 0.6, EXPO);
    WB(T.u1, "#u-1");
    RISE(T.u2, ["#u-2-0", "#u-2-1"]);
    if (!{str(compact).lower()}) {{ S(T.u3, "#u-3", {{ opacity: 1 }}); SW(T.u3, "#u-3", "#0e1116"); }}
    // colour flood: the card holds while the ground floods to Navy from the bottom; later the card lifts away
    A(T.flood, "#u-navy", {{ clipPath: ["inset(100% 0px 0px 0px)", "inset(0% 0px 0px 0px)"] }}, 0.4, INOUT2);
    A(T.flood, "#u-dock", {{ clipPath: ["inset(100% 0px 0px 0px)", "inset(0% 0px 0px 0px)"] }}, 0.4, INOUT2);
    A(T.lift, "#u-card", {{ clipPath: ["{ins1}", "{ins0}"] }}, 0.3, IN3);
"""
    return css, html, js


# ============================================================ END CARD — Navy (the only Navy in the film)
# lockup -> slogan (masked rise #2) -> "비어 있던 학력 칸, / 얼마나 남았을까?" (gold line) -> 1:1 line -> phone (muted)
# -> "아래 링크에서 내 경우 확인하기" + a thin gold arrow pointing at the platform's own link under the video.
# No button or pill shape: the video cannot be clicked.
def build_end(T, compact=False):
    lay = dict(lock=232, slo=364, q=636, one=896, tel=1040, act=1196, arr=1290) if not compact else \
        dict(lock=262, slo=400, q=690, tel=960, act=1110, arr=1206)
    slo_mode = "wb" if compact else "rise"
    css = """
    #e-ground { background: #0b1a33; opacity: 0; }
    #e-dock { background: #102245; opacity: 0; }
"""
    one = "" if compact else text("e-1", "body", lay["one"], ["지금 학력·학점으로 남은 과정,", "1:1로 짚어드려요"], "on-navy", "wb")
    ay = lay["arr"]
    arrow = (f'<svg class="sv" viewBox="0 0 1080 1920" data-layout-ignore data-gold>'
             f'<path id="e-arr" d="M540 {ay} L540 {ay + 120} M512 {ay + 92} L540 {ay + 120} L568 {ay + 92}" stroke="#b8955a" '
             f'stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none" style="opacity:0"/></svg>')
    html = f'''    <div id="e-ground" class="field" data-layout-ignore></div>
    <div id="e-dock" class="dock" data-fill data-layout-ignore></div>
    {lockup("e-lock", lay["lock"])}
    {text("e-slo", "head", lay["slo"], ["책임지는 자리로,", "지금 있는 자리에서."], "on-navy", slo_mode)}
    {text("e-q", "head", lay["q"], ["비어 있던 학력 칸,", "!얼마나 !남았을까?"], "on-navy", "wb")}
    {one}
    {text("e-tel", "body", lay["tel"], ["전화 문의 070-4006-7128 (평일 10–18시)"], "m-d", "wb", tx=True)}
    {text("e-act", "body", lay["act"], ["아래 링크에서 내 경우 확인하기"], "on-navy", "wb")}
    {arrow}'''
    js = f"""
    const T = {J(T)};
    S(T.ground, ["#e-ground", "#e-dock"], {{ opacity: 1 }});   // under the USP layer's own flood until the card has lifted
    A(T.lock, "#e-lock", {{ opacity: [0, 1], filter: ["blur(8px)", "blur(0px)"] }}, 0.2, OUT);
    if ({str(compact).lower()}) WB(T.slo, "#e-slo"); else RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    WB(T.q, "#e-q");
    if (!{str(compact).lower()}) WB(T.one, "#e-1");
    WB(T.tel, "#e-tel");
    WB(T.act, "#e-act");
    DRAW(T.c0, T.arr, "#e-arr", 0.5, EXPO);
"""
    return css, html, js


# ============================================================ LEGAL overlay: badge always on, disclaimers from the USP
def build_legal(t_total, disc, navy_at):
    css = """
    #root { pointer-events: none; }
"""
    html = f'''    <div id="l-tag" class="clip row t-small" style="color:#3c4043;top:147px" data-start="0" data-duration="{t_total:.3f}" data-track-index="1">가상 인물 · 연출</div>
    <div id="l-d" class="clip" data-start="{disc:.3f}" data-duration="{t_total - disc:.3f}" data-track-index="2">
      <div id="l-d1" class="row t-small m-d" style="top:1494px">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</div>
      <div id="l-d2" class="row t-small m-d" style="top:1530px">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</div>
    </div>'''
    js = f"""
    // on the Navy end card the compliance text is the light grey (>= 4.5:1 on Navy)
    A({navy_at}, "#l-tag", {{ color: ["#3c4043", "#9aa0a6"] }}, 0.3, INOUT2);
"""
    return css, html, js


# ============================================================ assemble
OVER = 0.7          # an outgoing scene keeps playing under the next one while the next one grows / floods over it
if VARIANT == "30":
    C = dict(resume=0, pen=D(4), sign=D(5), benefit=D(7), usp=D(9), end=D(11), fin=30.0)
    T_r = dict(push1=D(1), prints=[D(1), B(6), D(2)], caret=D(2), out=fr(B(10) - 0.22), c1=B(10), c2=fr(B(10) + 0.2), end=C["pen"])
    T_p = dict(c0=C["pen"], end=C["sign"])
    T_s = dict(c0=C["sign"], head=fr(C["sign"] + 0.2), hit=C["sign"], you=fr(C["sign"] + 1.25), end=C["benefit"])
    T_b = dict(c0=C["benefit"], week=fr(C["benefit"] + 0.6), l1=C["benefit"], l2=fr(C["benefit"] + 1.75), end=C["usp"])
    T_u = dict(c0=C["usp"], card=fr(C["usp"] + 0.1), u1=fr(C["usp"] + 0.35), u2=fr(C["usp"] + 0.35), u3=fr(C["usp"] + 0.85), flood=C["end"], lift=fr(C["end"] + 2.05))
    T_e = dict(c0=C["end"], ground=fr(T_u["lift"] + 0.3), lock=fr(C["end"] + 0.4), slo=fr(C["end"] + 0.4), q=fr(C["end"] + 2.35), one=fr(C["end"] + 2.45),
               tel=fr(C["end"] + 2.55), act=fr(C["end"] + 2.65), arr=fr(C["end"] + 2.8))
    SCENE_SPECS = [
        ("resume", C["resume"], C["pen"] + OVER, build_resume(T_r), 2),
        ("pen", C["pen"], C["sign"], build_pen(T_p), 3),
        ("sign", C["sign"], C["benefit"], build_sign(T_s), 3),
        ("benefit", C["benefit"], C["usp"], build_benefit(T_b), 3),
        ("usp", C["usp"], fr(T_u["lift"] + 0.35), build_usp(T_u), 4),
        ("end", C["end"], C["fin"], build_end(T_e), 5),
    ]
    CUTS = [(C["pen"], "S2 box -> world (pen insert)"), (C["sign"], "S3 hard cut on the pen touch: paper world, You stroke"),
            (C["benefit"], "S4 dip cut: living-room table"), (C["usp"], "S5 dip cut: stairs + USP card"), (C["end"], "S6 Navy flood: end card")]
    MOVES = [(0, "S1 push 1.00->1.06"), (T_r["push1"], "S1 pan -50px; entry 1 prints"), (T_r["c1"], "S1 caption swap"),
             (T_s["hit"], "S3 You stroke (pen sfx)"), (T_b["l2"], "S4 line 2"), (T_u["card"], "S5 card mask reveal"), (T_e["act"], "S6 CTA block (tap sfx)")]
else:
    C = dict(resume=0, sign=D(2), benefit=D(4), usp=D(5), end=D(6), fin=15.0)
    T_r = dict(push1=D(1), prints=[0, 0, 0], caret=0, out=fr(D(1) - 0.22), c1=D(1), c2=fr(D(1) + 0.2), end=C["sign"])
    T_s = dict(c0=C["sign"], head=fr(C["sign"] + 0.55), hit=B(10), you=fr(B(10) + 1.15), end=C["benefit"])
    T_b = dict(c0=C["benefit"], week=fr(C["benefit"] + 0.5), l1=fr(C["benefit"] + 0.1), l2=99, end=C["usp"])
    T_u = dict(c0=C["usp"], card=fr(C["usp"] + 0.05), u1=fr(C["usp"] + 0.25), u2=fr(C["usp"] + 0.35), u3=99, flood=C["end"], lift=fr(C["end"] + 0.2))
    T_e = dict(c0=C["end"], ground=fr(T_u["lift"] + 0.3), lock=fr(C["end"] + 0.35), slo=fr(C["end"] + 0.35), q=fr(C["end"] + 0.5),
               tel=fr(C["end"] + 0.55), act=fr(C["end"] + 0.6), arr=fr(C["end"] + 0.65))
    SCENE_SPECS = [
        ("resume", C["resume"], C["sign"] + OVER, build_resume(T_r, compact=True), 2),
        ("sign", C["sign"], C["benefit"], build_sign(T_s, grow=True), 3),
        ("benefit", C["benefit"], C["usp"], build_benefit(T_b, compact=True), 3),
        ("usp", C["usp"], fr(T_u["lift"] + 0.35), build_usp(T_u, compact=True), 4),
        ("end", C["end"], C["fin"], build_end(T_e, compact=True), 5),
    ]
    CUTS = [(C["sign"], "S3 box -> world: paper, You stroke"), (C["benefit"], "S4 dip cut: living-room table"),
            (C["usp"], "S5 dip cut: stairs + USP card"), (C["end"], "S6 Navy flood: end card")]
    MOVES = [(0, "S1 push"), (T_r["c1"], "S1 caption swap + pan"), (T_s["hit"], "S3 You stroke (pen sfx)"),
             (T_u["card"], "S5 card mask reveal"), (T_e["act"], "S6 CTA block (tap sfx)")]

SFX = [(T_s["hit"], "pen"), (T_e["act"], "tap")]

SLOTS = []
Z = {}
for cid, t0, t1, (css, html, js), z in SCENE_SPECS:
    SLOTS.append(scene(cid, t0, t1, css, html, js))
    Z[cid] = z
lc, lh, lj = build_legal(TOTAL, C["end"], fr(C["end"] + 0.15))
SLOTS.append(scene("legal", 0, TOTAL, lc, lh, lj))
Z["legal"] = 6


def beat_of(t):
    k = min(range(len(GRID)), key=lambda i: abs(GRID[i] - t))
    return k, round((t - GRID[k]) * FPS, 2)


json.dump({"variant": VARIANT, "offset": OFFSET, "bpm": BEATS["bpm"],
           "cuts": [{"t": round(t, 3), "frame": round(t * FPS), "label": l, "beat": beat_of(t)[0], "off_frames": beat_of(t)[1], "downbeat": is_down(t)} for t, l in CUTS],
           "moves": [{"t": round(t, 3), "label": l} for t, l in MOVES],
           "sfx": [{"t": round(t, 3), "kind": k} for t, k in SFX],
           "scenes": [{"id": s[0], "start": s[1], "duration": s[2]} for s in SLOTS]},
          open(os.path.join(ROOT, "beats", "cuts.json" if VARIANT == "30" else "cuts-15s.json"), "w"), indent=1)

# ---------------------------------------------------------------- index.html
hosts = []
for cid, start, dur in SLOTS:
    track = {"legal": 3}.get(cid, 1 if Z[cid] % 2 == 0 else 2)
    hosts.append(f'''      <div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: {Z[cid]}"></div>''')
audio = "assets/audio/mix-30s.mp3" if VARIANT == "30" else "assets/audio/mix-15s.mp3"
index = f'''<!doctype html>
<html
  lang="ko"
  data-resolution="portrait"
  data-composition-variables='[
  {{"id":"color-ink","type":"color","label":"Ink","default":"#0E1116"}},
  {{"id":"color-paper","type":"color","label":"Paper","default":"#F7F6F2"}},
  {{"id":"color-navy","type":"color","label":"Navy","default":"#0B1A33"}},
  {{"id":"color-accent","type":"color","label":"Gold","default":"#B8955A"}},
  {{"id":"font-display","type":"string","label":"Display font","default":"PretendardGOV"}}
]'
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <!-- anime.js v4.5.0 (MIT), local bundle: lib/anime.umd.min.js -->
    <script src="lib/anime.umd.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #f7f6f2; }}
    </style>
  </head>
  <body>
    <!-- 「마지막 서명」 편 B 재취업 {VARIANT}초 · v7 (paper, ink, daylight photographs) · anime.js v4 · cuts on the bar lines of the BGM. Generated by tools/build.py -->
    <div
      id="root"
      data-no-timeline
      data-motion-blur="on"
      data-composition-id="main"
      data-start="0"
      data-duration="{TOTAL:g}"
      data-width="1080"
      data-height="1920"
    >
{chr(10).join(hosts)}

      <!-- BGM excerpt ("News - News Music", NastelBom, Pixabay 629329) + 2 SFX, mixed by tools/make_audio.py. See MUSIC.md -->
      <audio id="bgm" class="clip" src="{audio}" data-start="0" data-duration="{TOTAL:g}" data-track-index="10" data-volume="1"></audio>
    </div>
  </body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)

live = {s[0] + ".html" for s in SLOTS}
for f in os.listdir(os.path.join(OUT, "compositions")):
    if f.endswith(".html") and f not in live:
        os.remove(os.path.join(OUT, "compositions", f))

if VARIANT == "15":
    for sub in ("fonts", "img", "audio"):
        os.makedirs(os.path.join(OUT, "assets", sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets/fonts/PretendardGOV-subset.woff2"), os.path.join(OUT, "assets/fonts/"))
    for f in os.listdir(os.path.join(OUT, "assets/img")):
        os.remove(os.path.join(OUT, "assets/img", f))
    for f in ("mark-gold.svg", "B-01-resume-desk.jpg", "B-02-paper.jpg", "B-03-living-table.jpg", "A-04-stairs.jpg"):
        shutil.copy(os.path.join(ROOT, "assets/img", f), os.path.join(OUT, "assets/img/"))
    src = os.path.join(ROOT, "assets/audio/mix-15s.mp3")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "assets/audio/"))
    os.makedirs(os.path.join(OUT, "lib"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "lib/anime.umd.min.js"), os.path.join(OUT, "lib/"))
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(OUT, "hyperframes.json"))

print(f"{VARIANT}s: offset {OFFSET}s, {len(SLOTS)} scenes ->", OUT)
print("   box inset", BOX_INSET, " sign rule y", SIG_RULE, " you top", SIG_YOU_T, " nib", NIB)
for c in SLOTS:
    print("  ", c)
for t, l in CUTS:
    k, d = beat_of(t)
    print(f"   cut {t:6.3f} f{round(t * FPS):<4d} B{k:<3d} {'downbeat' if is_down(t) else 'beat    '} {d:+.2f}fr  {l}")
