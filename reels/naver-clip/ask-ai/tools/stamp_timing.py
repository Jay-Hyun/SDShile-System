#!/usr/bin/env python3
"""lib/cue.js 의 시각을 HTML 속성(data-start / data-duration)에 찍는다 — 30초(루트)와 15초(v15) 모두. (v7)

Usage: python3 tools/stamp_timing.py          (tools/build_15s.py 가 v15 를 만든 뒤 자동으로 부른다)
 - index.html: 루트 길이, phone/world/legal 씬, 오디오 길이
 - compositions/legal.html: 배지·안내·고지 클립
JS 안의 시각은 window.HFCUE 를 직접 읽으므로 찍을 필요가 없다.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import ROOT, cue  # noqa: E402


def r3(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def set_clip(s, elem_id, start, dur):
    m = re.search(r'<(?:div|audio)\b[^>]*\bid="%s"[^>]*>' % re.escape(elem_id), s, re.S)
    assert m, elem_id
    tag = m.group(0)
    new = re.sub(r'data-start="[^"]*"', f'data-start="{r3(start)}"', tag)
    new = re.sub(r'data-duration="[^"]*"', f'data-duration="{r3(dur)}"', new)
    return s[: m.start()] + new + s[m.end():]


def stamp(base, cut):
    c = cue(cut)
    end = c["END"]
    p = os.path.join(base, "index.html")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'(data-composition-id="main"\s+data-start="0"\s+data-duration=")[^"]*"', lambda m: m.group(1) + f'{int(end)}"', s)
    s = set_clip(s, "phone", 0, c["WORLD"] + 0.1)
    s = set_clip(s, "world", c["GROW"], end - c["GROW"])
    s = set_clip(s, "legal", 0, end)
    s = set_clip(s, "bgm", 0, end)
    s = set_clip(s, "sfx", 0, end)
    open(p, "w", encoding="utf-8").write(s)
    p = os.path.join(base, "compositions", "legal.html")
    s = open(p, encoding="utf-8").read()
    sw = c["GROW"] + 0.35  # 말풍선이 화면 대부분을 덮으면 배지가 '연출'로
    s = set_clip(s, "lg-b1", 0, sw)
    s = set_clip(s, "lg-b2", sw, c["FLOOD"] + 0.2 - sw)
    s = set_clip(s, "lg-n", 0, c["GROW"])
    s = set_clip(s, "lg-l", c["FLOOD"] + 0.3, end - (c["FLOOD"] + 0.3))
    open(p, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    stamp(ROOT, 30)
    if os.path.exists(os.path.join(ROOT, "v15", "index.html")):
        stamp(os.path.join(ROOT, "v15"), 15)
    print("stamped")
