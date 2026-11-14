"""Original 60-second score for the opening film: piano and strings only, synthesised with numpy.

One harmony per scene; the piano restates a four-note motif (D-A-G-F) each time the picture changes.
Strings enter at 13 s, thin out toward 49 s, a solo cello carries the theme up Calvary, and at
53.5 s the strings open into D major with the light. No percussion, brass or choir.

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


def chord(names, t0, dur, amp, **kw):
    for i, nm in enumerate(names):
        strings(nm, t0, dur, amp, pan=(i % 3 - 1) * 0.45, **kw)


def motif(t0, notes, amp=0.17, step=1.0):
    """The four-note figure the piano returns to at every scene."""
    for i, nm in enumerate(notes):
        piano(nm, t0 + i * step, amp * (1.12 if i == 1 else 1.0), pan=-0.2 + 0.13 * i)


# Piano and strings only. One scene = one harmony; the piano restates the motif each time.
#        start  piano motif                      strings (None = piano alone)            level
SCENES = [
    (0.0,  ['D4', 'A4', 'G4', 'F4'],            None,                                   0.0),   # Stephen
    (4.0,  ['D4', 'Bb4', 'A4', 'F4'],           None,                                   0.0),   # Damascus road
    (8.0,  ['D4', 'Bb4', 'A4', 'G4'],           ['G2', 'D3'],                           0.05),  # the light
    (13.0, ['C4', 'A4', 'G4', 'F4'],            ['F2', 'C3', 'A3', 'C4'],               0.085), # Ananias: strings arrive
    (17.0, ['C5', 'G5', 'F5', 'E5'],            ['C2', 'G2', 'E3', 'G3', 'C4'],         0.09),  # dawn at sea
    (21.0, ['D3', 'G3', 'F3', 'D3'],            ['G1', 'G2', 'D3', 'Bb3'],              0.11),  # shipwreck: low and dark
    (25.0, ['A3', 'F4', 'E4', 'D4'],            ['D2', 'A2', 'D3', 'F3'],               0.085), # prison
    (29.0, ['D4', 'Bb4', 'A4', 'F4'],           ['Bb1', 'F2', 'D3', 'F3', 'Bb3'],       0.09),  # Athens
    (33.0, ['C5', 'A5', 'G5', 'F5'],            ['F2', 'C3', 'F3', 'A3', 'C4'],         0.09),  # Miletus
    (37.0, ['D4', 'Bb4', 'A4', 'G4'],           ['G2', 'D3', 'G3', 'Bb3'],              0.075), # chains
    (41.0, ['E4', 'A4', 'G4', 'E4'],            ['A2', 'E3', 'A3', 'D4'],               0.06),  # Rome
]
for k, (t0, notes, low, level) in enumerate(SCENES):
    dur = (SCENES[k + 1][0] if k + 1 < len(SCENES) else 45.0) - t0
    motif(t0 + 0.3, notes, amp=0.19 if k < 3 else 0.16, step=min(1.0, (dur - 0.6) / 4))
    if low:
        chord(low, t0, dur, level, attack=1.3, release=1.6)
piano('D2', 0.3, 0.12)
piano('Bb1', 4.3, 0.12)
piano('A4', 11.2, 0.15, 0.1)      # the light: one held dominant before the strings come in
piano('C#5', 12.1, 0.13, 0.2)
strings('A2', 11.0, 2.0, 0.06, attack=1.0, release=1.2)

# ---- 45-49 s · the last morning: nearly nothing ------------------------------------
piano('E4', 45.3, 0.15, -0.1)
piano('A4', 46.3, 0.14, 0.1)
chord(['A2', 'E3'], 45.0, 3.2, 0.05, attack=1.2, release=1.0, swell=[1.0, 0.1])

# ---- 49-53.5 s · Calvary: a solo cello says the whole theme -------------------------
strings('D2', 49.2, 4.3, 0.09, attack=1.5, release=0.8, swell=[0.5, 1.5])
for nm, t0, d in [('D3', 49.3, 0.95), ('A3', 50.3, 0.95), ('G3', 51.3, 0.7), ('F3', 52.05, 0.7), ('E3', 52.8, 0.7)]:
    strings(nm, t0, d, 0.2 + 0.035 * (t0 - 49), attack=0.14, release=0.5, bright=1.4)
strings('A3', 52.3, 1.2, 0.07, attack=1.0, release=0.5, pan=-0.4, swell=[0.3, 1.3])
strings('C#4', 52.6, 0.9, 0.07, attack=0.8, release=0.5, pan=0.4, swell=[0.3, 1.3])

# ---- 53.5 s · the light: the strings open into D major (a bloom, not a hit) ---------
chord(['D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4', 'A4'], 53.5, 1.0, 0.15, attack=0.8, release=1.2, bright=1.5)
strings('D5', 53.7, 0.9, 0.08, attack=0.6, release=1.0, pan=0.2, bright=1.6)
for i, nm in enumerate(['D4', 'F#4', 'A4', 'D5']):
    piano(nm, 53.5 + i * 0.25, 0.12, -0.3 + 0.2 * i)

# ---- 54.5-57.5 s · the campus: the same motif, now in major ------------------------
chord(['G2', 'D3', 'G3', 'B3', 'D4'], 54.5, 1.5, 0.14, attack=0.5, release=1.0, bright=1.4)
chord(['A2', 'E3', 'A3', 'C#4', 'E4'], 56.0, 1.5, 0.14, attack=0.5, release=1.0, bright=1.4)
motif(54.5, ['D5', 'A5', 'G5', 'F#5'], amp=0.17, step=0.75)
strings('B4', 54.5, 1.4, 0.07, attack=0.4, pan=0.3, bright=1.5)
strings('C#5', 56.0, 1.4, 0.07, attack=0.4, pan=0.3, bright=1.5)

# ---- 57.5-60 s · title: home, and room for the first sung note ----------------------
chord(['D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4'], 57.5, 1.3, 0.15, attack=0.4, release=1.2, swell=[1.0, 0.35], bright=1.4)
piano('D5', 57.5, 0.18, -0.15)
piano('A5', 58.2, 0.14, 0.1)
piano('D6', 58.9, 0.12, 0.0)

# ---- balance: the journey sits about 8 dB under the bloom at 53.5 s -------------------
tt = np.arange(N) / SR
mix *= np.interp(tt, [0, 52.5, 53.6, 60], [0.62, 0.62, 1.0, 1.0])[:, None]

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
for a, b, nm in [(0, 13, 'piano'), (13, 21, 'strings in'), (21, 29, 'dark'), (29, 45, 'journey'), (45, 49, 'thinning'), (49, 53.5, 'cello'), (53.5, 54.5, 'bloom'), (54.5, 57.5, 'major'), (57.5, 60, 'title')]:
    print(f'  {nm:10s} {a:>5}-{b:<4} {rms(a, b):6.1f} dBFS')
