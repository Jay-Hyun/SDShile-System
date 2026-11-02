// Centering + type-size audit for settled frames (art direction v3, §1–2, §8).
//
//   node tools/measure.cjs [--variant 15] [--at 1.5,2.9,...] [--shots DIR] [--json OUT]
//
// Serves the project folder (or v15/) on a local port, injects the HyperFrames runtime that the
// pinned CLI ships (hyperframe.runtime.iife.js), seeks the root timeline with
// window.__player.renderSeek(t) and, at each time, collects every visible text run:
//   - box   = union of the Range client rects of every visible text node in one line (its nearest
//             non-inline ancestor), so a centred line with a gold word is measured as one line, by
//             its glyph-advance box and not by its 840px block
//   - size  = computed font-size of the runs in that line
//   - dx    = box centre x - 540
// A run counts as visible when the product of ancestor opacities is > 0.02, nothing is display:none
// or visibility:hidden, and the box survives clipping by every overflow:hidden / clip-path ancestor.
// Prints one table per time plus the font-size set, then the empty-band measure (tools/density.py:
// largest contiguous run of flat, object-free rows, % of 1920) from a screenshot of each moment.
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
const DEFAULT_AT = { "30": "1.5,2.95,6.7,10.35,13.85,17.3,20.95,24.3,27.2,29.8", "15": "1.2,4.6,8.1,9.95,12.2,14.8" };
const TIMES = opt("--at", DEFAULT_AT[VARIANT]).split(",").map(Number);
const SHOT_DIR = opt("--shots", fs.mkdtempSync(path.join(require("os").tmpdir(), "measure-")));
const JSON_OUT = opt("--json", null);

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

function collect() {
  const out = [];
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
  const clipBy = (el, r) => {
    // intersect with every ancestor that clips (overflow hidden/clip, or a clip-path inset)
    let { left, top, right, bottom } = r;
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
    return right - left > 1 && bottom - top > 1;
  };
  // group text runs by their line: the nearest ancestor that is not display:inline (a .li, .row, .pill)
  const blockOf = (el) => {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const d = getComputedStyle(e).display;
      if (d !== "inline" && d !== "contents") return e;
    }
    return el;
  };
  const groups = new Map();
  const walk = (doc) => {
    const tw = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      if (!n.textContent.trim()) continue;
      const el = n.parentElement;
      if (!el || ["SCRIPT", "STYLE", "TEMPLATE"].includes(el.tagName)) continue;
      const op = visibleChain(el);
      if (op <= 0.02) continue;
      const rg = doc.createRange();
      rg.selectNodeContents(n);
      const rects = [...rg.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
      if (!rects.length) continue;
      const blk = blockOf(el);
      const g = groups.get(blk) || { rects: [], sizes: new Set(), weights: new Set(), op: 0, text: "" };
      g.rects.push(...rects);
      g.sizes.add(parseFloat(getComputedStyle(el).fontSize));
      g.weights.add(getComputedStyle(el).fontWeight);
      g.op = Math.max(g.op, op);
      groups.set(blk, g);
    }
  };
  walk(document);
  for (const [blk, g] of groups) {
    const box = g.rects.reduce((a, r) => ({ left: Math.min(a.left, r.left), top: Math.min(a.top, r.top), right: Math.max(a.right, r.right), bottom: Math.max(a.bottom, r.bottom) }),
      { left: 1e9, top: 1e9, right: -1e9, bottom: -1e9 });
    if (!clipBy(blk, box)) continue;
    const host = blk.closest("[data-composition-id]");
    out.push({
      comp: host ? host.getAttribute("data-composition-id") : "?",
      id: blk.id || blk.className || blk.tagName,
      text: blk.textContent.replace(/\s+/g, " ").trim().slice(0, 28),
      size: Math.max(...g.sizes),
      sizes: [...g.sizes],
      weight: [...g.weights].join("/"),
      cx: +((box.left + box.right) / 2).toFixed(2),
      top: Math.round(box.top),
      bottom: Math.round(box.bottom),
      w: Math.round(box.right - box.left),
      opacity: +g.op.toFixed(2),
    });
  }
  return out;
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
  const report = [];
  const shotFiles = [];
  const sizes = new Map();
  let worst = 0;
  for (const t of TIMES) {
    await page.evaluate((tt) => window.__player.renderSeek(tt, { exact: true }), t);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.evaluate(() => document.fonts.ready);
    fs.mkdirSync(SHOT_DIR, { recursive: true });
    const shot = path.join(SHOT_DIR, `t${t.toFixed(2)}.png`);
    await page.screenshot({ path: shot });
    shotFiles.push(shot);
    const rows = (await page.evaluate(collect)).sort((a, b) => a.top - b.top);
    console.log(`\n t=${t.toFixed(2)}s  (${rows.length} visible text runs)`);
    console.log("  comp     id                       size  wt   top  bottom   width   centre-x      dx   text");
    for (const r of rows) {
      const dx = r.cx - 540;
      worst = Math.max(worst, Math.abs(dx));
      r.sizes.forEach((z) => sizes.set(z, (sizes.get(z) || 0) + 1));
      console.log(`  ${r.comp.padEnd(8)} ${String(r.id).slice(0, 24).padEnd(24)} ${String(r.size).padStart(4)} ${String(r.weight).padStart(4)} ${String(r.top).padStart(5)} ${String(r.bottom).padStart(6)} ${String(r.w).padStart(7)} ${r.cx.toFixed(2).padStart(9)} ${(dx >= 0 ? "+" : "") + dx.toFixed(2).padStart(6)}   ${r.text}`);
    }
    report.push({ t, rows: rows.map((r) => ({ ...r, dx: +(r.cx - 540).toFixed(2) })) });
  }
  // empty-band measure (§7-1): largest contiguous run of flat, object-free rows per frame
  const dens = require("child_process").spawnSync("python3", [path.join(__dirname, "density.py"), ...shotFiles], { encoding: "utf8" });
  const bands = dens.stdout.trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
  let worstBand = 0;
  console.log("\n empty band (largest contiguous flat row band, % of 1920; limit 35%)");
  bands.forEach((b, i) => {
    worstBand = Math.max(worstBand, b.band_pct);
    report[i].band = b;
    console.log(`  t=${TIMES[i].toFixed(2)}s  ${String(b.band_px).padStart(4)} px  ${String(b.band_pct).padStart(5)} %   rows ${b.band_from}-${b.band_to}${b.band_pct > 35 ? "   OVER" : ""}`);
  });
  console.log(`\nfont-size set (px: count): ${[...sizes.entries()].sort((a, b) => a[0] - b[0]).map(([s, c]) => `${s}: ${c}`).join(", ")}`);
  console.log(`max |centre-x - 540| = ${worst.toFixed(2)} px  -> ${worst <= 2 ? "PASS" : "FAIL"} (limit 2 px)`);
  if (errors.length) console.log("page errors:", errors);
  console.log(`largest empty band = ${worstBand}% of frame height`);
  if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ variant: VARIANT, times: TIMES, sizes: [...sizes.keys()].sort((a, b) => a - b), maxDx: +worst.toFixed(2), maxBandPct: worstBand, report }, null, 1));
  await browser.close();
  server.close();
  process.exit(worst <= 2 ? 0 : 1);
})().catch((e) => {
  console.error(e);
  server.close();
  process.exit(2);
});
