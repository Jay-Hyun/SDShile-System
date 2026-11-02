"""Subset Pretendard GOV Variable to the glyphs this project uses.

Usage: python3 tools/subset_font.py [path/to/PretendardGOVVariable.woff2]
Default source: $PRETENDARD_GOV (the 5MB full font is not committed).
Collects every character in index.html + compositions/*.html (+ printable ASCII).
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PRETENDARD_GOV", "")
if not src or not os.path.exists(src):
    sys.exit("full font not found: pass the path or set PRETENDARD_GOV")
chars = set(chr(c) for c in range(0x20, 0x7F))
for f in [os.path.join(ROOT, "index.html")] + glob.glob(os.path.join(ROOT, "compositions", "*.html")):
    chars |= set(open(f, encoding="utf-8").read())
chars = "".join(sorted(c for c in chars if ord(c) >= 0x20))
txt = os.path.join(ROOT, "assets", "fonts", ".subset-chars.txt")
open(txt, "w", encoding="utf-8").write(chars)
out = os.path.join(ROOT, "assets", "fonts", "PretendardGOV-subset.woff2")
subprocess.run([sys.executable, "-m", "fontTools.subset", src, f"--text-file={txt}", "--flavor=woff2",
                f"--output-file={out}", "--layout-features=*", "--no-hinting"], check=True)
os.remove(txt)
print(out, os.path.getsize(out), "bytes,", len(chars), "chars")
