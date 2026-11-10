"""Pintura: a cor nasce de material + rampa + regra, nunca de ruido por voxel.

Passes: degrau de luz pela normal suavizada -> gradiente vertical (pes mais escuros) -> oclusao so nas dobras ->
borda clara so na crista voltada para a luz -> padrao logico do material -> acabamentos da ficha -> limpeza de orfaos.
"""
from __future__ import annotations

import numpy as np

from . import util_grade as ug
from .contrato import Modelo
from .paleta import Paleta, valor

# Luz de FORMA (discreta; o Roblox ilumina por cima): de cima, da frente e da direita da criatura.
LUZ = np.array([0.42, 0.78, -0.46])
LUZ = LUZ / np.linalg.norm(LUZ)

# contraste = quantos degraus a luz percorre; ao = forca da oclusao; crista = realce de aresta
PERFIS = {
    "pele": dict(contraste=0.75, ao=1, crista=0), "tecido": dict(contraste=0.85, ao=1, crista=0),
    "couro": dict(contraste=0.9, ao=1, crista=1), "metal": dict(contraste=1.35, ao=1, crista=1),
    "osso": dict(contraste=0.9, ao=1, crista=1), "pedra": dict(contraste=0.95, ao=1, crista=1),
    "madeira": dict(contraste=0.85, ao=1, crista=0), "cabelo": dict(contraste=0.8, ao=1, crista=0),
    "fungo": dict(contraste=0.85, ao=1, crista=0), "chapado": dict(contraste=0, ao=0, crista=0),
    "brilho": dict(contraste=0, ao=0, crista=0),
}


def _hash3(x, y, z, semente=0):
    """Hash inteiro deterministico por celula (para escolher blocos/pintas, nunca por voxel solto)."""
    h = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (semente * 2654435761)
    return (h & 0x7FFFFFFF) % 1000 / 1000.0


def pintar(modelo: Modelo, paleta: Paleta, *, acabamentos: list[dict] | None = None, semente: int = 0) -> dict:
    """Preenche grade.cor de todas as pecas e modelo.cores / cores_brilho. Devolve metricas."""
    tabela: dict[str, int] = {}
    cores: list[str] = []
    brilho: set[int] = set()

    def idx_cor(hexa: str, eh_brilho: bool) -> int:
        if hexa not in tabela:
            cores.append(hexa)
            tabela[hexa] = len(cores)
        if eh_brilho:
            brilho.add(tabela[hexa])
        return tabela[hexa]

    alt_min, alt_max = modelo.caixa()[0][1], modelo.caixa()[1][1]
    orfaos = 0
    for peca in modelo.pecas:
        g = peca.grade
        oc = g.mat > 0
        sup = ug.superficie(oc)
        nrm = ug.normal_suavizada(oc, r=2, passes=2)
        suave = ug.ocupacao_suavizada(oc, r=2)
        fe = ug.faces_expostas(oc)  # dir, esq, topo, base, tras, frente
        lam = (nrm * LUZ).sum(-1)
        nx, ny, nz = oc.shape
        X, Y, Z = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing="ij")
        # coordenadas absolutas em voxels (padroes nao "andam" quando a peca e recortada)
        ax = X + int(round(g.origem[0] / g.v))
        ay = Y + int(round(g.origem[1] / g.v))
        az = Z + int(round(g.origem[2] / g.v))
        altura_rel = ((ay + 0.5) * g.v - alt_min) / max(alt_max - alt_min, 1e-6)
        degrau = np.zeros(oc.shape, np.int16)
        cor = np.zeros(oc.shape, np.uint16)
        for mi, mat in enumerate(modelo.materiais, start=1):
            sel = g.mat == mi
            if not sel.any():
                continue
            rampa = paleta.rampa(mat.rampa)
            n = len(rampa)
            pf = PERFIS.get(mat.perfil, PERFIS["tecido"])
            base = mat.tom if mat.tom >= 0 else (n - 1) // 2
            if pf["contraste"] == 0:
                d = np.full(oc.shape, base, np.int16)
            else:
                # luz em faixas limpas: quantiza a lambertiana suavizada
                amp = pf["contraste"] * (n - 1) / 2.0
                d = np.rint(base + lam * amp).astype(np.int16)
                d -= (altura_rel < 0.18).astype(np.int16)            # pes e base um degrau mais escuros
                d -= ((suave > 0.72) & sup).astype(np.int16) * pf["ao"]  # oclusao so nas dobras
                if pf["crista"]:
                    crista = fe[2] & (fe[0] | fe[5]) & (suave < 0.42)   # aresta convexa de cima voltada para a luz
                    d += crista.astype(np.int16)
                d += _padrao(mat.perfil, ax, ay, az, fe, lam, altura_rel, semente)
            degrau = np.where(sel, np.clip(d, 0, n - 1), degrau)
            for k in range(n):
                m = sel & (degrau == k)
                if m.any():
                    cor[m] = idx_cor(rampa[k], mat.brilho)
        g.cor = cor
    for ac in acabamentos or []:
        _acabamento(modelo, paleta, ac, idx_cor, semente)
    protegidas = {i for i, c in enumerate(cores, 1) if i in brilho}
    chapados = {mi for mi, m in enumerate(modelo.materiais, 1) if m.perfil in ("chapado", "brilho")}
    for peca in modelo.pecas:
        orfaos += _limpar_orfaos(peca.grade, chapados)
    modelo.cores = cores
    modelo.cores_brilho = brilho
    return {"cores": len(cores), "orfaos_corrigidos": orfaos, **grupos_de_valor(modelo)}


def _padrao(perfil, ax, ay, az, fe, lam, altura_rel, semente) -> np.ndarray:
    """Variacao com logica por material, sempre em clusters (nunca voxel solto)."""
    d = np.zeros(ax.shape, np.int16)
    if perfil == "pedra":
        fiada = ay // 3
        bx = (ax + (fiada % 2) * 3) // 5
        bz = (az + (fiada % 2) * 2) // 5
        h = np.vectorize(_hash3)(bx, fiada, bz, semente)
        d += (h > 0.72).astype(np.int16) - (h < 0.2).astype(np.int16)   # blocos inteiros mais claros/escuros
        d -= ((ay % 3 == 0) & ~fe[2]).astype(np.int16) * (h > 0.45)       # junta sob a fiada, em parte dos blocos
    elif perfil == "madeira":
        d -= ((ax + az) % 4 == 0).astype(np.int16)                      # veio
    elif perfil == "cabelo":
        lateral = fe[0] | fe[1]
        mecha = np.where(lateral, az % 4 == 0, ax % 4 == 0)             # mechas: riscas ao longo do fio
        d -= mecha.astype(np.int16)
        d += (fe[2] & ~mecha & (lam > 0.55) & ((ax // 4 + az // 4) % 2 == 0)).astype(np.int16) * 0  # reservado
    elif perfil == "metal":
        d += (((ax - ay) % 7 == 0) & (lam > 0.15)).astype(np.int16) * 2  # faixa de reflexo diagonal
    elif perfil == "tecido":
        d -= ((ay % 5 == 0) & (altura_rel < 0.5) & ((ax + az) % 4 == 0)).astype(np.int16)  # pregas na barra
    return d


def _acabamento(modelo, paleta, ac, idx_cor, semente):
    """Acabamentos com logica geometrica: musgo_em_cima, sangue_escorrido, ferrugem_nas_arestas, pintas,
    listras, gradiente_vertical. Campos: tipo, material (da paleta padrao), pecas (lista ou todas), forca."""
    tipo = ac.get("tipo")
    mat = paleta.material(ac.get("material", {"musgo_em_cima": "musgo", "sangue_escorrido": "sangue",
                                             "ferrugem_nas_arestas": "bronze", "pintas": "osso",
                                             "listras": "escuro"}.get(tipo, "musgo")))
    rampa = paleta.rampa(mat.rampa)
    forca = float(ac.get("forca", 0.5))
    alvo = ac.get("pecas")
    so_mats = ac.get("materiais")
    nomes = [m.nome for m in modelo.materiais]
    for peca in modelo.pecas:
        if alvo and peca.nome not in alvo:
            continue
        g = peca.grade
        oc = g.mat > 0
        fe = ug.faces_expostas(oc)
        nx, ny, nz = oc.shape
        X, Y, Z = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing="ij")
        ax = X + int(round(g.origem[0] / g.v)); ay = Y + int(round(g.origem[1] / g.v)); az = Z + int(round(g.origem[2] / g.v))
        h = np.vectorize(_hash3)(ax // 3, ay // 2, az // 3, semente + 7)
        if tipo == "musgo_em_cima":
            m = fe[2] & (h < forca)
            m |= ug.vizinho(m, 0, 1, 0) & oc & (fe[0] | fe[1] | fe[4] | fe[5]) & (h < forca * 0.5)  # escorre 1 voxel
        elif tipo == "sangue_escorrido":
            topo = fe[2] & (h < forca * 0.6)
            m = topo.copy()
            for k in (1, 2, 3):
                m |= ug.vizinho(topo, 0, k, 0) & oc & (h < forca * (0.6 - 0.15 * k))
        elif tipo == "ferrugem_nas_arestas":
            n_exp = fe.sum(0)
            m = oc & (n_exp >= 2) & (h < forca)
        elif tipo == "pintas":
            m = fe[2] & (((ax // 3) + (az // 3)) % 2 == 0) & (ax % 3 == 1) & (az % 3 == 1) & (h < forca + 0.3)
            m |= ug.vizinho(m, 1, 0, 0) & fe[2] & (h < forca * 0.6)
        elif tipo == "listras":
            m = oc & (ug.superficie(oc)) & ((ay // int(ac.get("largura", 2))) % 2 == 0)
        elif tipo == "gradiente_vertical":
            continue
        else:
            raise ValueError(f'acabamento "{tipo}" nao existe; use musgo_em_cima, sangue_escorrido, '
                             f'ferrugem_nas_arestas, pintas ou listras')
        if so_mats:
            ok = np.isin(g.mat, [nomes.index(n) + 1 for n in so_mats if n in nomes])
            m &= ok
        m &= ug.superficie(oc)
        if m.any():
            claro = fe[2] | fe[5]
            g.cor[m & claro] = idx_cor(rampa[min(len(rampa) - 1, len(rampa) // 2 + 1)], mat.brilho)
            g.cor[m & ~claro] = idx_cor(rampa[len(rampa) // 2 - 1], mat.brilho)


def _limpar_orfaos(g, mats_protegidos) -> int:
    """Voxel de superficie cuja cor difere de todos os vizinhos de face vira a cor mais comum entre eles."""
    oc = g.mat > 0
    sup = ug.superficie(oc)
    viz = [ug.vizinho(g.cor, dx, dy, dz) for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
    viz = np.stack(viz)
    tem = viz > 0
    igual = (viz == g.cor[None]) & tem
    orfao = sup & ~igual.any(0) & (tem.sum(0) >= 3) & ~np.isin(g.mat, list(mats_protegidos) or [-1])
    n = int(orfao.sum())
    for i, j, k in np.argwhere(orfao):
        v = viz[:, i, j, k]
        v = v[v > 0]
        vals, cont = np.unique(v, return_counts=True)
        g.cor[i, j, k] = vals[cont.argmax()]
    return n


def grupos_de_valor(modelo: Modelo) -> dict:
    """Fracao da superficie em escuro / medio / claro (pela luminancia) e em brilho."""
    lum = np.array([0.0] + [valor(c) for c in modelo.cores])
    tot = np.zeros(4)
    for peca in modelo.pecas:
        g = peca.grade
        sup = ug.superficie(g.mat > 0)
        c = g.cor[sup]
        eb = np.isin(c, list(modelo.cores_brilho) or [-1])
        L = lum[c]
        tot += [np.sum((L < 0.42) & ~eb), np.sum((L >= 0.42) & (L < 0.66) & ~eb), np.sum((L >= 0.66) & ~eb), eb.sum()]
    s = max(tot.sum(), 1)
    return {"escuro": round(tot[0] / s, 3), "medio": round(tot[1] / s, 3), "claro": round(tot[2] / s, 3),
            "brilho": round(tot[3] / s, 4)}
