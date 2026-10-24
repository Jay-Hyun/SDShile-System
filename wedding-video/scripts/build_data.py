#!/usr/bin/env python3
"""Map the timed lyrics and beat grid onto the edit and write assets/js/data.js (window.FILM).

Also writes data/edit_lyrics.json (same content, for review) and data/film.json (FILM for the Python tools).
Run after align_lyrics.py and edit_audio.py.
Scenes are chapters of the edit, in edit seconds; every scene file reads its window from FILM.scenes.

Word times come from data/lyrics.aligned.json (scripts/realign_lyrics.py, forced alignment) when present.

Cut timing: every word also gets `q`, the cut time for a shot that opens on that word: the 16th-note grid point
the word is sung on (onset + 35 ms, rounded to the grid) minus 10 ms, so the new picture is up on the frame the
syllable lands; never at or before the previous word, which must stay on the outgoing shot. The intro has no
drums to lock to, so there a cut simply leads the voice by 30 ms. Scene boundaries are the q of the scene's first
word. Shots cut on Q(i); words light on their sung onset.
"""
import json
import math
import os

cuts = json.load(open("data/cuts.json"))
beats = json.load(open("data/beats.json"))
lyrics = json.load(open("data/lyrics.aligned.json" if os.path.exists("data/lyrics.aligned.json") else "data/lyrics.timed.json"))
couple = json.load(open("data/couple.json"))

NOMINAL = [  # id, nominal start (edit seconds), what it is; starts are snapped to the beat grid below
    ("s0", 0.0, "intro: the two rooms, opposites, the title split by the wall"),
    ("s1", 17.40, "rap 1: he watches the girl next door"),
    ("s2", 54.53, "chorus 1: light through the wall, their memories inside the set"),
    ("s3", 92.56, "rap 2: night; the wall goes down"),
    ("s4", 115.80, "bridge: one room, two chairs, widescreen"),
    ("s5", 132.70, "final chorus: the real photos on their walls"),
    ("s6", 171.60, "outro: the house at night, the card"),
]

period = beats["beat_period"]
first = beats["first_beat"]


def grid(a, b, step):
    """grid points (quarter = period, 8th = period / 2) in [a, b]"""
    k0 = math.ceil((a - first) / step - 1e-9)
    k1 = math.floor((b - first) / step + 1e-9)
    return [round(first + k * step, 4) for k in range(k0, k1 + 1)]


LEAD = 0.035  # the sung onset sits this far ahead of its grid point (consonant before the beat)


def snap(onset, lo=-1.0, hi=1e9, free=False):
    """cut for a shot that opens on a word sung at `onset`: its 16th-note grid point - 10 ms (strictly after lo)"""
    t = onset - 0.03
    if not free:
        # grid points the syllable can belong to: up to 120 ms before its onset, at most 40 ms after it
        g = grid(onset - 0.12, onset + 0.04, period / 4)
        if g:
            t = min(g, key=lambda p: abs(p - (onset + LEAD))) - 0.01
    return round(min(max(t, lo + 0.02), hi), 4)


def to_edit(t):
    """source seconds -> edit seconds, or None if t falls in a removed span"""
    for seg in cuts["segments"]:
        if seg["src0"] - 1e-6 <= t < seg["src1"] + 1e-6:
            return round(seg["dst0"] + (t - seg["src0"]), 3)
    return None


def scene_of(t, scenes):
    for sid, a, b, _ in scenes:
        if a <= t < b:
            return sid
    return scenes[-1][0]


NOM = [(sid, a, NOMINAL[i + 1][1] if i + 1 < len(NOMINAL) else cuts["duration"], n) for i, (sid, a, n) in enumerate(NOMINAL)]

out = []
for e in lyrics:
    words = []
    for w in e["words"]:
        s, en = to_edit(w["start"]), to_edit(w["end"])
        if s is None:
            continue
        words.append({"t": w["t"], "start": s, "end": en if en is not None else round(s + 0.3, 3)})
    if not words:
        continue
    out.append({"line": e["line"], "section": e["section"], "scene": scene_of(words[0]["start"], NOM),
                "text": " ".join(w["t"] for w in words), "start": words[0]["start"], "end": words[-1]["end"],
                "words": words})

# a line can straddle a scene boundary only at a pickup; give each word its own scene too
for e in out:
    for w in e["words"]:
        w["scene"] = scene_of(w["start"], NOM)

# snap scene boundaries to the grid without moving any word to another scene
allw = [w for e in out for w in e["words"]]
starts = [0.0]
for sid, a, _ in NOMINAL[1:]:
    before = [w["start"] for w in allw if w["start"] < a]
    after = [w["start"] for w in allw if w["start"] >= a]
    lo = (before[-1] + 0.02) if before else 0.0
    if after and after[0] - a < 3.0:
        starts.append(snap(after[0], lo=lo, hi=after[0] - 0.001))
    else:  # instrumental boundary: nearest quarter beat
        starts.append(min(grid(a - period, a + period, period), key=lambda p: abs(p - a)))
SCENES = [(sid, starts[i], starts[i + 1] if i + 1 < len(starts) else cuts["duration"], n)
          for i, (sid, _, n) in enumerate(NOMINAL)]
for e in out:
    for w in e["words"]:
        assert scene_of(w["start"], SCENES) == w["scene"], (w, "changed scene")

# the musical cut time for every word (a shot that opens on it)
prev = -1.0
scene_start = {sid: a for sid, a, _, _ in SCENES}
for w in allw:
    s0 = scene_start[w["scene"]]
    first_in_scene = all(x["start"] >= w["start"] for x in allw if x["scene"] == w["scene"])
    w["q"] = s0 if first_in_scene else snap(w["start"], lo=max(prev + 0.08, s0 + 0.05), free=w["start"] < 15.0)
    prev = w["start"]

film = {
    "fps": 30,
    "duration": cuts["duration"],
    "bpm": beats["bpm"],
    "beatPeriod": period,
    "firstBeat": first,  # the beat grid is continuous through the edit (cuts are whole bars)
    "firstDownbeat": beats["downbeats"][0],
    "scenes": {sid: {"start": a, "dur": round(b - a, 3), "note": n} for sid, a, b, n in SCENES},
    "lyrics": out,
    "couple": couple,
    "photos": json.load(open("data/photos.json")),
}
json.dump(out, open("data/edit_lyrics.json", "w"), ensure_ascii=False, indent=1)
json.dump(film, open("data/film.json", "w"), ensure_ascii=False, indent=1)
with open("assets/js/data.js", "w") as f:
    f.write("/* generated by scripts/build_data.py — do not edit */\nwindow.FILM = ")
    json.dump(film, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")
print(f"{len(out)} lines, {sum(len(e['words']) for e in out)} words, duration {cuts['duration']}")
print("scenes:", " ".join(f"{sid}@{a:.3f}" for sid, a, _, _ in SCENES))
for e in out:
    print(f'{e["scene"]} {e["start"]:7.2f}-{e["end"]:7.2f} {e["text"][:60]}')
