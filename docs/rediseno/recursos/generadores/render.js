const { chromium } = require('playwright');
(async () => {
  const [file, outdir, scale] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: Number(scale || 0.5) });
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const ids = await p.$$eval('.board', els => els.map(e => [e.id, e.offsetHeight]));
  for (const [id, h] of ids) { await (await p.$('#' + id)).screenshot({ path: `${outdir}/${id}.png` }); }
  console.log(JSON.stringify(ids));
  await b.close();
})();
