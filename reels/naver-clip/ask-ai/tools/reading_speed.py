#!/usr/bin/env python3
"""v7 구간별 읽기 속도 (공백 뺀 새 글자 수 ÷ 그 글이 화면에 머무는 초). 기준: 새 메인 텍스트 ≤ 10자/초.
Usage: python3 tools/reading_speed.py      시각은 lib/cue.js. 배지·※ 안내(컴플라이언스)는 따로 센다.
엔드카드는 마지막까지 머무는 포스터라 창 = FLOOD → END."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import cue  # noqa: E402


def n(s):
    return len([c for c in s if not c.isspace()])


Q = "전문대 나왔는데, 퇴근하고 법 공부 할 수 있을까?"
LEAD, KEY = "반복 업무는 자동화되고,", "최종 판단과 법적 책임은 사람이 맡게 됩니다."
HAND = "이건 책임지고 답할 분께 넘길게요"
ANS1, ANS1S = "퇴근 후·주말에, 100% 온라인으로 들을 수 있어요.", "퇴근 후·주말에, 100% 온라인으로."
ANS2 = "이미 딴 학점이 있으면 기간·비용을 줄일 수 있어요."
LIST = "100% 온라인, 출석 없이 교육부장관 명의 법학사 전문대 졸업이면 60학점부터"
SLO = "책임지는 자리로, 지금 있는 자리에서."
LOGO, QQ = "경찰복지사이버평생교육원", "내 학점이면, 얼마나 남았을까?"
ONE, ACT, TEL = "지금 학력·학점으로 남은 과정, 1:1로 짚어드려요", "아래 링크에서 내 경우 확인하기", "전화 문의 070-4006-7128 (평일 10–18시)"
DISC = "로스쿨 입학·변호사시험 합격·취업을 보장하지 않습니다."


def row(name, a, b, text, note=""):
    k = n(text) if isinstance(text, str) else sum(map(n, text))
    d = b - a
    flag = "✓" if k / d <= 10 else "✗"
    print(f"| {name} | {a:.2f}–{b:.2f} | {d:.2f} | {k} | {k/d:.1f} | {flag} | {note} |")


def table(cut):
    c = cue(cut)
    print(f"\n### {cut}s\n| 구간 | 시각 (s) | 길이 | 새 글자 | 자/초 | ≤10 | 비고 |\n|---|---|---|---|---|---|---|")
    row("훅 질문 (폰 안 → Display)", 0, c["DIVE"], Q)
    if cut == 30:
        row("AI 답 앞 문단", c["LEAD"], c["KEY"], LEAD)
        row("AI 답 핵심", c["KEY"], c["HAND"], KEY, "다음 새 글(핸드오프)까지")
        row("AI 답 핵심 (화면에 머무는 창)", c["KEY"], c["GROW"], KEY, "핸드오프 동안에도 위에 남아 있다")
        row("핸드오프", c["HAND"], c["GROW"], HAND)
        row("상담사 답 ①", c["WORLD"], c["ANS2"], ["상담사", ANS1])
        row("상담사 답 ②", c["ANS2"], c["DIP1"], ANS2)
        row("근거 카드", c["DIP1"], c["DIP2"], LIST)
        row("슬로건", c["DIP2"], c["FLOOD"], SLO)
        row("엔드카드 (메인: 질문형 CTA + 1:1 + 행동 줄)", c["FLOOD"], 30, [QQ, ONE, ACT])
        row("엔드카드 (전부: + 락업·전화·고지)", c["FLOOD"], 30, [QQ, ONE, ACT, LOGO, TEL, DISC], "포스터 정지 4.2 s")
    else:
        row("핸드오프", c["HAND"], c["GROW"], HAND)
        row("상담사 답", c["WORLD"], c["DIP2"], ANS1S, "15초는 '상담사' 라벨 없음")
        row("슬로건", c["DIP2"], c["FLOOD"], SLO)
        row("엔드카드 (메인: 질문형 CTA + 행동 줄)", c["FLOOD"], 15, [QQ, ACT])
        row("엔드카드 (전부: + 락업·전화·고지)", c["FLOOD"], 15, [QQ, ACT, LOGO, TEL, DISC], "포스터 정지 3.9 s")


if __name__ == "__main__":
    table(30)
    table(15)
