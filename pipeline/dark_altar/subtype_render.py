"""Renderizador pixel art das Artes de Subtipo (modo 'atlas pre-renderizado').

Mesmo dado do catalogo Luau -> mesma composicao em pixel art 64x64:
  1. fundo (bgHex) + vinheta em dither
  2. monograma (watermarkGlyph) quase no tom do fundo
  3. gravura (etchingPattern) em linhas finas, baixo contraste
  4. emblema concentrico (centerSilhouettes) estilo xilogravura: contorno de tinta,
     3 tons do acento (sombra hachurada / meio / luz), luz do topo-esquerda
  5. particulas (particleGlyph) e, se isGlitchy, fatias deslocadas (glitch estatico)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "roblox-pixel-art" / "scripts"))

from pixelforge.canvas import Canvas  # noqa: E402
from pixelforge.color import hex_to_rgb, mix  # noqa: E402
from pixelforge.font import text_mask  # noqa: E402
from pixelforge.noise import hash01  # noqa: E402
from pixelforge.raster import (SHAPES, dilate, edge_inner, grid, lines_mask,  # noqa: E402
                               shape_mask)
from pixelforge.shade import bands, clean_index_map, dither_threshold, light_intensity  # noqa: E402

BLACK = (6, 5, 10)
WHITE = (255, 248, 236)
S = 64


def _seed(sid: str) -> int:
    return sum((i + 1) * ord(c) for i, c in enumerate(sid)) % 100000


# ------------------------------------------------------------------ gravuras
def etching(pattern: str, sid: str, size: int = S) -> np.ndarray:
    seed = _seed(sid)
    xs, ys = grid(size, size)
    cx = cy = size / 2.0
    m = np.zeros((size, size), dtype=bool)
    if pattern == "WAVES":
        for k, base in enumerate(range(4, size, 7)):
            ph = hash01(k, 1, seed) * 6.28
            yy = base + 2.0 * np.sin(xs / 5.5 + ph)
            m |= np.abs(ys - yy) < 0.5
    elif pattern == "RAYS":
        ang = np.degrees(np.arctan2(ys - cy, xs - cx)) % 360
        r = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        near = np.min(np.stack([np.abs(((ang - a + 180) % 360) - 180) for a in range(0, 360, 15)]), axis=0)
        ray = (near * np.pi / 180 * r) < 0.55
        dash = ((r.astype(int) // 3) % 3) != 0
        m |= ray & dash & (r > 6)
    elif pattern == "ABYSS":
        r = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        # aneis cada vez mais proximos no centro (sensacao de queda)
        rings = [4, 7, 11, 16, 22, 29, 37, 46]
        for rr in rings:
            m |= np.abs(r - rr) < 0.5
        ang = np.arctan2(ys - cy, xs - cx)
        spiral = np.abs(((r - ang * 3.2 + 100) % 9.0) - 4.5) < 0.5
        m |= spiral & (r > 24)
    elif pattern == "SPIKES":
        for row, y0 in enumerate(range(6, size + 6, 10)):
            off = 5 if row % 2 else 0
            for x0 in range(-5 + off, size + 5, 10):
                h = 3 + int(hash01(x0, y0, seed) * 3)
                pts = [(x0 - 2, y0), (x0, y0 - h), (x0 + 2, y0)]
                m |= lines_mask(size, size, [(pts[0][0], pts[0][1], pts[1][0], pts[1][1]),
                                             (pts[1][0], pts[1][1], pts[2][0], pts[2][1])])
    elif pattern == "ARCHES":
        # arcada gotica: arcos ogivais + colunas
        w_arch = 16
        for x0 in range(0, size + w_arch, w_arch):
            for y0 in (size - 2, size // 2 - 4):
                top = y0 - 22
                left, right = x0 - w_arch // 2 + 1, x0 + w_arch // 2 - 1
                # ogiva = dois arcos de circulo que se cruzam no topo
                rr = (right - left) * 0.9
                for (ccx, sign) in ((right - rr, 1), (left + rr, -1)):
                    a = np.sqrt((xs - ccx) ** 2 + (ys - (y0 - 10)) ** 2)
                    arc = (np.abs(a - rr) < 0.55) & (ys < y0 - 10) & (ys > top) & \
                          ((xs - x0) * sign <= 0.5)
                    m |= arc
                m |= (np.abs(xs - left) < 0.5) & (ys >= y0 - 11) & (ys <= y0)
                m |= (np.abs(xs - right) < 0.5) & (ys >= y0 - 11) & (ys <= y0)
    elif pattern == "ROOTS":
        rng = np.random.default_rng(seed)
        segs: List[Tuple[int, int, int, int]] = []

        def grow(x, y, ang, length, depth):
            if depth > 4 or length < 3:
                return
            x1 = int(round(x + math.cos(ang) * length))
            y1 = int(round(y + math.sin(ang) * length))
            segs.append((int(x), int(y), x1, y1))
            grow(x1, y1, ang + rng.uniform(-0.6, -0.15), length * 0.72, depth + 1)
            if rng.random() < 0.7:
                grow(x1, y1, ang + rng.uniform(0.15, 0.6), length * 0.66, depth + 1)

        for x0 in (6, 22, 40, 57):
            grow(x0, size - 1, -math.pi / 2 + rng.uniform(-0.3, 0.3), 12, 0)
        for x0 in (14, 48):
            grow(x0, 0, math.pi / 2 + rng.uniform(-0.3, 0.3), 9, 1)
        m |= lines_mask(size, size, segs)
    elif pattern == "FRACTAL":
        rng = np.random.default_rng(seed)
        pts = rng.uniform(0, size, (14, 2))
        d = np.stack([np.sqrt((xs - px) ** 2 + (ys - py) ** 2) for px, py in pts])
        d.sort(axis=0)
        m |= (d[1] - d[0]) < 0.9  # bordas de Voronoi = facetas de cristal
    elif pattern == "SCALES":
        r_s = 6
        for row, y0 in enumerate(range(0, size + r_s, r_s)):
            off = r_s if row % 2 else 0
            for x0 in range(-r_s + off, size + r_s, r_s * 2):
                a = np.sqrt((xs - x0) ** 2 + (ys - y0) ** 2)
                m |= (np.abs(a - r_s) < 0.55) & (ys > y0)
    return m


# ------------------------------------------------------------------ particulas
PARTICLE_BITMAPS = {
    "·": ["#"],
    "†": [".#.", "###", ".#.", ".#."],
    "◆": [".#.", "###", ".#."],
    "~": ["#...", ".#.#", "...."][:2],
}


def stamp(c: Canvas, bmp: List[str], x: int, y: int, col) -> None:
    for yy, row in enumerate(bmp):
        for xx, ch in enumerate(row):
            if ch == "#":
                c.put(x + xx, y + yy, col)


# ------------------------------------------------------------------ render principal
def render(st, size: int = S) -> Canvas:
    bg = hex_to_rgb(st.bg)
    acc = hex_to_rgb(st.accent)
    bg_dark = mix(bg, BLACK, 0.55)
    etch_c = mix(bg, acc, 0.20)
    wm_c = mix(bg, acc, 0.11)
    acc_hi = mix(acc, WHITE, 0.45)
    acc_mid = mix(acc, bg, 0.30)
    acc_dark = mix(acc, bg, 0.62)
    ink = mix(bg, BLACK, 0.70)
    part_c = mix(acc, bg, 0.45)

    c = Canvas(size, size, bg)
    xs, ys = grid(size, size)
    cx = cy = size / 2.0

    # 2. monograma
    scale = 4 if len(st.watermark) == 1 else 3
    tm = text_mask(st.watermark, scale=scale, bold=True)
    th, tw = tm.shape
    ox, oy = (size - tw) // 2, (size - th) // 2
    wm = np.zeros((size, size), dtype=bool)
    wm[max(0, oy):oy + th, max(0, ox):ox + tw] = tm[:min(th, size - oy), :min(tw, size - ox)]
    c.fill_mask(wm, wm_c)

    # 3. gravura
    et = etching(st.pattern, st.sid, size)
    c.fill_mask(et & ~wm, etch_c)
    c.fill_mask(et & wm, mix(etch_c, acc, 0.12))

    # 1b. vinheta em degraus (escurece os cantos, foca o centro).
    #     Dither ESTILIZADO: so 0% / 50% (xadrez) / 100% -> sem pontos isolados (ruido).
    r = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / (size * 0.5)
    checker = ((np.mgrid[0:size, 0:size][0] + np.mgrid[0:size, 0:size][1]) % 2) == 0
    solid = r > 1.18
    half = (r > 1.02) & ~solid
    c.fill_mask((solid | (half & checker)) & ~et, bg_dark)

    # 4. emblema concentrico (xilogravura)
    union = np.zeros((size, size), dtype=bool)
    for sil in st.sils:
        fn = SHAPES[sil.shape]
        m = shape_mask(size, size, fn, cx, cy, sil.sx * size / 2.0, sil.sy * size / 2.0, sil.rot, snap=True)
        if not m.any():
            continue
        # contorno de tinta separa a forma da gravura e das formas anteriores
        c.fill_mask(dilate(m, 4) & ~m, ink)
        lam = light_intensity(m, profile="dome", depth=2.2)
        idx = bands(lam, m, 3, bias=0.06)
        idx = clean_index_map(idx)
        shadow = idx == 0
        hatch = shadow & (((np.mgrid[0:size, 0:size][1] - np.mgrid[0:size, 0:size][0]) % 3) == 0)
        # hachura: remove tracos de 1px soltos na borda da faixa de sombra
        from pixelforge.raster import remove_specks
        hatch = remove_specks(hatch, 1)
        c.fill_mask(shadow, acc_dark)
        c.fill_mask(hatch, acc_mid)
        c.fill_mask(idx == 1, acc)
        c.fill_mask(idx == 2, acc_hi)
        # sel-out: borda do lado da sombra mais escura
        e = edge_inner(m, 4)
        c.fill_mask(e & ((xs - cx) + (ys - cy) > 0), acc_dark)
        union |= m

    # 5. particulas em anel, longe do emblema
    seed = _seed(st.sid)
    bmp = PARTICLE_BITMAPS.get(st.particle, ["#"])
    keep_out = dilate(dilate(union, 8), 8)
    placed = 0
    for k in range(40):
        if placed >= 7:
            break
        a = hash01(k, 3, seed) * 2 * math.pi
        rr = size * (0.30 + 0.16 * hash01(k, 5, seed))
        px = int(round(cx + math.cos(a) * rr))
        py = int(round(cy + math.sin(a) * rr))
        h, w = len(bmp), len(bmp[0])
        if px < 2 or py < 2 or px + w > size - 2 or py + h > size - 2:
            continue
        if keep_out[py:py + h, px:px + w].any():
            continue
        stamp(c, bmp, px, py, acc if placed % 3 == 0 else part_c)
        keep_out[max(0, py - 3):py + h + 3, max(0, px - 3):px + w + 3] = True
        placed += 1

    # glitch estatico: 2 fatias horizontais deslocadas + linha 'quebrada'
    if st.glitchy:
        for k, (hgt, shift) in enumerate(((2, 2), (1, -3), (3, -1))):
            y0 = int(8 + hash01(k, 7, seed) * (size - 16))
            c.px[y0:y0 + hgt] = np.roll(c.px[y0:y0 + hgt], shift, axis=1)
        y1 = int(size * 0.5 + (hash01(9, 9, seed) - 0.5) * 20)
        row = c.px[y1]
        lit = (row[:, 0].astype(int) + row[:, 1] + row[:, 2]) > (sum(acc) * 0.8)
        row[lit, :3] = acc_hi
    return c
