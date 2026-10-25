#!/usr/bin/env python3
"""Regenerate compositions/lyrics.html from lyrics.json.

Edit a line's text or times in lyrics.json (MR seconds), then run:
    python3 tools/build_lyrics.py
Needs fontTools + brotli (pip install fonttools brotli) to measure line widths.
If you add characters that never appeared before, also re-subset the font
(see README.md), or they fall back to a system font.
"""
import html
import json
import math
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
CHAR_IN = 0.7
CHAR_STAGGER = 0.035
FADE_OUT = 0.35
FONT_SIZE = 110
LETTER_SPACING = 0.02  # em
MAX_WIDTH = 1536  # 80% title-safe width; longer lines are set smaller to fit
# the song's own words, set in gold: one per line, "사랑" wins when both appear
GOLD_WORDS = ["사랑", "옷자락"]

lines = json.loads((ROOT / "lyrics.json").read_text(encoding="utf-8"))["lines"]
mr_len = 286.5  # the lyrics host slot (the MR is cut at 285.4 s)

font = TTFont(ROOT / "assets" / "fonts" / "GowunBatang-Bold-subset.woff2")
upm, cmap, hmtx = font["head"].unitsPerEm, font.getBestCmap(), font["hmtx"]


def line_width(text, size):
    advance = sum(hmtx[cmap[ord(ch)]][0] for ch in text) / upm
    return (advance + LETTER_SPACING * len(text)) * size


def gold_span(text):
    for word in GOLD_WORDS:
        i = text.find(word)
        if i >= 0:
            return i, i + len(word)
    return None


markup, tweens = [], []
for ln in lines:
    lid, start, end, text = ln["id"], ln["start"], ln["end"], ln["text"]
    dur = round(end - start, 2)
    gold = gold_span(text)
    words, pos = [], 0
    for word in text.split(" "):
        chars = []
        for ch in word:
            cls = "c g" if gold and gold[0] <= pos < gold[1] else "c"
            chars.append(f'<span class="{cls}">{html.escape(ch)}</span>')
            pos += 1
        pos += 1  # the space
        words.append(f'<span class="w">{"".join(chars)}</span>')
    size = FONT_SIZE
    if line_width(text, size) > MAX_WIDTH:
        size = math.floor(FONT_SIZE * MAX_WIDTH / line_width(text, FONT_SIZE))
    fit = f' style="font-size: {size}px"' if size != FONT_SIZE else ""
    markup.append(
        f'    <div id="{lid}" class="clip line" data-start="{start}" data-duration="{dur}" data-track-index="0">'
        f'<div id="{lid}-t" class="lt"{fit}>{" ".join(words)}</div></div>'
    )
    tweens.append(
        f'      tl.fromTo("#{lid}-t .c", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: {CHAR_IN}, ease: "power3.out", stagger: {CHAR_STAGGER} }}, {start});\n'
        f'      tl.fromTo("#{lid}-t", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: -10, duration: {FADE_OUT}, ease: "power2.in", immediateRender: false }}, {round(end - FADE_OUT, 2)});\n'
        f'      tl.set("#{lid}-t", {{ opacity: 0, visibility: "hidden" }}, {end});'
    )

# hard 0-blur shadows only: a soft edge over chroma green keys into a green fringe
ring = ", ".join(
    f"{round(2 * math.cos(a * math.pi / 8), 2)}px {round(2 * math.sin(a * math.pi / 8), 2)}px 0 #1e150c" for a in range(16)
)

page = f"""<template>
  <style>
    @font-face {{
      font-family: "Gowun Batang";
      src: url("assets/fonts/GowunBatang-Bold-subset.woff2") format("woff2");
      font-weight: 700;
    }}
    #root {{
      position: absolute;
      inset: 0;
    }}
    #root .line {{
      position: absolute;
      inset: 0;
    }}
    #root .lt {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 110px;
      text-align: center;
      font-family: "Gowun Batang", serif;
      font-size: {FONT_SIZE}px;
      font-weight: 700;
      line-height: 1.25;
      letter-spacing: {LETTER_SPACING}em;
      color: #fffaf0;
      text-shadow: {ring}, 3px 4px 0 #1e150c;
    }}
    #root .w {{
      display: inline-block;
      white-space: nowrap;
    }}
    #root .c {{
      display: inline-block;
    }}
    #root .g {{
      color: #e6c07a;
    }}
  </style>
  <div id="root" data-composition-id="lyrics" data-width="1920" data-height="1080" data-layout-allow-caption-zone>
{chr(10).join(markup)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
      tl.set({{}}, {{}}, {mr_len});
      window.__timelines["lyrics"] = tl;
    }})();
  </script>
</template>
"""

out = ROOT / "compositions" / "lyrics.html"
out.write_text(page, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({len(lines)} lines)")
