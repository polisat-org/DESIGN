"""Gera todos os arquivos das camisetas PoliSat.

Uso:  python3 build.py            (gera SVGs, dados do visualizador 3D e lista de jobs)
      depois:  node render.js      (PDFs, mockups 3D, fichas tecnicas)
"""
import os, json, base64, re, shutil, csv, math
import lib as L
import modelos as Mo

OUT = os.path.abspath(os.path.join(L.HERE, '..'))
MOD = os.path.join(OUT, 'modelos')
TIPO = {'polo': 'Polo', 'algodao': 'Algodão', 'dryfit': 'Dry-fit'}


def w(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)


def darker(hexc, k=0.55):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


def placement_doc(p):
    if p.crop:
        cx, cy, cw, ch = p.crop
        vb = (cx + 300, cy + 20, cw, ch)
        return L.svg_doc(vb, p.art(False)), cw, ch
    return L.svg_doc((0, 0, p.w, p.h), p.art(False)), p.w, p.h


def box_of(p):
    if p.crop:
        return p.crop
    return (p.x, p.y, p.w, p.h)


def jobs_fonts():
    return os.path.join(L.REPO, 'banners', 'fonte_editavel', 'fonts')


def main():
    models = Mo.build_models()
    jobs = {'pdf': [], 'mockups': [], 'fichas': []}
    viewer = []
    ficha_data = []
    for m in models:
        d = os.path.join(MOD, m['slug'])
        if os.path.isdir(d):
            shutil.rmtree(d)
        imp = os.path.join(d, 'impressao')
        pan = os.path.join(d, 'paineis_visualizacao')
        name_spec = Mo.NAME_SPEC.get(m['id'])
        # paineis completos (alta qualidade) — usados na ficha
        P = Mo.panels_for(m, web=False, name='' if name_spec else 'NAME')
        for k, svg in P.items():
            w(os.path.join(pan, f'{k}.svg'), svg)
        files = []
        if m['sublimacao']:
            for k, svg in P.items():
                nm = 'costas_sem_nome' if k == 'costas' else k
                fp = os.path.join(imp, f'{m["id"]}_{nm}.svg')
                w(fp, svg)
                x, y, ww, hh = L.FRAME[k]
                files.append((fp, ww, hh))
            ex = Mo.panels_for(m, web=False, name='NAME')['costas']
            fp = os.path.join(imp, f'{m["id"]}_costas_exemplo_nome.svg')
            w(fp, ex); files.append((fp, 600, 780))
            # nome editavel (texto vivo com fonte ND Logos) + lista de nomes
            ns = name_spec
            x, y, ww, hh = L.FRAME['costas']
            ed = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{ww}mm" height="{hh}mm" '
                  f'viewBox="{x} {y} {ww} {hh}"><!-- Area do nome: {ns["w"]} x {ns["h"]} mm, topo a {ns["y"]} mm do HPS. '
                  f'Fonte ND Logos, altura {ns["size"]} pt-mm. Substitua NAME pelo nome de cada pessoa e converta em curvas. -->'
                  f'<rect x="{ns["cx"] - ns["w"] / 2}" y="{ns["y"]}" width="{ns["w"]}" height="{ns["h"]}" fill="none" stroke="#ff00ff" stroke-width="0.5" stroke-dasharray="4 3"/>'
                  f'<text x="{ns["cx"]}" y="{ns["y"] + ns["h"] / 2 + ns["size"] * 0.36:.1f}" text-anchor="middle" font-family="ND Logos" '
                  f'font-size="{ns["size"]}" letter-spacing="{ns["size"] * 0.06:.1f}" fill="{ns["color"]}">NAME</text></svg>\n')
            w(os.path.join(imp, f'{m["id"]}_nome_editavel.svg'), ed)
            with open(os.path.join(imp, 'lista_nomes.csv'), 'w', newline='', encoding='utf-8') as f:
                cw = csv.writer(f)
                cw.writerow(['nome_nas_costas', 'tamanho', 'quantidade'])
                cw.writerow(['EXEMPLO', 'M', '1'])
            # guias de molde (contorno, linha central)
            for k in ('frente', 'costas', 'manga_esq', 'manga_dir'):
                x, y, ww, hh = L.FRAME[k]
                outline = L.body_outline('dryfit', k) if k in ('frente', 'costas') else L.sleeve_outline('dryfit')
                guide = (f'<path d="{outline}" fill="none" stroke="#ff00ff" stroke-width="0.8"/>'
                         f'<path d="M0 {y} V{y + hh}" stroke="#00b4ff" stroke-width="0.5" stroke-dasharray="6 4"/>'
                         f'<path d="M{x} 0 H{x + ww}" stroke="#00b4ff" stroke-width="0.5" stroke-dasharray="6 4"/>')
                w(os.path.join(imp, 'guias', f'guia_{k}.svg'), L.svg_doc((x, y, ww, hh), guide))
        else:
            for p in m['placements']:
                doc, ww, hh = placement_doc(p)
                fp = os.path.join(imp, f'{m["id"]}_{p.pid}_{round(ww)}x{round(hh)}mm.svg')
                w(fp, doc)
                files.append((fp, ww, hh))
        for fp, ww, hh in files:
            jobs['pdf'].append({'svg': fp, 'pdf': fp[:-4] + '.pdf', 'w': ww, 'h': hh})
        # dados do visualizador (versao web)
        PW = Mo.panels_for(m, web=True, name='' if name_spec else 'NAME')
        viewer.append(dict(id=m['id'], slug=m['slug'], nome=m['nome'], garment=m['garment'], tipo=TIPO[m['garment']],
                           cor=m['cor_tecido'], swatch=m['fabric'], inner=darker(m['fabric'], 0.6 if m['fabric'] > '#888' else 1.0),
                           conceito=m['conceito'], name=name_spec, panels=PW))
        for v in ('front', 'back', 'side'):
            jobs['mockups'].append({'id': m['id'], 'view': v, 'out': os.path.join(d, f'mockup_{m["id"]}_{ {"front": "frente", "back": "costas", "side": "lado"}[v]}.png')})
        # dados da ficha
        pls = []
        if not m['sublimacao']:
            for p in m['placements']:
                bx, by, bw, bh = box_of(p)
                pls.append(dict(pid=p.pid, label=p.label, panel=p.panel, x=bx, y=by, w=bw, h=bh, tecnica=p.tecnica,
                                cores=p.cores))
        ficha_data.append(dict(id=m['id'], slug=m['slug'], nome=m['nome'], garment=m['garment'], tipo=TIPO[m['garment']],
                               tecido=m['tecido'], tecnica=m['tecnica'], conceito=m['conceito'], sub=m['sublimacao'],
                               gola=m.get('gola_desc', ''), placements=pls, dir=d, name=name_spec,
                               files=[os.path.relpath(f[0], d) for f in files]))
    # visualizador 3D
    vdir = os.path.join(OUT, 'visualizador_3d')
    os.makedirs(vdir, exist_ok=True)
    geom = {k: v for k, v in L.GARMENTS.items()}
    js = ('// Gerado por _fonte/build.py — nao editar a mao\n'
          f'window.GEOM = {json.dumps(geom)};\nwindow.FRAME = {json.dumps(L.FRAME)};\n'
          f'window.SHIRTS = {json.dumps(viewer, ensure_ascii=False)};\n')
    # contornos dos glifos ND Logos (o navegador rejeita o arquivo da fonte; desenhamos com Path2D)
    f_, gs, cmap, upem, hmtx = L._font('R')
    glyphs = {}
    for cp in cmap:
        ch = chr(cp)
        if cp < 0x250 and ch.strip():
            d, adv, _ = L.text_d(ch, 1000)
            glyphs[ch] = [d, round(adv, 1)]
    js += f'window.GLYPHS = {json.dumps(glyphs, ensure_ascii=False)};\n'
    w(os.path.join(vdir, 'dados.js'), js)
    with open(os.path.join(L.HERE, 'viewer_template.html'), encoding='utf-8') as f:
        html = f.read()
    brand_d, brand_w, _ = L.text_d('POLISAT', 100, 'R', 0.04)
    html = html.replace('__BRAND__', f'<svg viewBox="0 -76 {brand_w:.0f} 80" height="22" aria-label="PoliSat"><path fill="currentColor" d="{brand_d}"/></svg>')
    for key, fn in (('__THREE__', 'three.module.js'), ('__ORBIT__', 'OrbitControls.js')):
        with open(os.path.join(L.SRC, 'three', fn), 'rb') as f:
            html = html.replace(key, base64.b64encode(f.read()).decode())
    w(os.path.join(vdir, 'index.html'), html)
    # ativos (logos normalizados)
    at = os.path.join(OUT, 'ativos_vetoriais')
    if os.path.isdir(at):
        shutil.rmtree(at)
    def save_logo(fn, name, variant):
        lg = L.logo(name, variant)
        vx, vy, vw, vh = lg.viewbox
        k = 100 / vw
        w(os.path.join(at, fn), L.svg_doc((0, 0, vw * k, vh * k), L.put(name, variant, 0, 0, vw * k, vh * k)))
    for fn, n, v in [('polisat_fundo_escuro.svg', 'polisat', 'white'), ('polisat_fundo_claro.svg', 'polisat', 'dark'),
                     ('polisat_fundo_marinho.svg', 'polisat', 'navy'), ('polisat_simbolo_fundo_escuro.svg', 'polisat_icon', 'white'),
                     ('polisat_simbolo_fundo_claro.svg', 'polisat_icon', 'dark'), ('usp_preto.svg', 'usp', 'original'),
                     ('usp_branco.svg', 'usp', 'white'), ('poli_selo_preto.svg', 'poli', 'dark'), ('poli_selo_branco.svg', 'poli', 'white'),
                     ('bandeira_brasil.svg', 'bandeira', 'original')]:
        save_logo(fn, n, v)
    for s in L.SPONSORS:
        save_logo(f'patrocinadores/{s}_branco.svg', 'sp:' + s, 'white')
        save_logo(f'patrocinadores/{s}_cor_fundo_claro.svg', 'sp:' + s, 'light_bg')
    bdir = os.path.join(L.HERE, '_build')
    for f in ficha_data:
        jobs['fichas'].append({'svg': os.path.join(bdir, f'ficha_{f["id"]}.svg'),
                               'pdf': os.path.join(f['dir'], f'ficha_tecnica_{f["id"]}.pdf'),
                               'png': os.path.join(f['dir'], f'ficha_tecnica_{f["id"]}.png')})
    jobs['ficha_data'] = ficha_data
    jobs['models'] = [{'id': f['id'], 'nome': f['nome'], 'tipo': f['tipo'], 'dir': f['dir']} for f in ficha_data]
    jobs['viewer'] = os.path.join(vdir, 'index.html')
    jobs['out'] = OUT
    jobs['fonts'] = jobs_fonts()
    jobs['polisat_logo'] = L.svg_doc((0, 0, 705, 372), L.put('polisat', 'dark', 0, 0, 705, 372))
    w(os.path.join(L.HERE, 'jobs.json'), json.dumps(jobs, ensure_ascii=False))
    print('modelos:', len(models), '| pdf jobs:', len(jobs['pdf']), '| dados.js KB:', len(js) // 1024)


if __name__ == '__main__':
    main()
