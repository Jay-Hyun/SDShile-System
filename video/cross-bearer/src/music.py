"""Original 65-second score for the opening film: a real (sampled) grand piano, a solo cello and a
barely-there string pad.

The piano is played, not programmed: a sustain pedal, rolled chords, a left hand that flows in
broken chords and a right hand that sings the four-note motif (D-A-G-F) as a melody.
D minor, one harmony per 4-second scene; at 53.5 s it opens into D major with the light, and the
last chord is left to ring out on its own for the final seconds.

Usage: python3 src/music.py  ->  out/music-raw/cross-bearer-score.wav (48 kHz, 16-bit stereo, unmastered)
Then src/master.sh polishes and masters it with the bitwize-music tools into out/music.wav.
"""
import os
import wave
import numpy as np
from sampler import Piano, Cello, warm, midi, SR

DUR = 65.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
pad = np.zeros((N, 2))
piano = Piano()
cello = Cello()


# ---- soft synthetic string pad (kept far in the background) --------------------------
def strings(note, t0, dur, amp=0.04, attack=1.4, release=1.8, pan=0.0, swell=None):
    f = 440.0 * 2 ** ((midi(note) - 69) / 12)
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for cents in (-7, 0, 6):
        fv = f * 2 ** (cents / 1200)
        vib = 1 + 0.0035 * np.clip((t - 0.4) / 0.8, 0, 1) * np.sin(2 * np.pi * (5.1 + cents * 0.02) * t + rng.uniform(0, 6))
        phase = 2 * np.pi * np.cumsum(fv * vib) / SR + rng.uniform(0, 6)
        for k in range(1, 10):
            if fv * k > 5000:
                break
            sig += np.sin(k * phase) / k * np.exp(-k * 0.3)
    e = np.ones(n)
    a, r = min(int(attack * SR), n // 2), min(int(release * SR), n // 2)
    e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    e[n - r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    if swell is not None:
        e *= np.interp(t, [0, dur + release], swell)
    sig *= e * amp / 3
    i = int(t0 * SR)
    sig = sig[: max(0, N - i)]
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    pad[i:i + len(sig), 0] += sig * left
    pad[i:i + len(sig), 1] += sig * right


def bed(names, t0, dur, amp=0.04, **kw):
    for i, nm in enumerate(names):
        strings(nm, t0, dur, amp, pan=(i % 3 - 1) * 0.5, **kw)


# ---- piano gestures --------------------------------------------------------------
def left(t0, pattern, step, vel, count, cresc=0.0):
    """Flowing broken chord: the pattern repeats, the first note of each group leans a little."""
    for k in range(count):
        v = vel + cresc * k / max(count - 1, 1)
        piano.note(pattern[k % len(pattern)], t0 + k * step, v * (1.12 if k % len(pattern) == 0 else 1.0), hold=step * 1.1)


def sing(notes, vel, octave=False, rise=0.0):
    """Right-hand melody: (name, time, length). The line swells toward its middle like a breath."""
    for k, (nm, t, d) in enumerate(notes):
        shape = 1 + 0.12 * np.sin(np.pi * k / max(len(notes) - 1, 1))
        v = (vel + rise * k / max(len(notes) - 1, 1)) * shape
        piano.note(nm, t, v, hold=d)
        if octave:
            piano.note(midi(nm) + 12, t + 0.012, v * 0.86, hold=d)


# ---- 0-8 s · Stephen, the Damascus road: low octaves and a few high notes, lots of air ----
piano.chord(['D1', 'D2'], 0.25, 0.42, hold=3.5)
sing([('D5', 1.1, 0.9), ('A5', 2.05, 0.8), ('G5', 2.8, 0.7), ('F5', 3.45, 1.0)], 0.36)
piano.pedal(4.0)
piano.chord(['Bb0', 'Bb1'], 4.1, 0.46, hold=3.5)
sing([('D5', 5.0, 0.9), ('Bb5', 5.95, 0.8), ('A5', 6.7, 0.7), ('F5', 7.35, 0.9)], 0.4)

# ---- 8-13 s · the light: one sweep from the bottom of the keyboard to the top -----------
piano.pedal(8.0)
SWEEP = ['G1', 'D2', 'G2', 'Bb2', 'D3', 'G3', 'Bb3', 'D4', 'G4', 'Bb4', 'D5', 'G5', 'Bb5', 'D6', 'G6']
t = 8.05
for k, nm in enumerate(SWEEP):
    piano.note(nm, t, 0.3 + 0.5 * k / (len(SWEEP) - 1), hold=0.3)
    t += 0.24 * 0.93 ** k                      # the hand quickens as it climbs
piano.pedal(11.0)
piano.chord(['A1', 'A2'], 11.0, 0.72, hold=1.9)
piano.chord(['E3', 'A3', 'C#4', 'E4', 'A4'], 11.04, 0.6, hold=1.9, roll=0.035)
piano.note('E5', 12.0, 0.42, hold=0.9)
piano.note('A5', 12.5, 0.36, hold=0.5)
bed(['A2', 'E3'], 10.6, 2.2, 0.035, swell=[0.4, 1.0])

# ---- 13-29 s · called, sent, wrecked, jailed: the left hand flows, the right hand sings ----
piano.pedal(13.0, 15.0, 17.0, 19.0, 21.0, 23.0, 25.0, 27.0)
left(13.0, ['F2', 'C3', 'A3', 'C3', 'F3', 'C3', 'A3', 'C3'], 0.5, 0.36, 8)
sing([('A4', 13.0, 1.0), ('C5', 14.0, 0.5), ('A4', 14.5, 0.5), ('G4', 15.0, 1.0), ('F4', 16.0, 1.0)], 0.52)
bed(['F2', 'C3', 'A3'], 13.0, 4.0, 0.04)

left(17.0, ['C2', 'G2', 'E3', 'G2', 'C3', 'G2', 'E3', 'G2'], 0.5, 0.4, 8)
sing([('G4', 17.0, 1.0), ('E5', 18.0, 1.0), ('D5', 19.0, 0.5), ('C5', 19.5, 0.5), ('E5', 20.0, 1.0)], 0.58)
bed(['C2', 'G2', 'E3', 'C4'], 17.0, 4.0, 0.045)

left(21.0, ['G1', 'D2', 'Bb2', 'D2', 'G2', 'D2', 'Bb2', 'D2'], 0.5, 0.5, 8)       # the storm: lower, heavier
sing([('D4', 21.0, 1.0), ('G4', 22.0, 0.5), ('Bb4', 22.5, 0.5), ('A4', 23.0, 1.0), ('G4', 24.0, 1.0)], 0.62)
for nm, tt_, d in [('D3', 21.0, 1.0), ('G3', 22.0, 0.5), ('Bb3', 22.5, 0.5), ('A3', 23.0, 1.0), ('G3', 24.0, 1.0)]:
    piano.note(nm, tt_, 0.5, hold=d)
bed(['G1', 'G2', 'D3'], 21.0, 4.0, 0.05)

left(25.0, ['D2', 'A2', 'F3', 'A2', 'D3', 'A2', 'F3', 'A2'], 0.5, 0.34, 8)        # the prison: hushed
sing([('F4', 25.0, 1.5), ('E4', 26.5, 0.5), ('D4', 27.0, 1.0), ('A3', 28.0, 1.0)], 0.44)
bed(['D2', 'A2', 'F3'], 25.0, 4.0, 0.04)

# ---- 29-45 s · preaching, farewell, chains, Rome: sixteenths, the melody in octaves --------
piano.pedal(29.0, 31.0, 33.0, 35.0, 37.0, 39.0, 41.0, 43.0)
left(29.0, ['Bb1', 'F2', 'Bb2', 'D3', 'F3', 'D3', 'Bb2', 'F2'], 0.25, 0.4, 16, cresc=0.06)
sing([('D5', 29.0, 1.0), ('F5', 30.0, 1.0), ('Bb5', 31.0, 1.5), ('A5', 32.5, 0.5)], 0.6, octave=True, rise=0.05)
bed(['Bb1', 'F2', 'D3', 'Bb3'], 29.0, 4.0, 0.045)

left(33.0, ['F1', 'C2', 'F2', 'A2', 'C3', 'A2', 'F2', 'C2'], 0.25, 0.46, 16, cresc=0.06)
sing([('A5', 33.0, 1.0), ('C6', 34.0, 1.0), ('A5', 35.0, 0.5), ('G5', 35.5, 0.5), ('F5', 36.0, 1.0)], 0.66, octave=True, rise=0.05)
bed(['F2', 'C3', 'A3', 'C4'], 33.0, 4.0, 0.05)

left(37.0, ['G1', 'D2', 'G2', 'Bb2', 'D3', 'Bb2', 'G2', 'D2'], 0.25, 0.54, 16, cresc=0.06)   # the peak of the journey
sing([('G5', 37.0, 1.0), ('Bb5', 38.0, 1.0), ('D6', 39.0, 1.5), ('C6', 40.5, 0.5)], 0.74, octave=True, rise=0.06)
bed(['G1', 'G2', 'D3', 'Bb3'], 37.0, 4.0, 0.055)

left(41.0, ['A1', 'E2', 'A2', 'E2', 'D3', 'E2', 'A2', 'E2'], 0.5, 0.36, 8, cresc=-0.1)       # Rome: it settles
sing([('D5', 41.0, 2.0), ('C#5', 43.0, 1.8)], 0.46)
bed(['A1', 'E2', 'A2'], 41.0, 4.0, 0.04, swell=[1.0, 0.3])

# ---- 45-49 s · the last morning: almost nothing -------------------------------------
piano.pedal(45.0)
piano.note('A1', 45.2, 0.3, hold=3.5)
piano.note('E4', 46.0, 0.3, hold=1.0)
piano.note('A4', 47.0, 0.28, hold=1.5)

# ---- 49-53.5 s · Calvary: the cello says the whole theme; the piano only walks ---------
piano.pedal(49.1, 50.2, 51.2, 52.7)
for nm, tt_, d, v in [('D3', 49.2, 1.0, 0.5), ('A3', 50.2, 1.0, 0.58), ('G3', 51.2, 0.75, 0.64), ('F3', 51.95, 0.75, 0.7), ('E3', 52.7, 0.85, 0.82)]:
    cello.note(nm, tt_, d, v)
for names, tt_, v in [(['D1', 'D2'], 49.2, 0.34), (['D1', 'D2'], 50.2, 0.4), (['G1', 'G2'], 51.2, 0.48), (['A1', 'A2'], 52.7, 0.62)]:
    piano.chord(names, tt_, v, hold=0.9)
bed(['D2', 'A2'], 49.2, 4.1, 0.05, attack=2.0, release=0.8, swell=[0.5, 1.5])
bed(['A3', 'C#4'], 52.2, 1.2, 0.045, attack=1.0, release=0.6, swell=[0.3, 1.3])

# ---- 53.5 s · the light: the bottom octave, a rolled D major, and the top of the piano raining down
piano.pedal(53.45)
piano.chord(['D1', 'D2'], 53.5, 0.98, hold=1.0)
piano.chord(['A2', 'D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5'], 53.52, 0.86, hold=1.0, roll=0.03)
for k, nm in enumerate(['F#6', 'D6', 'A5', 'F#5', 'D6', 'A5', 'F#5', 'D5']):
    piano.note(nm, 53.78 + k * 0.09, 0.62 - 0.02 * k, hold=0.2)
bed(['D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'F#4'], 53.5, 5.0, 0.075, attack=0.8, release=2.5)

# ---- 54.5-58.5 s · the campus: the motif in major, both hands wide -------------------
piano.pedal(54.5, 56.5)
left(54.5, ['G1', 'D2', 'G2', 'B2', 'D3', 'B2', 'G2', 'D2'], 0.25, 0.6, 8)
left(56.5, ['A1', 'E2', 'A2', 'C#3', 'E3', 'C#3', 'A2', 'E2'], 0.25, 0.62, 8)
sing([('D5', 54.5, 1.0), ('A5', 55.5, 1.0), ('G5', 56.5, 1.0), ('F#5', 57.5, 1.0)], 0.84, octave=True)
for nm, tt_ in [('B4', 54.5), ('D5', 55.5), ('C#5', 56.5), ('A4', 57.5)]:
    piano.note(nm, tt_ + 0.01, 0.6, hold=1.0)                       # inner voice fills the hand
bed(['G1', 'G2', 'D3', 'B3'], 54.5, 2.0, 0.07, attack=0.4)
bed(['A1', 'A2', 'E3', 'C#4'], 56.5, 2.0, 0.07, attack=0.4)

# ---- 58.5-65 s · title: home. One rolled chord, a slow climb, and then it is left to ring ----
piano.pedal(58.5)                                                   # the pedal now stays down to the end
piano.chord(['D1', 'D2'], 58.5, 0.84, hold=6.0)
piano.chord(['A2', 'D3', 'F#3', 'A3', 'D4'], 58.53, 0.72, hold=6.0, roll=0.04)
t, gap = 59.25, 0.42
for k, nm in enumerate(['F#4', 'A4', 'D5', 'F#5', 'A5']):
    piano.note(nm, t, 0.5 - 0.05 * k, hold=5.0)
    t += gap
    gap *= 1.22                                                     # ritardando
piano.note('D6', 62.6, 0.3, hold=2.4)
bed(['D2', 'A2', 'D3', 'F#3', 'A3'], 58.5, 2.2, 0.07, attack=0.5, release=3.0, swell=[1.0, 0.25])

# ---- render, warm the piano, place everything in one hall ----------------------------
keys = warm(piano.render(N)) * 0.9
solo = cello.render(N) * 0.55
mix = keys + solo + pad

ir_n = int(3.6 * SR)
ir_t = np.arange(ir_n) / SR
wet = np.zeros_like(mix)
size = 1 << int(np.ceil(np.log2(N + ir_n)))
for ch in range(2):
    ir = rng.standard_normal(ir_n) * np.exp(-ir_t * 1.8) * np.minimum(ir_t / 0.025, 1)
    ir = np.convolve(ir, np.ones(8) / 8, 'same')  # dark, long tail
    ir /= np.sqrt(np.sum(ir ** 2))
    wet[:, ch] = np.fft.irfft(np.fft.rfft(mix[:, ch], size) * np.fft.rfft(ir, size), size)[:N]
out = mix + 0.36 * wet

fade_out = np.ones(N)
tail = int(0.8 * SR)                                # the piano has already died away; this only closes the file
fade_out[N - tail:] = np.cos(np.linspace(0, np.pi / 2, tail)) ** 2
out *= fade_out[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.3) / np.tanh(1.3) * 0.92

path = os.path.join(os.path.dirname(__file__), '..', 'out', 'music-raw', 'cross-bearer-score.wav')  # mastered afterwards, see master.sh
os.makedirs(os.path.dirname(path), exist_ok=True)
with wave.open(path, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())

rms = lambda a, b: 20 * np.log10(np.sqrt(np.mean(out[int(a * SR):int(b * SR)] ** 2)) + 1e-9)
print(f'{os.path.normpath(path)}  {N / SR:.1f}s  peak {np.max(np.abs(out)):.2f}  piano notes {len(piano.events)}')
for a, b, nm in [(0, 8, 'opening'), (8, 13, 'sweep'), (13, 29, 'flowing'), (29, 41, 'building'), (41, 49, 'settling'),
                 (49, 53.5, 'cello'), (53.5, 54.5, 'light'), (54.5, 58.5, 'major'), (58.5, 60, 'last chord')]:
    print(f'  {nm:10s} {a:>5}-{b:<4} {rms(a, b):6.1f} dBFS')
print('  ring-out   ' + '  '.join(f'{s}s {rms(s, s + 1):.0f}' for s in range(59, 65)))
