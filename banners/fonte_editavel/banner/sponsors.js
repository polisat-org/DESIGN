// ===== SPONSORS =====
// Put the logo files in this folder (banner/) and list them here, e.g.:
// const SPONSORS = ['logo_empresa1.png', 'logo_empresa2.svg'];
// While the list is empty, dashed placeholders are shown.
const SPONSORS = [];
const SPONSOR_PLACEHOLDERS = 6;
function renderSponsors(){
  const row=document.querySelector('.sponsors .row'); if(!row) return;
  row.innerHTML='';
  if(SPONSORS.length){SPONSORS.forEach(src=>{const i=document.createElement('img');i.src=src;row.appendChild(i)})}
  else for(let k=0;k<SPONSOR_PLACEHOLDERS;k++){const d=document.createElement('div');d.className='slot';d.textContent='SPONSOR';row.appendChild(d)}
}
document.addEventListener('DOMContentLoaded',renderSponsors);
