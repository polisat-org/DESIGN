"""PNG (7200 x 9600) -> print JPG + 90 x 120 cm PDF, small previews and the comparison sheet."""
import sys, os, glob
from PIL import Image
out = sys.argv[1]
DPI = 7200 / (900 / 25.4)  # 90 cm wide
thumbs = []
for png in sorted(glob.glob(os.path.join(out, 'vertical*_90x120cm.png'))):
    im = Image.open(png).convert('RGB')
    base = png[:-4]
    im.save(base + '.jpg', quality=93, dpi=(DPI, DPI))
    im.save(base + '.pdf', resolution=DPI, title=os.path.basename(base))
    t = im.resize((900, 1200), Image.LANCZOS)
    t.save(os.path.join(out, 'previews', os.path.basename(base).replace('_90x120cm', '') + '.png'))
    thumbs.append(t); os.remove(png); print('exported', os.path.basename(base))
if thumbs:
    sheet = Image.new('RGB', (900 * 3 + 40, 1200 * 2 + 20), (128, 128, 128))
    for i, t in enumerate(thumbs[:6]):
        sheet.paste(t, ((i % 3) * 920, (i // 3) * 1220))
    sheet.save(os.path.join(out, 'previews', 'comparativo_6_modelos.png'))
