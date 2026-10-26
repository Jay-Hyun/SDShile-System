"""v4 scene generator: one change per beat, steady camera, no bounce.

Usage: python3 tools/build_scenes.py   (run from the project root)
Writes compositions/*.html and the scene hosts in index.html from the beat grid
in beats/assets/music/bgm.mp3.json.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = open(os.path.join(ROOT, "tools", "common.css")).read()
BEATS = [b["time"] for b in json.load(open(os.path.join(ROOT, "beats/assets/music/bgm.mp3.json")))["beats"]]
BEATS[0] = 0.0
TOTAL = 28.0

# Eye line: every hero word lands on this vertical band so the eye never hunts.
EYE = 700

CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" /></svg>'
XMARK = '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="#ff5a4e" stroke-width="3.2" stroke-linecap="round" /></svg>'

# Shared motion vocabulary. Arrivals land on the beat and stay still; nothing overshoots.
HELPERS = r"""
    const D = __DUR__;
    const B = __BEATS__;
    // 등장: 블러 → 선명, 짧고 정확하게. 오버슈트 없음
    function IN(sel, t, from, dur) {
      const f = Object.assign({ opacity: 0, filter: "blur(12px)" }, from || {});
      const to = { opacity: 1, filter: "blur(0px)", duration: dur || 0.16, ease: "power3.out" };
      for (const k in f) if (!(k in to)) to[k] = k.startsWith("scale") ? 1 : 0;
      tl.fromTo(sel, f, to, t);
    }
    // 퇴장: 다음 비트 직전에 짧게 빠짐
    function OUT(sel, t, to) {
      tl.to(sel, Object.assign({ opacity: 0, filter: "blur(10px)", duration: 0.07, ease: "power2.in" }, to || {}), t - 0.07);
    }
    // 카메라: 씬 내내 한 방향으로 천천히 다가감 (펌프·흔들림 없음)
    tl.fromTo(CAM, { scale: 1 }, { scale: 1.06, duration: __CAMD__, ease: "none" }, 0);
    tl.fromTo(BG, { scale: 1.08 }, { scale: 1, duration: D, ease: "none" }, 0);
"""


def L(i, start):
    return round(BEATS[i] - start, 3)


def scene(cid, a, b, css, html, js, bg="", cam_tail=0.0):
    start = BEATS[a]
    end = TOTAL if b is None else BEATS[b]
    local = {i: L(i, start) for i in range(len(BEATS)) if start - 1e-6 <= BEATS[i] < end - 1e-6}
    helpers = (HELPERS.replace("__DUR__", str(round(end - start, 3)))
               .replace("__CAMD__", str(round(end - start - cam_tail, 3)))
               .replace("__BEATS__", json.dumps({str(k): v for k, v in local.items()})))
    s = f'''<template>
  <style>
{COMMON}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-bg" class="bgl" data-layout-ignore>{bg}</div>
    <div id="{cid}-cam" class="cam" data-layout-allow-overlap>
{html}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const CAM = "#{cid}-cam", BG = "#{cid}-bg";
{helpers}
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
'''
    open(os.path.join(ROOT, "compositions", cid + ".html"), "w").write(s)
    return (cid, round(start, 3), round(end - start, 3))


SLOTS = []

# ---------- poster B0–B3 ----------
# AI가 준 답을 믿어도 되는지 아는 사람 = 법학 전공. 그 아래 왜 여기인지의 근거.
SLOTS.append(scene("poster", 0, 3, f"""
    #root {{ color: #ffffff; background: #0b1a33; }}
    #po-grid {{ position: absolute; inset: 0; }}
    .gl {{ stroke: rgba(255, 255, 255, 0.3); stroke-width: 2; }}
    .gh {{ fill: #ffffff; }}
    #po-alert {{ top: 190px; display: flex; justify-content: center; }}
    #po-alert div {{ height: 70px; padding: 0 30px; border-radius: 999px; background: #ff5a4e; color: #fff; font-size: 36px; font-weight: 900; display: flex; align-items: center; gap: 14px; letter-spacing: -0.02em; }}
    #po-alert i {{ width: 14px; height: 14px; border-radius: 50%; background: #fff; }}
    #po-l1 {{ top: 320px; font-size: 76px; font-weight: 800; color: rgba(255, 255, 255, 0.7); white-space: nowrap; }}
    #po-l2 {{ top: 420px; font-size: 92px; font-weight: 900; white-space: nowrap; }}
    #po-l3 {{ top: 535px; font-size: 150px; font-weight: 900; line-height: 1; color: #f0d595; white-space: nowrap; }}
    #po-ans {{ top: 715px; font-size: 56px; font-weight: 800; letter-spacing: 0.02em; }}
    #po-only {{ top: 820px; display: flex; justify-content: center; }}
    #po-only div {{ height: 112px; padding: 0 40px; border-radius: 28px; background: #fbf9f4; color: #0b1a33; font-size: 56px; font-weight: 900; display: flex; align-items: center; gap: 14px; letter-spacing: -0.04em; }}
    #po-only b {{ color: #2e5cbe; }}
    #po-only sup {{ font-size: 34px; color: #2e5cbe; align-self: flex-start; margin-top: 22px; }}
    #po-pts {{ top: 960px; display: flex; justify-content: center; gap: 14px; }}
    .pt {{ height: 84px; padding: 0 26px; border-radius: 22px; background: rgba(255, 255, 255, 0.14); border: 2px solid rgba(255, 255, 255, 0.4); font-size: 38px; font-weight: 800; display: flex; align-items: center; gap: 10px; letter-spacing: -0.03em; white-space: nowrap; }}
    .pt img {{ width: 40px; height: 40px; }}
    #po-cta {{ top: 1090px; font-size: 46px; font-weight: 900; color: #f0d595; }}
    #po-fine {{ top: 1262px; font-size: 30px; font-weight: 500; line-height: 1.3; color: rgba(255, 255, 255, 0.78); letter-spacing: -0.02em; }}
""", """      <svg id="po-grid" viewBox="0 0 1080 1920" data-layout-ignore>
        <line class="gl" x1="60" y1="0" x2="60" y2="1920" />
        <line class="gl" x1="1020" y1="0" x2="1020" y2="1920" />
        <line class="gl" x1="0" y1="525" x2="1080" y2="525" />
        <line class="gl" x1="0" y1="700" x2="1080" y2="700" />
        <rect class="gh" x="52" y="517" width="16" height="16" />
        <rect class="gh" x="1012" y="517" width="16" height="16" />
        <rect class="gh" x="52" y="692" width="16" height="16" />
        <rect class="gh" x="1012" y="692" width="16" height="16" />
      </svg>
      <div id="po-alert" class="stage"><div><i></i>11/10 접수 마감 · 11/4 개강</div></div>
      <div id="po-l1" class="stage">AI가 답을 줄 때,</div>
      <div id="po-l2" class="stage">그 답을 믿어도 되는지</div>
      <div id="po-l3" class="stage">아는 사람.</div>
      <div id="po-ans" class="stage">— 법학 전공</div>
      <div id="po-only" class="stage"><div>평생교육원 중 법학 전공 <b>단 1곳</b><sup>*</sup></div></div>
      <div id="po-pts" class="stage">
        <div class="pt"><img src="assets/img/moe-emblem.svg" alt="" />교육부장관 명의 학사</div>
        <div class="pt">일하면서 100% 온라인</div>
      </div>
      <div id="po-cta" class="stage">부담 없는 상담 · 070-4006-7128</div>
      <div id="po-fine" class="stage">* 전공필수(물권법·채권총칙) 개설 평생교육원 기준, 2026.10 조회<br />입학·합격·취업을 보장하지 않습니다.</div>""", """
    // 첫 프레임 = 완성 포스터(썸네일). 카메라만 천천히, 마지막에 '아는 사람' 속으로
    tl.to(CAM, { scale: 3.2, opacity: 0, filter: "blur(16px)", duration: 0.3, ease: "power3.in", transformOrigin: "50% 32%" }, D - 0.3);
""", bg='<div class="mesh"></div>', cam_tail=0.3))

# ---------- why B3–B9 ----------
# 장면: 계약서는 AI가 금방 쓰지만, 서명하는 손은 망설인다 → 그 망설임을 확신으로, 법학 전공
SLOTS.append(scene("far", 3, 9, f"""
    #root {{ color: #0b1a33; background: var(--noise), var(--pat-ruled), var(--paper-tone); }}
    .ta {{ top: {EYE - 70}px; font-size: 80px; font-weight: 800; color: #6b6660; white-space: nowrap; }}
    .tb {{ top: {EYE + 50}px; font-size: 112px; font-weight: 900; white-space: nowrap; }}
    #fa-mesh {{ position: absolute; inset: 0; }}
    #fa-a3 {{ color: rgba(255, 255, 255, 0.9); }}
    #fa-b3 {{ top: {EYE + 40}px; font-size: 200px; line-height: 1; color: #f0d595; }}
""", """      <div id="fa-a1" class="stage ta">계약서 한 장,</div>
      <div id="fa-b1" class="stage tb">AI는 금방 씁니다.</div>
      <div id="fa-a2" class="stage ta" data-layout-allow-overlap>그런데 서명하는 손은</div>
      <div id="fa-b2" class="stage tb" data-layout-allow-overlap>여전히 망설이죠.</div>
      <div id="fa-mesh" class="mesh" data-layout-ignore></div>
      <div id="fa-a3" class="stage ta" data-layout-allow-overlap>그 망설임을 확신으로,</div>
      <div id="fa-b3" class="stage tb" data-layout-allow-overlap>법학 전공.</div>""", """
    // B3 계약서 한 장, · B4 AI는 금방 씁니다. · B5 그런데 서명하는 손은 · B6 여전히 망설이죠. · B7 그 망설임을 확신으로, · B8 법학 전공.
    IN("#fa-a1", B[3], { y: 24 }, 0.2);
    IN("#fa-b1", B[4], { y: 30 });
    OUT(["#fa-a1", "#fa-b1"], B[5], { y: -60 });
    IN("#fa-a2", B[5], { y: 24 }, 0.2);
    IN("#fa-b2", B[6], { y: 30 });
    // B7: 화면이 그라데이션으로 바뀌며 답
    tl.fromTo("#fa-mesh", { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.16, ease: "power3.inOut" }, B[7] - 0.1);
    OUT(["#fa-a2", "#fa-b2"], B[7], { y: -60 });
    IN("#fa-a3", B[7], { y: 24 }, 0.2);
    IN("#fa-b3", B[8], { scale: 1.15, filter: "blur(16px)" }, 0.22);
    OUT(CAM, D, {});
"""))

# ---------- who B9–B15 ----------
items = ["직장인", "비전공자", "수험생", "로스쿨 준비생"]
LH = 130
SLOTS.append(scene("who", 9, 15, f'''
    #root {{ color: #0b1a33; background: var(--noise), var(--pat-dots), var(--paper-tone); }}
    #wh-label {{ top: {EYE - 210}px; font-size: 60px; font-weight: 800; color: #6b6660; }}
    #wh-row {{ position: absolute; left: 0; width: 1080px; top: {EYE - LH}px; height: {LH * 3}px; }}
    #wh-box {{ position: absolute; left: 170px; top: {LH + 13}px; width: 104px; height: 104px; border-radius: 22px; background: #2e5cbe; display: flex; align-items: center; justify-content: center; }}
    #wh-box svg {{ width: 70px; height: 70px; }}
    #wh-list {{ position: absolute; left: 310px; top: 0; }}
    .wi {{ height: {LH}px; font-size: 100px; font-weight: 900; line-height: {LH}px; white-space: nowrap; }}
    #wh-ok {{ top: {EYE + 20}px; white-space: nowrap; font-size: 130px; font-weight: 900; line-height: 1; }}
    #wh-ok b {{ color: #2e5cbe; }}
    #wh-sub {{ top: {EYE + 250}px; font-size: 56px; font-weight: 800; }}
''', f'''      <div id="wh-label" class="stage">지금 내 자리에서</div>
      <div id="wh-row" data-layout-allow-overflow data-layout-allow-overlap>
        <div id="wh-box">{CHECK}</div>
        <div id="wh-list">{''.join(f'<div class="wi" id="wh-i{i}">{t}</div>' for i, t in enumerate(items))}</div>
      </div>
      <div id="wh-ok" class="stage" data-layout-allow-overlap>출발선은 <b>같아요.</b></div>
      <div id="wh-sub" class="stage">법을 처음 배워도 괜찮아요</div>''', f'''
    // B9 체크 + 직장인 · B10 비전공자 · B11 수험생 · B12 로스쿨 준비생 · B13 누구나 OK · B14 서브
    const LH = {LH};
    IN("#wh-label", B[9], {{ y: -20 }});
    IN("#wh-box", B[9], {{ scale: 0.6 }}, 0.14);
    tl.fromTo("#wh-box svg path", {{ strokeDasharray: "24 24", strokeDashoffset: 24 }}, {{ strokeDashoffset: 0, duration: 0.16, ease: "power2.out" }}, B[9] + 0.08);
    tl.set("#wh-list", {{ y: LH }}, 0);
    tl.fromTo(".wi", {{ opacity: 0 }}, {{ opacity: 0, duration: 0.01 }}, 0);
    tl.fromTo("#wh-i1", {{ opacity: 0 }}, {{ opacity: 0.16, duration: 0.01 }}, 0);
    [9, 10, 11, 12].forEach((b, i) => {{
      if (i > 0) tl.to("#wh-list", {{ y: LH - i * LH, duration: 0.16, ease: "power3.out" }}, B[b]);
      tl.to(`#wh-i${{i}}`, {{ opacity: 1, duration: 0.1 }}, B[b]);
      if (i > 0) tl.to(`#wh-i${{i - 1}}`, {{ opacity: 0.16, duration: 0.1 }}, B[b]);
      if (i > 1) tl.to(`#wh-i${{i - 2}}`, {{ opacity: 0, duration: 0.1 }}, B[b]);
      if (i > 0 && i < 3) tl.to(`#wh-i${{i + 1}}`, {{ opacity: 0.16, duration: 0.1 }}, B[b]);
    }});
    // B13: 리스트가 한 줄로 모이며 같은 자리에 '누구나 OK'
    OUT(["#wh-row", "#wh-label"], B[13], {{ scaleY: 0.3 }});
    IN("#wh-ok", B[13], {{ scale: 1.1 }});
    IN("#wh-sub", B[13] + 0.12, {{ y: 30 }});
    OUT(CAM, D, {{}});
'''))

# ---------- online B15–B21 ----------
SLOTS.append(scene("online", 15, 21, f'''
    #root {{ color: #ffffff; background: var(--noise), var(--pat-dots), var(--paper-tone); }}
    .q {{ top: {EYE}px; font-size: 230px; font-weight: 900; line-height: 1; }}
    .x {{ position: absolute; left: 290px; top: {EYE - 135}px; width: 500px; height: 500px; }}
    #on-t1 {{ top: {EYE - 330}px; font-size: 130px; font-weight: 900; }}
    #on-t2 {{ top: {EYE + 350}px; font-size: 130px; font-weight: 900; }}
    .oc {{ position: absolute; top: {EYE - 150}px; width: 340px; height: 420px; border-radius: 34px; background: #fbf9f4; color: #0b1a33; box-shadow: 0 30px 70px rgba(11, 26, 51, 0.45); padding: 34px 30px; letter-spacing: -0.03em; }}
    #on-c1 {{ left: 80px; }}
    #on-c2 {{ left: 370px; z-index: 2; }}
    #on-c3 {{ left: 660px; }}
    .oc small {{ display: block; font-size: 30px; font-weight: 700; color: #7d6233; }}
    .oc b {{ display: block; margin-top: 12px; font-size: 52px; font-weight: 900; line-height: 1.12; }}
    .oc .bar {{ position: absolute; left: 30px; right: 30px; bottom: 44px; height: 14px; border-radius: 7px; background: #e8e2d6; overflow: hidden; }}
    .oc .bar i {{ display: block; width: 100%; height: 100%; background: linear-gradient(90deg, #2e5cbe, #e0c27e); transform-origin: 0 50%; }}
    .oc .ic {{ position: absolute; left: 30px; bottom: 90px; font-size: 30px; font-weight: 800; color: #2e5cbe; }}
    #on-pill {{ top: {EYE + 540}px; display: flex; justify-content: center; }}
    #on-pill div {{ height: 80px; padding: 0 38px; border-radius: 999px; background: #0b1a33; color: #f0d595; font-size: 42px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }}
''', f'''      <div id="on-q1" class="stage q">퇴사?</div>
      <svg id="on-x1" class="x" viewBox="0 0 24 24" data-layout-ignore><path d="M5 5l14 14M19 5L5 19" stroke="#ff5a4e" stroke-width="2.2" stroke-linecap="round" /></svg>
      <div id="on-q2" class="stage q" data-layout-allow-overlap>재입학?</div>
      <svg id="on-x2" class="x" viewBox="0 0 24 24" data-layout-ignore><path d="M5 5l14 14M19 5L5 19" stroke="#ff5a4e" stroke-width="2.2" stroke-linecap="round" /></svg>
      <div id="on-t1" class="stage">퇴근 후,</div>
      <div id="on-c1" class="oc"><small>평일 밤</small><b>민법총칙<br />3주차</b><div class="ic">▶ 수강 중</div><div class="bar"><i id="on-b1"></i></div></div>
      <div id="on-c2" class="oc"><small>주말</small><b>형법<br />몰아보기</b><div class="ic">▶ 2강 연속</div><div class="bar"><i id="on-b2"></i></div></div>
      <div id="on-c3" class="oc"><small>이동 중</small><b>헌법<br />복습</b><div class="ic">▶ 모바일</div><div class="bar"><i id="on-b3"></i></div></div>
      <div id="on-t2" class="stage">온라인으로.</div>
      <div id="on-pill" class="stage"><div>오프라인 수업 0회</div></div>''', '''
    // B15 퇴사? · B16 ✕ 그어짐 · B17 재입학? · B18 ✕ · B19 퇴근 후 [카드] 온라인으로 · B20 오프라인 0회
    tl.fromTo(BG, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.14, ease: "power3.inOut" }, 0);
    IN("#on-q1", B[15], { x: 120 });
    tl.fromTo("#on-x1 path", { strokeDasharray: "20 20", strokeDashoffset: 20 }, { strokeDashoffset: 0, duration: 0.14, ease: "power2.out" }, B[16]);
    OUT(["#on-q1", "#on-x1"], B[17], { x: -160 });
    IN("#on-q2", B[17], { x: 160 });
    tl.fromTo("#on-x2 path", { strokeDasharray: "20 20", strokeDashoffset: 20 }, { strokeDashoffset: 0, duration: 0.14, ease: "power2.out" }, B[18]);
    OUT(["#on-q2", "#on-x2"], B[19], { x: -160 });
    // B19: 문장이 위아래로 벌어지고 그 사이로 카드
    IN("#on-t1", B[19], { y: 300 });
    IN("#on-t2", B[19], { y: -300 });
    tl.fromTo("#on-c1", { opacity: 0, y: 160, rotation: -8 }, { opacity: 1, y: 30, rotation: -8, duration: 0.22, ease: "power3.out" }, B[19] + 0.04);
    tl.fromTo("#on-c2", { opacity: 0, y: 160 }, { opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }, B[19] + 0.08);
    tl.fromTo("#on-c3", { opacity: 0, y: 160, rotation: 8 }, { opacity: 1, y: 30, rotation: 8, duration: 0.22, ease: "power3.out" }, B[19] + 0.12);
    tl.fromTo(["#on-b1", "#on-b2", "#on-b3"], { scaleX: 0.05 }, { scaleX: 0.7, duration: 0.8, ease: "power2.inOut", stagger: 0.06 }, B[19] + 0.1);
    IN("#on-pill div", B[20] - 0.2, { y: 30 });
    OUT(CAM, D, {});
''', bg='<div class="mesh scan"></div>'))

# ---------- degree B21–B27 ----------
SLOTS.append(scene("degree", 21, 27, f'''
    #root {{ color: #0b1a33; background: var(--noise), var(--pat-guilloche), var(--paper-tone); }}
    #dg-t {{ top: {EYE}px; font-size: 160px; font-weight: 900; }}
    #dg-t .b {{ color: #2e5cbe; }}
    #dg-cert {{ position: absolute; left: 260px; top: 470px; width: 560px; height: 680px; background: #fffdf8; color: #161616; border: 3px solid #b8955a; outline: 2px solid #b8955a; outline-offset: -18px; box-shadow: 0 40px 90px rgba(11, 26, 51, 0.25); padding: 58px 52px 0; text-align: center; letter-spacing: -0.03em; }}
    .dc-no {{ font-size: 30px; color: #6b6660; text-align: left; }}
    .dc-title {{ font-size: 70px; font-weight: 800; letter-spacing: 0.4em; margin: 20px 0 30px 0.4em; }}
    .dc-field {{ font-size: 32px; font-weight: 600; text-align: left; line-height: 1.75; }}
    .dc-field b {{ color: #7d6233; font-weight: 800; }}
    .dc-body {{ margin-top: 18px; font-size: 30px; line-height: 1.5; color: #3a3732; text-align: left; }}
    .dc-sign {{ position: absolute; left: 0; right: 0; bottom: 58px; font-size: 40px; font-weight: 800; letter-spacing: 0.08em; }}
    #dg-stamp {{ position: absolute; right: 60px; bottom: 40px; width: 96px; height: 96px; }}
    #dg-mark {{ position: absolute; left: 50%; top: 44%; width: 360px; margin-left: -180px; text-align: center; font-size: 120px; font-weight: 900; color: rgba(184, 149, 90, 0.16); letter-spacing: 0.2em; transform: rotate(-18deg); }}
    #dg-sub {{ top: 1190px; font-size: 50px; font-weight: 800; }}
    #dg-sub .g {{ color: #7d6233; font-size: 64px; font-weight: 900; }}
''', '''      <div id="dg-t" class="stage"><span class="w" id="dg-w1">학위는</span> <span class="w b" id="dg-w2">진짜.</span></div>
      <div id="dg-cert">
        <div class="dc-no">예시 · 제 2026-0000000 호</div>
        <div class="dc-title">학위증</div>
        <div class="dc-field">성&nbsp;&nbsp;&nbsp;명&nbsp;&nbsp;홍길동</div>
        <div class="dc-field">전&nbsp;&nbsp;&nbsp;공&nbsp;&nbsp;<b>법학 전공(학사)</b></div>
        <div class="dc-body">위 사람은 「학점인정 등에 관한 법률」 제9조에 따라 법학사의 학위를 수여합니다.</div>
        <div class="dc-sign">교육부장관</div>
        <img id="dg-stamp" src="assets/img/moe-emblem.svg" alt="" />
        <div id="dg-mark">예시</div>
      </div>
      <div id="dg-sub" class="stage"><span class="w" id="dg-s1">교육부장관 명의</span> <span class="w g" id="dg-s2">법학사</span></div>''', '''
    // B21 학위는 · B22 진짜. · B23 학위증 · B24 직인 · B25 교육부장관 명의 · B26 법학사
    // '학위는'이 혼자일 땐 정중앙, '진짜.'가 붙으면 함께 중앙 정렬
    tl.set("#dg-w1", { x: 170 }, 0);
    IN("#dg-w1", B[21], { scale: 2.2, filter: "blur(24px)" }, 0.26);
    tl.to("#dg-w1", { x: 0, duration: 0.16, ease: "power3.out" }, B[22]);
    IN("#dg-w2", B[22], { x: 60 });
    // B23: 제목이 위로 밀려나며 그 자리로 학위증이 올라옴 (시선은 그대로 아래→위)
    tl.to("#dg-t", { y: 250 - 700, scale: 0.875, duration: 0.3, ease: "power3.inOut" }, B[23] - 0.04);
    tl.fromTo("#dg-cert", { opacity: 0, y: 520 }, { opacity: 1, y: 0, duration: 0.32, ease: "power3.out" }, B[23]);
    IN("#dg-stamp", B[24], { scale: 1.6 }, 0.12);
    IN("#dg-s1", B[24] + 0.14, { y: 30 });
    IN("#dg-s2", B[25], { y: 30 });
    OUT(CAM, D, {});
'''))

# ---------- together B27–B33 ----------
chips = [("퇴근 후 1시간", 110, 250, -6), ("주말 집중 플랜", 610, 220, 5), ("진도 체크", 90, 400, 4),
         ("시험 대비", 730, 380, -5), ("과목 추천", 200, 540, -3), ("맞춤 일정", 640, 530, 4)]
SLOTS.append(scene("together", 27, 33, f'''
    #root {{ color: #ffffff; background: var(--noise), var(--pat-stars), var(--ink-tone); }}
    #tg-q {{ top: {EYE}px; font-size: 150px; font-weight: 900; line-height: 1; white-space: nowrap; color: rgba(255, 255, 255, 0.62); }}
    #tg-line {{ top: {EYE + 180}px; font-size: 150px; font-weight: 900; line-height: 1; white-space: nowrap; }}
    #tg-yes {{ color: #f0d595; }}
    #tg-badge {{ top: {EYE + 400}px; display: flex; justify-content: center; }}
    #tg-badge div {{ height: 92px; padding: 0 40px; border-radius: 999px; background: radial-gradient(circle at 30% 30%, #fff2c9, #e0c27e 50%, #b8955a 100%); color: #0b1a33; font-size: 46px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.03em; }}
    #tg-sub {{ top: {EYE + 520}px; font-size: 48px; font-weight: 800; color: rgba(255, 255, 255, 0.88); }}
    .chip {{ position: absolute; height: 84px; padding: 0 30px; border-radius: 22px; background: rgba(255, 255, 255, 0.08); border: 2px solid rgba(255, 255, 255, 0.22); font-size: 38px; font-weight: 800; display: flex; align-items: center; white-space: nowrap; letter-spacing: -0.03em; }}
''', '''      <div id="tg-q" class="stage">공부는 혼자,</div>
      <div id="tg-line" class="stage">계획은 <span id="tg-yes">같이.</span></div>
      <div id="tg-badge" class="stage"><div>1:1 학습플래너</div></div>
      <div id="tg-sub" class="stage">내 일정에 맞춰 짜 드려요</div>
''' + "\n".join(f'      <div class="chip" id="tg-c{i}" style="left: {x}px; top: {y}px">{t}</div>' for i, (t, x, y, r) in enumerate(chips)), '''
    // B27 공부는 혼자, · B28 계획은 같이. · B29 1:1 학습플래너 배지 · B30 서브 · B31 플랜 칩
    const rot = ''' + json.dumps([r for *_, r in chips]) + ''';
    IN("#tg-q", B[27], { scale: 1.1 });
    IN("#tg-line", B[28], { y: 60 });
    IN("#tg-badge div", B[29], { y: 30 });
    IN("#tg-sub", B[30], { y: 30 });
    rot.forEach((r, i) => {
      tl.fromTo(`#tg-c${i}`, { opacity: 0, rotation: r, filter: "blur(8px)" }, { opacity: 1, rotation: r, filter: "blur(0px)", duration: 0.16, ease: "power3.out" }, B[31] + i * 0.03);
    });
    OUT(CAM, D, {});
'''))

# ---------- subjects B33–B41 ----------
subs = [("헌법", 80, 240, -6), ("형법", 700, 220, 5), ("행정법", 420, 170, -3), ("상법", 90, 1060, 4),
        ("민사소송법", 500, 1110, -4), ("형사소송법", 120, 1200, 3), ("노동법", 810, 1010, -6),
        ("경제법", 790, 1140, 5), ("물권법", 120, 520, -4), ("채권총칙", 600, 520, 4)]
SLOTS.append(scene("subjects", 33, 41, '''
    #root { color: #0b1a33; background: var(--noise), var(--pat-stars), var(--ink-tone); }
    #sj-paper { position: absolute; inset: 0; background: var(--noise), var(--pat-hatch), var(--paper-tone); }
    .sc { position: absolute; padding: 22px 30px; border-radius: 22px; background: #ffffff; border: 2px solid #e8e2d6; box-shadow: 0 16px 40px rgba(11, 26, 51, 0.12); font-size: 46px; font-weight: 900; white-space: nowrap; letter-spacing: -0.03em; }
    .sc small { display: block; font-size: 30px; font-weight: 700; color: #6b6660; }
    .sc.hot { background: #0b1a33; color: #f0d595; border-color: #e0c27e; }
    .sc.hot small { color: #f0d595; }
    #sj-t1 { top: 700px; font-size: 76px; font-weight: 800; line-height: 1.1; color: #6b6660; }
    #sj-t1 b { color: #2e5cbe; }
    #sj-t2 { top: 805px; font-size: 104px; font-weight: 900; line-height: 1.1; }
    #sj-t2 b { color: #2e5cbe; }
    #sj-tag { top: 950px; display: flex; justify-content: center; }
    #sj-tag div { height: 80px; padding: 0 34px; border-radius: 999px; background: #e0c27e; color: #0b1a33; font-size: 42px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }
    #sj-fine { top: 1290px; font-size: 30px; font-weight: 500; color: #6b6660; letter-spacing: -0.02em; }
''', '''      <div id="sj-paper" data-layout-ignore></div>
''' + "\n".join(f'      <div class="sc{" hot" if t in ("물권법", "채권총칙") else ""}" id="sj-s{i}" style="left: {x}px; top: {y}px">{"<small>전공필수</small>" if t in ("물권법", "채권총칙") else ""}{t}</div>' for i, (t, x, y, r) in enumerate(subs)) + '''
      <div id="sj-t1" class="stage">교양 몇 과목 말고,</div>
      <div id="sj-t2" class="stage"><b>법학 전공</b>으로.</div>
      <div id="sj-tag" class="stage"><div>물권법·채권총칙 개설은 여기뿐*</div></div>
      <div id="sj-fine" class="stage">* 표준교육과정 전공필수 개설 평생교육원 기준, 2026.10 조회</div>''', '''
    // B33 종이 아이리스 · B34 과목 카드 · B35 진짜 '법학 전공' · B36 과목으로 · B37 나머지 흐림 · B38 물권법 · B39 채권총칙 · B40 여기뿐*
    const rot = ''' + json.dumps([r for *_, r in subs]) + ''';
    tl.fromTo("#sj-paper", { clipPath: "circle(0% at 50% 40%)" }, { clipPath: "circle(120% at 50% 40%)", duration: 0.3, ease: "power3.inOut" }, B[33]);
    rot.forEach((r, i) => {
      tl.fromTo(`#sj-s${i}`, { opacity: 0, y: -160, rotation: r }, { opacity: 1, y: 0, rotation: r, duration: 0.2, ease: "power3.out" }, B[34] + i * 0.035);
    });
    IN("#sj-t1", B[35], { y: 30 });
    IN("#sj-t2", B[35] + 0.12, { y: 30 });
    tl.to(["#sj-s0", "#sj-s1", "#sj-s2", "#sj-s3", "#sj-s4", "#sj-s5", "#sj-s6", "#sj-s7"], { opacity: 0.22, duration: 0.14 }, B[36]);
    tl.fromTo("#sj-s8", { scale: 1 }, { scale: 1.12, duration: 0.14, ease: "power3.out", immediateRender: false }, B[37]);
    tl.fromTo("#sj-s9", { scale: 1 }, { scale: 1.12, duration: 0.14, ease: "power3.out", immediateRender: false }, B[38]);
    IN("#sj-tag div", B[39], { y: 24 });
    IN("#sj-fine", B[39], {}, 0.2);
    OUT(CAM, D, {});
'''))

# ---------- paths B41–B49 ----------
cards = [("로스쿨", "지원 자격 학사학위", 90, 330, -8), ("로펌·법무팀", "법학 전공으로 증명", 600, 300, 7), ("경찰·공무원", "수험 과목과 학위를 함께", 300, 1010, -4)]
SLOTS.append(scene("paths", 41, 49, f'''
    #root {{ color: #ffffff; background: var(--noise), var(--pat-topo), var(--ink-tone); }}
    #pa-t1 {{ top: {EYE - 60}px; font-size: 140px; font-weight: 900; }}
    #pa-t2 {{ top: {EYE + 100}px; font-size: 140px; font-weight: 900; color: #f0d595; }}
    .slash {{ position: absolute; width: 8px; height: 260px; background: #ffffff; border-radius: 4px; }}
    .mc {{ position: absolute; width: 400px; padding: 28px 32px; border-radius: 26px; background: #fbf9f4; color: #0b1a33; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5); letter-spacing: -0.03em; }}
    .mc b {{ display: block; font-size: 50px; font-weight: 900; }}
    .mc span {{ display: block; margin-top: 6px; font-size: 30px; font-weight: 700; color: #2e5cbe; }}
    .mc i {{ position: absolute; right: 26px; top: 26px; font-style: normal; font-size: 30px; font-weight: 900; color: #1f9d55; background: #d9f5e3; border-radius: 10px; padding: 4px 12px; }}
    #pa-fine {{ top: 1270px; font-size: 30px; font-weight: 500; color: rgba(255, 255, 255, 0.62); letter-spacing: -0.02em; }}
''', '''      <div class="slash" id="pa-sl1" style="left: 300px; top: 560px" data-layout-ignore></div>
      <div class="slash" id="pa-sl2" style="left: 770px; top: 860px" data-layout-ignore></div>
      <div id="pa-t1" class="stage">어디로 가든</div>
      <div id="pa-t2" class="stage">기본기는 법학.</div>
''' + "\n".join(f'      <div class="mc" id="pa-m{i}" style="left: {x}px; top: {y}px"><i>↗</i><b>{a}</b><span>{b}</span></div>' for i, (a, b, x, y, r) in enumerate(cards)) + '''
      <div id="pa-fine" class="stage">※ 로스쿨 입학·인턴·채용 여부는 각 기관의 선발 기준에 따릅니다.</div>''', '''
    // B41 이 길이 · B42 칼선 · B43~B45 진로 카드 · B46 가까워져요 · B47 면책
    const rot = ''' + json.dumps([r for *_, r in cards]) + ''';
    IN("#pa-t1", B[41], { scale: 1.3, filter: "blur(18px)" }, 0.22);
    tl.fromTo(["#pa-sl1", "#pa-sl2"], { scaleY: 0, rotation: 18, opacity: 1 }, { scaleY: 1, rotation: 18, duration: 0.12, ease: "power3.out", stagger: 0.04 }, B[42]);
    tl.to(["#pa-sl1", "#pa-sl2"], { opacity: 0, duration: 0.12 }, B[42] + 0.24);
    [43, 44, 45].forEach((b, i) => {
      tl.fromTo(`#pa-m${i}`, { opacity: 0, y: i === 2 ? 220 : -220, rotation: rot[i] }, { opacity: 1, y: 0, rotation: rot[i], duration: 0.22, ease: "power3.out" }, B[b]);
    });
    IN("#pa-t2", B[46], { y: 40 });
    IN("#pa-fine", B[46], {}, 0.2);
    OUT(CAM, D, {});
'''))

# ---------- go B49–B53 ----------
SLOTS.append(scene("go", 49, 53, f'''
    #root {{ color: #ffffff; background: var(--noise), var(--pat-stars), var(--ink-tone); }}
    #go-t {{ top: {EYE}px; font-size: 180px; font-weight: 900; white-space: nowrap; display: flex; align-items: center; justify-content: center; gap: 24px; }}
    #go-t svg {{ width: 150px; height: 150px; }}
    #go-white {{ position: absolute; inset: 0; background: #fbf9f4; }}
''', '''      <div id="go-t" class="stage"><span class="w" id="go-w1">상담</span><span class="w" id="go-w2">신청</span><svg id="go-arrow" viewBox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" /></svg></div>''', '''
    // B49 상담 · B50 신청 · B51 → · B52 화살표 방향으로 흰 화면이 밀려와 CTA로
    tl.fromTo(BG, { clipPath: "circle(0% at 50% 40%)" }, { clipPath: "circle(120% at 50% 40%)", duration: 0.2, ease: "power3.inOut" }, 0);
    IN("#go-w1", B[49], { scale: 1.6, filter: "blur(20px)" }, 0.2);
    IN("#go-w2", B[50], { x: 60 });
    tl.fromTo("#go-arrow", { opacity: 0, x: -60 }, { opacity: 1, x: 0, duration: 0.16, ease: "power3.out" }, B[51]);
    tl.to("#go-arrow", { x: 40, duration: 0.3, ease: "power2.in" }, B[52] - 0.1);
''', bg='<div class="mesh"></div>') )
# 흰 화면 와이프는 CTA 씬 시작에서 처리

# ---------- cta B53–end ----------
SLOTS.append(scene("cta", 53, None, f'''
    #root {{ color: #0b1a33; background: var(--noise), var(--pat-stars), var(--ink-tone); }}
    #ct-paper {{ position: absolute; inset: 0; background: var(--noise), var(--pat-rings), var(--paper-tone); }}
    #ct-lead {{ top: {EYE - 310}px; font-size: 48px; font-weight: 700; color: #6b6660; }}
    #ct-b1 {{ top: {EYE - 230}px; font-size: 180px; font-weight: 900; line-height: 1; }}
    #ct-b2 {{ top: {EYE - 40}px; font-size: 140px; font-weight: 900; line-height: 1; color: #2e5cbe; }}
    #ct-pill {{ top: {EYE + 160}px; display: flex; justify-content: center; }}
    #ct-pill div {{ height: 70px; padding: 0 30px; border-radius: 999px; background: #ff5a4e; color: #fff; font-size: 38px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }}
    #ct-btn {{ position: absolute; left: 110px; top: {EYE + 260}px; width: 860px; height: 156px; border-radius: 999px; background: linear-gradient(100deg, #12264a 0%, #2e5cbe 55%, #c9a666 100%); color: #ffffff; display: flex; align-items: center; justify-content: center; gap: 24px; box-shadow: 0 24px 60px rgba(46, 92, 190, 0.35); }}
    #ct-btn svg {{ width: 60px; height: 60px; }}
    #ct-btn b {{ font-size: 84px; font-weight: 900; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }}
    #ct-cursor {{ position: absolute; left: 880px; top: {EYE + 380}px; width: 90px; height: 90px; }}
    #ct-hours {{ top: {EYE + 440}px; font-size: 36px; font-weight: 800; letter-spacing: -0.02em; }}
    #ct-brand {{ top: {EYE + 496}px; font-size: 36px; font-weight: 800; color: #7d6233; letter-spacing: -0.02em; }}
    #ct-fine {{ top: {EYE + 552}px; font-size: 30px; font-weight: 500; line-height: 1.3; color: #6b6660; letter-spacing: -0.02em; }}
''', '''      <div id="ct-paper" data-layout-ignore></div>
      <div id="ct-lead" class="stage">결정은 상담 뒤에 해도 늦지 않아요</div>
      <div id="ct-b1" class="stage">질문만</div>
      <div id="ct-b2" class="stage">들고 오세요.</div>
      <div id="ct-pill" class="stage"><div>11/10 접수 마감 · 11/4 개강</div></div>
      <div id="ct-btn"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="#fff" /></svg><b>070-4006-7128</b></div>
      <svg id="ct-cursor" viewBox="0 0 24 24" data-layout-ignore><path d="M5 3l14 7-6.2 1.8L10.8 18z" fill="#ffffff" stroke="#0b1a33" stroke-width="1.6" stroke-linejoin="round" /></svg>
      <div id="ct-hours" class="stage">평일 10~18시 · 내 학력 기준 1:1 상담</div>
      <div id="ct-brand" class="stage">경찰복지사이버평생교육원</div>
      <div id="ct-fine" class="stage">※ 변호사·검사·법무관은 로스쿨 졸업·변호사시험 합격 등 별도 요건이 필요하며,<br />이 과정은 입학·합격·취업을 보장하지 않습니다.</div>''', '''
    // B53 흰 화면 와이프 + 망설여진다면 · B54 상담만 · B55 받아도 돼요 · B56 마감 · B57 버튼 · B58 커서 · B59 클릭 · B60 정보
    tl.fromTo("#ct-paper", { clipPath: "inset(0% 0% 0% 100%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.16, ease: "power3.inOut" }, 0);
    IN("#ct-lead", B[53] + 0.1, { y: -20 });
    IN("#ct-b1", B[54], { scale: 1.4, filter: "blur(18px)" }, 0.22);
    IN("#ct-b2", B[55], { y: 40 });
    IN("#ct-pill div", B[56], { y: 24 });
    IN("#ct-btn", B[57], { y: 60 }, 0.22);
    tl.fromTo("#ct-cursor", { opacity: 0, x: 200, y: 220 }, { opacity: 1, x: 0, y: 0, duration: 0.3, ease: "power3.out" }, B[58]);
    tl.fromTo("#ct-btn", { scale: 1 }, { scale: 0.96, duration: 0.07, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, B[59]);
    tl.fromTo("#ct-cursor", { scale: 1 }, { scale: 0.86, duration: 0.07, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, B[59]);
    IN(["#ct-hours", "#ct-brand", "#ct-fine"], B[58], { y: 16 }, 0.2);
'''))

# ---------- index.html hosts ----------
p = os.path.join(ROOT, "index.html")
s = open(p).read()
a = s.index('      <div id="poster"')
b = s.index("      <!-- BGM")
hosts = "".join(f'''      <div id="{n}" class="clip" data-composition-id="{n}" data-composition-src="compositions/{n}.html"
        data-start="{st:g}" data-duration="{du:g}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
''' for n, st, du in SLOTS)
open(p, "w").write(s[:a] + hosts + "\n" + s[b:])
print("\n".join(f"{n:9s} {st:6.3f} +{du:.3f}" for n, st, du in SLOTS))
