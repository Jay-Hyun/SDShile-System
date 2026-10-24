#!/usr/bin/env python3
"""Cut the song to ~3 minutes on bar boundaries and remap every timed thing to the edit.

Cuts are whole bars, so the beat phase never shifts. Each cut point sits at downbeat + phi, where
phi (shared by both sides of a cut) is searched so the isolated vocal is quietest at both seams.
Seams get a 25 ms equal-power crossfade.

Writes assets/audio/edit.wav and data/cuts.json:
  { "segments": [{"src0","src1","dst0"}], "removed": [[src0, src1]], "duration" }
Usage: /opt/mediaenv/bin/python scripts/edit_audio.py
"""
import json

import librosa
import numpy as np
import soundfile as sf

SONG = "assets/raw/drive/root/song.mp3"
VOX = "assets/audio/demucs/htdemucs/song/vocals.wav"
OUT = "assets/audio/edit.wav"

# (first bar removed, first bar kept again, phi or None to search, crossfade s, why)
# phi is chosen by line: rap2's dropped lines (도무지 97.42 ... 있는데) span exactly 6 bars up to 반대라서 (111.27),
# so the seams sit just before 도무지 and just before 반대라서; chorus2 keeps its pickup line and lands just
# before the bridge's 두 (166.81), both seams on the sustained 요 of 같아요.
CUTS = [
    (42, 48, -0.323, 0.04, "rap2: drop 도무지 … 이상한 게 있는데 (3 lines)"),
    (56, 72, -0.160, 0.06, "chorus2: keep its pickup 사랑할 것 같아요, land on the bridge 두 사람 이렇게"),
    (98, 107, 0.0, 0.025, "outro: drop 9 instrumental bars"),
]

beats = json.load(open("data/beats.json"))
period = beats["beat_period"]
bar = 4 * period
first_down = beats["downbeats"][0]

y, sr = sf.read(SONG, always_2d=True) if SONG.endswith(".wav") else (None, None)
if y is None:
    y, sr = librosa.load(SONG, sr=44100, mono=False)
    y = y.T
vox, vsr = librosa.load(VOX, sr=22050, mono=True)
vrms = librosa.feature.rms(y=vox, hop_length=110)[0]  # 5 ms hops
vt = np.arange(len(vrms)) * 110 / vsr


def vocal_energy(t, w=0.06):
    m = (vt >= t - w) & (vt <= t + w)
    return float(vrms[m].mean()) if m.any() else 0.0


removed, fades = [], []
for b0, b1, phi, xfade, why in CUTS:
    t0, t1 = first_down + b0 * bar, first_down + b1 * bar
    if phi is None:
        phi = min((vocal_energy(t0 + p) + vocal_energy(t1 + p) + 0.002 * abs(p), p)
                  for p in np.arange(-0.6, 0.25, 0.005))[1]
    removed.append((round(t0 + phi, 4), round(t1 + phi, 4)))
    fades.append(xfade)
    print(f"cut bars {b0}-{b1}: {t0 + phi:.3f} -> {t1 + phi:.3f} (phi {phi:+.3f}, vocal "
          f"{vocal_energy(t0 + phi):.3f}/{vocal_energy(t1 + phi):.3f}, xfade {xfade * 1000:.0f} ms)  {why}")

total = len(y) / sr
segments, src = [], 0.0
for r0, r1 in removed:
    segments.append((src, r0))
    src = r1
segments.append((src, total))

parts, out_segments, dst = [], [], 0.0
for i, (s0, s1) in enumerate(segments):
    a, b = int(round(s0 * sr)), int(round(s1 * sr))
    xf_next = int(fades[i] * sr) if i < len(fades) else 0
    # carry xf_next/2 samples past the seam so the crossfade is centred on it
    chunk = y[a - (int(fades[i - 1] * sr) // 2 if i else 0):b + xf_next // 2].copy()
    if parts:
        xf = int(fades[i - 1] * sr)
        fade_in = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
        fade_out = np.cos(np.linspace(0, np.pi / 2, xf))[:, None]
        prev = parts[-1]
        tail = prev[-xf:] * fade_out + chunk[:xf] * fade_in
        parts[-1] = prev[:-xf]
        chunk = np.concatenate([tail, chunk[xf:]])
    parts.append(chunk)
    out_segments.append({"src0": round(s0, 4), "src1": round(s1, 4), "dst0": round(dst, 4)})
    dst += s1 - s0
audio = np.concatenate(parts)
sf.write(OUT, audio, sr, subtype="PCM_16")
json.dump({"segments": out_segments, "removed": removed, "duration": round(len(audio) / sr, 4)},
          open("data/cuts.json", "w"), indent=1)
print(f"edit: {len(audio) / sr:.2f} s -> {OUT}")
