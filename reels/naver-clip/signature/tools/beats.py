"""Beat analysis for assets/music/source.mp3 with numpy + ffmpeg only.

python3 tools/beats.py  -> beats/source.json
Onset envelope = half-wave-rectified log-spectral flux (hop 256 @ 22.05 kHz).
Tempo = autocorrelation peak of the envelope in 70–180 BPM; beat phase = the
constant-tempo grid offset with the highest summed onset strength, then each
beat is refined to the local onset peak within ±35 ms (DP-free, the track is
quantised so the grid holds). Downbeat = the bar phase (of 4) with the most
low-band (<150 Hz) onset energy.
"""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets/music/source.mp3")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "beats/source.json")
SR, HOP, N = 22050, 256, 2048

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
dur = len(x) / SR
win = np.hanning(N)
nfr = 1 + (len(x) - N) // HOP
idx = np.arange(N)[None, :] + HOP * np.arange(nfr)[:, None]
S = np.abs(np.fft.rfft(x[idx] * win, axis=1))
freqs = np.fft.rfftfreq(N, 1 / SR)
L = np.log1p(1000 * S)
flux = np.maximum(0, np.diff(L, axis=0))
env = flux.sum(1)
low = flux[:, freqs[1:] < 150].sum(1) if False else flux[:, (freqs < 150)].sum(1)
hi = flux[:, freqs > 2000].sum(1)
fps_env = SR / HOP
t_env = (np.arange(len(env)) + 1) * HOP / SR + N / 2 / SR
def norm(a):
    a = a - np.convolve(a, np.ones(64) / 64, "same")
    a = np.maximum(a, 0)
    return a / (a.max() + 1e-9)
envn, lown, hin = norm(env), norm(low), norm(hi)

# tempo
ac = np.correlate(envn, envn, "full")[len(envn) - 1:]
lags = np.arange(len(ac))
bpm_l = 60 * fps_env / np.maximum(lags, 1)
mask = (bpm_l >= 70) & (bpm_l <= 180)
# weight toward 120 a little (log-gaussian)
w = np.exp(-0.5 * (np.log2(bpm_l / 120) / 1.0) ** 2)
lag = lags[mask][np.argmax((ac * w)[mask])]
# refine with parabolic interpolation
a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
lag_f = lag + 0.5 * (a - c) / (a - 2 * b + c)
period = lag_f / fps_env
# fine search period ±1.5% and phase on the grid
def score(p, ph):
    ts = np.arange(ph, dur, p)
    fi = np.clip(np.round((ts - t_env[0]) * fps_env).astype(int), 0, len(envn) - 1)
    return envn[fi].sum()
best = (-1, None, None)
for p in np.linspace(period * 0.985, period * 1.015, 61):
    for ph in np.arange(0, p, 0.004):
        s = score(p, ph)
        if s > best[0]:
            best = (s, p, ph)
_, period, phase = best
bpm = 60 / period
grid = np.arange(phase, dur - 0.05, period)
beats = []
for g in grid:
    lo, hi_ = g - 0.035, g + 0.035
    m = (t_env >= lo) & (t_env <= hi_)
    if m.any() and envn[m].max() > 0.15:
        beats.append(float(t_env[m][np.argmax(envn[m])]))
    else:
        beats.append(float(g))
beats = np.array(beats)
def at(a, t):
    i = int(round((t - t_env[0]) * fps_env))
    i0, i1 = max(0, i - 3), min(len(a), i + 4)
    return float(a[i0:i1].max()) if i1 > i0 else 0.0
strength = np.array([at(envn, t) for t in beats])
lowstr = np.array([at(lown, t) for t in beats])
phase_score = [lowstr[k::4].mean() + 0.5 * strength[k::4].mean() for k in range(4)]
db0 = int(np.argmax(phase_score))
downbeats = beats[db0::4]

# accents: onset peaks well above local median, anywhere (not only on beats)
from_peaks = []
thr = np.percentile(envn, 97)
for i in range(2, len(envn) - 2):
    if envn[i] >= thr and envn[i] == envn[i - 3:i + 4].max():
        from_peaks.append((float(t_env[i]), float(envn[i]), float(lown[i])))
accents = [dict(t=round(t, 3), s=round(s, 3), low=round(l, 3)) for t, s, l in from_peaks]

# energy per beat (RMS dBFS) and low-band share for breaks
rms_db = []
for k in range(len(beats)):
    a0 = int(beats[k] * SR); a1 = int((beats[k + 1] if k + 1 < len(beats) else beats[k] + period) * SR)
    seg = x[a0:a1]
    rms_db.append(round(float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)), 2))
rms_db = np.array(rms_db)
med = np.median(rms_db)
breaks = []
k = 0
while k < len(rms_db):
    if rms_db[k] < med - 4:
        j = k
        while j + 1 < len(rms_db) and rms_db[j + 1] < med - 4:
            j += 1
        breaks.append(dict(start=round(float(beats[k]), 3), end=round(float(beats[j] + period), 3), min_db=float(rms_db[k:j + 1].min())))
        k = j + 1
    else:
        k += 1

# 1-second loudness profile
sec = []
for s in range(int(dur)):
    seg = x[s * SR:(s + 1) * SR]
    sec.append(round(float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)), 1))

out = dict(source=os.path.relpath(SRC, ROOT), duration=round(dur, 3), sr=SR, hop=HOP,
           bpm=round(float(bpm), 3), period=round(float(period), 5), phase=round(float(phase), 4),
           downbeat_phase=db0,
           beats=[round(float(b), 3) for b in beats],
           beat_strength=[round(float(s), 3) for s in strength],
           beat_low=[round(float(s), 3) for s in lowstr],
           beat_rms_db=[float(v) for v in rms_db],
           downbeats=[round(float(b), 3) for b in downbeats],
           accents=accents, breaks=breaks, rms_per_second=sec)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1)
print(f"bpm={bpm:.3f} period={period:.4f}s phase={phase:.3f} beats={len(beats)} downbeat_phase={db0}")
print("breaks:", breaks)
print("rms/s:", sec)
