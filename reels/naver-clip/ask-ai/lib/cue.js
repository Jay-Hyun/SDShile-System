/* v7 편 A 「AI에게 물었다」 — 컷·챕터·레이아웃 상수의 단일 출처 (30s / 15s).
 * 브라우저: window.HFCUE(cut), Node: import("./lib/cue.js") 뒤 globalThis.HFCUE(cut). tools/timing.py 가 Node 로 읽는다.
 *
 * 음악: Alex_Besss "News Background" (Pixabay 602905), 130.002 BPM. 원곡 다운비트(_shared/beats/C-alex.json beats[3::4]).
 * 발췌 in-point = 원곡 다운비트 3.239 s (영상 0 = 다운비트, 첫 프레임부터 음악이 들린다). 한 번도 자르지 않고 30 s / 15 s 이어 재생.
 * 영상 다운비트 V[k] = 원곡 다운비트(3.239 이후 k번째) − 3.239. 1마디 ≈ 1.846 s (55.4 f).
 */
(function (root) {
  const SRC_DB = [3.239, 5.085, 6.931, 8.777, 10.623, 12.469, 14.315, 16.173, 18.007, 19.853, 21.699, 23.545, 25.391, 27.237, 29.083, 30.941, 32.787];
  const IN = 3.239;
  const FPS = 30;
  const snap = (t) => Math.round(t * FPS) / FPS;
  const V = SRC_DB.map((t) => snap(t - IN)); // 영상 다운비트(프레임 스냅)
  const P = 60 / 130.002;
  const BAR = 4 * P;

  function cue(cut) {
    const is30 = cut === 30;
    const c = { cut, IN, V, P, BAR, FPS, END: is30 ? 30 : 15 };
    c.JUMP = V[1]; // 마디 2: 질문이 폰에서 튀어 올라 Display 144 (종이 띠)
    c.DIVE = V[2]; // 마디 3: 폰 화면이 세계가 된다 (0.65 s in-out)
    c.DIVE_D = 0.65;
    c.TAP1 = 1.2; // 셋째 덩어리 타이핑 탭
    c.TAP2 = c.JUMP - 0.04; // 전송 탭
    if (is30) {
      Object.assign(c, {
        LEAD: V[3], // AI 답 앞 문단 (흐림)
        KEY: V[4], // 핵심 문장
        HAND: V[5], // 핸드오프 말풍선
        TRACK: V[6] + 0.5, // 카메라가 말풍선으로 (0.6 s)
        WORLD: V[7], // 말풍선이 세계가 됨 → 주말 책상 (도착 = 다운비트)
        ANS2: V[9], // 상담사 답 ②
        DIP1: V[11], // 딥컷 → 부엌 + 종이 카드
        DIP2: V[13], // 딥컷 → 계단 + 슬로건
        FLOOD: V[14], // 컬러 플러드 → Navy 엔드카드
      });
    } else {
      Object.assign(c, {
        HAND: V[2] + 0.95,
        TRACK: V[3] + 0.5,
        WORLD: V[4],
        DIP2: V[5],
        FLOOD: V[6],
      });
    }
    c.GROW_D = 0.65;
    c.GROW = snap(c.WORLD - c.GROW_D); // 말풍선이 자라기 시작
    c.TRACK_D = 0.6;
    // ---- 레이아웃 (프레임 좌표, 화면 1080×1920) ----
    // 채팅: 헤더 y 240–302, 입력 독(전체 폭 필드) y 1440–1920, 사이 302–1440 에 말풍선 스택을 위·아래 같은 틈으로.
    const HB = 302, DT = 1440, G = 40;
    const L = { HB, DT, G };
    if (is30) {
      L.hU = 212; // 사용자 말풍선: Body 44 두 줄 + 패딩 44
      L.hA1 = 617; // AI 답: Head 88 다섯 줄 + 패딩 56
      L.hA2 = 298; // 핸드오프: Head 88 두 줄 + 패딩 48
      const sA = L.hU + G + L.hA1;
      L.yU = HB + Math.round((DT - HB - sA) / 2);
      L.yA1 = L.yU + L.hU + G;
      const sB = L.hA1 + G + L.hA2;
      L.offB = HB + Math.round((DT - HB - sB) / 2) - L.yA1; // HAND 에서 스택이 올라가는 양
      L.yA2 = L.yA1 + L.hA1 + G; // 스레드 좌표
    } else {
      L.hU = 415; // 사용자 말풍선: Head 88 세 줄 + 패딩 56
      L.hA2 = 415; // 핸드오프: Head 88 세 줄 + 패딩 56
      const s = L.hU + G + L.hA2;
      L.yU = HB + Math.round((DT - HB - s) / 2);
      L.yA2 = L.yU + L.hU + G;
      L.offB = 0;
    }
    // 카메라 트랙: 핸드오프 말풍선을 1.10배로 당겨 중심을 y 1060 으로 (위 말풍선이 y 168 위 UI 띠로 밀려나지 않을 만큼만)
    L.TS = 1.1;
    const CYT = 1060;
    const a2c = L.yA2 + L.offB + L.hA2 / 2;
    L.trackY = CYT - a2c;
    L.a2c = a2c;
    const hw = (840 * L.TS) / 2, hh = (L.hA2 * L.TS) / 2;
    L.bub = { t: CYT - hh, b: CYT + hh, l: 540 - hw, r: 540 + hw, rad: 36 * L.TS };
    c.L = L;
    return c;
  }
  cue.P = P;
  cue.BAR = BAR;
  cue.V = V;
  if (typeof module !== "undefined" && module.exports) module.exports = cue;
  else root.HFCUE = cue;
})(typeof window !== "undefined" ? window : globalThis);
