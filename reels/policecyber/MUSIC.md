# BGM

사용 곡: **Event - Event Music** — lNPLUSMUSIC (Pixabay #611920)
https://pixabay.com/music/percussion-event-event-music-611920/

- 라이선스: Pixabay Content License(상업 이용 가능, 출처 표기 불필요). 곡 페이지에 Content ID / AI 생성 표시 없음(2026-10-26 확인).
- 원본: 52.2s, 134 BPM, -11.7 LUFS, 트루피크 +1.1 dBFS(원본 자체가 클리핑).
- `assets/music/bgm.mp3` 가공:
  - 원본 0~30s, 0.2s 페이드인 / 28.5s부터 1.5s 페이드아웃
  - 0~2.6s 로우패스(650Hz) → 2.6s "생각보다 가까워요" 등장 때 0.3s 동안 필터 열림 (멀리 → 가까이)
  - 리미터로 피크 -1.2 dBFS, 약 -14.4 LUFS (렌더 결과 -15.4 LUFS)
- 씬 전환은 비트(`beats/assets/music/bgm.mp3.json`)에 맞춤: 6.2 / 10.23 / 14.14 / 18.05 / 22.09 / 25.98s
