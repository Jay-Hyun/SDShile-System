#!/usr/bin/env python3
"""Turn a still into a short 2.5D "living photo" clip: a real camera move through the picture.

Depth comes from Depth Anything V2 (small, ONNX, CPU). When a cutout of the couple exists
(assets/media/cutout/<key>.png) the subject is a rigid layer at its own depth and the plate
behind it is inpainted, so edges never rubber-sheet; otherwise the whole frame is warped by depth.

Usage:
  /opt/mediaenv/bin/python scripts/living_photo.py <key> <out-name> [--size 1920x1080]
      [--dur 4] [--move push|pull|left|right|up|down|push-left|push-right|pull-up]
      [--amount 1.0] [--focus 0.5,0.4] [--zoom 1.0] [--dof 1.0]
Output: assets/media/living/<out-name>.mp4 (H.264, 30 fps, GOP 10, no audio)
"""
import argparse
import json
import os
import subprocess

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL = "/opt/models/da2s.onnx"
FPS = 30

ap = argparse.ArgumentParser()
ap.add_argument("key", help="photos.json key, gen:<id> (assets/media/gen/<id>.png), or a path to any .png")
ap.add_argument("name")
ap.add_argument("--size", default="1920x1080")
ap.add_argument("--dur", type=float, default=4.0)
ap.add_argument("--move", default="push")
ap.add_argument("--amount", type=float, default=1.0)
ap.add_argument("--focus", default="0.5,0.42")
ap.add_argument("--zoom", type=float, default=1.0, help="extra framing zoom on top of cover")
ap.add_argument("--dof", type=float, default=1.0)
ap.add_argument("--ease", default="inout", help="inout | linear | out")
ap.add_argument("--layers", action="store_true", help="also write the subject alone as <name>_fg.webm (VP9 alpha) and the plate as <name>_bg.mp4")
a = ap.parse_args()

W, H = map(int, a.size.split("x"))
fx, fy = map(float, a.focus.split(","))
photos = json.load(open("data/photos.json"))
if a.key.endswith(".png"):
    src_path = a.key  # any image path (v5 plates: assets/media/gen5/<id>.png)
elif a.key.startswith("gen:"):
    src_path = f"assets/media/gen/{a.key[4:]}.png"
else:
    src_path = photos[a.key]
src = np.asarray(Image.open(src_path).convert("RGB")).astype(np.float32) / 255.0
ih, iw = src.shape[:2]


def depth_of(img):
    """Relative disparity in [0,1] (1 = nearest) at image resolution."""
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    long = 518
    s = long / max(img.shape[:2])
    h14 = max(14, int(round(img.shape[0] * s / 14)) * 14)
    w14 = max(14, int(round(img.shape[1] * s / 14)) * 14)
    x = cv2.resize(img, (w14, h14), interpolation=cv2.INTER_AREA)
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    d = sess.run(None, {"pixel_values": x})[0][0]
    d = cv2.resize(d, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    return cv2.GaussianBlur(d, (0, 0), 3)


def inpaint(img, mask, small=640):
    """Fill mask from its surroundings (soft, low-frequency fill: it sits behind the subject)."""
    s = small / max(img.shape[:2])
    sm = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    mm = (cv2.resize(mask.astype(np.uint8) * 255, (sm.shape[1], sm.shape[0])) > 0).astype(np.uint8) * 255
    mm = cv2.dilate(mm, np.ones((5, 5), np.uint8))
    if sm.ndim == 2:
        f = cv2.inpaint((sm * 255).astype(np.uint8), mm, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    else:
        f = cv2.inpaint((sm * 255).astype(np.uint8), mm, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    f = cv2.GaussianBlur(f, (0, 0), 4)
    f = cv2.resize(f, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 6)
    if img.ndim == 3:
        m = m[..., None]
    return img * (1 - m) + f * m


depth = depth_of(src)
cut_path = f"assets/media/cutout/{a.key}.png"  # generated plates have no separate subject layer
fg = None
if os.path.exists(cut_path):
    c = Image.open(cut_path).convert("RGBA").resize((iw, ih), Image.LANCZOS)
    fg = np.asarray(c).astype(np.float32) / 255.0
    alpha = fg[..., 3]
    hard = alpha > 0.08
    ds = float(np.median(depth[alpha > 0.5])) if (alpha > 0.5).any() else 0.8
    grow = cv2.dilate(hard.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    bg = inpaint(src, grow)
    bgd = inpaint(depth, grow)
    # keep the plate behind the subject at most as near as the subject itself
    bgd = np.minimum(bgd, ds)
else:
    bg, bgd = src, depth
    ds = float(np.percentile(depth, 85))

# depth of field: the plate softens with distance behind the subject's plane
if a.dof > 0:
    soft = cv2.GaussianBlur(bg, (0, 0), 2.2 * a.dof * iw / 2560)
    softer = cv2.GaussianBlur(bg, (0, 0), 5.0 * a.dof * iw / 2560)
    k = np.clip((ds - bgd) * 2.2, 0, 1)[..., None]
    bg = np.where(k < 0.5, bg * (1 - 2 * k) + soft * 2 * k, soft * (2 - 2 * k) + softer * (2 * k - 1))

# disparity -> parallax weight: far things still move a little
par = 0.12 + 0.88 * bgd
pars = 0.12 + 0.88 * ds

# framing: cover W x H, then extra zoom; focus point picks the crop centre
S = max(W / iw, H / ih) * 1.06 * a.zoom  # out px per image px (6 % overscan for the move)
cx = float(np.clip(fx * iw, W / 2 / S, iw - W / 2 / S))
cy = float(np.clip(fy * ih, H / 2 / S, ih - H / 2 / S))
S = float(S)

A = a.amount
moves = {
    # (dolly, truck x px, truck y px) at the end of the clip, in output pixels at parallax 1
    "push": (0.16, 0, 0),
    "pull": (-0.14, 0, 0),
    "left": (0.03, 90, 0),
    "right": (0.03, -90, 0),
    "up": (0.03, 0, 70),
    "down": (0.03, 0, -70),
    "push-left": (0.12, 70, 0),
    "push-right": (0.12, -70, 0),
    "pull-up": (-0.1, 0, 60),
}
D_END, TX_END, TY_END = (m * A for m in moves[a.move])
start_back = a.move.startswith("pull")

uu, vv = np.meshgrid(np.arange(W, dtype=np.float32) - W / 2, np.arange(H, dtype=np.float32) - H / 2)
dsm = cv2.resize(par.astype(np.float32), (iw // 4, ih // 4), interpolation=cv2.INTER_AREA)


def ease(t):
    if a.ease == "linear":
        return t
    if a.ease == "out":
        return 1 - (1 - t) ** 3
    return t * t * (3 - 2 * t)


os.makedirs("assets/media/living", exist_ok=True)
out = f"assets/media/living/{a.name}.mp4"
enc = subprocess.Popen(
    ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "10", "-bf", "0", "-pix_fmt", "yuv420p",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", out],
    stdin=subprocess.PIPE)

layers = a.layers and fg is not None
encs = [enc]
if layers:
    enc_bg = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "10", "-bf", "0", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart",
         f"assets/media/living/{a.name}_bg.mp4"], stdin=subprocess.PIPE)
    enc_fg = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "22", "-row-mt", "1", "-deadline", "good",
         "-cpu-used", "4", "-g", "10", "-auto-alt-ref", "0", f"assets/media/living/{a.name}_fg.webm"], stdin=subprocess.PIPE)
    encs += [enc_bg, enc_fg]
bg8 = np.clip(bg * 255, 0, 255).astype(np.uint8)
fg8 = np.clip(fg * 255, 0, 255).astype(np.uint8) if fg is not None else None
n = int(round(a.dur * FPS))
for i in range(n):
    e = ease(i / max(n - 1, 1))
    # a pull starts pushed in and opens up to the base framing, so the overscan always covers
    dol = -D_END * (1 - e) if start_back else D_END * e
    tx, ty = TX_END * (e - 0.5), TY_END * (e - 0.5)
    # plate: fixed-point solve for the source pixel given its own depth
    x, y = uu.copy(), vv.copy()
    for _ in range(3):
        px = (cx + x / S).astype(np.float32)
        py = (cy + y / S).astype(np.float32)
        d = cv2.remap(dsm, px / 4, py / 4, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        x = uu * (1 - dol * d) + tx * d
        y = vv * (1 - dol * d) + ty * d
    frame = cv2.remap(bg8, (cx + x / S).astype(np.float32), (cy + y / S).astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if layers:
        enc_bg.stdin.write(frame.tobytes())
    if fg8 is not None:
        xs = uu * (1 - dol * pars) + tx * pars
        ys = vv * (1 - dol * pars) + ty * pars
        f = cv2.remap(fg8, (cx + xs / S).astype(np.float32), (cy + ys / S).astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        al = f[..., 3:4].astype(np.float32) / 255
        frame = (frame.astype(np.float32) * (1 - al) + f[..., :3].astype(np.float32) * al).astype(np.uint8)
        if layers:
            enc_fg.stdin.write(np.ascontiguousarray(f).tobytes())
    enc.stdin.write(frame.tobytes())
for e in encs:
    e.stdin.close()
    e.wait()
print(f"{a.key} -> {out} {W}x{H} {a.dur}s move={a.move} subject={'cutout' if fg is not None else 'depth'} ds={ds:.2f}")
