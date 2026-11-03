#!/usr/bin/env python3
"""렌더된 MP4 의 픽셀로 빈 띠를 잰다 (DOM 이 아니라 실제로 그려진 화면). 4 fps 로 훑는다.

Usage: python3 tools/gapscan.py 30|15 [mp4]        (`npm run verify` 가 부른다)
- 한 행이 "비었다" = 그 행의 픽셀 99.5% 이상이 행 중앙값 색에서 ±10 이내. (같은 색 전체 폭 필드도 빈 행으로 센다 — DOM 측정과
  다른 점이고, 일부러 그렇다: 입력 독 위 여백처럼 눈에 빈 자리로 보이는 곳을 잡는다.)
- 안쪽 구간 = y 240–1560 (높이의 12.5%–81.25%). 그 안의 가장 긴 연속 빈 행 묶음이 200px 을 넘으면 실패.
- 면제: 입력 시트 접힘(C2–C2+0.8 s, 리드 승인), 하드컷(15s C6 만 — v6 의 30초는 하드컷 없음)과 오프닝 윈도우(WIN–WIN+1.2) 앞뒤 0.4 s. 면제한 표본은 모두 출력한다.
왜 만들었나: 15초 엔드카드에서 DOM 측정(임의 시각으로 건너뛰기)은 정상이었지만 렌더(프레임을 차례로)는 유도 줄이 버튼 아래에 있어
312px 빈 띠가 났다. DOM 과 렌더가 다를 수 있으니 픽셀이 최종 판정이다.
"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import ROOT, cue  # noqa: E402

LIMIT = 200  # px
FPS, W, H = 4, 270, 480  # 1/4 해상도 → 1 행 = 4px


def frames(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return np.frombuffer(raw, np.uint8).reshape(n, H, W, 3).astype(int)


def empty_runs(img, tol=10):
    med = np.median(img, axis=1)
    empty = (np.abs(img - med[:, None, :]).max(axis=2) <= tol).mean(axis=1) >= 0.995
    runs, s = [], None
    for y, e in enumerate(empty):
        if e and s is None:
            s = y
        if not e and s is not None:
            runs.append((s, y))
            s = None
    if s is not None:
        runs.append((s, H))
    return runs


def excused_windows(cut):
    """v7: 0.5 s 미만 전환과 그 앞뒤 0.4 s 만 면제 (질문 점프, 디바이스 다이브, 카메라 트랙 + 말풍선이 세계가 됨, 딥컷, 플러드+캐리)."""
    c = cue(cut)
    w = [(c["JUMP"] - 0.1, c["JUMP"] + 0.8, "question jump %.3f" % c["JUMP"]),
         (c["DIVE"] - 0.4, c["DIVE"] + c["DIVE_D"] + 0.4, "device dive %.3f" % c["DIVE"]),
         (c["TRACK"] - 0.1, c["WORLD"] + 0.4, "track + bubble becomes world %.3f–%.3f" % (c["TRACK"], c["WORLD"])),
         (c["DIP2"] - 0.4, c["DIP2"] + 0.4, "dip cut %.3f" % c["DIP2"]),
         (c["FLOOD"] - 0.1, c["FLOOD"] + 1.0, "flood + carry %.3f" % c["FLOOD"])]
    if cut == 30:
        w.append((c["DIP1"] - 0.4, c["DIP1"] + 0.9, "dip cut + card reveal %.3f" % c["DIP1"]))
    return w


def scan(path, cut, verbose=True):
    fr = frames(path)
    wins = excused_windows(cut)
    lo, hi = int(H * 0.125), int(H * 0.8125)  # y 240–1560
    rows = []
    for i, img in enumerate(fr):
        t = i / FPS
        inner = [(max(a, lo), min(b, hi)) for a, b in empty_runs(img)]
        inner = [(a * 4, b * 4) for a, b in inner if b > a]
        big = max(inner, key=lambda r: r[1] - r[0], default=(0, 0))
        why = next((w[2] for w in wins if w[0] <= t <= w[1]), None)
        rows.append((t, big[1] - big[0], big, why))
    fails = [r for r in rows if r[1] > LIMIT and not r[3]]
    excused = [r for r in rows if r[1] > LIMIT and r[3]]
    if verbose:
        print(f"## {cut}s 픽셀 빈 띠 ({os.path.basename(path)}, {len(rows)} 표본 @ {FPS} fps, 안쪽 y 240–1560, 한도 {LIMIT}px)")
        print("| 구분 | t (s) | 가장 긴 빈 띠 | y 범위 | 면제 사유 |\n|---|---|---|---|---|")
        for r in sorted(rows, key=lambda r: -r[1])[:6]:
            tag = "✗ 실패" if (r[1] > LIMIT and not r[3]) else ("면제" if r[1] > LIMIT else "✓")
            print(f"| {tag} | {r[0]:.2f} | {r[1]} px | {r[2][0]}–{r[2][1]} | {r[3] or ''} |")
        print(f"최대(면제 제외) {max([r[1] for r in rows if not (r[1] > LIMIT and r[3])], default=0)} px; 면제한 표본 {len(excused)}개" + (": " + ", ".join(f"{r[0]:.2f}s({r[1]}px)" for r in excused) if excused else ""))
    return fails, excused, rows


if __name__ == "__main__":
    cut = int(sys.argv[1])
    path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "renders", f"ask-ai-{cut}s.mp4")
    fails, _, _ = scan(path, cut)
    if fails:
        print("FAIL:", ", ".join(f"{r[0]:.2f}s({r[1]}px)" for r in fails))
        sys.exit(1)
    print("PASS")
