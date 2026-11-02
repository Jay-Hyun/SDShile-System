#!/usr/bin/env python3
"""30초 프로젝트에서 15초판 v15/ 를 만든다 (05-ask-ai.md §3).

Usage: python3 tools/build_15s.py
- compositions/chat.html, brand.html 을 복사하며 `const CUT = 30;` → 15 로 바꾼다. 15초 문구·배치·타이밍은 각 씬
  스크립트의 CUT === 15 분기에 있다 (하나의 마크업, 두 개의 타임라인).
- legal 은 15초 시각으로 바꾼다: 연출 대화 고지 3.0, 버튼이 열리기 시작 7.9, 브랜드(원곡 크래시) 8.5.
- v15/assets → ../assets, v15/lib → ../lib 심볼릭 링크. v15 파일은 직접 고치지 말고 이 생성기나 원본을 고친다.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V15 = os.path.join(ROOT, "v15")

# 30s → 15s (chat.html / brand.html 의 WIN·BR 과 같은 값)
NOTE30, NOTE15 = 3.839, 3.0
WIN30, WIN15 = 536 / 30, 237 / 30
BRAND30, BRAND15 = 18.476, 8.5


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


def r3(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def main():
    os.makedirs(V15, exist_ok=True)
    link("assets")
    link("lib")
    for name in ("chat.html", "brand.html"):
        wr("compositions/" + name, sub(rd("compositions/" + name), "const CUT = 30;", "const CUT = 15;"))

    s = rd("compositions/legal.html")
    b1_end = WIN15 + 0.98
    b2_start = WIN15 + 0.933
    s = sub(s, 'id="lg-b1" class="clip" data-start="0" data-duration="18.85"', f'id="lg-b1" class="clip" data-start="0" data-duration="{r3(b1_end)}"')
    s = sub(s, 'id="lg-b2" class="clip" data-start="18.8" data-duration="11.2"', f'id="lg-b2" class="clip" data-start="{r3(b2_start)}" data-duration="{r3(15 - b2_start)}"')
    s = sub(s, 'id="lg-n" class="clip" data-start="3.839" data-duration="14.328"', f'id="lg-n" class="clip" data-start="{r3(NOTE15)}" data-duration="{r3(WIN15 + 0.3 - NOTE15)}"')
    s = sub(s, 'id="lg-l" class="clip" data-start="18.476" data-duration="11.524"', f'id="lg-l" class="clip" data-start="{r3(BRAND15)}" data-duration="{r3(15 - BRAND15)}"')
    s = sub(s, "const T = { note: 3.839, win: 536 / 30, brand: 18.476, end: 30 };", "const T = { note: 3.0, win: 237 / 30, brand: 8.5, end: 15 };")
    wr("compositions/legal.html", s)

    s = rd("index.html")
    s = sub(s, 'data-duration="30"\n      data-fps', 'data-duration="15"\n      data-fps')
    s = sub(s, 'data-start="0" data-duration="19.1"', 'data-start="0" data-duration="9.15"')
    s = sub(s, 'data-start="17.8667" data-duration="12.1333"', f'data-start="{r3(WIN15)}" data-duration="{r3(15 - WIN15)}"')
    s = s.replace('data-start="0" data-duration="30"', 'data-start="0" data-duration="15"')
    s = sub(s, 'src="assets/audio/bgm.wav"', 'src="assets/audio/bgm-15s.wav"')
    s = sub(s, 'src="assets/audio/sfx.wav"', 'src="assets/audio/sfx-15s.wav"')
    s = sub(s, "C1–C6 가상 챗봇 화면 (한 컷, 0–17.867). [상담사 연결]이 열리는 동안 19.1까지 아래에 깔림",
            "C1–C4 가상 챗봇 화면 (한 컷, 0–7.9). [상담사 연결]이 열리는 동안 9.15까지 아래에 깔림")
    s = sub(s, "C7–C10 상담 화면 · 엔드카드 (17.867 버튼이 열리기 시작 → 18.476 원곡 B섹션 크래시 = 열림 중간점)",
            "C5–C6 상담 화면 · 엔드카드 (7.9 버튼이 열리기 시작 → 8.5 원곡 B섹션 크래시 = 열림 중간점)")
    s = sub(s, "<!-- 엔진:", "<!-- 15초판: tools/build_15s.py 가 생성 — 직접 고치지 말 것 -->\n      <!-- 엔진:")
    assert 'data-duration="30"' not in s and "bgm.wav" not in s
    wr("index.html", s)
    for f in ("hyperframes.json",):
        wr(f, rd(f))
    print("v15 written")


if __name__ == "__main__":
    main()
