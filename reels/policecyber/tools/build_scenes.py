import os,sys
OUT=sys.argv[1]
COMMON=open(os.path.join(os.path.dirname(__file__),'common.css')).read()
CHECK='<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" /></svg>'
def scene(cid, css, html, js):
    s=f'''<template>
  <style>
{COMMON}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
'''
    open(os.path.join(OUT,cid+'.html'),'w').write(s)

# ---------- poster (0–1.2) ----------
scene('poster','''
    #root { color: #ffffff; background: #0b1a33; }
    #po-grid { position: absolute; inset: 0; }
    .gl { stroke: rgba(255, 255, 255, 0.35); stroke-width: 2; }
    .gh { fill: #ffffff; }
    #po-alert { top: 196px; display: flex; justify-content: center; }
    #po-alert div { height: 72px; padding: 0 32px; border-radius: 999px; background: #ff5a4e; color: #fff; font-size: 38px; font-weight: 900; display: flex; align-items: center; gap: 14px; letter-spacing: -0.02em; box-shadow: 0 12px 30px rgba(255, 90, 78, 0.4); }
    #po-alert i { width: 16px; height: 16px; border-radius: 50%; background: #fff; }
    #po-kicker { top: 318px; font-size: 68px; font-weight: 800; }
    #po-kicker b { color: #f0d595; }
    #po-one { position: absolute; left: 0; width: 1080px; top: 400px; text-align: center; font-weight: 900; line-height: 1; letter-spacing: -0.06em; white-space: nowrap; }
    #po-one .pre, #po-one .post { font-size: 160px; }
    #po-one .n { font-size: 500px; color: #f0d595; text-shadow: 0 24px 80px rgba(11, 26, 51, 0.55); }
    #po-one sup { font-size: 80px; color: #f0d595; vertical-align: 3em; }
    #po-seal { position: absolute; left: 770px; top: 430px; width: 230px; height: 230px; border-radius: 50%; background: #fbf9f4; color: #0b1a33; border: 6px solid #b8955a; box-shadow: 0 0 0 6px #fbf9f4, 0 20px 50px rgba(0, 0, 0, 0.45); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; font-weight: 900; line-height: 1.1; }
    #po-seal img { width: 58px; height: 58px; margin-bottom: 6px; }
    #po-seal span { font-size: 30px; letter-spacing: -0.04em; }
    #po-seal b { font-size: 44px; color: #7d6233; }
    #po-nos { top: 965px; display: flex; justify-content: center; gap: 16px; }
    .no { height: 100px; padding: 0 30px; border-radius: 24px; background: rgba(255, 255, 255, 0.16); border: 2px solid rgba(255, 255, 255, 0.45); font-size: 46px; font-weight: 800; display: flex; align-items: center; gap: 12px; letter-spacing: -0.03em; }
    .no svg { width: 46px; height: 46px; }
    #po-sub { top: 1100px; font-size: 54px; font-weight: 900; }
    #po-fine { top: 1262px; font-size: 30px; font-weight: 500; line-height: 1.3; color: rgba(255, 255, 255, 0.78); letter-spacing: -0.02em; }
''','''    <div id="po-cam" class="cam" data-layout-allow-overlap>
      <div class="mesh" data-layout-ignore></div>
      <svg id="po-grid" viewBox="0 0 1080 1920" data-layout-ignore>
        <line class="gl" x1="60" y1="0" x2="60" y2="1920" />
        <line class="gl" x1="1020" y1="0" x2="1020" y2="1920" />
        <line class="gl" x1="0" y1="430" x2="1080" y2="430" />
        <line class="gl" x1="0" y1="910" x2="1080" y2="910" />
        <rect class="gh" x="52" y="422" width="16" height="16" />
        <rect class="gh" x="1012" y="422" width="16" height="16" />
        <rect class="gh" x="52" y="902" width="16" height="16" />
        <rect class="gh" x="1012" y="902" width="16" height="16" />
      </svg>
      <div id="po-alert" class="stage"><div><i></i>11/10 접수 마감 · 11/4 개강</div></div>
      <div id="po-kicker" class="stage">평생교육원 중 <b>법학 전공</b>은</div>
      <div id="po-one" data-layout-allow-overlap><span class="pre">단 </span><span class="n">1</span><span class="post">곳</span><sup>*</sup></div>
      <div id="po-seal" data-layout-allow-overlap><img src="assets/img/moe-emblem.svg" alt="" /><span>교육부장관 명의</span><b>학사학위</b></div>
      <div id="po-nos" class="stage">
        <div class="no">퇴사<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="#ff5a4e" stroke-width="4" stroke-linecap="round" /></svg></div>
        <div class="no">재입학<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="#ff5a4e" stroke-width="4" stroke-linecap="round" /></svg></div>
        <div class="no">출석수업<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="#ff5a4e" stroke-width="4" stroke-linecap="round" /></svg></div>
      </div>
      <div id="po-sub" class="stage">일하면서, 온라인으로 법학사</div>
      <div id="po-fine" class="stage">* 전공필수(물권법·채권총칙) 개설 평생교육원 기준, 2026.10 조회<br />입학·합격·취업을 보장하지 않습니다.</div>
    </div>''','''    // 첫 프레임 = 완성 포스터(썸네일). 비트(0.37 / 0.81)에 펀치
    tl.fromTo("#po-cam", { scale: 1.04 }, { scale: 1, duration: 0.95, ease: "none" }, 0);
    tl.fromTo("#po-seal", { rotation: -12 }, { rotation: -12, duration: 0.01 }, 0);
    tl.fromTo("#po-one .n", { scale: 1.14 }, { scale: 1, duration: 0.3, ease: "expo.out", immediateRender: false }, 0.37);
    tl.fromTo("#po-seal", { scale: 1.25 }, { scale: 1, duration: 0.25, ease: "power4.out", immediateRender: false }, 0.37);
    tl.fromTo(".no svg", { scale: 1.7 }, { scale: 1, duration: 0.25, ease: "power4.out", stagger: 0.05, immediateRender: false }, 0.81);
    // 퇴장: '1' 속으로 줌
    tl.to("#po-cam", { scale: 1.7, opacity: 0, filter: "blur(18px)", duration: 0.24, ease: "power3.in", transformOrigin: "50% 33%" }, 0.96);''')

# ---------- far (1.2–3.67, 2.47) ----------
scene('far','''
    #root { color: #0b1a33; background: #fbf9f4; }
    .grad { background: linear-gradient(100deg, #0b1a33 0%, #2e5cbe 60%, #b8955a 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
    #fa-big { top: 700px; font-size: 300px; font-weight: 900; line-height: 1; }
    #fa-line { top: 760px; font-size: 104px; font-weight: 800; }
    #fa-mesh { position: absolute; inset: 0; }
    #fa-grid { position: absolute; inset: 0; }
    .gl { stroke: rgba(255, 255, 255, 0.4); stroke-width: 2; }
    .gh { fill: #ffffff; }
    .far { top: 690px; font-size: 280px; font-weight: 900; line-height: 1; color: #ffffff; }
    #fa-g1 { top: 380px; opacity: 0.25; }
    #fa-g2 { top: 1000px; opacity: 0.25; }
''','''    <div id="fa-cam" class="cam">
      <div id="fa-big" class="stage grad">변호사</div>
      <div id="fa-line" class="stage"><span class="w">그</span> <span class="w">꿈,</span> <span class="w">아직도</span></div>
    </div>
    <div id="fa-mesh" class="mesh" data-layout-ignore></div>
    <svg id="fa-grid" viewBox="0 0 1080 1920" data-layout-ignore>
      <line class="gl" x1="0" y1="660" x2="1080" y2="660" />
      <line class="gl" x1="0" y1="1000" x2="1080" y2="1000" />
      <line class="gl" x1="120" y1="0" x2="120" y2="1920" />
      <line class="gl" x1="960" y1="0" x2="960" y2="1920" />
      <rect class="gh" x="112" y="652" width="16" height="16" />
      <rect class="gh" x="952" y="652" width="16" height="16" />
      <rect class="gh" x="112" y="992" width="16" height="16" />
      <rect class="gh" x="952" y="992" width="16" height="16" />
    </svg>
    <div id="fa-g1" class="stage far" data-layout-ignore>멀게?</div>
    <div id="fa-word" class="stage far" data-layout-allow-overlap>멀게?</div>
    <div id="fa-g2" class="stage far" data-layout-ignore>멀게?</div>''','''    // 로컬 비트: .38 .81 1.19 1.57 2.02
    // '변호사' 초근접 블러 → 안착 (레퍼런스 'Ready')
    tl.fromTo("#fa-big", { scale: 2.6, filter: "blur(30px)", opacity: 0.4 }, { scale: 1, filter: "blur(0px)", opacity: 1, duration: 0.38, ease: "expo.out" }, 0);
    tl.to("#fa-big", { scale: 0.86, duration: 0.4, ease: "none" }, 0.38);
    tl.to("#fa-big", { opacity: 0, filter: "blur(12px)", duration: 0.08, ease: "power2.in" }, 0.73);
    tl.fromTo("#fa-line .w", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power3.out", stagger: 0.11 }, 0.81);
    tl.fromTo("#fa-cam", { scale: 1.06 }, { scale: 0.96, duration: 1.19, ease: "none" }, 0);
    // 그라데이션 플러드 + '멀게?' 잔상 (레퍼런스 'big?')
    tl.fromTo("#fa-mesh", { clipPath: "circle(0% at 50% 45%)" }, { clipPath: "circle(120% at 50% 45%)", duration: 0.25, ease: "power2.inOut" }, 1.1);
    tl.fromTo("#fa-grid", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 1.25);
    tl.fromTo("#fa-word", { opacity: 0, scale: 0.6, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.25, ease: "expo.out" }, 1.19);
    tl.fromTo("#fa-g1", { opacity: 0, y: 140 }, { opacity: 0.25, y: 0, duration: 0.3, ease: "expo.out" }, 1.4);
    tl.fromTo("#fa-g2", { opacity: 0, y: -140 }, { opacity: 0.25, y: 0, duration: 0.3, ease: "expo.out" }, 1.4);
    tl.fromTo("#fa-word", { scale: 1 }, { scale: 0.92, duration: 1.0, ease: "none", immediateRender: false }, 1.44);
    tl.to(["#fa-word", "#fa-g1", "#fa-g2", "#fa-grid"], { opacity: 0, filter: "blur(10px)", duration: 0.14, ease: "power3.in" }, 2.33);''')

# ---------- who (3.67–6.37, 2.7) ----------
items=['직장인','비전공자','수험생','로스쿨 준비생']
LH=128
scene('who','''
    #root { color: #0b1a33; background: #fbf9f4; }
    #wh-label { top: 430px; font-size: 60px; font-weight: 800; color: #6b6660; }
    #wh-row { position: absolute; left: 0; width: 1080px; top: 640px; height: 384px; }
    #wh-box { position: absolute; left: 170px; top: 140px; width: 104px; height: 104px; border-radius: 22px; background: #2e5cbe; display: flex; align-items: center; justify-content: center; }
    #wh-box svg { width: 70px; height: 70px; }
    #wh-list { position: absolute; left: 310px; top: 0; }
    .wi { height: %dpx; font-size: 100px; font-weight: 900; line-height: %dpx; white-space: nowrap; }
    #wh-sub { top: 1090px; font-size: 52px; font-weight: 800; }
    #wh-sub b { color: #2e5cbe; }
''' % (LH,LH),'''    <div id="wh-cam" class="cam">
      <div id="wh-label" class="stage">이런 분도 시작해요</div>
      <div id="wh-row" data-layout-allow-overflow data-layout-allow-overlap>
        <div id="wh-box">%s</div>
        <div id="wh-list">%s</div>
      </div>
      <div id="wh-sub" class="stage">법을 처음 배워도 <b>OK</b></div>
    </div>''' % (CHECK, ''.join(f'<div class="wi" id="wh-i{i}">{t}</div>' for i,t in enumerate(items))),'''    // 로컬 비트: .46 .9 1.35 1.8 2.25 — 체크박스 옆 단어 롤 (레퍼런스 'Your ☑')
    const LH = %d, beats = [0.0, 0.46, 0.9, 1.35];
    tl.fromTo("#wh-cam", { scale: 1.06 }, { scale: 0.96, duration: 2.7, ease: "none" }, 0);
    tl.fromTo("#wh-label", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, 0);
    tl.fromTo("#wh-box", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(1.8)" }, 0.08);
    tl.fromTo("#wh-box svg", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }, 0.3);
    tl.fromTo("#wh-list", { y: LH }, { y: LH, duration: 0.01 }, 0);
    tl.fromTo(".wi", { opacity: 0 }, { opacity: 0, duration: 0.01 }, 0);
    tl.fromTo("#wh-i1", { opacity: 0 }, { opacity: 0.18, duration: 0.01 }, 0);
    beats.forEach((t, i) => {
      if (i > 0) tl.to("#wh-list", { y: LH - i * LH, duration: 0.2, ease: "expo.out" }, t);
      tl.to(`#wh-i${i}`, { opacity: 1, duration: 0.12 }, t);
      if (i > 0) tl.to(`#wh-i${i - 1}`, { opacity: 0.18, duration: 0.12 }, t);
      if (i > 1) tl.to(`#wh-i${i - 2}`, { opacity: 0, duration: 0.12 }, t);
      if (i < 3 && i > 0) tl.to(`#wh-i${i + 1}`, { opacity: 0.18, duration: 0.12 }, t);
    });
    tl.fromTo("#wh-sub", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.25, ease: "expo.out" }, 1.8);
    tl.to("#wh-cam", { opacity: 0, filter: "blur(12px)", duration: 0.16, ease: "power3.in" }, 2.54);''' % LH)

# ---------- online (6.37–9.06, 2.69) ----------
scene('online','''
    #root { color: #ffffff; background: #fbf9f4; }
    #on-mesh { position: absolute; inset: 0; }
    #on-t1 { top: 380px; font-size: 130px; font-weight: 900; }
    #on-t2 { top: 1050px; font-size: 130px; font-weight: 900; }
    .oc { position: absolute; top: 590px; width: 340px; height: 420px; border-radius: 34px; background: #fbf9f4; color: #0b1a33; box-shadow: 0 30px 70px rgba(11, 26, 51, 0.45); padding: 34px 30px; letter-spacing: -0.03em; }
    #on-c1 { left: 80px; }
    #on-c2 { left: 370px; z-index: 2; }
    #on-c3 { left: 660px; }
    .oc small { display: block; font-size: 30px; font-weight: 700; color: #7d6233; }
    .oc b { display: block; margin-top: 12px; font-size: 52px; font-weight: 900; line-height: 1.12; }
    .oc .bar { position: absolute; left: 30px; right: 30px; bottom: 44px; height: 14px; border-radius: 7px; background: #e8e2d6; overflow: hidden; }
    .oc .bar i { display: block; width: 100%; height: 100%; background: linear-gradient(90deg, #2e5cbe, #e0c27e); transform-origin: 0 50%; }
    .oc .ic { position: absolute; left: 30px; bottom: 90px; font-size: 30px; font-weight: 800; color: #2e5cbe; }
    #on-pill { top: 1235px; display: flex; justify-content: center; }
    #on-pill div { height: 76px; padding: 0 36px; border-radius: 999px; background: #0b1a33; color: #f0d595; font-size: 40px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }
''','''    <div id="on-mesh" class="mesh" data-layout-ignore></div>
    <div id="on-cam" class="cam" data-layout-allow-overlap>
      <div id="on-t1" class="stage">퇴근 후,</div>
      <div id="on-c1" class="oc"><small>평일 밤</small><b>민법총칙<br />3주차</b><div class="ic">▶ 수강 중</div><div class="bar"><i id="on-b1"></i></div></div>
      <div id="on-c2" class="oc"><small>주말</small><b>형법<br />몰아보기</b><div class="ic">▶ 2강 연속</div><div class="bar"><i id="on-b2"></i></div></div>
      <div id="on-c3" class="oc"><small>이동 중</small><b>헌법<br />복습</b><div class="ic">▶ 모바일</div><div class="bar"><i id="on-b3"></i></div></div>
      <div id="on-t2" class="stage">온라인으로.</div>
      <div id="on-pill" class="stage"><div>오프라인 수업 0회</div></div>
    </div>''','''    // 로컬 비트: .44 .91 1.35 1.79 2.22 — 문장 사이로 카드가 끼어듦 (레퍼런스 'Show [photos] what matters')
    tl.fromTo("#on-mesh", { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.25, ease: "power2.inOut" }, 0);
    tl.fromTo("#on-cam", { scale: 1.05 }, { scale: 0.96, duration: 2.69, ease: "none" }, 0);
    tl.fromTo("#on-t1", { opacity: 0, filter: "blur(10px)", y: 260 }, { opacity: 1, filter: "blur(0px)", y: 0, duration: 0.3, ease: "expo.out" }, 0.1);
    tl.fromTo("#on-t2", { opacity: 0, filter: "blur(10px)", y: -260 }, { opacity: 1, filter: "blur(0px)", y: 0, duration: 0.3, ease: "expo.out" }, 0.1);
    tl.fromTo("#on-c1", { opacity: 0, y: 200, rotation: -14 }, { opacity: 1, y: 30, rotation: -8, duration: 0.4, ease: "expo.out" }, 0.44);
    tl.fromTo("#on-c2", { opacity: 0, y: 200, rotation: 0 }, { opacity: 1, y: 0, rotation: 0, duration: 0.4, ease: "expo.out" }, 0.56);
    tl.fromTo("#on-c3", { opacity: 0, y: 200, rotation: 14 }, { opacity: 1, y: 30, rotation: 8, duration: 0.4, ease: "expo.out" }, 0.68);
    tl.fromTo(["#on-b1", "#on-b2", "#on-b3"], { scaleX: 0.05 }, { scaleX: 0.7, duration: 1.2, ease: "power2.inOut", stagger: 0.1 }, 0.9);
    tl.fromTo("#on-pill div", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }, 1.35);
    tl.to("#on-cam", { opacity: 0, filter: "blur(12px)", duration: 0.16, ease: "power3.in" }, 2.52);''')

# ---------- degree (9.06–11.62, 2.56) ----------
scene('degree','''
    #root { color: #0b1a33; background: #fbf9f4; }
    #dg-t { top: 250px; font-size: 140px; font-weight: 900; }
    #dg-t .b { color: #2e5cbe; }
    #dg-cert { position: absolute; left: 260px; top: 470px; width: 560px; height: 680px; background: #fffdf8; color: #161616; border: 3px solid #b8955a; outline: 2px solid #b8955a; outline-offset: -18px; box-shadow: 0 40px 90px rgba(11, 26, 51, 0.25); padding: 58px 52px 0; text-align: center; letter-spacing: -0.03em; }
    .dc-no { font-size: 30px; color: #6b6660; text-align: left; }
    .dc-title { font-size: 70px; font-weight: 800; letter-spacing: 0.4em; margin: 20px 0 30px 0.4em; }
    .dc-field { font-size: 32px; font-weight: 600; text-align: left; line-height: 1.75; }
    .dc-field b { color: #7d6233; font-weight: 800; }
    .dc-body { margin-top: 18px; font-size: 30px; line-height: 1.55; color: #3a3732; text-align: left; }
    .dc-sign { position: absolute; left: 0; right: 0; bottom: 58px; font-size: 40px; font-weight: 800; letter-spacing: 0.08em; }
    #dg-stamp { position: absolute; right: 60px; bottom: 40px; width: 96px; height: 96px; }
    #dg-mark { position: absolute; left: 50%; top: 44%; width: 360px; margin-left: -180px; text-align: center; font-size: 120px; font-weight: 900; color: rgba(184, 149, 90, 0.16); letter-spacing: 0.2em; transform: rotate(-18deg); }
    #dg-sub { top: 1200px; font-size: 46px; font-weight: 800; }
    #dg-sub b { color: #7d6233; }
''','''    <div id="dg-cam" class="cam" data-layout-allow-overlap>
      <div id="dg-t" class="stage"><span class="w">학위는</span> <span class="w b">진짜.</span></div>
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
      <div id="dg-sub" class="stage"><b>교육부장관 명의</b> 법학사 · 로스쿨 지원 자격</div>
    </div>''','''    // 로컬 비트: .46 .91 1.35 1.74 2.11 — 거대 블러 단어 → 안착 (레퍼런스 'Boost')
    tl.fromTo("#dg-cam", { scale: 1.05 }, { scale: 0.96, duration: 2.56, ease: "none" }, 0);
    tl.fromTo("#dg-t .w:first-child", { opacity: 0.3, scale: 2.4, filter: "blur(26px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.36, ease: "expo.out" }, 0);
    tl.fromTo("#dg-t .b", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out" }, 0.46);
    tl.fromTo("#dg-cert", { opacity: 0, y: 520, rotation: -14, scale: 0.8 }, { opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.55, ease: "expo.out" }, 0.6);
    tl.fromTo("#dg-stamp", { opacity: 0, scale: 2.4, rotation: -25 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.22, ease: "power4.out" }, 1.35);
    tl.fromTo("#dg-sub", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.25, ease: "expo.out" }, 1.5);
    tl.to("#dg-cam", { opacity: 0, filter: "blur(12px)", duration: 0.15, ease: "power3.in" }, 2.4);''')

# ---------- together (11.62–14.32, 2.7) dark ----------
chips=[('퇴근 후 1시간',110,300,-6),('주말 집중 플랜',620,250,5),('진도 체크',90,1080,4),('시험 대비',700,1120,-5),('과목 추천',130,1240,-3),('맞춤 일정',700,1250,4)]
scene('together','''
    #root { color: #ffffff; background: #0a1020; }
    #tg-line { top: 600px; font-size: 130px; font-weight: 900; white-space: nowrap; }
    #tg-coin { display: inline-flex; width: 150px; height: 150px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #fff2c9, #e0c27e 45%, #9c7a3e 100%); color: #0b1a33; font-size: 60px; font-weight: 900; align-items: center; justify-content: center; vertical-align: -0.18em; margin: 0 14px; box-shadow: 0 0 60px rgba(224, 194, 126, 0.55); letter-spacing: -0.04em; }
    #tg-together { color: #f0d595; }
    #tg-sub { top: 830px; font-size: 48px; font-weight: 800; color: rgba(255, 255, 255, 0.85); }
    .chip { position: absolute; height: 82px; padding: 0 30px; border-radius: 22px; background: rgba(255, 255, 255, 0.08); border: 2px solid rgba(255, 255, 255, 0.22); font-size: 38px; font-weight: 800; display: flex; align-items: center; white-space: nowrap; letter-spacing: -0.03em; }
''','''    <div id="tg-cam" class="cam" data-layout-allow-overlap>
      <div id="tg-line" class="stage"><span class="w" id="tg-w1">혼자</span> <span class="w" id="tg-w2">말고,</span><span id="tg-coin">1:1</span><span class="w" id="tg-together">같이.</span></div>
      <div id="tg-sub" class="stage">학습플래너가 내 일정에 맞춰 설계해요</div>
%s
    </div>''' % '\n'.join(f'      <div class="chip" id="tg-c{i}" style="left: {x}px; top: {y}px">{t}</div>' for i,(t,x,y,r) in enumerate(chips)),'''    // 로컬 비트: .45 .9 1.35 1.8 2.25 — 단어 사이 코인 (레퍼런스 'Convert 🪙 faster'), 떠다니는 칩 ('Trusted by')
    const rot = %s;
    tl.fromTo("#tg-cam", { scale: 1.06 }, { scale: 0.96, duration: 2.7, ease: "none" }, 0);
    tl.fromTo("#tg-w1", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power3.out" }, 0);
    tl.fromTo("#tg-w2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power3.out" }, 0.45);
    tl.fromTo("#tg-coin", { opacity: 0, scale: 0, rotationY: 180 }, { opacity: 1, scale: 1, rotationY: 0, duration: 0.4, ease: "back.out(1.6)" }, 0.9);
    tl.fromTo("#tg-together", { opacity: 0, filter: "blur(10px)", x: 40 }, { opacity: 1, filter: "blur(0px)", x: 0, duration: 0.2, ease: "expo.out" }, 1.35);
    tl.fromTo("#tg-sub", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power2.out" }, 1.5);
    rot.forEach((r, i) => {
      tl.fromTo(`#tg-c${i}`, { opacity: 0, scale: 0.5, rotation: 0 }, { opacity: 1, scale: 1, rotation: r, duration: 0.35, ease: "back.out(1.6)" }, 1.0 + i * 0.12);
      tl.fromTo(`#tg-c${i}`, { y: 0 }, { y: i %% 2 ? -36 : 36, duration: 1.6, ease: "none", immediateRender: false }, 1.0 + i * 0.12);
    });
    tl.to("#tg-cam", { opacity: 0, filter: "blur(12px)", duration: 0.15, ease: "power3.in" }, 2.55);''' % [r for *_,r in chips])

# ---------- subjects (14.32–17.77, 3.45) ----------
subs=[('헌법',80,240,-6),('형법',700,220,5),('행정법',420,170,-3),('상법',90,1060,4),('민사소송법',500,1110,-4),('형사소송법',120,1200,3),('노동법',810,1010,-6),('경제법',790,1140,5),('물권법',120,520,-4),('채권총칙',600,520,4)]
scene('subjects','''
    #root { color: #0b1a33; background: #0a1020; }
    #sj-bg { position: absolute; inset: 0; background: #fbf9f4; }
    #sj-blob { position: absolute; left: -300px; top: 300px; width: 1680px; height: 1680px; border-radius: 50%; background: radial-gradient(circle, #ffffff 0%, #9bb4ec 35%, #2e5cbe 55%, rgba(224, 194, 126, 0.9) 70%, rgba(10, 16, 32, 0) 72%); }
    .sc { position: absolute; padding: 22px 30px; border-radius: 22px; background: #ffffff; border: 2px solid #e8e2d6; box-shadow: 0 16px 40px rgba(11, 26, 51, 0.12); font-size: 46px; font-weight: 900; white-space: nowrap; letter-spacing: -0.03em; }
    .sc small { display: block; font-size: 26px; font-weight: 700; color: #6b6660; }
    .sc.hot { background: #0b1a33; color: #f0d595; border-color: #e0c27e; }
    .sc.hot small { color: #f0d595; }
    #sj-title { top: 690px; font-size: 104px; font-weight: 900; line-height: 1.1; }
    #sj-title b { color: #2e5cbe; }
    #sj-tag { top: 950px; display: flex; justify-content: center; }
    #sj-tag div { height: 76px; padding: 0 32px; border-radius: 999px; background: #e0c27e; color: #0b1a33; font-size: 40px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }
    #sj-fine { top: 1290px; font-size: 30px; font-weight: 500; color: #6b6660; letter-spacing: -0.02em; }
''','''    <div id="sj-bg"></div>
    <div id="sj-cam" class="cam" data-layout-allow-overlap>
%s
      <div id="sj-title" class="stage">진짜 <b>‘법학 전공’</b><br />과목으로</div>
      <div id="sj-tag" class="stage"><div>물권법·채권총칙 개설은 여기뿐*</div></div>
      <div id="sj-fine" class="stage">* 표준교육과정 전공필수 개설 평생교육원 기준, 2026.10 조회</div>
    </div>
    <div id="sj-blob" data-layout-ignore></div>''' % '\n'.join(f'      <div class="sc{" hot" if t in ("물권법","채권총칙") else ""}" id="sj-s{i}" style="left: {x}px; top: {y}px">{"<small>전공필수</small>" if t in ("물권법","채권총칙") else ""}{t}</div>' for i,(t,x,y,r) in enumerate(subs)),'''    // 로컬 비트: .45 .9 1.27 1.66 2.11 2.54 3.0 — 원형 블롭 전환 + 카드 콜라주 (레퍼런스 리뷰 카드)
    const rot = %s;
    tl.fromTo("#sj-blob", { scale: 0.05, opacity: 1 }, { scale: 2.2, opacity: 1, duration: 0.4, ease: "power3.in" }, 0);
    tl.to("#sj-blob", { opacity: 0, duration: 0.15 }, 0.38);
    tl.fromTo("#sj-bg", { opacity: 0 }, { opacity: 1, duration: 0.05 }, 0.3);
    tl.fromTo("#sj-cam", { scale: 1.08 }, { scale: 0.96, duration: 3.45, ease: "none" }, 0);
    rot.forEach((r, i) => {
      tl.fromTo(`#sj-s${i}`, { opacity: 0, scale: 0.6, rotation: 0, y: 60 }, { opacity: 1, scale: 1, rotation: r, y: 0, duration: 0.35, ease: "back.out(1.5)" }, 0.4 + i * 0.07);
    });
    tl.fromTo("#sj-title", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, 0.9);
    // 물권법·채권총칙만 남기고 흐리게
    tl.to(["#sj-s0", "#sj-s1", "#sj-s2", "#sj-s3", "#sj-s4", "#sj-s5", "#sj-s6", "#sj-s7"], { opacity: 0.25, duration: 0.2 }, 1.66);
    tl.fromTo(["#sj-s8", "#sj-s9"], { scale: 1 }, { scale: 1.12, duration: 0.25, ease: "back.out(2)", immediateRender: false }, 1.66);
    tl.fromTo("#sj-tag div", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }, 1.75);
    tl.fromTo("#sj-fine", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 1.8);
    tl.to("#sj-cam", { opacity: 0, filter: "blur(12px)", duration: 0.15, ease: "power3.in" }, 3.3);''' % [r for *_,r in subs])

# ---------- paths (17.77–21.22, 3.45) dark ----------
cards=[('로스쿨','지원 자격 학사학위',90,330,-8),('로펌·법무팀','법학 전공으로 증명',600,300,7),('경찰·공무원','수험 과목과 학위를 함께',300,1010,-4)]
scene('paths','''
    #root { color: #ffffff; background: #0a1020; }
    #pa-t1 { top: 640px; font-size: 140px; font-weight: 900; }
    #pa-t2 { top: 800px; font-size: 140px; font-weight: 900; color: #f0d595; }
    .slash { position: absolute; width: 10px; height: 260px; background: #ffffff; border-radius: 5px; }
    .mc { position: absolute; width: 400px; padding: 28px 32px; border-radius: 26px; background: #fbf9f4; color: #0b1a33; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5); letter-spacing: -0.03em; }
    .mc b { display: block; font-size: 50px; font-weight: 900; }
    .mc span { display: block; margin-top: 6px; font-size: 30px; font-weight: 700; color: #2e5cbe; }
    .mc i { position: absolute; right: 26px; top: 26px; font-style: normal; font-size: 30px; font-weight: 900; color: #1f9d55; background: #d9f5e3; border-radius: 10px; padding: 4px 12px; }
    #pa-fine { top: 1270px; font-size: 30px; font-weight: 500; color: rgba(255, 255, 255, 0.6); letter-spacing: -0.02em; }
''','''    <div id="pa-cam" class="cam" data-layout-allow-overlap>
      <div class="slash" id="pa-sl1" style="left: 300px; top: 560px" data-layout-ignore></div>
      <div class="slash" id="pa-sl2" style="left: 770px; top: 860px" data-layout-ignore></div>
      <div id="pa-t1" class="stage">이 길이</div>
      <div id="pa-t2" class="stage">가까워져요</div>
%s
      <div id="pa-fine" class="stage">※ 로스쿨 입학·인턴·채용 여부는 각 기관의 선발 기준에 따릅니다.</div>
    </div>''' % '\n'.join(f'      <div class="mc" id="pa-m{i}" style="left: {x}px; top: {y}px"><i>↗</i><b>{a}</b><span>{b}</span></div>' for i,(a,b,x,y,r) in enumerate(cards)),'''    // 로컬 비트: .46 .89 1.34 1.8 2.25 2.62 3.0 — 칼선 + 기울어진 수치 카드 (레퍼런스 'Backed by')
    const rot = %s;
    tl.fromTo("#pa-cam", { scale: 1.06 }, { scale: 0.96, duration: 3.45, ease: "none" }, 0);
    tl.fromTo("#pa-t1", { opacity: 0, scale: 1.5, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, 0);
    tl.fromTo(["#pa-sl1", "#pa-sl2"], { scaleY: 0, rotation: 18, opacity: 1 }, { scaleY: 1, rotation: 18, duration: 0.18, ease: "power3.out", stagger: 0.06 }, 0.46);
    tl.to(["#pa-sl1", "#pa-sl2"], { scaleY: 0, opacity: 0, duration: 0.15, ease: "power3.in" }, 0.75);
    tl.fromTo("#pa-t2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power3.out" }, 0.46);
    rot.forEach((r, i) => {
      tl.fromTo(`#pa-m${i}`, { opacity: 0, y: i === 2 ? 300 : -300, rotation: 0 }, { opacity: 1, y: 0, rotation: r, duration: 0.45, ease: "expo.out" }, 0.89 + i * 0.45);
    });
    tl.fromTo("#pa-fine", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 1.5);
    tl.to("#pa-cam", { opacity: 0, filter: "blur(12px)", duration: 0.15, ease: "power3.in" }, 3.3);''' % [r for *_,_,_,r in cards])

# ---------- go (21.22–23.02, 1.8) ----------
scene('go','''
    #root { color: #ffffff; background: #0a1020; }
    #go-mesh { position: absolute; inset: 0; }
    #go-t { top: 760px; font-size: 170px; font-weight: 900; white-space: nowrap; display: flex; align-items: center; justify-content: center; gap: 20px; }
    #go-t svg { width: 140px; height: 140px; }
''','''    <div id="go-mesh" class="mesh" data-layout-ignore></div>
    <div id="go-cam" class="cam" data-layout-allow-overlap>
      <div id="go-t" class="stage"><span>상담 신청</span><svg id="go-arrow" viewBox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
    </div>''','''    // 로컬 비트: .44 .89 1.35 — 거대 단어 줌아웃 + 화살표 (레퍼런스 'Get Started →')
    tl.fromTo("#go-mesh", { clipPath: "circle(0% at 50% 45%)" }, { clipPath: "circle(120% at 50% 45%)", duration: 0.25, ease: "power2.inOut" }, 0);
    tl.fromTo("#go-cam", { scale: 2.2, filter: "blur(10px)" }, { scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 0.05);
    tl.fromTo("#go-cam", { scale: 1 }, { scale: 0.9, duration: 1.1, ease: "none", immediateRender: false }, 0.55);
    tl.fromTo("#go-arrow", { x: -40, opacity: 0 }, { x: 0, opacity: 1, duration: 0.25, ease: "expo.out" }, 0.44);
    tl.fromTo("#go-arrow", { x: 0 }, { x: 24, duration: 0.15, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, 0.89);
    tl.to("#go-cam", { opacity: 0, filter: "blur(12px)", duration: 0.15, ease: "power3.in" }, 1.65);''')

# ---------- cta (23.02–28, 4.98) ----------
scene('cta','''
    #root { color: #0b1a33; background: #fbf9f4; }
    #ct-lead { top: 380px; font-size: 60px; font-weight: 700; color: #6b6660; }
    #ct-b1 { top: 470px; font-size: 180px; font-weight: 900; line-height: 1; }
    #ct-b2 { top: 660px; font-size: 140px; font-weight: 900; line-height: 1; color: #2e5cbe; }
    #ct-pill { top: 860px; display: flex; justify-content: center; }
    #ct-pill div { height: 68px; padding: 0 30px; border-radius: 999px; background: #ff5a4e; color: #fff; font-size: 36px; font-weight: 900; display: flex; align-items: center; letter-spacing: -0.02em; }
    #ct-btn { position: absolute; left: 110px; top: 960px; width: 860px; height: 156px; border-radius: 999px; background: linear-gradient(100deg, #12264a 0%, #2e5cbe 55%, #c9a666 100%); color: #ffffff; display: flex; align-items: center; justify-content: center; gap: 24px; box-shadow: 0 24px 60px rgba(46, 92, 190, 0.35); }
    #ct-btn svg { width: 60px; height: 60px; }
    #ct-btn b { font-size: 84px; font-weight: 900; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    #ct-cursor { position: absolute; left: 880px; top: 1080px; width: 90px; height: 90px; }
    #ct-hours { top: 1140px; font-size: 36px; font-weight: 800; letter-spacing: -0.02em; }
    #ct-brand { top: 1196px; font-size: 36px; font-weight: 800; color: #7d6233; letter-spacing: -0.02em; }
    #ct-fine { top: 1252px; font-size: 30px; font-weight: 500; line-height: 1.3; color: #6b6660; letter-spacing: -0.02em; }
''','''    <div id="ct-cam" class="cam" data-layout-allow-overlap>
      <div id="ct-lead" class="stage">망설여진다면,</div>
      <div id="ct-b1" class="stage">상담만</div>
      <div id="ct-b2" class="stage">받아도 돼요.</div>
      <div id="ct-pill" class="stage"><div>11/10 접수 마감 · 11/4 개강</div></div>
      <div id="ct-btn"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="#fff" /></svg><b>070-4006-7128</b></div>
      <svg id="ct-cursor" viewBox="0 0 24 24" data-layout-ignore><path d="M5 3l14 7-6.2 1.8L10.8 18z" fill="#ffffff" stroke="#0b1a33" stroke-width="1.6" stroke-linejoin="round" /></svg>
      <div id="ct-hours" class="stage">평일 10~18시 · 내 학력에 맞춘 1:1 플랜 상담</div>
      <div id="ct-brand" class="stage">경찰복지사이버평생교육원</div>
      <div id="ct-fine" class="stage">※ 변호사·검사·법무관은 로스쿨 졸업·변호사시험 합격 등 별도 요건이 필요하며,<br />이 과정은 입학·합격·취업을 보장하지 않습니다.</div>
    </div>''','''    // 로컬 비트: .45 .89 1.34 1.8 2.18 2.55 3.0 3.45 — 그라데이션 버튼 + 커서 클릭 (레퍼런스 'Book a demo')
    tl.fromTo("#ct-cam", { scale: 1.04 }, { scale: 0.98, duration: 4.98, ease: "none" }, 0);
    tl.fromTo("#ct-lead", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, 0);
    tl.fromTo("#ct-b1", { opacity: 0, scale: 1.6, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, 0.45);
    tl.fromTo("#ct-b2", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power3.out" }, 0.89);
    tl.fromTo("#ct-pill div", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }, 1.34);
    tl.fromTo("#ct-btn", { opacity: 0, y: 80, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "expo.out" }, 1.34);
    tl.fromTo(["#ct-hours", "#ct-brand", "#ct-fine"], { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.out", stagger: 0.1 }, 1.8);
    // 커서가 들어와 버튼 클릭
    tl.fromTo("#ct-cursor", { opacity: 0, x: 220, y: 260 }, { opacity: 1, x: 0, y: 0, duration: 0.5, ease: "power3.out" }, 2.18);
    tl.fromTo("#ct-cursor", { scale: 1 }, { scale: 0.85, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, 2.68);
    tl.fromTo("#ct-btn", { scale: 1 }, { scale: 0.95, duration: 0.09, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, 2.7);''')
print('ok')
