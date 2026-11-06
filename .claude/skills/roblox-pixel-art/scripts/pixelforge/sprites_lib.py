"""Biblioteca de sprites desenhados a mao (formato de texto do modulo sprite.py).

Cada sprite tem:
  - rows: o desenho (silhueta + regioes de material)
  - materials: material de cada letra (rampa da paleta + parametros de volume)
  - fixed: cores fixas (frestas, olhos, gemas)
Para ver um sprite: python -m pixelforge sprite NOME --out out/sprite.png
"""
from __future__ import annotations

import math
from typing import Dict, List

from .sprite import Material, SpriteSpec, mirror_rows

# ------------------------------------------------------------------ anjo de pedra
# Metade esquerda desenhada a mao (20 colunas); a direita e espelhada.
# w/v = penas em faixas alternadas (o vinco entre materiais desenha cada pena)
# h = capuz/cabeca, f = sombra do rosto (fixa), s = manto, a = maos, A = brilho nas maos
_ANGEL_TOP = [
    "......w.............",
    ".....ww.............",
    ".....www............",
    "....wwww............",
    "....wwwww...........",
    "...wwwwwww..........",
    "...wwwwwwww.........",
    "..wwwwwwwwkw........",
    "..wwwwwwwkwww.......",
    "..wwwwwwkwwwww......",
    ".wwwwwwkwwwwwkw.....",
    ".wwwwwkwwwwwkwww....",
    ".wwwwkwwwwwkwwwww...",
    ".wwwkwwwwwkwwwwkw...",
    "wwwkwwwwwkwwwwkww..h",
    "wwkwwwwwkwwwwkwww.hh",
    "wkwwwwwkwwwwkwww.hhh",
    "wwwwwwkwwwwkwww.hhhh",
    "kwwwwkwwwwkwww..hhhf",
    ".wwwkwwwwkwww...hhff",
    ".wwkwwwwkww....shhhh",
    "..kwwwwkww....sshhhh",
    "..wwwwkw.....sssshhh",
    "...wwkw.....ssssssss",
    "...wkw.....sssssssss",
    "....w.....ssssssssss",
    ".........sssssssssss",
    ".........ssssssssaaa",
    "........ssssssssaaaa",
    "........sssssssssaaA",
    "........ssssssssssaa",
]


def _angel_robe(start_row: int = 31, end_row: int = 50) -> List[str]:
    rows = []
    for r in range(start_row, end_row + 1):
        t = (r - start_row) / (end_row - start_row)
        left = int(round(8 - 4.5 * t))            # manto alarga para baixo
        row = ["."] * 20
        for x in range(left, 20):
            row[x] = "s"
        fold1 = left + 3 + int(t * 2)
        fold2 = 15 - int(t * 2)
        for fx in (fold1, fold2):
            if left < fx < 19:
                row[fx] = "k"
        rows.append("".join(row))
    return rows


def _angel_plinth() -> List[str]:
    rows = []
    rows.append("..cccccccccccccccccc")
    rows.append("..cccccccccccccccccc")
    for i in range(8):
        row = list("....pppppppppppppppp")
        if 1 <= i <= 6:
            row[7] = "k"
            if i in (1, 6):
                for x in range(7, 20):
                    row[x] = "k"
        rows.append("".join(row))
    rows.append("..cccccccccccccccccc")
    rows.append("..pppppppppppppppppp")
    return rows


def _feathered(rows: List[str], band: int = 3) -> List[str]:
    """Reorganiza a regiao da asa (w/v) em FAIXAS de pena coerentes (band px de largura,
    na diagonal do ombro para a ponta). Alternar material a cada pixel vira ruido."""
    out = []
    for y, r in enumerate(rows):
        row = list(r)
        for x, ch in enumerate(row):
            if ch in "wv":
                k = (x * 2 + y) // (band * 2)
                row[x] = "w" if k % 2 == 0 else "v"
        out.append("".join(row))
    return out


def _angel_face(rows: List[str]) -> List[str]:
    """Rosto sob o capuz: sombra so de 2 px de altura + queixo claro (le como cabeca inclinada)."""
    out = [list(r) for r in rows]
    for y, r in enumerate(out):
        for x, ch in enumerate(r):
            if ch == "f" and y >= 20:
                r[x] = "h"
    return ["".join(r) for r in out]


ANGEL_STATUE = SpriteSpec(
    rows=mirror_rows(_angel_face(_ANGEL_TOP) + _angel_robe() + _angel_plinth()),
    materials={
        # penas finas entre linhas: so 2 tons (luz/sombra). 3+ bandas em faixa de 4 px viram serrilhado
        "w": Material("slate", lo=3, hi=4, depth=2.4, local=0.6),
        "h": Material("slate", lo=2, hi=5, depth=2.8),
        "s": Material("slate", lo=1, hi=5, depth=2.4, local=0.35),
        "a": Material("slate", lo=2, hi=5, depth=2.0, bias=0.08),
        "c": Material("slate", lo=2, hi=5, depth=1.6, local=0.8),
        "p": Material("slate", lo=1, hi=3, depth=1.4, local=0.8),
    },
    fixed={"f": "void:0", "k": "slate:2"},
)

# ------------------------------------------------------------------ bigorna sobre toco
_ANVIL = [
    "..........IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII....",
    "......iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii..",
    "..iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii..",
    "....iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii.",
    ".......iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii.",
    "...........iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii..",
    ".............iiiiiiiiiiiiiiiiiiiiiiiiiiii.....",
    "...............iiiiiiiiiiiiiiiiiiiiiiii.......",
    ".................iiiiiiiiiiiiiiiiiiii.........",
    "..................iiiiiiiiiiiiiiiiii..........",
    "..................iiiiiiiiiiiiiiiiii..........",
    "..................iiiiiiiiiiiiiiiiii..........",
    ".................iiiiiiiiiiiiiiiiiiii.........",
    "...............iiiiiiiiiiiiiiiiiiiiiiii.......",
    ".............iiiiiiiiiiiiiiiiiiiiiiiiiiii.....",
    "............iiiiiiiiiiiiiiiiiiiiiiiiiiiiii....",
    "...........wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww..",
    "...........wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww..",
    "..........wwwwwkwwwwwwwwwwwwwwwwwwwkwwwwwwwww.",
    "..........wwwwwkwwwwwwwwwkwwwwwwwwwkwwwwwwwww.",
    "..........wwwwwkwwwwwwwwwkwwwwwwwwwwwwwwwwwww.",
    "..........wwwwwwwwwwwwwwwkwwwwwwwwwwwwwkwwwww.",
    "..........wwwwwwwwkwwwwwwwwwwwwwwwwwwwwkwwwww.",
    "..........wwwwwwwwkwwwwwwwwwwwwkwwwwwwwwwwwww.",
    "..........wwwwwwwwwwwwwwwwwwwwwkwwwwwwwwwwwww.",
    "...........wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww..",
]

ANVIL = SpriteSpec(
    rows=_ANVIL,
    materials={
        "i": Material("slate", lo=1, hi=5, depth=3.2, local=0.55),
        "w": Material("earth", lo=0, hi=3, depth=2.0, local=0.5),
    },
    fixed={"k": "earth:0"},
)


# ------------------------------------------------------------------ barril
def _barrel_rows(w: int = 22, h: int = 26) -> List[str]:
    rows = []
    for y in range(h):
        t = y / (h - 1)
        half = (w / 2.0 - 2) + 2.0 * math.sin(math.pi * t)
        row = []
        for x in range(w):
            dx = abs(x - (w - 1) / 2.0)
            if dx > half:
                row.append(".")
                continue
            if y in (2, 3, h // 2 - 1, h // 2, h - 4, h - 3):
                row.append("m")                     # aros de ferro
            elif int(round((x - (w - 1) / 2.0) / max(half, 1) * 3 + 3)) % 2 == 0 and dx > 1 and (x + y) % 9 == 0:
                row.append("k")
            else:
                row.append("w")
        rows.append("".join(row))
    # tampo
    top = list(rows[0])
    rows[0] = "".join("t" if ch != "." else "." for ch in top)
    return rows


BARREL = SpriteSpec(
    rows=_barrel_rows(),
    materials={
        "w": Material("earth", lo=1, hi=4, depth=2.6, local=0.3),
        "m": Material("slate", lo=1, hi=4, depth=1.6, local=0.8),
        "t": Material("earth", lo=2, hi=4, depth=1.0),
    },
    fixed={"k": "earth:1"},
)

LIBRARY: Dict[str, SpriteSpec] = {
    "angel_statue": ANGEL_STATUE,
    "anvil": ANVIL,
    "barrel": BARREL,
}
