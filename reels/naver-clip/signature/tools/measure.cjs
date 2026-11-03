// Layout audit for settled frames (art direction v3 / v3.2: §1–2, §7-2, §8).
//
//   node tools/measure.cjs [--variant 15] [--at 1.5,2.9,...] [--shots DIR] [--json OUT] [--no-reading]
//
// Serves the project folder (or v15/) on a local port, injects the HyperFrames runtime that the
// pinned CLI ships (hyperframe.runtime.iife.js), seeks the root timeline with
// window.__player.renderSeek(t) and, at each time, measures:
//
//  1. every visible text line (its nearest non-inline ancestor): the glyph-advance box (union of the
//     Range client rects), computed font-size, dx = box centre - 540. A logo lockup ([data-lockup],
//     mark + name) is measured as one unit by its flex box, because the mark is not text.
//  2. WHITESPACE (tools/density.py on a screenshot of the moment):
//       empty band = the largest contiguous run of flat, object-free rows (edges included), where a
//                    declared full-bleed footer field ([data-fill]) counts as filled;
//       max gap    = the largest run BETWEEN two blocks (edge runs excluded), measured with the
//                    compliance overlay (연출 badge, disclaimers: the `legal` layer) hidden.
//  3. READING RATE (default on; --no-reading skips it): the page is swept at 20 fps; every caption line
//     (not texture [data-tx]: documents, UI status, button labels, the phone block; not the legal layer,
//     not the lockup) is timed from the first moment it is fully visible; a line that only repeats words
//     already shown is a re-read and is skipped; lines that arrive together form an event; the event's
//     characters (without spaces) are divided by the time until the next event or the next hard cut.
//
// Exits 1 when any |dx| > 2.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.dirname(__dirname);
const argv = process.argv.slice(2);
const opt = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const VARIANT = opt("--variant", "30");
const DIR = VARIANT === "15" ? path.join(ROOT, "v15") : ROOT;
const DUR = VARIANT === "15" ? 15 : 30;
const DEFAULT_AT = { "30": "1.5,2.95,6.7,10.35,13.85,17.3,20.95,24.3,27.2,29.8", "15": "1.2,4.6,8.1,9.95,12.2,14.8" };
const TIMES = opt("--at", DEFAULT_AT[VARIANT]).split(",").map(Number);
const SHOT_DIR = opt("--shots", fs.mkdtempSync(path.join(require("os").tmpdir(), "measure-")));
const JSON_OUT = opt("--json", null);
const READING = !argv.includes("--no-reading");

function findRuntime() {
  const base = "/root/.npm/_npx";
  for (const d of fs.existsSync(base) ? fs.readdirSync(base) : []) {
    const pj = path.join(base, d, "node_modules/hyperframes/package.json");
    if (fs.existsSync(pj) && JSON.parse(fs.readFileSync(pj, "utf8")).version === "0.8.200") {
      return path.join(base, d, "node_modules/hyperframes/dist/hyperframe.runtime.iife.js");
    }
  }
  throw new Error("hyperframes@0.8.200 not in the npx cache: run `npx --yes hyperframes@0.8.200 --version` once");
}
const RUNTIME = findRuntime();
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".mp3": "audio/mpeg", ".json": "application/json", ".png": "image/png" };

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  if (url === "/__hf_runtime.js") {
    res.writeHead(200, { "content-type": "text/javascript" });
    return res.end(fs.readFileSync(RUNTIME));
  }
  const file = path.join(DIR, url === "/" ? "index.html" : url);
  if (!file.startsWith(DIR) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404);
    return res.end();
  }
  let body = fs.readFileSync(file);
  if (url === "/" || url === "/index.html") {
    body = body.toString().replace("</body>", '<script src="/__hf_runtime.js"></script></body>');
  }
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
  res.end(body);
});

// runs in the page: every visible text line + lockups + declared footer fields
function collect() {
  const out = [];
  const docks = [];
  const W = 1080, H = 1920;
  const visibleChain = (el) => {
    let op = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden") return 0;
      op *= parseFloat(cs.opacity);
    }
    return op;
  };
  // fraction of the box that survives every clipping ancestor (overflow hidden/clip, clip-path inset)
  const clipFrac = (el, r) => {
    let { left, top, right, bottom } = r;
    const area = (r.right - r.left) * (r.bottom - r.top);
    for (let e = el.parentElement; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      const clips = /(hidden|clip)/.test(cs.overflow + cs.overflowX + cs.overflowY) || (cs.clipPath && cs.clipPath !== "none");
      if (!clips) continue;
      const b = e.getBoundingClientRect();
      let ins = [0, 0, 0, 0];
      const m = cs.clipPath && cs.clipPath.match(/^inset\(([^)]*)\)/);
      if (m) {
        const v = m[1].split(" round")[0].trim().split(/\s+/).map(parseFloat);
        ins = [v[0], v[1] ?? v[0], v[2] ?? v[0], v[3] ?? v[1] ?? v[0]];
      }
      left = Math.max(left, b.left + ins[3]); top = Math.max(top, b.top + ins[0]);
      right = Math.min(right, b.right - ins[1]); bottom = Math.min(bottom, b.bottom - ins[2]);
    }
    left = Math.max(left, 0); top = Math.max(top, 0); right = Math.min(right, W); bottom = Math.min(bottom, H);
    if (right - left <= 1 || bottom - top <= 1) return 0;
    return ((right - left) * (bottom - top)) / area;
  };
  const blockOf = (el) => {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const d = getComputedStyle(e).display;
      // word spans (.w) and printed entries (.ent) are inline-blocks inside one line: measure the line
      if (d !== "inline" && d !== "contents" && !e.classList.contains("w") && !e.classList.contains("ent")) return e;
    }
    return el;
  };
  const hostOf = (el) => {
    const h = el.closest("[data-composition-id]");
    return h ? h.getAttribute("data-composition-id") : "?";
  };
  const groups = new Map();
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement;
    if (!el || ["SCRIPT", "STYLE", "TEMPLATE"].includes(el.tagName)) continue;
    const op = visibleChain(el);
    if (op <= 0.02) continue;
    const rg = document.createRange();
    rg.selectNodeContents(n);
    const rects = [...rg.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
    if (!rects.length) continue;
    const blk = blockOf(el);
    const g = groups.get(blk) || { rects: [], sizes: new Set(), weights: new Set(), op: 0 };
    g.rects.push(...rects);
    g.sizes.add(parseFloat(getComputedStyle(el).fontSize));
    g.weights.add(getComputedStyle(el).fontWeight);
    g.op = Math.max(g.op, op);
    groups.set(blk, g);
  }
  for (const [blk, g] of groups) {
    const box = g.rects.reduce((a, r) => ({ left: Math.min(a.left, r.left), top: Math.min(a.top, r.top), right: Math.max(a.right, r.right), bottom: Math.max(a.bottom, r.bottom) }),
      { left: 1e9, top: 1e9, right: -1e9, bottom: -1e9 });
    const frac = clipFrac(blk, box);
    if (frac <= 0.001) continue;
    const comp = hostOf(blk);
    const chars = blk.textContent.replace(/\s+/g, "").length;
    out.push({
      comp,
      id: blk.id || (blk.parentElement && blk.parentElement.id) || blk.className || blk.tagName,
      key: comp + ":" + (blk.id || blk.parentElement?.id || blk.textContent.slice(0, 8)),
      text: blk.textContent.replace(/\s+/g, " ").trim().slice(0, 28),
      full: blk.textContent.replace(/\s+/g, " ").trim(),
      size: Math.max(...g.sizes),
      sizes: [...g.sizes],
      weight: [...g.weights].join("/"),
      cx: +((box.left + box.right) / 2).toFixed(2),
      top: Math.round(box.top),
      bottom: Math.round(box.bottom),
      w: Math.round(box.right - box.left),
      opacity: +g.op.toFixed(2),
      vis: +(frac * Math.min(1, g.op)).toFixed(3),
      chars,
      tx: !!blk.closest("[data-tx]"),
      legal: comp === "legal",
      inLock: !!blk.closest("[data-lockup],[data-grid]"),
    });
  }
  // a lockup is measured as one unit (its flex box: mark + gap + name)
  for (const el of document.querySelectorAll("[data-lockup]")) {
    const op = visibleChain(el);
    const r = el.getBoundingClientRect();
    if (op <= 0.02 || r.width < 1) continue;
    const frac = clipFrac(el, r);
    if (frac <= 0.001) continue;
    out.push({ comp: hostOf(el), id: "lockup", key: hostOf(el) + ":lockup", text: "[mark] " + el.textContent.trim().slice(0, 12), size: 44, sizes: [44], weight: "600",
      cx: +((r.left + r.right) / 2).toFixed(2), top: Math.round(r.top), bottom: Math.round(r.bottom), w: Math.round(r.width), opacity: +op.toFixed(2), vis: +(frac * Math.min(1, op)).toFixed(3),
      chars: 0, tx: true, legal: false, inLock: false, lockup: true });
  }
  // a row of cells ([data-grid], e.g. the week strip) is measured as one unit: the union of its cells
  for (const el of document.querySelectorAll("[data-grid]")) {
    const op = visibleChain(el);
    if (op <= 0.02) continue;
    const rs = [...el.children].map((c) => c.getBoundingClientRect()).filter((r) => r.width > 0);
    if (!rs.length) continue;
    const L = Math.min(...rs.map((r) => r.left)), R = Math.max(...rs.map((r) => r.right));
    out.push({ comp: hostOf(el), id: "grid:" + el.id, key: hostOf(el) + ":grid", text: "[row of " + rs.length + " cells]", size: 44, sizes: [44], weight: "500",
      cx: +((L + R) / 2).toFixed(2), top: Math.round(Math.min(...rs.map((r) => r.top))), bottom: Math.round(Math.max(...rs.map((r) => r.bottom))), w: Math.round(R - L), opacity: +op.toFixed(2), vis: 1,
      chars: 0, tx: true, legal: false, inLock: false, lockup: true });
  }
  for (const el of document.querySelectorAll("[data-fill]")) {
    if (visibleChain(el) <= 0.02) continue;
    const r = el.getBoundingClientRect();
    docks.push([Math.round(r.top), Math.round(r.bottom)]);
  }
  return { rows: out, docks };
}

function flatPaper(on) {
  for (const host of [document, ...[...document.querySelectorAll("*")].filter((e) => e.shadowRoot).map((e) => e.shadowRoot)]) {
    let st = host.querySelector && host.querySelector("#__flat");
    if (on && !st) { st = document.createElement("style"); st.id = "__flat"; st.textContent = "[data-paper]{background-image:none !important;background-color:#f7f6f2 !important}"; (host.head || host).appendChild(st); }
    if (!on && st) st.remove();
  }
}
function goldPaint(on) {
  const id = "__gold";
  let st = document.getElementById(id);
  if (on && !st) {
    st = document.createElement("style"); st.id = id;
    st.textContent = "[data-gold],[data-gold] *{color:#ff00ff !important;background-color:#ff00ff !important;stroke:#ff00ff !important} [data-gold] .w, .au{color:#ff00ff !important;background-color:transparent !important} .lmark[data-gold]{background-color:#ff00ff !important} svg[data-gold]{background-color:transparent !important} .du[data-gold]{background-color:#ff00ff !important} .dl.au{background-color:transparent !important}";
    document.head.appendChild(st);
  }
  if (!on && st) st.remove();
}
function setLegal(hidden) {
  const el = document.querySelector('[data-composition-id="legal"]');
  if (el) el.style.display = hidden ? "none" : "";   // (the runtime sets visibility on .clip children itself)
}

(async () => {
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: "load" });
  await page.waitForFunction(() => window.__player && typeof window.__player.renderSeek === "function", null, { timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  const seek = async (t) => {
    await page.evaluate((tt) => window.__player.renderSeek(tt, { exact: true }), t);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  };
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  const report = [];
  const sizes = new Map();
  let worst = 0, worstBand = 0, worstGap = 0;
  for (const t of TIMES) {
    await seek(t);
    await page.evaluate(() => document.fonts.ready);
    const shot = path.join(SHOT_DIR, `t${t.toFixed(2)}.png`);
    const shotNoLegal = path.join(SHOT_DIR, `t${t.toFixed(2)}-nolegal.png`);
    await page.screenshot({ path: shot });
    // whitespace is measured with the paper texture swapped for flat Paper, so texture never counts as "filled"
    await page.evaluate(flatPaper, true);
    const shotFlat = path.join(SHOT_DIR, `t${t.toFixed(2)}-flat.png`);
    await page.screenshot({ path: shotFlat });
    await page.evaluate(setLegal, true);
    await page.screenshot({ path: shotNoLegal });
    await page.evaluate(setLegal, false);
    await page.evaluate(flatPaper, false);
    // gold audit: repaint every [data-gold] element magenta and count the changed pixels
    await page.evaluate(goldPaint, true);
    const shotGold = path.join(SHOT_DIR, `t${t.toFixed(2)}-gold.png`);
    await page.screenshot({ path: shotGold });
    await page.evaluate(goldPaint, false);
    const px = JSON.parse(require("child_process").spawnSync("python3", [path.join(__dirname, "pixels.py"), shot, shotGold], { encoding: "utf8" }).stdout.trim());
    const { rows: all, docks } = await page.evaluate(collect);
    const rows = all.filter((r) => !r.inLock).sort((a, b) => a.top - b.top);
    const fill = docks.flatMap(([a, b]) => ["--fill", `${a}:${b}`]);
    const run = (file) => JSON.parse(require("child_process").spawnSync("python3", [path.join(__dirname, "density.py"), ...fill, file], { encoding: "utf8" }).stdout.trim());
    const band = run(shotFlat);
    const gap = run(shotNoLegal);
    worstBand = Math.max(worstBand, band.band_pct);
    worstGap = Math.max(worstGap, gap.gap_px);
    console.log(`\n t=${t.toFixed(2)}s  (${rows.length} visible lines)   empty band ${band.band_px}px = ${band.band_pct}% (rows ${band.band_from}-${band.band_to})   max gap ${gap.gap_px}px (rows ${gap.gap_from}-${gap.gap_to})   dark ${px.dark_pct}%   gold ${px.gold_pct}%${docks.length ? "   dock " + docks.map((d) => d.join("-")).join(",") : ""}`);
    console.log("  comp     id                       size  wt   top  bottom   width   centre-x      dx   text");
    for (const r of rows) {
      const dx = r.cx - 540;
      worst = Math.max(worst, Math.abs(dx));
      r.sizes.forEach((z) => sizes.set(z, (sizes.get(z) || 0) + 1));
      console.log(`  ${r.comp.padEnd(8)} ${String(r.id).slice(0, 24).padEnd(24)} ${String(r.size).padStart(4)} ${String(r.weight).padStart(4)} ${String(r.top).padStart(5)} ${String(r.bottom).padStart(6)} ${String(r.w).padStart(7)} ${r.cx.toFixed(2).padStart(9)} ${(dx >= 0 ? "+" : "") + dx.toFixed(2).padStart(6)}   ${r.text}${r.lockup ? "   <- lockup (mark + name)" : ""}`);
    }
    report.push({ t, band, gap, px, rows: rows.map((r) => ({ ...r, dx: +(r.cx - 540).toFixed(2) })) });
  }

  // ---- reading rate
  let reading = null;
  if (READING) {
    const cutsFile = path.join(ROOT, "beats", VARIANT === "15" ? "cuts-15s.json" : "cuts.json");
    const cuts = fs.existsSync(cutsFile) ? JSON.parse(fs.readFileSync(cutsFile, "utf8")).cuts.map((c) => c.t) : [];
    const first = new Map();
    const STEP = 0.05;
    for (let t = 0; t < DUR - 1e-6; t += STEP) {
      await seek(t);
      const { rows } = await page.evaluate(collect);
      for (const r of rows) {
        if (r.tx || r.legal || r.inLock || r.lockup || !r.chars) continue;
        if (r.vis >= 0.9 && !first.has(r.key)) first.set(r.key, { t, chars: r.chars, text: r.text, full: r.full, top: r.top, key: r.key });
      }
    }
    // a line that only repeats words already shown (an earlier line, or a substring of one) is a re-read, not new text
    const lines = [...first.values()].sort((a, b) => a.t - b.t || a.top - b.top);
    const norm = (x) => x.replace(/\s+/g, "");
    let history = "";
    const events = [];
    for (const l of lines) {
      const n = norm(l.full);
      const repeat = history.includes(n);
      history += n;
      if (repeat) continue;
      const ev = events[events.length - 1];
      if (ev && l.t - ev.last <= 0.35) { ev.chars += l.chars; ev.texts.push(l.text); ev.last = l.t; }
      else events.push({ t: l.t, last: l.t, chars: l.chars, texts: [l.text] });
    }
    const hardCuts = [0, ...cuts, DUR].sort((a, b) => a - b);
    events.forEach((e, i) => {
      const nextEv = i + 1 < events.length ? events[i + 1].t : DUR;
      const nextCut = hardCuts.find((c) => c > e.t + 1e-6) ?? DUR;
      e.until = Math.min(nextEv, nextCut);
      e.window = +(e.until - e.t).toFixed(2);
      e.cps = +(e.chars / e.window).toFixed(1);
    });
    reading = events.map((e) => ({ t: +e.t.toFixed(2), chars: e.chars, window: e.window, cps: e.cps, text: e.texts.join(" / ") }));
    console.log("\n reading rate (caption lines only; documents, UI status and the legal layer are texture), limit 10 chars/s");
    console.log("  t       chars  window  chars/s");
    for (const e of reading) console.log(`  ${e.t.toFixed(2).padStart(5)}  ${String(e.chars).padStart(5)}  ${String(e.window).padStart(6)}  ${String(e.cps).padStart(7)}${e.cps > 10 ? "  OVER" : ""}   ${e.text.slice(0, 60)}`);
    console.log(`  peak ${Math.max(...reading.map((e) => e.cps))} chars/s`);
  }

  console.log(`\nfont-size set (px: count): ${[...sizes.entries()].sort((a, b) => a[0] - b[0]).map(([s, c]) => `${s}: ${c}`).join(", ")}`);
  console.log(`max |centre-x - 540| = ${worst.toFixed(2)} px  -> ${worst <= 2 ? "PASS" : "FAIL"} (limit 2 px)`);
  console.log(`largest empty band = ${worstBand}% of frame height (limit 15%)   largest block gap = ${worstGap}px (limit 140px)`);
  if (errors.length) console.log("page errors:", errors);
  if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ variant: VARIANT, times: TIMES, sizes: [...sizes.keys()].sort((a, b) => a - b), maxDx: +worst.toFixed(2), maxBandPct: worstBand, maxGapPx: worstGap, reading, report }, null, 1));
  await browser.close();
  server.close();
  process.exit(worst <= 2 ? 0 : 1);
})().catch((e) => {
  console.error(e);
  server.close();
  process.exit(2);
});
