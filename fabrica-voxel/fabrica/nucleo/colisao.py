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
        # nao conta: outro item, a mao que segura, o que esta preso nessa mao (luva) e o braco dessa mao
        braco = pai.get(self.mao) if papel.get(pai.get(self.mao)) == "braco" else None
        self.corpo = [p for p in modelo.pecas if papel.get(p.osso) != "item" and p.osso not in (self.mao, braco)
                      and pai.get(p.osso) != self.mao]

    def inversas(self, M: dict) -> list:
        """Inversas das matrizes das pecas do corpo num quadro: calcule uma vez e passe em `inv` ao testar candidatos."""
        return [np.linalg.inv(M[b.osso]) for b in self.corpo]

    def dentro(self, M: dict, empurrao=None, inv=None, M_item=None) -> float:
        """Fracao dos voxels de superficie do item que estao dentro de alguma peca do corpo (ou abaixo do chao)."""
        if not len(self.P):
            return 0.0
        mundo = self.P1 @ (M[self.item] if M_item is None else M_item).T
        if empurrao is not None:
            mundo = mundo.copy()
            mundo[:, :3] += empurrao
        d = mundo[:, 1] < -1e-6                      # abaixo do chao tambem e "atravessar"
        if inv is None:
            inv = self.inversas(M)
        for b, Mi in zip(self.corpo, inv):
            loc = mundo @ Mi.T
            ijk = np.floor((loc[:, :3] - b.grade.origem) / b.grade.v).astype(int)
            ok = np.all((ijk >= 0) & (ijk < np.array(b.grade.mat.shape)), axis=1)
            if ok.any():
                d[ok] |= b.grade.mat[ijk[ok, 0], ijk[ok, 1], ijk[ok, 2]] > 0
        return float(d.mean())


def itens(modelo: Modelo) -> list[str]:
    return [o.nome for o in modelo.ossos if o.papel == "item"]


def _repouso_dos_pais(modelo: Modelo, osso) -> np.ndarray:
    """Quaternion do giro de repouso acumulado dos ancestrais (braco dobrado, por exemplo)."""
    from .contrato import quat_mul
    q = np.array([0.0, 0.0, 0.0, 1.0])
    cadeia = []
    o = modelo.osso(osso.pai) if osso.pai else None
    while o is not None:
        cadeia.append(o)
        o = modelo.osso(o.pai) if o.pai else None
    for o in reversed(cadeia):
        q = quat_mul(q, np.array(o.repouso))
    return q


def escolher_empunhadura(modelo: Modelo, item: str, preferida: dict | None = None) -> dict:
    """Escolhe como o item fica na mao em repouso: o candidato mais perto da pose preferida que nao toca o corpo
    nem o chao. preferida = {"frente", "fora", "giros", "max_inclinacao", "antebraco"}: "fora" = para o lado da mao;
    "antebraco" = quanto o cotovelo fica dobrado para a frente (graus) quando o heroi tem braco.
    Os angulos do item sao medidos no MUNDO: com o antebraco dobrado, a espada continua a 50 graus do prumo."""
    from .contrato import quat_conj, quat_mul
    pref = {"frente": 50.0, "fora": 8.0, "giros": [0], "antebraco": 0.0, **(preferida or {})}
    osso = modelo.osso(item)
    mao = modelo.osso(osso.pai)
    lado = 1.0 if mao.nome.endswith("_D") else -1.0
    tem_braco = bool(mao.pai) and modelo.osso(mao.pai).papel == "braco"
    pecas = [p for p in modelo.pecas if p.osso == item]
    v = pecas[0].grade.v if pecas else 0.125
    soqs = [s for s in modelo.soquetes if s.osso == item]
    lim = float(pref.get("max_inclinacao", 90))   # lanterna e tocha quase nao inclinam: preferem escorregar para fora
    cands = sorted(((f, o) for f in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90) for o in (0, 8, 16, 24, 32, 40)
                    if abs(f - pref["frente"]) <= lim and abs(o - pref["fora"]) <= lim),
                   key=lambda c: abs(c[0] - pref["frente"]) + 1.5 * abs(c[1] - pref["fora"]))
    dobras = [float(pref["antebraco"])] if tem_braco else [0.0]
    if tem_braco:                                   # se a dobra preferida nao livrar, tenta dobrar mais e menos
        dobras += [d for d in (30.0, 60.0, 90.0, 110.0, 0.0) if d != dobras[0]]
    # poses de prova: o item tem de ficar livre tambem com a cabeca e o tronco inclinados (dano, queda, olhar em volta)
    nomes = [o.nome for o in modelo.ossos]
    provas = [None]
    for o in modelo.ossos:
        if o.papel == "cabeca":
            provas += [(o.nome, quat_semantico(a, b, c)) for a, b, c in ((22, 0, 0), (-22, 0, 0), (0, 22, 0), (0, -22, 0), (0, 0, 14), (0, 0, -14))]
        elif o.papel == "corpo" and o.pai and modelo.osso(o.pai).pai is None:
            provas += [(o.nome, quat_semantico(a, b, 0)) for a, b in ((14, 0), (-14, 0), (0, 20), (0, -20))]

    def medir(cena):
        pior = 0.0
        for pv in provas:
            if pv is None:
                M = matrizes_dos_ossos(modelo.ossos)
            else:
                rot = np.tile(np.array([0.0, 0.0, 0.0, 1.0]), (len(nomes), 1))
                rot[nomes.index(pv[0])] = pv[1]
                M = matrizes_dos_ossos(modelo.ossos, rot=rot, nomes=nomes)
            pior = max(pior, cena.dentro(M))
            if pior > 0 and melhor is not None and pior >= melhor[0]:
                break
        return pior

    melhor = None
    andou = 0
    for k in (0, 1, 2, 3, 4):                 # ultimo recurso: o item escorrega k voxels para fora dentro da mao
        if k:
            for p in pecas:
                p.grade.origem = p.grade.origem + np.array([lado * v, 0.0, 0.0])
            andou = k
        cena = _Cena(modelo, item)
        for dob in dobras:
            mao.repouso = tuple(float(x) for x in quat_semantico(-dob, 0.0, 0.0)) if dob else IDENT
            qp = _repouso_dos_pais(modelo, osso)
            for g in pref["giros"]:           # giro = escudo de lado, preso ao braco, em vez de atravessado no peito
                for f, o in cands:
                    osso.repouso = tuple(float(x) for x in quat_mul(quat_conj(qp), quat_semantico(f, -lado * g, lado * o)))
                    d = medir(cena)
                    if melhor is None or d < melhor[0] - 1e-9:
                        melhor = (d, f, o, g, k, dob)
                    if d == 0.0:
                        break
                if melhor[0] == 0.0:
                    break
            if melhor[0] == 0.0:
                break
        if melhor[0] == 0.0:
            break
    d, f, o, g, k, dob = melhor
    if andou != k:                            # volta para o deslocamento escolhido
        for p in pecas:
            p.grade.origem = p.grade.origem + np.array([lado * v * (k - andou), 0.0, 0.0])
    for s_ in soqs:
        s_.pos = (s_.pos[0] + lado * v * k, s_.pos[1], s_.pos[2])
    mao.repouso = tuple(float(x) for x in quat_semantico(-dob, 0.0, 0.0)) if dob else IDENT
    qp = _repouso_dos_pais(modelo, osso)
    osso.repouso = tuple(float(x) for x in quat_mul(quat_conj(qp), quat_semantico(f, -lado * g, lado * o)))
    return {"frente": f, "fora": o, "giro": g, "voxels_para_fora": k, "antebraco": dob, "dentro": round(d, 4)}


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
            braco = por_nome[mao].pai
            if braco and por_nome[braco].papel == "braco" and braco in cl.ossos:
                _desviar_pelo_ombro(modelo, cl, cena, braco, lado, tolerancia, rel)
                if cl.meta.get("largar_item"):           # morte: se nem assim livrar, o item solta da mao e cai ao lado
                    _desviar_por_translacao(modelo, cl, cena, it, lado, tolerancia, passos, eixo_nome, rel)
                continue
            piv = np.append(np.array(por_nome[it].pivo), 1.0)
            _desviar_por_translacao(modelo, cl, cena, mao, lado, tolerancia, passos, eixo_nome, rel)
    return rel


def _desviar_por_translacao(modelo: Modelo, cl, cena: _Cena, anda: str, lado: float, tolerancia: float, passos, eixo_nome: str, rel: dict):
    """Empurra o osso `anda` (a mao solta, ou o proprio item quando ele pode largar da mao) para fora do corpo."""
    por_nome = {o.nome: o for o in modelo.ossos}
    it = cena.item
    mao = anda
    km = cl.ossos.index(anda)
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
            ds = [r, fr, ld, (r + fr), (ld + fr), (r + bx * 0.6), (r - bx * 0.8)]
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
        if cl.laco and len(ruins) > 0.3 * n:                 # toca quase o tempo todo (asa batendo): afasta de vez, sem vai e vem
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
        e["max_studs"] = round(max(e.get("max_studs", 0.0), float(np.linalg.norm(Ds, axis=1).max())), 3)


def _desviar_pelo_ombro(modelo: Modelo, cl, cena: _Cena, braco: str, lado: float, tolerancia: float, rel: dict):
    """Heroi com braco: a mao nao pode sair do braco, entao quem desvia e o ombro ou o punho. Nos quadros em que o
    item toca o corpo, o braco abre (para fora, para a frente) ou o item gira no punho (ponta para fora, para a frente,
    para tras), o minimo que livra. Uma manobra por clipe, alargada e suavizada no tempo."""
    from .contrato import matriz_translacao, quat_mul, matriz_para_quat
    por_nome = {o.nome: o for o in modelo.ossos}
    kb = cl.ossos.index(braco)
    ki = cl.ossos.index(cena.item)
    piv = np.array(por_nome[braco].pivo)
    piv_i = np.append(np.array(por_nome[cena.item].pivo), 1.0)
    sub, mudou = [braco], True
    while mudou:
        mudou = False
        for o in modelo.ossos:
            if o.pai in sub and o.nome not in sub:
                sub.append(o.nome)
                mudou = True
    # manobras: ("ombro", fora, frente) gira o braco; ("punho", fora, frente) gira so o item, em eixos do mundo
    dirs = [("ombro", 1.0, 0.0), ("ombro", 0.0, -1.0), ("ombro", 0.7, -0.7), ("punho", 1.0, 0.0), ("punho", 0.0, 1.0),
            ("punho", 0.7, 0.7), ("punho", 0.0, -1.0), ("ombro", 0.0, 1.0)]
    passos = np.arange(8.0, 97.0, 8.0)

    def giro_mundo(fora, fr):
        return quat_para_matriz(quat_semantico(fr, 0.0, lado * fora))

    rot0 = cl.rot.copy()                      # para desfazer onde o alargamento estragou um quadro que estava bom

    def item_em(M, q, tipo, fora, fr):
        """Matriz do item com a manobra aplicada. O braco e a mao nao contam como corpo, entao so o item muda."""
        if tipo == "ombro":
            R = np.eye(4)
            R[:3, :3] = quat_para_matriz(cl.rot[q, kb])
            X = np.eye(4)
            X[:3, :3] = giro_mundo(fora, fr)
            A = M[braco] @ matriz_translacao(piv) @ R.T
            return A @ X @ np.linalg.inv(A) @ M[cena.item]
        g = (M[cena.item] @ piv_i)[:3]
        W = np.eye(4)
        W[:3, :3] = giro_mundo(fora, fr)
        return matriz_translacao(g) @ W @ matriz_translacao(-g) @ M[cena.item]

    for volta in range(5):
        n = cl.n_quadros
        Ms = [matrizes_do_quadro(modelo, cl, q) for q in range(n)]
        ruins = [q for q in range(n) if cena.dentro(Ms[q]) > tolerancia]
        if not ruins:
            break
        S = np.full((len(dirs), len(ruins)), np.inf)
        for a, q in enumerate(ruins):
            inv = cena.inversas(Ms[q])
            for b, (tipo, do, df) in enumerate(dirs):
                for s_ in passos:
                    if cena.dentro(Ms[q], inv=inv, M_item=item_em(Ms[q], q, tipo, do * s_, df * s_)) <= tolerancia:
                        S[b, a] = s_
                        break
        custo = [(int(np.isinf(S[b]).sum()), float(np.where(np.isinf(S[b]), 0, S[b]).sum())) for b in range(len(dirs))]
        b = min(range(len(dirs)), key=lambda x: custo[x])
        aplicar = {}                                   # manobra -> angulos por quadro
        for a, q in enumerate(ruins):
            alt = b if np.isfinite(S[b, a]) else int(np.argmin(S[:, a]))
            mag = S[alt, a] if np.isfinite(S[alt, a]) else passos[-1]
            aplicar.setdefault(alt, np.zeros((n, 3)))[q, :2] = np.array(dirs[alt][1:]) * mag
        maior = 0.0
        for alt, D in aplicar.items():
            if cl.laco and len(ruins) > 0.3 * n:
                Ds = np.tile(D[np.argmax(np.linalg.norm(D, axis=1))], (n, 1))
            elif volta < 3:
                Ds = _suavizar(D, cl.laco, alarga=3 + 2 * volta) * (1.0 + 0.2 * volta)
            elif volta < 4:
                Ds = _suavizar(D, cl.laco, alarga=2, sigma=0.6) * 1.15
            else:
                Ds = D
            maior = max(maior, float(np.linalg.norm(Ds, axis=1).max()))
            for q in range(n):
                if abs(Ds[q, 0]) < 1e-6 and abs(Ds[q, 1]) < 1e-6:
                    continue
                if dirs[alt][0] == "ombro":
                    cl.rot[q, kb] = quat_mul(quat_semantico(Ds[q, 1], 0.0, lado * Ds[q, 0]), cl.rot[q, kb]).astype(np.float32)
                else:                                  # giro em eixos do mundo, trazido para o eixo local do item
                    R = quat_para_matriz(cl.rot[q, ki])
                    Mr = Ms[q][cena.item][:3, :3]
                    cl.rot[q, ki] = matriz_para_quat(R @ Mr.T @ giro_mundo(Ds[q, 0], Ds[q, 1]) @ Mr).astype(np.float32)
        e = rel.setdefault(cl.nome, {}).setdefault(cena.item, {"quadros": 0, "max_graus": 0.0})
        e["quadros"] = max(e["quadros"], len(ruins))
        e["max_graus"] = round(max(e.get("max_graus", 0.0), maior), 1)
    for q in range(cl.n_quadros):             # quadro que era limpo e ficou sujo pelo alargamento volta ao original
        if cena.dentro(matrizes_do_quadro(modelo, cl, q)) > tolerancia:
            agora = cl.rot[q].copy()
            cl.rot[q, kb], cl.rot[q, ki] = rot0[q, kb], rot0[q, ki]
            if cena.dentro(matrizes_do_quadro(modelo, cl, q)) > tolerancia:
                cl.rot[q] = agora
