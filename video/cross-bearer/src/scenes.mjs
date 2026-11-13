// v2 — Paul's journey. Ten scenes built from generated stills with slow camera moves.
import { W, H, C, E, A, fill, ellipse, rect, radial, linearA, group, shape, image, text, fade, comp } from './lib.mjs';

export const IMG_W = 2880, IMG_H = 1620;   // every still is normalised to this size by build.mjs
const COVER = (W / IMG_W) * 100;           // scale at which a still exactly covers the frame
const BAR = Math.round((H - W / 2.39) / 2); // 2.39:1 letterbox bar height

function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

/** Ken Burns move: zoom factors are relative to "cover"; offsets are frame pixels from centre. */
function still(file, op, { z0 = 1.04, z1 = 1.12, from = [0, 0], to = [0, 0], t0 = 0, ease = E.lin, o = 100, shake } = {}) {
  let p = A([[t0, [W / 2 + from[0], H / 2 + from[1]], ease], [op, [W / 2 + to[0], H / 2 + to[1]]]]);
  if (shake) {
    const r = rng(shake);
    p = A(Array.from({ length: Math.floor(op / 4) + 1 }, (_, i) => [i * 4, [W / 2 + (r() - 0.5) * 34, H / 2 + (r() - 0.5) * 22], E.inOut]));
  }
  return image('still-' + file, file, IMG_W, IMG_H, { p, o, s: A([[t0, [COVER * z0, COVER * z0], ease], [op, [COVER * z1, COVER * z1]]]) });
}

/** Film dressing shared by every scene: vignette, drifting dust, caption scrim, letterbox. */
function dressing(op, seed, { dust = 26 } = {}) {
  const r = rng(seed);
  return [
    shape('vignette', [ellipse(0, 0, 2400), { ty: 'gf', t: 2, o: { a: 0, k: 100 }, r: 1, s: { a: 0, k: [0, 0] }, e: { a: 0, k: [1200, 0] },
      g: { p: 3, k: { a: 0, k: [0, 0, 0, 0, 0.55, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0.55, 0.05, 1, 0.8] } } }], { p: [W / 2, H / 2] }),
    shape('dust', Array.from({ length: dust }, () => group([ellipse(r() * W, 140 + r() * 800, 2 + r() * 4), fill(C.goldHi, 18 + r() * 40)])),
      { p: A([[0, [0, 30], E.lin], [op, [28, -50]]]), o: A([[0, 55], [op / 2, 100], [op, 55]]) }),
    shape('scrim', [rect(0, 620, W, H - 620), linearA(620, H - BAR, C.black, 0, 0.82)]),
    shape('letterbox', [rect(0, 0, W, BAR), rect(0, H - BAR, W, BAR), fill(C.black)]),
  ];
}

/** Light-leak transition: the frame blooms in from, and out to, warm light. */
const leak = (op, { dIn = 14, dOut = 9, max = 70, color = C.goldHi, inMax = max } = {}) =>
  shape('leak', [rect(0, 0, W, H), fill(color)], { o: A([[0, inMax, E.out], [dIn, 0, E.lin], [op - dOut, 0, E.in], [op - 1, max]]) });

/** Lyric caption: one or two sung lines (large) and the passage they come from (small, gold). */
function caption({ lines, ref, tIn, tOut, size = 60, id = '', yBase = H - BAR - 92, gap = 78, stagger = 16 }) {
  const n = lines.length;
  return [
    ...lines.map((ln, k) => text(`lyric${id}-${k}`, ln, { y: yBase - (n - 1 - k) * gap, size, o: fade(tIn + k * stagger, tOut), sid: `lyric${id}${k + 1}` })),
    ref && text('ref' + id, ref, { y: yBase + 52, size: 25, color: C.gold, track: 80, o: fade(tIn + n * stagger + 6, tOut, 100, 12) }),
  ];
}

// ================= 기 · the call =================
// ---- 1 · the road to Damascus (0–6 s) -------------------------------------------
function scene1() {
  const op = 180;
  return comp('1 다메섹 가는 길', op, [
    still('01-damascus-road.jpg', op, { z0: 1.0, z1: 1.1 }),
    dressing(op, 11),
    caption({ lines: ['죄인 중에 괴수'], ref: '디모데전서 1:15', tIn: 40, tOut: 170, size: 66 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [40, 0]]) }),
    leak(op, { inMax: 0, max: 100, dOut: 7 }),
  ]);
}

// ---- 2 · the light from heaven (6–14 s) ------------------------------------------
function scene2() {
  const op = 240;
  return comp('2 하늘의 빛', op, [
    still('02-light-from-heaven.jpg', op, { z0: 1.14, z1: 1.02, from: [0, -50], to: [0, 20] }),
    shape('glare', [ellipse(0, 0, 2600), radial(C.goldHi, 1300, 0.9, 0)], { p: [1640, 150], o: A([[0, 100, E.out], [80, 28], [160, 40], [240, 22]]), s: A([[0, [130, 130], E.out], [90, [90, 90]], [240, [100, 100]]]) }),
    dressing(op, 12, { dust: 40 }),
    caption({ lines: ['난 지극히 작은 자', '무익한 날 부르셔서'], ref: '에베소서 3:8', tIn: 44, tOut: 228 }),
    leak(op, { inMax: 100, dIn: 34, color: '#ffffff', max: 0 }),
    shape('fade-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[224, 0, E.in], [239, 100]]) }),
  ]);
}

// ================= 승 · sent =================
// ---- 3 · sent out at golden dawn (14–20 s) ----------------------------------------
function scene3() {
  const op = 180;
  return comp('3 금빛 새벽 항해', op, [
    still('03-ship-at-dawn.jpg', op, { z0: 1.12, z1: 1.12, from: [-90, 0], to: [90, 0] }),
    dressing(op, 13),
    caption({ lines: ['간절한 기대와 소망', '부끄럽지 않게'], ref: '빌립보서 1:20', tIn: 26, tOut: 170 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [30, 0]]) }),
    leak(op, { inMax: 0, max: 0 }),
    shape('cut-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[172, 0, E.in], [179, 100]]) }),
  ]);
}

// ---- 4 · storm and shipwreck (20–25 s) -------------------------------------------
export const BOLTS = [12, 58, 102]; // lightning frames; music.py hits a drum on each
function scene4() {
  const op = 150;
  const bolt = t => [[t, 0, E.out], [t + 2, 78, E.out], [t + 5, 10, E.out], [t + 7, 55, E.out], [t + 16, 0]];
  return comp('4 파선', op, [
    still('04-shipwreck-storm.jpg', op, { z0: 1.16, z1: 1.16, shake: 5 }),
    shape('lightning', [rect(0, 0, W, H), fill('#dfe8ff')], { o: A([[0, 0], ...BOLTS.flatMap(bolt)]) }),
    dressing(op, 14, { dust: 0 }),
    caption({ lines: ['어디든지 가리라', '주 위해서라면'], ref: '고린도후서 11:25', tIn: 16, tOut: 142, stagger: 12 }),
    shape('cuts', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [8, 0, E.lin], [141, 0, E.in], [149, 100]]) }),
  ]);
}

// ---- 5 · midnight in Philippi (25–31 s) ------------------------------------------
function scene5() {
  const op = 180;
  return comp('5 빌립보 감옥', op, [
    still('05-philippi-prison.jpg', op, { z0: 1.0, z1: 1.1, from: [0, 20], to: [0, -20] }),
    dressing(op, 15, { dust: 34 }),
    caption({ lines: ['내 몸에 밴 십자가', '그 보혈의 향기'], ref: '갈라디아서 6:17', tIn: 24, tOut: 170 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [26, 0]]) }),
    leak(op, { inMax: 0 }),
  ]);
}

// ================= 전 · the cross =================
// ---- 6 · farewell at Miletus (31–37 s) --------------------------------------------
function scene6() {
  const op = 180;
  return comp('6 밀레도 작별', op, [
    still('06-miletus-farewell.jpg', op, { z0: 1.14, z1: 1.03 }),
    dressing(op, 16),
    caption({ lines: ['살아도 주를 위해', '죽어도 주를 위해'], ref: '로마서 14:8', tIn: 22, tOut: 168 }),
    leak(op, { max: 0 }),
    shape('fade-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[166, 0, E.in], [179, 100]]) }),
  ]);
}

// ---- 7 · the last letter, Rome (37–42 s) -------------------------------------------
function scene7() {
  const op = 150;
  return comp('7 로마 옥중서신', op, [
    still('07-rome-letter.jpg', op, { z0: 1.0, z1: 1.14 }),
    dressing(op, 17, { dust: 30 }),
    caption({ lines: ['사나 죽으나 난 주의 것'], ref: '로마서 14:8', tIn: 22, tOut: 134, size: 64 }),
    shape('fades', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [24, 0, E.lin], [124, 0, E.in], [146, 100]]) }),
  ]);
}

// ---- 8 · Calvary (42–50 s): 2 s of black, the climb, the burst at 48 s ----------------
function scene8() {
  const op = 240, cut = 62, burst = 180;
  return comp('8 갈보리', op, [
    still('08-calvary.jpg', op, { t0: cut, z0: 1.22, z1: 1.06, from: [0, -150], to: [0, 30], ease: E.soft, o: A([[cut, 0, E.out], [cut + 34, 100]]) }),
    shape('burst', [ellipse(0, 0, 3400), radial(C.goldHi, 1700, 1, 0)], { p: [1250, 470], o: A([[burst - 6, 0, E.out], [burst + 22, 100]]), s: A([[burst - 6, [6, 6], E.out], [op - 6, [110, 110]]]) }),
    dressing(op, 18, { dust: 0 }),
    caption({ id: 'a', lines: ['십자가의 능력', '십자가의 소망'], ref: '고린도전서 1:18', tIn: 4, tOut: cut + 4, size: 64, yBase: H / 2 + 50, gap: 86, stagger: 10 }),
    caption({ id: 'b', lines: ['내 안에 주만 사시는 것'], ref: '갈라디아서 2:20', tIn: cut + 40, tOut: 228, size: 66 }),
    shape('white-out', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[burst + 30, 0, E.in], [op - 2, 100]]) }),
  ]);
}

// ================= 결 · handed on =================
// ---- 9 · campus mission at golden dawn (50–56 s) / 10 · title (56–60 s) -----------------
const Z9 = [1.0, 1.09], Z10 = [1.09, 1.15];

function scene9() {
  const op = 180;
  return comp('9 캠퍼스 선교', op, [
    still('09-campus-dawn.jpg', op, { z0: Z9[0], z1: Z9[1] }),
    dressing(op, 19, { dust: 34 }),
    caption({ lines: ['무익한 날 부르셔서', '십자가 전케 하셨네'], ref: '오늘, 캠퍼스에서', tIn: 44, tOut: 172, size: 64 }),
    shape('white-in', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[0, 100, E.out], [40, 0]]) }),
  ]);
}

function scene10() {
  const op = 120;
  const reveal = [{ nm: 'reveal', a: { o: { a: 0, k: 0 } },
    s: { t: 0, b: 1, sh: 1, r: 1, rn: 0, xe: { a: 0, k: 0 }, ne: { a: 0, k: 0 }, a: { a: 0, k: 100 }, o: { a: 0, k: 0 }, e: { a: 0, k: 100 },
      s: A([[10, 0, E.soft], [62, 100]]) } }];
  return comp('10 타이틀', op, [
    still('09-campus-dawn.jpg', op, { z0: Z10[0], z1: Z10[1] }),
    dressing(op, 20, { dust: 34 }),
    shape('dim', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 0, E.out], [44, 66]]) }),
    shape('letterbox-top', [rect(0, 0, W, BAR), rect(0, H - BAR, W, BAR), fill(C.black)]),
    text('title', '십자가의 전달자', { y: H / 2 + 30, size: 170, font: 'B', color: C.goldHi, animators: reveal }),
    text('group', '로뎀청년회', { y: H / 2 + 132, size: 44, color: C.white, o: A([[60, 0, E.out], [86, 100]]), sid: 'groupName' }),
  ]);
}

export const scenes = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10];
