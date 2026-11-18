# PoliSat — DESIGN

Design files for Team PoliSat's **Hermes Mission** at CubeDesign 2026.

## Structure

| Path | Contents |
|---|---|
| `Design Package - Cube Design 2026.pdf` | Hermes mission design package (technical source for the banner content) |
| `logo_para_colocar_nas_imagens_geradas/` | Hermes mission patch and PoliSat logos |
| `banners/vertical_90x120cm/` | Print-ready banners, 90 × 120 cm (PDF + JPG, ~200 dpi) — 6 models |
| `banners/vertical_90x120cm/impressao_CMYK/` | **Files for the print shop:** vector PDF, 90 × 120 cm, CMYK — 7 models |
| `banners/vertical_90x120cm/previews/` | Small previews and a side-by-side comparison sheet |
| `banners/fonte_editavel/` | Editable HTML sources, fonts and assets for the banners |
| `camisetas/` | Team shirts: 3 polo, 3 cotton, 3 dry-fit — print files, tech sheets, 3D viewer (see `camisetas/README.md`) |

## Banner models

Six banners about mission Hermes and its subsystems, plus one general template. They use dark, serious grounds with
one vivid accent each (labels, numbers and a band above the footer), PoliSat renders from `banners/0 IMAGENS POLISAT/` (prepared copies in
`banner/imagens/`), the Hermes patch next to the PoliSat logo in the header, and the same footer with
**Escola Politécnica + USP** and all **9 sponsors**. The copy is
descriptive, and every number comes from the design package.

1. **Missão** — navy / yellow: what Hermes does and why from orbit, with the orbit render
2. **Payload** — charcoal / orange: the ADS-B receiver chain (antenna → RTL-SDR → Raspberry Pi → OBC)
3. **Plataforma** — dark teal / aqua: internal render and the six subsystems
4. **ADCS** — indigo / yellow and orange: reaction wheel, detumbling and pointing
5. **Comunicação** — dark plum / pink: LoRa link, antenna deployment mechanism and OBC states
6. **Estrutura** — forest green / lime: structure, power, radiation and thermal
7. **Técnico** (`vertical7_tecnico.html`) — white / navy / yellow, to pair with Missão: one-page summary of the
   design package (figures `imagens/dp_*.png` taken from it, numbered as in the DP), link and power budgets, PCBs,
   and the committee's open items (yellow "OPEN" bars) plus the on-site test matrix. Footer is 210 mm tall here.
8. **Modelo geral** (`modelo_geral.html`) — template for any occasion. Edit only the `CONTEUDO` block at the
   top: theme (`royal`, `fire`, `teal`, `violet`, `magenta`, `green`), whether to show the Hermes patch, the two header lines, image, label, title,
   text and up to four numbers. Then export.

## Sponsors

The footer is built by `banners/fonte_editavel/banner/sponsors.js`. To add or remove a sponsor, put its logo in
`banner/logos/patrocinadores/<name>_cor_fundo_claro.svg` and edit the `SPONSORS` list. Logos are sized by area,
so wide and compact marks look equally strong.

## Exporting

```sh
cd banners/fonte_editavel
npm i playwright@1.49.1 && npx playwright install chromium   # once
node exportar.js
```

This writes the JPG and PDF files (7200 × 9600 px, 90 × 120 cm, about 203 dpi), the previews and the comparison
sheet to `banners/vertical_90x120cm/`. In the HTML, 1 px equals 1 mm on the printed banner.

### Print files (send these to the print shop)

```sh
node exportar_impressao.js
```

This writes `banners/vertical_90x120cm/impressao_CMYK/<name>_90x120cm_CMYK.pdf`: exact size 900 × 1200 mm,
all colors in CMYK (Ghostscript's CMYK profile), text, logos and drawings as vectors (sharp at any size), photos
enlarged to at least ~150 dpi on the banner and shadowed elements at ~318 dpi. No bleed or crop marks are added;
if the print shop asks for bleed, the background has to be extended in the HTML. Needs Ghostscript (`gs`).

## Fonts

Archivo and IBM Plex Mono (SIL Open Font License). The word HERMES uses **ND Logos** (dafont), a demo font
licensed for personal use only — contact the authors for other uses.
