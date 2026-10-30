#!/usr/bin/env python3
"""Time every word of a list of display lines against a vocal stem with CTC forced alignment (torchaudio MMS_FA).

Hangul is romanised (Revised Romanization from the jamo) for the MMS character set; <star> tokens at the two ends
of the window absorb any audio before the first and after the last word.

Usage: python scripts/align_words.py <vocals.wav> <lines.json> <t0> <t1> <out.json>
lines.json: [{"ko": "...", ...}, ...]; out.json: the same list with "words": [{"t", "s", "e"}] (seconds in the file).
"""
import json
import re
import sys

import librosa
import torch
import torchaudio

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


def align(y, sr, words, t0, t1, model, DICT):
    wav = torch.from_numpy(y[int(t0 * sr): int(t1 * sr)]).float().unsqueeze(0)
    with torch.inference_mode():
        emission, _ = model(wav)
    emission = emission[0]
    tokens, owner = [DICT["*"]], [-1]
    for i, w in enumerate(words):
        for ch in romanize(w):
            tokens.append(DICT[ch])
            owner.append(i)
    tokens.append(DICT["*"])
    owner.append(-1)
    ali, _ = torchaudio.functional.forced_align(emission.unsqueeze(0), torch.tensor([tokens], dtype=torch.int32), blank=0)
    ali = ali[0].tolist()
    ratio = (wav.shape[1] / sr) / emission.shape[0]
    spans, ti, prev = {}, -1, 0
    for f, tok in enumerate(ali):
        if tok != 0 and (tok != prev or prev == 0):
            ti += 1
        if tok != 0 and 0 <= ti < len(owner) and owner[ti] >= 0:
            s = spans.setdefault(owner[ti], [f, f])
            s[1] = f
        prev = tok
    return [(round(t0 + spans[i][0] * ratio, 3), round(t0 + (spans[i][1] + 1) * ratio, 3)) if i in spans else None
            for i in range(len(words))]


if __name__ == "__main__":
    vocals, lines_path, t0, t1, out_path = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True)
    model.eval()
    DICT = bundle.get_dict(star="*")
    y, sr = librosa.load(vocals, sr=bundle.sample_rate, mono=True)
    lines = json.load(open(lines_path))
    words = [(li, w) for li, l in enumerate(lines) for w in l["ko"].split()]
    times = align(y, sr, [w for _, w in words], t0, t1, model, DICT)
    for l in lines:
        l["words"] = []
    for (li, w), tt in zip(words, times):
        s, e = tt if tt else (None, None)
        lines[li]["words"].append({"t": w, "s": s, "e": e})
    for l in lines:
        ws = [w for w in l["words"] if w["s"] is not None]
        l["start"], l["end"] = (ws[0]["s"], ws[-1]["e"]) if ws else (None, None)
    json.dump(lines, open(out_path, "w"), ensure_ascii=False, indent=1)
    for l in lines:
        print(f'{l["start"]:7.2f}-{l["end"]:7.2f}  {l["ko"]}')
