"""Fichas tecnicas (A3 paisagem) e prancha comparativa — 100% vetoriais, textos em curvas.

Roda depois dos mockups:  python3 ficha.py   (le jobs.json; escreve _build/*.svg)
O render.js converte os SVGs em PDF e PNG.
"""
import os, sys, json, base64, html, datetime
import lib as L

PANEL_NAME = {'frente': 'Frente', 'costas': 'Costas', 'manga_esq': 'Manga esquerda', 'manga_dir': 'Manga direita'}
DARK, MUTED, ORANGE, MAG, CYAN = '#1b1d22', '#6b7080', '#e35b00', '#ff00aa', '#00a0e0'


def uri(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def T(x, y, s, size, font='RM', fill=DARK, anchor='start', ls=0.0):
    return L.text(s, x, y, size, fill, anchor, font, ls)


def wrap(s, width, size, font='RM'):
    words, lines, cur = s.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if L.text_width(t, size, font) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, width, size, font='RM', fill=DARK, lh=1.3):
    out = ''
    lines = wrap(s, width, size, font)
    for i, ln in enumerate(lines):
        out += T(x, y + i * size * lh, ln, size, font, fill)
    return out, len(lines) * size * lh


def pos_text(p):
    cx = p['x'] + p['w'] / 2
    if p['panel'] in ('frente', 'costas'):
        if abs(cx) < 2:
            side = 'centralizado na linha central'
        else:
            wl = cx > 0 if p['panel'] == 'frente' else cx < 0
            side = f'centro a {abs(cx):.0f} mm da linha central (lado {"esquerdo" if wl else "direito"} de quem veste)'
        return f'{side}; topo a {max(0, p["y"]):.0f} mm do HPS'
    return f'centralizado na linha externa da manga; topo a {p["y"]:.0f} mm da costura do ombro'


def view(model_dir, g, panel, pls, numbers, x, y, wmm):
    fx, fy, fw, fh = L.FRAME[panel]
    if panel in ('frente', 'costas'):
        outline = L.body_outline(g, panel)
        vb = (-275, -30, 550, 770)
    else:
        outline = L.sleeve_outline(g)
        G = L.GARMENTS[g]
        half = 3.1416 * G['SR0']
        vb = (-half - 8, -12, 2 * half + 16, G['SL'] + 24)
    hmm = wmm * vb[3] / vb[2]
    img = uri(os.path.join(model_dir, 'paineis_visualizacao', f'{panel}.svg'), 'image/svg+xml')
    cid = f'clip_{panel}'
    k = vb[2] / wmm  # unidades de painel por mm de papel
    marks = ''
    for p in pls:
        if p['panel'] != panel:
            continue
        n = numbers[p['pid']]
        r = 2.6 * k
        mx, my = p['x'] + p['w'], p['y']
        marks += (f'<rect x="{p["x"]:.1f}" y="{p["y"]:.1f}" width="{p["w"]:.1f}" height="{p["h"]:.1f}" fill="none" stroke="{MAG}" '
                  f'stroke-width="{0.3 * k:.2f}" stroke-dasharray="{1.2 * k:.1f} {0.7 * k:.1f}"/>'
                  f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r:.1f}" fill="{MAG}"/>'
                  + L.text(str(n), mx, my + r * 0.45, r * 1.3, '#ffffff', 'middle', 'RB'))
    guides = f'<path d="M0 {vb[1]} V{vb[1] + vb[3]}" stroke="{CYAN}" stroke-width="{0.2 * k:.2f}" stroke-dasharray="{1.5 * k:.1f} {1 * k:.1f}"/>'
    if panel in ('frente', 'costas'):
        guides += (f'<path d="M{vb[0]} 0 H{vb[0] + vb[2]}" stroke="{CYAN}" stroke-width="{0.2 * k:.2f}" stroke-dasharray="{1.5 * k:.1f} {1 * k:.1f}"/>'
                   + L.text('HPS', vb[0] + 2 * k, -1.2 * k, 2.4 * k, CYAN, 'start', 'RS'))
    return (f'<svg x="{x}" y="{y}" width="{wmm}" height="{hmm:.2f}" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" overflow="visible">'
            f'<clipPath id="{cid}"><path d="{outline}"/></clipPath>'
            f'<image x="{fx}" y="{fy}" width="{fw}" height="{fh}" xlink:href="{img}" clip-path="url(#{cid})" preserveAspectRatio="none"/>'
            f'<path d="{outline}" fill="none" stroke="#2a2a2a" stroke-width="{0.3 * k:.2f}"/>{guides}{marks}</svg>'), hmm


def file_use(b):
    for key, txt in (('costas_sem_nome', 'Costas: arte de produção (nome aplicado por pessoa)'),
                     ('costas_exemplo', 'Costas: referência com o nome posicionado'), ('frente', 'Frente: painel inteiro'),
                     ('manga_esq', 'Manga esquerda (de quem veste)'), ('manga_dir', 'Manga direita (de quem veste)'),
                     ('gola', 'Gola / punhos (ribana)')):
        if key in b:
            return txt
    return ''


def ficha_svg(f, logo_w):
    g, pls, d, mid = f['garment'], f['placements'], f['dir'], f['id']
    numbers = {p['pid']: i + 1 for i, p in enumerate(pls)}
    o = []
    # cabecalho
    o.append('<rect x="0" y="0" width="420" height="22" fill="#111216"/>')
    o.append(L.A.place(L.logo('polisat', 'white'), 12, 5, None, 12))
    o.append(T(44, 9.6, f'FICHA TÉCNICA  ·  {f["tipo"].upper()}', 3.0, 'RS', '#ff8a2a', ls=0.12))
    o.append(T(44, 17.4, f'{mid}  {f["nome"].upper()}', 6.4, 'OR', '#ffffff', ls=0.03))
    o.append(T(408, 10.2, 'Equipe PoliSat  ·  Escola Politécnica da USP', 3.2, 'RM', '#c9ccd4', 'end'))
    o.append(T(408, 15.4, f'Tamanho base M  ·  {datetime.date.today().strftime("%m/%Y")}', 3.2, 'RM', '#c9ccd4', 'end'))
    # vistas
    y0 = 33
    for (lab, x) in (('FRENTE', 12), ('COSTAS', 108)):
        o.append(T(x, y0 - 2, lab, 2.8, 'RB', MUTED, ls=0.12))
    v, h1 = view(d, g, 'frente', pls, numbers, 12, y0, 90); o.append(v)
    v, _ = view(d, g, 'costas', pls, numbers, 108, y0, 90); o.append(v)
    sx = 206
    o.append(T(sx, y0 - 2, 'MANGA ESQUERDA', 2.8, 'RB', MUTED, ls=0.12))
    v, hs = view(d, g, 'manga_esq', pls, numbers, sx, y0, 54); o.append(v)
    o.append(T(sx, y0 + hs + 7, 'MANGA DIREITA', 2.8, 'RB', MUTED, ls=0.12))
    v, _ = view(d, g, 'manga_dir', pls, numbers, sx, y0 + hs + 9, 54); o.append(v)
    gy = y0 + 2 * hs + 18
    o.append(T(sx, gy, 'GOLA / RIBANA', 2.8, 'RB', MUTED, ls=0.12))
    o.append(f'<image x="{sx}" y="{gy + 2}" width="54" height="6.5" preserveAspectRatio="none" xlink:href="{uri(os.path.join(d, "paineis_visualizacao", "gola.svg"), "image/svg+xml")}"/>'
             f'<rect x="{sx}" y="{gy + 2}" width="54" height="6.5" fill="none" stroke="#bbb" stroke-width="0.2"/>')
    # mockups
    mx = 268
    for i, vname in enumerate(('frente', 'costas')):
        fp = os.path.join(d, f'mockup_{mid}_{vname}.png')
        o.append(f'<rect x="{mx + i * 71}" y="{y0 - 3}" width="69" height="88.7" rx="2" fill="#eceef2"/>')
        if os.path.exists(fp):
            o.append(f'<image x="{mx + i * 71}" y="{y0 - 3}" width="69" height="88.7" xlink:href="{uri(fp, "image/png")}"/>')
    # especificacao
    y = y0 + 93
    o.append(T(mx, y, 'ESPECIFICAÇÃO', 2.9, 'RB', ORANGE, ls=0.14)); y += 5.2
    for k, val in (('Modelo', f'{f["tipo"]}  ·  {f["nome"]}'), ('Tecido', f['tecido']), ('Técnica', f['tecnica']),
                   ('Acabamento', f['gola'] or 'Gola em ribana na cor do corpo'), ('Conceito', f['conceito'])):
        o.append(T(mx, y, k, 3.1, 'RS', MUTED))
        p_, hh = para(mx + 24, y, val, 116, 3.1)
        o.append(p_); y += hh + 1.2
    # tabela / arquivos
    ty = max(y0 + h1 + 10, y + 4)
    if not f['sub']:
        o.append(T(12, ty, 'APLICAÇÕES', 2.9, 'RB', ORANGE, ls=0.14)); ty += 3
        cols = [(12, '#'), (20, 'ELEMENTO'), (86, 'TAMANHO'), (110, 'POSIÇÃO (TAMANHO M)'), (232, 'TÉCNICA'), (300, 'CORES')]
        o.append(f'<path d="M12 {ty + 4.6} H408" stroke="{DARK}" stroke-width="0.35"/>')
        for cx, lab in cols:
            o.append(T(cx, ty + 3.3, lab, 2.5, 'RB', MUTED, ls=0.08))
        ty += 4.6
        for p in pls:
            n = numbers[p['pid']]
            rowtop = ty + 1.6
            o.append(f'<circle cx="14.6" cy="{rowtop + 2.2}" r="2.3" fill="{MAG}"/>' + T(14.6, rowtop + 3.2, str(n), 2.8, 'RB', '#fff', 'middle'))
            o.append(T(20, rowtop + 3.2, p['label'], 3.1, 'RS'))
            o.append(T(20, rowtop + 7.0, PANEL_NAME[p['panel']], 2.7, 'RM', MUTED))
            o.append(T(86, rowtop + 3.2, f'{p["w"]:.0f} x {p["h"]:.0f} mm', 3.1, 'RS'))
            a, ha = para(110, rowtop + 3.2, pos_text(p), 118, 3.0)
            b, hb = para(232, rowtop + 3.2, p['tecnica'], 64, 3.0)
            o.append(a); o.append(b)
            cxp, cyp, hc = 300, rowtop, 0
            for c in p['cores']:
                lab = f'{c[0]}  {c[2]}'
                wlab = L.text_width(lab, 2.7, 'RM') + 6
                if cxp + wlab > 408:
                    cxp = 300; cyp += 4.2
                o.append(f'<rect x="{cxp}" y="{cyp + 0.8}" width="3.2" height="3.2" rx="0.5" fill="{c[1]}" stroke="#999" stroke-width="0.15"/>'
                         + T(cxp + 4.2, cyp + 3.5, lab, 2.7))
                cxp += wlab + 2
            hrow = max(8.2, ha + 1.5, hb + 1.5, cyp - rowtop + 5.5)
            ty += hrow + 1.2
            o.append(f'<path d="M12 {ty} H408" stroke="#d9dbe0" stroke-width="0.2"/>')
        notes = ['Arquivos de cada aplicação em escala 1:1 (SVG + PDF vetorial) na pasta impressao/; o nome do arquivo traz o tamanho em mm.',
                 'Medidas para o tamanho M. Nos outros tamanhos manter as distâncias ao HPS e a linha central; o tamanho dos logos não muda (PP/P: reduzir no máximo 10%).',
                 'Textos já convertidos em curvas. Pantone e referência aproximada: aprovar prova de cor antes da produção.']
        if g == 'polo':
            notes.append('Bordado: digitalizar a matriz a partir do vetor. Detalhes menores que 0,8 mm no selo da Poli podem ser simplificados. Sem patrocinadores na polo.')
    else:
        ns = f['name']
        o.append(T(12, ty, 'ARQUIVOS DE SUBLIMAÇÃO', 2.9, 'RB', ORANGE, ls=0.14)); ty += 6
        for fn in f['files']:
            o.append(T(12, ty, os.path.basename(fn), 3.0, 'RS') + T(110, ty, file_use(os.path.basename(fn)), 3.0, 'RM', MUTED)); ty += 4.6
        ty += 3
        o.append(T(12, ty, 'NOME NAS COSTAS', 2.9, 'RB', ORANGE, ls=0.14)); ty += 6
        for s in (f'Área reservada: {ns["w"]} x {ns["h"]} mm, centralizada, topo a {ns["y"]} mm do HPS (retângulo em {mid}_costas_exemplo_nome).',
                  f'Fonte ND Logos, altura nominal {ns["size"]} mm, espaçamento +60, cor {ns["color"]}. Nomes longos: reduzir até caber (margem de 20 mm de cada lado).',
                  f'Lista de nomes e tamanhos: impressao/lista_nomes.csv. Modelo editável: {mid}_nome_editavel.svg (converter o texto em curvas antes de imprimir).'):
            p_, hh = para(16, ty, s, 240, 3.1); o.append(f'<circle cx="13.2" cy="{ty - 1.1}" r="0.7" fill="{DARK}"/>' + p_); ty += hh + 0.8
        notes = ['Arte em quadro com sangria: frente/costas 600 x 780 mm, mangas 460 x 270 mm (tamanho M). Origem: linha central e HPS (guias em impressao/guias/).',
                 'Em outros tamanhos, encaixar o molde da confecção mantendo linha central e HPS; logos e área do nome não devem ser escalados.',
                 'Patch Hermes em bitmap 2048 px (acima de 170 dpi no maior uso). Demais elementos vetoriais, textos em curvas.']
    ty += 5
    o.append(T(12, ty, 'OBSERVAÇÕES PARA A GRÁFICA', 2.9, 'RB', ORANGE, ls=0.14)); ty += 6
    for s in notes:
        p_, hh = para(16, ty, s, 380, 3.1)
        o.append(f'<circle cx="13.2" cy="{ty - 1.1}" r="0.7" fill="{DARK}"/>' + p_); ty += hh + 0.8
    o.append(T(12, 290, 'Linha azul tracejada = linha central e HPS (ponto alto do ombro)  ·  retângulos magenta = área de cada aplicação', 2.7, 'RM', '#8a8f9c'))
    o.append(T(408, 290, 'Fonte: camisetas/_fonte  (python3 build.py && node render.js)', 2.7, 'RM', '#8a8f9c', 'end'))
    return L.svg_doc((0, 0, 420, 297), ''.join(o), bg='#ffffff'), ty


def comparativo_svg(models):
    W, cw, chh, pad = 2396, 376, 290, 20
    o = [f'<rect width="{W}" height="{3 * chh + 4 * pad + 70}" fill="#e9ebef"/>']
    o.append(L.A.place(L.logo('polisat', 'dark'), pad, 14, None, 34))
    o.append(T(W - pad, 40, 'CAMISETAS 2026   16 MODELOS', 16, 'OR', DARK, 'end', 0.04))
    order = {'Algodão': 0, 'Polo': 1, 'Dry-fit': 2}
    seen = {}
    for m in models:
        r = order.get(m['tipo'], 2)
        c = seen.get(r, 0); seen[r] = c + 1
        x, y = pad + c * (cw + pad), 70 + r * (chh + pad)
        o.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{chh}" rx="14" fill="#f7f8fa"/>')
        for j, vn in enumerate(('frente', 'costas')):
            fp = os.path.join(m['dir'], f'mockup_{m["id"]}_{vn}.png')
            if os.path.exists(fp):
                o.append(f'<image x="{x + 4 + j * 183}" y="{y + 6}" width="183" height="235.3" xlink:href="{uri(fp, "image/png")}"/>')
        o.append(T(x + 16, y + chh - 18, m['id'], 17, 'RB', ORANGE) + T(x + 52, y + chh - 18, m['nome'].upper(), 17, 'RB', DARK)
                 + T(x + cw - 16, y + chh - 18, m['tipo'].upper(), 13, 'RS', MUTED, 'end', 0.1))
    H = 70 + 3 * chh + 3 * pad
    return L.svg_doc((0, 0, W, H), ''.join(o)), W, H


def main():
    J = json.load(open(os.path.join(L.HERE, 'jobs.json'), encoding='utf-8'))
    bdir = os.path.join(L.HERE, '_build')
    os.makedirs(bdir, exist_ok=True)
    for f in J['ficha_data']:
        svg, h = ficha_svg(f, None)
        if h > 286:
            print('AVISO: ficha', f['id'], 'passou da pagina:', round(h))
        with open(os.path.join(bdir, f'ficha_{f["id"]}.svg'), 'w', encoding='utf-8') as fh:
            fh.write(svg)
    svg, W, H = comparativo_svg(J['models'])
    with open(os.path.join(bdir, 'comparativo.svg'), 'w', encoding='utf-8') as fh:
        fh.write(svg)
    json.dump({'w': W, 'h': H}, open(os.path.join(bdir, 'comparativo.json'), 'w'))
    print('fichas ok')


if __name__ == '__main__':
    main()
