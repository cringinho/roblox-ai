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
from typing import TYPE_CHECKING, List, Sequence, Tuple

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

    # ---------------------------------------------------------- estatuas aladas (sprite desenhado a mao)
    # Formas organicas vem do sprites_lib (texto) e sao sombreadas pelo motor; o rim light
    # violeta fica no lado que da para o vitral mais proximo.
    from .sprite import render_spec
    from .sprites_lib import ANGEL_STATUE
    for sx in (cx - 112, cx + 112):
        towards = 1 if sx < cx else -1
        st = render_spec(ANGEL_STATUE, pal, outline="both", rim=("violet:3", (towards, 0)))
        c.blit(st, int(sx - st.w / 2), floor_y - st.h + 1)

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


# =====================================================================================
# FORJA (segunda referencia do The Dark Altar)
# =====================================================================================
def _hex_cells(xw: np.ndarray, zw: np.ndarray, size: float) -> Tuple[np.ndarray, np.ndarray]:
    """Arredondamento cubico: coordenadas de mundo -> (q, r) da lajota hexagonal (flat-top)."""
    q = (2.0 / 3.0 * xw) / size
    r = (-1.0 / 3.0 * xw + math.sqrt(3) / 3.0 * zw) / size
    x, z = q, r
    y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    fix_x = (dx > dy) & (dx > dz)
    fix_y = ~fix_x & (dy > dz)
    rx = np.where(fix_x, -ry - rz, rx)
    rz = np.where(~fix_x & ~fix_y, -rx - ry, rz)
    return rx.astype(int), rz.astype(int)


def _warm_light(d: np.ndarray, r: float, levels: int = 5) -> np.ndarray:
    """Poca de luz (L-07/L-09): I = (1 - smoothstep(0.3r, r, d))^1.6, devolvida em 0..levels."""
    t = np.clip((d - 0.3 * r) / (0.7 * r), 0, 1)
    s = t * t * (3 - 2 * t)
    return np.clip((1 - s), 0, 1) ** 1.6 * levels


def _band_dither(t: np.ndarray, th: np.ndarray) -> np.ndarray:
    """Banda inteira com transicao em xadrez so perto da fronteira (+-1 nivel, estilizado)."""
    base = np.floor(t)
    frac = t - base
    up = (frac > 0.82) | ((frac > 0.62) & (th > 0.5))
    return (base + up).astype(int)


def forge(pal: Palette, w: int = 320, h: int = 180, frames: int = 6, seed: int = 11,
          posters: Sequence[Canvas] = ()) -> "Animation":
    """Interior de forja animado: lareira com fogo em loop, flicker de luz que so escurece,
    brasas subindo, lajotas hexagonais iluminadas pela fornalha, bigorna e barril desenhados
    (sprites_lib) com rim light do fogo, quadros de cartas na parede.

    posters: ate 5 imagens (ex.: artes de subtipo 24x24) penduradas no painel da direita;
    vazio = emblemas genericos.
    Retorna Animation (frames x 320x180) - exporte com sheet.export_gui_sheet (cabe em 1024).
    """
    from .anim import Animation, ticks
    from .fx import fire_loop
    from .raster import polygon_mask, remove_specks
    from .sprite import render_spec
    from .sprites_lib import ANVIL, BARREL

    V = pal.ramp("void").colors
    S = pal.ramp("slate").colors
    E = pal.ramp("earth").colors
    F = pal.ramp("ember").colors
    G = pal.ramp("gold").colors
    xs, ys = grid(w, h)
    th = dither_threshold(w, h, 4)
    floor_y = int(h * 0.64)
    fire_x, fire_y = 95.0, floor_y - 12.0
    flicker = [0.00, 0.05, 0.02, 0.06, 0.01, 0.04, 0.03, 0.05]
    fire = fire_loop(pal, w=22, h=34, frames=frames, seed=seed)
    fire2 = fire_loop(pal, w=22, h=30, frames=frames, seed=seed + 4)
    anvil = render_spec(ANVIL, pal, outline="both", rim=("ember:4", (-1, 0)))
    barrel = render_spec(BARREL, pal, outline="both", rim=("ember:3", (-1, 0)))

    # ------------------------------------------------------------------ geometria fixa
    wall = ys < floor_y
    hood = polygon_mask(w, h, [(58, 6), (132, 6), (146, 46), (44, 46)])
    mantel = (xs >= 40) & (xs < 150) & (ys >= 46) & (ys < 52)
    surround = (xs >= 48) & (xs < 142) & (ys >= 52) & (ys < floor_y - 4)
    arch_r = 22.0
    arch_cx, arch_spring = 95.0, 80.0
    opening = (((xs - arch_cx) ** 2 + (ys - arch_spring) ** 2 <= arch_r ** 2) & (ys <= arch_spring)) | \
              ((np.abs(xs - arch_cx) <= arch_r) & (ys > arch_spring) & (ys < floor_y - 4))
    voussoir = (((xs - arch_cx) ** 2 + (ys - arch_spring) ** 2 <= (arch_r + 5) ** 2) & (ys <= arch_spring + 1)) & ~opening
    hearth = (xs >= 62) & (xs < 128) & (ys >= floor_y - 4) & (ys < floor_y + 3)
    board = (xs >= 198) & (xs < 306) & (ys >= 20) & (ys < 112)
    beam = ys < 7

    # lajotas hexagonais em perspectiva
    vp_y = floor_y - 50
    yy = np.maximum(ys - vp_y, 1.0)
    z = 3000.0 / yy
    xw = (xs - 160) * z / 95.0
    q, r = _hex_cells(xw, z, 15.0)
    cell_id = q * 1000 + r
    grout = np.zeros((h, w), dtype=bool)
    grout[:, :-1] |= cell_id[:, :-1] != cell_id[:, 1:]
    grout[:-1, :] |= cell_id[:-1, :] != cell_id[1:, :]
    tone = np.vectorize(lambda a, b: hash01(int(a), int(b), seed))(q, r)

    out: List[Canvas] = []
    for f in range(frames):
        k = 1.0 - flicker[f % len(flicker)]                    # flicker SO escurece
        jitter = np.array([round((hash01(y, f, seed) - 0.5) * 2.2) for y in range(h)], dtype=float)[:, None]
        d_wall = np.sqrt((xs - fire_x + jitter) ** 2 + (ys - fire_y) ** 2)
        d_floor = np.sqrt((xs - fire_x + jitter) ** 2 + ((ys - fire_y) * 2.3) ** 2)
        Lw = _band_dither(_warm_light(d_wall, 112 * k, 4), th)
        Lf = _band_dither(_warm_light(d_floor, 128 * k, 4), th)

        c = Canvas(w, h, V[1])
        warm = [V[2], pal["blood:1"], E[1], pal["blood:2"], F[2]]   # 0 = sem luz .. 4 = mais quente
        warm_hi = [V[3], E[1], pal["blood:2"], E[2], F[3]]

        # parede de pedra fria (blocos 16x8) que esquenta perto do fogo
        rows = (ys.astype(int) // 8)
        offs = np.where(rows % 2 == 0, 0, 8)
        bx = (xs.astype(int) + offs) // 16
        mortar = ((ys.astype(int) % 8) == 0) | (((xs.astype(int) + offs) % 16) == 0)
        btone = np.vectorize(lambda a, b: hash01(int(a), int(b), seed + 3))(rows, bx) > 0.5
        for lv in range(5):
            m = wall & (Lw == lv)
            c.fill_mask(m & ~mortar & btone, warm_hi[lv] if lv else V[3])
            c.fill_mask(m & ~mortar & ~btone, warm[lv] if lv else V[2])
            c.fill_mask(m & mortar, warm[max(0, lv - 1)] if lv else V[1])

        # viga do teto
        c.fill_mask(beam, E[0])
        c.fill_mask(beam & (ys == 6), V[0])
        c.fill_mask(beam & (ys == 1), E[1])

        # coifa da lareira (pedra clara iluminada por baixo) + consolo + moldura de tijolos
        hood_t = np.clip((ys - 6) / 40.0, 0, 1)
        hb = (ys.astype(int) - 6) // 7
        hoff = np.where(hb % 2 == 0, 0, 7)
        hmortar = (((ys.astype(int) - 6) % 7) == 0) | (((xs.astype(int) + hoff) % 14) == 0)
        c.fill_mask(hood & (hood_t < 0.55), S[2])
        c.fill_mask(hood & (hood_t >= 0.55), S[3])
        c.fill_mask(hood & (hood_t >= 0.85), E[2])
        c.fill_mask(hood & hmortar, S[1])
        c.fill_mask(hood & hmortar & (hood_t >= 0.85), E[1])
        c.fill_mask(edge_inner(hood, 4) & (xs < 95) & (hood_t < 0.85), S[4])
        c.fill_mask(mantel, S[5])
        c.fill_mask(mantel & (ys == 51), S[2])
        c.fill_mask(mantel & (ys == 46), S[6])
        sb = (ys.astype(int) // 5)
        so = np.where(sb % 2 == 0, 0, 5)
        smortar = ((ys.astype(int) % 5) == 0) | (((xs.astype(int) + so) % 10) == 0)
        c.fill_mask(surround & ~smortar, E[2])
        c.fill_mask(surround & smortar, E[1])
        c.fill_mask(surround & ~smortar & (np.abs(xs - arch_cx) < 38) & (Lw >= 3), pal["blood:3"])
        # aduelas do arco (radiais) bem iluminadas
        ang = np.degrees(np.arctan2(ys - arch_spring, xs - arch_cx))
        vline = (np.abs((ang + 180) % 15 - 7.5) < 1.0)
        c.fill_mask(voussoir & ~vline, F[2])
        c.fill_mask(voussoir & vline, E[1])
        c.fill_mask(voussoir & (ys < arch_spring - arch_r + 2), F[3])

        # interior da fornalha + leito de carvao + fogo animado
        c.fill_mask(opening, pal["blood:0"])
        c.fill_mask(opening & (ys > arch_spring + 12), pal["blood:1"])
        fa, fb = fire.frames[f % len(fire.frames)], fire2.frames[(f + 2) % len(fire2.frames)]
        c.blit(fb, int(arch_cx - 22), floor_y - 4 - fb.h)
        c.blit(fa, int(arch_cx - 6), floor_y - 4 - fa.h)
        for i in range(14):
            ex = int(arch_cx - 18 + i * 2.7)
            ey = floor_y - 6 - int(hash01(i, f // 2, seed) * 2)
            c.put(ex, ey, F[5] if (i + f) % 3 == 0 else F[3])
            c.put(ex + 1, ey + 1, F[2])
        c.fill_mask(hearth, S[3])
        c.fill_mask(hearth & (ys == floor_y - 4), S[5])

        # painel de madeira com quadros de cartas
        c.fill_mask(board, E[1])
        c.fill_mask(board & ((xs.astype(int) - 198) % 12 == 0), E[0])
        c.fill_mask(edge_inner(board, 4), E[2])
        slots = [(206, 28), (238, 28), (270, 28), (222, 70), (254, 70)]
        accents = [pal["abyss:4"], pal["blood:4"], pal["gold:4"], pal["ember:4"], pal["spirit:4"]]
        for i, (px_, py_) in enumerate(slots):
            fr = Canvas(28, 36, V[0])
            fr.rect_outline(0, 0, 28, 36, G[3], 1)
            fr.rect_outline(1, 1, 26, 34, pal["violet:2"], 1)
            if i < len(posters):
                art = posters[i]
                fr.blit(art, (28 - art.w) // 2, 3)
            else:
                from .raster import SHAPES, shape_mask
                m = shape_mask(24, 24, SHAPES["DIAMOND"], 12, 12, 6, 9)
                em = Canvas(24, 24, V[1])
                em.fill_mask(m, accents[i])
                fr.blit(em, 2, 3)
            fr.fill_rect(3, 29, 22, 4, V[1])
            fr.fill_rect(5, 30, 18, 1, G[2])
            for cxk in (3, 23):
                fr.put(cxk, 1, G[4])
            c.blit(fr, px_, py_)
            # vela embaixo dos quadros de baixo
            if i >= 3:
                c.fill_rect(px_ + 12, py_ + 37, 3, 4, pal["bone:4"])
                c.put(px_ + 13, py_ + 35 + (f % 2), F[5])
                c.put(px_ + 13, py_ + 36, F[4])

        # piso de lajotas hexagonais com a poca de luz quente
        floor = ys >= floor_y
        f_cold = [V[1], V[2]]
        f_warm = [[V[1], V[2]], [pal["blood:1"], E[1]], [E[1], E[2]], [E[2], pal["blood:3"]], [F[2], F[3]]]
        for lv in range(5):
            m = floor & (Lf == lv)
            pair = f_warm[lv] if lv else f_cold
            c.fill_mask(m & (tone > 0.5), pair[1])
            c.fill_mask(m & (tone <= 0.5), pair[0])
        c.fill_mask(floor & grout, V[0])
        c.fill_mask(floor & grout & (Lf >= 3), pal["blood:1"])
        # luz na borda de cada lajota (bisel do lado do fogo)
        lit_edge = floor & ~grout & np.roll(grout, 1, axis=0) & (Lf >= 2)
        c.fill_mask(lit_edge, F[2])

        # sombra projetada da bigorna (para longe do fogo) + bigorna + barril
        ax, ay = 150, h - anvil.h - 4
        shadow = polygon_mask(w, h, [(ax + 12, ay + anvil.h - 2), (ax + anvil.w + 26, ay + anvil.h - 2),
                                     (ax + anvil.w + 40, h - 1), (ax + 18, h - 1)]) & floor
        c.fill_mask(shadow & (Lf <= 2), V[0])
        c.fill_mask(shadow & (Lf > 2), E[0])
        c.blit(anvil, ax, ay)
        bx_, by_ = 268, floor_y + 8
        c.fill_mask(polygon_mask(w, h, [(bx_ + 4, by_ + barrel.h - 2), (bx_ + barrel.w + 10, by_ + barrel.h - 2),
                                        (bx_ + barrel.w + 16, by_ + barrel.h + 4), (bx_ + 8, by_ + barrel.h + 4)]) & floor, V[0])
        c.blit(barrel, bx_, by_)

        # brasas subindo da fornalha (fase inteira -> loop perfeito)
        for i in range(6):
            ph = (f / frames + i / 6.0) % 1.0
            ex = int(arch_cx - 10 + i * 4 + math.sin(2 * math.pi * (ph + i * 0.3)) * 2)
            ey = int(floor_y - 30 - ph * 46)
            if hood[ey, ex] or opening[ey, ex] or not wall[ey, ex]:
                c.put(ex, ey, F[5] if ph < 0.4 else (F[4] if ph < 0.7 else F[2]))

        # vinheta (dither estilizado)
        vig = np.clip((np.abs(xs - 160) / 160.0) ** 2 + (np.abs(ys - 95) / 110.0) ** 2 - 0.62, 0, 1)
        c.fill_mask((vig > 0.08) & (vig > th * 0.7), V[0])

        c.px = pal.quantize(c.px)
        out.append(c)
    return Animation("forge", out, [ticks(6)] * frames, loop=True,
                     tags={"kind": "scene", "contrast_frames": ""})
