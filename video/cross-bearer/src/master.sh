#!/usr/bin/env bash
# Polish and master the synthesised score with the bitwize-music plugin's audio tools.
#   BITWIZE=<checkout of bitwize-music-studio/claude-ai-music-skills> src/master.sh
# Needs the plugin venv: ~/.bitwize-music/venv (matchering, pyloudnorm, scipy, soundfile, noisereduce).
set -euo pipefail
cd "$(dirname "$0")/.."
: "${BITWIZE:?set BITWIZE to the plugin checkout}"
PY="${BITWIZE_PY:-$HOME/.bitwize-music/venv/bin/python}"
RAW=out/music-raw
rm -rf "$RAW/polished" "$RAW/mastered"
"$PY" "$BITWIZE/tools/mixing/mix_tracks.py" "$RAW" --full-mix --genre cinematic --output-dir polished
"$PY" "$BITWIZE/tools/mastering/master_tracks.py" "$RAW/polished" --genre cinematic --output-dir mastered
cp "$RAW/polished/mastered/cross-bearer-score.wav" out/music.wav
