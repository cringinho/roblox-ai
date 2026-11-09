"""Operacoes em grade booleana/inteira, so com numpy (sem scipy).

Convencoes (iguais as do contrato):
  - arrays indexados [x, y, z]; +X = direita (dir), +Y = cima (topo), FRENTE = -Z.
  - fora da grade conta como VAZIO em todas as funcoes (uma face na borda da grade e face exposta).
  - voxel NUNCA e reamostrado: nao existe funcao de reamostrar aqui, de proposito. Mudar de corte
    e refazer a forma no corte novo.

Resumo da API:
  vizinho, deslocar, com_margem
  dilatar, erodir, casca, contar_vizinhos
  componentes, remover_soltos
  ocupacao_suavizada, normal_suavizada
  superficie, faces_expostas, ORDEM_FACES, NORMAIS_FACES
  comprimento_corrida, espessura_minima
  distancia_euclidiana, distancia_com_sinal, propagar_rotulos
  caixa_ocupada, recortar_array, recortar
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from .contrato import Grade

# Ordem fixa das 6 faces usada em todo o pacote.
ORDEM_FACES: tuple[str, ...] = ("dir", "esq", "topo", "base", "tras", "frente")
NORMAIS_FACES = np.array(
    [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=np.int64
)
INDICE_FACE: dict[str, int] = {n: i for i, n in enumerate(ORDEM_FACES)}

_VIZ6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def _conferir_viz(viz: int) -> None:
    if viz not in (6, 26):
        raise ValueError(f"viz={viz!r} nao existe; use 6 (vizinhos de face) ou 26 (face, aresta e canto), ex.: viz=6")


# --------------------------------------------------------------------------- deslocamentos

def deslocar(a: np.ndarray, eixo: int, passo: int, preencher=0) -> np.ndarray:
    """Move o conteudo `passo` celulas ao longo de `eixo` (positivo = indice maior). saida[i + passo] = a[i]."""
    a = np.asarray(a)
    saida = np.full_like(a, preencher)
    n = a.shape[eixo]
    if passo == 0:
        saida[...] = a
        return saida
    if abs(passo) >= n:
        return saida
    de = [slice(None)] * a.ndim
    para = [slice(None)] * a.ndim
    if passo > 0:
        de[eixo] = slice(0, n - passo)
        para[eixo] = slice(passo, n)
    else:
        de[eixo] = slice(-passo, n)
        para[eixo] = slice(0, n + passo)
    saida[tuple(para)] = a[tuple(de)]
    return saida


def vizinho(a: np.ndarray, dx: int = 0, dy: int = 0, dz: int = 0, fora=0) -> np.ndarray:
    """Valor do vizinho no deslocamento (dx, dy, dz): saida[i] = a[i + d]. Fora da grade vale `fora`."""
    saida = np.asarray(a)
    for eixo, d in enumerate((dx, dy, dz)):
        if d:
            saida = deslocar(saida, eixo, -int(d), fora)
    return saida


def com_margem(a: np.ndarray, n: int, valor=0) -> np.ndarray:
    """Copia de `a` com n celulas de margem em volta (nos 3 primeiros eixos)."""
    larg = [(n, n)] * 3 + [(0, 0)] * (np.asarray(a).ndim - 3)
    return np.pad(a, larg, mode="constant", constant_values=valor)


# --------------------------------------------------------------------------- morfologia

def dilatar(m: np.ndarray, n: int = 1, viz: int = 6) -> np.ndarray:
    """Dilata a mascara n vezes. viz=6 cresce em losango (faces); viz=26 cresce em cubo.

    A grade nao cresce: de margem antes com `com_margem` se a forma encosta na borda.
    """
    _conferir_viz(viz)
    m = np.asarray(m, dtype=bool)
    for _ in range(int(n)):
        if viz == 6:
            novo = m.copy()
            for eixo in range(3):
                novo |= deslocar(m, eixo, 1, False)
                novo |= deslocar(m, eixo, -1, False)
            m = novo
        else:
            for eixo in range(3):
                m = m | deslocar(m, eixo, 1, False) | deslocar(m, eixo, -1, False)
    return m


def erodir(m: np.ndarray, n: int = 1, viz: int = 6) -> np.ndarray:
    """Erode a mascara n vezes (fora da grade = vazio, entao a borda da grade tambem erode)."""
    _conferir_viz(viz)
    m = np.asarray(m, dtype=bool)
    for _ in range(int(n)):
        if viz == 6:
            novo = m.copy()
            for eixo in range(3):
                novo &= deslocar(m, eixo, 1, False)
                novo &= deslocar(m, eixo, -1, False)
            m = novo
        else:
            for eixo in range(3):
                m = m & deslocar(m, eixo, 1, False) & deslocar(m, eixo, -1, False)
    return m


def casca(m: np.ndarray, n: int = 1, viz: int = 6) -> np.ndarray:
    """Casca externa: dilata n e remove o miolo (os voxels que ja eram da forma)."""
    m = np.asarray(m, dtype=bool)
    return dilatar(m, n, viz) & ~m


def contar_vizinhos(m: np.ndarray, viz: int = 6) -> np.ndarray:
    """Quantos vizinhos ocupados cada celula tem (0..6 ou 0..26), uint8."""
    _conferir_viz(viz)
    m = np.asarray(m, dtype=bool)
    if viz == 6:
        c = np.zeros(m.shape, dtype=np.uint8)
        for d in _VIZ6:
            c += vizinho(m, *d, fora=False)
        return c
    s = m.astype(np.uint8)
    for eixo in range(3):
        s = s + deslocar(s, eixo, 1, 0) + deslocar(s, eixo, -1, 0)
    return (s - m.astype(np.uint8)).astype(np.uint8)


# --------------------------------------------------------------------------- componentes conexos

def componentes(m: np.ndarray) -> tuple[np.ndarray, int]:
    """Rotula componentes conexos por vizinhanca de FACE.

    Devolve (rotulos int32 [nx, ny, nz], n). Rotulo 0 = vazio; 1 = o MAIOR componente, 2 = o segundo, ...
    (empate: vence o que tem o primeiro voxel em ordem de varredura). Vetorizado: uniao por raiz
    minima com salto de ponteiro, converge em poucas dezenas de passos mesmo em formas compridas.
    """
    m = np.asarray(m, dtype=bool)
    rot = np.zeros(m.shape, dtype=np.int32)
    idx = np.flatnonzero(m)
    n = idx.size
    if n == 0:
        return rot, 0
    ident = np.full(m.size, -1, dtype=np.int64)
    ident[idx] = np.arange(n)
    ident = ident.reshape(m.shape)
    la, lb = [], []
    for eixo in range(3):
        if m.shape[eixo] < 2:
            continue
        fa = [slice(None)] * 3
        fb = [slice(None)] * 3
        fa[eixo] = slice(0, -1)
        fb[eixo] = slice(1, None)
        ambos = m[tuple(fa)] & m[tuple(fb)]
        la.append(ident[tuple(fa)][ambos])
        lb.append(ident[tuple(fb)][ambos])
    a = np.concatenate(la) if la else np.zeros(0, dtype=np.int64)
    b = np.concatenate(lb) if lb else np.zeros(0, dtype=np.int64)
    pai = np.arange(n, dtype=np.int64)
    if a.size:
        while True:
            pa, pb = pai[a], pai[b]
            if np.array_equal(pa, pb):
                break
            menor = np.minimum(pa, pb)
            np.minimum.at(pai, pa, menor)
            np.minimum.at(pai, pb, menor)
            while True:  # salto de ponteiro ate todo mundo apontar para a raiz
                salto = pai[pai]
                if np.array_equal(salto, pai):
                    break
                pai = salto
    raizes, inverso, tam = np.unique(pai, return_inverse=True, return_counts=True)
    ordem = np.lexsort((raizes, -tam))           # maior primeiro; empate pela raiz (primeiro voxel)
    posto = np.empty(len(raizes), dtype=np.int32)
    posto[ordem] = np.arange(1, len(raizes) + 1, dtype=np.int32)
    rot.reshape(-1)[idx] = posto[inverso]
    return rot, int(len(raizes))


def remover_soltos(m: np.ndarray, manter: Optional[np.ndarray] = None) -> tuple[np.ndarray, int]:
    """Remove pedacos soltos. Sem `manter`: fica so o maior componente.
    Com `manter` (mascara): ficam os componentes que tocam a mascara.

    Devolve (mascara limpa, numero de voxels removidos).
    """
    m = np.asarray(m, dtype=bool)
    rot, n = componentes(m)
    if n <= 1 and manter is None:
        return m.copy(), 0
    if manter is None:
        limpo = rot == 1
    else:
        manter = np.asarray(manter, dtype=bool)
        if manter.shape != m.shape:
            raise ValueError(f"`manter` tem forma {manter.shape}, a grade tem {m.shape}; passe uma mascara do mesmo tamanho")
        vivos = np.unique(rot[manter & m])
        limpo = np.isin(rot, vivos[vivos > 0])
    return limpo, int(np.count_nonzero(m) - np.count_nonzero(limpo))


# --------------------------------------------------------------------------- suavizacao e normais

def _media_caixa_eixo(a: np.ndarray, eixo: int, r: int, fora: float) -> np.ndarray:
    n = a.shape[eixo]
    larg = [(0, 0)] * a.ndim
    larg[eixo] = (r + 1, r)
    p = np.pad(a, larg, mode="constant", constant_values=fora)
    c = np.cumsum(p, axis=eixo, dtype=np.float64)
    alto = [slice(None)] * a.ndim
    baixo = [slice(None)] * a.ndim
    alto[eixo] = slice(2 * r + 1, 2 * r + 1 + n)
    baixo[eixo] = slice(0, n)
    return ((c[tuple(alto)] - c[tuple(baixo)]) / (2 * r + 1)).astype(np.float32)


def ocupacao_suavizada(m: np.ndarray, r: int = 2, passes: int = 1, fora: float = 0.0) -> np.ndarray:
    """Media em caixa separavel de raio r (janela 2r+1) da ocupacao; float32 em [0, 1].

    Leitura para um voxel de superficie com r=2: ~0.60 = face plana, ~0.36 = aresta convexa de 90 graus,
    ~0.22 = canto convexo, >= 0.75 = dobra/canto concavo. `passes` > 1 repete o filtro (fica mais redondo).
    """
    a = np.asarray(m, dtype=np.float32)
    r = int(r)
    if r <= 0:
        return a.copy()
    for _ in range(max(1, int(passes))):
        for eixo in range(3):
            a = _media_caixa_eixo(a, eixo, r, fora)
    return a


def normal_suavizada(m: np.ndarray, r: int = 2, passes: int = 2) -> np.ndarray:
    """Normal do VOLUME: gradiente negativo da ocupacao suavizada, normalizado. float32 [nx, ny, nz, 3].

    Aponta para fora da forma. Onde o gradiente some (miolo, ou chapa de 1 voxel vista de dentro)
    cai para a media das normais das faces expostas; se ainda assim der zero, devolve vetor nulo.
    """
    m = np.asarray(m, dtype=bool)
    s = ocupacao_suavizada(m, r, passes)
    g = np.empty(m.shape + (3,), dtype=np.float32)
    for eixo in range(3):
        g[..., eixo] = -(deslocar(s, eixo, -1, 0.0) - deslocar(s, eixo, 1, 0.0)) * 0.5
    norma = np.linalg.norm(g, axis=-1)
    fraco = norma < 1e-4
    if fraco.any():
        fe = faces_expostas(m)
        alt = np.zeros_like(g)
        for i in range(6):
            alt += fe[i][..., None] * NORMAIS_FACES[i].astype(np.float32)
        g = np.where(fraco[..., None], alt, g)
        norma = np.linalg.norm(g, axis=-1)
    g = g / np.maximum(norma, 1e-6)[..., None]
    g[norma < 1e-6] = 0.0
    return g


# --------------------------------------------------------------------------- superficie

def faces_expostas(m: np.ndarray) -> np.ndarray:
    """bool [6, nx, ny, nz] na ordem de ORDEM_FACES (dir, esq, topo, base, tras, frente):
    True onde o voxel e ocupado e o vizinho daquela direcao e vazio."""
    m = np.asarray(m, dtype=bool)
    saida = np.empty((6,) + m.shape, dtype=bool)
    for i, nrm in enumerate(NORMAIS_FACES):
        saida[i] = m & ~vizinho(m, int(nrm[0]), int(nrm[1]), int(nrm[2]), fora=False)
    return saida


def superficie(m: np.ndarray) -> np.ndarray:
    """Mascara dos voxels ocupados com ao menos uma face exposta."""
    m = np.asarray(m, dtype=bool)
    return m & ~erodir(m, 1, 6)


# --------------------------------------------------------------------------- espessura

def comprimento_corrida(m: np.ndarray, eixo: int) -> np.ndarray:
    """Para cada voxel ocupado, o tamanho da corrida continua de ocupados que passa por ele ao longo de `eixo`."""
    m = np.asarray(m, dtype=bool)
    mm = np.moveaxis(m, eixo, 0)
    n = mm.shape[0]
    pos = np.arange(1, n + 1, dtype=np.int32).reshape((n,) + (1,) * (mm.ndim - 1))
    ult_vazio = np.maximum.accumulate(np.where(mm, 0, pos), axis=0)       # posicao do ultimo vazio antes
    frente = pos - ult_vazio                                               # ocupados seguidos ate aqui
    rev = mm[::-1]
    ult_vazio_r = np.maximum.accumulate(np.where(rev, 0, pos), axis=0)
    tras = (pos - ult_vazio_r)[::-1]
    corrida = np.where(mm, frente + tras - 1, 0).astype(np.int32)
    return np.moveaxis(corrida, 0, eixo)


def espessura_minima(m: np.ndarray) -> np.ndarray:
    """Espessura minima LOCAL em voxels (int32): a menor corrida entre os 3 eixos. 0 onde vazio."""
    m = np.asarray(m, dtype=bool)
    e = comprimento_corrida(m, 0)
    e = np.minimum(e, comprimento_corrida(m, 1))
    e = np.minimum(e, comprimento_corrida(m, 2))
    return np.where(m, e, 0).astype(np.int32)


# --------------------------------------------------------------------------- distancias

def distancia_euclidiana(m: np.ndarray, alcance: int = 8) -> np.ndarray:
    """Distancia exata (em voxels, centro a centro) ate a celula True mais proxima, truncada em `alcance`.

    Celula True vale 0. Sem nenhuma celula True, tudo vale `alcance`. Custo: 3 * (2*alcance) deslocamentos.
    """
    m = np.asarray(m, dtype=bool)
    alcance = int(alcance)
    grande = np.float32(alcance * alcance + 1)
    d2 = np.where(m, np.float32(0), grande).astype(np.float32)
    for eixo in range(3):
        melhor = d2.copy()
        for j in range(1, alcance + 1):
            jj = np.float32(j * j)
            np.minimum(melhor, deslocar(d2, eixo, j, grande) + jj, out=melhor)
            np.minimum(melhor, deslocar(d2, eixo, -j, grande) + jj, out=melhor)
        d2 = melhor
    return np.sqrt(np.minimum(d2, np.float32(alcance * alcance)))


def distancia_com_sinal(m: np.ndarray, alcance: int = 8) -> np.ndarray:
    """Distancia com sinal ate a SUPERFICIE da forma voxelizada: negativa dentro, positiva fora.

    Fora: distancia ate o ocupado mais proximo - 0.5. Dentro: -(distancia ate o vazio mais proximo) + 0.5.
    (Fora da grade conta como vazio.) Truncada em +-alcance.
    """
    m = np.asarray(m, dtype=bool)
    fora = distancia_euclidiana(m, alcance) - 0.5
    mp = com_margem(m, 1, False)
    dentro = distancia_euclidiana(~mp, alcance)[1:-1, 1:-1, 1:-1] - 0.5
    return np.where(m, -dentro, fora).astype(np.float32)


def propagar_rotulos(rot: np.ndarray, alvo: np.ndarray, n: int = 8) -> np.ndarray:
    """Preenche as celulas de `alvo` que tem rotulo 0 com o rotulo do vizinho de face ja rotulado
    (ordem fixa de direcoes: dir, esq, topo, base, tras, frente), repetindo ate n vezes."""
    rot = np.array(rot, copy=True)
    alvo = np.asarray(alvo, dtype=bool)
    for _ in range(int(n)):
        falta = alvo & (rot == 0)
        if not falta.any():
            break
        mudou = False
        for d in _VIZ6:
            viz = vizinho(rot, *d, fora=0)
            pega = falta & (viz != 0)
            if pega.any():
                rot[pega] = viz[pega]
                falta &= ~pega
                mudou = True
        if not mudou:
            break
    return rot


# --------------------------------------------------------------------------- recorte

def caixa_ocupada(m: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]:
    """(lo, hi) em indices da regiao nao nula (hi exclusivo), ou None se a grade esta vazia."""
    m = np.asarray(m) != 0
    if not m.any():
        return None
    lo = np.zeros(3, dtype=np.int64)
    hi = np.zeros(3, dtype=np.int64)
    for eixo in range(3):
        outros = tuple(e for e in range(3) if e != eixo)
        onde = np.flatnonzero(m.any(axis=outros))
        lo[eixo] = onde[0]
        hi[eixo] = onde[-1] + 1
    return lo, hi


def recortar_array(a: np.ndarray, margem: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Recorta um array na caixa ocupada (mais `margem` celulas vazias em volta).
    Devolve (array recortado, indice do canto minimo no array original; pode ser negativo com margem)."""
    cx = caixa_ocupada(a)
    if cx is None:
        raise ValueError("grade vazia: nao ha o que recortar (nenhuma forma ocupou voxel)")
    lo, hi = cx
    corte = a[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
    if margem > 0:
        corte = com_margem(corte, margem, 0)
    return np.ascontiguousarray(corte), lo - margem


def recortar(grade: Grade, margem: int = 0) -> Grade:
    """Nova Grade recortada na caixa ocupada, com a origem ajustada (continua multiplo de v)."""
    cx = caixa_ocupada(grade.mat)
    if cx is None:
        raise ValueError("grade vazia: nao ha o que recortar (nenhuma forma ocupou voxel)")
    lo, hi = cx
    fatia = tuple(slice(int(lo[e]), int(hi[e])) for e in range(3))
    mat = np.ascontiguousarray(grade.mat[fatia])
    cor = np.ascontiguousarray(grade.cor[fatia]) if grade.cor is not None else None
    if margem > 0:
        mat = com_margem(mat, margem, 0)
        cor = com_margem(cor, margem, 0) if cor is not None else None
    return Grade(v=grade.v, origem=np.asarray(grade.origem, dtype=float) + (lo - margem) * grade.v, mat=mat, cor=cor)
