// Generates scenes/scene-N/{lottie.json,controls.json} and subsets the Korean fonts into each scene folder.
import { mkdirSync, writeFileSync, existsSync, copyFileSync, rmSync, readdirSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scenes, IMG_W, IMG_H } from './scenes.mjs';
import { FR } from './lib.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const FONT_URL = 'https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/SubsetOTF/KR/';
const FONT_FILES = ['NotoSerifKR-Regular.otf', 'NotoSerifKR-Bold.otf'];

const comps = scenes.map(f => f());
const total = comps.reduce((n, c) => n + c.op, 0);
if (total !== 60 * FR) throw new Error(`scenes add up to ${total} frames, expected ${60 * FR}`);

// every glyph any scene uses, plus ASCII so slot edits with digits/punctuation still render
const used = new Set(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~·—');
const walk = v => { if (typeof v === 'string') for (const ch of v) used.add(ch); else if (v && typeof v === 'object') Object.values(v).forEach(walk); };
comps.forEach(c => c.layers.filter(l => l.ty === 5).forEach(l => walk(l.t.d)));
const glyphs = [...used].join('');

mkdirSync(join(root, 'fonts-src'), { recursive: true });
for (const f of FONT_FILES) {
  const src = join(root, 'fonts-src', f);
  if (!existsSync(src)) execFileSync('curl', ['-sSfL', '-o', src, FONT_URL + f], { stdio: 'inherit' });
  execFileSync('pyftsubset', [src, `--text=${glyphs}`, `--output-file=${join(root, 'fonts-src', 'subset-' + f)}`, '--name-IDs=*', '--layout-features=*', '--notdef-outline'], { stdio: 'inherit' });
}

// stills: images/<name>.(jpg|png|webp) -> cache/<name>.jpg, cover-cropped to IMG_W x IMG_H.
// A missing still becomes a flat placeholder so the cut can be previewed; the build says so loudly.
mkdirSync(join(root, 'cache'), { recursive: true });
const missing = [];
function stillFor(file) {
  const base = file.replace(/\.jpg$/, ''), out = join(root, 'cache', file);
  const src = ['.jpg', '.jpeg', '.png', '.webp'].map(e => join(root, 'images', base + e)).find(existsSync);
  if (!src) {
    missing.push(file);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', `gradients=s=${IMG_W}x${IMG_H}:c0=0x1b1410:c1=0x6b4a2a:x0=0:y0=0:x1=${IMG_W}:y1=${IMG_H}:seed=${base.charCodeAt(1)}`, '-frames:v', '1', '-q:v', '3', out]);
  } else if (!existsSync(out) || statSync(out).mtimeMs < statSync(src).mtimeMs) {
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-vf', `scale=${IMG_W}:${IMG_H}:force_original_aspect_ratio=increase:flags=lanczos,crop=${IMG_W}:${IMG_H}`, '-frames:v', '1', '-q:v', '2', out]);
  }
  return out;
}

for (const d of readdirSync(join(root, 'scenes'))) rmSync(join(root, 'scenes', d), { recursive: true, force: true });
comps.forEach((c, i) => {
  const dir = join(root, 'scenes', `scene-${i + 1}`);
  mkdirSync(dir, { recursive: true });
  for (const a of c.assets) copyFileSync(stillFor(a.p), join(dir, a.p));
  writeFileSync(join(dir, 'lottie.json'), JSON.stringify(c));
  const labels = { bgColor: '배경색', verse: '말씀', verse1: '말씀 1', verse2: '말씀 2', question: '질문', pledge: '다짐 문구', groupName: '청년회 이름' };
  writeFileSync(join(dir, 'controls.json'), JSON.stringify({ controls: Object.keys(c.slots).map(sid => ({ sid, label: labels[sid] || sid.replace(/^verse([ab]?)$/, (_, g) => `말씀${g ? ' ' + g.toUpperCase() : ''}`) })) }, null, 2));
  for (const f of FONT_FILES) copyFileSync(join(root, 'fonts-src', 'subset-' + f), join(dir, f));
  console.log(`scene-${i + 1}  ${String(c.op).padStart(3)}f  ${(c.op / FR).toFixed(1)}s  ${c.nm}`);
});
if (missing.length) console.log(`PLACEHOLDER stills (not generated yet): ${[...new Set(missing)].join(', ')}`);
console.log(`total ${total} frames = ${total / FR}s, ${glyphs.length} glyphs`);
