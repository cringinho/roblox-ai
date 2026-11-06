"""'Editions' de carta no estilo Balatro (foil / holo / polychrome / negative), em pixel art.

Mecanismo (UI-11/UI-12 do dossie): o efeito e calculado POR TEXEL da arte nativa, a partir
de um campo animado formado por 3 centros orbitando. Depois a cor e QUANTIZADA de volta para
a paleta, entao o resultado continua sendo pixel art (paleta fechada, sem degrade).
Os centros orbitam com velocidades inteiras -> o loop fecha em `frames` quadros.

Uso no Roblox: folha de GUI (SpriteAnimator) para cartas raras/promocionais; para +4 na mao
use o foil_tile barato da spec e reserve isto para a carta ampliada / colecao.
"""
from __future__ import annotations

import math
from typing import List

import numpy as np

from .anim import Animation, ticks
from .canvas import Canvas
from .palette import Palette, srgb_to_oklab_np


def _oklab_to_srgb_np(lab: np.ndarray) -> np.ndarray:
    M = np.array([[1.0, 0.3963377774, 0.2158037573],
                  [1.0, -0.1055613458, -0.0638541728],
                  [1.0, -0.0894841775, -1.2914855480]])
    lms_ = lab @ M.T
    lms = lms_ ** 3
    M2 = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                   [-1.2684380046, 2.6097574011, -0.3413193965],
                   [-0.0041960863, -0.7034186147, 1.7076147010]])
    lin = np.clip(lms @ M2.T, 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    return np.clip(srgb * 255.0, 0, 255)


def _field(w: int, h: int, f: int, frames: int, freq: float, seed: int) -> np.ndarray:
    """Soma de cossenos das distancias a 3 centros orbitando (velocidades inteiras = loop)."""
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    u, v = xs / w, ys / h
    t = 2 * math.pi * f / frames
    acc = np.zeros((h, w))
    for k, speed in enumerate((1, -1, 2)):
        ph = rng.uniform(0, 2 * math.pi)
        cx = 0.5 + 0.35 * math.cos(t * speed + ph)
        cy = 0.5 + 0.35 * math.sin(t * speed + ph * 1.3)
        d = np.sqrt((u - cx) ** 2 + (v - cy) ** 2)
        acc += np.cos(d * freq * 2 * math.pi - t * speed)
    return (acc / 3.0 + 1.0) / 2.0  # 0..1


def apply_edition(art: Canvas, pal: Palette, kind: str, f: int, frames: int = 8, seed: int = 3) -> Canvas:
    px = art.px
    h, w = px.shape[:2]
    m = px[..., 3] > 0
    rgb = px[..., :3].astype(np.float64)
    lab = srgb_to_oklab_np(rgb)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.sqrt(A * A + B * B)
    H = np.arctan2(B, A)
    if kind == "polychrome":
        fld = _field(w, h, f, frames, 1.2, seed)
        H = H + fld * 2 * math.pi
        C = np.maximum(C, 0.06) * 1.25
        L = L * 0.95 + 0.04
    elif kind == "holo":
        fld = _field(w, h, f, frames, 2.6, seed)
        ys, xs = np.mgrid[0:h, 0:w]
        grid_ = (((xs + ys + f * 2) % 8) == 0) | (((xs - ys + f) % 8) == 0)
        H = H + fld * (2 * math.pi / 3) + grid_ * 0.8
        C = np.maximum(C, 0.05) * 1.3
        # puxa para azul-violeta misturando VETORES (misturar angulos quebra na volta do circulo)
        hv = math.atan2(-0.13, 0.03)
        a_ = C * np.cos(H) * 0.45 + C * math.cos(hv) * 0.55
        b_ = C * np.sin(H) * 0.45 + C * math.sin(hv) * 0.55
        H = np.arctan2(b_, a_)
        C = np.sqrt(a_ * a_ + b_ * b_) * 1.1
        L = L * 0.75 + 0.18 + grid_ * 0.06
    elif kind == "foil":
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
        cx, cy = w / 2, h / 2
        r = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        ang = np.arctan2(ys - cy, xs - cx)
        t = 2 * math.pi * f / frames
        rings = (np.cos(r * 0.55 - t * 2) + 1) / 2
        sweep = (np.cos(ang * 3 + t) + 1) / 2
        mask = rings * 0.55 + sweep * 0.45
        hot = mask > 0.62
        A = np.where(hot, A * 0.5 - 0.01, A)
        B = np.where(hot, B * 0.5 - 0.07, B)          # azul metalico
        L = np.where(hot, np.minimum(L + 0.12, 0.97), L)
        lab2 = np.stack([L, A, B], axis=-1)
        out_rgb = _oklab_to_srgb_np(lab2)
        c = Canvas(w, h)
        c.px[..., :3] = out_rgb.astype(np.uint8)
        c.px[..., 3] = np.where(m, 255, 0)
        c.px = pal.quantize(c.px)
        return c
    elif kind == "negative":
        L = 1.0 - L
        H = -H + 0.2
    else:
        raise ValueError(f"edition desconhecida: {kind}")
    A2, B2 = C * np.cos(H), C * np.sin(H)
    out_rgb = _oklab_to_srgb_np(np.stack([L, A2, B2], axis=-1))
    c = Canvas(w, h)
    c.px[..., :3] = out_rgb.astype(np.uint8)
    c.px[..., 3] = np.where(m, 255, 0)
    c.px = pal.quantize(c.px)
    return c


def edition_anim(art: Canvas, pal: Palette, kind: str, frames: int = 8, seed: int = 3,
                 ms: int = 0) -> Animation:
    frames_out: List[Canvas] = [apply_edition(art, pal, kind, f, frames, seed) for f in range(frames)]
    dur = ms or ticks(6)
    return Animation(f"edition_{kind}", frames_out, [dur] * frames, loop=True,
                     tags={"kind": "edition", "edition": kind})
