"""BGM excerpt + two quiet SFX for 「마지막 서명」 (no synthesized music).

Usage (project root; numpy + ffmpeg):
  python3 tools/make_audio.py              -> assets/audio/mix-30s.mp3
  python3 tools/make_audio.py --variant 15 -> assets/audio/mix-15s.mp3 (+ copy in v15/assets/audio/)

Music: assets/music/source.mp3 = "Breaking News Intro" by kornevmusic (Pixabay 527939), user supplied.
The excerpt starts on a beat (beats/source.json) and plays at its natural level and tone: no filter,
no ducking (round 4: "먹먹해지는 효과는 빼줘"), and no stop either (round 5: the hook's short music stop
is gone; the 30s C2 cut moved from B7, where the music used to return, to the downbeat B8). The only
automation is the fade into the end. The quiet of C4/C5 is carried by the track's own drumless build.
SFX (client: "조잡한 효과음도 줄여봐"): exactly two per cut, both clean tones without noise — the CTA
tap (one sine, -20 dB under the music around it) and the pen touch of the signature (a soft wood
tone, -18 dB, riding the music's biggest hit). Cue times come from the picture (beats/cuts*.json
"sfx", written by tools/build.py — run the builder first). Master: -15 LUFS, true peak <= -1 dBTP.
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
OFFSET = {"30": 8.789, "15": 15.796}[VARIANT]
N = int(SR * DUR)

BEATS = json.load(open(os.path.join(ROOT, "beats", "source.json")))
_i0 = min(range(len(BEATS["beats"])), key=lambda k: abs(BEATS["beats"][k] - OFFSET))
GRID = [b - BEATS["beats"][_i0] for b in BEATS["beats"][_i0:]]


def B(k):
    k0 = int(k)
    return GRID[k0] + (k - k0) * (GRID[k0 + 1] - GRID[k0])


# ------------------------------------------------------------------ music excerpt (natural level and tone)
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{OFFSET:.4f}", "-t", f"{DUR + 0.5:.3f}",
                      "-i", os.path.join(ROOT, "assets/music/source.mp3"), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
mus = np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, 2)[:N]
if len(mus) < N:
    mus = np.vstack([mus, np.zeros((N - len(mus), 2))])
t = np.arange(N) / SR


def curve(points):
    """piecewise-linear dB curve over t from [(time, dB), ...]"""
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


db = lambda v: 10 ** (v / 20)
# Music is continuous from the excerpt's first sample: no stop, no duck, no filter (round 5, v6). The only gain
# automation is the 0.3 s fade at the very end. The excerpt offset puts the track's biggest hit (source 21.037)
# on the "You" stroke: video 12.248 s in the 30s (offset 8.789), 5.241 s in the 15s (offset 15.796).
g = curve([(0, 0), (DUR - 0.3, 0), (DUR, -40)])
music = mus * db(g)[:, None]


# ------------------------------------------------------------------ SFX: two clean tones
def t_arr(d):
    return np.arange(int(d * SR)) / SR


def tap_tone():
    """the CTA tap: one soft sine (660 Hz), 5 ms attack, short decay — no square, no noise"""
    tt = t_arr(0.2)
    return np.sin(2 * np.pi * 660 * tt) * np.minimum(1, tt / 0.005) * np.exp(-tt / 0.05)


def pen_wood():
    """the pen touch: a soft wood tone (two decaying partials), 2 ms attack, no click noise, no thump"""
    tt = t_arr(0.35)
    wood = np.sin(2 * np.pi * 1050 * tt) * np.exp(-tt / 0.02) + 0.6 * np.sin(2 * np.pi * 620 * tt) * np.exp(-tt / 0.035)
    return wood * np.minimum(1, tt / 0.002)


REL_DB = {"tap": -20.0, "pen": -18.0}   # level of the tone's first 80 ms against the music's RMS around it
SOUND = {"tap": tap_tone, "pen": pen_wood}
sfx = np.zeros(N)
CUES = json.load(open(os.path.join(ROOT, "beats", "cuts.json" if VARIANT == "30" else "cuts-15s.json")))["sfx"]
assert len(CUES) == 2 and {c["kind"] for c in CUES} == {"tap", "pen"}, CUES
for cue in CUES:
    sig = SOUND[cue["kind"]]()
    at = cue["t"] + 1 / 30                       # sound lands one frame after its picture
    i = int(round(at * SR))
    w0, w1 = max(0, i - int(0.3 * SR)), min(N, i + int(0.5 * SR))
    mrms = np.sqrt(np.mean(music[w0:w1] ** 2))
    srms = np.sqrt(np.mean(sig[: int(0.08 * SR)] ** 2))
    sig = sig * (mrms / srms) * db(REL_DB[cue["kind"]])
    j = min(N, i + len(sig))
    sfx[i:j] += sig[: j - i]
    print(f"  sfx {cue['kind']:<5s} t={cue['t']:.3f}s  {REL_DB[cue['kind']]:+.0f} dB vs music RMS {20 * np.log10(mrms):.1f} dBFS")

mix = music + sfx[:, None]


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
