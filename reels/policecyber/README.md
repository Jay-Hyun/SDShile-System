# 경찰복지사이버평생교육원 홍보 릴스 (HyperFrames)

1080×1920, 30fps, 28초. 레퍼런스(SaaS Promo Teaser) 문법: 흰 배경 + 브랜드 그라데이션 + 다크 교차, 단어 블러 등장, 계속되는 줌아웃, 체크박스 단어 롤, 잔상 단어, 카드 콜라주, 커서 클릭 CTA. 컷은 BGM 비트(134 BPM)에 맞춤.

| 시간 | 씬 | 내용 |
|---|---|---|
| 0–1.2s | poster | 1차 훅 포스터: 접수 마감 알림, "평생교육원 중 법학 전공은 단 1곳*", 교육부장관 명의 학사 직인, 퇴사·재입학·출석수업 ✕ |
| 1.2–3.7s | far | 2차 훅: 초근접 블러 '변호사' → "그 꿈, 아직도" → 그라데이션 위 '멀게?' 잔상 |
| 3.7–6.4s | who | 체크박스 롤: 직장인 / 비전공자 / 수험생 / 로스쿨 준비생 |
| 6.4–9.1s | online | "퇴근 후, [수강 카드 3장] 온라인으로." 오프라인 수업 0회 |
| 9.1–11.6s | degree | 학위는 진짜. 교육부장관 명의 학위증 |
| 11.6–14.3s | together | 혼자 말고, (1:1 코인) 같이. 떠다니는 플랜 칩 |
| 14.3–17.8s | subjects | 원형 블롭 전환 → 과목 카드 콜라주, 물권법·채권총칙 전공필수 강조 |
| 17.8–21.2s | paths | 이 길이 가까워져요 + 로스쿨/로펌·법무팀/경찰·공무원 카드 |
| 21.2–23s | go | 상담 신청 → |
| 23–28s | cta | 상담만 받아도 돼요 · 마감 · 그라데이션 전화 버튼 + 커서 클릭 · 면책 |

씬 파일은 `tools/build_scenes.py`(+ `tools/common.css`)로 생성: `python3 tools/build_scenes.py compositions`.

```bash
npx hyperframes@0.8.200 preview      # 미리보기
npx hyperframes@0.8.200 check        # 검사
npx hyperframes@0.8.200 render -o renders/out.mp4
```

폰트: `assets/fonts/PretendardGOVVariable.woff2` 는 사용 글자만 남긴 서브셋. 문구를 바꿔 새 글자가 생기면
원본 Pretendard GOV Variable로 다시 `pyftsubset` 해야 한다.
