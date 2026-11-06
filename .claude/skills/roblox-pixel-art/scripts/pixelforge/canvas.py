"""Canvas RGBA com alpha duro (0 ou 255) e primitivas pixel-perfect.

Regras embutidas:
- nunca existe alpha intermediario (pixel art = transparencia binaria)
- linhas usam Bresenham + limpeza de 'cotovelos' (pixel-perfect)
- compor (blit) respeita alpha duro
- ampliar so por fator inteiro (nearest neighbor)
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from .color import RGB, RGBA

Color = Sequence[int]


def _c4(c: Color) -> Tuple[int, int, int, int]:
    if len(c) == 4:
        return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))
    return (int(c[0]), int(c[1]), int(c[2]), 255)


class Canvas:
    def __init__(self, w: int, h: int, fill: Optional[Color] = None):
        self.w, self.h = int(w), int(h)
        self.px = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        if fill is not None:
            self.px[...] = _c4(fill)

    # ------------------------------------------------------------ basico
    @staticmethod
    def from_array(a: np.ndarray) -> "Canvas":
        c = Canvas(a.shape[1], a.shape[0])
        c.px = a.astype(np.uint8).copy()
        return c

    @staticmethod
    def from_image(img: Image.Image) -> "Canvas":
        return Canvas.from_array(np.array(img.convert("RGBA")))

    def copy(self) -> "Canvas":
        return Canvas.from_array(self.px)

    def to_image(self) -> Image.Image:
        return Image.fromarray(self.px, "RGBA")

    def save(self, path, scale: int = 1) -> None:
        img = self.to_image()
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        img.save(path)

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x: int, y: int, c: Color) -> None:
        if self.inside(x, y):
            self.px[y, x] = _c4(c)

    def get(self, x: int, y: int) -> RGBA:
        return tuple(int(v) for v in self.px[y, x])  # type: ignore[return-value]

    def alpha_mask(self) -> np.ndarray:
        return self.px[..., 3] > 0

    def clear(self) -> None:
        self.px[...] = 0

    # ------------------------------------------------------------ preenchimentos
    def fill_rect(self, x: int, y: int, w: int, h: int, c: Color) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0:
            self.px[y0:y1, x0:x1] = _c4(c)

    def fill_mask(self, mask: np.ndarray, c: Color) -> None:
        self.px[mask] = _c4(c)

    def rect_outline(self, x: int, y: int, w: int, h: int, c: Color, t: int = 1) -> None:
        for i in range(t):
            self.fill_rect(x + i, y + i, w - 2 * i, 1, c)
            self.fill_rect(x + i, y + h - 1 - i, w - 2 * i, 1, c)
            self.fill_rect(x + i, y + i, 1, h - 2 * i, c)
            self.fill_rect(x + w - 1 - i, y + i, 1, h - 2 * i, c)

    # ------------------------------------------------------------ linhas
    def line(self, x0: int, y0: int, x1: int, y1: int, c: Color, perfect: bool = True) -> None:
        for (x, y) in line_points(x0, y0, x1, y1, perfect):
            self.put(x, y, c)

    def polyline(self, pts: Sequence[Tuple[int, int]], c: Color, closed: bool = False) -> None:
        seq = list(pts) + ([pts[0]] if closed else [])
        allp: List[Tuple[int, int]] = []
        for a, b in zip(seq, seq[1:]):
            seg = bresenham(a[0], a[1], b[0], b[1])
            if allp and seg and seg[0] == allp[-1]:
                seg = seg[1:]
            allp.extend(seg)
        for (x, y) in pixel_perfect(allp):
            self.put(x, y, c)

    # ------------------------------------------------------------ composicao
    def blit(self, src: "Canvas", x: int, y: int) -> None:
        """Cola src em (x,y) respeitando alpha duro (alpha>0 sobrescreve)."""
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        w = min(src.w - sx0, self.w - dx0)
        h = min(src.h - sy0, self.h - dy0)
        if w <= 0 or h <= 0:
            return
        s = src.px[sy0:sy0 + h, sx0:sx0 + w]
        d = self.px[dy0:dy0 + h, dx0:dx0 + w]
        m = s[..., 3] > 0
        d[m] = s[m]

    def blend_over(self, src: "Canvas", x: int, y: int, opacity: float) -> None:
        """Mistura com opacidade (use so ANTES de quantizar; o resultado deve voltar a paleta)."""
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        w = min(src.w - sx0, self.w - dx0)
        h = min(src.h - sy0, self.h - dy0)
        if w <= 0 or h <= 0:
            return
        s = src.px[sy0:sy0 + h, sx0:sx0 + w].astype(np.float64)
        d = self.px[dy0:dy0 + h, dx0:dx0 + w].astype(np.float64)
        m = s[..., 3] > 0
        d[m, :3] = d[m, :3] * (1 - opacity) + s[m, :3] * opacity
        d[m, 3] = np.maximum(d[m, 3], 255)
        self.px[dy0:dy0 + h, dx0:dx0 + w] = d.astype(np.uint8)

    def flip_x(self) -> "Canvas":
        return Canvas.from_array(self.px[:, ::-1])

    def flip_y(self) -> "Canvas":
        return Canvas.from_array(self.px[::-1, :])

    def crop(self, x: int, y: int, w: int, h: int) -> "Canvas":
        out = Canvas(w, h)
        out.blit(Canvas.from_array(self.px[max(0, y):y + h, max(0, x):x + w]), max(0, -x), max(0, -y))
        return out

    def bbox(self) -> Optional[Tuple[int, int, int, int]]:
        m = self.alpha_mask()
        if not m.any():
            return None
        ys, xs = np.where(m)
        return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

    def scaled(self, k: int) -> "Canvas":
        """Ampliacao inteira nearest (unica forma permitida de escalar pixel art)."""
        return Canvas.from_array(np.repeat(np.repeat(self.px, k, axis=0), k, axis=1))

    def unique_colors(self) -> List[RGB]:
        m = self.alpha_mask()
        cols = {tuple(int(v) for v in p[:3]) for p in self.px[m]}
        return sorted(cols)  # type: ignore[return-value]


# ---------------------------------------------------------------- algoritmos de linha
def bresenham(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    pts: List[Tuple[int, int]] = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return pts


def pixel_perfect(pts: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Remove 'cotovelos' (L-corners): se a-b-c formam um L, b sai.

    E a regra classica de linha pixel-perfect: uma linha de 1px nunca deve ter
    pixels que se tocam pelos dois lados (horizontal E vertical) num canto.
    """
    out: List[Tuple[int, int]] = []
    i = 0
    n = len(pts)
    while i < n:
        if 0 < i < n - 1 and out:
            a, b, c = out[-1], pts[i], pts[i + 1]
            if (a[0] == b[0] or a[1] == b[1]) and (b[0] == c[0] or b[1] == c[1]) \
                    and a[0] != c[0] and a[1] != c[1]:
                i += 1
                continue
        out.append(pts[i])
        i += 1
    return out


def line_points(x0: int, y0: int, x1: int, y1: int, perfect: bool = True) -> List[Tuple[int, int]]:
    pts = bresenham(x0, y0, x1, y1)
    return pixel_perfect(pts) if perfect else pts
