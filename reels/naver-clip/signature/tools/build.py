"""「마지막 서명」 — anime.js v4 scene generator, art direction v3 (30s at the project root, 15s in v15/).

Usage (from the project root):
  python3 tools/build.py              # compositions/*.html + index.html      (30s)
  python3 tools/build.py --variant 15 # v15/compositions/*.html + v15/index.html (15s)

Look: docs/ads/naver-clip/02-art-direction.md. One axis (x=540, every text row is a 840px centred
block between 120px margins), four sizes (112 / 72 / 40 / 26), flat Ink / Paper / Navy fields with
Gold only for the human side (caret, signature stroke, "첫 계단", "국내 유일*") and Red only for the
toast. Motion vocabulary: masked line rise (800ms expo-out, 90ms between lines, 4 steps max), UI
entrance (320ms, 16px), leave (300ms ease-in, 8px), one linear 1.00->1.03 push per shot, SVG line
drawing (1100ms in-out) and hard cuts. The signature stroke is the one loud moment.

Edit (client note): cuts sit on bar lines (downbeats of beats/source.json), 2-4 bars apart; nothing
inside a shot is placed on the beat. Exception: the 30s C2 cut stays on B7, the beat where the
music edit comes back after its 2.70s stop (MUSIC.md). Chapter changes that continue the same stage
(C3 toast, C5, C6 signature, USP, C7 S2, C8) are moves inside a shot, not cuts.

Engine: anime.js v4 only (lib/anime.umd.min.js). Every scene builds ONE paused timeline
(`autoplay: false`) and pushes it to window.__hfAnime. HyperFrames seeks every anime instance to
the ROOT time in ms, so all positions below are absolute video seconds. No randomness, no timers.
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

# ---------------------------------------------------------------- beat grid
BEATS = json.load(open(os.path.join(ROOT, "beats", "source.json")))
OFFSET = {"30": 8.789, "15": 15.796}[VARIANT]  # excerpt in-point in the source (a beat)
_i0 = min(range(len(BEATS["beats"])), key=lambda k: abs(BEATS["beats"][k] - OFFSET))
GRID = [round(b - BEATS["beats"][_i0], 3) for b in BEATS["beats"][_i0:]]
DOWN = [round(d - BEATS["beats"][_i0], 3) for d in BEATS["downbeats"] if d >= BEATS["beats"][_i0] - 0.01]


def B(k):
    """k-th beat of the excerpt (video seconds)."""
    k0 = int(k)
    return round(GRID[k0] + (k - k0) * (GRID[k0 + 1] - GRID[k0]), 3)


def is_down(t):
    return any(abs(t - d) < 0.02 for d in DOWN)


# ---------------------------------------------------------------- copy (01-last-signature.md)
DOCS = [
    dict(title="계약 검토의견서",
         body=["갑의 해지 통지는 요건을 갖추었습니다.", "을의 지체 책임은 일부 제한됩니다.", "위약금 조항은 감액될 여지가 있습니다."],
         last=["추가 자료 확인 후 보완을 권합니다.", "제5조의 해석은 갑에게 유리합니다.", "위약금 조항은 감액될 여지가 있습니다.",
               "을의 지체 책임은 일부 제한됩니다.", "갑의 해지 통지는 요건을 갖추었습니다."]),
    dict(title="소장 초안(가상)",
         body=["피고 을은 원고 갑에게 지급하라.", "소송비용은 피고 을이 부담한다."],
         last=["제1항은 가집행할 수 있다.", "피고 을은 계약금을 반환하라.", "원고 갑의 나머지 청구를 유지한다.",
               "소송비용은 피고 을이 부담한다.", "피고 을은 원고 갑에게 지급하라."]),
    dict(title="법률 검토 보고서",
         body=["현 단계에서 분쟁 위험은 낮습니다.", "합의 조건의 재검토를 권합니다."],
         last=["을과의 협상을 우선 권합니다.", "갑의 주장은 대체로 타당합니다.", "증빙 보완 시 승소 가능성이 높아집니다.",
               "합의 조건의 재검토를 권합니다.", "현 단계에서 분쟁 위험은 낮습니다."]),
]
WM = "[가상 문서 · 예시]"
SIG = "법률 검토·책임자 서명"
NEW = '그 칸으로 가는 <span class="au">첫 계단</span>'
BRAND = "경찰복지사이버평생교육원"
MARK = '<img class="mark" src="assets/img/mark.svg" alt="">'
CHECK = ('<svg class="ok" viewBox="0 0 24 24"><path d="M4.5 12.5l4.6 4.6L19.5 6.8" fill="none" stroke="currentColor" '
         'stroke-width="2.6" stroke-linecap="square"/></svg>')

# ---------------------------------------------------------------- html helpers


def text(id_, size, top, lines, tone, rise=False, cls="", style="", tx=False):
    """A centred text block: one masked line per entry (each line its own block, so each is centred).
    tx marks document / UI texture (not a caption to be read): the reading-rate audit skips it."""
    lis = "".join(f'<span class="ln"><span id="{id_}-{i}" class="li">{t}</span></span>' for i, t in enumerate(lines))
    return (f'<div id="{id_}" class="row t-{size} {tone}{" rise" if rise else ""}{" " + cls if cls else ""}"{" data-tx" if tx else ""} '
            f'style="top:{top}px;{style}">{lis}</div>')


def rule(id_, y, w, cls="", style=""):
    return f'<div id="{id_}" class="rule {cls}" style="left:{540 - w / 2:g}px;top:{y}px;width:{w}px;{style}"></div>'


def caret(id_, x, y, h=44, cls=""):
    return f'<div id="{id_}" class="caret {cls}" style="left:{x}px;top:{y}px;height:{h}px;opacity:0"></div>'


def sheet(id_, top, h, w=840, tone="var(--paper)"):
    return f'<div id="{id_}" class="sheet" style="left:{540 - w / 2:g}px;top:{top}px;width:{w}px;height:{h}px;background:{tone}"></div>'


def pill(id_, top, w, label, bg, fg, extra="", h=136, tx=False):
    return (f'<div id="{id_}" class="pill t-body"{" data-tx" if tx else ""} style="left:{540 - w / 2:g}px;top:{top}px;width:{w}px;height:{h}px;'
            f'background:{bg};color:{fg};{extra}">{label}</div>')


def ids(id_, n):
    return [f"#{id_}-{i}" for i in range(n)]


# ---------------------------------------------------------------- anime.js helpers (absolute seconds)
HELPERS = r"""
    const tl = anime.createTimeline({ autoplay: false });
    const ms = (s) => Math.round(s * 1000);
    const EXPO = anime.cubicBezier(0.16, 1, 0.3, 1);          // masked line rise (800 ms)
    const UI = anime.cubicBezier(0.22, 1, 0.36, 1);           // interface entrance (320 ms)
    const EXIT = anime.cubicBezier(0.55, 0.055, 0.675, 0.19); // leaving for good (300 ms)
    const INOUT = anime.cubicBezier(0.76, 0, 0.24, 1);        // line drawing, things that travel
    function A(t, sel, props, dur, ease) { tl.add(sel, Object.assign({ duration: Math.max(1, ms(dur)), ease: ease || UI }, props), ms(t)); }
    function S(t, sel, props) { tl.set(sel, props, ms(t)); }
    // lines rise from behind their own baseline; 90 ms apart, 4 steps at most
    function RISE(t, sels, dur) {
      sels.slice(0, 4).forEach((s, i) => { S(t + i * 0.09, s, { opacity: 1 }); A(t + i * 0.09, s, { translateY: ["110%", "0%"] }, dur || 0.8, EXPO); });
    }
    function LEAVE(t, sels, gap) {
      sels.forEach((s, i) => A(t + i * (gap == null ? 0.09 : gap), s, { opacity: [1, 0], translateY: [0, -8] }, 0.3, EXIT));
    }
    function ENTER(t, sel) { A(t, sel, { opacity: [0, 1], translateY: [16, 0] }, 0.32, UI); }
    // one linear push per shot, about the frame centre
    function PUSH(t0, t1, sel) { A(t0, sel, { scale: [1, 1.03] }, t1 - t0, "linear"); }
    // a text caret: standard 530 ms on / off, not tied to the music
    function CARET(sel, t0, t1) { let on = true; for (let t = t0; t < t1 - 1e-6; t += 0.53) { S(t, sel, { opacity: on ? 1 : 0 }); on = !on; } }
    // SVG stroke drawing (1100 ms in-out)
    function DRAW(t0, t, sel, dur) {
      const d = anime.svg.createDrawable(sel);
      S(t0, d, { draw: "0 0" });
      S(t, sel, { opacity: 1 });
      A(t, d, { draw: ["0 0", "0 1"] }, dur || 1.1, INOUT);
    }
"""


def scene(cid, t0, t1, css, html, js):
    s = f'''<template>
  <style>
{COMMON}
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


# ============================================================ shared fragments (v6 편 B · 재취업)
# The "You" signature: one continuous cursive stroke (capital Y, lowercase ou), drawn by hand as SVG
# cubic beziers in a 1080-wide sketch frame; placed by its bbox centre and scale, stroke always 4px.
YOU_PATH = ("M 296 214 C 300 176, 352 160, 362 200 C 370 240, 350 300, 380 328 C 410 352, 458 318, 476 262 "
            "C 484 236, 490 206, 498 176 C 494 262, 486 372, 458 432 C 444 462, 404 462, 410 430 "
            "C 418 386, 540 330, 610 300 C 630 290, 640 262, 616 258 C 590 254, 574 290, 584 320 "
            "C 592 344, 628 344, 640 318 C 648 300, 644 280, 634 272 C 650 276, 668 276, 670 292 "
            "C 672 316, 672 338, 692 340 C 716 342, 728 306, 732 278 C 730 310, 734 338, 758 340 "
            "C 800 342, 850 316, 886 266")
YOU_BOX = (296, 176, 886, 454)
YOU_BASE = 341                   # baseline of the 'o' and 'u' in the sketch frame
YOU_SCALE = 1.2
NAVY_FIELD = "#15284a"


def you_g(id_, scale, cx, cy, style="opacity:0"):
    """the signature path with its bbox centre on (cx, cy) at `scale`; the stroke stays 4px on screen"""
    bx, by = (YOU_BOX[0] + YOU_BOX[2]) / 2, (YOU_BOX[1] + YOU_BOX[3]) / 2
    return (f'<g transform="translate({cx - bx * scale:.2f} {cy - by * scale:.2f}) scale({scale})">'
            f'<path id="{id_}" d="{YOU_PATH}" stroke="#b8955a" stroke-width="{4 / scale:.3f}" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none" style="{style}"/></g>')


def you_rule_y(cy):
    """y of the writing line under the "ou" baseline for a signature centred on cy"""
    return round(cy - (YOU_BOX[1] + YOU_BOX[3]) / 2 * YOU_SCALE + YOU_BASE * YOU_SCALE + 10)


def lockup(id_, top, cls=""):
    """logo lockup: gold mark (62px high) + 18px gap + name (Body 44 / 600), one row centred on x=540"""
    return (f'<div id="{id_}" class="row lock{" " + cls if cls else ""}" style="top:{top}px">'
            f'<div class="lockrow" data-lockup><span class="lmark"></span><span>{BRAND}</span></div></div>')


def dock():
    """full-width footer field, y 1580-1920, one tone off the ground (declared to the measure with data-fill)"""
    return '<div class="dock" data-fill data-layout-ignore></div>'


# ============================================================ HOOK (0–3.5s) — Ink + résumé
# f0 is complete: "15년 경력. 이력서 첫 줄에서 멈췄습니다." over a résumé page whose education field is a big
# blank with a blinking caret (the page runs off the bottom of the frame).
def build_hook(T):
    css = """
    #h-ground { background: var(--ink); }
"""
    html = f'''    <div id="h-ground" class="field" data-layout-ignore></div>
    <div id="h-cam" class="cam" data-layout-allow-overflow>
      {sheet("h-sh", 640, 1400)}
      {text("h-c1", "display", 235, ["15년 경력."], "on-ink")}
      {text("h-c2", "head", 398, ["이력서 첫 줄에서", "멈췄습니다."], "on-ink")}
      {text("h-rt", "body", 664, ["이력서"], "m-l", tx=True)}
      {text("h-ed", "head", 742, ["학력"], "on-paper", tx=True)}
      {sheet("h-pn", 870, 330, 760, "var(--sheet-2)")}
      {rule("h-r", 1130, 640, "on-paper")}
      {caret("h-c", 200, 1040, 84, "on-paper")}
      {text("h-cr", "head", 1240, ["경력"], "on-paper", tx=True)}
      {text("h-cl", "body", 1352, [r[0] + " · " + r[1] for r in CAREER], "m-l", tx=True)}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#h-cam");
    CARET("#h-c", T.c0, T.end);
"""
    return css, html, js


# ============================================================ CARDS (3.5–10.5s) — Ink
# Career cards stack up and tick off one by one; the education slot at the foot stays blank.
CAREER = [("영업관리 팀장", "8년"), ("현장 운영 총괄", "5년"), ("고객 상담 리더", "2년")]


def build_cards(T):
    css = """
    #k-ground { background: var(--ink); }
    .tt { position: relative; }
    .ok { position: absolute; left: calc(100% + 20px); top: 50%; width: 56px; height: 56px; margin-top: -28px; color: var(--ink); opacity: 0; }
    .kc { opacity: 0; }
"""
    parts = []
    for i, (role, yrs) in enumerate(CAREER):
        y = 470 + i * 214
        parts.append(sheet(f"k-s{i}", y, 200, 840, "var(--paper)").replace('class="sheet"', 'class="sheet kc"'))
        parts.append(text(f"k-r{i}", "head", y + 12, [f'<span class="tt">{role}<span id="k-k{i}">{CHECK}</span></span>'], "on-paper", tx=True, cls="kc"))
        parts.append(text(f"k-y{i}", "body", y + 122, [yrs], "m-l", tx=True, cls="kc"))
    html = f'''    <div id="k-ground" class="field" data-layout-ignore></div>
    <div id="k-cam" class="cam" data-layout-allow-overflow>
      {text("k-cap", "head", 250, ["경력은 증명됐습니다.", "학력 칸만 남았어요."], "on-ink", rise=True)}
      {"".join(parts)}
      {sheet("k-sl", 1112, 536)}
      {text("k-lb", "head", 1140, ["학력"], "on-paper", tx=True)}
      {rule("k-rl", 1584, 720, "on-paper")}
      {caret("k-c", 180, 1500, 80, "on-paper")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#k-cam");
    CARET("#k-c", T.c0, T.end);
    RISE(T.cap1, ["#k-cap-0"]);
    [0, 1, 2].forEach((i) => A(T.stack + i * 0.07, ["#k-s" + i, "#k-r" + i, "#k-y" + i], {{ opacity: [0, 1], translateY: [16, 0] }}, 0.32, UI));
    T.oks.forEach((t, i) => A(t, "#k-k" + i + " .ok", {{ opacity: [0, 1] }}, 0.32, UI));
    RISE(T.cap2, ["#k-cap-1"]);
"""
    return css, html, js


# ============================================================ SIGN (10.5–15.75s) — Navy
# The blank signature field (840x950, Navy one tone lighter) waits with its caret and writing line while
# the music builds; on the biggest hit the gold monoline "You" is written INSIDE it (createDrawable,
# 4px, nothing crosses the edges) and "이 칸의 이름, 당신." rises under it.
FIELD_TOP, FIELD_H = 420, 950
SENT_T = 1398


def build_sign(T):
    fcy = FIELD_TOP + FIELD_H / 2
    rule_y = you_rule_y(fcy)
    css = f"""
    #s-ground {{ background: var(--navy); }}
    #s-field {{ position: absolute; left: 120px; top: {FIELD_TOP}px; width: 840px; height: {FIELD_H}px; background: {NAVY_FIELD}; }}
    .sv {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
"""
    html = f'''    <div id="s-ground" class="field" data-layout-ignore></div>
    {dock()}
    <div id="s-cam" class="cam" data-layout-allow-overflow>
      {text("s-lab", "body", 330, [SIG], "m-d", tx=True)}
      <div id="s-field"></div>
      {rule("s-r", rule_y, 720, "", "color:#43578a")}
      {caret("s-c", 180, rule_y - 84, 80, "au")}
      <svg class="sv" viewBox="0 0 1080 1920" data-layout-ignore>{you_g("s-ink", YOU_SCALE, 540, fcy)}</svg>
      {text("s-you2", "head", SENT_T, ['이 칸의 이름, <span class="au">당신.</span>'], "on-ink", rise=True)}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#s-cam");
    CARET("#s-c", T.c0, T.hit);
    S(T.hit, "#s-c", {{ opacity: 0 }});
    DRAW(T.c0, T.hit, "#s-ink", T.draw);
    RISE(T.you, ["#s-you2-0"]);
"""
    return css, html, js


# ============================================================ BENEFIT (15.75–22.75s) — Paper over Navy
# 퇴근 후·주말에, 100% 온라인으로. / 이미 딴 학점이 있으면 기간·비용을 줄일 수 있어요.
# Top (Paper): the first line over a week strip (weekday evenings dark, the weekend gold).
# Bottom (Navy): the second line over a block grid of credits (the earned ones turn gold on the hit).
# Never months, never a price. compact (15s) = the second line only, on a full Navy ground with a taller grid.
DAYS = ["월", "화", "수", "목", "금", "토", "일"]
SPLIT = 980


def credit_grid(top, rows, h, earned=3):
    bl = []
    for r in range(rows):
        for c in range(5):
            n = r * 5 + c
            x = 120 + c * (156 + 15)
            y = top + r * (h + 12)
            bl.append(f'<div id="g-{n}" class="gb" style="left:{x}px;top:{y}px;width:156px;height:{h}px;background:{NAVY_FIELD}"></div>')
    return "".join(bl)


def build_benefit(T, compact=False):
    if compact:
        rows, h, gtop, s2 = 5, 190, 650, 262
    else:
        rows, h, gtop, s2 = 2, 125, 1400, 1040
    css = f"""
    #g-ground {{ background: var(--navy); }}
    #g-paper {{ position: absolute; left: 0; top: 0; width: 1080px; height: {SPLIT}px; background: var(--paper); overflow: hidden; }}
    .gb {{ position: absolute; }}
    .dl {{ position: absolute; width: 108px; text-align: center; }}
    .bar {{ position: absolute; width: 108px; background: var(--sheet-3); overflow: hidden; }}
    .bar i {{ position: absolute; left: 0; bottom: 0; width: 100%; height: 110px; background: var(--navy); }}
    .bar.we {{ background: var(--gold); }}
"""
    week = ""
    for i, d in enumerate(DAYS):
        x = 120 + i * (108 + 14)
        we = i >= 5
        week += (f'<div class="dl t-body {"on-paper" if we else "m-l"}" data-tx style="left:{x}px;top:520px">{d}</div>'
                 f'<div class="bar{" we" if we else ""}" style="left:{x}px;top:590px;height:280px">{"" if we else "<i></i>"}</div>')
    paper = "" if compact else f'''
      <div id="g-paper" data-layout-allow-overflow>
        {text("g-s1", "head", 250, ["퇴근 후·주말에,", "100% 온라인으로."], "on-paper", rise=True)}
        <div id="g-week" data-grid>{week}</div>
      </div>'''
    html = f'''    <div id="g-ground" class="field" data-layout-ignore></div>
    <div id="g-cam" class="cam" data-layout-allow-overflow>
      {paper}
      {text("g-s2", "head", s2, ["이미 딴 학점이 있으면", "기간·비용을", "줄일 수 있어요."], "on-ink", rise=True)}
      <div id="g-grid">{credit_grid(gtop, rows, h)}</div>
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#g-cam");
    if (!{str(compact).lower()}) {{
      RISE(T.s1, ["#g-s1-0", "#g-s1-1"]);
      ENTER(T.week, "#g-week");
    }}
    RISE(T.s2, ["#g-s2-0", "#g-s2-1", "#g-s2-2"]);
    ENTER(T.grid, "#g-grid");
    // the credits already earned turn gold, one after another
    A(T.gold, ["#g-0", "#g-1", "#g-2"], {{ backgroundColor: ["{NAVY_FIELD}", "#b8955a"] }}, 0.5, UI, {{ delay: anime.stagger(90) }});
"""
    return css, html, js


# ============================================================ USP (22.75–27.15s) — Navy
# The signature field again (cropped to 420 high, "You" inside) over the first step and the USP block.
def build_usp(T):
    top, fh = 215, 420
    fcy = top + fh / 2
    rule_y = you_rule_y(fcy)
    css = f"""
    #u-ground {{ background: var(--navy); }}
    #u-field {{ position: absolute; left: 120px; top: {top}px; width: 840px; height: {fh}px; background: {NAVY_FIELD}; }}
    .sv {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
"""
    html = f'''    <div id="u-ground" class="field" data-layout-ignore></div>
    {dock()}
    <div id="u-cam" class="cam" data-layout-allow-overflow>
      <div id="u-field"></div>
      {rule("u-r", rule_y, 720, "", "color:#43578a")}
      <svg class="sv" viewBox="0 0 1080 1920" data-layout-ignore>{you_g("u-ink", YOU_SCALE, 540, fcy, style="opacity:1")}</svg>
      {text("u-nl", "body", 695, [NEW], "on-ink", rise=True)}
      {text("u-u1", "body", 818, ["국내 유일*"], "au", rise=True)}
      {text("u-u2", "display", 886, ["100% 온라인", "법학사"], "on-ink", rise=True)}
      {text("u-u3", "small", 1204, ["교육부장관 명의 · '법학 전공' 표기"], "m-d", rise=True)}
      {lockup("u-lock", 1330, "later")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#u-cam");
    RISE(T.step, ["#u-nl-0"]);
    RISE(T.usp, ["#u-u1-0", "#u-u2-0", "#u-u2-1", "#u-u3-0"]);
    ENTER(T.lock, "#u-lock");
"""
    return css, html, js


# ============================================================ END (27.15–30s / 12.25–15s) — Navy
# lockup -> slogan (Head 88, gold underline) -> the USP block (already read) -> ONE primary CTA (gold button,
# two lines) -> phone as a small secondary line. The lockup, USP block and button are on the frame from the cut;
# the slogan rises, the phone settles, the underline draws.
CTA = ["내 학점으로 남은 기간,", "무료로 진단받기"]


def build_end(T):
    css = """
    #e-ground { background: var(--navy); }
    .sv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
"""
    ul_y = 664
    underline = f"M120 {ul_y} C 360 {ul_y + 3}, 640 {ul_y - 1}, 840 {ul_y - 7} S 945 {ul_y - 13}, 960 {ul_y - 15}"
    html = f'''    <div id="e-ground" class="field" data-layout-ignore></div>
    {dock()}
    <div id="e-cam" class="cam" data-layout-allow-overflow>
      {lockup("e-lock", 282)}
      {text("e-slo", "head", 447, ["책임지는 자리로,", "지금 있는 자리에서."], "on-ink", rise=True)}
      <svg class="sv" viewBox="0 0 1080 1920" data-layout-ignore><path id="e-ul" d="{underline}" stroke="#b8955a" stroke-width="5" stroke-linecap="round" fill="none" style="opacity:0"/></svg>
      <div id="e-info">
        {text("e-ug", "body", 775, ["국내 유일*"], "au")}
        {text("e-uh", "head", 837, ["100% 온라인 법학사"], "on-ink")}
        {text("e-u3", "small", 945, ["교육부장관 명의 · '법학 전공' 표기"], "m-d")}
      </div>
      {pill("e-btn", 1066, 840, "<br>".join(CTA), "var(--gold)", "var(--navy)", tx=True, h=170)}
      <div id="e-tel" class="later" data-tx>
        {text("e-tn", "body", 1352, ["070-4006-7128 (평일 10–18시)"], "m-d")}
      </div>
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#e-cam");
    RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    DRAW(T.c0, T.ul, "#e-ul", 1.1);
    ENTER(T.tel, "#e-tel");
"""
    return css, html, js


# ============================================================ LEGAL overlay (가상 인물 · 연출 badge + 고지 L1·L2), fixed positions
def build_legal(t0, t1, tag, disc, tag_text="가상 인물 · 연출", on_paper=None):
    """tag=(start,end) abs, always on; disclaimers from `disc` to the end (Small 26, y 1494 / 1530, above the footer field)."""
    css = """
    #root { pointer-events: none; }
"""
    html = f'''    <div id="l-tag" class="clip row t-small m-d" data-start="{tag[0] - t0:.3f}" data-duration="{tag[1] - tag[0]:.3f}" data-track-index="1" style="top:142px">{tag_text}</div>
    <div id="l-d" class="clip" data-start="{disc - t0:.3f}" data-duration="{t1 - disc:.3f}" data-track-index="2">
      <div id="l-d1" class="row t-small m-d" style="top:1494px">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</div>
      <div id="l-d2" class="row t-small m-d" style="top:1530px">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</div>
    </div>'''
    js = "" if not on_paper else f"""
    // the badge sits on the Paper half during the benefit scene: darker grey there (>= 3:1)
    S({on_paper[0]}, "#l-tag", {{ color: "#5f6368" }});
    S({on_paper[1]}, "#l-tag", {{ color: "#9aa0a6" }});
"""
    return css, html, js


# ============================================================ assemble
if VARIANT == "30":
    # cuts: B8 / B24 / B36 / B52 are downbeats of the excerpt (offset 8.789 = a source downbeat), B62 the beat
    # nearest the spec's 27 s. The biggest hit of the track (source 21.037) lands on B28 = the "You" stroke.
    C = dict(hook=0, cards=B(8), sign=B(24), benefit=B(36), usp=B(52), end=B(62), fin=30.0)
    T_h = dict(c0=C["hook"], end=C["cards"])
    T_k = dict(c0=C["cards"], cap1=C["cards"] + 0.12, stack=C["cards"] + 0.30, oks=[B(11), B(13), B(15)], cap2=B(16) + 0.05, end=C["sign"])
    T_s = dict(c0=C["sign"], hit=B(28), draw=1.1, you=B(28) + 1.2, end=C["benefit"])
    T_g = dict(c0=C["benefit"], s1=C["benefit"] + 0.08, s2=C["benefit"] + 0.20, week=C["benefit"] + 0.30, grid=C["benefit"] + 0.38,
               gold=B(44), end=C["usp"])
    T_u = dict(c0=C["usp"], step=C["usp"] + 0.04, usp=C["usp"] + 0.12, lock=C["usp"] + 0.45, end=C["end"])
    T_e = dict(c0=C["end"], slo=C["end"] + 0.05, tel=C["end"] + 0.25, ul=C["end"] + 0.60, end=C["fin"])
    SCENE_SPECS = [
        ("hook", C["hook"], C["cards"], build_hook(T_h)),
        ("cards", C["cards"], C["sign"], build_cards(T_k)),
        ("sign", C["sign"], C["benefit"], build_sign(T_s)),
        ("benefit", C["benefit"], C["usp"], build_benefit(T_g)),
        ("usp", C["usp"], C["end"], build_usp(T_u)),
        ("end", C["end"], C["fin"], build_end(T_e)),
    ]
    DISC = C["usp"]          # L1·L2 with the USP
    CUTS = [(C["cards"], "S2 cards"), (C["sign"], "S3 signature field"), (C["benefit"], "S4 benefit"), (C["usp"], "S5 USP"), (C["end"], "S6 end card")]
    MOVES = [(T_k["stack"], "S2 career cards"), (T_k["cap2"], "S2 caption 2 + build"), (T_s["hit"], "S3 signature stroke (biggest hit)"),
             (T_s["you"], "S3 sentence"), (T_g["gold"], "S4 earned credits turn gold (2nd hit)"), (T_u["step"], "S5 stack"), (T_e["tel"], "S6 phone")]
else:
    # 15s: hook -> You signature -> one benefit line -> CTA. Offset 15.796 (a source downbeat): the drumless build
    # runs under the hook, the biggest hit is B12 (the stroke), the second hit B28 is the CTA cut.
    C = dict(hook=0, sign=B(8), benefit=B(20), end=B(28), fin=15.0)
    T_h = dict(c0=C["hook"], end=C["sign"])
    T_s = dict(c0=C["sign"], hit=B(12), draw=1.1, you=B(12) + 1.1, end=C["benefit"])
    T_g = dict(c0=C["benefit"], s2=C["benefit"] + 0.10, grid=C["benefit"] + 0.25, gold=C["benefit"] + 1.30, end=C["end"])
    T_e = dict(c0=C["end"], slo=C["end"] + 0.05, tel=C["end"] + 0.25, ul=C["end"] + 0.60, end=C["fin"])
    SCENE_SPECS = [
        ("hook", C["hook"], C["sign"], build_hook(T_h)),
        ("sign", C["sign"], C["benefit"], build_sign(T_s)),
        ("benefit", C["benefit"], C["end"], build_benefit(T_g, compact=True)),
        ("end", C["end"], C["fin"], build_end(T_e)),
    ]
    DISC = C["end"]          # L1·L2 with the USP block of the end card
    CUTS = [(C["sign"], "S3 signature field"), (C["benefit"], "S4 benefit line"), (C["end"], "S6 end card")]
    MOVES = [(T_s["hit"], "S3 signature stroke (biggest hit)"), (T_s["you"], "S3 sentence"), (T_g["gold"], "S4 earned credits turn gold"),
             (T_e["tel"], "S6 phone")]

# sound: exactly two quiet tones — the pen touch on the biggest hit, a soft tap when the CTA lands. No clicks, whips or swipes.
SFX = [(T_s["hit"], "pen"), (T_e["c0"], "tap")]

SLOTS = []
for cid, t0, t1, (css, html, js) in SCENE_SPECS:
    SLOTS.append(scene(cid, t0, t1, css, html, js))
lc, lh, lj = build_legal(0, TOTAL, (0, TOTAL), DISC, on_paper=(C["benefit"], C["usp"]) if VARIANT == "30" else None)
SLOTS.append(scene("legal", 0, TOTAL, lc, lh, lj))


def beat_of(t):
    k = min(range(len(GRID)), key=lambda i: abs(GRID[i] - t))
    return k, round((t - GRID[k]) * 30, 2)


json.dump({"variant": VARIANT, "offset": OFFSET, "bpm": BEATS["bpm"],
           "cuts": [{"t": round(t, 3), "frame": round(t * 30), "label": l, "beat": beat_of(t)[0], "downbeat": is_down(t)} for t, l in CUTS],
           "moves": [{"t": round(t, 3), "label": l} for t, l in MOVES],
           "sfx": [{"t": round(t, 3), "kind": k} for t, k in SFX],
           "scenes": [{"id": s[0], "start": s[1], "duration": s[2]} for s in SLOTS]},
          open(os.path.join(ROOT, "beats", "cuts.json" if VARIANT == "30" else "cuts-15s.json"), "w"), indent=1)

# ---------------------------------------------------------------- index.html
hosts = []
for cid, start, dur in SLOTS:
    z = {"legal": 6}.get(cid, 2)
    track = {"legal": 3}.get(cid, 1)
    hosts.append(f'''      <div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: {z}"></div>''')
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0e1116; }}
    </style>
  </head>
  <body>
    <!-- 「마지막 서명」 {VARIANT}초 · anime.js v4 · art direction v3 · cuts on the bar lines of the BGM (beats/source.json). Generated by tools/build.py -->
    <div
      id="root"
      data-no-timeline
      data-composition-id="main"
      data-start="0"
      data-duration="{TOTAL:g}"
      data-width="1080"
      data-height="1920"
    >
{chr(10).join(hosts)}

      <!-- BGM excerpt ("Breaking News Intro", kornevmusic, Pixabay 527939) + SFX, mixed by tools/make_audio.py. See MUSIC.md -->
      <audio id="bgm" class="clip" src="{audio}" data-start="0" data-duration="{TOTAL:g}" data-track-index="10" data-volume="1"></audio>
    </div>
  </body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)

# stale scene files from the v2 cut (whip / dust / desk / fx) are removed so `check` only sees this cut
live = {s[0] + ".html" for s in SLOTS}
for f in os.listdir(os.path.join(OUT, "compositions")):
    if f.endswith(".html") and f not in live:
        os.remove(os.path.join(OUT, "compositions", f))

if VARIANT == "15":
    for sub in ("fonts", "img", "audio"):
        os.makedirs(os.path.join(OUT, "assets", sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets/fonts/PretendardGOV-subset.woff2"), os.path.join(OUT, "assets/fonts/"))
    shutil.copy(os.path.join(ROOT, "assets/img/mark.svg"), os.path.join(OUT, "assets/img/"))
    src = os.path.join(ROOT, "assets/audio/mix-15s.mp3")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "assets/audio/"))
    os.makedirs(os.path.join(OUT, "lib"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "lib/anime.umd.min.js"), os.path.join(OUT, "lib/"))
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(OUT, "hyperframes.json"))

print(f"{VARIANT}s: offset {OFFSET}s, {len(SLOTS)} scenes ->", OUT)
for c in SLOTS:
    print("  ", c)
for t, l in CUTS:
    k, d = beat_of(t)
    print(f"   cut {t:6.3f}  B{k:<3d} {'downbeat' if is_down(t) else 'beat    '} {d:+.2f}fr  {l}")
