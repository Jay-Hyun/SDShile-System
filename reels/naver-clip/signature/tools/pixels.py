"""Pixel audits for v7 (04-v7-visual.md §6 b, e).

python3 tools/pixels.py frame.png frame-goldpaint.png  -> JSON line
  dark_pct : share of pixels with luma (Rec.709) < 25%  (night-look guard: <= 40% before the end card)
  gold_pct : share of pixels that change to magenta when every [data-gold] element is repainted #FF00FF
             (so photo wood/stone tones never count as gold)
"""
import json
import sys

import numpy as np
from PIL import Image

a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.float32)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.float32)
luma = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
changed = (np.abs(a - b).sum(axis=2) > 60) & (b[..., 0] > 150) & (b[..., 2] > 150) & (b[..., 1] < 120)
print(json.dumps({"dark_pct": round(100 * float((luma < 0.25 * 255).mean()), 1), "gold_pct": round(100 * float(changed.mean()), 2)}))
