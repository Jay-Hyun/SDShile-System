#!/usr/bin/env python3
"""렌더된 MP4 의 오디오를 같은 믹스(bgm+sfx 스템의 합)의 320 kbps AAC 로 바꿔 끼운다. 영상 스트림은 그대로 복사(-c:v copy).

Usage: python3 tools/remux_audio.py [30|15]      (생략하면 둘 다; npm run render 뒤에 돈다)
이유: 렌더러의 AAC(≈194 kbps, 옵션 없음)는 밝은 구간에서 10 kHz 이상 비율을 최대 −2 dB 깎는다(스템은 원곡과 같다).
320 kbps 로 다시 인코딩하면 −0.2 dB 안이다. 비트레이트마다 트루피크 오버슈트가 들쭉날쭉하다(이 믹스: 192k −0.4, 256k +0.4,
320k −2.1 dBTP, 무손실 −2.2) — 그래서 320k 로 고정한다. 바꾸면 반드시 ebur128 로 TP ≤ −1 dBTP 를 다시 잰다. 믹스·길이·라우드니스는 그대로다.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pcm(p):
    w = wave.open(p)
    return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, w.getnchannels()).astype(np.int32)


def remux(cut):
    suf = "-15s" if cut == 15 else ""
    mp4 = os.path.join(ROOT, "renders", f"ask-ai-{cut}s.mp4")
    mix = np.clip(pcm(os.path.join(ROOT, f"assets/audio/bgm{suf}.wav")) + pcm(os.path.join(ROOT, f"assets/audio/sfx{suf}.wav")), -32768, 32767).astype("<i2")
    with tempfile.TemporaryDirectory() as td:
        wp = os.path.join(td, "mix.wav")
        w = wave.open(wp, "wb")
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(mix.tobytes())
        w.close()
        out = os.path.join(td, "out.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-i", wp, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", str(len(mix) / 48000), "-movflags", "+faststart", out], check=True)
        os.replace(out, mp4)
    print(f"remuxed {mp4}")


if __name__ == "__main__":
    for c in ([int(sys.argv[1])] if len(sys.argv) > 1 else [30, 15]):
        remux(c)
