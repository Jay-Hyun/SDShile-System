# 특송 영상 — 옷자락에서 전해지는 사랑

HyperFrames(HTML → MP4) 프로젝트. 1920×1080, 30fps, 약 5분 18초.

| 구간 | 시간 | 내용 |
|---|---|---|
| 프렐류드 | 0:00–0:27.5 | 막 5:27-28 (병든 여인) → 막 5:33-34 (옷자락을 향한 손) → 제목. 잔잔한 배경음 |
| MR | 0:27.5–5:18.3 | 순수 크로마 그린 #00FF00 + 하단 가사 한 줄씩(고운바탕, 「사랑」「옷자락」 금빛). MR 원곡 그대로 |

## 준비물 (레포에 없음)

MR 음원은 저작권 때문에 레포에 넣지 않았다. 렌더 전에 `assets/audio/mr.mp3` 로 복사할 것
(소리엘 「옷자락에서 전해지는 사랑 (MR)」, 피치 1.00 · 템포 100, 290.78 s).

## 명령

```bash
npx hyperframes@0.8.192 check              # 검사
npx hyperframes@0.8.192 preview            # 브라우저 미리보기
npx hyperframes@0.8.192 render -o renders/special-song_full.mp4
```

## 가사 수정

`lyrics.json` 의 `text` / `start` / `end` (MR 기준 초)를 고친 뒤 `python3 tools/build_lyrics.py`.
타이밍 출처: 벅스 소리엘 원곡 싱크 가사, MR 비트(66 BPM)와 대조. 각 줄은 실제 노래보다 0.35초 먼저 뜸.
새 글자를 쓰면 폰트 서브셋을 다시 만들 것 (가사·제목 = 고운바탕 Bold, 구절 = Noto Serif KR):

```bash
pip install fonttools brotli
curl -LO "https://raw.githubusercontent.com/google/fonts/main/ofl/gowunbatang/GowunBatang-Bold.ttf"
pyftsubset GowunBatang-Bold.ttf --text-file=chars.txt --flavor=woff2 --layout-features='*' \
  --output-file=assets/fonts/GowunBatang-Bold-subset.woff2
```

## 크로마키

MR 구간 배경은 RGB (0,255,0). OBS/vMix 등에서 크로마키(또는 컬러키) 필터를 걸면 가사만 남는다.
프렐류드 이미지에는 초록이 없어서 영상 전체에 키를 걸어도 프렐류드는 그대로 보인다.
가사는 블러 없는 진한 외곽선이라 키 가장자리가 깨끗하다.

가사 구간에는 하단에 아주 옅은 검은 틴트(가독성용)가 초록 안에 칠해져 있다. 가사 글자 중간 높이부터 화면 맨 아래까지,
**OBS 크로마키 기본값(유사도 400, 부드러움 80, 키 컬러 스필 감소 100)에 맞춰** 키를 걸면 맨 아래가 약 25%만 어두워지도록
계산했다. 초록 원본을 그대로 보면 하단이 진한 초록 띠로 보이지만, 키를 걸면 거의 다 빠지고 살짝만 남는다.
크로마키는 초록 정도로만 투명도를 정해서 설정을 바꾸면 결과가 크게 달라진다 (화면 맨 아래 기준):

| OBS 유사도 | 하단 틴트 |
|---|---|
| 420 | 약 6% (거의 안 보임) |
| **400 (기본값)** | **약 25% (의도한 값)** |
| 380 | 약 50% |
| 360 | 약 85% (진함) |

틴트에 아주 옅은 청록 기가 보이면 "키 컬러 스필 감소"를 올리면 된다. 틴트 시작 높이(`TINT_START`)와 세기(`PEAK`)는
`tools/build_tint.py`에서 고치고 실행한 뒤 다시 렌더한다. vMix 등 다른 키어는 계산 방식이 달라서 따로 확인이 필요하다.
