"""Definicao dos 9 modelos de camiseta PoliSat.

Cada modelo gera:
  - paineis completos (frente, costas, manga_esq, manga_dir, gola) usados no mockup/3D e na ficha
  - arquivos de impressao: estampas localizadas (algodao/polo) ou paineis de sublimacao (dry-fit)
Coordenadas em mm (ver lib.py).
"""
import math
import lib as L
from lib import text, put, put_center, hermes_patch, sponsor_grid, cubesat, stars, plane

BLACK_FAB = '#141416'
NAVY_FAB = '#152039'
WHITE_FAB = '#f5f5f2'


# Area do nome (costas dos dry-fit): centro x, topo y, largura, altura, tamanho da fonte, cor do texto
NAME_SPEC = {
    'D1': dict(cx=0, y=568, w=340, h=84, size=46, color='#ffffff'),
    'D2': dict(cx=0, y=548, w=330, h=80, size=44, color='#ffffff'),
    'D3': dict(cx=0, y=568, w=360, h=80, size=48, color='#ffffff'),
}


class Placement:
    def __init__(self, pid, label, panel, x, y, w, h, art, tecnica, cores, crop=None):
        self.crop = crop  # (x, y, w, h) no painel, para artes desenhadas no quadro inteiro
        self.pid, self.label, self.panel = pid, label, panel
        self.x, self.y, self.w, self.h = x, y, w, h
        self.art = art  # funcao (web:bool) -> svg em coordenadas locais 0..w, 0..h
        self.tecnica, self.cores = tecnica, cores

    def svg_in_panel(self, web=False):
        return f'<g transform="translate({self.x:.2f} {self.y:.2f})">{self.art(web)}</g>'


def full(svg):
    """Arte desenhada em coordenadas absolutas do painel (placement ocupa o painel inteiro)."""
    return f'<g transform="translate(300 20)">{svg}</g>'


def logo_box(name, variant, w=None, h=None):
    a = L.aspect(name, variant)
    if w is None:
        w = h * a
    if h is None:
        h = w / a
    return w, h, (lambda web, n=name, v=variant, ww=w, hh=h: put(n, v, 0, 0, ww, hh))


def place_logo(pid, label, panel, name, variant, cx, top, w=None, h=None, tecnica='', cores=()):
    ww, hh, art = logo_box(name, variant, w, h)
    return Placement(pid, label, panel, cx - ww / 2, top, ww, hh, art, tecnica, cores)


def flag_placement(panel, cx, top, w, tecnica, pid='manga_dir_bandeira'):
    return place_logo(pid, 'Bandeira do Brasil', panel, 'bandeira', 'original', cx, top, w=w, tecnica=tecnica,
                      cores=[('Verde', L.BR_GREEN, 'Pantone 355 C'), ('Amarelo', L.BR_YELLOW, 'Pantone 116 C'),
                             ('Azul', L.BR_BLUE, 'Pantone 280 C'), ('Branco', '#ffffff', 'White')])


def sleeve_stack(panel, items, top, gap, tecnica, cores, pid):
    """Empilha logos centralizados na linha externa da manga."""
    parts = []
    y = 0
    maxw = 0
    for name, variant, w, h in items:
        ww, hh, _ = logo_box(name, variant, w, h)
        parts.append((name, variant, ww, hh, y))
        y += hh + gap
        maxw = max(maxw, ww)
    H = y - gap

    def art(web, parts=parts, maxw=maxw):
        return ''.join(put(n, v, (maxw - ww) / 2, yy, ww, hh) for n, v, ww, hh, yy in parts)
    return Placement(pid, ' + '.join({'poli': 'Selo Poli', 'usp': 'Logo USP'}.get(p[0], p[0]) for p in parts),
                     panel, -maxw / 2, top, maxw, H, art, tecnica, cores)


# ------------------------------------------------------------------ elementos de acabamento (so mockup)

def tee_finish(panel, g, fab):
    """Costuras de barra/manga (so para visualizacao)."""
    G = L.GARMENTS[g]
    s = 'rgba(0,0,0,0.18)' if fab != BLACK_FAB else 'rgba(255,255,255,0.07)'
    if panel in ('frente', 'costas'):
        y = G['L'] - 22
        return (f'<path d="M-300 {y} H300 M-300 {y + 6} H300" stroke="{s}" stroke-width="0.8" stroke-dasharray="2 1.4" fill="none"/>')
    if panel.startswith('manga'):
        y = G['SL'] - 20
        return f'<path d="M-230 {y} H230 M-230 {y + 6} H230" stroke="{s}" stroke-width="0.8" stroke-dasharray="2 1.4" fill="none"/>'
    return ''


def polo_finish(panel, fab, rib, stripes, btn='#f2f2f2'):
    G = L.GARMENTS['polo']
    out = ''
    shade = 'rgba(0,0,0,0.22)' if fab != BLACK_FAB else 'rgba(255,255,255,0.10)'
    if panel == 'frente':
        pw, pl, y0 = G['placketW'] / 2, G['placketL'], G['FND'] - 6
        out += (f'<rect x="{-pw}" y="{y0}" width="{2 * pw}" height="{pl}" fill="{fab}" stroke="{shade}" stroke-width="1.6"/>'
                f'<path d="M{-pw + 3} {y0} V{y0 + pl - 3} H{pw - 3} V{y0}" stroke="{shade}" stroke-width="0.7" stroke-dasharray="2 1.4" fill="none"/>'
                f'<path d="M0 {y0} V{y0 + pl}" stroke="{shade}" stroke-width="0.6"/>')
        for by in (y0 + 62, y0 + 118):
            out += (f'<circle cx="0" cy="{by}" r="6" fill="{btn}" stroke="rgba(0,0,0,0.25)" stroke-width="0.6"/>'
                    f'<circle cx="-1.6" cy="{by - 1.6}" r="0.9" fill="rgba(0,0,0,0.4)"/><circle cx="1.6" cy="{by - 1.6}" r="0.9" fill="rgba(0,0,0,0.4)"/>'
                    f'<circle cx="-1.6" cy="{by + 1.6}" r="0.9" fill="rgba(0,0,0,0.4)"/><circle cx="1.6" cy="{by + 1.6}" r="0.9" fill="rgba(0,0,0,0.4)"/>')
        out += f'<path d="M-300 {G["L"] - 20} H300" stroke="{shade}" stroke-width="0.8" stroke-dasharray="2 1.4"/>'
    if panel == 'costas':
        out += f'<path d="M-300 {G["L"] - 20} H300" stroke="{shade}" stroke-width="0.8" stroke-dasharray="2 1.4"/>'
    if panel.startswith('manga'):
        y = G['SL'] - 26
        out += f'<rect x="-230" y="{y}" width="460" height="60" fill="{rib}"/>'
        out += rib_lines(-230, y, 460, 60, rib)
        for (off, h, c) in stripes:
            out += f'<rect x="-230" y="{y + 26 * off}" width="460" height="{h * 26}" fill="{c}"/>'
    return out


def rib_lines(x, y, w, h, base):
    lines = ''.join(f'<path d="M{x + i:.1f} {y} v{h}"/>' for i in range(0, int(w), 3))
    return f'<g stroke="rgba(0,0,0,0.13)" stroke-width="0.9">{lines}</g>'


def gola_panel(rib, stripes=()):
    """Textura da gola. v: 0 = costura no decote, 1 = borda externa. stripes: (inicio, espessura, cor) em fracao."""
    out = f'<rect x="0" y="0" width="1000" height="120" fill="{rib}"/>'
    for (a, h, c) in stripes:
        out += f'<rect x="0" y="{a * 120:.1f}" width="1000" height="{h * 120:.1f}" fill="{c}"/>'
    out += rib_lines(0, 0, 1000, 120, rib)
    return out

# ------------------------------------------------------------------ graficos especiais


def circle_3pts(p1, p2, p3):
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def orbit_lines_art(color, sat_color, accent, n=5, gap=9.0, sw=1.6):
    """Arcos orbitais da frente (modelo Orbit). Coordenadas absolutas do painel frente."""
    cx, cy, R = circle_3pts((-205, -15), (-95, 330), (262, 610))
    out = []
    for i in range(n):
        r = R + (i - (n - 1) / 2) * gap
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
    clip = L.body_outline('algodao', 'frente')
    # satelite no arco central
    ang = math.atan2(250 - cy, -118 - cx)
    sx, sy = cx + R * math.cos(ang), cy + R * math.sin(ang)
    tang = math.degrees(ang) + 90
    sat = (f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="15" fill="{accent}" opacity="0.18"/>'
           f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="9" fill="{BLACK_FAB}"/>' + cubesat(sx, sy + 5, 9.5, sat_color, panel=accent, sw=1.1))
    return (f'<clipPath id="orbclip"><path d="{clip}"/></clipPath>'
            f'<g clip-path="url(#orbclip)">{"".join(out)}</g>{sat}')


def ground_track(x0, x1, yc, amp, period, phase, color, sw=1.8, dash='7 5'):
    pts = []
    n = 160
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = yc - amp * math.sin(2 * math.pi * (x + phase) / period)
        pts.append(f'{x:.1f} {y:.1f}')
    return f'<path d="M{" L".join(pts)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-dasharray="{dash}" stroke-linecap="round"/>'


def blueprint_art(c, accent):
    """Desenho técnico do CubeSat 1U (costas do modelo Blueprint). Caixa local 340 x 330."""
    out = [f'<g fill="none" stroke="{c}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">']
    ox, oy = 170, 175  # centro
    s = 92  # meia aresta projetada
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    hgt = 210
    P = lambda x, y, z: (ox + (x - y) * c30, oy + (x + y) * s30 - z)
    # vertices do cubo: x,y em [-s/1.6, s/1.6]; z em [-hgt/2, hgt/2]
    a = s * 0.95
    V = {k: P(*v) for k, v in {
        'A': (-a, -a, hgt / 2), 'B': (a, -a, hgt / 2), 'C': (a, a, hgt / 2), 'D': (-a, a, hgt / 2),
        'E': (-a, -a, -hgt / 2), 'F': (a, -a, -hgt / 2), 'G': (a, a, -hgt / 2), 'H': (-a, a, -hgt / 2)}.items()}
    path = lambda *ks: 'M' + ' L'.join(f'{V[k][0]:.1f} {V[k][1]:.1f}' for k in ks)
    out.append(f'<path d="{path("A", "B", "C", "D")} Z"/>')
    out.append(f'<path d="{path("D", "C", "G", "H")} Z"/>')
    out.append(f'<path d="{path("C", "B", "F", "G")} Z"/>')
    # trilhos (rails) nas arestas visiveis
    for k1, k2 in (('D', 'H'), ('C', 'G'), ('B', 'F')):
        (x1, y1), (x2, y2) = V[k1], V[k2]
        out.append(f'<path d="M{x1 + 4:.1f} {y1 + 2:.1f} L{x2 + 4:.1f} {y2 + 2:.1f}" stroke-width="0.6" opacity="0.7"/>')
    # paineis solares: 2x3 celulas em cada face lateral
    def face_grid(k0, k1, k2, k3, nu=2, nv=3, inset=0.09):
        p0, p1, p2, p3 = (V[k] for k in (k0, k1, k2, k3))
        g = []
        for i in range(nu):
            for j in range(nv):
                def pt(u, v):
                    x = p0[0] + (p1[0] - p0[0]) * u + (p3[0] - p0[0]) * v
                    y = p0[1] + (p1[1] - p0[1]) * u + (p3[1] - p0[1]) * v
                    return x, y
                u0, u1 = (i + inset) / nu, (i + 1 - inset) / nu
                v0, v1 = (j + inset) / nv, (j + 1 - inset) / nv
                q = [pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1)]
                g.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in q) + ' Z')
        return f'<path d="{" ".join(g)}" stroke-width="0.8" fill="{accent}" fill-opacity="0.22"/>'
    out.append(face_grid('D', 'C', 'G', 'H'))
    out.append(face_grid('C', 'B', 'F', 'G'))
    # antena patch no topo
    cxm, cym = (V['A'][0] + V['C'][0]) / 2, (V['A'][1] + V['C'][1]) / 2
    q = [P(-a * 0.45, -a * 0.45, hgt / 2), P(a * 0.45, -a * 0.45, hgt / 2), P(a * 0.45, a * 0.45, hgt / 2), P(-a * 0.45, a * 0.45, hgt / 2)]
    out.append('<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in q) + f' Z" fill="{accent}" fill-opacity="0.35"/>')
    # monopolos (antenas)
    for (px, py, dx, dy) in ((V['B'][0], V['B'][1] + 30, 70, -40), (V['D'][0], V['D'][1] + 30, -70, -40)):
        out.append(f'<path d="M{px:.1f} {py:.1f} l{dx} {dy}" stroke-width="1.1"/><circle cx="{px + dx:.1f}" cy="{py + dy:.1f}" r="1.8" fill="{c}"/>')
    out.append('</g>')
    # cotas
    dim = [f'<g stroke="{c}" stroke-width="0.6" fill="none" opacity="0.85">']
    def dline(p, q, off, label, pos=0.5, rot=None):
        (x1, y1), (x2, y2) = p, q
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * off, dx / ln * off
        a1 = (x1 + nx, y1 + ny); a2 = (x2 + nx, y2 + ny)
        dim.append(f'<path d="M{x1:.1f} {y1:.1f} L{a1[0] + nx * 0.25:.1f} {a1[1] + ny * 0.25:.1f} M{x2:.1f} {y2:.1f} L{a2[0] + nx * 0.25:.1f} {a2[1] + ny * 0.25:.1f}"/>')
        dim.append(f'<path d="M{a1[0]:.1f} {a1[1]:.1f} L{a2[0]:.1f} {a2[1]:.1f}"/>')
        for (ax_, ay_, sg) in ((a1[0], a1[1], 1), (a2[0], a2[1], -1)):
            ux, uy = dx / ln * sg, dy / ln * sg
            dim.append(f'<path d="M{ax_:.1f} {ay_:.1f} l{(ux * 5 - uy * 1.6):.1f} {(uy * 5 + ux * 1.6):.1f} M{ax_:.1f} {ay_:.1f} l{(ux * 5 + uy * 1.6):.1f} {(uy * 5 - ux * 1.6):.1f}"/>')
        mx, my = a1[0] + dx * pos + nx * 0.55, a1[1] + dy * pos + ny * 0.55
        r = rot if rot is not None else math.degrees(math.atan2(dy, dx))
        if r > 90 or r < -90:
            r += 180
        lab.append(f'<g transform="translate({mx:.1f} {my:.1f}) rotate({r:.1f})">{text(label, 0, 3.2, 9, c, "middle")}</g>')
    lab = []
    dline(V['H'], V['G'], 18, '100')
    dline(V['G'], V['F'], 18, '100')
    dline(V['B'], V['F'], -26, '113', rot=-90)
    dim.append('</g>')
    # mira nos cantos
    marks = ''
    for (mx, my) in ((8, 8), (332, 8), (8, 322), (332, 322)):
        marks += f'<path d="M{mx - 6} {my} h12 M{mx} {my - 6} v12" stroke="{c}" stroke-width="0.6" opacity="0.6"/>'
    # orbita eliptica atras
    orb = (f'<ellipse cx="{ox}" cy="{oy + 10}" rx="165" ry="52" fill="none" stroke="{accent}" stroke-width="1.2" '
           f'stroke-dasharray="5 4" transform="rotate(-14 {ox} {oy + 10})"/>')
    return orb + ''.join(out) + ''.join(dim) + ''.join(lab) + marks + text('1U', 300, 300, 20, c, 'end')


def halftone_band(x0, y0, x1, y1, width, color, cell=7.0, rmax=2.9, side=1):
    """Pontos meio-tom que desaparecem a partir de uma faixa (estilo jersey)."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy * side, ux * side
    out = []
    steps = int(ln / cell)
    rows = int(width / cell)
    for i in range(steps + 1):
        for j in range(rows):
            t = j / rows
            r = rmax * (1 - t) ** 1.3
            if r < 0.35:
                continue
            off = (cell / 2) if j % 2 else 0
            px = x0 + ux * (i * cell + off) + nx * j * cell
            py = y0 + uy * (i * cell + off) + ny * j * cell
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}"/>')
    return f'<g fill="{color}">{"".join(out)}</g>'


def name_plate(cx, y, w, h, fab, edge, txt_color, name='NAME', size=44, plate=None):
    plate = plate or 'none'
    out = (f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="6" fill="{plate}" stroke="{edge}" stroke-width="1.4" stroke-dasharray="0"/>')
    if name:
        d, tw, cap = L.text_d(name, size, 'R', 0.06)
        k = min(1, (w - 40) / tw)
        out += f'<g transform="translate({cx - tw * k / 2:.2f} {y + h / 2 + cap * k / 2:.2f}) scale({k:.4f})"><path fill="{txt_color}" d="{d}"/></g>'
    return out


# ------------------------------------------------------------------ MODELOS

def build_models():
    M = []
    poli_usp_white = [('poli', 'white', 52, None), ('usp', 'white', 50, None)]
    poli_usp_dark = [('poli', 'dark', 52, None), ('usp', 'original', 50, None)]
    BR_COLORS = [('Verde', L.BR_GREEN, 'Pantone 355 C'), ('Amarelo', L.BR_YELLOW, 'Pantone 116 C'),
                 ('Azul', L.BR_BLUE, 'Pantone 280 C'), ('Branco', '#ffffff', 'White')]
    C_WHITE = ('Branco', '#ffffff', 'White')
    C_BLUE = ('Azul PoliSat', L.POLISAT_BLUE, 'Pantone 2945 C (aprox.)')
    C_INK = ('Preto', L.INK, 'Pantone Black 6 C')
    SILK = 'Silk-screen (serigrafia) com tinta plastisol, ou DTF'

    # ================= ALGODAO 01 — ORBIT (preto)
    fab = BLACK_FAB
    pl = [
        Placement('frente_orbitas', 'Órbitas + CubeSat', 'frente', -300, -20, 600, 780,
                  lambda web: full(orbit_lines_art('#ffffff', '#ffffff', L.POLISAT_BLUE)), SILK, [C_WHITE, C_BLUE],
                  crop=(-262, -2, 524, 724)),
        place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', 'white', 112, 150, w=105,
                   tecnica=SILK, cores=[C_WHITE, C_BLUE]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp_white, 40, 12, SILK, [C_WHITE], 'manga_esq_poli_usp'),
        place_logo('costas_icone', 'Símbolo PoliSat (nuca)', 'costas', 'polisat_icon', 'white', 0, 52, w=46,
                   tecnica=SILK, cores=[C_WHITE, C_BLUE]),
        Placement('costas_patrocinadores', 'Patrocinadores', 'costas', -160, 400, 320, 190,
                  lambda web: sponsor_grid(0, 0, 320, 190, 'white'), SILK, [C_WHITE]),
    ]
    M.append(dict(id='A1', slug='algodao_01_orbit', nome='Orbit', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor PRETO', cor_tecido='Preto',
                  tecnica=SILK, placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Trajetória orbital cruzando o peito até um CubeSat — evolução da camiseta atual da equipe.'))

    # ================= ALGODAO 02 — GROUND TRACK (branca)
    fab = WHITE_FAB
    def gt_front(web):
        return (ground_track(-262, 262, 318, 62, 560, 40, L.POLISAT_BLUE) +
                f'<circle cx="-118" cy="{318 - 62 * math.sin(2 * math.pi * (-118 + 40) / 560):.1f}" r="11" fill="none" stroke="{L.POLISAT_BLUE}" stroke-width="1.4"/>'
                f'<circle cx="-118" cy="{318 - 62 * math.sin(2 * math.pi * (-118 + 40) / 560):.1f}" r="4.4" fill="{L.POLISAT_BLUE}"/>')
    def gt_back(web):
        # continua a onda pelas costas (visto de tras)
        return ground_track(-262, 262, 250, 62, 560, 40 + 262 * 2, L.POLISAT_BLUE)
    pl = [
        Placement('frente_groundtrack', 'Ground track (onda)', 'frente', -300, -20, 600, 780,
                  lambda web: full(gt_front(web)), SILK, [C_BLUE], crop=(-263, 238, 526, 158)),
        place_logo('peito_polisat', 'Logo PoliSat (centro do peito)', 'frente', 'polisat', 'dark', 0, 135, w=200,
                   tecnica=SILK, cores=[C_INK, C_BLUE]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp_dark, 40, 12, SILK, [C_INK], 'manga_esq_poli_usp'),
        place_logo('costas_icone', 'Símbolo PoliSat (nuca)', 'costas', 'polisat_icon', 'dark', 0, 52, w=46,
                   tecnica=SILK, cores=[C_INK, C_BLUE]),
        Placement('costas_groundtrack', 'Ground track (continuação)', 'costas', -300, -20, 600, 780,
                  lambda web: full(gt_back(web)), SILK, [C_BLUE], crop=(-263, 178, 526, 144)),
        Placement('costas_patrocinadores', 'Patrocinadores (cor)', 'costas', -165, 360, 330, 200,
                  lambda web: sponsor_grid(0, 0, 330, 200, 'light_bg'), 'DTF (full color) — logos nas cores originais',
                  [('CMYK', '#888888', 'Cores originais das marcas')]),
    ]
    M.append(dict(id='A2', slug='algodao_02_groundtrack', nome='Ground Track', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor BRANCO', cor_tecido='Branco',
                  tecnica=SILK + ' / patrocinadores em DTF', placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Logo grande no peito com o rastro de solo (ground track) do satelite dando a volta na camiseta.'))

    # ================= ALGODAO 03 — BLUEPRINT (marinho)
    fab = NAVY_FAB
    pl = [
        place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', 'navy', 112, 150, w=100,
                   tecnica=SILK, cores=[C_WHITE, ('Azul claro', L.POLISAT_BLUE_LIGHT, 'Pantone 2727 C (aprox.)')]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp_white, 40, 12, SILK, [C_WHITE], 'manga_esq_poli_usp'),
        place_logo('costas_usp', 'Logo USP (nuca)', 'costas', 'usp', 'white', 0, 50, w=58, tecnica=SILK, cores=[C_WHITE]),
        Placement('costas_blueprint', 'Desenho técnico CubeSat 1U', 'costas', -170, 92, 340, 330,
                  lambda web: blueprint_art('#ffffff', L.POLISAT_BLUE_LIGHT), SILK,
                  [C_WHITE, ('Azul claro', L.POLISAT_BLUE_LIGHT, 'Pantone 2727 C (aprox.)')]),
        Placement('costas_patrocinadores', 'Patrocinadores', 'costas', -155, 472, 310, 170,
                  lambda web: sponsor_grid(0, 0, 310, 170, 'white'), SILK, [C_WHITE]),
    ]
    M.append(dict(id='A3', slug='algodao_03_blueprint', nome='Blueprint', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor AZUL MARINHO', cor_tecido='Azul marinho',
                  tecnica=SILK, placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Frente minimalista; nas costas, desenho técnico de um CubeSat 1U com cotas reais (100 mm).'))

    # ================= POLOS (bordado)
    BORD = 'Bordado (matriz a partir do vetor)'
    CN = {BLACK_FAB: 'preta', NAVY_FAB: 'azul marinho', WHITE_FAB: 'branca', L.POLISAT_BLUE: 'azul PoliSat',
          '#ffffff': 'branco', L.POLISAT_BLUE_LIGHT: 'azul claro'}
    def polo(id_, slug, nome, fab, cor, pol_var, logos_var, flag_w, rib, stripes, conceito, cores_logo, btn):
        pl = [
            place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', pol_var, 108, 168, w=88,
                       tecnica=BORD, cores=cores_logo),
            flag_placement('manga_dir', 0, 52, flag_w, 'Bordado'),
            place_logo('manga_esq_poli', 'Selo Escola Politécnica', 'manga_esq', 'poli', logos_var, 0, 44, w=50,
                       tecnica=BORD, cores=[cores_logo[0]]),
            place_logo('costas_usp', 'Logo USP (nuca, abaixo da gola)', 'costas', 'usp', 'white' if logos_var == 'white' else 'original',
                       0, 58, w=52, tecnica=BORD, cores=[cores_logo[0]]),
        ]
        gstr = [(0.80, 0.05, stripes[0]), (0.88, 0.05, stripes[1])]
        cuff = [(0.35, 0.14, stripes[0]), (0.62, 0.14, stripes[1])]
        return dict(id=id_, slug=slug, nome=nome, garment='polo', fabric=fab, tecido=f'Malha piquet (algodão/poliéster) — cor {cor}',
                    cor_tecido=cor, tecnica=BORD, placements=pl, gola=gola_panel(rib, gstr), cuff=(rib, cuff), btn=btn,
                    sublimacao=False, conceito=conceito,
                    gola_desc=f'Gola e punhos em ribana {CN[rib]} com 2 frisos ({CN[stripes[0]]} e {CN[stripes[1]]})')
    M.append(polo('P1', 'polo_01_classic_black', 'Classic Black', BLACK_FAB, 'PRETO', 'white', 'white', 64,
                  BLACK_FAB, (L.POLISAT_BLUE, L.POLISAT_BLUE),
                  'Polo preta clássica com frisos azul PoliSat na gola e nos punhos.', [C_WHITE, C_BLUE], '#1b1b1d'))
    M.append(polo('P2', 'polo_02_navy', 'Navy', NAVY_FAB, 'AZUL MARINHO', 'navy', 'white', 64,
                  NAVY_FAB, ('#ffffff', L.POLISAT_BLUE_LIGHT),
                  'Polo marinho com frisos branco + azul claro; bordados em branco.', [C_WHITE, ('Azul claro', L.POLISAT_BLUE_LIGHT, 'linha azul claro')], '#f2f2f2'))
    M.append(polo('P3', 'polo_03_white', 'White', WHITE_FAB, 'BRANCO', 'dark', 'dark', 64,
                  WHITE_FAB, (L.POLISAT_BLUE, '#141416'),
                  'Polo branca com frisos azul PoliSat e preto; bordados em preto e azul.', [C_INK, C_BLUE], '#f2f2f2'))

    # ================= DRY-FIT (sublimacao total — missao Hermes)
    SUB = 'Sublimação total (full print) em tecido dry-fit poliéster'
    M.append(dict(id='D1', slug='dryfit_01_messenger', nome='Messenger', garment='dryfit', fabric=BLACK_FAB,
                  tecido='Dry-fit 100% poliéster (branco p/ sublimação)', cor_tecido='Branco (sublimado preto)',
                  tecnica=SUB, sublimacao=True, panels=dry_messenger, gola=gola_panel('#141416', [(0.55, 0.12, L.H_ORANGE)]),
                  gola_desc='Gola e punhos em ribana preta com friso laranja; punho da manga sublimado em degradê vermelho-laranja',
                  conceito='Faixa diagonal vermelho→laranja com meio-tom, como uma trajetória de lançamento; patch Hermes no peito.'))
    M.append(dict(id='D2', slug='dryfit_02_horizon', nome='Horizon', garment='dryfit', fabric='#0b1226',
                  tecido='Dry-fit 100% poliéster (branco p/ sublimação)', cor_tecido='Branco (sublimado)',
                  tecnica=SUB, sublimacao=True, panels=dry_horizon, gola=gola_panel('#0b1226', [(0.55, 0.12, L.H_ORANGE)]),
                  gola_desc='Gola em ribana azul-noite com friso laranja; punho da manga sublimado em degradê vermelho-laranja',
                  conceito='Horizonte da Terra com aviões transmitindo ADS-B e o CubeSat em órbita — a missão Hermes em uma imagem.'))
    M.append(dict(id='D3', slug='dryfit_03_livery', nome='Livery', garment='dryfit', fabric='#f4f4f2',
                  tecido='Dry-fit 100% poliéster (branco p/ sublimação)', cor_tecido='Branco (sublimado)',
                  tecnica=SUB, sublimacao=True, panels=dry_livery, gola=gola_panel('#141416', [(0.55, 0.12, L.H_RED)]),
                  gola_desc='Gola em ribana preta com friso vermelho; mangas sublimadas em degradê com punho preto',
                  conceito='Pintura estilo equipe de corrida / baja: blocos angulados vermelho, laranja e preto; patrocinadores em cor.'))
    return M

# ------------------------------------------------------------------ DRY-FIT paineis
# Cada funcao retorna {painel: svg} — arte completa com sangria (o painel inteiro e impresso).


def _defs_grad(gid, stops, x1=0, y1=0, x2=1, y2=0, units='objectBoundingBox', extra=''):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"{" stop-opacity=" + chr(34) + str(op) + chr(34) if op is not None else ""}/>'
                for o, c, op in stops)
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="{units}"{extra}>{s}</linearGradient>'


def _frame_rect(panel, fill):
    x, y, w, h = L.FRAME[panel]
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def _sleeve_common(panel, base, cuff_grad, logos_var, web, extra=''):
    G = L.GARMENTS['dryfit']
    out = _frame_rect(panel, base) + extra
    out += f'<rect x="-230" y="{G["SL"] - 34}" width="460" height="64" fill="url(#{cuff_grad})"/>'
    if panel == 'manga_dir':
        out += put_center('bandeira', 'original', 0, 82, w=74)
    else:
        out += put_center('poli', logos_var, 0, 70, w=50)
        out += put_center('usp', 'white' if logos_var == 'white' else 'original', 0, 128, w=48)
    return out


def dry_messenger(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    defs = (_defs_grad('mband', [(0, L.H_RED, None), (0.6, L.H_ORANGE, None), (1, L.H_AMBER, None)], -300, 700, 300, 100, 'userSpaceOnUse') +
            _defs_grad('mcuff', [(0, L.H_RED, None), (1, L.H_ORANGE, None)]) +
            _defs_grad('mhem', [(0, L.H_RED, None), (1, L.H_ORANGE, None)]))
    P = {}
    # frente: faixa de (300,760) a (-300,120)
    x0, y0, x1, y1 = 330, 900, -330, 260
    def band(off, w):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
        a = (x0 + nx * off, y0 + ny * off); b = (x1 + nx * off, y1 + ny * off)
        c = (x1 + nx * (off + w), y1 + ny * (off + w)); d = (x0 + nx * (off + w), y0 + ny * (off + w))
        return 'M' + ' L'.join(f'{p[0]:.1f} {p[1]:.1f}' for p in (a, b, c, d)) + ' Z'
    f = _frame_rect('frente', BLACK_FAB)
    f += halftone_band(x0, y0, x1, y1, 120, L.H_RED, side=-1)
    f += f'<path d="{band(0, 120)}" fill="url(#mband)"/>'
    f += f'<path d="{band(132, 6)}" fill="{L.H_AMBER}"/><path d="{band(146, 3)}" fill="{L.H_ORANGE}"/>'
    f += f'<path d="{band(-14, 4)}" fill="#ffffff"/>'
    f += put('polisat', 'white', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    # costas
    c = _frame_rect('costas', BLACK_FAB)
    c += f'<rect x="-300" y="{G["L"] - 48}" width="600" height="68" fill="url(#mhem)"/>'
    c += halftone_band(-330, G['L'] - 48, 330, G['L'] - 48, 70, L.H_RED, side=1)
    c += put_center('polisat', 'white', 0, 112, w=150)
    hd, hw, hc = L.text_d('HERMES', 64, 'R', 0.04)
    c += (f'<g transform="translate({-hw / 2:.1f} 262)"><path d="{hd}" fill="url(#mband)"/></g>' if False else
          f'<g transform="translate({-hw / 2:.1f} 262)"><path d="{hd}" fill="{L.H_ORANGE}"/></g>')
    c += text('MISSION', 0, 192, 17, '#ffffff', 'middle', ls=0.5)
    c += f'<path d="M-200 292 H200" stroke="{L.H_RED}" stroke-width="1.5"/>'
    c += sponsor_grid(-165, 318, 330, 200, 'white')
    c += f'<path d="M-200 540 H200" stroke="{L.H_RED}" stroke-width="1.5"/>'
    c += name_plate(0, 568, 340, 84, BLACK_FAB, L.H_ORANGE, '#ffffff', name, 46, plate='#1d1d20')
    P['costas'] = c
    stripe = f'<path d="M-230 {G["SL"] - 46} H230" stroke="{L.H_AMBER}" stroke-width="3"/>'
    P['manga_dir'] = _sleeve_common('manga_dir', BLACK_FAB, 'mcuff', 'white', web, stripe)
    P['manga_esq'] = _sleeve_common('manga_esq', BLACK_FAB, 'mcuff', 'white', web, stripe)
    return P, defs


def _earth(cx, cy, R, glow_id, earth_id, grid_color='#3fa9f5', w=600, sw=0.7):
    out = (f'<circle cx="{cx}" cy="{cy}" r="{R + 26}" fill="url(#{glow_id})"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{earth_id})"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{L.H_AMBER}" stroke-width="3"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{R + 6}" fill="none" stroke="{L.H_ORANGE}" stroke-width="1.6" opacity="0.6"/>')
    g = [f'<clipPath id="ecl{cy}"><circle cx="{cx}" cy="{cy}" r="{R - 2}"/></clipPath><g clip-path="url(#ecl{cy})" fill="none" stroke="{grid_color}" stroke-width="{sw}" opacity="0.45">']
    for k in range(1, 9):
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R * abs(math.cos(k * math.pi / 18)):.1f}" ry="{R}"/>')
    for k in range(1, 10):
        yy = cy - R + k * 40
        g.append(f'<path d="M{cx - R} {yy} H{cx + R}"/>')
    g.append('</g>')
    return out + ''.join(g)


def dry_horizon(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    defs = (_defs_grad('hsky', [(0, '#05070f', None), (0.55, '#0b1730', None), (1, '#1a2550', None)], 0, 0, 0, 1) +
            '<radialGradient id="hglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0.93" stop-color="#ff6a00" stop-opacity="0.9"/>'
            '<stop offset="0.965" stop-color="#e30613" stop-opacity="0.45"/><stop offset="1" stop-color="#e30613" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="hearth" cx="0.5" cy="0.08" r="0.6"><stop offset="0" stop-color="#1f5d8c"/><stop offset="0.5" stop-color="#0f2f55"/>'
            '<stop offset="1" stop-color="#07152b"/></radialGradient>' +
            _defs_grad('hcuff', [(0, L.H_RED, None), (1, L.H_ORANGE, None)]))
    P = {}
    R = 1250
    ecy = 470 + R
    f = _frame_rect('frente', 'url(#hsky)')
    f += stars(-300, -20, 600, 520, 260, 11, avoid=lambda x, y: (x > 40 and y < 280 and x < 190) or (x < -40 and x > -200 and y < 260))
    # orbita tracejada + cubesat
    f += f'<path d="M-320 300 Q0 120 320 300" fill="none" stroke="#7fb2ff" stroke-width="1.3" stroke-dasharray="6 5" opacity="0.8"/>'
    f += cubesat(10, 206, 12, '#ffffff', panel=L.POLISAT_BLUE, sw=1.1, rot=20)
    f += _earth(0, ecy, R, 'hglow', 'hearth')
    # avioes + ondas ADS-B
    for (px, py, rot) in ((-190, 440, 70), (-60, 418, 95), (95, 425, 105), (215, 452, 120)):
        f += plane(px, py, 22, rot, '#ffffff')
        for k in (1, 2):
            f += f'<path d="M{px - 9 * k - 6} {py - 10 - 6 * k} Q{px} {py - 18 - 9 * k} {px + 9 * k + 6} {py - 10 - 6 * k}" fill="none" stroke="#ffae00" stroke-width="1.4" opacity="{0.9 - 0.3 * k:.2f}"/>'
        f += f'<path d="M{px} {py - 14} L10 218" stroke="#ffae00" stroke-width="0.7" stroke-dasharray="2 4" opacity="0.55"/>'
    f += put('polisat', 'white', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    c = _frame_rect('costas', 'url(#hsky)')
    c += stars(-300, -20, 600, 700, 300, 23, avoid=lambda x, y: (abs(x) < 120 and 60 < y < 250) or (abs(x) < 185 and 535 < y < 645))
    c += _earth(0, 690 + R, R, 'hglow', 'hearth')
    c += hermes_patch(-92, 60, 184, web)
    c += sponsor_grid(-165, 290, 330, 200, 'white')
    c += name_plate(0, 548, 330, 80, '#0b1226', '#ffae00', '#ffffff', name, 44, plate='none')
    P['costas'] = c
    st = stars(-230, -30, 460, 200, 70, 5)
    P['manga_dir'] = _sleeve_common('manga_dir', '#0b1730', 'hcuff', 'white', web, st)
    P['manga_esq'] = _sleeve_common('manga_esq', '#0b1730', 'hcuff', 'white', web, st)
    return P, defs


def dry_livery(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    base = '#f4f4f2'
    defs = (_defs_grad('lred', [(0, L.H_RED, None), (1, L.H_ORANGE, None)], 0, 1, 1, 0) +
            _defs_grad('lred2', [(0, L.H_ORANGE, None), (1, L.H_RED, None)], 0, 0, 1, 1) +
            _defs_grad('lsl', [(0, L.H_RED, None), (1, L.H_ORANGE, None)], 0, 0, 0, 1))
    P = {}
    f = _frame_rect('frente', base)
    # blocos angulados laterais (simetricos) — como carenagem
    for sg in (1, -1):
        f += f'<path d="M{sg * 320} 300 L{sg * 320} 780 L{sg * 60} 780 L{sg * 200} 560 Z" fill="url(#lred)"/>'
        f += f'<path d="M{sg * 320} 470 L{sg * 320} 780 L{sg * 150} 780 L{sg * 250} 600 Z" fill="#141416"/>'
        f += f'<path d="M{sg * 200} 545 L{sg * 320} 330 L{sg * 320} 300 L{sg * 186} 540 Z" fill="#141416"/>'
    # chevron central
    f += f'<path d="M-60 780 L0 700 L60 780 L40 780 L0 726 L-40 780 Z" fill="#141416"/>'
    f += f'<path d="M-300 -20 H300 V8 H-300 Z" fill="#141416"/>'
    f += put('polisat', 'dark', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    c = _frame_rect('costas', base)
    for sg in (1, -1):
        c += f'<path d="M{sg * 320} 260 L{sg * 320} 780 L{sg * 230} 780 L{sg * 230} 420 Z" fill="url(#lred2)"/>'
        c += f'<path d="M{sg * 320} 540 L{sg * 320} 780 L{sg * 262} 780 L{sg * 262} 600 Z" fill="#141416"/>'
    c += f'<path d="M-300 -20 H300 V30 H-300 Z" fill="#141416"/>'
    c += put_center('polisat', 'dark', 0, 104, w=160)
    c += sponsor_grid(-170, 200, 340, 250, 'light_bg', scale=1.15)
    c += f'<rect x="-300" y="560" width="600" height="96" fill="#141416"/>'
    c += f'<rect x="-300" y="656" width="600" height="10" fill="url(#lred)"/>'
    c += name_plate(0, 568, 360, 80, '#141416', 'none', '#ffffff', name, 48, plate='#141416')
    c += put_center('usp', 'original', -150, 712, w=50) + put_center('poli', 'dark', 150, 712, w=44)
    P['costas'] = c
    def sl(panel):
        out = _frame_rect(panel, 'url(#lsl)')
        out += f'<path d="M-230 {G["SL"] - 34} H230 V240 H-230 Z" fill="#141416"/>'
        out += f'<path d="M-230 {G["SL"] - 44} H230" stroke="#ffffff" stroke-width="3"/>'
        if panel == 'manga_dir':
            out += f'<rect x="-41" y="{82 - 28}" width="82" height="56" fill="#ffffff"/>' + put_center('bandeira', 'original', 0, 82, w=74)
        else:
            out += put_center('poli', 'white', 0, 70, w=50) + put_center('usp', 'white', 0, 128, w=48)
        return out
    P['manga_dir'] = sl('manga_dir')
    P['manga_esq'] = sl('manga_esq')
    return P, defs


# ------------------------------------------------------------------ montagem dos paineis

def panels_for(m, web=False, name='NAME'):
    """Retorna {painel: svg_completo} para mockup/3D (inclui cor do tecido e acabamentos)."""
    out = {}
    if m['sublimacao']:
        P, defs = m['panels'](web, name)
        for k, body in P.items():
            out[k] = L.svg_doc(L.FRAME[k], body, defs)
    else:
        for k in ('frente', 'costas', 'manga_esq', 'manga_dir'):
            body = _frame_rect(k, m['fabric'])
            if m['garment'] == 'polo' and k == 'frente':
                pass
            for p in m['placements']:
                if p.panel == k:
                    body += p.svg_in_panel(web)
            if m['garment'] == 'polo':
                rib, cuff = m['cuff']
                body += polo_finish(k, m['fabric'], rib, cuff, m['btn'])
            else:
                body += tee_finish(k, m['garment'], m['fabric'])
            out[k] = L.svg_doc(L.FRAME[k], body)
    out['gola'] = L.svg_doc(L.FRAME['gola'], m['gola'])
    return out
