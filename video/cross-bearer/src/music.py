"""Original 60-second score for the opening film, synthesised with numpy only.

Tempo is 60 BPM so one beat is one second and every cue lines up with the storyboard:
  0-6   drone, the road to Damascus         37-42  Rome: the motif almost alone
  6-14  the light: shock chord + motif      42-44  silence (reverb tail only)
  14-20 golden dawn at sea, rolling piano   44-48  solo cello climbs the hill
  20-25 storm: drums on each lightning cut  48-50  tutti, turn to D major (the burst of light)
  25-31 prison at midnight: a wordless hymn 50-56  the motif in major
  31-37 farewell, dominant                  56-60  final chord, last second is tail

Usage: python3 src/music.py  ->  out/music-raw/cross-bearer-score.wav (48 kHz, 16-bit stereo, unmastered)
Then src/master.sh polishes and masters it with the bitwize-music tools into out/music.wav.
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


def brass(note, t0, dur, amp=0.12, pan=0.0, attack=0.07, release=0.5, swell=None):
    """Horn/trombone section: saw stack whose brightness opens with the envelope."""
    f, n = hz(note), int((dur + release) * SR)
    t = np.arange(n) / SR
    e = env(n, attack, release)
    if swell is not None:
        e = e * np.interp(t, [0, dur + release], swell)
    out = np.zeros(n)
    for cents in (-5, 4):
        fv = f * 2 ** (cents / 1200)
        phase = 2 * np.pi * fv * t + rng.uniform(0, 6) + 0.002 * np.sin(2 * np.pi * 4.6 * t)
        for k in range(1, 18):
            if fv * k > 7000:
                break
            out += np.sin(k * phase) / k * e ** (0.35 * k)  # upper partials arrive later and leave sooner
    add(out * e * amp / 2, t0, pan)


def choir(note, t0, dur, amp=0.06, pan=0.0, attack=0.5, release=1.4, swell=None):
    """Wordless 'ah': harmonics shaped by three vowel formants, several loosely tuned voices."""
    f, n = hz(note), int((dur + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    formant = lambda fr: (np.exp(-((fr - 800) / 180) ** 2) + 0.55 * np.exp(-((fr - 1180) / 200) ** 2)
                          + 0.3 * np.exp(-((fr - 2800) / 420) ** 2) + 0.12)
    for _ in range(5):
        fv = f * 2 ** (rng.uniform(-9, 9) / 1200)
        vib = 1 + 0.004 * np.sin(2 * np.pi * rng.uniform(4.6, 5.8) * t + rng.uniform(0, 6))
        phase = 2 * np.pi * np.cumsum(fv * vib) / SR + rng.uniform(0, 6)
        for k in range(1, 40):
            if fv * k > 5200:
                break
            out += np.sin(k * phase) * formant(fv * k) / k ** 0.6
    e = env(n, attack, release)
    if swell is not None:
        e = e * np.interp(t, [0, dur + release], swell)
    add(out * e * amp / 5, t0, pan)


def boom(t0, amp=0.9):
    """Sub impact: a low sine that falls and rings, with a short thud on top."""
    n = int(3.5 * SR)
    t = np.arange(n) / SR
    f = 34 + 30 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5)
    thud = np.convolve(rng.standard_normal(n), np.ones(140) / 140, 'same') * np.exp(-t * 16) * 2.6
    add((body + thud) * amp, t0)


def timp(t0, amp=0.5, note='D2'):
    f, n = hz(note), int(1.6 * SR)
    t = np.arange(n) / SR
    body = (np.sin(2 * np.pi * f * (1 + 0.04 * np.exp(-t * 30)) * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 6)) * np.exp(-t * 3.2)
    skin = np.convolve(rng.standard_normal(n), np.ones(40) / 40, 'same') * np.exp(-t * 45) * 1.5
    add((body + skin) * amp, t0, 0.1)


def crash(t0, amp=0.3):
    n = int(4.5 * SR)
    t = np.arange(n) / SR
    for pan, shift in ((-0.4, 0), (0.4, 1543)):
        noise = np.roll(np.diff(np.diff(rng.standard_normal(n + 2))), shift)
        add(noise * np.exp(-t * 1.3) * np.minimum(t / 0.004, 1) * amp * 0.07, t0, pan)


def tremolo(note, t0, dur, amp=0.08, pan=0.0, swell=(0.3, 1.0)):
    """Bowed tremolo: short repeated strokes that crowd together into a shimmer."""
    stroke = 1 / 13
    k = 0
    while k * stroke < dur:
        g = np.interp(k * stroke / dur, [0, 1], swell)
        strings(note, t0 + k * stroke, stroke * 0.8, amp * g, attack=0.012, release=0.06, pan=pan, bright=1.8)
        k += 1


def chord(names, t0, dur, amp, **kw):
    for i, nm in enumerate(names):
        strings(nm, t0, dur, amp, pan=(i % 3 - 1) * 0.45, **kw)


# ---- 0-6 s · the road to Damascus -------------------------------------------
strings('D2', 0.0, 6.2, 0.16, attack=2.5, release=1.2)
strings('A2', 1.0, 5.0, 0.09, attack=2.0, release=1.2, pan=0.3)
strings('Eb3', 3.0, 3.0, 0.05, attack=1.5, release=0.6, pan=-0.3)  # unease: the persecutor
piano('A4', 1.4, 0.16, -0.1)
piano('D5', 3.6, 0.13, 0.15)

# ---- 6-14 s · the light from heaven: the call ---------------------------------
MOTIF = ['D4', 'A4', 'G4', 'F4']


def motif(t0, octave=0, amp=0.2, notes=MOTIF, step=1.0):
    for i, nm in enumerate(notes):
        piano(nm[:-1] + str(int(nm[-1]) + octave), t0 + i * step, amp * (1.0 if i != 1 else 1.15), pan=-0.2 + 0.13 * i)


drum(6.0, 0.8)
boom(6.0, 0.9)
chord(['D2', 'A2', 'D3', 'A3'], 6.0, 4.0, 0.15, attack=0.05, release=1.4)
for nm, pan in (('A5', -0.5), ('D6', 0.5), ('E6', 0.0)):
    strings(nm, 6.0, 4.5, 0.05, attack=0.05, release=2.0, pan=pan, bright=2.0, swell=[1.0, 0.15])
chord(['Bb1', 'F2', 'D3'], 10.0, 3.8, 0.13)
motif(7.6)

# ---- 14-20 s · sent out at golden dawn (major, open) ---------------------------
chord(['F2', 'C3', 'F3', 'A3'], 14.0, 3.0, 0.12)
chord(['C2', 'G2', 'E3', 'G3', 'C4'], 17.0, 3.0, 0.12, swell=[1.0, 1.3])
motif(14.6, notes=['F4', 'C5', 'Bb4', 'A4'])
for i, nm in enumerate(['A4', 'C5', 'F5', 'C5', 'A4', 'C5', 'G4', 'C5', 'E5', 'C5', 'G4', 'C5']):  # rolling water
    piano(nm, 14.0 + i * 0.5, 0.05, 0.4)

# ---- 20-25 s · storm and shipwreck ------------------------------------------------
boom(20.0, 1.0)
brass('G1', 20.0, 2.4, 0.13, attack=0.1)
brass('A1', 22.5, 2.1, 0.14, attack=0.1, release=0.4)
chord(['G1', 'G2', 'D3', 'G3', 'Bb3'], 20.0, 2.5, 0.19, attack=0.05, bright=1.7)
chord(['A1', 'A2', 'E3', 'A3', 'C#4'], 22.5, 2.2, 0.2, attack=0.05, release=0.5, bright=1.8)
strings('D5', 20.0, 2.3, 0.09, attack=0.05, pan=0.4, bright=1.8)
strings('E5', 22.5, 2.0, 0.1, attack=0.05, release=0.4, pan=0.4, bright=1.8)
for t0, a in [(20.0, 0.8), (20.4, 0.95), (21.0, 0.5), (21.5, 0.6), (21.93, 0.95), (22.5, 0.6), (23.0, 0.5),
              (23.4, 0.95), (23.9, 0.6), (24.3, 0.7), (24.55, 0.75), (24.8, 0.85)]:
    drum(t0, a)
swell(23.7, 1.2, 0.6)

# ---- 25-31 s · midnight in Philippi: a hymn in the dark -------------------------
for names, t0 in ((('Bb3', 'D4', 'F4'), 25.3), (('A3', 'C4', 'F4'), 28.0)):
    for k, nm in enumerate(names):
        pad(nm, t0, 2.6, 0.06, (k - 1) * 0.5)
strings('Bb1', 25.3, 2.6, 0.1, attack=1.0)
strings('F2', 28.0, 2.8, 0.1, attack=0.6)
motif(26.0, notes=['D4', 'F4', 'G4', 'A4'], amp=0.16)

# ---- 31-37 s · farewell at Miletus ------------------------------------------------
chord(['G2', 'D3', 'G3', 'Bb3'], 31.0, 3.0, 0.14)
chord(['A1', 'A2', 'E3', 'A3', 'D4'], 34.0, 1.5, 0.14)
chord(['A1', 'A2', 'E3', 'A3', 'C#4'], 35.5, 1.5, 0.14, release=1.2)
strings('D5', 31.0, 2.8, 0.06, pan=0.5)
strings('E5', 34.0, 2.8, 0.06, pan=0.5, swell=[1.0, 0.4])
motif(32.0, notes=['G4', 'D5', 'C5', 'Bb4'], amp=0.2)
drum(31.0, 0.45)
drum(34.0, 0.45)

# ---- 37-42 s · the last letter: almost alone ---------------------------------------
strings('D2', 37.0, 3.8, 0.12, attack=1.0, release=1.2, swell=[1.0, 0.2])
strings('A2', 37.0, 3.4, 0.07, attack=1.2, release=1.2, pan=0.3, swell=[1.0, 0.15])
motif(37.6, amp=0.2, step=0.85)

# ---- 42-44 s · silence ---------------------------------------------------------

# ---- 44-48 s · the climb: solo cello over a gathering roll ------------------------
strings('D2', 44.0, 4.0, 0.1, attack=1.2, release=0.3, swell=[0.5, 1.6])
strings('D1', 45.0, 3.0, 0.1, attack=1.5, release=0.3, swell=[0.3, 1.7])
for nm, t0, d in [('D3', 44.0, 1.0), ('A3', 45.0, 1.0), ('G3', 46.0, 0.5), ('F3', 46.5, 0.5), ('E3', 47.0, 0.5), ('A3', 47.5, 0.5)]:
    strings(nm, t0, d, 0.2 + 0.04 * (t0 - 44), attack=0.12, release=0.5, bright=1.5)
# timpani: heartbeat that accelerates into a roll
t0, gap, k = 44.0, 0.5, 0
while t0 < 47.96:
    timp(t0, 0.1 + 0.11 * (t0 - 44), 'D2' if k % 2 == 0 else 'A1')
    gap = max(0.075, gap * 0.9)
    t0 += gap
    k += 1
# shimmer and voices rise step by step under the cello
for nm, t0, pan in [('A4', 45.0, -0.5), ('D5', 46.0, 0.5), ('E5', 46.75, -0.3), ('G5', 47.25, 0.3), ('A5', 47.6, 0.0)]:
    tremolo(nm, t0, 48.0 - t0, 0.05, pan)
for nm, t0, pan in [('A3', 45.5, -0.4), ('D4', 46.3, 0.4), ('E4', 47.0, -0.2), ('A4', 47.5, 0.2)]:
    choir(nm, t0, 48.0 - t0, 0.07, pan, attack=0.5, release=0.25, swell=[0.3, 1.5])
brass('A2', 46.5, 1.5, 0.1, attack=1.2, release=0.15, swell=[0.2, 1.6])
brass('E3', 47.0, 1.0, 0.1, pan=0.3, attack=0.9, release=0.15, swell=[0.2, 1.6])
swell(46.0, 2.0, 0.7)

# ---- 48-50 s · the burst: D major, everything ---------------------------------------
boom(48.0, 1.3)
crash(48.0, 1.0)
timp(48.0, 1.1, 'D2')
timp(48.5, 0.6, 'D2')
timp(49.0, 0.8, 'A1')
timp(49.5, 0.6, 'D2')
chord(['D1', 'D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5'], 48.0, 2.0, 0.2, attack=0.04, release=1.4, bright=1.9)
for nm, pan in (('D2', -0.5), ('A2', 0.5), ('D3', -0.3), ('F#3', 0.3), ('A3', 0.0)):
    brass(nm, 48.0, 2.0, 0.17, pan, attack=0.05, release=0.6)
for nm, pan in (('D4', -0.5), ('F#4', 0.5), ('A4', -0.2), ('D5', 0.2)):
    choir(nm, 48.0, 2.0, 0.1, pan, attack=0.06, release=1.2)
for nm, t0 in [('F#5', 48.0), ('A5', 49.0)]:
    strings(nm, t0, 1.0, 0.17, attack=0.08, release=0.9, bright=2.0, pan=0.2)
for i, nm in enumerate(['D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6', 'A5']):
    piano(nm, 48.0 + i * 0.25, 0.14, -0.4 + 0.07 * i)

# ---- 50-56 s · the motif in major, handed on: brass sings, strings run ----------------
PROG = [(50.0, 2.0, ['D2', 'A2', 'D3', 'F#3', 'A3'], ['D4', 'F#4', 'A4']),
        (52.0, 2.0, ['G1', 'G2', 'D3', 'G3', 'B3'], ['D4', 'G4', 'B4']),
        (54.0, 1.0, ['B1', 'B2', 'D3', 'F#3'], ['D4', 'F#4', 'B4']),
        (55.0, 1.0, ['A1', 'A2', 'E3', 'A3', 'C#4'], ['C#4', 'E4', 'A4'])]
for t0, d, low, high in PROG:
    chord(low, t0, d, 0.15, attack=0.3)
    for k, nm in enumerate(high):
        choir(nm, t0, d, 0.075, (k - 1) * 0.5, attack=0.25, release=0.8)
    for k in range(int(d / 0.25)):          # running sixteenths: root, fifth, octave
        nm = [low[1], low[2], low[-1], low[2]][k % 4]
        strings(nm, t0 + k * 0.25, 0.14, 0.11 * (1.25 if k % 4 == 0 else 1.0), attack=0.015, release=0.1, pan=0.35 if k % 2 else -0.35, bright=1.8)
for nm, t0, d in [('D4', 50.0, 1.0), ('A4', 51.0, 1.0), ('G4', 52.0, 1.0), ('F#4', 53.0, 1.0), ('D4', 54.0, 1.0), ('E4', 55.0, 1.0)]:
    brass(nm, t0, d, 0.2, -0.15, attack=0.06, release=0.35)
    brass(nm[:-1] + '3', t0, d, 0.13, 0.25, attack=0.06, release=0.35)
    strings(nm[:-1] + '5', t0, d, 0.13, attack=0.1, release=0.7, bright=1.7, pan=0.25)
    piano(nm[:-1] + '5', t0, 0.12, -0.2)
for t0, a, nm in [(50.0, 0.9, 'D2'), (51.0, 0.45, 'A1'), (52.0, 0.8, 'G1'), (53.0, 0.45, 'D2'), (54.0, 0.8, 'B1'), (55.0, 0.7, 'A1'), (55.5, 0.5, 'A1'), (55.75, 0.6, 'A1')]:
    timp(t0, a, nm)
boom(50.0, 0.7)
boom(52.0, 0.5)
swell(55.0, 1.0, 0.7)

# ---- 56-60 s · title: the last chord, and room for the first sung note -----------------
boom(56.0, 1.1)
crash(56.0, 0.8)
timp(56.0, 1.0, 'D2')
chord(['D1', 'D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4'], 56.0, 2.2, 0.18, attack=0.05, release=1.3, swell=[1.0, 0.35])
for nm, pan in (('D2', -0.5), ('A2', 0.5), ('D3', 0.0), ('F#3', 0.3), ('A3', -0.3), ('D4', 0.0)):
    brass(nm, 56.0, 2.0, 0.16, pan, attack=0.05, release=1.0, swell=[1.0, 0.3])
for nm, pan in (('D4', -0.4), ('F#4', 0.4), ('A4', -0.2), ('D5', 0.2)):
    choir(nm, 56.0, 2.2, 0.09, pan, attack=0.08, release=1.4, swell=[1.0, 0.4])
piano('D5', 56.0, 0.2, -0.15)
piano('A5', 57.0, 0.16, 0.1)
piano('D6', 58.0, 0.14, 0.0)

# ---- balance: about 10 dB between the quiet acts and the turn at 48 s -----------------
tt = np.arange(N) / SR
mix *= np.interp(tt, [0, 42, 44, 48, 60], [1.25, 1.25, 1.1, 0.9, 0.9])[:, None]

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

path = os.path.join(os.path.dirname(__file__), '..', 'out', 'music-raw', 'cross-bearer-score.wav')  # mastered afterwards, see master.sh
os.makedirs(os.path.dirname(path), exist_ok=True)
with wave.open(path, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())

rms = lambda a, b: 20 * np.log10(np.sqrt(np.mean(out[int(a * SR):int(b * SR)] ** 2)) + 1e-9)
print(f'{os.path.normpath(path)}  {N / SR:.1f}s  peak {np.max(np.abs(out)):.2f}')
for a, b, nm in [(0, 6, 'road'), (6, 14, 'light'), (14, 20, 'sea'), (20, 25, 'storm'), (25, 31, 'prison'), (31, 37, 'farewell'), (37, 42, 'rome'), (43, 44, 'silence'), (44, 48, 'cello'), (48, 50, 'burst'), (50, 56, 'major'), (56, 60, 'title')]:
    print(f'  {nm:10s} {a:>5}-{b:<4} {rms(a, b):6.1f} dBFS')
