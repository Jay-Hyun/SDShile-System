# Reference notes — 4 Korean kinetic-typography videos

Measured from the files in Drive `영상레퍼런스` (watch frames, 8–15 fps bursts, ffmpeg scene/onset analysis).
Tempi: How It's Done ≈160 (feels 80) · Love Lee ≈100 · **Actor ≈105 (closest to our 104)** · GODS ≈146 (feels 73).

## Per reference (grammar only)

**How It's Done (HID)** — ultra-condensed caps (Druk/Anton class) at 35–45% cap height, Hangul in heavy gothic
(Black Han Sans class) at ~55% with a lavender→pink vertical gradient fill. Constant subject sandwich
(ground → giant word → cutout → small caption), layer order swaps mid-line. Pink pen-script always *written on*.
Hits on 2-beat / 1-beat gaps; flashes 83–190 ms. Palette navy `#061527`, hot pink `#f6014b`, lavender gradient
`#879de7 → #beade8 → #ede9f9`. Moments: zoom-out of a letter's counters (scale ~20→1 in 3 frames), backlit
letter-windows with god-rays, Hangul outline↔per-stroke fill, 2-frame palette inversion, polaroid page-curl.

**Love Lee** — mood-led, weak beat lock, long 2–6-beat holds with camera drift. Inflated balloon title,
social-post card UI, circle iris with syllables typed inside then iris opens (~400 ms), syllable spread → tracking
collapse (2 em → 0.05 em over ~1 s), filmstrip recap, "breakdown" ending with guide/keyframe UI over earlier shots.
Palette periwinkle `#6666d9`, lilac `#bbbced`, mint `#96e6b7`, pink `#d470ae`, cream `#eed2a7`.

**Actor** — cream paper + grain + vignette; cobalt `#4554f1`, cream `#e8e4db`, orange `#eca039`, ink `#232024`.
Hangul in neutral gothic medium, white on blue, ~7–8% cap height, left-aligned 2–3-line stacks.
**Jamo IME typing** (ㅇ→여→연, ~125 ms/step) with a scalloped-badge cursor; slot-block reveal; hairline→black
weight morph then scale to fill; word pop ±8 px baseline jitter then reflow (400 ms quart-out); 3D crown orbiting
through type with shadow; zoom out of a glyph-shaped clip; 4-colour strobe + speed lines as chorus pickup.
Hangul words land on 8ths (~285 ms), background colour changes on beats.

**GODS** — most grid-locked: letters on 16ths, words on beats, scenes on 8/16 sixteenths. Electric blue `#0900e0`,
black, clay greys. Typing at 1 sixteenth/letter with block caret; bars `scaleX` from an edge (expo-out, ~1 beat);
rectangle morph tall→square→wide (~900 ms); 3×3 repeat grid in one 16th; dither/checker letter fills; type in 3D
depth between screens and silhouettes; clay 3D renders.

## Transferable recipe (104 BPM: beat 577 ms, 8th 288, 16th 144, 32nd 72, bar 2308)

Compute every time from the beat map (`data/beats.json`), never by accumulating rounded frames.
Eases: expo-out `cubic-bezier(.16,1,.3,1)` · quart-out `(.25,1,.5,1)` · back-out `(.34,1.56,.64,1)`.

1. **Slam + creep** — scale 1.12→1, opacity 0→1, 120 ms expo-out; hold creeps 1→1.04 linear to the next hit; exit hard cut. Sung: 1 word/beat. Rap: 1 word/8th.
2. **Subject sandwich** — ground → giant word (40–70% cap) → couple cutout → caption; swap front/behind on a downbeat.
3. **Hangul IME composition** — jamo states one per 32nd, syllable per 16th, pill/badge cursor one step ahead.
4. **Outline ↔ fill** — giant outline (1.5 px, 30%) holds the line small at centre; downbeat fills per stroke, 1-frame stagger.
5. **Drop with stretch** — translateY −120%→0, scaleY 1.8→1, 180 ms quart-out; Hangul syllable stagger 72 ms.
6. **Zoom out of a letterform** — scale 15→1, 140 ms expo-out, origin at a counter (first ㅇ of a key word hides the next scene).
7. **2-frame inversion / silhouette flash** — 67 ms at phrase starts, max 1 per 2 bars.
8. **Typing on 16ths** — block caret, newest glyph in accent for one step.
9. **Script write-on** — dim hero to 50% in 2 frames, then draw over 1–2 beats `inOutSine` (names, date).
10. **Weight morph** hairline→black over an 8th, then scale to fill on the next 8th (Pretendard has 100–900 statics).
11. **Slot-block reveal** — per-glyph rectangles one shade off the ground, glyphs replace them, 120 ms stagger, ghost copy at 30% offset 4 px.
12. **Repeat/tile multiply** — card → 0.33 and clone 3×3 inside one 16th (photo grids).
13. **Circle iris + tracking collapse** — `clip-path: circle(0→150%)` 1 beat inOutCubic; letter-spacing 2em→0.05em over 1 bar.
14. **Floor reflection** — scaleY(−1) copy, gradient mask, 3% below baseline.
15. **Colour-cycle strobe** — 4 colours × 2 frames as a chorus pickup.
16. **Blender** — inflated balloon letters, extruded fly-through title, hero object orbiting type with shadow catcher (rings instead of the crown), emissive backlit letters, clay set.
17. **Finishing** — grain/vignette for the paper look, 2–3-frame rgb shift on glitch hits, alpha overlays.

## Hangul gotchas

- Syllable split gives 3–4× fewer stagger units than Latin letters: go below (jamo composition, per-stroke fill) or above (spaced syllables). NFC syllables are single code points; jamo via `0xAC00 + (cho*21 + jung)*28 + jong`.
- No reference condenses Hangul; punch comes from heavy normal-width gothic at huge size, with condensed Latin beside it. Never `scaleX` Hangul below 0.85.
- `-webkit-text-stroke` can show internal contour overlaps on some Korean fonts: test, or use SVG outlines.
- `word-break: keep-all`; break per 어절; left-aligned stacks read best.
- Subset Korean fonts to the lyric glyphs (`pyftsubset`) to keep renders fast.
