// v6 — Paul from Acts to the letters: twelve shots, then Calvary, the campus and the title.
// Shots cross-fade into each other; nothing flashes.
import { W, H, C, E, A, fill, ellipse, rect, radial, linearA, group, shape, image, text, fade, comp } from './lib.mjs';

export const IMG_W = 2880, IMG_H = 1620;   // every still is normalised to this size by build.mjs
const COVER = (W / IMG_W) * 100;           // scale at which a still exactly covers the frame
const BAR = Math.round((H - W / 2.39) / 2); // 2.39:1 letterbox bar height

function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

/** Ken Burns move: zoom factors are relative to "cover"; offsets are frame pixels from centre. */
function still(file, op, { z0 = 1.04, z1 = 1.12, from = [0, 0], to = [0, 0], o = 100, shake, nm = 'still-' + file } = {}) {
  let p = A([[0, [W / 2 + from[0], H / 2 + from[1]], E.lin], [op, [W / 2 + to[0], H / 2 + to[1]]]]);
  if (shake) {
    const r = rng(shake);
    p = A(Array.from({ length: Math.floor(op / 10) + 1 }, (_, i) => [i * 10, [W / 2 + (r() - 0.5) * 18, H / 2 + (r() - 0.5) * 12], E.inOut]));
  }
  return image(nm, file, IMG_W, IMG_H, { p, o, s: A([[0, [COVER * z0, COVER * z0], E.lin], [op, [COVER * z1, COVER * z1]]]) });
}

/** The previous shot frozen on its last frame, laid underneath so the new shot can cross-fade over it. */
const held = shot => image('held-' + shot.file, shot.file, IMG_W, IMG_H,
  { p: [W / 2 + (shot.to?.[0] ?? 0), H / 2 + (shot.to?.[1] ?? 0)], s: [COVER * shot.z1, COVER * shot.z1] });

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

/** Verse caption: one line of the passage (large) and its reference (small, gold). */
function caption({ line, ref, tIn, tOut, size = 50, id = '' }) {
  const y = H - BAR - 92;
  return [
    text('verse' + id, line, { y, size, o: fade(tIn, tOut, 100, 14, 12), sid: 'verse' + id }),
    text('ref' + id, ref, { y: y + 52, size: 25, color: C.gold, track: 80, o: fade(tIn + 8, tOut, 100, 12, 12) }),
  ];
}

const XF = 18; // cross-fade length; every full-frame change ramps over at least 15 frames (no flashing)

// Paul, from Acts to the letters. Each shot: still, length, camera move, one line of scripture.
const SHOTS = [
  // ---- 기 · the persecutor is called
  { nm: '스데반의 죽음을 지켜보다', file: '10-stephen.jpg', op: 120, z0: 1.0, z1: 1.08,
    line: '내가 전에는 비방자요 박해자요 폭행자였으나', ref: '디모데전서 1:13' },
  { nm: '다메섹 가는 길', file: '01-damascus-road.jpg', op: 120, z0: 1.1, z1: 1.02,
    line: '죄인 중에 내가 괴수니라', ref: '디모데전서 1:15', size: 58 },
  { nm: '하늘의 빛', file: '02-light-from-heaven.jpg', op: 150, z0: 1.12, z1: 1.02, from: [0, -40], to: [0, 20],
    line: '모든 성도 중에 지극히 작은 자보다 더 작은 나에게 이 은혜를 주신 것은', ref: '에베소서 3:8', size: 44 },
  { nm: '아나니아의 안수', file: '11-ananias.jpg', op: 120, z0: 1.0, z1: 1.09,
    line: '이 사람은 내 이름을 이방인과 임금들과 이스라엘 자손들에게 전하기 위하여 택한 나의 그릇이라', ref: '사도행전 9:15', size: 38 },
  // ---- 승 · sent, beaten, preaching
  { nm: '금빛 새벽 항해', file: '03-ship-at-dawn.jpg', op: 120, z0: 1.1, z1: 1.1, from: [-60, 0], to: [60, 0],
    line: '나의 간절한 기대와 소망을 따라 아무 일에든지 부끄러워하지 아니하고', ref: '빌립보서 1:20', size: 44 },
  { nm: '파선', file: '04-shipwreck-storm.jpg', op: 120, z0: 1.14, z1: 1.14, shake: 5,
    line: '한 번 돌로 맞고 세 번 파선하고', ref: '고린도후서 11:25', size: 54 },
  { nm: '빌립보 감옥', file: '05-philippi-prison.jpg', op: 120, z0: 1.0, z1: 1.08, from: [0, 16], to: [0, -16],
    line: '내가 내 몸에 예수의 흔적을 지니고 있노라', ref: '갈라디아서 6:17', size: 52 },
  { nm: '아덴에서 전하다', file: '12-athens.jpg', op: 120, z0: 1.09, z1: 1.0,
    line: '예수 그리스도와 그가 십자가에 못 박히신 것 외에는 아무 것도 알지 아니하기로', ref: '고린도전서 2:2', size: 42 },
  // ---- 전 · to the end
  { nm: '밀레도 작별', file: '06-miletus-farewell.jpg', op: 120, z0: 1.1, z1: 1.02,
    line: '나의 생명조차 조금도 귀한 것으로 여기지 아니하노라', ref: '사도행전 20:24' },
  { nm: '예루살렘에서 결박되다', file: '13-jerusalem-chains.jpg', op: 120, z0: 1.0, z1: 1.09,
    line: '주 예수의 이름을 위하여 결박 당할 뿐 아니라 예루살렘에서 죽을 것도 각오하였노라', ref: '사도행전 21:13', size: 40 },
  { nm: '로마 옥중서신', file: '07-rome-letter.jpg', op: 120, z0: 1.0, z1: 1.1,
    line: '그러므로 사나 죽으나 우리가 주의 것이로다', ref: '로마서 14:8', size: 52 },
  { nm: '마지막 새벽', file: '14-last-dawn.jpg', op: 120, z0: 1.08, z1: 1.0,
    line: '나는 선한 싸움을 싸우고 나의 달려갈 길을 마치고 믿음을 지켰으니', ref: '디모데후서 4:7', size: 46 },
];
const CALVARY = { nm: '갈보리', file: '08-calvary.jpg', op: 165, z0: 1.2, z1: 1.06, from: [0, -130], to: [0, 24] };
const CAMPUS = { nm: '캠퍼스', file: '09-campus-dawn.jpg', op: 120, z0: 1.0, z1: 1.05 };
const TITLE = { nm: '타이틀', file: '09-campus-dawn.jpg', op: 195, z0: 1.05, z1: 1.13 };  // held long so the last chord can ring

function paulScene(shot, i) {
  const { op } = shot, prev = SHOTS[i - 1];
  return comp(`${i + 1} ${shot.nm}`, op, [
    prev && held(prev),
    still(shot.file, op, { ...shot, o: prev ? A([[0, 0, E.lin], [XF, 100]]) : 100 }),
    dressing(op, 11 + i, { dust: shot.shake ? 0 : 28 }),
    caption({ line: shot.line, ref: shot.ref, size: shot.size, tIn: prev ? 10 : 30, tOut: op - 4 }),
    !prev && shape('fade-in', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 100, E.lin], [36, 0]]) }),
  ]);
}

// ---- Calvary (49–54.5 s): why he ran. The light rises from 53.5 s and carries into the campus.
function calvaryScene() {
  const { op } = CALVARY, burst = 135;
  return comp(`13 ${CALVARY.nm}`, op, [
    held(SHOTS.at(-1)),
    still(CALVARY.file, op, { ...CALVARY, o: A([[0, 0, E.lin], [30, 100]]) }),
    shape('burst', [ellipse(0, 0, 3400), radial(C.goldHi, 1700, 1, 0)], { p: [1250, 470], o: A([[burst - 14, 0, E.lin], [burst + 10, 100]]), s: A([[burst - 14, [6, 6], E.out], [op, [110, 110]]]) }),
    dressing(op, 31, { dust: 0 }),
    caption({ id: 'a', line: '십자가의 도가 … 구원을 받는 우리에게는 하나님의 능력이라', ref: '고린도전서 1:18', size: 46, tIn: 14, tOut: 92 }),
    caption({ id: 'b', line: '오직 내 안에 그리스도께서 사시는 것이라', ref: '갈라디아서 2:20', size: 54, tIn: 92, tOut: 158 }),
    shape('white-out', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[burst, 0, E.lin], [op - 1, 100]]) }),
  ]);
}

// ---- 결 · today: the campus (54.5–58.5 s) and the title (58.5–65 s)
function campusScene() {
  const { op } = CAMPUS;
  return comp(`14 ${CAMPUS.nm}`, op, [
    still(CAMPUS.file, op, CAMPUS),
    dressing(op, 32, { dust: 30 }),
    caption({ line: '우리는 십자가에 못 박힌 그리스도를 전하니', ref: '고린도전서 1:23', size: 54, tIn: 18, tOut: op - 2 }),
    shape('white-in', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[0, 100, E.lin], [34, 0]]) }),
  ]);
}

function titleScene() {
  const { op } = TITLE;
  const reveal = [{ nm: 'reveal', a: { o: { a: 0, k: 0 } },
    s: { t: 0, b: 1, sh: 1, r: 1, rn: 0, xe: { a: 0, k: 0 }, ne: { a: 0, k: 0 }, a: { a: 0, k: 100 }, o: { a: 0, k: 0 }, e: { a: 0, k: 100 },
      s: A([[4, 0, E.soft], [38, 100]]) } }];
  return comp(`15 ${TITLE.nm}`, op, [
    still(TITLE.file, op, TITLE),
    dressing(op, 33, { dust: 30 }),
    shape('dim', [rect(0, 0, W, H), fill(C.black)], { o: A([[0, 0, E.lin], [24, 66]]) }),
    shape('letterbox-top', [rect(0, 0, W, BAR), rect(0, H - BAR, W, BAR), fill(C.black)]),
    text('title', '십자가의 전달자', { y: H / 2 + 30, size: 170, font: 'B', color: C.goldHi, animators: reveal }),
    text('group', '로뎀청년회', { y: H / 2 + 132, size: 44, color: C.white, o: A([[32, 0, E.out], [50, 100]]), sid: 'groupName' }),
    shape('fade-out', [rect(0, 0, W, H), fill(C.black)], { o: A([[op - 34, 0, E.lin], [op - 2, 100]]) }),
  ]);
}

export const scenes = [...SHOTS.map((shot, i) => () => paulScene(shot, i)), calvaryScene, campusScene, titleScene];
