#!/usr/bin/env python3
"""렌더된 MP4에서 컷(프레임 차 피크)을 찾아 편집된 음악의 비트 그리드와 대조한다.
Usage: python3 tools/verify_cuts.py 30|15
기획된 컷(beats/cuts-N.json)마다 ±3프레임 안의 최대 프레임 차 피크를 찾고, 그 프레임과 가장 가까운 비트의 거리(프레임)를 보고한다.
비트 그리드 = 실제로 들리는 음악의 비트 (구간별: A·B·C 세그먼트, 무음 구간은 A 그리드 연장).
"""
import json, subprocess, sys
import numpy as np
cut = int(sys.argv[1])
c = json.load(open(f"beats/cuts-{cut}.json"))
P = c["beat_period"]
W, H = 72, 128
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"renders/ask-ai-{cut}s.mp4", "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
beats = []
for s in c["music_segments"]:
    k = 0
    while s["v0"] + k * P < s["v1"] - 1e-6:
        beats.append(s["v0"] + k * P); k += 1
R = c["R_slam"]
beats += [t for t in np.arange(0, R, P) if t > c["music_segments"][0]["v1"]]  # 무음 개그 구간 = A 그리드 연장
beats = np.array(sorted(beats))
rows, ok = [], 0
for name, t in c["cuts"].items():
    if name in ("C1", "end"):
        continue
    f0 = round(t * 30)
    win = range(max(1, f0 - 3), min(len(d) - 1, f0 + 3) + 1)
    pk = max(win, key=lambda i: d[i])
    nb = beats[np.argmin(np.abs(beats - pk / 30))]
    off = pk - nb * 30
    good = abs(off) <= 2
    ok += good
    rows.append(f"| {name} | {t:.3f} | {pk} ({pk/30:.3f}) | {d[pk]:.1f} | {nb:.3f} | {off:+.1f} | {'✓' if good else '✗'} |")
print("| cut | planned s | detected frame (s) | Δ luma | nearest beat s | off (frames) | ±2f |")
print("|---|---|---|---|---|---|---|")
print("\n".join(rows))
print(f"on-beat: {ok}/{len(rows)} = {100*ok/len(rows):.0f}%")
# 정적 구간: 연속 프레임 차 < 0.05 가 1.5s 넘는지
still = d < 0.05
run, worst, ws = 0, 0, 0
for i, s in enumerate(still):
    run = run + 1 if s else 0
    if run > worst: worst, ws = run, i - run + 1
print(f"longest static run: {worst} frames ({worst/30:.2f}s) from {ws/30:.2f}s")
