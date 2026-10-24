#!/bin/bash
# Every living-photo clip the film uses: key name size dur move focus [amount] [layers]
# "layers" also writes <name>_bg.mp4 + <name>_fg.webm (subject alone, VP9 alpha) for type-behind-subject shots
cd "$(dirname "$0")/.."
P=/opt/mediaenv/bin/python
while read -r key name size dur move focus amount layers; do
  [ -z "$key" ] || [ "${key:0:1}" = "#" ] && continue
  [ -f "assets/media/living/$name.mp4" ] && continue
  nice -n 10 $P scripts/living_photo.py "$key" "$name" --size "$size" --dur "$dur" --move "$move" --focus "$focus" --amount "${amount:-1}" ${layers:+--layers}
done <<'LIST'
# chorus 1
w03 c1_w03 1920x1080 4.5 push 0.5,0.2
w10 c1_w10 960x1080 3.6 push-right 0.5,0.28
w23 c1_w23 960x1080 3.6 push-left 0.5,0.3
w33 c1_w33 1920x1080 4.6 push 0.5,0.55 0.8
w40 c1_w40 1920x1080 3.6 pull 0.5,0.38
w30 c1_w30 1920x1080 2.2 right 0.5,0.42 1.4
w31 c1_w31 1920x1080 2.2 left 0.5,0.4 1.4
w36 c1_w36 1920x1080 2.2 push 0.5,0.45
w05 c1_w05 1920x1080 3.0 push 0.5,0.2
w03 c1_w03L 1920x1080 4.5 push 0.5,0.24 0.9 layers
w05 c1_w05L 1920x1080 3.0 push 0.5,0.22 1 layers
# rap 2
w29 r2_w29 1920x1080 5.0 push 0.5,0.24
# bridge (letterboxed diptych, then together)
w11 br_w11 960x830 9.6 left 0.5,0.34 0.8
w13 br_w13 960x830 9.6 right 0.5,0.3 0.8
w12 br_w12L 1920x1080 8.0 push 0.5,0.42 0.7 layers
# final chorus
w06 fc_w06 1920x1080 2.6 push 0.5,0.3 1.2
w41 fc_w41 640x1080 7.0 push 0.5,0.4
w43 fc_w43 640x1080 6.0 up 0.5,0.45
w44 fc_w44 640x1080 5.6 push 0.5,0.4
w19 fc_w19 1920x1080 4.6 push-left 0.5,0.24
w35 fc_w35 1920x1080 2.8 push 0.5,0.55
w38 fc_w38 1920x1080 2.8 right 0.5,0.5
w45 fc_w45 1920x1080 3.0 pull 0.5,0.5
w04 fc_w04L 1920x1080 3.4 push 0.5,0.22 1 layers
# generated dioramas (gen:<id> = assets/media/gen/<id>.png)
gen:e01 g_e01 1920x1080 2.4 push 0.5,0.5 1
gen:e05 g_e05 1920x1080 2.6 push 0.5,0.55 1
gen:e08 g_e08 1920x1080 4.6 push 0.5,0.5 0.8
gen:e10 g_e10 1920x1080 2.4 push 0.5,0.5 1
gen:e07 g_e07 1920x1080 5.6 up 0.5,0.5 0.8
gen:e02 g_e02 1920x1080 5.6 push 0.5,0.55 1
gen:e03 g_e03 1920x1080 4.6 right 0.5,0.55 1
gen:e09 g_e09 1920x1080 8.0 push 0.5,0.45 1.6
LIST
echo LIVING_DONE
