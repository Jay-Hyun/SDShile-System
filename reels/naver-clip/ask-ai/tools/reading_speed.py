#!/usr/bin/env python3
"""구간별 읽기 속도 (공백 뺀 글자 수 ÷ 구간 초). 기준: 새로 뜨는 메인 텍스트 ≤ 10자/초 (훅 ≤ 8).
Usage: python3 tools/reading_speed.py
CTA 트랙(유도·버튼·안내·전화)과 앞 장면에서 이미 읽은 문장의 반복은 따로 센다. 시각은 lib/cue.js 에서.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import cue  # noqa: E402


def n(s):
    return len([c for c in s if not c.isspace()])


TITLE, Q1 = "AI가 답 못 한 질문", "AI 시대에도 안 없어질 직업 알려줘."
LEAD = ["반복 업무는 점점 자동화되고,", "문서 정리와 자료 검색도 빨라지겠지만"]
KEY = ["…최종 판단과 법적 책임이", "따르는 일은 사람이 맡게 됩니다."]
EX = "예: 법조인, 법무 책임자"
Q2 = "나 전문대 나왔고 회사 다니는데, 법 공부 할 수 있어?"
GAG = ["고민 중…", "아직 고민 중…", "음…"]
A2 = "이건 책임지고 답할 분께 넘길게요"
USP = "국내 유일 100% 온라인 법학사*"
QUOTE = "“나 전문대 나왔고 회사 다니는데…”"
ANS = "첫 계단은, 전문대면 60학점부터"
HEAD = "AI도 넘긴 질문, 사람이 1:1로 답해드려요."
LIST = ["100% 온라인, 출석 없이", "교육부장관 명의 법학사", "전문대 졸업이면 60학점부터"]
SLO = "책임지는 자리로, 지금 있는 자리에서."
PUSH, BTN, NOTE = "내 학력으로 몇 학기? 1:1로 확인하세요", "무료 상담 신청", "상담만 받아도 돼요."
CHAT_BTN = "상담사 연결"


def row(name, a, b, main, track=0, note=""):
    d = b - a
    t = main + track
    print(f"| {name} | {a:.3f}–{b:.3f} | {d:.2f} | {main} | {main/d:.1f} | {track} | {t/d:.1f} | {note} |")


def table(cut):
    c = cue(cut)
    R, BR, END = c["R"], c["BR"], c["END"]
    print(f"\n### {cut}s\n| 구간 | 시각 (s) | 길이 | 새 메인 글자 | 자/초 | 트랙·반복 글자 | 합계 자/초 | 비고 |\n|---|---|---|---|---|---|---|---|")
    if cut == 30:
        row("C1 훅", 0, c["C2"], n(TITLE) + n(Q1), 0, "훅 ≤ 8자/초")
        row("C2 답변", c["C2"], c["C3"], sum(map(n, KEY)), sum(map(n, LEAD)), "흐린 앞 문단 2줄은 보조(리드 승인), 핵심 문장만 메인")
        row("C3 예시", c["C3"], c["C4"], n(EX))
        row("C4 질문 입력", c["C4"], c["GAG"], n(Q2))
        row("고민 중…", c["GAG"], R, sum(map(n, GAG)), 0, "글자 개그(음악은 계속)")
        row("C6 책임 넘김", R, c["WIN"], n(A2), n(CHAT_BTN))
        row("C7 USP", BR, c["C8"], n(USP), n(QUOTE), "인용은 챗에서 이미 읽음")
        row("C8 사람의 답", c["C8"], c["C9"], n(ANS))
        row("엔드 ① CTA 문장", c["C9"], c["LIST"], n(HEAD), n(PUSH) + n(BTN), "유도·버튼은 CTA 트랙")
        row("엔드 ② 증거 리스트", c["LIST"], c["SLO"], sum(map(n, LIST)))
        row("엔드 ③ 슬로건", c["SLO"], END, n(SLO), n(NOTE))
        main = n(HEAD) + sum(map(n, LIST)) + n(SLO)
        trk = n(PUSH) + n(BTN) + n(NOTE)
        print(f"\n엔드 시퀀스 {c['C9']:.3f}–{END} ({END-c['C9']:.3f}s): 메인 {main}자 = {main/(END-c['C9']):.1f}자/초, 트랙 포함 {main+trk}자 = {(main+trk)/(END-c['C9']):.1f}자/초")
    else:
        row("C1 훅", 0, c["C2"], n(TITLE) + n(Q1), 0, "훅 ≤ 8자/초")
        short = ["반복 업무는 점점 자동화되겠지만,", "법적 책임은 사람 몫입니다.", "예: 법조인"]
        row("C2 답변", c["C2"], c["C3"], sum(map(n, short)))
        row("C3 질문·고민 중…", c["C3"], R, n("전문대 졸 직장인도 법 공부 돼?") + n(GAG[0]))
        row("C4 책임 넘김", R, c["WIN"], n("책임질 분께 넘길게요"), n(CHAT_BTN))
        row("C5 USP", BR, c["C5b"], n(USP), n(PUSH), "유도는 전화와 함께 일찍(CTA 트랙)")
        row("C5b 사람의 답", c["C5b"], c["C6"], n("첫 계단, 전문대면 60학점부터"))
        row("C6 엔드카드", c["C6"], END, n(SLO), n(BTN), "새 글은 슬로건 하나(+버튼)")


if __name__ == "__main__":
    table(30)
    table(15)
