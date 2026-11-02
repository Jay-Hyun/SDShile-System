#!/usr/bin/env python3
"""「AI에게 물었다」 오디오: 제공 BGM 편집 + 비트 맞춤 SFX + 마스터.

Usage: python3 tools/make_audio.py [--cut 15]
  assets/music/source.mp3 (grand_project, Pixabay 505611) 를 잘라 붙인다. 합성 음악은 없다.
  → assets/audio/bgm.wav, sfx.wav (30s) / bgm-15s.wav, sfx-15s.wav (15s)
  두 스템에 같은 게인·리미터를 걸어 합이 −15 LUFS(±0.3), 트루피크 ≤ −1 dBTP.
  편집 구간·큐는 beats/cuts-30.json / cuts-15.json 으로도 저장(HTML 타이밍과 같은 수식).

음악 편집 (P = 1비트 = 60/125.03 s, 소스 다운비트 1.007 + 4P·k):
  30s  A  src 1.007→  v 0.000–12.477 (26P)   → 12.477 테이프 스톱 0.5s (로딩 개그, 음악 멈춤)
       —  무음 12.98–14.637 (초침 틱만)
       B  src 12.524→ v 14.637–26.154 (24P)  14.637 다운비트 슬램(🙂 말풍선), 18.476 = src 16.363 B섹션 크래시(브랜드)
       C  src 29.800→ v 26.154–30.000          28.073 = src 31.719 마지막 크래시, 29.65–30.0 페이드
  15s  A  src 1.007→  v 0.000–5.759 (12P)    → 5.759 테이프 스톱
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
def cues(cut):
    B = lambda k: k * P
    if cut == 30:
        R = B(30.5)
        T7 = R + 8 * P
        c = {
            "dur": 30.0, "R": R, "brand": T7,
            "cuts": {"C1": 0.0, "C2": B(6), "C3": B(14), "C4": B(20), "C5": B(26), "C6": R,
                     "C7": T7, "C8": T7 + 6 * P, "C9": T7 + 11 * P, "C10": R + 26 * P, "end": 30.0},
            "music": [
                {"v0": 0.0, "v1": B(26), "src": DB0, "tail": "tapestop"},
                {"v0": R, "v1": R + 24 * P, "src": src_downbeat(12.524)},
                {"v0": R + 24 * P, "v1": 30.0, "src": src_downbeat(29.8), "fade": 0.35},
            ],
        }
    else:
        R = 8.5 - 4 * P
        c = {
            "dur": 15.0, "R": R, "brand": 8.5,
            "cuts": {"C1": 0.0, "C2": B(6), "C3": B(10), "gag": B(12), "C4": R, "C5": 8.5, "C6": 8.5 + 8 * P, "end": 15.0},
            "music": [
                {"v0": 0.0, "v1": B(12), "src": DB0, "tail": "tapestop"},
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
def build_music(c, src):
    N = int(round(c["dur"] * SR))
    out = np.zeros((N, 2))
    xf = int(0.006 * SR)
    for seg in c["music"]:
        i0, i1 = int(round(seg["v0"] * SR)), int(round(seg["v1"] * SR))
        s0 = int(round(seg["src"] * SR))
        piece = src[s0 : s0 + (i1 - i0)].copy()
        piece[:xf] *= np.linspace(0, 1, xf)[:, None]
        if seg.get("fade"):
            nf = int(seg["fade"] * SR)
            piece[-nf:] *= (np.linspace(1, 0, nf) ** 1.5)[:, None]
        elif not seg.get("tail"):
            piece[-xf:] *= np.linspace(1, 0, xf)[:, None]
        out[i0 : i0 + len(piece)] += piece
        if seg.get("tail") == "tapestop":
            # 테이프 스톱: 재생 속도 1→0 (0.5s), 피치가 같이 내려간다. 원곡을 늦춘 것뿐, 새 음은 없다.
            T = 0.5
            n = int(T * SR)
            tau = np.arange(n) / SR
            pos = seg["src"] + (seg["v1"] - seg["v0"]) + tau - tau ** 2 / (2 * T)
            idx = pos * SR
            base = np.arange(len(src))
            ts = np.stack([np.interp(idx, base, src[:, ch]) for ch in range(2)], axis=1)
            ts *= (1 - tau / T)[:, None] ** 0.6
            # 끝으로 갈수록 고역을 깎아 '늘어지는' 느낌 (1-pole LPF, 계수 스윕)
            y = np.zeros_like(ts)
            prev = np.zeros(2)
            for k in range(n):
                a = 0.9 - 0.85 * (k / n)
                prev = prev + a * (ts[k] - prev)
                y[k] = prev
            out[i1 : i1 + n] = y[: N - i1]
    return out


# ------------------------------------------------------------------ SFX (원 make_audio.py의 SFX 함수, 음악 없음)
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


def noise(d):
    return rng.standard_normal(int(SR * d))


def key_click(heavy=False):
    d = 0.05
    t = t_arr(d)
    c = fft_filter(noise(d), lo=1800 if not heavy else 900, hi=6500) * env(len(t), 0.0003, 0.006 if not heavy else 0.012)
    body = np.sin(2 * np.pi * (240 if not heavy else 160) * t) * env(len(t), 0.0005, 0.012)
    return 0.7 * c + 0.4 * body


def whoosh(d=0.45, up=True, lo=400, hi=5000):
    t = t_arr(d)
    nz = noise(d)
    a, b = fft_filter(nz, lo=lo, hi=lo * 3), fft_filter(nz, lo=hi / 3, hi=hi)
    x = t / d if up else 1 - t / d
    return (a * (1 - x) + b * x) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2


def pop(f0=900, f1=420, d=0.09):
    t = t_arr(d)
    f = f1 + (f0 - f1) * np.exp(-t / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.035)


def boing():
    d = 0.22
    t = t_arr(d)
    f = 480 + 1100 * (1 - np.exp(-t / 0.05))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * env(len(t), 0.002, 0.08)


def tap():
    d = 0.08
    t = t_arr(d)
    return (np.sin(2 * np.pi * 1150 * t) * 0.6 + np.sin(2 * np.pi * 620 * t) * 0.5) * env(len(t), 0.0005, 0.018) + 0.2 * fft_filter(noise(d), lo=2500) * env(len(t), 0.0003, 0.004)


def marker():
    d = 0.22
    t = t_arr(d)
    return fft_filter(noise(d), lo=2500, hi=9000) * np.sin(np.pi * t / d) ** 1.5 * (1 + 0.5 * np.sin(2 * np.pi * 38 * t))


def clock_tick(hi=True):
    d = 0.05
    t = t_arr(d)
    return (np.sin(2 * np.pi * (2300 if hi else 1700) * t) + 0.4 * fft_filter(noise(d), lo=3000)) * env(len(t), 0.0003, 0.007)


def cricket():
    out = np.zeros(int(SR * 0.6))
    for k in range(2):
        for j in range(3):
            d = 0.035
            t = t_arr(d)
            s = np.sin(2 * np.pi * 4600 * t) * np.sin(np.pi * t / d) ** 2
            i = int(SR * (k * 0.28 + j * 0.05))
            out[i : i + len(s)] += s
    return out


def sweep_shine():
    s = whoosh(0.6, up=True, lo=1500, hi=12000)
    t = t_arr(0.6)
    return s + 0.1 * sum(np.sin(2 * np.pi * f * t) for f in (2637, 3136, 3951)) / 3 * np.sin(np.pi * t / 0.6) ** 2


def chime():
    t = t_arr(1.2)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5) + 0.2 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.15) for f in (1318.5, 1975.5))
    return s / 2 * env(len(t), 0.003, 5)


def build_sfx(c):
    N = int(round(c["dur"] * SR))
    buf = np.zeros((N, 2))

    def place(sig, t, gain=1.0, pan=0.0):
        # 소리는 그림보다 1프레임 늦게 (sound.md)
        i = int(round((t + 1 / 30) * SR))
        if i >= N:
            return
        sig = sig[: N - i]
        buf[i : i + len(sig), 0] += sig * gain * np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
        buf[i : i + len(sig), 1] += sig * gain * np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)

    B = lambda k: k * P
    R = c["R"]
    if c["dur"] == 30.0:
        place(pop(1100, 600), B(3), 0.35)                    # 타이핑 점 등장
        place(whoosh(0.3, True, 600, 6000), B(6) - 0.1, 0.22)  # 스크롤
        place(marker(), B(14), 0.28, -0.2)                   # 형광펜 ×2
        place(marker(), B(15), 0.28, 0.2)
        place(pop(800, 500), B(16), 0.3)                     # 예시 줄
        # C4 입력: 백스페이스 2회(32분) + 타이핑(32분)
        place(key_click(True), B(21), 0.4)
        place(key_click(True), B(21.5), 0.4)
        for k in range(16):
            place(key_click(), B(22) + k * P / 4, 0.26, float(rng.uniform(-0.3, 0.3)))
        place(tap(), B(24) - 0.05, 0.45)                     # 전송 버튼
        place(whoosh(0.35, True, 500, 5000), B(24), 0.3)     # 전송 '슝'
        # C5 정적: 초침 틱(무음 그리드 유지) + 귀뚜라미
        for k, hi in ((27, True), (28, False), (29, True)):
            place(clock_tick(hi), B(k), 0.5)
        place(cricket(), B(29.6), 0.18, 0.4)
        place(pop(950, 520), R, 0.3)                         # 🙂 말풍선 (음악 슬램과 함께)
        place(boing(), R + 4 * P, 0.42)                      # 🙂 히트
        place(tap(), R + 7 * P, 0.5)                         # 상담사 연결 탭
        T7 = c["brand"]
        place(sweep_shine(), T7 - 0.08, 0.3)                 # 원형 전환
        place(chime(), T7 + P, 0.22)                         # 로고 차임
        place(pop(900, 480), T7 + 7 * P, 0.3)                # 상담사 말풍선
        for k in range(8):                                   # 0→60 카운트 틱(8분)
            place(clock_tick(k % 2 == 0), T7 + 7.5 * P + k * P / 4, 0.14)
        place(tap(), R + 24 * P, 0.4)                        # 무료 상담 신청 탭
    else:
        place(pop(1100, 600), B(3), 0.35)
        place(whoosh(0.3, True, 600, 6000), B(6) - 0.1, 0.22)
        place(marker(), B(8), 0.28, -0.2)
        place(marker(), B(8.5), 0.28, 0.2)
        place(pop(800, 500), B(9), 0.3)
        place(whoosh(0.35, True, 500, 5000), B(10) - 0.05, 0.3)  # 질문 전송
        place(clock_tick(True), B(13), 0.5)
        place(clock_tick(False), B(13) + 0.36, 0.5)
        place(pop(950, 520), R, 0.3)
        place(boing(), R + 2 * P, 0.42)
        place(tap(), R + 3.5 * P, 0.5)
        place(sweep_shine(), 8.5 - 0.08, 0.3)
        place(chime(), 8.5 + 0.5 * P, 0.22)
        place(pop(900, 480), 8.5 + 4 * P, 0.3)
        for k in range(8):
            place(clock_tick(k % 2 == 0), 8.5 + 4.5 * P + k * P / 4, 0.14)
    return buf


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
    sfx = build_sfx(c)
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
           "cuts": {k: round(v, 4) for k, v in c["cuts"].items()},
           "music_segments": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()} for s in c["music"]],
           "mix": {"integrated_lufs": i_lufs, "true_peak_dbtp": tp, "gain": round(float(gain), 4),
                   "max_gain_reduction_db": round(float(20 * np.log10(np.min(g))), 2)}}
    json.dump(rec, open(os.path.join(ROOT, "beats", f"cuts-{cut}.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
