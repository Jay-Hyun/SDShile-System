"""Subset Pretendard GOV Variable to the glyphs this project uses.

Usage: python3 tools/subset_font.py [path/to/PretendardGOVVariable.woff2]
  (default source: $PRETENDARD_GOV or ../_shared/fonts/PretendardGOVVariable.woff2)
Collects every character in index.html, compositions/*.html and v15/compositions/*.html (copy, code, digits for
the 0→60 counter) and writes assets/fonts/PretendardGOV-subset.woff2 with the wght axis kept.
The emoji 🙂 is drawn as inline SVG, so it is not in the font.
Re-run after changing any on-screen copy.
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PRETENDARD_GOV")
       or os.path.join(ROOT, "..", "_shared", "fonts", "PretendardGOVVariable.woff2"))
files = [os.path.join(ROOT, "index.html")] + sorted(glob.glob(os.path.join(ROOT, "compositions", "*.html"))) + sorted(glob.glob(os.path.join(ROOT, "v15", "compositions", "*.html")))
chars = set()
for f in files:
    chars |= set(open(f, encoding="utf-8").read())
chars |= set(" 0123456789…·–※*:'%(),.?!「」")
chars = {c for c in chars if c.isprintable() and ord(c) < 0x1F000}
text = "".join(sorted(chars))
out = os.path.join(ROOT, "assets", "fonts", "PretendardGOV-subset.woff2")
subprocess.run([sys.executable, "-m", "fontTools.subset", src, "--text=" + text, "--flavor=woff2",
                "--layout-features=*", "--output-file=" + out], check=True)
print(f"{len(chars)} chars ({sum(1 for c in chars if '가' <= c <= '힣')} hangul) -> {out} ({os.path.getsize(out)} bytes)")
