"""Definicao dos 12 modelos de camiseta PoliSat (4 polo, 4 algodao, 4 dry-fit).

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
    'D2': dict(cx=0, y=568, w=360, h=80, size=48, color='#141416'),
    'D3': dict(cx=0, y=470, w=360, h=80, size=48, color='#ffffff'),
    'D4': dict(cx=0, y=568, w=340, h=84, size=46, color='#ffffff'),
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


def ground_track(x0, x1, yc, amp, period, phase, color, sw=1.8, dash='7 5'):
    pts = []
    n = 160
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = yc - amp * math.sin(2 * math.pi * (x + phase) / period)
        pts.append(f'{x:.1f} {y:.1f}')
    return f'<path d="M{" L".join(pts)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-dasharray="{dash}" stroke-linecap="round"/>'


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


# ------------------------------------------------------------------ paleta 2026 (alem de preto/azul/branco)
GRAFITE = '#2d3035'
PETROLEO = '#123c45'
AREIA = '#d8ccb1'
VINHO = '#5b1e2b'
SKY = '#6fb7ff'          # tinta azul-ceu
CREAM = '#efe6d2'        # tinta creme
EMBER = '#e8611a'        # tinta laranja
INK_NAVY = '#16213a'     # tinta marinho
SILVER = '#b9bec7'       # linha prata (bordado)
GOLD = '#d9a520'


def polo_finish2(panel, fab, rib, stripes, btn, placket=None):
    """Acabamentos da polo para o mockup: carcela, botoes, barra e punhos."""
    G = L.GARMENTS['polo']
    out = ''
    light = fab in (WHITE_FAB, AREIA)
    shade = 'rgba(0,0,0,0.22)' if light else 'rgba(255,255,255,0.10)'
    if panel == 'frente':
        pw, pl, y0 = G['placketW'] / 2, G['placketL'], G['FND'] - 6
        pf = placket or fab
        out += (f'<rect x="{-pw}" y="{y0}" width="{2 * pw}" height="{pl}" fill="{pf}" stroke="{shade}" stroke-width="1.6"/>'
                f'<path d="M{-pw + 3} {y0} V{y0 + pl - 3} H{pw - 3} V{y0}" stroke="{shade}" stroke-width="0.7" stroke-dasharray="2 1.4" fill="none"/>'
                f'<path d="M0 {y0} V{y0 + pl}" stroke="{shade}" stroke-width="0.6"/>')
        for by in (y0 + 62, y0 + 118):
            out += (f'<circle cx="0" cy="{by}" r="6" fill="{btn}" stroke="rgba(0,0,0,0.25)" stroke-width="0.6"/>'
                    + ''.join(f'<circle cx="{dx}" cy="{by + dy}" r="0.9" fill="rgba(0,0,0,0.4)"/>' for dx in (-1.6, 1.6) for dy in (-1.6, 1.6)))
    if panel in ('frente', 'costas'):
        out += f'<path d="M-300 {G["L"] - 20} H300" stroke="{shade}" stroke-width="0.8" stroke-dasharray="2 1.4"/>'
    if panel.startswith('manga'):
        y = G['SL'] - 26
        out += f'<rect x="-230" y="{y}" width="460" height="60" fill="{rib}"/>' + rib_lines(-230, y, 460, 60, rib)
        for (off, h, c) in stripes:
            out += f'<rect x="-230" y="{y + 26 * off}" width="460" height="{h * 26}" fill="{c}"/>'
    return out


def sat_wings(cx, cy, s, ink, accent, fill, sw=None, rot=0):
    """Satelite com paineis solares abertos (icone vetorial). s = lado do corpo."""
    sw = sw or s * 0.07
    w, h = s * 1.55, s * 0.62
    g = [f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot})" stroke="{ink}" stroke-width="{sw:.2f}" stroke-linejoin="round">']
    for sg in (-1, 1):
        x0 = sg * (s / 2 + s * 0.35)
        xa = x0 if sg > 0 else x0 - w
        g.append(f'<path d="M{sg * s / 2:.2f} 0 H{x0:.2f}" fill="none"/>')
        g.append(f'<rect x="{xa:.2f}" y="{-h / 2:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{accent}"/>')
        for k in range(1, 4):
            xx = xa + w * k / 4
            g.append(f'<path d="M{xx:.2f} {-h / 2:.2f} V{h / 2:.2f}" stroke-width="{sw * 0.55:.2f}" fill="none"/>')
        g.append(f'<path d="M{xa:.2f} 0 H{xa + w:.2f}" stroke-width="{sw * 0.55:.2f}" fill="none"/>')
    g.append(f'<rect x="{-s / 2:.2f}" y="{-s / 2:.2f}" width="{s:.2f}" height="{s:.2f}" fill="{fill}"/>')
    g.append(f'<path d="M{-s / 2:.2f} {-s / 6:.2f} H{s / 2:.2f} M{-s / 2:.2f} {s / 6:.2f} H{s / 2:.2f}" stroke-width="{sw * 0.55:.2f}" fill="none"/>')
    # antena parabolica
    g.append(f'<path d="M0 {-s / 2:.2f} V{-s * 0.85:.2f}" fill="none"/>'
             f'<path d="M{-s * 0.32:.2f} {-s * 0.95:.2f} Q0 {-s * 0.62:.2f} {s * 0.32:.2f} {-s * 0.95:.2f}" fill="none"/>')
    g.append('</g>')
    return ''.join(g)


def text_arc(txt, cx, cy, r, center_deg, size, fill, font='R', ls=0.12, outside=True):
    """Texto ao longo de um arco (centro do texto em center_deg; 0 = topo, sentido horario)."""
    widths = [L.text_width(ch, size, font) if ch != ' ' else size * 0.32 for ch in txt]
    total = sum(widths) + ls * size * (len(txt) - 1)
    ang_total = total / r
    out = []
    a = math.radians(center_deg) - (ang_total / 2 if outside else -ang_total / 2)
    for ch, wch in zip(txt, widths):
        da = (wch + ls * size) / r
        mid = a + (wch / 2 / r) * (1 if outside else -1)
        if ch != ' ':
            d, _, _ = L.text_d(ch, size, font)
            x = cx + r * math.sin(mid)
            y = cy - r * math.cos(mid)
            rot = math.degrees(mid) + (0 if outside else 180)
            out.append(f'<path fill="{fill}" d="{d}" transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) translate({-wch / 2:.2f} {size * 0.35 if not outside else 0:.2f})"/>')
        a += da * (1 if outside else -1)
    return ''.join(out)


def globe_art(cx, cy, R, ink, accent, fab, n_sat=True):
    """Globo em arame com 3 planos orbitais e CubeSats (A1 Constellation)."""
    o = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{fab}" stroke="{ink}" stroke-width="1.6"/>',
         f'<g fill="none" stroke="{ink}" stroke-width="0.9" opacity="0.55">']
    for k in (1, 2, 3, 4, 5):
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R * abs(math.cos(k * math.pi / 12)):.1f}" ry="{R}"/>')
    for lat in (-60, -30, 0, 30, 60):
        yy = cy - R * math.sin(math.radians(lat)) * 0.96
        hw = R * math.cos(math.radians(lat))
        o.append(f'<ellipse cx="{cx}" cy="{yy:.1f}" rx="{hw:.1f}" ry="{hw * 0.16:.1f}"/>')
    o.append('</g>')
    sats = []
    for i, (rot, rx, ry, t) in enumerate(((-24, 1.55, 0.40, 0.18), (18, 1.45, 0.34, 0.66), (72, 1.38, 0.30, 0.86))):
        dash = '' if i == 0 else ' stroke-dasharray="6 4"'
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R * rx:.1f}" ry="{R * ry:.1f}" fill="none" stroke="{accent}" stroke-width="1.5" '
                 f'transform="rotate({rot} {cx} {cy})"{dash}/>')
        a = 2 * math.pi * t
        px, py = R * rx * math.cos(a), R * ry * math.sin(a)
        rr = math.radians(rot)
        sx, sy = cx + px * math.cos(rr) - py * math.sin(rr), cy + px * math.sin(rr) + py * math.cos(rr)
        sats.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="{fab}"/>' + cubesat(sx, sy + 5, 9, ink, panel=accent, sw=1.1))
    # estacoes de solo
    for (ax, ay) in ((-40, 52), (55, 30), (-70, -10)):
        o.append(f'<path d="M{cx + ax - 4} {cy + ay + 3} L{cx + ax} {cy + ay - 4} L{cx + ax + 4} {cy + ay + 3} Z" fill="{accent}"/>')
    return ''.join(o) + ''.join(sats)


def exploded_art(ink, accent, fab):
    """Vista explodida de um CubeSat 1U com chamadas (A3 Exploded). Caixa local 380 x 420."""
    ox, oy, k = 140, 330, 1.0
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    P = lambda x, y, z: (ox + (x - y) * c30 * k, oy + (x + y) * s30 * k - z * k)
    a = 52
    out, labels = [], []
    def poly(pts, fill, sw=1.2, op=1):
        return (f'<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) +
                f' Z" fill="{fill}" fill-opacity="{op}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>')
    def plate(z, t, top_fill, label, deco=None):
        A_, B_, C_, D_ = (P(-a, -a, z + t), P(a, -a, z + t), P(a, a, z + t), P(-a, a, z + t))
        A0, B0, C0, D0 = (P(-a, -a, z), P(a, -a, z), P(a, a, z), P(-a, a, z))
        s = poly([D_, C_, C0, D0], fab) + poly([C_, B_, B0, C0], fab) + poly([A_, B_, C_, D_], top_fill)
        if deco:
            s += deco(z + t)
        out.append(s)
        lx, ly = B_  # canto direito
        labels.append((lx, ly + (C_[1] - ly) * 0.5, label))
    zs = [0, 70, 140, 205, 265]
    # estrutura 1U (aramado) na base
    def frame(z0):
        h = 60
        s = ''
        for (x, y) in ((-a, -a), (a, -a), (a, a), (-a, a)):
            p0, p1 = P(x, y, z0), P(x, y, z0 + h)
            s += f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{ink}" stroke-width="1.4"/>'
        for zz in (z0, z0 + h):
            q = [P(-a, -a, zz), P(a, -a, zz), P(a, a, zz), P(-a, a, zz)]
            s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in q) + f' Z" fill="none" stroke="{ink}" stroke-width="1.4"/>'
        return s
    out.append(frame(zs[0] - 60))
    labels.append((P(a, -a, -30)[0], P(a, -a, -30)[1], '1U FRAME'))
    def chips(z):
        s = ''
        for (x, y, w) in ((-30, -20, 24), (10, 5, 16), (-5, 30, 12)):
            q = [P(x, y, z), P(x + w, y, z), P(x + w, y + w, z), P(x, y + w, z)]
            s += poly(q, accent, 0.8)
        return s
    def cells(z):
        s = ''
        for i in range(2):
            for j in range(2):
                x0, y0 = -a + 6 + i * (a - 3), -a + 6 + j * (a - 3)
                q = [P(x0, y0, z), P(x0 + a - 9, y0, z), P(x0 + a - 9, y0 + a - 9, z), P(x0, y0 + a - 9, z)]
                s += poly(q, accent, 0.8, 0.55)
        return s
    def batts(z):
        s = ''
        for y in (-25, 15):
            p0, p1 = P(-35, y, z + 6), P(35, y, z + 6)
            s += f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{accent}" stroke-width="10" stroke-linecap="round"/>'
        return s
    def antennas(z):
        s = ''
        c = P(0, 0, z)
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p0 = P(dx * a, dy * a, z)
            p1 = P(dx * (a + 60), dy * (a + 60), z)
            s += f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{ink}" stroke-width="1.3"/>'
        s += f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="5" fill="{accent}" stroke="{ink}" stroke-width="1"/>'
        return s
    plate(zs[0], 4, fab, 'EPS', batts)
    plate(zs[1], 4, fab, 'OBC', chips)
    plate(zs[2], 4, fab, 'PAYLOAD', chips)
    plate(zs[3], 4, fab, 'SOLAR CELLS', cells)
    plate(zs[4], 4, fab, 'ANTENNA', antennas)
    # eixo de montagem
    p0, p1 = P(0, 0, -70), P(0, 0, 320)
    axis = f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{accent}" stroke-width="1" stroke-dasharray="6 4"/>'
    lab = ''
    for i, (lx, ly, t) in enumerate(labels):
        tx = 282
        lab += (f'<path d="M{lx + 4:.1f} {ly:.1f} H{tx - 6}" stroke="{ink}" stroke-width="0.7"/>'
                f'<circle cx="{lx + 4:.1f}" cy="{ly:.1f}" r="1.8" fill="{ink}"/>' + text(t, tx, ly + 3.2, 9, ink))
        lab += text(f'0{i + 1}', tx - 10, ly + 3.2, 7, accent, 'end')
    return axis + ''.join(out) + lab


def badge_art(R, ink, accent, fab):
    """Emblema vintage circular (A4 Badge). Caixa local 2R x 2R."""
    cx = cy = R
    ri = R - 27
    o = [f'<circle cx="{cx}" cy="{cy}" r="{R - 1.5}" fill="none" stroke="{ink}" stroke-width="3"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{ri}" fill="none" stroke="{ink}" stroke-width="1.6"/>',
         f'<clipPath id="bdgclip"><circle cx="{cx}" cy="{cy}" r="{ri - 1}"/></clipPath><g clip-path="url(#bdgclip)">']
    # Terra
    er = ri * 1.6
    ecy = cy + ri * 0.45 + er
    o.append(f'<circle cx="{cx}" cy="{ecy:.1f}" r="{er:.1f}" fill="{ink}"/>')
    for k in range(1, 7):
        o.append(f'<ellipse cx="{cx}" cy="{ecy:.1f}" rx="{er * abs(math.cos(k * math.pi / 14)):.1f}" ry="{er:.1f}" fill="none" stroke="{fab}" stroke-width="0.7" opacity="0.6"/>')
    for k in range(1, 4):
        yy = ecy - er + k * 13
        o.append(f'<path d="M{cx - ri} {yy:.1f} H{cx + ri}" stroke="{fab}" stroke-width="0.7" opacity="0.6"/>')
    o.append(f'<circle cx="{cx}" cy="{ecy:.1f}" r="{er + 4:.1f}" fill="none" stroke="{accent}" stroke-width="2.2"/>')
    o.append('</g>')
    # estrelas
    o.append(stars(cx - ri, cy - ri, 2 * ri, ri * 1.2, 26, 77, fill=ink, avoid=lambda x, y: math.hypot(x - cx, y - cy) > ri - 6, rmax=1.4))
    # orbita + satelite
    o.append(f'<ellipse cx="{cx}" cy="{cy - 4}" rx="{ri * 0.82:.1f}" ry="{ri * 0.30:.1f}" fill="none" stroke="{accent}" stroke-width="1.6" transform="rotate(-16 {cx} {cy - 4})"/>')
    o.append(sat_wings(cx, cy - 10, 20, ink, accent, fab, sw=1.4, rot=-16))
    # textos no anel
    o.append(text_arc('POLISAT', cx, cy, R - 21.5, 0, 15, ink, 'R', 0.22))
    o.append(text_arc('SÃO PAULO  BRAZIL', cx, cy, R - 8.5, 180, 11.5, ink, 'R', 0.16, outside=False))
    for ang in (-62, 62):
        x, y = cx + (R - 14) * math.sin(math.radians(ang + 180)), cy - (R - 14) * math.cos(math.radians(ang + 180))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{accent}"/>')
    for ang in (-90, 90):
        x, y = cx + (R - 14) * math.sin(math.radians(ang)), cy - (R - 14) * math.cos(math.radians(ang))
        o.append(f'<path d="M{x:.1f} {y - 5:.1f} L{x + 1.5:.1f} {y - 1.5:.1f} L{x + 5:.1f} {y:.1f} L{x + 1.5:.1f} {y + 1.5:.1f} L{x:.1f} {y + 5:.1f} '
                 f'L{x - 1.5:.1f} {y + 1.5:.1f} L{x - 5:.1f} {y:.1f} L{x - 1.5:.1f} {y - 1.5:.1f} Z" fill="{accent}"/>')
    return ''.join(o)


def orbit_ring(w, h, ink, sat):
    """Anel orbital bordado em volta do logo do peito (P1)."""
    cx, cy = w / 2, h / 2
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2 - 2}" ry="{h / 2 - 2}" fill="none" stroke="{ink}" stroke-width="1.2" transform="rotate(-8 {cx} {cy})"/>'
            f'<circle cx="{cx + (w / 2 - 2) * math.cos(math.radians(-38)):.1f}" cy="{cy + (h / 2 - 2) * math.sin(math.radians(-38)) - 6:.1f}" r="3.2" fill="{sat}"/>')


# ------------------------------------------------------------------ MODELOS

def build_models():
    M = []
    BR_COLORS = None
    C_WHITE = ('Branco', '#ffffff', 'White')
    C_BLUE = ('Azul PoliSat', L.POLISAT_BLUE, 'Pantone 2945 C (aprox.)')
    C_INK = ('Preto', L.INK, 'Pantone Black 6 C')
    C_SKY = ('Azul-céu', SKY, 'Pantone 279 C (aprox.)')
    C_CREAM = ('Creme', CREAM, 'Pantone 7527 C (aprox.)')
    C_EMBER = ('Laranja', EMBER, 'Pantone 1595 C (aprox.)')
    C_NAVYINK = ('Marinho', INK_NAVY, 'Pantone 289 C (aprox.)')
    SILK = 'Silk-screen (serigrafia) com tinta plastisol, ou DTF'
    poli_usp = lambda v1, v2: [('poli', v1, 52, None), ('usp', v2, 50, None)]

    # ================= ALGODAO 01 — CONSTELLATION (preto)
    fab = BLACK_FAB
    pl = [
        place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', 'blue:' + SKY, 112, 150, w=100,
                   tecnica=SILK, cores=[C_WHITE, C_SKY]),
        Placement('frente_satelite', 'Satélite (barra frontal)', 'frente', 150, 610, 90, 50,
                  lambda web: (f'<path d="M0 40 Q45 0 90 12" fill="none" stroke="{SKY}" stroke-width="1.2" stroke-dasharray="3 3"/>'
                               + cubesat(78, 16, 8, '#ffffff', panel=SKY, sw=1.0)), SILK, [C_WHITE, C_SKY]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp('white', 'white'), 40, 12, SILK, [C_WHITE], 'manga_esq_poli_usp'),
        place_logo('costas_icone', 'Símbolo PoliSat (nuca)', 'costas', 'polisat_icon', 'blue:' + SKY, 0, 52, w=40,
                   tecnica=SILK, cores=[C_WHITE, C_SKY]),
        Placement('costas_constelacao', 'Globo + constelação de CubeSats', 'costas', -190, 110, 380, 290,
                  lambda web: globe_art(190, 145, 112, '#ffffff', SKY, BLACK_FAB), SILK, [C_WHITE, C_SKY]),
        Placement('costas_patrocinadores', 'Patrocinadores', 'costas', -155, 440, 310, 175,
                  lambda web: sponsor_grid(0, 0, 310, 175, 'white'), SILK, [C_WHITE]),
    ]
    M.append(dict(id='A1', slug='algodao_01_constellation', nome='Constellation', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor PRETO', cor_tecido='Preto',
                  tecnica=SILK, placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Nas costas, a Terra em arame cercada por três planos orbitais com CubeSats; frente limpa com um satélite discreto na barra.'))

    # ================= ALGODAO 02 — GROUND TRACK (branca) — mantida
    fab = WHITE_FAB
    def gt_front(web):
        return (ground_track(-262, 262, 318, 62, 560, 40, L.POLISAT_BLUE) +
                f'<circle cx="-118" cy="{318 - 62 * math.sin(2 * math.pi * (-118 + 40) / 560):.1f}" r="11" fill="none" stroke="{L.POLISAT_BLUE}" stroke-width="1.4"/>'
                f'<circle cx="-118" cy="{318 - 62 * math.sin(2 * math.pi * (-118 + 40) / 560):.1f}" r="4.4" fill="{L.POLISAT_BLUE}"/>')
    def gt_back(web):
        return ground_track(-262, 262, 250, 62, 560, 40 + 262 * 2, L.POLISAT_BLUE)
    pl = [
        Placement('frente_groundtrack', 'Ground track (onda)', 'frente', -300, -20, 600, 780,
                  lambda web: full(gt_front(web)), SILK, [C_BLUE], crop=(-263, 238, 526, 158)),
        place_logo('peito_polisat', 'Logo PoliSat (centro do peito)', 'frente', 'polisat', 'dark', 0, 135, w=200,
                   tecnica=SILK, cores=[C_INK, C_BLUE]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp('dark', 'original'), 40, 12, SILK, [C_INK], 'manga_esq_poli_usp'),
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
                  conceito='Logo grande no peito com o rastro de solo (ground track) do satélite dando a volta na camiseta.'))

    # ================= ALGODAO 03 — EXPLODED (azul petroleo)
    fab = PETROLEO
    pl = [
        place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', 'mono:' + CREAM, 112, 150, w=100,
                   tecnica=SILK, cores=[C_CREAM]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp('mono:' + CREAM, 'mono:' + CREAM), 40, 12, SILK, [C_CREAM], 'manga_esq_poli_usp'),
        place_logo('costas_usp', 'Logo USP (nuca)', 'costas', 'usp', 'mono:' + CREAM, 0, 46, w=54, tecnica=SILK, cores=[C_CREAM]),
        Placement('costas_explodida', 'Vista explodida CubeSat 1U', 'costas', -180, 92, 380, 445,
                  lambda web: exploded_art(CREAM, EMBER, PETROLEO), SILK, [C_CREAM, C_EMBER]),
        Placement('costas_patrocinadores', 'Patrocinadores', 'costas', -150, 540, 300, 150,
                  lambda web: sponsor_grid(0, 0, 300, 150, 'mono:' + CREAM), SILK, [C_CREAM]),
    ]
    M.append(dict(id='A3', slug='algodao_03_exploded', nome='Exploded', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor AZUL PETRÓLEO', cor_tecido='Azul petróleo',
                  tecnica=SILK, placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Vista explodida de um CubeSat 1U (antena, células solares, payload, OBC, EPS e estrutura) em tinta creme e laranja.'))

    # ================= ALGODAO 04 — BADGE (areia)  [novo]
    fab = AREIA
    pl = [
        Placement('frente_emblema', 'Emblema PoliSat (centro do peito)', 'frente', -105, 140, 210, 210,
                  lambda web: badge_art(105, INK_NAVY, EMBER, AREIA), SILK, [C_NAVYINK, C_EMBER]),
        flag_placement('manga_dir', 0, 48, 78, SILK),
        sleeve_stack('manga_esq', poli_usp('mono:' + INK_NAVY, 'mono:' + INK_NAVY), 40, 12, SILK, [C_NAVYINK], 'manga_esq_poli_usp'),
        place_logo('costas_polisat', 'Logo PoliSat (costas)', 'costas', 'polisat', 'dark', 0, 70, w=130,
                   tecnica=SILK, cores=[C_INK, C_BLUE]),
        Placement('costas_patrocinadores', 'Patrocinadores', 'costas', -160, 270, 320, 185,
                  lambda web: sponsor_grid(0, 0, 320, 185, 'mono:' + INK_NAVY), SILK, [C_NAVYINK]),
    ]
    M.append(dict(id='A4', slug='algodao_04_badge', nome='Badge', garment='algodao', fabric=fab,
                  tecido='Malha 100% algodão penteado fio 30.1 — cor AREIA (bege)', cor_tecido='Areia',
                  tecnica=SILK, placements=pl, gola=gola_panel(fab), sublimacao=False,
                  conceito='Emblema vintage estilo agência espacial: satélite em órbita sobre a Terra, POLISAT e SÃO PAULO BRAZIL no anel.'))

    # ================= POLOS (bordado + recortes)
    BORD = 'Bordado (matriz a partir do vetor)'
    CN = {BLACK_FAB: 'preta', NAVY_FAB: 'azul-marinho', WHITE_FAB: 'branca', L.POLISAT_BLUE: 'azul PoliSat', '#ffffff': 'branco',
          SKY: 'azul-céu', GRAFITE: 'grafite', VINHO: 'vinho', AREIA: 'areia', SILVER: 'prata'}
    def polo(id_, slug, nome, fab, cor, pol_var, logos_var, rib, stripes, conceito, cores_logo, btn, extra_pl=(),
             construcao='', under=None, base=None, placket=None, cor_label=None):
        pl = list(extra_pl) + [
            place_logo('peito_polisat', 'Logo PoliSat (peito esquerdo)', 'frente', 'polisat', pol_var, 108, 168, w=88,
                       tecnica=BORD, cores=cores_logo),
            flag_placement('manga_dir', 0, 52, 64, 'Bordado'),
            place_logo('manga_esq_poli', 'Selo Escola Politécnica', 'manga_esq', 'poli', logos_var, 0, 44, w=50,
                       tecnica=BORD, cores=[cores_logo[0]]),
            place_logo('costas_usp', 'Logo USP (nuca, abaixo da gola)', 'costas', 'usp', logos_var if logos_var != 'dark' else 'original',
                       0, 58, w=52, tecnica=BORD, cores=[cores_logo[0]]),
        ]
        gstr = [(0.80, 0.05, stripes[0]), (0.88, 0.05, stripes[1])] if stripes else []
        cuff = [(0.35, 0.14, stripes[0]), (0.62, 0.14, stripes[1])] if stripes else []
        desc = f'Gola e punhos em ribana {CN[rib]}' + (f' com 2 frisos ({CN[stripes[0]]} e {CN[stripes[1]]})' if stripes else ' lisa')
        if construcao:
            desc += '. ' + construcao
        return dict(id=id_, slug=slug, nome=nome, garment='polo', fabric=fab, tecido=f'Malha piquet (algodão/poliéster) — cor {cor}',
                    cor_tecido=cor_label or cor.capitalize(), tecnica=BORD, placements=pl, gola=gola_panel(rib, gstr), cuff=(rib, cuff),
                    btn=btn, sublimacao=False, conceito=conceito, gola_desc=desc, under=under or {}, base=base or {}, placket=placket)

    # P1 ORBIT — preta com anel orbital bordado em prata
    ring = Placement('peito_orbita', 'Anel orbital bordado (envolve o logo)', 'frente', 108 - 66, 168 + 23 - 40, 132, 80,
                     lambda web: orbit_ring(132, 80, SILVER, SKY), 'Bordado — linha prata, ponto corrido duplo',
                     [('Prata', SILVER, 'linha metalizada prata'), C_SKY])
    M.append(polo('P1', 'polo_01_orbit', 'Orbit', BLACK_FAB, 'PRETO', 'blue:' + SKY, 'white', BLACK_FAB, (SKY, '#ffffff'),
                  'Polo preta com um anel orbital bordado em prata envolvendo o logo, como um satélite em volta da marca.',
                  [C_WHITE, C_SKY], '#1b1b1d', extra_pl=[ring], cor_label='Preto'))

    # P2 YOKE — grafite com pala azul PoliSat nos ombros
    yk = lambda yl: (f'<path d="M-300 -20 H300 V{yl} H-300 Z" fill="{L.POLISAT_BLUE}"/>'
                     f'<path d="M-300 {yl} H300" stroke="#ffffff" stroke-width="2.2"/>')
    M.append(polo('P2', 'polo_02_yoke', 'Yoke', GRAFITE, 'GRAFITE', 'white', 'white', GRAFITE, ('#ffffff', L.POLISAT_BLUE),
                  'Polo grafite com pala (recorte) azul PoliSat nos ombros, separada por vivo branco — corte de uniforme técnico.',
                  [C_WHITE, C_BLUE], '#f2f2f2', construcao='Recorte de pala em piquet azul PoliSat (frente até 95 mm do HPS, costas até 150 mm) com vivo branco de 2 mm na costura',
                  under={'frente': yk(95), 'costas': yk(150)}, cor_label='Grafite + azul'))

    # P3 CONTRAST — branca com gola, carcela e punhos marinho + CubeSat bordado na barra
    hem_sat = Placement('barra_cubesat', 'CubeSat bordado (barra, lado esquerdo)', 'frente', 175, 630, 30, 34,
                        lambda web: cubesat(15, 19, 12, NAVY_FAB, panel=L.POLISAT_BLUE, sw=1.2), BORD,
                        [('Marinho', NAVY_FAB, 'linha marinho'), C_BLUE])
    M.append(polo('P3', 'polo_03_contrast', 'Contrast', WHITE_FAB, 'BRANCO', 'dark', 'dark', NAVY_FAB, ('#ffffff', L.POLISAT_BLUE),
                  'Polo branca com gola, punhos e carcela marinho em contraste e um pequeno CubeSat bordado na barra.',
                  [C_INK, C_BLUE], '#f2f2f2', extra_pl=[hem_sat], placket=NAVY_FAB,
                  construcao='Carcela em piquet marinho', cor_label='Branco + marinho'))

    # P4 RAGLAN — vinho com mangas raglan areia  [novo]
    G = L.GARMENTS['polo']
    def raglan(panel):
        nw = G['NW']
        ny = G['FND'] if panel == 'frente' else G['BND']
        return ''.join(f'<path d="M{sg * nw * 0.55:.1f} {ny * 0.55:.1f} L{sg * 320} -20 L{sg * 320} {G["UAY"] + 10} L{sg * G["UAX"]} {G["UAY"] + 10} Z" fill="{AREIA}"/>'
                       f'<path d="M{sg * nw * 0.55:.1f} {ny * 0.55:.1f} L{sg * G["UAX"]} {G["UAY"] + 10}" stroke="{VINHO}" stroke-width="1.2" opacity="0.5"/>'
                       for sg in (-1, 1))
    M.append(polo('P4', 'polo_04_raglan', 'Raglan', VINHO, 'VINHO', 'blue:' + AREIA, 'mono:' + AREIA, VINHO, (AREIA, '#ffffff'),
                  'Polo vinho com mangas raglan areia — bicolor de clube, bordados em areia.',
                  [('Areia', AREIA, 'linha bege'), ('Branco', '#ffffff', 'White')], '#e9dfc8',
                  construcao='Mangas raglan em piquet areia (recorte do decote até a cava)',
                  under={'frente': raglan('frente'), 'costas': raglan('costas')},
                  base={'manga_esq': AREIA, 'manga_dir': AREIA}, cor_label='Vinho + areia'))

    # ================= DRY-FIT (sublimacao total — missao Hermes)
    SUB = 'Sublimação total (full print) em tecido dry-fit poliéster'
    TEC = 'Dry-fit 100% poliéster branco (sublimação total)'
    M.append(dict(id='D1', slug='dryfit_01_ignition', nome='Ignition', garment='dryfit', fabric=BLACK_FAB, tecido=TEC,
                  cor_tecido='Preto + chamas', tecnica=SUB, sublimacao=True, panels=dry_ignition,
                  gola=gola_panel('#141416', [(0.55, 0.12, L.H_ORANGE)]),
                  gola_desc='Gola em ribana preta com friso laranja; punhos sublimados em degradê de chama',
                  conceito='Pluma de exaustão de foguete subindo da barra, com diamantes de choque e faixas laterais de corrida.'))
    M.append(dict(id='D2', slug='dryfit_02_rollpattern', nome='Roll Pattern', garment='dryfit', fabric='#f4f4f2', tecido=TEC,
                  cor_tecido='Branco + preto', tecnica=SUB, sublimacao=True, panels=dry_roll,
                  gola=gola_panel('#141416', [(0.55, 0.12, L.H_ORANGE)]),
                  gola_desc='Gola em ribana preta com friso laranja; mangas assimétricas (preta / branca)',
                  conceito='Padrão de rolagem preto e branco dos foguetes clássicos, com faixa de interestágio laranja e rebites.'))
    M.append(dict(id='D3', slug='dryfit_03_pitwall', nome='Pit Wall', garment='dryfit', fabric=PETROLEO, tecido=TEC,
                  cor_tecido='Petróleo + laranja', tecnica=SUB, sublimacao=True, panels=dry_pitwall,
                  gola=gola_panel('#0b2a31', [(0.55, 0.12, L.H_ORANGE)]),
                  gola_desc='Gola em ribana petróleo escuro com friso laranja',
                  conceito='Livery de Fórmula 1: curva laranja varrendo do quadril ao ombro com filetes brancos e vermelhos.'))
    M.append(dict(id='D4', slug='dryfit_04_solararray', nome='Solar Array', garment='dryfit', fabric='#0a1834', tecido=TEC,
                  cor_tecido='Azul-noite + dourado', tecnica=SUB, sublimacao=True, panels=dry_solar,
                  gola=gola_panel('#0a1834', [(0.55, 0.12, GOLD)]),
                  gola_desc='Gola em ribana azul-noite com friso dourado; mangas com padrão de células solares',
                  conceito='A camiseta vira o satélite: corpo em manta térmica dourada (MLI) e painéis solares abertos nas laterais.'))
    return M


# ------------------------------------------------------------------ DRY-FIT paineis

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



def flame(cx, base, w, h, seed, fill, op=1.0, n=22):
    import random
    r = random.Random(seed)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = cx - w / 2 + w * t
        env = max(0, 1 - (2 * t - 1) ** 2) ** 0.75
        tongue = 1.0 if i % 2 == 0 else 0.55 + r.random() * 0.25
        pts.append((x, base - h * env * tongue * (0.85 + r.random() * 0.15)))
    d = f'M{cx - w / 2:.1f} {base + 40}'
    d += f' L{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        d += f' Q{x0:.1f} {y0:.1f} {(x0 + x1) / 2:.1f} {(y0 + y1) / 2:.1f}'
    d += f' L{pts[-1][0]:.1f} {pts[-1][1]:.1f} L{cx + w / 2:.1f} {base + 40} Z'
    return f'<path d="{d}" fill="{fill}" opacity="{op}"/>'


def plume(cx, base, scale, seed=1, diamonds=True):
    o = ''
    for i, (c, w, h, op) in enumerate(((L.H_RED, 700, 470, 0.9), (L.H_ORANGE, 500, 390, 0.95), (L.H_AMBER, 320, 290, 1),
                                        ('#ffe08a', 170, 190, 1), ('#fff6dc', 70, 100, 1))):
        o += flame(cx, base, w * scale, h * scale, seed + i, c, op)
    if diamonds:
        for k, (dy, dw, dh) in enumerate(((-60, 46, 70), (-140, 36, 56), (-205, 26, 42))):
            y = base + dy * scale
            o += (f'<path d="M{cx} {y - dh * scale / 2:.1f} L{cx + dw * scale / 2:.1f} {y:.1f} L{cx} {y + dh * scale / 2:.1f} '
                  f'L{cx - dw * scale / 2:.1f} {y:.1f} Z" fill="#ffffff" opacity="{0.75 - k * 0.15:.2f}"/>')
    return o


def dry_ignition(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    defs = _defs_grad('icuff', [(0, L.H_AMBER, None), (0.5, L.H_ORANGE, None), (1, L.H_RED, None)], 0, 0, 0, 1)
    P = {}
    f = _frame_rect('frente', BLACK_FAB)
    f += halftone_band(-330, 430, 330, 430, 150, L.H_RED, side=-1, cell=8, rmax=3.2)
    f += plume(0, 790, 1.0, 3)
    for sg in (1, -1):
        f += f'<path d="M{sg * 226} 250 L{sg * 246} 250 L{sg * 258} 780 L{sg * 238} 780 Z" fill="{L.H_ORANGE}"/>'
        f += f'<path d="M{sg * 214} 250 L{sg * 219} 250 L{sg * 231} 780 L{sg * 226} 780 Z" fill="{L.H_AMBER}"/>'
    f += put('polisat', 'white', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    c = _frame_rect('costas', BLACK_FAB)
    c += plume(0, 800, 0.62, 9, diamonds=False)
    for sg in (1, -1):
        c += f'<path d="M{sg * 226} 250 L{sg * 246} 250 L{sg * 258} 780 L{sg * 238} 780 Z" fill="{L.H_ORANGE}"/>'
    c += put_center('polisat', 'white', 0, 100, w=130)
    c += text('MISSION', 0, 178, 15, '#ffffff', 'middle', ls=0.5)
    hd, hw, _ = L.text_d('HERMES', 56, 'R', 0.04)
    c += f'<g transform="translate({-hw / 2:.1f} 236)"><path d="{hd}" fill="{L.H_ORANGE}"/></g>'
    c += sponsor_grid(-165, 268, 330, 200, 'white')
    c += name_plate(0, 568, 340, 84, BLACK_FAB, L.H_AMBER, '#ffffff', name, 46, plate='#141416')
    P['costas'] = c
    for k in ('manga_dir', 'manga_esq'):
        s = _frame_rect(k, BLACK_FAB)
        s += f'<rect x="-230" y="{G["SL"] - 60}" width="460" height="90" fill="url(#icuff)"/>'
        s += flame(0, G['SL'] - 40, 520, 70, 4, L.H_ORANGE, 0.9)
        if k == 'manga_dir':
            s += put_center('bandeira', 'original', 0, 82, w=74)
        else:
            s += put_center('poli', 'white', 0, 70, w=50) + put_center('usp', 'white', 0, 128, w=48)
        P[k] = s
    return P, defs


def rivets(y, x0, x1, fill, step=12, r=1.6):
    return ''.join(f'<circle cx="{x:.1f}" cy="{y}" r="{r}" fill="{fill}"/>' for x in [x0 + i * step for i in range(int((x1 - x0) / step) + 1)])


def dry_roll(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    W, K, O = '#f4f4f2', '#141416', L.H_ORANGE
    defs = ''
    P = {}
    f = _frame_rect('frente', W)
    f += f'<rect x="-300" y="-20" width="300" height="380" fill="{K}"/><rect x="0" y="400" width="300" height="380" fill="{K}"/>'
    f += f'<rect x="-300" y="360" width="600" height="40" fill="{O}"/>'
    f += f'<path d="M-300 364 H300 M-300 396 H300" stroke="{K}" stroke-width="0.8"/>'
    f += rivets(352, -294, -6, '#f4f4f2') + rivets(352, 6, 294, K) + rivets(408, -294, -6, K) + rivets(408, 6, 294, '#f4f4f2')
    f += put('polisat', 'dark', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    f += text('HERMES', -112, 268, 15, '#f4f4f2', 'middle', ls=0.3)
    P['frente'] = f
    c = _frame_rect('costas', W)
    c += f'<rect x="-300" y="-20" width="600" height="205" fill="{K}"/>'
    c += put_center('polisat', 'white', 0, 95, w=140)
    c += rivets(196, -294, 294, K)
    c += sponsor_grid(-170, 215, 340, 250, 'light_bg', scale=1.1)
    c += f'<rect x="-300" y="664" width="300" height="120" fill="{K}"/>'
    c += f'<rect x="-300" y="552" width="600" height="112" fill="{O}"/>'
    c += f'<path d="M-300 556 H300 M-300 660 H300" stroke="{K}" stroke-width="0.8"/>'
    c += rivets(544, -294, 294, K) + rivets(672, -294, -6, '#f4f4f2') + rivets(672, 6, 294, K)
    c += name_plate(0, 568, 360, 80, O, 'none', K, name, 48, plate='none')
    P['costas'] = c
    for k, base, fg, lv in (('manga_dir', K, '#f4f4f2', 'white'), ('manga_esq', W, K, 'dark')):
        s = _frame_rect(k, base)
        s += f'<rect x="-230" y="{G["SL"] - 34}" width="460" height="64" fill="{O}"/><path d="M-230 {G["SL"] - 30} H230" stroke="{fg}" stroke-width="0.8"/>'
        s += rivets(G['SL'] - 42, -226, 226, fg)
        if k == 'manga_dir':
            s += put_center('bandeira', 'original', 0, 82, w=74)
        else:
            s += put_center('poli', lv, 0, 70, w=50) + put_center('usp', 'original' if lv == 'dark' else 'white', 0, 128, w=48)
        P[k] = s
    return P, defs


def swoosh(x0, y0, c1, c2, x1, y1, w0, w1, fill, extra=''):
    """Faixa curva afunilada (bezier cubica) de largura w0 -> w1."""
    out = f'M{x0} {y0} C{c1[0]} {c1[1]} {c2[0]} {c2[1]} {x1} {y1} L{x1} {y1 + w1} C{c2[0]} {c2[1] + (w0 + w1) / 2} {c1[0]} {c1[1] + w0} {x0} {y0 + w0} Z'
    return f'<path d="{out}" fill="{fill}"{extra}/>'


def dry_pitwall(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    defs = (_defs_grad('pbase', [(0, '#155160', None), (1, '#082229', None)], 0, 0, 0, 1) +
            _defs_grad('psw', [(0, L.H_RED, None), (0.55, L.H_ORANGE, None), (1, L.H_AMBER, None)], 0, 1, 1, 0) +
            _defs_grad('pcuff', [(0, L.H_RED, None), (1, L.H_ORANGE, None)]))
    P = {}
    f = _frame_rect('frente', 'url(#pbase)')
    f += swoosh(-330, 640, (-120, 560), (120, 420), 330, 250, 120, 40, '#0a2a31')
    f += swoosh(-330, 662, (-120, 582), (120, 442), 330, 268, 96, 26, 'url(#psw)')
    f += f'<path d="M-330 652 C-120 572 120 432 330 258" fill="none" stroke="#ffffff" stroke-width="3"/>'
    f += f'<path d="M-330 772 C-120 692 120 520 330 300" fill="none" stroke="{L.H_RED}" stroke-width="1.6"/>'
    f += f'<path d="M-330 784 C-120 704 120 532 330 312" fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.7"/>'
    f += put('polisat', 'white', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    c = _frame_rect('costas', 'url(#pbase)')
    c += swoosh(-330, 720, (-120, 690), (120, 640), 330, 560, 60, 22, 'url(#psw)')
    c += f'<path d="M-330 712 C-120 682 120 632 330 552" fill="none" stroke="#ffffff" stroke-width="2.4"/>'
    c += put_center('polisat', 'white', 0, 98, w=140)
    c += f'<path d="M-170 160 H170" stroke="{L.H_ORANGE}" stroke-width="2"/><path d="M-170 165 H170" stroke="#ffffff" stroke-width="0.8"/>'
    c += sponsor_grid(-165, 190, 330, 220, 'white', scale=1.05)
    c += f'<path d="M-170 440 H170" stroke="{L.H_ORANGE}" stroke-width="2"/>'
    c += name_plate(0, 470, 360, 80, '#0a2a31', L.H_ORANGE, '#ffffff', name, 48, plate='#0a2a31')
    P['costas'] = c
    for k in ('manga_dir', 'manga_esq'):
        s = _frame_rect(k, '#0f4350')
        s += f'<rect x="-230" y="{G["SL"] - 34}" width="460" height="64" fill="url(#pcuff)"/><path d="M-230 {G["SL"] - 42} H230" stroke="#ffffff" stroke-width="2.4"/>'
        if k == 'manga_dir':
            s += put_center('bandeira', 'original', 0, 82, w=74)
        else:
            s += put_center('poli', 'white', 0, 70, w=50) + put_center('usp', 'white', 0, 128, w=48)
        P[k] = s
    return P, defs


def mli(x, y, w, h, seed):
    """Manta termica dourada (MLI) amassada: triangulos com tons de ouro."""
    import random
    r = random.Random(seed)
    tones = ['#a8780e', '#c99418', '#e2b23a', '#f3cf63', '#b98510', '#d6a227', '#fbe08f']
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c99418"/>']
    cell = 26
    pts = {}
    for i in range(int(w / cell) + 2):
        for j in range(int(h / cell) + 2):
            pts[(i, j)] = (x + i * cell + (r.random() - 0.5) * cell * 0.7, y + j * cell + (r.random() - 0.5) * cell * 0.7)
    for i in range(int(w / cell) + 1):
        for j in range(int(h / cell) + 1):
            a, b, c, d = pts[(i, j)], pts[(i + 1, j)], pts[(i + 1, j + 1)], pts[(i, j + 1)]
            for tri in ((a, b, c), (a, c, d)):
                o.append('<path d="M' + ' L'.join(f'{px:.1f} {py:.1f}' for px, py in tri) + f' Z" fill="{r.choice(tones)}"/>')
    return f'<clipPath id="mli{seed}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#mli{seed})">' + ''.join(o) + '</g>'


def solar_wing(x, y, w, h, cols, rows):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c9ced6"/>']
    gap = 3.0
    cw, ch = (w - gap * (cols + 1)) / cols, (h - gap * (rows + 1)) / rows
    for i in range(cols):
        for j in range(rows):
            cx, cy = x + gap + i * (cw + gap), y + gap + j * (ch + gap)
            o.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="url(#cell)"/>'
                     f'<path d="M{cx:.1f} {cy + ch / 2:.1f} H{cx + cw:.1f} M{cx + cw / 3:.1f} {cy:.1f} V{cy + ch:.1f} M{cx + 2 * cw / 3:.1f} {cy:.1f} V{cy + ch:.1f}" '
                     f'stroke="#9fb4d8" stroke-width="0.35" opacity="0.7"/>')
    return ''.join(o)


def dry_solar(web=False, name='NAME'):
    G = L.GARMENTS['dryfit']
    NV = '#0a1834'
    defs = ('<linearGradient id="cell" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a4fa8"/><stop offset="0.5" stop-color="#14306f"/>'
            '<stop offset="1" stop-color="#0c1f4d"/></linearGradient>')
    P = {}
    def satellite(top, body_w=210, wing_y=None, seed=1):
        wing_y = wing_y if wing_y is not None else top + 60
        s = ''
        for sg in (1, -1):
            x0 = body_w / 2 + 30
            s += f'<rect x="{min(sg * (body_w / 2), sg * x0):.1f}" y="{wing_y + 72}" width="30" height="10" fill="#c9ced6"/>'
            s += solar_wing(x0 if sg > 0 else -330, wing_y, 330 - x0, 160, 3, 4)
        s += mli(-body_w / 2, top, body_w, 820 - top, seed)
        s += f'<rect x="{-body_w / 2}" y="{top}" width="{body_w}" height="{820 - top}" fill="none" stroke="#fbe08f" stroke-width="1.4"/>'
        return s
    f = _frame_rect('frente', NV)
    f += stars(-300, -20, 600, 300, 160, 41)
    f += satellite(300, seed=3)
    f += f'<path d="M0 300 V245" stroke="#c9ced6" stroke-width="2.4"/><circle cx="0" cy="241" r="4" fill="#c9ced6"/>'
    f += put('polisat', 'white', 112 - 52, 150, w=104)
    f += hermes_patch(-112 - 46, 130, 92, web)
    P['frente'] = f
    c = _frame_rect('costas', NV)
    c += stars(-300, -20, 600, 380, 150, 52, avoid=lambda x, y: abs(x) < 175 and 150 < y < 360)
    c += put_center('polisat', 'white', 0, 92, w=140)
    c += sponsor_grid(-165, 160, 330, 190, 'white')
    c += satellite(380, wing_y=410, seed=8)
    c += name_plate(0, 568, 340, 84, NV, '#fbe08f', '#ffffff', name, 46, plate=NV)
    P['costas'] = c
    for k in ('manga_dir', 'manga_esq'):
        s = _frame_rect(k, NV) + solar_wing(-240, -40, 480, 230, 8, 5)
        s += f'<rect x="-230" y="{G["SL"] - 34}" width="460" height="64" fill="{NV}"/><path d="M-230 {G["SL"] - 34} H230" stroke="{GOLD}" stroke-width="3"/>'
        s += f'<rect x="-46" y="44" width="92" height="118" rx="8" fill="{NV}"/>' if k == 'manga_esq' else f'<rect x="-42" y="53" width="84" height="58" fill="#ffffff"/>'
        if k == 'manga_dir':
            s += put_center('bandeira', 'original', 0, 82, w=74)
        else:
            s += put_center('poli', 'white', 0, 82, w=46) + put_center('usp', 'white', 0, 136, w=44)
        P[k] = s
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
            body = _frame_rect(k, m.get('base', {}).get(k, m['fabric']))
            body += m.get('under', {}).get(k, '')
            for p in m['placements']:
                if p.panel == k:
                    body += p.svg_in_panel(web)
            if m['garment'] == 'polo':
                rib, cuff = m['cuff']
                body += polo_finish2(k, m['fabric'], rib, cuff, m['btn'], m.get('placket'))
            else:
                body += tee_finish(k, m['garment'], m['fabric'])
            out[k] = L.svg_doc(L.FRAME[k], body)
    out['gola'] = L.svg_doc(L.FRAME['gola'], m['gola'])
    return out
