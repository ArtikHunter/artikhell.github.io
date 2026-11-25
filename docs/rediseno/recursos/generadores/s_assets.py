"""Síntesis «Revelado»: texturas, fondos de sección y tratamientos de foto."""
import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance, ImageChops

S = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/user/artikhell.github.io'
OUT = os.path.join(S, 'assets')
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(7)

NEGRO = np.array([11, 7, 7], np.float32)
CREMA = np.array([239, 230, 210], np.float32)
ROJO = np.array([196, 42, 28], np.float32)
ROJO_OSC = np.array([94, 14, 9], np.float32)
MEDIO = np.array([132, 80, 62], np.float32)  # niebla óxido entre papel y cuarto


# ---------------- ruido ----------------
def periodic_noise(h, w, sigma, seed):
    """Ruido gaussiano filtrado en frecuencia: sin costuras (repetible)."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h, w))
    ky = np.fft.fftfreq(h)[:, None]
    kx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (kx ** 2 + ky ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(n) * g))
    return (out - out.mean()) / (out.std() + 1e-9)


def fbm(h, w, seed, scales=((90, .6), (30, .3), (8, .1))):
    acc = np.zeros((h, w))
    for i, (s, a) in enumerate(scales):
        acc += a * periodic_noise(h, w, s, seed + i)
    return acc / (acc.std() + 1e-9)


def wrap_draw(draw_fn, size):
    for dx in (-size, 0, size):
        for dy in (-size, 0, size):
            draw_fn(dx, dy)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def save(im, name, q=86):
    p = os.path.join(OUT, name)
    if name.endswith('.png'):
        im.save(p, optimize=True)
    else:
        im.convert('RGB').save(p, quality=q, optimize=True, progressive=True)
    return name


# ---------------- texturas repetibles ----------------
def tile_negro(size=512, seed=1):
    a = np.zeros((size, size, 3), np.float32) + NEGRO
    a += fbm(size, size, seed)[..., None] * np.array([4.5, 3.0, 3.0])
    a += RNG.normal(0, 6.5, (size, size))[..., None] * np.array([1, .9, .85])
    im = to_img(a)  # RGB: así ImageDraw mezcla con transparencia
    d = ImageDraw.Draw(im, 'RGBA')
    rng = np.random.default_rng(seed + 50)
    specks = [(rng.uniform(0, size), rng.uniform(0, size), rng.uniform(.4, 1.2), int(rng.uniform(22, 60))) for _ in range(34)]
    hairs = []
    for _ in range(2):
        x, y = rng.uniform(0, size, 2)
        pts = [(x, y)]
        ang = rng.uniform(0, 2 * np.pi)
        for _ in range(18):
            ang += rng.normal(0, .25)
            x += 3 * np.cos(ang); y += 3 * np.sin(ang)
            pts.append((x, y))
        hairs.append((pts, int(rng.uniform(6, 12))))

    def dr(dx, dy):
        for x, y, r, al in specks:
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(235, 220, 200, al))
        for pts, al in hairs:
            d.line([(px + dx, py + dy) for px, py in pts], fill=(230, 215, 195, al), width=1)
    wrap_draw(dr, size)
    return im.convert('RGB')


def tile_crema(size=512, seed=2):
    a = np.zeros((size, size, 3), np.float32) + CREMA
    a += fbm(size, size, seed)[..., None] * np.array([5, 5, 6])
    a += RNG.normal(0, 4.2, (size, size))[..., None]
    im = to_img(a)  # RGB: así ImageDraw mezcla con transparencia
    d = ImageDraw.Draw(im, 'RGBA')
    rng = np.random.default_rng(seed + 50)
    fibers = []
    for _ in range(360):
        x, y = rng.uniform(0, size, 2)
        L = rng.uniform(6, 40); ang = rng.uniform(0, np.pi)
        c = int(rng.uniform(150, 215))
        fibers.append(((x, y, x + L * np.cos(ang), y + L * np.sin(ang)), (c, c - 8, c - 24, int(rng.uniform(7, 22)))))
    for _ in range(40):
        x, y = rng.uniform(0, size, 2)
        L = rng.uniform(6, 30); ang = rng.uniform(0, np.pi)
        fibers.append(((x, y, x + L * np.cos(ang), y + L * np.sin(ang)), (255, 252, 244, 40)))

    def dr(dx, dy):
        for (x0, y0, x1, y1), col in fibers:
            d.line([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)], fill=col, width=1)
    wrap_draw(dr, size)
    return im.convert('RGB')


def halftone_layer(h, w, period, intensity, color, rmax=None, angle=0.0):
    """Puntos de trama (Ben-Day) cuyo radio sigue `intensity` (0..1)."""
    rmax = rmax or period * 0.52
    sc = 2
    im = Image.new('RGBA', (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ca, sa = np.cos(angle), np.sin(angle)
    diag = int(np.hypot(w, h) / period) + 2
    cx, cy = w / 2, h / 2
    for i in range(-diag, diag):
        for j in range(-diag, diag):
            u, v = i * period, j * period
            x = cx + u * ca - v * sa
            y = cy + u * sa + v * ca
            if x < -period or y < -period or x > w + period or y > h + period:
                continue
            xi, yi = int(np.clip(x, 0, w - 1)), int(np.clip(y, 0, h - 1))
            t = intensity[yi, xi]
            if t <= 0.02:
                continue
            r = rmax * np.sqrt(min(t, 1.0))
            if r < .45:
                continue
            d.ellipse([(x - r) * sc, (y - r) * sc, (x + r) * sc, (y + r) * sc], fill=color)
    return im.resize((w, h), Image.LANCZOS)


def tile_rojo(size=512, seed=3):
    a = np.zeros((size, size, 3), np.float32) + np.array([150, 26, 17], np.float32)
    f = fbm(size, size, seed)
    a += f[..., None] * np.array([16, 4, 3])
    a += RNG.normal(0, 6, (size, size))[..., None] * np.array([1, .6, .6])
    im = to_img(a).convert('RGBA')
    inten = np.clip(0.35 + 0.35 * fbm(size, size, seed + 9, ((60, 1),)), 0, 1)
    ht = halftone_layer(size, size, 8, inten, (88, 10, 7, 120))
    im.alpha_composite(ht)
    return im.convert('RGB')


def tiled(tile, w, h):
    out = Image.new('RGB', (w, h))
    for y in range(0, h, tile.height):
        for x in range(0, w, tile.width):
            out.paste(tile, (x, y))
    return out


negro = tile_negro(); save(negro, 's_negro.jpg', 88)
crema = tile_crema(); save(crema, 's_crema.jpg', 88)
rojo = tile_rojo(); save(rojo, 's_rojo.jpg', 88)


# ---------------- fondos de sección ----------------
def glow_bg(w, h, cx, cy, sig, strength, ht_period=12, ht_alpha=150, base=None):
    base = base or tiled(negro, w, h)
    a = np.asarray(base).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sig ** 2))
    a = a + g[..., None] * ROJO * strength
    im = to_img(a).convert('RGBA')
    ring = np.clip(g * 1.25, 0, 1) * (1 - np.clip((g - .55) * 2.2, 0, 1))  # trama más visible en el borde del halo
    im.alpha_composite(halftone_layer(h, w, ht_period, ring, (205, 48, 30, ht_alpha), angle=np.pi / 4))
    return im.convert('RGB')


save(glow_bg(1440, 900, 640, 500, 250, .34, 12, 110), 's_hero_bg.jpg')
save(glow_bg(390, 844, 195, 330, 130, .34, 9, 110), 's_m_hero_bg.jpg')
save(glow_bg(1440, 900, 720, -40, 330, .46, 11, 64), 's_load_bg.jpg')
save(glow_bg(390, 844, 195, -30, 230, .46, 8, 64), 's_m_load_bg.jpg')


def fog_bg(w, h, seed=21):
    """Papel arriba → niebla óxido → cuarto negro abajo (el degradé de Cuarto rojo)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    fog = fbm(h, w, seed, ((140, .7), (50, .3)))
    t = yy / h + 0.03 * fog
    t = np.clip((t - .30) / .66, 0, 1)
    t = t * t * (3 - 2 * t)
    pap = np.asarray(tiled(crema, w, h)).astype(np.float32)
    neg = np.asarray(tiled(negro, w, h)).astype(np.float32)
    # cadena de color: papel → óxido → rojo oscuro → negro
    def lerp(a, b, u):
        return a + (b - a) * u[..., None]
    t1 = np.clip(t / .38, 0, 1)
    t2 = np.clip((t - .38) / .32, 0, 1)
    t3 = np.clip((t - .70) / .30, 0, 1)
    col = lerp(pap, pap * 0 + MEDIO + (pap - CREMA) * .6, t1)
    col = np.where((t > .38)[..., None], lerp(MEDIO + (neg - NEGRO) * 1.4, ROJO_OSC * .48 + (neg - NEGRO), t2), col)
    col = np.where((t > .70)[..., None], lerp(ROJO_OSC * .48 + (neg - NEGRO), neg, t3), col)
    # polvo de Beksiński en la franja media
    mid = np.exp(-((t - .5) ** 2) / .03)
    col += (fbm(h, w, seed + 5, ((12, 1),)) * 6 * mid)[..., None]
    return to_img(col)


save(fog_bg(1440, 980), 's_fog_bg.jpg')


def red_room(w, h, seed=31):
    base = tiled(rojo, w, h)
    a = np.asarray(base).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w * .42) / (w * .75)) ** 2 + ((yy - h * .38) / (h * .9)) ** 2)
    vig = np.clip((r - .35) / .7, 0, 1)
    a = a * (1 - .55 * vig[..., None])
    im = to_img(a).convert('RGBA')
    im.alpha_composite(halftone_layer(h, w, 11, np.clip(vig * 1.1, 0, 1), (40, 4, 3, 150), angle=np.pi / 4))
    return im.convert('RGB')


save(red_room(1440, 900), 's_red_bg.jpg')
save(red_room(390, 844), 's_m_red_bg.jpg')


# ---------------- fotos ----------------
def load(name, w):
    im = ImageOps.exif_transpose(Image.open(os.path.join(REPO, name))).convert('RGB')
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def crop_ratio(im, ratio, fy=.5, fx=.5):
    W, H = im.size
    if W / H > ratio:
        nw = round(H * ratio); x = round((W - nw) * fx)
        return im.crop((x, 0, x + nw, H))
    nh = round(W / ratio); y = round((H - nh) * fy)
    return im.crop((0, y, W, y + nh))


def grain(im, amount=10, seed=1):
    a = np.asarray(im).astype(np.float32)
    n = np.random.default_rng(seed).normal(0, amount, a.shape[:2])[..., None]
    return to_img(a + n)


def revelar(im, expo=1.0, gamma=1.05):
    """Revelado rojo: negro → rojo antorcha. `expo` < 1 = todavía latente."""
    g = np.asarray(ImageOps.grayscale(im)).astype(np.float32) / 255
    g = np.clip(g * expo, 0, 1) ** gamma
    d = np.array([12, 2, 2], np.float32); l = np.array([255, 96, 62], np.float32)
    return to_img(d + (l - d) * g[..., None])


def chroma(im, s=3):
    r, g, b = im.split()
    r = ImageChops.offset(r, s, 0); b = ImageChops.offset(b, -s, 0)
    return Image.merge('RGB', (r, g, b))


def crt(im, w, h, k=.09):
    im = crop_ratio(im, w / h).resize((w, h), Image.LANCZOS)
    a = np.asarray(chroma(im, 3)).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / (w - 1) * 2 - 1; ny = yy / (h - 1) * 2 - 1
    r2 = nx * nx + ny * ny
    sx = nx * (1 + k * r2); sy = ny * (1 + k * r2)
    px = ((sx + 1) / 2 * (w - 1)).clip(0, w - 1).astype(int)
    py = ((sy + 1) / 2 * (h - 1)).clip(0, h - 1).astype(int)
    out = a[py, px]
    scan = .78 + .22 * (np.sin(yy * np.pi / 2.4) ** 2)
    out = out * scan[..., None] * np.clip(1.12 - .5 * r2, 0, 1)[..., None] * 1.1 + .02
    img = to_img(out * 255)
    return grain(Image.blend(img, img.filter(ImageFilter.GaussianBlur(5)), .2), 7, 3)


P = {}
def put(k, im, name, q=86):
    P[k] = save(im, name, q)

# Pantalla del TV (se incrusta en el SVG del TV, 2x)
put('tv_screen', crt(load('DR-1.jpg', 1600), 992, 784), 's_tv_screen.jpg', 88)
put('m_tv_screen', crt(load('DR-1.jpg', 1200), 496, 392), 's_m_tv_screen.jpg', 86)

# Retrato revelado: el hombre a la derecha, el muro oscuro a la izquierda para el nombre
def retrato(W, H, scale_h, x_off, fy=.0):
    src = load('perfil.jpg', 2400)
    sh = round(H * scale_h); sw = round(src.width * sh / src.height)
    src = src.resize((sw, sh), Image.LANCZOS)
    rev = revelar(src, 1.0, 1.08)
    canvas = Image.new('RGB', (W, H), (12, 2, 2))
    canvas.paste(rev, (x_off, round(-(sh - H) * fy)))
    a = np.asarray(canvas).astype(np.float32)
    xx = np.arange(W)[None, :].astype(np.float32)
    fade = np.clip((xx - x_off) / 260, 0, 1)
    a = a * (.0 + fade[..., None]) + np.array([12, 2, 2]) * (1 - fade[..., None])
    return grain(to_img(a), 11, 5)

put('retrato', retrato(1440, 900, 1.08, 300, .25), 's_retrato.jpg', 84)
put('m_retrato', crop_ratio(retrato(1500, 844, 1.0, 0, 0), 390 / 844, .5, .52), 's_m_retrato.jpg', 84)

# Selección de fotos (color) y una foto «latente»
sel = [('CFC-20.jpg', .5), ('AH-1.jpg', .5), ('VENT-1.jpg', .5), ('HM-10.jpg', .5), ('IQQ-1.jpg', .5)]
for i, (f, fy) in enumerate(sel):
    put(f'foto{i}', grain(crop_ratio(load(f, 900), 4 / 3, fy), 6, 10 + i), f's_foto{i}.jpg')
put('foto3_lat', grain(revelar(crop_ratio(load('HM-10.jpg', 900), 4 / 3), .55, 1.25), 9, 19), 's_foto3_lat.jpg')

# Cine
put('cine', grain(crop_ratio(load('remake-5.jpg', 2400), 2.39, .56), 8, 40), 's_cine.jpg', 84)
put('cine2', grain(crop_ratio(load('HM-1.jpg', 1100), 2.39, .62), 8, 41), 's_cine2.jpg')
put('m_cine', grain(crop_ratio(load('remake-5.jpg', 1400), 2.39, .56), 8, 42), 's_m_cine.jpg')

# Trayectoria
put('cv_film', grain(crop_ratio(load('remake-5.jpg', 900), 16 / 9, .55), 7, 50), 's_cv_film.jpg')
for i, f in enumerate(['FECH-1.jpg', 'FECH-5.jpg']):
    put(f'cv_arch{i}', grain(crop_ratio(load(f, 600), 4 / 3), 7, 51 + i), f's_cv_arch{i}.jpg')

# Sello del sobre y copia de carga
put('sello', grain(revelar(crop_ratio(load('perfil.jpg', 900), 4 / 5, .3, .6)), 9, 60), 's_sello.jpg')

def print_revelando(w, h):
    """Copia saliendo del corte: arriba revelada, abajo todavía latente."""
    src = crop_ratio(load('DR-1.jpg', 1400), w / h, .5, .30).resize((w, h), Image.LANCZOS)
    full = np.asarray(revelar(src, 1.0)).astype(np.float32)
    lat = np.asarray(revelar(src, .32, 1.6)).astype(np.float32)
    yy = np.arange(h)[:, None].astype(np.float32) / h
    m = np.clip((yy - .15) / .75, 0, 1) ** 1.2
    return grain(to_img(full * (1 - m[..., None]) + lat * m[..., None]), 10, 61)

put('carga', print_revelando(560, 700), 's_carga.jpg')
put('m_carga', print_revelando(280, 350), 's_m_carga.jpg')

# Demostración del revelado (materiales)
demo = crop_ratio(load('DR-4.jpg', 900), 4 / 3)
put('demo0', grain(demo, 6, 70), 's_demo0.jpg')
put('demo1', grain(revelar(demo, .45, 1.5), 9, 71), 's_demo1.jpg')
put('demo2', grain(revelar(demo, 1.0), 9, 72), 's_demo2.jpg')

json.dump(P, open(os.path.join(OUT, 's_index.json'), 'w'), indent=1)
print('ok', len(P))
