"""BGM excerpt + beat-synced SFX for 「마지막 서명」 (no synthesized music).

Usage (project root; numpy + ffmpeg):
  python3 tools/make_audio.py              -> assets/audio/mix-30s.mp3
  python3 tools/make_audio.py --variant 15 -> assets/audio/mix-15s.mp3 (+ copy in v15/assets/audio/)

Music: assets/music/source.mp3 = "Breaking News Intro" by kornevmusic (Pixabay 527939), user supplied.
The excerpt starts on a beat (beats/source.json); automation below is volume and a low-pass
sweep only (the track has no break where the story needs silence). SFX are short noise/transient
effects (click, error "뚱", pen "톡", tick) placed at the picture's cue times (beats/cuts*.json "sfx",
written by tools/build.py — run the builder first). No whips or swipes; no tonal music is generated. Master: -15 LUFS integrated target, true peak <= -1 dBTP.
"""
import json
import os
import shutil
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "30"
DUR = 15.0 if VARIANT == "15" else 30.0
OFFSET = {"30": 1.776, "15": 10.971}[VARIANT]
N = int(SR * DUR)
rng = np.random.default_rng(1102)

BEATS = json.load(open(os.path.join(ROOT, "beats", "source.json")))
_i0 = min(range(len(BEATS["beats"])), key=lambda k: abs(BEATS["beats"][k] - OFFSET))
GRID = [b - BEATS["beats"][_i0] for b in BEATS["beats"][_i0:]]


def B(k):
    k0 = int(k)
    return GRID[k0] + (k - k0) * (GRID[k0 + 1] - GRID[k0])


# ------------------------------------------------------------------ music excerpt
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFFSET:.4f}", "-t", f"{DUR + 0.5:.3f}",
                      "-i", os.path.join(ROOT, "assets/music/source.mp3"), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
mus = np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, 2)[:N]
if len(mus) < N:
    mus = np.vstack([mus, np.zeros((N - len(mus), 2))])
t = np.arange(N) / SR


def lowpass(x, fc):
    S = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(S * (1 / (1 + (f / fc) ** 4))[:, None], len(x), axis=0)


def curve(points, kind="lin"):
    """piecewise curve over t from [(time, value), ...]"""
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


# low-pass sweep = crossfade along a ladder of low-passed copies by log cutoff
LADDER = [250.0, 600.0, 1500.0, 4000.0, 20000.0]
copies = [lowpass(mus, fc) for fc in LADDER[:-1]] + [mus]


def sweep(fc_curve):
    lf = np.log(np.clip(fc_curve, LADDER[0], LADDER[-1]))
    ll = np.log(LADDER)
    out = np.zeros_like(mus)
    for i in range(len(LADDER) - 1):
        w = np.clip((lf - ll[i]) / (ll[i + 1] - ll[i]), 0, 1)
        inside = (lf >= ll[i]) & (lf <= ll[i + 1])
        out[inside] = (copies[i][inside] * (1 - w[inside, None]) + copies[i + 1][inside] * w[inside, None])
    out[lf <= ll[0]] = copies[0][lf <= ll[0]]
    out[lf >= ll[-1]] = copies[-1][lf >= ll[-1]]
    return out


db = lambda v: 10 ** (v / 20)
if VARIANT == "30":
    # 2.70–3.05 short stop (spec C1 "2.8s 짧은 스톱"), slam back on the C2 cut (beat 7)
    # C3 toast → C4: low-pass sweep 20k→250 Hz and duck -13 dB (spec "리버스 스윕 → 무음", C4 정적)
    # C5: the track's own drumless build; filter opens and level returns into the pen hit (B44 = 19.26 s)
    # end: lands on the downbeat hit B68 (29.78 s), 0.2 s fade to 30.0
    fc = curve([(0, 20000), (B(21), 20000), (B(23), 250), (B(32), 250), (B(39), 4000), (B(43.5), 20000), (DUR, 20000)])
    g = curve([(0, 0), (2.69, 0), (2.70, -40), (B(7) - 0.012, -40), (B(7), 0), (B(21), 0), (B(23), -13), (B(32), -13),
               (B(40), -4), (B(43.5), 0), (B(68), 0), (DUR, -40)])
else:
    # hook glitch stop, toast → C4' sweep down + duck (falls into the track's drumless build), open into the hit B23
    fc = curve([(0, 20000), (B(8), 20000), (B(11), 300), (B(16), 500), (B(21), 4000), (B(22.5), 20000), (DUR, 20000)])
    g = curve([(0, 0), (B(4.75), 0), (B(4.75) + 0.01, -40), (B(5) - 0.012, -40), (B(5), 0), (B(8), 0), (B(11), -11),
               (B(18), -8), (B(22.5), 0), (B(34), 0), (DUR, -40)])
music = sweep(fc) * db(g)[:, None]


# ------------------------------------------------------------------ SFX (reused from the first draft, noise/transient based)
def t_arr(d):
    return np.arange(int(d * SR)) / SR


def band(sig, lo, hi):
    n = len(sig)
    S = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi < SR / 2:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(S * m, n)


def norm(x):
    p = np.max(np.abs(x))
    return x / p if p > 0 else x


def tick(level=0.3, f=3200):
    n = int(0.02 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.003) + band(rng.standard_normal(n), 2000, 8000) * np.exp(-tt / 0.002) * 0.4) * level


def click(level=0.5):
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    a = band(rng.standard_normal(n), 1500, 7000) * np.exp(-tt / 0.003)
    b = np.zeros(n)
    i = int(0.018 * SR)
    b[i:] = band(rng.standard_normal(n - i), 1000, 5000) * np.exp(-np.arange(n - i) / SR / 0.004) * 0.6
    return norm(a + b) * level


def error_tone(level=0.55):
    tt = t_arr(0.26)
    f = 190 - 40 * tt / 0.26
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.35 + np.sin(ph) + 0.4 * np.sin(2 * ph)
    x = band(x, 0, 1800)
    return norm(x) * np.minimum(1, tt / 0.005) * np.exp(-tt / 0.12) * level


def pen_tok(level=1.0):
    tt = t_arr(0.5)
    wood = np.sin(2 * np.pi * 1050 * tt) * np.exp(-tt / 0.018) + 0.6 * np.sin(2 * np.pi * 620 * tt) * np.exp(-tt / 0.03)
    thump = np.sin(2 * np.pi * (90 + 60 * np.exp(-tt / 0.02)) * tt) * np.exp(-tt / 0.09) * 0.9
    cl = band(rng.standard_normal(len(tt)), 2500, 9000) * np.exp(-tt / 0.002) * 0.6
    return (wood + thump + cl) * level


sfx = np.zeros(N)


def place(sig, at, gain=1.0):
    at += 1 / 30  # sound lands one frame after its picture
    i = int(round(at * SR))
    j = min(N, i + len(sig))
    if i < N:
        sfx[i:j] += sig[: j - i] * gain


# SFX cues come from the picture (tools/build.py writes them into beats/cuts*.json), so sound and
# picture cannot drift apart. Art direction v3: restraint — only what the story needs, kept quiet:
# the generate presses, the error toast (one tone), the pen touch of the signature (on the music's
# biggest hit, so it rides the hit rather than towering over it), a soft tick when the button arrives.
CUES = json.load(open(os.path.join(ROOT, "beats", "cuts.json" if VARIANT == "30" else "cuts-15s.json")))["sfx"]
SOUND = {
    "click": lambda: click(0.32),
    "error": lambda: error_tone(0.38),
    "pen": lambda: pen_tok(0.62),
    "tick": lambda: tick(0.16, 1900),
}
for cue in CUES:
    place(SOUND[cue["kind"]](), cue["t"], 1.0)

mix = music + sfx[:, None] * 0.5


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    return float(txt.split("I:")[1].split("LUFS")[0]), float(txt.split("Peak:")[1].split("dBFS")[0])


out_dir = os.path.join(ROOT, "assets", "audio")
os.makedirs(out_dir, exist_ok=True)
tmp = os.path.join(out_dir, f".mix-raw-{VARIANT}.wav")
write_wav(tmp, mix / np.max(np.abs(mix)) * 0.5)
I, tp = measure(tmp)
final = os.path.join(out_dir, f"mix-{VARIANT}s.mp3")
TARGET = -15.0
gain = TARGET - I
for _ in range(3):
    # limiter at -2.5 dBFS sample peak with 4x oversampling so the true peak stays under -1 dBTP after encoding
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-af",
                    f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.75:attack=2:release=80:level=false,aresample=48000",
                    "-c:a", "libmp3lame", "-b:a", "256k", final], check=True)
    I2, tp2 = measure(final)
    if abs(I2 - TARGET) < 0.4:
        break
    gain += TARGET - I2
os.remove(tmp)
if VARIANT == "15" and os.path.isdir(os.path.join(ROOT, "v15")):
    os.makedirs(os.path.join(ROOT, "v15", "assets", "audio"), exist_ok=True)
    shutil.copy(final, os.path.join(ROOT, "v15", "assets", "audio", os.path.basename(final)))
print(f"mix-{VARIANT}s.mp3: I={I2:.1f} LUFS, true peak={tp2:.1f} dBTP (excerpt {OFFSET:.3f}–{OFFSET + DUR:.3f}s of source)")
