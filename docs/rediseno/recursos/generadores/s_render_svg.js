// Rasteriza un SVG (o una hoja de stickers) con fondo transparente.
// Uso: node s_render_svg.js <assets_dir> <svg_file> <out_png> <scale>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [dir, svgFile, out, scale] = process.argv.slice(2);
  const fonts = fs.readFileSync(path.join(dir, 'fonts.css'), 'utf8');
  const svg = fs.readFileSync(path.join(dir, svgFile), 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8"><base href="file://${dir}/"><style>${fonts} body{margin:0;background:transparent} svg{display:block}</style></head><body>${svg}</body></html>`;
  const tmp = path.join(dir, '_render_tmp.html');
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1200 }, deviceScaleFactor: Number(scale || 2) });
  await p.goto('file://' + tmp, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await (await p.$('svg')).screenshot({ path: out, omitBackground: true });
  await b.close();
  fs.unlinkSync(tmp);
  console.log('rendered', out);
})();
