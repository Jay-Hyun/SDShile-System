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
# f0 is complete: headline, status, three stacked sheets (back two show title + watermark strip).
def build_hook(T):
    d0, d1, d2 = DOCS
    css = """
    #h-ground { background: var(--ink); }
"""
    html = f'''    <div id="h-ground" class="field" data-layout-ignore></div>
    <div id="h-cam" class="cam" data-layout-allow-overflow>
      {sheet("h-s2", 664, 560, 760, "var(--sheet-3)")}
      {sheet("h-s1", 792, 480, 800, "var(--sheet-2)")}
      {sheet("h-s0", 920, 370)}
      {text("h-head", "display", 300, ["AI가", "다 써줍니다."], "on-ink")}
      {text("h-stat", "small", 590, ['법률 검토 문서 3건 작성 · <span class="on-ink">생성 완료 0.1s</span>'], "m-d")}
      {text("h-t2", "body", 682, [d2["title"]], "on-paper")}
      {text("h-w2", "small", 738, [WM], "m-l")}
      {text("h-t1", "body", 810, [d1["title"]], "on-paper")}
      {text("h-w1", "small", 866, [WM], "m-l")}
      {text("h-t0", "body", 938, [d0["title"]], "on-paper")}
      {text("h-w0", "small", 994, [WM], "m-l")}
      {text("h-b0", "small", 1046, d0["body"], "on-paper")}
      {text("h-sg", "small", 1182, [SIG], "m-l")}
      {rule("h-r0", 1246, 240, "m-l")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#h-cam");
"""
    return css, html, js


# ============================================================ TEASE (C1 S2 / C1' S2 + C3') — Paper
# Cut to the page itself: the last lines of the document and the one blank line, caret waiting.
# 15s continues into C3': '생성' button, three presses (the lines above change, the blank stays), toast.
def build_tease(T, presses=False):
    d0 = DOCS[0]
    pairs = [(d0["last"][1], d0["last"][0]), (d0["last"][2], d0["last"][3]), (d0["last"][4], d0["body"][1]), (d0["body"][0], d0["last"][1])]
    css = """
    #t-ground { background: var(--paper); }
"""
    lines = ""
    for v, (a, b) in enumerate(pairs if presses else pairs[:1]):
        lines += text(f"t-l{v}", "small", 852, [a, b], "on-paper", rise=v > 0)
    extra = ""
    if presses:
        extra = (pill("t-btn", 1230, 320, "생성", "var(--ink)", "var(--paper)", "opacity:0") +
                 pill("t-toast", 1230, 840, "이 항목은 생성할 수 없습니다.", "var(--red)", "var(--paper)", "opacity:0"))
    html = f'''    <div id="t-ground" class="field" data-layout-ignore></div>
    <div id="t-cam" class="cam" data-layout-allow-overflow>
      {text("t-cap", "display", 300, ["딱 한 칸만", "빼고."], "on-paper", rise=True)}
      {text("t-wm", "small", 790, [WM], "m-l")}
      {lines}
      {text("t-sg", "body", 980, [SIG], "on-paper")}
      {rule("t-r", 1100, 600, "on-paper")}
      {caret("t-c", 240, 1048, 44, "on-paper")}
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
# Three sheets stacked on the axis; each one's body sets line by line, then its check appears.
# The signature line at the foot of each sheet stays empty.
def build_fill(T):
    css = """
    #f-ground { background: var(--ink); }
    .tt { position: relative; }
    .ok { position: absolute; left: calc(100% + 14px); top: 50%; width: 30px; height: 30px; margin-top: -15px; color: var(--ink); opacity: 0; }
"""
    parts = []
    for i, d in enumerate(DOCS):
        y = 330 + i * 344
        parts.append(sheet(f"f-s{i}", y, 320))
        parts.append(text(f"f-t{i}", "body", y + 24, [f'<span class="tt">{d["title"]}<span id="f-k{i}">{CHECK}</span></span>'], "on-paper"))
        parts.append(text(f"f-w{i}", "small", y + 80, [WM], "m-l"))
        parts.append(text(f"f-b{i}", "small", y + 136, d["body"][:2], "on-paper", rise=True))
        parts.append(text(f"f-g{i}", "small", y + 228, [SIG], "m-l"))
        parts.append(rule(f"f-r{i}", y + 284, 240, "m-l"))
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
# Payoff of the teaser: the three signature lines, '생성' pressed four times — the sentence above each
# line changes every time, the lines stay empty — then the toast (the only red in the film).
def build_blank(T):
    css = """
    #b-ground { background: var(--ink); }
"""
    parts = []
    nvar = len(T["presses"]) + 1
    for i, d in enumerate(DOCS):
        y = 630 + i * 214
        parts.append(sheet(f"b-s{i}", y, 200))
        for v in range(nvar):
            parts.append(text(f"b-l{i}v{v}", "small", y + 28, [d["last"][v]], "m-l", rise=v > 0))
        parts.append(text(f"b-g{i}", "body", y + 72, [SIG], "on-paper"))
        parts.append(rule(f"b-r{i}", y + 166, 360, "on-paper"))
        parts.append(caret(f"b-c{i}", 360, y + 128, 34, "on-paper"))
    html = f'''    <div id="b-ground" class="field" data-layout-ignore></div>
    <div id="b-cam" class="cam" data-layout-allow-overflow>
      {text("b-cap", "display", 300, ["딱 한 칸만", "빼고."], "on-ink", rise=True)}
      {"".join(parts)}
      {pill("b-btn", 1290, 320, "생성", "var(--paper)", "var(--ink)", "opacity:0")}
      {pill("b-toast", 1290, 840, "이 항목은 생성할 수 없습니다.", "var(--red)", "var(--paper)", "opacity:0")}
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
# Everything but the signature line is gone. Two lines of thought arrive over it.
# 30s C5 (a move on the bar line, no cut): the thoughts and the label leave, the blank line draws
# out to the full width of the frame ("그 자리"), the next two lines take the same slots.
# 15s: the bridge line takes the slots, then the caret turns gold (someone is about to sign).
def build_quiet(T, c1, c2, c3=None, c4=None, bridge=None):
    css = """
    #q-ground { background: var(--ink); }
"""
    slots = (text("q-c1", "head", 400, [c1], "on-ink", rise=True) +
             text("q-c2", "display", 520, list(c2), "on-ink", rise=True))
    if c3:
        slots += (text("q-c3", "head", 400, [c3], "on-ink", rise=True) +
                  text("q-c4", "display", 520, list(c4), "on-ink", rise=True))
    if bridge:
        slots += text("q-br", "head", 560, list(bridge), "on-ink", rise=True)
    html = f'''    <div id="q-ground" class="field" data-layout-ignore></div>
    <div id="q-cam" class="cam" data-layout-allow-overflow>
      {slots}
      {text("q-sg", "body", 980, [SIG], "m-d")}
      {rule("q-r", 1100, 600, "on-ink")}
      {caret("q-c", 240, 1048, 44, "on-ink")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#q-cam");
    RISE(T.c1, ["#q-c1-0"]);
    RISE(T.c2, ["#q-c2-0", "#q-c2-1"]);
    CARET("#q-c", T.c0, T.c5 != null ? T.c5 : T.end);
    if (T.c5 != null) {{
      LEAVE(T.c5, ["#q-c1-0", "#q-c2-0", "#q-c2-1", "#q-sg-0"]);
      S(T.c5, "#q-c", {{ opacity: 0 }});
      A(T.ext, "#q-r", {{ scaleX: [1, 1.8] }}, 1.1, INOUT);
      RISE(T.c3, ["#q-c3-0"]);
      RISE(T.c4, ["#q-c4-0", "#q-c4-1"]);
    }}
    if (T.br != null) {{
      LEAVE(T.br, ["#q-c1-0", "#q-c2-0", "#q-c2-1"]);
      RISE(T.brIn, ["#q-br-0", "#q-br-1"]);
      S(T.gold, "#q-c", {{ backgroundColor: "#b8955a" }});
    }}
"""
    return css, html, js


# ============================================================ SIGN (C6 / C6') — Navy (brand field)
# THE signature moment: a gold stroke draws across the empty line (1100 ms in-out). The label is
# replaced by '그 칸으로 가는 첫 계단', then the USP stack rises above it with the stroke as its base,
# and the brand settles under the line.
def build_sign(T, compact=False):
    css = """
    #s-ground { background: var(--navy); }
    #s-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    .mark { position: absolute; left: 518.4px; width: 43.2px; height: 48px; }
"""
    u3 = "교육부장관 명의" if compact else "교육부장관 명의 · '법학 전공' 표기"
    stroke = "M228 1110 C 380 1113, 560 1107, 700 1099 S 826 1085, 856 1079"
    html = f'''    <div id="s-ground" class="field" data-layout-ignore></div>
    <div id="s-cam" class="cam" data-layout-allow-overflow>
      {text("s-u1", "body", 400, ["국내 유일*"], "au", rise=True)}
      {text("s-u2", "display", 476, ["100% 온라인", "법학사"], "on-ink", rise=True)}
      {text("s-u3", "body", 764, [u3], "m-d", rise=True)}
      {text("s-sg", "body", 980, [SIG], "m-d")}
      {text("s-nl", "head", 958, [NEW], "on-ink", rise=True)}
      {rule("s-r", 1100, 600, "m-d")}
      {caret("s-c", 240, 1048, 44, "au")}
      <svg id="s-svg" viewBox="0 0 1080 1920" data-layout-ignore>
        <path id="s-ink" d="{stroke}" stroke="#b8955a" stroke-width="6" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      <div id="s-br" class="later">{MARK.replace('class="mark"', 'class="mark" style="top:1170px"')}{text("s-bn", "body", 1228, [BRAND], "on-ink")}</div>
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#s-cam");
    if (T.caret != null) CARET("#s-c", T.caret, T.hit);
    S(T.hit, "#s-c", {{ opacity: 0 }});
    DRAW(T.c0, T.hit, "#s-ink", 1.1);
    A(T.hit, "#s-r", {{ opacity: [1, 0] }}, 1.1, INOUT);  // the blank gives way to the signature
    LEAVE(T.oldOut, ["#s-sg-0"]);
    RISE(T.newIn, ["#s-nl-0"]);
    RISE(T.usp, ["#s-u1-0", "#s-u2-0", "#s-u2-1", "#s-u3-0"]);
    ENTER(T.brand, "#s-br");
"""
    return css, html, js


# ============================================================ CTA (C7 + C8) — Paper, 30s only
# C7: '생성하는 쪽' / '서명하는 쪽' as a two-row choice; a Navy selector travels from the first row to
# the second (in-out), the text inverts inside it. S2 on the bar line: the consult button.
# C8 (a move inside the shot): the headline and the choice leave, the slogan rises, its gold
# underline draws, USP / brand / phone settle; the button stays where it is.
def build_cta(T):
    css = """
    #c-ground { background: var(--paper); }
    #c-sel { position: absolute; left: 120px; top: 679px; width: 840px; height: 124px; background: var(--navy); overflow: hidden; }
    #c-selin { position: absolute; left: -120px; top: -679px; width: 1080px; height: 1920px; }
    #c-svg, #c-selsvg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    .mark { position: absolute; left: 518.4px; width: 43.2px; height: 48px; }
"""
    gold_b = "M440 941 C 500 935, 580 946, 640 937"
    underline = "M246 545 C 420 536, 640 551, 834 538"
    html = f'''    <div id="c-ground" class="field" data-layout-ignore></div>
    <div id="c-cam" class="cam" data-layout-allow-overflow>
      {text("c-head", "display", 300, ["서명하는 쪽으로", "넘어오세요."], "on-paper", rise=True)}
      <div id="c-choice">
        {text("c-a", "head", 700, ["생성하는 쪽"], "m-l")}
        {text("c-b", "head", 840, ["서명하는 쪽"], "on-paper")}
        <svg id="c-svg" viewBox="0 0 1080 1920" data-layout-ignore><path d="{gold_b}" stroke="#b8955a" stroke-width="5" stroke-linecap="round" fill="none"/></svg>
        <div id="c-sel" data-layout-allow-occlusion data-layout-allow-overlap>
          <div id="c-selin">
            {text("c-a2", "head", 700, ["생성하는 쪽"], "on-ink")}
            {text("c-b2", "head", 840, ["서명하는 쪽"], "on-ink")}
            <svg id="c-selsvg" viewBox="0 0 1080 1920" data-layout-ignore><path d="{gold_b}" stroke="#b8955a" stroke-width="5" stroke-linecap="round" fill="none"/></svg>
          </div>
        </div>
      </div>
      {text("e-slo", "head", 330, ["책임지는 자리로,", "지금 있는 자리에서."], "on-paper", rise=True)}
      <svg id="e-svg" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px" data-layout-ignore>
        <path id="e-ul" d="{underline}" stroke="#b8955a" stroke-width="5" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      <div id="e-info" class="later">
        {text("e-u", "body", 716, ["국내 유일* 100% 온라인 법학사"], "on-paper")}
        {text("e-u3", "small", 776, ["교육부장관 명의 · '법학 전공' 표기"], "m-l")}
        {MARK.replace('class="mark"', 'class="mark" style="top:856px"')}
        {text("e-bn", "body", 914, [BRAND], "on-paper")}
        {text("e-tel", "body", 1344, ["070-4006-7128 (평일 10–18시)"], "on-paper")}
      </div>
      {pill("c-btn", 1150, 720, "무료 상담 신청", "var(--navy)", "var(--paper)", "opacity:0")}
      {text("c-sub", "small", 1278, ["상담만 받아도 돼요."], "m-l", cls="later")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#c-cam");
    RISE(T.head, ["#c-head-0", "#c-head-1"]);
    // the selector travels one row down; its inside counter-moves so the inverted copy stays in register
    A(T.slide, "#c-sel", {{ translateY: [0, 140] }}, 0.7, INOUT);
    A(T.slide, "#c-selin", {{ translateY: [0, -140] }}, 0.7, INOUT);
    ENTER(T.btn, "#c-btn");
    ENTER(T.sub, "#c-sub");
    // C8
    LEAVE(T.e, ["#c-head-0", "#c-head-1", "#c-choice"]);
    RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    DRAW(T.c0, T.ul, "#e-ul", 1.1);
    ENTER(T.info, "#e-info");
"""
    return css, html, js


# ============================================================ END (C8') — Paper, 15s only
def build_end(T):
    css = """
    #e-ground { background: var(--paper); }
    .mark { position: absolute; left: 518.4px; width: 43.2px; height: 48px; }
"""
    underline = "M246 545 C 420 536, 640 551, 834 538"
    html = f'''    <div id="e-ground" class="field" data-layout-ignore></div>
    <div id="e-cam" class="cam" data-layout-allow-overflow>
      {text("e-slo", "head", 330, ["책임지는 자리로,", "지금 있는 자리에서."], "on-paper", rise=True)}
      <svg id="e-svg" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px" data-layout-ignore>
        <path id="e-ul" d="{underline}" stroke="#b8955a" stroke-width="5" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      <div id="e-info" class="later">
        {MARK.replace('class="mark"', 'class="mark" style="top:700px"')}
        {text("e-bn", "body", 758, [BRAND], "on-paper")}
        {text("e-tel", "body", 1290, ["070-4006-7128 (평일 10–18시)"], "on-paper")}
      </div>
      {pill("e-btn", 1150, 720, "무료 상담 신청", "var(--navy)", "var(--paper)", "opacity:0")}
    </div>'''
    js = f"""
    const T = {J(T)};
    PUSH(T.c0, T.end, "#e-cam");
    RISE(T.slo, ["#e-slo-0", "#e-slo-1"]);
    DRAW(T.c0, T.ul, "#e-ul", 1.1);
    ENTER(T.info, "#e-info");
    ENTER(T.btn, "#e-btn");
"""
    return css, html, js


# ============================================================ LEGAL overlay (연출 + 고지 L1·L2), fixed positions
def build_legal(t0, t1, tag, disc, light_from):
    """tag=(start,end) abs; disclaimers from `disc` to the end. Mute tone for Ink/Navy, darker on Paper."""
    css = """
    #root { pointer-events: none; }
"""
    html = f'''    <div id="l-tag" class="clip row t-small m-d" data-start="{tag[0] - t0:.3f}" data-duration="{tag[1] - tag[0]:.3f}" data-track-index="1" style="top:142px">연출</div>
    <div id="l-d" class="clip" data-start="{disc - t0:.3f}" data-duration="{t1 - disc:.3f}" data-track-index="2">
      <div id="l-d1" class="row t-small m-d" style="top:1494px">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</div>
      <div id="l-d2" class="row t-small m-d" style="top:1530px">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</div>
    </div>'''
    js = f"""
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
    T_q = dict(c0=C["quiet"], c1=C["quiet"] + 0.08, c2=12.12, c5=B(32), ext=B(32) + 0.08, c3=14.62, c4=15.50,
               br=None, end=C["sign"])
    T_s = dict(c0=C["sign"], caret=C["sign"] + 0.28, hit=B(44), oldOut=B(44) + 0.55, newIn=B(44) + 0.65,
               usp=B(48), brand=21.90, end=C["cta"])
    T_c = dict(c0=C["cta"], head=C["cta"] + 0.05, slide=25.35, btn=B(60), sub=B(60) + 0.09, e=27.50, slo=27.85,
               ul=28.15, info=27.95, end=C["fin"])
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
    DISC = T_s["usp"]        # L1·L2 with the USP (spec f630)
    LIGHT_FROM = C["cta"]
    CUTS = [(C["tease"], "C1 S2"), (C["fill"], "C2"), (C["blank"], "C3"), (C["quiet"], "C4"), (C["sign"], "C6"), (C["cta"], "C7")]
    MOVES = [(T_b["toast"] + 0.3, "C3 S3 toast (entrance)"), (T_q["c5"], "C5 line draws out (in shot)"),
             (T_s["hit"], "C6 S2 signature stroke"), (T_s["usp"], "C6 S3 USP stack"), (T_c["btn"], "C7 S2 button"),
             (T_c["e"], "C8 end card (in shot)")]
else:
    C = dict(hook=0, tease=B(3), quiet=B(11), sign=B(23), end=B(27), fin=15.0)
    T_h = dict(c0=C["hook"], end=C["tease"])
    T_t = dict(c0=C["tease"], cap=C["tease"] + 0.05, btn=B(5), presses=[2.40, 2.64, 2.88], toast=2.98, end=C["quiet"])
    T_q = dict(c0=C["quiet"], c1=C["quiet"] + 0.08, c2=6.40, c5=None, br=B(19), brIn=B(19) + 0.45, gold=9.207, end=C["sign"])
    T_s = dict(c0=C["sign"], caret=None, hit=C["sign"], oldOut=C["sign"] + 0.06, newIn=C["sign"] + 0.14,
               usp=10.70, brand=11.17, end=C["end"])
    T_e = dict(c0=C["end"], slo=C["end"] + 0.05, ul=12.15, info=12.25, btn=12.30, end=C["fin"])
    SCENE_SPECS = [
        ("hook", C["hook"], C["tease"], build_hook(T_h)),
        ("tease", C["tease"], C["quiet"], build_tease(T_t, presses=True)),
        ("quiet", C["quiet"], C["sign"], build_quiet(T_q, "AI가 대신할수록,", ("책임질 자리는", "더 귀해집니다."),
                                                     bridge=("그 칸은,", '법을 아는 <span class="au">사람의 몫</span>'))),
        ("sign", C["sign"], C["end"], build_sign(T_s, compact=True)),
        ("end", C["end"], C["fin"], build_end(T_e)),
    ]
    TAG = (9.0, 12.0)        # 연출: spec f270–f359
    DISC = T_s["usp"]        # spec f321 (10.7)
    LIGHT_FROM = C["end"]
    CUTS = [(C["tease"], "C1' S2"), (C["quiet"], "C4'"), (C["sign"], "C6' (signature)"), (C["end"], "C8'")]
    MOVES = [(T_t["btn"], "C3' button (music returns)"), (T_t["toast"] + 0.3, "C3' toast"), (T_q["br"], "C4' S3 bridge"),
             (T_s["usp"], "C6' S3 USP")]

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
