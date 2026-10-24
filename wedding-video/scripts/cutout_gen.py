#!/usr/bin/env python3
"""Cut out generated subjects (items with "alpha": true) -> assets/media/gen/cut/<id>.png, trimmed to content.

If GPT already delivered real transparency it is kept; otherwise rembg (isnet-general-use) removes the flat ground.
Usage: /opt/mediaenv/bin/python scripts/cutout_gen.py [ids...]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

M = json.load(open("data/gen_assets.json"))
ids = sys.argv[1:]
os.makedirs("assets/media/gen/cut", exist_ok=True)
session = None
for it in M["items"]:
    if not it["alpha"] or (ids and it["id"] not in ids):
        continue
    src, dst = f"assets/media/gen/{it['id']}.png", f"assets/media/gen/cut/{it['id']}.png"
    if not os.path.exists(src) or (os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(src)):
        continue
    im = Image.open(src).convert("RGBA")
    a = np.asarray(im)[..., 3]
    if (a < 250).mean() < 0.05:  # no real transparency: remove the flat ground
        if session is None:
            from rembg import new_session
            session = new_session("isnet-general-use")
        from rembg import remove
        im = remove(im.convert("RGB"), session=session, post_process_mask=True)
    bbox = im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
    if bbox:
        pad = 12
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    im.save(dst, optimize=True)
    print(it["id"], "->", dst, im.size, flush=True)
