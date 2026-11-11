function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs,parent){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e}
function stars(g,n,w,h,seed,maxY){const r=rng(seed);for(let i=0;i<n;i++){const x=r()*w,y=r()*(maxY||h),s=r();
 if(window.NOSPARK&&NOSPARK(x,y))continue; if(s>0.985){sparkle(g,x,y,4+r()*5)}else el('circle',{cx:x,cy:y,r:(s*s*1.6+0.25).toFixed(2),fill:'#fff',opacity:(0.35+r()*0.65).toFixed(2)},g)}}
function sparkle(g,x,y,s){el('path',{d:`M${x} ${y-s}Q${x} ${y} ${x+s} ${y}Q${x} ${y} ${x} ${y+s}Q${x} ${y} ${x-s} ${y}Q${x} ${y} ${x} ${y-s}Z`,fill:'#fff'},g)}
const PLANE='M12 1.5c.8 0 1.3 1.2 1.3 2.6V9l8.2 4.6v2l-8.2-2.4v5.2l2.4 1.8v1.6L12 21l-3.7.8v-1.6l2.4-1.8v-5.2l-8.2 2.4v-2L10.7 9V4.1c0-1.4.5-2.6 1.3-2.6z';
function plane(g,x,y,size,rot,fill){const p=el('path',{d:PLANE,fill:fill||'#fff',transform:`translate(${x} ${y}) rotate(${rot}) scale(${size/24}) translate(-12 -12)`},g);return p}
function fit(){document.querySelectorAll('[data-fit]').forEach(e=>{const W=+e.dataset.fit;let f=200;e.style.fontSize=f+'px';f=f*W/e.scrollWidth;e.style.fontSize=f+'px'})}
