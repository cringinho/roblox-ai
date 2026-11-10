"""Auditoria: P1 (geometria e movimento, recusa) e P2 (arte, nota 0-100 com minimo por tipo).

Cada regra devolve {regra, passou, valor, limite, conserto}. Os limites vem de registro/config/auditoria.json.
Limites marcados "calibrar" sao propostas: ajuste com um conjunto de assets aprovados a mao.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import util_grade as ug
from .anim import medir
from .exporta import TETO_TRIANGULOS, contar_triangulos
from .paleta import valor
from .pintura import grupos_de_valor
from .render import render_modelo

PASTA_CONFIG = Path(__file__).resolve().parents[2] / "registro" / "config"
PADRAO = {
    "monstro": {"nota_minima": 75, "brilho_max": 0.04, "cores": [6, 32], "assimetria_min": 0.004,
                "voxels_min": 1000, "ossos_min": 8},
    "heroi": {"nota_minima": 75, "brilho_max": 0.03, "cores": [8, 40], "assimetria_min": 0.0},
    "item": {"nota_minima": 70, "brilho_max": 0.40, "cores": [3, 24], "assimetria_min": 0.0},
    "prop": {"nota_minima": 70, "brilho_max": 0.08, "cores": [3, 32], "assimetria_min": 0.0},
    "estrutura": {"nota_minima": 70, "brilho_max": 0.05, "cores": [4, 40], "assimetria_min": 0.0},
}


def perfil(tipo: str) -> dict:
    cfg = dict(PADRAO)
    arq = PASTA_CONFIG / "auditoria.json"
    if arq.exists():
        for k, v in json.loads(arq.read_text(encoding="utf-8")).get("perfis", {}).items():
            cfg[k] = {**cfg.get(k, {}), **v}
    return cfg.get(tipo, cfg["monstro"])


def _r(regra, passou, val, limite, conserto):
    return {"regra": regra, "passou": bool(passou), "valor": val, "limite": limite, "conserto": conserto}


def atravessamento(modelo, *, passo: int = 2, so_repouso: bool = False) -> dict:
    """Quanto cada item de mao (osso de papel "item") entra no corpo, no repouso e em cada clipe.
    Devolve {"pior": fracao 0..1 dos voxels do item dentro de outra peca, "onde": ..., "repouso": fracao, "itens": {...}}.
    Nao conta a mao que segura o item, os filhos dela nem outro item."""
    from .contrato import matrizes_do_quadro, matrizes_dos_ossos
    papel = {o.nome: o.papel for o in modelo.ossos}
    pai = {o.nome: o.pai for o in modelo.ossos}
    itens = [o.nome for o in modelo.ossos if o.papel == "item"]
    res = {"pior": 0.0, "onde": None, "repouso": 0.0, "itens": {}}
    if not itens:
        return res
    poses = [("repouso", 0, matrizes_dos_ossos(modelo.ossos))]
    if not so_repouso:
        for nome, cl in modelo.clipes.items():
            poses += [(nome, q, matrizes_do_quadro(modelo, cl, q)) for q in range(0, cl.n_quadros, passo)]
    for it in itens:
        pts = []
        for p in modelo.pecas:
            if p.osso == it:
                g = p.grade
                idx = np.argwhere(ug.superficie(g.mat > 0))
                pts.append(g.origem + (idx + 0.5) * g.v)
        if not pts:
            continue
        P = np.concatenate(pts)
        P1 = np.concatenate([P, np.ones((len(P), 1))], 1)
        corpo = [p for p in modelo.pecas if papel.get(p.osso) != "item" and p.osso != pai.get(it) and pai.get(p.osso) != pai.get(it)]
        pior_it = (0.0, None)
        for clipe, q, M in poses:
            mundo = P1 @ M[it].T
            dentro = np.zeros(len(P), bool)
            por_peca = {}
            for b in corpo:
                loc = mundo @ np.linalg.inv(M[b.osso]).T
                ijk = np.floor((loc[:, :3] - b.grade.origem) / b.grade.v).astype(int)
                ok = np.all((ijk >= 0) & (ijk < np.array(b.grade.mat.shape)), axis=1)
                h = np.zeros(len(P), bool)
                h[ok] = b.grade.mat[ijk[ok, 0], ijk[ok, 1], ijk[ok, 2]] > 0
                if h.any():
                    por_peca[b.nome] = int(h.sum())
                    dentro |= h
            f = float(dentro.mean())
            if clipe == "repouso":
                res["repouso"] = max(res["repouso"], f)
            if f > pior_it[0]:
                pior_it = (f, {"item": it, "clipe": clipe, "quadro": q, "pecas": por_peca})
        res["itens"][it] = round(pior_it[0], 4)
        if pior_it[0] > res["pior"]:
            res["pior"], res["onde"] = pior_it[0], pior_it[1]
    res["pior"], res["repouso"] = round(res["pior"], 4), round(res["repouso"], 4)
    return res


def p1(modelo, tipo: str = "monstro") -> list[dict]:
    pf = perfil(tipo)
    out = []
    soltos = {}
    pais = {o.nome: o.pai for o in modelo.ossos}
    papeis = {o.nome: o.papel for o in modelo.ossos}
    for p in modelo.pecas:
        rot, n = ug.componentes(p.grade.mat > 0)
        if n <= 1:
            continue
        # pedacos separados so valem se cada um encosta em outra peca do mesmo osso (ex.: duas orelhas na cabeca)
        viz = np.zeros(p.grade.mat.shape, bool)
        for q in modelo.pecas:
            if q is not p and q.osso in (p.osso, pais.get(p.osso)) and q.grade.v == p.grade.v:
                off = np.round((q.grade.origem - p.grade.origem) / p.grade.v).astype(int)
                a0 = np.maximum(off, 0); b0 = np.minimum(off + np.array(q.grade.mat.shape), np.array(viz.shape))
                if np.all(b0 > a0):
                    s0 = a0 - off
                    viz[a0[0]:b0[0], a0[1]:b0[1], a0[2]:b0[2]] |= q.grade.mat[s0[0]:s0[0] + b0[0] - a0[0], s0[1]:s0[1] + b0[1] - a0[1], s0[2]:s0[2] + b0[2] - a0[2]] > 0
        perto = ug.dilatar(viz, 1, 26)
        orfaos = sum(1 for k in range(1, n + 1) if not (perto & (rot == k)).any())
        if orfaos > (0 if viz.any() else 1):
            soltos[p.nome] = orfaos
    out.append(_r("voxels_soltos", not soltos, soltos or 0, "1 componente por peca",
                  "Ha pedacos desconectados dentro da peca. Engrosse o detalhe (minimo 2 voxels), encoste-o no corpo "
                  "ou separe-o em outra peca com osso proprio."))
    cortes = sorted({float(p.grade.v) for p in modelo.pecas})
    out.append(_r("um_tamanho_de_voxel", len(cortes) <= 1, cortes, "1 tamanho por modelo",
                  'Ha pecas com tamanhos de voxel diferentes (mixels). Use o mesmo "corte" em todas as pecas do modelo; '
                  "se precisa de mais detalhe, suba o corte do modelo inteiro."))
    if pf.get("voxels_min") or pf.get("ossos_min"):
        nv, nb = modelo.n_voxels(), sum(1 for o in modelo.ossos if o.pai is not None)
        ok = nv >= pf.get("voxels_min", 0) and nb >= pf.get("ossos_min", 0)
        out.append(_r("detalhe_minimo", ok, {"voxels": nv, "ossos": nb},
                      f'>= {pf.get("voxels_min", 0)} voxels e >= {pf.get("ossos_min", 0)} ossos',
                      'Criatura simples demais. Mais ossos: "segmentos": 2 nos bracos e pernas, mandibula, orelhas, cauda em '
                      'cadeia. Mais voxels: garras, dentes, espinhos e placas com "repetir"; ou aumente o corpo.'))
    tri = contar_triangulos(modelo)
    modelo.meta["triangulos"] = tri["total"]
    out.append(_r("triangulos_por_malha", tri["maior"] <= TETO_TRIANGULOS, tri["maior"], TETO_TRIANGULOS,
                  "Divida a peca maior em duas, ou simplifique o padrao de cor (cada troca de cor quebra a fusao de faces)."))
    gv = grupos_de_valor(modelo)
    out.append(_r("brilho", gv["brilho"] <= pf["brilho_max"], gv["brilho"], pf["brilho_max"],
                  "Brilho demais compete com os alvos. Deixe material de brilho so em olhos, nucleos e pontas."))
    mn, mx = modelo.caixa()
    out.append(_r("pe_no_chao", abs(mn[1]) <= 0.26 or modelo.meta.get("flutua"), round(float(mn[1]), 3), "0 +- 0.25",
                  'O modelo nao encosta no chao. A primeira forma deve usar "em": "chao"; se ele flutua de proposito, '
                  'ponha "meta": {"flutua": true}.'))
    if any(o.papel == "item" for o in modelo.ossos):
        at = atravessamento(modelo, passo=1)
        onde = at["onde"] or {}
        out.append(_r("item_atravessa_corpo", at["pior"] <= 0.02,
                      {"pior": at["pior"], "repouso": at["repouso"], "clipe": onde.get("clipe"), "quadro": onde.get("quadro"),
                       "pecas": onde.get("pecas")}, "<= 2% dos voxels do item dentro do corpo, em todo quadro",
                      "O item de mao entra no corpo. Confira se o item tem os soquetes Pegada e Ponta, se a classe de pegada "
                      'esta certa ("pegada" na ficha do item) e se a caixa do item cabe no limite da classe. Em golpe novo, '
                      "leve o arco para a frente do corpo (centro_H.frente) ou abra o raio (arco.raio_mao_H)."))
    for nome, cl in modelo.clipes.items():
        m = medir(modelo, cl, papeis)
        lim = 70 if cl.laco else 150       # acao (golpe) pode ter quadro de borrao; laco nao pode estalar
        out.append(_r(f"clipe_{nome}_giro", m["giro_max_graus_quadro"] <= lim, m["giro_max_graus_quadro"], f"{lim} graus/quadro",
                      "Algum osso estala. Aumente a duracao do trecho ou reduza a amplitude."))
        if cl.laco:
            out.append(_r(f"clipe_{nome}_laco", m["salto_no_laco"] <= 2.5, m["salto_no_laco"], "<= 2.5x um passo normal",
                          'O laco nao fecha. Em "onda" use "harm" inteiro; em "poses" a ultima chave deve voltar a primeira.'))
        minimo = min(2, len(modelo.ossos) - 1) if nome in ("Parado", "Andar", "Correr") else 1
        out.append(_r(f"clipe_{nome}_vivo", m["ossos_em_movimento"] >= minimo, m["ossos_em_movimento"], f">= {minimo} ossos",
                      "Quase nada se mexe. Some camadas: respiracao no tronco e um 'seguir' ou 'onda' defasada na cabeca."))
        if nome in ("Parado", "Andar", "Correr"):
            out.append(_r(f"clipe_{nome}_gemeos", m["gemeos"] < 0.98, m["gemeos"], "< 0.98",
                          "Lado direito e esquerdo estao espelhados perfeitos (cara de codigo). Defase um lado em 3 a 8% "
                          'do ciclo ("fase") e mude a amplitude em 10%.'))
    return out


def p2(modelo, tipo: str = "monstro") -> dict:
    pf = perfil(tipo)
    m = []

    def met(nome, nota, val, alvo, conserto, peso):
        m.append({"metrica": nome, "nota": round(float(np.clip(nota, 0, 1)), 3), "valor": val, "alvo": alvo,
                  "conserto": conserto, "peso": peso})

    gv = grupos_de_valor(modelo)
    # 1. valor: precisa dos tres grupos; nenhum acima de 70% nem abaixo de 8%
    fr = np.array([gv["escuro"], gv["medio"], gv["claro"]])
    met("grupos_de_valor", 1 - max(0, fr.max() - 0.62) * 3 - max(0, 0.10 - fr.min()) * 6, gv, "3 grupos; maior <= 62%, menor >= 10%",
        "O modelo esta todo num valor so. Escolha rampas de luminancias diferentes para materiais vizinhos "
        "(um escuro, um medio, um claro) e mantenha um foco claro pequeno.", 20)
    # 2. paleta
    nc = len(modelo.cores)
    lo, hi = pf["cores"]
    met("tamanho_da_paleta", 1 - max(0, lo - nc) / lo - max(0, nc - hi) / hi, nc, f"{lo} a {hi} cores",
        "Cores demais viram ruido; de menos, chapado. Ajuste o numero de materiais (3 a 6 e o normal).", 10)
    extremos = [c for c in modelo.cores if min(int(c[i:i + 2], 16) for i in (1, 3, 5)) < 6 and max(int(c[i:i + 2], 16) for i in (1, 3, 5)) < 10
                or min(int(c[i:i + 2], 16) for i in (1, 3, 5)) > 250]
    met("sem_preto_ou_branco_puros", 0 if extremos else 1, extremos, "nenhuma", "Troque por um tom da rampa.", 5)
    # 3. ruido e descanso
    orf = tot = desc = 0
    for p in modelo.pecas:
        g = p.grade
        sup = ug.superficie(g.mat > 0)
        viz = np.stack([ug.vizinho(g.cor, *d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))])
        tem = viz > 0
        ig = (viz == g.cor[None]) & tem
        orf += int((sup & ~ig.any(0) & (tem.sum(0) >= 3)).sum())
        desc += int((sup & (ig.sum(0) == tem.sum(0))).sum())
        tot += int(sup.sum())
    f_orf, f_desc = orf / max(tot, 1), desc / max(tot, 1)
    met("voxels_orfaos", 1 - f_orf / 0.03, round(f_orf, 4), "<= 1.5% da superficie",
        "Ha voxels de cor isolada (ruido). Padrao so em clusters de 3 ou mais; tire estampas de 1 voxel.", 15)
    met("area_de_descanso", 1 - max(0, 0.35 - f_desc) * 4 - max(0, f_desc - 0.92) * 6, round(f_desc, 3), "35% a 92% da superficie lisa",
        "Detalhe em tudo = detalhe em nada (ou liso demais = chapado). Concentre o detalhe na cabeca/arma e deixe "
        "areas calmas no resto.", 15)
    # 4. silhueta: frente e camera do jogo
    occs = {}
    for vista in ("frente", "grade"):
        im = np.array(render_modelo(modelo, vista=vista, px_por_stud=24, modo="silhueta").convert("L")) < 128
        ys, xs = np.nonzero(im)
        occs[vista] = float(im.sum()) / max((np.ptp(ys) + 1) * (np.ptp(xs) + 1), 1) if len(ys) else 0
    o = occs["frente"]
    met("silhueta", 1 - max(0, 0.30 - o) * 4 - max(0, o - 0.86) * 5, {k: round(v, 3) for k, v in occs.items()},
        "ocupa 30% a 86% da caixa vista de frente",
        "Silhueta de caixote (muito cheia) ou esfiapada (muito vazia). Acrescente 1 ou 2 formas que saiam do corpo "
        "(chifre, cauda, arma, ombreira) ou engrosse as partes finas.", 20)
    # 5. assimetria (criaturas)
    dif = tot2 = 0
    for p in modelo.pecas:
        g = p.grade
        if abs(g.origem[0] + g.mat.shape[0] * g.v / 2) < g.v:       # peca centrada em X
            oc = g.mat > 0
            dif += int((oc ^ oc[::-1]).sum()) + int(((g.cor != g.cor[::-1]) & oc & oc[::-1]).sum())
            tot2 += int(oc.sum()) * 2
    assim = dif / max(tot2, 1)
    alvo = pf["assimetria_min"]
    met("assimetria", 1 if assim >= alvo else assim / max(alvo, 1e-9), round(assim, 4), f">= {alvo}",
        "Simetria perfeita parece codigo. Acrescente 1 a 3 quebras intencionais sem espelho: uma ombreira so, "
        "um chifre quebrado, uma cicatriz, um remendo.", 10 if alvo > 0 else 0)
    # 6. foco: os voxels mais claros estao concentrados na metade de cima
    lum = np.array([0.0] + [valor(c) for c in modelo.cores])
    alt_min, alt_max = modelo.caixa()[0][1], modelo.caixa()[1][1]
    cima = baixo = 0.0
    for p in modelo.pecas:
        g = p.grade
        sup = ug.superficie(g.mat > 0)
        ys = g.origem[1] + (np.argwhere(sup)[:, 1] + 0.5) * g.v
        L = lum[g.cor[sup]]
        meio = (alt_min + alt_max) / 2
        cima += float(L[ys >= meio].sum()); baixo += float(L[ys < meio].sum())
        cima_n = 1
    razao = cima / max(cima + baixo, 1e-9)
    met("claro_em_cima", 1 - max(0, 0.45 - razao) * 4, round(razao, 3), ">= 45% da luz na metade de cima",
        "A base esta mais clara que o topo. Escureca pes e base; clareie cabeca e ombros (o olho vai para o claro).", 5)
    pt = sum(x["peso"] for x in m)
    nota = 100 * sum(x["nota"] * x["peso"] for x in m) / max(pt, 1)
    piores = sorted([x for x in m if x["peso"] > 0], key=lambda x: x["nota"])[:3]
    return {"nota": round(nota, 1), "minimo": pf["nota_minima"], "passou": nota >= pf["nota_minima"], "metricas": m,
            "piores": [{"metrica": x["metrica"], "nota": x["nota"], "conserto": x["conserto"]} for x in piores]}
