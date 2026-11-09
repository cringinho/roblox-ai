"""Contrato da Fabrica de Voxel: tipos e matematica comuns a todos os modulos.

NAO mude assinaturas nem convencoes deste arquivo sem atualizar docs/ARQUITETURA.md.

Convencoes (resumo; a versao completa esta em docs/ARQUITETURA.md, secao 2):
  - Unidade: stud. Chao em Y = 0. +Y cima. FRENTE = -Z. +X = lado direito da criatura (_D).
  - Grades numpy indexadas [x, y, z]. Centro do voxel (i, j, k) = origem + (i + .5, j + .5, k + .5) * v.
  - Rotacao semantica em graus: frente (topo vai para -Z), esquerda (vira para _E), tombar_direita (topo vai para +X).
    R = Ry(esquerda) . Rx(-frente) . Rz(-tombar_direita)
  - Quaternion [x, y, z, w]. Matrizes 4x4 atuam em vetores coluna (p' = M @ p).
  - O repouso de todo osso tem os eixos do modelo (sem rotacao). Um osso so guarda o pivo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

VERSAO_FABRICA = "4.0.0"

# Lado do voxel, em studs, por corte.
CORTES: dict[str, float] = {"mundo": 0.25, "grade": 0.125, "perto": 0.0625, "susto": 0.03125}

LADRILHO = 4.0  # studs
CLASSES_TAMANHO: dict[str, float] = {"P": 3.0, "M": 4.0, "G": 5.0}  # altura H do heroi, em studs
FPS = 30

# Nomes canonicos de clipe e apelidos antigos aceitos na leitura.
CLIPES_CANONICOS = ("Parado", "Andar", "Correr", "Alerta", "Preparar", "Ataque", "Dano", "Morte", "Susto")
APELIDOS_CLIPE = {"Ocioso": "Parado", "Passo": "Andar", "Mover": "Andar"}

# Eixos do modelo.
CIMA = np.array([0.0, 1.0, 0.0])
FRENTE = np.array([0.0, 0.0, -1.0])
DIREITA = np.array([1.0, 0.0, 0.0])


# --------------------------------------------------------------------------- matematica

def desloc_semantico(d: Optional[dict]) -> np.ndarray:
    """{"frente": a, "cima": b, "direita": c} -> vetor [dx, dy, dz] (dz = -frente).

    Aceita tambem "tras" (= -frente), "baixo" (= -cima) e "esquerda" (= -direita).
    """
    if not d:
        return np.zeros(3)
    conhecidos = {"frente", "tras", "cima", "baixo", "direita", "esquerda"}
    extras = set(d) - conhecidos
    if extras:
        raise ValueError(
            f"deslocamento com chave desconhecida {sorted(extras)}; use {sorted(conhecidos)}, "
            'ex.: {"frente": 2, "cima": 1}'
        )
    dx = float(d.get("direita", 0)) - float(d.get("esquerda", 0))
    dy = float(d.get("cima", 0)) - float(d.get("baixo", 0))
    dz = -(float(d.get("frente", 0)) - float(d.get("tras", 0)))
    return np.array([dx, dy, dz])


def quat_ident() -> np.ndarray:
    return np.array([0.0, 0.0, 0.0, 1.0])


def quat_de_eixo(eixo, graus: float) -> np.ndarray:
    e = np.asarray(eixo, dtype=float)
    n = np.linalg.norm(e)
    if n < 1e-12:
        return quat_ident()
    e = e / n
    m = np.radians(graus) / 2.0
    s = np.sin(m)
    return np.array([e[0] * s, e[1] * s, e[2] * s, np.cos(m)])


def quat_mul(a, b) -> np.ndarray:
    """Produto a * b: aplica b primeiro, depois a."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ])


def quat_norm(q) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    return quat_ident() if n < 1e-12 else q / n


def quat_conj(q) -> np.ndarray:
    return np.array([-q[0], -q[1], -q[2], q[3]])


def quat_semantico(frente: float = 0.0, esquerda: float = 0.0, tombar_direita: float = 0.0) -> np.ndarray:
    """Rotacao a partir dos tres angulos semanticos, em graus.

    frente > 0: o topo vai para a frente (-Z).   esquerda > 0: vira para o lado esquerdo (_E, -X).
    tombar_direita > 0: o topo vai para a direita (+X).
    """
    qy = quat_de_eixo((0, 1, 0), esquerda)
    qx = quat_de_eixo((1, 0, 0), -frente)
    qz = quat_de_eixo((0, 0, 1), -tombar_direita)
    return quat_norm(quat_mul(qy, quat_mul(qx, qz)))


def quat_para_matriz(q) -> np.ndarray:
    x, y, z, w = quat_norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def matriz_para_quat(m) -> np.ndarray:
    m = np.asarray(m, dtype=float)
    t = m[0, 0] + m[1, 1] + m[2, 2]
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    return quat_norm(q)


def quat_slerp(a, b, t: float) -> np.ndarray:
    a = quat_norm(a)
    b = quat_norm(b)
    d = float(np.dot(a, b))
    if d < 0:
        b, d = -b, -d
    if d > 0.9995:
        return quat_norm(a + t * (b - a))
    th = np.arccos(np.clip(d, -1, 1))
    return (np.sin((1 - t) * th) * a + np.sin(t * th) * b) / np.sin(th)


def quat_girar(q, v) -> np.ndarray:
    return quat_para_matriz(q) @ np.asarray(v, dtype=float)


def matriz_trs(trans=(0, 0, 0), rot=(0, 0, 0, 1), escala=(1, 1, 1)) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = quat_para_matriz(rot) * np.asarray(escala, dtype=float)[None, :]
    m[:3, 3] = trans
    return m


def matriz_translacao(t) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = t
    return m


def aplicar(m, pontos) -> np.ndarray:
    """Aplica uma matriz 4x4 a um array [..., 3] de pontos."""
    p = np.asarray(pontos, dtype=float)
    return p @ m[:3, :3].T + m[:3, 3]


# --------------------------------------------------------------------------- tipos

@dataclass
class Material:
    """Um material nomeado da ficha: aponta para uma rampa e um perfil de pintura."""
    nome: str
    rampa: str                 # nome de uma rampa da paleta
    perfil: str = "tecido"     # pele, tecido, couro, metal, osso, pedra, madeira, cabelo, fungo, brilho
    brilho: bool = False       # True = vira Neon no Roblox e malha <Peca>_Brilho
    tom: int = -1              # degrau base da rampa; -1 = meio


@dataclass
class Grade:
    """Grade de voxels de UMA peca, em coordenadas de repouso do modelo."""
    v: float                           # lado do voxel em studs (um dos CORTES)
    origem: np.ndarray                 # (3,) canto minimo em studs, multiplo de v
    mat: np.ndarray                    # uint8 [nx, ny, nz]; 0 = vazio; indice em Modelo.materiais (1-based)
    cor: Optional[np.ndarray] = None   # uint16 [nx, ny, nz]; indice em Modelo.cores (1-based); 0 = sem cor

    @property
    def forma(self) -> tuple[int, int, int]:
        return tuple(self.mat.shape)  # type: ignore[return-value]

    def ocupacao(self) -> np.ndarray:
        return self.mat > 0

    def n_voxels(self) -> int:
        return int(np.count_nonzero(self.mat))

    def centros(self) -> np.ndarray:
        """Centros dos voxels ocupados, [n, 3], em studs (repouso)."""
        idx = np.argwhere(self.mat > 0)
        return self.origem + (idx + 0.5) * self.v

    def caixa(self) -> tuple[np.ndarray, np.ndarray]:
        """(min, max) em studs da regiao ocupada. Levanta ValueError se vazia."""
        idx = np.argwhere(self.mat > 0)
        if len(idx) == 0:
            raise ValueError("grade vazia")
        return self.origem + idx.min(0) * self.v, self.origem + (idx.max(0) + 1) * self.v


@dataclass
class Peca:
    nome: str
    osso: str
    grade: Grade
    escala_animada: bool = False       # True = a peca recebe trilha de escala (gosma, squash)


@dataclass
class Osso:
    nome: str
    pai: Optional[str]
    pivo: tuple[float, float, float]   # studs, repouso, espaco do modelo; multiplo do v da peca
    papel: str = "corpo"               # raiz, corpo, cabeca, mandibula, mao, pe, perna, braco, cauda, asa, orelha, ...
    limites: Optional[dict] = None     # {"frente": [-30, 45], "esquerda": [-20, 20], "tombar_direita": [-10, 10]}
    mola: Optional[dict] = None        # {"freq_hz": 2.5, "amort": 0.7, "max_graus": 25}


@dataclass
class Soquete:
    nome: str
    osso: str
    pos: tuple[float, float, float]    # studs, repouso


@dataclass
class Clipe:
    nome: str
    duracao: float
    ossos: list[str]
    trans: np.ndarray                  # float32 [n, nb, 3]  delta local em studs
    rot: np.ndarray                    # float32 [n, nb, 4]  quat xyzw local
    escala: Optional[np.ndarray] = None  # float32 [n, nb, 3]
    fps: int = FPS
    laco: bool = False
    marcadores: list[tuple[str, float]] = field(default_factory=list)
    vel_raiz: float = 0.0              # studs/s que o JOGO desloca a raiz enquanto o clipe toca (para medir deslize)
    meta: dict = field(default_factory=dict)

    @property
    def n_quadros(self) -> int:
        return int(self.trans.shape[0])

    @staticmethod
    def quadros_para(duracao: float, laco: bool, fps: int = FPS) -> int:
        n = int(round(duracao * fps))
        return max(n, 1) if laco else max(n, 1) + 1

    @classmethod
    def vazio(cls, nome: str, duracao: float, ossos: list[str], laco: bool = False, fps: int = FPS) -> "Clipe":
        n = cls.quadros_para(duracao, laco, fps)
        nb = len(ossos)
        rot = np.zeros((n, nb, 4), dtype=np.float32)
        rot[..., 3] = 1.0
        return cls(nome=nome, duracao=duracao, ossos=list(ossos), trans=np.zeros((n, nb, 3), dtype=np.float32),
                   rot=rot, fps=fps, laco=laco)

    def tempo_do_quadro(self, i: int) -> float:
        return i / self.fps


@dataclass
class Modelo:
    id: str
    nome: str
    pecas: list[Peca] = field(default_factory=list)
    ossos: list[Osso] = field(default_factory=list)       # pais antes dos filhos
    soquetes: list[Soquete] = field(default_factory=list)
    materiais: list[Material] = field(default_factory=list)  # indice 1-based nas grades (mat = i + 1)
    cores: list[str] = field(default_factory=list)           # hex; indice 1-based nas grades (cor = i + 1)
    cores_brilho: set[int] = field(default_factory=set)      # indices 1-based de cores que sao Neon
    clipes: dict[str, Clipe] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    def osso(self, nome: str) -> Osso:
        for o in self.ossos:
            if o.nome == nome:
                return o
        raise KeyError(f"osso '{nome}' nao existe; existem: {[o.nome for o in self.ossos]}")

    def peca(self, nome: str) -> Peca:
        for p in self.pecas:
            if p.nome == nome:
                return p
        raise KeyError(f"peca '{nome}' nao existe; existem: {[p.nome for p in self.pecas]}")

    def n_voxels(self) -> int:
        return sum(p.grade.n_voxels() for p in self.pecas)

    def caixa(self) -> tuple[np.ndarray, np.ndarray]:
        mins, maxs = zip(*(p.grade.caixa() for p in self.pecas if p.grade.n_voxels()))
        return np.min(mins, axis=0), np.max(maxs, axis=0)


# --------------------------------------------------------------------------- cinematica direta

def ordem_topologica(ossos: list[Osso]) -> list[Osso]:
    """Devolve os ossos com pais antes dos filhos. Levanta ValueError em ciclo ou pai inexistente."""
    nomes = {o.nome for o in ossos}
    feito: list[Osso] = []
    visto: set[str] = set()
    pend = list(ossos)
    while pend:
        avancou = False
        for o in list(pend):
            if o.pai is None or o.pai in visto:
                feito.append(o)
                visto.add(o.nome)
                pend.remove(o)
                avancou = True
            elif o.pai not in nomes:
                raise ValueError(f"osso '{o.nome}' tem pai '{o.pai}' que nao existe")
        if not avancou:
            raise ValueError(f"ciclo na hierarquia de ossos: {[o.nome for o in pend]}")
    return feito


def matrizes_dos_ossos(ossos: list[Osso], trans=None, rot=None, escala=None, nomes=None) -> dict[str, np.ndarray]:
    """Cinematica direta de UM quadro.

    ossos: lista do modelo. trans/rot/escala: arrays [nb, 3], [nb, 4], [nb, 3] na ordem de `nomes`
    (ossos ausentes de `nomes` ficam em repouso). Devolve {nome: M 4x4} onde M leva coordenadas de
    REPOUSO do modelo para a pose:  M = M_pai . T(pivo) . T(trans) . R(rot) . S(escala) . T(-pivo)
    """
    indice = {n: i for i, n in enumerate(nomes or [])}
    saida: dict[str, np.ndarray] = {}
    for o in ordem_topologica(ossos):
        i = indice.get(o.nome)
        t = trans[i] if (trans is not None and i is not None) else (0.0, 0.0, 0.0)
        q = rot[i] if (rot is not None and i is not None) else (0.0, 0.0, 0.0, 1.0)
        s = escala[i] if (escala is not None and i is not None) else (1.0, 1.0, 1.0)
        piv = np.asarray(o.pivo, dtype=float)
        local = matriz_translacao(piv) @ matriz_trs(t, q, s) @ matriz_translacao(-piv)
        saida[o.nome] = (saida[o.pai] @ local) if o.pai else local
    return saida


def matrizes_do_quadro(modelo: Modelo, clipe: Clipe, quadro: int) -> dict[str, np.ndarray]:
    q = quadro % clipe.n_quadros
    esc = clipe.escala[q] if clipe.escala is not None else None
    return matrizes_dos_ossos(modelo.ossos, clipe.trans[q], clipe.rot[q], esc, clipe.ossos)
