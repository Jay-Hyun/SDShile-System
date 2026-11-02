#!/usr/bin/env python3
"""30초 프로젝트에서 15초판 v15/ 를 만든다 (05-ask-ai.md §3).

Usage: python3 tools/build_15s.py
- compositions/*.html 을 복사하며 `const CUT = 30;` → 15 로 바꾼다. 15초 문구·배치·타이밍은 각 씬 스크립트의
  CUT === 15 분기에 있다 (하나의 마크업, 두 개의 비트 타임라인).
- legal 은 브랜드 진입 8.5초(원곡 B섹션 크래시)에 배지 교체·각주·고지.
- v15/assets → ../assets, v15/lib → ../lib 심볼릭 링크. v15 파일은 직접 고치지 말고 이 생성기나 원본을 고친다.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V15 = os.path.join(ROOT, "v15")
BRAND = 8.5


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


def main():
    os.makedirs(V15, exist_ok=True)
    link("assets")
    link("lib")
    for name in ("chat.html", "brand.html"):
        s = rd("compositions/" + name)
        assert "const CUT = 30;" in s
        wr("compositions/" + name, s.replace("const CUT = 30;", "const CUT = 15;"))

    s = rd("compositions/legal.html")
    s = s.replace('data-start="0" data-duration="18.467"', f'data-start="0" data-duration="{BRAND}"')
    s = s.replace('data-start="18.467" data-duration="11.533"', f'data-start="{BRAND}" data-duration="{15 - BRAND}"')
    s = s.replace("const T = 18.467;", f"const T = {BRAND};")
    s = s.replace("30초 18.467", "15초 8.5").replace("사양 18.0", "사양 8.5")
    assert "18.467" not in s
    wr("compositions/legal.html", s)

    s = rd("index.html")
    s = s.replace('data-duration="30"\n      data-fps', 'data-duration="15"\n      data-fps')
    s = s.replace('data-start="0" data-duration="19"', 'data-start="0" data-duration="9"')
    s = s.replace('data-start="18.467" data-duration="11.533"', f'data-start="{BRAND}" data-duration="{15 - BRAND}"')
    s = s.replace('data-start="0" data-duration="30"', 'data-start="0" data-duration="15"')
    s = s.replace('src="assets/audio/bgm.wav"', 'src="assets/audio/bgm-15s.wav"').replace('src="assets/audio/sfx.wav"', 'src="assets/audio/sfx-15s.wav"')
    s = s.replace("C1–C6 가상 챗봇 화면 (0–18.467). 브랜드 원형 전환 아래로 19.0까지 깔림", "C1–C4 가상 챗봇 화면 (0–8.5). 원형 전환 아래로 9.0까지")
    s = s.replace("C7–C10 브랜드 · 상담 화면 · 엔드카드 (18.467–30.0, 원곡 B섹션 크래시에 진입)", "C5–C6 브랜드 · 상담사 답 · 엔드카드 (8.5–15.0, 원곡 B섹션 크래시에 진입)")
    s = s.replace("<!-- 엔진:", "<!-- 15초판: tools/build_15s.py 가 생성 — 직접 고치지 말 것 -->\n      <!-- 엔진:", 1)
    assert 'data-duration="30"' not in s and "bgm.wav" not in s
    wr("index.html", s)
    for f in ("hyperframes.json",):
        wr(f, rd(f))
    print("v15 written")


if __name__ == "__main__":
    main()
