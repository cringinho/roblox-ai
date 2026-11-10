"""Formas que deixam o modelo menos quadrado: lapidar (tira as quinas) e capa (pano com caimento).

lapidar: remove o voxel das arestas convexas onde o volume e grosso o bastante. Um bloco grande ganha quina chanfrada;
um detalhe fino (2 voxels) fica como esta. Serve para modelo importado de blocos e para qualquer ficha.

capa: em vez de uma placa reta, um pano que nasce nos ombros, abre para baixo, curva em volta do corpo, tem pregas que
aprofundam para a barra e barra recortada. Sai em N pedacos, cada um com seu osso em cadeia, para balancar.
"""
from __future__ import annotations

import numpy as np

from .contrato import Grade, Osso, Peca


def _corrida(oc: np.ndarray, eixo: int) -> np.ndarray:
    """Comprimento da fileira de voxels ocupados que passa por cada voxel, ao longo do eixo."""
    def frente(a):
        c = np.cumsum(a, axis=eixo)
        z = np.maximum.accumulate(np.where(a, 0, c), axis=eixo)
        return c - z
    f = frente(oc)
    b = np.flip(frente(np.flip(oc, eixo)), eixo)
    return np.where(oc, f + b - 1, 0)


def lapidar(mat: np.ndarray, passes: int = 1, grosso: int = 4) -> np.ndarray:
    """Devolve a grade com as arestas convexas chanfradas. `grosso` = espessura minima (voxels) para mexer."""
    m = mat.copy()
    for k in range(int(passes)):
        oc = np.pad(m > 0, 1)
        exp = []
        for e in range(3):
            a = np.roll(oc, 1, e)
            b = np.roll(oc, -1, e)
            exp.append((~a | ~b) & oc)
        runs = [_corrida(oc, e) for e in range(3)]
        lim = grosso * (k + 1)
        ok = [~exp[e] | (runs[e] >= lim) for e in range(3)]
        n_exp = exp[0].astype(np.int8) + exp[1] + exp[2]
        tira = oc & (n_exp >= 2) & ok[0] & ok[1] & ok[2]
        m[tira[1:-1, 1:-1, 1:-1]] = 0
    return m


def capa(modelo, spec: dict, indice_material: dict, v: float) -> list[str]:
    """Cria a capa a partir de `spec` (medidas em voxels do modelo):
    {"nome": "Manto", "pai": "Torax", "topo": y, "base": y, "larg_topo": n, "larg_base": n, "z": z das costas,
     "afasta": quanto a barra fica para tras, "abraca": quanto as bordas vem para a frente, "segmentos": 3,
     "prega": 1, "passo_prega": 6, "barra": "pontas" | "reta", "fora": material, "forro": material, "debrum": material}
    Devolve os nomes das pecas criadas (<nome>1, <nome>2, ...)."""
    nome = spec.get("nome", "Manto")
    topo, base = float(spec["topo"]), float(spec["base"])
    lt, lb = float(spec["larg_topo"]), float(spec["larg_base"])
    z0, afasta, abraca = float(spec["z"]), float(spec.get("afasta", 6)), float(spec.get("abraca", 4))
    esp = int(spec.get("espessura", 2))
    nseg = int(spec.get("segmentos", 3))
    prega, passo = float(spec.get("prega", 1)), int(spec.get("passo_prega", 6))
    fora, forro, debrum = (indice_material[spec[k]] for k in ("fora", "forro", "debrum"))
    alt = int(round(topo - base))
    larg = int(np.ceil(max(lt, lb))) + 2
    prof = int(np.ceil(afasta + abraca + prega + esp)) + 4
    g = np.zeros((larg, alt, prof), np.uint8)
    xs = np.arange(larg) - larg / 2 + 0.5
    zmin = z0 - abraca - 1
    for j in range(alt):
        t = 1.0 - (j + 0.5) / alt                         # 0 no ombro, 1 na barra
        meia = (lt + (lb - lt) * t ** 0.8) / 2
        zc = z0 + afasta * t * t
        for i, x in enumerate(xs):
            if abs(x) > meia:
                continue
            borda = min(1.0, abs(x) / max(meia, 1e-6))
            z = zc - abraca * borda ** 2 * (0.4 + 0.6 * (1 - t))      # as bordas abracam mais perto do ombro
            z += prega * t * (1.0 if (int(np.floor(x + 1000)) // passo) % 2 else 0.0)   # pregas aprofundam para a barra
            if spec.get("barra", "pontas") == "pontas" and j < 3 and (int(np.floor(x + 1000)) // 3) % 2 == 0 and j < 2 + (abs(x) < meia - 1):
                continue                                   # barra recortada em pontas
            k0 = int(round(z - zmin))
            for d in range(esp):
                if 0 <= k0 + d < prof:
                    g[i, j, k0 + d] = fora if d == esp - 1 else forro
            if j < 5 and j >= 3 and 0 <= k0 + esp - 1 < prof:
                g[i, j, k0 + esp - 1] = debrum             # debrum logo acima das pontas
            if abs(x) > meia - 1.5 and t < 0.25 and 0 <= k0 + esp - 1 < prof:
                g[i, j, k0 + esp - 1] = debrum             # gola: borda dourada so perto do ombro
    origem = np.array([-larg / 2, base, zmin]) * v
    cortes = [int(round(alt * (1 - (s / nseg)))) for s in range(nseg + 1)]      # de cima para baixo
    criadas, pai = [], spec["pai"]
    for s in range(nseg):
        j1, j0 = cortes[s], cortes[s + 1]
        sub = g[:, j0:j1, :]
        if not sub.any():
            continue
        idx = np.argwhere(sub > 0)
        a, b = idx.min(0), idx.max(0) + 1
        nm = f"{nome}{s + 1}"
        org = origem + np.array([a[0], j0 + a[1], a[2]]) * v
        modelo.pecas.append(Peca(nome=nm, osso=nm, grade=Grade(v=v, origem=org, mat=sub[a[0]:b[0], a[1]:b[1], a[2]:b[2]].copy())))
        linha = sub[:, -1, :]                              # pivo: meio da fileira de cima deste pedaco
        zi = np.argwhere(linha > 0)
        zp = (zi[:, 1].mean() + 0.5 + zmin) * v if len(zi) else (z0 * v)
        modelo.ossos.append(Osso(nm, pai, (0.0, float((base + j1) * v), float(zp)), "pano"))
        criadas.append(nm)
        pai = nm
    return criadas
