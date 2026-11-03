#!/usr/bin/env node
/* 정렬·글자 크기 측정 (02-art-direction.md §1·§8): 지정한 시각마다 보이는 텍스트를 모두 모아
 *   - 가운데 정렬 요소(data-m="c"): 박스 중심 x 와 540 의 차 (|Δx| ≤ 2px 이 기준)
 *   - 말풍선 컬럼(data-m="col"): 좌우 여백 (대칭이면 중심 = 540)
 *   - 계산된 font-size 집합 (4종 이하가 기준)
 *   - 블록 사이 최대 틈: 보이는 블록(data-m 글자·말풍선·버튼, data-fill 입력 독·풋터 필드)을 위에서 아래로 놓고 이웃한 두 블록 사이의
 *     세로 틈의 최댓값 (§7-2 기준 ≤ 140px). 독·풋터는 위 가장자리까지의 틈을 재므로 보수적이다
 *   - 빈 띠: 글자·오브제 픽셀이 하나도 없는 가장 긴 연속 행 묶음 (프레임 높이 1920 의 %, §7-2 기준 ≤ 15%).
 *     바탕색과 다른 전체 폭 필드(입력 독·풋터)는 채움으로 센다
 * 을 표로 낸다. 어느 쪽에도 속하지 않는 보이는 텍스트는 "unannotated" 로 따로 보고한다.
 *
 * 시간 이동: 렌더러처럼 0 초부터 프레임을 하나씩 앞으로 걸어서 간다(기본, 시각은 오름차순으로 정렬).
 *   임의의 시각으로 바로 건너뛰면(`--random`, hyperframes snapshot 도 이 방식) 같은 요소에 글라이드 뒤 set 을 건 경우처럼
 *   anime.js 가 계산하는 값이 달라질 수 있다 — 15초 엔드카드에서 DOM 측정(건너뛰기)은 정상인데 렌더(차례로)는 유도 줄이
 *   버튼 아래에 있던 사고의 원인이다. `--compare` 는 두 방식을 모두 돌려 위치가 다른 요소를 보고한다.
 *
 * Usage:
 *   npx hyperframes@0.8.200 preview --background --port 4611        (프로젝트 폴더에서; v15 는 v15/ 에서)
 *   node tools/measure_frames.cjs http://localhost:4611/api/projects/ask-ai/preview 3,6.8,9.5 [--json out.json] [--compare|--random]
 * 미리보기 서버가 data-hf-id 를 소스에 박으므로, 측정이 끝나면 `preview --stop` 한다.
 */
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch (e) {
  ({ chromium } = require("/opt/node-tools/node_modules/playwright"));
}
const fs = require("fs");

const url = process.argv[2];
const times = (process.argv[3] || "").split(",").filter(Boolean).map(Number);
const jsonOut = process.argv.includes("--json") ? process.argv[process.argv.indexOf("--json") + 1] : null;
if (!url || !times.length) {
  console.error("usage: node tools/measure_frames.cjs <preview-url> <t1,t2,...> [--json out.json]");
  process.exit(2);
}

function collect() {
  const W = 1080, H = 1920, AXIS = 540;
  const vis = (el) => {
    let op = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === "none" || cs.visibility === "hidden") return null;
      op *= parseFloat(cs.opacity);
    }
    if (op < 0.05) return null;
    let r = el.getBoundingClientRect();
    // v7: 사진 속 폰 화면(배율 ≈ 0.27)에 합성된 축소 UI 는 측정하지 않는다 (축소 배율 < 0.5)
    if (el.offsetWidth > 0 && r.width / el.offsetWidth < 0.5) return null;
    let box = { l: r.left, t: r.top, r: r.right, b: r.bottom };
    const inset = (n) => {
      // clip-path: inset(t r b l ...) — 오프닝 윈도우, 말풍선 줄 단위 공개, 입력창이 위로 자라는 모양
      const m = /inset\(([-\d.]+)px(?: ([-\d.]+)px)?(?: ([-\d.]+)px)?(?: ([-\d.]+)px)?/.exec(getComputedStyle(n).clipPath || "");
      if (!m) return;
      const it = +m[1], ir = m[2] != null ? +m[2] : it, ib = m[3] != null ? +m[3] : it, il = m[4] != null ? +m[4] : ir;
      const pr = n.getBoundingClientRect();
      const sx = pr.width / (n.offsetWidth || pr.width), sy = pr.height / (n.offsetHeight || pr.height);
      box = { l: Math.max(box.l, pr.left + il * sx), t: Math.max(box.t, pr.top + it * sy), r: Math.min(box.r, pr.right - ir * sx), b: Math.min(box.b, pr.bottom - ib * sy) };
    };
    inset(el); // 자기 자신의 clip-path
    const own = { ...box }; // 자기 clip-path 만 적용한 보이는 영역 (말풍선이 줄 단위로 자라는 중이면 이만큼이 '전부'다)
    // 조상의 overflow 마스크(줄 마스크 등)·clip-path 로 잘리면 그만큼만 보인다
    for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.overflow !== "visible" || cs.overflowX !== "visible" || cs.overflowY !== "visible") {
        const pr = n.getBoundingClientRect();
        box = { l: Math.max(box.l, pr.left), t: Math.max(box.t, pr.top), r: Math.min(box.r, pr.right), b: Math.min(box.b, pr.bottom) };
      }
      inset(n);
    }
    box = { l: Math.max(box.l, 0), t: Math.max(box.t, 0), r: Math.min(box.r, W), b: Math.min(box.b, H) };
    const area = Math.max(0, box.r - box.l) * Math.max(0, box.b - box.t);
    const full = Math.max(1, (own.r - own.l) * (own.b - own.t));
    if (area / full < 0.5) return null; // 조상 마스크 안에서 올라오는 중이거나 화면 밖
    return { op, rect: r, box };
  };
  const onTop = () => true; // 가림은 vis() 의 overflow·clip-path 교차로 판단한다
  const directText = (el) => Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
  const label = (el) => (el.id ? "#" + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : ""));
  // 보이는 글자만 (불투명도 0 인 교체 문구, 롤 띠의 가려진 숫자는 뺀다)
  const txt = (el) => {
    const parts = [];
    const walk = (n) => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3) {
          if (c.textContent.trim() && vis(c.parentElement)) parts.push(c.textContent);
        } else if (c.nodeType === 1) walk(c);
      }
    };
    walk(el);
    return parts.join("").replace(/\s+/g, " ").trim().slice(0, 40);
  };

  const centred = [], cols = [], sizes = {}, stray = [];
  document.querySelectorAll('[data-m="c"]').forEach((el) => {
    const v = vis(el);
    if (!v || !onTop(el, v.rect)) return;
    const cx = (v.rect.left + v.rect.right) / 2;
    centred.push({ el: label(el), text: txt(el), fs: getComputedStyle(el).fontSize, cx: +cx.toFixed(2), dx: +(cx - AXIS).toFixed(2), y: Math.round(v.rect.top) });
  });
  document.querySelectorAll('[data-m="col"]').forEach((el) => {
    const v = vis(el);
    if (!v || !onTop(el, v.rect)) return;
    const L = v.rect.left, R = W - v.rect.right;
    cols.push({ el: label(el), text: txt(el), w: +(v.rect.right - v.rect.left).toFixed(1), L: +L.toFixed(2), R: +R.toFixed(2), cx: +((v.rect.left + v.rect.right) / 2).toFixed(2), dx: +((v.rect.left + v.rect.right) / 2 - AXIS).toFixed(2), y: Math.round(v.rect.top) });
  });
  document.querySelectorAll("body *").forEach((el) => {
    if (!directText(el) || ["SCRIPT", "STYLE", "TEMPLATE"].includes(el.tagName)) return;
    const v = vis(el);
    if (!v || !onTop(el, v.rect)) return;
    const fs = getComputedStyle(el).fontSize;
    (sizes[fs] = sizes[fs] || []).push(txt(el));
    if (!el.closest("[data-m]") && !el.querySelector("[data-m]")) stray.push({ el: label(el), text: txt(el), fs });
  });
  // 블록 사이 틈: 보이는 블록의 세로 구간을 합쳐 위에서 아래로 훑는다
  const blocks = [];
  document.querySelectorAll("[data-m], [data-fill]").forEach((el) => {
    const v = vis(el);
    if (!v || v.box.b - v.box.t < 2) return;
    blocks.push({ name: label(el), t: v.box.t, b: v.box.b });
  });
  blocks.sort((a, b) => a.t - b.t);
  const merged = [];
  for (const k of blocks) {
    const last = merged[merged.length - 1];
    if (last && k.t <= last.b + 0.5) { last.b = Math.max(last.b, k.b); last.last = k.name; }
    else merged.push({ first: k.name, last: k.name, t: k.t, b: k.b });
  }
  const gaps = [];
  for (let i = 1; i < merged.length; i++) gaps.push({ gap: +(merged[i].t - merged[i - 1].b).toFixed(1), from: merged[i - 1].last, to: merged[i].first, y: Math.round(merged[i - 1].b) });
  const maxGap = gaps.reduce((m, g) => (g.gap > m.gap ? g : m), { gap: 0, from: "-", to: "-", y: 0 });
  // 로고 락업: 브랜드 프레임마다 심볼 + 기관명이 한 줄로 보이고 락업 전체 중심이 x=540 인지
  let logo = null;
  const lr = document.querySelector("#w-logo-row") || document.querySelector("#br-logo-row"), lm = document.querySelector("#w-mark") || document.querySelector("#br-mark");
  if (lr && lm && vis(lr)) {
    const a = lr.getBoundingClientRect(), m = lm.getBoundingClientRect();
    const name = lr.lastElementChild.getBoundingClientRect();
    logo = { cx: +((a.left + a.right) / 2).toFixed(2), mark: Math.round(m.width) + "×" + Math.round(m.height), gapMarkName: +(name.left - m.right).toFixed(1), sameRow: Math.abs((m.top + m.bottom) / 2 - (name.top + name.bottom) / 2) < 3 };
  }
  // v7: 골드 면적 (디자인 요소만, 사진 제외): 골드 글자 박스 + 골드 선(SVG 경로 bbox, 최소 두께 = 선 굵기) + 골드 면(락업 심볼)
  let goldA = 0;
  const GOLD = "rgb(184, 149, 90)";
  document.querySelectorAll("body *").forEach((el) => {
    const cs = getComputedStyle(el);
    let hit = false;
    if (cs.color === GOLD && directText(el)) hit = true;
    if (cs.backgroundColor === GOLD) hit = true;
    if (el.tagName === "path" && (cs.stroke === GOLD || el.getAttribute("stroke") === "#b8955a")) hit = true;
    if (!hit) return;
    const v = vis(el.tagName === "path" ? el.closest("svg") : el);
    if (!v) return;
    const r = el.getBoundingClientRect();
    const sw = el.tagName === "path" ? parseFloat(cs.strokeWidth) || 3 : 0;
    goldA += Math.max(r.width, sw) * Math.max(r.height, sw);
  });
  const goldPct = +((100 * goldA) / (W * H)).toFixed(2);
  // 모든 id 요소의 보이는 위치 (걷기·건너뛰기 비교용)
  const pos = {};
  document.querySelectorAll("[id]").forEach((el) => {
    if (!el.closest("#root") && !el.id.startsWith("b-") && !el.id.startsWith("ch-")) return;
    const v = vis(el);
    if (v) pos[el.id] = [Math.round(v.box.t), Math.round(v.box.l)];
  });
  return { centred, cols, sizes, stray, gaps, maxGap, logo, pos, goldPct };
}

// 스크린샷(PNG base64)을 빈 페이지 canvas 로 풀어, 바탕색(최빈색)과 다른 픽셀이 없는 행의 최장 연속 구간을 잰다
function emptyBand(b64) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas");
      c.width = img.width;
      c.height = img.height;
      const g = c.getContext("2d");
      g.drawImage(img, 0, 0);
      const { data, width: w, height: h } = g.getImageData(0, 0, img.width, img.height);
      const count = new Map();
      for (let y = 0; y < h; y += 8) for (let x = 0; x < w; x += 8) {
        const i = (y * w + x) * 4, k = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2];
        count.set(k, (count.get(k) || 0) + 1);
      }
      const bg = [...count.entries()].sort((a, b) => b[1] - a[1])[0][0];
      const br = bg >> 16, bgc = (bg >> 8) & 255, bb = bg & 255;
      let run = 0, best = 0, bestEnd = 0;
      for (let y = 0; y < h; y++) {
        let empty = true;
        for (let x = 0; x < w; x += 2) {
          const i = (y * w + x) * 4;
          if (Math.abs(data[i] - br) + Math.abs(data[i + 1] - bgc) + Math.abs(data[i + 2] - bb) > 30) { empty = false; break; }
        }
        run = empty ? run + 1 : 0;
        if (run > best) { best = run; bestEnd = y; }
      }
      // v7: 어두운 픽셀 비율(루마 < 25% = 64/255)과 골드 면적(#B8955A 근처, 맨해튼 거리 < 60)
      let dark = 0, gold = 0, n = 0;
      for (let y = 0; y < h; y += 2) for (let x = 0; x < w; x += 2) {
        const i = (y * w + x) * 4, r = data[i], g = data[i + 1], b = data[i + 2];
        n++;
        if (0.2126 * r + 0.7152 * g + 0.0722 * b < 64) dark++;
        if (Math.abs(r - 184) + Math.abs(g - 149) + Math.abs(b - 90) < 60) gold++;
      }
      resolve({ px: best, from: bestEnd - best + 1, to: bestEnd + 1, pct: +((100 * best) / h).toFixed(1), dark: +((100 * dark) / n).toFixed(1), gold: +((100 * gold) / n).toFixed(2) });
    };
    img.src = "data:image/png;base64," + b64;
  });
}

const random = process.argv.includes("--random");
const compare = process.argv.includes("--compare");

async function run(browser, decoder, walk) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.__playerReady === true && window.__player && typeof window.__player.renderSeek === "function", null, { timeout: 60000, polling: 100 }); // 런타임이 rAF 를 쥐고 있어 interval 폴링
  await page.evaluate(() => window.__player.enableRenderMode && window.__player.enableRenderMode());
  await page.evaluate(() => document.fonts.ready);
  const seek = (t) => page.evaluate(async (t) => { const r = window.__player.renderSeek(t); if (r && r.then) await r; }, t);
  const out = [];
  let cur = 0;
  if (walk) await seek(0);
  for (const t of [...times].sort((a, b) => a - b)) {
    const target = Math.round(t * 30);
    if (walk) { while (cur < target) { cur++; await seek(cur / 30); } } // 렌더러처럼 프레임을 차례로
    else await seek(t);
    await page.waitForTimeout(100);
    const m = await page.evaluate(collect);
    if (decoder) {
      const shot = (await page.screenshot()).toString("base64");
      m.band = await decoder.evaluate(emptyBand, shot);
    }
    out.push({ t, ...m });
  }
  await page.close();
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const decoder = await browser.newPage();
  const out = await run(browser, decoder, !random);
  if (compare) {
    const other = await run(browser, null, false);
    const diffs = [];
    out.forEach((f, i) => {
      for (const id of new Set([...Object.keys(f.pos), ...Object.keys(other[i].pos)])) {
        const a = f.pos[id], b = other[i].pos[id];
        if (!a || !b || Math.abs(a[0] - b[0]) > 2 || Math.abs(a[1] - b[1]) > 2) diffs.push(`${f.t}s #${id}: walk ${a ? a.join(",") : "hidden"} vs jump ${b ? b.join(",") : "hidden"}`);
      }
    });
    console.log(diffs.length ? "WALK vs JUMP DIFFERENCES (" + diffs.length + "):\n  " + diffs.slice(0, 40).join("\n  ") : "walk vs jump: identical positions for every id'd element at every time");
  }
  const allSizes = new Set();
  out.forEach((f) => Object.keys(f.sizes).forEach((s) => allSizes.add(s)));
  await browser.close();

  let worst = 0;
  const lines = [];
  lines.push("| t (s) | element | text | font-size | centre x | Δx from 540 |");
  lines.push("|---|---|---|---|---|---|");
  for (const f of out) for (const c of f.centred) {
    worst = Math.max(worst, Math.abs(c.dx));
    lines.push(`| ${f.t} | ${c.el} | ${c.text} | ${c.fs} | ${c.cx} | ${c.dx >= 0 ? "+" : ""}${c.dx} |`);
  }
  lines.push("");
  lines.push("| t (s) | bubble | text | width | left margin | right margin | centre Δx |");
  lines.push("|---|---|---|---|---|---|---|");
  let worstCol = 0;
  for (const f of out) for (const c of f.cols) {
    worstCol = Math.max(worstCol, Math.abs(c.dx));
    lines.push(`| ${f.t} | ${c.el} | ${c.text} | ${c.w} | ${c.L} | ${c.R} | ${c.dx >= 0 ? "+" : ""}${c.dx} |`);
  }
  lines.push("");
  lines.push("| t (s) | max gap between adjacent blocks (px) | between (y) | ≤ 140 | largest empty band (rows y) | px | % of 1920 | ≤ 15% | dark px % (≤40 before end card) | gold design area % (≤5) |");
  lines.push("|---|---|---|---|---|---|---|---|---|---|");
  let worstGap = 0, worstBand = 0;
  for (const f of out) {
    worstGap = Math.max(worstGap, f.maxGap.gap);
    worstBand = Math.max(worstBand, f.band.pct);
    lines.push(`| ${f.t} | ${f.maxGap.gap} | ${f.maxGap.from} → ${f.maxGap.to} (${f.maxGap.y}) | ${f.maxGap.gap <= 140 ? "✓" : "✗"} | ${f.band.from}–${f.band.to} | ${f.band.px} | ${f.band.pct} | ${f.band.pct <= 15 ? "✓" : "✗"} | ${f.band.dark} | ${f.goldPct} |`);
  }
  const brandFrames = out.filter((f) => f.logo);
  lines.push("");
  lines.push("| t (s) | logo lockup centre x | mark (px) | mark → name gap | one row |");
  lines.push("|---|---|---|---|---|");
  for (const f of brandFrames) lines.push(`| ${f.t} | ${f.logo.cx} | ${f.logo.mark} | ${f.logo.gapMarkName} | ${f.logo.sameRow ? "✓" : "✗"} |`);
  const strays = out.flatMap((f) => f.stray.map((s) => `${f.t}s ${s.el} "${s.text}" ${s.fs}`));
  const sizeList = [...allSizes].sort((a, b) => parseFloat(a) - parseFloat(b));
  lines.push("");
  lines.push(`font sizes seen (computed): ${sizeList.join(", ")} — ${sizeList.length} sizes`);
  lines.push(`max |Δx| centred text: ${worst.toFixed(2)} px; max |Δx| bubble column centre: ${worstCol.toFixed(2)} px`);
  lines.push(`max block gap over all frames: ${worstGap} px; largest empty band over all frames: ${worstBand}%`);
  lines.push(`unannotated visible text: ${strays.length ? strays.join("; ") : "none"}`);
  console.log(lines.join("\n"));
  if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(out, null, 1));
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
