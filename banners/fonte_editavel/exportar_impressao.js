// Print files for the print shop: vector PDF, 90 x 120 cm, CMYK.
// Setup once:  npm i playwright@1.49.1 && npx playwright install chromium   (+ Ghostscript and python3 + Pillow)
// Run:         node exportar_impressao.js
//
// 1. Chromium prints each banner to a PDF. Text, logos and drawings stay vector (sharp at any size).
// 2. Photos are enlarged with Lanczos before printing, so each one reaches at least ~150 dpi on the
//    banner and the print shop's RIP does not enlarge them with blocky pixels. This smooths them,
//    it cannot add detail the source files do not have.
// 3. Ghostscript scales the page to exactly 900 x 1200 mm and converts every color to CMYK
//    (Ghostscript's CMYK profile), keeping images at full resolution.
const {chromium}=require('playwright'),fs=require('fs'),os=require('os'),path=require('path'),{execFileSync}=require('child_process');
const ROOT=__dirname,OUT=path.resolve(ROOT,'..','vertical_90x120cm','impressao_CMYK');
const W_MM=900,H_MM=1200,PT=72/25.4,Z=4; // page drawn Z times larger: Chromium rasterizes shadows/filters at 300 dpi of the page, so Z=4 gives them ~300 dpi on the banner
const MIME={'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.ttf':'font/ttf'};
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'banner-print-'));
  // enlarged copies of the photos (served in place of banner/imagens/*)
  const big=path.join(tmp,'imagens');fs.mkdirSync(big);
  execFileSync('python3',['-c',`
import sys,os
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]
for f in sorted(os.listdir(src)):
    im=Image.open(os.path.join(src,f)); k=min(5.0,max(1.0,5400/im.width))
    if k>1: im=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS)
    if f.lower().endswith(('.jpg','.jpeg')): im.convert('RGB').save(os.path.join(dst,f),quality=95,subsampling=0)
    else: im.save(os.path.join(dst,f),optimize=False,compress_level=3)
    print('  imagem',f,im.size)
`,path.join(ROOT,'banner','imagens'),big],{stdio:'inherit'});
  const files=fs.readdirSync(path.join(ROOT,'banner')).filter(f=>/^(vertical\d.*|modelo.*)\.html$/.test(f)).sort();
  const b=await chromium.launch();
  for(const f of files){
    const p=await b.newPage({viewport:{width:900,height:1200}});
    await p.route('http://banner.local/**',r=>{const rel=decodeURIComponent(new URL(r.request().url()).pathname);
      let fp=path.join(ROOT,rel);if(rel.startsWith('/banner/imagens/'))fp=path.join(big,path.basename(rel));
      if(!fs.existsSync(fp))return r.fulfill({status:404,body:''});
      r.fulfill({status:200,contentType:MIME[path.extname(fp).toLowerCase()]||'application/octet-stream',body:fs.readFileSync(fp)})});
    await p.goto('http://banner.local/banner/'+f);await p.evaluate(()=>window.fontsReady);
    await p.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))));await p.waitForTimeout(500);
    await p.emulateMedia({media:'screen'});
    await p.addStyleTag({content:`html,body{width:${900*Z}px!important;height:${1200*Z}px!important}.banner{transform:scale(${Z});transform-origin:0 0}`});await p.waitForTimeout(300);
    const name=f.replace('.html',''),rgb=path.join(tmp,name+'.pdf'),pdf=path.join(OUT,`${name}_90x120cm_CMYK.pdf`);
    await p.pdf({path:rgb,width:`${900*Z}px`,height:`${1200*Z}px`,printBackground:true,pageRanges:'1',margin:{top:0,right:0,bottom:0,left:0}});
    await p.close();
    execFileSync('gs',['-q','-dNOPAUSE','-dBATCH','-dSAFER','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.6',
      `-dDEVICEWIDTHPOINTS=${(W_MM*PT).toFixed(2)}`,`-dDEVICEHEIGHTPOINTS=${(H_MM*PT).toFixed(2)}`,'-dFIXEDMEDIA','-dPDFFitPage','-dAutoRotatePages=/None',
      '-sColorConversionStrategy=CMYK','-sProcessColorModel=DeviceCMYK',
      '-dDownsampleColorImages=false','-dDownsampleGrayImages=false','-dDownsampleMonoImages=false',
      '-dAutoFilterColorImages=false','-dColorImageFilter=/DCTEncode','-dJPEGQ=95','-dEmbedAllFonts=true','-dSubsetFonts=true',
      `-sOutputFile=${pdf}`,rgb]);
    console.log('pronto',path.basename(pdf));
  }
  await b.close();fs.rmSync(tmp,{recursive:true,force:true});
})();
