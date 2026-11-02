"""Synthesised sound bed for 「마지막 서명」 30s (music + SFX, no voice).

Usage: python3 tools/make_audio.py   (from the project root; needs numpy + ffmpeg)
Writes assets/audio/stems/{music,sfx}.mp3 and assets/audio/bed.mp3 (mixed, ~-16 LUFS, true peak <= -1 dBTP).
Cues follow docs/ads/naver-clip/01-last-signature.md §2/§4 (BGM + SFX columns):
  0.0  120BPM minimal pulse, kick on beat 1 · 2.8 short stop · 3.0 pulse + hats
  9.5  reverse sweep → 10.0 cut to silence (room tone + sub drone) · 11.6 single piano note
  14.0 piano 3-note motif, 15.5 string pad in · 18.0 full beat drop · 19.47 pen "톡" (mix peak)
  26.5 decay · 27.5 final chord + tail · 30.0 clean end
"""
import os
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(1102)
BPM = 120
BEAT = 60 / BPM


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def band(sig, lo, hi):
    """Brick-ish band-pass in the frequency domain with soft edges."""
    n = len(sig)
    S = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi < SR / 2:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(S * m, n)


def lowpass(sig, hi):
    return band(sig, 0, hi)


def env(n, a, d, curve=6.0):
    """attack seconds, then exponential decay over d seconds."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / max(d, 1e-4) * (curve / 6.0) * 1.0))
    return e


def norm(x):
    p = np.max(np.abs(x))
    return x / p if p > 0 else x


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(freq, d, detune=0.0):
    t = t_arr(d)
    out = np.zeros_like(t)
    for k in range(1, 14):
        f = freq * (1 + detune) * k
        if f > 9000:
            break
        out += np.sin(2 * np.pi * f * t) / k
    return out


def reverb(sig, seconds=1.6, mix=0.3):
    ir_n = int(seconds * SR)
    ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / (seconds / 5))
    ir = lowpass(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(sig) + ir_n
    wet = np.fft.irfft(np.fft.rfft(sig, n) * np.fft.rfft(ir, n), n)[: len(sig)]
    return sig * (1 - mix) + wet * mix * 3.0


# ------------------------------------------------------------------ instruments
def kick(level=1.0):
    t = t_arr(0.42)
    f = 46 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.16)
    click = band(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t / 0.004) * 0.35
    harm = np.sin(2 * ph) * np.exp(-t / 0.07) * 0.35  # audible on phone speakers
    return (body + click + harm) * level


def hat(level=0.25, d=0.045):
    n = int(0.12 * SR)
    x = band(rng.standard_normal(n), 7000, 16000) * env(n, 0.001, d)
    return norm(x) * level


def clap(level=0.5):
    n = int(0.3 * SR)
    x = band(rng.standard_normal(n), 900, 5000)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        i = int(o * SR)
        e[i:] += np.exp(-np.arange(n - i) / SR / 0.012)
    e += np.exp(-np.arange(n) / SR / 0.09) * 0.6
    return norm(x * e) * level


def pluck(m, d=0.22, level=0.3, bright=2600):
    x = saw(midi(m), d) * env(int(d * SR), 0.003, d / 3.2)
    return lowpass(x, bright) * level


def bass(m, d, level=0.5):
    t = t_arr(d)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
    e = np.minimum(1, t / 0.006) * np.exp(-t / (d * 0.9))
    return x * e * level


def piano(m, d=2.6, level=0.5):
    t = t_arr(d)
    f = midi(m)
    x = np.zeros_like(t)
    for k, a in enumerate([1, 0.55, 0.28, 0.16, 0.09, 0.05], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        x += a * np.sin(2 * np.pi * fk * t) * np.exp(-t / (d / (0.7 + 0.5 * k)))
    x *= np.minimum(1, t / 0.004)
    return x * level


def pad(ms, d, level=0.2, attack=1.2, release=0.8):
    x = np.zeros(int(d * SR))
    for m in ms:
        for dt in (-0.004, 0.0, 0.005):
            x += saw(midi(m), d, dt)
    x = lowpass(x, 1800)
    t = t_arr(d)
    e = np.minimum(1, t / attack) * np.minimum(1, np.maximum(0, (d - t) / release))
    return norm(x) * e * level


def noise_sweep(d, f0, f1, level, rise=True):
    n = int(d * SR)
    x = np.zeros(n)
    seg = int(0.03 * SR)
    for i in range(0, n, seg):
        p = i / n
        fc = f0 * (f1 / f0) ** p
        s = band(rng.standard_normal(seg * 2), fc * 0.6, fc * 1.6)[:seg]
        x[i:i + seg] += s[: len(x[i:i + seg])]
    x = norm(x)
    t = np.arange(n) / n
    e = t ** 2 if rise else (1 - t) ** 2
    return x * e * level


# ------------------------------------------------------------------ music
music = np.zeros(N)
DM, BB, FM, CM = [50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]
PROG = [DM, BB, FM, CM]
ROOTS = [38, 34, 41, 36]

# A 0–2.8: minimal tech pulse, kick on first beat (+ soft four-on-floor), short stop at 2.8
for b in range(6):
    t = b * BEAT
    if t < 2.8:
        place(music, kick(1.0 if b == 0 else 0.55), t)
for e in range(11):
    t = e * BEAT / 2
    if t < 2.75:
        place(music, pluck([69, 74][e % 2], level=0.22), t)
# B 3.0–9.5: pulse resumes + hi-hats
for b in range(13):
    t = 3.0 + b * BEAT
    if t < 9.5:
        place(music, kick(0.7), t)
        bar = int((t - 3.0) // 2) % 4
        place(music, bass(ROOTS[bar] + 12, BEAT * 0.9, 0.32), t)
for e in range(26):
    t = 3.0 + e * BEAT / 2
    if t < 9.5:
        bar = int((t - 3.0) // 2) % 4
        place(music, pluck(PROG[bar][e % 3] + 12, level=0.2), t)
        if e % 2 == 1:
            place(music, hat(0.22), t)
# 9.5 reverse sweep → cut at 10.0
rs = noise_sweep(0.5, 300, 6000, 0.55, rise=True)
place(music, rs, 9.5)
# fade out pulses under the sweep
i0, i1 = int(9.5 * SR), int(10.0 * SR)
music[i0:i1] *= np.linspace(1, 0.2, i1 - i0)
music[i1:int(11.55 * SR)] = 0.0
# 11.6 single piano note (with reverb), 14.0 three-note motif, 15.5 string pad
pn = np.zeros(N)
place(pn, piano(57, 3.2, 0.55), 11.6)
for k, (m, t) in enumerate([(62, 14.2), (65, 14.7), (69, 15.2), (62, 16.2), (65, 16.7), (67, 17.2)]):
    place(pn, piano(m, 2.4, 0.42 if k < 3 else 0.36), t)
music += reverb(pn, 2.2, 0.35)
pd = pad([50, 57, 62, 65], 2.5, 0.16, attack=1.2, release=0.3)
place(music, pd, 15.5)
place(music, pad([46, 53, 58, 62], 0.9, 0.2, attack=0.2, release=0.25), 17.1)
place(music, noise_sweep(1.2, 400, 5000, 0.25, rise=True), 16.8)

# 18.0–27.5: full beat drop
drop = np.zeros(N)
for b in range(19):
    t = 18.0 + b * BEAT
    if t >= 27.5:
        break
    bar = int((t - 18.0) // 2) % 4
    place(drop, kick(1.0), t)
    if b % 2 == 1:
        place(drop, clap(0.42), t)
    for s in range(2):
        place(drop, bass(ROOTS[bar], BEAT / 2 * 0.92, 0.55), t + s * BEAT / 2)
for e in range(76):
    t = 18.0 + e * BEAT / 4
    if t >= 27.5:
        break
    bar = int((t - 18.0) // 2) % 4
    place(drop, hat(0.16 if e % 2 else 0.1, 0.03), t)
    if e % 2 == 0:
        place(drop, pluck(PROG[bar][(e // 2) % 3] + 12, d=0.18, level=0.17, bright=3200), t)
for bar in range(5):
    t = 18.0 + bar * 2.0
    if t < 27.5:
        place(drop, pad([m + 12 for m in PROG[bar % 4]], 2.0, 0.12, attack=0.05, release=0.2), t)
# decay from 26.5 → 27.5
i0, i1 = int(26.5 * SR), int(27.5 * SR)
drop[i0:i1] *= np.linspace(1, 0.0, i1 - i0) ** 1.5
drop[i1:] = 0
music += drop
# 27.5 final chord (F add9) + reverb tail, clean end at 30.0
fin = np.zeros(N)
for m in (41, 53, 57, 60, 67):
    place(fin, piano(m, 2.5, 0.3), 27.5)
place(fin, pad([53, 57, 60, 67], 2.5, 0.14, attack=0.05, release=1.2), 27.5)
music += reverb(fin, 1.8, 0.35)

# ------------------------------------------------------------------ SFX
sfx = np.zeros(N)


def swoosh(d=0.18, lo=1200, hi=6000, level=0.4):
    n = int(d * SR)
    x = band(rng.standard_normal(n), lo, hi)
    t = np.arange(n) / n
    return norm(x) * np.sin(np.pi * t) ** 1.5 * level


def tick(level=0.25, f=3200):
    n = int(0.02 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.003) + band(rng.standard_normal(n), 2000, 8000) * np.exp(-t / 0.002) * 0.4) * level


def ding(level=0.3):
    t = t_arr(0.6)
    x = np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 2352 * t)
    return x * np.exp(-t / 0.16) * np.minimum(1, t / 0.002) * level


def click(level=0.4):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    a = band(rng.standard_normal(n), 1500, 7000) * np.exp(-t / 0.003)
    b = np.zeros(n)
    i = int(0.018 * SR)
    b[i:] = band(rng.standard_normal(n - i), 1000, 5000) * np.exp(-np.arange(n - i) / SR / 0.004) * 0.6
    return norm(a + b) * level


def error_tone(level=0.45):
    t = t_arr(0.26)
    f = 190 - 40 * t / 0.26
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.35 + np.sin(ph) + 0.4 * np.sin(2 * ph)
    x = lowpass(x, 1800)
    return norm(x) * np.minimum(1, t / 0.005) * np.exp(-t / 0.12) * level


def pen_tok(level=1.0):
    t = t_arr(0.5)
    wood = np.sin(2 * np.pi * 1050 * t) * np.exp(-t / 0.018) + 0.6 * np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.03)
    thump = np.sin(2 * np.pi * (90 + 60 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.09) * 0.9
    cl = band(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t / 0.002) * 0.6
    return (wood + thump + cl) * level


def crash(d=2.2, level=0.3):
    n = int(d * SR)
    x = band(rng.standard_normal(n), 3000, 15000)
    return norm(x) * env(n, 0.002, 0.55) * level


def pop(f=900, level=0.3):
    t = t_arr(0.09)
    ff = f * (1 + 0.6 * np.exp(-t / 0.01))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.03) * np.minimum(1, t / 0.001) * level


# C1: paper "슉슉슉", counter "띵", blink ticks from 1.5
for k, t in enumerate([0.0, 0.11, 0.22]):
    place(sfx, swoosh(0.16, 900 + 300 * k, 6000, 0.38), t)
place(sfx, ding(0.26), 0.3)
place(sfx, swoosh(0.35, 500, 4000, 0.35), 1.53)  # tilt-down whoosh
for k in range(3):
    place(sfx, tick(0.2), 2.0 + k * 16 / 30)
place(sfx, band(rng.standard_normal(int(0.07 * SR)), 300, 8000) * 0.25, 2.8)  # glitch
# C2: typing texture 3.0–5.9 (accelerating), check ticks
t = 3.05
while t < 5.85:
    place(sfx, tick(0.12 + 0.06 * rng.random(), 2400 + 1600 * rng.random()), t)
    t += 0.075 - 0.035 * ((t - 3.0) / 2.9) + 0.02 * rng.random()
for k, n in enumerate([165, 171, 177]):
    place(sfx, pop(1200 + 200 * k, 0.32), n / 30 + 1 / 30)
# C3: blink ticks, 4 clicks, error x2, reverse sweep (in music)
for k in range(3):
    place(sfx, tick(0.2), 6.55 + k * 16 / 30)
for n in [216, 226, 236, 246]:
    place(sfx, click(0.45), n / 30 + 1 / 30)
    place(sfx, band(rng.standard_normal(int(0.035 * SR)), 400, 9000) * 0.12, n / 30)
place(sfx, error_tone(0.5), 255 / 30 + 1 / 30)
place(sfx, error_tone(0.42), 255 / 30 + 0.36)
# C4: room tone + low sub drone 10.0–14.0
n = int(4.0 * SR)
room = band(rng.standard_normal(n), 80, 2500)
room = norm(room) * 0.012
tt = np.arange(n) / SR
drone = (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 110 * tt) + 0.25 * np.sin(2 * np.pi * 165 * tt)) * 0.06
drone *= np.minimum(1, tt / 1.2) * np.minimum(1, (4.0 - tt) / 0.6)
place(sfx, room + drone, 10.0)
# dissolve shimmer (soft)
place(sfx, noise_sweep(1.2, 6000, 2000, 0.05, rise=False), 10.2)
# C5: paper flip
pf = band(rng.standard_normal(int(0.4 * SR)), 1500, 7000)
pf *= (np.abs(np.sin(np.arange(len(pf)) / SR * 2 * np.pi * 22)) ** 2) * np.sin(np.pi * np.arange(len(pf)) / len(pf))
place(sfx, norm(pf) * 0.3, 14.05)
# C6: pen "톡" at contact f584 (mix peak), impact crash, ink scratch, riser, typo pops
place(sfx, pen_tok(1.0), 584 / 30 + 1 / 30)
place(sfx, crash(2.4, 0.22), 584 / 30 + 1 / 30)
ns = int(1.4 * SR)
scr = band(rng.standard_normal(ns), 2500, 7000) * (0.5 + 0.5 * np.abs(np.sin(np.arange(ns) / SR * 2 * np.pi * 9)))
scr *= np.minimum(1, np.arange(ns) / SR / 0.05) * np.minimum(1, (1.4 - np.arange(ns) / SR) / 0.2)
place(sfx, norm(scr) * 0.1, 585 / 30)
place(sfx, noise_sweep(0.8, 500, 8000, 0.3, rise=True), 20.2)
for k, t in enumerate([21.0, 21.15, 21.3, 21.3]):
    place(sfx, pop(700 + 150 * k, 0.3), t + 1 / 30)
# C7: swipe "휙", button "톡" + pulse
place(sfx, swoosh(0.4, 700, 7000, 0.45), 760 / 30 + 0.12)
place(sfx, swoosh(0.3, 400, 3000, 0.3), 780 / 30)
place(sfx, click(0.35), 798 / 30 + 1 / 30)
place(sfx, pop(1100, 0.22), 812 / 30 + 1 / 30)
# C8: signature finish "샥"
place(sfx, swoosh(0.28, 2500, 11000, 0.4), 27.5)

# ------------------------------------------------------------------ mix + write
mix = music * 0.62 + sfx * 0.9
# clean end at 30.0
fade = int(0.35 * SR)
mix[-fade:] *= np.linspace(1, 0, fade) ** 2
music[-fade:] *= np.linspace(1, 0, fade) ** 2

out_dir = os.path.join(ROOT, "assets", "audio")
os.makedirs(os.path.join(out_dir, "stems"), exist_ok=True)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


pk = np.max(np.abs(mix))
write_wav(os.path.join(out_dir, "stems", "music.wav"), music * 0.62 / pk * 0.5)
write_wav(os.path.join(out_dir, "stems", "sfx.wav"), sfx * 0.9 / pk * 0.5)
raw = os.path.join(out_dir, "stems", "mix-raw.wav")
write_wav(raw, mix / pk * 0.5)


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    I = float(txt.split("I:")[1].split("LUFS")[0])
    tp = float(txt.split("Peak:")[1].split("dBFS")[0])
    return I, tp


I, tp = measure(raw)
gain = -16.0 - I
final = os.path.join(out_dir, "bed.mp3")
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-af",
                f"volume={gain:.2f}dB,alimiter=limit=0.79:attack=1:release=60:level=false",
                "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k", final], check=True)
I2, tp2 = measure(final)
# one corrective pass if the limiter pulled loudness down
if I2 < -16.6:
    g2 = -16.0 - I2
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-af",
                    f"volume={gain + g2:.2f}dB,alimiter=limit=0.79:attack=1:release=60:level=false",
                    "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k", final], check=True)
    I2, tp2 = measure(final)
os.remove(raw)
for stem in ("music", "sfx"):  # keep stems small: wav -> mp3
    w = os.path.join(out_dir, "stems", stem + ".wav")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", w, "-c:a", "libmp3lame", "-b:a", "160k",
                    os.path.join(out_dir, "stems", stem + ".mp3")], check=True)
    os.remove(w)
print(f"raw I={I:.1f} LUFS tp={tp:.1f}  ->  bed.mp3 I={I2:.1f} LUFS true-peak={tp2:.1f} dBTP")
