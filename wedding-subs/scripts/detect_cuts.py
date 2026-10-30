#!/usr/bin/env python3
"""Hard cuts in the draft (first frame of each new shot, seconds) -> work/cuts.json. Fades count at their midpoint."""
import json
import subprocess

import numpy as np

W, H, FPS = 160, 90, 24
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", "assets/raw/draft.mov", "-vf",
                      f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
# a shot change: the picture differs a lot from 0.5 s earlier and is stable again 0.5 s later (covers dissolves);
# the change is dated where the frame-to-frame difference peaks inside it
far = np.abs(fr[12:] - fr[:-12]).mean(axis=(1, 2))  # far[k] = frame k+12 vs frame k
cuts = []
k = 0
while k < len(far):
    if far[k] > 22:
        j = k
        while j < len(far) and far[j] > 22:
            j += 1
        lo, hi = k, min(j + 12, len(d))
        peak = lo + int(np.argmax(d[lo:hi]))
        cuts.append(round((peak + 1) / FPS, 3))
        k = j + 12
    else:
        k += 1
# picture appears from black (fade-in start): first frame whose mean rises above a floor after black
mean = fr.mean(axis=(1, 2))
for k in range(1, len(mean)):
    if mean[k - 1] < 4 <= mean[k]:
        cuts.append(round(k / FPS, 3))
cuts = sorted(set(cuts))
json.dump(cuts, open("work/cuts.json", "w"))
print(len(cuts), "cuts:", " ".join(f"{c:.2f}" for c in cuts if c < 100))
