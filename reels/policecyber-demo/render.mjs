// 렌더: demo.html을 seek(t)로 프레임마다 찍어 ffmpeg로 MP4를 만든다.
//   node render.mjs --draft        30fps, 모션 블러 없음
//   node render.mjs                30fps, 프레임당 서브프레임 4개 평균(셔터 180°)
import { createRequire } from "module";
import { spawn, execFileSync } from "child_process";
import fs from "fs";
import path from "path";
const { chromium } = createRequire(import.meta.url)("playwright");

const draft = process.argv.includes("--draft");
const SUB = draft ? 1 : 4, FPS = 30, SHUTTER = 0.5;
fs.mkdirSync("renders", { recursive: true });
const silent = "renders/_video.mp4", out = draft ? "renders/policecyber-demo-draft.mp4" : "renders/policecyber-demo.mp4";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto("file://" + path.resolve("demo.html"));
await page.evaluate(async () => { await document.fonts.ready; window.remeasure(); });
const { duration, cues } = await page.evaluate(() => ({ duration: window.VIDEO.duration, cues: window.CUES }));
fs.writeFileSync("renders/_cues.json", JSON.stringify(cues));

const vf = SUB > 1 ? ["-vf", `tmix=frames=${SUB},select='not(mod(n\\,${SUB}))',setpts=N/${FPS}/TB`] : [];
const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS * SUB), "-i", "-", ...vf,
  "-r", String(FPS), "-c:v", "libx264", "-preset", draft ? "veryfast" : "slow", "-crf", draft ? "20" : "16", "-pix_fmt", "yuv420p", silent], { stdio: ["pipe", "inherit", "inherit"] });

const N = Math.round(duration * FPS);
const t0 = Date.now();
for (let f = 0; f < N; f++) {
  for (let k = 0; k < SUB; k++) {
    const t = (f + (SUB > 1 ? (k / SUB) * SHUTTER : 0)) / FPS;
    await page.evaluate((t) => window.seek(t), t);
    const buf = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  }
  if (f % 60 === 0) process.stdout.write(`frame ${f}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();

// 오디오: 효과음 합성 + BGM(원곡 0s부터, 1.5s 첫 강박) 믹스 후 mux
execFileSync("python3", ["sfx.py", "renders/_cues.json", "renders/_audio.wav", String(duration)], { stdio: "inherit" });
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", silent, "-i", "renders/_audio.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], { stdio: "inherit" });
for (const f of [silent, "renders/_audio.wav", "renders/_cues.json"]) fs.rmSync(f, { force: true });
console.log("done", out);
