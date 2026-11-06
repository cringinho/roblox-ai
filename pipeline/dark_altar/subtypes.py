"""FONTE DE VERDADE das 120 Artes de Subtipo (The Dark Altar).

Edite AQUI e rode:  python pipeline/dark_altar/build_subtypes.py
Isso gera:
  - src/shared/Config/SubtypeArtCatalog120.luau  (dados tipados --!strict)
  - art/dark-altar/subtypes/*                     (atlas pixel art + previas)

Convencoes dos campos (iguais no Luau):
  bgHex/accentHex : "#RRGGBB". bg e derivado da cor da familia + 10% do acento,
                    com contraste WCAG acento/fundo >= 5.5 garantido pelo gerador.
  etchingPattern  : textura de gravura do fundo (8 tipos).
  centerSilhouettes: emblema CONCENTRICO (todas as formas no centro). scaleX/scaleY
                    em fracao da area da arte (0..1); rotation em graus horarios
                    (igual a GuiObject.Rotation).
  watermarkGlyph  : monograma de fundo (1-2 letras/glifos, sem emoji).
  particleGlyph   : "·" | "†" | "◆" | "~"
  isGlitchy       : tremor por grafema (utf8.graphemes) em subtipos sombrios/abissais.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

PATTERNS = ("SPIKES", "ARCHES", "WAVES", "RAYS", "ABYSS", "ROOTS", "FRACTAL", "SCALES")
SHAPES = ("DIAMOND", "PILLAR", "RING", "BLADE", "CRESCENT", "CROWN")
PARTICLES = ("·", "†", "◆", "~")  # · † ◆ ~

DOT, DAGGER, LOZ, WAVE = PARTICLES


@dataclass(frozen=True)
class Sil:
    shape: str
    sx: float
    sy: float
    rot: float = 0.0


def D(sx, sy, rot=0.0): return Sil("DIAMOND", sx, sy, rot)
def P(sx, sy, rot=0.0): return Sil("PILLAR", sx, sy, rot)
def R(sx, sy, rot=0.0): return Sil("RING", sx, sy, rot)
def B(sx, sy, rot=0.0): return Sil("BLADE", sx, sy, rot)
def C(sx, sy, rot=0.0): return Sil("CRESCENT", sx, sy, rot)
def K(sx, sy, rot=0.0): return Sil("CROWN", sx, sy, rot)


@dataclass
class Family:
    key: str
    label: str
    bg_base: str
    subtypes: List["Subtype"] = field(default_factory=list)


@dataclass
class Subtype:
    sid: str
    name: str
    accent: str
    pattern: str
    sils: List[Sil]
    watermark: str
    particle: str
    glitchy: bool
    family: str = ""
    order: int = 0
    bg: str = ""  # preenchido pelo gerador


FAMILIES: List[Family] = []


def fam(key: str, label: str, bg_base: str) -> Family:
    f = Family(key, label, bg_base)
    FAMILIES.append(f)
    return f


def add(f: Family, sid: str, name: str, accent: str, pattern: str, sils: List[Sil],
        watermark: str, particle: str = DOT, glitchy: bool = False) -> None:
    f.subtypes.append(Subtype(sid, name, accent, pattern, sils, watermark, particle, glitchy, f.key))


# =============================================================== 1. CINZA / NEUTRO (4)
F = fam("NEUTRO", "Cinza/Neutro", "#1B1B21")
add(F, "Treinamento", "Treinamento", "#A3A8B4", "ARCHES", [R(.62, .62), P(.16, .80), D(.14, .14)], "T")
add(F, "Mercenario", "Mercenário", "#B9A37C", "SPIKES", [B(.26, .88, -35), B(.26, .88, 35), R(.24, .24)], "M")
add(F, "Veterano", "Veterano", "#C8CDD6", "ARCHES", [R(.74, .74), B(.24, .92), D(.20, .20, 45)], "V", DAGGER)
add(F, "ReliquiaAncestral", "Relíquia Ancestral", "#E3CF9C", "RAYS", [R(.88, .88), K(.62, .48), D(.18, .18)], "R", LOZ)

# =============================================================== 2. AMARELO-AREIA (9)
F = fam("AREIA", "Amarelo-Areia", "#231B10")
add(F, "Oasis", "Oásis", "#CFE0A0", "WAVES", [R(.84, .34), C(.52, .52, -30), D(.12, .12)], "OA", WAVE)
add(F, "Cacto", "Cacto", "#C2C46A", "SPIKES", [P(.26, .88), P(.18, .62, 90)], "CA")
add(F, "Deserto", "Deserto", "#E6B45E", "RAYS", [R(.66, .66), D(.30, .30), D(.92, .20)], "DS")
add(F, "Duna", "Duna", "#F0C77A", "WAVES", [C(.86, .52, 200), C(.56, .34, 200)], "DU")
add(F, "Fossil", "Fóssil", "#D7C9A6", "SCALES", [R(.72, .72), R(.42, .42), C(.30, .30, 45)], "FS")
add(F, "Escorpiao", "Escorpião", "#E0963A", "SPIKES", [C(.72, .72, -60), B(.20, .62, 180), D(.24, .32)], "ES", DAGGER)
add(F, "TempestadeAreia", "Tempestade de Areia", "#CDAA6A", "WAVES", [C(.88, .88), C(.62, .62, 120), C(.36, .36, 240)], "TA", WAVE)
add(F, "Mumia", "Múmia", "#E2D4B0", "ARCHES", [P(.42, .92), D(.22, .12)], "MU", DAGGER)
add(F, "Farao", "Faraó", "#FFD45C", "RAYS", [R(.92, .92), D(.52, .76), K(.62, .44)], "FA", LOZ)

# =============================================================== 3. VERDE (13)
F = fam("VERDE", "Verde", "#0F1D12")
add(F, "Salada", "Salada", "#A8D86A", "ROOTS", [C(.52, .52, -45), C(.52, .52, 135), D(.16, .16)], "SA")
add(F, "Floresta", "Floresta", "#5FAE5A", "ROOTS", [D(.40, .84), P(.12, .92), R(.86, .86)], "FL")
add(F, "Pinheiro", "Pinheiro", "#4E9C6A", "SPIKES", [D(.54, .92), D(.36, .58), P(.10, .94)], "PI")
add(F, "Inseto", "Inseto", "#9BC44E", "SCALES", [D(.30, .56), B(.16, .84, -42), B(.16, .84, 42)], "IN")
add(F, "Planicie", "Planície", "#B5D07A", "WAVES", [P(.12, .90, 90), R(.40, .40), D(.12, .12)], "PL")
add(F, "Vegetal", "Vegetal", "#7CC46A", "ROOTS", [C(.66, .66, -30), P(.10, .82)], "VG")
add(F, "Legume", "Legume", "#C8B85A", "ROOTS", [C(.42, .88), R(.20, .20)], "LG")
add(F, "Folha", "Folha", "#6FCB7E", "ROOTS", [D(.44, .88, 30), B(.08, .92, 30)], "FO")
add(F, "Ninfa", "Ninfa", "#A6E8B8", "WAVES", [R(.88, .88), C(.70, .70), D(.22, .40)], "NI", LOZ)
add(F, "Natureza", "Natureza", "#8FD45E", "ROOTS", [R(.82, .82), D(.46, .46, 45), D(.14, .14)], "NA")
add(F, "Fruto", "Fruto", "#D8E26A", "ROOTS", [R(.58, .58), D(.12, .32), C(.32, .22, -45)], "FR")
add(F, "Indigena", "Indígena", "#C9D67A", "RAYS", [R(.52, .52), B(.24, .88, -20), B(.24, .88, 20)], "ID")
add(F, "Vida", "Vida", "#9CF0A0", "RAYS", [R(.86, .86), D(.24, .64), D(.64, .24)], "VI", LOZ)

# =============================================================== 4. BRANCO (11)
F = fam("BRANCO", "Branco", "#1A1B24")
add(F, "Ar", "Ar", "#DDE6F0", "WAVES", [C(.82, .82, 30), C(.50, .50, 210)], "AR", WAVE)
add(F, "Vapor", "Vapor", "#CFD8E0", "WAVES", [C(.86, .60), C(.62, .44, 180), C(.38, .28)], "VA", WAVE)
add(F, "Cinzas", "Cinzas", "#BDB8B4", "FRACTAL", [C(.72, .42, 180), R(.50, .50), D(.16, .16)], "CI")
add(F, "Alada", "Alada", "#F0EEE6", "ARCHES", [C(.74, .74, 45), C(.74, .74, 135), D(.16, .30)], "AL")
add(F, "Fantasma", "Fantasma", "#C9D4E8", "ABYSS", [C(.68, .68, 90), R(.36, .36), D(.10, .10)], "FN", WAVE, True)
add(F, "Justica", "Justiça", "#EDE3C8", "ARCHES", [B(.22, .94), P(.08, .82, 90), R(.30, .30)], "JU", "†")
add(F, "Anjo", "Anjo", "#FFF4D6", "RAYS", [R(.64, .22), C(.70, .70, 45), C(.70, .70, 135), D(.14, .28)], "AN", DAGGER)
add(F, "Arcanjo", "Arcanjo", "#FFE9A8", "RAYS", [R(.82, .82), C(.74, .74, 45), C(.74, .74, 135), B(.22, .96)], "AC", DAGGER)
add(F, "Divino", "Divino", "#FFF7E0", "RAYS", [R(.90, .90), D(.36, .92), D(.92, .36)], "DV", LOZ)
add(F, "Semideus", "Semideus", "#F2DFA2", "ARCHES", [R(.86, .86), P(.20, .62), K(.60, .42)], "SD", DAGGER)
add(F, "Serafim", "Serafim", "#FFF8EC", "RAYS", [C(.86, .86, 0), C(.86, .86, 120), C(.86, .86, 240), R(.30, .30)], "SF", DAGGER)

# =============================================================== 5. AZUL-CLARO (10)
F = fam("AZUL_CLARO", "Azul-Claro", "#0B1B25")
add(F, "Gelo", "Gelo", "#9EE6F2", "FRACTAL", [D(.56, .88), D(.30, .50)], "GE", LOZ)
add(F, "Cristal", "Cristal", "#7FE0F0", "FRACTAL", [D(.36, .92), D(.26, .66, -30), D(.26, .66, 30)], "CR", LOZ)
add(F, "Peixe", "Peixe", "#5FC8E8", "SCALES", [D(.82, .42), B(.14, .40, 90), R(.12, .12)], "PX", WAVE)
add(F, "Raio", "Raio", "#BDEBFF", "RAYS", [D(.18, .92, 20), D(.18, .62, -20), R(.80, .80)], "RA")
add(F, "Geada", "Geada", "#B8EEF5", "FRACTAL", [B(.12, .92), B(.12, .92, 60), B(.12, .92, 120), D(.20, .20)], "GD", LOZ)
add(F, "Nevasca", "Nevasca", "#D6F4FA", "WAVES", [R(.88, .88), B(.10, .80), B(.10, .80, 60), B(.10, .80, 120)], "NV", WAVE)
add(F, "Espirito", "Espírito", "#8FF0E8", "ABYSS", [C(.72, .72, -30), R(.48, .48), D(.14, .14)], "EP", WAVE)
add(F, "Diamante", "Diamante", "#CFF8FF", "FRACTAL", [R(.92, .92), D(.66, .90), D(.36, .50)], "DI", LOZ)
add(F, "Plasma", "Plasma", "#7FD9FF", "RAYS", [R(.82, .82), R(.50, .50), D(.20, .20, 45)], "PM")
add(F, "Aurora", "Aurora", "#9DF5C8", "WAVES", [C(.92, .62), C(.70, .46), C(.48, .32)], "AU", WAVE)

# =============================================================== 6. AZUL-ESCURO (11)
F = fam("AZUL_ESCURO", "Azul-Escuro", "#090E22")
add(F, "Oceano", "Oceano", "#4F86E8", "WAVES", [R(.88, .88), C(.86, .52)], "OC", WAVE)
add(F, "Mar", "Mar", "#5B9CF0", "WAVES", [C(.80, .48), C(.54, .34, 180)], "MA", WAVE)
add(F, "Onda", "Onda", "#79B4FF", "WAVES", [C(.86, .86, -45), C(.50, .50, -45)], "ON", WAVE)
add(F, "Sereia", "Sereia", "#7FC6E8", "SCALES", [C(.62, .62, 90), R(.36, .36), K(.42, .28)], "SR", WAVE)
add(F, "AbismoMarinho", "Abismo Marinho", "#3E6FD8", "ABYSS", [R(.92, .92), R(.62, .62), R(.32, .32)], "AM", WAVE, True)
add(F, "Espaco", "Espaço", "#8E9CFF", "ABYSS", [R(.90, .32, -20), R(.40, .40), D(.12, .12)], "EÇ")
add(F, "Estrela", "Estrela", "#CFD8FF", "RAYS", [D(.30, .92), D(.92, .30), D(.46, .46, 45)], "ET", LOZ)
add(F, "Cometa", "Cometa", "#A9C2FF", "RAYS", [B(.28, .92, -45), R(.30, .30)], "CO")
add(F, "Profundeza", "Profundeza", "#2F5BC4", "ABYSS", [C(.88, .88, 180), R(.46, .46), P(.10, .40)], "PF", WAVE, True)
add(F, "Leviata", "Leviatã", "#4FA0D8", "SCALES", [C(.92, .92), C(.62, .62, 180), D(.18, .30)], "LV", WAVE, True)
add(F, "Dimensao", "Dimensão", "#8A7CFF", "ABYSS", [D(.88, .88), D(.62, .62, 45), R(.30, .30)], "DM", LOZ, True)

# =============================================================== 7. MARROM (10)
F = fam("MARROM", "Marrom", "#1D120A")
add(F, "Terra", "Terra", "#B98A55", "ROOTS", [D(.82, .52), P(.12, .60)], "TE")
add(F, "Lama", "Lama", "#9C7A52", "WAVES", [C(.82, .42, 180), R(.40, .40)], "LA", WAVE)
add(F, "Pantano", "Pântano", "#8A9A5A", "WAVES", [C(.80, .40, 180), P(.10, .82, -15), P(.10, .82, 15)], "PN", WAVE)
add(F, "Madeira", "Madeira", "#C08A4E", "ROOTS", [R(.62, .62), R(.32, .32), P(.36, .94)], "MD")
add(F, "Caranguejo", "Caranguejo", "#E07A4E", "SCALES", [D(.62, .38), C(.44, .44, -45), C(.44, .44, 225)], "CG")
add(F, "RaizPetrificada", "Raiz Petrificada", "#A89A86", "ROOTS", [P(.20, .92), B(.12, .82, 40), B(.12, .82, -40)], "RP")
add(F, "Desmatamento", "Desmatamento", "#8C5A3A", "ROOTS", [P(.50, .50), B(.16, .88, 45)], "DT", DAGGER)
add(F, "Aracnideo", "Aracnídeo", "#C46A4E", "SPIKES", [D(.30, .42), B(.10, .92, 30), B(.10, .92, -30), B(.10, .92, 70), B(.10, .92, -70)], "AK", DAGGER)
add(F, "Terremoto", "Terremoto", "#D19A5A", "FRACTAL", [D(.92, .30), B(.14, .92, 15), D(.20, .20)], "TM")
add(F, "GolemBarro", "Golem de Barro", "#B07A4A", "ROOTS", [P(.62, .88), D(.22, .14), K(.50, .30)], "GB")

# =============================================================== 8. PRETO (11)
F = fam("PRETO", "Preto", "#0A090E")
add(F, "Obsidiana", "Obsidiana", "#7A6FA0", "FRACTAL", [D(.52, .92), D(.30, .62, 30)], "OB", LOZ)
add(F, "Lixo", "Lixo", "#8A8F6A", "SPIKES", [R(.62, .62), D(.30, .30, 20), C(.40, .40, 200)], "LX")
add(F, "Petroleo", "Petróleo", "#6F6A9A", "WAVES", [C(.82, .82), R(.50, .50), D(.14, .26)], "PT", WAVE)
add(F, "Pedra", "Pedra", "#8C8C96", "FRACTAL", [D(.82, .62, 10), D(.40, .30, -10)], "PD")
add(F, "Aco", "Aço", "#B4BCC8", "SCALES", [R(.62, .62), B(.30, .94)], "AÇ")
add(F, "Montanha", "Montanha", "#9A96A8", "SPIKES", [D(.92, .80), D(.50, .44)], "MT")
add(F, "Sombra", "Sombra", "#6A5A8A", "ABYSS", [C(.88, .88, 200), R(.42, .42)], "SB", WAVE, True)
add(F, "AcoNegro", "Aço Negro", "#9AA0B8", "SCALES", [B(.24, .92, -35), B(.24, .92, 35), D(.24, .24)], "AN", DAGGER)
add(F, "Void", "Void", "#8B6BFF", "ABYSS", [R(.92, .92), R(.66, .66), R(.40, .40)], "VO", DOT, True)
add(F, "Vulcao", "Vulcão", "#FF6A3D", "RAYS", [D(.92, .72), B(.16, .60, 180), D(.20, .20)], "VU")
add(F, "Eclipse", "Eclipse", "#FFB84D", "ABYSS", [R(.88, .88), R(.66, .66), C(.52, .52)], "EC", DOT, True)

# =============================================================== 9. ROSA (10)
F = fam("ROSA", "Rosa", "#210E1C")
add(F, "Fada", "Fada", "#FFA3D1", "FRACTAL", [C(.68, .68, 45), C(.68, .68, 135), D(.18, .40)], "FD", LOZ)
add(F, "Fofo", "Fofo", "#FFC2DD", "WAVES", [R(.62, .62), R(.34, .34), D(.12, .12)], "FF")
add(F, "Brilho", "Brilho", "#FFE1F0", "RAYS", [D(.30, .92), D(.92, .30), D(.40, .40, 45)], "BR", LOZ)
add(F, "Espelho", "Espelho", "#E8D0F0", "FRACTAL", [R(.66, .90), P(.12, .42), D(.16, .16)], "EL", LOZ)
add(F, "Fragmentacao", "Fragmentação", "#E58AC0", "FRACTAL", [D(.70, .70), D(.46, .46, 30), D(.24, .24, 60)], "FG", LOZ, True)
add(F, "Beleza", "Beleza", "#FF9EC4", "ARCHES", [R(.86, .86), D(.30, .50), K(.50, .36)], "BE", LOZ)
add(F, "Ilusao", "Ilusão", "#D59CFF", "FRACTAL", [R(.90, .60), R(.60, .90), D(.20, .20)], "IL", DOT, True)
add(F, "Prisma", "Prisma", "#FFC4F2", "RAYS", [D(.70, .90), B(.10, .90, 60), B(.10, .90, -60)], "PR", LOZ)
add(F, "ArcoIris", "Arco-Íris", "#FFB3C8", "ARCHES", [C(.92, .92, 135), C(.66, .66, 135), C(.40, .40, 135)], "AI")
add(F, "MiragemAstral", "Miragem Astral", "#E7A6FF", "ABYSS", [R(.88, .40, -25), D(.30, .30), C(.56, .56)], "MG", LOZ, True)

# =============================================================== 10. VERMELHO (11)
F = fam("VERMELHO", "Vermelho", "#230A0B")
add(F, "Fogo", "Fogo", "#FF7A3D", "RAYS", [D(.40, .92), D(.24, .62, -25), D(.24, .62, 25)], "FO")
add(F, "Lava", "Lava", "#FF5A2E", "WAVES", [C(.86, .42, 180), R(.40, .40)], "LA")
add(F, "Dragonoide", "Dragonoide", "#E8463A", "SCALES", [C(.82, .82, -20), D(.40, .62)], "DR")
add(F, "Bomba", "Bomba", "#FFB347", "RAYS", [R(.66, .66), B(.10, .52, 45), D(.16, .16)], "BO")
add(F, "Forja", "Forja", "#FF8F3F", "RAYS", [P(.50, .42, 90), B(.22, .88), D(.16, .16)], "FJ")
add(F, "Demonio", "Demônio", "#E0303B", "SPIKES", [C(.52, .52, -45), C(.52, .52, 225), D(.20, .36)], "DE", DAGGER, True)
add(F, "Inferno", "Inferno", "#FF4A1F", "SPIKES", [D(.36, .92), D(.22, .66, -30), D(.22, .66, 30), K(.70, .40)], "IF", DAGGER)
add(F, "Solar", "Solar", "#FFC94A", "RAYS", [R(.60, .60), D(.94, .24), D(.24, .94)], "SO")
add(F, "Destruicao", "Destruição", "#F2553A", "FRACTAL", [B(.20, .92, 45), B(.20, .92, -45), D(.24, .24)], "DT", DAGGER)
add(F, "Supernova", "Supernova", "#FFE07A", "RAYS", [R(.92, .92), D(.36, .94), D(.94, .36), D(.50, .50, 45)], "SN", LOZ)
add(F, "Dragao", "Dragão", "#FF3B30", "SCALES", [C(.92, .92), K(.42, .30), D(.18, .26)], "DG", DAGGER)

# =============================================================== 11. ROXO (10)
F = fam("ROXO", "Roxo", "#170D27")
add(F, "Maldicao", "Maldição", "#B388FF", "SPIKES", [R(.86, .86), C(.70, .70, -90), D(.20, .20)], "ML", DAGGER)
add(F, "Veneno", "Veneno", "#C08CF2", "WAVES", [D(.40, .66), R(.30, .30)], "VN", WAVE)
add(F, "Peso", "Peso", "#9C8AC8", "ARCHES", [D(.82, .52), P(.12, .52)], "PE")
add(F, "Trevas", "Trevas", "#7A5ACF", "ABYSS", [C(.86, .86, 160), C(.50, .50, -20)], "TR", WAVE, True)
add(F, "Hydra", "Hydra", "#A07CFF", "SCALES", [C(.62, .62, -40), C(.62, .62, 0), C(.62, .62, 40)], "HY", DAGGER)
add(F, "Corrupcao", "Corrupção", "#C25BFF", "ROOTS", [D(.50, .50, 45), B(.12, .90, 30), B(.12, .90, -30)], "CP", WAVE, True)
add(F, "Micelio", "Micélio", "#B49AE8", "ROOTS", [R(.62, .36), P(.16, .62), D(.12, .12)], "MC")
add(F, "Peste", "Peste", "#9D7AD6", "FRACTAL", [R(.80, .80), R(.46, .46), D(.22, .22, 45)], "PT")
add(F, "Necromante", "Necromante", "#C9B0FF", "ABYSS", [B(.14, .94), C(.52, .52, -90), D(.20, .20)], "NC", DAGGER, True)
add(F, "Lich", "Lich", "#D9C4FF", "ABYSS", [R(.86, .86), K(.66, .46), D(.20, .30)], "LI", DAGGER, True)

# =============================================================== 12. VINHO (10)
F = fam("VINHO", "Vinho", "#1E070E")
add(F, "Vinho", "Vinho", "#C0384F", "WAVES", [R(.52, .52), P(.12, .62)], "VH", WAVE)
add(F, "Vampiro", "Vampiro", "#E0435A", "SPIKES", [C(.86, .60, 90), B(.18, .62, 170), B(.18, .62, 190)], "VP", DAGGER)
add(F, "Sangue", "Sangue", "#D42A3E", "WAVES", [D(.50, .80), R(.30, .30)], "SG")
add(F, "Parasita", "Parasita", "#B04A6A", "ROOTS", [C(.70, .70, 30), C(.42, .42, 210), D(.16, .16)], "PA", WAVE)
add(F, "Controle", "Controle", "#C46A8A", "RAYS", [K(.62, .40, 180), B(.08, .90), R(.30, .30)], "CT", DOT, True)
add(F, "Mutacao", "Mutação", "#E05A7A", "FRACTAL", [D(.62, .42, 20), D(.42, .62, -20), R(.30, .30)], "MU", WAVE, True)
add(F, "Hemorragia", "Hemorragia", "#FF4D5E", "WAVES", [D(.30, .62, -30), D(.30, .62), D(.30, .62, 30)], "HM")
add(F, "GengivaGotica", "Gengiva Gótica", "#E87A8E", "SPIKES", [C(.90, .62, 90), D(.16, .40, -20), D(.16, .40, 20)], "GG", DAGGER)
add(F, "PactoSanguineo", "Pacto Sanguíneo", "#C02040", "ARCHES", [R(.66, .66), B(.20, .92), D(.30, .30, 45)], "PS", DAGGER)
add(F, "Nosferatu", "Nosferatu", "#C9405A", "ABYSS", [C(.86, .86), P(.40, .92), D(.16, .16)], "NO", DAGGER, True)


def all_subtypes() -> List[Subtype]:
    out: List[Subtype] = []
    n = 0
    for f in FAMILIES:
        for i, s in enumerate(f.subtypes):
            n += 1
            s.order = n
            s.family = f.key
            out.append(s)
    return out


EXPECTED_COUNTS = {
    "NEUTRO": 4, "AREIA": 9, "VERDE": 13, "BRANCO": 11, "AZUL_CLARO": 10, "AZUL_ESCURO": 11,
    "MARROM": 10, "PRETO": 11, "ROSA": 10, "VERMELHO": 11, "ROXO": 10, "VINHO": 10,
}
