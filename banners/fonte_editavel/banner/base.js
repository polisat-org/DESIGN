function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs,parent){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e}
function stars(g,n,w,h,seed,maxY){const r=rng(seed);for(let i=0;i<n;i++){const x=r()*w,y=r()*(maxY||h),s=r();
 if(window.NOSPARK&&NOSPARK(x,y))continue; if(s>0.985){sparkle(g,x,y,4+r()*5)}else el('circle',{cx:x,cy:y,r:(s*s*1.6+0.25).toFixed(2),fill:'#fff',opacity:(0.35+r()*0.65).toFixed(2)},g)}}
function sparkle(g,x,y,s){el('path',{d:`M${x} ${y-s}Q${x} ${y} ${x+s} ${y}Q${x} ${y} ${x} ${y+s}Q${x} ${y} ${x-s} ${y}Q${x} ${y} ${x} ${y-s}Z`,fill:'#fff'},g)}
const PLANE='M12 1.5c.8 0 1.3 1.2 1.3 2.6V9l8.2 4.6v2l-8.2-2.4v5.2l2.4 1.8v1.6L12 21l-3.7.8v-1.6l2.4-1.8v-5.2l-8.2 2.4v-2L10.7 9V4.1c0-1.4.5-2.6 1.3-2.6z';
function plane(g,x,y,size,rot,fill){const p=el('path',{d:PLANE,fill:fill||'#fff',transform:`translate(${x} ${y}) rotate(${rot}) scale(${size/24}) translate(-12 -12)`},g);return p}
function fit(){document.querySelectorAll('[data-fit]').forEach(e=>{const W=+e.dataset.fit;let f=200;e.style.fontSize=f+'px';f=f*W/e.scrollWidth;e.style.fontSize=f+'px'})}
// ---- 2026 refresh helpers ----
// Isometric projection: x to the right-down, y to the left-down, z up.
function iso(x,y,z,o){const c=Math.cos(Math.PI/6),s=.5;return [o[0]+(x-y)*c,o[1]+(x+y)*s-z]}
function poly(g,pts,attrs){return el('polygon',Object.assign({points:pts.map(p=>p.join(',')).join(' ')},attrs),g)}
function line(g,a,b,attrs){return el('line',Object.assign({x1:a[0],y1:a[1],x2:b[0],y2:b[1]},attrs),g)}
// 2U CubeSat line drawing (100 x 100 x 227 mm) — returns anchor points for callouts.
function cubesat(g,o,k,col,fill){
  const W=100*k,D=100*k,H=227*k,P=(x,y,z)=>iso(x,y,z,o);
  const st={stroke:col,'stroke-width':2.4,'stroke-linejoin':'round',fill:'none'},thin={stroke:col,'stroke-width':1.3,opacity:.75};
  poly(g,[P(W,0,0),P(W,D,0),P(W,D,H),P(W,0,H)],Object.assign({},st,{fill:fill||'none'}));     // right face (+x)
  poly(g,[P(0,D,0),P(W,D,0),P(W,D,H),P(0,D,H)],Object.assign({},st,{fill:fill||'none'}));     // left face (+y)
  poly(g,[P(0,0,H),P(W,0,H),P(W,D,H),P(0,D,H)],st);                                           // top
  // solar cells: 2 x 3 per face per U
  for(const face of ['x','y']){
    for(let u=0;u<2;u++)for(let c=0;c<2;c++)for(let r=0;r<3;r++){
      const m=8*k,cw=(100*k-3*m)/2,ch=(113.5*k-4*m)/3,a=m+c*(cw+m),b=u*113.5*k+m+r*(ch+m);
      const q=face==='x'?[P(W,a,b),P(W,a+cw,b),P(W,a+cw,b+ch),P(W,a,b+ch)]:[P(a,D,b),P(a+cw,D,b),P(a+cw,D,b+ch),P(a,D,b+ch)];
      poly(g,q,Object.assign({},thin,{fill:'none'}));
    }
  }
  // 1U seam
  line(g,P(W,0,113.5*k),P(W,D,113.5*k),st);line(g,P(0,D,113.5*k),P(W,D,113.5*k),st);
  // patch antenna on top
  const a=22*k,b=78*k;poly(g,[P(a,a,H),P(b,a,H),P(b,b,H),P(a,b,H)],Object.assign({},st,{'stroke-width':2}));
  poly(g,[P(a,a,H),P(a+10*k,a,H),P(a,a+10*k,H)],{fill:col});poly(g,[P(b,b,H),P(b-10*k,b,H),P(b,b-10*k,H)],{fill:col});
  // LoRa monopoles
  line(g,P(W,D*0.15,H*0.98),P(W+70*k,D*0.15,H*0.98),st);line(g,P(W*0.15,D,H*0.98),P(W*0.15,D+70*k,H*0.98),st);
  return {top:P(W/2,D/2,H),antenna:P(b,a,H),lora:P(W+70*k,D*0.15,H*0.98),panel:P(W,D/2,H*0.25),seam:P(0,D,113.5*k),obc:P(W*0.5,D,H*0.62),base:P(W,D,0)};
}
// ---- fonts: registered through the FontFace API (more reliable than @font-face in headless export) ----
const FONTS=[['Archivo','../fonts/Archivo_wdth_wght.ttf',{weight:'100 900',stretch:'62% 125%'}],
 ['Plex','../fonts/IBMPlexMono-Medium.ttf',{weight:'500'}],['Plex','../fonts/IBMPlexMono-SemiBold.ttf',{weight:'600'}],
 ['NDLogos','../fonts/NDLogos-Regular.ttf',{}]];
window.fontsReady=Promise.all(FONTS.map(async([fam,url,d])=>{const buf=await (await fetch(url)).arrayBuffer();const f=new FontFace(fam,buf,d);await f.load();document.fonts.add(f)}))
 .then(()=>{window.fit&&fit()});
// ND Logos has unusual vertical metrics (calibrated by rendering): these margins make the line box
// hug the capitals, so the space around big titles is set by the letters themselves.
function trim(){document.querySelectorAll('.nd').forEach(e=>{e.style.lineHeight='1em';e.style.marginTop='0';e.style.marginBottom='-.08em'})}
const _fit=fit;fit=function(){_fit();trim()};
