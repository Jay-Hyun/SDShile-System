#!/usr/bin/env python3
"""「AI에게 물었다」 오디오: 제공 BGM 편집(끊김 없음) + 효과음 2개(질문 전송·[상담사 연결] 누름) + 마스터.

Usage: python3 tools/make_audio.py [--cut 15]
  assets/music/source.mp3 (grand_project, Pixabay 505611) 를 잘라 붙인다. 합성 음악은 없다.
  → assets/audio/bgm.wav, sfx.wav (30s) / bgm-15s.wav, sfx-15s.wav (15s)
  두 스템에 같은 게인·리미터를 걸어 합이 −15 LUFS(±0.3), 트루피크 ≤ −1 dBTP.
  시각은 lib/cue.js 가 단일 출처(tools/timing.py 로 읽는다). 챕터·컷·효과음 표는 beats/cuts-30.json / cuts-15.json 에도 저장.

음악 편집 v6 — 곡 그대로, 무음·페이드·필터·덕킹·피치 변화 없음 (P = 1박 = 60/125.03 s, 소스 다운비트 1.007 + 4P·k):
  30s  A  src 1.007→   v 0.000–10.557 (22P)   정수 박자 R 에서 B 로 이음 (반 마디 짧은 마디). R = B 의 다운비트(🙂 책임 넘김)
       B  src 12.524→  v 10.557–25.914 (32P)  14.396 = src 16.363 B섹션 크래시 = 오프닝 윈도우 중간점(상담사 답 ①), 18.236/22.075 = 답 ②/근거
       C  src 29.800→  v 25.914–30.000        B→C 는 마디선끼리(원곡 27.881→29.8, 1마디 건너뜀). 27.833 = src 31.719 마지막 크래시, 29.65–30.0 엔딩 페이드 0.35 s
  15s  A  src 1.007→   v 0.000–6.718 (14P)
       B  src 14.443→  v 6.718–10.557 (8P)    6.718 = B 의 다운비트, 8.638 = src 16.363 크래시
       C  src 29.800→  v 10.557–15.000        12.477 = src 31.719 마지막 크래시, 14.6–15.0 엔딩 페이드 0.4 s
  이음새는 6 ms 등전력 크로스페이드(겹치는 구간에서 앞은 cos, 뒤는 sin). 뒤 구간은 다운비트 6 ms 앞부터 깔아 다운비트가 온전한 게인으로 온다.
  R 이 정수 박자라 A·B·C 의 박 그리드가 하나로 이어진다.
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import cue  # noqa: E402

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


# ------------------------------------------------------------------ 큐 (lib/cue.js 와 같은 값)
# 챕터 = 다운비트(1마디 BAR). A 구간 다운비트 = k·BAR, B·C 구간 = R + k·BAR (R = 첫 구간의 끝 = 두 번째 구간의 다운비트).
# cuts = 실제 화면이 갈리는 지점: 하드컷(30s C9, 15s C6) + 시그니처 오프닝 윈도우의 중간점(가장 빠른 순간 = 크래시).
def cues(cut):
    x = cue(cut)
    BAR, R, WIN, CS = x["BAR"], x["R"], x["WIN"], x["CS"]
    if cut == 30:
        chapters = {"hook": 0.0, "send": x["C2"], "lead": x["C2b"], "key": x["C3"], "hand": x["HAND"],
                    "S1": x["BR"], "S2": x["S2"], "S3": x["S3"], "S4": x["S4"], "end": 30.0}
        cuts = {"open_mid": WIN + 0.6}
        music = [
            {"v0": 0.0, "v1": R, "src": DB0},
            {"v0": R, "v1": CS, "src": src_downbeat(12.524)},
            {"v0": CS, "v1": 30.0, "src": src_downbeat(29.8), "fade": 0.35},
        ]
    else:
        chapters = {"hook": 0.0, "send": x["C2"], "hand": x["HAND"], "S1": x["BR"], "C6": x["C6"], "end": 15.0}
        cuts = {"open_mid": WIN + 0.6, "C6": x["C6"]}
        music = [
            {"v0": 0.0, "v1": R, "src": DB0},
            {"v0": R, "v1": CS, "src": src_downbeat(14.443)},
            {"v0": CS, "v1": 15.0, "src": src_downbeat(29.8), "fade": 0.4},
        ]
    return {"dur": float(x["END"]), "R": R, "brand": x["BR"], "win": WIN, "send": x["SEND"], "press": x["PRESS"],
            "chapters": chapters, "cuts": cuts, "music": music}


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
XF = 0.006  # 이음새 크로스페이드 6 ms (등전력)


def build_music(c, src):
    N = int(round(c["dur"] * SR))
    out = np.zeros((N, 2))
    xf = int(XF * SR)
    th = np.linspace(0, np.pi / 2, xf)
    g_in, g_out = np.sin(th)[:, None], np.cos(th)[:, None]
    segs = c["music"]
    for k, seg in enumerate(segs):
        i0, i1 = int(round(seg["v0"] * SR)), int(round(seg["v1"] * SR))
        s0 = int(round(seg["src"] * SR))
        pre = xf if k > 0 else 0  # 뒤 구간은 다운비트 6 ms 앞부터 깔아 앞 구간의 마지막 6 ms 와 겹친다
        piece = src[s0 - pre : s0 + (i1 - i0)].copy()
        if k == 0:
            piece[:xf] *= np.linspace(0, 1, xf)[:, None]  # 곡 첫 소리의 클릭 방지
        else:
            piece[:xf] *= g_in
        if k < len(segs) - 1:
            piece[-xf:] *= g_out
        elif seg.get("fade"):
            nf = int(seg["fade"] * SR)
            piece[-nf:] *= (np.linspace(1, 0, nf) ** 1.5)[:, None]  # 엔딩 페이드만 허용
        start = i0 - pre
        end = min(N, start + len(piece))
        out[start:end] += piece[: end - start]
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

    place_rel(c["send"], "질문 전송 탭")  # 보내기 누름 (입력 시트가 접히기 직전)
    place_rel(c["press"], "[상담사 연결] 누름 탭")
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
    rec = {"cut": cut, "bpm": BEATS["bpm"], "beat_period": P, "R": round(c["R"], 4), "brand": round(c["brand"], 4),
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
