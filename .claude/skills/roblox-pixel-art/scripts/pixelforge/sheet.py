"""Exportacao para Roblox.

Dois destinos com regras diferentes (ver references/05-roblox-integracao.md):

1) GUI (ImageLabel/ImageButton) -> export_gui_sheet()
   - Resolucao NATIVA (sem ampliar) + ResampleMode = Pixelated no Roblox.
   - Quadros em grade com 'padding' transparente (evita sangrar o quadro vizinho).
   - Duracao por quadro preservada (SpriteAnimator.luau le o modulo gerado).
   - Imagem <= 1024x1024 (acima disso o Roblox reduz e destroi o pixel).

2) ParticleEmitter (Flipbook) -> export_flipbook()
   - Textura QUADRADA com grade 2x2 / 4x4 / 8x8 (4 / 16 / 64 quadros).
   - Particulas sao filtradas (bilinear): cada celula e AMPLIADA por fator inteiro
     (nearest) antes do upload -> o borrao fica sub-pixel e o pixel continua nitido.
   - Framerate fixo: holds sao 'assados' repetindo quadros (Animation.resample_fixed).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image

from .anim import Animation
from .canvas import Canvas

MAX_IMAGE = 1024
MAX_FLIPBOOK_FPS = 30.0  # limite do ParticleEmitter


def alpha_bleed(img: Image.Image, passes: int = 8) -> Image.Image:
    """Copia a cor das bordas para os pixels TRANSPARENTES (alpha continua 0).

    Motivo: o upload do Roblox transforma RGB de pixels transparentes em preto e a
    filtragem (particulas, mipmaps, compressao no mobile) mistura esse preto com a
    borda -> franja escura. Com o bleed, a mistura acontece com a propria cor."""
    import numpy as np
    a = np.array(img.convert("RGBA"))
    rgb = a[..., :3].astype(np.int32)
    filled = a[..., 3] > 0
    for _ in range(passes):
        if filled.all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros(filled.shape, dtype=np.int32)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            sh_f = np.roll(np.roll(filled, dy, 0), dx, 1)
            sh_c = np.roll(np.roll(rgb, dy, 0), dx, 1)
            acc += sh_c * sh_f[..., None]
            cnt += sh_f
        grow = (~filled) & (cnt > 0)
        rgb[grow] = acc[grow] // cnt[grow][:, None]
        filled = filled | grow
    a[..., :3] = rgb.astype(np.uint8)
    return Image.fromarray(a, "RGBA")


@dataclass
class GuiSheet:
    image: Image.Image
    cols: int
    rows: int
    cell_w: int
    cell_h: int
    pad: int
    rects: List[Tuple[int, int, int, int]]  # (x, y, w, h) para ImageRectOffset/ImageRectSize


def pack_grid(frames: Sequence[Canvas], pad: int = 1, max_size: int = MAX_IMAGE,
              cols: Optional[int] = None) -> GuiSheet:
    fw, fh = frames[0].w, frames[0].h
    n = len(frames)
    cw, ch = fw + pad * 2, fh + pad * 2
    if cols is None:
        cols = max(1, min(n, max_size // cw))
        # tenta deixar a folha o mais quadrada possivel
        best = cols
        for c in range(1, cols + 1):
            r = math.ceil(n / c)
            if c * cw <= max_size and r * ch <= max_size:
                if abs(c * cw - r * ch) < abs(best * cw - math.ceil(n / best) * ch):
                    best = c
        cols = best
    rows = math.ceil(n / cols)
    W, H = cols * cw, rows * ch
    if W > max_size or H > max_size:
        raise ValueError(f"folha {W}x{H} passa de {max_size}px: divida a animacao ou reduza quadros")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rects = []
    for i, f in enumerate(frames):
        x = (i % cols) * cw + pad
        y = (i // cols) * ch + pad
        img.alpha_composite(f.to_image(), (x, y))
        rects.append((x, y, fw, fh))
    return GuiSheet(img, cols, rows, fw, fh, pad, rects)


def luau_sprite_module(anim: Animation, sheet: GuiSheet, asset_id: str = "rbxassetid://0") -> str:
    """Gera um ModuleScript Luau (--!strict) com os retangulos e duracoes da animacao."""
    lines = [
        "--!strict",
        f"-- Gerado pelo PixelForge. Animacao: {anim.name}",
        "-- Coloque em ReplicatedStorage/Shared/Sprites/ e troque 'image' pelo ID enviado.",
        "-- Uso: SpriteAnimator.play(imageLabel, require(este_modulo))",
        "",
        "export type Frame = { x: number, y: number, w: number, h: number, ms: number }",
        "export type SpriteData = {",
        "\tname: string,",
        "\timage: string,",
        "\tloop: boolean,",
        "\tpivotX: number,",
        "\tpivotY: number,",
        "\tframes: { Frame },",
        "}",
        "",
        "local data: SpriteData = {",
        f'\tname = "{anim.name}",',
        f'\timage = "{asset_id}",',
        f"\tloop = {'true' if anim.loop else 'false'},",
        f"\tpivotX = {anim.pivot[0]},",
        f"\tpivotY = {anim.pivot[1]},",
        "\tframes = {",
    ]
    for (x, y, w, h), ms in zip(sheet.rects, anim.durations_ms):
        lines.append(f"\t\t{{ x = {x}, y = {y}, w = {w}, h = {h}, ms = {int(ms)} }},")
    lines += ["\t},", "}", "", "return table.freeze(data)", ""]
    return "\n".join(lines)


def export_gui_sheet(anim: Animation, out_dir: Path, pad: int = 1,
                     asset_id: str = "rbxassetid://0", upscale: int = 1) -> Dict[str, Path]:
    """upscale=4 ('hi-fi mobile'): cada pixel da arte vira um bloco 4x4 = exatamente um
    bloco de compressao de GPU -> a compressao com perdas do mobile nao mistura cores.
    Custa 16x memoria: use em sprites pequenos/criticos. Retangulos saem ja multiplicados."""
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = [f.scaled(upscale) for f in anim.frames] if upscale > 1 else anim.frames
    sheet = pack_grid(frames, pad * upscale)
    png = out_dir / f"{anim.name}_gui{'_x' + str(upscale) if upscale > 1 else ''}.png"
    alpha_bleed(sheet.image).save(png)
    meta = {
        "name": anim.name, "target": "gui", "loop": anim.loop,
        "cell": [sheet.cell_w, sheet.cell_h], "pad": pad, "cols": sheet.cols, "rows": sheet.rows,
        "frames": [{"x": r[0], "y": r[1], "w": r[2], "h": r[3], "ms": int(ms)}
                   for r, ms in zip(sheet.rects, anim.durations_ms)],
        "roblox": {"ResampleMode": "Pixelated", "ScaleType": "Stretch",
                   "note": "ImageRectSize = (w,h); ImageRectOffset = (x,y); tamanho na tela = multiplo inteiro de (w,h)"},
        "tags": anim.tags,
    }
    js = out_dir / f"{anim.name}_gui.json"
    js.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    lua = out_dir / f"{anim.name}_Sprite.luau"
    lua.write_text(luau_sprite_module(anim, sheet, asset_id), encoding="utf-8")
    return {"png": png, "json": js, "luau": lua}


# ---------------------------------------------------------------- flipbook (ParticleEmitter)
FLIPBOOK_LAYOUTS = {4: ("Grid2x2", 2), 16: ("Grid4x4", 4), 64: ("Grid8x8", 8)}


def flipbook_frames(anim: Animation, layout: Optional[int] = None,
                    fps: Optional[float] = None) -> Tuple[List[Canvas], int, float]:
    """Escolhe grade e taxa: reamostra em fps fixo e completa ate 4/16/64 quadros.
    Retorna (quadros, n_grade, fps)."""
    if fps is None:
        fps = round(1000.0 / min(anim.durations_ms))
    fps = max(4.0, min(MAX_FLIPBOOK_FPS, float(fps)))
    frames = anim.resample_fixed(fps)
    n = len(frames)
    if layout is None:
        layout = 4 if n <= 4 else (16 if n <= 16 else 64)
    if n > layout:
        # comprime o tempo: reamostra para caber na grade (mantem a duracao total)
        fps = min(MAX_FLIPBOOK_FPS, layout * 1000.0 / anim.total_ms)
        frames = anim.resample_fixed(fps)[:layout]
    while len(frames) < layout:
        # one-shot: completa com quadro vazio (a particula deve morrer antes);
        # loop: repete do inicio para nao 'piscar'
        frames.append(frames[len(frames) % max(1, len(frames))].copy() if anim.loop else Canvas(anim.w, anim.h))
    return frames, layout, fps


def export_flipbook(anim: Animation, out_dir: Path, texture: int = 1024,
                    layout: Optional[int] = None, fps: Optional[float] = None) -> Dict[str, Path]:
    """Gera a textura quadrada do Flipbook com celulas ampliadas por fator inteiro."""
    out_dir.mkdir(parents=True, exist_ok=True)
    frames, n, fps = flipbook_frames(anim, layout, fps)
    enum_name, g = FLIPBOOK_LAYOUTS[n]
    cell = texture // g
    # margem garantida (doc Roblox: espacamento entre quadros; mipmaps pedem mais)
    gutter = max(4, cell // 16)
    k = max(1, min((cell - 2 * gutter) // anim.w, (cell - 2 * gutter) // anim.h))
    img = Image.new("RGBA", (texture, texture), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        big = f.scaled(k).to_image()
        x = (i % g) * cell + (cell - big.width) // 2
        y = (i // g) * cell + (cell - big.height) // 2
        img.alpha_composite(big, (x, y))
    png = out_dir / f"{anim.name}_flipbook_{enum_name}.png"
    alpha_bleed(img).save(png)
    lifetime = n / fps
    meta = {
        "name": anim.name, "target": "ParticleEmitter",
        "texture": texture, "cell": cell, "upscale": k, "gutter": gutter,
        "properties": {
            "FlipbookLayout": f"Enum.ParticleFlipbookLayout.{enum_name}",
            "FlipbookMode": "Enum.ParticleFlipbookMode." + ("Loop" if anim.loop else "OneShot"),
            "FlipbookFramerate": f"NumberRange.new({fps:.2f})",
            "FlipbookBlendFrames": "false  (padrao true faz crossfade e borra a troca de quadros)",
            "Lifetime": f"NumberRange.new({lifetime:.3f})" if not anim.loop else "livre (loop)",
            "LightEmission": "1 para fogo/luz; 0 para fumaca/sangue",
            "Orientation": "FacingCamera",
        },
        "note": "Particulas sao filtradas; o upscale inteiro mantem a leitura pixelada. OneShot: Lifetime = quadros/fps.",
    }
    js = out_dir / f"{anim.name}_flipbook.json"
    js.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"png": png, "json": js}


def upscale_for_3d(c: Canvas, target: int = 1024) -> Canvas:
    """Textura 3D (Decal/Texture/SurfaceAppearance) e sempre filtrada: amplie por fator
    inteiro ate perto de 'target' antes do upload para o borrao ficar invisivel."""
    k = max(1, target // max(c.w, c.h))
    return c.scaled(k)
