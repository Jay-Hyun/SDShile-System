#!/usr/bin/env python3
"""lib/cue.js 의 시각을 HTML 속성(data-start / data-duration)에 찍는다 — 30초(루트)와 15초(v15) 모두.

Usage: python3 tools/stamp_timing.py          (tools/build_15s.py 가 v15 를 만든 뒤 자동으로 부른다)
 - index.html: 루트 길이, chat/brand/legal 클립, 오디오 길이
 - compositions/legal.html: 배지·고지·각주 클립
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
    """<... id="elem_id" ...> 여는 태그 안의 data-start / data-duration 을 바꾼다."""
    m = re.search(r'<(?:div|audio)\b[^>]*\bid="%s"[^>]*>' % re.escape(elem_id), s, re.S)
    assert m, elem_id
    tag = m.group(0)
    new = re.sub(r'data-start="[^"]*"', f'data-start="{r3(start)}"', tag)
    new = re.sub(r'data-duration="[^"]*"', f'data-duration="{r3(dur)}"', new)
    return s[: m.start()] + new + s[m.end():]


def stamp(base, cut):
    c = cue(cut)
    end, win, br = c["END"], c["WIN"], c["BR"]
    # --- index.html
    p = os.path.join(base, "index.html")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'(data-composition-id="main"\s+data-start="0"\s+data-duration=")[^"]*"', lambda m: m.group(1) + f'{int(end)}"', s)
    s = set_clip(s, "chat", 0, win + 1.2 + 0.03)  # 버튼이 열리는 1.2초가 끝날 때까지
    s = set_clip(s, "brand", win, end - win)
    s = set_clip(s, "legal", 0, end)
    s = set_clip(s, "bgm", 0, end)
    s = set_clip(s, "sfx", 0, end)
    open(p, "w", encoding="utf-8").write(s)
    # --- legal.html
    p = os.path.join(base, "compositions", "legal.html")
    s = open(p, encoding="utf-8").read()
    s = set_clip(s, "lg-b1", 0, win + 0.98)  # 열린 창이 위쪽을 덮은 뒤 배지가 바뀐다
    s = set_clip(s, "lg-b2", win + 0.933, end - (win + 0.933))
    s = set_clip(s, "lg-n", 0, win + 0.3)
    s = set_clip(s, "lg-l", br, end - br)
    open(p, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    stamp(ROOT, 30)
    stamp(os.path.join(ROOT, "v15"), 15)
    print("stamped 30s + v15")
