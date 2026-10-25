#!/usr/bin/env python3
"""Key out the chroma-green compositing areas of generated plates (picture frames, mirror, TV, phone).

For every item in data/gen_v5.json with a "green" field:
  assets/media/gen5/<id>_keyed.png   plate with transparent holes where the green was (edge-feathered, despilled)
  data/green_rects.json              {id: {W, H, holes: [{x, y, w, h}, ...]}} hole boxes in source pixels, left to right
  assets/js/green.js                 the same as window.GREEN for the compositions
Real footage is placed under each hole in HTML, so the frame's own shape (oval mirror, rounded screen) masks it.
A plate whose "green" mentions "every" keeps every sizeable hole; otherwise only the largest one. Rounded screens
get their quad from lines fitted to the straight edges; "media_aspect" (w / h of the real screen) extends the quad
under whatever hides the bottom of the screen (a phone in its stand).

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


def edge_quad(comp):
    """Corners of a rounded-corner screen (a phone, a TV): straight lines fitted to the middle of each edge and
    intersected, so the picture's corners sit under the rounded glass like a real display. None unless the area
    fills that quad like a rounded rectangle does (an oval would not)."""
    ys, xs = np.nonzero(comp)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()

    def fit(pts):
        vx, vy, cx, cy = cv2.fitLine(np.array(pts, np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        return np.array([cx, cy]), np.array([vx, vy])

    rows = range(int(y0 + 0.2 * (y1 - y0)), int(y1 - 0.2 * (y1 - y0)))
    cols = range(int(x0 + 0.25 * (x1 - x0)), int(x1 - 0.25 * (x1 - x0)))
    left = fit([(np.flatnonzero(comp[y])[0], y) for y in rows])
    right = fit([(np.flatnonzero(comp[y])[-1], y) for y in rows])
    top = fit([(x, np.flatnonzero(comp[:, x])[0]) for x in cols])
    bottom = fit([(x, np.flatnonzero(comp[:, x])[-1]) for x in cols])

    def meet(a, b):
        (p, u), (q, v) = a, b
        t = np.linalg.solve(np.array([u, -v]).T, q - p)
        return p + t[0] * u

    quad = np.array([meet(top, left), meet(top, right), meet(bottom, right), meet(bottom, left)], np.float32)
    if not 0.95 <= float(comp.sum()) / cv2.contourArea(quad) <= 1.01:
        return None
    return [[round(float(p[0]), 1), round(float(p[1]), 1)] for p in quad]


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
        quad = frame_quad(comp) or edge_quad(comp)
        asp = it.get("media_aspect")  # w / h of the real screen (a phone in a stand shows less than all of it)
        if quad is not None and asp:
            q = np.array(quad, float)
            w = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
            h = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
            if w / asp > h + 1:  # the bottom of the screen is hidden: continue the quad behind what covers it
                k = (w / asp) / h
                q[3] = q[0] + (q[3] - q[0]) * k
                q[2] = q[1] + (q[2] - q[1]) * k
                quad = [[round(float(x), 1), round(float(y), 1)] for x, y in q]
        if quad is not None:
            hole["quad"] = quad
        holes.append(hole)
    holes.sort(key=lambda d: d["x"])
    rects[it["id"]] = {"W": int(W), "H": int(H), "holes": holes}
    print(it["id"], holes)

json.dump(rects, open(rects_path, "w"), indent=1)
open("assets/js/green.js", "w").write("window.GREEN = " + json.dumps(rects) + ";\n")
