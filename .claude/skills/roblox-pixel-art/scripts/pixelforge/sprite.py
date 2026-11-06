"""Sprites desenhados a mao (texto) + sombreamento automatico por material.

Por que: formas organicas (estatuas, criaturas, rostos, props com personalidade)
feitas so por geometria ficam esquematicas. O artista (humano ou IA) DESENHA a
silhueta e as regioes de material em texto; o motor faz o trabalho repetitivo e
dificil de acertar a mao: rampa hue-shifted, luz consistente (topo-esquerda),
vincos entre materiais, sel-out, rim light e oclusao no contato com o chao.

Formato (uma string por linha, mesma largura):
    '.'            transparente
    letra minuscula material sombreado automaticamente (definido em `materials`)
    letra MAIUSCULA mesmo material, forcado para o tom de brilho (especular)
    outro caractere cor fixa definida em `fixed` (olhos, gemas, runas, frestas)

Exemplo:
    rows = ["..ii..", ".iIii.", "iiiiii", ".wwww."]
    sprite = render_sprite(rows, {"i": Material("slate"), "w": Material("earth")}, pal)

Dica de desenho: escreva a metade esquerda e use mirror_rows() para simetria.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from .canvas import Canvas
from .color import RGB
from .palette import Palette
from .raster import N4, edge_inner, edge_outer, shift
from .shade import LIGHT_TOP_LEFT, _norm, bands, clean_index_map, height_field


@dataclass
class Material:
    ramp: str                    # nome da rampa na paleta
    lo: int = 1                  # degrau mais escuro usado no sombreamento
    hi: Optional[int] = None     # degrau mais claro (None = penultimo)
    depth: float = 2.6           # 'altura' do volume (mais = mais contraste de forma)
    bias: float = 0.0            # empurra para claro (+) ou escuro (-)
    crease: bool = True          # vinco escuro na fronteira com outro material
    local: float = 0.45          # peso do volume da propria regiao vs. silhueta inteira


Fixed = Union[str, RGB]          # "ramp:idx" ou RGB


@dataclass
class SpriteSpec:
    rows: List[str]
    materials: Dict[str, Material]
    fixed: Dict[str, Fixed] = field(default_factory=dict)


def mirror_rows(left: Sequence[str], odd_center: bool = False) -> List[str]:
    """Completa a metade direita espelhando a esquerda (simetria de estatuas, escudos, coroas)."""
    out = []
    for r in left:
        right = r[::-1]
        out.append(r + (right[1:] if odd_center else right))
    return out


def parse(rows: Sequence[str]) -> np.ndarray:
    w = max(len(r) for r in rows)
    grid = np.full((len(rows), w), ".", dtype="<U1")
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            grid[y, x] = ch
    return grid


def _resolve(pal: Palette, c: Fixed) -> RGB:
    if isinstance(c, str):
        return pal[c]
    return c


def render_sprite(rows: Sequence[str], materials: Dict[str, Material], pal: Palette,
                  fixed: Optional[Dict[str, Fixed]] = None, light=LIGHT_TOP_LEFT,
                  outline: Optional[str] = "selout", outline_color: Optional[Fixed] = None,
                  rim: Optional[Tuple[Fixed, Tuple[float, float]]] = None,
                  contact_ao: int = 2) -> Canvas:
    """Renderiza o sprite.

    outline: None | "selout" (borda interna derivada da cor) | "outer" (contorno externo
             na cor outline_color, padrao void:0) | "both".
    rim: (cor, (dx, dy)) luz de recorte vinda da direcao (dx, dy) - ex.: fogo a esquerda (-1, 0).
    contact_ao: linhas no pe do sprite que escurecem 1 degrau (oclusao no contato com o chao).
    """
    fixed = fixed or {}
    g = parse(rows)
    h, w = g.shape
    c = Canvas(w, h)
    union = g != "."
    hg = height_field(union, "dome")
    lx, ly, lz = _norm(light)

    region_masks: Dict[str, np.ndarray] = {}
    for key in materials:
        m = (g == key) | (g == key.upper())
        if m.any():
            region_masks[key] = m

    for key, m in region_masks.items():
        mat = materials[key]
        ramp = pal.ramp(mat.ramp).colors
        hi = len(ramp) - 2 if mat.hi is None else mat.hi
        n = max(1, hi - mat.lo + 1)
        hr = height_field(m, "dome")
        hh = (1 - mat.local) * hg + mat.local * hr
        gy, gx = np.gradient(hh * mat.depth)
        nx, ny, nz = -gx, -gy, np.ones_like(hh)
        ln = np.sqrt(nx * nx + ny * ny + nz * nz)
        lam = np.clip((nx * lx + ny * ly + nz * lz) / ln, 0, 1)
        idx = bands(np.where(m, lam, 0), m, n, mat.bias)
        idx = clean_index_map(idx)
        for i in range(n):
            mm = idx == i
            if mm.any():
                c.fill_mask(mm, ramp[min(len(ramp) - 1, mat.lo + i)])
        hl = g == key.upper()
        if hl.any():
            c.fill_mask(hl, ramp[min(len(ramp) - 1, hi + 1)])

    # vincos: pixel cujo vizinho de OUTRO material esta a esquerda/acima fica 1 degrau mais
    # escuro (linha de 1 px no lado da sombra da juncao)
    src = c.px.copy()
    fixed_mask = np.isin(g, list(fixed.keys())) if fixed else np.zeros_like(union)
    for key, m in region_masks.items():
        if not materials[key].crease:
            continue
        other = union & ~m & ~fixed_mask           # linha fixa ja e linha: nao gera vinco
        touch = np.zeros_like(m)
        for dx, dy in ((-1, 0), (0, -1)):
            touch |= shift(other, -dx, -dy)
        from .raster import thin_elbows
        crease = thin_elbows(m & touch)              # vinco pixel-perfect
        ys, xs = np.where(crease)
        for y, x in zip(ys, xs):
            col = tuple(int(v) for v in src[y, x, :3])
            c.put(x, y, pal.shift(col, -1))

    for ch, col in fixed.items():
        fm = g == ch
        if fm.any():
            c.fill_mask(fm, _resolve(pal, col))

    # oclusao no contato com o chao
    if contact_ao > 0:
        rows_any = np.where(union.any(axis=1))[0]
        if len(rows_any):
            bottom = rows_any.max()
            ao = union & (np.arange(h)[:, None] > bottom - contact_ao)
            ys, xs = np.where(ao)
            px = c.px.copy()
            for y, x in zip(ys, xs):
                col = tuple(int(v) for v in px[y, x, :3])
                c.put(x, y, pal.shift(col, -1))

    # rim light (antes do sel-out para a borda iluminada ganhar a cor da fonte)
    if rim is not None:
        rcol, (dx, dy) = rim
        rc = _resolve(pal, rcol)
        e = edge_inner(union, 4)
        facing = np.zeros_like(union)
        sx = -1 if dx < 0 else (1 if dx > 0 else 0)
        sy = -1 if dy < 0 else (1 if dy > 0 else 0)
        if sx:
            facing |= ~shift(union, -sx, 0)
        if sy:
            facing |= ~shift(union, 0, -sy)
        c.fill_mask(e & facing, rc)

    if outline in ("selout", "both"):
        from .raster import thin_elbows
        e = thin_elbows(edge_inner(union, 4))        # sel-out pixel-perfect
        ys, xs = np.where(e)
        px = c.px.copy()
        rim_mask = None
        if rim is not None:
            rim_mask = (px[..., :3] == np.array(_resolve(pal, rim[0]))).all(axis=-1)
        for y, x in zip(ys, xs):
            if rim_mask is not None and rim_mask[y, x]:
                continue
            if g[y, x] in fixed:
                continue
            ox = oy = 0
            for ddx, ddy in N4:
                xx, yy = x + ddx, y + ddy
                if not (0 <= xx < w and 0 <= yy < h) or not union[yy, xx]:
                    ox += ddx
                    oy += ddy
            lit = (ox * lx + oy * ly) > 0.2
            col = tuple(int(v) for v in px[y, x, :3])
            c.put(x, y, pal.shift(col, -1 if lit else -2))
    if outline in ("outer", "both"):
        oc = _resolve(pal, outline_color or "void:0")
        pad = Canvas(w + 2, h + 2)
        pad.blit(c, 1, 1)
        m2 = pad.alpha_mask()
        from .raster import thin_elbows
        pad.fill_mask(thin_elbows(edge_outer(m2, 4)), oc)   # contorno pixel-perfect
        return pad
    return c


def render_spec(spec: SpriteSpec, pal: Palette, **kw) -> Canvas:
    return render_sprite(spec.rows, spec.materials, pal, spec.fixed, **kw)
