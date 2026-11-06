"""Paletas e ramps com hue shifting.

Conceitos (ver references/01-fundamentos.md):
- Ramp: escada de tons do escuro ao claro. Aqui ela e gerada em OKLCH com:
    * luz (L) em degraus iguais
    * matiz girando para FRIO nas sombras e para QUENTE nas luzes (hue shifting)
    * croma (saturacao) com pico no meio e caindo nas pontas (curva de saturacao)
- Paleta: conjunto de ramps nomeadas. Toda arte final e quantizada para ela
  (garante paleta fechada = consistencia entre assets).
- shift(cor, +-n): anda n degraus na ramp da cor (base do sel-out, rim light, AO).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .color import (RGB, hex_to_rgb, hue_lerp, oklch_to_rgb, rgb_to_hex,
                    rgb_to_oklch)


# ---------------------------------------------------------------- numpy OKLab
def srgb_to_oklab_np(rgb: np.ndarray) -> np.ndarray:
    """rgb: (...,3) uint8/float 0..255 -> (...,3) OKLab."""
    c = rgb.astype(np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    lms = lin @ M1.T
    lms_ = np.cbrt(lms)
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return lms_ @ M2.T


# ---------------------------------------------------------------- ramp
def make_ramp(anchor: str, steps: int = 6, l_min: float = 0.18, l_max: float = 0.92,
              hue_shift: float = 22.0, cool_hue: float = 285.0, warm_hue: float = 90.0,
              chroma_scale: float = 1.0, chroma_dark: float = 0.6,
              chroma_light: float = 0.45) -> List[RGB]:
    """Gera uma ramp hue-shifted a partir de uma cor ancora.

    hue_shift: giro maximo (graus) aplicado nas pontas. Sombras giram em direcao a
    cool_hue (azul/roxo), luzes em direcao a warm_hue (amarelo). Valores tipicos:
    12-20 (materiais), 25-45 (fogo/magia).
    """
    L0, C0, H0 = rgb_to_oklch(hex_to_rgb(anchor))
    C0 *= chroma_scale
    # posicao relativa da ancora dentro do intervalo de luz
    ta = min(max((L0 - l_min) / max(1e-6, (l_max - l_min)), 0.05), 0.95)
    out: List[RGB] = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0.5
        L = l_min + (l_max - l_min) * t
        if t < ta:  # lado da sombra
            k = (ta - t) / ta
            target = cool_hue
            C = C0 * (1 - (1 - chroma_dark) * k ** 1.2)
        else:  # lado da luz
            k = (t - ta) / (1 - ta)
            target = warm_hue
            C = C0 * (1 - (1 - chroma_light) * k ** 1.4)
        # gira no maximo hue_shift*k graus, sem passar do alvo
        d = ((target - H0 + 540.0) % 360.0) - 180.0
        rot = math.copysign(min(abs(d), hue_shift * k), d)
        H = (H0 + rot) % 360.0
        out.append(oklch_to_rgb(L, C, H))
    # remove duplicatas acidentais (gamut mapping pode colapsar extremos)
    dedup: List[RGB] = []
    for c in out:
        if not dedup or c != dedup[-1]:
            dedup.append(c)
    return dedup


@dataclass
class Ramp:
    name: str
    colors: List[RGB]

    def __len__(self) -> int:
        return len(self.colors)

    def __getitem__(self, i: int) -> RGB:
        i = max(0, min(len(self.colors) - 1, i))
        return self.colors[i]

    def hexes(self) -> List[str]:
        return [rgb_to_hex(c) for c in self.colors]


@dataclass
class Palette:
    name: str
    ramps: Dict[str, Ramp] = field(default_factory=dict)

    # ------------------------------------------------------------ construcao
    def add(self, ramp: Ramp) -> "Palette":
        self.ramps[ramp.name] = ramp
        self._index = None  # invalida cache
        return self

    def pin(self, ramp_name: str, hex_color: str) -> None:
        """Substitui o degrau mais proximo da ramp por uma cor exata (token de design)."""
        from .color import oklab_distance
        r = self.ramps[ramp_name]
        c = hex_to_rgb(hex_color)
        i = min(range(len(r.colors)), key=lambda k: oklab_distance(r.colors[k], c))
        r.colors[i] = c
        self._index = None

    # ------------------------------------------------------------ consulta
    def ramp(self, name: str) -> Ramp:
        return self.ramps[name]

    def __getitem__(self, key: str) -> RGB:
        """Atalho 'ramp:indice' -> cor. Ex.: pal['ember:3']. Indices negativos valem."""
        name, _, idx = key.partition(":")
        r = self.ramps[name]
        i = int(idx) if idx else len(r) // 2
        if i < 0:
            i = len(r) + i
        return r[i]

    def colors(self) -> List[RGB]:
        seen: List[RGB] = []
        for r in self.ramps.values():
            for c in r.colors:
                if c not in seen:
                    seen.append(c)
        return seen

    def _build_index(self) -> Dict[RGB, Tuple[str, int]]:
        idx: Dict[RGB, Tuple[str, int]] = {}
        for r in self.ramps.values():
            for i, c in enumerate(r.colors):
                idx.setdefault(c, (r.name, i))
        return idx

    def locate(self, c: RGB) -> Optional[Tuple[str, int]]:
        if getattr(self, "_index", None) is None:
            self._index = self._build_index()
        return self._index.get(tuple(c[:3]))  # type: ignore[arg-type]

    def shift(self, c: RGB, steps: int) -> RGB:
        """Anda 'steps' degraus na ramp da cor (negativo = mais escuro)."""
        loc = self.locate(c)
        if loc is None:
            c = self.nearest(c)
            loc = self.locate(c)
            if loc is None:
                return c
        name, i = loc
        return self.ramps[name][i + steps]

    def nearest(self, c: RGB) -> RGB:
        pal = np.array(self.colors(), dtype=np.float64)
        lab = srgb_to_oklab_np(pal)
        q = srgb_to_oklab_np(np.array([c[:3]], dtype=np.float64))[0]
        k = int(np.argmin(((lab - q) ** 2).sum(axis=1)))
        return tuple(int(v) for v in pal[k])  # type: ignore[return-value]

    def quantize(self, img: np.ndarray, alpha_threshold: int = 128) -> np.ndarray:
        """Quantiza uma imagem RGBA (H,W,4) para a paleta (OKLab) com alpha duro."""
        out = img.copy()
        a = out[..., 3]
        mask = a >= alpha_threshold
        pal = np.array(self.colors(), dtype=np.float64)
        pal_lab = srgb_to_oklab_np(pal)
        px = out[..., :3][mask].astype(np.float64)
        if len(px):
            lab = srgb_to_oklab_np(px)
            d = ((lab[:, None, :] - pal_lab[None, :, :]) ** 2).sum(axis=2)
            k = np.argmin(d, axis=1)
            out[..., :3][mask] = pal[k].astype(np.uint8)
        out[..., 3] = np.where(mask, 255, 0).astype(np.uint8)
        out[..., :3][~mask] = 0
        return out

    # ------------------------------------------------------------ io
    def to_json(self) -> Dict:
        return {"name": self.name,
                "ramps": {k: r.hexes() for k, r in self.ramps.items()}}

    def save(self, path: Path) -> None:
        Path(path).write_text(json.dumps(self.to_json(), indent=2), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "Palette":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        p = Palette(data["name"])
        for k, hx in data["ramps"].items():
            p.add(Ramp(k, [hex_to_rgb(h) for h in hx]))
        return p


# ---------------------------------------------------------------- paleta mestre
#: Tokens de design obrigatorios (vem da especificacao da Forja). Sao "pinados"
#: nas ramps para que toda arte use exatamente estes valores.
FORGE_TOKENS = {
    "slate_border": "#1E1E24",
    "iron_outline": "#2C2E35",
    "uncommon_cyan": "#4DD0E1",
    "epic_violet": "#B388FF",
    "mythic_amber": "#E5A93C",
}


def altar_palette() -> Palette:
    """Paleta mestre 'ALTAR' (gotico de alto contraste, ~80 cores em 13 ramps).

    Regra de uso: fundos vivem nas ramps void/slate/abyss (valor baixo, pouco croma);
    o croma alto fica reservado para acentos, VFX e pontos focais (vitrais, fogo).
    """
    p = Palette("ALTAR")
    spec: Sequence[Tuple[str, str, dict]] = (
        ("void",   "#2B2140", dict(steps=7, l_min=0.11, l_max=0.55, hue_shift=10)),
        ("slate",  "#3A3B47", dict(steps=9, l_min=0.12, l_max=0.88, hue_shift=16, chroma_scale=1.0)),
        ("bone",   "#B3A07E", dict(steps=6, l_min=0.30, l_max=0.95, hue_shift=14)),
        ("blood",  "#9A2838", dict(steps=7, l_min=0.16, l_max=0.80, hue_shift=18, cool_hue=330, warm_hue=45)),
        ("ember",  "#E0601E", dict(steps=7, l_min=0.30, l_max=0.98, hue_shift=42, cool_hue=15, warm_hue=100,
                                   chroma_dark=0.9, chroma_light=0.35)),
        ("gold",   "#D49A2E", dict(steps=6, l_min=0.30, l_max=0.96, hue_shift=20, cool_hue=40, warm_hue=100)),
        ("violet", "#7A4BC2", dict(steps=7, l_min=0.16, l_max=0.92, hue_shift=20, cool_hue=280, warm_hue=320)),
        ("spirit", "#33A6B8", dict(steps=6, l_min=0.20, l_max=0.96, hue_shift=18, cool_hue=250, warm_hue=170)),
        ("moss",   "#4E8A38", dict(steps=6, l_min=0.17, l_max=0.90, hue_shift=22, cool_hue=200, warm_hue=105)),
        ("abyss",  "#2F4FB0", dict(steps=6, l_min=0.13, l_max=0.88, hue_shift=18, cool_hue=290, warm_hue=230)),
        ("rose",   "#C2588F", dict(steps=6, l_min=0.22, l_max=0.94, hue_shift=18, cool_hue=310, warm_hue=20)),
        ("earth",  "#7D5631", dict(steps=6, l_min=0.17, l_max=0.84, hue_shift=18, cool_hue=20, warm_hue=85)),
        ("sand",   "#C9A45E", dict(steps=6, l_min=0.28, l_max=0.95, hue_shift=16, cool_hue=45, warm_hue=100)),
    )
    for name, anchor, kw in spec:
        p.add(Ramp(name, make_ramp(anchor, **kw)))
    p.pin("slate", FORGE_TOKENS["slate_border"])
    p.pin("slate", FORGE_TOKENS["iron_outline"])
    p.pin("spirit", FORGE_TOKENS["uncommon_cyan"])
    p.pin("violet", FORGE_TOKENS["epic_violet"])
    p.pin("gold", FORGE_TOKENS["mythic_amber"])
    # extremos absolutos (flash de impacto / whiteout e sombra total)
    p.add(Ramp("flash", [hex_to_rgb("#0A0710"), hex_to_rgb("#FFF8EC")]))
    return p
