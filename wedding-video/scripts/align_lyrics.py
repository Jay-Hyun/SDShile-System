#!/usr/bin/env python3
"""Align the known lyrics (data/lyrics.txt) to the song.

1. transcribe the (ideally vocal-isolated) track with faster-whisper, word timestamps
2. flatten both the transcript and the known lyrics to Hangul/latin syllables
3. difflib-align the syllable sequences; matched lyric syllables take the transcript time,
   unmatched ones are interpolated between their matched neighbours
4. snap word starts to the nearest 16th note of data/beats.json (within 90 ms)

Writes data/whisper_raw.json (cached transcript) and data/lyrics.timed.json:
  [{ "line": i, "text": "...", "start": s, "end": s, "words": [{ "t": "...", "start": s, "end": s }] }]
Usage: /opt/mediaenv/bin/python scripts/align_lyrics.py <audio> [--model large-v3] [--retranscribe]
"""
import argparse
import difflib
import json
import os
import re

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("--model", default="large-v3")
ap.add_argument("--retranscribe", action="store_true")
args = ap.parse_args()

RAW = "data/whisper_raw.json"
lines = [l.strip() for l in open("data/lyrics.txt", encoding="utf-8") if l.strip()]


def syllables(s):
    """Hangul syllables count one each; latin words count as one unit."""
    return re.findall(r"[가-힣]|[A-Za-z]+|[0-9]", s)


if args.retranscribe or not os.path.exists(RAW):
    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    import subprocess
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", args.audio, "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)
    prompt = " ".join(lines[:3])
    segments, info = model.transcribe(
        audio, language="ko", word_timestamps=True, vad_filter=False,
        beam_size=5, initial_prompt=prompt, condition_on_previous_text=False,
    )
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "start": w.start, "end": w.end, "p": w.probability})
        print(f"[{seg.start:7.2f} -> {seg.end:7.2f}] {seg.text}", flush=True)
    json.dump(words, open(RAW, "w"), ensure_ascii=False, indent=0)

words = json.load(open(RAW))

# Repeated choruses defeat one global alignment, so align section by section. Each section lists the
# lyric line indices it holds and the source-time window its words fall in (read off the whisper segments).
SECTIONS = [
    ("intro", range(0, 3), 0.0, 17.7),
    ("rap1", range(3, 8), 17.6, 54.3),
    ("chorus1", range(8, 14), 54.2, 92.75),
    ("rap2", range(14, 22), 92.6, 128.05),
    ("chorus2", range(22, 27), 128.0, 166.8),
    ("final", range(27, 32), 166.7, 222.6),
]

# reference syllables, remembering which line/word each belongs to
line_words = [l.replace("(", " ").replace(")", " ").split() for l in lines]
ref_pos = []
times = []
matched = 0
total = 0
for name, rng_lines, t0, t1 in SECTIONS:
    hyp, hyp_t = [], []
    for w in words:
        if not (t0 <= w["start"] < t1):
            continue
        syl = syllables(w["w"])
        if not syl:
            continue
        span = (w["end"] - w["start"]) / len(syl)
        for k, sy in enumerate(syl):
            hyp.append(sy)
            hyp_t.append((w["start"] + k * span, w["start"] + (k + 1) * span))
    ref, pos = [], []
    for li in rng_lines:
        for wi, w in enumerate(line_words[li]):
            for sy in syllables(w):
                ref.append(sy)
                pos.append((li, wi))
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    sec_times = [None] * len(ref)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            sec_times[a + k] = hyp_t[b + k]
    # pin the section edges so interpolation never leaks across sections
    if sec_times[0] is None:
        sec_times[0] = (hyp_t[0][0], hyp_t[0][1]) if hyp_t else (t0, t0 + 0.2)
    if sec_times[-1] is None:
        sec_times[-1] = (hyp_t[-1][0], hyp_t[-1][1]) if hyp_t else (t1 - 0.2, t1)
    m = sum(t is not None for t in sec_times)
    print(f"section {name}: matched {m}/{len(ref)}")
    matched += m
    total += len(ref)
    ref_pos += pos
    times += sec_times

idx = [i for i, t in enumerate(times) if t is not None]
starts = np.interp(range(len(times)), idx, [times[i][0] for i in idx])
ends = np.interp(range(len(times)), idx, [times[i][1] for i in idx])
section_of = {li: name for name, rng_lines, _, _ in SECTIONS for li in rng_lines}

# onset snap: word starts move to the nearest vocal onset (isolated vocal stem) within 120 ms;
# failing that, to the nearest 16th note within 90 ms
import librosa

vy, vsr = librosa.load(args.audio if os.path.exists(args.audio) else "assets/audio/demucs/htdemucs/song/vocals.wav",
                       sr=22050, mono=True)
onsets = librosa.onset.onset_detect(y=vy, sr=vsr, hop_length=256, units="time", backtrack=True, delta=0.06)
beats = json.load(open("data/beats.json"))
period, first = beats["beat_period"], beats["first_beat"]
sixteenth = period / 4


rms = librosa.feature.rms(y=vy, hop_length=256)[0]
rms_t = np.arange(len(rms)) * 256 / vsr
active = rms > 0.03


def to_voice(t):
    """A word cannot start in vocal silence: push it forward to where the voice starts (<= 0.9 s)."""
    i = int(np.searchsorted(rms_t, t))
    if i < len(active) and active[i:i + 4].any():
        return t
    j = i + int(np.argmax(active[i:i + int(0.9 * vsr / 256)])) if active[i:i + int(0.9 * vsr / 256)].any() else i
    return float(rms_t[min(j, len(rms_t) - 1)])


def snap(t):
    t = max(0.0, to_voice(t))
    if len(onsets):
        k = int(np.argmin(np.abs(onsets - t)))
        if abs(onsets[k] - t) <= 0.12:
            return float(onsets[k])
    g = first + round((t - first) / sixteenth) * sixteenth
    return g if abs(g - t) <= 0.09 else t


out = []
for li, ws in enumerate(line_words):
    entry = {"line": li, "text": lines[li], "section": section_of[li], "words": []}
    for wi, w in enumerate(ws):
        ks = [k for k, p in enumerate(ref_pos) if p == (li, wi)]
        if not ks:
            continue
        st, en = snap(float(starts[ks[0]])), float(ends[ks[-1]])
        conf = sum(times[k] is not None for k in ks) / len(ks)
        entry["words"].append({"t": w, "start": round(st, 3), "end": round(max(en, st + 0.08), 3),
                               "conf": round(conf, 2)})
    entry["start"] = entry["words"][0]["start"]
    entry["end"] = entry["words"][-1]["end"]
    out.append(entry)

# The final chorus is chorus 1 sung again 56 bars later (cross-correlation of the vocal onset envelopes
# gives a lag of 0.00 +- 0.01 s on every line at +129.23 s), and its backing vocals confuse whisper,
# so its words take chorus 1's times, syllable-aligned.
TRANSPLANT = {"src_lines": range(8, 14), "dst": [(28, 7), (29, 0), (30, 0), (31, 0)], "offset": 129.23}
src_syl = []
for li in TRANSPLANT["src_lines"]:
    for w in out[li]["words"]:
        sy = syllables(w["t"])
        span = (w["end"] - w["start"]) / max(1, len(sy))
        for k, x in enumerate(sy):
            src_syl.append((x, w["start"] + k * span + TRANSPLANT["offset"], w["start"] + (k + 1) * span + TRANSPLANT["offset"]))
dst_words = [(li, wi) for li, first in TRANSPLANT["dst"] for wi in range(first, len(out[li]["words"]))]
dst_syl, owner = [], []
for li, wi in dst_words:
    for x in syllables(out[li]["words"][wi]["t"]):
        dst_syl.append(x)
        owner.append((li, wi))
sm = difflib.SequenceMatcher(None, [x[0] for x in src_syl], dst_syl, autojunk=False)
tmap = [None] * len(dst_syl)
for a_, b_, n_ in sm.get_matching_blocks():
    for k in range(n_):
        tmap[b_ + k] = src_syl[a_ + k][1:]
ok_idx = [i for i, t in enumerate(tmap) if t is not None]
ts = np.interp(range(len(dst_syl)), ok_idx, [tmap[i][0] for i in ok_idx])
te = np.interp(range(len(dst_syl)), ok_idx, [tmap[i][1] for i in ok_idx])
for li, wi in dst_words:
    ks = [k for k, o in enumerate(owner) if o == (li, wi)]
    w = out[li]["words"][wi]
    w["start"], w["end"], w["conf"] = round(float(ts[ks[0]]), 3), round(float(te[ks[-1]]), 3), 1.0
print(f"final chorus transplanted from chorus 1: {len(ok_idx)}/{len(dst_syl)} syllables matched")

# manual overrides, then enforce strictly increasing starts (>= 80 ms apart) and ends after starts
if os.path.exists("data/lyrics_overrides.json"):
    ov = json.load(open("data/lyrics_overrides.json"))
    for li, words_ov in ov.items():
        if li.startswith("_"):
            continue
        for w in out[int(li)]["words"]:
            if w["t"] in words_ov:
                w["start"] = words_ov[w["t"]]
flat = [w for e in out for w in e["words"]]
for a_, b_ in zip(flat, flat[1:]):
    if b_["start"] < a_["start"] + 0.08:
        b_["start"] = round(a_["start"] + 0.08, 3)
for a_, b_ in zip(flat, flat[1:]):
    a_["end"] = round(max(a_["start"] + 0.08, min(a_["end"], b_["start"] + 0.4)), 3)
for e in out:
    e["start"], e["end"] = e["words"][0]["start"], e["words"][-1]["end"]

json.dump(out, open("data/lyrics.timed.json", "w"), ensure_ascii=False, indent=1)
print(f"matched {matched}/{total} syllables ({matched / total:.0%})")
for e in out:
    low = [w["t"] for w in e["words"] if w["conf"] < 0.5]
    print(f'{e["start"]:7.2f}-{e["end"]:7.2f} {e["text"][:40]}' + (f"   ?? {low}" if low else ""))
