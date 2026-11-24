// Renders the avatar PNG exports and the six-point publishing test sheet. Run: node src/avatar_check.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const dir = path.join(root, 'svg', 'avatar');
const png = path.join(root, 'avatar');
fs.mkdirSync(png, { recursive: true });
const svg = fs.readFileSync(path.join(dir, 'spinosaurus-avatar.svg'), 'utf8');
const sil = fs.readFileSync(path.join(dir, 'spinosaurus-silhouette.svg'), 'utf8');
const uri = s => 'data:image/svg+xml;base64,' + Buffer.from(s).toString('base64');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  const shot = async (html, file, w, h, scale = 1) => {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await p.setContent(html); await p.screenshot({ path: file }); await p.close();
  };
  for (const s of [1024, 800, 400, 320, 200])
    await shot(`<body style="margin:0"><img src="${uri(svg)}" width="${s}" height="${s}"></body>`, path.join(png, `spinosaurus-avatar-${s}.png`), s, s);
  const circ = (s, extra = '', bg = '#fff') => `<div style="width:${s}px;height:${s}px;border-radius:50%;overflow:hidden;background:${bg};${extra}"><img src="${uri(svg)}" width="${s}" height="${s}" style="display:block;${extra.includes('gray') ? 'filter:grayscale(1)' : ''}"></div>`;
  const cell = (t, inner, bg = '#fff', fg = '#222') => `<div style="background:${bg};color:${fg};padding:14px;display:flex;flex-direction:column;align-items:center;gap:10px;font:600 15px sans-serif">${inner}<div>${t}</div></div>`;
  const html = `<body style="margin:0;background:#ddd;display:grid;grid-template-columns:repeat(3,auto);gap:6px;width:max-content">
   ${cell('1  40 px', `<div style="display:flex;gap:12px;align-items:center">${circ(40)}${circ(98)}</div><div style="height:260px"></div>`)}
   ${cell('2  circle mask, guide ring = safe zone', `<div style="position:relative">${circ(400)}<div style="position:absolute;inset:40px;border:2px dashed #e0368a;border-radius:50%"></div></div>`)}
   ${cell('3  grayscale', circ(260, 'filter:gray'))}
   ${cell('4  light mode', circ(200), '#fff')}
   ${cell('5  dark mode', circ(200, '', '#0f0f0f'), '#0f0f0f', '#eee')}
   ${cell('6  silhouette (40 px and 260 px)', `<div style="display:flex;gap:12px;align-items:center"><img src="${uri(sil)}" width="40" style="border-radius:50%"><img src="${uri(sil)}" width="260" style="border-radius:50%"></div>`)}
  </body>`;
  await shot(html, path.join(png, 'publishing-test.png'), 1300, 760);
  await b.close();
})();
