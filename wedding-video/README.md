# 반대가 끌리는 이유 — wedding pre-ceremony lyric film

HyperFrames composition (HTML → MP4) for god「반대가 끌리는 이유」, cut to ~3:05, for 박준익 & 김명지 (2026. 11. 07 SAT).

Story (v5, "두 개의 방, 하나의 집"): one premium miniature world. A dollhouse cross-section on a studio table: his
cobalt room (the orderly study of a purchasing manager: binders with index tabs, a squared stack of documents, a
calculator) and her coral room (a counselor's room: two armchairs facing each other, tissues, a teapot) share one
wall. Light comes through it, they lean and press their hands on it, it
sinks into the floor on "마음이 열렸어", and the ending returns to the opening camera with the wall gone; the card
writes "Happy Wedding Day" by hand (`scripts/calligraphy.py`: the lettering's skeleton as pen strokes). Their real
photos and videos appear only inside the set (picture frames, an oval mirror, a TV, a phone, a corkboard), and each
one fills most of the frame.

Timing: word times come from CTC forced alignment of the isolated vocal (`scripts/realign_lyrics.py`); chorus 1
and the final chorus are the same recording and their independent alignments agree within ~20 ms. Every cut sits
on the beat grid: `scripts/build_data.py` gives each word a cut time `q` (the 16th-note grid point the word is sung
on, minus 10 ms; in the drumless intro, 30 ms ahead of the voice) and snaps the scene boundaries the same way;
scenes cut on `Q(i)`, words light on the voice (`T(i)`), and `scripts/sync_media.py` keeps every video's timing in
step.

Motion language: depth-parallax camera moves on every plate at one constant on-screen speed (linear, so the camera
is still travelling when we cut), hard cuts on the beat (only the drumless intro dissolves, through focus), no
springs, shakes or flashes.
Lyrics are set as a whole line in a quiet tone and each word lights at its sung onset (two-tone colour per
background); in the intro each word breathes in from blur as it is sung, under window light, dust and a soft
glow; rap sections stack rows that recede. Kit: `assets/js/design.js` (`D.*`) on top of the clock and
helpers in `assets/js/kinetic.js` (`K.bridge`, `K.letterbox`, `K.knock/zoomThrough`, `K.leak`).

## Rebuild from scratch

```bash
scripts/fetch_drive.sh                                   # photos, song, references (needs data/drive_manifest.json)
python3 scripts/fetch_icloud.py <shortGUID> assets/raw/icloud
scripts/prep_media.sh all                                # photos 2560 px, footage 1080p/30 fps, rotation fixes
scripts/fetch_fonts.sh && /opt/mediaenv/bin/python scripts/make_textures.py
/opt/mediaenv/bin/python -m demucs --two-stems=vocals -n htdemucs -o assets/audio/demucs assets/raw/drive/root/song.mp3
/opt/mediaenv/bin/python scripts/analyze_audio.py assets/raw/drive/root/song.mp3
/opt/mediaenv/bin/python scripts/align_lyrics.py assets/audio/demucs/htdemucs/song/vocals.wav
/opt/mediaenv/bin/python scripts/realign_lyrics.py       # forced alignment -> data/lyrics.aligned.json (preferred)
/opt/mediaenv/bin/python scripts/edit_audio.py           # 3-minute bar-aligned edit -> assets/audio/edit.wav
python3 scripts/build_data.py                            # -> assets/js/data.js (lyrics in edit time, scenes)
for k in w08 w10 w16 w17; do /opt/mediaenv/bin/python scripts/cutout.py birefnet-portrait $k; done   # likeness refs
curl -L -o /opt/models/da2s.onnx https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx

# v5 world: GPT image generation through the Codex CLI (ChatGPT login: `codex login --device-auth`)
python3 scripts/gen_v5.py --jobs 4                       # data/gen_v5.json -> assets/media/gen5/ (sheets, plates, edits)
/opt/mediaenv/bin/python scripts/key_green.py            # green frames/mirror/TV/phone -> *_keyed.png + frame quads in assets/js/green.js
# her head where she leans on the wall beside him, shrunk with a local warp (reads <id>_orig.png, so re-running
# is safe); the v8 dollhouse plates (E01 family) were drawn with matching heads and need no fix
for a in "E02 948,365,118,170 880,470 0.87 --ramp 70 --keep-x 836 --vfill 836,975" \
         "E02g 948,365,118,170 880,470 0.87 --ramp 70 --keep-x 836 --vfill 836,975" \
         "E02h 1005,320,140,135 1010,480 0.87 --ramp 60 --keep-x 852 --vfill 852,940" \
         "E02r 967,320,125,125 880,440 0.87 --ramp 60 --keep-x 846 --vfill 846,975"; do
  /opt/mediaenv/bin/python scripts/fix_head.py $a       # one process per plate (rembg)
done
python3 scripts/sync_media.py                            # beat-grid cuts -> video data-start/duration, scene hosts, clip lengths
scripts/living_v5.sh                                     # constant-speed depth camera moves (data/living_v5.tsv) -> assets/media/living/v5_*.mp4
/opt/mediaenv/bin/python scripts/calligraphy.py         # Happy Wedding Day pen strokes -> assets/js/calligraphy.js
npx hyperframes check && npx hyperframes render --sdr -w 4 -o renders/wedding-v8.mp4 .
```

`assets/media/gen5/E09w.png` (the partition wall that sinks in s3) is cut from E09a with the hands painted out;
the snippet that made it is in the v5 commit history. Knockout-type geometry: `scripts/knock_points.py`.

Couple names and date live in `data/couple.json`; the film shows no venue. Reference analysis:
`docs/reference-notes.md`. Film spec: `SPEC.md`.

iPhone HDR clips (HLG/BT.2020, P3) are tone-mapped to SDR Rec.709 in `prep_media.sh`
(zscale → linear, npl 203 → mobius); render with `--sdr` so nothing promotes the output to HDR.
