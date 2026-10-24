#!/usr/bin/env python3
"""Generate the film's illustrated world with GPT image generation through the Codex CLI (ChatGPT login).

Reads data/gen_assets.json; for each item asks `codex exec` to make one image and save it to
assets/media/gen/<id>.png. Characters get the couple's own cutouts attached as likeness references.
Items with "alpha": true are generated on a flat background and cut out afterwards (scripts/cutout_gen.py).

Usage: python3 scripts/gen_images.py [ids...] [--jobs 3] [--force]
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
M = json.load(open("data/gen_assets.json"))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
jobs = int(next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--jobs"), 3))
force = "--force" in sys.argv
items = [it for it in M["items"] if not args or it["id"] in args]
os.makedirs("assets/media/gen", exist_ok=True)
os.makedirs("assets/media/gen/log", exist_ok=True)


def brief(it):
    out = f"assets/media/gen/{it['id']}.png"
    who = []
    refs = []
    if it["kind"] in ("char", "pair"):
        for w in (["groom", "bride"] if it["kind"] == "pair" else [it["who"]]):
            who.append(M[w])
            refs.append(M["refs"][w])
        who.append(M["figurine"])
    bg = ("Isolate the subject on a perfectly flat, plain light warm grey background (#e8e5df), no floor line, "
          "no props around it, soft contact shadow only directly under it.") if it["alpha"] else "Full-bleed scene, no border."
    likeness = ("The attached photos are the real couple: keep their hairstyles, glasses, face shapes and overall "
                "look recognisable, translated into the clay figurine style (do not make it photorealistic).") if refs else ""
    text = f"""Use your image generation tool to create exactly ONE image, then save it as a PNG file at this exact path
inside the working folder: {out}
Aspect/size: {it['size']} (landscape if wider than tall).

Art style (keep it identical across the whole series): {M['style']}
{' '.join(who)}
Subject: {it['prompt']}
{bg}
{likeness}

Do not draw any text or letters. When the file is saved, reply with only the saved path."""
    return out, refs, text


def run(it):
    out, refs, text = brief(it)
    if os.path.exists(out) and not force:
        return f"{it['id']}: exists"
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", ROOT, "--sandbox", "workspace-write",
           "-o", f"assets/media/gen/log/{it['id']}.md", "-"]  # prompt from stdin; images after it so -i can't eat "-"
    for r in refs:
        cmd += ["-i", r]
    p = subprocess.run(cmd, input=text, text=True, capture_output=True, timeout=900)
    ok = os.path.exists(out)
    open(f"assets/media/gen/log/{it['id']}.log", "w").write(p.stdout[-4000:] + "\n---\n" + p.stderr[-4000:])
    return f"{it['id']}: {'ok' if ok else 'MISSING'} (exit {p.returncode})"


with ThreadPoolExecutor(jobs) as ex:
    for r in ex.map(run, items):
        print(r, flush=True)
