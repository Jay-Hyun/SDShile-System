import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
import path from 'path';
const times = process.argv.slice(3).map(Number), out = process.argv[2];
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + path.resolve('demo.html')); await p.evaluate(() => document.fonts.ready);
for (const t of times) { await p.evaluate(t => window.seek(t), t); await p.screenshot({ path: `${out}/f_${t.toFixed(2)}.png` }); }
await b.close();
