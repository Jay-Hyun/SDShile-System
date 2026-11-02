#!/usr/bin/env python3
"""「AI에게 물었다」 오디오: 제공 BGM 편집 + 효과음 2개(질문 전송·[상담사 연결] 누름) + 마스터.

Usage: python3 tools/make_audio.py [--cut 15]
  assets/music/source.mp3 (grand_project, Pixabay 505611) 를 잘라 붙인다. 합성 음악은 없다.
  → assets/audio/bgm.wav, sfx.wav (30s) / bgm-15s.wav, sfx-15s.wav (15s)
  두 스템에 같은 게인·리미터를 걸어 합이 −15 LUFS(±0.3), 트루피크 ≤ −1 dBTP.
  편집 구간·챕터·컷은 beats/cuts-30.json / cuts-15.json 으로도 저장(HTML 타이밍과 같은 수식).
  아트 디렉션 v3: 컷·챕터는 다운비트(1마디 = 4P)에만. 먹먹해지는 처리(LPF·피치 다운) 없음, 합성 효과음은 부드러운 탭 2개뿐(음악보다 −20dB).

음악 편집 (P = 1비트 = 60/125.03 s, 소스 다운비트 1.007 + 4P·k):
  30s  A  src 1.007→  v 0.000–12.477 (26P)   → 12.477 클린 스톱: 비트에서 80ms 페이드 후 완전 무음 (로딩 개그)
       —  무음 12.98–14.637 (초침 틱만)
       B  src 12.524→ v 14.637–26.154 (24P)  14.637 다운비트 슬램(🙂 말풍선), 18.476 = src 16.363 B섹션 크래시(브랜드)
       C  src 29.800→ v 26.154–30.000          28.073 = src 31.719 마지막 크래시, 29.65–30.0 페이드
  15s  A  src 1.007→  v 0.000–5.759 (12P)    → 5.759 클린 스톱 (다운비트, 80ms 페이드 → 무음)
       B  src 14.443→ v 6.580–10.420 (8P)      6.580 슬램, 8.500 = src 16.363 크래시(브랜드)
       C  src 29.800→ v 10.420–15.000          12.339 = src 31.719 크래시(슬로건), 14.6–15.0 페이드
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
BEATS = json.load(open(os.path.join(ROOT, "beats", "source.json")))
P = 60.0 / BEATS["bpm"]
DB0 = 1.007  # 소스 첫 다운비트 (beats/source.json downbeats[0])
rng = np.random.default_rng(5)


def src_downbeat(t):
    """가장 가까운 소스 다운비트 (분석 그리드)"""
    d = np.array(BEATS["downbeats"])
    return float(d[np.argmin(np.abs(d - t))])


# ------------------------------------------------------------------ 큐 (HTML과 같은 수식)
# 챕터 = 다운비트(1마디 BAR = 4P). 30s A 구간 다운비트 = k·BAR, B 구간 = R + k·BAR (R = 음악 복귀 다운비트).
# cuts = 실제 화면이 갈리는 지점: 하드컷(30s C9·C10, 15s C6) + 시그니처 오프닝 윈도우의 중간점(가장 빠른 순간 = 크래시).
# chat 은 컷 없이 한 컷으로 흐른다(말풍선이 도착하면 컬럼이 450ms in-out 으로 밀려 올라간다).
def cues(cut):
    B = lambda k: k * P
    BAR = 4 * P
    if cut == 30:
        R = B(30.5)
        WIN = 536 / 30  # [상담사 연결]이 열리기 시작 (1200ms, 중간점 = 크래시)
        c = {
            "dur": 30.0, "R": R, "brand": R + 2 * BAR, "win": WIN,
            "chapters": {"C1": 0.0, "C2": 2 * BAR, "C3": 4 * BAR, "C4": 5 * BAR, "C5": B(26), "C6": R,
                         "C7": R + 2 * BAR, "C8": R + 3 * BAR, "C9": R + 4 * BAR, "C10": R + 6 * BAR, "end": 30.0},
            # C10 은 엔드 시퀀스 안의 문장 교체(퇴장 300ms → 다운비트에 상승)라 하드컷이 아니다
            "cuts": {"open_mid": WIN + 0.6, "C9": R + 4 * BAR},
            "music": [
                {"v0": 0.0, "v1": B(26), "src": DB0, "tail": "stop"},
                {"v0": R, "v1": R + 24 * P, "src": src_downbeat(12.524)},
                {"v0": R + 24 * P, "v1": 30.0, "src": src_downbeat(29.8), "fade": 0.35},
            ],
        }
    else:
        R = 8.5 - 4 * P
        WIN = 237 / 30
        c = {
            "dur": 15.0, "R": R, "brand": 8.5, "win": WIN,
            # 15s C2·C3 은 훅 3초(8자/초)와 고민 중(5.759 테이프 스톱) 사이에 들어가야 해서 읽는 속도에 둔 장면 안 등장 (컷 아님)
            "chapters": {"C1": 0.0, "C2": 3.0, "C2u": 2 * BAR, "C3": 4.9, "gag": 3 * BAR, "C4": R, "C5": 8.5,
                         "C5b": R + 2 * BAR, "C6": R + 3 * BAR, "end": 15.0},
            "cuts": {"open_mid": WIN + 0.6, "C6": R + 3 * BAR},
            "music": [
                {"v0": 0.0, "v1": B(12), "src": DB0, "tail": "stop"},
                {"v0": R, "v1": 8.5 + 4 * P, "src": src_downbeat(14.443)},
                {"v0": 8.5 + 4 * P, "v1": 15.0, "src": src_downbeat(29.8), "fade": 0.4},
            ],
        }
    return c


# ------------------------------------------------------------------ 입출력
def load_src():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets/music/source.mp3"),
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1)), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1))


# ------------------------------------------------------------------ 음악 편집
STOP_FADE = 0.08  # 클린 스톱: 정지 지점(비트)부터 80ms 페이드아웃, 그 뒤 완전 무음. 필터·피치 변화 없음


def build_music(c, src):
    N = int(round(c["dur"] * SR))
    out = np.zeros((N, 2))
    xf = int(0.006 * SR)
    for seg in c["music"]:
        i0, i1 = int(round(seg["v0"] * SR)), int(round(seg["v1"] * SR))
        s0 = int(round(seg["src"] * SR))
        n = i1 - i0
        if seg.get("tail") == "stop":
            n += int(STOP_FADE * SR)
        piece = src[s0 : s0 + n].copy()
        piece[:xf] *= np.linspace(0, 1, xf)[:, None]
        if seg.get("fade"):
            nf = int(seg["fade"] * SR)
            piece[-nf:] *= (np.linspace(1, 0, nf) ** 1.5)[:, None]
        elif seg.get("tail") == "stop":
            nf = int(STOP_FADE * SR)
            piece[-nf:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nf)))[:, None]
        else:
            piece[-xf:] *= np.linspace(1, 0, xf)[:, None]
        out[i0 : i0 + len(piece)] += piece[: N - i0]
    return out


# ------------------------------------------------------------------ 효과음: 부드러운 탭 2개뿐
def t_arr(d):
    return np.arange(int(SR * d)) / SR


def fft_filter(x, lo=None, hi=None, order=2):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, n)


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-t / d)


def soft_tap():
    """손끝으로 누르는 부드러운 탭: 낮은 몸통(170Hz, 14ms 감쇠) + 2.5kHz 아래로 깎은 짧은 클릭. 피크 1로 정규화."""
    d = 0.07
    t = t_arr(d)
    body = np.sin(2 * np.pi * 170 * t) * env(len(t), 0.0015, 0.014)
    click = fft_filter(rng.standard_normal(len(t)), lo=300, hi=2500) * env(len(t), 0.0008, 0.004)
    x = 0.9 * body + 0.35 * click
    return x / np.max(np.abs(x))


REL_DB = -20.0  # 탭 RMS(첫 40ms) = 주변 음악 RMS(±0.5s) − 20dB


def build_sfx(c, music):
    N = int(round(c["dur"] * SR))
    buf = np.zeros((N, 2))
    cue_list = []

    def place_rel(t, name):
        sig = soft_tap()
        i = int(round((t + 1 / 30) * SR))  # 소리는 그림보다 1프레임 늦게 (sound.md)
        a, b = max(0, i - SR // 2), min(N, i + SR // 2)
        m_rms = float(np.sqrt(np.mean(music[a:b] ** 2)))
        s_rms = float(np.sqrt(np.mean(sig[: int(0.04 * SR)] ** 2)))
        gain = m_rms * 10 ** (REL_DB / 20) / s_rms
        sig = sig[: N - i] * gain
        buf[i : i + len(sig)] += sig[:, None]
        cue_list.append({"t": round(t, 3), "sfx": name, "rel_db": REL_DB, "music_rms_dbfs": round(20 * np.log10(m_rms), 1)})

    BAR = 4 * P
    if c["dur"] == 30.0:
        kSend = 5 * BAR + 0.25 + 0.6 + 0.25 + 0.5 + 0.7  # chat.html C4: 아래 입력창 전송
        place_rel(kSend, "질문 전송 탭")
    else:
        place_rel(4.9, "질문 전송 탭")  # 15s: 다시 묻는 말풍선
    place_rel(c["win"] - 0.42, "[상담사 연결] 누름 탭")
    return buf, cue_list


def limiter_gain(mix, ceiling, w=240):
    a = np.max(np.abs(mix), axis=1)
    req = np.minimum(1.0, ceiling / np.maximum(a, 1e-9))
    pad = (-len(req)) % w
    r = np.concatenate([req, np.ones(pad)]).reshape(-1, w).min(axis=1)
    r = np.minimum(r, np.minimum(np.r_[r[1:], 1.0], np.r_[1.0, r[:-1]]))
    g = np.repeat(r, w)[: len(req)]
    k = np.hanning(2 * w)
    k /= k.sum()
    gp = np.concatenate([np.full(w, g[0]), g, np.full(w, g[-1])])
    return np.convolve(gp, k, mode="same")[w:-w][:, None]


def main():
    cut = 15 if "--cut" in sys.argv and sys.argv[sys.argv.index("--cut") + 1] == "15" else 30
    c = cues(cut)
    src = load_src()
    music = build_music(c, src)
    sfx, sfx_cues = build_sfx(c, music)
    out = os.path.join(ROOT, "assets", "audio")
    os.makedirs(out, exist_ok=True)
    suffix = "-15s" if cut == 15 else ""
    tmp = os.path.join(out, "_mix_tmp.wav")
    target, ceiling = -15.0, 10 ** (-1.7 / 20)
    gain = 0.6
    for _ in range(10):
        raw = (music + sfx) * gain
        g = limiter_gain(raw, ceiling)
        write_wav(tmp, raw * g)
        i_lufs, tp = measure(tmp)
        if abs(i_lufs - target) < 0.1:
            break
        gain *= 10 ** ((target - i_lufs) / 20)
    g = limiter_gain((music + sfx) * gain, ceiling)
    write_wav(os.path.join(out, "bgm" + suffix + ".wav"), music * gain * g)
    write_wav(os.path.join(out, "sfx" + suffix + ".wav"), sfx * gain * g)
    write_wav(tmp, (music + sfx) * gain * g)
    i_lufs, tp = measure(tmp)
    os.remove(tmp)
    rec = {"cut": cut, "bpm": BEATS["bpm"], "beat_period": P, "R_slam": round(c["R"], 4), "brand": round(c["brand"], 4),
           "win": round(c["win"], 4),
           "chapters": {k: round(v, 4) for k, v in c["chapters"].items()},
           "cuts": {k: round(v, 4) for k, v in c["cuts"].items()},
           "sfx": sfx_cues,
           "music_segments": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()} for s in c["music"]],
           "mix": {"integrated_lufs": i_lufs, "true_peak_dbtp": tp, "gain": round(float(gain), 4),
                   "max_gain_reduction_db": round(float(20 * np.log10(np.min(g))), 2)}}
    json.dump(rec, open(os.path.join(ROOT, "beats", f"cuts-{cut}.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
