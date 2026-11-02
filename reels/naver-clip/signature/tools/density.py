"""Whitespace measures (art direction v3.2 §7-2) from a screenshot.

python3 tools/density.py [--fill y0:y1 ...] frame1.png [frame2.png ...]   -> one JSON line per frame

A row is EMPTY when it is a single flat colour (every pixel within 24 of the row median, summed over
RGB) and that colour matches the rows 8px above and below, so a 4px full-bleed line or a field edge
counts as an object while a flat ground (Ink, Paper, Navy, or either half of a split) counts as empty.
`--fill y0:y1` declares a full-bleed footer/dock field: those rows count as FILLED (an object), and an
empty run next to them counts as an edge run, like the frame's own top and bottom.

  band_px / band_pct : the largest contiguous run of EMPTY rows anywhere (edges included)
  gap_px / gap_pct   : the largest INTERIOR run, i.e. between two object rows (edge runs excluded):
                       the vertical gap between adjacent blocks
"""
import json
import sys

import numpy as np
from PIL import Image

TOL = 24
args = sys.argv[1:]
fills = []
files = []
i = 0
while i < len(args):
    if args[i] == "--fill":
        a, b = args[i + 1].split(":")
        fills.append((int(float(a)), int(float(b))))
        i += 2
    else:
        files.append(args[i])
        i += 1

for path in files:
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    h = a.shape[0]
    med = np.median(a, axis=1)                                   # (h, 3) row median colour
    flat = np.abs(a - med[:, None, :]).sum(axis=2).max(axis=1) < TOL
    up = np.r_[np.full(8, True), np.abs(med[8:] - med[:-8]).sum(axis=1) < TOL]
    dn = np.r_[np.abs(med[:-8] - med[8:]).sum(axis=1) < TOL, np.full(8, True)]
    empty = flat & up & dn
    edge = np.zeros(h, bool)                                     # rows that make a run an "edge" run
    for y0, y1 in fills:
        y0, y1 = max(0, y0), min(h, y1)
        empty[y0:y1] = False
        edge[max(0, y0 - 8):min(h, y1 + 8)] = True      # the 8px edge rule makes the field's own rim an edge too
    runs = []
    y = 0
    while y < h:
        if empty[y]:
            s = y
            while y < h and empty[y]:
                y += 1
            runs.append((s, y))
        else:
            y += 1
    best = max(runs, key=lambda r: r[1] - r[0], default=(0, 0))
    interior = [r for r in runs if r[0] > 0 and r[1] < h and not edge[r[0] - 1] and not edge[min(h - 1, r[1])]]
    gbest = max(interior, key=lambda r: r[1] - r[0], default=(0, 0))
    print(json.dumps({"file": path,
                      "band_px": int(best[1] - best[0]), "band_pct": round(100 * (best[1] - best[0]) / h, 1),
                      "band_from": int(best[0]), "band_to": int(best[1]),
                      "gap_px": int(gbest[1] - gbest[0]), "gap_from": int(gbest[0]), "gap_to": int(gbest[1]),
                      "empty_rows_pct": round(100 * empty.mean(), 1)}))
