// ===== FOOTER: institutions + sponsors =====
// Every banner ends with <div class="foot"></div>; this script fills it.
// To add or remove a sponsor, edit SPONSORS. Files live in logos/patrocinadores/.
// Logos are sized by area (not by height) so wide and compact marks look equally strong.
const SPONSORS = [
  'ansys', 'st', 'solidworks',
  'fdte', 'citi', 'amigosdapoli',
  'griffus', 'indusmart', 'pme',
];
const LOGO_AREA = 7600;   // px² per sponsor logo (≈ 76 cm² printed)
const LOGO_MAX_W = 186, LOGO_MAX_H = 64;

function renderFooter(){
  const f = document.querySelector('.foot'); if(!f) return;
  f.innerHTML = `
    <div class="inst"><div class="mono">A student team of</div>
      <div class="logos"><img class="poli" src="logos/poli_selo_preto.svg" alt="Escola Politécnica"><img class="usp" src="logos/usp_preto.svg" alt="USP"></div></div>
    <div class="sp"><div class="mono">Made possible by</div><div class="grid"></div></div>`;
  const g = f.querySelector('.grid');
  SPONSORS.forEach(name => {
    const i = new Image();
    i.alt = name;
    i.onload = () => {
      const a = i.naturalWidth / i.naturalHeight;
      let h = Math.sqrt(LOGO_AREA / a), w = h * a;
      if (w > LOGO_MAX_W) { w = LOGO_MAX_W; h = w / a; }
      if (h > LOGO_MAX_H) { h = LOGO_MAX_H; w = h * a; }
      i.style.width = w + 'px'; i.style.height = h + 'px';
    };
    i.src = `logos/patrocinadores/${name}_cor_fundo_claro.svg`;
    g.appendChild(i);
  });
}
document.addEventListener('DOMContentLoaded', renderFooter);
