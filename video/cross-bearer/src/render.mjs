// Renders the scenes with Skia Skottie (canvaskit-wasm), the same engine as the official player.
//   node src/render.mjs still <scene> <frame> [out.png]
//   node src/render.mjs sheet                      -> out/sheet-<scene>.png (first / mid / last)
//   node src/render.mjs video                      -> out/video-silent.mp4 (+ out/final.mp4 when out/music.wav exists)
import { readFileSync, readdirSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { spawn, spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
const ckDir = dirname(require.resolve('canvaskit-wasm/bin/full/canvaskit.js'));
const CK = await require('canvaskit-wasm/bin/full/canvaskit.js')({ locateFile: f => join(ckDir, f) });

const sceneDirs = readdirSync(join(root, 'scenes')).filter(d => /^scene-\d+$/.test(d))
  .sort((a, b) => +a.split('-')[1] - +b.split('-')[1]);

function load(scene) {
  const dir = join(root, 'scenes', scene);
  const json = readFileSync(join(dir, 'lottie.json'), 'utf8');
  const assets = {};
  for (const f of readdirSync(dir)) if (/\.(otf|ttf|ttc|png|jpg|svg)$/i.test(f)) assets[f] = readFileSync(join(dir, f)).buffer;
  const anim = CK.MakeManagedAnimation(json, assets);
  if (!anim) throw new Error(`Skottie failed to load ${scene}`);
  return { anim, meta: JSON.parse(json) };
}

function draw(surface, anim, frame, w, h) {
  const canvas = surface.getCanvas();
  canvas.clear(CK.BLACK);
  anim.seekFrame(frame);
  anim.render(canvas, CK.LTRBRect(0, 0, w, h));
  surface.flush();
}

const [mode, a1, a2, a3] = process.argv.slice(2);
mkdirSync(join(root, 'out'), { recursive: true });

if (mode === 'still' || mode === 'sheet') {
  const jobs = mode === 'still'
    ? [[a1, [+a2], a3 || join(root, 'out', `${a1}-${a2}.png`)]]
    : sceneDirs.filter(s => !a1 || s === a1).map(s => {
      const op = JSON.parse(readFileSync(join(root, 'scenes', s, 'lottie.json'), 'utf8')).op;
      const frames = a2 ? a2.split(',').map(Number) : [0, Math.round(op * 0.3), Math.round(op * 0.6), op - 1];
      return [s, frames, join(root, 'out', `sheet-${s}.png`)];
    });
  for (const [scene, frames, out] of jobs) {
    const { anim } = load(scene);
    const cols = Math.min(frames.length, 2), rows = Math.ceil(frames.length / cols);
    const cw = frames.length === 1 ? 1920 : 960, ch = cw * 9 / 16;
    const sheet = CK.MakeSurface(cw * cols, ch * rows), cell = CK.MakeSurface(cw, ch);
    frames.forEach((f, i) => {
      draw(cell, anim, f, cw, ch);
      const img = cell.makeImageSnapshot();
      sheet.getCanvas().drawImage(img, (i % cols) * cw, Math.floor(i / cols) * ch, null);
      img.delete();
    });
    writeFileSync(out, sheet.makeImageSnapshot().encodeToBytes());
    console.log(out, frames.join(','));
  }
} else if (mode === 'video') {
  const silent = join(root, 'out', 'video-silent.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1920x1080', '-r', '30',
    '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const surface = CK.MakeSurface(1920, 1080);
  const info = { width: 1920, height: 1080, colorType: CK.ColorType.RGBA_8888, alphaType: CK.AlphaType.Unpremul, colorSpace: CK.ColorSpace.SRGB };
  let total = 0;
  for (const scene of sceneDirs) {
    const { anim, meta } = load(scene);
    for (let f = 0; f < meta.op; f++) {
      draw(surface, anim, f, 1920, 1080);
      const img = surface.makeImageSnapshot();
      const px = img.readPixels(0, 0, info);
      img.delete();
      if (!ff.stdin.write(Buffer.from(px.buffer, px.byteOffset, px.byteLength))) await new Promise(r => ff.stdin.once('drain', r));
      total++;
    }
    anim.delete();
    console.log(`${scene}: ${meta.op} frames (running total ${total})`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log(silent, total, 'frames');
  const wav = join(root, 'out', 'music.wav');
  if (existsSync(wav)) {
    const final = join(root, 'out', 'final.mp4');
    spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
      '-shortest', '-movflags', '+faststart', final], { stdio: 'inherit' });
    console.log(final);
  }
} else {
  console.error('usage: render.mjs still <scene> <frame> [out] | sheet [scene] [f1,f2,..] | video');
  process.exit(1);
}
