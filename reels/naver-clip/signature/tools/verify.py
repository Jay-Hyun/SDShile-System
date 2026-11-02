"""Verify a render: ffprobe, loudness, cut-vs-downbeat audit and a centring re-check on decoded frames.

python3 tools/verify.py renders/last-signature-30s.mp4 30
python3 tools/verify.py renders/last-signature-15s.mp4 15

Cuts are detected from the MP4 itself, on luma AND chroma: each frame is scaled to 160x284 YCbCr and
the score is mean |dY| + mean |dCb| + mean |dCr| between consecutive frames, so a hue change with
little luma change (Ink #0E1116 -> Navy #0B1A33) still registers. A frame is a cut when its score is
>= 18 and >= 3x the local median (wipes and entrances spread over many frames do not qualify).
Every detected cut is matched to the nearest beat and the nearest DOWNBEAT of the excerpt
(beats/source.json); the planned cuts (beats/cuts*.json) are listed with the measured frame.

Centring: at 4 frames per cut the DOM text boxes are measured by tools/measure.cjs (same seek), the
same frames are decoded from the MP4 at full size, and inside each line's box the glyph ink is found
against the local ground: the table reports the DOM box centre and the ink centre against x=540.
Writes renders/verify-<v>s.json and a contact strip around each planned cut (renders/cuts-<v>s.jpg).
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mp4, V = sys.argv[1], sys.argv[2]
OFFSET = {"30": 1.776, "15": 10.971}[V]
CENTRE_FRAMES = {"30": [415, 628, 816, 894], "15": [36, 243, 366, 444]}[V]
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

# ------------------------------------------------------------------ cuts (luma + chroma)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={W}:{H},format=yuv444p", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 3, H, W).astype(np.float32)   # planar Y, Cb, Cr
diff = np.abs(np.diff(fr, axis=0)).mean(axis=(2, 3)).sum(axis=1)             # diff[i] = change i -> i+1
cuts = []
for i in range(len(diff)):
    lo, hi = max(0, i - 8), min(len(diff), i + 9)
    loc = np.median(np.r_[diff[lo:i], diff[i + 1:hi]])
    if diff[i] >= 18 and diff[i] >= 3 * max(loc, 1.5) and diff[i] == diff[max(0, i - 2):i + 3].max():
        cuts.append(i + 1)  # first frame of the new picture

SRC = json.load(open(os.path.join(ROOT, "beats", "source.json")))
B0 = min(range(len(SRC["beats"])), key=lambda k: abs(SRC["beats"][k] - OFFSET))
grid = [b - SRC["beats"][B0] for b in SRC["beats"][B0:]]
downs = [d - SRC["beats"][B0] for d in SRC["downbeats"] if d >= SRC["beats"][B0] - 0.01]
beat_frames = np.array([g * FPS for g in grid])
down_frames = np.array([d * FPS for d in downs])
down_idx = {int(np.argmin(np.abs(beat_frames - d))) for d in down_frames}


def near(f):
    k = int(np.argmin(np.abs(beat_frames - f)))
    j = int(np.argmin(np.abs(down_frames - f)))
    return k, f - beat_frames[k], f - down_frames[j]


rows, ok, okd = [], 0, 0
for f in cuts:
    k, d, dd = near(f)
    hit, hitd = abs(d) <= 2, abs(dd) <= 2
    ok += hit
    okd += hitd
    rows.append(dict(frame=f, t=round(f / FPS, 3), beat=k, downbeat=k in down_idx, off_beat_frames=round(float(d), 2),
                     off_downbeat_frames=round(float(dd), 2), within2=bool(hit), on_downbeat=bool(hitd), score=round(float(diff[f - 1]), 1)))
print(f"\ndetected cuts: {len(cuts)}; within +-2 frames of a beat: {ok}; of a downbeat: {okd}")
print(" frame      t   beat  downbeat  off-beat(fr)  off-downbeat(fr)  score")
for r_ in rows:
    print(f" {r_['frame']:5d} {r_['t']:7.3f}  B{r_['beat']:<3d}   {'yes' if r_['downbeat'] else 'no ':3s}      {r_['off_beat_frames']:+6.2f}           {r_['off_downbeat_frames']:+7.2f}      {r_['score']:5.1f}")

planned = json.load(open(os.path.join(ROOT, "beats", "cuts.json" if V == "30" else "cuts-15s.json")))["cuts"]
print("\nplanned cuts -> nearest detected cut")
pl = []
for c in planned:
    f = c["frame"]
    m = min(cuts, key=lambda x: abs(x - f)) if cuts else None
    k, d, dd = near(f)
    pl.append(dict(c, detected=m, detected_off=(m - f) if m is not None else None, beat_off=round(float(d), 2)))
    print(f"  {c['label']:<20s} t={c['t']:6.3f} f{f:<4d} B{k:<3d} {'downbeat' if k in down_idx else 'beat    '} detected f{m} ({(m - f) if m is not None else 'n/a':+})")

# ------------------------------------------------------------------ centring on decoded frames
tmpd = tempfile.mkdtemp(prefix="verify-")
times = ",".join(f"{f / FPS:.6f}" for f in CENTRE_FRAMES)
env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
subprocess.run(["node", os.path.join(ROOT, "tools", "measure.cjs"), "--variant", V, "--at", times, "--json",
                os.path.join(tmpd, "m.json"), "--shots", tmpd], env=env, capture_output=True, check=False)
dom = json.load(open(os.path.join(tmpd, "m.json")))["report"]
centring = []
worst_dom, worst_ink = 0.0, 0.0
print("\ncentring on decoded MP4 frames (DOM box centre / glyph-ink centre in the decoded pixels, vs x=540)")
for f, rep in zip(CENTRE_FRAMES, dom):
    img = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{f})", "-vframes", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    px = np.frombuffer(img, np.uint8).reshape(1920, 1080, 3).astype(np.int32)
    print(f"  frame {f} (t={f / FPS:.3f}s)")
    for ln in rep["rows"]:
        left, right = ln["cx"] - ln["w"] / 2, ln["cx"] + ln["w"] / 2
        y0, y1 = int(ln["top"]) + 3, int(ln["bottom"]) - 3
        x0, x1 = max(0, int(left) - 40), min(1080, int(right) + 40)
        band = px[y0:y1, x0:x1]
        sides = np.r_[px[y0:y1, x0:max(x0, int(left) - 12)].reshape(-1, 3), px[y0:y1, min(x1, int(right) + 12):x1].reshape(-1, 3)]
        bg = np.median(sides if len(sides) else band.reshape(-1, 3), axis=0)
        ink = (np.abs(band - bg).sum(axis=2) > 90).sum(axis=0) >= 2
        if not ink.any():
            continue
        xs = np.nonzero(ink)[0]
        icx = x0 + (xs[0] + xs[-1] + 1) / 2
        worst_dom = max(worst_dom, abs(ln["dx"]))
        worst_ink = max(worst_ink, abs(icx - 540))
        centring.append(dict(frame=f, text=ln["text"], size=ln["size"], dom_dx=ln["dx"], ink_dx=round(float(icx - 540), 1)))
        print(f"    {ln['size']:>4}px  DOM {ln['dx']:+6.2f}  ink {icx - 540:+6.1f}   {ln['text']}")
print(f"  max |DOM dx| = {worst_dom:.2f} px, max |ink dx| = {worst_ink:.1f} px")

json.dump(dict(probe=dict(width=vs["width"], height=vs["height"], r=vs["r_frame_rate"], frames=vs.get("nb_frames"),
                          duration=probe["format"]["duration"], audio=[a["codec_name"] for a in aus]),
               loudness=dict(I=I, LRA=LRA, TP=TP), detected=rows, planned=pl,
               within2_pct=round(100 * ok / max(1, len(cuts)), 1), on_downbeat=okd,
               centring=dict(frames=CENTRE_FRAMES, max_dom_dx=worst_dom, max_ink_dx=round(worst_ink, 1), lines=centring)),
          open(os.path.join(ROOT, "renders", f"verify-{V}s.json"), "w"), indent=1)

# contact strip: the frame before and the frame at each planned cut
tiles = []
for c in planned:
    tiles += [c["frame"] - 1, c["frame"]]
sel = "+".join(f"eq(n\\,{f})" for f in tiles)
out = os.path.join(ROOT, "renders", f"cuts-{V}s.jpg")
cols = 6
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-vf",
                f"select='{sel}',scale=180:320,drawtext=text='%{{n}}':x=6:y=6:fontsize=18:fontcolor=yellow,tile={cols}x{(len(tiles) + cols - 1) // cols}",
                "-frames:v", "1", "-vsync", "vfr", out], check=False)
print("strip:", out)
