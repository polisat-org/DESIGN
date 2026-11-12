"""Normaliza os logos (SVG) para uso nas artes das camisetas.

- Converte estilos de classe (CSS) em atributos inline (RIPs/Corel nem sempre leem <style>)
- Prefixa ids para que varios SVGs possam ser combinados num unico arquivo
- Gera versoes monocromaticas (ex.: branco para tecido escuro)
"""
import re, copy
import xml.etree.ElementTree as ET

SVGNS = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVGNS)
ET.register_namespace('xlink', XLINK)

DROP = {'metadata', 'title', 'desc', 'namedview', 'RDF'}


def _local(tag):
    return tag.split('}')[-1]


def _parse_css(text):
    rules = {}
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    for sel, body in re.findall(r'([^{}]+)\{([^}]*)\}', text):
        for s in sel.split(','):
            s = s.strip()
            if s.startswith('.'):
                rules.setdefault(s[1:], []).append(body.strip().rstrip(';'))
    return rules


def _style_dict(s):
    d = {}
    for part in (s or '').split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            d[k.strip()] = v.strip()
    return d


def _style_str(d):
    return ';'.join(f'{k}:{v}' for k, v in d.items())


class Logo:
    def __init__(self, root, viewbox):
        self.root = root
        self.viewbox = viewbox  # (x, y, w, h)

    @property
    def aspect(self):
        return self.viewbox[2] / self.viewbox[3]

    def copy(self):
        return Logo(copy.deepcopy(self.root), self.viewbox)


def load(path, prefix):
    tree = ET.parse(path)
    root = tree.getroot()
    vb = root.get('viewBox')
    if vb:
        vb = tuple(float(v) for v in re.split(r'[ ,]+', vb.strip()))
    else:
        vb = (0, 0, float(re.sub('[a-z]', '', root.get('width'))), float(re.sub('[a-z]', '', root.get('height'))))
    css = {}
    for st in root.iter(f'{{{SVGNS}}}style'):
        for k, v in _parse_css(st.text or '').items():
            css.setdefault(k, []).extend(v)
    # remove style / metadata
    for parent in list(root.iter()):
        for ch in list(parent):
            if _local(ch.tag) == 'style' or _local(ch.tag) in DROP or not isinstance(ch.tag, str):
                parent.remove(ch)
    ids = {}
    for e in root.iter():
        if e.get('id'):
            ids[e.get('id')] = f'{prefix}_{e.get("id")}'
    for e in root.iter():
        cls = e.attrib.pop('class', None)
        if cls:
            d = {}
            for c in cls.split():
                for body in css.get(c, []):
                    d.update(_style_dict(body))
            d.update(_style_dict(e.get('style')))
            e.set('style', _style_str(d))
        if e.get('id'):
            e.set('id', ids[e.get('id')])
        for k, v in list(e.attrib.items()):
            if k.startswith('{http://www.inkscape') or k.startswith('{http://sodipodi') or 'data-name' in k:
                del e.attrib[k]
                continue
            if 'url(#' in v:
                v = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{ids.get(m.group(1), m.group(1))})', v)
                e.set(k, v)
            if _local(k) == 'href' and v.startswith('#'):
                e.set(k, '#' + ids.get(v[1:], v[1:]))
    return Logo(root, vb)


COLOR_KEYS = ('fill', 'stroke', 'stop-color')


def recolor(logo, color):
    """Todas as cores visiveis viram `color` (mantem none/transparente)."""
    lg = logo.copy()
    for e in lg.root.iter():
        for k in COLOR_KEYS:
            v = e.get(k)
            if v and v not in ('none', 'transparent') and not v.startswith('url('):
                e.set(k, color)
        st = _style_dict(e.get('style'))
        if st:
            for k in COLOR_KEYS:
                if k in st and st[k] not in ('none', 'transparent') and not st[k].startswith('url('):
                    st[k] = color
            e.set('style', _style_str(st))
    lg.root.set('fill', color)
    return lg


def map_colors(logo, mapping):
    """Substitui cores especificas (mapping: {'#13408f': '#ffffff'})."""
    lg = logo.copy()
    norm = {k.lower(): v for k, v in mapping.items()}
    for e in lg.root.iter():
        for k in COLOR_KEYS:
            v = e.get(k)
            if v and v.lower() in norm:
                e.set(k, norm[v.lower()])
        st = _style_dict(e.get('style'))
        if st:
            for k in COLOR_KEYS:
                if k in st and st[k].lower() in norm:
                    st[k] = norm[st[k].lower()]
            e.set('style', _style_str(st))
    return lg


def crop(logo, vb):
    lg = logo.copy()
    lg.viewbox = vb
    return lg


def inner_xml(logo):
    out = []
    for ch in logo.root:
        out.append(ET.tostring(ch, encoding='unicode'))
    s = ''.join(out)
    s = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', '', s)
    s = s.replace('ns1:href', 'xlink:href')
    return s


def place(logo, x, y, w=None, h=None, align='xMidYMid'):
    """Posiciona o logo numa caixa (unidades do documento, mm)."""
    vx, vy, vw, vh = logo.viewbox
    if w is None:
        w = h * vw / vh
    if h is None:
        h = w * vh / vw
    attrs = ''
    if logo.root.get('fill'):
        attrs = f' fill="{logo.root.get("fill")}"'
    fr = logo.root.get('fill-rule')
    if fr:
        attrs += f' fill-rule="{fr}"'
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'viewBox="{vx} {vy} {vw} {vh}" preserveAspectRatio="{align} meet" overflow="visible"{attrs}>'
            f'{inner_xml(logo)}</svg>')
