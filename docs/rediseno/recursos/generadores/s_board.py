"""Rellena la plantilla de tableros (stickers sobre el TV, lámpara, hoja de stickers, TV vectorial) e incrusta los recursos."""
import os, re, json, base64, sys

S = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(S, 'assets')
tpl = open(os.path.join(S, 's_boards.tpl.html')).read()
meta = json.load(open(os.path.join(A, 's_stickers.json')))


def sticker(name, left, top, width, rot, extra=''):
    w, h = meta[name]
    svg = open(os.path.join(A, f's_st_{name}.svg')).read()
    svg = re.sub(r' width="\d+" height="\d+"', '', svg, count=1)
    height = width * h / w
    return (f'<div class="stk" data-sticker="{name}" style="left:{left:.0f}px;top:{top:.0f}px;width:{width:.0f}px;height:{height:.0f}px;'
            f'transform:rotate({rot}deg){extra}">{svg}</div>')


def on_tv(ox, oy, s):
    """Posiciones en coordenadas del SVG del TV (1100×960) → página."""
    P = [('perro', 186, 708, 200, -5), ('diablo', 150, 300, 108, -12), ('estrella', 762, 306, 60, 8), ('copihue', 758, 598, 70, 14)]
    return ''.join(sticker(n, ox + x * s, oy + y * s, w * s, r) for n, x, y, w, r in P)


def lamp(cx, top, scale=1.0):
    s = scale
    return (f'<svg class="lamp" style="left:{cx - 80 * s:.0f}px;top:{top}px" width="{160 * s:.0f}" height="{170 * s:.0f}" viewBox="0 0 160 170">'
            '<line x1="80" y1="0" x2="80" y2="62" stroke="#140807" stroke-width="3"/>'
            '<path d="M44 62 L116 62 L132 118 L28 118 Z" fill="#1c0b09" stroke="#140807" stroke-width="3"/>'
            '<rect x="30" y="112" width="100" height="16" rx="3" fill="#ff5c3c"/>'
            '<rect x="30" y="112" width="100" height="16" rx="3" fill="none" stroke="#140807" stroke-width="3"/>'
            '<path d="M38 128 L122 128 L150 170 L10 170 Z" fill="#ff5c3c" opacity=".16"/>'
            '<rect x="40" y="115" width="44" height="4" rx="2" fill="#ffd9cc" opacity=".8"/>'
            '</svg>')


sheet = ''.join(sticker(n, 0, 0, meta[n][0] * .82, 0).replace('position:absolute', '').replace('class="stk"', 'class="stk" style-pos="static"').replace('left:0px;top:0px;', 'position:relative;') for n in meta)
tv_vec = open(os.path.join(A, 's_tv_vec.svg')).read().replace('width="1100" height="960"', 'width="620" height="541"')
env = sticker('altiro', 22, 268, 130, 8)

html = (tpl.replace('{{TV_STICKERS}}', on_tv(225, 18, .9))
           .replace('{{M_TV_STICKERS}}', on_tv(20, 214, 350 / 1100))
           .replace('{{LAMP_DESK}}', lamp(720, 0))
           .replace('{{LAMP_MOB}}', lamp(195, 0, .6))
           .replace('{{STICKER_SHEET}}', sheet)
           .replace('{{TV_VEC}}', tv_vec)
           .replace('{{ENV_STICKER}}', env))
open(os.path.join(S, 's_boards.src.html'), 'w').write(html)

# incrustar fuentes e imágenes (src=, href= y url())
html = html.replace('/*FONTS*/', open(os.path.join(A, 'fonts.css')).read())
cache = {}
def uri(p):
    if p not in cache:
        mime = 'image/png' if p.endswith('.png') else 'image/jpeg'
        cache[p] = f'data:{mime};base64,' + base64.b64encode(open(os.path.join(S, p), 'rb').read()).decode()
    return cache[p]
html = re.sub(r'(?<=src=")(assets/[^"]+)', lambda m: uri(m.group(1)), html)
html = re.sub(r'(?<=href=")(assets/[^"]+)', lambda m: uri(m.group(1)), html)
html = re.sub(r'url\((assets/[^)]+)\)', lambda m: 'url(' + uri(m.group(1)) + ')', html)
open(os.path.join(S, 's_boards.html'), 'w').write(html)
print('s_boards.html', round(len(html) / 1e6, 2), 'MB', len(cache), 'assets')
