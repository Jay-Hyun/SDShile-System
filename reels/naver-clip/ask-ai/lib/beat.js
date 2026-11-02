/* 비트 그리드 + anime.js v4 모션 어휘 (HyperFrames 결정적 렌더용, 아트 디렉션 v3)
 * - 모든 시간은 "영상 절대 초". HyperFrames의 anime 어댑터는 하위 컴포지션에도 절대 시간(ms)으로 seek 한다.
 * - P = 1비트, BAR = 1마디(4P) (beats/source.json bpm 125.03). 시간은 30fps 프레임에 스냅한다.
 * - 컷·챕터 전환만 다운비트에 둔다. 장면 안의 모션은 비트에 치지 않고 아래 곡선으로 흐른다.
 * - rAF·타이머·랜덤 없음.
 */
(function () {
  const A = window.anime;
  const P = 60 / 125.03;
  const BAR = 4 * P;
  const FPS = 30;
  const fr = (t) => Math.round(t * FPS);
  const ms = (t) => (fr(t) * 1000) / FPS; // 프레임 스냅된 ms
  const FRAME = 1000 / FPS;

  // 02-art-direction.md §4 모션 어휘
  const E = {
    rise: A.cubicBezier(0.16, 1, 0.3, 1), // 마스크 라인 상승 800ms
    ui: A.cubicBezier(0.22, 1, 0.36, 1), // UI 등장 320ms
    exit: A.cubicBezier(0.55, 0.055, 0.675, 0.19), // 퇴장 300ms
    draw: A.cubicBezier(0.76, 0, 0.24, 1), // 라인 드로잉 1100ms · 오프닝 윈도우 1200ms
    glide: A.cubicBezier(0.65, 0, 0.35, 1), // 컬럼 글라이드 450ms (in-out)
    roll: A.cubicBezier(0.33, 1, 0.68, 1), // 숫자 롤 700ms (ease-out)
  };
  const D = { rise: 800, ui: 320, exit: 300, draw: 1100, open: 1200, glide: 450, roll: 700, press: 140, line: 90 };

  function timeline() {
    const tl = A.createTimeline({ autoplay: false, defaults: { ease: E.ui, duration: D.ui } });
    window.__hfAnime = window.__hfAnime || [];
    window.__hfAnime.push(tl);
    return tl;
  }

  // 마스크 라인 상승: 줄마다 자기 기준선 마스크(.ln, overflow hidden)에서 105% → 0, 줄 사이 90ms (최대 4단계)
  function rise(tl, inners, t, gap) {
    const list = Array.isArray(inners) ? inners : [inners];
    list.forEach((el, i) => tl.add(el, { translateY: ["105%", "0%"], duration: D.rise, ease: E.rise }, ms(t + i * (gap == null ? D.line / 1000 : gap))));
  }
  // 줄이 마스크 위로 빠져나간다 (교체식 문구). 퇴장 곡선, 300ms
  function riseOut(tl, inner, t) {
    tl.add(inner, { translateY: ["0%", "-105%"], duration: D.exit, ease: E.exit }, ms(t));
  }
  // UI 등장: 16px 상승 + 불투명도, 320ms. 오버슈트 없음
  function ui(tl, el, t) {
    tl.add(el, { opacity: [0, 1], translateY: [16, 0], duration: D.ui, ease: E.ui }, ms(t));
  }
  // 퇴장: 불투명도 + 8px 상승, 300ms
  function exit(tl, el, t) {
    tl.add(el, { opacity: [1, 0], translateY: [0, -8], duration: D.exit, ease: E.exit }, ms(t));
  }
  // 카메라: 컷 하나에 한 번, 1.00 → 1.03 선형 푸시
  function push(tl, el, t0, t1, s0, s1) {
    tl.add(el, { scale: [s0 == null ? 1 : s0, s1 == null ? 1.03 : s1], duration: ms(t1) - ms(t0), ease: "linear" }, ms(t0));
  }

  window.HF = { A, P, BAR, B: (k) => k * P, ms, fr, FRAME, E, D, timeline, rise, riseOut, ui, exit, push };
})();
