"""Prepara fuentes (base64) e imágenes tratadas para los tableros de Figma."""
import base64, io, re, sys, urllib.request, os, json
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw

S = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/user/artikhell.github.io'
OUT = os.path.join(S, 'assets')
os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'

# ---------- fuentes: solo subconjunto latin ----------
css = open(os.path.join(S, 'fonts', 'fonts.css')).read()
blocks = re.findall(r'/\* (\S+) \*/\s*(@font-face\s*{[^}]*})', css)
faces = []
cache = {}
for subset, block in blocks:
    if subset != 'latin':
        continue
    url = re.search(r'url\((https://[^)]+)\)', block).group(1)
    if url not in cache:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        cache[url] = base64.b64encode(urllib.request.urlopen(req).read()).decode()
    block = block.replace(url, 'data:font/woff2;base64,' + cache[url])
    block = re.sub(r'\s*unicode-range:[^;]*;', '', block)
    faces.append(block)
open(os.path.join(OUT, 'fonts.css'), 'w').write('\n'.join(faces))
print('font faces', len(faces), 'files', len(cache))

# ---------- utilidades de imagen ----------
def load(name, w):
    im = Image.open(os.path.join(REPO, name)).convert('RGB')
    im = ImageOps.exif_transpose(im)
    h = round(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)

def crop_ratio(im, ratio, fy=0.5, fx=0.5):
    W, H = im.size
    if W / H > ratio:
        nw = round(H * ratio); x = round((W - nw) * fx)
        return im.crop((x, 0, x + nw, H))
    nh = round(W / ratio); y = round((H - nh) * fy)
    return im.crop((0, y, W, y + nh))

def grain(im, amount=14, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(im).astype(np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def duotone(im, dark, light, gamma=1.0):
    g = np.asarray(ImageOps.grayscale(im)).astype(np.float32) / 255
    g = g ** gamma
    d = np.array(dark, np.float32); l = np.array(light, np.float32)
    out = d + (l - d) * g[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

def bw(im, contrast=1.35):
    g = ImageOps.grayscale(im)
    g = ImageEnhance.Contrast(g).enhance(contrast)
    return g.convert('RGB')

def crt(im, w=880, h=660):
    """Pantalla CRT: barril, líneas de barrido, viñeta y brillo."""
    im = crop_ratio(im, 4 / 3).resize((w, h), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / (w - 1)) * 2 - 1; ny = (yy / (h - 1)) * 2 - 1
    r2 = nx * nx + ny * ny
    k = 0.10
    sx = nx * (1 + k * r2); sy = ny * (1 + k * r2)
    px = ((sx + 1) / 2 * (w - 1)).clip(0, w - 1).astype(int)
    py = ((sy + 1) / 2 * (h - 1)).clip(0, h - 1).astype(int)
    out = a[py, px]
    outside = (np.abs(sx) > 1) | (np.abs(sy) > 1)
    # líneas de barrido + máscara RGB sutil
    scan = 0.80 + 0.20 * (np.sin(yy * np.pi / 2.0) ** 2)
    out = out * scan[..., None]
    trip = np.stack([(xx % 3 == 0), (xx % 3 == 1), (xx % 3 == 2)], -1).astype(np.float32)
    out = out * (0.90 + 0.10 * trip)
    # viñeta + bloom
    vig = np.clip(1.15 - 0.55 * r2, 0, 1)
    out = out * vig[..., None]
    out = out * 1.08 + 0.03
    out[outside] = 0.02
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    glow = img.filter(ImageFilter.GaussianBlur(6))
    img = Image.blend(img, glow, 0.18)
    return grain(img, 9, 3)

def save(im, name, q=80):
    p = os.path.join(OUT, name)
    if name.endswith('.png'):
        im.save(p, optimize=True)
    else:
        im.save(p, quality=q, optimize=True, progressive=True)
    return p

def noise_tile(size, base, amount, seed, fibers=False, alpha=None):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (size, size))
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) - 128
    arr = np.array(base, np.float32)[None, None, :] + n[..., None] * amount / 40
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    if fibers:
        d = ImageDraw.Draw(img, 'RGBA')
        for _ in range(int(size * 0.9)):
            x, y = rng.uniform(0, size, 2)
            L = rng.uniform(8, 46); ang = rng.uniform(0, np.pi)
            c = int(rng.uniform(150, 205))
            d.line([(x, y), (x + L * np.cos(ang), y + L * np.sin(ang))], fill=(c, c - 6, c - 18, int(rng.uniform(18, 48))), width=1)
    return img

# ---------- texturas ----------
save(noise_tile(512, (239, 233, 220), 7, 11, fibers=True), 'washi.jpg', 84)
save(noise_tile(512, (229, 222, 206), 8, 12, fibers=True), 'washi2.jpg', 84)
save(noise_tile(512, (214, 203, 180), 10, 13, fibers=False), 'salitre.jpg', 82)
save(noise_tile(512, (12, 11, 10), 6, 14), 'negro.jpg', 82)
save(noise_tile(512, (92, 14, 9), 9, 15), 'rojo.jpg', 82)

# ---------- fotos ----------
P = {}
def put(key, im, name, q=80):
    save(im, name, q); P[key] = name

# Dirección 1 — Señal
put('d1_crt', crt(load('DR-1.jpg', 1200)), 'd1_crt.jpg', 84)
put('d1_crt_m', crt(load('DR-4.jpg', 1200), 700, 525), 'd1_crt_m.jpg', 84)
for i, (f, fy) in enumerate([('CFC-20.jpg', .5), ('AH-1.jpg', .5), ('VENT-1.jpg', .5), ('HM-10.jpg', .5)]):
    put(f'd1_still{i}', grain(crop_ratio(load(f, 900), 4 / 3, fy), 8, i), f'd1_still{i}.jpg')
put('d1_film', grain(crop_ratio(load('remake-5.jpg', 1600), 16 / 9, .55), 8, 7), 'd1_film.jpg')
put('d1_film2', grain(crop_ratio(load('HM-1.jpg', 1000), 16 / 9, .6), 8, 8), 'd1_film2.jpg')
put('d1_portrait', crt(load('perfil.jpg', 1000), 480, 360), 'd1_portrait.jpg')
for i, f in enumerate(['FECH-1.jpg', 'FECH-5.jpg', 'FECH-9.jpg']):
    put(f'd1_arch{i}', grain(crop_ratio(load(f, 600), 4 / 3), 8, 20 + i), f'd1_arch{i}.jpg')

# Dirección 2 — Pliego
put('d2_hero', grain(crop_ratio(load('DR-1.jpg', 1400), 1.37), 6, 30), 'd2_hero.jpg')
put('d2_p1', grain(load('IQQ-1.jpg', 1100), 6, 31), 'd2_p1.jpg')
put('d2_p2', grain(load('AH-1.jpg', 800), 6, 32), 'd2_p2.jpg')
put('d2_p3', grain(load('HM-10.jpg', 800), 6, 33), 'd2_p3.jpg')
put('d2_p4', grain(load('CFC-1.jpg', 800), 6, 34), 'd2_p4.jpg')
put('d2_film1', grain(bw(crop_ratio(load('remake-3.jpg', 1000), 4 / 5, .5)), 12, 35), 'd2_film1.jpg')
put('d2_film2', grain(bw(crop_ratio(load('HM-1.jpg', 1000), 4 / 5, .5, .62)), 12, 36), 'd2_film2.jpg')
put('d2_stamp', grain(crop_ratio(load('perfil.jpg', 600), 4 / 5, .5), 6, 37), 'd2_stamp.jpg')
for i, f in enumerate(['FECH-1.jpg', 'FECH-5.jpg', 'FECH-9.jpg']):
    put(f'd2_arch{i}', grain(crop_ratio(load(f, 500), 1.25), 7, 40 + i), f'd2_arch{i}.jpg')
put('d2_mhero', grain(crop_ratio(load('CFC-20.jpg', 900), 4 / 5), 6, 45), 'd2_mhero.jpg')

# Dirección 3 — Cuarto rojo
put('d3_hero', grain(duotone(crop_ratio(load('DR-1.jpg', 1800), 16 / 10, .45), (14, 2, 2), (255, 92, 60), 1.05), 10, 50), 'd3_hero.jpg', 82)
put('d3_portrait', grain(bw(crop_ratio(load('perfil.jpg', 1000), 4 / 5, .45), 1.25), 12, 51), 'd3_portrait.jpg')
put('d3_s1', grain(duotone(load('IQQ-1.jpg', 1200), (54, 36, 20), (240, 230, 208), 0.9), 9, 52), 'd3_s1.jpg')
put('d3_s2', grain(load('AH-10.jpg', 900), 9, 53), 'd3_s2.jpg')
put('d3_s3', grain(load('MX-1.jpg', 900), 9, 54), 'd3_s3.jpg')
put('d3_s4', grain(load('HM-1.jpg', 900), 9, 55), 'd3_s4.jpg')
put('d3_film', grain(crop_ratio(load('TREN-1.jpg', 1800), 2.39, .5), 10, 56), 'd3_film.jpg')
put('d3_film2', grain(bw(crop_ratio(load('remake-3.jpg', 900), 2.39, .45)), 12, 57), 'd3_film2.jpg')
for i, f in enumerate(['FECH-1.jpg', 'FECH-5.jpg', 'FECH-9.jpg']):
    put(f'd3_arch{i}', grain(duotone(crop_ratio(load(f, 500), 1.25), (10, 4, 3), (236, 226, 208)), 9, 60 + i), f'd3_arch{i}.jpg')
put('d3_loader', grain(duotone(crop_ratio(load('remake-5.jpg', 700), 4 / 5), (40, 4, 3), (205, 60, 40), 1.4), 14, 64), 'd3_loader.jpg')
put('d3_mhero', grain(duotone(crop_ratio(load('DR-4.jpg', 900), 9 / 16, .5, .62), (14, 2, 2), (255, 92, 60), 1.05), 10, 65), 'd3_mhero.jpg')

json.dump(P, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
print(len(P), 'images')

# --- ajustes (segunda pasada) ---
put('d3_mhero', grain(duotone(crop_ratio(load('DR-1.jpg', 1800), 9 / 16, .5, .30), (14, 2, 2), (255, 92, 60), 1.0), 10, 65), 'd3_mhero.jpg', 82)
put('d3_loader', grain(duotone(crop_ratio(load('remake-5.jpg', 700), 4 / 5), (40, 4, 3), (225, 80, 56), 1.0), 14, 64), 'd3_loader.jpg')
json.dump(P, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
