"""Elementos de UI em pixel art: paineis 9-slice, mascaras de borda e estados de botao.

Regras (references/03-ui-icones-telas.md):
- 9-slice: cantos fixos, bordas e centro esticam -> SliceCenter = Rect(c, c, w-c, h-c).
  No Roblox: ScaleType = Slice, SliceCenter = Rect.new(...), SliceScale = inteiro (2, 3).
- Mascara de borda BRANCA + ImageColor3 permite trocar a cor por codigo e aplicar
  UIGradient (ex.: borda violeta girando) sem gerar uma imagem por cor.
- Botao: Normal / Hover / Pressed / Disabled com o MESMO tamanho; Pressed desce 1px
  e inverte o bevel; Disabled perde croma e contraste.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .canvas import Canvas
from .color import RGB, mix
from .palette import Palette


@dataclass
class NineSlice:
    canvas: Canvas
    center: Tuple[int, int, int, int]  # x0, y0, x1, y1 para Rect.new

    def luau_rect(self) -> str:
        return "Rect.new({}, {}, {}, {})".format(*self.center)


def border_mask(thickness: int = 1, size: int = 12, color: RGB = (255, 255, 255)) -> NineSlice:
    """Borda branca de N px para tingir no Roblox (ImageColor3) e/ou aplicar UIGradient."""
    c = Canvas(size, size)
    c.rect_outline(0, 0, size, size, color, thickness)
    k = thickness + 2
    return NineSlice(c, (k, k, size - k, size - k))


def panel(pal: Palette, w: int = 24, h: int = 24, face: str = "slate:1", rim: str = "slate:2",
          light: str = "slate:4", shadow: str = "slate:0", corner: int = 6, rivets: bool = True) -> NineSlice:
    """Painel gotico: aro de ferro com bevel (luz topo-esquerda), face escura, rebites nos cantos."""
    c = Canvas(w, h, pal[face])
    c.rect_outline(0, 0, w, h, pal[shadow], 1)                 # contorno externo
    c.fill_rect(1, 1, w - 2, 1, pal[light])                    # bevel claro (topo)
    c.fill_rect(1, 1, 1, h - 2, pal[light])                    # bevel claro (esquerda)
    c.fill_rect(1, h - 2, w - 2, 1, pal[rim])                  # bevel escuro (base)
    c.fill_rect(w - 2, 1, 1, h - 2, pal[rim])                  # bevel escuro (direita)
    c.rect_outline(2, 2, w - 4, h - 4, pal[shadow], 1)         # sulco interno
    if rivets:
        for (x, y) in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
            c.put(x, y, pal[light])
            c.put(x + 1, y, pal[rim])
            c.put(x, y + 1, pal[rim])
            c.put(x + 1, y + 1, pal[shadow])
    return NineSlice(c, (corner, corner, w - corner, h - corner))


def button_states(pal: Palette, w: int = 40, h: int = 14, accent: str = "blood") -> Dict[str, Canvas]:
    """Quatro estados do mesmo botao (mesmo tamanho -> troca de Image sem pulo de layout)."""
    A = pal.ramp(accent).colors
    out: Dict[str, Canvas] = {}

    def make(face: RGB, top: RGB, bottom: RGB, edge: RGB, pressed: bool) -> Canvas:
        c = Canvas(w, h)
        oy = 1 if pressed else 0
        body_h = h - 1
        c.fill_rect(0, 1, w, body_h, edge)                      # sombra/base
        c.fill_rect(1, oy, w - 2, body_h - 1, face)
        c.rect_outline(0, oy, w, body_h, edge, 1)
        if not pressed:
            c.fill_rect(1, oy + 1, w - 2, 1, top)
            c.fill_rect(1, oy + body_h - 2, w - 2, 1, bottom)
        else:
            c.fill_rect(1, oy + 1, w - 2, 1, bottom)            # bevel invertido
        return c

    out["normal"] = make(A[2], A[4], A[1], pal["void:0"], False)
    out["hover"] = make(A[3], A[5], A[2], pal["void:0"], False)
    out["pressed"] = make(A[2], A[4], A[1], pal["void:0"], True)
    grey = pal.ramp("slate").colors
    out["disabled"] = make(grey[2], grey[3], grey[1], pal["void:0"], False)
    return out
