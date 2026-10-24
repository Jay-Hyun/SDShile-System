# 반대가 끌리는 이유 — wedding pre-ceremony lyric film

HyperFrames composition (HTML → MP4) for god「반대가 끌리는 이유」, cut to ~3:05.
Kinetic lyrics run on anime.js v4 driven by each scene's GSAP clock (`assets/js/kinetic.js`, `K.bridge`).
Look: ivory / film black / studio grey, gothic (Pretendard) ↔ myeongjo (Noto Serif KR), the couple's own
photos and footage, two Blender inserts (black lacquer × white porcelain title, gold rings).

## Rebuild from scratch

```bash
scripts/fetch_drive.sh                                   # photos, song, references (needs data/drive_manifest.json)
python3 scripts/fetch_icloud.py <shortGUID> assets/raw/icloud
scripts/prep_media.sh all                                # photos 2560 px, footage 1080p/30 fps, rotation fixes
scripts/fetch_fonts.sh && /opt/mediaenv/bin/python scripts/make_textures.py
/opt/mediaenv/bin/python -m demucs --two-stems=vocals -n htdemucs -o assets/audio/demucs assets/raw/drive/root/song.mp3
/opt/mediaenv/bin/python scripts/analyze_audio.py assets/raw/drive/root/song.mp3
/opt/mediaenv/bin/python scripts/align_lyrics.py assets/audio/demucs/htdemucs/song/vocals.wav
/opt/mediaenv/bin/python scripts/edit_audio.py           # 3-minute bar-aligned edit -> assets/audio/edit.wav
python3 scripts/build_data.py                            # -> assets/js/data.js (lyrics in edit time, scenes)
for k in w03 w05 ...; do /opt/mediaenv/bin/python scripts/cutout.py birefnet-portrait $k; done   # one per process
blender -b -P scripts/blender/b1_title_v2.py -- --out renders/blender/b1/ --samples 10
blender -b -P scripts/blender/b4_rings.py -- --out renders/blender/b4/ --samples 10
scripts/encode_inserts.sh b1 b4                          # PNG sequences -> VP9-alpha webm + last-frame stills
npx hyperframes check && npx hyperframes render
```

Couple names, date and venue live in `data/couple.json` (placeholders until confirmed).
Reference analysis: `docs/reference-notes.md`. Film spec: `SPEC.md`.
