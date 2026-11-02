"""Build the 15-second cut (05-ask-ai.md §3) as the sub-project v15/.

Usage: python3 tools/build_15s.py      (run from reels/naver-clip/ask-ai)
HyperFrames check/snapshot read only a project's index.html, so the 15s cut lives in
v15/ with its own index.html. v15/assets is a symlink to ../assets (same font, mark, audio).
Each 15s scene reuses the 30s scene's <style> block verbatim (read from compositions/*.html)
plus a few 15s overrides, so a style change in the 30s scenes carries over on the next build.
The 30s files are only read, never written.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V15 = os.path.join(ROOT, "v15")


def style_of(name):
    s = open(os.path.join(ROOT, "compositions", name), encoding="utf-8").read()
    return re.search(r"<style>(.*?)</style>", s, re.S).group(1).rstrip()


def write(rel, text):
    p = os.path.join(V15, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


AVATAR = '<svg viewBox="0 0 72 72"><rect width="72" height="72" rx="20" fill="#a9afb7" /><circle cx="26" cy="36" r="6.5" fill="#2b2f35" /><circle cx="46" cy="36" r="6.5" fill="#2b2f35" /></svg>'
SEND = '<svg viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" /></svg>'
HAND = '<path d="M10 7.5c0-.83.67-1.5 1.5-1.5S13 6.67 13 7.5v6h1.76c.19 0 .37.04.54.11l4.54 2.26c.53.22.91.76.91 1.38 0 .06-.01.13-.02.2l-.75 5.27c-.11.73-.69 1.28-1.44 1.28h-6.79c-.41 0-.79-.17-1.06-.44l-4.94-4.94.79-.8c.2-.2.48-.33.79-.33.09 0 .16.02.24.03l3.43.72z" fill="#ffffff" stroke="{stroke}" stroke-width="1.1" stroke-linejoin="round" />'
EMO = '<svg id="a2-emo" class="emo" viewBox="0 0 36 36"><circle cx="18" cy="18" r="17" fill="#ffcc4d" /><ellipse cx="12.5" cy="14" rx="2.3" ry="3.2" fill="#664500" /><ellipse id="emo-eye" cx="23.5" cy="14" rx="2.3" ry="3.2" fill="#664500" /><path id="emo-wink" d="M20.6 14.6 Q23.5 11.6 26.4 14.6" fill="none" stroke="#664500" stroke-width="2.2" stroke-linecap="round" /><path d="M10 21.5 Q18 28.5 26 21.5" fill="none" stroke="#664500" stroke-width="2.4" stroke-linecap="round" /></svg>'

# ------------------------------------------------------------------ chat (C1–C4, 0–8.9)
CHAT_CSS = style_of("chat.html") + """
    /* ---- 15s overrides ---- */
    #ch-a1 { height: 300px; clip-path: inset(0px 0px 300px 0px round 10px 36px 36px 36px); }
    #a1-chip { margin-top: 16px; display: inline-flex; align-items: center; height: 88px; padding: 0 30px; border-radius: 44px; border: 3px solid var(--color-teal, #2a9d8f); color: #1f6f66; font-weight: 600; }
    #a1-chip b { font-weight: 800; margin-left: 12px; }
    #ch-note { top: 796px; }
    #ch-u2 { top: 860px; }
    #ch-av2 { top: 1110px; }
    #ch-dots { top: 1114px; }
    .st { top: 1118px; }
    #ch-a2 { top: 1110px; }
    #ch-btn { top: 1254px; }
    #ch-hand { top: 1284px; }
"""

CHAT_HTML = f"""<template>
  <style>{CHAT_CSS}
  </style>
  <div id="root" data-composition-id="chat" data-width="1080" data-height="1920">
    <div id="ch-cam" class="cam" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="ch-vp" data-layout-allow-overflow>
        <div id="ch-thread">
          <div id="ch-title">AI가 답 못 한 질문<i></i></div>
          <div id="ch-u1" class="bub user" data-layout-allow-occlusion>AI 시대에도 안 없어질<br />직업 알려줘.</div>

          <div id="ch-av1" class="av">{AVATAR}</div>
          <div id="ch-typing" class="bub ai"><span class="td"></span><span class="td"></span><span class="td"></span></div>

          <div id="ch-a1" class="bub ai" data-layout-allow-occlusion>
            <div id="a1-key" class="typed"><span id="hl1" class="hl">법적 책임</span>은<i class="nl"></i><span id="hl2" class="hl">사람</span> 몫입니다.<span id="a1-caret" class="caret"></span></div>
            <div id="a1-chip">예:<b>법조인</b></div>
          </div>
          <div id="ch-note">※ 연출된 가상 대화입니다</div>

          <div id="ch-u2" class="bub user">전문대 졸 직장인도<br />법 공부 돼?</div>

          <div id="ch-av2" class="av"><svg viewBox="0 0 72 72"><rect width="72" height="72" rx="20" fill="#a9afb7" /><g id="av2-eyes"><circle cx="26" cy="36" r="6.5" fill="#2b2f35" /><circle cx="46" cy="36" r="6.5" fill="#2b2f35" /></g></svg></div>
          <div id="ch-dots" class="bub ai"><span class="sd"></span><span class="sd"></span><span class="sd"></span><span id="sd4" class="sd"></span><span id="sd5" class="sd"></span></div>
          <div id="st1" class="st">고민 중…</div>

          <div id="ch-a2" class="bub ai"><span id="a2-text" class="typed"><span class="ul">책임<i id="a2-ul"></i></span>질 분께 넘길게요</span>{EMO}</div>
          <div id="ch-btn"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.6" fill="none" stroke="#fff" stroke-width="2" /><path d="M5 20c.6-3.6 3.4-5.6 7-5.6s6.4 2 7 5.6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" /><path d="M6.2 9.4V8a5.8 5.8 0 0 1 11.6 0v1.4" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" /></svg>상담사 연결</div>
          <svg id="ch-hand" viewBox="0 0 24 24">{HAND.format(stroke="#161616")}</svg>
        </div>
      </div>

      <div id="ch-comp">메시지를 입력하세요<div class="send">{SEND}</div></div>
    </div>
    <!-- 고정 앱 헤더 (카메라 줌 밖) -->
    <div id="ch-top" data-layout-allow-occlusion>
      <div id="ch-head">
        {AVATAR}
        <b>AI 어시스턴트</b>
      </div>
      <div id="ch-hr"></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});

    function items(sel) {{
      const el = document.querySelector(sel);
      const out = [];
      (function walk(node) {{
        for (const n of Array.from(node.childNodes)) {{
          if (n.nodeType === 3) {{
            const f = document.createDocumentFragment();
            for (const c of n.textContent) {{
              const s = document.createElement("span");
              s.className = "ch";
              s.textContent = c;
              f.appendChild(s);
              out.push(s);
            }}
            node.replaceChild(f, n);
          }} else if (n.nodeType === 1) {{
            if (n.classList.contains("nl")) out.push(n);
            else if (!n.classList.contains("caret") && n.tagName !== "I") walk(n);
          }}
        }}
      }})(el);
      return out;
    }}
    function TYPE(sel, t0, t1) {{
      const it = items(sel);
      const n = it.length;
      it.forEach((s, i) => {{
        tl.set(s, {{ display: s.classList.contains("nl") ? "block" : "inline" }}, +(t0 + ((t1 - t0) * i) / Math.max(1, n - 1)).toFixed(3));
      }});
    }}
    function Z(s, px, py, dy) {{
      return {{ scale: s, x: +(px * (1 - s)).toFixed(2), y: +(py * (1 - s) + (dy || 0)).toFixed(2) }};
    }}
    const seen = new Set();
    function FT(sel, a, b, t) {{
      const first = !seen.has(sel);
      seen.add(sel);
      tl.fromTo(sel, a, Object.assign({{ immediateRender: first }}, b), t);
    }}
    function CAM(t, dur, a, b, ease) {{
      FT("#ch-cam", a, Object.assign({{}}, b, {{ duration: dur, ease: ease || "power2.inOut" }}), t);
    }}
    function SCROLL(t, dur, a, b, ease) {{
      FT("#ch-thread", {{ y: -a }}, {{ y: -b, duration: dur, ease: ease || "power3.inOut" }}, t);
    }}
    function CLIP(t, dur, a, b, ease) {{
      const r = (v) => "inset(0px 0px " + v + "px 0px round 10px 36px 36px 36px)";
      FT("#ch-a1", {{ clipPath: r(a) }}, {{ clipPath: r(b), duration: dur, ease: ease || "power3.out" }}, t);
    }}

    const C0 = Z(1, 0, 0), C1 = Z(1.04, 540, 820), C2 = Z(1.03, 480, 720), C3 = Z(1.05, 420, 1150);

    // ===== C1 훅 0.0–3.0 (30초판과 같다) =====
    CAM(0, 1.5, C0, C1, "power1.out");
    tl.fromTo(["#ch-av1", "#ch-typing"], {{ opacity: 0, scale: 0.6, transformOrigin: "0% 0%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 1.5);
    tl.fromTo(".td", {{ opacity: 0.25 }}, {{ opacity: 1, duration: 0.2, yoyo: true, repeat: 5, stagger: 0.12, ease: "sine.inOut" }}, 1.62);

    // ===== C2 3.0–5.0: 타이핑 1.2초 → 1.3초 형광펜 → 1.5초 칩. 고지 3.0–8.5 =====
    tl.to("#ch-title", {{ opacity: 0, y: -30, duration: 0.2, ease: "power2.in" }}, 3.0);
    tl.to("#ch-typing", {{ opacity: 0, duration: 0.1, ease: "none" }}, 3.0);
    CLIP(3.0, 0.3, 300, 104);
    SCROLL(3.0, 0.4, -120, 160);
    CAM(3.0, 0.4, C1, C0, "power2.inOut");
    tl.fromTo("#ch-note", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, 3.0);
    tl.set("#a1-caret", {{ opacity: 1 }}, 3.1);
    TYPE("#a1-key", 3.15, 4.15);
    tl.set("#a1-caret", {{ opacity: 0 }}, 4.2);
    CAM(3.4, 1.6, C0, C2, "power1.inOut");
    tl.to("#hl1", {{ backgroundSize: "100% 46%", duration: 0.18, ease: "power2.out" }}, 4.3);
    tl.to("#hl2", {{ backgroundSize: "100% 46%", duration: 0.14, ease: "power2.out" }}, 4.4);
    CLIP(4.5, 0.25, 104, 0);
    tl.fromTo("#ch-note", {{ y: -104 }}, {{ y: 0, duration: 0.25, ease: "power3.out" }}, 4.5);
    tl.fromTo("#a1-chip", {{ scale: 0.7, transformOrigin: "0% 50%" }}, {{ scale: 1, duration: 0.3, ease: "back.out(2)" }}, 4.5);

    // ===== C3 5.0–6.8: 사용자 재질문 → 6.0 "고민 중…" (BGM 컷) =====
    tl.fromTo("#ch-u2", {{ opacity: 0, y: 240, scale: 0.92, transformOrigin: "100% 100%" }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.3)" }}, 5.0);
    SCROLL(5.0, 0.5, 160, 400, "power3.out");
    CAM(5.0, 0.4, C2, C0, "power3.out");
    tl.fromTo(["#ch-av2", "#ch-dots", "#st1"], {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "expo.out" }}, 6.0);
    CAM(6.0, 0.8, C0, C3, "none");
    tl.fromTo("#ch-dots .sd", {{ y: 0 }}, {{ y: -12, duration: 0.18, yoyo: true, repeat: 3, stagger: 0.07, ease: "sine.inOut" }}, 6.05);
    tl.fromTo("#sd4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.06, ease: "none" }}, 6.3);
    tl.fromTo("#sd5", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.06, ease: "none" }}, 6.55);
    tl.fromTo("#av2-eyes", {{ x: 0, y: 0 }}, {{ x: -7, duration: 0.2, ease: "power2.inOut" }}, 6.25);
    tl.to("#av2-eyes", {{ x: 7, duration: 0.25, ease: "power2.inOut" }}, 6.45);

    // ===== C4 6.8–8.5: '책임'을 이유로 넘긴다 → 1.1초 버튼 펄스 → 1.4초 탭 =====
    tl.to(["#ch-dots", "#st1"], {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, 6.8);
    tl.to("#av2-eyes", {{ x: 0, duration: 0.15, ease: "power2.out" }}, 6.8);
    SCROLL(6.8, 0.4, 400, 500, "power3.out");
    CAM(6.8, 0.25, C3, C0, "power3.out");
    tl.fromTo("#ch-a2", {{ opacity: 0, scale: 0.8, transformOrigin: "0% 0%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.7)" }}, 6.85);
    TYPE("#a2-text", 6.92, 7.4);
    tl.fromTo("#a2-emo", {{ scale: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.25, ease: "back.out(2.6)" }}, 7.45);
    tl.fromTo("#a2-ul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.2, ease: "power2.out" }}, 7.55);
    tl.fromTo("#emo-wink", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, ease: "none" }}, 7.75);
    tl.fromTo("#emo-eye", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.01, ease: "none" }}, 7.75);
    tl.to("#emo-wink", {{ opacity: 0, duration: 0.01, ease: "none" }}, 7.95);
    tl.to("#emo-eye", {{ opacity: 1, duration: 0.01, ease: "none" }}, 7.95);
    tl.fromTo("#ch-btn", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "expo.out" }}, 7.55);
    tl.to("#ch-btn", {{ scale: 0.95, duration: 0.08, ease: "power2.out" }}, 7.9);
    tl.to("#ch-btn", {{ scale: 1.05, duration: 0.1, ease: "power2.out" }}, 7.98);
    tl.to("#ch-btn", {{ scale: 1, duration: 0.08, ease: "power2.inOut" }}, 8.08);
    tl.fromTo("#ch-hand", {{ opacity: 0, x: 150, y: 170 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.25, ease: "power3.out" }}, 7.95);
    tl.to("#ch-hand", {{ scale: 0.86, duration: 0.07, ease: "power2.out" }}, 8.2);
    tl.to("#ch-btn", {{ scale: 0.96, backgroundColor: "#1f7a6f", boxShadow: "0 0 0 14px rgba(42, 157, 143, 0.28)", duration: 0.07, ease: "power2.out" }}, 8.2);
    tl.to("#ch-hand", {{ scale: 1, duration: 0.1, ease: "power2.out" }}, 8.28);

    window.__timelines["chat"] = tl;
  </script>
</template>
"""

# ------------------------------------------------------------------ brand (C5–C6, 8.5–15.0)
src_brand = open(os.path.join(ROOT, "compositions", "brand.html"), encoding="utf-8").read()
DESK = re.search(r'(<svg id="br-desk".*?</svg>)', src_brand, re.S).group(1)
LOGO_SVG = re.search(r'(<div id="br-cs".*?</div>)', src_brand, re.S).group(1)
TEL = re.search(r'(<div id="br-tel".*?</div>)', src_brand, re.S).group(1)
BTN = re.search(r'(<div id="br-btn">.*?</div>)', src_brand, re.S).group(1)

BRAND_CSS = style_of("brand.html").replace("circle(0px at 410px 1230px)", "circle(0px at 410px 1200px)") + """
    /* ---- 15s overrides ---- */
    #br-cs { top: 844px; }
    #br-bub { top: 840px; }
    #br-num { color: #7d6233; }
    #br-s1 { top: 760px; }
    #br-s2 { top: 880px; }
"""

BRAND_HTML = f"""<template>
  <style>{BRAND_CSS}
  </style>
  <div id="root" data-composition-id="brand" data-width="1080" data-height="1920">
    <div id="br-wrap" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="br-ground" data-layout-ignore></div>
      <div id="br-grid" data-layout-ignore></div>
      <!-- C6 배경: 저녁 책상 벡터 일러스트(스톡 대체, 블러). "연출" 배지 15.0까지 유지 -->
      {DESK}
      <div id="br-sweep" data-layout-ignore></div>

      <div id="br-cam" class="cam" data-layout-allow-overlap>
        <div id="br-logo" class="stage"><img src="assets/img/mark-gold.svg" alt="" />경찰복지사이버평생교육원</div>

        <div id="br-h1" class="stage">국내 유일</div>
        <div id="br-h2" class="stage">100% 온라인 법학사<sup>*</sup></div>

        {LOGO_SVG}
        <div id="br-bub"><svg class="stair" viewBox="0 0 24 24"><path d="M3 20h6v-5h5v-5h5V5h2" fill="none" stroke="#b8955a" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" /></svg>첫 계단,<br />전문대면 <span id="br-num"><b id="br-cnt">60</b><i id="br-numul"></i></span>학점부터</div>

        <div id="br-s1" class="slo">책임지는 자리로,</div>
        <div id="br-s2" class="slo">지금 있는 자리에서.</div>

        {BTN}
        {TEL}
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // 로컬 시간 = 전체 시간 − 8.5
    function IN(sel, t, from, dur, ease) {{
      const f = Object.assign({{ opacity: 0, filter: "blur(8px)" }}, from || {{}});
      const to = {{ opacity: 1, filter: "blur(0px)", duration: dur || 0.3, ease: ease || "expo.out" }};
      for (const k in f) if (!(k in to)) to[k] = k.startsWith("scale") ? 1 : 0;
      tl.fromTo(sel, f, to, t);
    }}
    function OUT(sel, t, to, dur) {{
      tl.to(sel, Object.assign({{ opacity: 0, filter: "blur(8px)", duration: dur || 0.2, ease: "power2.in" }}, to || {{}}), t);
    }}

    // ===== C5 반전·브랜드 + 사람의 답 8.5–12.5 =====
    tl.fromTo("#br-wrap", {{ clipPath: "circle(0px at 410px 1200px)" }}, {{ clipPath: "circle(2300px at 410px 1200px)", duration: 0.4, ease: "power2.out" }}, 0);
    tl.fromTo("#br-sweep", {{ x: 0, rotation: 18 }}, {{ x: 2700, rotation: 18, duration: 0.55, ease: "power2.inOut" }}, 0.2);
    tl.fromTo("#br-desk", {{ opacity: 0, scale: 1.06 }}, {{ opacity: 0, scale: 1.06, duration: 0.01 }}, 0);
    IN("#br-logo", 0.4, {{ y: -16 }}, 0.3);
    IN("#br-h1", 0.9, {{ y: 70, filter: "blur(10px)" }}, 0.45);
    IN("#br-h2", 1.05, {{ y: 70, filter: "blur(10px)" }}, 0.45);
    IN("#br-tel", 0.5, {{ y: 16 }}, 0.3);
    IN("#br-cs", 2.0, {{ scale: 0.6 }}, 0.3, "back.out(2)");
    tl.fromTo("#br-bub", {{ opacity: 0, scale: 0.85, transformOrigin: "0% 100%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.6)" }}, 2.2);
    const cnt = {{ v: 0 }};
    tl.fromTo(cnt, {{ v: 0 }}, {{ v: 60, duration: 0.65, ease: "power2.out", onUpdate: () => {{ document.querySelector("#br-cnt").textContent = String(Math.round(cnt.v)); }} }}, 2.35);
    tl.fromTo("#br-numul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.2, ease: "power2.out" }}, 3.0);
    tl.fromTo("#br-cam", {{ scale: 1 }}, {{ scale: 1.03, duration: 1.6, ease: "power1.inOut" }}, 2.2);

    // ===== C6 엔드카드 12.5–15.0: 1행 착지와 동시에 버튼 팝 → 13.1 2행 → 홀드 =====
    OUT(["#br-h1", "#br-h2", "#br-cs", "#br-bub"], 3.8, {{ y: -50 }});
    tl.to("#br-cam", {{ scale: 1, duration: 0.3, ease: "power2.inOut" }}, 3.8);
    tl.fromTo("#br-desk", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out", immediateRender: false }}, 3.85);
    tl.fromTo("#br-desk", {{ scale: 1.06 }}, {{ scale: 1, duration: 2.65, ease: "power1.out", immediateRender: false }}, 3.85);
    IN("#br-s1", 4.0, {{ y: -110, filter: "blur(4px)" }}, 0.45, "back.out(1.5)");
    tl.fromTo("#br-btn", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)" }}, 4.0);
    IN("#br-s2", 4.6, {{ y: -110, filter: "blur(4px)" }}, 0.45, "back.out(1.5)");

    window.__timelines["brand"] = tl;
  </script>
</template>
"""

# ------------------------------------------------------------------ legal
LEGAL_CSS = style_of("legal.html")
LEGAL_HTML = f"""<template>
  <style>{LEGAL_CSS}
  </style>
  <div id="root" data-composition-id="legal" data-width="1080" data-height="1920">
    <div id="lg-badge1" class="clip" data-start="0" data-duration="8.5" data-track-index="1"><div class="badge">가상 챗봇 화면 · 연출</div></div>
    <div id="lg-badge2" class="clip" data-start="8.5" data-duration="6.5" data-track-index="1"><div class="badge">연출</div></div>
    <div id="lg-foot-c" class="clip" data-start="8.5" data-duration="6.5" data-track-index="2"><div id="lg-foot" class="bar">*'국내 유일': 100% 온라인 법학사 과정, 2026.10 조회 기준</div></div>
    <div id="lg-warn-c" class="clip" data-start="8.5" data-duration="6.5" data-track-index="3"><div id="lg-warn" class="bar">로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다.</div></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo(["#lg-foot", "#lg-warn"], {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out", stagger: 0.05 }}, 8.6);
    tl.set({{}}, {{}}, 15);
    window.__timelines["legal"] = tl;
  </script>
</template>
"""

root_index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
head = root_index[: root_index.index("<body>")]
INDEX = head + """<body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="15"
      data-fps="30"
      data-width="1080"
      data-height="1920"
    >
      <!-- 15초판 (05-ask-ai.md §3). tools/build_15s.py 가 생성 — 직접 고치지 말 것 -->
      <!-- C1–C4 가상 챗봇 화면 (0–8.5). 8.5–8.9는 원형 마스크 아래에 깔림 -->
      <div id="chat" class="clip" data-composition-id="chat" data-composition-src="compositions/chat.html"
        data-start="0" data-duration="8.9" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 1"></div>
      <!-- C5–C6 브랜드 · 상담사 답 · 엔드카드 (8.5–15.0) -->
      <div id="brand" class="clip" data-composition-id="brand" data-composition-src="compositions/brand.html"
        data-start="8.5" data-duration="6.5" data-track-index="2" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
      <div id="legal" class="clip" data-composition-id="legal" data-composition-src="compositions/legal.html"
        data-start="0" data-duration="15" data-track-index="3" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 3"></div>

      <!-- 사운드 베드: tools/make_audio.py --cut 15 (VO는 추후) -->
      <audio id="bgm" class="clip" src="assets/audio/bgm-15s.wav" data-start="0" data-duration="15" data-track-index="4" data-volume="1"></audio>
      <audio id="sfx" class="clip" src="assets/audio/sfx-15s.wav" data-start="0" data-duration="15" data-track-index="5" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    os.makedirs(V15, exist_ok=True)
    write("index.html", INDEX)
    write("compositions/chat.html", CHAT_HTML)
    write("compositions/brand.html", BRAND_HTML)
    write("compositions/legal.html", LEGAL_HTML)
    for name in ("hyperframes.json",):
        write(name, open(os.path.join(ROOT, name), encoding="utf-8").read())
    write("meta.json", '{\n  "id": "naver-clip-ask-ai-15s",\n  "name": "naver-clip-ask-ai-15s",\n  "createdAt": "2026-11-02T05:00:00.000Z"\n}\n')
    write(".gitignore", ".hyperframes/\n")
    link = os.path.join(V15, "assets")
    if not os.path.islink(link):
        os.symlink("../assets", link)
    print("wrote", V15)
