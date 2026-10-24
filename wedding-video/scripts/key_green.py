#!/usr/bin/env python3
"""Key out the chroma-green compositing areas of generated plates (picture frames, mirror, TV, phone).

For every item in data/gen_v5.json with a "green" field:
  assets/media/gen5/<id>_keyed.png   plate with transparent holes where the green was (edge-feathered, despilled)
  data/green_rects.json              {id: {W, H, holes: [{x, y, w, h}, ...]}} hole boxes in source pixels, left to right
  assets/js/green.js                 the same as window.GREEN for the compositions
Real footage is placed under each hole in HTML, so the frame's own shape (oval mirror, rounded screen) masks it.
A plate whose "green" mentions "every" keeps every sizeable hole; otherwise only the largest one.

Usage: /opt/mediaenv/bin/python scripts/key_green.py [ids...]
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

M = json.load(open("data/gen_v5.json"))
OUT = M["out"]
ids = sys.argv[1:]
rects_path = "data/green_rects.json"
rects = json.load(open(rects_path)) if os.path.exists(rects_path) else {}

def frame_quad(comp):
    """Four corners (TL, TR, BR, BL) of a straight-edged picture area, or None for an oval/irregular one.
    The picture is warped onto this quad so it lies in the plane of the frame (perspective-correct)."""
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(cnt)
    if cv2.contourArea(hull) == 0:
        return None
    # a quad-shaped area fills its hull; an ellipse fills ~0.79 of its quad hull
    peri = cv2.arcLength(hull, True)
    ap = None
    for eps in np.linspace(0.005, 0.08, 60):
        a = cv2.approxPolyDP(hull, eps * peri, True)
        if len(a) == 4:
            ap = a.reshape(4, 2).astype(float)
            break
    if ap is None or not 0.93 <= cv2.contourArea(cnt) / cv2.contourArea(ap.astype(np.float32)) <= 1.08:
        return None
    s = ap.sum(1)
    d = ap[:, 1] - ap[:, 0]
    tl, br, tr, bl = ap[np.argmin(s)], ap[np.argmax(s)], ap[np.argmin(d)], ap[np.argmax(d)]
    return [[round(float(p[0]), 1), round(float(p[1]), 1)] for p in (tl, tr, br, bl)]


for it in M["items"]:
    if not it.get("green") or (ids and it["id"] not in ids):
        continue
    src = f"{OUT}/{it['id']}.png"
    if not os.path.exists(src):
        print(it["id"], "missing")
        continue
    rgb = np.asarray(Image.open(src).convert("RGB")).astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    greenness = g - np.maximum(r, b)
    hard = ((greenness > 60) & (g > 120)).astype(np.uint8)
    hard = cv2.morphologyEx(hard, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(hard)
    if n < 2:
        print(it["id"], "no green found")
        continue
    H, W = hard.shape
    areas = stats[1:, cv2.CC_STAT_AREA]
    if "every" in it["green"]:
        keep = [1 + j for j in range(n - 1) if areas[j] >= 0.0008 * W * H]
    else:
        keep = [1 + int(np.argmax(areas))]
    region = np.isin(lab, keep).astype(np.uint8)
    region = cv2.morphologyEx(region, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # grow 2 px so the anti-aliased green rim goes too, then feather
    grown = cv2.dilate(region, np.ones((5, 5), np.uint8))
    alpha = 1.0 - cv2.GaussianBlur(grown.astype(np.float32), (0, 0), 1.2)
    # despill: pull green down to max(r, b) near the holes
    near = cv2.dilate(grown, np.ones((15, 15), np.uint8)).astype(bool)
    out = rgb.copy()
    spill = near & (g > np.maximum(r, b))
    out[..., 1][spill] = np.maximum(r, b)[spill]
    rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), (np.clip(alpha, 0, 1) * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(f"{OUT}/{it['id']}_keyed.png", optimize=True)
    holes = []
    for k in keep:
        comp = (lab == k).astype(np.uint8)
        x, y, w, h = cv2.boundingRect(comp)
        hole = {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "fill": round(float(comp.sum()) / (w * h), 2)}
        quad = frame_quad(comp)
        if quad is not None:
            hole["quad"] = quad
        holes.append(hole)
    holes.sort(key=lambda d: d["x"])
    rects[it["id"]] = {"W": int(W), "H": int(H), "holes": holes}
    print(it["id"], holes)

json.dump(rects, open(rects_path, "w"), indent=1)
open("assets/js/green.js", "w").write("window.GREEN = " + json.dumps(rects) + ";\n")
