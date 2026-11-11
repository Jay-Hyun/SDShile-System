// Generates scenes/scene-N/{lottie.json,controls.json} and subsets the Korean fonts into each scene folder.
import { mkdirSync, writeFileSync, existsSync, copyFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scenes } from './scenes.mjs';
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

comps.forEach((c, i) => {
  const dir = join(root, 'scenes', `scene-${i + 1}`);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'lottie.json'), JSON.stringify(c));
  const labels = { bgColor: '배경색', verse: '말씀', verse1: '말씀 1', verse2: '말씀 2', question: '질문', pledge: '다짐 문구', groupName: '청년회 이름' };
  writeFileSync(join(dir, 'controls.json'), JSON.stringify({ controls: Object.keys(c.slots).map(sid => ({ sid, label: labels[sid] || sid })) }, null, 2));
  for (const f of FONT_FILES) copyFileSync(join(root, 'fonts-src', 'subset-' + f), join(dir, f));
  console.log(`scene-${i + 1}  ${String(c.op).padStart(3)}f  ${(c.op / FR).toFixed(1)}s  ${c.nm}`);
});
console.log(`total ${total} frames = ${total / FR}s, ${glyphs.length} glyphs`);
