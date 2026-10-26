# 경찰복지사이버평생교육원 홍보 릴스 (HyperFrames)

1080×1920, 30fps, 30초. 앵글: "법조계가 멀게만 느껴졌던 사람들" — 씬마다 법원이 가까워지는 구조.

| 시간 | 씬 파일 | 내용 |
|---|---|---|
| 0–6s | compositions/hook.html | 종합 훅: "나와는 먼 얘기 같았나요?" → "생각보다 가까워요" + 핵심 3포인트 |
| 6–10s | compositions/start.html | 법대 안 나와도 — 지금 학력 그대로 |
| 10–14s | compositions/online.html | 일 그만두지 않아도 — 퇴근 후·주말, 오프라인 0회 |
| 14–18s | compositions/planner.html | 혼자가 아니어도 — 1:1 학습 설계 |
| 18–22s | compositions/degree.html | 교양 아닌 '법학 전공' 학위 (교육부장관 명의) |
| 22–26s | compositions/paths.html | 로스쿨 · 로펌/법무팀 · 경찰/공무원 |
| 26–30s | compositions/cta.html | 상담 CTA, 개강/마감, 면책 |

배경(법원·길·과목 마키)은 compositions/world.html 하나가 30초 내내 깔림.

```bash
npx hyperframes@0.8.200 preview      # 미리보기
npx hyperframes@0.8.200 check        # 검사
npx hyperframes@0.8.200 render -o renders/out.mp4
```

폰트: `assets/fonts/PretendardGOVVariable.woff2` 는 사용 글자만 남긴 서브셋. 문구를 바꿔 새 글자가 생기면
원본 Pretendard GOV Variable로 다시 `pyftsubset` 해야 한다.
