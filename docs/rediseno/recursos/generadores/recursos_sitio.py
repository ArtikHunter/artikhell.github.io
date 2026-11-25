"""Genera la carpeta recursos/ del sitio: TV, retratos revelados, copia de la carga,
carta de ajuste, texturas y fondos. Uso (desde cualquier carpeta):

    CHROMIUM_PATH=/ruta/a/chrome python3 docs/rediseno/recursos/generadores/recursos_sitio.py

Requiere numpy, Pillow y Playwright para Python (para rasterizar el TV)."""
import io
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[3]
DESTINO = REPO / 'recursos'
sys.path.insert(0, str(AQUI))
import s_tv  # noqa: E402  (solo define el TV y los stickers)

NEGRO = np.array([11, 7, 7], np.float32)
CREMA = np.array([239, 230, 210], np.float32)
ROJO = np.array([196, 42, 28], np.float32)
ROJO_OSC = np.array([94, 14, 9], np.float32)
MEDIO = np.array([132, 80, 62], np.float32)
rng = np.random.default_rng(7)


# ---------------- ruido y texturas ----------------
def periodic_noise(h, w, sigma, seed):
    n = np.random.default_rng(seed).normal(0, 1, (h, w))
    ky = np.fft.fftfreq(h)[:, None]
    kx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (kx ** 2 + ky ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(n) * g))
    return (out - out.mean()) / (out.std() + 1e-9)


def fbm(h, w, seed, scales=((90, .6), (30, .3), (8, .1))):
    acc = sum(a * periodic_noise(h, w, s, seed + i) for i, (s, a) in enumerate(scales))
    return acc / (acc.std() + 1e-9)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wrap_draw(draw_fn, size):
    for dx in (-size, 0, size):
        for dy in (-size, 0, size):
            draw_fn(dx, dy)


def tile_negro(size=512, seed=1):
    a = np.zeros((size, size, 3), np.float32) + NEGRO
    a += fbm(size, size, seed)[..., None] * np.array([4.5, 3.0, 3.0])
    a += rng.normal(0, 6.5, (size, size))[..., None] * np.array([1, .9, .85])
    im = to_img(a)
    d = ImageDraw.Draw(im, 'RGBA')
    r2 = np.random.default_rng(seed + 50)
    specks = [(r2.uniform(0, size), r2.uniform(0, size), r2.uniform(.4, 1.2), int(r2.uniform(22, 60))) for _ in range(34)]

    def dr(dx, dy):
        for x, y, r, al in specks:
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(235, 220, 200, al))
    wrap_draw(dr, size)
    return im


def tile_crema(size=512, seed=2):
    a = np.zeros((size, size, 3), np.float32) + CREMA
    a += fbm(size, size, seed)[..., None] * np.array([5, 5, 6])
    a += rng.normal(0, 4.2, (size, size))[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im, 'RGBA')
    r2 = np.random.default_rng(seed + 50)
    fibers = []
    for _ in range(360):
        x, y = r2.uniform(0, size, 2)
        L = r2.uniform(6, 40); ang = r2.uniform(0, np.pi)
        c = int(r2.uniform(150, 215))
        fibers.append(((x, y, x + L * np.cos(ang), y + L * np.sin(ang)), (c, c - 8, c - 24, int(r2.uniform(7, 22)))))

    def dr(dx, dy):
        for (x0, y0, x1, y1), col in fibers:
            d.line([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)], fill=col, width=1)
    wrap_draw(dr, size)
    return im


def halftone_layer(h, w, period, intensity, color, angle=0.0):
    rmax = period * 0.52
    sc = 2
    im = Image.new('RGBA', (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ca, sa = np.cos(angle), np.sin(angle)
    diag = int(np.hypot(w, h) / period) + 2
    for i in range(-diag, diag):
        for j in range(-diag, diag):
            u, v = i * period, j * period
            x = w / 2 + u * ca - v * sa
            y = h / 2 + u * sa + v * ca
            if x < -period or y < -period or x > w + period or y > h + period:
                continue
            t = intensity[int(np.clip(y, 0, h - 1)), int(np.clip(x, 0, w - 1))]
            r = rmax * np.sqrt(min(t, 1.0)) if t > .02 else 0
            if r >= .45:
                d.ellipse([(x - r) * sc, (y - r) * sc, (x + r) * sc, (y + r) * sc], fill=color)
    return im.resize((w, h), Image.LANCZOS)


def tile_rojo(size=512, seed=3):
    a = np.zeros((size, size, 3), np.float32) + np.array([150, 26, 17], np.float32)
    a += fbm(size, size, seed)[..., None] * np.array([16, 4, 3])
    a += rng.normal(0, 6, (size, size))[..., None] * np.array([1, .6, .6])
    im = to_img(a).convert('RGBA')
    inten = np.clip(0.35 + 0.35 * fbm(size, size, seed + 9, ((60, 1),)), 0, 1)
    im.alpha_composite(halftone_layer(size, size, 8, inten, (88, 10, 7, 120)))
    return im.convert('RGB')


def tiled(tile, w, h):
    out = Image.new('RGB', (w, h))
    for y in range(0, h, tile.height):
        for x in range(0, w, tile.width):
            out.paste(tile, (x, y))
    return out


def glow_bg(base, cx, cy, sig, strength, ht_period, ht_alpha):
    a = np.asarray(base).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sig ** 2))
    a = a + g[..., None] * ROJO * strength
    im = to_img(a).convert('RGBA')
    ring = np.clip(g * 1.25, 0, 1) * (1 - np.clip((g - .55) * 2.2, 0, 1))
    im.alpha_composite(halftone_layer(h, w, ht_period, ring, (205, 48, 30, ht_alpha), angle=np.pi / 4))
    return im.convert('RGB')


def fog_bg(w, h, crema, negro, seed=21):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / h + 0.03 * fbm(h, w, seed, ((140, .7), (50, .3)))
    t = np.clip((t - .30) / .66, 0, 1)
    t = t * t * (3 - 2 * t)
    pap = np.asarray(tiled(crema, w, h)).astype(np.float32)
    neg = np.asarray(tiled(negro, w, h)).astype(np.float32)

    def lerp(a, b, u):
        return a + (b - a) * u[..., None]
    t1 = np.clip(t / .38, 0, 1); t2 = np.clip((t - .38) / .32, 0, 1); t3 = np.clip((t - .70) / .30, 0, 1)
    col = lerp(pap, MEDIO + (pap - CREMA) * .6, t1)
    col = np.where((t > .38)[..., None], lerp(MEDIO + (neg - NEGRO) * 1.4, ROJO_OSC * .48 + (neg - NEGRO), t2), col)
    col = np.where((t > .70)[..., None], lerp(ROJO_OSC * .48 + (neg - NEGRO), neg, t3), col)
    return to_img(col)


# ---------------- fotos ----------------
def load(name, w):
    im = ImageOps.exif_transpose(Image.open(REPO / name)).convert('RGB')
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def crop_ratio(im, ratio, fy=.5, fx=.5):
    W, H = im.size
    if W / H > ratio:
        nw = round(H * ratio); x = round((W - nw) * fx)
        return im.crop((x, 0, x + nw, H))
    nh = round(W / ratio); y = round((H - nh) * fy)
    return im.crop((0, y, W, y + nh))


def grain(im, amount, seed):
    a = np.asarray(im).astype(np.float32)
    return to_img(a + np.random.default_rng(seed).normal(0, amount, a.shape[:2])[..., None])


def revelar(im, expo=1.0, gamma=1.05):
    g = np.clip(np.asarray(ImageOps.grayscale(im)).astype(np.float32) / 255 * expo, 0, 1) ** gamma
    d = np.array([12, 2, 2], np.float32); l = np.array([255, 96, 62], np.float32)
    return to_img(d + (l - d) * g[..., None])


def retrato(W, H, x_off, fy):
    """Retrato revelado: el hombre a la derecha y el muro oscuro a la izquierda para el nombre."""
    src = load('perfil.jpg', 3000)
    sh = round(H * 1.08); sw = round(src.width * sh / src.height)
    rev = revelar(src.resize((sw, sh), Image.LANCZOS), 1.0, 1.08)
    canvas = Image.new('RGB', (W, H), (12, 2, 2))
    canvas.paste(rev, (x_off, round(-(sh - H) * fy)))
    a = np.asarray(canvas).astype(np.float32)
    fade = np.clip((np.arange(W)[None, :] - x_off) / (W * .18), 0, 1)
    a = a * fade[..., None] + np.array([12, 2, 2]) * (1 - fade[..., None])
    return grain(to_img(a), 7, 5)


BARS = [(222, 220, 208), (201, 176, 55), (63, 167, 181), (76, 154, 74), (176, 74, 143), (215, 48, 31), (45, 63, 160)]


def carta_ajuste(w, h, sc=2):
    W, H = w * sc, h * sc
    im = Image.new('RGB', (W, H), (38, 37, 34))
    d = ImageDraw.Draw(im)
    step = 40 * sc
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(84, 82, 76), width=sc)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(84, 82, 76), width=sc)
    R = int(min(W, H) * 0.44); cx, cy = W // 2, H // 2
    circ = Image.new('L', (W, H), 0)
    ImageDraw.Draw(circ).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    inner = Image.new('RGB', (W, H), (20, 20, 18))
    di = ImageDraw.Draw(inner)
    bw = 2 * R / len(BARS)
    for i, c in enumerate(BARS):
        di.rectangle([cx - R + i * bw, cy - R, cx - R + (i + 1) * bw, cy - int(R * .22)], fill=c)
    di.rectangle([cx - R, cy - int(R * .22), cx + R, cy + int(R * .22)], fill=(10, 10, 9))
    for i in range(6):
        g = int(20 + i * 42)
        di.rectangle([cx - R + i * (2 * R / 6), cy + int(R * .22), cx - R + (i + 1) * (2 * R / 6), cy + int(R * .6)], fill=(g, g, g - 4))
    for i in range(0, 2 * R, 6 * sc):
        di.rectangle([cx - R + i, cy + int(R * .6), cx - R + i + 3 * sc, cy + R], fill=(200, 198, 188))
    im.paste(inner, (0, 0), circ)
    d = ImageDraw.Draw(im)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(232, 230, 218), width=2 * sc)
    return im.resize((w, h), Image.LANCZOS)


def textura_pintada(im):
    """Grano, vetas de pincel y manchas suaves sobre el TV rasterizado (conserva la transparencia)."""
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    r = np.random.default_rng(5)

    def ruido(h, w):
        n = (r.normal(0, 1, (h, w)) * 40 + 128).clip(0, 255).astype(np.uint8)
        return np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC)).astype(np.float32) / 128 - 1
    m = 1 + 0.05 * r.normal(0, 1, (H, W)) + 0.07 * ruido(H // 14 + 1, W // 2 + 1) + 0.06 * ruido(H // 90 + 2, W // 90 + 2)
    a[..., :3] = np.clip(a[..., :3] * m[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def render_svg(svg, escala):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        page = browser.new_page(viewport={'width': 1200, 'height': 1000}, device_scale_factor=escala)
        page.set_content('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:transparent}svg{display:block}</style>' + svg)
        png = page.locator('svg').screenshot(omit_background=True)
        browser.close()
    return Image.open(io.BytesIO(png)).convert('RGBA')


def guardar(im, nombre, **kw):
    ruta = DESTINO / nombre
    im.save(ruta, **kw)
    print(f'{nombre:22s} {im.size[0]}×{im.size[1]}  {ruta.stat().st_size // 1024} KB')


def main():
    DESTINO.mkdir(exist_ok=True)
    negro, crema, rojo = tile_negro(), tile_crema(), tile_rojo()
    guardar(negro, 'textura-negro.jpg', quality=86, optimize=True, progressive=True)
    guardar(crema, 'textura-crema.jpg', quality=86, optimize=True, progressive=True)
    guardar(rojo, 'textura-rojo.jpg', quality=86, optimize=True, progressive=True)
    guardar(glow_bg(tiled(negro, 1920, 1200), 960, 600, 330, .34, 12, 110), 'fondo-tv.jpg', quality=80, optimize=True, progressive=True)
    guardar(fog_bg(1920, 1200, crema, negro), 'liquido.jpg', quality=80, optimize=True, progressive=True)
    guardar(retrato(2400, 1500, 600, .25), 'retrato.jpg', quality=78, optimize=True, progressive=True)
    vertical = crop_ratio(retrato(3420, 1920, 0, 0), 1080 / 1920, .5, .52).resize((1080, 1920), Image.LANCZOS)
    guardar(vertical, 'retrato-movil.jpg', quality=78, optimize=True, progressive=True)
    copia = crop_ratio(load('DR-1.jpg', 1400), 560 / 700, .5, .30).resize((560, 700), Image.LANCZOS)
    guardar(grain(revelar(copia), 8, 61), 'carga.jpg', quality=82, optimize=True, progressive=True)
    guardar(carta_ajuste(600, 450), 'carta-ajuste.png', optimize=True)
    tv = textura_pintada(render_svg(s_tv.tv_svg(None, '', solo_marco=True), 2))
    guardar(tv, 'tv.webp', quality=82, method=6)
    guardar(tv.resize((900, round(tv.height * 900 / tv.width)), Image.LANCZOS), 'tv-movil.webp', quality=84, method=6)


if __name__ == '__main__':
    main()
