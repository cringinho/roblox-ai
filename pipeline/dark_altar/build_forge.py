"""Gera os assets pixel art da Forja (+0..+5), mascaras de forma/gravura e mockups.

Uso (na raiz):  python pipeline/dark_altar/build_forge.py

Saidas em art/dark-altar/forge/:
  ForgeOrnamentAtlas.png   -> todos os ornamentos (ImageRectOffset em ForgeOrnamentAtlas.luau)
  ShapeMaskAtlas.png       -> 6 silhuetas x 3 camadas (fill/shade/ink), brancas p/ ImageColor3
  EtchingAtlas.png         -> 8 gravuras brancas 64x64 (tingir com ResolvedColors.etch)
  mock_forge_levels.png    -> previa da carta em +0..+5 (referencia visual da spec)
e src/shared/Config/ForgeOrnamentAtlas.luau (retangulos tipados).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "roblox-pixel-art" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from pixelforge.canvas import Canvas  # noqa: E402
from pixelforge.color import hex_to_rgb, mix  # noqa: E402
from pixelforge.font import text_mask  # noqa: E402
from pixelforge.fx import circle_pts, holy_pillar  # noqa: E402
from pixelforge.palette import altar_palette  # noqa: E402
from pixelforge.raster import (SHAPES, dilate, edge_inner, edge_outer, f_crown, grid,  # noqa: E402
                               polygon_mask, shape_mask)
from pixelforge.shade import bands, clean_index_map, light_intensity  # noqa: E402
from pixelforge.ui import border_mask  # noqa: E402

import subtypes as data  # noqa: E402
from build_subtypes import derive_colors  # noqa: E402
from subtype_render import etching, render  # noqa: E402

OUT = ROOT / "art" / "dark-altar" / "forge"
LUAU = ROOT / "src" / "shared" / "Config" / "ForgeOrnamentAtlas.luau"
PAL = altar_palette()
WHITE = (255, 255, 255)

# tokens da spec
SLATE = hex_to_rgb("#1E1E24")
IRON = hex_to_rgb("#2C2E35")
CYAN = hex_to_rgb("#4DD0E1")
VIOLET = hex_to_rgb("#B388FF")
AMBER = hex_to_rgb("#E5A93C")


# ------------------------------------------------------------------ sombreamento de bevel
def bevel(c: Canvas, mask: np.ndarray, outline, dark, mid, light, hi=None) -> None:
    """Bevel classico de pixel art (luz topo-esquerda), consistente em qualquer orientacao:
    pixel exposto em cima/esquerda = claro; exposto embaixo/direita = escuro."""
    h, w = mask.shape
    from pixelforge.raster import erode, thin_elbows
    c.fill_mask(thin_elbows(edge_outer(mask, 4)), outline)       # contorno pixel-perfect
    pad = np.pad(mask, 1, constant_values=False)
    up = ~pad[:-2, 1:-1]
    left = ~pad[1:-1, :-2]
    down = ~pad[2:, 1:-1]
    right = ~pad[1:-1, 2:]
    tl = (up | left) & mask
    br = (down | right) & mask
    # partes de 1 px de espessura (filigrana, pontas) ficam no tom medio: alternar claro/escuro
    # pixel a pixel em traco fino vira ruido
    thick = dilate(erode(mask, 4), 4) & mask
    c.fill_mask(mask, mid)
    c.fill_mask(tl & ~br & thick, light)
    c.fill_mask(br & ~tl & thick, dark)
    if hi is not None:
        # brilho especular so onde vira cluster (2+ pixels de quina iluminada juntos)
        corner = mask & up & left & thick
        from pixelforge.raster import remove_specks
        c.fill_mask(remove_specks(corner | (tl & ~br & thick & corner), 1), hi)


def iron_ramp():
    s = PAL.ramp("slate").colors
    return dict(outline=s[0], dark=s[2], mid=s[3], light=s[5], hi=s[7])


def gold_ramp():
    g = PAL.ramp("gold").colors
    return dict(outline=PAL["void:0"], dark=g[1], mid=g[3], light=g[4], hi=g[5])


def bone_ramp():
    b = PAL.ramp("bone").colors
    return dict(outline=PAL["void:0"], dark=b[1], mid=b[3], light=b[4], hi=b[5])


def violet_ramp():
    v = PAL.ramp("violet").colors
    return dict(outline=PAL["void:0"], dark=v[1], mid=v[3], light=v[4], hi=v[6])


def mask_from_rows(rows: List[str], ch: str = "x") -> np.ndarray:
    return np.array([[c == ch for c in r] for r in rows], dtype=bool)


# ------------------------------------------------------------------ ornamentos
def corner(orient: str) -> Canvas:
    """Cantoneira de ferro forjado (L com pontas lanceoladas) + rebite."""
    rows = [
        "xxxxxxxxx..",
        "xxxxxxxxxx.",
        "xxxxxxxxx..",
        "xxx........",
        "xxx........",
        "xxx........",
        "xxx........",
        "xxx........",
        "xxx........",
        ".x.........",
        "...........",
    ]
    m = mask_from_rows(rows)
    if orient in ("tr", "br"):
        m = m[:, ::-1]
    if orient in ("bl", "br"):
        m = m[::-1, :]
    big = np.pad(m, 1, constant_values=False)
    c = Canvas(big.shape[1], big.shape[0])
    bevel(c, big, **iron_ramp())
    # rebite no encontro das hastes
    rx = 2 if orient in ("tl", "bl") else big.shape[1] - 4
    ry = 2 if orient in ("tl", "tr") else big.shape[0] - 4
    c.put(rx, ry, PAL["slate:7"])
    c.put(rx + 1, ry + 1, PAL["slate:1"])
    return c


def ogival_arch(w: int = 41, h: int = 18) -> Canvas:
    """Arco ogival de catedral (ogiva equilatera normalizada para caber no sprite):
    dois arcos de circulo que se cruzam em ponta + soleira + trifolio com vitral."""
    xs, ys = grid(w, h)
    cx = w / 2.0
    base = h - 3.0

    def ogive(a: float, top: float) -> np.ndarray:
        # u: -1..1 na largura; v: 0 na base .. 1 no apice. Ogiva equilatera em (u, v*sqrt3).
        u = (xs - cx) / a
        v = (base - ys) / max(base - top, 1e-3)
        vv = v * math.sqrt(3.0)
        return ((u + 1) ** 2 + vv ** 2 <= 4.0) & ((u - 1) ** 2 + vv ** 2 <= 4.0) & (v >= 0)

    outer = ogive(w / 2.0 - 0.5, 0.0)
    inner = ogive(w / 2.0 - 3.5, 3.0)
    m = outer & ~inner
    m |= (ys >= base) & (ys <= h - 1) & (np.abs(xs - cx) <= w / 2.0 - 0.5)   # soleira
    tre = np.zeros_like(m)
    for (dx, dy) in ((0, -3.6), (-3.0, -0.8), (3.0, -0.8)):
        tre |= np.sqrt((xs - cx - dx) ** 2 + (ys - (base - 4) - dy) ** 2) <= 1.9
    ring = dilate(tre, 4) & ~tre & inner
    m |= ring
    c = Canvas(w, h)
    bevel(c, m, **iron_ramp())
    c.fill_mask(tre & inner, PAL["spirit:3"])
    c.fill_mask(tre & inner & (ys < base - 6), PAL["spirit:4"])
    return c


def rune_seal(d: int = 15) -> Canvas:
    xs, ys = grid(d, d)
    r = (d - 1) / 2.0
    disc = (xs - r - 0.5) ** 2 + (ys - r - 0.5) ** 2 <= (r - 0.2) ** 2
    c = Canvas(d, d)
    bevel(c, disc, **iron_ramp())
    inner = disc & ~dilate(~disc, 4) & ~dilate(dilate(~disc, 4), 4)
    c.fill_mask(inner, PAL["slate:2"])
    g = text_mask("‡")
    oy, ox = (d - 7) // 2, (d - 5) // 2
    gm = np.zeros((d, d), dtype=bool)
    gm[oy:oy + 7, ox:ox + 5] = g
    c.fill_mask(gm, PAL["spirit:4"])
    c.fill_mask(gm & (ys < d / 2), PAL["spirit:5"])
    return c


def thorn_filigree(h: int = 64, side: str = "l") -> Canvas:
    """Filigrana espinhosa DUPLA: dois cipos entrelacados com espinhos para fora."""
    w = 9
    m = np.zeros((h, w), dtype=bool)
    thorns = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for ph in (0.0, math.pi):
            x = int(round(4 + 2.2 * math.sin(y / 5.0 + ph)))
            m[y, x] = True
            if 0 <= x + 1 < w and ph == 0.0:
                m[y, x + 1] = True
        if y % 8 == 3:
            x = int(round(4 + 2.2 * math.sin(y / 5.0)))
            for k in range(1, 3):
                xx = x - k - 1
                if 0 <= xx < w:
                    thorns[y - k + 1, xx] = True
    m |= thorns
    c = Canvas(w, h)
    bevel(c, m, **violet_ramp())
    # espinhos: cluster de 2 px com o tom claro da rampa (nao pixel solto de cor unica)
    c.fill_mask(thorns & dilate(thorns, 4) & (np.roll(thorns, 1, axis=1) | np.roll(thorns, -1, axis=1) |
                                               np.roll(thorns, 1, axis=0) | np.roll(thorns, -1, axis=0)), PAL["violet:4"])
    if side == "r":
        return c.flip_x()
    return c


def triple_crown(w: int = 33, h: int = 19) -> Canvas:
    m = shape_mask(w, h, f_crown, w / 2.0, h / 2.0 + 1, w / 2.0 - 1.5, h / 2.0 - 1)
    c = Canvas(w, h)
    bevel(c, m, **gold_ramp())
    # gemas na faixa: rubi, ametista, rubi
    by = int(h * 0.72)
    for gx, col in ((w // 2 - 8, PAL["blood:4"]), (w // 2, PAL["violet:4"]), (w // 2 + 8, PAL["blood:4"])):
        c.put(gx, by, col)
        c.put(gx + 1, by, col)
        c.put(gx, by - 1, mix(col, WHITE, 0.4))
    return c


def relic_frame(w: int = 72, h: int = 104) -> Canvas:
    """Moldura viva +5: banda de gengiva (rosa-sangue) com dentes de osso apontando para dentro."""
    c = Canvas(w, h)
    xs, ys = grid(w, h)
    band = np.zeros((h, w), dtype=bool)
    band[:, :] = True
    band[4:h - 4, 4:w - 4] = False
    gum = PAL.ramp("rose").colors
    blood = PAL.ramp("blood").colors
    bevel(c, band, outline=PAL["void:0"], dark=blood[2], mid=gum[2], light=gum[3], hi=gum[4])
    # veias
    for y in range(6, h - 6, 9):           # veias: tracos curtos de 2 px (cluster, nao ponto)
        c.put(1, y, blood[3]); c.put(1, y + 1, blood[3])
        c.put(w - 2, y + 4, blood[3]); c.put(w - 2, y + 5, blood[3])
    # dentes (2x3) ao longo da borda interna
    b = bone_ramp()
    # dentes em clusters de 2 px por tom (claro na raiz, medio no meio, ponta escura)
    for x in range(7, w - 7, 5):
        for (yy, dy) in ((4, 1), (h - 5, -1)):
            for xx in (x, x + 1):
                c.put(xx, yy, b["light"])
                c.put(xx, yy + dy, b["mid"])
            c.put(x, yy + 2 * dy, b["dark"])
    for y in range(9, h - 9, 6):
        for (xx, dx) in ((4, 1), (w - 5, -1)):
            for yv in (y, y + 1):
                c.put(xx, yv, b["light"])
                c.put(xx + dx, yv, b["mid"])
            c.put(xx + 2 * dx, y, b["dark"])
    # nos de osso nos cantos
    for (x, y) in ((0, 0), (w - 6, 0), (0, h - 6), (w - 6, h - 6)):
        knob = np.zeros((6, 6), dtype=bool)
        yy, xx = np.mgrid[0:6, 0:6]
        knob[(xx - 2.5) ** 2 + (yy - 2.5) ** 2 <= 7.5] = True
        k = Canvas(6, 6)
        bevel(k, knob, **b)
        c.blit(k, x, y)
    return c


def ember_frames() -> List[Canvas]:
    E = PAL.ramp("ember").colors
    out = []
    for k in range(3):
        c = Canvas(3, 3)
        if k == 0:
            c.put(1, 0, E[4]); c.put(0, 1, E[4]); c.put(2, 1, E[4]); c.put(1, 2, E[4]); c.put(1, 1, E[6])
        elif k == 1:
            c.put(1, 1, E[5]); c.put(1, 2, E[3])
        else:
            c.put(1, 1, E[2])
        out.append(c)
    return out


def glyph_sprite(ch: str, col) -> Canvas:
    g = text_mask(ch)
    c = Canvas(5, 7)
    c.fill_mask(g, col)
    return c


def foil_tile(n: int = 32) -> Canvas:
    """Foil holografico ESCURO: faixas diagonais violeta/ciano/ambar/rosa em valor baixo,
    transicao em xadrez (dither 50%). Periodo divide 32 -> tile perfeito."""
    cols = [PAL["violet:2"], PAL["spirit:1"], PAL["gold:1"], PAL["rose:1"]]
    c = Canvas(n, n)
    for y in range(n):
        for x in range(n):
            t = ((x + y) % n) / n * len(cols)
            i = int(t)
            frac = t - i
            j = (i + 1) % len(cols)
            use_next = frac > 0.75 or (frac > 0.5 and (x + y) % 2 == 0)
            c.put(x, y, cols[j] if use_next else cols[i])
    return c


# ------------------------------------------------------------------ mascaras (modo A)
def shape_layers(shape: str, size: int = 64) -> Tuple[Canvas, Canvas, Canvas]:
    """Camadas brancas para tingir no Roblox: fill, shade (hachura da sombra), ink (contorno)."""
    m = shape_mask(size, size, SHAPES[shape], size / 2, size / 2, size / 2 - 3, size / 2 - 3)
    fill = Canvas(size, size); fill.fill_mask(m, WHITE)
    lam = light_intensity(m, profile="dome", depth=2.2)
    idx = clean_index_map(bands(lam, m, 3, bias=0.06))
    yy, xx = np.mgrid[0:size, 0:size]
    shadow = (idx == 0)
    shade = Canvas(size, size)
    shade.fill_mask(shadow & ((xx - yy) % 3 != 0), WHITE)
    ink = Canvas(size, size); ink.fill_mask(dilate(m, 4) & ~m, WHITE)
    return fill, shade, ink


def etching_white(pattern: str, size: int = 64) -> Canvas:
    c = Canvas(size, size)
    c.fill_mask(etching(pattern, "ATLAS", size), WHITE)
    return c


# ------------------------------------------------------------------ empacotamento
def pack(items: Dict[str, Canvas], width: int = 256, pad: int = 1) -> Tuple[Image.Image, Dict[str, Tuple[int, int, int, int]]]:
    """Empacotador por prateleiras (shelf) com padding transparente."""
    order = sorted(items.items(), key=lambda kv: -kv[1].h)
    x = y = 0
    shelf = 0
    rects: Dict[str, Tuple[int, int, int, int]] = {}
    placed = []
    for name, c in order:
        if x + c.w + pad * 2 > width:
            x = 0
            y += shelf
            shelf = 0
        rects[name] = (x + pad, y + pad, c.w, c.h)
        placed.append((name, c, x + pad, y + pad))
        x += c.w + pad * 2
        shelf = max(shelf, c.h + pad * 2)
    H = y + shelf
    H2 = 1
    while H2 < H:
        H2 *= 2
    img = Image.new("RGBA", (width, H2), (0, 0, 0, 0))
    for name, c, px, py in placed:
        img.alpha_composite(c.to_image(), (px, py))
    return img, rects


def emit_rects_luau(module: str, image_note: str, rects: Dict[str, Tuple[int, int, int, int]],
                    extra: str = "") -> str:
    L = [
        "--!strict",
        "--[[",
        f"\t{module}.luau  (GERADO por pipeline/dark_altar/build_forge.py - nao edite a mao)",
        "\tColoque em: ReplicatedStorage > Shared > Config",
        f"\t{image_note}",
        "\tUse sempre com ResampleMode = Enum.ResamplerMode.Pixelated e tamanho = multiplo inteiro do sprite.",
        "]]",
        "",
        "export type Sprite = { offset: Vector2, size: Vector2 }",
        "",
        f"local {module} = {{}}",
        "",
        f'{module}.IMAGE = "rbxassetid://0" -- troque pelo ID apos o upload',
        "",
        "local SPRITES: { [string]: Sprite } = {",
    ]
    for name in sorted(rects):
        x, y, w, h = rects[name]
        L.append(f"\t{name} = {{ offset = Vector2.new({x}, {y}), size = Vector2.new({w}, {h}) }},")
    L += [
        "}",
        "",
        f"function {module}.get(name: string): Sprite?",
        "\treturn SPRITES[name]",
        "end",
        "",
        "-- Aplica o sprite num ImageLabel. scale = fator inteiro (pixel art nunca usa escala fracionada).",
        f"function {module}.apply(label: ImageLabel, name: string, scale: number): boolean",
        "\tlocal sprite = SPRITES[name]",
        "\tif sprite == nil then",
        f'\t\twarn(`[{module}] sprite inexistente: {{name}}`)',
        "\t\treturn false",
        "\tend",
        "\tlocal k = math.max(1, math.floor(scale))",
        f"\tlabel.Image = {module}.IMAGE",
        "\tlabel.ResampleMode = Enum.ResamplerMode.Pixelated",
        "\tlabel.ImageRectOffset = sprite.offset",
        "\tlabel.ImageRectSize = sprite.size",
        "\tlabel.Size = UDim2.fromOffset(sprite.size.X * k, sprite.size.Y * k)",
        "\treturn true",
        "end",
        extra,
        f"return table.freeze({module})",
        "",
    ]
    return "\n".join(L)


# ------------------------------------------------------------------ mockup da carta
CARD_W, CARD_H = 72, 104


def card_mock(level: int, art: Canvas, ornaments: Dict[str, Canvas], pillar: Canvas, foil: Canvas) -> Canvas:
    M = Canvas(CARD_W + 28, CARD_H + 36, (14, 11, 20, 255))
    ox, oy = 14, 22
    if level >= 5:  # coluna de luz atras da carta
        col = pillar
        for k in range(0, M.h, col.h):
            pass
        big = Canvas(col.w, M.h)
        for yy in range(M.h):
            src = int(yy / M.h * col.h)
            big.px[yy] = col.px[src]
        big_scaled = Canvas(col.w * 2, M.h)
        big_scaled.px = np.repeat(big.px, 2, axis=1)
        M.blit(big_scaled, (M.w - big_scaled.w) // 2, 0)
    card = Canvas(CARD_W, CARD_H, SLATE)
    card.blit(art, 4, 14)
    if level >= 4:  # foil holografico escuro sobre a arte
        tile = Canvas(64, 64)
        for ty in range(0, 64, foil.h):
            for tx in range(0, 64, foil.w):
                tile.blit(foil, tx, ty)
        card.blend_over(tile, 4, 14, 0.28)
    # titulo, custo e tag
    tm = text_mask("GOLPE")
    t = Canvas(tm.shape[1], 7); t.fill_mask(tm, PAL["bone:4"])
    card.blit(t, (CARD_W - tm.shape[1]) // 2, 4)
    gem = text_mask("◆"); g = Canvas(5, 7); g.fill_mask(gem, PAL["gold:4"]); card.blit(g, 4, 4)
    tag = text_mask("[ATQ]"); tg = Canvas(tag.shape[1], 7); tg.fill_mask(tag, PAL["ember:4"])
    card.blit(tg, 5, 84)
    num = text_mask("6"); n = Canvas(5, 7); n.fill_mask(num, PAL["bone:5"]); card.blit(n, CARD_W - 11, 84)
    # bordas por nivel
    border = {0: IRON, 1: CYAN, 2: CYAN, 3: VIOLET, 4: AMBER, 5: PAL["blood:3"]}[level]
    thick = 1 if level == 0 else 2
    card.rect_outline(0, 0, CARD_W, CARD_H, border, thick)
    if level == 3:  # gradiente violeta girando (instantaneo): trecho mais claro
        for x in range(CARD_W // 2, CARD_W):
            card.put(x, 0, PAL["violet:6"]); card.put(x, 1, PAL["violet:5"])
        for y in range(0, CARD_H // 3):
            card.put(CARD_W - 1, y, PAL["violet:6"]); card.put(CARD_W - 2, y, PAL["violet:5"])
    if level == 2:  # varredura de reflexo metalico (sheen) num instante
        for y in range(CARD_H):
            for x in range(CARD_W):
                if abs((x + y) - 70) <= 2 and card.get(x, y)[3]:
                    r, gg, b, _ = card.get(x, y)
                    card.put(x, y, mix((r, gg, b), WHITE, 0.35))
    if level >= 5:
        card.blit(ornaments["relic_frame"], 0, 0)
    M.blit(card, ox, oy)
    if level >= 1:
        M.blit(ornaments["corner_tl"], ox - 2, oy - 2)
        M.blit(ornaments["corner_tr"], ox + CARD_W - 11, oy - 2)
        M.blit(ornaments["corner_bl"], ox - 2, oy + CARD_H - 11)
        M.blit(ornaments["corner_br"], ox + CARD_W - 11, oy + CARD_H - 11)
    if level >= 2:
        a = ornaments["arch_top"]
        M.blit(a, ox + (CARD_W - a.w) // 2, oy - a.h + 4)
        s = ornaments["rune_seal"]
        M.blit(s, ox + (CARD_W - s.w) // 2, oy + CARD_H - s.h // 2 - 1)
    if level >= 3:
        fl, fr = ornaments["filigree_l"], ornaments["filigree_r"]
        M.blit(fl, ox - fl.w + 3, oy + 20)
        M.blit(fr, ox + CARD_W - 3, oy + 20)
        for k, (ch, ang) in enumerate((("◆", 200), ("†", 330), ("◇", 80))):
            gx = int(ox + CARD_W / 2 + math.cos(math.radians(ang)) * (CARD_W * 0.62)) - 2
            gy = int(oy + CARD_H / 2 + math.sin(math.radians(ang)) * (CARD_H * 0.56)) - 3
            M.blit(glyph_sprite(ch, PAL["violet:5"]), gx, gy)
    if level >= 4:
        cr = ornaments["crown_triple"]
        M.blit(cr, ox + (CARD_W - cr.w) // 2, oy - cr.h - 8)
        for k, (ex, ey) in enumerate(((10, 40), (60, 22), (34, 8), (66, 70), (4, 80))):
            M.blit(ornaments[f"ember_{k % 3}"], ox + ex, oy + ey)
    return M


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    orn: Dict[str, Canvas] = {
        "border_1px": border_mask(1).canvas,
        "border_2px": border_mask(2).canvas,
        "corner_tl": corner("tl"), "corner_tr": corner("tr"),
        "corner_bl": corner("bl"), "corner_br": corner("br"),
        "arch_top": ogival_arch(),
        "rune_seal": rune_seal(),
        "filigree_l": thorn_filigree(64, "l"), "filigree_r": thorn_filigree(64, "r"),
        "crown_triple": triple_crown(),
        "relic_frame": relic_frame(),
        "foil_tile": foil_tile(),
        "glyph_diamond": glyph_sprite("◆", WHITE),
        "glyph_dagger": glyph_sprite("†", WHITE),
        "glyph_hollow": glyph_sprite("◇", WHITE),
    }
    for i, e in enumerate(ember_frames()):
        orn[f"ember_{i}"] = e
    # paleta fechada: tudo que nao e mascara branca volta para a paleta ALTAR
    for k, cv in orn.items():
        if not (k.startswith("border_") or k.startswith("glyph_")):
            cv.px = PAL.quantize(cv.px)
    img, rects = pack(orn, width=256)
    img.save(OUT / "ForgeOrnamentAtlas.png")
    extra = "\n-- SliceCenter das mascaras de borda (ScaleType = Slice, SliceScale = fator inteiro)\n" \
            f"{'ForgeOrnamentAtlas'}.SLICE_1PX = Rect.new(3, 3, 9, 9)\n" \
            f"{'ForgeOrnamentAtlas'}.SLICE_2PX = Rect.new(4, 4, 8, 8)\n"
    LUAU.write_text(emit_rects_luau("ForgeOrnamentAtlas", "Atlas: art/dark-altar/forge/ForgeOrnamentAtlas.png", rects, extra),
                    encoding="utf-8")

    # mascaras de forma (6 x 3 camadas) e gravuras (8)
    sm = Image.new("RGBA", (64 * 6, 64 * 3), (0, 0, 0, 0))
    for i, shp in enumerate(data.SHAPES):
        for j, layer in enumerate(shape_layers(shp)):
            sm.alpha_composite(layer.to_image(), (i * 64, j * 64))
    sm.save(OUT / "ShapeMaskAtlas.png")
    ea = Image.new("RGBA", (64 * 8, 64), (0, 0, 0, 0))
    for i, pat in enumerate(data.PATTERNS):
        ea.alpha_composite(etching_white(pat).to_image(), (i * 64, 0))
    ea.save(OUT / "EtchingAtlas.png")

    # mockups +0..+5 com a arte 'Fogo'
    subs = data.all_subtypes()
    fam_bg = {f.key: f.bg_base for f in data.FAMILIES}
    st = next(s for s in subs if s.sid == "Fogo")
    st.bg, st.accent, _ = derive_colors(fam_bg[st.family], st.accent)
    art = render(st)
    pillar = holy_pillar(PAL, w=24, h=64).frames[2]
    mocks = [card_mock(lv, art, orn, pillar, orn["foil_tile"]) for lv in range(6)]
    k = 3
    W = sum(m.w * k + 8 for m in mocks) + 8
    H = mocks[0].h * k + 30
    sheet = Image.new("RGBA", (W, H), (10, 8, 14, 255))
    d = ImageDraw.Draw(sheet)
    labels = ["+0 Comum", "+1 Incomum", "+2 Raro", "+3 Epico", "+4 Mitico", "+5 Reliquia (Sangue)"]
    x = 8
    for m, lab in zip(mocks, labels):
        sheet.paste(m.to_image().resize((m.w * k, m.h * k), Image.NEAREST), (x, 24))
        d.text((x + 4, 6), lab, fill=(225, 218, 235, 255))
        x += m.w * k + 8
    sheet.save(OUT / "mock_forge_levels.png")
    prev = Image.new("RGBA", (img.width * 3, img.height * 3), (24, 20, 30, 255))
    prev.alpha_composite(img.resize((img.width * 3, img.height * 3), Image.NEAREST))
    prev.save(OUT / "preview_ornaments_x3.png")
    print("ok:", ", ".join(sorted(rects)))
    print("atlas", img.size, "->", LUAU.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
