"""Synthesize the draft sound bed for 「AI에게 물었다」 30s (no VO).

Usage: python3 tools/make_audio.py [--cut 15]   (run from the project root; needs numpy + ffmpeg)
  --cut 15 writes bgm-15s.wav / sfx-15s.wav (15s cues, §3) instead of the 30s stems.
Writes assets/audio/bgm.wav (music stem) and assets/audio/sfx.wav (effects stem),
48 kHz stereo 16-bit, both exactly 30.0 s. The two stems are scaled by one shared gain
so their sum measures about -16 LUFS integrated with true peak <= -1 dBTP (ffmpeg ebur128).

Cues follow docs/ads/naver-clip/05-ask-ai.md §2 (30s):
  1.5 synth pulse (with typing dots) · 3.0–12.5 lo-fi beat 90 BPM · 12.5 hard BGM cut (silence is the joke)
  18.0 acoustic + piano upbeat (120 BPM) · 23.5–27 build · 27.0 resolve · 28.2 last chime, fade to 30.0
All randomness is seeded, so the files are reproducible.
"""
import json
import os
import re
import subprocess
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(5)


def t_arr(d):
    return np.arange(int(SR * d)) / SR


def place(buf, sig, t, gain=1.0, pan=0.0):
    """Add mono sig into stereo buf at time t (s)."""
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    r = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    buf[i : i + len(sig), 0] += sig * gain * l
    buf[i : i + len(sig), 1] += sig * gain * r


def fft_filter(x, lo=None, hi=None, order=2):
    """Zero-phase Butterworth-shaped magnitude filter in the frequency domain."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, n)


def env(n, a=0.005, d=0.2, shape="exp"):
    t = np.arange(n) / SR
    att = np.clip(t / max(a, 1e-4), 0, 1)
    dec = np.exp(-t / d) if shape == "exp" else np.clip(1 - t / d, 0, 1)
    return att * dec


def noise(d):
    return rng.standard_normal(int(SR * d))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- instruments
def kick(d=0.35):
    t = t_arr(d)
    f = 50 + 70 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(len(t), 0.002, 0.16) + 0.3 * fft_filter(noise(d), lo=1500) * env(len(t), 0.0005, 0.006)


def snare(d=0.25):
    t = t_arr(d)
    body = np.sin(2 * np.pi * 190 * t) * env(len(t), 0.001, 0.05)
    nz = fft_filter(noise(d), lo=1200, hi=7000) * env(len(t), 0.001, 0.09)
    return 0.5 * body + 0.6 * nz


def rim(d=0.12):
    t = t_arr(d)
    return (np.sin(2 * np.pi * 1700 * t) * 0.5 + fft_filter(noise(d), lo=2000, hi=6000) * 0.5) * env(len(t), 0.0005, 0.02)


def hat(d=0.06, open_=False):
    t = t_arr(0.2 if open_ else d)
    return fft_filter(noise(len(t) / SR), lo=7000) * env(len(t), 0.0005, 0.06 if open_ else 0.014)


def rhodes(m, d=2.6, vel=1.0):
    t = t_arr(d)
    f = midi(m)
    trem = 1 + 0.1 * np.sin(2 * np.pi * 4.2 * t)
    s = np.sin(2 * np.pi * f * t) + 0.28 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4) + 0.08 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.2)
    return s * env(len(t), 0.008, 1.4) * trem * vel


def bass(m, d=0.6, vel=1.0):
    t = t_arr(d)
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(len(t), 0.01, 0.35) * vel


def piano(m, d=2.0, vel=1.0):
    t = t_arr(d)
    f = midi(m)
    s = np.zeros_like(t)
    for k in range(1, 7):
        fk = f * k * (1 + 0.0004 * k * k)
        s += np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.2 + 0.9 * k)) / k
    return s * env(len(t), 0.003, 3.0) * vel


def pluck(m, d=1.2, vel=1.0, bright=0.5):
    """Karplus-Strong, vectorised one delay-line block at a time."""
    f = midi(m)
    p = int(SR / f)
    n = int(SR * d)
    out = np.zeros(n + p + 1)
    out[: p + 1] = fft_filter(rng.uniform(-1, 1, p + 1), hi=2000 + 6000 * bright)
    decay = 0.996
    i = p + 1
    while i < len(out):
        j = min(i + p, len(out))
        prev = out[i - p - 1 : j - p - 1]
        prev2 = out[i - p : j - p]
        out[i:j] = decay * 0.5 * (prev + prev2)
        i = j
    return out[p + 1 : p + 1 + n] * vel * env(n, 0.001, 10.0)


def bell(freqs, d=1.6, vel=1.0):
    t = t_arr(d)
    s = np.zeros_like(t)
    for f in freqs:
        s += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9) + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
    return s / len(freqs) * env(len(t), 0.004, 5) * vel


# ---------------------------------------------------------------- sfx
def key_click(heavy=False):
    d = 0.05
    t = t_arr(d)
    c = fft_filter(noise(d), lo=1800 if not heavy else 900, hi=6500) * env(len(t), 0.0003, 0.006 if not heavy else 0.012)
    body = np.sin(2 * np.pi * (240 if not heavy else 160) * t) * env(len(t), 0.0005, 0.012)
    return 0.7 * c + 0.4 * body


def whoosh(d=0.45, up=True, lo=400, hi=5000):
    n = int(SR * d)
    t = np.arange(n) / SR
    nz = noise(d)
    # sweep: crossfade a low- and a high-band version
    a = fft_filter(nz, lo=lo, hi=lo * 3)
    b = fft_filter(nz, lo=hi / 3, hi=hi)
    x = t / d if up else 1 - t / d
    s = a * (1 - x) + b * x
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return s * shape


def tail_whoosh():
    s = whoosh(0.5, up=True, lo=600, hi=6000)
    return s[len(s) // 2 :] * np.linspace(1, 0, len(s) - len(s) // 2)


def tick(f=2000, d=0.03):
    t = t_arr(d)
    return np.sin(2 * np.pi * f * t) * env(len(t), 0.0005, 0.006)


def pop(f0=900, f1=420, d=0.09):
    t = t_arr(d)
    f = f1 + (f0 - f1) * np.exp(-t / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.035)


def boing():
    # 🙂 "뿅": quick upward glide
    d = 0.22
    t = t_arr(d)
    f = 480 + 1100 * (1 - np.exp(-t / 0.05))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * env(len(t), 0.002, 0.08)


def tap():
    d = 0.08
    t = t_arr(d)
    return (np.sin(2 * np.pi * 1150 * t) * 0.6 + np.sin(2 * np.pi * 620 * t) * 0.5) * env(len(t), 0.0005, 0.018) + 0.2 * fft_filter(noise(d), lo=2500) * env(len(t), 0.0003, 0.004)


def marker():
    d = 0.24
    t = t_arr(d)
    s = fft_filter(noise(d), lo=2500, hi=9000)
    shape = np.sin(np.pi * t / d) ** 1.5
    grain = 1 + 0.5 * np.sin(2 * np.pi * 38 * t)
    return s * shape * grain


def clock_tick(hi=True):
    d = 0.05
    t = t_arr(d)
    f = 2300 if hi else 1700
    return (np.sin(2 * np.pi * f * t) + 0.4 * fft_filter(noise(d), lo=3000)) * env(len(t), 0.0003, 0.007)


def cricket():
    out = np.zeros(int(SR * 0.6))
    for k in range(2):
        for j in range(3):
            d = 0.035
            t = t_arr(d)
            s = np.sin(2 * np.pi * 4600 * t) * np.sin(np.pi * t / d) ** 2
            i = int(SR * (k * 0.28 + j * 0.05))
            out[i : i + len(s)] += s
    return out


def thump():
    d = 0.5
    t = t_arr(d)
    f = 48 + 60 * np.exp(-t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.18) + 0.25 * np.sin(2 * np.pi * 220 * t) * env(len(t), 0.001, 0.04)


def sweep_shine():
    s = whoosh(0.7, up=True, lo=1500, hi=12000)
    t = t_arr(0.7)
    shimmer = sum(np.sin(2 * np.pi * f * t) for f in (2637, 3136, 3951)) / 3 * np.sin(np.pi * t / 0.7) ** 2
    return s + 0.12 * shimmer


# ---------------------------------------------------------------- music
def build_music():
    m = np.zeros((N, 2))
    # 1.5 s: minimal synth pulse, once (with the typing dots)
    t = t_arr(0.9)
    pulse = (np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 330 * t) + 0.3 * np.sin(2 * np.pi * 440.5 * t)) * env(len(t), 0.01, 0.28)
    place(m, fft_filter(pulse, hi=2500), 1.5, 0.35)

    # 3.0–12.5: lo-fi beat, 90 BPM, plain
    beat = 60 / 90
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
    roots = [41, 40, 38, 36]
    t0 = 3.0
    lofi = np.zeros((N, 2))
    nbeats = int((12.5 - t0) / beat) + 1
    for b in range(nbeats):
        tb = t0 + b * beat
        if tb >= 12.5:
            break
        bar, pos = divmod(b, 4)
        if pos == 0:
            for k, note in enumerate(chords[bar % 4]):
                place(lofi, rhodes(note, d=beat * 4 + 0.3, vel=0.22), tb + 0.012 * k, 1.0, pan=-0.25 + 0.17 * k)
        if pos in (0, 2):
            place(lofi, kick(), tb, 0.75)
            place(lofi, bass(roots[bar % 4], d=beat * 1.6), tb, 0.35)
        if pos in (1, 3):
            place(lofi, snare(), tb, 0.32, pan=0.05)
        if pos == 3 and bar % 2 == 1:
            place(lofi, kick(), tb + beat * 0.5, 0.45)
        for e in range(2):  # swung eighth hats
            place(lofi, hat(), tb + e * beat * 0.58, 0.18 if e == 0 else 0.11, pan=0.3)
    # crackle
    cr = np.zeros(N)
    idx = rng.integers(int(3.0 * SR), int(12.5 * SR), 420)
    cr[idx] = rng.uniform(-1, 1, len(idx))
    cr = fft_filter(cr, lo=1500, hi=8000) * 0.6
    lofi[:, 0] += cr
    lofi[:, 1] += cr
    for c in range(2):
        lofi[:, c] = fft_filter(lofi[:, c], hi=5200, order=2)  # soften = lo-fi
    # 12.5: hard cut (12 ms ramp only to avoid a click)
    cut = int(12.5 * SR)
    ramp = int(0.012 * SR)
    lofi[cut - ramp : cut] *= np.linspace(1, 0, ramp)[:, None]
    lofi[cut:] = 0
    # fade in over the first bar
    a = int(3.0 * SR)
    lofi[a : a + int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    m += lofi

    # 18.0–30.0: acoustic guitar + piano upbeat, 120 BPM (beat 0.5 s, bar 2 s)
    up = np.zeros((N, 2))
    prog = [  # (start, chord midi notes for guitar, root, piano top melody notes)
        (18.0, [48, 55, 60, 64, 67], 36, [76, 79]),  # C
        (20.0, [43, 50, 55, 59, 62], 31, [74, 79]),  # G
        (22.0, [45, 52, 57, 60, 64], 33, [72, 76]),  # Am
        (24.0, [41, 48, 53, 57, 60], 29, [72, 77]),  # F
        (26.0, [43, 50, 55, 59, 62], 31, [74, 71]),  # G (build)
    ]
    for (ts, ch, root, mel) in prog:
        build = ts >= 24.0
        pattern = [0, 0.75, 1.0, 1.5, 1.75] if not build else [0, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75]
        length = 2.0 if ts < 26.0 else 1.0
        for p in pattern:
            if p >= length:
                continue
            tb = ts + p
            down = (p * 2) % 1 == 0
            for k, note in enumerate(ch if down else ch[2:]):
                place(up, pluck(note, d=0.9, vel=0.30 if down else 0.2, bright=0.55), tb + (0.009 * k if down else 0.006 * (4 - k)), 1.0, pan=-0.35)
        for p in [0, 1.0] if length == 2.0 else [0, 0.5]:
            place(up, kick(), ts + p, 0.55)
            place(up, bass(root, d=0.9), ts + p, 0.32)
        for p in [0.5, 1.5] if length == 2.0 else [0.5]:
            place(up, snare(0.2) * 0.6, ts + p, 0.3, pan=0.1)
            place(up, rim() * 0.4, ts + p, 0.3, pan=0.1)
        for e in range(int(length * 4)):
            place(up, hat(0.05), ts + e * 0.25, 0.1 if e % 2 else 0.14, pan=0.35)
        for j, note in enumerate(mel):
            place(up, piano(note, d=1.8, vel=0.32), ts + j * 1.0 + (0.5 if build else 0), 1.0, pan=0.25)
    # 27.0: resolve on C — strum + piano chord; 28.2 last chime + sustained Cmaj9
    for k, note in enumerate([48, 55, 60, 64, 67, 72]):
        place(up, pluck(note, d=2.5, vel=0.32, bright=0.4), 27.0 + 0.012 * k, 1.0, pan=-0.3)
    for note in [60, 64, 67, 71, 74]:
        place(up, piano(note, d=3.0, vel=0.2), 27.0, 1.0, pan=0.2)
    place(up, kick(), 27.0, 0.6)
    place(up, bass(36, d=2.5), 27.0, 0.35)
    for note in [48, 55, 62, 64, 71]:
        place(up, rhodes(note, d=1.9, vel=0.16), 28.2, 1.0)
    # fade out the tail 29.0–30.0
    a = int(29.0 * SR)
    up[a:] *= np.linspace(1, 0, N - a)[:, None] ** 1.5
    m += up
    return m


def build_sfx():
    s = np.zeros((N, 2))
    place(s, tail_whoosh(), 0.0, 0.25)                         # C1 전송 "슝" 꼬리
    place(s, tick(1900), 1.5, 0.35)                            # 타이핑 점 틱
    for k in range(3):
        place(s, tick(2400, 0.02), 1.65 + k * 0.24, 0.12)
    place(s, whoosh(0.5, up=False, lo=300, hi=4000), 2.95, 0.35)  # C2 스크롤 휙
    # C2 타이핑 틱 (글자마다 하나씩은 과하니 2글자에 1번)
    for k, tt in enumerate(np.linspace(3.6, 6.35, 17)):
        place(s, key_click(), tt + rng.uniform(-0.02, 0.02), 0.16 + 0.04 * rng.random(), pan=rng.uniform(-0.2, 0.2))
    place(s, bell([392.0, 588.0], d=1.2), 6.47, 0.28)          # 저음 "띵"
    place(s, marker(), 7.0, 0.4, pan=-0.15)                    # 마커 "쓱" ×2
    place(s, marker(), 7.28, 0.36, pan=0.15)
    for tt in np.linspace(8.15, 8.9, 7):
        place(s, key_click(), tt, 0.16, pan=rng.uniform(-0.2, 0.2))
    place(s, pop(), 9.0, 0.35)                                 # 팝
    # C4 키보드 · 백스페이스 2회 · 전송 "슝"
    place(s, key_click(True), 10.3, 0.3)
    place(s, key_click(True), 10.42, 0.3)
    for tt in np.linspace(10.55, 11.1, 12):
        place(s, key_click(), tt + rng.uniform(-0.01, 0.01), 0.22, pan=rng.uniform(-0.25, 0.25))
    place(s, tap(), 11.18, 0.25)
    place(s, whoosh(0.4, up=True, lo=500, hi=7000), 11.22, 0.5)
    # C5 초침 틱 (BGM 없음) + 귀뚜라미 1회
    for k, tt in enumerate(np.arange(12.6, 14.9, 0.5)):
        place(s, clock_tick(k % 2 == 0), tt, 0.3)
    place(s, cricket(), 14.4, 0.12, pan=0.3)
    # C6 말풍선 팝 · 🙂 "뿅" · 탭 "톡"
    place(s, pop(700, 380, 0.08), 15.08, 0.22)
    place(s, boing(), 16.28, 0.4)
    place(s, tap(), 17.62, 0.42)
    # C7 화이트 스윕 "샤악" · 따뜻한 차임
    place(s, sweep_shine(), 17.95, 0.45)
    place(s, bell([1046.5, 1318.5, 1568.0], d=1.8), 18.6, 0.22)
    # C8 팝 · 말풍선 팝 · 카운트 틱
    place(s, pop(), 21.0, 0.25)
    place(s, pop(820, 400), 21.65, 0.3)
    for v in range(10, 61, 10):  # count 0→60 power2.out over 0.7 s from 21.8
        p = 1 - np.sqrt(1 - v / 60)
        place(s, tick(2600, 0.025), 21.8 + 0.7 * p, 0.2)
    # C9 버튼 "톡" (바운스 · 탭 루프)
    place(s, tap(), 24.92, 0.32)
    place(s, tap(), 26.1, 0.38)
    # C10 착지 "둥" ×2 · 마지막 차임
    place(s, thump(), 27.15, 0.6)
    place(s, thump(), 27.75, 0.55)
    place(s, bell([1318.5, 1568.0, 2093.0], d=1.8), 28.2, 0.2)
    return s


def build_music15():
    """15s cues (§3): 1.5 pulse · 3.0 lo-fi · 6.0 BGM cut · 8.5 acoustic upbeat · 12.5 resolve."""
    m = np.zeros((N, 2))
    t = t_arr(0.9)
    pulse = (np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 330 * t) + 0.3 * np.sin(2 * np.pi * 440.5 * t)) * env(len(t), 0.01, 0.28)
    place(m, fft_filter(pulse, hi=2500), 1.5, 0.35)
    beat = 60 / 90
    chords = [[53, 57, 60, 64], [52, 55, 59, 62]]
    roots = [41, 40]
    lofi = np.zeros((N, 2))
    for b in range(8):
        tb = 3.0 + b * beat
        if tb >= 6.0:
            break
        bar, pos = divmod(b, 4)
        if pos == 0:
            for k, note in enumerate(chords[bar % 2]):
                place(lofi, rhodes(note, d=beat * 4 + 0.3, vel=0.22), tb + 0.012 * k, 1.0, pan=-0.25 + 0.17 * k)
        if pos in (0, 2):
            place(lofi, kick(), tb, 0.75)
            place(lofi, bass(roots[bar % 2], d=beat * 1.6), tb, 0.35)
        if pos in (1, 3):
            place(lofi, snare(), tb, 0.32, pan=0.05)
        for e in range(2):
            place(lofi, hat(), tb + e * beat * 0.58, 0.18 if e == 0 else 0.11, pan=0.3)
    for c in range(2):
        lofi[:, c] = fft_filter(lofi[:, c], hi=5200, order=2)
    cut, ramp = int(6.0 * SR), int(0.012 * SR)
    lofi[cut - ramp : cut] *= np.linspace(1, 0, ramp)[:, None]
    lofi[cut:] = 0
    a = int(3.0 * SR)
    lofi[a : a + int(0.2 * SR)] *= np.linspace(0, 1, int(0.2 * SR))[:, None]
    m += lofi
    up = np.zeros((N, 2))
    prog = [(8.5, [48, 55, 60, 64, 67], 36, [76, 79]), (10.5, [45, 52, 57, 60, 64], 33, [72, 76])]
    for (ts, ch, root, mel) in prog:
        for p in [0, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75]:
            tb = ts + p
            down = (p * 2) % 1 == 0
            for k, note in enumerate(ch if down else ch[2:]):
                place(up, pluck(note, d=0.9, vel=0.30 if down else 0.2, bright=0.55), tb + (0.009 * k if down else 0.006 * (4 - k)), 1.0, pan=-0.35)
        for p in [0, 1.0]:
            place(up, kick(), ts + p, 0.55)
            place(up, bass(root, d=0.9), ts + p, 0.32)
        for p in [0.5, 1.5]:
            place(up, snare(0.2) * 0.6, ts + p, 0.3, pan=0.1)
        for e in range(8):
            place(up, hat(0.05), ts + e * 0.25, 0.1 if e % 2 else 0.14, pan=0.35)
        for j, note in enumerate(mel):
            place(up, piano(note, d=1.8, vel=0.32), ts + j * 1.0, 1.0, pan=0.25)
    # 12.5 해결 코드 (F → C), ring out, fade 14.0–15.0
    for k, note in enumerate([41, 48, 53, 57, 60]):
        place(up, pluck(note, d=0.6, vel=0.26, bright=0.4), 12.0 + 0.01 * k, 1.0, pan=-0.3)
    for k, note in enumerate([48, 55, 60, 64, 67, 72]):
        place(up, pluck(note, d=2.5, vel=0.32, bright=0.4), 12.5 + 0.012 * k, 1.0, pan=-0.3)
    for note in [60, 64, 67, 71, 74]:
        place(up, piano(note, d=2.5, vel=0.2), 12.5, 1.0, pan=0.2)
    place(up, kick(), 12.5, 0.6)
    place(up, bass(36, d=2.0), 12.5, 0.35)
    a = int(14.0 * SR)
    up[a:] *= np.linspace(1, 0, N - a)[:, None] ** 1.5
    m += up
    return m


def build_sfx15():
    s = np.zeros((N, 2))
    place(s, tail_whoosh(), 0.0, 0.25)
    place(s, tick(1900), 1.5, 0.35)
    for k in range(3):
        place(s, tick(2400, 0.02), 1.65 + k * 0.24, 0.12)
    for tt in np.linspace(3.15, 4.15, 7):                      # C2 타이핑
        place(s, key_click(), tt + rng.uniform(-0.02, 0.02), 0.17, pan=rng.uniform(-0.2, 0.2))
    place(s, marker(), 4.3, 0.4, pan=-0.1)                     # 마커 "쓱"
    place(s, pop(), 4.5, 0.3)                                  # 칩
    for tt in np.linspace(4.6, 4.92, 6):                       # C3 키보드 → 전송
        place(s, key_click(), tt, 0.18, pan=rng.uniform(-0.25, 0.25))
    place(s, whoosh(0.35, up=True, lo=500, hi=7000), 4.95, 0.45)
    for k, tt in enumerate(np.arange(6.05, 6.8, 0.35)):        # 초침 틱 (BGM 컷)
        place(s, clock_tick(k % 2 == 0), tt, 0.3)
    place(s, pop(700, 380, 0.08), 6.85, 0.22)
    place(s, boing(), 7.45, 0.4)                               # 🙂 "뿅"
    place(s, tap(), 8.2, 0.42)                                 # 탭
    place(s, sweep_shine(), 8.45, 0.45)                        # 스윕
    place(s, bell([1046.5, 1318.5, 1568.0], d=1.8), 8.95, 0.22)  # 차임
    place(s, pop(820, 400), 10.7, 0.3)                         # 상담사 말풍선
    for v in range(10, 61, 10):
        p = 1 - np.sqrt(1 - v / 60)
        place(s, tick(2600, 0.025), 10.85 + 0.65 * p, 0.2)
    place(s, thump(), 12.52, 0.6)                              # 착지 "둥"
    place(s, tap(), 12.55, 0.25)                               # 버튼 팝
    place(s, thump(), 13.12, 0.55)
    return s


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i_lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1))
    return i_lufs, tp


def limiter_gain(mix, ceiling, w=480):
    """Look-ahead peak limiter as a gain envelope (same envelope goes on both stems)."""
    a = np.max(np.abs(mix), axis=1)
    req = np.minimum(1.0, ceiling / np.maximum(a, 1e-9))
    pad = (-len(req)) % w
    r = np.concatenate([req, np.ones(pad)]).reshape(-1, w).min(axis=1)
    r = np.minimum(r, np.minimum(np.r_[r[1:], 1.0], np.r_[1.0, r[:-1]]))
    g = np.repeat(r, w)[: len(req)]
    k = np.hanning(2 * w)
    k /= k.sum()
    return np.convolve(g, k, mode="same")[:, None]


def main():
    global DUR, N
    import sys
    cut15 = "--cut" in sys.argv and sys.argv[sys.argv.index("--cut") + 1] == "15"
    out = os.path.join(ROOT, "assets", "audio")
    os.makedirs(out, exist_ok=True)
    if cut15:
        DUR, N = 15.0, int(SR * 15.0)
        music, sfx = build_music15(), build_sfx15()
    else:
        music = build_music()
        sfx = build_sfx()
    suffix = "-15s" if cut15 else ""
    music *= 0.55  # bed sits a few dB under the effects
    tmp = os.path.join(out, "_mix_tmp.wav")
    target, ceiling = -16.0, 10 ** (-2.6 / 20)  # sample-peak ceiling leaves room for true peak + AAC
    gain = 1.0
    for _ in range(8):
        raw = (music + sfx) * gain
        g = limiter_gain(raw, ceiling)
        write_wav(tmp, raw * g)
        i_lufs, tp = measure(tmp)
        if abs(i_lufs - target) < 0.15:
            break
        gain *= 10 ** ((target - i_lufs) / 20)
    raw_m, raw_s = music * gain, sfx * gain
    g = limiter_gain(raw_m + raw_s, ceiling)
    write_wav(tmp, (raw_m + raw_s) * g)
    i_lufs, tp = measure(tmp)
    os.remove(tmp)
    write_wav(os.path.join(out, "bgm" + suffix + ".wav"), raw_m * g)
    write_wav(os.path.join(out, "sfx" + suffix + ".wav"), raw_s * g)
    info = {"integrated_lufs": i_lufs, "true_peak_dbtp": tp, "gain": round(float(gain), 4),
            "max_gain_reduction_db": round(float(20 * np.log10(np.min(g))), 2)}
    print(json.dumps(info))


if __name__ == "__main__":
    main()
