# REVIEW — 특송 「옷자락에서 전해지는 사랑」

## Revision 6 (requested by the person)
- The person was judging the raw green file. They wanted a fade that is faint at the bottom edge, eases up and is gone by the middle of the glyphs, not a band that starts at the glyph middle.
- The fade is now drawn exactly that way in the green: black from 35% at y 1080 down to 0% at y 917, on a smoothstep curve.
- Trade-off, stated to the person: a chroma key removes this in-green fade completely (the keyer model keeps 0%). `extras/tint_overlay.png` carries the same fade on a transparent background, for use between the camera and the keyed lyrics. The preview `renders/tint_preview.jpg` shows the raw file next to camera, overlay and keyed lyrics.
- The keyer-inversion design from revisions 4–5 is retired, and `tools/build_tint.py` now draws the shape directly and writes the PNG.

## Revision 5 (requested by the person)
- The tint is lower and lighter, and it now begins at the middle of the lyric glyphs (measured glyph rows y 875–960, middle 917; `TINT_START` is 915). Its keyed darkness eases from 0 there to 25% at the bottom (`PEAK`). The paint starts at y 880, so above that the raw green is untouched.
- Calibrated through an H.264 round trip of a snapshot frame. The keyed alpha after encoding is 0.04 at y 960, 0.15 at y 1000 and 0.25 at the bottom. Sensitivity at the bottom: Similarity 420 gives 0.06, 380 gives 0.52, 360 gives 0.85.
- A raw-versus-keyed preview image (`renders/tint_preview.jpg`) was sent, because the raw green file looks much darker than the keyed result.

## Revision 4 (requested by the person)
- Tint made light ("살짝") and kept inside the green, as the person chose over a PNG overlay or an alpha video. `tools/build_tint.py` designs it backwards from the keyed result: it sets the darkness wanted after keying (OBS default Similarity 400: 0% above y 800, 35% by y 960, 40% at the bottom), then inverts the keyer to find the paint at each height (26 stops, 20 px apart).
- Simulated over a stand-in picture: at 400 the keyed alpha is 0.06 at y 840, 0.29 at y 920, 0.37 at y 1000 and 0.40 at the bottom; the colour is a dark neutral with a faint green cast (+10). At 420 the tint drops to 0.16 and at 380 it rises to 0.70. The person was told about this sensitivity before choosing.
- Rendered file: 318.3 s, green (0,254,0) at the top, MR head at 27.5 s, -14.9 LUFS, true peak -1.5 dBTP, no clipping. After H.264 the tint pixels read (15,64,15) at y 860, (15,54,14) at y 960 and (16,52,15) at y 1070. Run through the keyer model, these give alpha 0.15, 0.38 and 0.47: the bottom came out a little darker than the 0.40 target. There is no tint at 40 s or 304 s.

## Revision 3 (requested by the person)
- Gradient lowered on request: it now starts at y 580 instead of 420. At similarity 400 it darkens from y≈840, just above the lyric, and is solid from y≈920.
- The title card is now two lines, 「옷자락에서 / 전해지는 사랑」, at 120 px.
- A bottom dark gradient now runs behind the lyrics (MR 26.8–276.1 s, with 1.5 s fades), drawn into the green as the person chose. The fully transparent alpha version was offered and declined.
- Measured, not seen on a real keyer: OBS's chroma-key math (v2 shader: similarity, smoothness 80, spill 100) was simulated on a rendered frame over a stand-in picture. At similarity 400 (the default) the bottom darkens from y≈760 and is solid below y≈880, with a faint green line at its top edge. At 450 it reads as a translucent tint. At 350 the band becomes larger and solid. The end colour (19,5,19) leans magenta so the solid part keys to a neutral dark instead of dark green (the first try, plain black, left a dark-green band). A little green at the band's edge cannot be avoided with a chroma key, and only an alpha video removes it fully.

## Revision 2 (requested by the person)
- Lyric spelling restored to the person's text: 「오래전 부터」, 「그 분이라면」, 「하신사랑」.
- Lyric style redone. Gowun Batang Bold at 90 px in ivory, a 2 px hard outline plus an angular 3/4 px shadow (still no blur, so it keys cleanly), and the song's own words 「사랑」/「옷자락」 in gold, one per line (6 lines). Characters rise one after another (0.035 s apart), and each line lifts out as it leaves. The old thick karaoke-style outline is gone.
- The title card uses the same face, with 「사랑」 in gold, so the title and lyrics read as one identity.
- Prelude cut from 42.0 s to 27.5 s: scene 1 is 11 s, scene 2 is 12.6 s, the title is 6.1 s, with 1.0 s dissolves. The MR now starts at 27.5 s and the film is 318.28 s.

## Creative calls
- Followed the singer's voice-memo storyboard directly: 5:27-28 over the hooded, ill woman → 5:33-34 over the hand reaching for the hem → the title rises → MR on chroma green.
- Images were made by GPT (Codex `image_gen`) using the clara-muz-team flow. Claude wrote the brief and checked the results: 1664×936, zero green-hue pixels, no text, Jesus' face not shown.
- Lyric timings come from Bugs' synced lyrics for the original Soriel recording (track 80045568). All 32 lines fall within ±0.4 s of the MR beat grid (66 BPM, one line every 8 beats). Each line appears 0.35 s before it is sung.
- The prelude music bed was made with MusicGen-small on this machine and shifted down a semitone from B to B♭ to match the MR. It is trimmed to 27 s with a 2 s fade-out.

## Measured vs looked at
- `check`: 0 errors.
- Looked at frames: t=4, 8, 14, 19, 24.5, 27.3, 56.4 (a line arriving), 128.5, 152, 287.5, plus a full-resolution crop of a lyric.
- MR is -11.4 LUFS with a true peak of +1.2 dBTP, so the source itself clips. It is set to 0.78 (-2.2 dB) in the mix.
- Rendered file: 1920×1080, 30 fps, 318.3 s. Green samples read (0,254,0). The MR head cross-correlates at exactly 27.5 s and the bed is silent from 27.0 s. The mix is -14.9 LUFS with a true peak of -1.5 dBTP and no clipping. Splits: `01_prelude.mp4` (27.5 s) and `02_mr_green_lyrics.mp4` (starts on green).
- Not checked: nobody has listened to the music bed.

## Reading time (shorter prelude)
- Verse 28 is on screen 4.6 s for 9 words. Verse 34 is on screen 4.6 s for 13 words, which is the tightest; the floor of 0.5 s + 0.3 s per word gives 4.4 s.

## Weakest shot
- Scene 2: the image's dark area is narrower, so the verse column (880 px) still touches the edge of the sandal. It stays readable.

## Warnings kept on purpose
- `timeline_track_too_dense`: every lyric line sits in one captions host, as the caption rules require.
- `contrast_aa_failure` (light text over #00FF00): the green is keyed out on air, and the dark outline provides the contrast, which the checker does not count.
- `first_frame_empty`: a fade up from black is intended for playing in a service.
