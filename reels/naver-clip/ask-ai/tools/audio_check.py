#!/usr/bin/env python3
"""음악 연속성 점검 (art direction §7-2 "음악은 끊지 않는다").

Usage: python3 tools/audio_check.py 30|15 [audio-or-mp4]      (생략하면 assets/audio 의 bgm+sfx 합)
  1. 최저 구간: 10 ms RMS 가 −40 dBFS 미만으로 이어지는 가장 긴 구간 (마지막 엔딩 페이드 제외). 50 ms 이상이면 끊김.
  2. 고민 중 구간 RMS 가 앞뒤 구간 평균과 몇 dB 차이인가 (±6 dB 이내여야 함).
  3. 이음새 클릭: 이음새 ±3 ms 안의 최대 샘플 간 차이 ÷ 주변 ±300 ms 의 99.9 백분위 차이 (클릭이면 ≫ 1).
  4. 고역(10 kHz+) 비율: 같은 구간 원곡 대비 dB 차이 (±1 dB 이내여야 함). 효과음(탭)이 든 0.25 s 는 뺀다.
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000


def load(path):
    if path.endswith(".wav"):
        w = wave.open(path)
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, w.getnchannels()).astype(np.float64) / 32768
        return x.mean(1)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def db(x):
    return 20 * np.log10(max(float(np.sqrt(np.mean(x ** 2))), 1e-12))


def hf_ratio_db(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return 10 * np.log10(X[f >= 10000].sum() + 1e-30) - 10 * np.log10(X.sum() + 1e-30)


def main():
    cut = int(sys.argv[1])
    c = json.load(open(os.path.join(ROOT, "beats", f"cuts-{cut}.json")))
    if len(sys.argv) > 2:
        x = load(sys.argv[2])
        label = sys.argv[2]
    else:
        suf = "-15s" if cut == 15 else ""
        x = load(os.path.join(ROOT, f"assets/audio/bgm{suf}.wav")) + load(os.path.join(ROOT, f"assets/audio/sfx{suf}.wav"))
        label = f"assets/audio/bgm{suf}.wav + sfx{suf}.wav"
    src = load(os.path.join(ROOT, "assets/music/source.mp3"))
    segs = c["music_segments"]
    R = c["R"]
    fade_start = segs[-1]["v1"] - segs[-1].get("fade", 0)
    print(f"## {cut}s audio check — {label} ({len(x)/SR:.3f} s)")

    # 1. 최저 구간
    n = int(0.010 * SR)
    m = len(x) // n
    rms = np.array([20 * np.log10(max(np.sqrt(np.mean(x[i * n:(i + 1) * n] ** 2)), 1e-12)) for i in range(m)])
    lim = int(fade_start / 0.010)
    low = rms[:lim] < -40
    run = best = start = bs = 0
    for i, v in enumerate(low):
        run = run + 1 if v else 0
        if run > best:
            best, bs = run, i - run + 1
    print(f"1. longest run below −40 dBFS (10 ms RMS, 0–{fade_start:.2f} s): {best*10} ms" + (f" at {bs*0.010:.2f} s" if best else "") + f"   [min 10 ms RMS = {rms[:lim].min():.1f} dBFS at {rms[:lim].argmin()*0.010:.2f} s]  -> {'OK' if best*10 < 50 else 'BREAK'}")

    # 2. 고민 중 구간
    g0 = c["chapters"]["gag"]
    w = 2.0
    pre = x[int((g0 - 0.1 - w) * SR):int((g0 - 0.1) * SR)]
    gag = x[int(g0 * SR):int(R * SR)]
    post = x[int(R * SR):int((R + w) * SR)]
    a, b, d = db(pre), db(gag), db(post)
    print(f"2. gag window {g0:.3f}–{R:.3f} s RMS {b:.1f} dBFS | before ({w:.0f} s) {a:.1f} | after ({w:.0f} s) {d:.1f} | gag − mean(neighbours) = {b-(a+d)/2:+.1f} dB  -> {'OK' if abs(b-(a+d)/2) <= 6 else 'OFF'}")

    # 3. 이음새 클릭
    seams = [segs[1]["v0"], segs[2]["v0"]]
    for t in seams:
        i = int(round(t * SR))
        k = int(0.003 * SR)
        d_in = np.abs(np.diff(x[i - k:i + k]))
        d_ctx = np.abs(np.diff(x[i - int(0.3 * SR):i + int(0.3 * SR)]))
        ref = np.percentile(d_ctx, 99.9)
        # 이음새 자리의 원곡(이음새 없는 곳)과 같은 방법으로 비교하려고, 원곡의 같은 박 위치도 잰다
        print(f"3. seam {t:.3f} s: max sample step in ±3 ms = {d_in.max():.4f} | 99.9th pct of ±300 ms = {ref:.4f} | ratio {d_in.max()/ref:.2f}  -> {'OK' if d_in.max() / ref <= 1.5 else 'CLICK?'}")

    # 4. 고역 비율 (원곡 대비)
    sfx_t = [s["t"] for s in c.get("sfx", [])]
    rows = []
    for si, sg in enumerate(segs):
        v0, v1 = sg["v0"] + (0.05 if si else 0.2), sg["v1"] - (0.05 if si < len(segs) - 1 else 0.6 if sg.get("fade") else 0.05)
        t = v0
        while t + 1.0 <= v1:
            if all(not (t - 0.1 <= s <= t + 1.25) for s in sfx_t):
                s0 = int((sg["src"] + (t - sg["v0"])) * SR)
                rows.append(hf_ratio_db(x[int(t * SR):int((t + 1.0) * SR)]) - hf_ratio_db(src[s0:s0 + SR]))
            t += 1.0
    rows = np.array(rows)
    print(f"4. >10 kHz share vs source over {len(rows)} one-second windows: mean {rows.mean():+.2f} dB, worst {rows[np.abs(rows).argmax()]:+.2f} dB  -> {'OK' if np.abs(rows).max() <= 1.0 else 'CHECK'}")


if __name__ == "__main__":
    main()
