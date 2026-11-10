"""Naturalidade: medidas do que o olho humano cobra de um movimento, calculadas no MUNDO (depois da cinematica).

O P1 antigo media as trilhas osso a osso (giro por quadro, emenda do laco). Aqui a medida e do que se ve:
o pe escorrega no apoio? o corpo tem peso no andar? o Parado repete num periodo so? a cauda gira em bloco?
Fontes e limiares: docs/pesquisa/17-percepcao-e-medidas.md (limiares iniciais, calibrados nos modelos aprovados).
"""
from __future__ import annotations

import numpy as np

from .anim import _cadeias_por_papel, _familia, ponta_da_perna
from .contrato import Clipe, Modelo, matrizes_do_quadro

PERNA = ("perna", "pe")


def _pontos(modelo: Modelo) -> dict[str, np.ndarray]:
    """Centro das pecas de cada osso, em repouso."""
    out = {}
    for o in modelo.ossos:
        cx = [p.grade.caixa() for p in modelo.pecas if p.osso == o.nome and p.grade.n_voxels()]
        if cx:
            out[o.nome] = (np.min([c[0] for c in cx], 0) + np.max([c[1] for c in cx], 0)) / 2
    return out


def _pes(modelo: Modelo) -> list[tuple[str, np.ndarray, float]]:
    """(osso da ponta da perna, ponto da sola em repouso, comprimento da perna)."""
    por_nome = {o.nome: o for o in modelo.ossos}
    tem_filho_perna = {o.pai for o in modelo.ossos if _familia(o.papel) in PERNA}
    out = []
    for o in modelo.ossos:
        if _familia(o.papel) not in PERNA or o.nome in tem_filho_perna:
            continue
        cx = [p.grade.caixa() for p in modelo.pecas if p.osso == o.nome and p.grade.n_voxels()]
        if not cx:
            continue
        sola = ponta_da_perna(modelo, o.nome)
        topo, comp, pt = o, 0.0, sola
        while True:                                          # comprimento = soma dos ossos, do quadril ate a ponta
            comp += float(np.linalg.norm(np.array(topo.pivo, float) - pt))
            pt = np.array(topo.pivo, float)
            if topo.pai in por_nome and _familia(por_nome[topo.pai].papel) in PERNA:
                topo = por_nome[topo.pai]
            else:
                break
        out.append((o.nome, sola, max(comp, 1e-3)))
    return out


def _mundo(modelo: Modelo, cl: Clipe, pontos: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    tr = {n: np.zeros((cl.n_quadros, 3)) for n in pontos}
    for q in range(cl.n_quadros):
        M = matrizes_do_quadro(modelo, cl, q)
        for n, p in pontos.items():
            tr[n][q] = (M[n] @ np.append(p, 1.0))[:3]
    return tr


def _atraso(a: np.ndarray, b: np.ndarray, laco: bool) -> float:
    """Quantos quadros b vem depois de a (correlacao cruzada, com interpolacao do pico)."""
    a, b = a - a.mean(), b - b.mean()
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    n = len(a)
    lim = max(2, n // 4)
    ds = np.arange(-lim, lim + 1)
    if laco:
        cc = np.array([float((a * np.roll(b, -d)).sum()) for d in ds])
    else:
        cc = np.array([float((a[max(0, -d):n - max(0, d)] * b[max(0, d):n - max(0, -d)]).sum()) for d in ds])
    i = int(np.argmax(cc))
    d = float(ds[i])
    if 0 < i < len(cc) - 1:
        den = cc[i - 1] - 2 * cc[i] + cc[i + 1]
        if abs(den) > 1e-12:
            d += 0.5 * (cc[i - 1] - cc[i + 1]) / den
    return d


def medir(modelo: Modelo, cl: Clipe) -> dict:
    """Numeros de naturalidade de um clipe. Chave ausente = a medida nao se aplica."""
    out: dict = {}
    mn, mx = modelo.caixa()
    H = float(mx[1] - mn[1]) or 1.0
    centros = _pontos(modelo)
    pes = _pes(modelo)
    pontos = dict(centros)
    for nome, sola, _ in pes:
        pontos["@sola:" + nome] = sola
    # a sola e um ponto do osso do pe: usa a matriz dele
    tr = {n: np.zeros((cl.n_quadros, 3)) for n in pontos}
    for q in range(cl.n_quadros):
        M = matrizes_do_quadro(modelo, cl, q)
        for n, p in pontos.items():
            tr[n][q] = (M[n.split(":", 1)[1] if n.startswith("@sola:") else n] @ np.append(p, 1.0))[:3]
    raiz = next((o.nome for o in modelo.ossos if o.pai is None), None)
    corpo = next((o.nome for o in modelo.ossos if o.papel == "corpo" and o.pai == raiz and o.nome in centros), None) \
        or next((o.nome for o in modelo.ossos if o.papel == "corpo" and o.nome in centros), None)
    t = np.arange(cl.n_quadros) / 30.0
    anda = cl.laco and cl.vel_raiz > 1e-6 and bool(pes)

    # 1. peso no andar: o corpo sobe e desce (dossie 17, medida 12; quadril humano: 5 cm em 1,7 m = 2,9%)
    if anda and corpo:
        # peso = o corpo sobe e desce OU vai de um lado ao outro (a Hidra do dono mostra o peso de lado), medido
        # contra o comprimento da perna (a altura engana em criatura de pescoco alto)
        perna = float(np.mean([c for _, _, c in pes]))
        out["peso_no_andar_pct"] = round(100 * float(max(np.ptp(tr[corpo][:, 1]), np.ptp(tr[corpo][:, 0]))) / perna, 2)
        out["pernas"] = len(pes)

    # 2. deslize do pe no apoio (medida 1): no apoio o pe anda para tras na velocidade da raiz, e nao sai do lugar no mundo
    if anda:
        pior = 0.0
        for nome, _, comp in pes:
            p = tr["@sola:" + nome]
            chao = p[:, 1] <= p[:, 1].min() + 0.25 * 0.125   # um quarto de voxel do ponto mais baixo
            if chao.all() or not chao.any():
                continue
            # janelas de contato (circular)
            ini = [q for q in range(cl.n_quadros) if chao[q] and not chao[q - 1]]
            for q0 in ini:
                idx = []
                q = q0
                while chao[q % cl.n_quadros] and len(idx) < cl.n_quadros:
                    idx.append(q)
                    q += 1
                idx = idx[1:-1]                              # o quadro de pousar e o de sair sao transicao
                if len(idx) < 3:
                    continue
                zz = np.array([p[i % cl.n_quadros, 2] - cl.vel_raiz * (i / 30.0) for i in idx])
                xx = np.array([p[i % cl.n_quadros, 0] for i in idx])
                pior = max(pior, float(np.hypot(np.ptp(zz), np.ptp(xx))) / comp)
        out["deslize_do_pe_pct"] = round(100 * pior, 2)

    # 3. periodos do Parado (medidas 11 e 13): quantos ritmos diferentes carregam o movimento
    if cl.laco and cl.nome == "Parado" and cl.n_quadros >= 60:
        energia = np.zeros(cl.n_quadros // 2)
        for n in centros:
            s = tr[n] - tr[n].mean(0)
            if np.abs(s).max() < 0.004 * H:
                continue
            e = (np.abs(np.fft.rfft(s, axis=0)) ** 2).sum(1)[1:cl.n_quadros // 2 + 1]
            energia[:len(e)] += e / (e.sum() + 1e-12)
        if energia.sum() > 0:
            fr = energia / energia.sum()
            out["ritmos_no_parado"] = int((fr >= 0.08).sum())
            out["periodo_dominante_s"] = round(cl.duracao / (int(np.argmax(fr)) + 1), 2)
        # de quanto em quanto tempo a pose INTEIRA volta a ser quase a mesma (o olho acha a emenda ai)
        X = np.concatenate([tr[n] - tr[n].mean(0) for n in centros], axis=1)
        tot = float((X ** 2).sum())
        if tot > 1e-9:
            n = cl.n_quadros
            repete = cl.duracao
            for d in range(max(3, n // 12), n - max(3, n // 12)):
                if float(((np.roll(X, -d, axis=0) - X) ** 2).sum()) / (2 * tot) < 0.15:
                    repete = d / 30.0
                    break
            out["repete_em_s"] = round(repete, 2)

    # 4. cadeias: a onda viaja (medida 9). Atraso medio entre elos vizinhos, em quadros
    if cl.laco:
        piores = []
        for fam, fila in _cadeias_por_papel(modelo):
            fila = [n for n in fila if n in centros]
            if len(fila) < 3:
                continue
            eixo = int(np.argmax([np.ptp(tr[fila[-1]][:, e]) for e in range(3)]))
            if np.ptp(tr[fila[-1]][:, eixo]) < 0.01 * H:
                continue
            # atraso do movimento de cada elo em relacao ao pai, tirando o que o pai ja carrega
            rel = [tr[fila[0]][:, eixo]] + [tr[fila[j]][:, eixo] - tr[fila[j - 1]][:, eixo] for j in range(1, len(fila))]
            atr = [abs(_atraso(rel[j], rel[j + 1], True)) for j in range(len(rel) - 1) if np.ptp(rel[j]) > 1e-4 and np.ptp(rel[j + 1]) > 1e-4]
            if atr:
                piores.append((round(float(np.mean(atr)), 2), fila[0]))
        if piores:
            out["atraso_por_elo_quadros"] = min(piores)[0]
            out["cadeia_mais_dura"] = min(piores)[1]

    # 5. estalo (medida 7): pico de solavanco contra a mediana, so informativo
    if corpo and cl.n_quadros > 8:
        v = np.diff(tr[corpo], axis=0, append=tr[corpo][:1]) if cl.laco else np.diff(tr[corpo], axis=0)
        j = np.linalg.norm(np.diff(v, 2, axis=0), axis=1)
        if np.median(j) > 1e-9:
            out["solavanco_pico_sobre_mediana"] = round(float(j.max() / np.median(j)), 1)
    return out
