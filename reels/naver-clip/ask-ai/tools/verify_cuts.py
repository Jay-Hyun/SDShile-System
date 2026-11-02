#!/usr/bin/env python3
"""챕터·컷을 편집된 음악의 다운비트와 대조한다.
Usage: python3 tools/verify_cuts.py 30|15 [--plan]
- 계획표: beats/cuts-N.json 의 챕터마다 가장 가까운 다운비트와의 거리(프레임). MP4 없이 돈다.
- 렌더 대조(--plan 이 아니고 renders/ask-ai-Ns.mp4 가 있을 때): 실제 화면이 갈리는 지점(cuts: 하드컷 + 오프닝 윈도우 중간점)마다
  ±3프레임 안의 프레임 차 피크를 찾아, 그 프레임과 가장 가까운 비트의 거리(프레임)를 보고한다. 최장 정지 구간도 잰다.
비트 그리드 = 실제로 들리는 음악의 비트 (구간별: A·B·C 세그먼트, 음악은 끊기지 않는다). 다운비트 = 구간 시작 + 4P·k.
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

cut = int(sys.argv[1])
plan_only = "--plan" in sys.argv
c = json.load(open(f"beats/cuts-{cut}.json"))
P = c["beat_period"]
segs = c["music_segments"]

beats, downs = [], []
for s in segs:
    k = 0
    while s["v0"] + k * P < s["v1"] - 1e-6:
        t = s["v0"] + k * P
        beats.append(t)
        if k % 4 == 0:
            downs.append(t)
        k += 1

beats, downs = np.array(sorted(beats)), np.array(sorted(downs))

print(f"## {cut}s 챕터 ↔ 다운비트 (계획)")
print("| chapter | t (s) | nearest downbeat (s) | off (frames) |")
print("|---|---|---|---|")
for name, t in c["chapters"].items():
    if name == "end":
        continue
    nd = downs[np.argmin(np.abs(downs - t))]
    print(f"| {name} | {t:.3f} | {nd:.3f} | {(t - nd) * 30:+.1f} |")

mp4 = f"renders/ask-ai-{cut}s.mp4"
if plan_only or not os.path.exists(mp4):
    print("\n(렌더 대조 생략: --plan 또는 MP4 없음)")
    sys.exit(0)

# 픽셀 빈 띠: DOM 이 아니라 렌더된 화면으로 (tools/gapscan.py)
import gapscan  # noqa: E402
print()
gap_fails, _, _ = gapscan.scan(mp4, cut)
if gap_fails:
    print("FAIL gapscan:", ", ".join(f"{r[0]:.2f}s({r[1]}px)" for r in gap_fails))
    GAP_FAIL = True
else:
    print("PASS gapscan")
    GAP_FAIL = False

W, H = 72, 128
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
rows, ok = [], 0
for name, t in c["cuts"].items():
    f0 = round(t * 30)
    win = range(max(1, f0 - 3), min(len(d) - 1, f0 + 3) + 1)
    pk = max(win, key=lambda i: d[i])
    nb = beats[np.argmin(np.abs(beats - pk / 30))]
    off = pk - nb * 30
    good = abs(off) <= 2
    ok += good
    rows.append(f"| {name} | {t:.3f} | {pk} ({pk/30:.3f}) | {d[pk]:.1f} | {nb:.3f} | {off:+.1f} | {'✓' if good else '✗'} |")
print(f"\n## {cut}s 렌더 컷 ↔ 비트")
print("| cut | planned s | detected frame (s) | Δ luma | nearest beat s | off (frames) | ±2f |")
print("|---|---|---|---|---|---|---|")
print("\n".join(rows))
print(f"on-beat: {ok}/{len(rows)} = {100*ok/len(rows):.0f}%")
# 정적 구간: 연속 프레임 차 < 0.05 가 1.5s 넘는지
still = d < 0.05
run, worst, ws = 0, 0, 0
for i, s in enumerate(still):
    run = run + 1 if s else 0
    if run > worst:
        worst, ws = run, i - run + 1
print(f"longest static run: {worst} frames ({worst/30:.2f}s) from {ws/30:.2f}s")
if GAP_FAIL:
    sys.exit(1)
