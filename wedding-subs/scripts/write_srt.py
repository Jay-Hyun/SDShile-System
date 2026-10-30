#!/usr/bin/env python3
"""renders/wedding-subs.ko.srt and .en.srt from assets/js/subs.js (lyrics and messages; English for lyrics only)."""
import json

S = json.loads(open("assets/js/subs.js").read().split("window.SUBS = ", 1)[1].rstrip().rstrip(";"))


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


ko = [(l["s"], l["e"], l["ko"]) for l in S["lyrics"]] + [(m["s"], m["e"], f'[{m["who"]}] {m["ko"]}') for m in S["msgs"]]
en = [(l["s"], l["e"], l["en"]) for l in S["lyrics"]]
for name, rows in (("ko", sorted(ko)), ("en", en)):
    with open(f"renders/wedding-subs.{name}.srt", "w") as f:
        for i, (s, e, t) in enumerate(rows, 1):
            f.write(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n")
    print(name, len(rows))
