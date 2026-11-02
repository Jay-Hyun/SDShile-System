#!/usr/bin/env python3
"""BGM 비트 분석 (numpy + ffmpeg).

assets/music/source.mp3 → beats/source.json
- 온셋 엔벨로프(스펙트럴 플럭스, 저역/전대역), 템포(자기상관), 비트 그리드(위상 정렬),
  다운비트(마디 첫 박: 저역 에너지 최대 위상), 강세 온셋(피크 피킹), 브레이크(RMS 저점).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/music/source.mp3"
OUT = ROOT / "beats/source.json"
SR = 22050
HOP = 256  # 11.6 ms


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def stft_mag(x, n=1024):
    win = np.hanning(n).astype(np.float32)
    frames = 1 + (len(x) - n) // HOP
    idx = np.arange(n)[None, :] + HOP * np.arange(frames)[:, None]
    return np.abs(np.fft.rfft(x[idx] * win, axis=1))


def flux(mag, lo, hi):
    freqs = np.fft.rfftfreq(1024, 1 / SR)
    band = (freqs >= lo) & (freqs < hi)
    m = np.log1p(100 * mag[:, band])
    d = np.diff(m, axis=0, prepend=m[:1])
    f = np.maximum(d, 0).sum(axis=1)
    f -= np.convolve(f, np.ones(16) / 16, mode="same")  # 로컬 평균 제거
    f = np.maximum(f, 0)
    return f / (f.max() + 1e-9)


def main():
    x = load(SRC)
    dur = len(x) / SR
    mag = stft_mag(x)
    t = (np.arange(mag.shape[0]) * HOP + 512) / SR
    env = flux(mag, 30, 11000)
    low = flux(mag, 30, 160)
    fps_env = SR / HOP

    # 템포: 자기상관 (70–180 BPM)
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm_of = 60 * fps_env / np.maximum(lags, 1)
    ok = (bpm_of >= 70) & (bpm_of <= 180)
    cand = lags[ok][np.argsort(ac[ok])[::-1][:8]]
    lag = cand[0]
    # 서브샘플 정밀화: 여러 배수에서 피크
    best_bpm, best_score = None, -1
    for bpm in np.arange(60 * fps_env / (lag + 1.5), 60 * fps_env / (lag - 1.5), 0.01):
        period = 60 / bpm
        score = 0
        for k in range(1, 9):
            L = k * period * fps_env
            i = int(L)
            if i + 1 >= len(ac):
                break
            score += ac[i] * (1 - (L - i)) + ac[i + 1] * (L - i)
        if score > best_score:
            best_bpm, best_score = bpm, score
    bpm = float(best_bpm)
    period = 60 / bpm

    # 위상: 비트 위치에서 엔벨로프 합이 최대가 되는 오프셋
    def env_at(times, e):
        return np.interp(times, t, e)

    phases = np.linspace(0, period, 400, endpoint=False)
    scores = [env_at(np.arange(p, dur, period), env).sum() for p in phases]
    phase = float(phases[int(np.argmax(scores))])
    beats = np.arange(phase, dur - 0.05, period)
    # 각 비트를 ±40ms 안 최대 온셋으로 미세 보정 (드리프트 없음 확인용)
    refined = []
    for b in beats:
        w = (t > b - 0.04) & (t < b + 0.04)
        refined.append(float(t[w][np.argmax(env[w])]) if w.any() and env[w].max() > 0.15 else float(b))
    drift = float(np.median(np.array(refined) - beats))

    # 다운비트: 4박 중 저역 온셋 합이 최대인 위상
    lowsum = [env_at(beats[k::4], low).sum() for k in range(4)]
    db0 = int(np.argmax(lowsum))
    downbeats = beats[db0::4]

    # 강세 온셋: 엔벨로프 피크(>0.45), 최소 간격 120ms
    acc = []
    for i in range(1, len(env) - 1):
        if env[i] > 0.45 and env[i] >= env[i - 1] and env[i] >= env[i + 1]:
            if not acc or t[i] - acc[-1][0] > 0.12:
                acc.append((float(t[i]), float(env[i])))
            elif env[i] > acc[-1][1]:
                acc[-1] = (float(t[i]), float(env[i]))

    # RMS(250ms) / 저역 RMS 프로필 → 브레이크 후보
    win = int(0.25 * SR)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
    rt = np.arange(0, dur, 0.25)
    rprof = [float(20 * np.log10(rms[int(s * SR)] + 1e-9)) for s in rt]
    med = float(np.median(rprof))
    breaks = [round(float(s), 2) for s, v in zip(rt, rprof) if v < med - 6]

    # 마디별 에너지 (발췌 구간 선정용)
    bars = []
    for i, d in enumerate(downbeats):
        e = d + 4 * period
        if e > dur:
            break
        seg = x[int(d * SR):int(e * SR)]
        bars.append({"i": i, "t": round(float(d), 3), "rms_db": round(float(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)), 2),
                     "low_onset": round(float(env_at(np.arange(d, e, period), low).sum()), 2)})

    out = {
        "source": "assets/music/source.mp3",
        "duration": round(dur, 3),
        "bpm": round(bpm, 2),
        "beat_period": round(period, 5),
        "frames_per_beat_30fps": round(30 * period, 3),
        "phase": round(phase, 4),
        "onset_refine_median_offset": round(drift, 4),
        "downbeat_index_offset": db0,
        "beats": [round(float(b), 4) for b in beats],
        "downbeats": [round(float(b), 4) for b in downbeats],
        "accents": [{"t": round(a, 3), "s": round(s, 2)} for a, s in acc],
        "bars": bars,
        "rms_profile_db_250ms": [round(v, 1) for v in rprof],
        "quiet_250ms_slots": breaks,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"dur {dur:.3f}s  bpm {bpm:.2f}  period {period:.4f}s  phase {phase:.4f}  drift {drift*1000:.1f}ms  downbeat offset {db0}")
    print("downbeats:", " ".join(f"{d:.3f}" for d in downbeats))
    print("bars:", " ".join(f"{b['t']:.2f}:{b['rms_db']:.1f}/{b['low_onset']:.1f}" for b in bars))
    print("accents:", " ".join(f"{a:.2f}({s:.2f})" for a, s in acc))
    print("quiet:", breaks)
    print("rms:", " ".join(f"{v:.0f}" for v in rprof))


if __name__ == "__main__":
    sys.exit(main())
