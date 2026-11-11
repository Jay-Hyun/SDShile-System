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

function caption({ place, verse, ref, tIn, tOut, id = '', size = 50 }) {
  const y = H - BAR - 96;
  return [
    place && text('place' + id, place, { y: y - 70, size: 26, color: C.gold, track: 300, o: fade(tIn, tOut) }),
    text('verse' + id, verse, { y, size, o: fade(tIn + 8, tOut), sid: 'verse' + id }),
    text('ref' + id, ref, { y: y + 54, size: 25, color: C.gold, track: 80, o: fade(tIn + 16, tOut) }),
  ];
}

// ---- 1 · the road to Damascus (0–5 s) -------------------------------------------
function scene1() {
  const op = 150;
  return comp('1 다메섹 가는 길', op, [
    still('01-damascus-road.jpg', op, { z0: 1.0, z1: 1.1 }),
    dressing(op, 11),
    caption({ place: '다메섹 가는 길', verse: '사울이 주의 제자들에 대하여 여전히 위협과 살기가 등등하여', ref: '사도행전 9:1', tIn: 24, tOut: 142, size: 46 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [36, 0]]) }),
    leak(op, { inMax: 0, max: 100, dOut: 7 }),
  ]);
}

// ---- 2 · the light from heaven (5–12 s) ------------------------------------------
function scene2() {
  const op = 210;
  return comp('2 하늘의 빛', op, [
    still('02-light-from-heaven.jpg', op, { z0: 1.14, z1: 1.02, from: [0, -50], to: [0, 20] }),
    shape('glare', [ellipse(0, 0, 2600), radial(C.goldHi, 1300, 0.9, 0)], { p: [W / 2, 120], o: A([[0, 100, E.out], [70, 28], [140, 40], [210, 22]]), s: A([[0, [130, 130], E.out], [80, [90, 90]], [210, [100, 100]]]) }),
    dressing(op, 12, { dust: 40 }),
    caption({ verse: '사울아 사울아 네가 어찌하여 나를 박해하느냐', ref: '사도행전 9:4', tIn: 40, tOut: 200, size: 54 }),
    leak(op, { inMax: 100, dIn: 34, color: '#ffffff', max: 0 }),
    shape('fade-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[196, 0, E.in], [209, 100]]) }),
  ]);
}

// ---- 3 · sent out by sea (12–18 s) ---------------------------------------------
function scene3() {
  const op = 180;
  return comp('3 새벽 항해', op, [
    still('03-ship-at-dawn.jpg', op, { z0: 1.12, z1: 1.12, from: [-90, 0], to: [90, 0] }),
    dressing(op, 13),
    caption({ place: '안디옥에서 바다로', verse: '바나바와 사울을 따로 세우라', ref: '사도행전 13:2', tIn: 22, tOut: 170, size: 54 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [20, 0]]) }),
    leak(op, { inMax: 0, max: 0 }),
    shape('cut-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[172, 0, E.in], [179, 100]]) }),
  ]);
}

// ---- 4 · storm and shipwreck (18–24 s) -------------------------------------------
function scene4() {
  const op = 180;
  const bolt = t => [[t, 0, E.out], [t + 2, 78, E.out], [t + 5, 10, E.out], [t + 7, 55, E.out], [t + 16, 0]];
  return comp('4 파선', op, [
    still('04-shipwreck-storm.jpg', op, { z0: 1.16, z1: 1.16, shake: 5 }),
    shape('lightning', [rect(0, 0, W, H), fill('#dfe8ff')], { o: A([[0, 0], ...bolt(14), ...bolt(74), ...bolt(128)]) }),
    dressing(op, 14, { dust: 0 }),
    caption({ place: '고난', verse: '한 번 돌로 맞고 세 번 파선하고', ref: '고린도후서 11:25', tIn: 20, tOut: 170, size: 54 }),
    shape('cuts', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [8, 0, E.lin], [170, 0, E.in], [179, 100]]) }),
  ]);
}

// ---- 5 · midnight in Philippi (24–30 s) ------------------------------------------
function scene5() {
  const op = 180;
  return comp('5 빌립보 감옥', op, [
    still('05-philippi-prison.jpg', op, { z0: 1.0, z1: 1.1, from: [0, 20], to: [0, -20] }),
    dressing(op, 15, { dust: 34 }),
    caption({ place: '빌립보', verse: '한밤중에 바울과 실라가 기도하고 하나님을 찬송하매', ref: '사도행전 16:25', tIn: 22, tOut: 170, size: 48 }),
    shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [26, 0]]) }),
    leak(op, { inMax: 0 }),
  ]);
}

// ---- 6 · farewell at Miletus (30–36 s) --------------------------------------------
function scene6() {
  const op = 180;
  return comp('6 밀레도 작별', op, [
    still('06-miletus-farewell.jpg', op, { z0: 1.14, z1: 1.03 }),
    dressing(op, 16),
    caption({ place: '밀레도', verse: '나의 생명조차 조금도 귀한 것으로 여기지 아니하노라', ref: '사도행전 20:24', tIn: 22, tOut: 170, size: 48 }),
    leak(op, { max: 0 }),
    shape('fade-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[166, 0, E.in], [179, 100]]) }),
  ]);
}

// ---- 7 · the last letter, Rome (36–42 s) -------------------------------------------
function scene7() {
  const op = 180;
  return comp('7 로마 옥중서신', op, [
    still('07-rome-letter.jpg', op, { z0: 1.0, z1: 1.14 }),
    dressing(op, 17, { dust: 30 }),
    caption({ place: '로마', verse: '나의 달려갈 길을 마치고 믿음을 지켰으니', ref: '디모데후서 4:7', tIn: 22, tOut: 164, size: 54 }),
    shape('fades', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.out], [24, 0, E.lin], [152, 0, E.in], [176, 100]]) }),
  ]);
}

// ---- 8 · Calvary (42–50 s): 2 s of black, the climb, the burst at 48 s ----------------
function scene8() {
  const op = 240, cut = 62, burst = 180;
  return comp('8 갈보리', op, [
    still('08-calvary.jpg', op, { t0: cut, z0: 1.22, z1: 1.06, from: [0, -150], to: [0, 30], ease: E.soft, o: A([[cut, 0, E.out], [cut + 34, 100]]) }),
    shape('burst', [ellipse(0, 0, 3400), radial(C.goldHi, 1700, 1, 0)], { p: [W / 2, 400], o: A([[burst - 6, 0, E.out], [burst + 22, 100]]), s: A([[burst - 6, [6, 6], E.out], [op - 6, [110, 110]]]) }),
    dressing(op, 18, { dust: 0 }),
    text('question', '무엇이 그를 달리게 했는가', { y: H / 2 + 20, size: 62, o: fade(6, cut, 100, 22, 16), sid: 'question' }),
    caption({ verse: '내가 그리스도와 함께 십자가에 못 박혔나니', ref: '갈라디아서 2:20', tIn: cut + 30, tOut: 228, size: 54 }),
    shape('white-out', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[burst + 30, 0, E.in], [op - 2, 100]]) }),
  ]);
}

// ---- 9 · the campus at dawn (50–56 s) / 10 · title (56–60 s) ---------------------------
const Z9 = [1.0, 1.09], Z10 = [1.09, 1.15];

function scene9() {
  const op = 180;
  return comp('9 새벽 캠퍼스', op, [
    still('09-campus-dawn.jpg', op, { z0: Z9[0], z1: Z9[1] }),
    dressing(op, 19, { dust: 34 }),
    text('pledge', '이제, 우리가 달려갑니다', { y: 330, size: 82, font: 'B', o: fade(40, 172, 100, 26, 18), sid: 'pledge' }),
    caption({ verse: '아름답도다 좋은 소식을 전하는 자들의 발이여', ref: '로마서 10:15', tIn: 58, tOut: 172, size: 48 }),
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
    shape('dim', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 0, E.out], [44, 62]]) }),
    shape('letterbox-top', [rect(0, 0, W, BAR), rect(0, H - BAR, W, BAR), fill(C.black)]),
    text('title', '십자가의 전달자', { y: H / 2 + 30, size: 170, font: 'B', color: C.goldHi, animators: reveal }),
    text('group', '청년회', { y: H / 2 + 130, size: 40, color: C.white, o: A([[60, 0, E.out], [86, 100]]), sid: 'groupName' }),
  ]);
}

export const scenes = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10];
