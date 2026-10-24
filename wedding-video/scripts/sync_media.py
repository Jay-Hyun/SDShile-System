#!/usr/bin/env python3
"""Keep every media timing in step with the beat-grid cuts in data/film.json (scripts/build_data.py).

1. Scene hosts in index.html get FILM.scenes start/dur.
2. Every <video data-shot="A,B"> in compositions/*.html gets data-start/data-duration covering its shot, plus
   PRE/POST seconds of handle. A and B are scene-local word indices (the shot cuts on that word's q), "end"
   (the scene end) or "bN" (absolute beat N).
3. data/living_v5.tsv: each depth clip gets the duration its longest use needs, and a move amount that gives the
   same on-screen speed in every shot (so the camera drifts at one pace through the film, never stops at a cut).

Usage: python3 scripts/sync_media.py [--check]   (--check reports without writing)
"""
import glob
import json
import re
import subprocess
import sys

PRE, POST = 0.15, 0.15
CHECK = "--check" in sys.argv
F = json.load(open("data/film.json"))
P, B0 = F["beatPeriod"], F["firstBeat"]
SC = F["scenes"]


def words_of(sid):
    return [w for l in F["lyrics"] for w in l["words"] if w["scene"] == sid]


def at(token, sid):
    s = SC[sid]
    if token == "end":
        return s["dur"]
    if token.startswith("b"):
        return B0 + int(token[1:]) * P - s["start"]
    i = int(token)
    if i == 0:
        return 0.0
    return words_of(sid)[i]["q"] - s["start"]


_dur = {}


def clip_len(path):
    if path not in _dur:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout.strip()
        _dur[path] = float(out) if out else 0.0
    return _dur[path]


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def set_attr(tag, name, value):
    if attr(tag, name) is None:
        return tag.replace("<video ", f'<video {name}="{value}" ', 1)
    return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', tag, count=1)


need = {}
problems = []
for path in sorted(glob.glob("compositions/*.html")):
    html = open(path).read()
    sid = re.search(r'data-composition-id="(s\d)"', html).group(1)
    dur = SC[sid]["dur"]

    def fix(m):
        tag = m.group(0)
        shot = attr(tag, "data-shot")
        if not shot:
            return tag
        a, b = shot.split(",")
        t0, t1 = at(a, sid), at(b, sid)
        if t1 - t0 < 0.2:
            problems.append(f"{sid} {attr(tag, 'id')}: shot {shot} is {t1 - t0:.3f} s")
        s = round(max(0.0, t0 - PRE), 3)
        e = round(min(dur, t1 + POST), 3)
        tag = set_attr(tag, "data-start", f"{s:g}")
        tag = set_attr(tag, "data-duration", f"{e - s:g}")
        src = attr(tag, "src")
        rate = float(attr(tag, "data-playback-rate") or 1)
        mstart = float(attr(tag, "data-media-start") or 0)
        used = mstart + (e - s) * rate
        name = re.match(r"assets/media/living/(v5_[^/.]+)\.mp4$", src or "")
        if name:
            need[name.group(1)] = max(need.get(name.group(1), 0.0), used)
        elif clip_len(src) + 1e-3 < used:
            problems.append(f"{sid} {attr(tag, 'id')}: needs {used:.2f} s of {src} ({clip_len(src):.2f} s)")
        print(f"  {sid} {attr(tag, 'id'):10s} shot {shot:9s} -> start {s:7.3f} dur {e - s:6.3f}")
        return tag

    new = re.sub(r"<video\b[^>]*>", fix, html)
    if new != html and not CHECK:
        open(path, "w").write(new)

# scene hosts
idx = open("index.html").read()
for sid, s in SC.items():
    idx = re.sub(rf'(<div id="{sid}" [^>]*?data-start=")[^"]*(" data-duration=")[^"]*(")',
                 lambda m: f'{m.group(1)}{round(s["start"], 4)}{m.group(2)}{round(s["dur"], 4)}{m.group(3)}', idx)
if not CHECK:
    open("index.html", "w").write(idx)

# depth clips: duration from use, amount from a constant on-screen speed
SPEED = {"push": 0.022 / 0.16, "pull": 0.020 / 0.14, "left": 26 / 90, "right": 26 / 90, "up": 22 / 70, "down": 22 / 70,
         "push-left": 0.022 / 0.12, "push-right": 0.022 / 0.12, "pull-up": 0.020 / 0.10}
rows = []
for line in open("data/living_v5.tsv"):
    if line.startswith("#") or not line.strip():
        rows.append(line)
        continue
    name, plate, d, move, amount, focus, zoom, size = line.rstrip("\n").split("\t")
    if name in need:
        d = round(need[name] + 0.25, 2)
        a = min(1.3, SPEED[move] * d)
        z = float(zoom)
        if move in ("left", "right"):  # keep a long truck inside the overscan
            z = max(z, round(1 + max(0.0, 90 * a - 105) / 1700, 3))
        line = "\t".join([name, plate, f"{d:g}", move, f"{a:.2f}", focus, f"{z:g}", size]) + "\n"
    rows.append(line)
if not CHECK:
    open("data/living_v5.tsv", "w").write("".join(rows))

print("scenes:", " ".join(f"{k}@{v['start']:g}+{v['dur']:g}" for k, v in SC.items()))
print("depth clips:", ", ".join(f"{k} {v:.2f}s" for k, v in sorted(need.items())))
for p in problems:
    print("PROBLEM", p)
sys.exit(1 if problems else 0)
