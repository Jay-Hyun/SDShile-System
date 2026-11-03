#!/usr/bin/env python3
"""라벨 붙은 정지 화면 시트. Usage: python3 tools/contact_sheet.py <snapshot-dir> <out-prefix> "t:label,t:label,..." [cols]
label = settled | transition (+ 메모). 한 장에 cols×2 칸, 칸마다 '시각 · 라벨'."""
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

d, out, spec = sys.argv[1], sys.argv[2], sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 5
labels = {}
for item in spec.split(","):
    t, lab = item.split(":", 1)
    labels[float(t)] = lab
files = {}
for f in glob.glob(os.path.join(d, "frame-*-at-*s.png")):
    t = float(re.search(r"at-([\d.]+)s", f).group(1))
    files[t] = f
times = sorted(t for t in files if t in labels)
W, H = 324, 576
font = None
for cand in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
    if os.path.exists(cand):
        font = ImageFont.truetype(cand, 22)
font = font or ImageFont.load_default()
rows = 2
per = cols * rows
for si in range(0, len(times), per):
    chunk = times[si:si + per]
    sheet = Image.new("RGB", (cols * (W + 8) + 8, rows * (H + 40) + 8), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    for i, t in enumerate(chunk):
        x, y = 8 + (i % cols) * (W + 8), 8 + (i // cols) * (H + 40)
        sheet.paste(Image.open(files[t]).convert("RGB").resize((W, H)), (x, y + 32))
        lab = labels[t]
        col = (120, 220, 120) if lab.startswith("settled") else (240, 190, 90)
        dr.text((x, y + 4), f"{t:.2f}s  {lab}", fill=col, font=font)
    p = f"{out}-{si // per + 1}.jpg"
    sheet.save(p, quality=88)
    print(p)
