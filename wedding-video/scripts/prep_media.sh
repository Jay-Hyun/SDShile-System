#!/usr/bin/env bash
# Normalise raw media into render-friendly copies under assets/media/.
#   videos: autorotate, long edge 1920, 30 fps CFR, H.264, GOP 10 (fast seeking), no audio,
#           iPhone HDR (HLG / BT.2020) tone-mapped and Display-P3 converted to SDR Rec.709
#   photos: long edge 2560 (wedding) / original size capped at 2560 (date), JPEG q2
# Usage: scripts/prep_media.sh videos|photos|all
# Per-file manual rotation fixes live in ROTATE below (clockwise degrees, applied after autorotate).
set -euo pipefail
cd "$(dirname "$0")/.."
mode=${1:-all}

declare -A ROTATE=(
  ["_talkv_wzs9pQxft3_O5aLyPzqk4vOf5qr0kjHzk_talkv_high.mov"]=90
  ["IMG_1196.MOV"]=270
  ["IMG_1197.MOV"]=180
  ["IMG_1199.MOV"]=180
)

prep_videos() {
  mkdir -p assets/media/video
  python3 -I -c 'import json;[print(str(i) + chr(9) + m["file"]) for i, m in enumerate(json.load(open("assets/raw/icloud/manifest.json")))]' |
  while IFS=$'\t' read -r i f; do
    src="assets/raw/icloud/$f"
    out=$(printf "assets/media/video/v%02d.mp4" "$i")
    [ -f "$out" ] && continue
    rot=${ROTATE[$f]:-0}
    vf="fps=30"
    case $rot in
      90) vf="$vf,transpose=1" ;;
      180) vf="$vf,transpose=1,transpose=1" ;;
      270) vf="$vf,transpose=2" ;;
    esac
    vf="$vf,scale='if(gt(iw,ih),min(1920,iw),-2)':'if(gt(iw,ih),-2,min(1920,ih))':flags=lanczos,setsar=1"
    trc=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$src")
    pri=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_primaries -of csv=p=0 "$src")
    if [ "$trc" = "arib-std-b67" ] || [ "$trc" = "smpte2084" ]; then
      vf="$vf,zscale=tin=$trc:pin=bt2020:min=bt2020nc:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709"
      vf="$vf,tonemap=tonemap=mobius:desat=0:param=0.3,zscale=t=bt709:m=bt709:r=tv"
    elif [ "$pri" = "smpte432" ]; then
      vf="$vf,zscale=pin=smpte432:p=bt709:tin=bt709:t=bt709:m=bt709:r=tv"
    fi
    ffmpeg -nostdin -v error -y -i "$src" -vf "$vf,format=yuv420p" -an -c:v libx264 -preset medium -crf 17 \
      -pix_fmt yuv420p -g 10 -keyint_min 10 -sc_threshold 0 -color_primaries bt709 -color_trc bt709 \
      -colorspace bt709 -movflags +faststart "$out"
    echo "$out <- $f ($(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$out"))"
  done
}

prep_photos() {
  for folder in wedding date video_folder; do
    mkdir -p "assets/media/photo/$folder"
    find "assets/raw/drive/$folder" -type f -iname '*.jp*g' -print0 2>/dev/null |
    xargs -0 -P 4 -I{} bash -c '
      src="$1"; folder="$2"
      base=$(basename "$src"); base="${base%.*}"
      out="assets/media/photo/$folder/$(echo "$base" | tr " " "_").jpg"
      [ -f "$out" ] && exit 0
      ffmpeg -nostdin -v error -y -i "$src" -vf "scale='"'"'if(gt(iw,ih),min(2560,iw),-2)'"'"':'"'"'if(gt(iw,ih),-2,min(2560,ih))'"'"':flags=lanczos" -q:v 2 "$out"
    ' _ {} "$folder"
    echo "photos/$folder: $(find "assets/media/photo/$folder" -type f | wc -l)"
  done
}

case $mode in
  videos) prep_videos ;;
  photos) prep_photos ;;
  all) prep_videos; prep_photos ;;
esac
