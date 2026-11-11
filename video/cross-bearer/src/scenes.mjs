// The nine scenes of the opening film. Each function returns a Lottie composition.
import { W, H, C, E, A, hex, fill, stroke, trim, ellipse, rect, radial, linear, path, group, shape, nul, text, fade, comp } from './lib.mjs';

const GY = 700; // ground line shared by the witness scenes

// ---- shared pieces -------------------------------------------------------
function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

/** The travelling light: bright core + two soft halos. */
const lightShapes = () => [
  group([ellipse(0, 0, 16), fill(C.goldHi)]),
  group([ellipse(0, 0, 110), radial(C.goldHi, 55, 0.95, 0)]),
  group([ellipse(0, 0, 520), radial(C.gold, 260, 0.42, 0)]),
];
const light = (nm, t) => shape(nm, lightShapes(), t);

const halo = (nm, x, y, r, color = C.halo, o = 100, a0 = 1) =>
  shape(nm, [ellipse(0, 0, r * 2), radial(color, r, a0, 0)], { p: [x, y], o });

const ground = (y = GY) => [
  shape('ground', [rect(-200, y, W + 400, H - y + 200), fill(C.black)]),
  shape('ground-edge', [path([[-200, y], [W + 200, y]], { closed: false }), stroke(C.gold, 2, 14)]),
];

const curtain = (op, dIn = 8, dOut = 8, color = C.black) =>
  shape('curtain', [rect(0, 0, W, H), fill(color)], { o: A([[0, 100, E.out], [dIn, 0, E.lin], [op - dOut, 0, E.in], [op - 1, 100]]) });

/** Name tag + verse + reference, lower third. */
function caption({ name, verse, ref, tIn, tOut, x = W / 2, y = 915, size = 56, id = '', refColor = C.goldDim }) {
  return [
    name && text('name' + id, name, { y: y - 82, size: 28, color: C.gold, track: 160, o: fade(tIn, tOut) }),
    text('verse' + id, verse, { x, y, size, o: fade(tIn + 8, tOut), sid: 'verse' + id }),
    text('ref' + id, ref, { x, y: y + 62, size: 26, color: refColor, track: 80, o: fade(tIn + 18, tOut) }),
  ];
}

// ---- silhouettes (feet at 0,0; ~300 units tall; filled black) -------------
const BLK = () => fill(C.black);

const standing = () => [
  group([ellipse(0, -280, 44), BLK()]),
  group([path([[-12, -262], [-40, -244], [-48, -150], [-60, 0, 'c'], [60, 0, 'c'], [48, -150], [40, -244], [12, -262]], { smooth: true }), BLK()]),
];

/** Kneeling, face lifted to the upper right, arms open. */
const kneeling = () => [
  group([ellipse(24, -276, 44), BLK()]),
  group([path([[24, -216], [112, -250]], { closed: false }), stroke(C.black, 14)]),
  group([path([[14, -206], [104, -206]], { closed: false }), stroke(C.black, 14)]),
  group([path([[-118, 0, 'c'], [-112, -24], [-34, -42], [-30, -120], [-24, -226], [8, -248], [42, -228], [48, -120], [54, -32], [60, 0, 'c']], { smooth: true }), BLK()]),
];

/** Seated in profile facing right, leaning over the lap. */
const seated = () => [
  group([ellipse(26, -176, 42), BLK()]),
  group([path([[30, -160], [48, -142], [40, -128]], { smooth: true }), BLK()]), // beard
  group([path([[-44, 0, 'c'], [-50, -80], [-34, -138], [-4, -160], [28, -146], [44, -100], [92, -74], [100, 0, 'c'], [66, 0, 'c'], [60, -34], [-10, -30], [-8, 0, 'c']], { smooth: true }), BLK()]),
  group([path([[10, -128], [78, -92]], { closed: false }), stroke(C.black, 15)]), // forearm
];

/** Bent under the cross, climbing to the right. */
const bearer = () => [
  group([ellipse(34, -152, 36), BLK()]),
  group([path([[-34, 0, 'c'], [-40, -70], [-24, -128], [4, -150], [30, -134], [34, -70], [46, 0, 'c'], [14, 0, 'c'], [6, -40], [-6, 0, 'c']], { smooth: true }), BLK()]),
  group([path([[10, -128], [44, -112]], { closed: false }), stroke(C.black, 12)]),
  group([rect(-250, -9, 400, 18), rect(52, -74, 18, 148), BLK()], { p: [10, -146], r: -30 }), // the cross on the shoulder
];

const youth = v => [
  group([ellipse(0, -262, 42), BLK()]),
  group([path([[-10, -238], [-38, -226], [-44, -118, 'c'], [-30, 0, 'c'], [-5, 0, 'c'], [0, -112, 'c'], [5, 0, 'c'], [30, 0, 'c'], [44, -118, 'c'], [38, -226], [10, -238]], { smooth: true, tension: 0.7 }), BLK()]),
].filter(Boolean);

// ---- 1 · prologue (0–5 s) -------------------------------------------------
function scene1() {
  const op = 150;
  return comp('1 프롤로그', op, [
    halo('halo', 960, 430, 620, C.halo, A([[0, 0, E.out], [60, 70]])),
    light('spark', {
      p: A([[0, [960, 430]], [122, [960, 430], E.in], [150, [2150, 430]]]),
      s: A([[0, [0, 0], E.out], [34, [100, 100]], [78, [128, 128]], [122, [100, 100]]]),
    }),
    caption({ verse: '땅 끝까지 이르러 내 증인이 되리라', ref: '사도행전 1:8', tIn: 30, tOut: 140, y: 690, size: 62 }),
    curtain(op, 1, 6),
  ]);
}

// ---- 2 · Stephen (5–12 s) -------------------------------------------------
function scene2() {
  const op = 210, r = rng(7), fx = 960, sc = 112, chest = [972, GY - 178 * 1.12];
  const stones = Array.from({ length: 9 }, (_, i) => {
    const land = 48 + i * 13, x = [640, 1290, 740, 1200, 1110, 820, 1390, 540, 1280][i], size = 30 + r() * 22;
    const pts = Array.from({ length: 6 }, (_, k) => {
      const a = (k / 6) * Math.PI * 2, rad = size * (0.75 + r() * 0.4);
      return [Math.cos(a) * rad, Math.sin(a) * rad * 0.8];
    });
    const x0 = x + (x < fx ? -260 : 260);
    return shape('stone' + i, [path(pts), fill(C.black)], {
      p: A([[land - 20, [x0, -60], E.in], [land, [x, GY - size * 0.5], E.out], [land + 5, [x + (x < fx ? 12 : -12), GY - size * 0.9], E.in], [land + 10, [x + (x < fx ? 20 : -20), GY - size * 0.5]]]),
      r: A([[land - 20, 0, E.lin], [land + 10, x < fx ? 200 : -200]]),
    });
  });
  return comp('2 스데반', op, [
    halo('halo', fx, 470, 640),
    shape('heaven', [path([[880, -20], [1120, -20], [1330, GY], [700, GY]]), fill(C.gold, A([[0, 0, E.out], [70, 7]]))]),
    ground(),
    shape('stephen', kneeling(), { p: [fx, GY], s: [sc, sc] }),
    stones,
    light('spark', {
      p: A([[0, [-160, 520], E.out], [30, chest], [182, chest, E.in], [210, [2150, 380]]]),
      s: A([[30, [100, 100]], [100, [120, 120]], [170, [100, 100]]]),
    }),
    caption({ name: '스데반 · 첫 순교자', verse: '주여 이 죄를 그들에게 돌리지 마옵소서', ref: '사도행전 7:60', tIn: 38, tOut: 200 }),
    curtain(op),
  ]);
}

// ---- 3 · James (12–17 s) --------------------------------------------------
function scene3() {
  const op = 150, fx = 800, chest = [fx, GY - 175 * 1.3];
  const gone = A([[103, 100, [1, 0, 1, 0]], [104, 0]]);
  return comp('3 야고보', op, [
    halo('halo', 1150, 420, 700),
    shape('sword-shadow', [
      group([path([[0, 0], [16, -40], [10, -470], [0, -520], [-10, -470], [-16, -40]]), fill(C.black, 62)]),
      group([rect(-62, -44, 124, 16, 6), rect(-10, -28, 20, 78, 8), fill(C.black, 62)]),
    ], { p: [1330, 640], s: [118, 118], o: gone, r: A([[0, 72], [28, 72, E.soft], [92, -14, E.in], [103, 86]]) }),
    ground(),
    shape('james', standing(), { p: [fx, GY], s: [130, 130], o: gone }),
    light('spark', {
      p: A([[0, [-160, 470], E.out], [26, chest], [112, chest, E.in], [150, [2150, 330]]]),
      s: A([[26, [100, 100]], [104, [100, 100], E.out], [112, [150, 150]], [150, [100, 100]]]),
    }),
    shape('flash', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[101, 0, E.out], [105, 88, E.out], [132, 0]]) }),
    caption({ name: '야고보 · 사도 가운데 첫 순교', verse: '요한의 형제 야고보를 칼로 죽이니', ref: '사도행전 12:2', tIn: 14, tOut: 140 }),
    curtain(op),
  ]);
}

// ---- 4 · Paul (17–26 s) ---------------------------------------------------
function scene4() {
  const op = 270;
  const geo = (lon, lat) => [420 + (lon - 12.5) * 46, 180 + (42 - lat) * 38];
  const cities = [
    ['예루살렘', geo(35.2, 31.8), 20, [0, 44]], ['안디옥', geo(36.2, 36.2), 40, [0, -24]], ['에베소', geo(27.3, 37.9), 62, [0, 44]],
    ['빌립보', geo(24.3, 41.0), 78, [0, -24]], ['고린도', geo(22.9, 37.9), 94, [-10, 46]], ['로마', geo(12.5, 41.9), 110, [0, -26]],
  ];
  const mapOut = A([[140, 100, E.in], [160, 0]]);
  const mapO = (tIn, max = 100) => A([[tIn, 0, E.out], [tIn + 14, max, E.lin], [140, max, E.in], [160, 0]]);
  const cellIn = max => A([[148, 0, E.out], [172, max]]);
  const fx = 860, chest = [fx + 6, GY - 140 * 1.3];
  return comp('4 바울', op, [
    halo('map-glow', 960, 400, 900, '#3d3019', mapOut),
    shape('map-grid', [
      ...[250, 400, 550].map(y => group([path([[200, y], [1720, y]], { closed: false }), stroke(C.gold, 1.5, 9)])),
      ...[500, 800, 1100, 1400].map(x => group([path([[x, 110], [x, 660]], { closed: false }), stroke(C.gold, 1.5, 9)])),
    ], { o: mapO(0) }),
    text('sea', '지 중 해', { x: 900, y: 560, size: 34, color: C.goldDim, track: 400, o: mapO(10, 45) }),
    shape('route', [path(cities.map(c => c[1]), { closed: false, smooth: true, tension: 0.45 }), trim(0, A([[18, 0, E.inOut], [116, 100]])), stroke(C.gold, 5)], { o: mapOut }),
    cities.map(([nm, [x, y], t, [dx, dy]], i) => [
      shape('city' + i, [group([ellipse(0, 0, 12), fill(C.goldHi)]), group([ellipse(0, 0, 90), radial(C.gold, 45, 0.6, 0)])],
        { p: [x, y], o: mapO(t), s: A([[t, [0, 0], E.out], [t + 14, [100, 100]]]) }),
      text('city-label' + i, nm, { x: x + dx, y: y + dy, size: 26, color: C.white, o: mapO(t + 4, 85) }),
    ]),
    // prison
    halo('cell-glow', 1010, 440, 620, C.halo, cellIn(100)),
    shape('window', [
      ...[0, 1, 2].map(i => group([rect(1392 + i * 38, 190, 9, 150), fill(C.black)])),
      group([rect(1370, 190, 130, 150, 4), fill(C.gold, 22)]),
    ], { o: cellIn(100) }),
    shape('floor', [rect(-200, GY, W + 400, H), fill(C.black)], { o: cellIn(100) }),
    shape('table', [rect(940, GY - 168, 300, 14, 3), rect(960, GY - 156, 12, 156), rect(1208, GY - 156, 12, 156), fill(C.black)], { o: cellIn(100) }),
    shape('letter', [group([path([[1040, GY - 196], [1068, GY - 250]], { closed: false }), stroke(C.black, 4)]),
      group([path([[1010, GY - 172], [1150, GY - 172], [1162, GY - 180], [1022, GY - 180]]), fill(C.parchment, 90)])], { o: cellIn(100) }),
    shape('paul', seated(), { p: [fx, GY], s: [130, 130], o: cellIn(100) }),
    shape('stool', [rect(fx - 62, GY - 46, 100, 46, 4), fill(C.black)], { o: cellIn(100) }),
    shape('chain', [path([[962, GY - 118], [990, GY - 40], [1080, GY - 8], [1180, GY - 6]], { closed: false, smooth: true }),
      { ...stroke(C.black, 9), d: [{ n: 'd', nm: 'dash', v: { a: 0, k: 15 } }, { n: 'g', nm: 'gap', v: { a: 0, k: 9 } }] }], { o: cellIn(100) }),
    light('spark', { p: A([[150, chest], [240, chest, E.in], [270, [2150, 360]]]), o: cellIn(100), s: A([[150, [100, 100]], [200, [118, 118]], [240, [100, 100]]]) }),
    caption({ name: '바울 · 이방인의 사도', verse: '나의 생명조차 조금도 귀한 것으로 여기지 아니하노라', ref: '사도행전 20:24', tIn: 30, tOut: 258, size: 52 }),
    curtain(op),
  ]);
}

// ---- 5 · Peter (26–32 s) --------------------------------------------------
function scene5() {
  const op = 180, cx = 1000, top = 610;
  const arches = Array.from({ length: 5 }, (_, i) => group([rect(150 + i * 96, 520, 26, 150), fill(C.black)]));
  return comp('5 베드로', op, [
    nul('cam', { p: A([[0, [0, -130], E.soft], [165, [0, 0]]]) }),
    { ...halo('halo', cx, 330, 720), parent: 'cam' },
    { ...shape('rome', [
      ...arches, group([rect(130, 500, 450, 24), fill(C.black)]),
      ...[0, 1, 2, 3].map(i => group([rect(1452 + i * 62, 500, 22, 170), fill(C.black)])),
      group([path([[1420, 500], [1565, 440], [1710, 500]]), fill(C.black)]),
    ], { o: 80 }), parent: 'cam' },
    { ...shape('hill', [path([[-200, 760, 'c'], [300, 700], [700, 640], [cx, top], [1300, 640], [1700, 700], [2120, 760, 'c'], [2120, 1500, 'c'], [-200, 1500, 'c']], { smooth: true }), fill(C.black)]), parent: 'cam' },
    { ...shape('cross', [rect(cx - 12, top - 330, 24, 345), rect(cx - 95, top - 120, 190, 24), fill(C.black)]), parent: 'cam' },
    { ...light('spark', {
      p: A([[0, [-160, 600], E.out], [30, [cx, top - 215]], [152, [cx, top - 215], E.in], [180, [2150, 300]]]),
      s: A([[30, [100, 100]], [90, [122, 122]], [150, [100, 100]]]),
    }), parent: 'cam' },
    caption({ name: '베드로 · 거꾸로 선 십자가 (전승)', verse: '그리스도의 고난에 참여하는 것으로 즐거워하라', ref: '베드로전서 4:13', tIn: 24, tOut: 170 }),
    curtain(op),
  ]);
}

// ---- 6 · John (32–38 s) ---------------------------------------------------
function scene6() {
  const op = 180, r = rng(21), fx = 930, fy = 548, chest = [fx + 4, fy - 130 * 1.1];
  const stars = Array.from({ length: 34 }, () => group([ellipse(r() * W, r() * 470, 2 + r() * 3), fill(C.white, 30 + r() * 55)]));
  const wave = (nm, y, amp, color, shift, o = 100) => {
    const pts = Array.from({ length: 27 }, (_, i) => [-360 + i * 104, y + (i % 2 ? amp : -amp)]);
    return shape(nm, [path([...pts, [2400, 1400, 'c'], [-360, 1400, 'c']], { smooth: true }), fill(color, o)],
      { p: A([[0, [0, 0]], [90, [shift, 6]], [180, [0, 0]]]) });
  };
  return comp('6 요한', op, [
    shape('stars', stars, { o: A([[0, 70], [60, 100], [120, 70], [180, 100]]) }),
    halo('halo', 960, 420, 640, '#2a3856'),
    wave('wave-far', 640, 7, '#0f1a2e', 70),
    shape('island', [path([[560, 760, 'c'], [640, 660], [730, 600], [800, 560, 'c'], [1010, 546, 'c'], [1090, 590], [1200, 610], [1300, 690], [1380, 760, 'c']], { smooth: true }), fill(C.black)]),
    shape('john', seated(), { p: [fx, fy], s: [110, 110] }),
    shape('scroll', [
      ...[0, 1, 2, 3].map(i => group([path([[1010 + i * 3, 446 + i * 11], [1086 + i * 3, 440 + i * 11]], { closed: false }),
        trim(0, A([[46 + i * 22, 0, E.inOut], [66 + i * 22, 100]])), stroke(C.gold, 3.5)])),
      group([path([[996, 438], [1102, 428], [1114, 484], [1008, 494]]), fill(C.parchment)]),
    ]),
    wave('wave-mid', 700, 9, '#0a1220', -90),
    wave('wave-near', 752, 11, '#05080f', 110),
    light('spark', {
      p: A([[0, [-160, 470], E.out], [28, chest], [152, chest, E.in], [180, [2150, 250]]]),
      s: A([[28, [85, 85]], [90, [105, 105]], [150, [85, 85]]]),
    }),
    caption({ name: '요한 · 밧모섬 유배', verse: '예수를 증언하였음으로 말미암아 밧모라 하는 섬에 있었더니', ref: '요한계시록 1:9', tIn: 22, tOut: 170, size: 50 }),
    curtain(op),
  ]);
}

// ---- 7 · Calvary (38–50 s) ------------------------------------------------
function scene7() {
  const op = 360, top = [1560, 400];
  const hillPts = [[-200, 960], [200, 930], [520, 880], [800, 790], [1050, 660], [1280, 520], [1440, 432], [1560, 400], [1700, 430], [1900, 520], [2150, 640]];
  const walkPts = [[520, 880], [800, 790], [1050, 660], [1280, 520], [1440, 432], [1512, 410]];
  const seg = walkPts.slice(1).map((p, i) => Math.hypot(p[0] - walkPts[i][0], p[1] - walkPts[i][1]));
  const total = seg.reduce((a, b) => a + b, 0);
  let acc = 0;
  const walk = walkPts.map((p, i) => { if (i) acc += seg[i - 1]; return [Math.round(100 + (acc / total) * 160), p, E.lin]; });
  const sway = Array.from({ length: 15 }, (_, i) => [100 + i * 12, i % 2 ? 2.2 : -1.6, E.inOut]);
  const cam = l => ({ ...l, parent: 'cam' });
  const from = [[-100, 200], [300, -100], [1000, -120], [2000, 100], [2050, 800]];
  return comp('7 갈보리', op, [
    nul('cam', { p: top, a: top, s: A([[90, [100, 100], E.soft], [340, [111, 111]]]) }),
    cam(shape('sky', [rect(-300, -300, W + 600, 1300), linear(-100, 760, [[0, C.ink], [0.5, '#2a0b10'], [1, '#9c2020']])], { o: A([[88, 0, E.soft], [250, 100]]) })),
    cam(shape('rays', Array.from({ length: 14 }, (_, i) => group([path([[0, 0], [-46, -1900], [46, -1900]]), fill(C.goldHi, 30)], { r: i * (360 / 14) })),
      { p: top, o: A([[272, 0, E.out], [312, 100]]), r: A([[270, 0, E.lin], [360, 14]]), s: A([[270, [20, 20], E.out], [330, [100, 100]]]) })),
    cam(shape('burst', [ellipse(0, 0, 3000), radial(C.goldHi, 1500, 1, 0)], { p: top, o: A([[268, 0, E.out], [300, 100]]), s: A([[268, [4, 4], E.out], [336, [100, 100]]]) })),
    cam(halo('gather', top[0], top[1], 420, C.gold, A([[84, 0, E.out], [120, 55], [262, 55], [280, 0]]), 0.8)),
    from.map((p, i) => cam(light('spark' + i, { p: A([[52 + i * 4, p, E.inOut], [100, top]]), o: A([[52 + i * 4, 0, E.out], [62 + i * 4, 100], [96, 100, E.in], [112, 0]]), s: [70, 70] }))),
    cam(shape('hill', [path([...hillPts, [2150, 1500, 'c'], [-200, 1500, 'c']].map((p, i) => (i === 0 || i === hillPts.length - 1 ? [...p, 'c'] : p)), { smooth: true }), fill(C.black)], { o: A([[84, 0], [100, 100]]) })),
    cam(shape('bearer', bearer(), { p: A(walk), r: A(sway), s: [92, 92], o: A([[96, 0, E.out], [116, 100], [256, 100, E.in], [272, 0]]) })),
    cam(shape('cross', [rect(-11, -250, 22, 262), rect(-72, -196, 144, 22), fill(C.black)], { p: [top[0], top[1] + 6], o: A([[262, 0, E.out], [284, 100]]) })),
    text('question', '그들은 왜 이 길을 갔는가', { y: 560, size: 66, o: fade(10, 90, 100, 26, 20), sid: 'question' }),
    caption({ id: '1', verse: '예수께서 자기의 십자가를 지시고', ref: '요한복음 19:17', tIn: 116, tOut: 244, y: 232, size: 58 }),
    caption({ id: '2', verse: '제 십자가를 지고 나를 따를 것이니라', ref: '누가복음 9:23', tIn: 250, tOut: 350, x: 1250, y: 905, size: 54, refColor: C.gold }),
    shape('white-out', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[330, 0, E.in], [358, 100]]) }),
  ]);
}

// ---- 8 · handing on / 9 · title (50–60 s) ---------------------------------
const HORIZON = 760, FEET = 1180, YS = 1.7;
const youths = [[435, 0.96, 0], [610, 1.04, 1], [785, 0.98, 2], [960, 1.07, 0], [1135, 1.0, 1], [1310, 1.05, 2], [1485, 0.97, 1]];
const chestOf = ([x, k]) => [x, FEET - 190 * YS * k];

function campus(sunScale) {
  const k = 0.6, haze = '#2b2444';
  const b = (x, w, h) => rect(x, HORIZON - h * k, w, h * k + 40);
  const win = (x, w, h, cols, rows) => Array.from({ length: cols * rows }, (_, i) =>
    rect(x + 22 + (i % cols) * ((w - 44) / Math.max(cols - 1, 1)) - 6, HORIZON - h * k + 20 + Math.floor(i / cols) * 30, 12, 16));
  return [
    shape('sky', [rect(0, 0, W, H), linear(0, HORIZON, [[0, '#090e20'], [0.5, '#232647'], [0.82, '#a05c42'], [1, '#f6c070']])]),
    shape('sun', [ellipse(0, 0, 1300), radial(C.goldHi, 650, 0.9, 0)], { p: [960, HORIZON], s: sunScale }),
    shape('skyline', [
      b(60, 230, 170), b(300, 150, 225), b(470, 260, 135), b(1230, 190, 250), b(1440, 230, 150), b(1690, 210, 210),
      b(900, 300, 150), path([[880, HORIZON - 150 * k], [1050, HORIZON - 215 * k], [1220, HORIZON - 150 * k]]),      // main hall + pediment
      b(770, 74, 300), path([[762, HORIZON - 300 * k], [807, HORIZON - 372 * k], [852, HORIZON - 300 * k]]),         // clock tower
      ...[[250, 40], [690, 36], [1380, 38], [1650, 34], [20, 32]].flatMap(([x, r]) => [ellipse(x, HORIZON - r - 10, r * 2), rect(x - 3, HORIZON - 20, 6, 24)]),
      fill(haze),
    ]),
    shape('windows', [...win(60, 230, 170, 5, 2), ...win(1230, 190, 250, 4, 4), ...win(1690, 210, 210, 4, 3), ...win(900, 300, 150, 6, 2), fill(C.goldHi, 45)]),
    shape('clock', [ellipse(807, HORIZON - 262 * k, 24), fill(C.goldHi, 80)]),
    shape('plaza', [rect(-100, HORIZON, W + 200, 400), linear(HORIZON, H, [[0, '#4a3140'], [0.35, '#1c1526'], [1, '#07060c']])]),
    shape('youths', youths.map(([x, s, v]) => group(youth(v), { p: [x, FEET], s: [YS * s * 100, YS * s * 100] }))),
  ];
}

function scene8() {
  const op = 180;
  const names = ['스데반', '야고보', '바울', '베드로', '요한'];
  const nodes = [[250, 520], [500, 480], [750, 460], [1000, 458], [1250, 478]];
  const relay = [[-80, 600], ...nodes, [1500, 560], [1700, 720]];
  return comp('8 전달', op, [
    campus([100, 100]),
    shape('relay', [path(relay, { closed: false, smooth: true }), trim(0, A([[16, 0, E.inOut], [96, 100]])), stroke(C.goldHi, 3.5, 90)], { o: fade(14, 172, 100, 8, 20) }),
    nodes.map((p, i) => {
      const t = 26 + i * 12;
      return [
        shape('node' + i, [group([ellipse(0, 0, 12), fill(C.goldHi)]), group([ellipse(0, 0, 80), radial(C.goldHi, 40, 0.7, 0)])],
          { p, s: A([[t, [0, 0], E.out], [t + 12, [100, 100]]]), o: fade(t, 172, 100, 8, 20) }),
        text('node-label' + i, names[i], { x: p[0], y: p[1] - 24, size: 24, color: C.white, o: fade(t + 3, 172, 90, 12, 20) }),
      ];
    }),
    youths.map((y, i) => {
      const t = 98 + (youths.length - 1 - i) * 7;
      return light('lit' + i, { p: chestOf(y), s: A([[t, [0, 0], E.out], [t + 10, [100, 100], E.soft], [t + 26, [72, 72]]]) });
    }),
    text('pledge', '이제, 우리가 전합니다', { y: 200, size: 84, font: 'B', o: fade(36, 172, 100, 26, 20), sid: 'pledge' }),
    caption({ verse: '내가 여기 있나이다 나를 보내소서', ref: '이사야 6:8', tIn: 62, tOut: 172, y: 296, size: 46, refColor: C.goldHi }),
    shape('white-in', [rect(0, 0, W, H), fill(C.goldHi)], { o: A([[0, 100, E.out], [36, 0]]) }),
  ]);
}

function scene9() {
  const op = 120;
  // per-character reveal: opacity animator driven by a range selector sweeping left to right
  const reveal = [{ nm: 'reveal', a: { o: { a: 0, k: 0 } },
    s: { t: 0, b: 1, sh: 1, r: 1, rn: 0, xe: { a: 0, k: 0 }, ne: { a: 0, k: 0 }, a: { a: 0, k: 100 }, o: { a: 0, k: 0 }, e: { a: 0, k: 100 },
      s: A([[8, 0, E.soft], [62, 100]]) } }];
  return comp('9 타이틀', op, [
    campus(A([[0, [100, 100], E.soft], [120, [128, 128]]])),
    youths.map((y, i) => light('lit' + i, { p: chestOf(y), s: [72, 72] })),
    text('title', '십자가의 전달자', { y: 320, size: 164, font: 'B', color: C.goldHi, track: 40, animators: reveal }),
    text('group', '청년회', { y: 420, size: 40, color: C.white, track: 500, o: A([[58, 0, E.out], [84, 100]]), sid: 'groupName' }),
  ]);
}

export const scenes = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9];
