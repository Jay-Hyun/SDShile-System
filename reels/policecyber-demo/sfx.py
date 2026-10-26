"""효과음 합성 + BGM 믹스.  python3 sfx.py cues.json out.wav duration"""
import json, subprocess, sys
import numpy as np

SR = 44100
cues, out, dur = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
n = int(dur * SR)
fx = np.zeros(n)
rng = np.random.default_rng(7)
tt = lambda d: np.arange(int(d * SR)) / SR

def add(t, x, g):
    i = int(t * SR)
    x = x[: max(0, n - i)]
    fx[i : i + len(x)] += x * g

def tick():  # 키보드 틱: 짧은 노이즈 버스트
    t = tt(0.025); return rng.standard_normal(len(t)) * np.exp(-t * 260)

def click():
    t = tt(0.06); return (np.sin(2 * np.pi * 1900 * t) * 0.6 + rng.standard_normal(len(t)) * 0.4) * np.exp(-t * 120)

def noise_sweep(d, up=True):  # 휙: 밴드 이동 노이즈
    t = tt(d); x = rng.standard_normal(len(t))
    k = np.convolve(x, np.ones(6) / 6, "same")
    env = np.sin(np.pi * t / d) ** 2
    return (k if up else x * 0.5) * env

def hit():  # 낮은 타격 + 서브
    t = tt(1.2); f = 55 * np.exp(-t * 2) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) + rng.standard_normal(len(t)) * np.exp(-t * 40) * 0.3

def rise():  # 짧은 상승음 (끝이 블루 와이프에 닿음)
    t = tt(0.85); f = 300 + 1500 * (t / 0.85) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + noise_sweep(0.85) * 0.6) * (t / 0.85) ** 1.5

def mark():  # 형광펜 긋는 소리
    t = tt(0.3); x = rng.standard_normal(len(t)); x = np.convolve(x, np.ones(3) / 3, "same")
    return x * np.sin(np.pi * t / 0.3) ** 1.5

for c in cues:
    k, t = c["kind"], c["t"]
    if k == "tick": add(t, tick(), 0.09)
    elif k == "type":
        for j in range(6): add(t + j * 0.045, tick(), 0.1)
    elif k == "click": add(t, click(), 0.22)
    elif k == "swish": add(t - 0.2, noise_sweep(0.45), 0.16)
    elif k == "whoosh": add(t, noise_sweep(0.5), 0.3)
    elif k == "hit": add(t, hit(), 0.55)
    elif k == "rise": add(t, rise(), 0.22)
    elif k == "mark": add(t, mark(), 0.08)

fxpath = out + ".fx.wav"
pcm = (np.clip(fx, -1, 1) * 32767).astype(np.int16)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", fxpath], input=pcm.tobytes(), check=True)
# BGM은 1.3s 첫 강박에 배치. 효과음은 BGM 아래 살짝
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/bgm.mp3", "-i", fxpath, "-filter_complex",
                f"[0]adelay=1300|1300,volume=0.9[m];[1]aformat=channel_layouts=stereo[f];[m][f]amix=inputs=2:normalize=0,atrim=0:{dur},loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100,alimiter=limit=0.74:level=false",
                "-ar", "44100", out], check=True)
import os; os.remove(fxpath)
