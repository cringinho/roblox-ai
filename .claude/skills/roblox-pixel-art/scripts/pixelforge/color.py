"""Matematica de cor do PixelForge.

Tudo que envolve escolher cor passa por aqui:
- conversao sRGB <-> OKLab/OKLCH (espaco perceptual: passos de luz iguais = passos visuais iguais)
- contraste WCAG (legibilidade de texto/acento sobre fundo)
- utilitarios hex <-> RGB

OKLab foi escolhido porque o hue shifting fica previsivel: girar o matiz em OKLCH
nao muda a luminosidade percebida, entao a ramp continua com degraus de valor limpos.
"""
from __future__ import annotations

import math
from typing import Iterable, Tuple

RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


# ---------------------------------------------------------------- hex helpers
def hex_to_rgb(h: str) -> RGB:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"hex invalido: {h!r}")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(c: Iterable[int]) -> str:
    r, g, b = list(c)[:3]
    return "#{:02X}{:02X}{:02X}".format(int(r), int(g), int(b))


def rgba(h: str, a: int = 255) -> RGBA:
    r, g, b = hex_to_rgb(h)
    return (r, g, b, a)


# ---------------------------------------------------------------- sRGB <-> linear
def _to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


# ---------------------------------------------------------------- OKLab
def rgb_to_oklab(c: RGB) -> Tuple[float, float, float]:
    r, g, b = (_to_linear(v) for v in c[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def _oklab_to_linear(L: float, a: float, b: float) -> Tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def _in_gamut(lin: Tuple[float, float, float], eps: float = 1e-4) -> bool:
    return all(-eps <= v <= 1 + eps for v in lin)


def oklab_to_rgb(L: float, a: float, b: float) -> RGB:
    lin = _oklab_to_linear(L, a, b)
    return tuple(int(round(_to_srgb(v))) for v in lin)  # type: ignore[return-value]


# ---------------------------------------------------------------- OKLCH
def rgb_to_oklch(c: RGB) -> Tuple[float, float, float]:
    L, a, b = rgb_to_oklab(c)
    C = math.hypot(a, b)
    H = math.degrees(math.atan2(b, a)) % 360.0
    return (L, C, H)


def oklch_to_rgb(L: float, C: float, H: float) -> RGB:
    """Converte com gamut mapping: reduz o croma ate caber no sRGB (preserva luz e matiz)."""
    L = max(0.0, min(1.0, L))
    hr = math.radians(H)
    lo, hi = 0.0, max(0.0, C)
    a, b = hi * math.cos(hr), hi * math.sin(hr)
    if _in_gamut(_oklab_to_linear(L, a, b)):
        return oklab_to_rgb(L, a, b)
    for _ in range(24):  # busca binaria do maior croma valido
        mid = (lo + hi) / 2
        a, b = mid * math.cos(hr), mid * math.sin(hr)
        if _in_gamut(_oklab_to_linear(L, a, b)):
            lo = mid
        else:
            hi = mid
    a, b = lo * math.cos(hr), lo * math.sin(hr)
    return oklab_to_rgb(L, a, b)


def hue_lerp(h1: float, h2: float, t: float) -> float:
    """Interpola matiz pelo caminho mais curto do circulo."""
    d = ((h2 - h1 + 540.0) % 360.0) - 180.0
    return (h1 + d * t) % 360.0


def mix(c1: RGB, c2: RGB, t: float) -> RGB:
    """Mistura perceptual (em OKLab)."""
    L1, a1, b1 = rgb_to_oklab(c1)
    L2, a2, b2 = rgb_to_oklab(c2)
    return oklab_to_rgb(L1 + (L2 - L1) * t, a1 + (a2 - a1) * t, b1 + (b2 - b1) * t)


def oklab_distance(c1: RGB, c2: RGB) -> float:
    L1, a1, b1 = rgb_to_oklab(c1)
    L2, a2, b2 = rgb_to_oklab(c2)
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


# ---------------------------------------------------------------- contraste
def relative_luminance(c: RGB) -> float:
    r, g, b = (_to_linear(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1: RGB, c2: RGB) -> float:
    """Contraste WCAG 2.x (1..21). >=4.5 le bem texto pequeno; >=3 para formas grandes."""
    l1, l2 = relative_luminance(c1), relative_luminance(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def luma(c: RGB) -> float:
    """Valor (0..1) para o teste de escala de cinza: usa o L do OKLab."""
    return rgb_to_oklab(c)[0]
