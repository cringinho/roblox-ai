"""Cenarios do The Dark Altar (catedral e forja) prontos para o Roblox.

Uso (na raiz):  python pipeline/dark_altar/build_scenes.py

Saidas em art/dark-altar/scenes/:
  cathedral_320x180.png (+ _x4 para revisao)
  forge_gui.png + forge_Sprite.luau   -> 6 quadros 320x180 numa folha 966x364 (SpriteAnimator)
  forge.gif + forge_x4.png            -> revisao
A forja pendura nos quadros da parede as artes de subtipo do proprio jogo.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "roblox-pixel-art" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pixelforge import lint, preview, sheet  # noqa: E402
from pixelforge.palette import altar_palette  # noqa: E402
from pixelforge.scene import cathedral, forge  # noqa: E402

import subtypes as data  # noqa: E402
from build_subtypes import derive_colors  # noqa: E402
from subtype_render import render  # noqa: E402

OUT = ROOT / "art" / "dark-altar" / "scenes"
POSTERS = ["Leviata", "Dragao", "Eclipse", "Fogo", "Diamante"]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pal = altar_palette()
    subs = {s.sid: s for s in data.all_subtypes()}
    fam_bg = {f.key: f.bg_base for f in data.FAMILIES}
    posters = []
    for sid in POSTERS:
        st = subs[sid]
        st.bg, st.accent, _ = derive_colors(fam_bg[st.family], st.accent)
        posters.append(render(st, size=24))

    cath = cathedral(pal)
    cath.save(OUT / "cathedral_320x180.png")
    cath.save(OUT / "cathedral_320x180_x4.png", scale=4)
    print(lint.lint_canvas(cath, pal, "cathedral", 32, kind="background").text().splitlines()[0])
    # vitral cintilando: brilho que varre o vidro (shimmer) em 8 quadros - folha 966x546
    import numpy as np
    from pixelforge.anim import shimmer
    glass = [pal[k] for k in ("blood:4", "gold:4", "violet:4", "spirit:4", "abyss:4", "rose:4",
                              "ember:4", "violet:3", "abyss:3", "blood:3", "gold:5")]
    m = np.zeros((cath.h, cath.w), bool)
    for col in glass:
        m |= (cath.px[..., :3] == np.array(col)).all(-1)
    m[:, :60] = False
    m[:, 260:] = False
    m[110:] = False
    cath_anim = shimmer(cath, m, pal, frames=8, band=5, ms=110, name="cathedral")
    preview.gif(cath_anim, OUT / "cathedral.gif", scale=3, bg=None)
    sheet.export_gui_sheet(cath_anim, OUT)

    # editions (Balatro) sobre uma arte de subtipo - carta ampliada / colecao
    from pixelforge.edition import edition_anim
    ed_dir = ROOT / "art" / "dark-altar" / "editions"
    ed_dir.mkdir(parents=True, exist_ok=True)
    st = subs["Dragao"]
    st.bg, st.accent, _ = derive_colors(fam_bg[st.family], st.accent)
    art = render(st)
    for kind in ("foil", "holo", "polychrome", "negative"):
        ea = edition_anim(art, pal, kind)
        ea.name = f"edition_{kind}_Dragao"
        preview.gif(ea, ed_dir / f"{ea.name}.gif", scale=4, bg=None)
        sheet.export_gui_sheet(ea, ed_dir)
    print("editions ->", ed_dir.relative_to(ROOT))

    anim = forge(pal, posters=posters)
    anim.frames[0].save(OUT / "forge_320x180.png")
    anim.frames[0].save(OUT / "forge_x4.png", scale=4)
    preview.gif(anim, OUT / "forge.gif", scale=3, bg=None)
    paths = sheet.export_gui_sheet(anim, OUT)
    r = lint.lint_animation(anim, None, kind="background", max_colors=48)
    print(r.text().splitlines()[0], "->", ", ".join(p.name for p in paths.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
