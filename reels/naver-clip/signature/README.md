# 네이버 클립 콘셉트 1 「마지막 서명」 — 30초 초안 (HyperFrames)

1080×1920 · 30fps · 30.0초. 기준: `docs/ads/naver-clip/01-last-signature.md` §4 컷씬 시트(프레임 단위).
렌더: `renders/last-signature-30s.mp4` (**초안: 내레이션 없음, 스톡 대신 벡터 일러스트**)

| 씬 파일 | 컷 | 프레임 |
|---|---|---|
| `hook` | C1 0.1초, 그리고 한 칸 | f0–f89 |
| `fill` | C2 다 채워진다 | f90–f179 |
| `blank` | C3 딱 한 칸 | f180–f299 |
| `dust` | C4 귀해지는 칸 | f300–f419 |
| `desk` | C5 법을 아는 사람 (스톡 대체 일러스트) | f420–f539 |
| `sign` | C6 마지막 서명 → 첫 계단 → USP → 브랜드 | f540–f719 |
| `cross` | C7 넘어오세요 | f720–f824 |
| `end` | C8 엔드카드 | f825–f899 |
| `legal` | 상시 레이어: `연출` f465–f719, 고지 L1·L2 f630–f899 | f465–f899 |

씬 파일과 `index.html`은 `tools/build.py`(+ `tools/common.css`)가 생성한다. 손으로 고치지 말고 빌더를 고친 뒤 다시 생성한다.

```bash
python3 tools/build.py                       # compositions/*.html + index.html
python3 tools/make_audio.py                  # assets/audio/bed.mp3 (+ stems/), -16 LUFS, TP <= -1 dBTP
PRETENDARD_GOV=/path/PretendardGOVVariable.woff2 python3 tools/subset_font.py   # 문구 바꾸면 다시
npm run check && npm run snapshot && npm run render
```

## 사운드
- `assets/audio/bed.mp3`: numpy로 합성한 음악 베드 + SFX(스펙 BGM/SFX 열 큐 그대로: 120BPM 펄스, 2.8s 스톱, 9.5s 리버스 스윕 → 10.0s 무음, 11.6s 피아노 단음, 14s 3음 모티프, 18.0s 드롭, 19.47s 펜 "톡", 26.5s 감쇠, 27.5s 마지막 화음). 측정값: -16.3 LUFS, true peak -3.1 dBTP. 들어서 확인한 것은 아니다(측정만).
- `assets/audio/stems/{music,sfx}.mp3`: VO 믹스용 분리 스템.

## 남은 일 — 내레이션(VO)
VO는 녹음 전이라 넣지 않았다(가짜 VO 없음). 30대 중저음, 담담한 톤. 녹음 후 `<audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-volume="1">`를 `index.html`에 추가하고(빌더의 index 템플릿에도), 음악은 VO 구간에서 약 -8dB 덕킹 후 전체 -16 LUFS로 다시 맞춘다. 대사와 샷(스펙 §7, 모두 7자/초 이하):

| 샷 | 시간 | 대사 |
|---|---|---|
| C1 S1 | 0.0–1.5 | AI가 다 써줍니다. |
| C2 S1 / S2 | 3.0–4.2 / 4.2–6.0 | 검토의견서도, / 소장 초안도, 보고서도. |
| C3 S1 / S2 | 6.0–7.0 / 7.0–8.5 | 딱 한 칸만 / 빼고. |
| C4 S1 / S2 | 10.0–11.6 / 11.6–14.0 | AI가 일을 대신할수록, / 책임질 자리는 더 귀해집니다. |
| C5 S1 / S2 | 14.0–15.5 / 15.5–18.0 | 그 자리엔 언제나 / 법을 아는 사람이 있었습니다. |
| C6 S1 / S2 / S3 | 18.0–19.5 / 19.5–21.0 / 21.0–24.0 | 그 칸을 향한 / 첫 계단. / 100% 온라인 법학사, 교육부장관 명의로. |
| C7 S1 / S2 | 24.0–26.0 / 26.0–27.5 | 서명하는 쪽으로 넘어오세요. / 상담만 받아도 돼요. |
| C8 | 27.5–30.0 | 책임지는 자리로, 지금 있는 자리에서. |

## 컴플라이언스 메모
가상 "문서 도우미" UI(문서 글리프 아이콘, 상단 입력 스트립, 스파클·말풍선·사이드바·하단 입력창 없음). 문서 3장 모두 `[가상 문서 · 예시]`, 당사자 갑·을만 사용, 사건번호·법원명·휘장·직인 없음. 정부 로고(moe-emblem) 미사용. 브랜드 마크는 `_shared/img/mark-gold.svg`. "무료"는 버튼에만. 15초 버전은 아직 없다.
