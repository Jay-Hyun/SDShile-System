# 특송 영상 — 옷자락에서 전해지는 사랑

HyperFrames(HTML → MP4) 프로젝트. 1920×1080, 30fps, 약 5분 0초.

| 구간 | 시간 | 내용 |
|---|---|---|
| 프렐류드 | 0:00–0:27.5 | 막 5:27-28 (병든 여인) → 막 5:33-34 (옷자락을 향한 손) → 제목. 잔잔한 배경음 |
| MR | 0:27.5–5:00 | 순수 크로마 그린 #00FF00 + 하단 가사 한 줄씩(고운바탕 110 px, 「사랑」「옷자락」 금빛). MR은 끝 잡음 직전(271.8초)에서 페이드아웃 |

## 준비물 (레포에 없음)

MR 음원은 저작권 때문에 레포에 넣지 않았다. 렌더 전에 `assets/audio/mr.mp3` 로 복사할 것
(소리엘 「옷자락에서 전해지는 사랑 (MR)」, 피치 0.00 · **템포 105**, 276.94 s).
이전 템포 100 MR(290.78 s)을 쓰려면 `lyrics.json`과 `index.html`의 MR 관련 시각을 모두 ×1.05 해야 한다.

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

가사 구간에는 하단에 검은 틴트가 초록 안에 칠해져 있다. 맨 아래가 가장 진하고 위로 갈수록 옅어져 가사 글자 중간에서
사라진다. 크로마키는 옅은 어둠을 초록과 함께 지워 버리므로 일부러 진하게 칠했고, 키를 건 뒤 얼마나 남는지는 키어마다 다르다.

### ATEM 등 현장 키어에 맞추기

1. `renders/tint_calibration.mp4`(10초)를 본 영상과 같은 키 설정으로 띄운다. 하단이 5칸으로 나뉘어 1(연함)~5(진함) 틴트가 보인다.
2. 가장 적당한 번호를 고른다.
3. `tools/build_tint.py`의 `LEVEL`을 그 번호로 바꾸고 `python3 tools/build_tint.py` 실행 후 다시 렌더한다.

초록 원본을 그대로 보면 하단이 진한 초록 띠로 보이는데, 키를 걸면 대부분 빠지고 일부만 남는 게 정상이다.
테스트 클립 다시 만들기: `cd extras/tint-calibration && npx hyperframes@0.8.192 render -o ../../renders/tint_calibration.mp4`.

키어 대신 레이어로 깔고 싶으면 `extras/tint_overlay.png`(같은 모양, 최대 55%, 투명 배경)를 카메라와 가사 사이에 넣는다.

## MR 끝 잡음

MR 원본 파일에는 끝부분에 '지직' 하는 디지털 클릭 잡음이 들어 있다. 템포 105% 파일 기준 약 271.86초부터 끝(276.9초)까지이며,
음악은 그 전에 이미 -43 dB로 끝난다. 그래서 MR을 271.8초까지만 쓰고 마지막 2초를 페이드아웃한다(`index.html`의 `#mr`).
