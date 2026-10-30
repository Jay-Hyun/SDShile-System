#!/usr/bin/env python3
"""Pen strokes for a line of script lettering, so the card can write it on screen as if by hand.

The line is laid out by Chrome (the same engine that renders the film) as an SVG <text>, rasterised at 2x, and
skeletonised. The skeleton becomes a graph (junctions and ends as nodes, pixel chains as edges); short spurs are
pruned; then a pen walks it left to right, carrying straight on through junctions (smallest turn), lifting only
when nothing connected is left. Each stroke is cut into short pieces with their own width (the local letter
thickness), timed at one constant pen speed; dots become one short touch.

Writes assets/js/calligraphy.js: window.CALLI = { text, font, size, vb, x, y, ws, total, strokes: [{d, w, t, dur}] }
(viewBox units and ms from the first touch of the pen). s6 masks the <text> with these paths.

Usage: /opt/mediaenv/bin/python scripts/calligraphy.py [--text "Happy Wedding Day"] [--ms 3000]
"""
import argparse
import json
import os
import subprocess
import tempfile

import cv2
import numpy as np
from skimage.morphology import skeletonize

ap = argparse.ArgumentParser()
ap.add_argument("--text", default="Happy Wedding Day")
ap.add_argument("--font", default="Great Vibes")
ap.add_argument("--file", default="assets/fonts/GreatVibes-Regular.ttf")
ap.add_argument("--size", type=float, default=120)
ap.add_argument("--ws", type=float, default=16, help="extra word spacing (viewBox units)")
ap.add_argument("--ms", type=float, default=3000, help="writing time, pen lifts included")
ap.add_argument("--lift", type=float, default=25, help="ms the pen is lifted when it jumps")
args = ap.parse_args()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1500, 240
X, Y = W / 2, 160  # text anchor (middle) and baseline
K = 2  # raster scale

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * K}" height="{H * K}">'
       f'<rect width="{W}" height="{H}" fill="#000"/>'
       f'<text x="{X}" y="{Y}" text-anchor="middle" font-family="{args.font}" font-size="{args.size}" '
       f'word-spacing="{args.ws}" fill="#fff">{args.text}</text></svg>')
html = (f'<html><head><style>@font-face{{font-family:"{args.font}";src:url("file://{ROOT}/{args.file}")}}'
        f'html,body{{margin:0;background:#000}}</style></head><body>{svg}</body></html>')
tmp = tempfile.mkdtemp()
open(f"{tmp}/t.html", "w").write(html)
js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {W * K}, height: {H * K} }} }});
  await p.goto('file://{tmp}/t.html');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({{ path: '{tmp}/t.png', clip: {{ x: 0, y: 0, width: {W * K}, height: {H * K} }} }});
  await b.close();
}})();"""
subprocess.run(["node", "-e", js], check=True)
img = cv2.imread(f"{tmp}/t.png", cv2.IMREAD_GRAYSCALE)
ink = img > 110
dist = cv2.distanceTransform(ink.astype(np.uint8), cv2.DIST_L2, 5)
sk = skeletonize(ink)

# ---- skeleton graph -------------------------------------------------------------------------------------
pts = set(zip(*np.nonzero(sk)))  # (row, col)
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def nbrs(p):
    r, c = p
    out = []
    for dr, dc in N8:
        q = (r + dr, c + dc)
        if q not in pts:
            continue
        if dr and dc and ((r + dr, c) in pts or (r, c + dc) in pts):
            continue  # a diagonal step that an orthogonal pair already covers
        out.append(q)
    return out


def build():
    deg = {p: len(nbrs(p)) for p in pts}
    nodes = {p for p, d in deg.items() if d != 2}
    edges, seen = [], set()
    for n in nodes:
        for q in nbrs(n):
            if (n, q) in seen:
                continue
            chain = [n, q]
            prev, cur = n, q
            while cur not in nodes:
                nx = [x for x in nbrs(cur) if x != prev]
                if not nx:
                    break
                prev, cur = cur, nx[0]
                chain.append(cur)
            seen.add((chain[0], chain[1]))
            seen.add((chain[-1], chain[-2]))
            edges.append(chain)
    # closed loops with no node (an "o" drawn as a ring)
    covered = {p for e in edges for p in e}
    for p in sorted(pts - covered, key=lambda p: (p[1], p[0])):
        if p in covered:
            continue
        chain = [p]
        prev, cur = None, p
        while True:
            nx = [x for x in nbrs(cur) if x != prev and x not in chain[1:]]
            if not nx:
                break
            prev, cur = cur, nx[0]
            chain.append(cur)
            if cur == p:
                break
        covered.update(chain)
        edges.append(chain)
    return deg, nodes, edges


# prune spurs: end-to-junction edges shorter than the letter is thick there
for _ in range(4):
    deg, nodes, edges = build()
    cut = 0
    for e in edges:
        a, b = e[0], e[-1]
        ends = [x for x in (a, b) if deg.get(x, 0) == 1]
        junc = [x for x in (a, b) if deg.get(x, 0) >= 3]
        if len(ends) == 1 and junc and len(e) < max(10, 1.6 * dist[junc[0]]):
            for p in e:
                if p != junc[0]:
                    pts.discard(p)
            cut += 1
    if not cut:
        break
deg, nodes, edges = build()


# ---- pen walk ---------------------------------------------------------------------------------------------
def heading(chain, k=10):
    a = np.array(chain[0], float)
    b = np.array(chain[min(k, len(chain) - 1)], float)
    v = b - a
    n = np.linalg.norm(v)
    return v / n if n else v


inc = {}
for i, e in enumerate(edges):
    inc.setdefault(e[0], []).append(i)
    inc.setdefault(e[-1], []).append(i)
used = [False] * len(edges)


def oriented(i, start):
    e = edges[i]
    return e if e[0] == start else e[::-1]


strokes = []
while not all(used):
    # start near where the pen is if there is unused ink close by (finish the letter), else at the leftmost
    # unused ink; at the left end of that edge (a free end if it has one)
    cand = [i for i in range(len(edges)) if not used[i]]
    left = min(min(edges[i][0][1], edges[i][-1][1]) for i in cand)
    here = np.array(strokes[-1][-1], float) if strokes else None

    def cost(i):
        e = edges[i]
        x = min(e[0][1], e[-1][1])
        near = min(np.linalg.norm(np.array(e[0], float) - here), np.linalg.norm(np.array(e[-1], float) - here)) if here is not None else 0
        return (near if here is not None and near < 70 else 1e6) + (x - left) * (0 if here is not None and near < 70 else 1)
    i0 = min(cand, key=cost)
    a, b = edges[i0][0], edges[i0][-1]
    fa, fb = deg.get(a, 2) == 1, deg.get(b, 2) == 1
    start = (a if fa else b) if fa != fb else (a if a[1] <= b[1] else b)
    path = list(oriented(i0, start))
    used[i0] = True
    while True:
        end = path[-1]
        nxt = [i for i in inc.get(end, []) if not used[i]]
        if not nxt:
            break
        hin = -heading(path[::-1])
        best = max(nxt, key=lambda i: float(np.dot(hin, heading(oriented(i, end)))))
        used[best] = True
        path += oriented(best, end)[1:]
    strokes.append(path)
# components too small to have a skeleton edge (a dot) still need the pen
n_lab, lab = cv2.connectedComponents(ink.astype(np.uint8))
have = {lab[p] for s in strokes for p in s}
for k in range(1, n_lab):
    if k not in have:
        rr, cc = np.nonzero(lab == k)
        if len(rr) > 20:
            strokes.append([(int(rr.mean()), int(cc.mean()))])
strokes.sort(key=lambda s: min(p[1] for p in s))  # a dot is written where it sits, left to right


# ---- polylines, widths, timing --------------------------------------------------------------------------
def rdp(p, eps):
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]
    ab = b - a
    n = np.linalg.norm(ab)
    d = np.abs(ab[0] * (p[:, 1] - a[1]) - ab[1] * (p[:, 0] - a[0])) / n if n else np.linalg.norm(p - a, axis=1)
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(p[: i + 1], eps)[:-1], rdp(p[i:], eps)])
    return np.vstack([a, b])


pieces = []  # (stroke index, xy points in viewBox units, width, arc start, arc end)
stroke_len = {}
for si, s in enumerate(strokes):
    arr = np.array([(c / K, r / K) for r, c in s], float)
    thick = np.array([dist[p] / K for p in s])  # half-thickness, viewBox units
    if len(s) < 4:  # a dot: one short touch covering the blob
        r0 = float(max(dist[lab == lab[s[0]]].max() / K, 1.0))
        cx, cy = arr.mean(axis=0)
        arr = np.array([[cx - r0 * 0.4, cy + r0 * 0.3], [cx + r0 * 0.4, cy - r0 * 0.3]])
        L = float(np.linalg.norm(arr[1] - arr[0]))
        pieces.append((si, arr, 2.6 * r0 + 1.5, 0.0, L))
        stroke_len[si] = L
        continue
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(arr, axis=0), axis=1))]
    stroke_len[si] = float(arc[-1])
    step = 18  # pixels per piece (at 2x)
    for j in range(0, len(s) - 1, step):
        k1 = min(len(s), j + step + 3)  # overlap the next piece a little
        w = 2.0 * float(np.percentile(thick[j:k1], 90)) * 1.35 + 1.2
        pieces.append((si, rdp(arr[j:k1], 0.35), w, float(arc[j]), float(arc[k1 - 1])))

# one constant pen speed; a short lift only where the pen jumps to somewhere new
order = sorted(stroke_len)
lifts = {}
for a, b in zip(order, order[1:]):
    pa = np.array(strokes[a][-1], float) / K
    pb = np.array(strokes[b][0], float) / K
    lifts[b] = args.lift if np.linalg.norm(pa - pb) > 12 else 0.0
pen = sum(stroke_len.values()) / max(1.0, args.ms - sum(lifts.values()))  # units per ms
start, t = {}, 0.0
for si in order:
    t += lifts.get(si, 0.0)
    start[si] = t
    t += stroke_len[si] / pen
out = []
for si, seg, w, a0, a1 in pieces:
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in seg)
    out.append({"d": d, "w": round(w, 2), "t": round(start[si] + a0 / pen, 1), "dur": round(max((a1 - a0) / pen, 6.0), 1)})

CALLI = {"text": args.text, "font": args.font, "size": args.size, "vb": [W, H], "x": X, "y": Y, "ws": args.ws,
         "total": round(t, 1), "strokes": out}
with open("assets/js/calligraphy.js", "w") as f:
    f.write("/* generated by scripts/calligraphy.py — do not edit */\nwindow.CALLI = ")
    json.dump(CALLI, f, separators=(",", ":"))
    f.write(";\n")
# debug sheet: the pen order as a colour ramp over the letters
dbg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) // 3
for k, p in enumerate(out):
    hue = int(170 * k / max(1, len(out) - 1))
    col = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0, 0].tolist()
    xy = np.array([[float(v) for v in q.split(",")] for q in p["d"][1:].split(" L")]) * K
    cv2.polylines(dbg, [xy.astype(np.int32)], False, col, 2)
cv2.imwrite(os.environ.get("CALLI_DEBUG", f"{tmp}/order.png"), dbg)
print(f"{len(strokes)} strokes ({sum(1 for v in lifts.values() if v)} pen lifts), {len(out)} pieces, "
      f"{sum(stroke_len.values()):.0f} units of ink, writes in {t:.0f} ms")
