"""Empty-band measure (art direction v3.1 §7-1: no contiguous empty area > 35% of the frame height).

python3 tools/density.py frame1.png [frame2.png ...]   -> one JSON line per frame

A row is EMPTY when it is a single flat colour (every pixel within 24 of the row median, summed over
RGB) and that colour matches the rows 8px above and below — so a 4px full-bleed line or a field edge
counts as an object, while a flat ground (Ink, Paper, Navy, or either half of a split) counts as
empty. Reports the largest contiguous run of empty rows in px and % of the frame height.
"""
import json
import sys

import numpy as np
from PIL import Image

TOL = 24
for path in sys.argv[1:]:
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    h = a.shape[0]
    med = np.median(a, axis=1)                                   # (h, 3) row median colour
    flat = np.abs(a - med[:, None, :]).sum(axis=2).max(axis=1) < TOL
    up = np.r_[np.full(8, True), np.abs(med[8:] - med[:-8]).sum(axis=1) < TOL]
    dn = np.r_[np.abs(med[:-8] - med[8:]).sum(axis=1) < TOL, np.full(8, True)]
    empty = flat & up & dn
    best, cur, start, best_start = 0, 0, 0, 0
    for y in range(h):
        if empty[y]:
            if cur == 0:
                start = y
            cur += 1
            if cur > best:
                best, best_start = cur, start
        else:
            cur = 0
    print(json.dumps({"file": path, "band_px": int(best), "band_pct": round(100 * best / h, 1),
                      "band_from": int(best_start), "band_to": int(best_start + best), "empty_rows_pct": round(100 * empty.mean(), 1)}))
