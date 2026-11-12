"""Monta um pacote .zip por modelo com tudo o que a grafica precisa para produzir a camiseta.

Rode depois de `python3 build.py` e `node render.js` (precisa das fichas tecnicas em PDF e dos mockups).

    python3 pacotes.py                      # grava em ../visualizador_3d/downloads/
    python3 pacotes.py --out ../../camisetas-3d/downloads

Cada pacote contem:
    LEIA-ME.txt                    instrucoes para a grafica (tecido, tecnica, aplicacoes, cores)
    ficha_tecnica_XX.pdf / .png    ficha A3 com cotas
    impressao/                     arquivos de producao vetoriais 1:1 (SVG + PDF)
    mockups/                       imagens para aprovacao

Os zips sao deterministicos (data fixa, ordem fixa): gerar de novo sem mudar o design produz arquivos identicos.
Tambem grava `pacotes.js` (window.PACOTES) que o visualizador usa para mostrar os botoes de download.
"""
import argparse
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DEFAULT = os.path.join(HERE, '..', 'visualizador_3d', 'downloads')
DATE = (2026, 1, 1, 0, 0, 0)


def leia_me(f):
    L = []
    a = L.append
    a(f'POLISAT - CAMISETAS 2026 - MODELO {f["id"]} {f["nome"].upper()}  ({f["tipo"]})')
    a('=' * 72)
    a('')
    a(f'Tecido:   {f["tecido"]}')
    a(f'Tecnica:  {f["tecnica"]}')
    if f.get('gola'):
        a(f'Gola:     {f["gola"]}')
    a('Tamanho de referencia: M. Medidas em milimetros, escala 1:1.')
    a('Posicoes medidas a partir do HPS (ponto alto do ombro) e da linha central da peca;')
    a('na frente, x positivo = lado ESQUERDO de quem veste. Nas mangas, y conta da costura do ombro.')
    a('')
    a('CONTEUDO DO PACOTE')
    a('-' * 72)
    a(f'ficha_tecnica_{f["id"]}.pdf   Ficha tecnica A3: vistas com cotas, aplicacoes, cores e observacoes.')
    a('impressao/            ARQUIVOS DE PRODUCAO (vetor, escala 1:1). SVG e PDF com o mesmo conteudo.')
    a('mockups/              Imagens 3D apenas para aprovacao (nao usar para producao).')
    a('')
    if f['sub']:
        a('SUBLIMACAO TOTAL')
        a('-' * 72)
        a('- Paineis inteiros com sangria: frente e costas 600 x 780 mm, mangas 460 x 270 mm, gola 1000 x 120 mm.')
        a(f'- {f["id"]}_costas_sem_nome: arquivo de producao das costas (sem nome).')
        a(f'- {f["id"]}_costas_exemplo_nome: so referencia de como fica com o nome.')
        a(f'- {f["id"]}_nome_editavel.svg + lista_nomes.csv: nome de cada pessoa, aplicado na area reservada')
        nm = f.get('name') or {}
        if nm:
            a(f'  no fim das costas (centro a {nm["y"]} mm do HPS, area {nm["w"]} x {nm["h"]} mm, fonte ND Logos).')
        a('- guias/: contorno do molde, linha central e HPS para conferir o encaixe. Nao imprimir.')
        a('- Para outros tamanhos, ajuste o molde mantendo os elementos centrados na linha central.')
    else:
        a('APLICACOES')
        a('-' * 72)
        for p in f['placements']:
            cores = ', '.join(f'{c[0]} ({c[2]})' for c in p['cores'])
            a(f'- {p["label"]}')
            ref = 'da costura do ombro (topo da manga)' if p['panel'].startswith('manga') else 'do HPS'
            a(f'    painel: {p["panel"]} | tamanho: {p["w"]:.0f} x {p["h"]:.0f} mm | '
              f'canto sup. esq.: x={p["x"]:.0f} mm da linha central, y={p["y"]:.0f} mm {ref}')
            a(f'    tecnica: {p["tecnica"]}')
            if cores:
                a(f'    cores: {cores}')
        a('')
        a('- O nome de cada arquivo traz a aplicacao e o tamanho final (ex.: A1_peito_polisat_100x53mm).')
        a('- Logos brancos parecem invisiveis em leitores de PDF com fundo branco: o fundo e transparente.')
    a('')
    a('OBSERVACOES')
    a('-' * 72)
    a('- Textos ja convertidos em curvas (nao precisa instalar fontes).')
    a('- Cores Pantone aproximadas: pedir prova de cor antes da producao.')
    a('- Duvidas: equipe PoliSat - Escola Politecnica da USP.')
    return '\r\n'.join(L) + '\r\n'


def add(z, path, arc):
    zi = zipfile.ZipInfo(arc, DATE)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.external_attr = 0o644 << 16
    with open(path, 'rb') as fh:
        z.writestr(zi, fh.read(), compresslevel=9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_DEFAULT)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(HERE, 'jobs.json'), encoding='utf-8') as fh:
        jobs = json.load(fh)
    index = {}
    missing = []
    for f in jobs['ficha_data']:
        d, mid = f['dir'], f['id']
        files = []
        for fn in (f'ficha_tecnica_{mid}.pdf', f'ficha_tecnica_{mid}.png'):
            files.append((os.path.join(d, fn), fn))
        imp = os.path.join(d, 'impressao')
        for root, _, names in os.walk(imp):
            for n in names:
                p = os.path.join(root, n)
                files.append((p, os.path.relpath(p, d).replace(os.sep, '/')))
        for v in ('frente', 'costas', 'lado'):
            fn = f'mockup_{mid}_{v}.png'
            files.append((os.path.join(d, fn), 'mockups/' + fn))
        for p, _ in files:
            if not os.path.isfile(p):
                missing.append(p)
        if missing:
            continue
        top = f'{mid}_{f["slug"]}'
        zpath = os.path.join(out, top + '.zip')
        tmp = zpath + '.tmp'
        with zipfile.ZipFile(tmp, 'w') as z:
            zi = zipfile.ZipInfo(top + '/LEIA-ME.txt', DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, leia_me(f).encode('utf-8'))
            for p, arc in sorted(files, key=lambda t: t[1]):
                add(z, p, f'{top}/{arc}')
        os.replace(tmp, zpath)
        index[mid] = {'zip': f'downloads/{top}.zip', 'kb': os.path.getsize(zpath) // 1024, 'n': len(files) + 1}
    if missing:
        print('Faltam arquivos (rode build.py e render.js antes):', *missing[:10], sep='\n  ')
        sys.exit(1)
    with open(os.path.join(out, 'pacotes.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('// Gerado por _fonte/pacotes.py — nao editar a mao\n')
        fh.write(f'window.PACOTES = {json.dumps(index, ensure_ascii=False)};\n')
    total = sum(v['kb'] for v in index.values())
    print(f'{len(index)} pacotes em {out} | total {total / 1024:.1f} MB')


if __name__ == '__main__':
    main()
