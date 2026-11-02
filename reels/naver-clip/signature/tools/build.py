"""「마지막 서명」 — anime.js v4 scene generator (30s at the project root, 15s in v15/).

Usage (from the project root):
  python3 tools/build.py              # compositions/*.html + index.html      (30s)
  python3 tools/build.py --variant 15 # v15/compositions/*.html + v15/index.html (15s)

Engine: anime.js v4 only (lib/anime.umd.min.js). Every scene builds ONE paused timeline
(`autoplay: false`) and pushes it to window.__hfAnime. HyperFrames seeks every anime
instance to the ROOT time in ms, so all positions below are absolute video seconds.
Randomness (shake, grain, dust) uses anime.createSeededRandom.

Timing: every cut and accent is a beat of the BGM excerpt (beats/source.json, see MUSIC.md).
B(k) = k-th beat of the excerpt in video seconds. Copy and compliance follow
docs/ads/naver-clip/01-last-signature.md (cut order, 연출/예시/L1/L2, USP order).
"""
import json
import os
import random
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


def B(k):
    """k-th beat of the excerpt (video seconds). Fractions = 8th notes between beats."""
    k0 = int(k)
    fr = k - k0
    return round(GRID[k0] + fr * (GRID[k0 + 1] - GRID[k0]), 3)


# ---------------------------------------------------------------- shared art
ICON = ('<svg viewBox="0 0 64 64"><rect x="2" y="2" width="60" height="60" rx="16" fill="#22262B"/>'
        '<path d="M21 14h15l10 10v25a3 3 0 0 1-3 3H21a3 3 0 0 1-3-3V17a3 3 0 0 1 3-3z" fill="#F4F1EA"/>'
        '<path d="M36 14v10h10z" fill="#6F8F7A"/>'
        '<path d="M24 32h16M24 38h16M24 44h10" stroke="#22262B" stroke-width="2.6" stroke-linecap="round"/></svg>')
ICON_GREY = ICON.replace("#22262B", "#9A9C9F").replace("#6F8F7A", "#C9CBCD")
SENT = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
HAND_PTR = ('<svg viewBox="0 0 100 120"><path d="M38 8c6 0 10 4 10 10v34l4-1c2-8 16-8 18 1 4-6 16-4 17 4 5-3 13 0 13 8v24c0 16-12 28-28 28H54c-9 0-16-4-21-11L10 74c-4-6 0-14 8-13 4 0 7 3 10 6V18c0-6 4-10 10-10z" '
            'fill="#ffffff" stroke="#161616" stroke-width="5" stroke-linejoin="round"/></svg>')
PHONE = '<svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="#0B1A33"/></svg>'
PEN_ICON = ('<svg viewBox="0 0 120 120"><g transform="rotate(45 60 60)"><rect x="49" y="6" width="22" height="66" rx="8" fill="#161616"/>'
            '<rect x="49" y="20" width="22" height="6" fill="#B8955A"/><path d="M49 72h22l-11 34z" fill="#B8955A"/>'
            '<path d="M60 80v18" stroke="#161616" stroke-width="2.4"/></g></svg>')
# 매크로 펜 (가상 일러스트). 펜촉 끝 = viewBox (14, 586)
PEN_HAND = '''<svg viewBox="0 0 640 640" width="640" height="640" style="overflow:visible">
  <defs>
    <linearGradient id="@@-lq" x1="0" y1="-22" x2="0" y2="22" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#4a4f58"/><stop offset="0.28" stop-color="#15171b"/><stop offset="0.7" stop-color="#050506"/><stop offset="1" stop-color="#2a2d33"/></linearGradient>
    <linearGradient id="@@-gd" x1="0" y1="-18" x2="0" y2="18" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f3dfae"/><stop offset="0.45" stop-color="#c9a666"/><stop offset="1" stop-color="#8a6a33"/></linearGradient>
    <radialGradient id="@@-gl"><stop offset="0" stop-color="#fff4d6" stop-opacity="1"/><stop offset="0.35" stop-color="#e0c27e" stop-opacity="0.7"/><stop offset="1" stop-color="#e0c27e" stop-opacity="0"/></radialGradient>
    <filter id="@@-sh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  </defs>
  <g transform="translate(14 586) rotate(-45)">
    <rect x="60" y="34" width="1500" height="30" rx="15" fill="rgba(0,0,0,0.35)" filter="url(#@@-sh)"/>
    <rect x="118" y="-21" width="1500" height="42" rx="21" fill="url(#@@-lq)"/>
    <rect x="118" y="-21" width="1500" height="9" rx="4" fill="rgba(255,255,255,0.16)"/>
    <rect x="96" y="-17" width="30" height="34" rx="6" fill="url(#@@-gd)"/>
    <rect x="72" y="-15" width="28" height="30" rx="4" fill="#0d0e10"/>
    <rect x="430" y="-22" width="16" height="44" fill="url(#@@-gd)"/>
    <rect x="452" y="-22" width="5" height="44" fill="url(#@@-gd)"/>
    <path d="M0 0 C18 -4 40 -13 74 -15 L74 15 C40 13 18 4 0 0 Z" fill="url(#@@-gd)"/>
    <path d="M4 0 L56 0" stroke="#5a4320" stroke-width="1.6"/>
    <circle cx="56" cy="0" r="3.2" fill="#5a4320"/>
  </g>
  <circle id="@@-tip" cx="14" cy="586" r="46" fill="url(#@@-gl)" opacity="0"/>
</svg>'''
MARK = '<img src="assets/img/mark-gold.svg" alt="">'

DOCS = [
    dict(title="계약 검토의견서", hd="1. 검토 의견", mid="당사자: 갑 · 을",
         last=["갑의 해지 통지는 요건을 갖추었습니다.", "을의 지체 책임은 일부 제한됩니다.",
               "위약금 조항은 감액될 여지가 있습니다.", "제5조의 해석은 갑에게 유리합니다.",
               "추가 자료 확인 후 보완을 권합니다."]),
    dict(title="소장 초안(가상)", hd="청구 취지", mid="원고 갑 · 피고 을",
         last=["피고 을은 원고 갑에게 지급하라.", "소송비용은 피고 을이 부담한다.",
               "피고 을은 계약금을 반환하라.", "원고 갑의 나머지 청구를 유지한다.",
               "제1항은 가집행할 수 있다."]),
    dict(title="법률 검토 보고서", hd="검토 결론", mid="의뢰인: 갑",
         last=["현 단계에서 분쟁 위험은 낮습니다.", "합의 조건의 재검토를 권합니다.",
               "갑의 주장은 대체로 타당합니다.", "증빙 보완 시 승소 가능성이 높아집니다.",
               "을과의 협상을 우선 권합니다."]),
]
COLX = [60, 353, 646]
COLY, COLW, COLH = 430, 273, 1030
SIG_Y = COLY + 888 + 66  # vertical centre of the signature boxes (abs px)

rnd = random.Random(20261102)
BARS = []
for i in range(3):
    rows, y, k = [], 0, 0
    while y <= 610:
        rows.append(("mid", y) if k == 11 else ("bar", y, 100 if k % 6 == 0 else rnd.randint(58, 100), k % 6 == 0))
        y += 26
        k += 1
    BARS.append(rows)


def doc(i, p, ok_on=True, sig_style="", last_variants=False, filled=True):
    d = DOCS[i]
    rows = []
    for r in BARS[i]:
        if r[0] == "mid":
            rows.append(f'<div class="mid" style="top:{r[1] - 6}px">{d["mid"]}</div>')
        else:
            sx = "" if filled else "transform:scaleX(0);"
            rows.append(f'<div class="bar{" dk" if r[3] else ""}" style="top:{r[1]}px;width:{r[2]}%;transform-origin:0 50%;{sx}"></div>')
    if last_variants:
        last = "".join(f'<span id="{p}-l{i}-{v}" style="opacity:{1 if v == 0 else 0}">{t}</span>' for v, t in enumerate(d["last"]))
    else:
        last = f'<span>{d["last"][0]}</span>'
    ok = f'<div id="{p}-k{i}" class="ok" style="opacity:{1 if ok_on else 0}">✓</div>'
    return f'''<div id="{p}-d{i}" class="doc" style="left:{COLX[i]}px;top:{COLY}px;width:{COLW}px;height:{COLH}px">
        <div id="{p}-t{i}" class="dt">{d["title"]}</div>{ok}
        <div class="wm">[가상 문서 · 예시]</div>
        <div class="hd">{d["hd"]}</div>
        <div id="{p}-b{i}" class="body" style="height:724px">{"".join(rows)}<div class="last" style="left:0;right:0;top:644px">{last}</div></div>
        <div id="{p}-s{i}" class="sig" style="{sig_style}"><div class="lb">법률 검토·<br>책임자 서명:</div><div class="ul"></div><div id="{p}-c{i}" class="cur" style="opacity:0"></div></div>
      </div>'''


def ui_head(p, progress=False):
    right = (f'<span style="font-size:28px;font-weight:800;color:#6F8F7A;letter-spacing:-0.02em;white-space:nowrap">생성 중 <span id="{p}-pct">0</span>%</span>'
             if progress else f'<div class="sent">{SENT}</div>')
    return f'''<div class="ui-head"><span class="ui-icon">{ICON}</span><b>문서 도우미</b></div>
      <div class="ui-strip"><span class="q">법률 검토 문서 3건 작성</span>{right}</div>'''


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split(" "))


def chars(text, pid, acc_from=None):
    out = []
    for i, c in enumerate(text):
        style = ' style="color:var(--acc)"' if acc_from is not None and i >= acc_from else ""
        out.append(f'<span id="{pid}{i}" class="ch"{style}>{c}</span>')
    return "".join(out)


GL = '''<div id="@@-gl" class="full" style="opacity:0" data-layout-ignore>
      <div class="glitch" style="top:420px;height:46px;background:rgba(80,140,255,0.35)"></div>
      <div class="glitch" style="top:880px;height:22px;background:rgba(0,200,230,0.4)"></div>
      <div class="glitch" style="top:1210px;height:64px;background:rgba(255,255,255,0.3)"></div>
      <div class="glitch" style="top:1330px;height:14px;background:rgba(0,200,230,0.45)"></div>
    </div>'''
FLASH = '<div id="@@-flash" class="full" style="background:#ffffff;opacity:0" data-layout-ignore></div>'

# ---------------------------------------------------------------- anime.js helpers (absolute seconds)
HELPERS = r"""
    const tl = anime.createTimeline({ autoplay: false, defaults: { ease: "outExpo" } });
    const R = anime.createSeededRandom(__SEED__);
    const ms = (s) => Math.round(s * 1000);
    const FR = 1 / 30;
    // A: tween (props may be [from, to]); S: instant set; both at absolute video seconds
    function A(t, sel, props, dur, ease, extra) {
      tl.add(sel, Object.assign({ duration: Math.max(1, ms(dur == null ? 0.3 : dur)), ease: ease || "outExpo" }, props, extra || {}), ms(t));
    }
    function S(t, sel, props) { tl.set(sel, props, ms(t)); }
    // camera: point (px,py) lands at screen (cx,cy) at scale s (elements with class .cam use transform-origin 0 0)
    function camv(px, py, s, cx, cy) { return { translateX: (cx == null ? 490 : cx) - s * px, translateY: (cy == null ? 960 : cy) - s * py, scale: s }; }
    function CAM(t, sel, px, py, s, dur, ease, cx, cy) {
      const v = camv(px, py, s, cx, cy);
      if (!dur) S(t, sel, v); else A(t, sel, v, dur, ease || "inOutExpo");
    }
    // seeded camera shake on a wrapper (frames x amplitude px), returns to 0
    function SHAKE(t, sel, frames, amp) {
      for (let i = 0; i < frames; i++) {
        const a = amp * (1 - i / frames);
        S(t + i * FR, sel, { translateX: R(-a, a, 1), translateY: R(-a, a, 1), rotate: R(-a, a, 1) * 0.04 });
      }
      S(t + frames * FR, sel, { translateX: 0, translateY: 0, rotate: 0 });
    }
    // scale snap on a punch wrapper: hard jump to s, settles back on a long tail
    function PUNCH(t, sel, s, dur) { A(t, sel, { scale: [s, 1] }, dur || 0.35, "outExpo"); }
    // 1-frame flash
    function FLASH(t, sel, o) { S(t, sel, { opacity: o == null ? 1 : o }); S(t + FR, sel, { opacity: 0 }); }
    function GLITCH(t, cam, gl, dx) {
      S(t, cam, { translateX: dx }); S(t, gl, { opacity: 1 });
      S(t + FR, cam, { translateX: 0 }); S(t + FR, gl, { opacity: 0 });
    }
    // cursor blink: 8-frame on/off
    function BLINK(sel, t0, t1) { let on = true; for (let t = t0; t < t1 - 1e-6; t += 8 * FR) { S(t, sel, { opacity: on ? 1 : 0 }); on = !on; } }
    // word-level kinetic type: each word snaps in on its own time (scale + blur, no slide)
    function WORD(t, sel, s) {
      A(t, sel, { opacity: [0, 1], scale: [s || 1.4, 1], filter: ["blur(10px)", "blur(0px)"] }, 0.22, "outExpo");
    }
    function WORDS(t, sel, gap) {
      A(t, sel, { opacity: [0, 1], scale: [1.25, 1], filter: ["blur(10px)", "blur(0px)"] }, 0.2, "outExpo", { delay: anime.stagger(ms(gap || 0.08)) });
    }
    function OUT(t, sel, dur, extra) { A(t, sel, Object.assign({ opacity: 0, filter: "blur(8px)" }, extra || {}), dur || 0.14, "inQuad"); }
"""


def scene(cid, t0, t1, css, html, js, seed):
    s = f'''<template>
  <style>
{COMMON}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920"{" data-layout-ignore" if cid == "fx" else ""}>
{html}
  </div>
  <script>
  (function () {{
{HELPERS.replace("__SEED__", str(seed))}
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


SLOTS = []
CUTS = []  # (time, label) – picture cuts / hard accents for the beat audit

# ============================================================ HOOK  (C1 / C1')
# f0: ink stage, full headline + three fanned docs + '생성 완료 0.1s' (first frame complete).
# beats 1,2: hard punch-in cuts on the fan (headline stays). S2: whip tilt down to the three
# signature boxes; '딱 / 한 칸만 / 빼고.' snaps word by word on the beat; glitch + stop.
def build_hook(T):
    fan = []
    for i, (cx, cy, rot) in enumerate([(300, 1160, -8), (680, 1160, 8), (490, 1120, 0)]):
        di = [0, 2, 1][i]
        d = DOCS[di]
        bars = "".join(f'<div style="position:absolute;left:0;top:{j * 24}px;height:10px;border-radius:5px;width:{100 if j % 5 == 0 else 60 + (j * 37) % 40}%;background:{"#b9bec3" if j % 5 == 0 else "#d3d6d9"};transform-origin:0 50%"></div>'
                       for j in range(13))
        fan.append(f'''<div id="h-f{di}" class="abs" style="left:{cx - 190}px;top:{cy - 280}px;width:380px;height:560px;z-index:{2 if di == 1 else 1}">
        <div class="full" style="transform:rotate({rot}deg);background:#fff;border:2px solid #ddd8cc;border-radius:18px;box-shadow:0 30px 70px rgba(0,0,0,0.55)">
          <div class="abs" style="left:22px;top:20px;font-size:30px;font-weight:800;color:#22262B;white-space:nowrap">{d["title"]}</div>
          <div class="abs" style="left:20px;top:70px;padding:3px 10px;border-radius:8px;background:#e7eee9;color:#47604f;font-size:22px;font-weight:700;white-space:nowrap">[가상 문서 · 예시]</div>
          <div class="abs" style="left:22px;top:118px;font-size:24px;font-weight:800;color:#22262B">{d["hd"]}</div>
          <div class="abs" style="left:22px;right:22px;top:162px;height:300px">{bars}</div>
          <div id="h-fs{di}" class="abs" style="left:14px;right:14px;top:478px;height:62px;border-radius:10px;background:#eeece6"></div>
          <div class="abs" style="left:26px;top:494px;font-size:21px;font-weight:800;color:#6b7076;white-space:nowrap">법률 검토·책임자 서명: ____</div>
        </div>
      </div>''')
    css = """
    #h-bg { background: radial-gradient(70% 45% at 50% 62%, #1d2733 0%, #0e1218 60%, #08090c 100%); }
    #h-chip { position: absolute; left: 600px; top: 760px; height: 54px; padding: 0 22px; border-radius: 999px; background: var(--sage); color: #fff; font-size: 30px; font-weight: 800; display: flex; align-items: center; letter-spacing: -0.02em; white-space: nowrap; }
    #h-head { top: 250px; font-size: 132px; line-height: 1.08; color: #ffffff; text-shadow: 0 10px 40px rgba(0, 0, 0, 0.6); }
    #h-head .w, #h-cap .w { display: inline-block; }
    #h-cap { top: 250px; font-size: 118px; line-height: 1.08; color: #ffffff; text-shadow: 0 10px 40px rgba(0, 0, 0, 0.7); }
    #h-cap .w { opacity: 0; }
    #h-cap .hot { color: var(--gold-light); }
    #h-grid { opacity: 1; }
    #h-dim { background: #000; opacity: 0; }
    #h-band { background: linear-gradient(180deg, rgba(8, 9, 12, 0.97) 0px, rgba(8, 9, 12, 0.93) 560px, rgba(8, 9, 12, 0) 780px); opacity: 0; }
"""
    grid_final = dict(px=490, py=SIG_Y - 60, s=1.12, cy=1180)
    html = f'''    <div id="h-bg" class="full" data-layout-ignore></div>
    <div id="h-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="h-punch" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
        <div id="h-fanw" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
          <div class="abs" style="left:0;top:330px;width:1080px;height:200px">{ui_head("h")}</div>
          <div id="h-chip">생성 완료 0.1s</div>
          {"".join(fan)}
        </div>
        <div id="h-grid" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
          {doc(0, "h")}{doc(1, "h")}{doc(2, "h")}
        </div>
      </div>
    </div>
    <div id="h-dim" class="full" data-layout-ignore></div>
    <div id="h-band" class="full" data-layout-ignore></div>
    <div id="h-head" class="col cap">{words("AI가")}<br>{words("다 써줍니다.")}</div>
    <div id="h-cap" class="col cap"><span id="h-w0" class="w hot">딱</span> <span id="h-w1" class="w">한 칸만</span><br><span id="h-w2" class="w">빼고.</span></div>
    {GL.replace("@@", "h")}
    {FLASH.replace("@@", "h")}'''
    # the grid starts far below (off screen) at its final scale; the whip brings it up
    g = grid_final
    js = f"""
    const T = {J(T)};
    const G = camv({g["px"]}, {g["py"]}, {g["s"]}, 490, {g["cy"]});
    S(0, "#h-grid", Object.assign({{}}, G, {{ translateY: G.translateY + 1900 }}));
    CAM(0, "#h-fanw", 490, 960, 1, 0);
    CAM(0, "#h-punch", 490, 960, 1, 0);
    // f0: complete frame; micro shake on the downbeat + fan bounce
    SHAKE(0, "#h-shake", 4, 9);
    A(0, ["#h-f0", "#h-f2", "#h-f1"], {{ translateY: [-26, 0] }}, 0.5, anime.spring({{ bounce: 0.55, duration: 450 }}), {{ delay: anime.stagger(50) }});
    A(0.05, "#h-chip", {{ scale: [1.25, 1] }}, 0.35, "outBack(3)");
    // beat 1 / 2: hard punch-in cuts on doc titles (headline holds above)
    CAM(T.p1, "#h-punch", 300, 1000, 1.55, 0, null, 330, 1180);
    CAM(T.p2, "#h-punch", 680, 1000, 1.55, 0, null, 650, 1180);
    PUNCH(T.p1, "#h-shake", 1.06, 0.3); PUNCH(T.p2, "#h-shake", 1.06, 0.3);
    // S2: headline out, whip down to the signature boxes (one move, blur at its fastest)
    OUT(T.s2, "#h-head .w", 0.12, {{ translateY: -120 }});
    S(T.s2, "#h-punch", camv(490, 960, 1));
    A(T.s2, "#h-fanw", {{ translateY: -2100 }}, 0.4, "outExpo");
    A(T.s2, "#h-grid", {{ translateY: G.translateY }}, 0.42, "outExpo");
    A(T.s2, "#h-punch", {{ filter: ["blur(16px)", "blur(0px)"] }}, 0.3, "outQuad");
    A(T.s2, "#h-band", {{ opacity: [0, 1] }}, 0.3, "outQuad");
    WORD(T.w0, "#h-w0", 1.8); PUNCH(T.w0, "#h-shake", 1.05, 0.3);
    WORD(T.w1, "#h-w1", 1.5); PUNCH(T.w1, "#h-shake", 1.04, 0.3);
    WORD(T.w2, "#h-w2", 1.5); PUNCH(T.w2, "#h-shake", 1.04, 0.3);
    A(T.w0, ["#h-s0", "#h-s1", "#h-s2"], {{ backgroundColor: ["#eeece6", "#dbe9de"] }}, 0.3, "outQuad");
    ["#h-c0", "#h-c1", "#h-c2"].forEach((c) => BLINK(c, T.w0, T.end));
    // slow push while the words land (no frame holds still)
    A(T.s2 + 0.42, "#h-grid", {{ scale: [{g["s"]}, {g["s"] * 1.06}], translateX: [G.translateX, 490 - {g["s"] * 1.06} * 490], translateY: [G.translateY, {g["cy"]} - {g["s"] * 1.06} * {g["py"]}] }}, T.end - T.s2 - 0.42, "linear");
    // stop: glitch 2 frames, dim, then hard cut
    GLITCH(T.gl, "#h-shake", "#h-gl", 26);
    GLITCH(T.gl + 2 * FR, "#h-shake", "#h-gl", -18);
    A(T.gl + 3 * FR, "#h-dim", {{ opacity: [0, 0.45] }}, T.end - T.gl - 3 * FR, "inQuad");
"""
    return css, html, js


# ============================================================ FILL (C2)
def build_fill(T):
    css = """
    #f-bg { background: radial-gradient(70% 45% at 50% 55%, #1d2733 0%, #0e1218 60%, #08090c 100%); }
    #f-bar { position: absolute; left: 60px; top: 398px; width: 860px; height: 8px; border-radius: 4px; background: #2a3038; overflow: hidden; }
    #f-bar i { position: absolute; inset: 0; background: var(--sage); transform-origin: 0 50%; transform: scaleX(0); }
    #f-cam .ui-head b { color: #f4f1ea; }
"""
    html = f'''    <div id="f-bg" class="full" data-layout-ignore></div>
    <div id="f-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="f-cam" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
        {ui_head("f", progress=True)}
        <div id="f-bar"><i id="f-bari"></i></div>
        {doc(0, "f", ok_on=False, filled=False)}{doc(1, "f", ok_on=False, filled=False)}{doc(2, "f", ok_on=False, filled=False)}
      </div>
    </div>
    {FLASH.replace("@@", "f")}'''
    cx = [COLX[i] + COLW / 2 for i in range(3)]
    js = f"""
    const T = {J(T)};
    FLASH(T.c0, "#f-flash");
    // micro-cuts, one beat each: column 1 / 2 / 3 close (title + filling body), then the wide
    const CX = {J(cx)};
    [T.c0, T.c1, T.c2].forEach((t, i) => {{
      CAM(t, "#f-cam", CX[i], 720, 2.15, 0, null, 490, 900);
      A(t, "#f-cam", {{ translateY: "-=120" }}, T.c1 - T.c0, "linear");
      SHAKE(t, "#f-shake", 3, 8);
      A(t, "#f-b" + i + " .bar", {{ scaleX: [0, 1] }}, 0.18, "outExpo", {{ delay: anime.stagger(22) }});
    }});
    CAM(T.wide, "#f-cam", 490, 960, 1.18, 0, null, 490, 900);
    A(T.wide, "#f-cam", camv(490, 960, 1, 490, 960), T.end - T.wide, "outQuart");
    SHAKE(T.wide, "#f-shake", 3, 10);
    // progress count-up (innerHTML tween) and bar
    A(T.c0, "#f-pct", {{ innerHTML: [0, 50] }}, T.wide - T.c0, "inQuad", {{ modifier: (v) => Math.round(v) }});
    A(T.wide, "#f-pct", {{ innerHTML: [50, 99] }}, T.k2 - T.wide, "outQuad", {{ modifier: (v) => Math.round(v) }});
    A(T.c0, "#f-bari", {{ scaleX: [0, 0.5] }}, T.wide - T.c0, "inQuad");
    A(T.wide, "#f-bari", {{ scaleX: [0.5, 0.99] }}, T.k2 - T.wide, "outQuad");
    // checks spring-pop on the beat
    [T.k0, T.k1, T.k2].forEach((t, i) => {{
      A(t, "#f-k" + i, {{ opacity: [0, 1], scale: [0.2, 1] }}, 0.5, anime.spring({{ bounce: 0.6, duration: 380 }}));
      PUNCH(t, "#f-shake", 1.025, 0.25);
    }});
    // grey signature boxes stay empty: pulse them on the last beat
    A(T.k2, ["#f-s0", "#f-s1", "#f-s2"], {{ backgroundColor: ["#eeece6", "#d9d6cf"] }}, 0.3, "outQuad");
"""
    return css, html, js


# ============================================================ BLANK (C3 / C3')
def build_blank(T, cap_split=True, hold_cap=None):
    css = """
    #b-bg { background: radial-gradient(70% 45% at 50% 60%, #1d2733 0%, #0e1218 60%, #08090c 100%); }
    #b-cam .ui-head b { color: #f4f1ea; }
    #b-cap { top: 250px; font-size: 118px; line-height: 1.08; color: #ffffff; text-shadow: 0 10px 40px rgba(0, 0, 0, 0.7); }
    #b-cap .w { display: inline-block; opacity: 0; }
    #b-cap .hot { color: var(--gold-light); }
    #b-btn { position: absolute; left: 330px; top: 1500px; width: 320px; height: 108px; border-radius: 26px; background: #f4f1ea; color: #22262b; font-size: 46px; font-weight: 900; display: flex; align-items: center; justify-content: center; letter-spacing: -0.02em; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5); opacity: 0; }
    #b-ptr { position: absolute; left: 520px; top: 1555px; width: 96px; height: 116px; opacity: 0; }
    #b-toast { position: absolute; left: 90px; top: 700px; width: 800px; height: 120px; border-radius: 26px; background: #d93a2f; color: #fff; display: flex; align-items: center; justify-content: center; gap: 18px; font-size: 42px; font-weight: 900; letter-spacing: -0.03em; box-shadow: 0 24px 60px rgba(217, 58, 47, 0.45); opacity: 0; white-space: nowrap; }
    #b-toast i { width: 50px; height: 50px; border-radius: 50%; background: #fff; color: #d93a2f; font-style: normal; font-size: 34px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
    #b-band { background: linear-gradient(180deg, rgba(8, 9, 12, 0.97) 0px, rgba(8, 9, 12, 0.93) 560px, rgba(8, 9, 12, 0) 780px); opacity: 0; }
    #b-vig { background: radial-gradient(ellipse 60% 34% at 50% 52%, rgba(6, 7, 9, 0) 25%, rgba(6, 7, 9, 0.94) 100%); opacity: 0; }
"""
    cap = (f'<span id="b-w0" class="w hot">딱</span> <span id="b-w1" class="w">한 칸만</span><br><span id="b-w2" class="w">빼고.</span>')
    html = f'''    <div id="b-bg" class="full" data-layout-ignore></div>
    <div id="b-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="b-cam" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
        {ui_head("b")}
        {doc(0, "b", last_variants=True)}{doc(1, "b", last_variants=True)}{doc(2, "b", last_variants=True)}
      </div>
    </div>
    <div id="b-band" class="full" data-layout-ignore></div>
    <div id="b-vig" class="full" data-layout-ignore></div>
    <div id="b-cap" class="col cap">{cap}</div>
    <div id="b-btn">생성</div>
    <div id="b-ptr" data-layout-ignore>{HAND_PTR}</div>
    <div id="b-toast"><i>!</i>이 항목은 생성할 수 없습니다.</div>
    {GL.replace("@@", "b")}
    {FLASH.replace("@@", "b")}'''
    js = f"""
    const T = {J(T)};
    const GS = 1.12, GY = {SIG_Y - 60};
    // open: either from the wide (30s) or already on the signature boxes (15s)
    if (T.fromWide) {{
      FLASH(T.c0, "#b-flash", 0.85);
      CAM(T.c0, "#b-cam", 490, 960, 1, 0);
      CAM(T.tilt, "#b-cam", 490, GY, GS, 0.45, "outExpo", 490, 1180);
      A(T.tilt, "#b-cam", {{ filter: ["blur(14px)", "blur(0px)"] }}, 0.3, "outQuad");
    }} else {{
      CAM(T.c0, "#b-cam", 490, GY, GS, 0, null, 490, 1180);
    }}
    A(T.c0, ["#b-s0", "#b-s1", "#b-s2"], {{ backgroundColor: ["#dbe9de", "#dbe9de"] }}, 0.1);
    ["#b-c0", "#b-c1", "#b-c2"].forEach((c) => BLINK(c, T.c0, T.end));
    // caption: word by word on the beat, on an ink band (docs pass under it)
    A(T.w0 != null ? T.w0 : T.c0, "#b-band", {{ opacity: [0, 1] }}, 0.25, "outQuad");
    if (T.w0 != null) {{ WORD(T.w0, "#b-w0", 1.8); PUNCH(T.w0, "#b-shake", 1.05); }}
    if (T.w1 != null) WORD(T.w1, "#b-w1", 1.5);
    if (T.w2 != null) {{ WORD(T.w2, "#b-w2", 1.5); PUNCH(T.w2, "#b-shake", 1.04); }}
    if (T.wAll != null) S(T.wAll, "#b-cap .w", {{ opacity: 1, scale: 1, filter: "blur(0px)" }});
    // '생성' button + pointer, clicks on the beat: text above rerolls, signature stays empty
    A(T.btn, "#b-btn", {{ opacity: [0, 1], translateY: [60, 0], scale: [0.8, 1] }}, 0.5, anime.spring({{ bounce: 0.45, duration: 420 }}));
    A(T.btn, "#b-ptr", {{ opacity: [0, 1], translateX: [160, 0], translateY: [180, 0] }}, 0.25, "outExpo");
    T.clicks.forEach((t, k) => {{
      A(t, "#b-ptr", {{ scale: [0.82, 1] }}, 0.16, "outQuad");
      A(t, "#b-btn", {{ scale: [0.9, 1], backgroundColor: ["#6F8F7A", "#f4f1ea"] }}, 0.18, "outQuad");
      GLITCH(t, "#b-shake", "#b-gl", k % 2 ? -22 : 22);
      [0, 1, 2].forEach((i) => {{ S(t, "#b-l" + i + "-" + k, {{ opacity: 0 }}); S(t, "#b-l" + i + "-" + (k + 1), {{ opacity: 1 }}); }});
      A(t, ["#b-s0", "#b-s1", "#b-s2"], {{ backgroundColor: ["#f2c9c4", "#dbe9de"] }}, 0.2, "outQuad");
    }});
    // toast (the only red in the film): slam + shake
    if (T.capOut != null) {{ OUT(T.capOut, "#b-cap .w", 0.14, {{ translateY: -60 }}); A(T.capOut, "#b-band", {{ opacity: 0 }}, 0.3, "outQuad"); }}
    OUT(T.toast, ["#b-btn", "#b-ptr"], 0.14, {{ translateY: 40 }});
    A(T.toast, "#b-toast", {{ opacity: [0, 1], scale: [1.35, 1] }}, 0.3, "outExpo");
    SHAKE(T.toast, "#b-shake", 6, 18);
    A(T.toast + 2 * FR, "#b-toast", {{ translateX: [12, 0] }}, 0.25, anime.spring({{ bounce: 0.7, duration: 250 }}));
    // push in to one signature line, everything else falls into the dark
    CAM(T.push, "#b-cam", 490, {SIG_Y - 20}, 2.5, T.end - T.push, "inOutQuart", 490, 1030);
    A(T.push, "#b-toast", {{ translateY: [0, -90], scale: [1, 0.92] }}, T.end - T.push, "inOutQuart");
    A(T.push, "#b-vig", {{ opacity: [0, 1] }}, T.end - T.push, "inOutQuad");
"""
    return css, html, js


# ============================================================ DUST (C4 / C4' + bridge)
prng = random.Random(42)
PTS = []
for i in range(3):
    for _ in range(120):
        x = COLX[i] + 18 + prng.random() * (COLW - 36)
        y = COLY + 156 + prng.random() * 724
        PTS.append((x, y, prng.randint(5, 11)))
    for _ in range(14):
        PTS.append((COLX[i] + 18 + prng.random() * (COLW - 60), COLY + 14 + prng.random() * 130, prng.randint(3, 7)))


def build_dust(T, c1, c2, bridge=None):
    er = random.Random(7)
    EMB = "".join(f'<i style="left:{er.randint(60, 1000)}px;top:{er.randint(900, 1900)}px;width:{er.randint(3, 7)}px;height:{er.randint(3, 7)}px"></i>' for _ in range(46))
    pts_html = "".join(f'<i style="left:{x:.0f}px;top:{y:.0f}px;width:{s}px;height:{s}px"></i>' for (x, y, s) in PTS)
    css = """
    #d-bg { background: radial-gradient(70% 45% at 50% 60%, #1d2733 0%, #0e1218 60%, #08090c 100%); }
    #d-dark { background: radial-gradient(60% 40% at 50% 52%, #15181d, #050608 100%); opacity: 0; }
    #d-emb i { position: absolute; border-radius: 50%; background: #e0c27e; opacity: 0; }
    #d-pts i { position: absolute; border-radius: 50%; background: #c9cdd2; opacity: 0; }
    #d-c1 { top: 270px; font-size: 60px; font-weight: 800; color: #cfd3d8; }
    #d-c2 { top: 360px; font-size: 104px; line-height: 1.12; color: #ffffff; }
    #d-c1 .w, #d-c2 .w, #d-br .w { display: inline-block; opacity: 0; }
    #d-br { top: 1180px; font-size: 76px; line-height: 1.15; color: var(--gold-light); }
    #d-hlb { position: absolute; left: 140px; top: 850px; width: 700px; text-align: center; font-size: 48px; font-weight: 800; color: #f4f1ea; opacity: 0; }
    #d-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    #d-cur { position: absolute; left: 146px; top: 904px; width: 5px; height: 46px; background: #f4f1ea; opacity: 0; }
"""
    br = (f'<div id="d-br" class="col cap">{words(bridge[0])}<br>{words(bridge[1])}</div>' if bridge else "")
    html = f'''    <div id="d-bg" class="full" data-layout-ignore></div>
    <div id="d-dark" class="full" data-layout-ignore></div>
    <div id="d-push" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="d-page" class="full" data-layout-allow-overlap data-layout-allow-overflow>
        {doc(0, "d", sig_style="background:#dbe9de")}{doc(1, "d", sig_style="background:#dbe9de")}{doc(2, "d", sig_style="background:#dbe9de")}
      </div>
      <div id="d-pts" class="full" data-layout-ignore>{pts_html}</div>
      <div id="d-emb" class="full" data-layout-ignore>{EMB}</div>
      <div id="d-hlb">법률 검토·책임자 서명:</div>
      <svg id="d-svg" viewBox="0 0 1080 1920" data-layout-ignore>
        <path id="d-glow" d="M140 962 L840 962" stroke="#e0c27e" stroke-width="16" stroke-linecap="round" fill="none" stroke-opacity="0.35" style="filter:blur(8px);opacity:0"/>
        <path id="d-ul" d="M140 962 L840 962" stroke="#f4f1ea" stroke-width="5" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      <div id="d-cur"></div>
    </div>
    <div id="d-c1" class="col">{words(c1)}</div>
    <div id="d-c2" class="col cap">{words(c2[0])}<br>{words(c2[1])}</div>
    {br}'''
    js = f"""
    const T = {J(T)};
    CAM(T.c0, "#d-push", 490, 960, 1, 0);
    // S1: everything but the signature turns to dust and lifts, ground goes ink (seeded)
    WORDS(T.c0, "#d-c1 .w", 0.09);
    const pe = document.querySelectorAll("#d-pts i");
    pe.forEach((el) => {{
      const y = parseFloat(el.style.top);
      const t = T.c0 + 0.05 + Math.max(0, Math.min(1, ({COLY + 900} - y) / 900)) * 0.9 + R(0, 0.1, 3);
      A(t, el, {{ opacity: [0, 0.95] }}, 0.05, "linear");
      A(t + 0.05, el, {{ opacity: [0.95, 0], translateX: R(-90, 90, 0), translateY: -R(260, 820, 0) }}, R(0.9, 1.5, 2), "outQuad");
    }});
    [0, 1, 2].forEach((i) => A(T.c0 + 0.05, "#d-b" + i, {{ clipPath: ["inset(0% 0% 0% 0%)", "inset(0% 0% 100% 0%)"] }}, 0.95, "inQuad"));
    A(T.c0 + 0.85, ["#d-d0", "#d-d1", "#d-d2"], {{ opacity: [1, 0] }}, 0.35, "inQuad");
    A(T.c0 + 0.2, "#d-dark", {{ opacity: [0, 1] }}, 1.0, "inOutQuad");
    // the one line left: label + white underline drawn, glow, cursor
    A(T.c0 + 1.0, "#d-hlb", {{ opacity: [0, 1], filter: ["blur(10px)", "blur(0px)"] }}, 0.3, "outQuad");
    S(T.c0 + 1.0, "#d-ul", {{ opacity: 1 }});
    A(T.c0 + 1.0, anime.svg.createDrawable("#d-ul"), {{ draw: ["0 0", "0 1"] }}, 0.55, "inOutQuart");
    BLINK("#d-cur", T.c0 + 1.5, T.end);
    // S2 on the beat: second line word by word, glow draws, slow push (100→108%)
    OUT(T.s2, "#d-c1 .w", 0.2, {{ opacity: 0.45, filter: "blur(0px)" }});
    WORDS(T.s2, "#d-c2 .w", 0.1);
    S(T.s2, "#d-glow", {{ opacity: 1 }});
    A(T.s2, anime.svg.createDrawable("#d-glow"), {{ draw: ["0.5 0.5", "0 1"] }}, 0.9, "outQuad");
    A(T.c0 + 1.0, "#d-push", camv(490, 960, 1.14), T.end - T.c0 - 1.0, "linear");
    // embers keep rising through the stillness (seeded speeds/drift)
    document.querySelectorAll("#d-emb i").forEach((el) => {{
      const d = T.end - T.c0 - 1.0;
      A(T.c0 + 1.0, el, {{ opacity: [0, R(0.35, 0.8, 2), 0], translateY: [0, -R(500, 1300, 0)], translateX: [0, R(-60, 60, 0)] }}, d, "linear");
    }});
    if (T.br != null) {{
      OUT(T.br, ["#d-c1 .w", "#d-c2 .w"], 0.16);
      WORDS(T.br, "#d-br .w", 0.1);
    }}
"""
    return css, html, js


# ============================================================ DESK (C5)
def build_desk(T):
    sheets = []
    for k, (dx, dy, r) in enumerate([(-18, 22, -4), (14, 12, 3), (-6, 4, -1.5), (0, 0, 0.8)]):
        inner = ""
        if k == 3:
            inner = "".join(
                f'<div style="position:absolute;left:40px;top:{40 + j * 92}px;font-size:26px;font-weight:800;color:#8b857a">제{j + 1}조</div>'
                + "".join(f'<div style="position:absolute;left:130px;top:{50 + j * 92 + m * 22}px;height:9px;border-radius:5px;width:{300 - m * 60 - (j * 23) % 50}px;background:#cfc8bb"></div>' for m in range(3))
                for j in range(4))
        sheets.append(f'<div style="position:absolute;left:{dx}px;top:{dy}px;width:560px;height:400px;background:#f4efe4;border:1px solid #d7cfbf;border-radius:4px;transform:rotate({r}deg);box-shadow:0 6px 14px rgba(40,25,10,0.25)">{inner}</div>')
    css = """
    #k-ink { background: #07080a; }
    #k-c1 { top: 270px; font-size: 64px; font-weight: 800; color: #e9e3d6; }
    #k-c2 { top: 360px; font-size: 104px; line-height: 1.12; color: #ffffff; text-shadow: 0 8px 40px rgba(0, 0, 0, 0.7); }
    #k-c1 .w, #k-c2 .w { display: inline-block; opacity: 0; }
    #k-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #k-desk { opacity: 0; }
    .k-wall { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; background: radial-gradient(55% 45% at 88% 18%, rgba(255, 226, 180, 0.18), rgba(255, 226, 180, 0) 100%), linear-gradient(180deg, #0c0b0a 0%, #1d1915 70%, #2a231c 100%); }
    .k-win { position: absolute; left: 760px; top: 90px; width: 300px; height: 560px; border: 10px solid #0e0c0a; background: linear-gradient(160deg, rgba(255, 238, 205, 0.4), rgba(255, 220, 170, 0.14)); }
    .k-win::before { content: ""; position: absolute; left: 50%; top: 0; bottom: 0; width: 10px; margin-left: -5px; background: #0e0c0a; }
    .k-win::after { content: ""; position: absolute; top: 50%; left: 0; right: 0; height: 10px; margin-top: -5px; background: #0e0c0a; }
    .k-beam { position: absolute; width: 220px; height: 1500px; background: linear-gradient(180deg, rgba(255, 228, 180, 0.22), rgba(255, 228, 180, 0)); filter: blur(22px); transform-origin: 50% 0; }
    .k-top { position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; background: repeating-linear-gradient(177deg, rgba(0, 0, 0, 0.08) 0 3px, rgba(0, 0, 0, 0) 3px 26px), linear-gradient(180deg, #7d5a3d 0%, #573c27 45%, #2a1c12 100%); }
    .k-edge { position: absolute; left: 0; top: 957px; width: 1080px; height: 5px; background: linear-gradient(90deg, rgba(255, 214, 160, 0.35), rgba(255, 224, 176, 0.85) 70%, rgba(255, 214, 160, 0.5)); }
    .k-patch { position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; background: rgba(255, 222, 170, 0.14); clip-path: polygon(52% 0, 100% 0, 78% 100%, 18% 100%); filter: blur(10px); }
    #k-papers { position: absolute; left: 210px; top: 1080px; width: 560px; height: 420px; }
    #k-pen { position: absolute; left: 330px; top: 1120px; width: 420px; height: 160px; filter: blur(5px); }
    #k-dim { background: #000; opacity: 0; }
"""
    html = f'''    <div id="k-ink" class="full" data-layout-ignore></div>
    <div id="k-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
    <div id="k-desk" class="full" data-layout-ignore>
      <div id="k-dolly" class="full cam">
        <div class="k-wall"></div>
        <div class="k-win"></div>
        <div class="k-beam" style="left:720px;top:120px;transform:rotate(32deg)"></div>
        <div class="k-beam" style="left:880px;top:160px;transform:rotate(30deg);width:150px"></div>
        <div class="k-top"></div>
        <div class="k-patch"></div>
        <div class="k-edge"></div>
        <div id="k-papers"><div class="full" style="transform:perspective(1400px) rotateX(34deg);transform-origin:50% 100%">{"".join(sheets)}</div></div>
        <div id="k-pen"><svg viewBox="0 0 420 160" width="420" height="160"><g transform="rotate(-14 210 80)">
          <ellipse cx="214" cy="112" rx="190" ry="14" fill="rgba(30,18,8,0.35)"/>
          <rect x="70" y="66" width="300" height="30" rx="15" fill="#151515"/>
          <rect x="300" y="66" width="12" height="30" fill="#B8955A"/>
          <rect x="250" y="62" width="110" height="8" rx="4" fill="#B8955A"/>
          <path d="M70 70 L20 81 L70 92 Z" fill="#C9A666"/>
          <rect x="90" y="70" width="200" height="6" rx="3" fill="rgba(255,255,255,0.18)"/>
        </g></svg></div>
      </div>
    </div>
    </div>
    <svg id="k-svg" viewBox="0 0 1080 1920" data-layout-ignore>
      <path id="k-glow" d="M0 962 L1080 962" stroke="#e0c27e" stroke-width="18" stroke-linecap="round" fill="none" opacity="0.4" style="filter:blur(8px)"/>
      <path id="k-line" d="M0 962 L1080 962" stroke="#fff3dc" stroke-width="5" fill="none"/>
    </svg>
    <div id="k-dim" class="full" data-layout-ignore></div>
    <div id="k-c1" class="col">{words("그 자리엔 언제나")}</div>
    <div id="k-c2" class="col cap">{words("법을 아는 사람이")}<br>{words("있었습니다.")}</div>'''
    js = f"""
    const T = {J(T)};
    // S1: the signature underline (centre 140–840) stretches to the full frame width = the desk edge
    const dl = anime.svg.createDrawable("#k-line"), dg = anime.svg.createDrawable("#k-glow");
    S(T.c0, [dl, dg], {{ draw: "0.13 0.78" }});
    A(T.c0 + 0.1, [dl, dg], {{ draw: ["0.13 0.78", "0 1"] }}, T.s2 - T.c0 - 0.1, "inOutQuart");
    WORDS(T.c0, "#k-c1 .w", 0.1);
    // match cut on the beat: desk fades up under the line, line becomes the desk edge
    A(T.s2, "#k-desk", {{ opacity: [0.15, 1] }}, 0.12, "outQuad");
    A(T.s2, "#k-svg", {{ opacity: [1, 0] }}, 0.2, "outQuad");
    CAM(T.c0, "#k-dolly", 490, 962, 1, 0, null, 490, 962);
    A(T.s2, "#k-dolly", camv(490, 1150, 1.1, 490, 1150), T.end - T.s2, "linear");
    A(T.s2, "#k-c1 .w", {{ opacity: 0.55 }}, 0.3, "outQuad");
    WORDS(T.s2, "#k-c2 .w", 0.1);
    // rack focus papers -> pen
    A(T.s2 + 0.3, "#k-papers", {{ filter: ["blur(0px)", "blur(6px)"] }}, 1.3, "inOutQuad");
    A(T.s2 + 0.3, "#k-pen", {{ filter: ["blur(5px)", "blur(0px)"] }}, 1.3, "inOutQuad");
    // build: the track drops to a breath, then the camera steps in on every beat into the drop
    A(T.dip, "#k-dim", {{ opacity: [0, 0.5, 0] }}, T.b1 - T.dip, "inOutSine");
    [T.b1, T.b2, T.b3].forEach((t, i) => {{ PUNCH(t, "#k-shake", 1.03 + i * 0.02, 0.4); SHAKE(t, "#k-shake", 2, 4 + i * 3); }});
"""
    return css, html, js


# ============================================================ SIGN (C6 / C6')
OLD = "법률 검토·책임자 서명"
NEW = "그 칸으로 가는 첫 계단"


def build_sign(T, compact=False):
    css = """
    #s-paper { background: radial-gradient(70% 45% at 30% 58%, #fffaf0 0%, #ece3d2 70%, #cfc2aa 100%); }
    #s-ul { position: absolute; left: 120px; top: 998px; width: 740px; height: 4px; background: #2b2b2b; }
    #s-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    #s-pen { position: absolute; left: 136px; top: 414px; width: 640px; height: 640px; }
    #s-lb { top: 1036px; font-size: 56px; font-weight: 800; color: #2b2b2b; }
    #s-nl { top: 1032px; font-size: 64px; font-weight: 900; color: var(--ink); --acc: var(--gold-text); }
    #s-nl .ch { opacity: 0; }
    #s-navy { background: linear-gradient(180deg, rgba(11, 26, 51, 0.97) 0%, rgba(11, 26, 51, 0.94) 58%, rgba(11, 26, 51, 0.82) 100%); opacity: 0; }
    #s-base { position: absolute; left: 230px; top: 568px; width: 520px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); box-shadow: 0 0 18px rgba(224, 194, 126, 0.6); opacity: 0; transform-origin: 50% 50%; }
    #s-u1 { top: 604px; font-size: 50px; font-weight: 800; color: var(--gold-light); }
    #s-u2 { top: 668px; font-size: 92px; font-weight: 900; color: #ffffff; letter-spacing: -0.05em; }
    #s-u2 span { background: linear-gradient(100deg, #ffffff 40%, #ffe6b0 50%, #ffffff 60%) 0 0 / 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; }
    #s-u3 { top: 790px; font-size: 40px; font-weight: 600; color: rgba(255, 255, 255, 0.92); }
    #s-br { top: 872px; display: flex; justify-content: center; align-items: center; gap: 14px; font-size: 40px; font-weight: 800; color: var(--gold-light); }
    #s-br img { width: 52px; height: 58px; }
    #s-u1, #s-u2, #s-u3, #s-br { opacity: 0; }
    #s-tip { transform-box: fill-box; transform-origin: center; }
    #s-dim { background: radial-gradient(60% 40% at 30% 52%, rgba(0,0,0,0), rgba(0,0,0,0.6)); }
"""
    if compact:  # 15s: one-line USP stack (spec C6' S3 MASTER)
        css += """
    #s-u1 { top: 620px; font-size: 54px; }
    #s-u2 { top: 690px; font-size: 76px; }
    #s-u3 { top: 790px; font-size: 44px; font-weight: 700; }
"""
        usp = f'''<div id="s-u1" class="col">국내 유일*</div>
    <div id="s-u2" class="col"><span>100% 온라인 법학사</span></div>
    <div id="s-u3" class="col">교육부장관 명의</div>'''
    else:
        usp = f'''<div id="s-u1" class="col">국내 유일*</div>
    <div id="s-u2" class="col"><span>100% 온라인 법학사</span></div>
    <div id="s-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>'''
    # ink: a slightly living hand-drawn stroke along the line, tip starts at x=150
    ink = "M150 999 C 260 995, 330 1004, 430 998 S 640 993, 740 1000 S 830 1002, 860 998"
    html = f'''    <div id="s-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
    <div id="s-world" class="full cam" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="s-paper" class="full" data-layout-ignore></div>
      <div id="s-ul" data-layout-ignore></div>
      <svg id="s-svg" viewBox="0 0 1080 1920" data-layout-ignore>
        <path id="s-inkg" d="{ink}" stroke="#e0c27e" stroke-width="22" stroke-linecap="round" fill="none" stroke-opacity="0.5" style="filter:blur(9px);opacity:0"/>
        <path id="s-ink" d="{ink}" stroke="#c49a4e" stroke-width="8" stroke-linecap="round" fill="none" style="opacity:0"/>
      </svg>
      <div id="s-pen" data-layout-ignore>{PEN_HAND.replace("@@", "s")}</div>
      <div id="s-dim" class="full" data-layout-ignore></div>
    </div>
    </div>
    <div id="s-lb" class="col">{chars(OLD, "s-o")}</div>
    <div id="s-navy" class="full" data-layout-ignore></div>
    <div id="s-base" data-layout-ignore></div>
    <div id="s-nl" class="col" data-layout-allow-overlap data-layout-allow-overflow>{chars(NEW, "s-n", acc_from=NEW.index("첫"))}</div>
    {usp}
    <div id="s-br" class="col">{MARK}경찰복지사이버평생교육원</div>
    {FLASH.replace("@@", "s")}'''
    js = f"""
    const T = {J(T)};
    const OLDN = {len(OLD)}, NEWN = {len(NEW)};
    CAM(T.c0, "#s-world", 200, 1000, 1, 0, null, 200, 1000);
    S(T.c0, ["#s-ink", "#s-inkg"].map((s) => anime.svg.createDrawable(s)), {{ draw: "0 0" }});
    // S1: pen comes in fast, then creeps the last centimetre (slow motion) while the build rises
    A(T.c0, "#s-pen", {{ translateX: [190, 0], translateY: [-280, -60], opacity: [0, 1] }}, 0.45, "outExpo");
    A(T.c0 + 0.45, "#s-pen", {{ translateY: [-60, -8] }}, T.hit - T.c0 - 0.45 - 0.08, "inOutSine");
    A(T.c0, "#s-world", camv(200, 1000, 1.18, 200, 1000), T.hit - T.c0, "inQuad");
    A(T.c0, "#s-dim", {{ opacity: [0.2, 1] }}, T.hit - T.c0, "inQuad");
    (T.tense || []).forEach((t, i) => SHAKE(t, "#s-shake", 2, 2 + i * 2));
    // HIT: nib touches = the music's biggest hit. 1-frame white, scale snap, shake, glow
    A(T.hit - 0.08, "#s-pen", {{ translateY: [-8, 0] }}, 0.08, "inQuad");
    FLASH(T.hit, "#s-flash");
    S(T.hit, "#s-dim", {{ opacity: 0 }});
    PUNCH(T.hit, "#s-shake", 1.1, 0.5);
    SHAKE(T.hit + FR, "#s-world", 6, 16);
    A(T.hit, "#s-tip", {{ opacity: [0, 1], scale: [0.3, 1.4] }}, 0.25, "outExpo");
    A(T.hit + 0.25, "#s-tip", {{ opacity: [1, 0.7], scale: [1.4, 1] }}, 0.4, "outQuad");
    A(T.inkEnd, "#s-tip", {{ opacity: 0 }}, 0.25, "outQuad");
    S(T.hit, ["#s-ink", "#s-inkg"], {{ opacity: 1 }});
    // S2: gold ink draws along the line (createDrawable), pen tracks it; label is erased and retyped
    A(T.hit, ["#s-ink", "#s-inkg"].map((s) => anime.svg.createDrawable(s)), {{ draw: ["0 0", "0 1"] }}, T.inkEnd - T.hit, "inOutSine");
    A(T.hit, "#s-pen", {{ translateX: [0, 710] }}, T.inkEnd - T.hit, "inOutSine");
    A(T.hit, "#s-world", camv(520, 1000, 1.1, 520, 1000), T.inkEnd - T.hit, "inOutSine");
    for (let i = 0; i < OLDN; i++) S(T.hit + 0.05 + i * (T.lab - T.hit - 0.1) / OLDN, "#s-o" + (OLDN - 1 - i), {{ opacity: 0 }});
    A(T.lab, "#s-nl .ch", {{ opacity: [0, 1], translateY: [24, 0], scale: [1.3, 1] }}, 0.2, "outExpo", {{ delay: anime.stagger(ms(T.labDur / NEWN)) }});
    // S3 on the downbeat: navy flood, label folds up into the base, USP stack (staggered), brand
    A(T.usp, "#s-navy", {{ opacity: [0.6, 1] }}, 0.15, "outQuad");
    A(T.usp, "#s-world", {{ filter: ["blur(0px)", "blur(10px)"] }}, 0.4, "outQuad");
    A(T.usp, "#s-base", {{ opacity: [0, 1], translateX: [15, 0], translateY: [428, 0], scaleX: [1.365, 1] }}, 0.4, "outExpo");
    A(T.usp, "#s-nl", {{ translateY: [0, T.nlY], scale: [1, 0.82], color: ["#161616", "#fbf9f4"], "--acc": ["#7d6233", "#e0c27e"] }}, 0.4, "outExpo");
    WORD(T.usp, "#s-u1", 1.35);
    WORD(T.usp + 0.11, "#s-u2", 1.3);
    WORD(T.usp + 0.22, "#s-u3", 1.2);
    PUNCH(T.usp, "#s-shake", 1.04, 0.3);
    A(T.brand, "#s-br", {{ opacity: [0, 1], translateY: [24, 0] }}, 0.5, anime.spring({{ bounce: 0.4, duration: 450 }}));
    // keep it alive: gold sheen sweeps the hero line, punches on the accents
    A(T.usp + 0.4, "#s-u2 span", {{ backgroundPosition: ["100% 0", "0% 0"] }}, T.end - T.usp - 0.4, "inOutSine");
    (T.acc || []).forEach((t) => {{ PUNCH(t, "#s-u2", 1.08, 0.35); A(t, "#s-base", {{ scaleX: [1.25, 1] }}, 0.4, "outExpo"); }});
"""
    return css, html, js


# ============================================================ CROSS (C7)
def build_cross(T):
    mini_cards = "".join(
        f'<div style="position:absolute;left:{30 + j * 16}px;top:{230 + j * 150}px;width:{300 - j * 32}px;height:200px;background:#f5f5f4;border:2px solid #d6d6d4;border-radius:14px">'
        + "".join(f'<div style="position:absolute;left:18px;top:{26 + m * 26}px;height:10px;border-radius:5px;width:{70 + (m * 29) % 30}%;background:#d0d0ce"></div>' for m in range(5))
        + "</div>" for j in range(3))
    css = """
    #c-dark { background: #0b1a33; }
    #c-paper { background: radial-gradient(60% 40% at 100% 100%, rgba(224, 194, 126, 0.25), rgba(224, 194, 126, 0)), var(--paper); clip-path: circle(0px at 540px 960px); }
    #c-u1 { top: 232px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #c-u2 { top: 266px; font-size: 44px; font-weight: 900; color: var(--navy); letter-spacing: -0.05em; }
    #c-u3 { top: 324px; font-size: 28px; font-weight: 600; color: #3c4250; }
    #c-br { top: 364px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #c-br img { width: 30px; height: 34px; }
    #c-cap { top: 448px; font-size: 84px; line-height: 1.12; color: var(--navy); }
    #c-cap .w { display: inline-block; opacity: 0; }
    .c-panel { position: absolute; top: 700px; width: 420px; height: 740px; border-radius: 28px; overflow: hidden; opacity: 0; }
    #c-left { left: 60px; background: #e2e1dd; border: 2px solid #cfcecb; filter: grayscale(1); }
    #c-right { left: 500px; background: linear-gradient(180deg, #fff8ea, #fbefd6); border: 3px solid var(--gold); }
    .c-lab { position: absolute; left: 0; right: 0; top: 34px; text-align: center; font-size: 40px; font-weight: 900; }
    #c-div { position: absolute; left: 487px; top: 680px; width: 6px; height: 780px; border-radius: 3px; background: linear-gradient(180deg, rgba(184, 149, 90, 0), #b8955a 20%, #e0c27e 50%, #b8955a 80%, rgba(184, 149, 90, 0)); opacity: 0; transform-origin: 50% 50%; }
    #c-hand { position: absolute; left: 225px; top: 1080px; width: 100px; height: 120px; opacity: 0; }
    #c-exp { background: linear-gradient(180deg, #fff8ea, #fbefd6); clip-path: inset(700px 160px 480px 500px round 28px); opacity: 0; }
    #c-pen2 { position: absolute; left: 420px; top: 760px; width: 140px; height: 140px; }
    #c-line2 { position: absolute; left: 210px; top: 1060px; width: 560px; height: 7px; border-radius: 4px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); transform-origin: 50% 50%; }
    #c-sub { top: 1186px; font-size: 36px; font-weight: 800; color: #3c4250; opacity: 0; }
    #c-btn { position: absolute; left: 130px; top: 1250px; width: 720px; height: 110px; border-radius: 999px; background: var(--navy); color: #fff; font-size: 46px; font-weight: 900; display: flex; align-items: center; justify-content: center; letter-spacing: -0.03em; box-shadow: 0 18px 40px rgba(11, 26, 51, 0.32); opacity: 0; }
    #c-u1, #c-u2, #c-u3, #c-br { transform-origin: 50% 0; }
"""
    html = f'''    <div id="c-dark" class="full" data-layout-ignore></div>
    <div id="c-paper" class="full" data-layout-ignore></div>
    <div id="c-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
    <div id="c-left" class="c-panel" data-layout-allow-overlap data-layout-allow-overflow>
      <div class="c-lab" style="color:#6b6f73">생성하는 쪽</div>
      <div style="position:absolute;left:30px;top:118px;width:56px;height:56px">{ICON_GREY}</div>
      <div style="position:absolute;left:100px;top:122px;right:30px;height:48px;border-radius:14px;background:#f5f5f4;border:2px solid #d6d6d4"></div>
      {mini_cards}
    </div>
    <div id="c-right" class="c-panel">
      <div class="c-lab" style="color:var(--gold-text)">서명하는 쪽</div>
      <div style="position:absolute;left:140px;top:200px;width:140px;height:140px">{PEN_ICON}</div>
      <div style="position:absolute;left:60px;top:470px;width:300px;height:7px;border-radius:4px;background:linear-gradient(90deg,#a07c3f,#e0c27e 55%,#b8955a)"></div>
    </div>
    <div id="c-div" data-layout-ignore></div>
    <div id="c-exp" class="full" data-layout-ignore>
      <div id="c-pen2">{PEN_ICON}</div>
      <div id="c-line2"></div>
    </div>
    <div id="c-hand" data-layout-ignore>{HAND_PTR}</div>
    </div>
    <div id="c-u1" class="col">국내 유일*</div>
    <div id="c-u2" class="col">100% 온라인 법학사</div>
    <div id="c-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="c-br" class="col">{MARK}경찰복지사이버평생교육원</div>
    <div id="c-cap" class="col cap">{words("서명하는 쪽으로")}<br>{words("넘어오세요.")}</div>
    <div id="c-sub" class="col">상담만 받아도 돼요.</div>
    <div id="c-btn">무료 상담 신청</div>'''
    js = f"""
    const T = {J(T)};
    // iris from the gold base onto paper; USP/brand shrink to the top
    A(T.c0, "#c-paper", {{ clipPath: ["circle(0px at 490px 600px)", "circle(2300px at 490px 600px)"] }}, 0.5, "outExpo");
    [["#c-u1", 372, 1.79, "#e0c27e", "#7d6233"], ["#c-u2", 402, 2.09, "#ffffff", "#0b1a33"], ["#c-u3", 466, 1.43, "#ffffff", "#3c4250"], ["#c-br", 508, 1.43, "#e0c27e", "#7d6233"]]
      .forEach(([s, dy, sc, c0, c1]) => A(T.c0, s, {{ translateY: [dy, 0], scale: [sc, 1], color: [c0, c1] }}, 0.45, "outExpo"));
    // caption word by word on 8th notes
    A(T.cap, "#c-cap .w", {{ opacity: [0, 1], scale: [1.4, 1], filter: ["blur(10px)", "blur(0px)"] }}, 0.2, "outExpo", {{ delay: anime.stagger(ms(T.capGap)) }});
    // split: panels spring in from the sides, divider grows
    A(T.split, "#c-left", {{ opacity: [0, 1], translateX: [-260, 0] }}, 0.6, anime.spring({{ bounce: 0.35, duration: 500 }}));
    A(T.split + 0.08, "#c-right", {{ opacity: [0, 1], translateX: [260, 0] }}, 0.6, anime.spring({{ bounce: 0.35, duration: 500 }}));
    A(T.split + 0.1, "#c-div", {{ opacity: [0, 1], scaleY: [0, 1] }}, 0.35, "outExpo");
    A(T.split + 0.25, "#c-hand", {{ opacity: [0, 1], translateY: [60, 0] }}, 0.25, "outExpo");
    // swipe across the divider (fast, with blur), the right panel lights on arrival
    A(T.swipe, "#c-hand", {{ translateX: [0, 470], filter: ["blur(0px)", "blur(6px)", "blur(0px)"] }}, T.s2 - T.swipe, "inOutExpo");
    A(T.s2 - 0.05, "#c-right", {{ scale: [1.06, 1] }}, 0.3, "outExpo");
    A(T.swipe, "#c-left", {{ opacity: [1, 0.45] }}, 0.3, "outQuad");
    // S2 on the hit: right panel takes the frame, button springs in, two pulses on the beat
    A(T.s2, "#c-exp", {{ opacity: [1, 1], clipPath: ["inset(700px 160px 480px 500px round 28px)", "inset(0px 0px 0px 0px round 0px)"] }}, 0.5, "outExpo");
    A(T.s2, "#c-pen2", {{ translateX: [220, 0], translateY: [200, 0] }}, 0.5, "outExpo");
    A(T.s2, "#c-line2", {{ translateX: [220, 0], translateY: [410, 0], scaleX: [0.54, 1] }}, 0.5, "outExpo");
    OUT(T.s2, "#c-hand", 0.12);
    SHAKE(T.s2, "#c-shake", 3, 8);
    A(T.s2 + 0.05, "#c-btn", {{ opacity: [0, 1], translateY: [70, 0], scale: [0.7, 1] }}, 0.6, anime.spring({{ bounce: 0.5, duration: 500 }}));
    A(T.s2 + 0.12, "#c-sub", {{ opacity: [0, 1], filter: ["blur(8px)", "blur(0px)"] }}, 0.2, "outQuad");
    T.pulses.forEach((t) => A(t, "#c-btn", {{ scale: [1.07, 1] }}, 0.4, anime.spring({{ bounce: 0.6, duration: 380 }})));
"""
    return css, html, js


# ============================================================ END (C8 / C8')
def build_end(T, compact=False):
    css = """
    #e-bg { background: linear-gradient(180deg, #fff8ea, #fbefd6); }
    #e-paper { background: radial-gradient(60% 40% at 100% 100%, rgba(224, 194, 126, 0.3), rgba(224, 194, 126, 0)), radial-gradient(60% 38% at 0% 0%, rgba(46, 92, 190, 0.07), rgba(46, 92, 190, 0)), var(--paper); }
    #e-slo { top: 640px; font-size: 92px; line-height: 1.22; color: var(--navy); letter-spacing: -0.055em; clip-path: inset(0% 100% 0% 0%); }
    #e-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    #e-u1 { top: 960px; font-size: 46px; font-weight: 900; color: var(--navy); letter-spacing: -0.05em; }
    #e-u1 b { color: var(--gold-text); font-weight: 800; }
    #e-u3 { top: 1030px; font-size: 34px; font-weight: 600; color: #3c4250; }
    #e-br { top: 1112px; display: flex; justify-content: center; align-items: center; gap: 12px; font-size: 38px; font-weight: 800; color: var(--gold-text); }
    #e-br img { width: 40px; height: 45px; }
    #e-sub { top: 1186px; font-size: 36px; font-weight: 800; color: #3c4250; }
    #e-btn { position: absolute; left: 130px; top: 1250px; width: 720px; height: 110px; border-radius: 999px; background: var(--navy); color: #fff; font-size: 46px; font-weight: 900; display: flex; align-items: center; justify-content: center; letter-spacing: -0.03em; box-shadow: 0 18px 40px rgba(11, 26, 51, 0.32); }
    #e-tel { top: 1394px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 32px; font-weight: 800; color: var(--navy); letter-spacing: -0.02em; }
    #e-tel svg { width: 34px; height: 34px; }
"""
    if compact:
        css += """
    #e-br { top: 1040px; }
    #e-btn { opacity: 0; }
"""
        mid = f'<div id="e-br" class="col">{MARK}경찰복지사이버평생교육원</div>'
    else:
        mid = f'''<div id="e-u1" class="col"><b>국내 유일*</b> 100% 온라인 법학사</div>
    <div id="e-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="e-br" class="col">{MARK}경찰복지사이버평생교육원</div>
    <div id="e-sub" class="col">상담만 받아도 돼요.</div>'''
    html = f'''    <div id="e-bg" class="full" data-layout-ignore></div>
    <div id="e-paper" class="full" data-layout-ignore></div>
    <div id="e-shake" class="full" data-layout-allow-overlap data-layout-allow-overflow>
    <div id="e-slo" class="col cap">책임지는 자리로,<br>지금 있는 자리에서.</div>
    <svg id="e-svg" viewBox="0 0 1080 1920" data-layout-ignore>
      <path id="e-ulg" d="M150 896 C 330 884, 560 900, 830 886" stroke="#e0c27e" stroke-width="22" stroke-linecap="round" fill="none" stroke-opacity="0.6" style="filter:blur(8px);opacity:0"/>
      <path id="e-ul" d="M150 896 C 330 884, 560 900, 830 886" stroke="#b8955a" stroke-width="9" stroke-linecap="round" fill="none" style="opacity:0"/>
    </svg>
    {mid}
    <div id="e-btn">무료 상담 신청</div>
    <div id="e-tel" class="col">{PHONE}<span>070-4006-7128 (평일 10–18시)</span></div>
    </div>'''
    js = f"""
    const T = {J(T)};
    const ul = ["#e-ul", "#e-ulg"].map((s) => anime.svg.createDrawable(s));
    S(T.c0, ul, {{ draw: "0 0" }});
    A(T.c0, "#e-paper", {{ opacity: [0, 1] }}, 0.25, "outQuad");
    // slogan: left→right mask wipe, then the signature underline draws under it
    A(T.c0, "#e-slo", {{ clipPath: ["inset(0% 100% 0% 0%)", "inset(0% 0% 0% 0%)"] }}, T.wipe, "inOutQuart");
    S(T.c0 + T.wipe * 0.6, ["#e-ul", "#e-ulg"], {{ opacity: 1 }});
    A(T.c0 + T.wipe * 0.6, ul, {{ draw: ["0 0", "0 1"] }}, 0.6, "inOutQuart");
    A(T.c0, "#e-tel", {{ opacity: [0, 1], translateY: [16, 0] }}, 0.3, "outExpo");
    if (T.compact) {{
      A(T.c0 + 0.1, "#e-br", {{ opacity: [0, 1], translateY: [26, 0] }}, 0.35, "outExpo");
      A(T.c0 + 0.05, "#e-btn", {{ opacity: [0, 1], translateY: [70, 0], scale: [0.7, 1] }}, 0.6, anime.spring({{ bounce: 0.5, duration: 500 }}));
    }} else {{
      A(T.c0 + 0.12, ["#e-u1", "#e-u3", "#e-br"], {{ opacity: [0, 1], translateY: [26, 0] }}, 0.35, "outExpo", {{ delay: anime.stagger(70) }});
    }}
    T.pulses.forEach((t) => A(t, "#e-btn", {{ scale: [1.07, 1] }}, 0.4, anime.spring({{ bounce: 0.6, duration: 380 }})));
    // last hit: underline glows, frame snaps, then holds still to the end
    A(T.last, "#e-ulg", {{ strokeOpacity: [1, 0.6] }}, 0.5, "outQuad");
    PUNCH(T.last, "#e-shake", 1.025, 0.4);
"""
    return css, html, js


# ============================================================ LEGAL overlay (연출 + 고지 L1·L2)
def build_legal(t0, t1, tag, disc, dark_until):
    """tag=(start,end) abs, disc=start abs; disclaimers run to the end. Texts white on dark, ink on paper."""
    css = """
    #root { pointer-events: none; }
    #l-tag { position: absolute; left: 48px; top: 1500px; }
    .l-d { position: absolute; left: 60px; width: 860px; text-align: center; font-size: 24px; font-weight: 600; letter-spacing: -0.02em; white-space: nowrap; }
    .l-d span { opacity: 0.85; color: #ffffff; }
"""
    html = f'''    <div id="l-tag" class="clip" data-start="{tag[0] - t0:.3f}" data-duration="{tag[1] - tag[0]:.3f}" data-track-index="1"><div class="tag">연출</div></div>
    <div id="l-d1" class="clip l-d" data-start="{disc - t0:.3f}" data-duration="{t1 - disc:.3f}" data-track-index="2" style="top:1580px"><span id="l-d1i">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</span></div>
    <div id="l-d2" class="clip l-d" data-start="{disc - t0:.3f}" data-duration="{t1 - disc:.3f}" data-track-index="3" style="top:1615px"><span id="l-d2i">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</span></div>'''
    js = f"""
    // on the light C7/C8 grounds the disclaimers turn ink (still 85%)
    S({dark_until}, ["#l-d1i", "#l-d2i"], {{ color: "#161616" }});
"""
    return css, html, js


# ============================================================ FX overlay: seeded grain + vignette (whole film)
def build_fx(total):
    css = """
    #root { pointer-events: none; }
    #x-wrap { position: absolute; inset: 0; overflow: hidden; --gx: 0px; --gy: 0px; }
    #x-wrap::after { content: ""; position: absolute; left: -200px; top: -200px; width: 1480px; height: 2320px; background: var(--noise); opacity: 0.9; transform: translate(var(--gx), var(--gy)); }
    #x-vig { background: radial-gradient(ellipse 75% 60% at 50% 50%, rgba(0, 0, 0, 0) 55%, rgba(0, 0, 0, 0.3) 100%); }
"""
    html = '''    <div id="x-wrap" data-layout-ignore></div>
    <div id="x-vig" class="full" data-layout-ignore></div>'''
    js = f"""
    // grain re-seeds every 2 frames (seeded random offsets: identical every render)
    for (let t = 0; t < {total}; t += 2 * FR) S(t, "#x-wrap", {{ "--gx": R(-180, 180, 0) + "px", "--gy": R(-180, 180, 0) + "px" }});
"""
    return css, html, js


# ============================================================ assemble
SCENE_SPECS = []  # (cid, t0, t1, builder output, seed)

if VARIANT == "30":
    # cut points (beats of the excerpt). See README cut table.
    C = dict(hook=0, fill=B(7), blank=B(14), dust=B(23), desk=B(32), sign=B(41), cross=B(55), end=B(63), fin=30.0)
    T_h = dict(p1=B(1), p2=B(2), s2=B(3), w0=B(3) + 0.12, w1=B(4), w2=B(5), gl=B(6), end=C["fill"])
    T_f = dict(c0=C["fill"], c1=B(8), c2=B(9), wide=B(10), k0=B(11), k1=B(12), k2=B(13), end=C["blank"])
    T_b = dict(fromWide=True, c0=C["blank"], tilt=C["blank"], w0=B(15), w1=B(15.5), w2=B(16), wAll=None, btn=B(16),
               clicks=[B(17), B(18), B(18.5), B(19)], capOut=None, toast=B(20), push=B(21), end=C["dust"])
    T_d = dict(c0=C["dust"], s2=B(27), br=None, end=C["desk"])
    T_k = dict(c0=C["desk"], s2=B(35), dip=B(37), b1=B(38), b2=B(39), b3=B(40), end=C["sign"])
    T_s = dict(c0=C["sign"], tense=[B(42), B(43), B(43.5)], hit=B(44), lab=B(45), labDur=0.6, inkEnd=B(47), usp=B(48),
               brand=B(49), acc=[B(52), B(54)], nlY=-580, end=C["cross"])
    T_c = dict(c0=C["cross"], cap=B(55) + 0.12, capGap=B(55.5) - B(55), split=B(56), swipe=B(58), s2=B(60),
               pulses=[B(61), B(62)], end=C["end"])
    T_e = dict(c0=C["end"], wipe=B(64) - B(63), pulses=[B(65), B(67)], last=B(68), compact=False)
    SCENE_SPECS = [
        ("hook", C["hook"], C["fill"], build_hook(T_h)),
        ("fill", C["fill"], C["blank"], build_fill(T_f)),
        ("blank", C["blank"], C["dust"], build_blank(T_b)),
        ("dust", C["dust"], C["desk"], build_dust(T_d, "AI가 일을 대신할수록,", ("책임질 자리는", "더 귀해집니다."))),
        ("desk", C["desk"], C["sign"], build_desk(T_k)),
        ("sign", C["sign"], C["cross"], build_sign(T_s)),
        ("cross", C["cross"], C["end"], build_cross(T_c)),
        ("end", C["end"], C["fin"], build_end(T_e)),
    ]
    TAG = (T_k["s2"], C["cross"])        # 연출: desk/pen illustration shots (spec f465–f719)
    DISC = T_s["usp"]                    # L1·L2 with the USP (spec f630)
    LIGHT_FROM = C["cross"]
    CUTS = [(B(1), "C1 punch-in 1"), (B(2), "C1 punch-in 2"), (B(3), "C1 S2 whip"), (C["fill"], "C2"), (B(8), "C2 col2"),
            (B(9), "C2 col3"), (B(10), "C2 wide"), (C["blank"], "C3"), (B(20), "C3 S3 toast"), (C["dust"], "C4"),
            (C["desk"], "C5"), (B(35), "C5 S2 desk match"), (C["sign"], "C6"), (T_s["hit"], "C6 S2 pen touch"),
            (T_s["usp"], "C6 S3 USP"), (C["cross"], "C7"), (T_c["s2"], "C7 S2"), (C["end"], "C8")]
else:
    C = dict(hook=0, blank=B(5), dust=B(11), sign=B(21), end=B(28), fin=15.0)
    T_h = dict(p1=B(1), p2=B(2), s2=B(3), w0=B(3) + 0.12, w1=B(4), w2=B(4.5), gl=B(4.75) , end=C["blank"])
    T_b = dict(fromWide=False, c0=C["blank"], tilt=None, w0=None, w1=None, w2=None, wAll=C["blank"], btn=C["blank"],
               clicks=[B(6), B(6.5), B(7)], capOut=B(8), toast=B(8), push=B(9), end=C["dust"])
    T_d = dict(c0=C["dust"], s2=B(14), br=B(18), end=C["sign"])
    T_s = dict(c0=C["sign"], tense=[B(22), B(22.5)], hit=B(23), lab=B(23) + 0.12, labDur=0.32, inkEnd=B(24) + 0.2,
               usp=B(24), brand=B(25), acc=[B(26), B(27)], nlY=-580, end=C["end"])
    T_e = dict(c0=C["end"], wipe=0.5, pulses=[B(31), B(32)], last=B(34), compact=True)
    SCENE_SPECS = [
        ("hook", C["hook"], C["blank"], build_hook(T_h)),
        ("blank", C["blank"], C["dust"], build_blank(T_b)),
        ("dust", C["dust"], C["sign"], build_dust(T_d, "AI가 대신할수록,", ("책임질 자리는", "더 귀해집니다."),
                                                   bridge=("그 칸은,", "법을 아는 사람의 몫"))),
        ("sign", C["sign"], C["end"], build_sign(T_s, compact=True)),
        ("end", C["end"], C["fin"], build_end(T_e, compact=True)),
    ]
    TAG = (C["sign"], C["end"])          # 연출 spec f270–f359
    DISC = T_s["usp"]                    # spec f321
    LIGHT_FROM = C["end"]
    CUTS = [(B(1), "C1' punch-in 1"), (B(2), "C1' punch-in 2"), (B(3), "C1' S2 whip"), (C["blank"], "C3'"),
            (B(8), "C3' toast"), (C["dust"], "C4'"), (B(18), "C4' S3 bridge"), (C["sign"], "C6'"),
            (T_s["hit"], "C6' S2 pen touch"), (T_s["usp"], "C6' S3 USP"), (C["end"], "C8'")]

for k, (cid, t0, t1, (css, html, js)) in enumerate(SCENE_SPECS):
    SLOTS.append(scene(cid, t0, t1, css, html, js, seed=1100 + k))
lc, lh, lj = build_legal(TAG[0], TOTAL, TAG, DISC, LIGHT_FROM)
SLOTS.append(scene("legal", TAG[0], TOTAL, lc, lh, lj, seed=1199))
xc, xh, xj = build_fx(TOTAL)
SLOTS.append(scene("fx", 0, TOTAL, xc, xh, xj, seed=1198))

json.dump({"variant": VARIANT, "offset": OFFSET, "bpm": BEATS["bpm"],
           "cuts": [{"t": round(t, 3), "frame": round(t * 30), "label": l} for t, l in CUTS],
           "scenes": [{"id": s[0], "start": s[1], "duration": s[2]} for s in SLOTS]},
          open(os.path.join(OUT, "beats", "cuts.json") if VARIANT == "30" else os.path.join(ROOT, "beats", "cuts-15s.json"), "w"), indent=1)

# ---------------------------------------------------------------- index.html
hosts = []
for cid, start, dur in SLOTS:
    z = {"legal": 6, "fx": 5}.get(cid, 2)
    track = {"legal": 3, "fx": 2}.get(cid, 1)
    hosts.append(f'''      <div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: {z}"{" data-layout-ignore" if cid == "fx" else ""}></div>''')
audio = "assets/audio/mix-30s.mp3" if VARIANT == "30" else "assets/audio/mix-15s.mp3"
index = f'''<!doctype html>
<html
  lang="ko"
  data-resolution="portrait"
  data-composition-variables='[
  {{"id":"color-ground","type":"color","label":"Ink","default":"#0E1218"}},
  {{"id":"color-paper","type":"color","label":"Paper","default":"#FBF9F4"}},
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0e1218; }}
    </style>
  </head>
  <body>
    <!-- 「마지막 서명」 {VARIANT}초 · anime.js v4 · cuts on the BGM beat grid (beats/source.json). Generated by tools/build.py -->
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

      <!-- BGM excerpt ("Breaking News Intro", kornevmusic, Pixabay 527939) + beat-synced SFX, mixed by tools/make_audio.py. See MUSIC.md -->
      <audio id="bgm" class="clip" src="{audio}" data-start="0" data-duration="{TOTAL:g}" data-track-index="10" data-volume="1"></audio>
    </div>
  </body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)

if VARIANT == "15":
    for sub in ("fonts", "img", "audio"):
        os.makedirs(os.path.join(OUT, "assets", sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets/fonts/PretendardGOV-subset.woff2"), os.path.join(OUT, "assets/fonts/"))
    shutil.copy(os.path.join(ROOT, "assets/img/mark-gold.svg"), os.path.join(OUT, "assets/img/"))
    src = os.path.join(ROOT, "assets/audio/mix-15s.mp3")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "assets/audio/"))
    os.makedirs(os.path.join(OUT, "lib"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "lib/anime.umd.min.js"), os.path.join(OUT, "lib/"))
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(OUT, "hyperframes.json"))

print(f"{VARIANT}s: offset {OFFSET}s, {len(SLOTS)} scenes ->", OUT)
for c in SLOTS:
    print("  ", c)
