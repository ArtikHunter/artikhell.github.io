"""Textura pintada sobre el TV rasterizado y rastros de cursor (PNG transparentes)."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(S, 'assets')
rng = np.random.default_rng(5)


def texture_pass(src, dst):
    im = Image.open(src).convert('RGBA')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    grain = rng.normal(0, 1, (H, W))
    streak = np.asarray(Image.fromarray(((rng.normal(0, 1, (H // 14 + 1, W // 2 + 1)) * 40) + 128).clip(0, 255).astype(np.uint8))
                        .resize((W, H), Image.BICUBIC)).astype(np.float32) / 128 - 1
    blot = np.asarray(Image.fromarray(((rng.normal(0, 1, (H // 90 + 2, W // 90 + 2)) * 40) + 128).clip(0, 255).astype(np.uint8))
                      .resize((W, H), Image.BICUBIC)).astype(np.float32) / 128 - 1
    m = 1 + 0.05 * grain + 0.07 * streak + 0.06 * blot
    a[..., :3] = np.clip(a[..., :3] * m[..., None], 0, 255)
    Image.fromarray(a.astype(np.uint8)).save(dst, optimize=True)


texture_pass(os.path.join(S, 'prev', 'tv_raw2x.png'), os.path.join(A, 's_tv.png'))


# ---------------- rastros de cursor ----------------
W, H, SC = 420, 300, 2


def bez(p0, p1, p2, p3, n=220):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


PATH = bez(np.array([30, 250.]), np.array([120, 120.]), np.array([210, 300.]), np.array([318, 132.]))


def halftone_mask(inten, period, color, rmax=None):
    h, w = inten.shape
    rmax = rmax or period * .55
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(period // 2, h, period):
        off = (period // 2) if (y // period) % 2 else 0
        for x in range(off, w, period):
            t = inten[y, x]
            if t < .04:
                continue
            r = rmax * math.sqrt(min(t, 1))
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    return im


def trail_luz():
    w, h = W * SC, H * SC
    core = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(core)
    n = len(PATH)
    for i, (x, y) in enumerate(PATH):
        t = i / (n - 1)
        r = (1.5 + 7 * t ** 1.6) * SC
        v = int(255 * t ** 1.3)
        d.ellipse([x * SC - r, y * SC - r, x * SC + r, y * SC + r], fill=v)
    glow = np.asarray(core.filter(ImageFilter.GaussianBlur(9 * SC))).astype(np.float32) / 255
    inner = np.asarray(core.filter(ImageFilter.GaussianBlur(3 * SC))).astype(np.float32) / 255
    out = np.zeros((h, w, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = 255, 92, 60
    out[..., 3] = np.clip(glow * 1.6 * 255 * .7 + inner * 255 * .55, 0, 255)
    im = Image.fromarray(out.astype(np.uint8))
    im.alpha_composite(halftone_mask(np.clip(glow * 1.6, 0, 1), 7 * SC, (255, 120, 90, 120)))
    return im.resize((W * 2, H * 2), Image.LANCZOS)


def trail_fosforo():
    w, h = W * SC, H * SC
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(PATH)
    for i in range(n - 1):
        t = i / (n - 1)
        if (i // 3) % 5 == 4:
            continue  # cortes de barrido
        a = int(255 * t ** 1.2)
        (x0, y0), (x1, y1) = PATH[i], PATH[i + 1]
        d.line([(x0 * SC, y0 * SC), (x1 * SC, y1 * SC)], fill=(255, 140, 110, a), width=int((1.5 + 2.6 * t) * SC))
    glow = im.filter(ImageFilter.GaussianBlur(5 * SC))
    base = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    base.alpha_composite(glow); base.alpha_composite(glow); base.alpha_composite(im)
    # líneas de barrido sobre el rastro
    a = np.asarray(base).astype(np.float32)
    yy = np.arange(h)[:, None]
    a[..., 3] *= (0.72 + 0.28 * (np.sin(yy * np.pi / (2.2 * SC)) ** 2))
    return Image.fromarray(a.astype(np.uint8)).resize((W * 2, H * 2), Image.LANCZOS)


def trail_tinta():
    w, h = W * SC, H * SC
    n = len(PATH)
    left, right = [], []
    for i in range(n):
        p0 = PATH[max(i - 1, 0)]; p1 = PATH[min(i + 1, n - 1)]
        dv = p1 - p0; dv /= (np.linalg.norm(dv) + 1e-9)
        nrm = np.array([-dv[1], dv[0]])
        t = i / (n - 1)
        ww = (3 + 16 * math.sin(math.pi * min(t * 1.15, 1)) ** .7) * (1 + .25 * rng.normal())
        left.append((PATH[i] + nrm * ww / 2) * SC); right.append((PATH[i] - nrm * ww / 2) * SC)
    poly = [tuple(p) for p in left + right[::-1]]
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    dm = ImageDraw.Draw(mask)
    hx, hy = PATH[-1]
    for _ in range(26):  # salpicaduras
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(14, 46)
        rr = rng.uniform(1, 4.5) * SC
        x, y = (hx + r * math.cos(a)) * SC, (hy + r * math.sin(a)) * SC
        dm.ellipse([x - rr, y - rr, x + rr, y + rr], fill=255)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2 * SC))).astype(np.float32) / 255
    dry = np.zeros((h, w), np.float32)
    xx = np.arange(w)[None, :] / w
    dry = np.clip(.25 + .9 * xx, 0, 1)  # la cola se seca (más transparente)
    out = np.zeros((h, w, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = 239, 230, 210
    out[..., 3] = m * dry * 235
    im = Image.fromarray(out.astype(np.uint8))
    ht = halftone_mask(np.clip(m * (1 - dry) * 1.4, 0, 1), 7 * SC, (196, 42, 28, 230))
    im.alpha_composite(ht)
    return im.resize((W * 2, H * 2), Image.LANCZOS)


trail_luz().save(os.path.join(A, 's_trail_luz.png'), optimize=True)
trail_fosforo().save(os.path.join(A, 's_trail_fosforo.png'), optimize=True)
trail_tinta().save(os.path.join(A, 's_trail_tinta.png'), optimize=True)
print('ok')
