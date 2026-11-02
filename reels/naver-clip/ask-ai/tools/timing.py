"""lib/cue.js 의 큐 표를 파이썬에서 읽는다 (단일 출처). Node 로 평가해 JSON 으로 받는다.

    from timing import cue
    c = cue(30)   # {"R": 14.3965, "BR": 18.2356, "WIN": 17.6333, "C9": 22.0747, ...}
함수 값(EB)은 k 마디 뒤 시각을 파이썬 쪽에서 R + k·BAR 로 다시 만든다.
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_JS = """
import('./lib/cue.js').then(() => {
  const out = {};
  for (const n of [30, 15]) {
    const c = globalThis.HFCUE(n); const o = {};
    for (const k in c) if (typeof c[k] === 'number') o[k] = c[k];
    out[n] = o;
  }
  console.log(JSON.stringify(out));
});
"""
_cache = None


def cue(cut):
    global _cache
    if _cache is None:
        r = subprocess.run(["node", "-e", _JS], cwd=ROOT, capture_output=True, text=True, check=True)
        _cache = json.loads(r.stdout)
    c = dict(_cache[str(cut)])
    c["EB"] = lambda k: c["R"] + k * c["BAR"]
    return c


if __name__ == "__main__":
    for n in (30, 15):
        c = cue(n)
        print(n, {k: round(v, 4) for k, v in c.items() if not callable(v)})
