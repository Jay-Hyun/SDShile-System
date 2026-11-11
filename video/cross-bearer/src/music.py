"""Original 60-second score for the opening film, synthesised with numpy only.

Tempo is 60 BPM so one beat is one second and every cue lines up with the storyboard:
  0-5   drone, the road to Damascus         36-42  Rome: the motif almost alone
  5-12  the light: shock chord + motif      42-44  silence (reverb tail only)
  12-18 the sea, rolling piano              44-48  solo cello climbs the hill
  18-24 storm: drums on each lightning cut  48-50  tutti, turn to D major (the burst of light)
  24-30 prison at midnight: a wordless hymn 50-56  the motif in major
  30-36 farewell, dominant                  56-60  final chord, last second is tail

Usage: python3 src/music.py  ->  out/music.wav (48 kHz, 16-bit stereo)
"""
import os
import wave
import numpy as np

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))

NOTES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    """'F#4' / 'Bb2' -> frequency."""
    pc, rest = NOTES[name[0]], name[1:]
    if rest[0] == '#':
        pc, rest = pc + 1, rest[1:]
    elif rest[0] == 'b':
        pc, rest = pc - 1, rest[1:]
    return 440.0 * 2 ** ((pc + 12 * (int(rest) + 1) - 69) / 12)


def add(sig, t0, pan=0.0):
    i = int(t0 * SR)
    sig = sig[: max(0, N - i)]
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * left
    mix[i:i + len(sig), 1] += sig * right


def env(n, attack, release):
    e = np.ones(n)
    a, r = min(int(attack * SR), n // 2), min(int(release * SR), n // 2)
    e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    e[n - r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return e


def strings(note, t0, dur, amp=0.1, attack=0.6, release=1.0, pan=0.0, bright=1.0, swell=None):
    """Small detuned ensemble of band-limited saws with delayed vibrato."""
    f, n = hz(note), int((dur + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for cents in (-7, 0, 6):
        fv = f * 2 ** (cents / 1200)
        vib = 1 + 0.0035 * np.clip((t - 0.4) / 0.8, 0, 1) * np.sin(2 * np.pi * (5.1 + cents * 0.02) * t + rng.uniform(0, 6))
        phase = 2 * np.pi * np.cumsum(fv * vib) / SR + rng.uniform(0, 6)
        for k in range(1, 14):
            if fv * k > 9000:
                break
            out += np.sin(k * phase) / k * np.exp(-k * 0.22 / bright)
    e = env(n, attack, release)
    if swell is not None:
        e *= np.interp(t, [0, dur + release], swell)
    add(out * e * amp / 3, t0, pan)


def piano(note, t0, amp=0.2, pan=0.0, dur=5.0):
    f, n = hz(note), int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 10000:
            break
        out += np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.9 + 0.55 * k)) / k ** 1.25
    out *= np.minimum(t / 0.004, 1)
    add(out * amp, t0, pan)


def drum(t0, amp=0.5):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    f = 42 + 34 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.6)
    thud = np.convolve(rng.standard_normal(n), np.ones(90) / 90, 'same') * np.exp(-t * 28) * 2.2
    add((body + thud) * amp, t0)


def pad(note, t0, dur, amp=0.05, pan=0.0):
    """Soft choir-like 'ooh': few harmonics, slow breath."""
    f, n = hz(note), int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    out = sum(np.sin(2 * np.pi * f * k * (1 + d) * t + rng.uniform(0, 6)) * a
              for d in (-0.002, 0.0015) for k, a in ((1, 1), (2, 0.28), (3, 0.1), (4, 0.04)))
    add(out * env(n, 1.2, 1.6) * amp * (1 + 0.08 * np.sin(2 * np.pi * 0.23 * t)), t0, pan)


def swell(t0, dur, amp=0.25):
    """Cymbal-like noise rise into the climax."""
    n = int((dur + 3.0) * SR)
    t = np.arange(n) / SR
    noise = np.diff(rng.standard_normal(n + 1))
    rise = np.where(t < dur, (t / dur) ** 3, np.exp(-(t - dur) * 1.5))
    add(noise * rise * amp * 0.12, t0, -0.1)
    add(np.roll(noise, 977) * rise * amp * 0.12, t0, 0.1)


def chord(names, t0, dur, amp, **kw):
    for i, nm in enumerate(names):
        strings(nm, t0, dur, amp, pan=(i % 3 - 1) * 0.45, **kw)


# ---- 0-5 s · prologue ------------------------------------------------------
strings('D2', 0.0, 5.2, 0.16, attack=2.5, release=1.5)
strings('A2', 1.0, 4.2, 0.09, attack=2.0, release=1.5, pan=0.3)
piano('A4', 1.1, 0.16, -0.1)
piano('D5', 3.0, 0.13, 0.15)

# ---- 5-12 s · the light from heaven -----------------------------------------
MOTIF = ['D4', 'A4', 'G4', 'F4']


def motif(t0, octave=0, amp=0.2, notes=MOTIF, step=1.0):
    for i, nm in enumerate(notes):
        piano(nm[:-1] + str(int(nm[-1]) + octave), t0 + i * step, amp * (1.0 if i != 1 else 1.15), pan=-0.2 + 0.13 * i)


drum(5.0, 0.8)
chord(['D2', 'A2', 'D3', 'A3'], 5.0, 3.6, 0.15, attack=0.05, release=1.4)
for nm, pan in (('A5', -0.5), ('D6', 0.5), ('E6', 0.0)):
    strings(nm, 5.0, 4.0, 0.05, attack=0.05, release=2.0, pan=pan, bright=2.0, swell=[1.0, 0.15])
chord(['Bb1', 'F2', 'D3'], 8.6, 3.2, 0.13)
motif(6.5)

# ---- 12-18 s · sent out by sea ----------------------------------------------
chord(['F2', 'C3', 'F3', 'A3'], 12.0, 3.0, 0.12)
chord(['C2', 'G2', 'E3', 'G3', 'C4'], 15.0, 3.0, 0.12, swell=[1.0, 1.3])
motif(12.5, notes=['F4', 'C5', 'Bb4', 'A4'])
for i, nm in enumerate(['A4', 'C5', 'F5', 'C5', 'A4', 'C5', 'G4', 'C5', 'E5', 'C5', 'G4', 'C5']):  # rolling water
    piano(nm, 12.0 + i * 0.5, 0.05, 0.4)

# ---- 18-24 s · storm and shipwreck ---------------------------------------------
chord(['G1', 'G2', 'D3', 'G3', 'Bb3'], 18.0, 3.0, 0.19, attack=0.05, bright=1.7)
chord(['A1', 'A2', 'E3', 'A3', 'C#4'], 21.0, 2.7, 0.2, attack=0.05, release=0.5, bright=1.8)
strings('D5', 18.0, 2.8, 0.09, attack=0.05, pan=0.4, bright=1.8)
strings('E5', 21.0, 2.5, 0.1, attack=0.05, release=0.4, pan=0.4, bright=1.8)
for t0, a in [(18.0, 0.8), (18.47, 0.95), (19.0, 0.5), (19.5, 0.6), (20.0, 0.5), (20.47, 0.95), (21.0, 0.6), (21.5, 0.6),
              (22.0, 0.5), (22.27, 0.95), (22.75, 0.6), (23.25, 0.7), (23.5, 0.75), (23.75, 0.85)]:
    drum(t0, a)
swell(22.6, 1.3, 0.6)

# ---- 24-30 s · midnight in Philippi: a hymn in the dark -------------------------
for names, t0 in ((('Bb3', 'D4', 'F4'), 24.3), (('A3', 'C4', 'F4'), 27.0)):
    for k, nm in enumerate(names):
        pad(nm, t0, 2.6, 0.06, (k - 1) * 0.5)
strings('Bb1', 24.3, 2.6, 0.1, attack=1.0)
strings('F2', 27.0, 2.8, 0.1, attack=0.6)
motif(25.0, notes=['D4', 'F4', 'G4', 'A4'], amp=0.16)

# ---- 30-36 s · farewell at Miletus ------------------------------------------------
chord(['G2', 'D3', 'G3', 'Bb3'], 30.0, 3.0, 0.14)
chord(['A1', 'A2', 'E3', 'A3', 'D4'], 33.0, 1.5, 0.14)
chord(['A1', 'A2', 'E3', 'A3', 'C#4'], 34.5, 1.5, 0.14, release=1.2)
strings('D5', 30.0, 2.8, 0.06, pan=0.5)
strings('E5', 33.0, 2.8, 0.06, pan=0.5, swell=[1.0, 0.4])
motif(31.0, notes=['G4', 'D5', 'C5', 'Bb4'], amp=0.2)
drum(30.0, 0.45)
drum(33.0, 0.45)

# ---- 36-42 s · the last letter: almost alone ---------------------------------------
strings('D2', 36.0, 4.6, 0.12, attack=1.0, release=1.4, swell=[1.0, 0.2])
strings('A2', 36.0, 4.2, 0.07, attack=1.2, release=1.4, pan=0.3, swell=[1.0, 0.15])
motif(37.0, amp=0.2)
piano('D4', 41.0, 0.1)

# ---- 42-44 s · silence ---------------------------------------------------------

# ---- 44-48 s · solo cello up the hill ------------------------------------------
strings('D2', 44.0, 4.0, 0.1, attack=1.2, release=0.3, swell=[0.5, 1.6])
for nm, t0, d in [('D3', 44.0, 1.0), ('A3', 45.0, 1.0), ('G3', 46.0, 0.5), ('F3', 46.5, 0.5), ('E3', 47.0, 0.5), ('A3', 47.5, 0.5)]:
    strings(nm, t0, d, 0.3 + 0.05 * (t0 - 44), attack=0.12, release=0.5, bright=1.5)
for t0 in (44.0, 45.0, 46.0, 47.0):
    drum(t0, 0.36 + 0.07 * (t0 - 44))
strings('A4', 46.2, 1.8, 0.1, attack=1.4, release=0.3, pan=0.4, swell=[0.2, 1.4])
strings('C#5', 46.2, 1.8, 0.1, attack=1.4, release=0.3, pan=-0.4, swell=[0.2, 1.4])
swell(46.3, 1.7, 1.0)

# ---- 48-50 s · the burst: D major ------------------------------------------------
chord(['D1', 'D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5'], 48.0, 2.0, 0.2, attack=0.04, release=1.4, bright=1.9)
drum(48.0, 1.0)
drum(48.12, 0.6)
for nm, t0 in [('F#5', 48.0), ('A5', 49.0)]:
    strings(nm, t0, 1.0, 0.17, attack=0.08, release=0.9, bright=2.0, pan=0.2)
for i, nm in enumerate(['D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6', 'A5']):
    piano(nm, 48.0 + i * 0.25, 0.14, -0.4 + 0.07 * i)

# ---- 50-56 s · the motif in major, handed on ---------------------------------
chord(['D2', 'A2', 'D3', 'F#3', 'A3'], 50.0, 2.0, 0.15, attack=0.3)
chord(['G1', 'G2', 'D3', 'G3', 'B3'], 52.0, 2.0, 0.15, attack=0.3)
chord(['B1', 'B2', 'D3', 'F#3'], 54.0, 1.0, 0.15, attack=0.3)
chord(['A1', 'A2', 'E3', 'A3', 'C#4'], 55.0, 1.0, 0.15, attack=0.3)
for nm, t0, d in [('D5', 50.0, 1.0), ('A5', 51.0, 1.0), ('G5', 52.0, 1.0), ('F#5', 53.0, 1.0), ('D5', 54.0, 1.0), ('E5', 55.0, 1.0)]:
    strings(nm, t0, d, 0.15, attack=0.1, release=0.7, bright=1.7, pan=0.25)
    piano(nm, t0, 0.15, -0.2)
for nm in ('D4', 'F#4', 'A4'):
    pad(nm, 50.0, 2.0, 0.045, 0.5)
for nm in ('D4', 'G4', 'B4'):
    pad(nm, 52.0, 2.0, 0.045, -0.5)
for nm in ('D4', 'F#4', 'B4'):
    pad(nm, 54.0, 1.0, 0.045, 0.5)
for nm in ('C#4', 'E4', 'A4'):
    pad(nm, 55.0, 1.0, 0.045, -0.5)
drum(50.0, 0.55)
drum(52.0, 0.45)
drum(54.0, 0.45)

# ---- 56-60 s · title ---------------------------------------------------------
chord(['D1', 'D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4'], 56.0, 2.2, 0.17, attack=0.2, release=1.3, swell=[1.0, 0.35])
for nm in ('D4', 'F#4', 'A4', 'D5'):
    pad(nm, 56.0, 1.4, 0.05)
drum(56.0, 0.6)
piano('D5', 56.0, 0.2, -0.15)
piano('A5', 57.0, 0.16, 0.1)
piano('D6', 58.0, 0.14, 0.0)

# ---- reverb (synthetic hall) + master ---------------------------------------
ir_n = int(3.2 * SR)
ir_t = np.arange(ir_n) / SR
wet = np.zeros_like(mix)
size = 1 << int(np.ceil(np.log2(N + ir_n)))
for ch in range(2):
    ir = rng.standard_normal(ir_n) * np.exp(-ir_t * 2.1) * np.minimum(ir_t / 0.02, 1)
    ir = np.convolve(ir, np.ones(6) / 6, 'same')  # darker tail
    ir /= np.sqrt(np.sum(ir ** 2))
    wet[:, ch] = np.fft.irfft(np.fft.rfft(mix[:, ch], size) * np.fft.rfft(ir, size), size)[:N]
out = mix + 0.42 * wet

fade_out = np.ones(N)
tail = int(1.0 * SR)
fade_out[N - tail:] = np.cos(np.linspace(0, np.pi / 2, tail)) ** 2
fade_out[N - int(0.05 * SR):] = 0
out *= fade_out[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.5) / np.tanh(1.5) * 0.92  # gentle limiter, peak at about -0.7 dBFS

path = os.path.join(os.path.dirname(__file__), '..', 'out', 'music.wav')
os.makedirs(os.path.dirname(path), exist_ok=True)
with wave.open(path, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())

rms = lambda a, b: 20 * np.log10(np.sqrt(np.mean(out[int(a * SR):int(b * SR)] ** 2)) + 1e-9)
print(f'{os.path.normpath(path)}  {N / SR:.1f}s  peak {np.max(np.abs(out)):.2f}')
for a, b, nm in [(0, 5, 'road'), (5, 12, 'light'), (12, 18, 'sea'), (18, 24, 'storm'), (24, 30, 'prison'), (30, 36, 'farewell'), (36, 42, 'rome'), (43, 44, 'silence'), (44, 48, 'cello'), (48, 50, 'burst'), (50, 56, 'major'), (56, 60, 'title')]:
    print(f'  {nm:10s} {a:>5}-{b:<4} {rms(a, b):6.1f} dBFS')
