# 경찰복지사이버평생교육원 홍보 릴스 (HyperFrames)

1080×1920, 30fps, 28초. 레퍼런스(SaaS Promo Teaser) 문법을 따르되, 컷은 BGM 비트(134 BPM, `beats/assets/music/bgm.mp3.json`)마다 한 번의 변화로 맞췄다.

연출 원칙 (v4)
- 한 비트에 한 변화. 카피는 2~5글자로 쪼갬
- 핵심 단어는 항상 같은 눈높이(y=700)에 착지 → 시선이 화면을 헤매지 않음
- 카메라는 씬마다 한 방향으로 천천히 다가감. 펌프·흔들림·오버슈트(튀는 모션) 없음
- 등장은 블러→선명 0.14~0.3초, 퇴장은 다음 비트 0.07초 전

| 시간 | 씬 | 비트별 카피 |
|---|---|---|
| 0–1.2s | poster | 포스터 그대로(✕ 포함, 썸네일) → '1' 속으로 줌 |
| 1.2–3.7s | far | 꿈꿔본 적 있죠 · 변호사 · 검사 · 법무관 · 근데, 아직도 · 멀게? (+잔상) |
| 3.7–6.4s | who | ☑ 직장인 · 비전공자 · 수험생 · 로스쿨 준비생 · 누구나 OK |
| 6.4–9.1s | online | 퇴사? ✕ · 재입학? ✕ · 퇴근 후, [카드] 온라인으로. · 오프라인 수업 0회 |
| 9.1–11.6s | degree | 학위는 · 진짜. · 학위증 · 직인 · 교육부장관 명의 법학사 |
| 11.6–14.3s | together | 혼자? · 아니, · (1:1) · 같이. · 플랜 칩 |
| 14.3–17.8s | subjects | 과목 카드 · 진짜 '법학 전공' 과목으로 · 물권법 · 채권총칙 · 여기뿐* |
| 17.8–21.2s | paths | 이 길이 · 로스쿨 · 로펌·법무팀 · 경찰·공무원 · 가까워져요 |
| 21.2–23s | go | 상담 · 신청 · → |
| 23–28s | cta | 망설여진다면, · 상담만 · 받아도 돼요. · 마감 · 전화 버튼 · 커서 클릭 |

씬 파일과 index.html 씬 호스트는 `tools/build_scenes.py`(+ `tools/common.css`)가 비트 그리드에서 생성: `python3 tools/build_scenes.py`.

```bash
npx hyperframes@0.8.200 preview      # 미리보기
npx hyperframes@0.8.200 check        # 검사
npx hyperframes@0.8.200 render -o renders/out.mp4
```

폰트: `assets/fonts/PretendardGOVVariable.woff2` 는 사용 글자만 남긴 서브셋. 문구를 바꿔 새 글자가 생기면
원본 Pretendard GOV Variable로 다시 `pyftsubset` 해야 한다.
