#!/usr/bin/env python3
"""Regenerate the lyric tint: the #tint-ramp gradient in index.html, the ATEM
calibration clip (its own small project in extras/tint-calibration/) and the
optional overlay extras/tint_overlay.png.

The tint is painted into the chroma green, so what reaches the audience is what
the keyer keeps of it. Faint dark-over-green is keyed away with the green, so a
tint that survives must be painted strongly; how much of it a keyer keeps
depends on that keyer and its settings. LEVELS holds five strengths. Render
the calibration clip, run it through the same keyer, pick the column that looks
right, set LEVEL to that number, run this script and re-render the film.

    python3 tools/build_tint.py
    cd extras/tint-calibration && npx hyperframes@0.8.192 render -o ../../renders/tint_calibration.mp4
"""
import math
import re
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEVEL = 3
# paint opacity of END over #00FF00: (a0 at the middle of the lyric, L at the bottom edge)
LEVELS = {1: (0.50, 0.75), 2: (0.60, 0.82), 3: (0.68, 0.88), 4: (0.75, 0.93), 5: (0.82, 0.98)}
END = (19, 5, 19)  # leans magenta so the part a keyer keeps comes out a neutral dark
WIDTH, HEIGHT = 1920, 1080
TINT_TOP = 906  # middle of the lyric glyphs at 110 px (measured rows 854-958)
SOFT = 57  # px above TINT_TOP where the paint eases in, so the raw file has no hard edge
RAMP_TOP = TINT_TOP - SOFT
OVERLAY_PEAK = 0.55


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def paint(y, level):
    a0, peak = LEVELS[level]
    if y < TINT_TOP:
        return a0 * smoothstep((y - RAMP_TOP) / SOFT)
    return a0 + (peak - a0) * smoothstep((y - TINT_TOP) / (HEIGHT - TINT_TOP))


def gradient(level, step=7):
    stops = []
    for y in list(range(RAMP_TOP, HEIGHT, step)) + [HEIGHT]:
        pct = round((y - RAMP_TOP) / (HEIGHT - RAMP_TOP) * 100, 1)
        stops.append(f"rgba({END[0]}, {END[1]}, {END[2]}, {paint(y, level):.3f}) {pct:g}%")
    return "linear-gradient(to bottom, " + ", ".join(stops) + ")"


# --- the film: #tint-ramp in index.html -------------------------------------
index = ROOT / "index.html"
html, n = re.subn(
    r"(#tint-ramp \{.*?top: )\d+px;(\s*height: )\d+px;(\s*)background: linear-gradient\(.*?\);",
    lambda m: f"{m.group(1)}{RAMP_TOP}px;{m.group(2)}{HEIGHT - RAMP_TOP}px;{m.group(3)}background: {gradient(LEVEL)};",
    index.read_text(encoding="utf-8"),
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("could not find the #tint-ramp block in index.html")
index.write_text(html, encoding="utf-8")

# --- the calibration clip: every level side by side -------------------------
ring = ", ".join(
    f"{round(2 * math.cos(a * math.pi / 8), 2)}px {round(2 * math.sin(a * math.pi / 8), 2)}px 0 #1e150c" for a in range(16)
)
col_w = WIDTH // len(LEVELS)
columns, labels = [], []
for i, level in enumerate(LEVELS):
    columns.append(
        f'      <div id="cal-col{level}" class="clip col" data-start="0" data-duration="10" data-track-index="{i + 1}" '
        f'style="left: {i * col_w}px; background: {gradient(level)}"></div>'
    )
    labels.append(
        f'      <div id="cal-num{level}" class="clip num" data-start="0" data-duration="10" data-track-index="{i + 6}" '
        f'style="left: {i * col_w}px">{level}</div>'
    )
calibration = f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={WIDTH}, height={HEIGHT}" />
    <style>
      @font-face {{
        font-family: "Gowun Batang";
        src: url("assets/fonts/GowunBatang-Bold-subset.woff2") format("woff2");
        font-weight: 700;
      }}
      @font-face {{
        font-family: "Noto Serif KR";
        src: url("assets/fonts/NotoSerifKR-subset.woff2") format("woff2");
        font-weight: 200 900;
      }}
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        width: {WIDTH}px;
        height: {HEIGHT}px;
        overflow: hidden;
        background: #00ff00;
      }}
      #root {{
        position: relative;
        width: 100%;
        height: 100%;
        background: #00ff00;
      }}
      #root .col {{
        position: absolute;
        top: {RAMP_TOP}px;
        width: {col_w}px;
        height: {HEIGHT - RAMP_TOP}px;
      }}
      #root .num {{
        position: absolute;
        top: 140px;
        width: {col_w}px;
        text-align: center;
        font-family: "Noto Serif KR", serif;
        font-size: 160px;
        font-weight: 700;
        color: #fffaf0;
        text-shadow: {ring}, 3px 4px 0 #1e150c;
      }}
      #cal-lyric {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 110px;
        text-align: center;
        font-family: "Gowun Batang", serif;
        font-size: 110px;
        font-weight: 700;
        line-height: 1.25;
        letter-spacing: 0.02em;
        color: #fffaf0;
        text-shadow: {ring}, 3px 4px 0 #1e150c;
      }}
      #cal-lyric .g {{
        color: #e6c07a;
      }}
    </style>
  </head>
  <body>
    <!-- ATEM tint calibration: key this like the film and pick the column that looks right -->
    <div id="root" data-composition-id="calibration" data-start="0" data-duration="10" data-width="{WIDTH}" data-height="{HEIGHT}" data-no-timeline>
{chr(10).join(columns)}
{chr(10).join(labels)}
      <div id="cal-lyric" class="clip" data-start="0" data-duration="10" data-track-index="11">옷자락에서 전해지는 <span class="g">사랑</span></div>
    </div>
  </body>
</html>
"""
cal_dir = ROOT / "extras" / "tint-calibration"
(cal_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
for name in ("GowunBatang-Bold-subset.woff2", "NotoSerifKR-subset.woff2"):
    shutil.copyfile(ROOT / "assets" / "fonts" / name, cal_dir / "assets" / "fonts" / name)
(cal_dir / "index.html").write_text(calibration, encoding="utf-8")


# --- optional: the fade on a transparent background, for a downstream key ---
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
png(overlay, [bytes((0, 0, 0, round(OVERLAY_PEAK * smoothstep((y - RAMP_TOP) / (HEIGHT - RAMP_TOP)) * 255))) * WIDTH for y in range(HEIGHT)])

print(f"film uses level {LEVEL} {LEVELS[LEVEL]}; wrote index.html #tint-ramp, {cal_dir.relative_to(ROOT)}/index.html, {overlay.relative_to(ROOT)}")
