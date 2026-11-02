"""Verify a render against the beat grid: ffprobe, loudness, and cut-vs-beat audit.

python3 tools/verify.py renders/last-signature-30s.mp4 30
python3 tools/verify.py renders/last-signature-15s.mp4 15

Cuts are detected from the MP4 itself: mean absolute luma difference between consecutive frames
(160x284 grey), a frame is a cut when its diff is >= 3x the local median and >= 18/255.
Each detected cut is matched to the nearest beat of the excerpt (beats/source.json); planned cuts
(beats/cuts*.json) are listed with the measured frame. Writes renders/verify-<v>s.json and a
contact strip of the frames around each planned cut (renders/cuts-<v>s.jpg).
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mp4, V = sys.argv[1], sys.argv[2]
OFFSET = {"30": 1.776, "15": 10.971}[V]
FPS = 30
W, H = 160, 284

probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4],
                                  capture_output=True, text=True, check=True).stdout)
vs = [s for s in probe["streams"] if s["codec_type"] == "video"][0]
aus = [s for s in probe["streams"] if s["codec_type"] == "audio"]
print(f"video {vs['codec_name']} {vs['width']}x{vs['height']} r={vs['r_frame_rate']} frames={vs.get('nb_frames')} "
      f"dur={float(vs.get('duration', 0)):.3f}  format dur={float(probe['format']['duration']):.3f}")
for a in aus:
    print(f"audio {a['codec_name']} {a['sample_rate']}Hz ch={a['channels']} dur={float(a.get('duration', 0)):.3f}")
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"],
                   capture_output=True, text=True)
summ = r.stderr[r.stderr.rfind("Summary:"):]
I = float(summ.split("I:")[1].split("LUFS")[0])
LRA = float(summ.split("LRA:")[1].split("LU")[0])
TP = float(summ.split("Peak:")[1].split("dBFS")[0])
print(f"loudness I={I:.1f} LUFS  LRA={LRA:.1f} LU  true peak={TP:.1f} dBTP")

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))  # diff[i] = change from frame i to i+1
cuts = []
for i in range(len(diff)):
    lo, hi = max(0, i - 8), min(len(diff), i + 9)
    loc = np.median(np.r_[diff[lo:i], diff[i + 1:hi]])
    if diff[i] >= 18 and diff[i] >= 3 * max(loc, 1.5) and diff[i] == diff[max(0, i - 2):i + 3].max():
        cuts.append(i + 1)  # first frame of the new picture

B = json.load(open(os.path.join(ROOT, "beats", "source.json")))["beats"]
grid = [b - OFFSET for b in B if b >= OFFSET - 0.01]
beat_frames = np.array([g * FPS for g in grid])


def near(f):
    k = int(np.argmin(np.abs(beat_frames - f)))
    return k, f - beat_frames[k]


rows = []
ok = 0
for f in cuts:
    k, d = near(f)
    hit = abs(d) <= 2
    ok += hit
    rows.append(dict(frame=f, t=round(f / FPS, 3), beat=k, beat_t=round(grid[k], 3), off_frames=round(float(d), 2), within2=bool(hit),
                     diff=round(float(diff[f - 1]), 1)))
print(f"\ndetected cuts: {len(cuts)}, within ±2 frames of a beat: {ok} ({100 * ok / max(1, len(cuts)):.0f}%)")
print(" frame     t   beat  beat_t  off(fr)  diff")
for r_ in rows:
    print(f" {r_['frame']:5d} {r_['t']:6.3f}  B{r_['beat']:<3d} {r_['beat_t']:6.3f}  {r_['off_frames']:+6.2f}  {r_['diff']:5.1f} {'OK' if r_['within2'] else '--'}")

planned = json.load(open(os.path.join(ROOT, "beats", "cuts.json" if V == "30" else "cuts-15s.json")))["cuts"]
print("\nplanned cuts -> nearest detected cut")
pl = []
for c in planned:
    f = c["frame"]
    m = min(cuts, key=lambda x: abs(x - f)) if cuts else None
    k, d = near(f)
    pl.append(dict(c, detected=m, detected_off=(m - f) if m is not None else None, beat=k, beat_off=round(float(d), 2)))
    print(f"  {c['label']:<22s} t={c['t']:6.3f} f{f:<4d} beat B{k} ({d:+.2f} fr)  detected f{m} ({(m - f) if m is not None else 'n/a':+})")
json.dump(dict(probe=dict(width=vs["width"], height=vs["height"], r=vs["r_frame_rate"], frames=vs.get("nb_frames"),
                          duration=probe["format"]["duration"], audio=[a["codec_name"] for a in aus]),
               loudness=dict(I=I, LRA=LRA, TP=TP), detected=rows, planned=pl,
               within2_pct=round(100 * ok / max(1, len(cuts)), 1)),
          open(os.path.join(ROOT, "renders", f"verify-{V}s.json"), "w"), indent=1)

# contact strip: the frame before and the frame at each planned cut
tiles = []
for c in planned:
    for f in (c["frame"] - 1, c["frame"]):
        tiles.append(f)
sel = "+".join(f"eq(n\\,{f})" for f in tiles)
out = os.path.join(ROOT, "renders", f"cuts-{V}s.jpg")
cols = 6
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-vf",
                f"select='{sel}',scale=180:320,drawtext=text='%{{n}}':x=6:y=6:fontsize=18:fontcolor=yellow,tile={cols}x{(len(tiles) + cols - 1) // cols}",
                "-frames:v", "1", "-vsync", "vfr", out], check=False)
print("strip:", out)
