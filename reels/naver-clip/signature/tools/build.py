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
OFFSET = {"30": 1.776, "15": 10.971}[VARIANT]  # excerpt in-point in the source (a beat)
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


def text(id_, size, top, lines, tone, rise=False, cls="", style=""):
    """A centred text block: one masked line per entry (each line its own block, so each is centred)."""
    lis = "".join(f'<span class="ln"><span id="{id_}-{i}" class="li">{t}</span></span>' for i, t in enumerate(lines))
    return (f'<div id="{id_}" class="row t-{size} {tone}{" rise" if rise else ""}{" " + cls if cls else ""}" '
            f'style="top:{top}px;{style}">{lis}</div>')


def rule(id_, y, w, cls="", style=""):
    return f'<div id="{id_}" class="rule {cls}" style="left:{540 - w / 2:g}px;top:{y}px;width:{w}px;{style}"></div>'


def caret(id_, x, y, h=44, cls=""):
    return f'<div id="{id_}" class="caret {cls}" style="left:{x}px;top:{y}px;height:{h}px;opacity:0"></div>'


def sheet(id_, top, h, w=840, tone="var(--paper)"):
    return f'<div id="{id_}" class="sheet" style="left:{540 - w / 2:g}px;top:{top}px;width:{w}px;height:{h}px;background:{tone}"></div>'


def pill(id_, top, w, label, bg, fg, extra=""):
    return (f'<div id="{id_}" class="pill t-body" style="left:{540 - w / 2:g}px;top:{top}px;width:{w}px;height:110px;'
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


# ============================================================ HOOK (C1 S1 / C1' S1) — Ink
# f0 is complete: headline, status, a deck of three sheets filling the lower half (the front sheet
# runs off the bottom of the frame; the back two show their title + watermark strip).
def build_hook(T):
    d0, d1, d2 = DOCS
    css = """
    #h-ground { background: var(--ink); }
"""
    html = f'''    <div id="h-ground" class="field" data-layout-ignore></div>
    <div id="h-cam" class="cam" data-layout-allow-overflow>
      {sheet("h-s2", 720, 1300, 760, "var(--sheet-3)")}
      {sheet("h-s1", 890, 1200, 800, "var(--sheet-2)")}
      {sheet("h-s0", 1060, 1000)}
      {text("h-head", "display", 270, ["AI가", "다 써줍니다."], "on-ink")}
      {text("h-stat", "body", 610, ['법률 검토 문서 3건 작성 · <span class="on-ink">생성 완료 0.1s</span>'], "m-d")}
      {text("h-t2", "head", 734, [d2["title"]], "on-paper")}
      {text("h-w2", "small", 838, [WM], "m-l")}
      {text("h-t1", "head", 904, [d1["title"]], "on-paper")}
      {text("h-w1", "small", 1008, [WM], "m-l")}
      {text("h-t0", "head", 1074, [d0["title"]], "on-paper")}
      {text("h-w0", "small", 1178, [WM], "m-l")}
      {text("h-b0", "body", 1240, d0["body"], "on-paper")}
      {text("h-sg", "body", 1468, [SIG], "m-l")}
      {rule("h-r0", 1580, 420, "m-l")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#h-cam");
"""
    return css, html, js


# ============================================================ TEASE (C1 S2 / C1' S2 + C3') — Paper
# Cut to the page itself: the last lines of the document and the one blank line, full measure,
# caret waiting. 15s continues into C3': '생성' pressed three times (the lines above change, the
# blank stays), then the toast.
def build_tease(T, presses=False):
    d0 = DOCS[0]
    y0 = 300 if presses else 470  # the content group is centred in y 260–1440
    pairs = [(d0["last"][1], d0["last"][0]), (d0["last"][2], d0["last"][3]), (d0["last"][4], d0["body"][1]), (d0["body"][0], d0["last"][1])]
    css = """
    #t-ground { background: var(--paper); }
"""
    lines = ""
    for v, (a, b) in enumerate(pairs if presses else pairs[:1]):
        lines += text(f"t-l{v}", "body", y0 + 466, [a, b], "on-paper", rise=v > 0)
    extra = ""
    if presses:
        extra = (pill("t-btn", y0 + 890, 360, "생성", "var(--ink)", "var(--paper)", "opacity:0") +
                 pill("t-toast", y0 + 890, 840, "이 항목은 생성할 수 없습니다.", "var(--red)", "var(--paper)", "opacity:0"))
    html = f'''    <div id="t-ground" class="field" data-layout-ignore></div>
    <div id="t-cam" class="cam" data-layout-allow-overflow>
      {text("t-cap", "display", y0, ["딱 한 칸만", "빼고."], "on-paper", rise=True)}
      {text("t-wm", "small", y0 + 410, [WM], "m-l")}
      {lines}
      {text("t-sg", "head", y0 + 640, [SIG], "on-paper")}
      {rule("t-r", y0 + 830, 840, "on-paper")}
      {caret("t-c", 120, y0 + 752, 70, "on-paper")}
      {extra}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#t-cam");
    RISE(T.cap, ["#t-cap-0", "#t-cap-1"]);
    CARET("#t-c", T.c0, T.end);
    if (T.btn != null) {{
      ENTER(T.btn, "#t-btn");
      T.presses.forEach((t, k) => {{
        S(t, "#t-btn", {{ backgroundColor: "#b8955a", color: "#0e1116" }});
        S(t + 0.14, "#t-btn", {{ backgroundColor: "#0e1116", color: "#f7f6f2" }});
        S(t, ["#t-l" + k + "-0", "#t-l" + k + "-1"], {{ opacity: 0 }});
        RISE(t, ["#t-l" + (k + 1) + "-0", "#t-l" + (k + 1) + "-1"], 0.32);
      }});
      LEAVE(T.toast, ["#t-btn"]);
      ENTER(T.toast + 0.3, "#t-toast");  // the button is gone before the toast arrives
    }}
"""
    return css, html, js


# ============================================================ FILL (C2) — Ink
# Three full-measure sheets fill the frame; each one's body sets line by line (44px), then its check
# appears. The signature line at the foot of each sheet stays empty.
def build_fill(T):
    css = """
    #f-ground { background: var(--ink); }
    .tt { position: relative; }
    .ok { position: absolute; left: calc(100% + 18px); top: 50%; width: 44px; height: 44px; margin-top: -22px; color: var(--ink); opacity: 0; }
"""
    parts = []
    for i, d in enumerate(DOCS):
        y = 244 + i * 410
        parts.append(sheet(f"f-s{i}", y, 392))
        parts.append(text(f"f-t{i}", "head", y + 20, [f'<span class="tt">{d["title"]}<span id="f-k{i}">{CHECK}</span></span>'], "on-paper"))
        parts.append(text(f"f-w{i}", "small", y + 122, [WM], "m-l"))
        parts.append(text(f"f-b{i}", "body", y + 172, d["body"][:2], "on-paper", rise=True))
        parts.append(text(f"f-g{i}", "small", y + 312, [SIG], "m-l"))
        parts.append(rule(f"f-r{i}", y + 362, 300, "m-l"))
    html = f'''    <div id="f-ground" class="field" data-layout-ignore></div>
    <div id="f-cam" class="cam" data-layout-allow-overflow>
      {"".join(parts)}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#f-cam");
    T.fills.forEach((t, i) => RISE(t, ["#f-b" + i + "-0", "#f-b" + i + "-1"]));
    T.oks.forEach((t, i) => A(t, "#f-k" + i + " .ok", {{ opacity: [0, 1] }}, 0.32, UI));
"""
    return css, html, js


# ============================================================ BLANK (C3) — Ink
# Payoff of the teaser: three big signature fields, '생성' pressed four times — the sentence above each
# field changes every time, the fields stay empty — then the toast (the only red in the film).
def build_blank(T):
    css = """
    #b-ground { background: var(--ink); }
"""
    parts = []
    nvar = len(T["presses"]) + 1
    for i, d in enumerate(DOCS):
        y = 591 + i * 240
        parts.append(sheet(f"b-s{i}", y, 226))
        for v in range(nvar):
            parts.append(text(f"b-l{i}v{v}", "small", y + 16, [d["last"][v]], "m-l", rise=v > 0))
        parts.append(text(f"b-g{i}", "head", y + 50, [SIG], "on-paper"))
        parts.append(rule(f"b-r{i}", y + 202, 600, "on-paper"))
        parts.append(caret(f"b-c{i}", 240, y + 156, 44, "on-paper"))
    html = f'''    <div id="b-ground" class="field" data-layout-ignore></div>
    <div id="b-cam" class="cam" data-layout-allow-overflow>
      {text("b-cap", "display", 253, ["딱 한 칸만", "빼고."], "on-ink", rise=True)}
      {"".join(parts)}
      {pill("b-btn", 1327, 360, "생성", "var(--paper)", "var(--ink)", "opacity:0")}
      {pill("b-toast", 1327, 840, "이 항목은 생성할 수 없습니다.", "var(--red)", "var(--paper)", "opacity:0")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#b-cam");
    RISE(T.cap, ["#b-cap-0", "#b-cap-1"]);
    [0, 1, 2].forEach((i) => CARET("#b-c" + i, T.c0, T.end));
    ENTER(T.btn, "#b-btn");
    T.presses.forEach((t, k) => {{
      S(t, "#b-btn", {{ backgroundColor: "#b8955a" }});
      S(t + 0.14, "#b-btn", {{ backgroundColor: "#f7f6f2" }});
      [0, 1, 2].forEach((i) => {{
        S(t, "#b-l" + i + "v" + k + "-0", {{ opacity: 0 }});
        S(t, "#b-l" + i + "v" + (k + 1) + "-0", {{ opacity: 1 }});
        A(t, "#b-l" + i + "v" + (k + 1) + "-0", {{ translateY: ["110%", "0%"] }}, 0.32, EXPO);
      }});
    }});
    LEAVE(T.toast, ["#b-btn"]);
    ENTER(T.toast + 0.3, "#b-toast");  // the button is gone before the toast arrives
"""
    return css, html, js


# ============================================================ QUIET (C4 [+ C5] / C4' + bridge) — Ink
# The thoughts sit over a large blank signature field (one tone step up from Ink: line, caret, and
# the caption beneath like a signature block), so the frame reads top to bottom. 30s C5 (a move on the bar line, no cut): the thoughts and the field leave, its blank
# line draws out to the full width of the frame ("그 자리"), the next lines take the same slots.
# 15s: the bridge line takes the slots, then the caret turns gold (someone is about to sign).
def build_quiet(T, c1, c2, c3=None, c4=None, bridge=None):
    css = """
    #q-ground { background: var(--ink); }
    #q-panel { position: absolute; left: 120px; top: 1000px; width: 840px; height: 380px; background: var(--panel); }
"""
    slots = (text("q-c1", "head", 470, [c1], "on-ink", rise=True) +
             text("q-c2", "display", 607, list(c2), "on-ink", rise=True))
    if c3:
        slots += (text("q-c3", "head", 470, [c3], "m-d", rise=True) +
                  text("q-c4", "head", 607, list(c4), "on-ink", rise=True))
    if bridge:
        slots += text("q-br", "head", 607, list(bridge), "on-ink", rise=True)
    html = f'''    <div id="q-ground" class="field" data-layout-ignore></div>
    <div id="q-cam" class="cam" data-layout-allow-overflow>
      <div id="q-panel"></div>
      {slots}
      {text("q-sg", "body", 1282, [SIG], "m-d")}
      {rule("q-r", 1260, 720, "on-ink")}
      {caret("q-c", 180, 1180, 72, "on-ink")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#q-cam");
    RISE(T.c1, ["#q-c1-0"]);
    RISE(T.c2, ["#q-c2-0", "#q-c2-1"]);
    CARET("#q-c", T.c0, T.c5 != null ? T.c5 : T.end);
    if (T.c5 != null) {{
      LEAVE(T.c5, ["#q-c1-0", "#q-c2-0", "#q-c2-1", "#q-sg-0"], 0.05);
      S(T.c5, "#q-c", {{ opacity: 0 }});
      A(T.ext, "#q-panel", {{ opacity: [1, 0] }}, 0.6, INOUT);
      A(T.ext, "#q-r", {{ scaleX: [1, 1.5] }}, 1.1, INOUT);
      RISE(T.c3, ["#q-c3-0"]);
      RISE(T.c4, ["#q-c4-0", "#q-c4-1"]);
    }}
    if (T.br != null) {{
      LEAVE(T.br, ["#q-c1-0", "#q-c2-0", "#q-c2-1"], 0.05);
      RISE(T.brIn, ["#q-br-0", "#q-br-1"]);
      S(T.gold, "#q-c", {{ backgroundColor: "#b8955a" }});
    }}
"""
    return css, html, js


# ============================================================ SIGN (C6 / C6') — Navy (brand field)
# Client round 4 ("첫 계단을 YOU로"): one big blank signature field in the middle of the frame (Navy one
# tone lighter, 840x400) under its Small label. On the music's biggest hit a gold monoline hand
# signature "You" (one continuous stroke, capital Y) is written INSIDE the field (createDrawable,
# 1.1 s in-out; nothing crosses the field's edges); "이 칸의 이름, 당신." rises under it. On the next
# downbeat the field and the sentence glide up (450 ms in-out) and the step / USP / brand rise below.
YOU_PATH = ("M 296 214 C 300 176, 352 160, 362 200 C 370 240, 350 300, 380 328 C 410 352, 458 318, 476 262 "
            "C 484 236, 490 206, 498 176 C 494 262, 486 372, 458 432 C 444 462, 404 462, 410 430 "
            "C 418 386, 540 330, 610 300 C 630 290, 640 262, 616 258 C 590 254, 574 290, 584 320 "
            "C 592 344, 628 344, 640 318 C 648 300, 644 280, 634 272 C 650 276, 668 276, 670 292 "
            "C 672 316, 672 338, 692 340 C 716 342, 728 306, 732 278 C 730 310, 734 338, 758 340 "
            "C 800 342, 850 316, 886 266")
YOU_BOX = (296, 176, 886, 454)   # path bbox (drawn in a 1080-wide sketch frame)
YOU_SCALE = 1.15
FIELD_TOP, FIELD_H = 735, 400    # before the glide; the field's centre sits near the frame centre
GLIDE = -481                     # label 687 -> 206


def build_sign(T, compact=False):
    fcx, fcy = 540, FIELD_TOP + FIELD_H / 2
    bx, by = (YOU_BOX[0] + YOU_BOX[2]) / 2, (YOU_BOX[1] + YOU_BOX[3]) / 2
    tx, ty = fcx - bx * YOU_SCALE, fcy - by * YOU_SCALE
    css = f"""
    #s-ground {{ background: var(--navy); }}
    #s-field {{ position: absolute; left: 120px; top: {FIELD_TOP}px; width: 840px; height: {FIELD_H}px; background: #15284a; }}
    #s-svg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
"""
    u3 = "교육부장관 명의" if compact else "교육부장관 명의 · '법학 전공' 표기"
    y_step = FIELD_TOP + GLIDE + FIELD_H + 18 + 101 + 33     # under the glided sentence
    html = f'''    <div id="s-ground" class="field" data-layout-ignore></div>
    <div id="s-cam" class="cam" data-layout-allow-overflow>
      <div id="s-you">
        {text("s-lab", "small", FIELD_TOP - 48, [SIG], "m-d")}
        <div id="s-field"></div>
        <svg id="s-svg" viewBox="0 0 1080 1920" data-layout-ignore>
          <g transform="translate({tx:.2f} {ty:.2f}) scale({YOU_SCALE})">
            <path id="s-ink" d="{YOU_PATH}" stroke="#b8955a" stroke-width="{4 / YOU_SCALE:.2f}" stroke-linecap="round" stroke-linejoin="round" fill="none" style="opacity:0"/>
          </g>
        </svg>
        {text("s-you2", "head", FIELD_TOP + FIELD_H + 18, ['이 칸의 이름, <span class="au">당신.</span>'], "on-ink", rise=True)}
      </div>
      {text("s-nl", "body", y_step, [NEW], "on-ink", rise=True)}
      {text("s-u1", "body", y_step + 86, ["국내 유일*"], "au", rise=True)}
      {text("s-u2", "display", y_step + 156, ["100% 온라인", "법학사"], "on-ink", rise=True)}
      {text("s-u3", "small", y_step + 486, [u3], "m-d", rise=True)}
      {text("s-bn", "body", y_step + 548, [BRAND], "on-ink", cls="later")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#s-cam");
    DRAW(T.c0, T.hit, "#s-ink", T.draw);
    RISE(T.you, ["#s-you2-0"]);
    A(T.glide, "#s-you", {{ translateY: [0, {GLIDE}] }}, 0.45, INOUT);
    LEAVE(T.glide, ["#s-lab-0"]);  // the label has done its job; the step line below carries it on
    RISE(T.step, ["#s-nl-0"]);
    RISE(T.usp, ["#s-u1-0", "#s-u2-0", "#s-u2-1", "#s-u3-0"]);
    ENTER(T.brand, "#s-bn");
"""
    return css, html, js


# ============================================================ CTA (C7 + C8) — Paper over Navy, 30s only
# C7: the frame is split into two full-bleed fields. Paper on top: '생성하는 쪽' (what the AI produces,
# muted) and the headline '서명하는 쪽으로 / 넘어오세요.', 100px clear of the split. Navy below, its own
# evenly spaced stack: '서명하는 쪽' (gold), the gold signature, the button (S2, on the bar line), the note.
# C8 (a move inside the shot): the Paper field wipes up out of the frame (in-out) so the Navy side
# takes it all; the gold signature travels up to become the slogan's underline; the slogan (88px,
# two lines) rises, mark / USP / brand / phone settle. The button and its note do not move.
SPLIT = 940


def build_cta(T):
    d = [x["body"][0] for x in DOCS]
    css = f"""
    #c-ground {{ background: var(--navy); }}
    #c-paper {{ position: absolute; left: 0; top: 0; width: 1080px; height: {SPLIT}px; background: var(--paper); overflow: hidden; }}
    #c-svg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }}
    .mark {{ position: absolute; left: 518.4px; width: 43.2px; height: 48px; }}
"""
    gold = "M120 1138 C 360 1141, 640 1137, 840 1131 S 945 1125, 960 1123"   # ~y1135, under '서명하는 쪽'
    html = f'''    <div id="c-ground" class="field" data-layout-ignore></div>
    <div id="c-cam" class="cam" data-layout-allow-overflow>
      <div id="c-paper" data-layout-allow-overflow>
        {text("c-a", "head", 260, ["생성하는 쪽"], "m-l")}
        {text("c-af", "body", 400, d, "m-l")}
        {text("c-h", "head", 640, ["서명하는 쪽으로", "넘어오세요."], "on-paper", rise=True)}
      </div>
      {text("c-b", "head", 990, ["서명하는 쪽"], "au")}
      <svg id="c-svg" viewBox="0 0 1080 1920" data-layout-ignore>
        <path id="c-gold" d="{gold}" stroke="#b8955a" stroke-width="6" stroke-linecap="round" fill="none"/>
      </svg>
      {text("e-slo", "head", 408, ["책임지는 자리로,", "지금 있는 자리에서."], "on-ink", rise=True)}
      <div id="e-info" class="later">
        {MARK.replace('class="mark"', 'class="mark" style="top:260px"')}
        {text("e-u", "body", 776, ["국내 유일* 100% 온라인 법학사"], "on-ink")}
        {text("e-u3", "small", 842, ["교육부장관 명의 · '법학 전공' 표기"], "m-d")}
        {text("e-bn", "body", 998, [BRAND], "on-ink")}
        {text("e-tel", "body", 1380, ["070-4006-7128 (평일 10–18시)"], "on-ink")}
      </div>
      {pill("c-btn", 1180, 840, "무료 상담 신청", "var(--paper)", "var(--ink)", "opacity:0")}
      {text("c-sub", "small", 1312, ["상담만 받아도 돼요."], "m-d", cls="later")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#c-cam");
    RISE(T.head, ["#c-h-0", "#c-h-1"]);
    ENTER(T.btn, "#c-btn");
    ENTER(T.sub, "#c-sub");
    // C8: the Paper field wipes up (its contents go with it), the Navy-side label leaves,
    // the gold signature travels up under the slogan; button and note stay put
    LEAVE(T.e - 0.1, ["#c-b-0"]);
    A(T.e, "#c-paper", {{ clipPath: ["inset(0px 0px 0px 0px)", "inset(0px 0px {SPLIT}px 0px)"] }}, 0.9, INOUT);
    A(T.e + 0.03, "#c-gold", {{ translateY: [0, -485] }}, 0.8, INOUT);
    RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    ENTER(T.info, "#e-info");
"""
    return css, html, js


# ============================================================ END (C8') — Navy, 15s only
# The mark and the full-width button are on the frame from the cut (a Navy-to-Navy cut needs something
# that lands at once); the slogan rises, the underline draws, brand and phone settle.
def build_end(T):
    css = """
    #e-ground { background: var(--navy); }
    .mark { position: absolute; left: 518.4px; width: 43.2px; height: 48px; }
"""
    underline = "M120 653 C 360 656, 640 652, 840 646 S 945 640, 960 638"
    html = f'''    <div id="e-ground" class="field" data-layout-ignore></div>
    <div id="e-cam" class="cam" data-layout-allow-overflow>
      {text("e-slo", "head", 408, ["책임지는 자리로,", "지금 있는 자리에서."], "on-ink", rise=True)}
      <svg id="e-svg" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px" data-layout-ignore>
        <path id="e-ul" d="{underline}" stroke="#b8955a" stroke-width="6" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      {MARK.replace('class="mark"', 'class="mark" style="top:260px"')}
      <div id="e-info" class="later">
        {text("e-bn", "body", 791, [BRAND], "on-ink")}
        {text("e-tel", "body", 1243, ["070-4006-7128 (평일 10–18시)"], "on-ink")}
      </div>
      {pill("e-btn", 988, 840, "무료 상담 신청", "var(--paper)", "var(--ink)")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#e-cam");
    RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    DRAW(T.c0, T.ul, "#e-ul", 1.1);
    ENTER(T.info, "#e-info");
"""
    return css, html, js


# ============================================================ LEGAL overlay (연출 + 고지 L1·L2), fixed positions
def build_legal(t0, t1, tag, disc, light_from=None):
    """tag=(start,end) abs; disclaimers from `disc` to the end. Mute tone for Ink/Navy, darker on Paper."""
    css = """
    #root { pointer-events: none; }
"""
    html = f'''    <div id="l-tag" class="clip row t-small m-d" data-start="{tag[0] - t0:.3f}" data-duration="{tag[1] - tag[0]:.3f}" data-track-index="1" style="top:142px">연출</div>
    <div id="l-d" class="clip" data-start="{disc - t0:.3f}" data-duration="{t1 - disc:.3f}" data-track-index="2">
      <div id="l-d1" class="row t-small m-d" style="top:1494px">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</div>
      <div id="l-d2" class="row t-small m-d" style="top:1530px">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</div>
    </div>'''
    js = "" if light_from is None else f"""
    S({light_from}, ["#l-d1", "#l-d2"], {{ color: "#5f6368" }});
"""
    return css, html, js


# ============================================================ assemble
if VARIANT == "30":
    # hard cuts (bar lines of the excerpt; C2 = B7, where the music returns after its stop)
    C = dict(hook=0, tease=B(4), fill=B(7), blank=B(16), quiet=B(24), sign=B(40), cta=B(56), fin=30.0)
    T_h = dict(c0=C["hook"], end=C["tease"])
    T_t = dict(c0=C["tease"], cap=C["tease"] + 0.05, end=C["fill"], btn=None)
    T_f = dict(c0=C["fill"], fills=[3.20, 3.85, 4.50], oks=[3.95, 4.60, 5.25], end=C["blank"])
    T_b = dict(c0=C["blank"], cap=C["blank"] + 0.05, btn=7.30, presses=[7.62, 7.92, 8.20, 8.46], toast=8.58, end=C["quiet"])
    T_q = dict(c0=C["quiet"], c1=C["quiet"] + 0.08, c2=12.12, c5=B(32), ext=B(32) + 0.08, c3=14.42, c4=15.50,
               br=None, end=C["sign"])
    T_s = dict(c0=C["sign"], hit=B(44), draw=1.1, you=20.40, glide=B(48), step=B(48) + 0.40, usp=B(48) + 0.50,
               brand=21.95, end=C["cta"])
    T_c = dict(c0=C["cta"], head=C["cta"] + 0.05, btn=B(60), sub=B(60) + 0.09, e=27.20, slo=27.75,
               info=27.85, end=C["fin"])
    SCENE_SPECS = [
        ("hook", C["hook"], C["tease"], build_hook(T_h)),
        ("tease", C["tease"], C["fill"], build_tease(T_t)),
        ("fill", C["fill"], C["blank"], build_fill(T_f)),
        ("blank", C["blank"], C["quiet"], build_blank(T_b)),
        ("quiet", C["quiet"], C["sign"], build_quiet(T_q, "AI가 일을 대신할수록,", ("책임질 자리는", "더 귀해집니다."),
                                                     c3="그 자리엔 언제나", c4=("법을 아는 사람이", "있었습니다."))),
        ("sign", C["sign"], C["cta"], build_sign(T_s)),
        ("cta", C["cta"], C["fin"], build_cta(T_c)),
    ]
    TAG = (15.5, C["cta"])   # 연출: spec f465–f719 (15.5–24.0), held to the end of the shot
    DISC = T_s["glide"]      # L1·L2 on the USP downbeat (spec f630)
    LIGHT_FROM = None        # the disclaimers always sit on a dark field (Navy under C6, C7, C8)
    CUTS = [(C["tease"], "C1 S2"), (C["fill"], "C2"), (C["blank"], "C3"), (C["quiet"], "C4"), (C["sign"], "C6"), (C["cta"], "C7")]
    MOVES = [(T_b["toast"] + 0.3, "C3 S3 toast (entrance)"), (T_q["c5"], "C5 line draws out (in shot)"),
             (T_s["hit"], "C6 S2 signature stroke"), (T_s["usp"], "C6 S3 USP stack"), (T_c["btn"], "C7 S2 button"),
             (T_c["e"], "C8 end card (in shot)")]
else:
    C = dict(hook=0, tease=B(3), quiet=B(11), sign=B(23), end=B(28), fin=15.0)  # C8' on B28 (lead: USP >= 1.3 s)
    T_h = dict(c0=C["hook"], end=C["tease"])
    T_t = dict(c0=C["tease"], cap=C["tease"] + 0.05, btn=B(5), presses=[2.40, 2.64, 2.88], toast=2.98, end=C["quiet"])
    T_q = dict(c0=C["quiet"], c1=C["quiet"] + 0.08, c2=6.40, c5=None, br=B(19), brIn=B(19) + 0.3, gold=9.207, end=C["sign"])
    T_s = dict(c0=C["sign"], hit=C["sign"], draw=0.75, you=10.25, glide=10.45, step=10.78, usp=10.84,
               brand=11.20, end=C["end"])
    T_e = dict(c0=C["end"], slo=C["end"] + 0.05, info=C["end"] + 0.5, btn=C["end"], ul=C["end"] + 0.75, end=C["fin"])
    SCENE_SPECS = [
        ("hook", C["hook"], C["tease"], build_hook(T_h)),
        ("tease", C["tease"], C["quiet"], build_tease(T_t, presses=True)),
        ("quiet", C["quiet"], C["sign"], build_quiet(T_q, "AI가 대신할수록,", ("책임질 자리는", "더 귀해집니다."),
                                                     bridge=("그 칸은,", '법을 아는 <span class="au">사람의 몫</span>'))),
        ("sign", C["sign"], C["end"], build_sign(T_s, compact=True)),
        ("end", C["end"], C["fin"], build_end(T_e)),
    ]
    TAG = (9.0, C["end"])    # 연출: spec f270–f359 (9.0–12.0), held to the end of the staged shot
    DISC = 10.70             # L1·L2 at spec f321 (10.7), with the USP moment
    LIGHT_FROM = None
    CUTS = [(C["tease"], "C1' S2"), (C["quiet"], "C4'"), (C["sign"], "C6' (signature)"), (C["end"], "C8'")]
    MOVES = [(T_t["btn"], "C3' button (music returns)"), (T_t["toast"] + 0.3, "C3' toast"), (T_q["br"], "C4' S3 bridge"),
             (T_s["usp"], "C6' S3 USP")]

# sound on exactly two visible actions (client round 4: fewer, cleaner effects): the error toast and the
# pen touch of the signature. No clicks, ticks, whips or swipes.
if VARIANT == "30":
    SFX = [(T_b["toast"] + 0.3, "error"), (T_s["hit"], "pen")]
else:
    SFX = [(T_t["toast"] + 0.3, "error"), (T_s["hit"], "pen")]

SLOTS = []
for cid, t0, t1, (css, html, js) in SCENE_SPECS:
    SLOTS.append(scene(cid, t0, t1, css, html, js))
lc, lh, lj = build_legal(TAG[0], TOTAL, TAG, DISC, LIGHT_FROM)
SLOTS.append(scene("legal", TAG[0], TOTAL, lc, lh, lj))


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
