/* 비트 그리드 + anime.js v4 헬퍼 (HyperFrames 결정적 렌더용)
 * - 모든 시간은 "영상 절대 초". HyperFrames의 anime 어댑터는 하위 컴포지션에도 절대 시간(ms)으로 seek 한다.
 * - P = 1비트 (beats/source.json bpm 125.03). 시간은 30fps 프레임에 스냅한다.
 * - 랜덤은 anime.createSeededRandom 만 쓴다. rAF·타이머 없음.
 */
(function () {
  const A = window.anime;
  const P = 60 / 125.03;
  const FPS = 30;
  const fr = (t) => Math.round(t * FPS);
  const ms = (t) => (fr(t) * 1000) / FPS; // 프레임 스냅된 ms
  const FRAME = 1000 / FPS;

  function timeline() {
    const tl = A.createTimeline({ autoplay: false, defaults: { ease: "outExpo", duration: 300 } });
    window.__hfAnime = window.__hfAnime || [];
    window.__hfAnime.push(tl);
    return tl;
  }

  // 텍스트 노드를 글자 span(.ch, inline-block)으로 쪼갠다. 공백은 텍스트로 남겨 줄바꿈·간격 유지.
  function split(root) {
    const el = typeof root === "string" ? document.querySelector(root) : root;
    const out = [];
    (function walk(node) {
      for (const n of Array.from(node.childNodes)) {
        if (n.nodeType === 3) {
          const f = document.createDocumentFragment();
          for (const c of n.textContent) {
            if (/\s/.test(c)) {
              f.appendChild(document.createTextNode(c));
              continue;
            }
            const s = document.createElement("span");
            s.className = "ch";
            s.textContent = c;
            f.appendChild(s);
            out.push(s);
          }
          node.replaceChild(f, n);
        } else if (n.nodeType === 1 && !n.hasAttribute("data-nosplit")) walk(n);
      }
    })(el);
    return out;
  }

  // 글자 타이핑: step 초 간격(16분 = P/4, 32분 = P/8)으로 한 글자씩 팝
  function type(tl, chars, t0, step, opts) {
    const o = Object.assign({ y: 14, scale: 0.6 }, opts || {});
    chars.forEach((c, i) => {
      tl.add(c, { opacity: [0, 1], translateY: [o.y, 0], scale: [o.scale, 1], duration: 160, ease: "outBack(2.2)" }, ms(t0 + i * step));
    });
    return t0 + (chars.length - 1) * step;
  }

  // 시드 고정 흔들림: n프레임 동안 감쇠하는 x/y 지터, 끝은 0
  function shake(tl, target, t, amp, frames, seed) {
    const rnd = A.createSeededRandom(seed);
    const xs = [], ys = [];
    for (let i = 0; i < frames; i++) {
      const k = amp * (1 - i / frames);
      xs.push({ to: rnd(-1000, 1000) / 1000 * k, duration: FRAME, ease: "linear" });
      ys.push({ to: rnd(-1000, 1000) / 1000 * k, duration: FRAME, ease: "linear" });
    }
    xs.push({ to: 0, duration: FRAME, ease: "linear" });
    ys.push({ to: 0, duration: FRAME, ease: "linear" });
    tl.add(target, { translateX: xs, translateY: ys }, ms(t));
  }

  // 1프레임 플래시 (컷)
  function flash(tl, el, t, a) {
    tl.set(el, { opacity: a == null ? 0.8 : a }, ms(t));
    tl.set(el, { opacity: 0 }, ms(t) + FRAME);
  }

  window.HF = { A, P, B: (k) => k * P, ms, fr, FRAME, timeline, split, type, shake, flash };
})();
