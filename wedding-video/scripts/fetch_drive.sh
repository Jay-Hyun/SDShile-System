#!/usr/bin/env bash
# Download every file listed in data/drive_manifest.json from the publicly shared Drive folder.
# Usage: scripts/fetch_drive.sh [folder ...]   (default: wedding date video_folder root)
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=assets/raw/drive
folders=("${@:-wedding date video_folder root}")
[ $# -eq 0 ] && folders=(wedding date video_folder root)

python3 -I - "${folders[@]}" <<'EOF' > /tmp/drive_jobs.$$
import json, sys
want = set(sys.argv[1:])
for f in json.load(open("data/drive_manifest.json")):
    if f["folder"] in want:
        print(f'{f["id"]}\t{f["folder"]}\t{f["title"]}\t{f.get("size", 0)}')
EOF

fetch() {
  IFS=$'\t' read -r id folder title size <<<"$1"
  dir="$OUT/$folder"; mkdir -p "$dir"
  dest="$dir/$title"
  if [ -f "$dest" ] && [ "$(stat -c%s "$dest")" = "$size" ]; then return 0; fi
  for attempt in 1 2 3 4; do
    curl -sSL --fail -o "$dest.part" \
      "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" && break
    sleep $((2 ** attempt))
  done
  mv "$dest.part" "$dest"
  echo "ok $folder/$title"
}
export -f fetch; export OUT
tr '\n' '\0' < /tmp/drive_jobs.$$ | xargs -0 -P 4 -I{} bash -c 'fetch "$@"' _ {}
rm -f /tmp/drive_jobs.$$
echo "done: $(find "$OUT" -type f | wc -l) files"
