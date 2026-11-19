# Hermes technical banner: LaTeX version

LaTeX version of `banners/fonte_editavel/banner/vertical7_tecnico.html`: one page, 900 × 1200 mm, drawn with TikZ.
Each element sits at the same millimetre coordinates as in the HTML (1 px = 1 mm), measured from the top left corner.

## Overleaf

1. New Project → Upload Project → `hermes_tecnico_overleaf.zip` (or upload this folder's contents).
2. Menu → Compiler → **XeLaTeX** (the `latexmkrc` already asks for it) and Main document `main.tex`.
3. Recompile. The first compile of a 90 × 120 cm page takes a little longer.

| Path | Contents |
|---|---|
| `main.tex` | The banner. Panels are marked `% ===== N · ... =====`; text is plain LaTeX inside `\T{x}{y}{width}{...}`, `\li{...}` and `\onsite{x}{y}{width}{...}` |
| `fonts/` | Archivo (static instances cut from the variable font), IBM Plex Mono, ND Logos |
| `imagens/` | Figures from the Design Package (`dp_*.png`) and the mission patch |
| `logos/` | PoliSat, Escola Politécnica and USP logos as vector PDF |

Locally: `xelatex main.tex` (TeX Live 2022 or newer).

The PDF is RGB. For the print shop, use `banners/vertical_90x120cm/impressao_CMYK/vertical7_tecnico_90x120cm_CMYK.pdf`,
or convert this PDF with Ghostscript as in `banners/fonte_editavel/exportar_impressao.js`.

Fonts: Archivo and IBM Plex Mono are under the SIL Open Font License. ND Logos is a demo font for personal use only.
