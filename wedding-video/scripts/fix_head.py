#!/usr/bin/env python3
"""Shrink one character's head on a generated plate with a smooth local warp (no regeneration, so the face,
lighting and set stay exactly as approved).

Inside the head ellipse the person is minified by `scale` toward `anchor`, fading to identity over `ramp` px so the
neck and shoulders follow smoothly. Only the person is taken from the warp (BiRefNet silhouette, warped the same
way): every background pixel comes from the original, and the thin band the head no longer covers is inpainted
from the wall around it, so background lines stay perfectly straight. Pixels left of `keep_x` (a hard structure
such as the partition wall) are never moved. The original is kept as <id>_orig.png.

Usage: /opt/mediaenv/bin/python scripts/fix_head.py <id> cx,cy,rx,ry ax,ay scale [--ramp 70] [--keep-x 0]
"""
import argparse
import os
import shutil

import cv2
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("id")
ap.add_argument("ellipse")
ap.add_argument("anchor")
ap.add_argument("scale", type=float)
ap.add_argument("--ramp", type=float, default=70)
ap.add_argument("--keep-x", type=float, default=0)
ap.add_argument("--keep-right", action="store_true", help="protect the side right of keep-x instead of left")
ap.add_argument("--vfill", default="0,99999", help="x range where the wall is filled column by column (vertical mouldings)")
a = ap.parse_args()

path = f"assets/media/gen5/{a.id}.png"
orig = f"assets/media/gen5/{a.id}_orig.png"
if not os.path.exists(orig):
    shutil.copy(path, orig)
src = np.asarray(Image.open(orig).convert("RGB"))
H, W = src.shape[:2]
cx, cy, rx, ry = map(float, a.ellipse.split(","))
ax, ay = map(float, a.anchor.split(","))

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
dist = (r - 1.0) * np.minimum(rx, ry)  # px outside the head ellipse (approx.)
t = np.clip(dist / a.ramp, 0, 1)
w = 1 - (t * t * (3 - 2 * t))  # smoothstep falloff: 1 inside, 0 beyond the ramp
if a.keep_x:
    edge = np.clip((xx - a.keep_x) / 6.0, 0, 1) if not a.keep_right else np.clip((a.keep_x - xx) / 6.0, 0, 1)
    w = w * edge
k = (1.0 / a.scale - 1.0) * w
mapx = (ax + (xx - ax) * (1 + k)).astype(np.float32)
mapy = (ay + (yy - ay) * (1 + k)).astype(np.float32)
warped = cv2.remap(src, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# person alpha before and after the warp; background = original, with the uncovered band inpainted
from rembg import new_session, remove

alpha = np.asarray(remove(Image.fromarray(src), session=new_session("birefnet-portrait"), only_mask=True)).astype(np.float32) / 255
alpha_new = cv2.remap(alpha, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
# rebuild the wall under the whole original head (only true background borders the hole), the new head covers most of it
near = r <= 1.0 + (a.ramp + 20) / np.minimum(rx, ry)
hole = ((cv2.dilate((alpha > 0.05).astype(np.uint8), np.ones((11, 11), np.uint8)) > 0) & near).astype(np.uint8)
if a.keep_x:
    hole[:, : int(a.keep_x)] = 0
# the wall here is vertical (mouldings, panel seams): fill every column straight down from the wall above it,
# blending toward the wall below when the hole ends on background, so vertical lines continue unbroken
smooth = cv2.inpaint(src, hole * 255, 15, cv2.INPAINT_TELEA).astype(np.float32)
bg = src.astype(np.float32).copy()
bgmask = alpha < 0.05
vx0, vx1 = map(int, a.vfill.split(","))
for x in range(W):
    if not (vx0 <= x <= vx1):
        bg[hole[:, x] > 0, x] = smooth[hole[:, x] > 0, x]
        continue
    col = hole[:, x]
    if not col.any():
        continue
    ys = np.flatnonzero(col)
    starts = ys[np.r_[True, np.diff(ys) > 1]]
    ends = ys[np.r_[np.diff(ys) > 1, True]]
    for y0, y1 in zip(starts, ends):
        top = bg[max(y0 - 1, 0), x]
        below = y1 + 1 < H and bgmask[y1 + 1, x]
        if below:
            bot = bg[y1 + 1, x]
            f = np.linspace(0, 1, y1 - y0 + 3)[1:-1, None]
            bg[y0:y1 + 1, x] = top * (1 - f) + bot * f
        else:
            bg[y0:y1 + 1, x] = top
bg = np.clip(bg, 0, 255).astype(np.uint8)
an = cv2.GaussianBlur(alpha_new, (0, 0), 0.8)[..., None]
out = np.clip(warped * an + bg * (1 - an), 0, 255).astype(np.uint8)
Image.fromarray(out).save(path)
print(f"{a.id}: head {a.ellipse} scaled {a.scale} toward {a.anchor}")
