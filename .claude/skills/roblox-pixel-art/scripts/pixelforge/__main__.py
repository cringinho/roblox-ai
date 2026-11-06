"""CLI do PixelForge.  Rode a partir da pasta scripts/:  python -m pixelforge <comando>

Comandos:
  list                         lista os geradores de VFX
  palette [--out P]            salva a amostra da paleta ALTAR (+ JSON)
  fx NOME [--out D] [--gui] [--flipbook] [--upscale 4] [--seed N]
                               gera um VFX: tira + GIF de revisao e, se pedido, exports Roblox
  fx-all [--out D]             gera todos os VFX com exports e relatorio de lint
  lint PNG [--kind K]          nota 0-100 + problemas (kind: sprite|vfx|ui|background)
  preview-luau PNG [--scale K] imprime Luau de previa por EditableImage (MCP execute_luau)
  upload PNG [PNG...]          envia como assetType Image (Open Cloud; precisa ROBLOX_API_KEY)
  scene cathedral [--out P]    gera o cenario de catedral 320x180 (+ copia x4 p/ previa)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from . import fx, lint, preview, sheet
from .canvas import Canvas
from .palette import altar_palette


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pixelforge", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("palette"); p.add_argument("--out", default="out/palette.png")
    p = sub.add_parser("fx")
    p.add_argument("name"); p.add_argument("--out", default="out/fx")
    p.add_argument("--gui", action="store_true"); p.add_argument("--flipbook", action="store_true")
    p.add_argument("--upscale", type=int, default=1); p.add_argument("--seed", type=int)
    p = sub.add_parser("fx-all"); p.add_argument("--out", default="out/fx")
    p = sub.add_parser("lint"); p.add_argument("png"); p.add_argument("--kind", default="sprite")
    p.add_argument("--max-colors", type=int, default=24)
    p = sub.add_parser("preview-luau"); p.add_argument("png"); p.add_argument("--scale", type=int, default=4)
    p = sub.add_parser("upload"); p.add_argument("png", nargs="+")
    p = sub.add_parser("scene"); p.add_argument("kind", choices=["cathedral"])
    p.add_argument("--out", default="out/scene_cathedral.png"); p.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    pal = altar_palette()

    if a.cmd == "list":
        for k, f in fx.ALL.items():
            doc = (f.__doc__ or "").strip().splitlines()
            print(f"{k:15s} {doc[0] if doc else ''}")
        return 0
    if a.cmd == "palette":
        out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
        rows = list(pal.ramps.values())
        W = max(len(r) for r in rows)
        c = Canvas(W * 6, len(rows) * 6, (0, 0, 0, 255))
        for j, r in enumerate(rows):
            for i, col in enumerate(r.colors):
                c.fill_rect(i * 6, j * 6, 6, 6, col)
        c.save(out, scale=8)
        pal.save(out.with_suffix(".json"))
        print("ok", out)
        return 0
    if a.cmd in ("fx", "fx-all"):
        names = list(fx.ALL) if a.cmd == "fx-all" else [a.name]
        out = Path(a.out)
        report = {}
        for n in names:
            if n not in fx.ALL:
                print(f"VFX desconhecido: {n}. Use 'list'.", file=sys.stderr)
                return 2
            kw = {"seed": a.seed} if getattr(a, "seed", None) is not None else {}
            anim = fx.ALL[n](pal, **kw)
            preview.save_strip_and_gif(anim, out)
            r = lint.lint_animation(anim, pal)
            report[n] = {"score": r.score, "issues": r.issues}
            print(r.text())
            if a.cmd == "fx-all" or a.gui:
                sheet.export_gui_sheet(anim, out / "roblox", upscale=getattr(a, "upscale", 1))
            if a.cmd == "fx-all" or a.flipbook:
                sheet.export_flipbook(anim, out / "roblox")
        (out / "lint_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0
    if a.cmd == "lint":
        c = Canvas.from_image(Image.open(a.png))
        r = lint.lint_canvas(c, None, Path(a.png).name, a.max_colors, kind=a.kind)
        print(r.text())
        return 0 if r.score >= 80 else 1
    if a.cmd == "preview-luau":
        from .roblox import editable_image_luau
        c = Canvas.from_image(Image.open(a.png))
        print(editable_image_luau(c, Path(a.png).stem, a.scale))
        return 0
    if a.cmd == "scene":
        from .scene import cathedral
        out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
        c = cathedral(pal, seed=a.seed)
        c.save(out)
        c.save(out.with_name(out.stem + "_x4.png"), scale=4)
        r = lint.lint_canvas(c, pal, out.name, max_colors=32, kind="background")
        print(r.text())
        return 0
    if a.cmd == "upload":
        from .roblox import upload_images
        res = upload_images([Path(p) for p in a.png])
        print(json.dumps(res, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
