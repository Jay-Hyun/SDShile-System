#!/usr/bin/env python3
"""Geometry for knockout type: centre a word on 1920x1080 and find the deepest point inside its strokes.

The zoom-through transition scales the knockout around that point, so the frame lands inside a stroke
(fully open onto the media). Same font file and no kerning on both sides, so the browser matches.
Usage: python scripts/knock_points.py "사랑할" assets/fonts/NotoSerifKR-VF.ttf 800 600 [preview.png] [near-x,near-y]
"""
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

text, path, weight, size = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)
try:
    f.set_variation_by_axes([weight])
except Exception:
    pass
adv = f.getlength(text)
l, t, r, b = f.getbbox(text, anchor="ls")
x0 = 960 - adv / 2
base = 540 - (t + b) / 2
im = Image.new("L", (1920, 1080), 0)
ImageDraw.Draw(im).text((x0, base), text, font=f, fill=255, anchor="ls")
m = np.asarray(im)
dist = cv2.distanceTransform((m > 128).astype(np.uint8), cv2.DIST_L2, 5)
if len(sys.argv) > 6:  # optional "x,y": the deepest point near there (pick which stroke to fly into)
    nx, ny = map(int, sys.argv[6].split(","))
    yy, xx = np.mgrid[0:1080, 0:1920]
    dist = dist * (((xx - nx) ** 2 + (yy - ny) ** 2) < 220 ** 2)
y, x = np.unravel_index(np.argmax(dist), dist.shape)
print(f'{{"x": {x0:.1f}, "baseline": {base:.1f}, "advance": {adv:.1f}, "deep": [{x}, {y}], "radius": {dist.max():.1f}, "bbox": [{x0 + l:.0f}, {base + t:.0f}, {x0 + r:.0f}, {base + b:.0f}]}}')
if len(sys.argv) > 5:
    cv2.imwrite(sys.argv[5], cv2.circle(cv2.cvtColor(m, cv2.COLOR_GRAY2BGR), (int(x), int(y)), int(dist.max()), (0, 0, 255), 3))
