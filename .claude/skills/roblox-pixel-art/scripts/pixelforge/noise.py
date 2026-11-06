"""Ruido de valor periodico (tileable) para VFX em loop perfeito.

Por que periodico: um VFX em loop (fogo, aura, agua) so fica sem 'pulo' se o
quadro N for igual ao quadro 0. Usando ruido com periodo no eixo do tempo
(e/ou no eixo vertical que rola), o loop fecha matematicamente.
"""
from __future__ import annotations

import numpy as np


def _smooth(t: np.ndarray) -> np.ndarray:
    return t * t * (3.0 - 2.0 * t)


class PeriodicNoise3:
    """Ruido de valor 3D com periodos inteiros (px, py, pt) -> repete em x, y e tempo."""

    def __init__(self, px: int, py: int, pt: int, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.p = (px, py, pt)
        self.lat = rng.random((pt, py, px))

    def sample(self, x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
        px, py, pt = self.p
        x0 = np.floor(x).astype(np.int64)
        y0 = np.floor(y).astype(np.int64)
        t0 = int(np.floor(t))
        fx, fy, ft = _smooth(x - x0), _smooth(y - y0), _smooth(np.array(t - t0))
        L = self.lat

        def g(ti, yi, xi):
            return L[ti % pt, yi % py, xi % px]

        out = 0.0
        for dt, wt in ((0, 1 - ft), (1, ft)):
            ti = t0 + dt
            a = g(ti, y0, x0) * (1 - fx) + g(ti, y0, x0 + 1) * fx
            b = g(ti, y0 + 1, x0) * (1 - fx) + g(ti, y0 + 1, x0 + 1) * fx
            out = out + wt * (a * (1 - fy) + b * fy)
        return out


def fbm_loop(w: int, h: int, frame: int, frames: int, cells: int = 4, octaves: int = 3,
             seed: int = 0, scroll_y: float = 1.0) -> np.ndarray:
    """FBM em loop: campo (h,w) 0..1 que rola para CIMA e fecha o ciclo em 'frames'.

    cells = quantas celulas de ruido cabem na largura (escala do detalhe).
    scroll_y = quantos periodos verticais o campo sobe durante o loop (inteiro = loop perfeito).
    """
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        c = cells * (2 ** o)
        cy = max(1, int(round(c * h / w)))
        noise = PeriodicNoise3(c, cy, frames, seed + 101 * o)
        t = frame
        u = xs / w * c
        v = ys / h * cy + (frame / frames) * cy * scroll_y
        total += amp * noise.sample(u, v, t)
        norm += amp
        amp *= 0.5
    return total / norm


def value_noise2(w: int, h: int, cells: int = 8, seed: int = 0) -> np.ndarray:
    """Ruido 2D tileable simples (0..1) - texturas de pedra, manchas, variacao de tiles."""
    cy = max(1, int(round(cells * h / w)))
    n = PeriodicNoise3(cells, cy, 1, seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    return n.sample(xs / w * cells, ys / h * cy, 0.0)


def hash01(x: int, y: int, seed: int = 0) -> float:
    """Hash deterministico 0..1 (posicionamento de detalhes sem RNG global)."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFF) / float(0xFFFFFF)
