# Hermes jury banner (LaTeX, 90 × 120 cm)

A technical banner for the jury, which has already read the Design Package. Every design choice is shown with its
reason, and a matrix traces each HLR in "Rules 2026 - CubeSat" to its panel and verification method. Numbers come
from the Design Package; values marked `[derived]` are arithmetic on DP values, so the jury can check them.

| File | Contents |
|---|---|
| `hermes_banca_90x120cm.pdf` | Compiled banner (RGB), to review or share |
| `hermes_banca_90x120cm_CMYK_print.pdf` | **Print file**: CMYK (Ghostscript default_cmyk.icc), vector text and graphics, fonts embedded, images not downsampled or recompressed (lossless Flate, 203–520 ppi at final size) |
| `hermes_banca_preview.png` | Small preview |
| `main.tex` | Source: panels marked `% N · ...`, all coordinates in mm from the top left corner |
| `hermes_banca_overleaf.zip` | Ready to upload to Overleaf |
| `fonts/`, `imagens/`, `logos/` | Archivo, IBM Plex Mono, ND Logos; DP figures; PoliSat, Poli and USP logos |

Overleaf: New Project → Upload Project → `hermes_banca_overleaf.zip`, then Menu → Compiler → **XeLaTeX**.
Locally: `xelatex main.tex`.

Panels: 1 processing architecture (onboard / ground split), 2 payload front end and the ADS-B link budget,
3 decoder and data products (frame, required fields, HLR-ADS-08 metrics), 4 secondary mission, 5 TT&C,
6 EPS, 7 ADCS, 8 flight software, 9 structure, 10 thermal control, then the traceability matrix.

The HLR-ADS-08 metric definitions in panel 3 (decoded messages, data loss, latency) say how each metric is computed
from the logs. They give no target values, because the DP does not set any.
