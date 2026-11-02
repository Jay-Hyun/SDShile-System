"""「마지막 서명」 30초 — scene generator.

Usage: python3 tools/build.py   (from the project root)
Writes compositions/*.html and index.html. Timing is taken frame-for-frame from
docs/ads/naver-clip/01-last-signature.md §4 (30fps, absolute frames).
Scene-local times are written as F(n) = (n - scene_start_frame) / 30.
"""
import json
import os
import random
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = open(os.path.join(ROOT, "tools", "common.css"), encoding="utf-8").read()
TOTAL = 30.0
VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "30"
OUT = ROOT if VARIANT == "30" else os.path.join(ROOT, "v15")

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
# 매크로 펜 + 손 (가상 일러스트). 펜촉 끝 = viewBox (14, 586)
PEN_HAND = '''<svg viewBox="0 0 640 640" width="640" height="640" style="overflow:visible">
  <defs>
    <linearGradient id="@@-lq" x1="0" y1="-22" x2="0" y2="22" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#4a4f58"/><stop offset="0.28" stop-color="#15171b"/><stop offset="0.7" stop-color="#050506"/><stop offset="1" stop-color="#2a2d33"/></linearGradient>
    <linearGradient id="@@-gd" x1="0" y1="-18" x2="0" y2="18" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f3dfae"/><stop offset="0.45" stop-color="#c9a666"/><stop offset="1" stop-color="#8a6a33"/></linearGradient>
    <radialGradient id="@@-gl"><stop offset="0" stop-color="#fff4d6" stop-opacity="1"/><stop offset="0.35" stop-color="#e0c27e" stop-opacity="0.7"/><stop offset="1" stop-color="#e0c27e" stop-opacity="0"/></radialGradient>
    <filter id="@@-sh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  </defs>
  <g transform="translate(14 586) rotate(-45)">
    <rect id="@@-shadow" x="60" y="34" width="1500" height="30" rx="15" fill="rgba(60,40,15,0.28)" filter="url(#@@-sh)"/>
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
BODY_TOP = 156  # body top inside a doc

rnd = random.Random(20261102)
BARS = []
for i in range(3):
    rows = []
    y = 0
    k = 0
    while y <= 610:
        if k == 11:
            rows.append(("mid", y))
        else:
            w = 100 if k % 6 == 0 else rnd.randint(58, 100)
            rows.append(("bar", y, w, k % 6 == 0))
        y += 26
        k += 1
    BARS.append(rows)


def doc(i, p, ok_on=True, sig_style="", last_variants=False, ok_id=True):
    d = DOCS[i]
    rows = []
    for r in BARS[i]:
        if r[0] == "mid":
            rows.append(f'<div class="mid" style="top:{r[1] - 6}px">{d["mid"]}</div>')
        else:
            rows.append(f'<div class="bar{" dk" if r[3] else ""}" style="top:{r[1]}px;width:{r[2]}%"></div>')
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
    right = (f'<span id="{p}-pct" style="font-size:28px;font-weight:800;color:#6F8F7A;letter-spacing:-0.02em">생성 중 0%</span>'
             if progress else f'<div class="sent">{SENT}</div>')
    return f'''<div class="ui-head">{ICON}<b>문서 도우미</b></div>
      <div class="ui-strip"><span class="q">법률 검토 문서 3건 작성</span>{right}</div>'''


HELPERS = r"""
    const F0 = __F0__;
    const F = (n) => (n - F0) / 30;
    function IN(sel, t, from, dur, ease) {
      const f = Object.assign({ opacity: 0, filter: "blur(10px)" }, from || {});
      const to = { opacity: 1, filter: "blur(0px)", duration: dur || 0.2, ease: ease || "power3.out" };
      for (const k in f) if (!(k in to)) to[k] = k.startsWith("scale") ? 1 : 0;
      tl.fromTo(sel, f, to, t);
    }
    function OUT(sel, t, to, dur) {
      tl.to(sel, Object.assign({ opacity: 0, filter: "blur(8px)", duration: dur || 0.14, ease: "power2.in" }, to || {}), t);
    }
    // 커서 깜박임: 8프레임 간격 on/off (시간의 함수)
    function BLINK(sel, t0, t1) {
      let on = true;
      for (let t = t0; t < t1 - 1e-6; t += 8 / 30) { tl.set(sel, { opacity: on ? 1 : 0 }, t); on = !on; }
    }
    // 1프레임 글리치: 카메라 가로 밀림 + RGB 슬라이스
    function GLITCH(cam, gl, t, dx) {
      tl.set(cam, { x: dx }, t);
      tl.set(gl, { opacity: 1 }, t);
      tl.set(cam, { x: 0 }, t + 1 / 30);
      tl.set(gl, { opacity: 0 }, t + 1 / 30);
    }
"""

GL = '''<div id="@@-gl" class="full" style="opacity:0;pointer-events:none" data-layout-ignore>
      <div class="glitch" style="top:420px;height:46px;background:rgba(255,40,90,0.35)"></div>
      <div class="glitch" style="top:880px;height:22px;background:rgba(0,200,230,0.4)"></div>
      <div class="glitch" style="top:1210px;height:64px;background:rgba(255,40,90,0.28)"></div>
      <div class="glitch" style="top:1330px;height:14px;background:rgba(0,200,230,0.45)"></div>
    </div>'''


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}" style="display:inline-block">{w}</span>' for w in text.split(" "))


def chars(text, pid, acc_from=None):
    out = []
    for i, c in enumerate(text):
        style = ' style="color:var(--acc)"' if acc_from is not None and i >= acc_from else ""
        out.append(f'<span id="{pid}{i}" class="ch"{style}>{c}</span>')
    return "".join(out)


def scene(cid, f0, f1, css, html, js, variant="30"):
    helpers = HELPERS.replace("__F0__", str(f0))
    s = f'''<template>
  <style>
{COMMON}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{helpers}
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
'''
    if variant == VARIANT:
        os.makedirs(os.path.join(OUT, "compositions"), exist_ok=True)
        open(os.path.join(OUT, "compositions", cid + ".html"), "w", encoding="utf-8").write(s)
    return (cid, round(f0 / 30, 4), round((f1 - f0 + 1) / 30, 4))


SLOTS = []

# ============================================================ C1 hook f0–f89
fan = []
for i, (cx, cy, rot) in enumerate([(300, 1000, -8), (680, 1000, 8), (490, 965, 0)]):
    di = [0, 2, 1][i]
    d = DOCS[di]
    bars = "".join(f'<div style="position:absolute;left:0;top:{y}px;height:10px;border-radius:5px;width:{w}%;background:{"#b9bec3" if k % 5 == 0 else "#d3d6d9"}"></div>'
                   for k, (y, w) in enumerate((j * 24, 100 if j % 5 == 0 else 60 + (j * 37) % 40) for j in range(13)))
    fan.append(f'''<div id="h-f{di}" class="abs" style="left:{cx - 190}px;top:{cy - 280}px;width:380px;height:560px;z-index:{2 if di == 1 else 1}">
        <div class="full" style="transform:rotate({rot}deg);background:#fff;border:2px solid #ddd8cc;border-radius:18px;box-shadow:0 22px 50px rgba(34,38,43,0.16)">
          <div class="abs" style="left:22px;top:20px;font-size:30px;font-weight:800;color:#22262B;white-space:nowrap">{d["title"]}</div>
          <div class="abs" style="left:20px;top:70px;padding:3px 10px;border-radius:8px;background:#e7eee9;color:#47604f;font-size:22px;font-weight:700;white-space:nowrap">[가상 문서 · 예시]</div>
          <div class="abs" style="left:22px;top:118px;font-size:24px;font-weight:800;color:#22262B">{d["hd"]}</div>
          <div class="abs" style="left:22px;right:22px;top:162px;height:300px">{bars}</div>
          <div class="abs" style="left:14px;right:14px;top:478px;height:62px;border-radius:10px;background:#eeece6"></div>
          <div class="abs" style="left:26px;top:494px;font-size:21px;font-weight:800;color:#6b7076;white-space:nowrap">법률 검토·책임자 서명: ____</div>
        </div>
      </div>''')

hook_css = """
    #h-bg { background: var(--noise), var(--pat-dots), var(--ui-bg); }
    #h-chip { position: absolute; right: 160px; top: 408px; height: 50px; padding: 0 20px; border-radius: 999px; background: var(--sage); color: #fff; font-size: 28px; font-weight: 800; display: flex; align-items: center; letter-spacing: -0.02em; }
    #h-head { top: 482px; font-size: 104px; color: var(--ui-ink); }
    #h-cap { top: 250px; font-size: 96px; color: var(--ui-ink); }
    #h-flash { background: #ffffff; opacity: 0; }
"""
hook_html = f'''    <div id="h-bg" class="full" data-layout-ignore></div>
    <div id="h-cam" class="full" data-layout-allow-overlap>
      <div id="h-world" class="full">
        <div id="h-page" class="full">
          {ui_head("h")}
          <div id="h-chip">생성 완료 0.1s</div>
          {"".join(fan)}
        </div>
        <div id="h-row" class="full" style="top:2100px">
          <div class="full" style="top:-505px">
          {doc(0, "h")}{doc(1, "h")}{doc(2, "h")}
          </div>
        </div>
      </div>
      <div id="h-head" class="col cap">{words("AI가 다 써줍니다.")}</div>
    </div>
    <div id="h-cap" class="col cap"><span id="h-plate" class="plate">{words("딱 한 칸만 빼고.")}</span></div>
    {GL.replace("@@", "h")}
    <div id="h-flash" class="full" data-layout-ignore></div>'''
hook_js = """
    // S1 f0–f44: f0부터 완성 상태. 1–4프레임 카메라 셰이크, 문서 미세 바운스
    [[1, 7, -5], [2, -6, 4], [3, 4, 3], [4, -2, -2], [5, 0, 0]].forEach(([n, x, y]) => tl.set("#h-cam", { x, y }, F(n)));
    tl.fromTo(["#h-f0", "#h-f2", "#h-f1"], { y: -16 }, { y: 0, duration: 0.7, ease: "back.out(2.4)", stagger: 0.07 }, 0);
    tl.fromTo("#h-chip", { scale: 1.08 }, { scale: 1, duration: 0.35, ease: "power3.out" }, F(9));
    // S2 f45–f89: 헤드라인 위로 빠짐 → 스냅 틸트 다운
    OUT("#h-head", F(45), { y: -140 }, 0.18);
    tl.fromTo("#h-world", { y: 0 }, { y: -2100, duration: 0.42, ease: "expo.inOut" }, F(45));
    tl.fromTo("#h-world", { filter: "blur(0px)" }, { filter: "blur(14px)", duration: 0.25, ease: "power2.in" }, F(46));
    tl.to("#h-world", { filter: "blur(0px)", duration: 0.25, ease: "power2.out" }, F(46) + 0.25);
    tl.fromTo("#h-plate", { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.16, ease: "power3.out" }, F(47));
    tl.fromTo("#h-cap .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out", stagger: 0.067 }, F(48));
    // 서명란 강조 + 커서 깜박임
    tl.fromTo(["#h-s0", "#h-s1", "#h-s2"], { backgroundColor: "#eeece6" }, { backgroundColor: "#e1ebe3", duration: 0.3 }, F(62));
    ["#h-c0", "#h-c1", "#h-c2"].forEach((c) => BLINK(c, F(60), F(84)));
    // f83까지 자막, f84–f85 글리치 2프레임, f86–f89 화이트 플래시
    tl.set("#h-cap", { opacity: 0 }, F(84));
    GLITCH("#h-cam", "#h-gl", F(84), 22);
    GLITCH("#h-cam", "#h-gl", F(85), -16);
    tl.fromTo("#h-flash", { opacity: 0 }, { opacity: 1, duration: 3 / 30, ease: "none" }, F(86));
"""
SLOTS.append(scene("hook", 0, 89, hook_css, hook_html, hook_js))

# ============================================================ C2 fill f90–f179
fill_css = """
    #f-bg { background: var(--noise), var(--pat-dots), var(--ui-bg); }
    #f-bar { position: absolute; left: 60px; top: 398px; width: 860px; height: 8px; border-radius: 4px; background: #e2ddd2; overflow: hidden; }
    #f-bar i { position: absolute; inset: 0; background: var(--sage); transform-origin: 0 50%; }
    #f-flash { background: #ffffff; }
"""
fill_html = f'''    <div id="f-bg" class="full" data-layout-ignore></div>
    <div id="f-cam" class="full" data-layout-allow-overlap>
      {ui_head("f", progress=True)}
      <div id="f-bar"><i id="f-bari"></i></div>
      {doc(0, "f", ok_on=False)}{doc(1, "f", ok_on=False)}{doc(2, "f", ok_on=False)}
    </div>
    <div id="f-flash" class="full" data-layout-ignore></div>'''
fill_js = """
    tl.fromTo("#f-flash", { opacity: 1 }, { opacity: 0, duration: 0.2, ease: "power2.out" }, 0);
    // S1 f90–f125: 본문 0→50%, 타이핑 가속 / S2 f126–f179: 50→99%
    [0, 1, 2].forEach((i) => {
      const o = i * 0.06;
      tl.fromTo("#f-b" + i, { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 50% 0%)", duration: F(125) - o, ease: "power2.in" }, o);
      tl.to("#f-b" + i, { clipPath: "inset(0% 0% 0% 0%)", duration: F(176) - F(126) - o, ease: "power1.inOut" }, F(126) + o);
    });
    const pct = document.querySelector("#f-pct");
    const P = { v: 0 };
    tl.fromTo(P, { v: 0 }, { v: 50, duration: F(125), ease: "power2.in", onUpdate: () => (pct.textContent = "생성 중 " + Math.round(P.v) + "%") }, 0);
    tl.to(P, { v: 99, duration: F(176) - F(126), ease: "power1.inOut", onUpdate: () => (pct.textContent = "생성 중 " + Math.round(P.v) + "%") }, F(126));
    tl.fromTo("#f-bari", { scaleX: 0 }, { scaleX: 0.5, duration: F(125), ease: "power2.in" }, 0);
    tl.to("#f-bari", { scaleX: 0.99, duration: F(176) - F(126), ease: "power1.inOut" }, F(126));
    // ✓ 순차 팝 (f165 / f171 / f177)
    [165, 171, 177].forEach((n, i) => tl.fromTo("#f-k" + i, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2)" }, F(n)));
"""
SLOTS.append(scene("fill", 90, 179, fill_css, fill_html, fill_js))

# ============================================================ C3 blank f180–f299
blank_css = """
    #b-bg { background: var(--noise), var(--pat-dots), var(--ui-bg); }
    #b-cap { top: 250px; font-size: 96px; color: var(--ui-ink); }
    #b-btn { position: absolute; left: 330px; top: 1160px; width: 320px; height: 104px; border-radius: 26px; background: var(--ui-ink); color: #fff; font-size: 44px; font-weight: 800; display: flex; align-items: center; justify-content: center; letter-spacing: -0.02em; box-shadow: 0 16px 34px rgba(34, 38, 43, 0.25); }
    #b-ptr { position: absolute; left: 520px; top: 1215px; width: 96px; height: 116px; }
    #b-toast { position: absolute; left: 110px; top: 992px; width: 760px; height: 96px; border-radius: 22px; background: #2b2f34; color: #fff; display: flex; align-items: center; justify-content: center; gap: 16px; font-size: 36px; font-weight: 700; letter-spacing: -0.03em; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.3); }
    #b-toast i { width: 40px; height: 40px; border-radius: 50%; background: #d9644f; color: #fff; font-style: normal; font-size: 28px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
    #b-vig { background: radial-gradient(ellipse 62% 40% at 45% 46%, rgba(12, 12, 14, 0) 30%, rgba(12, 12, 14, 0.9) 100%); opacity: 0; }
"""
blank_html = f'''    <div id="b-bg" class="full" data-layout-ignore></div>
    <div id="b-cam" class="full" data-layout-allow-overlap>
      {ui_head("b")}
      {doc(0, "b", last_variants=True)}{doc(1, "b", last_variants=True)}{doc(2, "b", last_variants=True)}
    </div>
    <div id="b-vig" class="full" data-layout-ignore></div>
    <div id="b-cap" class="col cap"><span id="b-plate" class="plate"><span id="b-cap1">{words("딱 한 칸만")}</span> <span id="b-cap2" class="w" style="display:inline-block">빼고.</span></span></div>
    <div id="b-btn">생성</div>
    <div id="b-toast"><i>!</i>이 항목은 생성할 수 없습니다.</div>
    <div id="b-ptr" data-layout-ignore>{HAND_PTR}</div>
    {GL.replace("@@", "b")}'''
blank_js = """
    // S1 f180–f209: 틸트 다운, 세 서명란 가로로 나란히. 자막 '딱 한 칸만' f189
    tl.fromTo("#b-cam", { y: 0 }, { y: -505, duration: 1.0, ease: "power3.inOut" }, 0);
    tl.fromTo(["#b-s0", "#b-s1", "#b-s2"], { backgroundColor: "#eeece6" }, { backgroundColor: "#e1ebe3", duration: 0.4 }, 0.5);
    ["#b-c0", "#b-c1", "#b-c2"].forEach((c) => BLINK(c, F(196), F(300)));
    tl.fromTo("#b-plate", { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.16, ease: "power3.out" }, F(188));
    tl.fromTo("#b-cap1 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out", stagger: 0.067 }, F(189));
    // S2 f210–f254: '빼고.' 추가, 생성 버튼 + 손가락 커서, 4연타
    IN("#b-cap2", F(210), {}, 0.14);
    IN("#b-btn", F(210), { y: 40 }, 0.22);
    tl.fromTo("#b-ptr", { opacity: 0, x: 140, y: 160 }, { opacity: 1, x: 0, y: 0, duration: 0.2, ease: "power3.out" }, F(211));
    const CL = [216, 226, 236, 246];
    CL.forEach((n, k) => {
      const t = F(n);
      tl.fromTo("#b-ptr", { scale: 1 }, { scale: 0.86, duration: 0.05, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t);
      tl.fromTo("#b-btn", { scale: 1 }, { scale: 0.94, duration: 0.05, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t);
      GLITCH("#b-cam", "#b-gl", t, k % 2 ? -18 : 18);
      [0, 1, 2].forEach((i) => { tl.set("#b-l" + i + "-" + k, { opacity: 0 }, t); tl.set("#b-l" + i + "-" + (k + 1), { opacity: 1 }, t); });
    });
    // S3 f255–f299: 토스트, 서명란 하나 익스트림 클로즈업, 비네팅
    tl.fromTo("#b-toast", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.24, ease: "power3.out" }, F(255));
    tl.fromTo("#b-toast", { x: 0 }, { x: 10, duration: 0.04, yoyo: true, repeat: 3, ease: "none", immediateRender: false }, F(256));
    OUT(["#b-btn", "#b-ptr"], F(266), { y: 30 }, 0.16);
    tl.fromTo("#b-cam", { scale: 1, transformOrigin: "490px 1385px" }, { scale: 2.4, duration: 0.9, ease: "power3.inOut", immediateRender: false }, F(268));
    tl.to("#b-toast", { y: 168, duration: 0.9, ease: "power3.inOut" }, F(268));
    tl.fromTo("#b-vig", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.inOut" }, F(268));
"""
SLOTS.append(scene("blank", 180, 299, blank_css, blank_html, blank_js))

# ============================================================ C4 dust f300–f419
prng = random.Random(42)
pts = []
for i in range(3):
    for _ in range(130):
        x = COLX[i] + 18 + prng.random() * (COLW - 36)
        y = COLY + BODY_TOP + prng.random() * 724
        if i == 1 and y > COLY + 880:
            continue
        pts.append((x, y, prng.randint(5, 10), prng.random(), prng.random()))
    for _ in range(14):  # title / watermark / header
        x = COLX[i] + 18 + prng.random() * (COLW - 60)
        y = COLY + 14 + prng.random() * 130
        pts.append((x, y, prng.randint(3, 6), prng.random(), prng.random()))
    if i != 1:
        for _ in range(16):  # side signature boxes
            x = COLX[i] + 16 + prng.random() * (COLW - 32)
            y = COLY + 895 + prng.random() * 120
            pts.append((x, y, prng.randint(3, 6), prng.random(), prng.random()))
pts_html = "".join(f'<i style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{s}px;height:{s}px;border-radius:50%;background:#7d848b;opacity:0"></i>'
                   for (x, y, s, a, b) in pts)
pts_js = json.dumps([[round(y), round(a, 3), round(b, 3)] for (x, y, s, a, b) in pts])

dust_css = """
    #d-bg { background: var(--noise), var(--pat-dots), var(--ui-bg); }
    #d-dark { background: radial-gradient(60% 40% at 50% 50%, #22201d, #141414 100%); opacity: 0; }
    #d-c1 { top: 300px; font-size: 52px; font-weight: 800; color: var(--ui-ink); }
    #d-c2 { top: 380px; font-size: 84px; color: #fbf9f4; }
    #d-hero { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #d-hlb { position: absolute; left: 160px; top: 858px; width: 660px; text-align: center; font-size: 46px; font-weight: 800; color: #fbf9f4; }
    #d-hul { position: absolute; left: 160px; top: 958px; width: 660px; height: 4px; background: #fbf9f4; }
    #d-glow { position: absolute; left: 150px; top: 946px; width: 680px; height: 28px; border-radius: 14px; background: radial-gradient(50% 50% at 50% 50%, rgba(224, 194, 126, 0.75), rgba(224, 194, 126, 0)); }
    #d-cur { position: absolute; left: 164px; top: 912px; width: 4px; height: 40px; background: #fbf9f4; }
"""
dust_html = f'''    <div id="d-bg" class="full" data-layout-ignore></div>
    <div id="d-dark" class="full" data-layout-ignore></div>
    <div id="d-page" class="full" data-layout-allow-overlap>
      {doc(0, "d", sig_style="background:#e1ebe3")}{doc(1, "d", sig_style="background:#e1ebe3")}{doc(2, "d", sig_style="background:#e1ebe3")}
    </div>
    <div id="d-pts" class="full" data-layout-ignore>{pts_html}</div>
    <div id="d-push" class="full">
      <div id="d-hero">
        <div id="d-glow" data-layout-ignore></div>
        <div id="d-hlb">법률 검토·책임자 서명:</div>
        <div id="d-hul"></div>
        <div id="d-cur"></div>
      </div>
    </div>
    <div id="d-c1" class="col">{words("AI가 일을 대신할수록,")}</div>
    <div id="d-c2" class="col cap">책임질 자리는<br>더 귀해집니다.</div>'''
dust_js = """
    const PTS = __PTS__;
    // S1 f300–f347: 무음. 서명란 외 글자가 아래→위로 먼지처럼 흩어지고 배경이 먹색으로
    tl.fromTo("#d-c1 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out", stagger: 0.067 }, 0);
    [0, 1, 2].forEach((i) => tl.fromTo("#d-b" + i, { clipPath: "inset(0% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 100% 0%)", duration: 1.0, ease: "power1.in" }, 0.15));
    tl.fromTo(["#d-s0", "#d-s2"], { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "power1.in" }, 0.1);
    tl.fromTo(["#d-t0", "#d-t1", "#d-t2", "#d-k0", "#d-k1", "#d-k2", "#d-d0 .wm", "#d-d1 .wm", "#d-d2 .wm", "#d-d0 .hd", "#d-d1 .hd", "#d-d2 .hd"], { opacity: 1 }, { opacity: 0, duration: 0.25 }, 1.05);
    tl.fromTo(["#d-d0", "#d-d1", "#d-d2"], { backgroundColor: "rgba(255,255,255,1)", borderColor: "rgba(221,216,204,1)", boxShadow: "0 14px 34px rgba(34,38,43,0.1)" },
      { backgroundColor: "rgba(255,255,255,0)", borderColor: "rgba(221,216,204,0)", boxShadow: "0 14px 34px rgba(34,38,43,0)", duration: 0.3, ease: "power1.in" }, 0.95);
    tl.fromTo("#d-dark", { opacity: 0 }, { opacity: 1, duration: 1.2, ease: "power1.inOut" }, 0.35);
    tl.fromTo("#d-c1", { color: "#22262B" }, { color: "#cfcac0", duration: 0.8 }, 0.6);
    const pe = document.querySelectorAll("#d-pts i");
    pe.forEach((el, k) => {
      const [y, a, b] = PTS[k];
      const t = 0.15 + Math.max(0, Math.min(1, 1 - (y - 586) / 724)) * 1.0 + a * 0.08;
      tl.fromTo(el, { opacity: 0, x: 0, y: 0 }, { opacity: 0.9, duration: 0.06, ease: "none" }, t);
      tl.to(el, { opacity: 0, x: (b - 0.5) * 120, y: -(260 + a * 520), duration: 0.9 + b * 0.4, ease: "power1.out" }, t + 0.06);
    });
    // 가운데 서명란 → 먹색 화면의 흰 서명란 하나
    tl.fromTo("#d-s1", { opacity: 1 }, { opacity: 0, duration: 0.3 }, 1.3);
    tl.fromTo("#d-hero", { opacity: 0, y: 465, scale: 0.37, transformOrigin: "490px 920px" }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "power3.inOut" }, 1.25);
    BLINK("#d-cur", 1.8, 4.0);
    // S2 f348–f419: 자막 2, 느린 푸시인 100→108%, 밑줄 은은한 발광
    tl.fromTo("#d-c2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, F(348));
    tl.fromTo("#d-push", { scale: 1, transformOrigin: "490px 960px" }, { scale: 1.08, duration: F(420) - F(348), ease: "none" }, F(348));
    tl.fromTo("#d-glow", { opacity: 0 }, { opacity: 1, duration: 2.0, ease: "power1.inOut" }, F(352));
""".replace("__PTS__", pts_js)
SLOTS.append(scene("dust", 300, 419, dust_css, dust_html, dust_js))

# ============================================================ C5 desk f420–f539
sheets = []
for k, (dx, dy, r) in enumerate([(-18, 22, -4), (14, 12, 3), (-6, 4, -1.5), (0, 0, 0.8)]):
    top = k == 3
    inner = ""
    if top:
        inner = "".join(
            f'<div style="position:absolute;left:40px;top:{40 + j * 92}px;font-size:26px;font-weight:800;color:#8b857a">제{j + 1}조</div>'
            + "".join(f'<div style="position:absolute;left:{130}px;top:{50 + j * 92 + m * 22}px;height:9px;border-radius:5px;width:{300 - m * 60 - (j * 23) % 50}px;background:#cfc8bb"></div>' for m in range(3))
            for j in range(4))
    sheets.append(f'<div style="position:absolute;left:{dx}px;top:{dy}px;width:560px;height:400px;background:#f4efe4;border:1px solid #d7cfbf;border-radius:4px;transform:rotate({r}deg);box-shadow:0 6px 14px rgba(40,25,10,0.25)">{inner}</div>')

desk_css = """
    #k-ink { background: #141414; }
    #k-c1 { top: 300px; font-size: 56px; font-weight: 800; color: #e9e3d6; }
    #k-c2 { top: 380px; font-size: 84px; color: #fbf9f4; }
    #k-scaled { position: absolute; inset: 0; transform: scale(1.08); transform-origin: 490px 960px; }
    #k-hlb { position: absolute; left: 160px; top: 858px; width: 660px; text-align: center; font-size: 46px; font-weight: 800; color: #fbf9f4; }
    #k-line { position: absolute; left: 160px; top: 958px; width: 660px; height: 4px; background: #fbf9f4; transform-origin: 50% 50%; }
    #k-glow { position: absolute; left: 150px; top: 946px; width: 680px; height: 28px; border-radius: 14px; background: radial-gradient(50% 50% at 50% 50%, rgba(224, 194, 126, 0.75), rgba(224, 194, 126, 0)); }
    #k-desk { opacity: 0; }
    .k-wall { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; background: radial-gradient(55% 45% at 88% 18%, rgba(255, 226, 180, 0.2), rgba(255, 226, 180, 0) 100%), linear-gradient(180deg, #1d1a17 0%, #2c261f 70%, #3a3027 100%); }
    .k-win { position: absolute; left: 760px; top: 90px; width: 300px; height: 560px; border: 10px solid #1b1714; background: linear-gradient(160deg, rgba(255, 238, 205, 0.45), rgba(255, 220, 170, 0.18)); }
    .k-win::before { content: ""; position: absolute; left: 50%; top: 0; bottom: 0; width: 10px; margin-left: -5px; background: #1b1714; }
    .k-win::after { content: ""; position: absolute; top: 50%; left: 0; right: 0; height: 10px; margin-top: -5px; background: #1b1714; }
    .k-beam { position: absolute; width: 220px; height: 1500px; background: linear-gradient(180deg, rgba(255, 228, 180, 0.22), rgba(255, 228, 180, 0)); filter: blur(22px); transform-origin: 50% 0; }
    .k-top { position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; background: repeating-linear-gradient(177deg, rgba(0, 0, 0, 0.07) 0 3px, rgba(0, 0, 0, 0) 3px 26px), linear-gradient(180deg, #8d6545 0%, #6b4a31 45%, #3f2a1b 100%); }
    .k-edge { position: absolute; left: 0; top: 957px; width: 1080px; height: 5px; background: linear-gradient(90deg, rgba(255, 214, 160, 0.35), rgba(255, 224, 176, 0.85) 70%, rgba(255, 214, 160, 0.5)); }
    .k-patch { position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; background: rgba(255, 222, 170, 0.16); clip-path: polygon(52% 0, 100% 0, 78% 100%, 18% 100%); filter: blur(10px); }
    #k-papers { position: absolute; left: 210px; top: 1080px; width: 560px; height: 420px; }
    #k-pen { position: absolute; left: 330px; top: 1120px; width: 420px; height: 160px; }
"""
desk_html = f'''    <div id="k-ink" class="full" data-layout-ignore></div>
    <div id="k-desk" class="full" data-layout-ignore>
      <div id="k-dolly" class="full">
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
    <div id="k-scaled" data-layout-ignore>
      <div id="k-hlb">법률 검토·책임자 서명:</div>
      <div id="k-glow"></div>
      <div id="k-line"></div>
    </div>
    <div id="k-c1" class="col">{words("그 자리엔 언제나")}</div>
    <div id="k-c2" class="col cap">법을 아는 사람이<br>있었습니다.</div>'''
desk_js = """
    // S1 f420–f464: 발광하는 밑줄이 수평으로 늘어나 책상 모서리 라인으로 (매치컷)
    tl.fromTo("#k-c1 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out", stagger: 0.067 }, 0.05);
    tl.fromTo("#k-hlb", { opacity: 1 }, { opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power2.in" }, 0.1);
    tl.fromTo("#k-line", { scaleX: 1 }, { scaleX: 1.62, duration: 1.0, ease: "power2.inOut" }, 0.3);
    tl.fromTo("#k-line", { backgroundColor: "#fbf9f4" }, { backgroundColor: "#ffdcae", duration: 1.0 }, 0.3);
    tl.fromTo("#k-desk", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power1.inOut" }, F(458));
    tl.to(["#k-line", "#k-glow"], { opacity: 0, duration: 0.25 }, F(464));
    // S2 f465–f539: 스톡 대체 일러스트. 슬로 돌리 인, 랙 포커스(서류 → 펜)
    tl.fromTo("#k-dolly", { scale: 1, transformOrigin: "490px 1150px" }, { scale: 1.09, duration: 4.0 - 1.4, ease: "none" }, 1.4);
    tl.fromTo("#k-papers", { filter: "blur(0px)" }, { filter: "blur(5px)", duration: 1.3, ease: "power2.inOut" }, F(490));
    tl.fromTo("#k-pen", { filter: "blur(5px)" }, { filter: "blur(0px)", duration: 1.3, ease: "power2.inOut" }, F(490));
    tl.fromTo("#k-c1", { color: "#e9e3d6" }, { color: "#bdb5a6", duration: 0.4 }, F(465));
    tl.fromTo("#k-c2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, F(465));
"""
SLOTS.append(scene("desk", 420, 539, desk_css, desk_html, desk_js))

# ============================================================ C6 sign f540–f719
OLD = "법률 검토·책임자 서명"
NEW = "그 칸으로 가는 첫 계단"
sign_css = """
    #s-paper { background: var(--noise), radial-gradient(70% 45% at 30% 58%, #fffaf0 0%, #f1e9da 70%, #e3d8c4 100%); }
    #s-ul { position: absolute; left: 120px; top: 998px; width: 740px; height: 4px; background: #2b2b2b; }
    #s-ink { position: absolute; left: 150px; top: 996px; width: 710px; height: 7px; border-radius: 4px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); transform-origin: 0 50%; box-shadow: 0 0 14px rgba(224, 194, 126, 0.7); }
    #s-pen { position: absolute; left: 136px; top: 414px; width: 640px; height: 640px; }
    #s-lb { top: 1036px; font-size: 54px; font-weight: 800; color: #2b2b2b; }
    #s-nl { top: 1032px; font-size: 62px; font-weight: 900; color: var(--ink); --acc: var(--gold-text); }
    #s-flash { background: #ffffff; opacity: 0; }
    #s-navy { background: linear-gradient(180deg, rgba(11, 26, 51, 0.96) 0%, rgba(11, 26, 51, 0.93) 58%, rgba(11, 26, 51, 0.8) 100%); opacity: 0; }
    #s-base { position: absolute; left: 230px; top: 568px; width: 520px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); box-shadow: 0 0 14px rgba(224, 194, 126, 0.55); }
    #s-u1 { top: 604px; font-size: 46px; font-weight: 800; color: var(--gold-light); }
    #s-u2 { top: 664px; font-size: 88px; font-weight: 900; color: #ffffff; letter-spacing: -0.05em; }
    #s-u3 { top: 782px; font-size: 40px; font-weight: 600; color: rgba(255, 255, 255, 0.9); }
    #s-br { top: 866px; display: flex; justify-content: center; align-items: center; gap: 14px; font-size: 38px; font-weight: 800; color: var(--gold-light); }
    #s-br img { width: 50px; height: 56px; }
"""
sign_html = f'''    <div id="s-world" class="full" data-layout-allow-overlap>
      <div id="s-paper" class="full" data-layout-ignore></div>
      <div id="s-ul" data-layout-ignore></div>
      <div id="s-ink" data-layout-ignore></div>
      <div id="s-pen" data-layout-ignore>{PEN_HAND.replace("@@", "s")}</div>
    </div>
    <div id="s-lb" class="col">{chars(OLD, "s-o")}</div>
    <div id="s-flash" class="full" data-layout-ignore></div>
    <div id="s-navy" class="full" data-layout-ignore></div>
    <div id="s-base" data-layout-ignore></div>
    <div id="s-nl" class="col" data-layout-allow-overlap>{chars(NEW, "s-n", acc_from=NEW.index("첫"))}</div>
    <div id="s-u1" class="col">국내 유일*</div>
    <div id="s-u2" class="col">100% 온라인 법학사</div>
    <div id="s-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="s-br" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>'''
sign_js = """
    const OLDN = __OLDN__, NEWN = __NEWN__;
    // S1 f540–f584: 매크로. 펜촉이 서명란 위 1cm에서 → 접촉 0.3초 슬로모 → f584 화이트 플래시
    tl.fromTo("#s-pen", { x: 170, y: -240, opacity: 0 }, { x: 0, y: -46, opacity: 1, duration: 0.7, ease: "power3.out" }, 0);
    tl.to("#s-pen", { y: -10, duration: F(575) - 0.7, ease: "power1.inOut" }, 0.7);
    tl.fromTo("#s-tip", { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1.25, duration: 0.12, ease: "power2.out" }, F(584));
    tl.to("#s-tip", { scale: 0.9, opacity: 0.85, duration: 0.3, ease: "power2.out" }, F(588));
    tl.to("#s-tip", { opacity: 0, duration: 0.25 }, F(626));
    tl.to("#s-pen", { y: 0, duration: F(584) - F(575), ease: "sine.inOut" }, F(575));
    tl.fromTo("#s-world", { scale: 1.0, transformOrigin: "200px 1000px" }, { scale: 1.05, duration: F(584), ease: "none" }, 0);
    tl.fromTo("#s-flash", { opacity: 0 }, { opacity: 0.95, duration: 2 / 30, ease: "none" }, F(582));
    tl.to("#s-flash", { opacity: 0, duration: 0.3, ease: "power2.out" }, F(585));
    // S2 f585–f629: 금빛 잉크 라인 트래킹 + 라벨 지우고 '그 칸으로 가는 첫 계단' 리타이핑(f600–)
    tl.fromTo("#s-ink", { scaleX: 0 }, { scaleX: 1, duration: F(627) - F(585), ease: "power1.inOut" }, F(585));
    tl.to("#s-pen", { x: 710, duration: F(627) - F(585), ease: "power1.inOut" }, F(585));
    for (let i = 0; i < OLDN; i++) tl.set("#s-o" + (OLDN - 1 - i), { opacity: 0 }, F(586) + i * (13 / 30) / OLDN);
    for (let i = 0; i < NEWN; i++) tl.fromTo("#s-n" + i, { opacity: 0 }, { opacity: 1, duration: 0.04, ease: "none" }, F(600) + i * (25 / 30) / NEWN);
    // S3 f630–f719: 잉크 라인이 위로 접혀 타이포 기단 → USP 스택(0.15s 간격) + 브랜드(f639)
    tl.fromTo("#s-navy", { opacity: 0 }, { opacity: 1, duration: 0.35, ease: "power2.inOut" }, F(630));
    tl.fromTo("#s-world", { filter: "blur(0px)" }, { filter: "blur(9px)", duration: 0.45, ease: "power2.out" }, F(630));
    tl.fromTo("#s-base", { opacity: 0, x: 15, y: 428, scaleX: 1.365 }, { opacity: 1, x: 0, y: 0, scaleX: 1, duration: 0.4, ease: "power3.inOut" }, F(630));
    tl.fromTo("#s-nl", { y: 0, scale: 1 }, { y: -580, scale: 0.82, duration: 0.4, ease: "power3.inOut" }, F(630));
    tl.fromTo("#s-nl", { color: "#161616", "--acc": "#7d6233" }, { color: "#fbf9f4", "--acc": "#e0c27e", duration: 0.3 }, F(630));
    IN("#s-u1", F(630), { y: 30 }, 0.22);
    IN("#s-u2", F(630) + 0.15, { y: 30 }, 0.24);
    IN("#s-u3", F(630) + 0.3, { y: 30 }, 0.22);
    IN("#s-br", F(639), { y: 24 }, 0.24);
""".replace("__OLDN__", str(len(OLD))).replace("__NEWN__", str(len(NEW)))
SLOTS.append(scene("sign", 540, 719, sign_css, sign_html, sign_js))

# ============================================================ C7 cross f720–f824
mini_cards = "".join(
    f'<div style="position:absolute;left:{30 + j * 16}px;top:{230 + j * 150}px;width:{300 - j * 32}px;height:200px;background:#f5f5f4;border:2px solid #d6d6d4;border-radius:14px">'
    + "".join(f'<div style="position:absolute;left:18px;top:{26 + m * 26}px;height:10px;border-radius:5px;width:{70 + (m * 29) % 30}%;background:#d0d0ce"></div>' for m in range(5))
    + "</div>" for j in range(3))
cross_css = """
    #c-dark { background: radial-gradient(70% 45% at 30% 58%, #fffaf0 0%, #f1e9da 70%, #e3d8c4 100%); }
    #c-dark::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(11, 26, 51, 0.96) 0%, rgba(11, 26, 51, 0.93) 58%, rgba(11, 26, 51, 0.8) 100%); }
    #c-paper { background: var(--noise), radial-gradient(60% 40% at 100% 100%, rgba(224, 194, 126, 0.25), rgba(224, 194, 126, 0)), var(--paper); }
    #c-u1 { top: 232px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #c-u2 { top: 266px; font-size: 44px; font-weight: 900; color: var(--navy); letter-spacing: -0.05em; }
    #c-u3 { top: 324px; font-size: 28px; font-weight: 600; color: #3c4250; }
    #c-br { top: 364px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #c-br img { width: 30px; height: 34px; }
    #c-cap { top: 448px; font-size: 80px; color: var(--navy); }
    .c-panel { position: absolute; top: 700px; width: 420px; height: 740px; border-radius: 28px; overflow: hidden; }
    #c-left { left: 60px; background: #e8e7e3; border: 2px solid #d3d2ce; }
    #c-right { left: 500px; background: linear-gradient(180deg, #fff8ea, #fbefd6); border: 2px solid var(--gold); }
    .c-lab { position: absolute; left: 0; right: 0; top: 34px; text-align: center; font-size: 38px; font-weight: 800; }
    #c-div { position: absolute; left: 487px; top: 680px; width: 6px; height: 780px; border-radius: 3px; background: linear-gradient(180deg, rgba(184, 149, 90, 0), #b8955a 20%, #e0c27e 50%, #b8955a 80%, rgba(184, 149, 90, 0)); }
    #c-hand { position: absolute; left: 225px; top: 1080px; width: 100px; height: 120px; }
    #c-exp { background: linear-gradient(180deg, #fff8ea, #fbefd6); clip-path: inset(700px 160px 480px 500px round 28px); }
    #c-pen2 { position: absolute; left: 420px; top: 760px; width: 140px; height: 140px; }
    #c-line2 { position: absolute; left: 210px; top: 1060px; width: 560px; height: 7px; border-radius: 4px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); }
    #c-sub { top: 1186px; font-size: 34px; font-weight: 700; color: #3c4250; }
    #c-btn { position: absolute; left: 130px; top: 1250px; width: 720px; height: 110px; border-radius: 999px; background: var(--navy); color: #fff; font-size: 44px; font-weight: 800; display: flex; align-items: center; justify-content: center; letter-spacing: -0.03em; box-shadow: 0 18px 40px rgba(11, 26, 51, 0.28); }
"""
cross_html = f'''    <div id="c-dark" class="full" data-layout-ignore></div>
    <div id="c-paper" class="full" data-layout-ignore></div>
    <div id="c-left" class="c-panel" data-layout-allow-overlap>
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
    <div id="c-u1" class="col">국내 유일*</div>
    <div id="c-u2" class="col">100% 온라인 법학사</div>
    <div id="c-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="c-br" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>
    <div id="c-cap" class="col cap">{words("서명하는 쪽으로")}<br>{words("넘어오세요.")}</div>
    <div id="c-sub" class="col">상담만 받아도 돼요.</div>
    <div id="c-btn">무료 상담 신청</div>'''
cross_js = """
    // S1 f720–f779: 컬러 플러드(네이비 → 페이퍼), USP·브랜드 상단으로 축소 이동, 스플릿 등장, 스와이프
    tl.fromTo("#c-paper", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.inOut" }, 0.02);
    [["#c-u1", 375, 1.77, "#e0c27e", "#7d6233"], ["#c-u2", 420, 2.0, "#ffffff", "#0b1a33"], ["#c-u3", 458, 1.54, "#ffffff", "#3c4250"], ["#c-br", 516, 1.46, "#e0c27e", "#7d6233"]]
      .forEach(([s, dy, sc, c0, c1]) => {
        tl.fromTo(s, { y: dy, scale: sc }, { y: 0, scale: 1, duration: 0.5, ease: "power3.inOut" }, 0.02);
        tl.fromTo(s, { color: c0 }, { color: c1, duration: 0.3, ease: "power2.inOut" }, 0.02);
      });
    tl.fromTo("#c-cap .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out", stagger: 0.067 }, 0.3);
    IN("#c-left", 0.4, { x: -50 }, 0.3);
    IN("#c-right", 0.46, { x: 50 }, 0.3);
    tl.fromTo("#c-div", { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.35, ease: "power3.out" }, 0.5);
    tl.fromTo("#c-hand", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }, 0.95);
    tl.fromTo("#c-hand", { x: 0 }, { x: 470, duration: 0.6, ease: "power2.inOut", immediateRender: false }, F(760));
    tl.fromTo("#c-hand", { filter: "blur(0px)" }, { filter: "blur(4px)", duration: 0.3, ease: "power2.in", immediateRender: false }, F(760));
    tl.to("#c-hand", { filter: "blur(0px)", duration: 0.3, ease: "power2.out" }, F(760) + 0.3);
    // S2 f780–f824: 오른쪽 패널 풀스크린, 버튼 '무료 상담 신청', 펄스 2회, '상담만 받아도 돼요.'
    tl.fromTo("#c-exp", { clipPath: "inset(700px 160px 480px 500px round 28px)" }, { clipPath: "inset(0px 0px 0px 0px round 0px)", duration: 0.5, ease: "power3.inOut" }, F(780));
    tl.fromTo("#c-pen2", { x: 220, y: 200 }, { x: 0, y: 0, duration: 0.5, ease: "power3.inOut" }, F(780));
    tl.fromTo("#c-line2", { x: 220, y: 410, scaleX: 0.54 }, { x: 0, y: 0, scaleX: 1, duration: 0.5, ease: "power3.inOut" }, F(780));
    OUT("#c-hand", F(780), {}, 0.15);
    IN("#c-btn", F(780), { y: 50 }, 0.26);
    IN("#c-sub", F(783), { y: 20 }, 0.2);
    [F(798), F(812)].forEach((t) => tl.fromTo("#c-btn", { scale: 1 }, { scale: 1.045, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t));
"""
SLOTS.append(scene("cross", 720, 824, cross_css, cross_html, cross_js))

# ============================================================ C8 end f825–f899
end_css = """
    #e-bg { background: linear-gradient(180deg, #fff8ea, #fbefd6); }
    #e-paper { background: var(--noise), radial-gradient(60% 40% at 100% 100%, rgba(224, 194, 126, 0.28), rgba(224, 194, 126, 0)), radial-gradient(60% 38% at 0% 0%, rgba(46, 92, 190, 0.06), rgba(46, 92, 190, 0)), var(--paper); }
    #e-m1 { top: 232px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #e-m2 { top: 266px; font-size: 44px; font-weight: 900; color: var(--navy); letter-spacing: -0.05em; }
    #e-m3 { top: 324px; font-size: 28px; font-weight: 600; color: #3c4250; }
    #e-m4 { top: 364px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 28px; font-weight: 800; color: var(--gold-text); }
    #e-m4 img { width: 30px; height: 34px; }
    #e-cap { top: 448px; font-size: 80px; color: var(--navy); }
    #e-pen { position: absolute; left: 420px; top: 760px; width: 140px; height: 140px; }
    #e-slo { top: 648px; font-size: 88px; line-height: 1.25; color: var(--navy); letter-spacing: -0.055em; }
    #e-ul { position: absolute; left: 160px; top: 892px; width: 660px; height: 8px; border-radius: 4px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); transform-origin: 0 50%; }
    #e-u1 { top: 960px; font-size: 46px; font-weight: 900; color: var(--navy); letter-spacing: -0.05em; }
    #e-u1 b { color: var(--gold-text); font-weight: 800; }
    #e-u3 { top: 1030px; font-size: 34px; font-weight: 600; color: #3c4250; }
    #e-br { top: 1112px; display: flex; justify-content: center; align-items: center; gap: 12px; font-size: 38px; font-weight: 800; color: var(--gold-text); }
    #e-br img { width: 40px; height: 45px; }
    #e-sub { top: 1186px; font-size: 34px; font-weight: 700; color: #3c4250; }
    #e-btn { position: absolute; left: 130px; top: 1250px; width: 720px; height: 110px; border-radius: 999px; background: var(--navy); color: #fff; font-size: 44px; font-weight: 800; display: flex; align-items: center; justify-content: center; letter-spacing: -0.03em; box-shadow: 0 18px 40px rgba(11, 26, 51, 0.28); }
    #e-tel { top: 1394px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 30px; font-weight: 700; color: var(--navy); letter-spacing: -0.02em; }
    #e-tel svg { width: 32px; height: 32px; }
"""
end_html = f'''    <div id="e-bg" class="full" data-layout-ignore></div>
    <div id="e-paper" class="full" data-layout-ignore></div>
    <div id="e-m1" class="col">국내 유일*</div>
    <div id="e-m2" class="col">100% 온라인 법학사</div>
    <div id="e-m3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="e-m4" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>
    <div id="e-cap" class="col cap">서명하는 쪽으로<br>넘어오세요.</div>
    <div id="e-pen" data-layout-ignore>{PEN_ICON}</div>
    <div id="e-slo" class="col cap">책임지는 자리로,<br>지금 있는 자리에서.</div>
    <div id="e-ul" data-layout-ignore></div>
    <div id="e-u1" class="col"><b>국내 유일*</b> 100% 온라인 법학사</div>
    <div id="e-u3" class="col">교육부장관 명의 · '법학 전공' 표기</div>
    <div id="e-br" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>
    <div id="e-sub" class="col">상담만 받아도 돼요.</div>
    <div id="e-btn">무료 상담 신청</div>
    <div id="e-tel" class="col">{PHONE}<span>070-4006-7128 (평일 10–18시)</span></div>'''
end_js = """
    // f825–f899: C7 패널 → 엔드카드. 서명 잉크 라인이 슬로건 밑줄로, 슬로건 좌→우 마스크 와이프(f825–f839)
    tl.fromTo("#e-paper", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power1.inOut" }, 0);
    OUT(["#e-cap", "#e-pen"], 0, { y: -30 }, 0.15);
    OUT(["#e-m1", "#e-m2", "#e-m3", "#e-m4"], 0.02, { y: -20 }, 0.16);
    tl.fromTo("#e-slo", { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: F(839) - F(825), ease: "power2.inOut" }, F(825));
    tl.fromTo("#e-ul", { x: 50, y: 168, scaleX: 0.85 }, { x: 0, y: 0, scaleX: 1, duration: 0.45, ease: "power3.inOut" }, 0);
    tl.fromTo("#e-ul", { boxShadow: "0 0 18px rgba(224,194,126,0.9)" }, { boxShadow: "0 0 0px rgba(224,194,126,0)", duration: 0.6 }, 0.45);
    IN("#e-u1", 0.15, { y: 26 }, 0.26);
    IN("#e-u3", 0.22, { y: 26 }, 0.26);
    IN("#e-br", 0.29, { y: 26 }, 0.26);
    IN("#e-tel", 0.0, { y: 16 }, 0.24);
"""
SLOTS.append(scene("end", 825, 899, end_css, end_html, end_js))

# ============================================================ overlay: 연출 + 고지 L1·L2
legal_css = """
    #root { pointer-events: none; }
    #l-tag { position: absolute; left: 48px; top: 1500px; }
    .l-d { position: absolute; left: 60px; width: 860px; text-align: center; font-size: 24px; font-weight: 600; letter-spacing: -0.02em; white-space: nowrap; }
    .l-d span { opacity: 0.85; color: #ffffff; }
"""
legal_html = '''    <div id="l-tag" class="clip" data-start="0" data-duration="8.5" data-track-index="1"><div id="l-tagi" class="tag">연출</div></div>
    <div id="l-d1" class="clip l-d" data-start="5.5" data-duration="9" data-track-index="2" style="top:1580px"><span id="l-d1i">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</span></div>
    <div id="l-d2" class="clip l-d" data-start="5.5" data-duration="9" data-track-index="3" style="top:1615px"><span id="l-d2i">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</span></div>'''
legal_js = """
    // 연출: f465–f719 (overlay 시작 15.5s 기준 0–8.5s). 고지 L1·L2: f630–f899 (5.5–14.5s)
    // 24.0s(C7)부터 밝은 배경 → 먹색 85%
    tl.fromTo(["#l-d1i", "#l-d2i"], { color: "#ffffff" }, { color: "#161616", duration: 0.15, ease: "none" }, 8.55);
"""
SLOTS.append(scene("legal", 465, 899, legal_css, legal_html, legal_js))

# ============================================================ 15초 버전 (§3 + 15초 컷씬 시트) — python3 tools/build.py --variant 15 → v15/
SLOTS15 = []

# C1' f0–f59: C1 S1과 동일, f45–f59 스냅 틸트 다운 + 줌. 자막 '딱 한 칸만 빼고.' f45–f95(C3'까지 유지)
hook15_js = """
    [[1, 7, -5], [2, -6, 4], [3, 4, 3], [4, -2, -2], [5, 0, 0]].forEach(([n, x, y]) => tl.set("#h-cam", { x, y }, F(n)));
    tl.fromTo(["#h-f0", "#h-f2", "#h-f1"], { y: -16 }, { y: 0, duration: 0.7, ease: "back.out(2.4)", stagger: 0.07 }, 0);
    tl.fromTo("#h-chip", { scale: 1.08 }, { scale: 1, duration: 0.35, ease: "power3.out" }, F(9));
    OUT("#h-head", F(45), { y: -140 }, 0.12);
    tl.fromTo("#h-world", { y: 0 }, { y: -2100, duration: 0.4, ease: "expo.inOut" }, F(45));
    tl.fromTo("#h-world", { filter: "blur(0px)" }, { filter: "blur(14px)", duration: 0.2, ease: "power2.in" }, F(45));
    tl.to("#h-world", { filter: "blur(0px)", duration: 0.2, ease: "power2.out" }, F(45) + 0.2);
    tl.fromTo("#h-plate", { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.16, ease: "power3.out" }, F(47));
    tl.fromTo("#h-cap .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power3.out", stagger: 0.05 }, F(48));
    tl.fromTo(["#h-s0", "#h-s1", "#h-s2"], { backgroundColor: "#eeece6" }, { backgroundColor: "#e1ebe3", duration: 0.2 }, F(54));
    ["#h-c0", "#h-c1", "#h-c2"].forEach((c) => BLINK(c, F(56), F(60)));
"""
SLOTS15.append(scene("hook", 0, 59, hook_css, hook_html, hook15_js, variant="15"))

# C3' f60–f149: 서명란 클로즈업 유지, '생성' 3연타(f75·f90·f97), 토스트, 비네팅. 자막은 f95까지
blank15_js = """
    tl.set("#b-cam", { y: -505 }, 0);
    tl.set(["#b-s0", "#b-s1", "#b-s2"], { backgroundColor: "#e1ebe3" }, 0);
    ["#b-c0", "#b-c1", "#b-c2"].forEach((c) => BLINK(c, 0, F(150)));
    OUT("#b-cap", F(96), {}, 0.1);
    IN("#b-btn", F(61), { y: 40 }, 0.2);
    tl.fromTo("#b-ptr", { opacity: 0, x: 140, y: 160 }, { opacity: 1, x: 0, y: 0, duration: 0.2, ease: "power3.out" }, F(64));
    [75, 90, 97].forEach((n, k) => {
      const t = F(n);
      tl.fromTo("#b-ptr", { scale: 1 }, { scale: 0.86, duration: 0.05, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t);
      tl.fromTo("#b-btn", { scale: 1 }, { scale: 0.94, duration: 0.05, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t);
      GLITCH("#b-cam", "#b-gl", t, k % 2 ? -18 : 18);
      [0, 1, 2].forEach((i) => { tl.set("#b-l" + i + "-" + k, { opacity: 0 }, t); tl.set("#b-l" + i + "-" + (k + 1), { opacity: 1 }, t); });
    });
    tl.fromTo("#b-toast", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }, F(102));
    tl.fromTo("#b-toast", { x: 0 }, { x: 10, duration: 0.04, yoyo: true, repeat: 3, ease: "none", immediateRender: false }, F(103));
    OUT(["#b-btn", "#b-ptr"], F(108), { y: 30 }, 0.16);
    tl.fromTo("#b-cam", { scale: 1, transformOrigin: "490px 1385px" }, { scale: 2.4, duration: 0.9, ease: "power3.inOut", immediateRender: false }, F(110));
    tl.to("#b-toast", { y: 168, duration: 0.9, ease: "power3.inOut" }, F(110));
    tl.fromTo("#b-vig", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.inOut" }, F(110));
"""
SLOTS15.append(scene("blank", 60, 149, blank_css, blank_html, blank15_js, variant="15"))

# C4' f150–f269: 'AI가 대신할수록,'(S1 1.4s) / '책임질 자리는 더 귀해집니다.'(S2 f192) / 브리지 '그 칸은, 법을 아는 사람의 몫'(S3 f249–f269)
dust15_css = dust_css + """
    #d-br1 { top: 300px; font-size: 56px; font-weight: 800; color: #e9e3d6; }
    #d-br2 { top: 380px; font-size: 84px; color: #fbf9f4; }
"""
dust15_html = dust_html.replace(words("AI가 일을 대신할수록,"), words("AI가 대신할수록,")) + """
    <div id="d-br1" class="col">그 칸은,</div>
    <div id="d-br2" class="col cap">법을 아는 사람의 몫</div>"""
dust15_js = """
    const PTS = __PTS__;
    tl.fromTo("#d-c1 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power3.out", stagger: 0.06 }, 0);
    [0, 1, 2].forEach((i) => tl.fromTo("#d-b" + i, { clipPath: "inset(0% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 100% 0%)", duration: 0.85, ease: "power1.in" }, 0.1));
    tl.fromTo(["#d-s0", "#d-s2"], { opacity: 1 }, { opacity: 0, duration: 0.25, ease: "power1.in" }, 0.05);
    tl.fromTo(["#d-t0", "#d-t1", "#d-t2", "#d-k0", "#d-k1", "#d-k2", "#d-d0 .wm", "#d-d1 .wm", "#d-d2 .wm", "#d-d0 .hd", "#d-d1 .hd", "#d-d2 .hd"], { opacity: 1 }, { opacity: 0, duration: 0.2 }, 0.85);
    tl.fromTo(["#d-d0", "#d-d1", "#d-d2"], { backgroundColor: "rgba(255,255,255,1)", borderColor: "rgba(221,216,204,1)", boxShadow: "0 14px 34px rgba(34,38,43,0.1)" },
      { backgroundColor: "rgba(255,255,255,0)", borderColor: "rgba(221,216,204,0)", boxShadow: "0 14px 34px rgba(34,38,43,0)", duration: 0.28, ease: "power1.in" }, 0.8);
    tl.fromTo("#d-dark", { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power1.inOut" }, 0.25);
    tl.fromTo("#d-c1", { color: "#22262B" }, { color: "#cfcac0", duration: 0.7 }, 0.5);
    document.querySelectorAll("#d-pts i").forEach((el, k) => {
      const [y, a, b] = PTS[k];
      const t = 0.1 + Math.max(0, Math.min(1, 1 - (y - 586) / 724)) * 0.85 + a * 0.07;
      tl.fromTo(el, { opacity: 0, x: 0, y: 0 }, { opacity: 0.9, duration: 0.06, ease: "none" }, t);
      tl.to(el, { opacity: 0, x: (b - 0.5) * 120, y: -(260 + a * 520), duration: 0.8 + b * 0.3, ease: "power1.out" }, t + 0.06);
    });
    tl.fromTo("#d-s1", { opacity: 1 }, { opacity: 0, duration: 0.25 }, 1.1);
    tl.fromTo("#d-hero", { opacity: 0, y: 465, scale: 0.37, transformOrigin: "490px 920px" }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.inOut" }, 1.05);
    BLINK("#d-cur", 1.6, 4.0);
    tl.fromTo("#d-c2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, F(192));
    tl.fromTo("#d-push", { scale: 1, transformOrigin: "490px 960px" }, { scale: 1.08, duration: F(270) - F(192), ease: "none" }, F(192));
    tl.fromTo("#d-glow", { opacity: 0 }, { opacity: 1, duration: 1.6, ease: "power1.inOut" }, F(196));
    // S3 f249–f269 브리지 타이포
    OUT(["#d-c1", "#d-c2"], F(249), {}, 0.12);
    IN("#d-br1", F(250), {}, 0.16);
    IN("#d-br2", F(252), {}, 0.18);
""".replace("__PTS__", pts_js)
SLOTS15.append(scene("dust", 150, 269, dust15_css, dust15_html, dust15_js, variant="15"))

# C6' f270–f359: 펜 접촉 f299 + 플래시 → 잉크·리타이핑(f300–f320) → USP 스택 f321 + 브랜드 f330
sign15_html = sign_html.replace("<div id=\"s-u3\" class=\"col\">교육부장관 명의 · '법학 전공' 표기</div>", '<div id="s-u3" class="col">· 교육부장관 명의</div>')
sign15_js = """
    const OLDN = __OLDN__, NEWN = __NEWN__;
    tl.fromTo("#s-pen", { x: 170, y: -240, opacity: 0 }, { x: 0, y: -46, opacity: 1, duration: 0.35, ease: "power3.out" }, 0);
    tl.to("#s-pen", { y: -10, duration: F(290) - 0.35, ease: "power1.inOut" }, 0.35);
    tl.to("#s-pen", { y: 0, duration: F(299) - F(290), ease: "sine.inOut" }, F(290));
    tl.fromTo("#s-world", { scale: 1.0, transformOrigin: "200px 1000px" }, { scale: 1.05, duration: F(299), ease: "none" }, 0);
    tl.fromTo("#s-flash", { opacity: 0 }, { opacity: 0.95, duration: 2 / 30, ease: "none" }, F(297));
    tl.to("#s-flash", { opacity: 0, duration: 0.25, ease: "power2.out" }, F(300));
    tl.fromTo("#s-tip", { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1.25, duration: 0.12, ease: "power2.out" }, F(299));
    tl.to("#s-tip", { scale: 0.9, opacity: 0.85, duration: 0.25, ease: "power2.out" }, F(303));
    tl.to("#s-tip", { opacity: 0, duration: 0.2 }, F(318));
    tl.fromTo("#s-ink", { scaleX: 0 }, { scaleX: 1, duration: F(319) - F(300), ease: "power1.inOut" }, F(300));
    tl.to("#s-pen", { x: 710, duration: F(319) - F(300), ease: "power1.inOut" }, F(300));
    for (let i = 0; i < OLDN; i++) tl.set("#s-o" + (OLDN - 1 - i), { opacity: 0 }, F(300) + i * (5 / 30) / OLDN);
    for (let i = 0; i < NEWN; i++) tl.fromTo("#s-n" + i, { opacity: 0 }, { opacity: 1, duration: 0.03, ease: "none" }, F(305) + i * (14 / 30) / NEWN);
    tl.fromTo("#s-navy", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.inOut" }, F(321));
    tl.fromTo("#s-world", { filter: "blur(0px)" }, { filter: "blur(9px)", duration: 0.4, ease: "power2.out" }, F(321));
    tl.fromTo("#s-base", { opacity: 0, x: 15, y: 428, scaleX: 1.365 }, { opacity: 1, x: 0, y: 0, scaleX: 1, duration: 0.35, ease: "power3.inOut" }, F(321));
    tl.fromTo("#s-nl", { y: 0, scale: 1 }, { y: -580, scale: 0.82, duration: 0.35, ease: "power3.inOut" }, F(321));
    tl.fromTo("#s-nl", { color: "#161616", "--acc": "#7d6233" }, { color: "#fbf9f4", "--acc": "#e0c27e", duration: 0.25 }, F(321));
    IN("#s-u1", F(321), { y: 30 }, 0.2);
    IN("#s-u2", F(321) + 0.12, { y: 30 }, 0.22);
    IN("#s-u3", F(321) + 0.24, { y: 30 }, 0.2);
    IN("#s-br", F(330), { y: 24 }, 0.22);
""".replace("__OLDN__", str(len(OLD))).replace("__NEWN__", str(len(NEW)))
SLOTS15.append(scene("sign", 270, 359, sign_css, sign15_html, sign15_js, variant="15"))

# C8' f360–f449: 압축 엔드카드 — 슬로건(f360–f374 와이프, 무음 자막), 버튼 펄스 2회, 전화, 브랜드, 고지. USP 반복 없음
end15_css = end_css + """
    #e-navy { background: linear-gradient(180deg, #0b1a33 0%, #0e1f3b 60%, #1c2a42 100%); }
    #e-xk { top: 458px; font-size: 51px; font-weight: 900; color: #fbf9f4; --acc: var(--gold-light); }
    #e-x1 { top: 604px; font-size: 46px; font-weight: 800; color: var(--gold-light); }
    #e-x2 { top: 664px; font-size: 88px; font-weight: 900; color: #ffffff; letter-spacing: -0.05em; }
    #e-x3 { top: 782px; font-size: 40px; font-weight: 600; color: rgba(255, 255, 255, 0.9); }
    #e-xb { top: 866px; display: flex; justify-content: center; align-items: center; gap: 14px; font-size: 38px; font-weight: 800; color: var(--gold-light); }
    #e-xb img { width: 50px; height: 56px; }
    #e-xl { position: absolute; left: 230px; top: 568px; width: 520px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #a07c3f, #e0c27e 55%, #b8955a); }
"""
end15_html = f'''    <div id="e-paper" class="full" data-layout-ignore></div>
    <div id="e-navy" class="full" data-layout-ignore></div>
    <div id="e-xk" class="col">{chars(NEW, "e-xn", acc_from=NEW.index("첫"))}</div>
    <div id="e-x1" class="col">국내 유일*</div>
    <div id="e-x2" class="col">100% 온라인 법학사</div>
    <div id="e-x3" class="col">· 교육부장관 명의</div>
    <div id="e-xb" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>
    <div id="e-xl" data-layout-ignore></div>
    <div id="e-slo" class="col cap">책임지는 자리로,<br>지금 있는 자리에서.</div>
    <div id="e-ul" data-layout-ignore></div>
    <div id="e-br" class="col"><img src="assets/img/mark-gold.svg" alt="">경찰복지사이버평생교육원</div>
    <div id="e-btn">무료 상담 신청</div>
    <div id="e-tel" class="col">{PHONE}<span>070-4006-7128 (평일 10–18시)</span></div>'''
end15_js = """
    OUT(["#e-xk", "#e-x1", "#e-x2", "#e-x3"], 0, { y: -30 }, 0.15);
    tl.fromTo("#e-navy", { clipPath: "inset(0% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 100% 0%)", duration: 0.28, ease: "power2.inOut" }, 0.02);
    OUT("#e-xl", 0, { scaleX: 0.6 }, 0.14);
    tl.fromTo("#e-xb", { y: 0 }, { y: 246, duration: 0.4, ease: "power3.inOut" }, 0);
    tl.fromTo("#e-xb", { opacity: 1 }, { opacity: 0, duration: 0.2 }, 0.2);
    tl.fromTo("#e-slo", { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: F(374) - F(360), ease: "power2.inOut" }, 0);
    tl.fromTo("#e-ul", { scaleX: 0 }, { scaleX: 1, duration: 0.42, ease: "power2.inOut" }, F(366));
    tl.fromTo("#e-ul", { boxShadow: "0 0 18px rgba(224,194,126,0.9)" }, { boxShadow: "0 0 0px rgba(224,194,126,0)", duration: 0.6 }, 0.45);
    IN("#e-br", 0.22, { y: 20 }, 0.24);
    IN("#e-btn", 0.12, { y: 50 }, 0.26);
    IN("#e-tel", 0.05, { y: 16 }, 0.24);
    [1.2, 1.7].forEach((t) => tl.fromTo("#e-btn", { scale: 1 }, { scale: 1.045, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t));
"""
SLOTS15.append(scene("end", 360, 449, end15_css, end15_html, end15_js, variant="15"))

# 상시 레이어: 연출 f270–f359, 고지 L1·L2 f321–f449
legal15_html = '''    <div id="l-tag" class="clip" data-start="0" data-duration="3" data-track-index="1"><div id="l-tagi" class="tag">연출</div></div>
    <div id="l-d1" class="clip l-d" data-start="1.7" data-duration="4.3" data-track-index="2" style="top:1580px"><span id="l-d1i">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</span></div>
    <div id="l-d2" class="clip l-d" data-start="1.7" data-duration="4.3" data-track-index="3" style="top:1615px"><span id="l-d2i">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</span></div>'''
legal15_js = """
    // 연출 f270–f359 (0–3.0s), 고지 L1·L2 f321–f449 (1.7–6.0s). f360(C8') 밝은 배경 → 먹색 85%
    tl.fromTo(["#l-d1i", "#l-d2i"], { color: "#ffffff" }, { color: "#161616", duration: 0.12, ease: "none" }, 3.12);
"""
SLOTS15.append(scene("legal", 270, 449, legal_css, legal15_html, legal15_js, variant="15"))


# ---------------------------------------------------------------- index.html
def write_index(SLOTS, TOTAL, note):
  hosts = []
  for cid, start, dur in SLOTS:
      z = 5 if cid == "legal" else 2
      hosts.append(f'''      <div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{start}" data-duration="{dur}" data-track-index="{2 if cid == 'legal' else 1}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: {z}"></div>''')

  index = f'''<!doctype html>
<html
  lang="ko"
  data-resolution="portrait"
  data-composition-variables='[
  {{"id":"color-ground","type":"color","label":"Paper","default":"#FBF9F4"}},
  {{"id":"color-ink","type":"color","label":"Ink","default":"#161616"}},
  {{"id":"color-accent","type":"color","label":"Gold","default":"#B8955A"}},
  {{"id":"font-display","type":"string","label":"Display font","default":"PretendardGOV"}}
]'
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        margin: 0;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #161616;
      }}
    </style>
  </head>
  <body>
    <!-- {note} -->
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="{TOTAL:g}"
      data-width="1080"
      data-height="1920"
    >
{chr(10).join(hosts)}

      <!-- 사운드 베드(음악 + SFX, 합성). tools/make_audio.py. 내레이션은 추후 녹음 후 별도 <audio id="vo"> 로 추가 -->
      <audio id="bed" class="clip" src="assets/audio/bed.mp3" data-start="0" data-duration="{TOTAL:g}" data-track-index="10" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
  open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)
  for s in SLOTS:
      print(s)



if VARIANT == "30":
    write_index(SLOTS, 30.0, "「마지막 서명」 30초 · docs/ads/naver-clip/01-last-signature.md §4 컷씬 시트 기준. tools/build.py 가 생성")
else:
    write_index(SLOTS15, 15.0, "「마지막 서명」 15초 · docs/ads/naver-clip/01-last-signature.md §3 + 15초 컷씬 시트 기준. tools/build.py --variant 15 가 생성")
    # v15/ 는 독립 프로젝트(check 가 진입 파일을 고를 수 없어서). 에셋은 상위에서 복사
    for sub in ("fonts", "img", "audio"):
        os.makedirs(os.path.join(OUT, "assets", sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "img", "mark-gold.svg"), os.path.join(OUT, "assets", "img", "mark-gold.svg"))
    shutil.copy(os.path.join(ROOT, "assets", "fonts", "PretendardGOV-subset.woff2"), os.path.join(OUT, "assets", "fonts", "PretendardGOV-subset.woff2"))
    bed15 = os.path.join(ROOT, "assets", "audio", "bed-15s.mp3")
    if os.path.exists(bed15):
        shutil.copy(bed15, os.path.join(OUT, "assets", "audio", "bed.mp3"))
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(OUT, "hyperframes.json"))
    json.dump({"id": "naver-clip-signature-15s", "name": "naver-clip-signature-15s", "createdAt": "2026-11-02T00:00:00.000Z"},
              open(os.path.join(OUT, "meta.json"), "w"), indent=2)
