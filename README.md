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

1. **Horizonte** — Earth horizon with ADS-B aircraft
2. **Radar** — ADS-B radar screen and subsystems grid
3. **Mensageiro** — diagonal red band and "how it works" steps
4. **Blueprint** — technical drawing of the CubeSat with subsystem callouts
5. **Poster** — light Swiss-style poster
6. **Órbita** — signal path: aircraft → orbit → ground station

## Sponsors

The sponsor band at the bottom currently shows placeholders. To add logos, copy the image files into
`banners/fonte_editavel/banner/` and list them in `banners/fonte_editavel/banner/sponsors.js`:

```js
const SPONSORS = ['logo1.png', 'logo2.png'];
```

Then re-export the print files.

## Fonts

Orbitron, Rajdhani and Exo 2 (SIL Open Font License). Titles use **ND Logos** (dafont), a demo font
licensed for personal use only — contact the authors for other uses.
