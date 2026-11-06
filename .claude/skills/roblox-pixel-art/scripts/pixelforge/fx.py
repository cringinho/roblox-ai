"""Geradores procedurais de VFX em pixel art.

Todos seguem as mesmas regras (references/02-animacao-vfx.md):
1. Silhueta primeiro: forma forte e legivel em 1 quadro parado.
2. Cor por 'calor'/tempo: nucleo claro -> bordas escuras; ao longo da vida a ramp desce.
3. Quadro de impacto (flash) curto e segurado; dissipacao mais lenta que a explosao.
4. Sem pixels orfaos (exceto faiscas intencionais de 1px).
5. Loops fecham matematicamente (ruido periodico / fases inteiras).
6. Sem contorno escuro em VFX de luz (luz nao tem contorno); fumaca/sangue podem ter.

Cada funcao devolve um Animation pronto para sheet.export_*().
"""
from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .anim import Animation, ticks
from .canvas import Canvas
from .color import RGB
from .noise import PeriodicNoise3, fbm_loop, value_noise2
from .palette import Palette
from .raster import (dilate, edge_inner, f_arc_band, f_star, grid, polygon_mask,
                     remove_specks, shape_mask)
from .shade import clean_index_map, dither_threshold

Vec = Tuple[float, float]


# ---------------------------------------------------------------- helpers
def circle_pts(cx: int, cy: int, r: int) -> List[Tuple[int, int]]:
    """Circulo de 1px pelo algoritmo do ponto medio (anel limpo, sem pixels dobrados)."""
    pts = set()
    x, y, err = r, 0, 1 - r
    while x >= y:
        for a, b in ((x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)):
            pts.add((cx + a, cy + b))
        y += 1
        if err < 0:
            err += 2 * y + 1
        else:
            x -= 1
            err += 2 * (y - x) + 1
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def paint_bands(c: Canvas, heat: np.ndarray, thresholds: Sequence[float], colors: Sequence[RGB],
                clean: bool = True, min_neighbors: int = 2) -> np.ndarray:
    """heat >= thresholds[i] -> colors[i] (thresholds crescentes). Retorna a mascara total."""
    idx = np.full(heat.shape, -1, dtype=np.int32)
    for i, t in enumerate(thresholds):
        idx[heat >= t] = i
    if clean:
        alive = remove_specks(idx >= 0, min_neighbors)
        idx[~alive] = -1
        idx = clean_index_map(idx)
    for i, col in enumerate(colors):
        m = idx == i
        if m.any():
            c.fill_mask(m, col)
    return idx >= 0


def dissolve(mask: np.ndarray, amount: float, seed: int = 0, cells: int = 6) -> np.ndarray:
    """Dissolucao por ruido: amount 0 = intacto, 1 = sumiu (buracos crescem de forma organica)."""
    h, w = mask.shape
    n = value_noise2(w, h, cells, seed) * 0.75 + value_noise2(w, h, cells * 2, seed + 9) * 0.25
    return mask & (n > amount)


def sphere_lit(dx: np.ndarray, dy: np.ndarray, rr: float,
               light: Tuple[float, float, float] = (-0.55, -0.65, 0.52)) -> np.ndarray:
    """Iluminacao de esfera (-1..1): normal = (dx, dy, sqrt(1-dx2-dy2)) / r.
    Diferente de um gradiente linear, gera terminador curvo -> volume sem listras."""
    nx, ny = dx / max(rr, 1e-3), dy / max(rr, 1e-3)
    nz = np.sqrt(np.clip(1.0 - nx * nx - ny * ny, 0.0, 1.0))
    l = math.sqrt(sum(c * c for c in light))
    return (nx * light[0] + ny * light[1] + nz * light[2]) / l


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _anim(name: str, frames: List[Canvas], ms: List[int], loop: bool, **tags) -> Animation:
    return Animation(name, frames, ms, loop=loop, tags={k: str(v) for k, v in tags.items()})


# ================================================================= 1. FOGO (loop)
def fire_loop(pal: Palette, w: int = 24, h: int = 40, frames: int = 8, seed: int = 3,
              ramp: str = "ember", fps: float = 12.0) -> Animation:
    """Chama de tocha/forja em loop perfeito. Base larga e quente, linguas escuras no topo."""
    R = pal.ramp(ramp).colors
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    cx = (w - 1) / 2.0
    yn = ys / (h - 1)
    out: List[Canvas] = []
    for f in range(frames):
        n = fbm_loop(w, h, f, frames, cells=2, octaves=2, seed=seed, scroll_y=1.0) * 0.8 \
            + fbm_loop(w, h, f, frames, cells=4, octaves=1, seed=seed + 5, scroll_y=2.0) * 0.2
        sway_n = fbm_loop(w, h, f, frames, cells=1, octaves=1, seed=seed + 17, scroll_y=1.0)
        sway = (sway_n - 0.5) * 4.0 * (1 - yn)  # topo balanca mais que a base
        hw = (0.12 + 0.36 * yn ** 0.85) * w
        env = 1.0 - np.abs(xs - cx - sway) / np.maximum(hw, 1e-3)
        heat = env * 1.0 + yn ** 1.4 * 0.55 - 0.45 + (n - 0.5) * 0.95
        heat = np.where(yn > 0.93, heat - (yn - 0.93) * 12.0, heat)  # base arredondada
        c = Canvas(w, h)
        paint_bands(c, heat, [0.05, 0.20, 0.36, 0.52, 0.70, 0.86], [R[0], R[1], R[2], R[3], R[4], R[5]])
        # nucleo branco-quente so na base
        core = remove_specks((heat >= 0.97) & (yn > 0.6), 3)
        c.fill_mask(core & c.alpha_mask(), R[6])
        # brasas (faiscas de 1px, intencionais) em fase inteira -> loop perfeito
        for k in range(3):
            ph = (f / frames + k / 3.0) % 1.0
            ey = int(round(h * 0.55 - ph * h * 0.5))
            ex = int(round(cx + math.sin(2 * math.pi * (ph * 2 + k * 0.3)) * (2 + k)))
            if 0 <= ey < h and 0 <= ex < w and not c.alpha_mask()[ey, ex]:
                c.put(ex, ey, R[4] if ph < 0.5 else R[2])
        out.append(c)
    ms = int(round(1000 / fps))
    return _anim("fire_loop", out, [ms] * frames, True, ramp=ramp, kind="loop")


# ================================================================= 2. EXPLOSAO
def explosion(pal: Palette, size: int = 48, seed: int = 1, fire: str = "ember",
              smoke: str = "void") -> Animation:
    """Explosao: antecipacao -> flash (segurado) -> bola de fogo -> fumaca que sobe e dissolve."""
    F = pal.ramp(fire).colors
    S = pal.ramp(smoke).colors
    rng = np.random.default_rng(seed)
    cx = cy = size / 2.0
    xs, ys = grid(size, size)
    blobs = []
    for i in range(7):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.0, 0.20) * size if i else 0.0
        r = rng.uniform(0.15, 0.23) * size * (1.25 if i == 0 else 1.0)
        blobs.append((math.cos(a) * d, math.sin(a) * d - 0.04 * size, r))
    sparks = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.9, 1.4)) for _ in range(7)]
    out: List[Canvas] = []
    ms: List[int] = []

    # f0 antecipacao (nucleo pequeno)
    c = Canvas(size, size)
    m = (xs - cx) ** 2 + (ys - cy) ** 2 <= 3.2 ** 2
    c.fill_mask(dilate(m, 4) & ~m, F[4])
    c.fill_mask(m, F[6])
    out.append(c); ms.append(ticks(2))

    # f1 flash (quadro de impacto) - disco claro com borda quente
    c = Canvas(size, size)
    m = (xs - cx) ** 2 + (ys - cy) ** 2 <= (0.34 * size) ** 2
    c.fill_mask(m, F[6])
    c.fill_mask(edge_inner(m, 4), F[5])
    out.append(c); ms.append(ticks(3))

    def field(t: float, rise: float) -> Tuple[np.ndarray, np.ndarray]:
        best = np.zeros((size, size))
        shade = np.zeros((size, size))
        for (ox, oy, r) in blobs:
            k = 0.55 + 0.75 * ease_out(t)
            bx, by = cx + ox * (1 + 0.9 * t), cy + oy * (1 + 0.9 * t) - rise
            rr = r * k
            dx, dy = xs - bx, ys - by
            d = np.sqrt(dx * dx + dy * dy) / rr
            v = 1.0 - d
            upd = v > best
            best = np.where(upd, v, best)
            # sombreamento por blob: esfera iluminada do topo-esquerda
            shade = np.where(upd, sphere_lit(dx, dy, rr), shade)
        return best, shade

    # f2..f5 bola de fogo
    for t, dur in ((0.15, 3), (0.35, 3), (0.55, 4), (0.75, 4)):
        c = Canvas(size, size)
        fv, sh = field(t, rise=t * 2.0)
        noise = value_noise2(size, size, 8, seed + int(t * 100))
        heat = fv * (1.25 - t) + (noise - 0.5) * 0.35 + sh * 0.10
        alive = fv > 0
        heat = np.where(alive, heat, -1)
        paint_bands(c, heat, [-0.2, 0.10, 0.25, 0.42, 0.62], [S[2], F[1], F[2], F[3], F[4]][::1] if t > 0.5
                    else [F[1], F[2], F[3], F[4], F[5]])
        hot = (heat > 0.80) & alive
        c.fill_mask(hot & c.alpha_mask(), F[6] if t < 0.4 else F[5])
        # faiscas
        for (a, sp) in sparks:
            d0 = (0.25 + 0.55 * t) * size * sp * 0.6
            d1 = d0 + 3
            x0, y0 = cx + math.cos(a) * d0, cy + math.sin(a) * d0
            x1, y1 = cx + math.cos(a) * d1, cy + math.sin(a) * d1
            c.line(int(x0), int(y0), int(x1), int(y1), F[5] if t < 0.5 else F[3])
        out.append(c); ms.append(ticks(dur))

    # f6..f10 fumaca subindo e dissolvendo (mais lenta que a explosao)
    for i, (t, dur) in enumerate(((0.9, 5), (1.05, 5), (1.2, 6), (1.35, 6), (1.5, 7))):
        c = Canvas(size, size)
        fv, sh = field(min(t, 1.0) + (t - 1.0) * 0.3, rise=2.0 + (t - 0.75) * 10.0)
        alive = fv > 0.02
        alive = dissolve(alive, (t - 0.85) * 1.15, seed=seed + 5, cells=6)
        alive = remove_specks(alive, 2)
        tone = np.where(sh > 0.62, 4, np.where(sh > 0.25, 3, 2))
        tone = tone - int(i >= 3)
        idx = np.where(alive, tone, -1)
        idx = clean_index_map(idx)
        for k in range(len(S)):
            mm = idx == k
            if mm.any():
                c.fill_mask(mm, S[k])
        # brasas restantes no nucleo nos primeiros quadros de fumaca
        if i == 0:
            ember = remove_specks(alive & (fv > 0.74) & (value_noise2(size, size, 9, seed + i) > 0.5), 2)
            c.fill_mask(ember, F[1])
        out.append(c); ms.append(ticks(dur))
    return _anim("explosion", out, ms, False, fire=fire, smoke=smoke, kind="oneshot")


# ================================================================= 3. SLASH [ATQ]
def slash_arc(pal: Palette, size: int = 48, ramp: str = "bone", accent: Optional[str] = "blood",
              seed: int = 2) -> Animation:
    """Corte em arco com smear frame. Gume externo branco, corpo no acento, cauda escurece.
    A espessura afina nas DUAS pontas da janela visivel (crescente), nunca termina reto."""
    R = pal.ramp(ramp).colors
    A = pal.ramp(accent).colors if accent else R
    xs, ys = grid(size, size)
    cx, cy = size * 0.5, size * 0.64
    r_out = size * 0.46
    a0, a1 = 195.0, 345.0
    ang = (np.degrees(np.arctan2(ys - cy, xs - cx)) + 360.0) % 360.0
    s = (ang - a0) / (a1 - a0)
    r = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    wmax = size * 0.18
    noise = value_noise2(size, size, 10, seed)

    def arc(head: float, tail: float, width: float, darken: int, broken: float = 0.0) -> Canvas:
        c = Canvas(size, size)
        span = max(head - tail, 1e-3)
        k = np.clip((s - tail) / span, 0.0, 1.0)          # 0 na cauda .. 1 na ponta
        # perfil assimetrico: cresce devagar desde a cauda, afina rapido na ponta
        prof = np.where(k < 0.7, (k / 0.7) ** 0.8, ((1.0 - k) / 0.3) ** 0.6)
        wprof = wmax * width * prof
        inside = (s >= tail) & (s <= head) & (r <= r_out) & (r >= r_out - wprof)
        if broken > 0:
            inside &= noise > broken
            inside = remove_specks(inside, 2)
        q = (r_out - r) / np.maximum(wprof, 1e-3)  # 0 no gume, 1 no lado de dentro
        idx = np.full((size, size), -1)
        idx[inside & (q < 0.34)] = 3
        idx[inside & (q >= 0.34) & (q < 0.66)] = 2
        idx[inside & (q >= 0.66)] = 1
        idx[inside & (k < 0.22)] -= 1
        idx = np.where(inside, np.clip(idx - darken, 0, 3), -1)
        idx = clean_index_map(idx)
        cols = [A[1], A[3], R[-2], R[-1]]
        for kk, col in enumerate(cols):
            c.fill_mask(idx == kk, col)
        return c

    frames = [
        (arc(0.40, 0.00, 0.35, 0), ticks(2)),            # antecipacao: risco fino
        (arc(1.00, 0.00, 1.00, 0), ticks(3)),            # SMEAR: arco inteiro (quadro de impacto)
        (arc(1.00, 0.20, 0.85, 0), ticks(3)),
        (arc(1.00, 0.45, 0.62, 1), ticks(4)),
        (arc(1.00, 0.68, 0.42, 1, broken=0.42), ticks(4)),
        (arc(1.00, 0.84, 0.28, 2, broken=0.52), ticks(5)),
    ]
    out = [f for f, _ in frames]
    ms = [d for _, d in frames]
    tip = (cx + math.cos(math.radians(a1 - 4)) * (r_out - 2), cy + math.sin(math.radians(a1 - 4)) * (r_out - 2))
    for i, k in ((2, 1), (3, 2), (4, 3)):
        for j in range(3):
            a = math.radians(a1 + 25 + j * 28)
            px = int(round(tip[0] + math.cos(a) * (2 + k * 2)))
            py = int(round(tip[1] + math.sin(a) * (2 + k * 2)))
            out[i].put(px, py, R[-1] if k < 3 else A[3])
    last = Canvas(size, size)
    for j in range(2):
        last.put(int(tip[0]) + 3 + j * 2, int(tip[1]) + 2 + j, A[2])
    out.append(last); ms.append(ticks(5))
    return _anim("slash_arc", out, ms, False, ramp=ramp, accent=accent or ramp, tag="[ATQ]", kind="oneshot")


# ================================================================= 4. IMPACTO
def impact_spark(pal: Palette, size: int = 32, ramp: str = "gold", seed: int = 4) -> Animation:
    """Faisca de acerto: estrela (hit-stop) -> anel -> particulas que se afastam."""
    R = pal.ramp(ramp).colors
    W = pal.ramp("flash").colors[-1]
    cx = cy = size // 2
    out: List[Canvas] = []
    ms: List[int] = []
    # f0 estrela grande (segurar = hit-stop)
    c = Canvas(size, size)
    m = shape_mask(size, size, f_star(4, 0.22, -90), cx + 0.5, cy + 0.5, size * 0.47, size * 0.47)
    c.fill_mask(m, R[-2])
    inner = shape_mask(size, size, f_star(4, 0.22, -90), cx + 0.5, cy + 0.5, size * 0.30, size * 0.30)
    c.fill_mask(inner, W)
    out.append(c); ms.append(ticks(4))
    # f1 estrela 8 pontas menor + anel
    c = Canvas(size, size)
    m = shape_mask(size, size, f_star(8, 0.35, -90), cx + 0.5, cy + 0.5, size * 0.30, size * 0.30)
    c.fill_mask(m, R[-1])
    for (x, y) in circle_pts(cx, cy, int(size * 0.30)):
        c.put(x, y, R[-2])
    out.append(c); ms.append(ticks(2))
    parts = [(math.radians(45 + 90 * i + (15 if i % 2 else -10)), 1.0 + 0.15 * (i % 2)) for i in range(4)]
    for k, (rr, col_i, dur, dashed) in enumerate(((0.38, -3, 3, False), (0.44, -4, 3, True), (0.48, -5, 4, True))):
        c = Canvas(size, size)
        pts = circle_pts(cx, cy, int(size * rr))
        for j, (x, y) in enumerate(pts):
            if not dashed or (j // 2) % 2 == 0 or k == 0:
                if k < 2:
                    c.put(x, y, R[col_i])
        for (a, sp) in parts:
            d = size * (0.30 + 0.09 * (k + 1)) * sp
            px, py = int(round(cx + math.cos(a) * d)), int(round(cy + math.sin(a) * d))
            c.put(px, py, R[-1] if k == 0 else R[-3])
            if k < 2:
                c.put(px - int(round(math.cos(a))), py - int(round(math.sin(a))), R[-3] if k == 0 else R[-4])
        out.append(c); ms.append(ticks(dur))
    c = Canvas(size, size)
    for (a, sp) in parts[:2]:
        d = size * 0.52 * sp
        c.put(int(round(cx + math.cos(a) * d)), int(round(cy + math.sin(a) * d)), R[-4])
    out.append(c); ms.append(ticks(4))
    return _anim("impact_spark", out, ms, False, ramp=ramp, kind="oneshot")


# ================================================================= 5. CIRCULO MAGICO (loop)
RUNES = [
    ["010", "111", "010", "101"],
    ["110", "011", "010", "010"],
    ["101", "010", "101", "010"],
    ["111", "010", "010", "111"],
]


def magic_circle(pal: Palette, size: int = 48, ramp: str = "violet", frames: int = 8,
                 marks: int = 8) -> Animation:
    """Circulo ritual em loop. Geometria interna FIXA (hexagrama pixel-perfect nao gira:
    girar linhas finas gera jaggies). O movimento vem de: runas orbitando, um brilho
    que percorre o anel externo e pulso por ciclo de paleta."""
    R = pal.ramp(ramp).colors
    cx = cy = size // 2
    r1, r2, r3 = size // 2 - 2, size // 2 - 8, size // 2 - 15
    pulse = [3, 4, 5, 5, 4, 3, 3, 3]
    ring1 = circle_pts(cx, cy, r1)
    hexa = []
    for tri in (0, 1):
        pts = []
        for k in range(3):
            a = math.radians(-90 + k * 120 + (60 if tri else 0))
            pts.append((int(round(cx + math.cos(a) * (r3 - 1))), int(round(cy + math.sin(a) * (r3 - 1)))))
        hexa.append(pts)
    out: List[Canvas] = []
    for f in range(frames):
        c = Canvas(size, size)
        hi = R[min(len(R) - 1, pulse[f % len(pulse)])]
        for (x, y) in ring1:
            c.put(x, y, R[3])
        # cometa de luz percorrendo o anel externo (1 volta por loop)
        n = len(ring1)
        head = int(round(n * f / frames))
        for j in range(6):
            x, y = ring1[(head - j) % n]
            c.put(x, y, R[-1] if j < 2 else R[-2] if j < 4 else R[4])
        for (x, y) in circle_pts(cx, cy, r2):
            c.put(x, y, hi)
        for (x, y) in circle_pts(cx, cy, r3):
            c.put(x, y, R[2])
        step = 360.0 / marks
        for i in range(marks):
            a = math.radians(-90 + i * step + step * f / frames)
            rr = (r1 + r2) / 2.0
            gx = int(round(cx + math.cos(a) * rr)) - 1
            gy = int(round(cy + math.sin(a) * rr)) - 2
            g = RUNES[i % len(RUNES)]
            for yy, row in enumerate(g):
                for xx, ch in enumerate(row):
                    if ch == "1":
                        c.put(gx + xx, gy + yy, R[5] if i % 2 == 0 else R[4])
        c.polyline(hexa[0], hi, closed=True)
        c.polyline(hexa[1], R[3], closed=True)
        c.put(cx, cy, R[-1])
        out.append(c)
    return _anim("magic_circle", out, [ticks(5)] * frames, True, ramp=ramp, kind="loop")


# ================================================================= 6. ESCUDO [GRD]
def ward_shield(pal: Palette, size: int = 40, ramp: str = "spirit", seed: int = 6) -> Animation:
    """Guarda: hexagono que surge com overshoot, brilho varre a face, dissolve."""
    R = pal.ramp(ramp).colors
    W = pal.ramp("flash").colors[-1]
    cx = cy = size / 2.0
    xs, ys = grid(size, size)

    def hexagon(scale: float) -> np.ndarray:
        rad = size * 0.44 * scale
        pts = [(cx + math.cos(math.radians(-90 + 60 * k)) * rad,
                cy + math.sin(math.radians(-90 + 60 * k)) * rad * 1.05) for k in range(6)]
        return polygon_mask(size, size, pts)

    out: List[Canvas] = []
    ms: List[int] = []
    c = Canvas(size, size)
    d = shape_mask(size, size, lambda u, v: np.abs(u) + np.abs(v) <= 1, cx, cy, 3.5, 5.5)
    c.fill_mask(d, W)
    out.append(c); ms.append(ticks(2))
    checker = ((np.mgrid[0:size, 0:size][0] + np.mgrid[0:size, 0:size][1]) % 2) == 0
    for k, (scale, sweep, rim_i, fill_i, dur, diss) in enumerate((
            (0.55, None, -1, None, 3, 0.0),
            (1.08, None, -2, 2, 3, 0.0),
            (1.00, 0.15, -2, 2, 4, 0.0),
            (1.00, 0.50, -2, 2, 4, 0.0),
            (1.00, 0.85, -3, 2, 4, 0.0),
            (1.00, None, -3, 1, 5, 0.35),
            (1.00, None, -4, 1, 6, 0.65))):
        c = Canvas(size, size)
        hx = hexagon(scale)
        rim = edge_inner(hx, 8)
        rim2 = edge_inner(hx & ~rim, 4)
        if fill_i is not None:
            c.fill_mask(hx & ~rim & checker, R[fill_i])
        c.fill_mask(rim, R[rim_i])
        c.fill_mask(rim2, R[max(0, len(R) + rim_i - 2)] if rim_i < 0 else R[rim_i])
        if sweep is not None:
            band = np.abs((xs + ys) / (2 * size) - sweep) < 0.07
            c.fill_mask(hx & band & ~rim, R[-2])
            c.fill_mask(rim & band, W)
        if diss > 0:
            keep = dissolve(c.alpha_mask(), diss, seed)
            c.px[~keep] = 0
        out.append(c); ms.append(ticks(dur))
    return _anim("ward_shield", out, ms, False, ramp=ramp, tag="[GRD]", kind="oneshot")


# ================================================================= 7. AURA DE BUFF [BUF] (loop)
def ascend_aura(pal: Palette, w: int = 32, h: int = 48, frames: int = 8, ramp: str = "gold") -> Animation:
    """Chevrons subindo + base pulsante. Loop perfeito (fases inteiras)."""
    R = pal.ramp(ramp).colors
    cx = w // 2
    out: List[Canvas] = []
    chev = ["00100", "01110", "11011", "10001"]
    for f in range(frames):
        c = Canvas(w, h)
        # base eliptica
        pulse = (math.sin(2 * math.pi * f / frames) + 1) / 2
        rx, ry = 12 + int(round(pulse)), 3
        xs_, ys_ = grid(w, h)
        ell = ((xs_ - cx) / rx) ** 2 + ((ys_ - (h - 6)) / ry) ** 2 <= 1.0
        rim = edge_inner(ell, 8)
        c.fill_mask(rim & (ys_ >= h - 6), R[3])
        c.fill_mask(rim & (ys_ < h - 6), R[2])
        for i in range(3):
            ph = (f / frames + i / 3.0) % 1.0
            y = int(round(h - 10 - ph * (h - 14)))
            x = cx - 2 + int(round(math.sin(2 * math.pi * (ph + i * 0.37)) * 6))
            col = R[-1] if ph < 0.35 else (R[-2] if ph < 0.7 else R[2])
            for yy, row in enumerate(chev):
                for xx, ch in enumerate(row):
                    if ch == "1":
                        c.put(x + xx, y + yy, col)
        for i in range(4):
            ph = (f / frames * 2 + i / 4.0) % 1.0
            y = int(round(h - 8 - ph * (h - 10)))
            x = cx + int(round(math.cos(2 * math.pi * (i / 4.0)) * 10))
            if ph < 0.85:
                c.put(x, y, R[-2])
                if ph < 0.3:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        c.put(x + dx, y + dy, R[3])
        out.append(c)
    return _anim("ascend_aura", out, [ticks(5)] * frames, True, ramp=ramp, tag="[BUF]", kind="loop")


# ================================================================= 8. MALDICAO [DEB]
def curse_smoke(pal: Palette, size: int = 40, ramp: str = "violet", shadow: str = "void",
                seed: int = 8) -> Animation:
    """Fumaca amaldicoada: puffs esfericos (luz topo-esquerda), sobem, escurecem e dissolvem.
    Cor fica no meio-escuro da ramp: maldicao nao 'brilha', so a borda de luz acende."""
    V = pal.ramp(ramp).colors
    S = pal.ramp(shadow).colors
    rng = np.random.default_rng(seed)
    xs, ys = grid(size, size)
    cx, cy = size / 2.0, size * 0.64
    puffs = []
    for i in range(7):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.05, 0.22) * size
        puffs.append((math.cos(a) * d, math.sin(a) * d * 0.6, rng.uniform(0.11, 0.17) * size, rng.uniform(0.7, 1.3)))
    out: List[Canvas] = []
    ms: List[int] = []
    timeline = ((0.1, 3), (0.25, 3), (0.42, 4), (0.58, 4), (0.72, 5), (0.84, 5), (0.94, 6), (1.04, 6))
    for i, (t, dur) in enumerate(timeline):
        c = Canvas(size, size)
        best = np.zeros((size, size))
        lit = np.zeros((size, size))
        for (ox, oy, r, sp) in puffs:
            k = 0.55 + 0.75 * ease_out(t)
            bx, by = cx + ox * (1 + 0.8 * t), cy + oy - t * size * 0.30 * sp
            rr = r * k
            dx, dy = xs - bx, ys - by
            v = 1 - np.sqrt(dx * dx + dy * dy) / rr
            upd = v > best
            best = np.where(upd, v, best)
            lit = np.where(upd, sphere_lit(dx, dy, rr), lit)
        alive = best > 0
        if t > 0.5:
            alive = remove_specks(dissolve(alive, (t - 0.5) * 1.6, seed + 3, 7), 2)
        tone = np.where(lit > 0.80, 4, np.where(lit > 0.55, 3, np.where(lit > 0.25, 2, 1)))
        tone = np.where(alive, tone - (1 if t > 0.7 else 0), -1)
        tone = clean_index_map(tone)
        pal_cols = [S[1], S[2], V[1], V[2], V[3]]
        for k2, col in enumerate(pal_cols):
            c.fill_mask(tone == k2, col)
        out.append(c); ms.append(ticks(dur))
    return _anim("curse_smoke", out, ms, False, ramp=ramp, tag="[DEB]", kind="oneshot")


# ================================================================= 9. SANGUE [SAC]
def blood_burst(pal: Palette, size: int = 40, ramp: str = "blood", seed: int = 9) -> Animation:
    """Jato de sangue estilizado: respingo irregular (ruido, nao seno) + gotas balisticas
    alongadas na direcao do movimento, com brilho de 1px nos primeiros quadros."""
    B = pal.ramp(ramp).colors
    rng = np.random.default_rng(seed)
    cx, cy = size / 2.0, size * 0.42
    xs, ys = grid(size, size)
    drops = []
    for i in range(8):
        a = math.radians(-90 + (i - 3.5) / 3.5 * 62 + rng.uniform(-8, 8))
        sp = rng.uniform(0.75, 1.05) * size * 1.15
        drops.append((math.cos(a) * sp, math.sin(a) * sp, rng.uniform(1.2, 2.0)))
    g = size * 3.2
    ang = np.arctan2(ys - cy, xs - cx)
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    spikes = np.zeros_like(ang)
    for k in range(9):
        a = rng.uniform(-math.pi, math.pi)
        wdt = rng.uniform(0.12, 0.25)
        dd = np.angle(np.exp(1j * (ang - a)))
        spikes = np.maximum(spikes, np.clip(1 - np.abs(dd) / wdt, 0, 1) * rng.uniform(0.6, 1.3))
    out: List[Canvas] = []
    ms: List[int] = []
    for k, (rad, dur) in enumerate(((0.10, 2), (0.20, 3))):
        c = Canvas(size, size)
        lim = size * rad * (0.75 + 0.9 * spikes)
        m = remove_specks(dist <= lim, 2)
        c.fill_mask(m, B[3])
        c.fill_mask(edge_inner(m, 4) & (ys > cy), B[2])
        hl = m & (dist < size * rad * 0.45) & (xs < cx) & (ys < cy)
        c.fill_mask(hl, B[5])
        out.append(c); ms.append(ticks(dur))
    for k, t in enumerate((0.10, 0.18, 0.26, 0.34, 0.42, 0.50)):
        c = Canvas(size, size)
        core_r = size * 0.14 * max(0.0, 1 - t * 3.2)
        if core_r >= 1.5:
            m = dist <= core_r
            c.fill_mask(m, B[2])
        for (vx, vy, s) in drops:
            px = cx + vx * t
            py = cy + vy * t + 0.5 * g * t * t
            ux, uy = vx, vy + g * t
            ln = math.hypot(ux, uy) or 1
            ux, uy = ux / ln, uy / ln
            L = max(1, int(round(s * 1.5)))
            hx, hy = int(round(px)), int(round(py))
            # cabeca 2x2 nas gotas grandes (le melhor que 1px), cauda na direcao oposta ao movimento
            big = s > 1.6 and t < 0.4
            if big:
                for ddx, ddy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    c.put(hx + ddx, hy + ddy, B[3])
                c.put(hx, hy, B[5] if t < 0.3 else B[4])
            for j in range(1, L + 1):
                c.put(int(round(px - ux * j * 1.3)), int(round(py - uy * j * 1.3)), B[2])
            if not big:
                c.put(hx, hy, B[4] if t < 0.3 else B[3])
        out.append(c); ms.append(ticks(3 if k < 3 else 4))
    return _anim("blood_burst", out, ms, False, ramp=ramp, tag="[SAC]", kind="oneshot")


# ================================================================= 10. BRASAS (loop)
def embers_rising(pal: Palette, w: int = 24, h: int = 48, frames: int = 12, count: int = 7,
                  ramp: str = "ember", seed: int = 10) -> Animation:
    R = pal.ramp(ramp).colors
    rng = np.random.default_rng(seed)
    P = [(rng.uniform(3, w - 4), rng.uniform(0, 1), int(rng.integers(1, 3)), rng.uniform(1.0, 2.5)) for _ in range(count)]
    out: List[Canvas] = []
    for f in range(frames):
        c = Canvas(w, h)
        for (x0, ph, cyc, amp) in P:
            p = (f / frames + ph) % 1.0
            y = int(round(h - 2 - p * (h - 4)))
            x = int(round(x0 + math.sin(2 * math.pi * (cyc * f / frames + ph)) * amp))
            col = R[5] if p < 0.3 else (R[4] if p < 0.55 else (R[3] if p < 0.8 else R[1]))
            c.put(x, y, col)
            if p < 0.25:
                c.put(x, y + 1, R[3])  # rastro curto quando acabou de nascer
        out.append(c)
    return _anim("embers_rising", out, [ticks(5)] * frames, True, ramp=ramp, kind="loop")


# ================================================================= 11. COLUNA DE LUZ (loop)
def holy_pillar(pal: Palette, w: int = 24, h: int = 64, frames: int = 8, ramp: str = "gold") -> Animation:
    """Coluna de luz: faixas concentricas com nucleo branco; afina e some no topo;
    tracos verticais nas laterais sobem (fluxo); motes de luz subindo em loop."""
    R = pal.ramp(ramp).colors
    W = pal.ramp("flash").colors[-1]
    cx = (w - 1) / 2.0
    out: List[Canvas] = []
    for f in range(frames):
        c = Canvas(w, h)
        breathe = 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * f / frames))
        for y in range(h):
            yn = y / (h - 1)
            taper = min(1.0, 0.25 + yn / 0.45 * 0.75)      # topo mais fino
            if yn < 0.12 and (y + f) % 2:                   # ultimas linhas: 1 sim 1 nao
                continue
            for x in range(w):
                d = abs(x - cx) / taper
                if d <= 1.2 + breathe:
                    col = W
                elif d <= 3.6:
                    col = R[4]
                elif d <= 5.8 + breathe:
                    col = R[3]
                elif 7.0 <= d <= 8.2 and (y + f * 2 + (0 if x < cx else 3)) % 6 < 3:
                    col = R[2]                               # tracos que sobem
                else:
                    continue
                c.put(x, y, col)
        for i in range(4):
            ph = (f / frames + i / 4.0) % 1.0
            y = int(round(h - 2 - ph * (h - 6)))
            x = int(round(cx + (i - 1.5) * 7))
            if 0 <= x < w:
                c.put(x, y, W if ph < 0.6 else R[4])
        out.append(c)
    return _anim("holy_pillar", out, [ticks(5)] * frames, True, ramp=ramp, kind="loop")


ALL = {
    "fire_loop": fire_loop,
    "explosion": explosion,
    "slash_arc": slash_arc,
    "impact_spark": impact_spark,
    "magic_circle": magic_circle,
    "ward_shield": ward_shield,
    "ascend_aura": ascend_aura,
    "curse_smoke": curse_smoke,
    "blood_burst": blood_burst,
    "embers_rising": embers_rising,
    "holy_pillar": holy_pillar,
}
