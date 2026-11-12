// Renderiza: mockups 3D (PNG), fichas tecnicas (PDF+PNG), PDFs vetoriais das artes e o comparativo.
// Uso: node render.js   (requer playwright: npm i playwright@1.49.1)
const fs = require('fs'), path = require('path');
const {chromium} = require('playwright');
const J = JSON.parse(fs.readFileSync(path.join(__dirname, 'jobs.json'), 'utf8'));
const only = process.argv[2]; // opcional: mockups | fichas | pdf | comparativo
(async () => {
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  if (!only || only === 'mockups') {
    const p = await b.newPage({viewport: {width: 900, height: 1000}, colorScheme: 'light', deviceScaleFactor: 1.5});
    for (const m of J.mockups) {
      await p.goto('file://' + J.viewer + `?shot&model=${m.id}&view=${m.view}`);
      await p.waitForFunction(() => window.__ready, null, {timeout: 90000});
      await p.waitForTimeout(600);
      await p.screenshot({path: m.out, clip: {x: 100, y: 40, width: 700, height: 900}});
      console.log('mockup', path.basename(m.out));
    }
    await p.close();
  }
  if (!only || only === 'fichas' || only === 'comparativo') {
    require('child_process').execFileSync('python3', [path.join(__dirname, 'ficha.py')], {stdio: 'inherit'});
  }
  const wrap = (svgFile, wmm, hmm, unit) => {
    const svg = fs.readFileSync(svgFile, 'utf8').replace(/<\?xml[^>]*\?>/, '');
    const hp = svgFile.replace(/\.svg$/, '.html');
    fs.writeFileSync(hp, `<!doctype html><html><head><style>@page{size:${wmm}${unit} ${hmm}${unit};margin:0}html,body{margin:0;padding:0;background:#fff}
      svg{display:block;width:${wmm}${unit};height:${hmm}${unit}}</style></head><body>${svg}</body></html>`);
    return hp;
  };
  if (!only || only === 'fichas') {
    const p = await b.newPage({viewport: {width: 1588, height: 1123}, deviceScaleFactor: 1.4});
    for (const f of J.fichas) {
      await p.goto('file://' + wrap(f.svg, 420, 297, 'mm')); await p.waitForLoadState('load'); await p.waitForTimeout(300);
      await p.pdf({path: f.pdf, width: '420mm', height: '297mm', printBackground: true, pageRanges: '1'});
      await p.screenshot({path: f.png});
      console.log('ficha', path.basename(f.pdf));
    }
    await p.close();
  }
  if (!only || only === 'pdf') {
    const p = await b.newPage();
    for (const j of J.pdf) {
      const svg = fs.readFileSync(j.svg, 'utf8').replace(/<\?xml[^>]*\?>/, '');
      await p.setContent(`<!doctype html><html><head><style>@page{size:${j.w}mm ${j.h}mm;margin:0}html,body{margin:0;padding:0}
        svg{display:block;width:${j.w}mm;height:${j.h}mm}</style></head><body>${svg}</body></html>`, {waitUntil: 'load'});
      await p.pdf({path: j.pdf, width: `${j.w}mm`, height: `${j.h}mm`, printBackground: true, pageRanges: '1'});
    }
    console.log('pdfs', J.pdf.length);
    await p.close();
  }
  if (!only || only === 'comparativo') {
    const dim = JSON.parse(fs.readFileSync(path.join(__dirname, '_build', 'comparativo.json'), 'utf8'));
    const p = await b.newPage({viewport: {width: dim.w, height: dim.h}, deviceScaleFactor: 2});
    await p.goto('file://' + wrap(path.join(__dirname, '_build', 'comparativo.svg'), dim.w, dim.h, 'px')); await p.waitForLoadState('load');
    await p.screenshot({path: path.join(J.out, 'comparativo_modelos.png')});
    console.log('comparativo ok');
    await p.close();
  }
  await b.close();
})();
