"""Paleta: rampas nomeadas (do escuro ao claro), materiais padrao e matematica de cor.

Arquivos lidos de registro/paletas/*.json:
  {"id": "paleta.altar", "tipo": "paleta", "versao": 1, "rampas": {"bone": ["#382B1D", ...], ...}}
  {"id": "paleta.materiais", "tipo": "materiais", "versao": 1,
   "materiais": {"pele": {"rampa": "pele_marfim", "perfil": "pele", "brilho": false, "tom": 3, "opcoes": {...}}}}

Rampa por faixa: uma rampa longa pode ser usada em parte. "slate[2:7]" = degraus 2, 3, 4, 5 e 6 de "slate"
(mesma regra de fatia do Python: o primeiro entra, o ultimo nao). E assim que um Material escolhe os degraus.

Valor = L do OKLab, de 0 (preto) a 1 (branco). Matiz = angulo do OKLCh em graus
(vermelho ~30, laranja ~60, amarelo ~100, verde ~140, ciano ~200, azul ~260, roxo ~300, rosa ~350).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np

from .contrato import Material

RAIZ = Path(__file__).resolve().parents[2]
PASTA_PALETAS = RAIZ / "registro" / "paletas"

PERFIS = ("pele", "tecido", "couro", "metal", "osso", "pedra", "madeira", "cabelo", "fungo", "brilho", "chapado")

MATIZ_FRIO = 290.0     # roxo: para onde a sombra puxa
MATIZ_QUENTE = 95.0    # amarelo: para onde a luz puxa

_RE_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
_RE_FAIXA = re.compile(r"^([A-Za-z0-9_]+)\[(-?\d*):(-?\d*)\]$")


# --------------------------------------------------------------------------- conversoes

def hex_para_rgb(cor: str) -> tuple[int, int, int]:
    if not isinstance(cor, str) or not _RE_HEX.match(cor):
        raise ValueError(f'cor {cor!r} invalida; use hex "#RRGGBB" com 6 digitos, ex.: "#A02F3C"')
    return int(cor[1:3], 16), int(cor[3:5], 16), int(cor[5:7], 16)


def rgb_para_hex(rgb) -> str:
    r, g, b = (int(np.clip(round(float(c)), 0, 255)) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def srgb_para_linear(c) -> np.ndarray:
    """sRGB 0..1 -> linear 0..1."""
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_para_srgb(c) -> np.ndarray:
    c = np.asarray(c, dtype=np.float64)
    c = np.clip(c, 0.0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1_INV = np.linalg.inv(_M1)
_M2_INV = np.linalg.inv(_M2)


def rgb_para_oklab(rgb) -> np.ndarray:
    """RGB 0..255 [..., 3] -> OKLab [..., 3] (L em 0..1)."""
    lin = srgb_para_linear(np.asarray(rgb, dtype=np.float64) / 255.0)
    lms = np.cbrt(lin @ _M1.T)
    return lms @ _M2.T


def oklab_para_rgb(lab, cortar: bool = True) -> np.ndarray:
    """OKLab [..., 3] -> RGB 0..255 float (com cortar=True, preso em 0..255)."""
    lms = np.asarray(lab, dtype=np.float64) @ _M2_INV.T
    lin = (lms ** 3) @ _M1_INV.T
    rgb = linear_para_srgb(lin) * 255.0
    return np.clip(rgb, 0.0, 255.0) if cortar else rgb


def _lab(cor) -> np.ndarray:
    return rgb_para_oklab(hex_para_rgb(cor) if isinstance(cor, str) else cor)


def valor(cor) -> float:
    """Valor perceptual (L do OKLab), 0 = preto, 1 = branco. Aceita hex ou (r, g, b)."""
    return float(_lab(cor)[0])


def croma(cor) -> float:
    lab = _lab(cor)
    return float(np.hypot(lab[1], lab[2]))


def matiz(cor) -> float:
    """Matiz em graus (0..360) no OKLCh. Cinza puro devolve 0."""
    lab = _lab(cor)
    return float(np.degrees(np.arctan2(lab[2], lab[1])) % 360.0)


def _dif_angulo(a: float, b: float) -> float:
    """b - a no intervalo (-180, 180]."""
    d = (b - a + 180.0) % 360.0 - 180.0
    return 180.0 if d == -180.0 else d


def desvio_matiz(cores: Sequence[str], croma_min: float = 0.02) -> list[float]:
    """Desvio de matiz, em graus com sinal, entre cada degrau e o seguinte.
    Degrau quase cinza (croma < croma_min) nao tem matiz confiavel: o desvio que o envolve vale 0."""
    saida = []
    for a, b in zip(cores[:-1], cores[1:]):
        if croma(a) < croma_min or croma(b) < croma_min:
            saida.append(0.0)
        else:
            saida.append(_dif_angulo(matiz(a), matiz(b)))
    return saida


def lch_para_hex(L: float, C: float, h: float, canal_min: int = 10, canal_max: int = 245) -> str:
    """OKLCh -> hex, reduzindo o croma ate caber no sRGB e nos limites de canal [canal_min, canal_max]."""
    rad = np.radians(h)

    def tenta(c: float):
        rgb = oklab_para_rgb(np.array([L, c * np.cos(rad), c * np.sin(rad)]), cortar=False)
        return rgb, bool(rgb.min() >= canal_min - 0.5 and rgb.max() <= canal_max + 0.5)

    rgb, cabe = tenta(float(C))
    if not cabe:
        lo, hi = 0.0, float(C)
        achado = None
        for _ in range(24):
            meio = (lo + hi) / 2.0
            r, ok = tenta(meio)
            if ok:
                lo, achado = meio, r
            else:
                hi = meio
        rgb = achado if achado is not None else tenta(0.0)[0]
    return rgb_para_hex(np.clip(rgb, canal_min, canal_max))


def gerar_rampa(cor_base: str, n: int = 5, *, passo_valor: float = 0.10, desvio: float = 10.0,
                degrau_base: Optional[int] = None, matiz_frio: float = MATIZ_FRIO,
                matiz_quente: float = MATIZ_QUENTE) -> list[str]:
    """Gera uma rampa de n tons (escuro -> claro) a partir de uma cor-base.

    A cor-base fica no degrau `degrau_base` (padrao: o do meio). Para baixo escurece `passo_valor` por degrau,
    puxa o matiz para o frio/roxo (`desvio` graus por degrau) e perde croma; para cima clareia, puxa para o
    quente/amarelo e perde croma. Nenhum canal sai de 10..245 (nada de preto ou branco puros).
    """
    if not 4 <= n <= 7:
        raise ValueError(f"gerar_rampa: n={n} fora do aceito; use de 4 a 7 tons, ex.: n=5")
    lab = _lab(cor_base)
    L0, C0 = float(lab[0]), float(np.hypot(lab[1], lab[2]))
    h0 = float(np.degrees(np.arctan2(lab[2], lab[1])) % 360.0)
    b = n // 2 if degrau_base is None else int(np.clip(degrau_base, 0, n - 1))
    # cabe na faixa util de valor sem encostar em preto/branco
    L0 = float(np.clip(L0, 0.17 + passo_valor * b, 0.95 - passo_valor * (n - 1 - b)))
    cores = []
    for i in range(n):
        k = i - b
        L = L0 + passo_valor * k
        if k < 0:
            alvo = matiz_frio
            C = C0 * (1.0 - 0.16 * (-k)) + 0.012 * (-k)       # sombra: menos croma, mas nunca cinza morto
        else:
            alvo = matiz_quente
            C = C0 * (1.0 - 0.20 * k)
        d = _dif_angulo(h0, alvo)
        giro = np.sign(d) * min(abs(d), desvio * abs(k))
        cores.append(lch_para_hex(L, max(C, 0.0), (h0 + giro) % 360.0))
    return cores


def validar_rampa(cores: Sequence[str], *, min_tons: int = 4, max_tons: int = 7, passo_min: float = 0.02,
                  desvio_min: float = 4.0, croma_neutro: float = 0.035, nome: str = "rampa") -> list[str]:
    """Confere uma rampa. Devolve a lista de problemas (vazia = rampa valida). Regras:
      - de min_tons a max_tons tons, em hex #RRGGBB;
      - nada de #000000 nem #FFFFFF;
      - valor (L do OKLab) crescente do primeiro ao ultimo, com passo de ao menos `passo_min`;
      - desvio de matiz: a rampa colorida (croma maximo >= croma_neutro) precisa girar ao menos
        `desvio_min` graus do tom mais escuro ao mais claro (rampa reta = so o brilho muda = reprovada).
        Rampas neutras (cinzas) ficam isentas.
    """
    prob: list[str] = []
    cores = list(cores)
    for i, c in enumerate(cores):
        if not isinstance(c, str) or not _RE_HEX.match(c):
            prob.append(f'{nome}: o tom {i} ({c!r}) nao e hex "#RRGGBB"; ex.: "#5D4D38"')
    if prob:
        return prob
    if not min_tons <= len(cores) <= max_tons:
        prob.append(f"{nome}: tem {len(cores)} tons; o aceito e de {min_tons} a {max_tons}. "
                    f'Use uma faixa, ex.: "{nome}[0:{max_tons}]", ou acrescente tons')
    for i, c in enumerate(cores):
        if c.upper() in ("#000000", "#FFFFFF"):
            prob.append(f"{nome}: o tom {i} e {c.upper()} (preto ou branco puro); use um tom com matiz, "
                        f'ex.: "#0B0A12" no lugar de preto, "#F4EEDD" no lugar de branco')
    vals = [valor(c) for c in cores]
    for i in range(len(vals) - 1):
        if vals[i + 1] - vals[i] < passo_min:
            prob.append(f"{nome}: o valor nao sobe do tom {i} ({cores[i]}, L={vals[i]:.2f}) para o tom {i + 1} "
                        f"({cores[i + 1]}, L={vals[i + 1]:.2f}); a rampa vai do escuro ao claro com passo de ao "
                        f"menos {passo_min:.2f}. Reordene ou clareie o tom {i + 1}")
    if len(cores) >= 2 and max(croma(c) for c in cores) >= croma_neutro:
        coloridos = [c for c in cores if croma(c) >= 0.02]
        giro = abs(sum(desvio_matiz(coloridos))) if len(coloridos) >= 2 else 0.0
        if giro < desvio_min:
            prob.append(f"{nome}: rampa reta, o matiz gira so {giro:.1f} graus do escuro ao claro (minimo "
                        f"{desvio_min:.0f}). Puxe a sombra para o frio/roxo e a luz para o quente/amarelo; "
                        f'ex.: gerar_rampa("{cores[len(cores) // 2]}", {min(max(len(cores), 4), 7)})')
    return prob


def canais_fora(cores: Sequence[str], canal_min: int = 10, canal_max: int = 245) -> list[str]:
    """Cores com algum canal RGB fora de [canal_min, canal_max] (aviso de arte: sem folga para a luz do motor)."""
    return [c for c in cores if min(hex_para_rgb(c)) < canal_min or max(hex_para_rgb(c)) > canal_max]


def quantizar(imagem_rgb, cores: Sequence) -> tuple[np.ndarray, np.ndarray]:
    """Prende cada pixel a cor mais proxima (distancia no OKLab) de `cores` (hex ou (r, g, b)).

    imagem_rgb: array [..., 3] 0..255. Devolve (indices int32 [...] em `cores`, imagem uint8 [..., 3])."""
    img = np.asarray(imagem_rgb)
    tabela = np.array([hex_para_rgb(c) if isinstance(c, str) else tuple(c)[:3] for c in cores], dtype=np.float64)
    if len(tabela) == 0:
        raise ValueError("quantizar: a lista de cores esta vazia; passe ao menos uma cor, ex.: ['#382B1D', '#F4EEDD']")
    lab_t = rgb_para_oklab(tabela)
    plano = img.reshape(-1, 3)
    unicos, inverso = np.unique(plano, axis=0, return_inverse=True)
    lab_u = rgb_para_oklab(unicos)
    idx_u = np.empty(len(unicos), dtype=np.int32)
    for i in range(0, len(unicos), 4096):
        d = ((lab_u[i:i + 4096, None, :] - lab_t[None, :, :]) ** 2).sum(-1)
        idx_u[i:i + 4096] = np.argmin(d, axis=1)
    idx = idx_u[inverso.reshape(-1)].reshape(img.shape[:-1])
    return idx, tabela[idx].astype(np.uint8)


# --------------------------------------------------------------------------- Paleta

class Paleta:
    """Rampas nomeadas e tabela de materiais padrao."""

    def __init__(self, rampas: Optional[dict[str, list[str]]] = None, materiais: Optional[dict[str, dict]] = None):
        self.rampas: dict[str, list[str]] = {}
        self.tabela_materiais: dict[str, dict] = {}
        self.origem: dict[str, str] = {}
        for nome, cores in (rampas or {}).items():
            self.adicionar_rampa(nome, cores, validar=False)
        for nome, d in (materiais or {}).items():
            self.tabela_materiais[nome] = dict(d)

    # ---- carga
    @classmethod
    def carregar(cls, pasta: Optional[Path | str] = None) -> "Paleta":
        """Le todos os *.json da pasta (padrao: registro/paletas), em ordem alfabetica."""
        pasta = Path(pasta) if pasta else PASTA_PALETAS
        arquivos = sorted(pasta.glob("*.json"))
        if not arquivos:
            raise FileNotFoundError(f"nenhuma paleta em {pasta}; esperava arquivos como altar.json e materiais.json")
        p = cls()
        for arq in arquivos:
            try:
                dados = json.loads(arq.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise ValueError(f"{arq.name}: JSON invalido na linha {e.lineno}, coluna {e.colno}: {e.msg}") from None
            for nome, cores in dados.get("rampas", {}).items():
                if nome in p.rampas:
                    raise ValueError(f'{arq.name}: a rampa "{nome}" ja existe em {p.origem[nome]}; '
                                     f"de outro nome a uma delas")
                p.adicionar_rampa(nome, cores, validar=False)
                p.origem[nome] = arq.name
            for nome, d in dados.get("materiais", {}).items():
                p.tabela_materiais[nome] = dict(d)
        return p

    # ---- rampas
    def adicionar_rampa(self, nome: str, cores: Sequence[str], validar: bool = True, max_tons: int = 9) -> None:
        cores = [c.upper() for c in cores]
        if validar:
            prob = validar_rampa(cores, max_tons=max_tons, nome=nome)
            if prob:
                raise ValueError("rampa recusada:\n  - " + "\n  - ".join(prob))
        else:
            for c in cores:
                hex_para_rgb(c)
        self.rampas[nome] = cores

    def nomes_rampas(self) -> list[str]:
        return sorted(self.rampas)

    def tem_rampa(self, nome: str) -> bool:
        try:
            self.rampa(nome)
            return True
        except (KeyError, ValueError):
            return False

    def rampa(self, nome: str) -> list[str]:
        """Tons da rampa, do escuro ao claro. Aceita faixa: "slate[2:7]"."""
        if isinstance(nome, str) and nome.startswith("#"):          # "rampa": "#8A3FD1" gera 5 tons em volta dessa cor
            return gerar_rampa(nome, 5)
        m = _RE_FAIXA.match(nome) if isinstance(nome, str) else None
        base = m.group(1) if m else nome
        if base not in self.rampas:
            raise KeyError(f'rampa "{base}" nao existe; existem: {self.nomes_rampas()}. '
                           f'Ex.: "rampa": "bone" ou, por faixa, "slate[2:7]"')
        cores = self.rampas[base]
        if m:
            ini = int(m.group(2)) if m.group(2) else None
            fim = int(m.group(3)) if m.group(3) else None
            cores = cores[ini:fim]
            if not cores:
                raise ValueError(f'faixa vazia em "{nome}": a rampa "{base}" tem {len(self.rampas[base])} tons '
                                 f'(degraus 0 a {len(self.rampas[base]) - 1}); ex.: "{base}[0:{min(5, len(self.rampas[base]))}]"')
        return list(cores)

    def cor(self, rampa: str, degrau: int) -> str:
        """Cor do degrau (0 = mais escuro). Degrau fora da rampa e preso na ponta."""
        cores = self.rampa(rampa)
        return cores[int(np.clip(degrau, 0, len(cores) - 1))]

    # ---- materiais
    def nomes_materiais(self) -> list[str]:
        return sorted(self.tabela_materiais)

    def material(self, nome: str, *, como: Optional[str] = None, rampa: Optional[str] = None,
                 perfil: Optional[str] = None, brilho: Optional[bool] = None, tom: Optional[int] = None) -> Material:
        """Material padrao pelo nome. `como` renomeia; rampa/perfil/brilho/tom trocam campos.
        Ex.: paleta.material("tecido", como="tunica", rampa="blood[0:6]")."""
        if nome not in self.tabela_materiais:
            raise KeyError(f'material "{nome}" nao esta na tabela padrao; existem: {self.nomes_materiais()}. '
                           f'Ou crie um na ficha, ex.: {{"nome": "{nome}", "rampa": "bone", "perfil": "osso"}}')
        d = self.tabela_materiais[nome]
        m = Material(nome=como or nome, rampa=rampa or d["rampa"], perfil=perfil or d.get("perfil", "tecido"),
                     brilho=d.get("brilho", False) if brilho is None else bool(brilho),
                     tom=int(d.get("tom", -1)) if tom is None else int(tom))
        self.conferir_material(m)
        return m

    def materiais(self, nomes: Iterable[str]) -> list[Material]:
        return [self.material(n) for n in nomes]

    def opcoes(self, nome_material: str) -> dict:
        """Opcoes de pintura do material padrao (ex.: {"pintas": {...}}). Material desconhecido = {}."""
        return dict(self.tabela_materiais.get(nome_material, {}).get("opcoes", {}))

    def conferir_material(self, m: Material) -> None:
        """Levanta ValueError (que ensina) se o material aponta para rampa/perfil que nao existem."""
        if m.perfil not in PERFIS:
            raise ValueError(f'material "{m.nome}": perfil "{m.perfil}" nao existe; use um de {list(PERFIS)}, '
                             f'ex.: "perfil": "tecido"')
        try:
            cores = self.rampa(m.rampa)
        except KeyError as e:
            raise ValueError(f'material "{m.nome}": {e.args[0]}') from None
        if m.perfil not in ("brilho", "chapado") and not 4 <= len(cores) <= 7:
            raise ValueError(f'material "{m.nome}": a rampa "{m.rampa}" tem {len(cores)} tons; um material usa de 4 a 7. '
                             f'Escolha uma faixa, ex.: "{m.rampa.split("[")[0]}[0:{min(6, len(cores))}]"')
        if m.tom >= len(cores):
            raise ValueError(f'material "{m.nome}": tom {m.tom} nao existe na rampa "{m.rampa}" '
                             f"({len(cores)} tons: degraus 0 a {len(cores) - 1}); use -1 para o tom do meio")

    # ---- validacao
    def validar(self) -> list[str]:
        """Confere todas as rampas (ate 9 tons na rampa-mestre) e todos os materiais padrao (4 a 7 tons na faixa)."""
        prob: list[str] = []
        for nome in self.nomes_rampas():
            prob += validar_rampa(self.rampas[nome], max_tons=9, nome=nome)
        for nome in self.nomes_materiais():
            try:
                self.material(nome)
            except (ValueError, KeyError) as e:
                prob.append(str(e.args[0]))
        return prob
