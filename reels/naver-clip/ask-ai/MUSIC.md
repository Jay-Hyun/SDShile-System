# 음악 · 사운드 — 편 A 「AI에게 물었다」 v7

## 출처
- 곡: **Alex_Besss "News Background"** — Pixabay **ID 602905** (`_shared/music/C-alexbesss-news-background-602905.mp3`, 51.72 s)
- 프로젝트 사본: `assets/music/source.mp3` (같은 파일)
- **라이선스 확인은 사용자 몫이다.** Pixabay Content License 의 광고(유료 집행) 사용 범위를 집행 전에 확인할 것.
- 합성 음악 없음. v6 곡(grand_project 505611)은 더 쓰지 않는다.

## 박자
- `beats/source.json` = `_shared/beats/C-alex.json`(signature/tools/beats.py) 사본: 130.002 BPM, 1박 0.4615 s, 다운비트 = beats[3::4]
  (1.397, 3.239, 5.085, 6.931 …). 0–1.86 s 는 거의 무음 인트로, 1.858 s 첫 타격.

## 편집 (`tools/make_audio.py`, 시각은 `lib/cue.js`)
| 판 | 영상 | 원곡 | 비고 |
|---|---|---|---|
| 30s | 0.000–30.000 | 3.239–33.239 | 이음새 0. 영상 0 = 원곡 다운비트 → 첫 프레임부터 음악. 원곡 41.7 s 이후 큰 구간 미사용. 끝 0.3 s 페이드 |
| 15s | 0.000–15.000 | 3.239–18.239 | 같은 시작, 끝 0.3 s 페이드 |
무음·페이드(엔딩 제외)·로우패스·덕킹·피치 변화 없음. 리미터는 걸려 있으나(샘플 피크 −1.5 dBFS) 이 발췌에서는 게인 감소 0 dB.

## 효과음 (2개)
| 시각 | 효과음 | 레벨 |
|---|---|---|
| 1.200 | 폰 안 셋째 덩어리 입력 탭 | 주변 음악 RMS −20 dB |
| 1.793 | 질문 전송 탭 (마디 2 직전) | 주변 음악 RMS −20 dB |
탭 = 170 Hz 몸통(14 ms) + 2.5 kHz 아래 짧은 클릭, 그림보다 1프레임 늦게. 30s·15s 같은 자리.

## 마스터 (스템 합, ffmpeg ebur128)
- 30s: **−15.0 LUFS, TP −2.5 dBTP** · 15s: **−15.0 LUFS, TP −1.8 dBTP**
- `tools/audio_check.py`: −40 dBFS 미만 구간 0 ms(30s·15s; 최저 10 ms RMS −26.2 / −25.5 dBFS), 이음새 없음, 10 kHz+ 비율 원곡 대비 0.00 dB.
- 렌더 후: `npm run remux`(320 kbps AAC 로 교체) 뒤 MP4 로 다시 측정할 것.
