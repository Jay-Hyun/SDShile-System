#!/usr/bin/env bash
# Fonts used by the film (all OFL). Static Blender instances are derived from the variable fonts.
set -euo pipefail
cd "$(dirname "$0")/../assets" && mkdir -p fonts && cd fonts
G=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sfL -o NotoSerifKR-VF.ttf "$G/notoserifkr/NotoSerifKR%5Bwght%5D.ttf"
curl -sfL -o CormorantGaramond-Italic.ttf "$G/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf"
curl -sfL -o OFL-google-fonts.txt "$G/jua/OFL.txt"
for w in Bold Black ExtraBold; do
  curl -sfL -o "Pretendard-$w.woff2" "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/woff2/Pretendard-$w.woff2"
done
/opt/mediaenv/bin/python - <<'PY'
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
instancer.instantiateVariableFont(TTFont("NotoSerifKR-VF.ttf"), {"wght": 700}).save("NotoSerifKR-Bold.ttf")
for w in ("Black", "ExtraBold"):
    f = TTFont(f"Pretendard-{w}.woff2"); f.flavor = None; f.save(f"Pretendard-{w}.ttf")
PY
echo "fonts ready"
