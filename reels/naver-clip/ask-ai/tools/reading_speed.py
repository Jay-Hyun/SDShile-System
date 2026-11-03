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


Q = "전문대 나왔는데, 퇴근하고 법 공부 할 수 있을까?"
LEAD = "반복 업무는 자동화되고,"
KEY = "최종 판단과 법적 책임은 사람이 맡게 됩니다."
A2 = "이건 책임지고 답할 분께 넘길게요"
ANS1 = "퇴근 후·주말에, 100% 온라인으로 들을 수 있어요."
ANS2 = "이미 딴 학점이 있으면 기간·비용을 줄일 수 있어요."
LIST = ["100% 온라인, 출석 없이", "교육부장관 명의 법학사", "전문대 졸업이면 60학점부터"]
SLO = "책임지는 자리로, 지금 있는 자리에서."
BTN, TEL = "내 학점으로 남은 기간, 무료로 진단받기", "070-4006-7128 (평일 10–18시)"
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
        row("C1 훅(입력창에 질문)", 0, c["C2"], n(Q), 0, "훅 ≤ 8자/초")
        row("전송 · AI 점", c["C2"], c["C2b"], 0, n(Q), "질문은 말풍선으로 반복 (새 글 없음)")
        row("AI 답 ① 앞 문단", c["C2b"], c["C3"], n(LEAD), 0, "흐린 줄")
        row("AI 답 ② 핵심 문장", c["C3"], R, n(KEY))
        row("책임 넘김", R, c["WIN"], n(A2), n(CHAT_BTN))
        row("S1 상담사 답 ①", BR, c["S2"], n(ANS1), n(BTN) + n(TEL) + n(Q), "버튼·전화는 CTA 트랙(BR+0.75 부터 끝까지), 인용은 반복")
        row("S2 상담사 답 ②", c["S2"], c["S3"], n(ANS2))
        row("S3 근거 3줄", c["S3"], c["S4"], sum(map(n, LIST)))
        row("S4 슬로건", c["S4"], END, n(SLO))
    else:
        row("C1 훅(입력창에 질문)", 0, c["C2"], n(Q), 0, "훅 ≤ 8자/초")
        row("전송 · AI 점", c["C2"], c["HAND"], 0, n(Q), "질문은 말풍선으로 반복 (새 글 없음)")
        row("책임 넘김", c["HAND"], c["WIN"], n(A2), n(CHAT_BTN))
        row("S1 상담사 답", BR, c["C6"], n(ANS1), n(BTN) + n(TEL) + n(Q), "버튼·전화는 CTA 트랙, 인용은 반복")
        row("엔드카드 슬로건", c["C6"], END, n(SLO), 0, "새 글은 슬로건 하나 (버튼·전화는 계속)")


if __name__ == "__main__":
    table(30)
    table(15)
