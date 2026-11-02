#!/usr/bin/env node
/* 정렬·글자 크기 측정 (02-art-direction.md §1·§8): 지정한 시각마다 보이는 텍스트를 모두 모아
 *   - 가운데 정렬 요소(data-m="c"): 박스 중심 x 와 540 의 차 (|Δx| ≤ 2px 이 기준)
 *   - 말풍선 컬럼(data-m="col"): 좌우 여백 (대칭이면 중심 = 540)
 *   - 계산된 font-size 집합 (4종 이하가 기준)
 *   - 빈 띠: 글자·오브제 픽셀이 하나도 없는 가장 긴 연속 행 묶음 (프레임 높이 1920 의 %, §7-1 기준 ≤ 35%)
 * 을 표로 낸다. 어느 쪽에도 속하지 않는 보이는 텍스트는 "unannotated" 로 따로 보고한다.
 *
 * Usage:
 *   npx hyperframes@0.8.200 preview --background --port 4611        (프로젝트 폴더에서; v15 는 v15/ 에서)
 *   node tools/measure_frames.cjs http://localhost:4611/api/projects/ask-ai/preview 3,6.8,9.5 [--json out.json]
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
    let box = { l: r.left, t: r.top, r: r.right, b: r.bottom };
    // 조상의 overflow 마스크(줄 마스크 등)로 잘리면 그만큼만 보인다
    for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.overflow !== "visible" || cs.overflowX !== "visible" || cs.overflowY !== "visible") {
        const pr = n.getBoundingClientRect();
        box = { l: Math.max(box.l, pr.left), t: Math.max(box.t, pr.top), r: Math.min(box.r, pr.right), b: Math.min(box.b, pr.bottom) };
      }
      // clip-path: inset(t r b l ...) — 오프닝 윈도우, 말풍선 줄 단위 공개
      const m = /inset\(([-\d.]+)px(?: ([-\d.]+)px)?(?: ([-\d.]+)px)?(?: ([-\d.]+)px)?/.exec(cs.clipPath || "");
      if (m) {
        const it = +m[1], ir = m[2] != null ? +m[2] : it, ib = m[3] != null ? +m[3] : it, il = m[4] != null ? +m[4] : ir;
        const pr = n.getBoundingClientRect();
        const sx = pr.width / (n.offsetWidth || pr.width), sy = pr.height / (n.offsetHeight || pr.height);
        box = { l: Math.max(box.l, pr.left + il * sx), t: Math.max(box.t, pr.top + it * sy), r: Math.min(box.r, pr.right - ir * sx), b: Math.min(box.b, pr.bottom - ib * sy) };
      }
    }
    box = { l: Math.max(box.l, 0), t: Math.max(box.t, 0), r: Math.min(box.r, W), b: Math.min(box.b, H) };
    const area = Math.max(0, box.r - box.l) * Math.max(0, box.b - box.t);
    const full = Math.max(1, (r.right - r.left) * (r.bottom - r.top));
    if (area / full < 0.5) return null; // 마스크 안에서 올라오는 중이거나 화면 밖 (한 줄로 접힌 입력창 = 59%)
    return { op, rect: r };
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
  return { centred, cols, sizes, stray };
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
      resolve({ px: best, from: bestEnd - best + 1, to: bestEnd + 1, pct: +((100 * best) / h).toFixed(1) });
    };
    img.src = "data:image/png;base64," + b64;
  });
}

(async () => {
  const browser = await chromium.launch();
  const decoder = await browser.newPage();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => window.__playerReady === true && window.__player && typeof window.__player.renderSeek === "function", null, { timeout: 60000, polling: 100 }); // 런타임이 rAF 를 쥐고 있어 interval 폴링
  await page.evaluate(() => window.__player.enableRenderMode && window.__player.enableRenderMode());
  await page.evaluate(() => document.fonts.ready);
  const out = [];
  const allSizes = new Set();
  for (const t of times) {
    await page.evaluate(async (t) => { const r = window.__player.renderSeek(t); if (r && r.then) await r; }, t); // 렌더와 같은 결정적 seek
    await page.waitForTimeout(150);
    const m = await page.evaluate(collect);
    const shot = (await page.screenshot()).toString("base64");
    m.band = await decoder.evaluate(emptyBand, shot);
    Object.keys(m.sizes).forEach((s) => allSizes.add(s));
    out.push({ t, ...m });
  }
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
  lines.push("| t (s) | largest empty band (rows y) | px | % of 1920 | ≤ 35% |");
  lines.push("|---|---|---|---|---|");
  for (const f of out) lines.push(`| ${f.t} | ${f.band.from}–${f.band.to} | ${f.band.px} | ${f.band.pct} | ${f.band.pct <= 35 ? "✓" : "✗"} |`);
  const strays = out.flatMap((f) => f.stray.map((s) => `${f.t}s ${s.el} "${s.text}" ${s.fs}`));
  const sizeList = [...allSizes].sort((a, b) => parseFloat(a) - parseFloat(b));
  lines.push("");
  lines.push(`font sizes seen (computed): ${sizeList.join(", ")} — ${sizeList.length} sizes`);
  lines.push(`max |Δx| centred text: ${worst.toFixed(2)} px; max |Δx| bubble column centre: ${worstCol.toFixed(2)} px`);
  lines.push(`unannotated visible text: ${strays.length ? strays.join("; ") : "none"}`);
  console.log(lines.join("\n"));
  if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(out, null, 1));
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
