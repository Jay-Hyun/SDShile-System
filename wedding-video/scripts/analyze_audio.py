#!/usr/bin/env python3
"""Beat grid + energy/section map for the song.

Writes data/beats.json:
  { bpm, beats:[s], downbeats:[s], energy:[{t, rms}], novelty_peaks:[s] }
Downbeats: the beat phase (0..3) whose beats carry the most low-frequency onset energy.
Run with the media venv: /opt/mediaenv/bin/python scripts/analyze_audio.py assets/raw/drive/root/song.mp3
"""
import json
import sys

import librosa
import numpy as np

path = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "data/beats.json"
y, sr = librosa.load(path, sr=22050, mono=True)
hop = 512

onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=hop, start_bpm=103, tightness=400)
beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)

# fit a straight line to the beat times: a studio track has a fixed tempo, so a regression
# removes tracker jitter while keeping the true phase
idx = np.arange(len(beats))
mid = (beats > 20) & (beats < 230)
slope, intercept = np.polyfit(idx[mid], beats[mid], 1)
bpm = 60.0 / slope
grid = intercept + slope * idx
grid = grid[(grid >= 0) & (grid <= len(y) / sr)]

# downbeat phase from low-band (kick) onset energy
S = np.abs(librosa.stft(y, hop_length=hop))
freqs = librosa.fft_frequencies(sr=sr)
low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[freqs < 150]), sr=sr, hop_length=hop)
gf = librosa.time_to_frames(grid, sr=sr, hop_length=hop)
gf = gf[gf < len(low)]
phase_energy = [low[gf[p::4]].mean() for p in range(4)]
phase = int(np.argmax(phase_energy))
downbeats = grid[phase::4]

rms = librosa.feature.rms(y=y, hop_length=hop)[0]
rt = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
# energy per half-second
energy = []
for t0 in np.arange(0, rt[-1], 0.5):
    m = (rt >= t0) & (rt < t0 + 0.5)
    energy.append({"t": round(float(t0), 2), "rms": round(float(rms[m].mean()), 4)})

# structural novelty from chroma+mfcc self-similarity, used to suggest section boundaries
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13)
feat = librosa.util.sync(np.vstack([chroma, mfcc / 50]), gf, aggregate=np.median)
bounds = librosa.segment.agglomerative(feat, 14)
bound_times = [round(float(grid[min(b, len(grid) - 1)]), 3) for b in bounds]

json.dump({
    "bpm": round(float(bpm), 3),
    "beat_period": round(float(slope), 5),
    "first_beat": round(float(grid[0]), 4),
    "downbeat_phase": phase,
    "beats": [round(float(b), 4) for b in grid],
    "downbeats": [round(float(b), 4) for b in downbeats],
    "section_bounds": bound_times,
    "energy": energy,
}, open(out, "w"), indent=1)
print(f"bpm={bpm:.3f} beats={len(grid)} downbeat_phase={phase} first_downbeat={downbeats[0]:.3f}")
print("section bounds:", bound_times)
