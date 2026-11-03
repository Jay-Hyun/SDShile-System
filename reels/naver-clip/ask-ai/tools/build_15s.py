#!/usr/bin/env python3
"""30초 프로젝트에서 15초판 v15/ 를 만든다 (05-ask-ai.md §3).

Usage: python3 tools/build_15s.py
- compositions/chat.html, brand.html, legal.html 을 복사하며 `const CUT = 30;` → 15 로 바꾼다. 15초 문구·배치·타이밍은 각 씬
  스크립트의 CUT === 15 분기에 있다 (하나의 마크업, 두 개의 타임라인). 시각은 lib/cue.js 가 단일 출처.
- index.html 은 오디오 파일명·주석만 15초용으로 바꾸고, 클립 시각(data-start/duration)은 tools/stamp_timing.py 가 30초·15초 모두 찍는다.
- v15/assets → ../assets, v15/lib → ../lib 심볼릭 링크. v15 파일은 직접 고치지 말고 이 생성기나 원본을 고친다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stamp_timing import stamp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V15 = os.path.join(ROOT, "v15")


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    full = os.path.join(V15, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(s)


def link(name):
    p = os.path.join(V15, name)
    if os.path.islink(p) or os.path.exists(p):
        if os.path.islink(p):
            return
        raise SystemExit(f"{p} exists and is not a symlink")
    os.symlink(os.path.join("..", name), p)


def sub(s, old, new):
    assert old in s, old
    return s.replace(old, new)


def main():
    os.makedirs(V15, exist_ok=True)
    for old in ("chat.html", "brand.html"):
        p = os.path.join(V15, "compositions", old)
        if os.path.exists(p):
            os.remove(p)
    link("assets")
    link("lib")
    for name in ("phone.html", "world.html", "legal.html"):
        wr("compositions/" + name, sub(rd("compositions/" + name), "const CUT = 30;", "const CUT = 15;"))

    s = rd("index.html")
    s = sub(s, 'src="assets/audio/bgm.wav"', 'src="assets/audio/bgm-15s.wav"')
    s = sub(s, 'src="assets/audio/sfx.wav"', 'src="assets/audio/sfx-15s.wav"')
    s = sub(s, "<!-- v7 편 A", "<!-- 15초판: tools/build_15s.py 가 생성 — 직접 고치지 말 것 -->\n      <!-- v7 편 A")
    wr("index.html", s)
    for f in ("hyperframes.json",):
        wr(f, rd(f))
    stamp(ROOT, 30)
    stamp(V15, 15)
    assert 'bgm.wav' not in open(os.path.join(V15, "index.html"), encoding="utf-8").read()
    print("v15 written; timing stamped (30s + 15s)")


if __name__ == "__main__":
    main()
