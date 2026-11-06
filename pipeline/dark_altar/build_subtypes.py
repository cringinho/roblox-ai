"""Gera o catalogo Luau + atlas pixel art das 120 Artes de Subtipo.

Uso (na raiz do repositorio):
    python pipeline/dark_altar/build_subtypes.py            # gera tudo
    python pipeline/dark_altar/build_subtypes.py --check    # so valida

Saidas:
    src/shared/Config/SubtypeArtCatalog120.luau
    src/shared/Config/SubtypeArtAtlas120.luau          (retangulos do atlas, modo B)
    art/dark-altar/subtypes/SubtypeArtAtlas120.png      (1024x512, 16x8 celulas de 64px)
    art/dark-altar/subtypes/preview_<familia>.png       (previas ampliadas para revisao)
    art/dark-altar/subtypes/preview_all.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "roblox-pixel-art" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw  # noqa: E402

from pixelforge.color import (contrast_ratio, hex_to_rgb, mix, oklch_to_rgb,  # noqa: E402
                              rgb_to_hex, rgb_to_oklch)
from pixelforge.font import supported  # noqa: E402
from pixelforge.lint import lint_canvas  # noqa: E402
import subtypes as data  # noqa: E402
from subtype_render import render  # noqa: E402

LUAU_OUT = ROOT / "src" / "shared" / "Config" / "SubtypeArtCatalog120.luau"
ATLAS_LUAU_OUT = ROOT / "src" / "shared" / "Config" / "SubtypeArtAtlas120.luau"
ART_DIR = ROOT / "art" / "dark-altar" / "subtypes"
HIFI_LUAU_OUT = ROOT / "src" / "shared" / "Config" / "SubtypeArtAtlas120HiFi.luau"
MIN_CONTRAST = 5.5
BLOCKED = (0x2600, 0x27BF)  # Misc Symbols + Dingbats (emoji)


# ---------------------------------------------------------------- derivacao + validacao
def derive_colors(family_bg: str, accent: str):
    """Fundo = cor da familia + 10% do acento. Se o contraste nao fechar 5.5:1,
    primeiro escurece o fundo (ate 2 passos), depois CLAREIA o acento em OKLCH
    (mesmo matiz e croma) ate passar. Retorna (bg_hex, accent_hex, ajustado?)."""
    acc = hex_to_rgb(accent)
    bg = mix(hex_to_rgb(family_bg), acc, 0.10)
    k = 0
    while contrast_ratio(acc, bg) < MIN_CONTRAST and k < 2:
        bg = mix(bg, (0, 0, 0), 0.20)
        k += 1
    adjusted = False
    L, Cc, H = rgb_to_oklch(acc)
    while contrast_ratio(acc, bg) < MIN_CONTRAST and L < 0.98:
        L += 0.02
        acc = oklch_to_rgb(L, Cc, H)
        adjusted = True
    return rgb_to_hex(bg), rgb_to_hex(acc), adjusted


def blocked(s: str) -> bool:
    return any(BLOCKED[0] <= ord(ch) <= BLOCKED[1] for ch in s)


def validate(subs: List[data.Subtype]) -> List[str]:
    errs: List[str] = []
    if len(subs) != 120:
        errs.append(f"esperado 120 subtipos, encontrado {len(subs)}")
    counts: Dict[str, int] = {}
    ids = set()
    for s in subs:
        counts[s.family] = counts.get(s.family, 0) + 1
        if s.sid in ids:
            errs.append(f"subtypeId duplicado: {s.sid}")
        ids.add(s.sid)
        if not s.sid.isascii() or not s.sid.isidentifier():
            errs.append(f"{s.sid}: subtypeId deve ser ASCII sem espacos")
        if s.pattern not in data.PATTERNS:
            errs.append(f"{s.sid}: etchingPattern invalido {s.pattern}")
        if s.particle not in data.PARTICLES:
            errs.append(f"{s.sid}: particleGlyph invalido {s.particle!r}")
        if not (1 <= len(s.sils) <= 5):
            errs.append(f"{s.sid}: use 1-5 silhuetas")
        for sil in s.sils:
            if sil.shape not in data.SHAPES:
                errs.append(f"{s.sid}: shape invalido {sil.shape}")
            if not (0.05 <= sil.sx <= 1.0 and 0.05 <= sil.sy <= 1.0):
                errs.append(f"{s.sid}: escala fora de 0.05..1.0")
        for txt in (s.watermark, s.particle, s.name):
            if blocked(txt):
                errs.append(f"{s.sid}: caractere bloqueado (U+2600-27BF) em {txt!r}")
        if not all(supported(ch) for ch in s.watermark):
            errs.append(f"{s.sid}: watermark {s.watermark!r} sem glifo na fonte bitmap")
        if not (1 <= len(s.watermark) <= 2):
            errs.append(f"{s.sid}: watermark deve ter 1-2 caracteres")
        cr = contrast_ratio(hex_to_rgb(s.accent), hex_to_rgb(s.bg))
        if cr < MIN_CONTRAST:
            errs.append(f"{s.sid}: contraste {cr:.2f} < {MIN_CONTRAST}")
    for k, n in data.EXPECTED_COUNTS.items():
        if counts.get(k, 0) != n:
            errs.append(f"familia {k}: esperado {n}, encontrado {counts.get(k, 0)}")
    return errs


# ---------------------------------------------------------------- emissao Luau
def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fmt_num(v: float) -> str:
    t = f"{v:.2f}".rstrip("0").rstrip(".")
    return t if t not in ("-0", "") else "0"


def emit_luau(subs: List[data.Subtype]) -> str:
    fams = [(f.key, f.label) for f in data.FAMILIES]
    L: List[str] = []
    w = L.append
    w("--!strict")
    w("--[[")
    w("\tSubtypeArtCatalog120.luau")
    w("\tColoque em: ReplicatedStorage > Shared > Config  (Rojo: src/shared/Config/)")
    w("")
    w("\tGERADO AUTOMATICAMENTE por pipeline/dark_altar/build_subtypes.py.")
    w("\tNao edite a mao: edite pipeline/dark_altar/subtypes.py e rode o gerador.")
    w("")
    w("\tO que e: dados das 120 Artes de Subtipo (fundo das cartas) em 12 familias de cor.")
    w("\tCada entrada descreve uma composicao procedural de xilogravura gotica:")
    w("\t  fundo (bgHex) + gravura (etchingPattern) + monograma (watermarkGlyph)")
    w("\t  + emblema concentrico (centerSilhouettes) + particulas (particleGlyph).")
    w("\tRegras: sem emoji (bloco U+2600-27BF bloqueado); tags so entre colchetes")
    w("\t([ATQ] [GRD] [BUF] [DEB] [SAC]); glifos geometricos permitidos: ◆ ◇ ▸ † ‡ ▲ ~ ·")
    w("\tRotation em graus no sentido horario (igual a GuiObject.Rotation).")
    w("\tscaleX/scaleY = fracao do quadro da arte (0..1), centrado.")
    w("]]")
    w("")
    w('export type EtchingPattern = "SPIKES" | "ARCHES" | "WAVES" | "RAYS" | "ABYSS" | "ROOTS" | "FRACTAL" | "SCALES"')
    w('export type SilhouetteShape = "DIAMOND" | "PILLAR" | "RING" | "BLADE" | "CRESCENT" | "CROWN"')
    w('export type ParticleGlyph = "·" | "†" | "◆" | "~"')
    w("export type ColorFamily =")
    for i, (k, _) in enumerate(fams):
        w(f'\t{"| " if i else ""}"{k}"')
    w("")
    w("export type Silhouette = {")
    w("\tshape: SilhouetteShape,")
    w("\tscaleX: number,")
    w("\tscaleY: number,")
    w("\trotation: number,")
    w("}")
    w("")
    w("export type SubtypeArt = {")
    w("\tsubtypeId: string,")
    w("\tdisplayName: string,")
    w("\tfamily: ColorFamily,")
    w("\torder: number,")
    w("\tbgHex: string,")
    w("\taccentHex: string,")
    w("\tetchingPattern: EtchingPattern,")
    w("\tcenterSilhouettes: { Silhouette },")
    w("\twatermarkGlyph: string,")
    w("\tparticleGlyph: ParticleGlyph,")
    w("\tisGlitchy: boolean,")
    w("}")
    w("")
    w("export type ResolvedColors = {")
    w("\tbg: Color3,")
    w("\taccent: Color3,")
    w("\taccentLight: Color3, -- luz do emblema")
    w("\taccentShadow: Color3, -- sombra/hachura do emblema")
    w("\tetch: Color3, -- linhas da gravura (baixo contraste)")
    w("\twatermark: Color3, -- monograma (quase o fundo)")
    w("\tink: Color3, -- contorno de tinta do emblema")
    w("}")
    w("")
    w("export type FamilyInfo = { key: ColorFamily, label: string, count: number }")
    w("")
    w("-- ===================================================================== DADOS")
    w("local ENTRIES: { SubtypeArt } = {")
    cur = None
    for s in subs:
        if s.family != cur:
            cur = s.family
            label = next(lbl for k, lbl in fams if k == cur)
            w(f"\t-- ------------------------------------------------ {label}")
        w("\t{")
        w(f"\t\tsubtypeId = {lua_str(s.sid)},")
        w(f"\t\tdisplayName = {lua_str(s.name)},")
        w(f"\t\tfamily = {lua_str(s.family)},")
        w(f"\t\torder = {s.order},")
        w(f"\t\tbgHex = {lua_str(s.bg)},")
        w(f"\t\taccentHex = {lua_str(s.accent.upper())},")
        w(f"\t\tetchingPattern = {lua_str(s.pattern)},")
        w("\t\tcenterSilhouettes = {")
        for sil in s.sils:
            w(f"\t\t\t{{ shape = {lua_str(sil.shape)}, scaleX = {fmt_num(sil.sx)}, scaleY = {fmt_num(sil.sy)}, rotation = {fmt_num(sil.rot)} }},")
        w("\t\t},")
        w(f"\t\twatermarkGlyph = {lua_str(s.watermark)},")
        w(f"\t\tparticleGlyph = {lua_str(s.particle)},")
        w(f"\t\tisGlitchy = {'true' if s.glitchy else 'false'},")
        w("\t},")
    w("}")
    w("")
    w("local FAMILIES: { FamilyInfo } = {")
    for k, label in fams:
        n = sum(1 for s in subs if s.family == k)
        w(f"\t{{ key = {lua_str(k)}, label = {lua_str(label)}, count = {n} }},")
    w("}")
    w("")
    w(LUAU_API)
    return "\n".join(L) + "\n"


LUAU_API = r'''-- ===================================================================== INDICES
local BY_ID: { [string]: SubtypeArt } = {}
local BY_FAMILY: { [string]: { SubtypeArt } } = {}

for _, entry in ENTRIES do
	-- congela as listas internas para ninguem alterar os dados em tempo de jogo
	table.freeze(entry.centerSilhouettes)
	for _, sil in entry.centerSilhouettes do
		table.freeze(sil)
	end
	table.freeze(entry)
	BY_ID[entry.subtypeId] = entry
	local list = BY_FAMILY[entry.family]
	if list == nil then
		list = {}
		BY_FAMILY[entry.family] = list
	end
	table.insert(list, entry)
end
for _, list in BY_FAMILY do
	table.freeze(list)
end
table.freeze(ENTRIES)
table.freeze(FAMILIES)

-- ===================================================================== API
local SubtypeArtCatalog120 = {}

SubtypeArtCatalog120.COUNT = 120
SubtypeArtCatalog120.entries = ENTRIES
SubtypeArtCatalog120.families = FAMILIES

-- Retorna a arte do subtipo ou nil (nunca da erro: a UI decide o fallback).
function SubtypeArtCatalog120.get(subtypeId: string): SubtypeArt?
	return BY_ID[subtypeId]
end

-- Igual a get, mas com fallback seguro para o primeiro subtipo neutro (Treinamento).
function SubtypeArtCatalog120.getOrDefault(subtypeId: string): SubtypeArt
	local found = BY_ID[subtypeId]
	if found ~= nil then
		return found
	end
	warn(`[SubtypeArtCatalog120] subtipo desconhecido: {subtypeId} (usando Treinamento)`)
	return ENTRIES[1]
end

function SubtypeArtCatalog120.byFamily(family: ColorFamily): { SubtypeArt }
	return BY_FAMILY[family] or {}
end

-- Converte os hex em Color3 e deriva os tons auxiliares (mesma formula do atlas pixel art).
local INK = Color3.fromRGB(6, 5, 10)
local PAPER = Color3.fromRGB(255, 248, 236)

function SubtypeArtCatalog120.resolveColors(entry: SubtypeArt): ResolvedColors
	local bg = Color3.fromHex(entry.bgHex)
	local accent = Color3.fromHex(entry.accentHex)
	return {
		bg = bg,
		accent = accent,
		accentLight = accent:Lerp(PAPER, 0.45),
		accentShadow = accent:Lerp(bg, 0.62),
		etch = bg:Lerp(accent, 0.20),
		watermark = bg:Lerp(accent, 0.11),
		ink = bg:Lerp(INK, 0.70),
	}
end

-- Autoteste (rode no Command Bar: require(caminho).validate()).
-- Retorna lista de problemas; vazia = tudo certo.
local BLOCK_START = 0x2600
local BLOCK_END = 0x27BF

local function hasBlockedCodepoint(text: string): boolean
	for _, code in utf8.codes(text) do
		if code >= BLOCK_START and code <= BLOCK_END then
			return true
		end
	end
	return false
end

function SubtypeArtCatalog120.validate(): { string }
	local problems: { string } = {}
	if #ENTRIES ~= 120 then
		table.insert(problems, `esperado 120 entradas, encontrado {#ENTRIES}`)
	end
	for _, entry in ENTRIES do
		if hasBlockedCodepoint(entry.watermarkGlyph) or hasBlockedCodepoint(entry.displayName) then
			table.insert(problems, `{entry.subtypeId}: caractere bloqueado (emoji)`)
		end
		local okBg = pcall(Color3.fromHex, entry.bgHex)
		local okAccent = pcall(Color3.fromHex, entry.accentHex)
		if not okBg or not okAccent then
			table.insert(problems, `{entry.subtypeId}: hex invalido`)
		end
		if #entry.centerSilhouettes == 0 then
			table.insert(problems, `{entry.subtypeId}: sem silhuetas`)
		end
	end
	return problems
end

return table.freeze(SubtypeArtCatalog120)'''


def emit_atlas_luau(subs: List[data.Subtype], cols: int, cell: int) -> str:
    L = [
        "--!strict",
        "--[[",
        "\tSubtypeArtAtlas120.luau  (GERADO - nao edite a mao)",
        "\tColoque em: ReplicatedStorage > Shared > Config",
        "",
        "\tModo B (recomendado para mobile): 1 ImageLabel por carta usando o atlas",
        "\tSubtypeArtAtlas120.png (1024x512, celulas de 64x64). Configure no ImageLabel:",
        "\t  ResampleMode = Enum.ResamplerMode.Pixelated",
        "\t  ImageRectSize = Vector2.new(64, 64)",
        "\t  ImageRectOffset = SubtypeArtAtlas120.offsetOf(subtypeId)",
        "\tTroque IMAGE pelo rbxassetid do atlas depois do upload.",
        "]]",
        "",
        "local SubtypeArtAtlas120 = {}",
        "",
        'SubtypeArtAtlas120.IMAGE = "rbxassetid://0"',
        f"SubtypeArtAtlas120.CELL = {cell}",
        "",
        "local OFFSETS: { [string]: Vector2 } = {",
    ]
    for i, s in enumerate(subs):
        x, y = (i % cols) * cell, (i // cols) * cell
        L.append(f"\t{s.sid} = Vector2.new({x}, {y}),")
    L += [
        "}",
        "",
        "-- Offset do subtipo no atlas; Vector2.zero se nao existir (mostra o primeiro).",
        "function SubtypeArtAtlas120.offsetOf(subtypeId: string): Vector2",
        "\treturn OFFSETS[subtypeId] or Vector2.zero",
        "end",
        "",
        "function SubtypeArtAtlas120.apply(label: ImageLabel, subtypeId: string)",
        "\tlabel.Image = SubtypeArtAtlas120.IMAGE",
        "\tlabel.ResampleMode = Enum.ResamplerMode.Pixelated",
        "\tlabel.ImageRectSize = Vector2.new(SubtypeArtAtlas120.CELL, SubtypeArtAtlas120.CELL)",
        "\tlabel.ImageRectOffset = SubtypeArtAtlas120.offsetOf(subtypeId)",
        "end",
        "",
        "return table.freeze(SubtypeArtAtlas120)",
        "",
    ]
    return "\n".join(L)


def emit_hifi_luau(subs: List[data.Subtype], per_row: int, cell: int, per_page: int, n_pages: int) -> str:
    L = [
        "--!strict",
        "--[[",
        "\tSubtypeArtAtlas120HiFi.luau  (GERADO com --hifi - nao edite a mao)",
        "\tColoque em: ReplicatedStorage > Shared > Config",
        "",
        "\tVariante x4 para MOBILE: cada pixel da arte vira um bloco 4x4 = um bloco de compressao",
        "\tda GPU, entao a compressao com perdas do celular nao mistura cores vizinhas.",
        f"\t{n_pages} paginas de 1024x1024 ({per_page} artes por pagina, celulas de {cell}px).",
        "\tCusto: ~16x a memoria do atlas normal -> use so onde a cor estragar no aparelho.",
        "\tTroque cada PAGES[i] pelo rbxassetid da pagina i depois do upload (assetType Image).",
        "]]",
        "",
        "export type Entry = { page: number, offset: Vector2 }",
        "",
        "local SubtypeArtAtlas120HiFi = {}",
        "",
        f"SubtypeArtAtlas120HiFi.CELL = {cell}",
        "SubtypeArtAtlas120HiFi.PAGES = {",
    ]
    for i in range(n_pages):
        L.append(f'\t"rbxassetid://0", -- SubtypeArtAtlas120_x4_p{i + 1}.png')
    L += ["} :: { string }", "", "local ENTRIES: { [string]: Entry } = {"]
    for i, s_ in enumerate(subs):
        page = i // per_page
        j = i % per_page
        L.append(f"\t{s_.sid} = {{ page = {page + 1}, offset = Vector2.new({(j % per_row) * cell}, {(j // per_row) * cell}) }},")
    L += [
        "}",
        "",
        "function SubtypeArtAtlas120HiFi.get(subtypeId: string): Entry?",
        "\treturn ENTRIES[subtypeId]",
        "end",
        "",
        "-- Aplica a arte; retorna false (e nao mexe na label) se o subtipo nao existir.",
        "function SubtypeArtAtlas120HiFi.apply(label: ImageLabel, subtypeId: string): boolean",
        "\tlocal entry = ENTRIES[subtypeId]",
        "\tif entry == nil then",
        "\t\twarn(`[SubtypeArtAtlas120HiFi] subtipo desconhecido: {subtypeId}`)",
        "\t\treturn false",
        "\tend",
        "\tlabel.Image = SubtypeArtAtlas120HiFi.PAGES[entry.page]",
        "\tlabel.ResampleMode = Enum.ResamplerMode.Pixelated",
        "\tlabel.ImageRectSize = Vector2.new(SubtypeArtAtlas120HiFi.CELL, SubtypeArtAtlas120HiFi.CELL)",
        "\tlabel.ImageRectOffset = entry.offset",
        "\treturn true",
        "end",
        "",
        "return table.freeze(SubtypeArtAtlas120HiFi)",
        "",
    ]
    return "\n".join(L)


# ---------------------------------------------------------------- previas
def preview_sheet(items, cols: int, scale: int, title: str) -> Image.Image:
    cell = 64 * scale
    lab = 14
    rows = (len(items) + cols - 1) // cols
    W = cols * (cell + 6) + 6
    H = rows * (cell + lab + 6) + 26
    img = Image.new("RGBA", (W, H), (12, 10, 18, 255))
    d = ImageDraw.Draw(img)
    d.text((6, 6), title, fill=(230, 222, 240, 255))
    for i, (s, canvas) in enumerate(items):
        x = 6 + (i % cols) * (cell + 6)
        y = 26 + (i // cols) * (cell + lab + 6)
        img.paste(canvas.to_image().resize((cell, cell), Image.NEAREST), (x, y + lab))
        tag = ("~" if s.glitchy else "") + s.sid
        d.text((x, y), tag[:20], fill=(200, 196, 210, 255))
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--hifi", action="store_true",
                    help="gera tambem paginas x4 (1024x1024, 16 artes por pagina) contra a compressao do mobile")
    args = ap.parse_args()
    subs = data.all_subtypes()
    fam_bg = {f.key: f.bg_base for f in data.FAMILIES}
    for s in subs:
        bg, acc, adj = derive_colors(fam_bg[s.family], s.accent)
        if adj:
            print(f"  acento ajustado p/ contraste: {s.sid} {s.accent} -> {acc}")
        s.bg, s.accent = bg, acc
    errs = validate(subs)
    if errs:
        print("ERROS:")
        for e in errs:
            print(" -", e)
        return 1
    print(f"OK: {len(subs)} subtipos validos em {len(data.FAMILIES)} familias")
    if args.check:
        return 0

    luau = emit_luau(subs)
    assert not blocked(luau), "o .luau gerado contem caractere bloqueado"
    LUAU_OUT.parent.mkdir(parents=True, exist_ok=True)
    LUAU_OUT.write_text(luau, encoding="utf-8")
    print("escrito", LUAU_OUT.relative_to(ROOT), f"({luau.count(chr(10))} linhas)")

    ART_DIR.mkdir(parents=True, exist_ok=True)
    cols, cell = 16, 64
    atlas = Image.new("RGBA", (cols * cell, 8 * cell), (0, 0, 0, 0))
    rendered = []
    worst = []
    for i, s in enumerate(subs):
        cv = render(s)
        rendered.append((s, cv))
        atlas.paste(cv.to_image(), ((i % cols) * cell, (i // cols) * cell))
        r = lint_canvas(cv, None, s.sid, max_colors=14, kind="background")
        worst.append((r.score, s.sid, r.issues))
    atlas.save(ART_DIR / "SubtypeArtAtlas120.png")
    ATLAS_LUAU_OUT.write_text(emit_atlas_luau(subs, cols, cell), encoding="utf-8")
    print("escrito", ATLAS_LUAU_OUT.relative_to(ROOT))
    if args.hifi:
        k, per_row = 4, 4
        page_cell = 64 * k
        per_page = per_row * per_row
        pages = []
        for pi in range(0, len(rendered), per_page):
            page = Image.new("RGBA", (page_cell * per_row, page_cell * per_row), (0, 0, 0, 0))
            for j, (s_, cv) in enumerate(rendered[pi:pi + per_page]):
                page.paste(cv.scaled(k).to_image(), ((j % per_row) * page_cell, (j // per_row) * page_cell))
            name = f"SubtypeArtAtlas120_x4_p{len(pages) + 1}.png"
            page.save(ART_DIR / name)
            pages.append(name)
        HIFI_LUAU_OUT.write_text(emit_hifi_luau(subs, per_row, page_cell, per_page, len(pages)), encoding="utf-8")
        print(f"hi-fi: {len(pages)} paginas 1024x1024 ->", HIFI_LUAU_OUT.relative_to(ROOT))
    for f in data.FAMILIES:
        items = [(s, cv) for s, cv in rendered if s.family == f.key]
        preview_sheet(items, 7, 2, f"{f.label} ({len(items)})  ~ = isGlitchy").save(ART_DIR / f"preview_{f.key.lower()}.png")
    preview_sheet(rendered, 15, 1, "The Dark Altar - 120 Artes de Subtipo (64x64 nativo)").save(ART_DIR / "preview_all.png")
    worst.sort()
    print("lint (piores 5):")
    for sc, sid, iss in worst[:5]:
        print(f"  {sc:3d} {sid}: {'; '.join(iss[:2])}")
    print("media lint:", round(sum(w[0] for w in worst) / len(worst), 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
