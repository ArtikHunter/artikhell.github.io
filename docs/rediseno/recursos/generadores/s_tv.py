"""TV 2D estilizado (tinta, trama, registro corrido) y stickers chilenos originales, en SVG."""
import math, os, json
import numpy as np

S = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(S, 'assets')
INK = '#140807'
RED = '#c42a1c'
RED_TOP = '#dc4632'
RED_SIDE = '#77150e'
RED_DEEP = '#4e0c08'
CREAM = '#efe6d2'
CREAM_D = '#d9ccb1'
LEAF = '#38452a'
rng = np.random.default_rng(11)


def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def pts_path(pts, close=True):
    d = 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts)
    return d + (' Z' if close else '')


def rrect_pts(x0, y0, x1, y1, r, n=10):
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def hull(points):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in points))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def halftone(poly, period, angle, fn, rmax, color, op=1.0):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    R = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + period
    ca, sa = math.cos(angle), math.sin(angle)
    n = int(R / period) + 1
    out = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * period, j * period
            x = cx + u * ca - v * sa; y = cy + u * sa + v * ca
            if not inside(poly, x, y):
                continue
            t = fn(x, y)
            if t <= 0:
                continue
            r = rmax * math.sqrt(min(t, 1))
            if r < .7:
                continue
            out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>')
    return f'<g fill="{color}" opacity="{op}">' + ''.join(out) + '</g>'


def tapered(points, w, color, op):
    """Pincelada que se afina en los extremos (look pintado a mano)."""
    pts = np.array(points, float)
    n = len(pts)
    left, right = [], []
    for i in range(n):
        p0 = pts[max(i - 1, 0)]; p1 = pts[min(i + 1, n - 1)]
        d = p1 - p0; d = d / (np.linalg.norm(d) + 1e-9)
        nrm = np.array([-d[1], d[0]])
        t = i / (n - 1)
        ww = w * math.sin(math.pi * t) ** .8 * (0.85 + 0.3 * rng.random())
        left.append(pts[i] + nrm * ww / 2); right.append(pts[i] - nrm * ww / 2)
    poly = left + right[::-1]
    return f'<path d="{pts_path(poly)}" fill="{color}" opacity="{op}"/>'


def curve(p0, p1, bend, n=14):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) + 1e-9
    cx, cy = mx + nx / L * bend, my + ny / L * bend
    return [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1) for t in np.linspace(0, 1, n)]


# ======================= TELEVISOR =======================
FX, FY, FX1, FY1, FR = 140, 300, 880, 840, 64
BX, BY, BX1, BY1, BR = 371.4, 249.4, 948.6, 670.6, 50
SX, SY, SW, SH, SR = 192, 352, 496, 392, 54
FRONT = rrect_pts(FX, FY, FX1, FY1, FR)
BACK = rrect_pts(BX, BY, BX1, BY1, BR)
HULL = hull(FRONT + BACK)
c45 = FR * (1 - math.cos(math.radians(45)))
b45 = BR * (1 - math.cos(math.radians(45)))
F_TL, F_TR, F_BR = (FX + c45, FY + c45), (FX1 - c45, FY + c45), (FX1 - c45, FY1 - c45)
B_TL, B_TR, B_BR = (BX + b45, BY + b45), (BX1 - b45, BY + b45), (BX1 - b45, BY1 - b45)
TOP = [F_TL, (FX + FR, FY), (FX1 - FR, FY), F_TR, B_TR, (BX1 - BR, BY), (BX + BR, BY), B_TL]
SIDE = [F_TR, (FX1, FY + FR), (FX1, FY1 - FR), F_BR, B_BR, (BX1, BY1 - BR), (BX1, BY + BR), B_TR]
DEPTH = np.array([150, -110], float); DEPTH /= np.linalg.norm(DEPTH)


def doily(cx, cy, rho, s=.42, scallops=18):
    pts = []
    for th in np.linspace(0, 2 * math.pi, 361):
        r = rho * (1 + .05 * (1 + math.cos(scallops * th)) / 2)
        x = cx + r * math.cos(th) + r * s * DEPTH[0] * math.sin(th)
        y = cy + r * s * DEPTH[1] * math.sin(th)
        pts.append((x, y))
    return pts


def plane_pt(cx, cy, r, th, s=.42):
    return (cx + r * math.cos(th) + r * s * DEPTH[0] * math.sin(th), cy + r * s * DEPTH[1] * math.sin(th))


def side_matrix(ox, oy, sc):
    """Proyecta un sticker sobre la cara lateral (eje x → profundidad)."""
    return f'matrix({f(DEPTH[0]*sc)} {f(DEPTH[1]*sc)} 0 {f(sc)} {f(ox)} {f(oy)})'


def tv_svg(screen_href, side_sticker=''):
    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1100 960" width="1100" height="960">')
    o.append('<defs>')
    o.append(f'<clipPath id="tvHull"><path d="{pts_path(HULL)}"/></clipPath>')
    o.append(f'<clipPath id="tvFront"><path d="{pts_path(FRONT)}"/></clipPath>')
    o.append(f'<clipPath id="tvSide"><path d="{pts_path(SIDE)}"/></clipPath>')
    o.append(f'<clipPath id="tvScr"><path d="{pts_path(rrect_pts(SX, SY, SX + SW, SY + SH, SR))}"/></clipPath>')
    o.append('<radialGradient id="tvVig" cx="50%" cy="48%" r="62%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".7"/></radialGradient>')
    o.append('<linearGradient id="tvGlass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff6e8" stop-opacity=".34"/><stop offset=".45" stop-color="#fff6e8" stop-opacity="0"/></linearGradient>')
    o.append('</defs>')

    # registro corrido (impresión desfasada) detrás de todo
    o.append(f'<g transform="translate(7 6)" fill="none" stroke="#ff5c3c" stroke-width="5" opacity=".6" stroke-linejoin="round"><path d="{pts_path(HULL)}"/></g>')
    o.append(f'<g transform="translate(-4 -3)" fill="none" stroke="#efe6d2" stroke-width="2" opacity=".18" stroke-linejoin="round"><path d="{pts_path(HULL)}"/></g>')

    # cuerpo: casco, tapa y costado
    o.append(f'<path d="{pts_path(HULL)}" fill="{RED_DEEP}"/>')
    o.append('<g clip-path="url(#tvHull)">')
    o.append(f'<path d="{pts_path(TOP)}" fill="{RED_TOP}"/>')
    o.append(f'<path d="{pts_path(SIDE)}" fill="{RED_SIDE}"/>')
    o.append('</g>')
    # trama y achurado en el costado
    def side_fn(x, y):
        t = ((np.array([x, y]) - np.array(F_TR)) @ DEPTH) / 180
        return .18 + .62 * t + .25 * (y - 300) / 540
    o.append(f'<g clip-path="url(#tvSide)">{halftone(SIDE, 11, math.pi / 4, side_fn, 5.4, INK, .6)}')
    hatch = []
    for k in range(-30, 40):
        x0 = 860 + k * 9
        hatch.append(f'<line x1="{f(x0)}" y1="240" x2="{f(x0 - 120)}" y2="860"/>')
    o.append(f'<g stroke="{INK}" stroke-width="1.5" opacity=".32" clip-path="url(#tvSide)"><g clip-path="url(#tvHull)">' + ''.join(hatch) + '</g></g>')
    o.append(side_sticker)
    o.append('</g>')
    # pinceladas de luz en la tapa
    o.append(tapered(curve((215, 292), (800, 292), -6), 9, CREAM, .55))
    o.append(tapered(curve((420, 262), (880, 258), 4), 7, CREAM, .25))
    o.append(tapered(curve((900, 300), (935, 290), 0, 6), 5, CREAM, .3))
    # aristas
    o.append(f'<path d="M{f(F_TR[0])} {f(F_TR[1])} L{f(B_TR[0])} {f(B_TR[1])}" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>')
    o.append(f'<path d="{pts_path(HULL)}" fill="none" stroke="{INK}" stroke-width="7.5" stroke-linejoin="round"/>')

    # frente
    o.append(f'<path d="{pts_path(FRONT)}" fill="{RED}"/>')
    o.append('<g clip-path="url(#tvFront)">')
    for i in range(7):  # variación pintada
        y0 = 360 + i * 70 + rng.uniform(-14, 14)
        col = '#d43a28' if i % 2 else '#b0241a'
        o.append(tapered(curve((110, y0 + 40), (900, y0 - 50), rng.uniform(-30, 30), 18), rng.uniform(34, 60), col, .38))
    def front_fn(x, y):
        return ((y - 748) / 92) ** 1.4 * 1.05 if y > 748 else 0
    o.append(halftone([(FX, 748), (FX1, 748), (FX1, FY1), (FX, FY1)], 10, math.pi / 4, front_fn, 5, INK, .55))
    def front_right(x, y):
        return ((x - 820) / 60) * .7 if x > 820 else 0
    o.append(halftone([(820, FY), (FX1, FY), (FX1, FY1), (820, FY1)], 10, math.pi / 4, front_right, 4.6, INK, .45))
    o.append('</g>')
    o.append(tapered(curve((152, 390), (152, 770), -6), 9, CREAM, .6))
    o.append(tapered(curve((205, 309), (700, 309), 3), 6, CREAM, .5))
    o.append(f'<path d="{pts_path(FRONT)}" fill="none" stroke="{INK}" stroke-width="7.5" stroke-linejoin="round"/>')

    # marco y pantalla
    bez = rrect_pts(170, 330, 710, 766, 70)
    o.append(f'<path d="{pts_path(bez)}" fill="#1c0b09" stroke="{INK}" stroke-width="6"/>')
    o.append(tapered(curve((196, 380), (196, 700), -8), 5, CREAM, .22))
    o.append(tapered(curve((240, 346), (640, 346), 4), 4, CREAM, .2))
    o.append(f'<g clip-path="url(#tvScr)"><image href="{screen_href}" x="{SX}" y="{SY}" width="{SW}" height="{SH}" preserveAspectRatio="xMidYMid slice"/>')
    o.append(f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="url(#tvVig)"/>')
    o.append(f'<path d="M{SX} {SY} L{SX + 300} {SY} C{SX + 210} {SY + 70} {SX + 120} {SY + 170} {SX + 70} {SY + SH} L{SX} {SY + SH} Z" fill="url(#tvGlass)"/>')
    o.append(f'<path d="M{SX + 28} {SY + 70} C{SX + 34} {SY + 40} {SX + 52} {SY + 24} {SX + 92} {SY + 20}" stroke="#fff6e8" stroke-width="6" stroke-linecap="round" fill="none" opacity=".55"/>')
    o.append('</g>')
    o.append(f'<path d="{pts_path(rrect_pts(SX, SY, SX + SW, SY + SH, SR))}" fill="none" stroke="{INK}" stroke-width="5"/>')

    # panel: perillas, parlante, placa
    def knob(cx, cy, r, ang, ticks=12):
        g = []
        for k in range(ticks):
            a = math.radians(-120 + 240 * k / (ticks - 1))
            g.append(f'<line x1="{f(cx + (r + 8) * math.sin(a))}" y1="{f(cy - (r + 8) * math.cos(a))}" x2="{f(cx + (r + 16) * math.sin(a))}" y2="{f(cy - (r + 16) * math.cos(a))}" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>')
        g.append(f'<circle cx="{cx + 4}" cy="{cy + 5}" r="{r}" fill="{INK}" opacity=".55"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{CREAM}" stroke="{INK}" stroke-width="5"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{r * .72:.1f}" fill="{CREAM_D}" stroke="{INK}" stroke-width="3"/>')
        for k in range(18):
            a = 2 * math.pi * k / 18
            g.append(f'<line x1="{f(cx + r * .5 * math.cos(a))}" y1="{f(cy + r * .5 * math.sin(a))}" x2="{f(cx + r * .7 * math.cos(a))}" y2="{f(cy + r * .7 * math.sin(a))}" stroke="{INK}" stroke-width="1.6" opacity=".6"/>')
        a = math.radians(ang)
        g.append(f'<line x1="{cx}" y1="{cy}" x2="{f(cx + r * .9 * math.sin(a))}" y2="{f(cy - r * .9 * math.cos(a))}" stroke="{INK}" stroke-width="6.5" stroke-linecap="round"/>')
        g.append(f'<path d="M{f(cx - r * .78)} {f(cy - r * .2)} A{r * .8:.1f} {r * .8:.1f} 0 0 1 {f(cx - r * .1)} {f(cy - r * .78)}" stroke="#fffaf0" stroke-width="4" fill="none" opacity=".8" stroke-linecap="round"/>')
        return ''.join(g)
    o.append(knob(796, 432, 46, -38))
    o.append(knob(796, 566, 33, 52, 9))
    for k in range(6):
        y = 650 + k * 21
        o.append(f'<line x1="754" y1="{y}" x2="838" y2="{y}" stroke="{INK}" stroke-width="8.5" stroke-linecap="round"/>')
        o.append(f'<line x1="758" y1="{y + 6}" x2="834" y2="{y + 6}" stroke="#ff7a5c" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>')
    o.append(f'<rect x="756" y="782" width="82" height="28" rx="4" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>')
    o.append(f'<text x="797" y="802" text-anchor="middle" font-family="IBM Plex Mono" font-weight="500" font-size="15" fill="{INK}" letter-spacing="2">B·B</text>')

    # patas
    for x in (230, 730):
        o.append(f'<path d="M{x} 838 L{x + 80} 838 L{x + 72} 876 L{x + 8} 876 Z" fill="{RED_DEEP}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')

    # carpeta tejida sobre la tapa
    dcx, dcy, drho = 560, 286, 170
    o.append(f'<path d="{pts_path([(x + 4, y + 6) for x, y in doily(dcx, dcy, drho)])}" fill="{INK}" opacity=".35"/>')
    o.append(f'<path d="{pts_path(doily(dcx, dcy, drho))}" fill="{CREAM}" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    o.append(f'<path d="{pts_path(doily(dcx, dcy, drho - 14, scallops=36))}" fill="none" stroke="{INK}" stroke-width="1.3" opacity=".5"/>')
    spokes = []
    for i in range(32):
        th = 2 * math.pi * i / 32
        x0, y0 = plane_pt(dcx, dcy, 34, th); x1, y1 = plane_pt(dcx, dcy, drho - 16, th)
        spokes.append(f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}"/>')
    o.append(f'<g stroke="{INK}" stroke-width="1.1" opacity=".38">' + ''.join(spokes) + '</g>')
    for rr in (128, 96, 62):
        o.append(f'<path d="{pts_path(doily(dcx, dcy, rr, scallops=int(rr / 4)))}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 2.4" opacity=".6"/>')
    for rr, k, rx in ((112, 32, 3.6), (79, 24, 3.2)):
        for i in range(k):
            th = 2 * math.pi * (i + .5) / k
            x, y = plane_pt(dcx, dcy, rr, th)
            o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{rx}" ry="{rx * .5:.1f}" fill="{RED_SIDE}"/>')
    for i in range(6):
        th = 2 * math.pi * i / 6
        x, y = plane_pt(dcx, dcy, 26, th)
        o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="9" ry="4" fill="{CREAM_D}" stroke="{INK}" stroke-width="1.3"/>')

    # antena con papel aluminio
    bx, by = 596, 268
    for (x1, y1) in ((432, 44), (812, 62)):
        o.append(f'<line x1="{bx}" y1="{by - 8}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>')
        o.append(f'<line x1="{bx}" y1="{by - 8}" x2="{x1}" y2="{y1}" stroke="#a9a397" stroke-width="5" stroke-linecap="round"/>')
        o.append(f'<line x1="{bx - 1}" y1="{by - 10}" x2="{x1 - 1}" y2="{y1}" stroke="#f4efe4" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>')
        o.append(f'<circle cx="{x1}" cy="{y1}" r="10" fill="#a9a397" stroke="{INK}" stroke-width="3.5"/>')
    o.append(f'<ellipse cx="{bx}" cy="{by}" rx="34" ry="12" fill="{INK}"/>')
    o.append(f'<path d="M{bx - 30} {by} A30 24 0 0 1 {bx + 30} {by} Z" fill="#2a1512" stroke="{INK}" stroke-width="4"/>')
    o.append(f'<path d="M{bx - 18} {by - 10} A20 14 0 0 1 {bx + 4} {by - 20}" stroke="{CREAM}" stroke-width="3" fill="none" opacity=".6" stroke-linecap="round"/>')
    fx, fy = 432, 48
    foil = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        r = (38 if i % 2 else 27) + rng.uniform(-5, 5)
        foil.append((fx + r * math.cos(a) * 1.05, fy + r * math.sin(a) * .9))
    o.append(f'<path d="{pts_path(foil)}" fill="#c9c6bf" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(6, 24)
        x, y = fx + r * math.cos(a), fy + r * math.sin(a)
        o.append(f'<path d="M{f(x)} {f(y)} l{f(rng.uniform(-9, 9))} {f(rng.uniform(-8, 8))} l{f(rng.uniform(-6, 6))} {f(rng.uniform(4, 9))}" stroke="#7d7a73" stroke-width="1.5" fill="none"/>')
    o.append(f'<path d="M{fx - 16} {fy - 10} l10 -6 l6 8 z" fill="#ffffff" opacity=".85"/>')
    o.append(f'<path d="M{fx + 6} {fy + 6} l9 -3 l2 7 z" fill="#ffffff" opacity=".6"/>')
    o.append('</svg>')
    return ''.join(o)


# ======================= STICKERS =======================
def die(body, w, h, border=8):
    """Sticker troquelado: borde crema + sombra corta + arte."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<g transform="translate(3 4)" opacity=".38">{body("#000", border + 1)}</g>'
            f'{body("#f7f0e2", border)}{body(None, 0)}</svg>')


def st_perro():
    w, h = 280, 184
    def body(col, b):
        if col:
            return f'<rect x="{12 - b}" y="{12 - b}" width="{256 + 2 * b}" height="{160 + 2 * b}" rx="{10 + b}" fill="{col}"/>'
        dog = ('M8 92 C6 70 10 50 22 40 L18 8 L38 30 C48 26 58 28 66 34 L92 40 L94 50 L70 54 L90 66 L88 72 '
               'C76 76 64 78 54 80 C48 86 44 90 42 96 Z')
        return (f'<rect x="12" y="12" width="256" height="160" rx="8" fill="{CREAM}" stroke="{RED}" stroke-width="8"/>'
                f'<rect x="16" y="16" width="248" height="40" fill="{RED}"/>'
                f'<text x="140" y="47" text-anchor="middle" font-family="Encode Sans Condensed" font-weight="900" font-size="29" letter-spacing="2" fill="{CREAM}">¡CUIDADO!</text>'
                f'<g transform="translate(26 68) scale(.9)"><path d="{dog}" fill="{INK}"/>'
                f'<circle cx="52" cy="41" r="3.6" fill="{CREAM}"/>'
                f'<path d="M73 53 L77 60 L80 52 Z M81 64 L84 58 L87 65 Z" fill="{CREAM}"/>'
                f'<path d="M14 82 L44 86 L42 95 L12 91 Z" fill="{RED}"/></g>'
                f'<text x="122" y="108" font-family="Encode Sans Condensed" font-weight="900" font-size="44" fill="{INK}">PERRO</text>'
                f'<text x="122" y="152" font-family="Encode Sans Condensed" font-weight="900" font-size="44" fill="{INK}">BRAVO</text>')
    return die(body, w, h), w, h


def st_copihue():
    w, h = 176, 230
    bell = ('M92 74 C70 78 56 108 52 142 C50 162 48 180 40 200 L64 190 L86 208 L108 190 L134 198 '
            'C126 180 128 160 126 142 C122 108 112 80 92 74 Z')
    leaf1 = 'M98 26 C120 6 150 8 162 18 C142 34 118 36 98 26 Z'
    leaf2 = 'M96 30 C80 10 54 8 40 16 C58 32 80 36 96 30 Z'
    stem = 'M98 24 C116 40 108 60 92 76'
    def body(col, b):
        if col:
            sw = 2 * b
            return (f'<g fill="{col}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round">'
                    f'<path d="{bell}"/><path d="{leaf1}"/><path d="{leaf2}"/><path d="{stem}" fill="none" stroke-width="{sw + 6}"/></g>')
        return (f'<path d="{stem}" fill="none" stroke="{LEAF}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="{leaf1}" fill="{LEAF}" stroke="{INK}" stroke-width="3"/><path d="M100 26 C122 20 142 16 158 18" stroke="#6b7a52" stroke-width="2" fill="none"/>'
                f'<path d="{leaf2}" fill="{LEAF}" stroke="{INK}" stroke-width="3"/><path d="M94 30 C76 22 58 16 44 16" stroke="#6b7a52" stroke-width="2" fill="none"/>'
                f'<path d="{bell}" fill="{RED}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="M66 112 C60 140 58 168 54 190" stroke="#ff7a5c" stroke-width="7" fill="none" opacity=".7" stroke-linecap="round"/>'
                f'<path d="M92 78 C82 116 80 156 86 204 M92 78 C104 116 110 156 108 190" stroke="{INK}" stroke-width="2.6" fill="none" opacity=".75"/>'
                + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.6" ry="1.6" fill="#f6d2c2" opacity=".85"/>' for x, y in ((70, 130), (76, 150), (66, 160), (74, 172), (100, 120), (110, 146), (104, 168), (116, 170)))
                + f'<path d="M84 78 L92 64 L100 78 Z" fill="{LEAF}" stroke="{INK}" stroke-width="2.5"/>')
    return die(body, w, h), w, h


def st_diablo():
    w, h = 220, 224
    face = 'M60 72 C62 50 158 50 160 72 C178 92 182 132 168 162 C156 192 132 208 110 210 C88 208 64 192 52 162 C38 132 42 92 60 72 Z'
    hl = 'M70 80 C46 62 30 32 42 8 C52 32 68 48 94 60 Z'
    hr = 'M150 80 C174 62 190 32 178 8 C168 32 152 48 126 60 Z'
    def body(col, b):
        if col:
            return (f'<g fill="{col}" stroke="{col}" stroke-width="{2 * b}" stroke-linejoin="round">'
                    f'<path d="{face}"/><path d="{hl}"/><path d="{hr}"/></g>')
        teeth = ''.join(f'<path d="M{78 + i * 11} 156 L{83.5 + i * 11} 166 L{89 + i * 11} 156 Z" fill="{CREAM}"/>' for i in range(6))
        return (f'<path d="{hl}" fill="{CREAM}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="{hr}" fill="{CREAM}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<path d="M52 40 C60 46 70 52 80 56 M168 40 C160 46 150 52 140 56" stroke="{INK}" stroke-width="2.4" fill="none" opacity=".6"/>'
                f'<path d="{face}" fill="{RED}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
                f'<path d="M150 84 C170 110 170 160 140 196 C160 160 160 120 150 84 Z" fill="{INK}" opacity=".3"/>'
                f'<path d="M64 92 L106 106 L102 116 L60 103 Z M156 92 L114 106 L118 116 L160 103 Z" fill="{INK}"/>'
                f'<circle cx="84" cy="126" r="17" fill="{CREAM}" stroke="{INK}" stroke-width="4"/><circle cx="88" cy="128" r="7" fill="{INK}"/>'
                f'<circle cx="136" cy="126" r="17" fill="{CREAM}" stroke="{INK}" stroke-width="4"/><circle cx="132" cy="128" r="7" fill="{INK}"/>'
                f'<path d="M104 136 L110 148 L116 136" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linejoin="round"/>'
                f'<path d="M70 152 C90 160 130 160 150 152 C142 190 78 190 70 152 Z" fill="{INK}"/>{teeth}'
                f'<path d="M62 84 C70 74 82 70 92 72" stroke="#ff7a5c" stroke-width="5" fill="none" opacity=".75" stroke-linecap="round"/>')
    return die(body, w, h), w, h


def st_fia():
    w, h = 232, 168
    def body(col, b):
        if col:
            return f'<rect x="{14 - b}" y="{18 - b}" width="{204 + 2 * b}" height="{136 + 2 * b}" rx="{4 + b}" fill="{col}"/>'
        return (f'<rect x="14" y="18" width="204" height="136" rx="3" fill="{CREAM}" stroke="{INK}" stroke-width="3.5"/>'
                f'<rect x="84" y="6" width="66" height="24" fill="#f3ead6" opacity=".85" stroke="#cbbd9f" stroke-width="1" transform="rotate(-4 117 18)"/>'
                f'<text x="116" y="66" text-anchor="middle" font-family="Encode Sans Condensed" font-weight="900" font-size="36" fill="{INK}">HOY NO</text>'
                f'<text x="116" y="102" text-anchor="middle" font-family="Encode Sans Condensed" font-weight="900" font-size="36" fill="{RED}">SE FÍA</text>'
                f'<text x="116" y="136" text-anchor="middle" font-family="Bodoni Moda" font-style="italic" font-weight="700" font-size="25" fill="{INK}">mañana sí</text>'
                f'<path d="M64 144 C90 150 140 140 168 146" stroke="{INK}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    return die(body, w, h), w, h


def star(cx, cy, R, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts_path(pts)


def st_estrella():
    w, h = 156, 156
    def body(col, b):
        if col:
            return f'<circle cx="78" cy="78" r="{64 + b}" fill="{col}"/>'
        return (f'<circle cx="78" cy="78" r="64" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
                f'<circle cx="78" cy="78" r="52" fill="none" stroke="{CREAM}" stroke-width="2" stroke-dasharray="3 4" opacity=".8"/>'
                f'<path d="{star(78, 70, 38, 15)}" fill="{CREAM}" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>'
                f'<text x="78" y="124" text-anchor="middle" font-family="Encode Sans Condensed" font-weight="800" font-size="15" letter-spacing="3" fill="{CREAM}">CHILE</text>')
    return die(body, w, h), w, h


def st_altiro():
    w, h = 214, 140
    bub = 'M24 18 L190 18 C198 18 202 22 202 30 L202 88 C202 96 198 100 190 100 L92 100 L56 128 L64 100 L24 100 C16 100 12 96 12 88 L12 30 C12 22 16 18 24 18 Z'
    def body(col, b):
        if col:
            return f'<path d="{bub}" fill="{col}" stroke="{col}" stroke-width="{2 * b}" stroke-linejoin="round"/>'
        return (f'<path d="{bub}" fill="{CREAM}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<text x="107" y="76" text-anchor="middle" font-family="Encode Sans Condensed" font-weight="900" font-size="42" fill="{RED}" stroke="{INK}" stroke-width="1.2">¡AL TIRO!</text>')
    return die(body, w, h), w, h


STICKERS = {'perro': st_perro(), 'copihue': st_copihue(), 'diablo': st_diablo(), 'fia': st_fia(), 'estrella': st_estrella(), 'altiro': st_altiro()}
meta = {}
for k, (svg, w, h) in STICKERS.items():
    open(os.path.join(OUT, f's_st_{k}.svg'), 'w').write(svg)
    meta[k] = [w, h]

# sticker «Hoy no se fía» proyectado en el costado (va horneado en el raster)
fia_svg, fw, fh = STICKERS['fia']
inner = fia_svg.split('>', 1)[1].rsplit('</svg>', 1)[0]
side = f'<g transform="{side_matrix(898, 520, .52)}">{inner}</g>'
open(os.path.join(OUT, 's_tv_full.svg'), 'w').write(tv_svg('s_tv_screen.jpg', ''))
open(os.path.join(OUT, 's_tv_vec.svg'), 'w').write(tv_svg('assets/s_tv_screen.jpg', ''))
json.dump(meta, open(os.path.join(OUT, 's_stickers.json'), 'w'))
print('ok', {k: len(v[0]) for k, v in STICKERS.items()}, len(open(os.path.join(OUT, 's_tv_full.svg')).read()))
