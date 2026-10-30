#!/usr/bin/env python3
"""Force-align the friends' messages (data/messages.json) to the draft's vocal stem -> data/messages.timed.json."""
import json

import librosa
import torchaudio

from align_words import align

bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=True)
model.eval()
DICT = bundle.get_dict(star="*")
y, sr = librosa.load("work/demucs/htdemucs/draft/vocals.wav", sr=bundle.sample_rate, mono=True)
M = json.load(open("data/messages.json"))
for key, sec in M.items():
    words = [(li, w) for li, l in enumerate(sec["lines"]) for w in l["ko"].split()]
    times = align(y, sr, [w for _, w in words], sec["t0"], sec["t1"], model, DICT)
    for l in sec["lines"]:
        l["words"] = []
    for (li, w), tt in zip(words, times):
        sec["lines"][li]["words"].append({"t": w, "s": tt[0] if tt else None, "e": tt[1] if tt else None})
    for l in sec["lines"]:
        ws = [w for w in l["words"] if w["s"] is not None]
        l["start"], l["end"] = ws[0]["s"], ws[-1]["e"]
        print(f'{key:6s} {l["start"]:7.2f}-{l["end"]:7.2f} {l.get("who", "")} {l["ko"]}')
json.dump(M, open("data/messages.timed.json", "w"), ensure_ascii=False, indent=1)
