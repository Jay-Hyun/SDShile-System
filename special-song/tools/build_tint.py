#!/usr/bin/env python3
"""Regenerate the lyric tint: the #tint-ramp gradient in index.html and the
matching transparent overlay extras/tint_overlay.png.

The tint is a light black fade: faint at the bottom edge of the frame, fading
out upward and gone by the middle of the lyric glyphs.

It is drawn into the green video so the file looks right on its own. A chroma
keyer, though, removes everything this green-ish, so after keying that copy of
the tint is gone (the script prints what an OBS key at its defaults keeps).
To see the tint on air, put extras/tint_overlay.png above the camera and below
the keyed lyric video: it is the same fade on a transparent background.

    python3 tools/build_tint.py
"""
import math
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH, HEIGHT = 1920, 1080
TINT_TOP = 917  # middle of the lyric glyphs (measured rows 875-960): fully faded out here
PEAK = 0.35  # opacity of black at the bottom edge
STEP = 8


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def opacity(y):
    """Black opacity at row y: 0 at TINT_TOP, easing to PEAK at the bottom edge."""
    return PEAK * smoothstep((y - TINT_TOP) / (HEIGHT - TINT_TOP))


# --- CSS gradient in the green video ---------------------------------------
stops = []
for y in list(range(TINT_TOP, HEIGHT, STEP)) + [HEIGHT]:
    pct = round((y - TINT_TOP) / (HEIGHT - TINT_TOP) * 100, 1)
    stops.append(f"rgba(0, 0, 0, {opacity(y):.3f}) {pct:g}%")
css = "background: linear-gradient(to bottom, " + ", ".join(stops) + ");"
index = ROOT / "index.html"
html, n = re.subn(
    r"(#tint-ramp \{.*?top: )\d+px;(\s*height: )\d+px;(\s*)background: linear-gradient\(.*?\);",
    lambda m: f"{m.group(1)}{TINT_TOP}px;{m.group(2)}{HEIGHT - TINT_TOP}px;{m.group(3)}{css}",
    index.read_text(encoding="utf-8"),
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("could not find the #tint-ramp block in index.html")
index.write_text(html, encoding="utf-8")


# --- transparent PNG overlay with the same fade ----------------------------
def png(path, rows):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + row for row in rows)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


overlay = ROOT / "extras" / "tint_overlay.png"
overlay.parent.mkdir(exist_ok=True)
png(overlay, [bytes((0, 0, 0, round(opacity(y) * 255))) * WIDTH for y in range(HEIGHT)])


# --- what an OBS chroma key (defaults) keeps of the in-green copy ----------
CB = (-0.100644, -0.338572, 0.439216, 0.501961)
CR = (0.439216, -0.398942, -0.040274, 0.501961)


def chroma(rgb):
    return tuple(sum(c * k for c, k in zip(rgb, v[:3])) + v[3] for v in (CB, CR))


key = chroma((0.0, 1.0, 0.0))
px = (0.0, 1.0 - PEAK, 0.0)  # black at PEAK over green
base = math.dist(chroma(px), key) - 0.40
kept = min(max(base / 0.08, 0.0), 1.0) ** 1.5
print(f"wrote {len(stops)} stops and {overlay.relative_to(ROOT)}")
print(f"bottom edge: {PEAK:.0%} black; an OBS key at defaults keeps {kept:.0%} of the in-green copy")
