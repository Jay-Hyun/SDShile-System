#!/usr/bin/env python3
"""Re-time every lyric word with CTC forced alignment (torchaudio MMS_FA) on the isolated vocal.

The first pass (align_lyrics.py) took word times from faster-whisper, which drift by 0.2-0.5 s on sung
vocals. Here each section of data/lyrics.timed.json is aligned again: the words are romanised (Revised
Romanization from the Hangul jamo), framed by <star> tokens that absorb neighbouring audio, and aligned
against the vocal stem inside a window around the section. Word start = first character frame, end = last.

Writes data/lyrics.aligned.json (same shape as lyrics.timed.json, source seconds); build_data.py prefers it.
Usage: /opt/mediaenv/bin/python scripts/realign_lyrics.py [--margin 0.8]
"""
import argparse
import json
import re

import librosa
import numpy as np
import torch
import torchaudio

ap = argparse.ArgumentParser()
ap.add_argument("--margin", type=float, default=0.8)
ap.add_argument("--vocals", default="assets/audio/demucs/htdemucs/song/vocals.wav")
args = ap.parse_args()

CHO = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
JUNG = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu",
        "eu", "ui", "i"]
JONG = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t", "ng",
        "t", "t", "k", "t", "p", "t"]


def romanize(word):
    out = []
    for ch in word:
        c = ord(ch) - 0xAC00
        if 0 <= c <= 11171:
            out.append(CHO[c // 588] + JUNG[(c % 588) // 28] + JONG[c % 28])
        elif re.match(r"[A-Za-z]", ch):
            out.append(ch.lower())
    return "".join(out)


bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=True)
model.eval()
DICT = bundle.get_dict(star="*")
SR = bundle.sample_rate

y, _ = librosa.load(args.vocals, sr=SR, mono=True)
lines = json.load(open("data/lyrics.timed.json"))

# sections in order
order = []
for e in lines:
    if not order or order[-1] != e["section"]:
        order.append(e["section"])
groups = []
for sec in order:
    g = [e for e in lines if e["section"] == sec]
    groups.append(g)

out = json.loads(json.dumps(lines))
by_line = {e["line"]: e for e in out}
report = []
for g in groups:
    words = [w for e in g for w in e["words"]]
    a = max(0.0, words[0]["start"] - args.margin)
    b = min(len(y) / SR, max(w["end"] for w in words) + args.margin)
    wav = torch.from_numpy(y[int(a * SR): int(b * SR)]).float().unsqueeze(0)
    with torch.inference_mode():
        emission, _ = model(wav)
    emission = emission[0]
    rom = [romanize(w["t"]) for w in words]
    keep = [i for i, r in enumerate(rom) if r]
    # <star> only at the two ends (it absorbs the neighbouring audio); between words the alignment must stay tight
    tokens = [DICT["*"]]
    owner = [-1]
    for i in keep:
        for ch in rom[i]:
            tokens.append(DICT[ch])
            owner.append(i)
    tokens.append(DICT["*"])
    owner.append(-1)
    targets = torch.tensor([tokens], dtype=torch.int32)
    ali, scores = torchaudio.functional.forced_align(emission.unsqueeze(0), targets, blank=0)
    ali = ali[0].tolist()
    ratio = (wav.shape[1] / SR) / emission.shape[0]
    # walk the frame path: token index advances on each non-blank change
    spans = {}
    ti = -1
    prev = 0
    for f, tok in enumerate(ali):
        if tok != 0 and (tok != prev or prev == 0):
            ti += 1
        if tok != 0 and 0 <= ti < len(owner) and owner[ti] >= 0:
            s = spans.setdefault(owner[ti], [f, f])
            s[1] = f
        prev = tok
    for k, (e_line, w) in enumerate([(e["line"], w) for e in g for w in e["words"]]):
        if k not in spans:
            continue
        s0, s1 = spans[k]
        ns = round(a + s0 * ratio, 3)
        ne = round(a + (s1 + 1) * ratio, 3)
        for ow in by_line[e_line]["words"]:
            if ow is not None and ow["t"] == w["t"] and abs(ow["start"] - w["start"]) < 1e-6:
                report.append((g[0]["section"], w["t"], w["start"], ns))
                ow["start"], ow["end"] = ns, max(ne, ns + 0.08)
                break
    for e in g:
        le = by_line[e["line"]]
        le["start"] = le["words"][0]["start"]
        le["end"] = le["words"][-1]["end"]

json.dump(out, open("data/lyrics.aligned.json", "w"), ensure_ascii=False, indent=1)
d = np.array([r[3] - r[2] for r in report])
print(f"{len(report)} words re-timed; shift median {np.median(np.abs(d)) * 1000:.0f} ms, p90 {np.percentile(np.abs(d), 90) * 1000:.0f} ms")
for sec, t, old, new in report:
    if abs(new - old) > 0.12:
        print(f"  {sec:10s} {t:8s} {old:8.3f} -> {new:8.3f}  ({(new - old) * 1000:+.0f} ms)")

# ---- post-process -------------------------------------------------------------------------------------------
# 1. the final chorus is the same recording as chorus 1 (a whole number of bars later): align the two word lists,
#    and give both the same relative timing (the mean where the two alignments agree, otherwise the candidate that
#    keeps the word order and sits closer to the 16th-note grid).
# 2. outside the intro (no drums to lock to), snap word starts to the 16th grid when within 50 ms
#    (the vocal lands ~35 ms ahead of the grid: consonant before the beat).
beats = json.load(open("data/beats.json"))
P16 = beats["beat_period"] / 4
B0 = beats["first_beat"]
LEAD = 0.035


def grid_dist(t):
    k = round((t + LEAD - B0) / P16)
    return (t + LEAD) - (B0 + k * P16)


final = json.load(open("data/lyrics.aligned.json"))
c1 = [w for e in final if e["section"] == "chorus1" for w in e["words"]]
fc = [w for e in final if e["section"] == "final" for w in e["words"] if w["start"] >= 183.0]
pairs = []
i = j = 0
while i < len(c1) and j < len(fc):
    a, b = c1[i]["t"], fc[j]["t"]
    if a == b or a.startswith(b) or b.startswith(a):
        pairs.append((c1[i], fc[j]))
        i += 1
        j += 1
    elif i + 1 < len(c1) and c1[i + 1]["t"] == b:
        i += 1
    else:
        j += 1
offs = sorted(b["start"] - a["start"] for a, b in pairs)
OFF = offs[len(offs) // 2]
prev_rel = None
fixed = 0
for k, (a, b) in enumerate(pairs):
    ra, rb = a["start"], b["start"] - OFF
    if abs(ra - rb) <= 0.15:
        rel = (ra + rb) / 2
    else:
        nxt = None
        if k + 1 < len(pairs):
            na, nb = pairs[k + 1]
            nxt = (na["start"] + nb["start"] - OFF) / 2
        cands = [c for c in (ra, rb) if (prev_rel is None or c > prev_rel + 0.05) and (nxt is None or c < nxt - 0.05)]
        rel = min(cands or [ra, rb], key=lambda c: abs(grid_dist(c)))
        fixed += 1
    da, db_ = a["end"] - a["start"], b["end"] - b["start"]
    a["start"], b["start"] = round(rel, 3), round(rel + OFF, 3)
    a["end"], b["end"] = round(rel + max(da, 0.08), 3), round(rel + OFF + max(db_, 0.08), 3)
    prev_rel = rel
print(f"chorus pair: {len(pairs)} words, offset {OFF:.3f} s, {fixed} disagreements resolved")

snapped = 0
for e in final:
    if e["section"] == "intro":
        continue
    for w in e["words"]:
        d = grid_dist(w["start"])
        if abs(d) <= 0.05:
            w["start"] = round(w["start"] - d, 3)
            snapped += 1
for e in final:
    ws = e["words"]
    for k in range(len(ws) - 1):  # keep order after snapping
        if ws[k + 1]["start"] <= ws[k]["start"]:
            ws[k + 1]["start"] = round(ws[k]["start"] + 0.06, 3)
    e["start"], e["end"] = ws[0]["start"], ws[-1]["end"]
print(f"snapped {snapped} word starts to the 16th grid")
json.dump(final, open("data/lyrics.aligned.json", "w"), ensure_ascii=False, indent=1)

# 3. a section's first word cannot start before the previous section's last word (the aligner can grab the tail
#    of the previous section for a short pickup like "Yo"): put it one 16th before the next word instead.
final = json.load(open("data/lyrics.aligned.json"))
prev_last = None
moved = 0
for sec in order:
    ws = [w for e in final if e["section"] == sec for w in e["words"]]
    if prev_last is not None and ws and ws[0]["start"] < prev_last + 0.1 and len(ws) > 1:
        ws[0]["start"] = round(max(prev_last + 0.1, ws[1]["start"] - P16), 3)
        ws[0]["end"] = round(min(ws[0]["end"], ws[1]["start"]), 3) if ws[0]["end"] > ws[0]["start"] else round(ws[0]["start"] + 0.08, 3)
        moved += 1
    if ws:
        prev_last = ws[-1]["start"]
for e in final:
    e["start"], e["end"] = e["words"][0]["start"], e["words"][-1]["end"]
print(f"moved {moved} section-leading words after the previous section")
json.dump(final, open("data/lyrics.aligned.json", "w"), ensure_ascii=False, indent=1)
