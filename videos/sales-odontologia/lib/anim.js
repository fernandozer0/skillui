// Shared helpers for the frame-by-frame reels (reel4+): easing, transforms,
// Apple-emoji swapping and film grain. Every page exposes render(t) and DUR.
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const clamp = (x, a = 0, c = 1) => Math.min(c, Math.max(a, x));
const prog = (t, s, d) => clamp((t - s) / d);
const lerp = (a, c, x) => a + (c - a) * x;
const eOut = x => 1 - Math.pow(1 - x, 3), eIn = x => x * x * x;
const eExpo = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eBack = x => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const spring = x => x <= 0 ? 0 : 1 - Math.exp(-6 * x) * Math.cos(11 * x);
function rng(seed) { return () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }

function tf(el, { o = 1, x = 0, y = 0, s = 1, r = 0, bl = 0 } = {}) {
  el.style.opacity = o;
  el.style.transform = `translate(${x}px,${y}px) scale(${s}) rotate(${r}deg)`;
  el.style.filter = bl > 0.2 ? `blur(${bl.toFixed(1)}px)` : 'none';
}
function vis(el, t, a, c) { const v = t >= a && t < c; el.style.display = v ? '' : 'none'; return v; }
function pop(el, t, s0, d = 0.4) { const p = prog(t, s0, d); tf(el, { o: clamp(p * 4), s: t < s0 ? 0.001 : lerp(0.3, 1, eBack(p)) }); }
function upIn(el, t, s0, d = 0.4, dist = 60) { const p = eOut(prog(t, s0, d)); tf(el, { o: p, y: lerp(dist, 0, p) }); }
function slam(el, t, s0, from = 1.8, d = 0.22) {
  if (t < s0) { el.style.opacity = 0; return; }
  const p = prog(t, s0, d); tf(el, { o: clamp(p * 3), s: lerp(from, 1, eOut(p)), bl: lerp(14, 0, p) });
}
function stamp(el, t, s0, rot = -8, d = 0.3) {
  if (t < s0) { el.style.opacity = 0; return; }
  const p = prog(t, s0, d); tf(el, { o: clamp(p * 4), s: lerp(2.2, 1, eBack(p)), r: lerp(rot * 3, rot, eOut(p)) });
}
// sum of decaying pulses at the given times (for camera punches / flashes)
function pulses(t, times, len, amt) { let k = 0; times.forEach(h => { const dt = t - h; if (dt >= 0 && dt < len) k += amt * (1 - dt / len); }); return k; }

/* Apple emoji: replace emoji characters (incl. ZWJ sequences) with the iOS images in emoji/ */
const EMOJI_RE = /\p{Extended_Pictographic}️?(?:‍\p{Extended_Pictographic}️?)*/gu;
const emojiFile = s => [...s].map(c => c.codePointAt(0).toString(16)).filter(h => h !== 'fe0f').join('-');
function emojify(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); const nodes = [];
  while (walker.nextNode()) { EMOJI_RE.lastIndex = 0; if (EMOJI_RE.test(walker.currentNode.nodeValue)) nodes.push(walker.currentNode); }
  nodes.forEach(n => {
    const span = document.createElement('span');
    span.innerHTML = n.nodeValue.replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(EMOJI_RE, m => `<img class="em" src="${window.EMOJI_DIR || "emoji"}/${emojiFile(m)}.png">`);
    n.replaceWith(...span.childNodes);
  });
}

function makeGrain(canvas, seed = 1, light = false) {
  const g = canvas.getContext('2d'), frames = [];
  for (let k = 0; k < 4; k++) {
    const img = g.createImageData(canvas.width, canvas.height), r = rng(seed + k);
    for (let i = 0; i < img.data.length; i += 4) { const v = light ? 150 + r() * 105 : r() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    frames.push(img);
  }
  return t => g.putImageData(frames[Math.floor(t * 24) % 4], 0, 0);
}

function fitText(el, max) {
  let fs = parseFloat(getComputedStyle(el).fontSize);
  while (el.getBoundingClientRect().width > max && fs > 20) { fs -= 2; el.style.fontSize = fs + 'px'; }
}

const WA_PATH = 'M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 6.9L3 29l6.5-2c1.9 1 4.1 1.6 6.5 1.6 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.3c-2.1 0-4.1-.6-5.8-1.7l-.4-.3-3.9 1.2 1.2-3.7-.3-.4c-1.2-1.7-1.9-3.8-1.9-5.9C4.9 9.8 9.9 5 16 5s11.1 4.8 11.1 10.8S22.1 26.3 16 26.3zm6.1-8c-.3-.2-2-1-2.3-1.1-.3-.1-.5-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.3-.7.1-.3-.2-1.4-.5-2.7-1.7-1-.9-1.7-2-1.9-2.3-.2-.3 0-.5.1-.7l.5-.6c.2-.2.2-.3.3-.6.1-.2 0-.4 0-.6l-1.1-2.6c-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.4c.2.2 2.4 3.6 5.8 5 .8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 2-.8 2.2-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.6-.3z';
const TOOTH_PATH = 'M34 86 C14 62 14 22 42 16 C58 13 62 26 75 26 C88 26 92 13 108 16 C136 22 136 62 116 86';

/* markup builders for the shared brand pieces (styles in lib/common.css) */
const GOLD_DEFS = '<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="gg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d88f"/><stop offset="1" stop-color="#b7882e"/></linearGradient></defs></svg>';
const toothSVG = () => `<svg viewBox="0 0 150 100"><path fill="none" stroke="url(#gg)" stroke-width="13" stroke-linecap="round" d="${TOOTH_PATH}"/></svg>`;
const brandHTML = () => `<div id="brand">${toothSVG()}SALES ODONTOLOGIA</div>`;
const badgeHTML = () => `<div class="badge">${toothSVG()}<div class="n">SALES</div><div class="s">ODONTOLOGIA</div></div>`;
const waHTML = () => `<div class="wa"><div class="ic"><svg width="62" height="62" viewBox="0 0 32 32"><path fill="#25d366" d="${WA_PATH}"/></svg></div><div><div class="t1">Chame no WhatsApp</div><div class="t2">(41) 98414-4299</div></div></div>`;
// heartbeat pulse for the WhatsApp pill once it has landed
function waBeat(el, bt, from) { if (bt > from) { const k = ((bt - from) % 2) / 2; el.style.transform = `scale(${1 + 0.05 * Math.max(0, Math.sin(clamp(k / 0.18) * Math.PI))})`; } }
