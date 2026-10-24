# GPT 이미지 프롬프트 팩 (ClaraMuz용)

클라우드 세션에서는 ClaraMuz를 쓸 수 없습니다. ClaraMuz는 로컬 `codex` CLI와 ChatGPT 로그인을 거쳐 이미지를 만드는데, 이 세션에는 둘 다 없기 때문입니다.
아래 프롬프트를 로컬에서 ClaraMuz로 생성한 뒤, 지정한 경로에 1920×1080 PNG로 넣어 주세요. 다음 세션에서 컷에 바로 연결합니다.
실제 두 사람의 얼굴은 만들지 않습니다. 실루엣, 사물, 공간만 생성해서 진짜 사진과 섞어도 어색하지 않게 합니다.

공통 톤: 35mm 필름, 부드러운 창가 자연광, 낮은 채도, 크림/웜그레이 팔레트, 잔잔한 그레인. 텍스트와 로고는 넣지 않습니다.

| 파일 | 쓰일 자리 | 프롬프트 |
|---|---|---|
| `assets/media/gen/g01_magnets.png` | 인트로 "두 사람" 직전의 2초 오프닝 | Macro still life: two old horseshoe magnets, one matte black and one ivory ceramic, almost touching on cream linen, iron filings tracing field lines between them, soft window light from the left, shallow depth of field, 35mm film grain, muted warm palette, no text |
| `assets/media/gen/g02_opposites_sun_moon.png` | 브리지 "모든 게" 컷 (현재는 두 사람 사진 쌍) | Diptych photograph, left half: warm sunrise sun disc over calm sea; right half: cool full moon over the same sea at night; seamless centre split, identical horizon line, film photograph, muted tones, no text |
| `assets/media/gen/g03_city_bokeh.png` | 마지막 후렴 기억 터널의 배경 | Out-of-focus night city lights by a river in Seoul, large soft bokeh circles in amber and rose, dark warm background, cinematic 2.39:1 framing centred, film grain, no text |
| `assets/media/gen/g04_two_chairs.png` | 아웃트로 카드 뒤 배경 (선택) | Two different chairs side by side in an empty sunlit studio, one black leather armchair and one white wooden chair, long soft shadows, cream wall, minimal, film photograph, no people, no text |

생성 후 알려 주시면 `scripts/living_photo.py`로 깊이를 넣은 2.5D 카메라 무브까지 걸어서 해당 컷에 넣겠습니다.
