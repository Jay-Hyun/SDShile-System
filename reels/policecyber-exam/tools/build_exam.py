"""시험지(기출변형) 릴스 생성기.

Usage: python3 tools/build_exam.py   (run from the project root)
- 0~1.3s: 무음 표지 포스터 (썸네일)
- 1.3s: 드럼 첫 강박과 함께 문 1 시작. 이후 문항마다 비트 5개
Writes compositions/*.html and the scene hosts in index.html.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(ROOT, "tools", "exam.css")).read()
AUDIO_START = 1.3
TOTAL = 28.0
_det = [b["time"] for b in json.load(open(os.path.join(ROOT, "beats/assets/music/bgm.mp3.json")))["beats"]]
# 검출기가 놓친 곡의 첫 강박(오디오 0초)을 G0로 넣는다
G = [AUDIO_START] + [round(t + AUDIO_START, 3) for t in _det]

HELPERS = r"""
    const D = __DUR__;
    const B = __BEATS__;
    function IN(sel, t, from, dur) {
      const f = Object.assign({ opacity: 0, filter: "blur(10px)" }, from || {});
      const to = { opacity: 1, filter: "blur(0px)", duration: dur || 0.16, ease: "power3.out" };
      for (const k in f) if (!(k in to)) to[k] = k.startsWith("scale") ? 1 : 0;
      tl.fromTo(sel, f, to, t);
    }
    function OUT(sel, t, to) {
      tl.to(sel, Object.assign({ opacity: 0, filter: "blur(10px)", duration: 0.08, ease: "power2.in" }, to || {}), t - 0.08);
    }
    // 빨간 펜: 선이 그려져 나감 (pathLength=1)
    function PEN(sel, t, dur) {
      tl.fromTo(sel, { strokeDasharray: "1 1", strokeDashoffset: 1, opacity: 1 }, { strokeDashoffset: 0, duration: dur || 0.2, ease: "power2.out" }, t);
    }
    // 형광펜: 왼쪽 → 오른쪽
    function HL(sel, t) {
      tl.fromTo(sel, { backgroundSize: "0% 38%" }, { backgroundSize: "100% 38%", duration: 0.22, ease: "power2.out" }, t);
    }
    // 손글씨처럼 왼쪽부터 드러남
    function WRITE(sel, t, dur) {
      tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0%)", opacity: 1 }, { clipPath: "inset(0% 0% 0% 0%)", duration: dur || 0.3, ease: "none" }, t);
    }
    // 카메라: 천천히 다가감 (튀는 모션 없음)
    tl.fromTo(CAM, { scale: 1 }, { scale: 1.04, duration: __CAMD__, ease: "none" }, 0);
"""

CIRCLE = '<svg class="pen circle" viewBox="0 0 120 110"><path pathLength="1" d="M96 24 C80 6 30 6 14 32 C2 54 14 88 54 94 C92 98 114 74 106 46 C101 28 86 16 66 12" /></svg>'
SLASH = '<svg class="pen slash" viewBox="0 0 100 20" preserveAspectRatio="none"><path pathLength="1" d="M2 16 L98 4" /></svg>'
CHECK = '<svg viewBox="0 0 100 100"><path pathLength="1" d="M10 52 L40 82 L94 14" /></svg>'


def header(page):
    return f'''      <div class="hd">
        <div class="hd-top"><span>2026학년도 2학기 법학사 과정 문제지</span><b>홀수형</b></div>
        <div class="hd-title">제1교시 법학 영역</div>
        <div class="hd-rule"></div>
      </div>
      <div class="foot" data-layout-ignore><span>법학 영역</span><span>{page} / 5</span></div>'''


def opt(qid, n, num, text, pens=""):
    return f'<div class="opt" id="{qid}-o{n}"><span class="num">{num}</span><span class="txt">{text}</span>{pens}</div>'


def scene(cid, a, b, css, html, js, cam_tail=0.0, root_bg=None):
    start = 0.0 if a is None else G[a]
    end = TOTAL if b is None else (G[b] if b != "audio" else AUDIO_START)
    local = {} if a is None else {str(i): round(G[i] - start, 3) for i in range(len(G)) if start - 1e-6 <= G[i] < end - 1e-6}
    helpers = (HELPERS.replace("__DUR__", str(round(end - start, 3)))
               .replace("__CAMD__", str(round(end - start - cam_tail, 3)))
               .replace("__BEATS__", json.dumps(local)))
    bg = f"\n    #root {{ background: {root_bg}; }}" if root_bg else ""
    s = f'''<template>
  <style>
{CSS}{bg}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-cam" class="cam" data-layout-allow-overlap>
{html}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const CAM = "#{cid}-cam";
{helpers}
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
'''
    open(os.path.join(ROOT, "compositions", cid + ".html"), "w").write(s)
    return (cid, round(start, 3), round(end - start, 3))


SLOTS = []

# ---------- 표지 포스터 0~1.3s (무음, 썸네일) ----------
SLOTS.append(scene("cover", None, "audio", '''
    #cv-stamp { position: absolute; left: 690px; top: 330px; width: 300px; height: 112px; border: 6px solid #d93a2b; border-radius: 16px; color: #d93a2b; font-size: 40px; font-weight: 900; display: flex; align-items: center; justify-content: center; letter-spacing: -0.02em; background: rgba(247, 243, 234, 0.6); }
    #cv-kick { position: absolute; left: 110px; width: 860px; top: 480px; text-align: center; font-family: "NotoSerifKR", serif; font-size: 64px; font-weight: 700; }
    #cv-title { position: absolute; left: 60px; width: 960px; top: 580px; text-align: center; font-family: "NotoSerifKR", serif; font-size: 200px; font-weight: 900; line-height: 1; letter-spacing: 0.04em; }
    #cv-meta { position: absolute; left: 110px; width: 860px; top: 830px; display: flex; justify-content: center; gap: 0; font-size: 40px; font-weight: 800; }
    #cv-meta span { padding: 10px 26px; border: 3px solid #161616; }
    #cv-meta span + span { border-left: none; }
    #cv-scope { position: absolute; left: 110px; width: 860px; top: 950px; border: 3px solid #161616; padding: 26px 34px 22px; background: rgba(255, 255, 255, 0.5); }
    #cv-scope small { display: block; font-size: 30px; font-weight: 800; color: #3a3732; letter-spacing: 0.04em; }
    #cv-scope p { margin-top: 8px; font-size: 44px; font-weight: 800; line-height: 1.45; }
    #cv-scope p b { color: #2e5cbe; }
    #cv-fine { top: 1268px; text-align: center; }
    #cover-cam .hd-top b { visibility: hidden; }
''', header(1).replace('<div class="foot"', '<div class="foot" style="display: none"') + '''
      <div id="cv-stamp">11/10 접수 마감</div>
      <div id="cv-kick">AI 시대의</div>
      <div id="cv-title">법학 영역</div>
      <div id="cv-meta"><span>5문항</span><span>제한 시간 28초</span></div>
      <div id="cv-scope">
        <small>출제 범위</small>
        <p>· 평생교육원 중 <b>법학 전공 단 1곳*</b><br />· 교육부장관 명의 학사학위<br />· 퇴근 후 100% 온라인</p>
      </div>
      <div id="cv-fine" class="fine">* 전공필수(물권법·채권총칙) 개설 평생교육원 기준, 2026.10 조회<br />입학·합격·취업을 보장하지 않습니다.</div>''', '''
    // 첫 프레임 = 완성된 표지(썸네일). 끝에서 첫 문제로 종이가 넘어감
    tl.set("#cv-stamp", { rotation: -8 }, 0);
    tl.to(CAM, { y: -260, opacity: 0, filter: "blur(14px)", duration: 0.2, ease: "power3.in" }, D - 0.2);
''', cam_tail=0.2))

# ---------- 문 1 G0–G10 ----------
SLOTS.append(scene("q1", 0, 10, '''
    #q1-ans { left: 760px; top: 610px; font-size: 58px; }
''', header(1) + '''
      <div class="q" id="q1-q"><b>1.</b> AI가 답을 줄 때, 끝까지 사람이 해야 하는 일은?</div>
      <div class="opts">
        ''' + opt("q1", 1, "①", "계약서 초안 작성", SLASH) + '''
        ''' + opt("q1", 2, "②", "판례 검색", SLASH) + '''
        ''' + opt("q1", 3, "③", "조항 요약", SLASH) + '''
        ''' + opt("q1", 4, "④", "<b>그 답을 믿어도 되는지 판단</b>", CIRCLE) + '''
        ''' + opt("q1", 5, "⑤", "번역", SLASH) + '''
      </div>
      <div id="q1-ans" class="ans">정답 ④</div>
      <div class="ex" id="q1-ex"><small>해설</small><p>초안·검색·요약은 AI가.<br />판단의 기준은 <span class="hl" id="q1-hl">법학 전공</span>.</p></div>''', '''
    // G0 문제 · G1 ①②③ · G2 ④⑤ · G3 ①② 빗금 · G4 ③⑤ 빗금 · G5 ④ 동그라미 · G6 정답 ④ · G7 해설 · G8 형광펜
    tl.set(".pen path", { strokeDasharray: "1 1", strokeDashoffset: 1 }, 0);
    IN([".hd", ".foot"], B[0], { y: -30 }, 0.14);
    IN("#q1-q", B[0], { y: 40 }, 0.18);
    IN(["#q1-o1", "#q1-o2", "#q1-o3"], B[1], { x: 40 }, 0.16);
    IN(["#q1-o4", "#q1-o5"], B[2], { x: 40 }, 0.16);
    PEN("#q1-o1 .slash path", B[3]); PEN("#q1-o2 .slash path", B[3] + 0.1);
    PEN("#q1-o3 .slash path", B[4]); PEN("#q1-o5 .slash path", B[4] + 0.1);
    tl.to(["#q1-o1 .txt", "#q1-o2 .txt", "#q1-o3 .txt", "#q1-o5 .txt"], { opacity: 0.35, duration: 0.2 }, B[4] + 0.2);
    PEN("#q1-o4 .circle path", B[5], 0.26);
    WRITE("#q1-ans", B[6], 0.22);
    IN("#q1-ex", B[7], { y: 40 }, 0.2);
    HL("#q1-hl", B[8]);
    OUT(CAM, D, { y: -200 });
'''))

# ---------- 문 2 G10–G15 (O/X) ----------
SLOTS.append(scene("q2", 10, 15, '''
    #q2-ox { position: absolute; left: 110px; width: 860px; top: 640px; display: flex; justify-content: center; gap: 140px; font-family: "NotoSerifKR", serif; font-size: 180px; font-weight: 800; }
    #q2-ox span { position: relative; width: 200px; text-align: center; }
    #q2-ox .pen.circle { left: -20px; top: -10px; width: 240px; height: 240px; }
    #q2-ex { top: 1000px; }
''', header(2) + '''
      <div class="q" id="q2-q"><b>2.</b> 법학을 전공하려면 일을 그만둬야 한다.</div>
      <div id="q2-ox"><span id="q2-o">O</span><span id="q2-x">X''' + CIRCLE + '''</span></div>
      <div class="ex" id="q2-ex"><small>해설</small><p>퇴근 후 <span class="hl" id="q2-hl">100% 온라인</span>.<br />오프라인 수업 0회.</p></div>''', '''
    // G10 문제 · G11 O / X · G12 X 동그라미 · G13 해설 · G14 형광펜
    tl.set(".pen path", { strokeDasharray: "1 1", strokeDashoffset: 1 }, 0);
    IN("#q2-q", B[10], { y: 40 }, 0.18);
    IN(["#q2-o", "#q2-x"], B[11], { y: 30 }, 0.16);
    PEN("#q2-x .circle path", B[12], 0.26);
    tl.to("#q2-o", { opacity: 0.3, duration: 0.2 }, B[12] + 0.2);
    IN("#q2-ex", B[13], { y: 40 }, 0.2);
    HL("#q2-hl", B[14]);
    OUT(CAM, D, { y: -200 });
'''))

# ---------- 문 3 G15–G20 (빈칸) ----------
SLOTS.append(scene("q3", 15, 20, '''
    #q3-line { position: absolute; left: 110px; width: 860px; top: 640px; font-family: "NotoSerifKR", serif; font-size: 66px; font-weight: 700; line-height: 1.6; }
    #q3-blank { position: relative; display: inline-block; width: 420px; border-bottom: 5px solid #161616; height: 92px; vertical-align: -0.25em; margin: 0 8px; }
    #q3-fill { position: absolute; left: 20px; bottom: 6px; font-size: 76px; font-family: "PretendardGOV", sans-serif; font-weight: 900; color: #d93a2b; white-space: nowrap; }
    #q3-chk { position: absolute; left: 860px; top: 600px; width: 110px; height: 110px; }
    #q3-chk path { fill: none; stroke: #d93a2b; stroke-width: 8; stroke-linecap: round; stroke-linejoin: round; }
    #q3-ex { top: 1000px; }
''', header(3) + '''
      <div class="q" id="q3-q"><b>3.</b> 빈칸에 알맞은 말을 쓰시오.</div>
      <div id="q3-line">법학사 학위는<br /><span id="q3-blank"><span id="q3-fill">교육부장관</span></span>명의로 수여된다.</div>
      <svg id="q3-chk" viewBox="0 0 100 100">''' + CHECK[len('<svg viewBox="0 0 100 100">'):] + '''
      <div class="ex" id="q3-ex"><small>해설</small><p>4년제 대학 졸업과 동등한 학력.<br /><span class="hl" id="q3-hl">로스쿨 지원 가능</span> 학사학위.</p></div>''', '''
    // G15 문제 · G16 빈칸에 '교육부장관' · G17 체크 · G18 해설 · G19 형광펜
    tl.set("#q3-chk path", { strokeDasharray: "1 1", strokeDashoffset: 1 }, 0);
    IN(["#q3-q", "#q3-line"], B[15], { y: 40 }, 0.18);
    tl.set("#q3-fill", { opacity: 0 }, 0);
    WRITE("#q3-fill", B[16], 0.3);
    PEN("#q3-chk path", B[17], 0.2);
    IN("#q3-ex", B[18], { y: 40 }, 0.2);
    HL("#q3-hl", B[19]);
    OUT(CAM, D, { y: -200 });
'''))

# ---------- 문 4 G20–G25 ----------
SLOTS.append(scene("q4", 20, 25, '''
    #q4 .opts, .opts { top: 640px; }
    .opt { height: 120px; font-size: 66px; }
    .opt .pen.circle { left: -26px; top: -2px; width: 130px; height: 124px; }
    #q4-ex { top: 1000px; }
''', header(4) + '''
      <div class="q" id="q4-q"><b>4.</b> 법학을 ‘전공’으로 여는 평생교육원은?</div>
      <div class="opts">
        ''' + opt("q4", 1, "①", "여러 곳") + '''
        ''' + opt("q4", 2, "②", "<b>단 1곳*</b>", CIRCLE) + '''
      </div>
      <div class="ex" id="q4-ex"><small>해설</small><p>물권법·채권총칙까지 여는<br /><span class="hl" id="q4-hl">진짜 법학 전공</span>, 여기뿐입니다.</p></div>
      <div class="fine" id="q4-fine" style="top: 1270px">* 표준교육과정 전공필수(물권법·채권총칙) 개설 평생교육원 기준, 2026.10 조회</div>''', '''
    // G20 문제 · G21 선택지 · G22 ② 동그라미 · G23 해설 · G24 형광펜+각주
    tl.set(".pen path", { strokeDasharray: "1 1", strokeDashoffset: 1 }, 0);
    IN("#q4-q", B[20], { y: 40 }, 0.18);
    IN(["#q4-o1", "#q4-o2"], B[21], { x: 40 }, 0.16);
    PEN("#q4-o2 .circle path", B[22], 0.26);
    tl.to("#q4-o1", { opacity: 0.3, duration: 0.2 }, B[22] + 0.2);
    IN("#q4-ex", B[23], { y: 40 }, 0.2);
    IN("#q4-fine", B[23], {}, 0.2);
    HL("#q4-hl", B[24]);
    OUT(CAM, D, { y: -200 });
'''))

# ---------- 문 5 G25–G30 (서술형) ----------
SLOTS.append(scene("q5", 25, 30, '''
    #q5-box { position: absolute; left: 110px; width: 860px; top: 600px; height: 380px; border: 3px solid #161616; background: rgba(255, 255, 255, 0.45); }
    #q5-box small { position: absolute; left: 24px; top: 16px; font-size: 30px; font-weight: 800; color: #3a3732; }
    #q5-w1 { position: absolute; left: 60px; top: 90px; font-size: 80px; font-weight: 900; color: #d93a2b; white-space: nowrap; }
    #q5-w2 { position: absolute; left: 60px; top: 200px; font-size: 92px; font-weight: 900; color: #d93a2b; white-space: nowrap; letter-spacing: -0.02em; }
    #q5-score { position: absolute; left: 700px; top: 1000px; width: 260px; height: 200px; }
    #q5-score span { position: absolute; left: 0; top: 30px; width: 260px; text-align: center; font-family: "NotoSerifKR", serif; font-size: 120px; font-weight: 900; color: #d93a2b; font-style: italic; }
    #q5-score svg { position: absolute; left: -10px; top: 0; width: 280px; height: 220px; overflow: visible; }
    #q5-score path { fill: none; stroke: #d93a2b; stroke-width: 7; stroke-linecap: round; }
''', header(5) + '''
      <div class="q" id="q5-q"><b>5.</b> 지금 해야 할 일을 쓰시오. <span style="font-size: 40px; font-weight: 600">(서술형)</span></div>
      <div id="q5-box"><small>답란</small><div id="q5-w1">부담 없는 상담</div><div id="q5-w2">070-4006-7128</div></div>
      <div id="q5-score"><span id="q5-100">100</span><svg viewBox="0 0 120 110"><path pathLength="1" d="M96 24 C80 6 30 6 14 32 C2 54 14 88 54 94 C92 98 114 74 106 46 C101 28 86 16 66 12" /></svg></div>''', '''
    // G25 문제 · G26 '부담 없는 상담' · G27 전화번호 · G28 100점 · G29 유지
    tl.set("#q5-score path", { strokeDasharray: "1 1", strokeDashoffset: 1 }, 0);
    IN("#q5-q", B[25], { y: 40 }, 0.18);
    IN("#q5-box", B[25] + 0.08, { y: 30 }, 0.18);
    tl.set(["#q5-w1", "#q5-w2", "#q5-100"], { opacity: 0 }, 0);
    WRITE("#q5-w1", B[26], 0.32);
    WRITE("#q5-w2", B[27], 0.36);
    WRITE("#q5-100", B[28], 0.2);
    PEN("#q5-score path", B[28] + 0.1, 0.26);
    OUT(CAM, D, { y: -200 });
'''))

# ---------- 정답지 = CTA G30–28s ----------
SLOTS.append(scene("cta", 30, None, '''
    #ct-band { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #ct-label { position: absolute; left: 110px; width: 860px; top: 300px; text-align: center; font-size: 40px; font-weight: 800; letter-spacing: 0.3em; color: #d93a2b; }
    #ct-l1 { position: absolute; left: 60px; width: 960px; top: 400px; text-align: center; font-family: "NotoSerifKR", serif; font-size: 96px; font-weight: 800; }
    #ct-l2 { position: absolute; left: 60px; width: 960px; top: 530px; text-align: center; font-size: 150px; font-weight: 900; color: #2e5cbe; line-height: 1.05; }
    #ct-pill { position: absolute; left: 110px; width: 860px; top: 760px; display: flex; justify-content: center; }
    #ct-pill div { height: 70px; padding: 0 30px; border-radius: 999px; background: #d93a2b; color: #fff; font-size: 38px; font-weight: 900; display: flex; align-items: center; }
    #ct-btn { position: absolute; left: 110px; top: 870px; width: 860px; height: 156px; border-radius: 999px; background: linear-gradient(100deg, #12264a 0%, #2e5cbe 55%, #c9a666 100%); color: #fff; display: flex; align-items: center; justify-content: center; gap: 24px; box-shadow: 0 24px 60px rgba(46, 92, 190, 0.35); }
    #ct-btn svg { width: 60px; height: 60px; }
    #ct-btn b { font-size: 84px; font-weight: 900; letter-spacing: -0.03em; }
    #ct-cursor { position: absolute; left: 880px; top: 990px; width: 90px; height: 90px; }
    #ct-hours { position: absolute; left: 110px; width: 860px; top: 1056px; text-align: center; font-size: 38px; font-weight: 800; }
    #ct-brand { position: absolute; left: 110px; width: 860px; top: 1114px; text-align: center; font-size: 38px; font-weight: 800; color: #7d6233; }
    #ct-fine { top: 1180px; text-align: center; }
''', '''      <div id="ct-label">정 답 지</div>
      <div id="ct-l1">정답과 해설은,</div>
      <div id="ct-l2">상담에서.</div>
      <div id="ct-pill"><div>11/10 접수 마감 · 11/4 개강</div></div>
      <div id="ct-btn"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="#fff" /></svg><b>070-4006-7128</b></div>
      <svg id="ct-cursor" viewBox="0 0 24 24" data-layout-ignore><path d="M5 3l14 7-6.2 1.8L10.8 18z" fill="#ffffff" stroke="#0b1a33" stroke-width="1.6" stroke-linejoin="round" /></svg>
      <div id="ct-hours">평일 10~18시 · 내 학력 기준 1:1 상담</div>
      <div id="ct-brand">경찰복지사이버평생교육원</div>
      <div id="ct-fine" class="fine">※ 변호사·검사·법무관은 로스쿨 졸업·변호사시험 합격 등<br />별도 요건이 필요하며, 입학·합격·취업을 보장하지 않습니다.</div>''', '''
    // G30 정답지 · G31 상담에서. · G32 마감 · G33 버튼 · G34 커서 · G35 클릭 · 정보
    IN(["#ct-label", "#ct-l1"], B[30], { y: 40 }, 0.18);
    IN("#ct-l2", B[31], { scale: 1.3, filter: "blur(16px)" }, 0.22);
    IN("#ct-pill div", B[32], { y: 24 });
    IN("#ct-btn", B[33], { y: 60 }, 0.22);
    IN(["#ct-hours", "#ct-brand", "#ct-fine"], B[33] + 0.15, { y: 16 }, 0.2);
    tl.fromTo("#ct-cursor", { opacity: 0, x: 200, y: 220 }, { opacity: 1, x: 0, y: 0, duration: 0.3, ease: "power3.out" }, B[34]);
    tl.fromTo("#ct-btn", { scale: 1 }, { scale: 0.96, duration: 0.07, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, B[35]);
    tl.fromTo("#ct-cursor", { scale: 1 }, { scale: 0.86, duration: 0.07, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, B[35]);
'''))

# ---------- index.html hosts ----------
p = os.path.join(ROOT, "index.html")
s = open(p).read()
a = s.index("<!-- SCENES -->")
b = s.index("      <!-- BGM")
hosts = "<!-- SCENES -->\n" + "".join(f'''      <div id="{n}" class="clip" data-composition-id="{n}" data-composition-src="compositions/{n}.html"
        data-start="{st:g}" data-duration="{du:g}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
''' for n, st, du in SLOTS)
open(p, "w").write(s[:a] + hosts + s[b:])
print("\n".join(f"{n:6s} {st:6.3f} +{du:.3f}" for n, st, du in SLOTS))
