"""Tiny sample player for the score: a real grand piano and a real cello, read from npm packages.

Piano: Salamander Grand Piano V3 (@audio-samples/piano-velocity3/8/13) — stereo, three velocity
layers, one recording every minor third with its full natural decay.
Cello: tonejs-instrument-cello-mp3 — one bowed note per semitone, a few seconds long.

Notes are pitch-shifted from the nearest recording, blended between velocity layers, held by a
sustain pedal and nudged a few milliseconds off the grid so they sound played, not programmed.
"""
import os
import subprocess
import numpy as np

SR = 48000
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'node_modules')
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLATS = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}


def midi(name):
    """'F#4' / 'Bb2' / 60 -> MIDI number (C4 = 60)."""
    if isinstance(name, (int, np.integer)):
        return int(name)
    pc, octave = name[:-1], int(name[-1])
    return NAMES.index(FLATS.get(pc, pc)) + 12 * (octave + 1)


def decode(path):
    """Any audio file -> float32 stereo at SR, via ffmpeg."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype='<f4').reshape(-1, 2).astype(np.float64)


def shift(sample, semitones, length):
    """Resample so the pitch moves by `semitones`; return at most `length` frames."""
    ratio = 2 ** (semitones / 12)
    n = min(length, int(len(sample) / ratio) - 1)
    pos = np.arange(n) * ratio
    i = pos.astype(int)
    frac = (pos - i)[:, None]
    return sample[i] * (1 - frac) + sample[i + 1] * frac


class Piano:
    LAYERS = (3, 8, 13)                       # soft, medium, hard hammers
    ZONES = [n + o for o in '1234567' for n in ('C', 'D#', 'F#', 'A')] + ['A0', 'C8']

    def __init__(self, seed=3):
        self.rng = np.random.default_rng(seed)
        self.samples = {}
        for v in self.LAYERS:
            for z in self.ZONES:
                path = os.path.join(ROOT, '@audio-samples', f'piano-velocity{v}', 'audio', f'{z}v{v}.ogg')
                if os.path.exists(path):
                    self.samples[(midi(z), v)] = path
        self.zone_notes = sorted({m for m, _ in self.samples})
        self.cache = {}
        self.events = []      # (time, midi, velocity 0..1, key-up time)
        self.pedals = [0.0]   # times at which the sustain pedal is lifted and pressed again

    def _load(self, key):
        if key not in self.cache:
            self.cache[key] = decode(self.samples[key])
        return self.cache[key]

    def pedal(self, *times):
        self.pedals.extend(times)

    def note(self, name, t, vel=0.5, hold=0.4, human=True):
        if human:
            t += self.rng.normal(0, 0.006)
            vel *= 1 + self.rng.normal(0, 0.05)
        self.events.append((max(t, 0.0), midi(name), float(np.clip(vel, 0.05, 1.0)), t + hold))

    def chord(self, names, t, vel=0.5, hold=0.6, roll=0.022):
        """Bottom-to-top, slightly rolled, top note a touch louder."""
        for k, nm in enumerate(names):
            self.note(nm, t + k * roll, vel * (1.08 if k == len(names) - 1 else 0.94), hold)

    def render(self, n):
        out = np.zeros((n, 2))
        pedals = sorted(self.pedals) + [1e9]
        for t, m, vel, up in sorted(self.events):
            zone = min(self.zone_notes, key=lambda z: abs(z - m))
            # the damper falls at the first pedal change after the key comes up
            release = next(p for p in pedals if p >= up)
            length = min(n - int(t * SR), int((release - t + 0.6) * SR))
            if length <= 0:
                continue
            # blend the two velocity layers either side of this touch
            x = vel * 2
            lo, hi, mix = (3, 8, x) if x < 1 else (8, 13, x - 1)
            a = shift(self._load((zone, lo)), m - zone, length)
            b = shift(self._load((zone, hi)), m - zone, length)
            k = min(len(a), len(b))
            sig = a[:k] * (1 - mix) + b[:k] * mix
            # damper: quick but not instant fade once released
            rel = int((release - t) * SR)
            if rel < k:
                fade = np.exp(-np.arange(k - rel) / (0.11 * SR))
                sig[rel:] *= fade[:, None]
            # high notes sit right, low notes left, as heard from the bench — gently
            pan = np.clip((m - 60) / 60, -0.5, 0.5)
            sig = sig * np.array([1 - 0.35 * pan, 1 + 0.35 * pan]) * (0.25 + 0.75 * vel ** 1.4)
            i = int(t * SR)
            out[i:i + k] += sig
        return out


class Cello:
    def __init__(self):
        self.dir = os.path.join(ROOT, 'tonejs-instrument-cello-mp3')
        self.cache = {}
        self.events = []

    def note(self, name, t, dur, vel=0.6):
        self.events.append((t, midi(name), dur, vel))

    def render(self, n):
        out = np.zeros((n, 2))
        have = {}
        for f in os.listdir(self.dir):
            if f.endswith('.mp3') and ' ' not in f:
                have[midi(f[:-4].replace('s', '#'))] = os.path.join(self.dir, f)
        for t, m, dur, vel in self.events:
            zone = min(have, key=lambda z: abs(z - m))
            if zone not in self.cache:
                self.cache[zone] = decode(have[zone])
            sig = shift(self.cache[zone], m - zone, int((dur + 0.35) * SR)).copy()
            k = len(sig)
            tt = np.arange(k) / SR
            sig *= (np.minimum(tt / 0.06, 1) * np.minimum(np.maximum(k / SR - tt, 0) / 0.3, 1))[:, None]  # bow on, bow off
            i = int(t * SR)
            k = min(k, n - i)
            out[i:i + k] += sig[:k] * vel
        return out


def warm(x, cutoff=3200.0, depth_db=-5.0):
    """Felt-piano tilt: ease the top end down with a smooth shelf (FFT, zero phase)."""
    spec = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    shelf = 10 ** (depth_db / 20 * (1 / (1 + (cutoff / np.maximum(f, 1)) ** 2)))
    return np.fft.irfft(spec * shelf[:, None], len(x), axis=0)
