// Exports every banner/vertical*.html to print files (90 x 120 cm).
// Setup once:  npm i playwright@1.49.1 && npx playwright install chromium
// Run:         node exportar.js            (needs python3 + Pillow for the PDFs/previews)
// The page is served from a fake origin so fonts load reliably; 1 CSS px = 1 mm, rendered at 8x (≈203 dpi).
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');
const ROOT=__dirname,OUT=path.resolve(ROOT,'..','vertical_90x120cm'),SCALE=8;
const MIME={'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.png':'image/png','.ttf':'font/ttf'};
(async()=>{
  fs.mkdirSync(path.join(OUT,'previews'),{recursive:true});
  const files=fs.readdirSync(path.join(ROOT,'banner')).filter(f=>/^vertical\d.*\.html$/.test(f)).sort();
  const b=await chromium.launch();
  for(const f of files){
    const p=await b.newPage({viewport:{width:900,height:1200},deviceScaleFactor:SCALE});
    await p.route('http://banner.local/**',r=>{const fp=path.join(ROOT,decodeURIComponent(new URL(r.request().url()).pathname));
      if(!fs.existsSync(fp))return r.fulfill({status:404,body:''});r.fulfill({status:200,contentType:MIME[path.extname(fp)]||'application/octet-stream',body:fs.readFileSync(fp)})});
    await p.goto('http://banner.local/banner/'+f);await p.evaluate(()=>window.fontsReady);await p.waitForTimeout(500);
    const name=f.replace('.html','');
    await p.screenshot({path:path.join(OUT,`${name}_90x120cm.png`)});await p.close();console.log('rendered',name);
  }
  await b.close();
  execFileSync('python3',[path.join(ROOT,'exportar_pdf.py'),OUT],{stdio:'inherit'});
})();
