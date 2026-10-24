# REVIEW — 특송 「옷자락에서 전해지는 사랑」

## Creative calls
- Followed the singer's voice-memo storyboard directly: 5:27-28 over the hooded, ill woman → 5:33-34 over the hand reaching for the hem → the title rises → MR on chroma green. The other two storylines in `story.md` were skipped because the storyboard already fixed the story.
- Images were made by GPT (Codex `image_gen`) using the clara-muz-team flow. Claude wrote the brief and checked the results: 1664×936, zero green-hue pixels, no text, Jesus' face not shown.
- Lyric timings come from Bugs' synced lyrics for the original Soriel recording (track 80045568). All 32 lines fall within ±0.4 s of the MR beat grid (66 BPM, one line every 8 beats). Each line appears 0.35 s before it is sung.
- Lyric spelling: changed 「오래전 부터」 to 「오래전부터」, 「그 분이라면」 to 「그분이라면」 and 「하신사랑」 to 「하신 사랑」.
- The MR part uses a flat #00FF00 background. Lyrics are white with a hard, unblurred outline and drop shadow, so the chroma key edge stays clean.
- The prelude music bed was made with MusicGen-small on this machine and shifted down a semitone from B to B♭ to match the MR. It fades out between 39.5 and 41.5 s; the MR starts at 42.0 s.

## Measured vs looked at
- `check`: 0 errors.
- Looked at frames: t=5, 13/14, 22, 30/32, 38.5, 41.8, 72, 293.4 (lyrics), 322.8.
- Measured: MR is -11.4 LUFS with a true peak of +1.2 dBTP, so the source itself clips. It is set to 0.78 (-2.2 dB) in the mix. The bed is -16.7 LUFS before gain and plays at 0.6.
- Rendered file (`renders/special-song_full.mp4`): 1920×1080, 30 fps, 332.8 s, H.264 + AAC stereo 48 kHz. Green samples read (0,254,0). The MR head cross-correlates at exactly 42.0 s, the bed is silent from 41.5 s, the mix is -15.2 LUFS with a true peak of -1.8 dBTP and no clipping. A zoomed lyric edge goes green → dark outline → white, with no soft fringe.
- Split files: `01_prelude.mp4` (0–42 s) and `02_mr_green_lyrics.mp4` (42 s–end, starts on green).
- Not checked: nobody has listened to the music bed. Its loudness, lack of drums (percussive ratio 0.007) and key were measured, but whether it sounds good was not.

## Weakest shot
- Scene 2 (16.5–34 s): the image's dark area is narrower, so the verse column (880 px) still touches the edge of the sandal. It stays readable. With more time, regenerate the image with the subject pushed further right.

## Warnings kept on purpose
- `timeline_track_too_dense`: every lyric line sits in one captions host, as the caption rules require.
- `contrast_aa_failure` (white over #00FF00): the green is keyed out on air, and the dark outline provides the contrast, which the checker does not count.
- `first_frame_empty`: a fade up from black is intended for playing in a service, not for a social thumbnail.
