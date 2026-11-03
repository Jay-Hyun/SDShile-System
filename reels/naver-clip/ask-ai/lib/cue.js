/* 컷·챕터·장면 전환 시각의 단일 출처 (30s / 15s) — v6 편 A(청년).
 * 브라우저: window.HFCUE(cut), Node: import("./lib/cue.js") 뒤 globalThis.HFCUE(cut). tools/timing.py · stamp_timing.py · make_audio.py 가 Node 로 읽는다.
 *
 * 음악은 그대로(Pixabay 505611, 125.03 BPM), 끊김 없음: 첫 구간(원곡 다운비트 1.007에서)을 정수 박자 R 까지 이어 재생하고,
 * R 에서 두 번째 구간의 다운비트 시작(원곡 12.524 / 14.443)으로 6ms 등전력 크로스페이드로 잇는다. 마지막 구간 C(원곡 29.8)는 끝에서부터 맞춘다.
 * 두 번째 구간 안은 그대로라 원곡 B섹션 크래시(src 16.363)가 R + (src 16.363 − 두 번째 구간 src) = 브랜드 진입(BR)이다.
 *   30s: R = 박자 22 (10.557) → B src 12.524 (8마디 = 32박), 크래시 = R + 2마디 = 박자 30 (14.396), C(CS) = 박자 54 (25.914)
 *   15s: R = 박자 14 ( 6.718) → B src 14.443 (2마디),         크래시 = R + 1마디 ( 8.638), C(CS) = R + 2마디 (10.557)
 * v6 챕터(30s): 0 훅(입력창에 질문) · 3.84 전송 · 5.76/7.68 AI 답 · R(10.56) 책임 넘김 · BR(14.40) 상담사 답 ① · 18.24 ② · 22.07 근거 · 25.91 슬로건+CTA
 */
(function (root) {
  const P = 60 / 125.03; // 1박
  const BAR = 4 * P; // 1마디
  const FPS = 30;
  const snap = (t) => Math.round(t * FPS) / FPS;

  function cue(cut) {
    const is30 = cut === 30;
    const R = (is30 ? 22 : 14) * P; // 음악 이음새 = 🙂 답(30s)·B 시작(15s)이 뜨는 다운비트
    const BR = R + (is30 ? 2 : 1) * BAR; // 원곡 크래시 = 오프닝 윈도우의 중간점 = 브랜드 진입
    const WIN = snap(BR - 0.6); // [상담사 연결]이 열리기 시작 (1200ms in-out, 중간점 = BR)
    const CS = is30 ? 54 * P : R + 2 * BAR; // 마지막 음악 구간 C 시작 (끝에서부터 맞춘 다운비트)
    const c = { cut, P, BAR, R, BR, WIN, CS, END: is30 ? 30 : 15, FPS };
    // 챗 (A 구간 다운비트 = k·BAR). 입력창에 질문이 들어가는 훅 → 전송(C2) 에서 입력창이 접히고 대화가 시작된다
    c.C2 = 2 * BAR;
    c.SEND = c.C2 - 0.14; // 보내기 누름(140ms) 이 C2 다운비트에서 끝난다
    c.GAG = c.C2; // (호환) 입력창이 비는 시각
    c.PRESS = WIN - 0.42; // 누름 탭
    c.NOTE = 0; // ※ 연출된 가상 대화입니다: 입력 독 안에 처음부터
    c.EB = (k) => R + k * BAR;
    if (is30) {
      Object.assign(c, {
        C2b: 3 * BAR, // 흐린 앞 문단
        C3: 4 * BAR, // 핵심 문장
        HAND: R, // 🙂 책임 넘김
        S2: BR + 2 * BAR, // 상담사 답 ②
        S3: BR + 4 * BAR, // 근거 3줄
        S4: CS, // 슬로건 (인용 → 슬로건 교체)
      });
    } else {
      Object.assign(c, {
        HAND: 3 * BAR, // 🙂 책임 넘김 (A 구간 다운비트)
        C6: R + 3 * BAR, // 엔드카드 하드컷 = 마지막 크래시
      });
    }
    return c;
  }
  cue.P = P;
  cue.BAR = BAR;
  if (typeof module !== "undefined" && module.exports) module.exports = cue;
  else root.HFCUE = cue;
})(typeof window !== "undefined" ? window : globalThis);
