"""Previas para revisao humana/IA: tira de quadros, GIF animado e folha de contato.

Sempre revise sobre o FUNDO REAL do jogo (escuro) e na escala real de uso:
VFX que le bem sobre branco pode sumir sobre #1E1E24.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw

from .anim import Animation
from .canvas import Canvas

BG_DARK = (30, 30, 36, 255)      # #1E1E24 (ardosia da UI)
BG_VOID = (19, 14, 37, 255)      # void
CHECK_A = (40, 40, 48, 255)
CHECK_B = (32, 32, 40, 255)


def _bg(w: int, h: int, bg: Optional[Tuple[int, int, int, int]], cell: int = 4) -> Image.Image:
    if bg is not None:
        return Image.new("RGBA", (w, h), bg)
    img = Image.new("RGBA", (w, h), CHECK_A)
    d = ImageDraw.Draw(img)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=CHECK_B)
    return img


def frame_image(c: Canvas, scale: int, bg=BG_DARK) -> Image.Image:
    img = c.to_image().resize((c.w * scale, c.h * scale), Image.NEAREST)
    base = _bg(img.width, img.height, bg, cell=scale * 4)
    base.alpha_composite(img)
    return base


def strip(anim: Animation, scale: int = 4, bg=BG_DARK, gap: int = 2, label: bool = True) -> Image.Image:
    fw, fh = anim.w * scale, anim.h * scale
    top = 14 if label else 0
    out = Image.new("RGBA", (len(anim.frames) * (fw + gap) + gap, fh + gap * 2 + top), (12, 10, 18, 255))
    d = ImageDraw.Draw(out)
    for i, (f, ms) in enumerate(zip(anim.frames, anim.durations_ms)):
        x = gap + i * (fw + gap)
        out.paste(frame_image(f, scale, bg), (x, gap + top))
        if label:
            d.text((x + 2, 1), f"{i} {ms}ms", fill=(200, 196, 210, 255))
    return out


def gif(anim: Animation, path: Path, scale: int = 4, bg=BG_DARK) -> None:
    imgs = [frame_image(f, scale, bg).convert("RGB") for f in anim.frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=anim.durations_ms,
                 loop=0, disposal=2, optimize=False)


def contact_sheet(items: Sequence[Tuple[str, Canvas]], cols: int, scale: int = 2, bg=BG_DARK,
                  gap: int = 4, label_h: int = 12) -> Image.Image:
    if not items:
        raise ValueError("nada para montar")
    cw = max(c.w for _, c in items) * scale
    ch = max(c.h for _, c in items) * scale
    rows = (len(items) + cols - 1) // cols
    out = Image.new("RGBA", (cols * (cw + gap) + gap, rows * (ch + gap + label_h) + gap), (12, 10, 18, 255))
    d = ImageDraw.Draw(out)
    for i, (name, c) in enumerate(items):
        x = gap + (i % cols) * (cw + gap)
        y = gap + (i // cols) * (ch + gap + label_h)
        out.paste(frame_image(c, scale, bg), (x, y + label_h))
        d.text((x, y), name[:22], fill=(200, 196, 210, 255))
    return out


def save_strip_and_gif(anim: Animation, out_dir: Path, scale: int = 4, bg=BG_DARK) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    p1 = out_dir / f"{anim.name}_strip.png"
    p2 = out_dir / f"{anim.name}.gif"
    strip(anim, scale, bg).save(p1)
    gif(anim, p2, scale, bg)
    return [p1, p2]
