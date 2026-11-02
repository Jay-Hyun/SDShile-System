/* 컷·챕터·장면 전환 시각의 단일 출처 (30s / 15s).
 * 브라우저: window.HFCUE(cut), Node: require("./lib/cue.js")(cut). tools/timing.py · stamp_timing.py · make_audio.py 가 Node 로 읽는다.
 *
 * 음악 편집 (v3.2, 끊김 없음): 첫 구간(원곡 다운비트 1.007에서)을 정수 박자 R 까지 이어 재생하고,
 * R 에서 두 번째 구간의 다운비트 시작(원곡 12.524 / 14.443)으로 6ms 등전력 크로스페이드로 잇는다.
 * 두 번째 구간 안은 그대로라 원곡 B섹션 크래시(src 16.363)가 R + (src 16.363 − 두 번째 구간 src) = 브랜드 진입이다.
 *   30s: R = 박자 30 (14.3965)  → 두 번째 구간 src 12.524, 크래시 = R + 2마디
 *   15s: R = 박자 14 ( 6.7184)  → 두 번째 구간 src 14.443, 크래시 = R + 1마디
 */
(function (root) {
  const P = 60 / 125.03; // 1박
  const BAR = 4 * P; // 1마디
  const FPS = 30;
  const snap = (t) => Math.round(t * FPS) / FPS;

  function cue(cut) {
    const is30 = cut === 30;
    const R = (is30 ? 30 : 14) * P; // 음악 이음새 = 🙂 답이 뜨는 다운비트
    const BR = R + (is30 ? 2 : 1) * BAR; // 원곡 크래시 = 오프닝 윈도우의 중간점 = 브랜드 진입
    const WIN = snap(BR - 0.6); // [상담사 연결]이 열리기 시작 (1200ms in-out, 중간점 = BR)
    const c = { cut, P, BAR, R, BR, WIN, END: is30 ? 30 : 15, FPS };
    // 챗 (A 구간 다운비트 = k·BAR)
    if (is30) {
      Object.assign(c, { C2: 2 * BAR, C3: 4 * BAR, C4: 5 * BAR, SEND: 5 * BAR + 0.25 + 0.6 + 0.25 + 0.5 + 0.7, GAG: 5 * BAR + 0.25 + 0.6 + 0.25 + 0.5 + 0.7 + 0.08 });
    } else {
      Object.assign(c, { C2: 3.0, UL: 2 * BAR, EX: 4.3, C3: 4.9, SEND: 4.9, GAG: 4.9 });
    }
    c.PRESS = WIN - 0.42; // 누름 탭
    c.NOTE = 0; // ※ 연출된 가상 대화입니다: 입력 독 안에 처음부터
    // 브랜드: 두 번째 구간의 다운비트(R + k·BAR)에서 챕터가 바뀐다
    c.EB = (k) => R + k * BAR;
    if (is30) Object.assign(c, { C8: R + 3 * BAR, C9: R + 4 * BAR, LIST: R + 5 * BAR, SLO: R + 6 * BAR });
    else Object.assign(c, { C5b: R + 2 * BAR, C6: R + 3 * BAR });
    return c;
  }
  cue.P = P;
  cue.BAR = BAR;
  if (typeof module !== "undefined" && module.exports) module.exports = cue;
  else root.HFCUE = cue;
})(typeof window !== "undefined" ? window : globalThis);
