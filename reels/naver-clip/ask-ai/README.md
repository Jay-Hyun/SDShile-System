# 네이버 클립 콘셉트 5 「AI에게 물었다」 — 30초 드래프트 (HyperFrames)

1080×1920, 30fps, 30.0초. 사양: `docs/ads/naver-clip/05-ask-ai.md` §2(30초 타임라인)·§4(컷씬)·§5(엔드카드). 모션그래픽만 사용(스톡 없음).

| 파일 | 내용 |
|---|---|
| `index.html` | 루트(30초). 씬 호스트 3개 + 오디오 2트랙, 색 변수 |
| `compositions/chat.html` | C1–C6 (0–18.5) 가상 "AI 어시스턴트" 챗 UI. 타이핑·형광펜·입력창 클로즈업·"고민 중…" 개그·상담사 연결 버튼 |
| `compositions/brand.html` | C7–C10 (18–30) 원형 마스크 전환 → 로고·USP → 상담사 답(0→60) → CTA → 슬로건(저녁 책상 벡터 일러스트, 블러) |
| `compositions/legal.html` | 연출 배지(0–18 "가상 챗봇 화면 · 연출", 18–30 "연출"), '국내 유일' 각주 y1395, 보장 금지 고지 y1440 (18–30) |
| `tools/subset_font.py` | Pretendard GOV Variable 서브셋 → `assets/fonts/PretendardGOV-subset.woff2` (문구 바꾸면 다시 실행) |
| `tools/make_audio.py` | 사운드 베드 합성(numpy+ffmpeg) → `assets/audio/bgm.wav`, `sfx.wav` (합산 −16 LUFS, TP ≤ −1.5 dBTP) |

```bash
npm run font -- /path/to/PretendardGOVVariable.woff2   # 원본 폰트는 커밋하지 않음
npm run audio
npm run check
npm run snapshot
npm run render        # → renders/ask-ai-30s.mp4
```

## 오디오
- BGM: 1.5초 신스 펄스 1회 → 3.0–12.5 로파이 90BPM → **12.5초 뚝 끊김(정적 개그)** → 18.0 어쿠스틱+피아노 120BPM → 23.5부터 빌드업 → 27.0 해결 코드, 28.2 마지막 차임, 29–30 페이드.
- SFX: 전송음 꼬리, 타이핑 점 틱, 스크롤 휙, 타이핑, 저음 "띵", 마커 "쓱"×2, 팝, 백스페이스 2회, 전송 "슝", 초침 틱, 귀뚜라미, 🙂 "뿅", 탭 "톡", 화이트 스윕, 차임, 카운트 틱, 버튼 "톡", 착지 "둥"×2.
- **내레이션은 아직 없다.** AI 말풍선용 평평한 AI-TTS(C2·C3·C5·C6)와 사람 성우(C7–C10, 따뜻한 30대 톤)를 나중에 녹음해 `<audio>` 트랙으로 넣고, 그때 BGM을 VO 아래로 내리고(덕킹) 전체를 다시 −16 LUFS로 맞춘다. 대사와 타이밍은 사양 §7-1.

## 사양과 다른 점 (드래프트 판단)
- 연출 배지 26px → 28px (모바일 가독 하한).
- C4 입력창 클로즈업 130% → 115%(+위로 이동): 130%면 입력창이 세이프 영역(x ≤ 920, y < 1500)을 벗어남.
- C8 상담사 말풍선 "둥근 손글씨풍 서체": 오프라인에 한글 손글씨 폰트가 없어 Pretendard + 웜화이트·둥근 말풍선으로 AI와 구분.
- 슬로건 「」는 문서의 인용 표기로 보고 화면에는 넣지 않음.
- C10 배경 스톡(저녁 사무실 책상)은 벡터 일러스트로 대체(블러, "연출" 배지 유지).
- 중심축: 텍스트는 우측 160px 회피를 위해 x 80–920 세이프 컬럼 중앙(x 500)에 정렬.
- check 경고 유지: "아직 고민 중…" 0.9초 노출(사양 타이밍), 🙂 말풍선 3.3초(사양 타이밍), 같은 대상에 fromTo 반복(첫 호출만 immediateRender, 스냅샷으로 확인).

## 남은 일
- 15초 버전(사양 §3), VO 녹음·믹스, 실기기에서 네이버 클립 오버레이 가림 영역 재측정.

## 15초 버전 (`v15/`)
- 사양 §3: C1 3.0 / C2 2.0 / C3 1.8 / C4 1.7 / C5 4.0 / C6 2.5. 렌더: `renders/ask-ai-15s.mp4`.
- `python3 tools/build_15s.py` 가 `v15/`(index.html + compositions)를 생성한다. 30초 씬의 `<style>`을 그대로 가져오고 15초 전용 위치만 덮어쓴다. `v15/assets`는 `../assets` 심볼릭 링크. v15 파일은 직접 고치지 말고 생성기를 고친다.
- 오디오: `python3 tools/make_audio.py --cut 15` → `bgm-15s.wav`, `sfx-15s.wav` (6.0초 BGM 컷, 8.5 어쿠스틱, 12.5 해결 코드, −16 LUFS).
- 폰트 서브셋은 30초·15초 문구를 모두 포함한다(`tools/subset_font.py`가 v15도 스캔).
- 검사·렌더: `cd v15 && npx --yes hyperframes@0.8.200 check` / `render --quality delivery -o ../renders/ask-ai-15s.mp4`.
