# 경찰복지사이버평생교육원 홍보 릴스 (HyperFrames)

1080×1920, 30fps, 30초. SaaS 런칭 영상 스타일(큰 단어, 빠른 컷, 슬롯 롤, 가이드 라인). 컷은 BGM 비트(134 BPM)에 맞춤.

| 시간 | 씬 파일 | 내용 |
|---|---|---|
| 0–3.3s | compositions/poster.html | 1차 훅: 핵심을 모은 포스터 (유일한 법학 전공* · 오프라인 0회 · 교육부장관 명의 학사 · 1:1 · 개강 · 전화) |
| 3.3–8.4s | compositions/hook2.html | 2차 훅: 변호사→검사→법무관 슬롯 → "나랑은 먼 얘기?" → "아니요. 출발점은 법학 전공" |
| 8.4–11.1s | compositions/online.html | 일은 그대로 · 오프라인 수업 0회 |
| 11.1–13.7s | compositions/start.html | 법대 안 나와도, 학력 그대로 (고졸·전문대졸·대졸) |
| 13.7–16.8s | compositions/degree.html | 학위는 진짜 · 교육부장관 명의 법학사 |
| 16.8–19.4s | compositions/planner.html | 혼자 말고, 같이 · 1:1 학습 설계 |
| 19.4–23.7s | compositions/paths.html | 로스쿨/로펌/법무팀/경찰/공무원 롤 → 출발점은 법학 전공 |
| 23.7–30s | compositions/cta.html | 상담만 받아도 돼요 · 개강/마감 · 전화 버튼 · 면책 |

```bash
npx hyperframes@0.8.200 preview      # 미리보기
npx hyperframes@0.8.200 check        # 검사
npx hyperframes@0.8.200 render -o renders/out.mp4
```

폰트: `assets/fonts/PretendardGOVVariable.woff2` 는 사용 글자만 남긴 서브셋. 문구를 바꿔 새 글자가 생기면
원본 Pretendard GOV Variable로 다시 `pyftsubset` 해야 한다.
