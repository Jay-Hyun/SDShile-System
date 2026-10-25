#!/usr/bin/env python3
"""Regenerate the lyric tint gradient (#tint-ramp in index.html).

The tint is painted into the chroma green, so what the audience sees is what a
keyer keeps of it. The gradient is therefore designed backwards: pick the
darkness wanted after keying at each height, then invert the keyer to find the
pixel to paint there.

Keyer model: OBS chroma key (v2 shader) at its defaults -- key colour green,
Similarity 400, Smoothness 80, Spill reduction 100. Other Similarity values
shift the result a lot (420 roughly halves the tint, 380 nearly doubles it),
and other keyers (vMix, hardware switchers) use other maths.

    python3 tools/build_tint.py
"""
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SIMILARITY = 0.40
SMOOTHNESS = 0.08
END = (19, 5, 19)  # leans magenta so the kept part desaturates to a neutral dark
RAMP_TOP, RAMP_BOTTOM, STEP = 580, 1080, 20  # matches #tint-ramp top/height

CB = (-0.100644, -0.338572, 0.439216, 0.501961)
CR = (0.439216, -0.398942, -0.040274, 0.501961)


def chroma(rgb):
    return (
        sum(c * k for c, k in zip(rgb, CB[:3])) + CB[3],
        sum(c * k for c, k in zip(rgb, CR[:3])) + CR[3],
    )


KEY = chroma((0.0, 1.0, 0.0))


def keyed_alpha(a):
    """Alpha the keyer gives a pixel of END painted at opacity a over green."""
    px = tuple(g * (1 - a) + e / 255 * a for g, e in zip((0.0, 1.0, 0.0), END))
    cb, cr = chroma(px)
    base = math.hypot(cb - KEY[0], cr - KEY[1]) - SIMILARITY
    return min(max(base / SMOOTHNESS, 0.0), 1.0) ** 1.5


def paint_for(target):
    """Smallest paint opacity whose keyed alpha reaches target (keyed alpha rises with a)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if keyed_alpha(mid) < target:
            lo = mid
        else:
            hi = mid
    return hi


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def target(y):
    """Darkness wanted after keying: clear above y 800, 35% by y 960, 40% at the bottom."""
    if y < 800:
        return 0.0
    if y < 960:
        return 0.35 * smoothstep((y - 800) / 160)
    return 0.35 + 0.05 * (y - 960) / (RAMP_BOTTOM - 960)


threshold = paint_for(1e-6)  # the most paint the keyer still removes completely
stops = []
for y in range(RAMP_TOP, RAMP_BOTTOM + 1, STEP):
    if y < 800:
        # ease the paint up to the threshold so the green preview has no visible step
        a = threshold * smoothstep((y - RAMP_TOP) / (800 - RAMP_TOP))
    else:
        a = paint_for(target(y)) if target(y) > 0 else threshold
    pct = round((y - RAMP_TOP) / (RAMP_BOTTOM - RAMP_TOP) * 100, 1)
    stops.append(f"rgba({END[0]}, {END[1]}, {END[2]}, {a:.3f}) {pct:g}%")

css = "background: linear-gradient(to bottom, " + ", ".join(stops) + ");"
index = ROOT / "index.html"
html, n = re.subn(r"(#tint-ramp \{.*?)background: linear-gradient\(.*?\);", lambda m: m.group(1) + css, index.read_text(encoding="utf-8"), count=1, flags=re.S)
if n != 1:
    raise SystemExit("could not find the #tint-ramp background in index.html")
index.write_text(html, encoding="utf-8")
print(f"wrote {len(stops)} stops; keyer removes paint below {threshold:.3f}")
for y in (800, 860, 900, 960, 1080):
    a = paint_for(target(y)) if target(y) > 0 else threshold
    print(f"  y {y}: paint {a:.3f} -> keyed {keyed_alpha(a):.2f}")
