# PoliSat — DESIGN

Design files for Team PoliSat's **Hermes Mission** at CubeDesign 2026.

## Structure

| Path | Contents |
|---|---|
| `Design Package - Cube Design 2026.pdf` | Hermes mission design package (technical source for the banner content) |
| `logo_para_colocar_nas_imagens_geradas/` | Hermes mission patch and PoliSat logos |
| `banners/vertical_90x120cm/` | Print-ready banners, 90 × 120 cm (PDF + JPG, ~200 dpi) — 6 models |
| `banners/vertical_90x120cm/previews/` | Small previews and a side-by-side comparison sheet |
| `banners/fonte_editavel/` | Editable HTML sources, fonts and assets for the banners |
| `camisetas/` | Team shirts: 3 polo, 3 cotton, 3 dry-fit — print files, tech sheets, 3D viewer (see `camisetas/README.md`) |

## Banner models

All six share one system: flat colour, Archivo + IBM Plex Mono, the mission patch, and the same footer with
**Escola Politécnica + USP** and all **9 sponsors**. Every number on the banners comes from the design package.

1. **Céu** — sky blue, "Built to listen. Built to last.", Earth limb with three proof stats
2. **Margens** — paper, "Small satellite. Serious engineering.", list of link, structural and radiation margins
3. **Impulso** — flame orange, "Aim high. Then engineer it.", how it works in four steps
4. **Projeto** — PoliSat blue, "Designed by students. Engineered to fly.", 2U CubeSat line drawing with subsystems
5. **Destino** — cream, "Next stop: low Earth orbit.", oversized patch and team milestones
6. **Equipe** — navy, "27 students. 9 courses. 1 satellite.", competition results

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

## Fonts

Archivo and IBM Plex Mono (SIL Open Font License). The word HERMES uses **ND Logos** (dafont), a demo font
licensed for personal use only — contact the authors for other uses.
