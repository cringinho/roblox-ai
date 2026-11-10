"""Heroi: corpo-base + cabeca da classe + linhagem (feicoes e tracos) + aparencia + equipamento.

Regra central: GERAR, NAO DEFORMAR. O item nasce do corpo (casca) e cada traco abre o proprio espaco
(volume protegido = os voxels do traco + 1 de margem). Nada e feito por par raca x item.
"""
from __future__ import annotations

import copy

import numpy as np

from ..nucleo import sdf
from ..nucleo import util_grade as ug
from ..nucleo.contrato import CORTES, Grade, Osso, Peca, Soquete
from ..nucleo.forma import ErroFicha, construir_pecas
from ..nucleo.montagem import materiais_da_ficha, montar
from ..registro import Registro, _aplicar

V = CORTES["grade"]


def _espelhar_arte(linhas):
    return [l[::-1] for l in linhas]


def _linha_olhos(arte, afast):
    return [l + "." * afast + r for l, r in zip(arte, _espelhar_arte(arte))]


def escolha_de(reg: Registro, linhagem: str, predef: int = 1, escolha: dict | None = None) -> dict:
    lin = reg.fichas[reg.achar(f"linhagem.{linhagem}" if not linhagem.startswith("linhagem.") else linhagem)]
    pre = lin["predefinicoes"]
    if not 1 <= predef <= len(pre):
        raise ErroFicha(f'{lin["nome"]} tem {len(pre)} predefinicoes; use --predef de 1 a {len(pre)}')
    e = dict(pre[predef - 1])
    e.update(escolha or {})
    e["l"] = lin["id"].split(".", 1)[1]
    return e


def ficha_heroi(reg: Registro, escolha: dict, corpo: str | None = None) -> dict:
    """Monta a ficha (linguagem de forma) de um heroi a partir da escolha compacta do jogador."""
    lin = reg.fichas[reg.achar("linhagem." + escolha["l"])]
    tc = reg.fichas["classe_corpo.tabela"]
    cc = reg.fichas["classe_cabeca.tabela"]["classes"][lin["classe_cabeca"]]
    rosto = reg.fichas["aparencia.rosto"]
    cabelos = reg.fichas["aparencia.cabelos"]["cabelos"]
    t = tc["tamanhos"][lin["tamanho"]]
    corpo = str(corpo or lin.get("cabeca", {}).get("corpo_padrao", "1"))
    if str(corpo) not in tc["corpos"]:
        raise ErroFicha(f'corpo "{corpo}" nao existe; use 1 (ombro largo), 2 (quadril largo) ou 3 (robusto)')
    co = tc["corpos"][str(corpo)]
    esp = lin.get("cabeca", {})
    r = lin["rampas"]

    def rampa(chave, i):
        op = r.get(chave) or r["pele"]
        return op[int(i) % len(op)]

    brilho_olho = bool(esp.get("olhos_brilho"))
    mats = [
        {"nome": "pele", "rampa": rampa("pele", escolha.get("cp", 0)), "perfil": esp.get("perfil_pele", "pele")},
        {"nome": "cabelo", "rampa": rampa("cabelo", escolha.get("ch", 0)), "perfil": esp.get("cabelo_perfil", "cabelo")},
        {"nome": "sobrancelha", "rampa": rampa("cabelo", escolha.get("ch", 0)), "perfil": "chapado", "tom": 0},
        {"nome": "iris", "rampa": rampa("olhos", escolha.get("co", 0)), "perfil": "brilho" if brilho_olho else "chapado",
         "brilho": brilho_olho, "tom": 4 if brilho_olho else 1},
        {"nome": "roupa", "rampa": rampa("pele", escolha.get("cp", 0)) if esp.get("roupa_pele") else esp.get("roupa", "tecido_linho"),
         "perfil": esp.get("perfil_pele", "pele") if esp.get("roupa_pele") else ("metal" if esp.get("roupa") == "ferro" else "tecido")},
        {"nome": "gorro", "rampa": esp.get("gorro", "blood[1:6]"), "perfil": "tecido"},
        {"nome": "gola", "rampa": esp.get("gola", "blood[1:6]"), "perfil": "tecido"},
        {"nome": "ventre", "rampa": "sand", "perfil": "osso"},
        {"nome": "sapato", "rampa": "couro_escuro", "perfil": "couro"},
        {"nome": "chifre", "rampa": "bone", "perfil": "osso"},
        {"nome": "asa", "rampa": rampa("asa", 0) if "asa" in r else rampa("pele", escolha.get("cp", 0)),
         "perfil": esp.get("perfil_pele", "tecido")},
        {"nome": "asa_olho", "rampa": "void", "perfil": "chapado", "tom": 2},
        {"nome": "chapeu", "rampa": rampa("cabelo", escolha.get("ch", 0)), "perfil": "fungo"},
        {"nome": "chapeu_pinta", "rampa": "bone", "perfil": "chapado", "tom": 4},
        {"nome": "focinho", "rampa": rampa("pele", escolha.get("cp", 0)), "perfil": "chapado", "tom": 3},
        {"nome": "bico", "rampa": "gold", "perfil": "osso", "tom": 1},
        "olho_branco", "escuro", "boca", "ouro",
    ]
    tw, th, td = t["tronco"]
    pe, vao, mao = t["pe"], t["vao"], t["mao"]
    tronco = [{"op": "caixa", "nome": "t", "tam": [tw + co["robusto"], th, td + co["robusto"]], "chanfro": 1,
               "em": "chao", "desloc": {"cima": pe[1] + vao}, "material": "roupa"}]
    if co["ombro"]:
        tronco.append({"op": "caixa", "tam": [tw + co["robusto"] + co["ombro"], max(2, th // 3), td + co["robusto"]],
                       "em": "t.topo", "encaixe": "dentro", "material": "roupa"})
    if co["quadril"]:
        tronco.append({"op": "caixa", "tam": [tw + co["robusto"] + co["quadril"], max(2, th // 3), td + co["robusto"]],
                       "em": "t.base", "encaixe": "dentro", "material": "roupa"})
    tronco.append({"op": "caixa", "tam": [tw + 6, 1, td + 6], "em": "t.base", "encaixe": "dentro",
                   "desloc": {"cima": max(1, th // 4)}, "material": "sapato", "modo": "pintar"})
    cw, ch, cd = cc["cranio"]
    ch -= int(esp.get("cranio_baixo", 0))
    sobe = 1 if esp.get("cranio_baixo") else -1
    if esp.get("lapide"):
        cabeca = [{"op": "caixa", "nome": "cranio", "tam": [cw, ch - 2, 6], "em": "Tronco.t.topo", "desloc": {"cima": sobe}, "material": "pele"},
                  {"op": "caixa", "tam": [cw - 2, 1, 6], "em": "cranio.topo", "material": "pele"},
                  {"op": "caixa", "tam": [cw - 4, 1, 6], "em": "cranio.topo", "desloc": {"cima": 1}, "material": "pele"}]
    else:
        cabeca = [{"op": "caixa", "nome": "cranio", "tam": [cw, ch, cd], "raio": cc["raio"], "em": "Tronco.t.topo",
                   "desloc": {"cima": sobe}, "material": "pele"}]
    foc = esp.get("focinho", cc.get("focinho"))
    if foc:
        cabeca.append({"op": "caixa", "nome": "focinho", "tam": foc, "em": "cranio.frente", "desloc": {"baixo": 2},
                       "material": "bico" if esp.get("bico") else "pele"})
        if esp.get("bico"):
            cabeca.append({"op": "caixa", "tam": [2, 2, 2], "em": "focinho.frente", "desloc": {"baixo": 1}, "material": "bico"})
        if esp.get("focinho_claro"):
            cabeca.append({"op": "caixa", "tam": foc, "em": "focinho", "encaixe": "centro", "material": "focinho", "modo": "pintar"})
        if esp.get("focinho_ponta"):
            cabeca.append({"op": "caixa", "tam": [2, 1, 1], "em": "focinho.topo_frente", "encaixe": "dentro",
                           "material": esp["focinho_ponta"], "modo": "pintar"})
    if esp.get("nariz"):
        cabeca.append({"op": "caixa", "tam": esp["nariz"], "em": "cranio.frente", "desloc": {"baixo": 1}, "material": "pele"})
    if esp.get("sobrolho"):
        cabeca.append({"op": "caixa", "tam": [cw - 2, 2, 1], "em": "cranio.frente", "desloc": {"cima": 2}, "material": "pele"})
    leg = {"B": "olho_branco", "P": "iris", "G": "iris", "E": "escuro", "C": "sobrancelha", "M": "boca", "W": "olho_branco"}

    def arte(tabela, chave, nome):
        if str(chave) not in rosto[tabela]:
            raise ErroFicha(f'{nome} "{chave}" nao existe; opcoes: {list(rosto[tabela])}')
        return rosto[tabela][str(chave)]

    olhos = arte("olhos", escolha.get("o", 1), "olhos")
    oy = cc["olhos_y"] + (1 if foc else 0)
    afast = cc["afast"] if len(olhos[0]) < 3 else max(2, cc["afast"] - 2)
    cabeca.append({"op": "estampa", "em": "cranio", "face": "frente", "desloc": {"cima": oy + (1 if esp.get("olho_unico") else 0)},
                   "linhas": olhos if esp.get("olho_unico") else _linha_olhos(olhos, afast), "legenda": leg})
    sob = arte("sobrancelhas", escolha.get("s", 1), "sobrancelha")
    if sob != ["."]:
        cabeca.append({"op": "estampa", "em": "cranio", "face": "frente", "desloc": {"cima": oy + len(olhos) // 2 + 2},
                       "linhas": _linha_olhos(sob, afast + max(0, len(olhos[0]) - len(sob[0])) * 2), "legenda": leg})
    boca = arte("bocas", escolha.get("b", 1), "boca")
    if boca != ["."]:
        if foc and not esp.get("bico"):
            cabeca.append({"op": "estampa", "em": "focinho", "face": "frente", "desloc": {"baixo": 1}, "linhas": boca, "legenda": leg})
        elif not foc:
            cabeca.append({"op": "estampa", "em": "cranio", "face": "frente", "desloc": {"baixo": ch // 2 - 2}, "linhas": boca, "legenda": leg})
    if esp.get("runas"):
        cabeca.append({"op": "estampa", "em": "cranio", "face": "frente", "desloc": {"baixo": 3},
                       "linhas": ["G.G", ".G.", "G.G"], "legenda": leg})
    if esp.get("ventre_claro"):
        tronco.append({"op": "estampa", "em": "t", "face": "frente", "linhas": ["VVVV"] * max(3, th - 6), "legenda": {"V": "ventre"}})
    if esp.get("runas_no_tronco"):
        tronco.append({"op": "estampa", "em": "t", "face": "frente", "desloc": {"cima": 1}, "linhas": ["G..G", ".GG.", ".G..", "G.G."], "legenda": leg})
    longe = int(esp.get("maos_longe", 0))
    pecas = [{"nome": "Tronco", "formas": tronco}, {"nome": "Cabeca", "formas": cabeca}]
    h = str(escolha.get("h", 1))
    if h not in cabelos:
        raise ErroFicha(f'cabelo "{h}" nao existe; opcoes: ' + ", ".join(f'{k} ({v["nome"]})' for k, v in cabelos.items()))
    if cabelos[h]["formas"] and not esp.get("sem_cabelo"):
        fs = _aplicar(copy.deepcopy(cabelos[h]["formas"]), {"w": cw, "h": ch, "d": cd if not esp.get("lapide") else 6})
        for f in fs:
            f.setdefault("material", "cabelo")
        pecas.append({"nome": "Cabelo", "osso": "Cabeca", "formas": fs})
    for lado, nome in ((1, "D"), (-1, "E")):
        d = "direita" if lado > 0 else "esquerda"
        pecas.append({"nome": f"Mao_{nome}", "formas": [{"op": "caixa", "tam": [mao] * 3, "em": "Tronco.t.dir" if lado > 0 else "Tronco.t.esq",
                      "desloc": {d: t["mao_vao"] + longe + co["ombro"] // 2, "baixo": 1}, "material": "pele"}]})
    for lado, nome in ((1, "D"), (-1, "E")):
        d = "direita" if lado > 0 else "esquerda"
        pecas.append({"nome": f"Pe_{nome}", "formas": [{"op": "caixa", "tam": pe, "em": "chao", "desloc": {d: t["pe_x"], "frente": 0.5},
                      "material": "chifre" if escolha["l"] == "taurino" else "sapato"}]})
    ossos = [{"nome": "Tronco", "pai": "Raiz", "pivo": {"em": "Tronco.t.base"}, "papel": "corpo"},
             {"nome": "Cabeca", "pai": "Tronco", "pivo": {"em": "Cabeca.cranio.base"}, "papel": "cabeca"},
             {"nome": "Mao_D", "pai": "Tronco", "pivo": {"em": "Mao_D.centro"}, "papel": "mao"},
             {"nome": "Mao_E", "pai": "Tronco", "pivo": {"em": "Mao_E.centro"}, "papel": "mao"},
             {"nome": "Pe_D", "pai": "Raiz", "pivo": {"em": "Pe_D.centro"}, "papel": "pe"},
             {"nome": "Pe_E", "pai": "Raiz", "pivo": {"em": "Pe_E.centro"}, "papel": "pe"}]
    regras = {}
    tracos = list(lin.get("tracos", [])) + list(escolha.get("tracos_extra", []))
    for tid in tracos:
        tr = reg.fichas[reg.achar("traco." + tid)]
        for p in copy.deepcopy(tr["pecas"]):
            o = p.pop("osso", "Cabeca")
            p["formas"] = _aplicar(p["formas"], {"w": cw, "h": ch, "d": cd})
            for f in p["formas"]:
                f.setdefault("material", tr.get("material", "pele"))
            if isinstance(o, dict):
                ossos.append({"nome": p["nome"], **o})
                p["osso"] = p["nome"]
            else:
                p["osso"] = o
            if any(x["nome"] == p["nome"] for x in pecas):
                raise ErroFicha(f'dois tracos de {lin["nome"]} criam a peca "{p["nome"]}"; uma linhagem so pode ter um traco de cada tipo')
            pecas.append(p)
            regras[p["nome"]] = {"traco": tid, **tr.get("regras", {})}
    soq = [("Cabeca_Topo", "Cabeca", "Cabeca.cranio.topo"), ("Rosto", "Cabeca", "Cabeca.cranio.frente"),
           ("Costas", "Tronco", "Tronco.t.tras"), ("Ombro_D", "Tronco", "Tronco.t.topo_dir"), ("Ombro_E", "Tronco", "Tronco.t.topo_esq"),
           ("Pegada_D", "Mao_D", "Mao_D.centro"), ("Pegada_E", "Mao_E", "Mao_E.centro"), ("Cintura", "Tronco", "Tronco.t.base_frente"),
           ("Assento", "Tronco", "Tronco.t.base"), ("Pe_D", "Pe_D", "Pe_D.base"), ("Pe_E", "Pe_E", "Pe_E.base")]
    H = t["H_voxels"] * V
    return {"id": f'heroi.{escolha["l"]}_c{corpo}', "tipo": "modelo", "nome": lin["nome"], "materiais": mats, "pecas": pecas,
            "ossos": ossos, "soquetes": [{"nome": n, "osso": o, "em": e} for n, o, e in soq],
            "altura_ref_H": H, "tempo_por_porte": False,
            "meta": {"linhagem": escolha["l"], "corpo": str(corpo), "tamanho": lin["tamanho"], "classe_cabeca": lin["classe_cabeca"],
                     "escolha": escolha, "regras_tracos": regras, "cranio": [cw, ch, cd], "jeito": lin.get("jeito", "natural"),
                     "pose_descanso": lin.get("pose_descanso", "parado"), "flutua": lin.get("pose_descanso") == "pairar"}}


# --------------------------------------------------------------------------- equipamento

def _na_rede(src: Grade, dst: Grade) -> np.ndarray:
    """Ocupacao de `src` escrita nos indices de `dst` (mesmo corte)."""
    out = np.zeros(dst.mat.shape, bool)
    off = np.round((src.origem - dst.origem) / dst.v).astype(int)
    a = np.maximum(off, 0)
    b = np.minimum(off + np.array(src.mat.shape), np.array(dst.mat.shape))
    if np.any(b <= a):
        return out
    sa = a - off
    out[a[0]:b[0], a[1]:b[1], a[2]:b[2]] = src.mat[sa[0]:sa[0] + b[0] - a[0], sa[1]:sa[1] + b[1] - a[1], sa[2]:sa[2] + b[2] - a[2]] > 0
    return out


def _margem(g: Grade, n: int) -> Grade:
    return Grade(v=g.v, origem=g.origem - n * g.v, mat=np.pad(g.mat, n))


def _grade_caixa(mn_studs, mx_studs, margem=3) -> Grade:
    a = np.floor(np.asarray(mn_studs) / V).astype(int) - margem
    b = np.ceil(np.asarray(mx_studs) / V).astype(int) + margem
    return Grade(v=V, origem=a * V, mat=np.zeros(b - a, np.uint8))


def vestir(modelo, conjunto: dict, reg: Registro, paleta, resolver, caixas) -> dict:
    """Aplica um conjunto ao heroi JA MONTADO E AINDA NAO PINTADO. Devolve o relatorio do que foi feito."""
    nomes = [m.nome for m in modelo.materiais]
    for m in materiais_da_ficha(conjunto.get("materiais", []), paleta):
        if m.nome not in nomes:
            modelo.materiais.append(m)
            nomes.append(m.nome)

    def mi(n):
        if n not in nomes:
            raise ErroFicha(f'conjunto {conjunto.get("id")}: material "{n}" nao esta em "materiais" do conjunto. Declarados: {nomes}')
        return nomes.index(n) + 1

    rel = {"recortes": [], "escondidos": [], "movidos": [], "pecas_novas": []}
    regras = modelo.meta.get("regras_tracos", {})
    esc = set(modelo.meta.get("escolha", {}).get("esc", []))
    P = {p.nome: p for p in modelo.pecas}

    def remover(nome):
        modelo.pecas[:] = [p for p in modelo.pecas if p.nome != nome]
        if not any(p.osso == nome for p in modelo.pecas):
            modelo.ossos[:] = [o for o in modelo.ossos if o.nome != nome]
        rel["escondidos"].append(nome)

    def recortar(item: Peca, slot: str, detalhe: int):
        """Aplica as regras dos tracos contra este item."""
        for nome, rg in list(regras.items()):
            if nome not in {p.nome for p in modelo.pecas}:
                continue
            acao = rg.get(slot, "nada")
            if acao == "esconde":
                remover(nome)
            elif acao in ("recorta", "abre_embaixo"):
                tr = next(p for p in modelo.pecas if p.nome == nome)
                vol = ug.dilatar(_na_rede(tr.grade, item.grade), 1, 26)          # volume protegido: traco + 1 voxel
                if acao == "abre_embaixo":
                    col = vol.any(axis=1, keepdims=True)                          # abre a fenda ate a barra
                    ys = np.argwhere(vol)[:, 1]
                    if len(ys):
                        vol = vol | (col & (np.arange(vol.shape[1])[None, :, None] <= ys.max()))
                antes = item.grade.mat.copy()
                corta = vol & (antes > 0)
                if not corta.any():
                    continue
                item.grade.mat[corta] = 0
                _, n = ug.componentes(item.grade.mat > 0)
                if n > 1:                                                         # o furo partiu o item: o item esconde o traco
                    item.grade.mat[:] = antes
                    remover(nome)
                    rel["escondidos"][-1] = f"{nome} (o recorte partia o item)"
                    continue
                borda = ug.dilatar(corta, 1, 6) & (item.grade.mat > 0)
                item.grade.mat[borda] = detalhe                                   # 1 voxel de acabamento na borda
                rel["recortes"].append({"item": item.nome, "traco": nome, "voxels": int(corta.sum())})
            elif acao.startswith("move:"):
                rel["movidos"].append({"traco": nome, "slot": slot, "para": acao[5:]})

    def faixas(g: Grade, spec):
        oc = g.mat > 0
        ys = np.argwhere(oc)[:, 1]
        y0, y1 = ys.min(), ys.max() + 1
        rel_y = (np.arange(g.mat.shape[1]) - y0 + 0.5) / max(y1 - y0, 1)
        ant = 0.0
        for f in spec:
            sel = oc & ((rel_y >= ant) & (rel_y < f["ate"] + 1e-6))[None, :, None]
            g.mat[sel] = mi(f["material"])
            ant = f["ate"]

    # ---- tronco: casca = corpo dilatado em 1 voxel (macica, sem miolo exposto), pintada por faixas de altura
    if "tronco" in conjunto and "tronco" not in esc:
        t = P["Tronco"]
        g = _margem(t.grade, 1)
        g.mat = np.where(ug.dilatar(g.mat > 0, 1, 26), 1, 0).astype(np.uint8)
        faixas(g, conjunto["tronco"]["faixas"])
        emb = conjunto["tronco"].get("emblema")
        if emb:
            oc = g.mat > 0
            zf = np.argwhere(oc)[:, 2].min()
            L = emb["linhas"]
            cx, cy = g.mat.shape[0] // 2, int(g.mat.shape[1] * 0.62)
            for li, linha in enumerate(L):
                for ci, chh in enumerate(linha):
                    if chh != ".":
                        x, y = cx - len(linha) // 2 + ci, cy + len(L) // 2 - li
                        if 0 <= x < g.mat.shape[0] and 0 <= y < g.mat.shape[1] and oc[x, y, zf]:
                            g.mat[x, y, zf] = mi(emb["material"])
        t.grade = g
        recortar(t, "tronco", mi(conjunto["tronco"]["faixas"][-1]["material"]))
    if "luvas" in conjunto and "luvas" not in esc:
        for n in ("Mao_D", "Mao_E"):
            g = _margem(P[n].grade, 1)
            oc = g.mat > 0
            g.mat[oc] = mi(conjunto["luvas"]["material"])
            topo = np.argwhere(oc)[:, 1].max()
            punho = ug.dilatar(oc, 1, 26) & (np.arange(g.mat.shape[1])[None, :, None] == topo)
            g.mat[punho] = mi(conjunto["luvas"].get("detalhe", conjunto["luvas"]["material"]))
            P[n].grade = g
    if "botas" in conjunto and "botas" not in esc:
        for n in ("Pe_D", "Pe_E"):
            g = _margem(P[n].grade, 1)
            oc = ug.dilatar(g.mat > 0, 1, 26)
            oc[:, 0, :] = False                                           # nada abaixo do chao
            g.mat = np.where(oc, mi(conjunto["botas"]["material"]), 0).astype(np.uint8)
            g.mat[:, 1, :][oc[:, 1, :]] = mi(conjunto["botas"].get("detalhe", conjunto["botas"]["material"]))   # sola
            P[n].grade = g
    # ---- elmo / chapeu por classe de cabeca
    cmn, cmx = caixas["Cabeca.cranio"]
    cab = P["Cabeca"]
    for slot in ("elmo", "chapeu"):
        if slot not in conjunto or slot in esc:
            continue
        spec = conjunto[slot]
        g = _grade_caixa(cmn, cmx, margem=5)
        Pg = sdf.eixos(g.mat.shape, np.round(g.origem / V))
        c = (np.asarray(cmn) + np.asarray(cmx)) / 2 / V
        tam = (np.asarray(cmx) - np.asarray(cmn)) / V
        if slot == "elmo":
            ext = sdf.ocupado(sdf.caixa(Pg, c + [0, 0.5, 0], tam + [2, 1, 2], raio=3))
            regra = "elmo_fechado" if spec.get("tipo", "fechado") == "fechado" else "elmo_aberto"
            oc = ext & ~_na_rede(cab.grade, g)
            yy = (Pg[1] - c[1]) + 0 * Pg[0] + 0 * Pg[2]
            xx = Pg[0] - c[0] + 0 * Pg[1] + 0 * Pg[2]
            frente = (Pg[2] < c[2] - tam[2] / 2 + 1.5) + 0 * Pg[0] + 0 * Pg[1] > 0
            oy = reg.fichas["classe_cabeca.tabela"]["classes"][modelo.meta["classe_cabeca"]]["olhos_y"]
            if regra == "elmo_fechado":
                viseira = frente & (((np.abs(yy - oy - 0.0) < 1.0) & (np.abs(xx) < tam[0] / 2 - 1.5)) |
                                    ((np.abs(xx) < 1.0) & (yy < oy) & (yy > -tam[1] / 2 + 2)))
                oc &= ~viseira                                             # viseira em T
                fundo = viseira & ~ug.dilatar(oc, 0, 6)
            else:
                oc &= ~(frente & (np.abs(xx) < tam[0] / 2 - 1.5) & (yy < tam[1] / 2 - 3))
            g.mat = np.where(oc, mi(spec["material"]), 0).astype(np.uint8)
            det = mi(spec.get("detalhe", spec["material"]))
            g.mat[oc & (np.abs(yy + tam[1] / 2 - 0.5) < 0.6)] = det           # debrum na barra
            if spec.get("crista"):
                cr = sdf.ocupado(sdf.caixa(Pg, c + [0, tam[1] / 2 + 1.5, 0.5], [2, 2, tam[2] - 2]))
                g.mat[cr] = det
        else:
            regra = "chapeu"
            ext = sdf.ocupado(sdf.caixa(Pg, c + [0, tam[1] / 2 + 2.0, 0], [tam[0] + 2, 8, tam[2] + 2], raio=2))
            aba = sdf.ocupado(sdf.caixa(Pg, c + [0, tam[1] / 2 - 1.5, 0], [tam[0] + 8, 1, tam[2] + 8], chanfro=2))
            oc = (ext | aba) & ~_na_rede(cab.grade, g)
            g.mat = np.where(oc, mi(spec["material"]), 0).astype(np.uint8)
            fita = oc & ext & (np.abs((Pg[1] - c[1]) - tam[1] / 2 + 0.0) < 0.6 + 0 * Pg[0] + 0 * Pg[2])
            g.mat[fita] = mi(spec.get("detalhe", spec["material"]))
            ext = ext | aba
        item = Peca(nome="Elmo" if slot == "elmo" else "Chapeu_Item", osso="Cabeca", grade=g)
        if "Cabelo" in {p.nome for p in modelo.pecas}:                      # cabelo sob o elmo: apaga so a parte de dentro
            cb = next(p for p in modelo.pecas if p.nome == "Cabelo")
            dentro = _na_rede(Grade(v=V, origem=g.origem, mat=ug.dilatar(ext, 1, 26).astype(np.uint8)), cb.grade)
            cb.grade.mat[dentro] = 0
            if not cb.grade.mat.any():
                remover("Cabelo")
            else:
                rot, n = ug.componentes(cb.grade.mat > 0)                   # mecha solta que sobrou e apagada
                if n > 1:
                    maior = np.bincount(rot[rot > 0]).argmax()
                    cb.grade.mat[(rot > 0) & (rot != maior)] = 0
        modelo.pecas.append(item)
        recortar(item, regra, mi(spec.get("detalhe", spec["material"])))
        item.grade.mat, _ = _maior_componente(item.grade.mat)
        rel["pecas_novas"].append(item.nome)
    # ---- ombreiras: ornamento em tres tamanhos
    if "ombreiras" in conjunto and "ombreiras" not in esc:
        spec = conjunto["ombreiras"]
        tam = {"P": [3, 2, 4], "M": [4, 3, 5], "G": [5, 4, 7]}[modelo.meta["tamanho"]]
        tmn, tmx = caixas["Tronco.t"]
        for lado, nome in ((1, "D"), (-1, "E")):
            if spec.get("so_uma") and spec["so_uma"] != nome:
                continue
            c = np.array([(tmx[0] if lado > 0 else tmn[0]) / V + lado * (tam[0] / 2 - 1), tmx[1] / V + tam[1] / 2 - 1, (tmn[2] + tmx[2]) / 2 / V])
            g = _grade_caixa((c - np.array(tam)) * V, (c + np.array(tam)) * V, margem=2)
            Pg = sdf.eixos(g.mat.shape, np.round(g.origem / V))
            oc = sdf.ocupado(sdf.caixa(Pg, np.round(c * 2) / 2, tam, raio=1))
            g.mat = np.where(oc, mi(spec["material"]), 0).astype(np.uint8)
            esp_ = sdf.ocupado(sdf.caixa(Pg, np.round(c * 2) / 2 + [lado * 0.5, tam[1] / 2 + 0.5, 0], [1, 2 if modelo.meta["tamanho"] != "P" else 1, 1]))
            g.mat[esp_] = mi(spec.get("detalhe", spec["material"]))
            modelo.pecas.append(Peca(nome=f"Ombreira_{nome}", osso="Tronco", grade=g))
            rel["pecas_novas"].append(f"Ombreira_{nome}")
    # ---- capa: placa atras do tronco, com osso proprio e mola
    if "capa" in conjunto and "capa" not in esc:
        spec = conjunto["capa"]
        tmn, tmx = caixas["Tronco.t"]
        larg = (tmx[0] - tmn[0]) / V + 2
        alt = tmx[1] / V - 2
        c = np.array([0, (2 + tmx[1] / V) / 2, tmx[2] / V + 1.5])
        g = _grade_caixa((c - [larg, alt, 2]) * V, (c + [larg, alt, 2]) * V, margem=1)
        Pg = sdf.eixos(g.mat.shape, np.round(g.origem / V))
        oc = sdf.ocupado(sdf.caixa(Pg, np.round(c * 2) / 2, [larg, alt, 1]))
        gola = sdf.ocupado(sdf.caixa(Pg, [0, tmx[1] / V - 0.5, tmx[2] / V + 0.5], [larg, 1, 3]))
        g.mat = np.where(oc | gola, mi(spec["material"]), 0).astype(np.uint8)
        barra = oc & (Pg[1] < 3.5 + 0 * Pg[0] + 0 * Pg[2])
        g.mat[barra & ((np.floor(Pg[0]) % 3 == 0) + 0 * Pg[1] + 0 * Pg[2] > 0)] = 0   # barra recortada
        item = Peca(nome="Capa", osso="Capa", grade=g)
        modelo.ossos.append(Osso("Capa", "Tronco", (0.0, float(tmx[1] - V), float(tmx[2] + V)), "capa",
                                 mola={"freq_hz": 1.5, "amort": 0.6, "max_graus": 30}))
        modelo.pecas.append(item)
        recortar(item, "capa", mi(spec.get("detalhe", spec["material"])))
        item.grade.mat, _ = _maior_componente(item.grade.mat)
        rel["pecas_novas"].append("Capa")
    # ---- itens de mao: uma malha por item, presa na pegada
    for slot, mao in (("mao_principal", "Mao_D"), ("mao_secundaria", "Mao_E")):
        if slot not in conjunto or slot in esc:
            continue
        fi = reg.resolver(conjunto[slot])
        for m in materiais_da_ficha(fi.get("materiais", []), paleta):
            if m.nome not in nomes:
                modelo.materiais.append(m)
                nomes.append(m.nome)
        pcs, anc = construir_pecas(fi["pecas"], nomes)
        soq = {s["nome"]: anc["resolver"]({"em": s.get("em", "centro"), "desloc": s.get("desloc")}, pcs[0].nome) for s in fi.get("soquetes", [])}
        if "Pegada" not in soq:
            raise ErroFicha(f'{fi["id"]}: item de mao precisa do soquete "Pegada" (e de "Ponta" e "Base"). '
                            f'Ex.: {{"nome": "Pegada", "osso": "{pcs[0].nome}", "em": "cabo.centro"}}')
        alvo = np.array(modelo.osso(mao).pivo)
        d = np.round((alvo - soq["Pegada"]) / V) * V
        nome = "Item_D" if mao == "Mao_D" else "Item_E"
        for k, p in enumerate(pcs):
            p.grade.origem = p.grade.origem + d
            p.nome, p.osso = (nome if k == 0 else f"{nome}_{k}"), nome
            modelo.pecas.append(p)
        modelo.ossos.append(Osso(nome, mao, tuple(float(x) for x in alvo), "item"))
        for s, pos in soq.items():
            modelo.soquetes.append(Soquete(f"{nome}_{s}", nome, tuple(float(x) for x in pos + d)))
        modelo.meta.setdefault("itens", {})[nome] = {"id": fi["id"], "pegada": fi.get("pegada", "uma_mao"),
                                                      "comprimento": float(np.linalg.norm(soq.get("Ponta", soq["Pegada"]) - soq["Pegada"]))}
        rel["pecas_novas"].append(nome)
    from ..nucleo.contrato import ordem_topologica
    modelo.ossos[:] = ordem_topologica(modelo.ossos)
    modelo.meta["equipamento"] = {"conjunto": conjunto.get("id"), **rel}
    return rel


def _maior_componente(mat):
    rot, n = ug.componentes(mat > 0)
    if n <= 1:
        return mat, 0
    maior = np.bincount(rot[rot > 0]).argmax()
    out = np.where(rot == maior, mat, 0).astype(mat.dtype)
    return out, int(((rot > 0) & (rot != maior)).sum())


def montar_heroi(reg: Registro, paleta, linhagem: str, *, corpo: str | None = None, predef: int = 1, escolha: dict | None = None,
                 conjunto: str | None = None, clipes: list[dict] | None = None):
    """Devolve o Modelo do heroi (pintado, com clipes se pedidos)."""
    from ..nucleo.anim import assar_clipe
    from ..nucleo.pintura import pintar
    e = escolha_de(reg, linhagem, predef, escolha)
    ficha = ficha_heroi(reg, e, corpo)
    from ..nucleo import montagem
    capt = {}
    orig = montagem.pintar

    def interceptar(modelo, pal, **kw):
        if conjunto:
            cj = reg.fichas[reg.achar(conjunto if conjunto.startswith("conjunto.") else "conjunto." + conjunto)]
            capt["rel"] = vestir(modelo, cj, reg, pal, capt["res"], capt["caixas"])
        return orig(modelo, pal, **kw)

    pcs_orig = montagem.construir_pecas

    def construir(spec, nomes):
        pcs, anc = pcs_orig(spec, nomes)
        capt["res"], capt["caixas"] = anc["resolver"], anc["caixas"]
        return pcs, anc

    montagem.pintar, montagem.construir_pecas = interceptar, construir
    try:
        modelo = montar(ficha, paleta, com_clipes=False)
    finally:
        montagem.pintar, montagem.construir_pecas = orig, pcs_orig
    corpo = modelo.meta["corpo"]
    sufixo = f"_c{corpo}" + (f"_{conjunto.split('.')[-1]}" if conjunto else "")
    modelo.id = f"heroi_{e['l']}{sufixo}"
    H = ficha["altura_ref_H"]
    for r in clipes or []:
        modelo.clipes[r["nome"]] = assar_clipe(modelo, r, H=H, fator_tempo=1.0)
    return modelo
