#!/usr/bin/env python3
"""Regenerate compositions/lyrics.html from lyrics.json.

Edit a line's text or times in lyrics.json (MR seconds), then run:
    python3 tools/build_lyrics.py
If you add characters that never appeared before, also re-subset the font
(see README.md), or they fall back to a system font.
"""
import html
import math
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FADE_IN = 0.45
WORD_STAGGER = 0.08
FADE_OUT = 0.25

lines = json.loads((ROOT / "lyrics.json").read_text(encoding="utf-8"))["lines"]
mr_len = 290.78

markup, tweens = [], []
for ln in lines:
    lid, start, end = ln["id"], ln["start"], ln["end"]
    dur = round(end - start, 2)
    words = ln["text"].split(" ")
    spans = "".join(
        f'<span class="w">{html.escape(w)}{" " if i < len(words) - 1 else ""}</span>'
        for i, w in enumerate(words)
    )
    markup.append(
        f'    <div id="{lid}" class="clip line" data-start="{start}" data-duration="{dur}" data-track-index="0">'
        f'<div id="{lid}-t" class="lt">{spans}</div></div>'
    )
    tweens.append(
        f'      tl.fromTo("#{lid}-t .w", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: {FADE_IN}, ease: "power3.out", stagger: {WORD_STAGGER} }}, {start});\n'
        f'      tl.fromTo("#{lid}-t", {{ opacity: 1 }}, {{ opacity: 0, duration: {FADE_OUT}, ease: "power2.in", immediateRender: false }}, {round(end - FADE_OUT, 2)});\n'
        f'      tl.set("#{lid}-t", {{ opacity: 0, visibility: "hidden" }}, {end});'
    )

# hard 0-blur shadows only: a soft edge over chroma green keys into a green fringe
ring = ", ".join(
    f"{round(3.2 * math.cos(a * math.pi / 8), 2)}px {round(3.2 * math.sin(a * math.pi / 8), 2)}px 0 #1b130c" for a in range(16)
)

page = f"""<template>
  <style>
    @font-face {{
      font-family: "Noto Serif KR";
      src: url("assets/fonts/NotoSerifKR-subset.woff2") format("woff2");
      font-weight: 200 900;
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
      font-family: "Noto Serif KR", serif;
      font-size: 92px;
      font-weight: 800;
      line-height: 1.25;
      letter-spacing: -0.01em;
      color: #ffffff;
      text-shadow: {ring}, 0 5px 0 #1b130c;
    }}
    #root .w {{
      display: inline-block;
      white-space: pre;
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
