#!/usr/bin/env bash
# Depth-parallax camera moves for the v5 plates (data/living_v5.tsv), 3 at a time.
# Usage: scripts/living_v5.sh [name ...]   (no names = every row whose plate exists and clip is missing)
cd "$(dirname "$0")/.."
PY=/opt/mediaenv/bin/python
grep -v '^#' data/living_v5.tsv | while IFS=$'\t' read -r name plate dur move amount focus zoom size; do
  [ -n "$name" ] || continue
  if [ $# -gt 0 ]; then printf '%s\n' "$@" | grep -qx "$name" || continue
  elif [ -f "assets/media/living/$name.mp4" ]; then continue; fi
  [ -f "assets/media/gen5/$plate.png" ] || { echo "skip $name (no $plate)" >&2; continue; }
  echo "$PY scripts/living_photo.py assets/media/gen5/$plate.png $name --dur $dur --move $move --amount $amount --focus $focus --zoom $zoom --size $size --dof 0.25 --ease linear"
done | xargs -P 3 -I{} sh -c '{} 2>&1 | tail -1'
