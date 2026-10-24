#!/usr/bin/env python3
"""Seeded grain and paper textures (assets/media/tex). Run with the media venv."""
import os

import numpy as np
from PIL import Image, ImageFilter

os.makedirs("assets/media/tex", exist_ok=True)
rng = np.random.default_rng(7)
n = rng.normal(128, 38, (1024, 1024)).clip(0, 255).astype(np.uint8)
Image.fromarray(n, "L").save("assets/media/tex/grain.png", optimize=True)
base = rng.normal(0, 1, (512, 512))
blot = np.array(Image.fromarray(((base - base.min()) / np.ptp(base) * 255).astype(np.uint8))
                .resize((2048, 2048), Image.BICUBIC).filter(ImageFilter.GaussianBlur(18)), float)
fib = rng.normal(0, 1, (2048, 2048))
fib = np.array(Image.fromarray(((fib - fib.min()) / np.ptp(fib) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(1)), float)
v = (blot - blot.mean()) * 0.5 + (fib - fib.mean()) * 0.35 + 128
Image.fromarray(v.clip(0, 255).astype(np.uint8), "L").save("assets/media/tex/paper.png", optimize=True)
print("textures ready")
