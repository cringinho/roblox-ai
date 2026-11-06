"""Rasterizacao de formas em mascaras booleanas (sem anti-aliasing automatico).

Cada forma e avaliada no CENTRO de cada pixel, em coordenadas locais ja
rotacionadas/escaladas. Isso evita o borrao de 'rotacionar um bitmap'.

Regra de angulos limpos: em pixel art, retas so ficam limpas em inclinacoes
inteiras (1:1, 2:1, 1:2, 3:1 ...). snap_angle() aproxima o angulo pedido para
o angulo limpo mais proximo (0, 18.43, 26.57, 45, 63.43, 71.57, 90 ...).
"""
from __future__ import annotations

import math
from typing import Callable, List, Sequence, Tuple

import numpy as np

ShapeFn = Callable[[np.ndarray, np.ndarray], np.ndarray]

#: angulos com degraus inteiros (em graus, 0-90); espelhados para os 4 quadrantes
CLEAN_ANGLES = [0.0, math.degrees(math.atan(1 / 3)), math.degrees(math.atan(1 / 2)), 45.0,
                math.degrees(math.atan(2)), math.degrees(math.atan(3)), 90.0]


def snap_angle(deg: float) -> float:
    d = deg % 360.0
    base = math.floor(d / 90.0) * 90.0
    r = d - base
    best = min(CLEAN_ANGLES, key=lambda a: abs(a - r))
    return (base + best) % 360.0


def grid(w: int, h: int) -> Tuple[np.ndarray, np.ndarray]:
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    return xs + 0.5, ys + 0.5


def local(xs: np.ndarray, ys: np.ndarray, cx: float, cy: float, rx: float, ry: float,
          rot_deg: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    """Coordenadas locais normalizadas: (u,v) em [-1,1] dentro da caixa da forma.
    Rotacao em graus, sentido horario (igual ao GuiObject.Rotation do Roblox)."""
    t = math.radians(rot_deg)
    dx, dy = xs - cx, ys - cy
    u = (dx * math.cos(t) + dy * math.sin(t)) / max(rx, 1e-6)
    v = (-dx * math.sin(t) + dy * math.cos(t)) / max(ry, 1e-6)
    return u, v


def shape_mask(w: int, h: int, fn: ShapeFn, cx: float, cy: float, rx: float, ry: float,
               rot_deg: float = 0.0, snap: bool = False) -> np.ndarray:
    xs, ys = grid(w, h)
    if snap:
        rot_deg = snap_angle(rot_deg)
    u, v = local(xs, ys, cx, cy, rx, ry, rot_deg)
    return fn(u, v)


# ---------------------------------------------------------------- formas unitarias
def f_ellipse(u, v):
    return u * u + v * v <= 1.0


def f_ring(inner: float = 0.62):
    def fn(u, v):
        r2 = u * u + v * v
        return (r2 <= 1.0) & (r2 >= inner * inner)
    return fn


def f_diamond(u, v):
    return np.abs(u) + np.abs(v) <= 1.0


def f_rect(u, v):
    return (np.abs(u) <= 1.0) & (np.abs(v) <= 1.0)


def f_pillar(u, v):
    """Pinaculo gotico: fuste + capitel + base + agulha pontuda."""
    au = np.abs(u)
    shaft = (au <= 0.30) & (v >= -0.58) & (v <= 0.80)
    capital = (au <= 0.46) & (v >= -0.72) & (v < -0.58)
    base = (au <= 0.50) & (v > 0.80) & (v <= 1.0)
    spire = (v >= -1.0) & (v < -0.72) & (au <= 0.46 * (v + 1.0) / 0.28)
    return shaft | capital | base | spire


def f_blade(u, v):
    """Espada vertical, ponta para cima: lamina afinando + guarda + punho + pomo."""
    au = np.abs(u)
    blade_w = np.where(v < -0.62, 0.17 * (v + 1.0) / 0.38, 0.17)
    blade = (v >= -1.0) & (v <= 0.42) & (au <= blade_w)
    guard = (au <= 0.62) & (v > 0.42) & (v <= 0.55)
    grip = (au <= 0.09) & (v > 0.55) & (v <= 0.86)
    pommel = (u * u + ((v - 0.93) / 0.9) ** 2) <= 0.11 ** 2
    return blade | guard | grip | pommel


def f_crescent(u, v):
    outer = u * u + v * v <= 1.0
    inner = (u - 0.38) ** 2 + (v + 0.18) ** 2 <= 0.80 ** 2
    return outer & ~inner


def f_crown(u, v):
    """Coroa tripla: faixa + 3 pontas (a central mais alta) + perolas nas pontas."""
    band = (np.abs(u) <= 0.92) & (v >= 0.28) & (v <= 0.78)
    out = band.copy()
    for sc, top in ((-0.62, -0.50), (0.0, -0.92), (0.62, -0.50)):
        hw = 0.30
        t = (v - top) / (0.28 - top)
        spike = (v >= top) & (v <= 0.28) & (np.abs(u - sc) <= hw * np.clip(t, 0, 1))
        pearl = (u - sc) ** 2 + ((v - top + 0.06) / 1.0) ** 2 <= 0.10 ** 2
        out |= spike | pearl
    return out


def f_teardrop(u, v):
    """Gota/chama com ponta para cima (v<0)."""
    r = np.where(v > 0, 1.0, np.clip((v + 1.0), 0, 1) ** 1.6)
    return (u * u) <= (r * r) * (1.0 - np.clip(v, 0, 1) ** 2)


def f_arc_band(r_in: float, r_out: float, a0: float, a1: float):
    """Faixa de anel entre angulos (graus, 0 = direita, horario). Base de slashes."""
    def fn(u, v):
        r = np.sqrt(u * u + v * v)
        ang = (np.degrees(np.arctan2(v, u)) + 360.0) % 360.0
        lo, hi = a0 % 360.0, a1 % 360.0
        inside_ang = (ang >= lo) & (ang <= hi) if lo <= hi else (ang >= lo) | (ang <= hi)
        return (r >= r_in) & (r <= r_out) & inside_ang
    return fn


def f_star(points: int = 4, inner: float = 0.28, phase_deg: float = -90.0):
    """Estrela de impacto (spikes). inner = raio interno relativo."""
    def fn(u, v):
        r = np.sqrt(u * u + v * v)
        ang = np.arctan2(v, u) - math.radians(phase_deg)
        k = (np.cos(points * ang) + 1.0) / 2.0  # 1 nas pontas, 0 entre elas
        lim = inner + (1.0 - inner) * k ** 3
        return r <= lim
    return fn


def polygon_mask(w: int, h: int, pts: Sequence[Tuple[float, float]]) -> np.ndarray:
    """Point-in-polygon (regra par-impar) avaliado no centro dos pixels."""
    xs, ys = grid(w, h)
    inside = np.zeros((h, w), dtype=bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if y1 == y2:
            continue
        cond = ((y1 > ys) != (y2 > ys))
        xint = (x2 - x1) * (ys - y1) / (y2 - y1) + x1
        inside ^= cond & (xs < xint)
    return inside


SHAPES = {
    "DIAMOND": f_diamond,
    "PILLAR": f_pillar,
    "RING": f_ring(0.62),
    "BLADE": f_blade,
    "CRESCENT": f_crescent,
    "CROWN": f_crown,
    "ELLIPSE": f_ellipse,
    "RECT": f_rect,
    "TEARDROP": f_teardrop,
}


# ---------------------------------------------------------------- operacoes de mascara
def shift(m: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(m)
    h, w = m.shape
    xs0, xs1 = max(0, dx), min(w, w + dx)
    ys0, ys1 = max(0, dy), min(h, h + dy)
    out[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def dilate(m: np.ndarray, conn: int = 4) -> np.ndarray:
    out = m.copy()
    for dx, dy in (N4 if conn == 4 else N8):
        out |= shift(m, dx, dy)
    return out


def erode(m: np.ndarray, conn: int = 4) -> np.ndarray:
    out = m.copy()
    for dx, dy in (N4 if conn == 4 else N8):
        out &= shift(m, dx, dy)
    return out


def edge_inner(m: np.ndarray, conn: int = 4) -> np.ndarray:
    """Pixels da forma que tocam o exterior."""
    return m & ~erode(m, conn)


def edge_outer(m: np.ndarray, conn: int = 4) -> np.ndarray:
    """Pixels de fora que tocam a forma (onde vai o contorno externo)."""
    return dilate(m, conn) & ~m


def distance_inside(m: np.ndarray) -> np.ndarray:
    """Distancia (em erosoes) ate a borda, alternando 4/8 vizinhos (aprox. octogonal)."""
    d = np.zeros(m.shape, dtype=np.float64)
    cur = m.copy()
    k = 0
    while cur.any() and k < 512:
        d[cur] += 1.0
        cur = erode(cur, 4 if k % 2 == 0 else 8)
        k += 1
    return d


def remove_specks(m: np.ndarray, min_neighbors: int = 2) -> np.ndarray:
    """Remove pixels isolados de uma mascara (menos de N vizinhos 8-conectados)."""
    cnt = np.zeros(m.shape, dtype=np.int32)
    for dx, dy in N8:
        cnt += shift(m, dx, dy).astype(np.int32)
    return m & (cnt >= min_neighbors)


def fill_holes(m: np.ndarray, max_size: int = 1) -> np.ndarray:
    """Fecha buracos de 1px (pixel vazio cercado por 4 vizinhos cheios)."""
    cnt = np.zeros(m.shape, dtype=np.int32)
    for dx, dy in N4:
        cnt += shift(m, dx, dy).astype(np.int32)
    return m | (cnt >= 4)


def mirror_x(m: np.ndarray) -> np.ndarray:
    """Simetria horizontal (copia a metade esquerda na direita)."""
    w = m.shape[1]
    out = m.copy()
    out[:, w - w // 2:] = m[:, : w // 2][:, ::-1]
    return out


def lines_mask(w: int, h: int, segs: Sequence[Tuple[int, int, int, int]], perfect: bool = True) -> np.ndarray:
    from .canvas import line_points
    m = np.zeros((h, w), dtype=bool)
    for (x0, y0, x1, y1) in segs:
        for (x, y) in line_points(x0, y0, x1, y1, perfect):
            if 0 <= x < w and 0 <= y < h:
                m[y, x] = True
    return m


def points_on_circle(cx: float, cy: float, r: float, n: int, phase_deg: float = 0.0) -> List[Tuple[int, int]]:
    out = []
    for i in range(n):
        a = math.radians(phase_deg + 360.0 * i / n)
        out.append((int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a)))))
    return out
