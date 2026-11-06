"""Sombreamento, contorno e limpeza.

Regras implementadas (ver references/01-fundamentos.md):
- LUZ UNICA: toda forma recebe luz da mesma direcao (padrao: topo-esquerda).
- Sombreamento por campo de altura + direcao de luz -> evita 'pillow shading'
  (sombrear do centro para a borda, sem luz definida).
- Bandas da ramp quantizadas + limpeza de pixels orfaos -> clusters limpos.
- Sel-out: contorno interno com a versao mais escura da cor vizinha; lado da luz
  mais claro que o lado da sombra.
- Contorno externo opcional (UI/icones precisam; VFX normalmente nao).
- Dithering ordenado (Bayer) so para transicoes grandes/planas (ceu, luz volumetrica).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

import numpy as np

from .canvas import Canvas
from .color import RGB
from .palette import Palette, Ramp
from .raster import N4, N8, distance_inside, edge_inner, edge_outer, shift

LIGHT_TOP_LEFT = (-0.62, -0.70, 0.36)


def _norm(v: Sequence[float]) -> Tuple[float, float, float]:
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)


def height_field(mask: np.ndarray, profile: str = "dome", flat_top: float = 0.0) -> np.ndarray:
    """Altura 0..1 a partir da distancia ate a borda.
    profile: 'dome' (redondo), 'bevel' (chanfro: borda inclinada + topo plano), 'flat'."""
    d = distance_inside(mask)
    if d.max() <= 0:
        return d
    n = d / d.max()
    if profile == "dome":
        return np.sqrt(np.clip(n, 0, 1))
    if profile == "bevel":
        edge = max(1.0, 3.0)
        b = np.clip(d / edge, 0, 1)
        return b
    return (d > 0).astype(np.float64)


def light_intensity(mask: np.ndarray, light=LIGHT_TOP_LEFT, profile: str = "dome",
                    depth: float = 3.0) -> np.ndarray:
    """Intensidade lambertiana 0..1 dentro da mascara."""
    h = height_field(mask, profile) * depth
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx, -gy, np.ones_like(h)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    lx, ly, lz = _norm(light)
    lam = np.clip(nx * lx + ny * ly + nz * lz, 0.0, 1.0)
    return np.where(mask, lam, 0.0)


def bands(intensity: np.ndarray, mask: np.ndarray, n: int, bias: float = 0.0,
          gamma: float = 1.0) -> np.ndarray:
    """Quantiza intensidade em n faixas (indices 0..n-1)."""
    t = np.clip(intensity ** gamma + bias, 0.0, 0.9999)
    idx = (t * n).astype(np.int32)
    return np.where(mask, idx, -1)


def clean_index_map(idx: np.ndarray, passes: int = 2) -> np.ndarray:
    """Remove pixels orfaos num mapa de indices: se nenhum dos 8 vizinhos tem o
    mesmo indice, o pixel vira o indice vizinho mais comum (cluster limpo)."""
    out = idx.copy()
    h, w = idx.shape
    for _ in range(passes):
        changed = False
        src = out.copy()
        for y in range(h):
            for x in range(w):
                v = src[y, x]
                if v < 0:
                    continue
                neigh = []
                same = 0
                for dx, dy in N8:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and src[yy, xx] >= 0:
                        nv = src[yy, xx]
                        neigh.append(nv)
                        if nv == v:
                            same += 1
                if same == 0 and neigh:
                    vals, counts = np.unique(np.array(neigh), return_counts=True)
                    out[y, x] = vals[np.argmax(counts)]
                    changed = True
        if not changed:
            break
    return out


def paint_index_map(c: Canvas, idx: np.ndarray, ramp: Sequence[RGB], offset: int = 0) -> None:
    for i in range(int(idx.max()) + 1 if idx.max() >= 0 else 0):
        m = idx == i
        if m.any():
            j = max(0, min(len(ramp) - 1, i + offset))
            c.fill_mask(m, ramp[j])


def form_shade(c: Canvas, mask: np.ndarray, ramp: Sequence[RGB], light=LIGHT_TOP_LEFT,
               profile: str = "dome", depth: float = 3.0, lo: int = 1, hi: Optional[int] = None,
               bias: float = 0.0, clean: bool = True) -> np.ndarray:
    """Pinta 'mask' com sombreamento de forma usando ramp[lo..hi].
    Reservar ramp[0] para contorno/sombra mais escura e ramp[-1] para brilho especular."""
    hi = len(ramp) - 2 if hi is None else hi
    n = max(1, hi - lo + 1)
    lam = light_intensity(mask, light, profile, depth)
    idx = bands(lam, mask, n, bias)
    if clean:
        idx = clean_index_map(idx)
    paint_index_map(c, idx, ramp, offset=lo)
    return idx


def outline(c: Canvas, color: RGB, mask: Optional[np.ndarray] = None, conn: int = 4,
            perfect: bool = True) -> None:
    """Contorno externo de 1px. perfect=True remove cotovelos (linha pixel-perfect nas diagonais)."""
    from .raster import thin_elbows
    m = c.alpha_mask() if mask is None else mask
    e = edge_outer(m, conn)
    c.fill_mask(thin_elbows(e) if perfect else e, color)


def selout(c: Canvas, pal: Palette, mask: Optional[np.ndarray] = None,
           light=LIGHT_TOP_LEFT, dark_steps: int = 2, lit_steps: int = 1) -> None:
    """Sel-out: borda interna recebe a cor vizinha escurecida; menos escura no lado da luz."""
    from .raster import thin_elbows
    m = c.alpha_mask() if mask is None else mask
    e = thin_elbows(edge_inner(m, 4))
    lx, ly, _ = _norm(light)
    ys, xs = np.where(e)
    src = c.px.copy()
    h, w = m.shape
    for y, x in zip(ys, xs):
        # direcao para fora = media dos vizinhos vazios
        ox = oy = 0.0
        for dx, dy in N4:
            xx, yy = x + dx, y + dy
            if not (0 <= xx < w and 0 <= yy < h) or not m[yy, xx]:
                ox += dx
                oy += dy
        facing_light = (ox * lx + oy * ly) > 0.2
        col = tuple(int(v) for v in src[y, x, :3])
        steps = -lit_steps if facing_light else -dark_steps
        c.put(x, y, pal.shift(col, steps))


def drop_shadow(c: Canvas, color: RGB, dx: int = 1, dy: int = 1) -> None:
    """Sombra dura deslocada (UI). Aplica atras dos pixels existentes."""
    m = c.alpha_mask()
    sh = shift(m, dx, dy) & ~m
    c.fill_mask(sh, color)


def rim_light(c: Canvas, mask: np.ndarray, color: RGB, light=LIGHT_TOP_LEFT, width: int = 1) -> None:
    """Luz de recorte no lado OPOSTO a luz principal (contra-luz) - destaca do fundo escuro."""
    lx, ly, _ = _norm(light)
    e = edge_inner(mask, 4)
    ys, xs = np.where(e)
    h, w = mask.shape
    for y, x in zip(ys, xs):
        ox = oy = 0.0
        for dx, dy in N4:
            xx, yy = x + dx, y + dy
            if not (0 <= xx < w and 0 <= yy < h) or not mask[yy, xx]:
                ox += dx
                oy += dy
        if (ox * -lx + oy * -ly) > 0.5:
            c.put(x, y, color)


# ---------------------------------------------------------------- dithering
def bayer(n: int = 4) -> np.ndarray:
    """Matriz de Bayer normalizada (0..1). n = 2, 4 ou 8."""
    m = np.array([[0, 2], [3, 1]], dtype=np.float64)
    while m.shape[0] < n:
        k = m.shape[0]
        m = np.block([[4 * m + 0, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / (m.size)


def dither_threshold(w: int, h: int, n: int = 4, ox: int = 0, oy: int = 0) -> np.ndarray:
    b = bayer(n)
    ys, xs = np.mgrid[0:h, 0:w]
    return b[(ys + oy) % n, (xs + ox) % n]


def dither_mix(t: np.ndarray, n: int = 4, levels: Optional[Sequence[float]] = None) -> np.ndarray:
    """Dado t em 0..1, devolve mascara booleana 'usa cor B' por dithering ordenado.
    levels restringe a padroes legiveis (0, 1/4, 1/2, 3/4, 1) - evita textura de ruido."""
    h, w = t.shape
    th = dither_threshold(w, h, n)
    tt = t
    if levels is not None:
        lv = np.array(sorted(levels))
        tt = lv[np.abs(t[..., None] - lv[None, None, :]).argmin(axis=-1)]
    return tt > th


def gradient_dither(c: Canvas, mask: np.ndarray, t: np.ndarray, ramp: Sequence[RGB],
                    n: int = 4, stylized: bool = True) -> None:
    """Gradiente pela ramp usando dithering apenas na fronteira entre dois degraus."""
    k = len(ramp) - 1
    pos = np.clip(t, 0, 1) * k
    base = np.floor(pos).astype(np.int32)
    frac = pos - base
    levels = (0.0, 0.25, 0.5, 0.75, 1.0) if stylized else None
    up = dither_mix(frac, n, levels)
    idx = np.clip(base + up.astype(np.int32), 0, k)
    for i in range(k + 1):
        m = mask & (idx == i)
        if m.any():
            c.fill_mask(m, ramp[i])
