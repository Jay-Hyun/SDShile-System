#!/usr/bin/env bash
# Blender PNG sequences -> VP9 alpha WebM (what the scenes play) + the last frame as a still for the hold.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/media/blender
for b in "$@"; do
  src="renders/blender/$b"
  [ -d "$src" ] || { echo "no $src"; continue; }
  ffmpeg -nostdin -v error -y -framerate 30 -i "$src/f_%04d.png" -c:v libvpx-vp9 -pix_fmt yuva420p \
    -b:v 0 -crf 18 -row-mt 1 -deadline good -cpu-used 2 -auto-alt-ref 0 "assets/media/blender/$b.webm"
  cp "$(ls "$src"/f_*.png | tail -1)" "assets/media/blender/${b}_last.png"
  echo "$b: $(ls "$src"/f_*.png | wc -l) frames -> assets/media/blender/$b.webm"
done
