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

가사 구간에는 하단에 옅은 검정 페이드가 있다. 화면 맨 아래가 가장 진하고(35%) 위로 갈수록 옅어져서
가사 글자 중간 높이에서 사라진다.

**주의: 크로마키를 걸면 초록 영상 안의 페이드는 초록과 함께 빠져서 안 보인다.** 송출 화면에서 페이드가 보이게 하려면
`extras/tint_overlay.png`(같은 페이드를 투명 배경에 그린 1920×1080 PNG)를 쓴다:

1. OBS 장면에서 순서를 위에서부터 `가사 영상(크로마키 적용)` → `tint_overlay.png`(이미지 소스) → `카메라` 로 둔다.
2. 오버레이는 찬양(가사 구간) 동안만 켠다. 영상에서는 MR 시작 26.8초 무렵 들어와 276.1초 무렵 빠진다.

진하기나 시작 높이를 바꾸려면 `tools/build_tint.py`의 `PEAK`, `TINT_TOP`을 고치고 실행한다. 영상 안의 페이드와 PNG가
함께 다시 만들어지며, 그 뒤 다시 렌더한다.
