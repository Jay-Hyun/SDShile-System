# 네이버 클립 콘셉트 5 「AI에게 물었다」 — anime.js v4 재제작 (HyperFrames)

1080×1920, 30fps. 30초(루트)와 15초(`v15/`). 사양: `docs/ads/naver-clip/05-ask-ai.md`. 1차 GSAP 드래프트(평평·느림·합성 음악)는 반려되어 교체했다. 이전 판은 git 히스토리(f65d08a, bd435b5)에 있다.
**엔진은 anime.js v4.5.0 하나뿐이다**(`lib/anime.min.js`, 로컬 번들). GSAP 0건.

## 파일
| 파일 | 내용 |
|---|---|
| `index.html` | 루트(30초). 씬 호스트 3개 + 오디오 2트랙. `lib/anime.min.js`, `lib/beat.js` 로드 |
| `lib/beat.js` | 비트 그리드(P = 60/125.03 s), 프레임 스냅 ms, 타임라인 생성(`autoplay:false` → `window.__hfAnime`), 글자 분해·타이핑, 시드 흔들림(`anime.createSeededRandom`), 1프레임 플래시 |
| `compositions/chat.html` | C1–C6 가상 "AI 어시스턴트" 챗 UI. 키보드까지 채운 전체 화면, 측정 기반 대화 스택 |
| `compositions/brand.html` | C7–C10 원형 전환 → 로고·USP → 상담사 답(0→60 오도미터) → CTA → 슬로건 |
| `compositions/legal.html` | 연출 배지 교체, '국내 유일' 각주, 보장 금지 고지 |
| `tools/analyze_beats.py` | numpy+ffmpeg 비트 분석 → `beats/source.json` |
| `tools/make_audio.py` | 원곡 편집(발췌·테이프 스톱·스플라이스) + SFX + 마스터 → `assets/audio/*.wav`, `beats/cuts-*.json` |
| `tools/build_15s.py` | `v15/` 생성 (`const CUT = 30` → 15, legal·루트 타이밍). v15 파일은 직접 고치지 않는다 |
| `tools/verify_cuts.py` | 렌더 MP4의 컷(프레임 차 피크)을 비트 그리드와 대조, 최장 정지 구간 |
| `tools/subset_font.py` | Pretendard GOV 서브셋(키보드 자모 포함) |
| `MUSIC.md` | 곡 출처(Pixabay 505611), 편집 지점, 처리, 라우드니스 |

```bash
npm run beats && npm run audio && npm run build15
npm run check            # 30s; 15s는 cd v15 && npx --yes hyperframes@0.8.200 check
npm run render && npm run render15
npm run verify
```

## 연출 (템포·긴장감)
- 모든 컷·주요 모션은 125.03 BPM 그리드(B(k) = k·P)에 놓는다. 시간은 30fps 프레임에 스냅.
- 컷마다 1프레임 화이트 플래시, 강세마다 시드 고정 카메라 흔들림(4–7프레임 감쇠), 미세 카메라 푸시·펀치.
- 말풍선·버튼·🙂 은 spring(`anime.spring({bounce})`), AI 글자는 16분음표(30s)·32분음표(15s 및 사용자 입력) 스태거 팝.
- 형광펜은 비트에 `scaleX` 스윕, 제목·'책임'·'60' 밑줄은 `anime.svg.createDrawable` 라인 드로잉, 60은 오도미터 롤.
- 로딩 개그: 음악이 테이프 스톱으로 꺼지고(0.5 s) 무음 속 초침 틱 → "고민 중… / 아직 고민 중… / 음…" + 느린 줌. 🙂 말풍선은 **음악이 다운비트로 돌아오는 순간** 플래시·강한 흔들림과 함께 뜬다. 브랜드는 원곡 B섹션 크래시, 슬로건 마무리는 마지막 크래시에 맞췄다.
- 레이아웃: 대화창 y 390–1360을 측정한 높이로 아래부터 채우고, 입력창은 y 1376–1480(하단 420 px 위), 그 아래(y 1500–1920, 플랫폼 오버레이 구역)는 장식 키보드로 채웠다. C4 입력 때 키가 글자마다 눌린다.

## 컷 ↔ 비트 (렌더 MP4 실측, `npm run verify`)
30s 9/9, 15s 6/6 컷이 비트 ±2프레임 안. 최장 정지 0.70 s. 상세 표는 작업 보고에 있다.

## 사양과 다른 점
- 컷 경계를 비트로 다시 잡음(±0.5 s 이내): 30s C2 2.879 / C3 6.718 / C4 9.598 / C5 12.477 / C6 14.637 / C7 18.476 / C8 21.355 / C9 23.754 / C10 27.113. 15s C2 2.879 / C3 4.799(고민 중 5.759) / C4 6.580 / C5 8.500 / C6 12.339.
- 배지 교체·각주·고지 시작 = 브랜드 진입 18.467(사양 18.0, +0.47 s). 15s는 8.5 그대로.
- BGM 큐: 사양은 "C5–C6 정적, C7에 새 음악"이었으나 이번 지시에 따라 **🙂 말풍선(C6 시작)에서 음악 복귀**, 브랜드는 크래시. 정적 구간은 C5(30s 2.16 s, 15s 0.82 s).
- 사양의 로파이/어쿠스틱 BGM 대신 제공 곡 하나로 끝까지 간다.
- C4 사용자 재입력은 32분음표 속도(사양 1.0 s 망설임 → 백스페이스 2회 0.24 s 간격 + 16자 0.96 s).
- 15초 C3 "고민 중…"은 0.82 s(사양 "0.8초") — check `line_unread` 경고는 사양 타이밍이라 유지. 15초 C4 말풍선(9자, 1.9 s)도 같은 경고, 유지.
- 30초 "아직 고민 중…" 0.72 s(`line_unread` 경고): 교체식 코믹 비트, 6자라 읽힘. 유지.
- 배지 26 px → 28 px, 슬로건 「」 미표기, C10 배경 스톡은 벡터 일러스트(블러) — 1차와 같음.
- 내레이션(VO)은 아직 없다. 녹음하면 `<audio>` 트랙으로 넣고 BGM을 덕킹한 뒤 −15 LUFS로 다시 맞춘다.
