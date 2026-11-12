"""Biblioteca de desenho: geometria das pecas, texto em curvas (ND Logos), logos e elementos graficos.

Todas as unidades em milimetros (tamanho M). Origem: centro da peca, y=0 no ponto alto do ombro (HPS),
y cresce para baixo. Na frente, x positivo = lado ESQUERDO de quem veste.
"""
import os, re, math, base64, random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import assets as A

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
LOGOS_DIR = os.path.join(REPO, 'logo_para_colocar_nas_imagens_geradas')

# ----------------------------------------------------------------- cores
POLISAT_BLUE = '#13408f'
POLISAT_BLUE_LIGHT = '#4a7fe0'
INK = '#1d1d1b'
WHITE = '#ffffff'
BR_GREEN, BR_YELLOW, BR_BLUE = '#009c3b', '#ffdf00', '#002776'
H_RED, H_ORANGE, H_AMBER = '#e30613', '#ff6a00', '#ffae00'

# ----------------------------------------------------------------- geometria
GARMENTS = {
    # NW meia-largura do decote, FND/BND profundidade do decote frente/costas,
    # SP ponto do ombro, UA cava (axila), HEM barra, L comprimento, manga: comprimento e raios
    'algodao': dict(NW=95, FND=95, BND=22, SPX=228, SPY=48, UAX=262, UAY=255, HEMX=260, L=720,
                    SL=215, SR0=72, SR1=60, collar='rib', collarH=18, Dmax=130, beta=38),
    'dryfit': dict(NW=92, FND=92, BND=22, SPX=222, SPY=50, UAX=255, UAY=250, HEMX=250, L=730,
                   SL=210, SR0=70, SR1=56, collar='rib', collarH=16, Dmax=122, beta=38),
    'polo': dict(NW=86, FND=70, BND=20, SPX=226, SPY=46, UAX=262, UAY=255, HEMX=262, L=730,
                 SL=225, SR0=72, SR1=58, collar='polo', collarH=30, placketW=34, placketL=150, Dmax=132, beta=38),
}
# Quadros dos paineis (viewBox) — os mesmos usados no visualizador 3D
FRAME = {
    'frente': (-300, -20, 600, 780),
    'costas': (-300, -20, 600, 780),
    'manga_esq': (-230, -30, 460, 270),
    'manga_dir': (-230, -30, 460, 270),
    'gola': (0, 0, 1000, 120),
}


def body_halfwidth(g, y):
    G = GARMENTS[g]
    if y <= G['SPY']:
        return G['SPX']
    if y <= G['UAY']:
        t = (y - G['SPY']) / (G['UAY'] - G['SPY'])
        t = t * t * (3 - 2 * t)
        return G['SPX'] + (G['UAX'] - G['SPX']) * t
    t = (y - G['UAY']) / (G['L'] - G['UAY'])
    return G['UAX'] + (G['HEMX'] - G['UAX']) * t


def shoulder_y(g, x):
    G = GARMENTS[g]
    ax = abs(x)
    if ax <= G['NW']:
        return 0.0
    return G['SPY'] * min(1, (ax - G['NW']) / (G['SPX'] - G['NW']))


def neck_y(g, x, side='frente'):
    G = GARMENTS[g]
    d = G['FND'] if side == 'frente' else G['BND']
    t = min(1, abs(x) / G['NW'])
    return d * math.sqrt(max(0, 1 - t * t))


def body_outline(g, side='frente'):
    """Contorno do corpo (sem mangas) para molde/ficha."""
    G = GARMENTS[g]
    pts = []
    n = 24
    for i in range(n + 1):
        x = -G['NW'] + 2 * G['NW'] * i / n
        pts.append((x, neck_y(g, x, side)))
    pts.append((G['SPX'], G['SPY']))
    for i in range(1, 13):
        y = G['SPY'] + (G['UAY'] - G['SPY']) * i / 12
        # cava concava
        t = i / 12
        x = G['SPX'] - 14 * math.sin(math.pi * t) * (1 - t) + (G['UAX'] - G['SPX']) * t ** 2.2
        pts.append((x, y))
    pts.append((G['HEMX'], G['L']))
    pts.append((-G['HEMX'], G['L']))
    for (x, y) in reversed(pts[n + 2:n + 14]):
        pts.append((-x, y))
    pts.append((-G['SPX'], G['SPY']))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'


def sleeve_outline(g):
    """Molde aproximado da manga (cabeca da manga) no quadro da manga."""
    G = GARMENTS[g]
    circ = 2 * math.pi * G['SR0']
    half = circ / 2
    hem_half = math.pi * G['SR1']
    cap = 105
    pts = []
    n = 30
    for i in range(n + 1):
        x = -half + 2 * half * i / n
        t = x / half
        pts.append((x, cap * (1 - math.cos(t * math.pi / 2) ** 1.6) if abs(t) < 1 else cap))
    pts.append((hem_half, G['SL']))
    pts.append((-hem_half, G['SL']))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'


# ----------------------------------------------------------------- texto em curvas
_FONTS = {}


FONT_FILES = {'R': 'NDLogos-Regular.ttf', 'I': 'NDLogos-Italic.ttf', 'RM': 'Rajdhani-Medium.ttf',
              'RS': 'Rajdhani-SemiBold.ttf', 'RB': 'Rajdhani-Bold.ttf', 'OR': 'Orbitron_wght.ttf'}


def _font(style):
    if style not in _FONTS:
        f = TTFont(os.path.join(SRC, FONT_FILES[style]))
        _FONTS[style] = (f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm, f['hmtx'])
    return _FONTS[style]


def text_d(txt, size, style='R', ls=0.0):
    """Retorna (path_d, largura, altura_maiuscula) com baseline em y=0, inicio x=0. ls em em."""
    f, gs, cmap, upem, hmtx = _font(style)
    s = size / upem
    x = 0.0
    ds = []
    for ch in txt:
        if ch == ' ' and style in ('R', 'I'):
            x += size * 0.32 + ls * size
            continue
        gname = cmap.get(ord(ch))
        if gname is None:
            continue
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, x, 0))
        gs[gname].draw(tp)
        ds.append(pen.getCommands())
        x += hmtx[gname][0] * s + ls * size
    x -= ls * size
    capH = 0.72 * size
    try:
        capH = f['OS/2'].sCapHeight * s or capH
    except Exception:
        pass
    return ' '.join(ds), x, capH


def text(txt, x, y, size, fill, anchor='start', style='R', ls=0.0, extra=''):
    d, w, _ = text_d(txt, size, style, ls)
    dx = {'start': 0, 'middle': -w / 2, 'end': -w}[anchor]
    return f'<path transform="translate({x + dx:.3f} {y:.3f})" fill="{fill}" d="{d}"{extra}/>'


def text_width(txt, size, style='R', ls=0.0):
    return text_d(txt, size, style, ls)[1]


# ----------------------------------------------------------------- logos
_L = {}


def _load(key, path, crop=None):
    lg = A.load(path, key)
    if crop:
        lg = A.crop(lg, crop)
    return lg


def _hex(c):
    c = c.strip().lower()
    named = {'white': '#ffffff', 'black': '#000000'}
    if c in named:
        return named[c]
    m = re.match(r'rgb\(([^)]+)\)', c)
    if m:
        vals = []
        for v in m.group(1).split(','):
            v = v.strip()
            vals.append(round(float(v[:-1]) * 2.55) if v.endswith('%') else round(float(v)))
        return '#%02x%02x%02x' % tuple(vals[:3])
    if re.match(r'#[0-9a-f]{3}$', c):
        return '#' + ''.join(ch * 2 for ch in c[1:])
    return c


def _map_hex(logo, fn):
    lg = logo.copy()
    for e in lg.root.iter():
        for k in A.COLOR_KEYS:
            v = e.get(k)
            if v and v not in ('none', 'transparent') and not v.startswith('url('):
                e.set(k, fn(_hex(v)))
        st = A._style_dict(e.get('style'))
        if st:
            for k in A.COLOR_KEYS:
                if k in st and st[k] not in ('none', 'transparent') and not st[k].startswith('url('):
                    st[k] = fn(_hex(st[k]))
            e.set('style', A._style_str(st))
    return lg


def _mono(logo, color):
    lg = _map_hex(logo, lambda c: color)
    for e in lg.root.iter():  # gradientes viram cor solida
        for k in ('fill', 'stroke'):
            v = e.get(k)
            if v and v.startswith('url('):
                e.set(k, color)
        st = A._style_dict(e.get('style'))
        for k in ('fill', 'stroke'):
            if st.get(k, '').startswith('url('):
                st[k] = color
        if st:
            e.set('style', A._style_str(st))
    lg.root.set('fill', color)
    return lg


SPONSOR_FILES = {  # chave: (arquivo, recorte)
    'ansys': ('ansys.svg', None),
    'st': ('st.svg', None),
    'solidworks': ('solidworks.svg', (25.6, 197.0, 600.2, 257.6)),
    'fdte': ('fdte.svg', None),
    'citi': ('citi.svg', None),
    'griffus': ('griffus.svg', None),
    'indusmart': ('indusmart.svg', None),
    'amigosdapoli': ('adp.svg', None),
    'pme': ('PME.svg', (16.0, 15.4, 196.6, 54.2)),
}
SPONSORS = list(SPONSOR_FILES)


def logo(name, variant='original'):
    """name: polisat | polisat_icon | usp | poli | bandeira | sp:<sponsor>
    variant: original | white | dark | mono:<cor> | light_bg (patrocinador em fundo claro) | navy"""
    k = (name, variant)
    if k in _L:
        return _L[k]
    pid = re.sub(r'\W', '', f'{name}_{variant}')
    if name in ('polisat', 'polisat_icon'):
        crop = (226, -2, 206, 210) if name == 'polisat_icon' else None
        if variant in ('white', 'navy') or variant.startswith('blue:'):
            lg = _load(pid, os.path.join(LOGOS_DIR, 'logo_polisat', 'logo_branco_svg.svg'), crop)
            if variant == 'navy':
                lg = _map_hex(lg, lambda c: POLISAT_BLUE_LIGHT if c == POLISAT_BLUE else c)
            elif variant.startswith('blue:'):
                b = variant.split(':', 1)[1]
                lg = _map_hex(lg, lambda c: b if c == POLISAT_BLUE else c)
        elif variant.startswith('mono:'):
            lg = _mono(_load(pid, os.path.join(LOGOS_DIR, 'logo_polisat', 'logo_branco_svg.svg'), crop), variant[5:])
        else:
            lg = _load(pid, os.path.join(LOGOS_DIR, 'logo_polisat', 'logo_preto_svg.svg'), crop)
        if name == 'polisat_icon':  # mantem so o simbolo (arcos + cubo)
            for ch in list(lg.root):
                d = ch.get('d', '')
                m = re.match(r'M([\d.]+),([\d.]+)', d)
                if A._local(ch.tag) == 'path' and not (m and 480 < float(m.group(1)) < 610 and float(m.group(2)) < 600):
                    lg.root.remove(ch)
    elif name == 'usp':
        lg = _load(pid, os.path.join(SRC, 'usp.svg'), (35.0, 129.9, 740.2, 301.1))
    elif name == 'poli':
        lg = _load(pid, os.path.join(SRC, 'poli_selo.svg'), (88.6, 49.5, 686.3, 683.8))
    elif name == 'bandeira':
        lg = _load(pid, os.path.join(SRC, 'bandeira_brasil.svg'))
    elif name.startswith('sp:'):
        fn, crop = SPONSOR_FILES[name[3:]]
        lg = _load(pid, os.path.join(LOGOS_DIR, 'logo_patrocinadores', 'Logos vetorizadas', fn), crop)
        if variant == 'light_bg':
            lg = _map_hex(lg, lambda c: INK if c in ('#ffffff', '#fefefe') else c)
    else:
        raise KeyError(name)
    if variant.startswith('mono:') and name not in ('polisat', 'polisat_icon'):
        lg = _mono(lg, variant[5:])
    elif variant == 'white' and name not in ('polisat', 'polisat_icon', 'bandeira'):
        lg = _mono(lg, WHITE)
    elif variant == 'dark' and name not in ('polisat', 'polisat_icon', 'bandeira'):
        lg = _mono(lg, INK)
    _L[k] = lg
    return lg


def put(name, variant, x, y, w=None, h=None, align='xMidYMid'):
    return A.place(logo(name, variant), x, y, w, h, align)


def put_center(name, variant, cx, cy, w=None, h=None):
    lg = logo(name, variant)
    vx, vy, vw, vh = lg.viewbox
    if w is None:
        w = h * vw / vh
    if h is None:
        h = w * vh / vw
    return A.place(lg, cx - w / 2, cy - h / 2, w, h)


def aspect(name, variant='original'):
    return logo(name, variant).aspect


_PATCH = {}


def hermes_patch(x, y, w, web=False):
    key = 'web' if web else 'print'
    if key not in _PATCH:
        fn = 'hermes_patch_web.png' if web else 'hermes_patch.png'
        with open(os.path.join(SRC, fn), 'rb') as f:
            _PATCH[key] = base64.b64encode(f.read()).decode()
    h = w * 1792 / 2048
    return (f'<image x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/png;base64,{_PATCH[key]}"/>')


PATCH_ASPECT = 2048 / 1792

# ----------------------------------------------------------------- patrocinadores


def sponsor_grid(x, y, w, h, variant, cols=3, names=None, gap=(10, 8), scale=1.0):
    """Grade de patrocinadores com tamanho optico equilibrado."""
    names = names or SPONSORS
    rows = math.ceil(len(names) / cols)
    cw = (w - gap[0] * (cols - 1)) / cols
    ch = (h - gap[1] * (rows - 1)) / rows
    out = []
    area = cw * ch * 0.34 * scale
    for i, n in enumerate(names):
        r, c = divmod(i, cols)
        in_row = min(cols, len(names) - r * cols)
        off = (cols - in_row) * (cw + gap[0]) / 2
        a = aspect('sp:' + n, variant)
        lw = math.sqrt(area * a)
        lh = lw / a
        if lw > cw * 0.92:
            lw = cw * 0.92; lh = lw / a
        if lh > ch * 0.86:
            lh = ch * 0.86; lw = lh * a
        cx = x + off + c * (cw + gap[0]) + cw / 2
        cy = y + r * (ch + gap[1]) + ch / 2
        out.append(put_center('sp:' + n, variant, cx, cy, lw, lh))
    return ''.join(out)


def sponsor_row(x, y, w, h, variant, names, gap=10):
    """Uma linha de patrocinadores com alturas oticamente equilibradas, ocupando w."""
    asp = [aspect('sp:' + n, variant) for n in names]
    # altura relativa ~ 1/sqrt(aspecto) para equilibrar area
    hs = [h * min(1, 1.9 / math.sqrt(a)) for a in asp]
    ws = [hh * a for hh, a in zip(hs, asp)]
    tot = sum(ws) + gap * (len(names) - 1)
    k = min(1, w / tot)
    ws = [v * k for v in ws]; hs = [v * k for v in hs]
    tot = sum(ws) + gap * (len(names) - 1)
    cx = x + (w - tot) / 2
    out = []
    for n, ww, hh in zip(names, ws, hs):
        out.append(put('sp:' + n, variant, cx, y + (h - hh) / 2, ww, hh))
        cx += ww + gap
    return ''.join(out)

# ----------------------------------------------------------------- graficos


PLANE = ('M12 1.5c.8 0 1.3 1.2 1.3 2.6V9l8.2 4.6v2l-8.2-2.4v5.2l2.4 1.8v1.6L12 21l-3.7.8v-1.6l2.4-1.8v-5.2'
         'l-8.2 2.4v-2L10.7 9V4.1c0-1.4.5-2.6 1.3-2.6z')


def plane(x, y, size, rot, fill):
    return (f'<path d="{PLANE}" fill="{fill}" transform="translate({x:.2f} {y:.2f}) rotate({rot}) '
            f'scale({size / 24:.4f}) translate(-12 -12)"/>')


def cubesat(cx, cy, s, stroke, panel=None, sw=None, rot=0):
    """CubeSat 1U isometrico (linha). s = aresta aparente."""
    sw = sw or s * 0.06
    c30, s30 = math.cos(math.radians(30)) * s, math.sin(math.radians(30)) * s
    top = [(0, -s), (c30, -s + s30 - s * 0), (0, -s + 2 * s30), (-c30, -s + s30)]
    # vertices
    T = (0, -s); R = (c30, -s30); B = (0, 0); Lf = (-c30, -s30)
    R2 = (c30, s - s30); B2 = (0, s); L2 = (-c30, s - s30)
    P = lambda pts: 'M' + ' L'.join(f'{px:.2f} {py:.2f}' for px, py in pts) + ' Z'
    g = [f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot})" fill="none" stroke="{stroke}" '
         f'stroke-width="{sw:.2f}" stroke-linejoin="round">']
    if panel:
        g.append(f'<path d="{P([Lf, B, B2, L2])}" fill="{panel}" stroke="none"/>')
        g.append(f'<path d="{P([B, R, R2, B2])}" fill="{panel}" opacity="0.75" stroke="none"/>')
    g.append(f'<path d="{P([T, R, B, Lf])}"/><path d="{P([Lf, B, B2, L2])}"/><path d="{P([B, R, R2, B2])}"/>')
    # celulas solares (grade 2x2 nas faces laterais)
    for f in ((Lf, B, B2, L2), (B, R, R2, B2)):
        a, b, c, d = f
        for t in (0.5,):
            p1 = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            p2 = (d[0] + (c[0] - d[0]) * t, d[1] + (c[1] - d[1]) * t)
            g.append(f'<path d="M{p1[0]:.2f} {p1[1]:.2f} L{p2[0]:.2f} {p2[1]:.2f}" stroke-width="{sw * 0.6:.2f}"/>')
            q1 = (a[0] + (d[0] - a[0]) * t, a[1] + (d[1] - a[1]) * t)
            q2 = (b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t)
            g.append(f'<path d="M{q1[0]:.2f} {q1[1]:.2f} L{q2[0]:.2f} {q2[1]:.2f}" stroke-width="{sw * 0.6:.2f}"/>')
    # antenas
    g.append(f'<path d="M{T[0]:.2f} {T[1]:.2f} l{-s * 0.55:.2f} {-s * 0.5:.2f} M{R[0]:.2f} {R[1]:.2f} l{s * 0.6:.2f} {-s * 0.25:.2f}" '
             f'stroke-width="{sw * 0.7:.2f}" stroke-linecap="round"/>')
    g.append('</g>')
    return ''.join(g)


def stars(x, y, w, h, n, seed, fill='#fff', avoid=None, rmax=1.1):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        px, py = x + r.random() * w, y + r.random() * h
        if avoid and avoid(px, py):
            continue
        s = r.random()
        if s > 0.975:
            k = 2.2 + r.random() * 2.5
            out.append(f'<path d="M{px:.1f} {py - k:.1f}Q{px:.1f} {py:.1f} {px + k:.1f} {py:.1f}Q{px:.1f} {py:.1f} {px:.1f} {py + k:.1f}'
                       f'Q{px:.1f} {py:.1f} {px - k:.1f} {py:.1f}Q{px:.1f} {py:.1f} {px:.1f} {py - k:.1f}Z" fill="{fill}"/>')
        else:
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{(s * s * rmax + 0.25):.2f}" fill="{fill}" opacity="{0.35 + r.random() * 0.65:.2f}"/>')
    return ''.join(out)


def svg_doc(vb, body, defs='', w_mm=None, h_mm=None, bg=None, extra_attrs=''):
    x, y, w, h = vb
    w_mm = w_mm or w
    h_mm = h_mm or h
    bgr = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w_mm}mm" height="{h_mm}mm" viewBox="{x} {y} {w} {h}"{extra_attrs}>'
            f'<defs>{defs}</defs>{bgr}{body}</svg>\n')
