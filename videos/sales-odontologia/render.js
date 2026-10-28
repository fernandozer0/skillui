// Renders reel.html frame-by-frame into an MP4 (silent) via ffmpeg.
// Usage: node render.js [out.mp4] | node render.js --stills t1,t2,...
// Set PAGE=reel2.html to render another composition.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(__dirname, process.env.PAGE || 'reel.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const stage = await page.$('#stage');

  if (process.argv[2] === '--stills') {
    for (const t of process.argv[3].split(',').map(Number)) {
      await page.evaluate(t => render(t), t);
      await stage.screenshot({ path: `stills/${process.env.PAGE ? path.basename(process.env.PAGE, '.html') + '_' : ''}t${t.toFixed(2)}.png` });
    }
    await browser.close();
    return;
  }

  const out = process.argv[2] || 'reel_silent.mp4';
  const dur = await page.evaluate(() => DUR);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await stage.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stderr.write(`frame ${i}/${n}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
