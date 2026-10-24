# REVIEW — 특송 「옷자락에서 전해지는 사랑」

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
- Not checked: nobody has listened to the music bed.

## Reading time (shorter prelude)
- Verse 28 is on screen 4.6 s for 9 words. Verse 34 is on screen 4.6 s for 13 words, which is the tightest; the floor of 0.5 s + 0.3 s per word gives 4.4 s.

## Weakest shot
- Scene 2: the image's dark area is narrower, so the verse column (880 px) still touches the edge of the sandal. It stays readable.

## Warnings kept on purpose
- `timeline_track_too_dense`: every lyric line sits in one captions host, as the caption rules require.
- `contrast_aa_failure` (light text over #00FF00): the green is keyed out on air, and the dark outline provides the contrast, which the checker does not count.
- `first_frame_empty`: a fade up from black is intended for playing in a service.
