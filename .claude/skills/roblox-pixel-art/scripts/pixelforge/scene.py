"""Cenarios (backgrounds) em pixel art: nave de catedral gotica.

Regras de composicao aplicadas (references/04-cenarios-gotico.md):
- valor baixo e pouco croma no ambiente (pedra roxo-acinzentada); o UNICO croma
  alto fica nos vitrais = ponto focal (acento em ~10-20% da imagem)
- perspectiva de 1 ponto: porta central escura puxa o olho para o centro
- piso polido: reflexo espelhado da parede, escurecido e com degraus de dither
- luz colorida dos vitrais 'derramada' no chao em faixas
- fundo sem preto puro; topo (abobada) some na escuridao em dither ordenado
- tudo quantizado para a paleta ALTAR no final (paleta fechada)
"""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

import numpy as np

from .canvas import Canvas
from .color import RGB, mix
from .noise import hash01, value_noise2
from .palette import Palette
from .raster import dilate, edge_inner, edge_outer, grid
from .shade import dither_threshold


def _ogive_mask(xs, ys, cx: float, base: float, half_w: float, top: float) -> np.ndarray:
    u = (xs - cx) / half_w
    v = (base - ys) / max(base - top, 1e-3)
    vv = v * math.sqrt(3.0)
    arch = ((u + 1) ** 2 + vv ** 2 <= 4.0) & ((u - 1) ** 2 + vv ** 2 <= 4.0) & (v >= 0)
    return arch


def lancet(xs, ys, cx: float, top: float, bottom: float, half_w: float) -> np.ndarray:
    """Janela lanceta: retangulo + ogiva no topo."""
    spring = top + half_w * 1.6
    body = (np.abs(xs - cx) <= half_w) & (ys >= spring) & (ys <= bottom)
    return body | _ogive_mask(xs, ys, cx, spring, half_w, top)


def cathedral(pal: Palette, w: int = 320, h: int = 180, seed: int = 7) -> Canvas:
    xs, ys = grid(w, h)
    V = pal.ramp("void").colors
    S = pal.ramp("slate").colors
    c = Canvas(w, h, V[1])
    floor_y = int(h * 0.64)
    cx = w / 2.0

    # ---------------------------------------------------------- parede de tijolos
    wall = ys < floor_y
    bw, bh = 12, 5
    rows = (ys.astype(int) // bh)
    offs = np.where(rows % 2 == 0, 0, bw // 2)
    bx = ((xs.astype(int) + offs) // bw)
    mortar = ((ys.astype(int) % bh) == 0) | (((xs.astype(int) + offs) % bw) == 0)
    tone = np.vectorize(lambda r, b: hash01(int(r), int(b), seed))(rows, bx)
    brick_a = wall & ~mortar & (tone > 0.55)
    brick_b = wall & ~mortar & (tone <= 0.55)
    c.fill_mask(brick_b, V[2])
    c.fill_mask(brick_a, V[3])
    c.fill_mask(wall & mortar, V[1])
    # escuridao da abobada (topo) e laterais em dither ordenado 4x4
    th = dither_threshold(w, h, 4)
    dark_t = np.clip(1.0 - ys / (floor_y * 0.55), 0, 1) * 0.95 + np.clip(np.abs(xs - cx) / (w * 0.5) - 0.68, 0, 1) * 1.2
    c.fill_mask(wall & (dark_t > th + 0.25), V[1])
    c.fill_mask(wall & (dark_t > th + 0.85), V[0])

    # ---------------------------------------------------------- porta central (ogiva escura)
    door = lancet(xs, ys, cx, floor_y - 92, floor_y, 26)
    door_frame = dilate(dilate(door, 4), 4) & ~door & wall
    c.fill_mask(door_frame, S[2])
    c.fill_mask(edge_inner(dilate(dilate(door, 4), 4), 4) & ~door & (xs < cx), S[3])
    c.fill_mask(door, V[0])
    inner = lancet(xs, ys, cx, floor_y - 80, floor_y, 18)
    c.fill_mask(edge_inner(inner, 4) & door & (ys < floor_y - 10), V[1])

    # ---------------------------------------------------------- vitrais (unico croma alto)
    glass_cols = [pal["blood:4"], pal["gold:4"], pal["violet:4"], pal["spirit:4"], pal["abyss:4"],
                  pal["rose:4"], pal["ember:4"], pal["violet:3"], pal["abyss:3"], pal["blood:3"]]
    windows = []
    for wx in (cx - 74, cx + 74):
        win = lancet(xs, ys, wx, 14, floor_y - 26, 12)
        windows.append((wx, win))
        frame = dilate(dilate(win, 4), 8) & ~win
        c.fill_mask(frame, S[2])
        c.fill_mask(edge_inner(dilate(dilate(win, 4), 8), 4) & ~win & (xs < wx), S[4])
        # vidro em losangos (grade diagonal) com chumbo escuro
        u = (xs - wx) / 4.0
        v = (ys - 14) / 4.0
        a = np.floor(u + v)
        b = np.floor(u - v)
        lead = (np.abs((u + v) - np.round(u + v)) < 0.13) | (np.abs((u - v) - np.round(u - v)) < 0.13)
        # padrao DESENHADO (nao aleatorio): simetrico no eixo do vitral, em faixas
        # verticais de cor + medalhao central -> leitura de vitral, nao confete
        ua = np.floor(np.abs(xs - wx) / 4.0 + 0.5)            # coluna espelhada
        band = np.floor((ys - 14) / 10.0)                      # faixa vertical
        scheme = [(2, 7), (0, 9), (3, 8), (4, 2), (1, 0), (5, 2)]  # pares (centro, borda)
        cell_col = np.zeros((h, w), dtype=int)
        for bi in range(int(band.max()) + 1):
            cen, edge = scheme[bi % len(scheme)]
            m_b = band == bi
            cell_col[m_b & (ua <= 1)] = cen
            cell_col[m_b & (ua > 1)] = edge
        # medalhao: anel dourado com centro vermelho na altura media
        my = 14 + (floor_y - 26 - 14) * 0.45
        rr = np.sqrt((xs - wx) ** 2 + (ys - my) ** 2)
        cell_col[(rr <= 9) & (rr > 6)] = 1
        cell_col[rr <= 6] = 0
        # ruido leve: 1 em 7 losangos troca para a cor vizinha (vidro artesanal)
        jitter = np.vectorize(lambda p, q: hash01(int(p), int(q), seed + int(wx)))(a, b) > 0.86
        cell_col = np.where(jitter & (rr > 9), (cell_col + 2) % len(glass_cols), cell_col)
        for k, col in enumerate(glass_cols):
            c.fill_mask(win & ~lead & (cell_col == k), col)
        c.fill_mask(win & lead, V[0])
        # brilho: alguns losangos no topo mais claros
        hi = win & ~lead & (ys < 30) & (np.abs(xs - wx) < 5)
        c.fill_mask(hi, pal["gold:5"])
        # mainel central
        c.fill_mask(win & (np.abs(xs - wx) < 0.6), V[0])

    # ---------------------------------------------------------- colunas da porta + pilares de frente
    def column(x0: int, width: int, top: int, bottom: int, cols: Sequence[RGB]) -> None:
        for x in range(x0, x0 + width):
            t = (x - x0) / max(1, width - 1)
            # cilindro iluminado pela direita-centro (luz da nave): escuro na esquerda
            idx = 0 if t < 0.18 else (1 if t < 0.45 else (2 if t < 0.8 else 1))
            c.fill_rect(x, top, 1, bottom - top, cols[idx])
        c.fill_rect(x0 - 2, top, width + 4, 3, cols[2])        # capitel
        c.fill_rect(x0 - 2, bottom - 3, width + 4, 3, cols[1])  # base

    col_cols = [V[1], V[2], V[4]]
    for x0 in (int(cx - 42), int(cx + 34)):
        column(x0, 8, 6, floor_y, col_cols)
    big = [V[0], V[1], V[2]]
    column(0, 16, 0, h, big)
    column(w - 16, 16, 0, h, big)

    # ---------------------------------------------------------- degraus do altar
    for k, (y0, inset, col) in enumerate(((floor_y - 6, 44, S[2]), (floor_y - 3, 52, S[1]))):
        c.fill_rect(int(cx - 70 + inset - 44), y0, int(140 - 2 * (inset - 44)), 3, col)
        c.fill_rect(int(cx - 70 + inset - 44), y0, int(140 - 2 * (inset - 44)), 1, S[3])

    # ---------------------------------------------------------- estatuas aladas (silhueta + rim light)
    from .raster import polygon_mask
    for sx in (cx - 112, cx + 112):
        fy = floor_y - 12                                  # topo do pedestal
        plinth = (np.abs(xs - sx) <= 15) & (ys >= fy) & (ys < floor_y)
        cap = (np.abs(xs - sx) <= 17) & (ys >= fy) & (ys < fy + 2)
        robe = polygon_mask(w, h, [(sx - 4, fy - 34), (sx + 4, fy - 34), (sx + 9, fy), (sx - 9, fy)])
        hood = (xs - sx) ** 2 + ((ys - (fy - 37)) * 1.15) ** 2 <= 5.0 ** 2
        arms = polygon_mask(w, h, [(sx - 6, fy - 26), (sx + 6, fy - 26), (sx + 3, fy - 18), (sx - 3, fy - 18)])
        wing = np.zeros_like(robe)
        feathers = []
        for side in (-1, 1):
            # leque: 4 penas longas saindo do ombro, abrindo para cima e para fora
            ox, oy = sx + side * 3, fy - 30
            for k, (ang, ln) in enumerate(((96, 30), (108, 27), (120, 23), (132, 18), (144, 13))):
                a = math.radians(ang if side < 0 else 180 - ang)
                # cada pena nasce mais baixa e mais para fora ao longo do braco da asa
                ox, oy = sx + side * (3 + k * 2.2), fy - 31 + k * 3.2
                tx, ty = ox + math.cos(a) * ln, oy - math.sin(a) * ln
                # largura da pena perpendicular a direcao (para FORA do corpo)
                nx, ny = math.sin(a) * 5.0 * -side, math.cos(a) * 5.0 * -side
                poly = [(ox, oy), (ox + nx, oy + ny), (tx + nx * 0.45, ty + ny * 0.45), (tx, ty)]
                pm = dilate(polygon_mask(w, h, poly), 4)
                wing |= pm
                feathers.append(pm)
        body = robe | hood | arms | wing
        c.fill_mask(plinth, S[2])
        c.fill_mask(cap, S[3])
        c.fill_mask(edge_inner(plinth, 4) & (ys > fy + 2) & (xs < sx - 13), S[3])
        c.fill_mask(body, S[1])
        for fm in feathers:                                # separacao entre penas
            c.fill_mask(edge_inner(fm, 8) & ~edge_inner(body, 4), S[0])
        towards = 1 if sx < cx else -1                     # rim light do lado do vitral
        rim = edge_inner(body, 4) & (((xs - sx) * towards) > 2)
        c.fill_mask(rim & (ys < fy - 30), pal["violet:3"])
        c.fill_mask(rim & (ys >= fy - 30), S[4])
        c.fill_mask(hood & (((xs - sx) * towards) > 1), S[3])

    # ---------------------------------------------------------- piso xadrez em perspectiva + reflexo
    vp_y = floor_y - 46
    fl = ys >= floor_y
    yy = np.maximum(ys - vp_y, 1.0)
    z = 2600.0 / yy
    xw = (xs - cx) * z / 90.0
    tile = 38.0
    parity = ((np.floor(xw / tile) + np.floor(z / tile)) % 2).astype(int)
    base_a, base_b = V[2], V[1]
    src = c.px.copy()
    for y in range(floor_y, h):
        my = floor_y - (y - floor_y) - 1
        for x in range(w):
            base = base_a if parity[y, x] == 0 else base_b
            col = base
            if my >= 0:
                s = tuple(int(v) for v in src[my, x, :3])
                # reflexo: forte perto da linha do piso, some com a distancia (em degraus)
                dist = (y - floor_y) / (h - floor_y)
                k = 0.42 if dist < 0.25 else (0.28 if dist < 0.55 else 0.16)
                bright = sum(s) > sum(base) + 60
                if bright or dist < 0.55:
                    col = mix(base, s, k if bright else k * 0.5)
            c.px[y, x, :3] = col
            c.px[y, x, 3] = 255
    # linhas das juntas do piso (escuras, finas)
    gx = np.abs(xw / tile - np.round(xw / tile)) * tile < 0.9 * z / 90.0
    gz = np.abs(z / tile - np.round(z / tile)) * tile < 0.5 * z / 60.0
    c.fill_mask(fl & (gx | gz), V[1])

    # ---------------------------------------------------------- luz colorida derramada no piso
    for (wx, _), tint_i in zip(windows, (0, 3)):
        for k in range(6):
            col = glass_cols[(tint_i + k) % len(glass_cols)]
            y0 = floor_y + 6 + k
            x0 = int(wx + (cx - wx) * 0.25) + k * 3
            length = 22 - k * 2
            for j in range(length):
                if (j + k) % 3 != 2:
                    c.put(x0 + j * (1 if wx < cx else -1) * 2 // 2 + (j // 2) * (1 if wx < cx else -1), y0, col)

    # ---------------------------------------------------------- vinheta de cantos
    vig = np.clip((np.abs(xs - cx) / (w * 0.5)) ** 2 + (np.abs(ys - h * 0.45) / (h * 0.6)) ** 2 - 0.65, 0, 1)
    c.fill_mask((vig > th * 0.9) & (vig > 0.05), V[0])

    # ---------------------------------------------------------- poeira no feixe (motes)
    for k in range(14):
        px = int(cx - 60 + hash01(k, 1, seed) * 120)
        py = int(20 + hash01(k, 2, seed) * (floor_y - 30))
        c.put(px, py, V[5] if k % 3 else pal["gold:4"])

    c.px = pal.quantize(c.px)
    return c
