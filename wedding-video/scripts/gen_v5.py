#!/usr/bin/env python3
"""v5 asset generator: GPT image generation through the Codex CLI (ChatGPT login), ClaraMuz-style briefs.

Reads data/gen_v5.json. Each item becomes one `codex exec` job that calls the built-in image_gen tool with
explicit referenced_image_paths:
  - character sheets (CS1/CS2) are anchored on the couple's real photos;
  - every shot with people gets the sheets as identity anchors ("do not redesign");
  - "set_ref" passes another plate as the same-room reference;
  - "edit_of" edits an existing plate ("change only X; keep Y unchanged");
  - "green" asks for a flat chroma-green area (a frame, mirror, screen) that is keyed out later.
Phases run in order (sheets -> base plates -> edits); inside a phase jobs run in parallel.

Usage: python3 scripts/gen_v5.py [ids...] [--phase N] [--jobs 3] [--force]
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
M = json.load(open("data/gen_v5.json"))
OUT = M["out"]
argv = sys.argv[1:]
opts = {}
for flag in ("--jobs", "--phase"):
    if flag in argv:
        k = argv.index(flag)
        opts[flag] = int(argv[k + 1])
        del argv[k : k + 2]
force = "--force" in argv
ids = [a for a in argv if not a.startswith("--")]
jobs = opts.get("--jobs", 3)
os.makedirs(f"{OUT}/log", exist_ok=True)
ITEMS = {it["id"]: it for it in M["items"]}


def path_of(ref):
    """An item id (generated plate/sheet) or a project-relative path -> absolute path."""
    p = f"{OUT}/{ref}.png" if ref in ITEMS else ref
    return os.path.join(ROOT, p)


def who(person, outfit):
    return f"{M[person]}, wearing {M['outfits'][outfit][person]}"


def brief(it):
    out = f"{OUT}/{it['id']}.png"
    refs, roles = [], []

    def add(ref, role):
        refs.append(path_of(ref))
        roles.append(f"Image {len(refs)}: {role}")

    outfit = it.get("outfit", "daily")
    lines = []
    if it.get("sheet"):
        person = it["sheet"]
        for p in M["photos"][person]:
            add(p, f"real photo of the {person} (likeness reference only: face shape, glasses, hairstyle; do not copy the photo)")
        lines.append(f"Subject: {who(person, outfit)}.")
        lines.append(M["characters"])
    else:
        if it.get("edit_of"):
            add(it["edit_of"], "the image to EDIT")
        if it.get("set_ref"):
            add(it["set_ref"], "set reference: the same miniature room, furniture, materials and palette")
        for person in it.get("cast", []):
            add(M["sheets"][person], f"character anchor sheet for the {person}: do not redesign; keep exactly the same face, glasses, hairstyle, proportions and look")
        if it.get("cast"):
            lines.append("Characters: " + "; ".join(who(p, outfit) for p in it["cast"]) + ".")
            lines.append(M["characters"])

    w, h = map(int, it["size"].split("x"))
    orient = "landscape" if w > h else "portrait" if h > w else "square"
    green = ""
    if it.get("green"):
        green = (f"Compositing area: the {it['green']} must be filled edge to edge with flat, pure chroma green (#00FF00): "
                 "no reflection, no texture, no gradient, no glare. It will be replaced with footage later.")
    edit = ""
    if it.get("edit_of"):
        edit = ("This is an EDIT of Image 1. Repeat these invariants: same camera angle, framing, set, furniture, "
                "materials, lighting direction and colours; change nothing that is not asked for.")
    ref_line = (f"Call image_gen ONCE with referenced_image_paths set to exactly these files, in this order:\n"
                + "\n".join(f"  {r}" for r in refs) + "\n" + "\n".join(roles)) if refs else \
        "Call image_gen ONCE as a brand-new image (no reference images)."
    text = f"""Use your built-in image generation tool to create exactly ONE image, then save it as a PNG at this exact path inside the working folder:
{out}
{ref_line}

Use case: premium commercial key visual: a still frame for a wedding film shown on a large screen.
Asset type: {orient} {w}x{h} film plate.
{edit}
Primary request: {it['prompt']}
{chr(10).join(lines)}
Style/medium: {M['style']}
Lighting/mood: {M['light']}
Color palette: {M['palette']}
{green}
Constraints: one coherent photographic frame; no text, no letters, no numbers, no logos, no watermark.
Avoid: {M['avoid']}

When the file is saved, reply with only the saved path."""
    return out, text


def run(it):
    out, text = brief(it)
    if os.path.exists(out) and not force:
        return f"{it['id']}: exists"
    for attempt in (1, 2):
        cmd = ["codex", "exec", "--skip-git-repo-check", "-C", ROOT, "--sandbox", "workspace-write",
               "-o", f"{OUT}/log/{it['id']}.md", "-"]
        try:
            p = subprocess.run(cmd, input=text, text=True, capture_output=True, timeout=900)
            open(f"{OUT}/log/{it['id']}.log", "w").write(text + "\n---\n" + p.stdout[-3000:] + "\n---\n" + p.stderr[-3000:])
        except subprocess.TimeoutExpired:
            pass
        if os.path.exists(out):
            return f"{it['id']}: ok" + (" (retry)" if attempt == 2 else "")
    return f"{it['id']}: MISSING"


phases = sorted({it["phase"] for it in M["items"]})
if "--phase" in opts:
    phases = [opts["--phase"]]
for ph in phases:
    todo = [it for it in M["items"] if it["phase"] == ph and (not ids or it["id"] in ids)]
    if not todo:
        continue
    print(f"== phase {ph}: {len(todo)} items", flush=True)
    with ThreadPoolExecutor(jobs) as ex:
        for r in ex.map(run, todo):
            print(r, flush=True)
