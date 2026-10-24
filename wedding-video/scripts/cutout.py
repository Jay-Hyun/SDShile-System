#!/usr/bin/env python3
"""Cut the couple out of hero photos (transparent PNG) for the subject-sandwich shots.

Usage: /opt/mediaenv/bin/python scripts/cutout.py [model] key1 key2 ...
Keys come from data/photos.json (w00, d12, ...). Output: assets/media/cutout/<key>.png,
long edge 2000 px, alpha refined with alpha matting off (studio backdrops are clean).
"""
import json
import os
import sys

from PIL import Image
from rembg import new_session, remove

model = "birefnet-portrait"
keys = sys.argv[1:]
if keys and not keys[0][0] in "wdx":
    model, keys = keys[0], keys[1:]

photos = json.load(open("data/photos.json"))
os.makedirs("assets/media/cutout", exist_ok=True)
session = new_session(model)
for k in keys:
    out = f"assets/media/cutout/{k}.png"
    if os.path.exists(out):
        continue
    img = Image.open(photos[k]).convert("RGB")
    img.thumbnail((2000, 2000), Image.LANCZOS)
    cut = remove(img, session=session, post_process_mask=True)
    bbox = cut.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    cut.save(out, optimize=True)
    print(f"{k} -> {out} {cut.size} bbox={bbox}", flush=True)
