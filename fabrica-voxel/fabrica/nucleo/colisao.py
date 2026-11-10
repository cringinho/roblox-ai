"""Itens de mao que nao atravessam o corpo.

Tres defesas, nesta ordem:
1. EMPUNHADURA: o osso do item ganha um giro de repouso (a arma fica inclinada, como no Minecraft e no Trove),
   escolhido por medicao entre candidatos em volta da pose preferida da classe de pegada.
2. TRAJETO: o golpe e desenhado pela frente do corpo e recua pela guarda (ver anim._golpe).
3. DESVIO: depois de assar cada clipe, todo quadro em que o item ainda entra no corpo empurra a mao para fora
   ate livrar; o empurrao e alargado e suavizado no tempo para nao dar tranco.
O portao P1 "item_atravessa_corpo" (auditoria.atravessamento) confere o resultado.
"""
from __future__ import annotations

import numpy as np

from . import util_grade as ug
from .contrato import Modelo, matrizes_do_quadro, matrizes_dos_ossos, quat_para_matriz, quat_semantico

IDENT = (0.0, 0.0, 0.0, 1.0)


class _Cena:
    """Pontos de superficie de um item e as pecas do corpo que ele nao pode atravessar."""

    def __init__(self, modelo: Modelo, item: str):
        papel = {o.nome: o.papel for o in modelo.ossos}
        pai = {o.nome: o.pai for o in modelo.ossos}
        self.item, self.mao = item, pai[item]
        pts = []
        for p in modelo.pecas:
            if p.osso == item:
                g = p.grade
                pts.append(g.origem + (np.argwhere(ug.superficie(g.mat > 0)) + 0.5) * g.v)
        self.P = np.concatenate(pts) if pts else np.zeros((0, 3))
        self.P1 = np.concatenate([self.P, np.ones((len(self.P), 1))], 1)
        # nao conta: outro item, a mao que segura, e o que esta preso nessa mao (luva)
        self.corpo = [p for p in modelo.pecas if papel.get(p.osso) != "item" and p.osso != self.mao and pai.get(p.osso) != self.mao]

    def dentro(self, M: dict, empurrao=None) -> float:
        """Fracao dos voxels de superficie do item que estao dentro de alguma peca do corpo."""
        if not len(self.P):
            return 0.0
        mundo = self.P1 @ M[self.item].T
        if empurrao is not None:
            mundo = mundo.copy()
            mundo[:, :3] += empurrao
        d = np.zeros(len(self.P), bool)
        for b in self.corpo:
            loc = mundo @ np.linalg.inv(M[b.osso]).T
            ijk = np.floor((loc[:, :3] - b.grade.origem) / b.grade.v).astype(int)
            ok = np.all((ijk >= 0) & (ijk < np.array(b.grade.mat.shape)), axis=1)
            if ok.any():
                d[ok] |= b.grade.mat[ijk[ok, 0], ijk[ok, 1], ijk[ok, 2]] > 0
        return float(d.mean())


def itens(modelo: Modelo) -> list[str]:
    return [o.nome for o in modelo.ossos if o.papel == "item"]


def escolher_empunhadura(modelo: Modelo, item: str, preferida: dict | None = None) -> dict:
    """Escolhe o giro de repouso do item: o candidato mais perto da pose preferida que nao toca o corpo.
    preferida = {"frente": graus, "fora": graus} ("fora" = para o lado da mao que segura)."""
    pref = {"frente": 50.0, "fora": 8.0, "giros": [0], **(preferida or {})}
    osso = modelo.osso(item)
    lado = 1.0 if osso.pai.endswith("_D") else -1.0
    pecas = [p for p in modelo.pecas if p.osso == item]
    v = pecas[0].grade.v if pecas else 0.125
    soqs = [s for s in modelo.soquetes if s.osso == item]
    lim = float(pref.get("max_inclinacao", 90))   # lanterna e tocha quase nao inclinam: preferem escorregar para fora
    cands = sorted(((f, o) for f in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90) for o in (0, 8, 16, 24, 32, 40)
                    if abs(f - pref["frente"]) <= lim and abs(o - pref["fora"]) <= lim),
                   key=lambda c: abs(c[0] - pref["frente"]) + 1.5 * abs(c[1] - pref["fora"]))
    melhor = None
    andou = 0
    for k in (0, 1, 2, 3, 4):                 # ultimo recurso: o item escorrega k voxels para fora dentro da mao
        if k:
            for p in pecas:
                p.grade.origem = p.grade.origem + np.array([lado * v, 0.0, 0.0])
            andou = k
        cena = _Cena(modelo, item)
        for g in pref["giros"]:               # giro = escudo de lado, preso ao braco, em vez de atravessado no peito
            for f, o in cands:
                osso.repouso = tuple(float(x) for x in quat_semantico(f, -lado * g, lado * o))
                d = cena.dentro(matrizes_dos_ossos(modelo.ossos))
                if melhor is None or d < melhor[0] - 1e-9:
                    melhor = (d, f, o, g, k)
                if d == 0.0:
                    break
            if melhor[0] == 0.0:
                break
        if melhor[0] == 0.0:
            break
    d, f, o, g, k = melhor
    if andou != k:                            # volta para o deslocamento escolhido
        for p in pecas:
            p.grade.origem = p.grade.origem + np.array([lado * v * (k - andou), 0.0, 0.0])
    for s in soqs:
        s.pos = (s.pos[0] + lado * v * k, s.pos[1], s.pos[2])
    osso.repouso = tuple(float(x) for x in quat_semantico(f, -lado * g, lado * o)) if (f or o or g) else IDENT
    return {"frente": f, "fora": o, "giro": g, "voxels_para_fora": k, "dentro": round(d, 4)}


def _suavizar(D: np.ndarray, laco: bool, alarga: int = 3, sigma: float = 1.6) -> np.ndarray:
    """Alarga cada empurrao para os quadros vizinhos (comeca antes, termina depois) e borra no tempo."""
    n = len(D)
    if n < 3:
        return D
    norma = np.linalg.norm(D, axis=1)
    idx = np.arange(n)
    larg = np.zeros_like(D)
    for q in range(n):
        viz = (idx[max(0, q - alarga):q + alarga + 1] if not laco else (np.arange(q - alarga, q + alarga + 1) % n))
        larg[q] = D[viz[np.argmax(norma[viz])]]
    r = int(np.ceil(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.concatenate([larg[-r:], larg, larg[:r]]) if laco else np.concatenate([np.repeat(larg[:1], r, 0), larg, np.repeat(larg[-1:], r, 0)])
    return np.stack([np.convolve(pad[:, e], k, mode="valid") for e in range(3)], 1)


def desviar_itens(modelo: Modelo, *, tolerancia: float = 0.0, alcance_H: float = 0.45) -> dict:
    """Empurra a mao para fora nos quadros em que o item entra no corpo. Altera os clipes no lugar.
    Devolve {clipe: {item: {"quadros": n, "max_studs": d}}} com o que foi mexido."""
    rel: dict = {}
    its = itens(modelo)
    if not its or not modelo.clipes:
        return rel
    mn, mx = modelo.caixa()
    H = float(modelo.meta.get("H", mx[1] - mn[1]))
    v = min(p.grade.v for p in modelo.pecas)
    passos = np.arange(1, int(alcance_H * H / v) + 1) * v
    por_nome = {o.nome: o for o in modelo.ossos}
    eixo_nome = next((o.nome for o in modelo.ossos if o.papel in ("corpo", "tronco") and o.nome != "Raiz"), modelo.ossos[0].nome)
    for cl in modelo.clipes.values():
        for it in its:
            cena = _Cena(modelo, it)
            mao = cena.mao
            if mao not in cl.ossos:
                continue
            km = cl.ossos.index(mao)
            lado = 1.0 if mao.endswith("_D") else -1.0
            piv = np.append(np.array(por_nome[it].pivo), 1.0)
            for volta in range(7):                      # mede, empurra, suaviza; repete se a suavizacao deixou resto
                n = cl.n_quadros
                Ms = [matrizes_do_quadro(modelo, cl, q) for q in range(n)]
                pai_m = por_nome[mao].pai
                Rm = [(M[pai_m][:3, :3] if pai_m else np.eye(3)) @ quat_para_matriz(por_nome[mao].repouso) for M in Ms]
                ruins = [q for q in range(n) if cena.dentro(Ms[q]) > tolerancia]
                if not ruins:
                    break
                fr, ld, bx = np.array([0.0, 0.0, -1.0]), np.array([lado, 0.0, 0.0]), np.array([0.0, -1.0, 0.0])

                def direcoes(q):
                    pos = (Ms[q][it] @ piv)[:3]
                    eixo = (Ms[q][eixo_nome] @ np.append(np.array(por_nome[eixo_nome].pivo), 1.0))[:3]
                    r = pos - eixo
                    r[1] = 0.0
                    r = r / np.linalg.norm(r) if np.linalg.norm(r) > 1e-6 else ld
                    ds = [r, fr, ld, (r + fr), (ld + fr), (r + bx * 0.6), (fr + bx * 0.6)]
                    return [d / np.linalg.norm(d) for d in ds]

                # UMA direcao para o clipe inteiro (direcoes diferentes por quadro se anulam ao suavizar):
                # a que livra mais quadros com o menor empurrao
                S = np.full((7, len(ruins)), np.inf)
                for a, q in enumerate(ruins):
                    for b, d in enumerate(direcoes(q)):
                        for s_ in passos:
                            if cena.dentro(Ms[q], d * s_) <= tolerancia:
                                S[b, a] = s_
                                break
                custo = [(int(np.isinf(S[b]).sum()), float(np.where(np.isinf(S[b]), 0, S[b]).sum())) for b in range(7)]
                b = min(range(7), key=lambda x: custo[x])
                D = np.zeros((n, 3))
                for a, q in enumerate(ruins):
                    ds = direcoes(q)
                    if np.isfinite(S[b, a]):
                        D[q] = ds[b] * S[b, a]
                    else:                                # esta direcao nao livra este quadro: a melhor das outras
                        alt = int(np.argmin(S[:, a]))
                        D[q] = ds[alt] * (S[alt, a] if np.isfinite(S[alt, a]) else passos[-1])
                if len(ruins) > 0.3 * n:                 # toca quase o tempo todo (asa batendo): afasta de vez, sem vai e vem
                    Ds = np.tile(D[np.argmax(np.linalg.norm(D, axis=1))], (n, 1))
                elif volta < 4:
                    Ds = _suavizar(D, cl.laco, alarga=3 + 2 * volta) * (1.0 + 0.2 * volta)
                elif volta < 6:                          # sobrou resto: borra bem menos (prefere um ajuste seco a atravessar)
                    Ds = _suavizar(D, cl.laco, alarga=2, sigma=0.6) * 1.15
                else:
                    Ds = D
                for q in range(n):
                    cl.trans[q, km] += (Rm[q].T @ Ds[q]).astype(np.float32)
                e = rel.setdefault(cl.nome, {}).setdefault(it, {"quadros": 0, "max_studs": 0.0})
                e["quadros"] = max(e["quadros"], len(ruins))
                e["max_studs"] = round(max(e["max_studs"], float(np.linalg.norm(Ds, axis=1).max())), 3)
    return rel
