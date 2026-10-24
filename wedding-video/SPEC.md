# SPEC — 반대가 끌리는 이유 (wedding pre-ceremony lyric film)

GOAL:    guests laugh and lean in: two very different people, shown as two opposite type systems, keep
         getting pulled together until the film ends on their names, the date and two linked rings.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps, H.264 CRF 16 + AAC 320k, 2 s black head and tail for the venue.
TIME:    ~180 s x 30 = ~5400 frames. 104.0 BPM, beat 0.5769 s = 17.31 frames, bar 2.308 s = 69.2 frames.
         Every time is computed from data/beats.json (first beat 0.80 s in the source), never accumulated.

LOOK:    medium = printed matter + studio objects.
         ground: cream paper #F3EEE3 with paper.png fibre at 7% multiply and grain.png at 6% overlay;
                 dark chapters use ink #14121A / GODS black #0E0E12; chorus uses a lavender field
                 #C9B6FF -> #F3EEE3 radial (HID / Love Lee use it; solid + local glow, never a full-frame linear).
         ink A (N pole, groom): cobalt #2F3BFF, Black Han Sans, hero words 300-560 px (28-52% frame height),
                 tracking -0.02em; Latin in Anton.
         ink B (S pole, bride): pink #FF5C8A, Jua, same sizes; handwriting in Gaegu Bold / NanumPenScript,
                 Latin script in Mrs Saint Delafield.
         overprint AB: where A and B overlap, multiply -> violet #6A2BD9 (the only place violet appears).
         hit colour: #FF2D55 only for 2-frame flashes.
         meta type: Pretendard Bold 26-30 px, tracking 0.24em caps, used only for the N / S pole marks
                 and the date line (no corner HUD, no frame borders).
         photographs: the couple's own photos, never filtered with CSS; cutouts (BiRefNet) for the
                 subject sandwich; date photos (low-res) only as cards <= 520 px tall.
         3D: Blender Cycles inserts on transparent film with shadow catcher: chrome cobalt "반대", balloon
                 pink "끌림", balloon chorus syllables, clay keycaps, gold rings.

OBJECTS: the couple (photos and footage, real); a bar magnet's two poles = two type systems; magnetic
         field lines (SVG, 2.5 px, the pole colours); keycaps (sculpted profile, Hangul legends); two
         gold wedding rings, one with a stone; the photo-booth strip "WE'RE GETTING MARRIED".

MOTION:  A enters on expo-out cubic-bezier(.16,1,.3,1) in 120-180 ms, lands dead still (creep 1->1.04 max).
         B enters on a damped spring (zeta 0.45, 2 cycles) in 450-520 ms with +-8 deg roll.
         attraction = ease-in (power 3) approach, contact on a beat, spring settle zeta 0.4.
         repulsion = spring jolt zeta 0.35 apart.
         stagger: Hangul syllables 72 ms (a 32nd), words on 8ths in rap, on beats when sung.
         exits 40-50% shorter than entrances; hits are 0 ms sets 40-190 ms before the vocal onset.
         camera moves (scale/x on wrappers) power2.inOut; footage push 1.0 -> 1.06 max.

SHOTS:   see the shot list in compositions/ (one scene per chapter) and docs/shots.md once timed.
BANNED:  dark navy void with small centred type; glow/bloom/lens flares/particles as decoration;
         mesh gradients, glass cards; serif display on cream; italic accent words; numbered labels;
         pill chips as UI; everything centred; everything fading in at once; fade+slide-up on every
         element; text drifting while read; corner brackets/HUD; logo in a corner; CSS filters on photos;
         same treatment > 6 s; scaleX on Hangul below 0.85.
QA:      first frame not empty; every lyric word on screen at its sung onset +-2 frames; every word held
         >= 1 beat when sung, >= 1 8th when rapped; 360 px phone sheet readable; B1 impact lands on its
         downbeat; ending card holds >= 2.5 s.
