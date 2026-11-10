"""Linguagem de forma: transforma a lista de operacoes de cada peca em grades de voxels.

Tudo em VOXELS INTEIROS do corte da peca, posicionado por ANCORA + deslocamento semantico
({"frente": 2, "cima": 1, "direita": -3}). Nunca coordenada absoluta. Ver docs/ARQUITETURA.md, secao 5.

Uso:
    pecas, ancoras = construir_pecas(spec_pecas, nomes_materiais)
    ancoras["Tronco.topo"] -> ponto em studs;  ancoras["Cabeca.cranio.frente"] -> idem
"""
from __future__ import annotations

import difflib

import numpy as np

from . import sdf
from .contrato import CORTES, Grade, Peca, desloc_semantico

OPS = ("caixa", "elipsoide", "capsula", "cilindro", "cone", "estampa", "voxels", "placas", "bloco")
MODOS = ("uniao", "so_vazio", "cortar", "pintar")
# normal (em voxels) de cada ancora simples; combinacoes somam (ex.: topo_frente)
_NORMAIS = {"topo": (0, 1, 0), "base": (0, -1, 0), "frente": (0, 0, -1), "tras": (0, 0, 1),
            "dir": (1, 0, 0), "esq": (-1, 0, 0), "centro": (0, 0, 0)}
_CAMPO = 160  # lado da grade de trabalho, em voxels (a peca e recortada no fim)


class ErroFicha(ValueError):
    """Erro de ficha com mensagem que ensina o conserto."""


def _sugerir(nome: str, opcoes) -> str:
    perto = difflib.get_close_matches(str(nome), [str(o) for o in opcoes], n=3, cutoff=0.5)
    return f' Voce quis dizer {perto}?' if perto else ""


class _Caixas:
    """Guarda a caixa (min, max em voxels do modelo) de cada peca e forma nomeada."""

    def __init__(self):
        self.cx: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        self.eixo_x = 0.0
        self.eixos: dict[str, float] = {}   # formas criadas com "espelhar" guardam o eixo, para encadear

    def por(self, nome, mn, mx):
        if nome in self.cx:
            a, b = self.cx[nome]
            mn, mx = np.minimum(a, mn), np.maximum(b, mx)
        self.cx[nome] = (np.asarray(mn, float), np.asarray(mx, float))

    def ponto(self, ref: str, peca_atual: str) -> tuple[np.ndarray, np.ndarray]:
        """Resolve 'chao', 'topo', 'cranio.topo', 'Tronco.topo', 'Tronco.cinto.frente' -> (ponto, normal)."""
        if ref == "chao":
            self.eixo_x = 0.0
            return np.zeros(3), np.array([0.0, 1.0, 0.0])
        partes = ref.split(".")
        anc = partes[-1]
        alvo = ".".join(partes[:-1])
        if anc not in _NORMAIS and not all(p in _NORMAIS for p in anc.split("_")):
            alvo, anc = ref, "centro"
        if alvo == "":
            chave = peca_atual
        elif alvo in self.cx:
            chave = alvo
        elif f"{peca_atual}.{alvo}" in self.cx:
            chave = f"{peca_atual}.{alvo}"
        else:
            raise ErroFicha(f'ancora "{ref}": nao existe peca nem forma chamada "{alvo}". Existem: {sorted(self.cx)}.'
                            f'{_sugerir(alvo, self.cx)} Formato: "topo", "<forma>.frente" ou "<Peca>.topo".')
        if chave not in self.cx:
            raise ErroFicha(f'ancora "{ref}": a peca "{chave}" ainda nao tem forma. A primeira forma de uma peca '
                            f'deve usar "em": "chao" ou a ancora de outra peca, ex.: "Tronco.topo".')
        mn, mx = self.cx[chave]
        p = (mn + mx) / 2
        self.eixo_x = self.eixos.get(chave, float(p[0]))   # eixo de espelho = centro da caixa de referencia
        n = np.zeros(3)
        for parte in anc.split("_"):
            v = np.array(_NORMAIS[parte], float)
            n += v
            for e in range(3):
                if v[e] > 0:
                    p[e] = mx[e]
                elif v[e] < 0:
                    p[e] = mn[e]
        return p, n


def _centro_de(op: dict, tam, caixas: _Caixas, peca: str) -> np.ndarray:
    p, n = caixas.ponto(op.get("em", "chao" if peca not in caixas.cx else "centro"), peca)
    enc = op.get("encaixe", "fora")
    if enc not in ("fora", "dentro", "centro"):
        raise ErroFicha(f'"encaixe": "{enc}" invalido; use "fora" (encosta por fora da face), "dentro" ou "centro".')
    s = {"fora": 0.5, "dentro": -0.5, "centro": 0.0}[enc]
    c = p + np.sign(n) * np.asarray(tam, float) * s + desloc_semantico(op.get("desloc"))
    # alinhar a rede: dimensao par -> centro em borda de voxel; impar -> em centro de voxel
    t = np.asarray(tam, float)
    par = (np.round(t) % 2 == 0)
    return np.where(par, np.round(c), np.floor(c) + 0.5)


def _ponto_livre(spec, op, caixas, peca) -> np.ndarray:
    """Ponto de capsula: {"em": ancora, "desloc": {...}} ou so um deslocamento a partir de op["em"]."""
    if isinstance(spec, dict) and "em" in spec:
        p, _ = caixas.ponto(spec["em"], peca)
        return p + desloc_semantico(spec.get("desloc"))
    p, _ = caixas.ponto(op.get("em", "centro"), peca)
    return p + desloc_semantico(spec if isinstance(spec, dict) else None)


def _expandir(formas: list[dict]) -> list[dict]:
    """"repetir": {"n": 4, "passo": {"tras": 3}} vira n copias da forma, cada uma deslocada um passo a mais.
    Serve para dentes, garras, espinhos, costelas, placas. A copia i (a partir da 2a) chama-se <nome>_<i>."""
    out = []
    for op in formas:
        r = op.get("repetir")
        if not r:
            out.append(op)
            continue
        if not isinstance(r, dict) or "n" not in r:
            raise ErroFicha('"repetir" precisa de {"n": quantas, "passo": {"tras": 3}} (passo em voxels, com nome de direcao).')
        for i in range(int(r["n"])):
            c = {k: v for k, v in op.items() if k != "repetir"}
            d = dict(c.get("desloc") or {})
            for kk, vv in (r.get("passo") or {}).items():
                d[kk] = d.get(kk, 0) + vv * i
            c["desloc"] = d
            if i and c.get("nome"):
                c["nome"] = f'{c["nome"]}_{i + 1}'
            out.append(c)
    return out


_NOME_EIXO = {0: ("direita", "esquerda"), 1: ("cima", "baixo"), 2: ("tras", "frente")}


def _placas(op: dict, caixas: "_Caixas", peca: str, onde: str) -> list[dict]:
    """"op": "placas" cobre uma face de uma forma com uma grade de placas em relevo (escamas, couraca, rebites).
    {"op": "placas", "em": "t", "face": "topo", "tam": [3, 1, 3], "vao": 1, "margem": 2, "material": "detalhe"}
    "tam" e o tamanho de UMA placa nos eixos do modelo; "so_borda": true deixa so o anel de fora (coroa de espinhos)."""
    ref, face = op.get("em", ""), op.get("face", "topo")
    if face not in sdf.FACES:
        raise ErroFicha(f'{onde}: "face": "{face}" invalida; use uma de {list(sdf.FACES)}.')
    chave = ref if ref in caixas.cx else f"{peca}.{ref}"
    if chave not in caixas.cx:
        raise ErroFicha(f'{onde}: "placas" precisa de "em" com o nome de uma forma ja feita. Existem: {sorted(caixas.cx)}.')
    mn, mx = caixas.cx[chave]
    F = sdf.FACES[face]
    eu, ev = F["u"][0], F["v"][0]
    tam = [int(x) for x in op.get("tam", [3, 1, 3])]
    vao, mar = int(op.get("vao", 1)), int(op.get("margem", 1))
    out = []
    conta = []
    for e in (eu, ev):
        livre = (mx[e] - mn[e]) - 2 * mar
        n = int((livre + vao) // (tam[e] + vao))
        conta.append((n, tam[e] + vao))
    (nu, pu), (nv, pv) = conta
    for i in range(nu):
        for j in range(nv):
            if op.get("so_borda") and 0 < i < nu - 1 and 0 < j < nv - 1:
                continue
            du = (i - (nu - 1) / 2) * pu
            dv = (j - (nv - 1) / 2) * pv
            d = {}
            for e, val in ((eu, du), (ev, dv)):
                if val:
                    d[_NOME_EIXO[e][0] if val > 0 else _NOME_EIXO[e][1]] = abs(val)
            out.append({"op": "caixa", "tam": tam, "em": f"{chave}.{face}", "desloc": d, "material": op.get("material", "")})
    return out


def construir_pecas(spec_pecas: list[dict], nomes_materiais: list[str], campo: int | None = None) -> tuple[list[Peca], dict]:
    """Constroi todas as pecas. Devolve (pecas, ancoras em studs). `campo` = lado da grade de trabalho em voxels
    (padrao 160 = 20 studs); chefe grande pede mais."""
    global _CAMPO
    antigo = _CAMPO
    if campo:
        _CAMPO = int(campo)
    try:
        return _construir_pecas(spec_pecas, nomes_materiais)
    finally:
        _CAMPO = antigo


def _construir_pecas(spec_pecas: list[dict], nomes_materiais: list[str]) -> tuple[list[Peca], dict]:
    indice = {n: i + 1 for i, n in enumerate(nomes_materiais)}
    caixas = _Caixas()
    pecas: list[Peca] = []
    cortes: dict[str, float] = {}
    meio = _CAMPO // 2
    off = np.array([meio, 16, meio], float)  # voxel do modelo (0,0,0) fica neste indice da grade de trabalho

    def mat_de(nome, onde):
        if nome not in indice:
            raise ErroFicha(f'{onde}: material "{nome}" nao foi declarado em "materiais". Declarados: '
                            f'{sorted(indice)}.{_sugerir(nome, indice)}')
        return indice[nome]

    for sp in spec_pecas:
        nome = sp["nome"]
        corte = sp.get("corte", "grade")
        if corte not in CORTES:
            raise ErroFicha(f'peca "{nome}": corte "{corte}" invalido; use um de {list(CORTES)}.')
        v = CORTES[corte]
        cortes[nome] = v
        # as caixas guardadas estao em voxels DESTE corte quando todas as pecas usam o mesmo corte; pecas de
        # cortes diferentes sao convertidas por fator inteiro
        g = np.zeros((_CAMPO,) * 3, np.uint8)
        fila = list(_expandir(sp.get("formas", [])))
        i = -1
        while fila:
            op = fila.pop(0)
            i += 1
            onde = f'peca "{nome}", forma {i + 1}'
            tipo = op.get("op")
            if tipo not in OPS:
                raise ErroFicha(f'{onde}: "op": "{tipo}" nao existe. Use uma de {list(OPS)}.{_sugerir(tipo, OPS)}')
            if tipo == "placas":                          # vira varias caixas, com as medidas da forma de referencia
                fila[:0] = _placas(op, caixas, nome, onde)
                i -= 1
                continue
            modo = op.get("modo", "uniao")
            if modo not in MODOS:
                raise ErroFicha(f'{onde}: "modo": "{modo}" invalido; use um de {list(MODOS)}.')
            lados = [1, -1] if op.get("espelhar") else [1]
            for lado in lados:
                oc, mn, mx, mat_arr = _avaliar(op, tipo, lado, g, caixas, nome, off, mat_de, onde)
                if oc is None:
                    continue
                sl = tuple(slice(int(a), int(b)) for a, b in zip(mn + off, mx + off))
                alvo = g[sl]
                m = mat_arr if mat_arr is not None else mat_de(op.get("material", ""), onde) if modo != "cortar" else 0
                if modo == "uniao":
                    alvo[oc] = m[oc] if isinstance(m, np.ndarray) else m
                elif modo == "so_vazio":
                    sel = oc & (alvo == 0)
                    alvo[sel] = m[sel] if isinstance(m, np.ndarray) else m
                elif modo == "cortar":
                    alvo[oc] = 0
                elif modo == "pintar":
                    sel = oc & (alvo > 0)
                    alvo[sel] = m[sel] if isinstance(m, np.ndarray) else m
                if modo != "cortar":
                    idx = np.argwhere(oc)
                    if len(idx):
                        bmn, bmx = mn + idx.min(0), mn + idx.max(0) + 1
                        caixas.por(nome, bmn, bmx)
                        if op.get("nome") and op.get("espelhar"):
                            caixas.eixos[f'{nome}.{op["nome"]}'] = caixas.eixo_x
                        if op.get("nome"):
                            if lado == 1:
                                caixas.cx.pop(f'{nome}.{op["nome"]}', None)
                            caixas.por(f'{nome}.{op["nome"]}' + ("" if lado == 1 or not op.get("espelhar") else "_E"),
                                       bmn, bmx)
        idx = np.argwhere(g > 0)
        if len(idx) == 0:
            raise ErroFicha(f'peca "{nome}" ficou vazia: nenhuma forma ocupou voxel. Confira "tam" (minimo 1) e "modo".')
        a, b = idx.min(0), idx.max(0) + 1
        grade = Grade(v=v, origem=(a - off) * v, mat=g[a[0]:b[0], a[1]:b[1], a[2]:b[2]].copy())
        caixas.cx[nome] = (a - off, b - off)
        pecas.append(Peca(nome=nome, osso=sp.get("osso", nome), grade=grade,
                          escala_animada=bool(sp.get("escala_animada", False))))

    ancoras = {}
    for chave, (mn, mx) in caixas.cx.items():
        v = cortes.get(chave.split(".")[0], CORTES["grade"])
        ancoras[chave] = (mn * v, mx * v)
    return pecas, {"caixas": ancoras, "resolver": lambda ref, peca="": _resolver(caixas, cortes, ref, peca)}


def _resolver(caixas: _Caixas, cortes, ref: str, peca: str = "") -> np.ndarray:
    """Ancora -> ponto em studs (para pivos e soquetes). ref pode ser str ou {"em":..., "desloc":...}."""
    desloc = None
    if isinstance(ref, dict):
        ref, desloc = ref.get("em", "chao"), ref.get("desloc")
    p, _ = caixas.ponto(ref, peca)
    alvo = ref.split(".")[0] if ref != "chao" else peca
    v = cortes.get(alvo if alvo in cortes else peca, CORTES["grade"])
    return (p + desloc_semantico(desloc)) * v


def _avaliar(op, tipo, lado, g, caixas, peca, off, mat_de, onde):
    """Devolve (ocupacao local, min, max em voxels do modelo, array de material ou None)."""
    def esp(p):  # espelha em X, em torno do centro da caixa de referencia (vale para largura par e impar)
        p = np.array(p, float)
        if lado < 0:
            p[0] = 2 * caixas.eixo_x - p[0]
        return p

    if tipo == "bloco":                                   # caixa em coordenada absoluta: so para ficha importada por programa
        c, t = np.array(op["centro"], float), np.array(op["tam"], float)
        mn, mx = np.floor(c - t / 2 + 1e-6), np.floor(c - t / 2 + 1e-6) + np.round(t)
        return np.ones((mx - mn).astype(int), bool), mn, mx, None
    if tipo == "voxels":
        pts = np.array(op.get("pontos", []), float).reshape(-1, 3)
        base, _ = caixas.ponto(op.get("em", "centro"), peca)
        pts = np.floor(esp(base) + pts * [lado, 1, 1])
        mn, mx = pts.min(0), pts.max(0) + 1
        oc = np.zeros((mx - mn).astype(int), bool)
        for q in (pts - mn).astype(int):
            oc[tuple(q)] = True
        return oc, mn, mx, None
    if tipo == "estampa":
        return _estampa(op, g, caixas, peca, off, mat_de, onde)
    if tipo == "capsula":
        a = esp(_ponto_livre(op.get("de"), op, caixas, peca))
        b = esp(_ponto_livre(op.get("ate"), op, caixas, peca))
        r0 = float(op.get("r0", op.get("raio", 1)))
        r1 = float(op.get("r1", r0))
        rm = max(r0, r1) + 1
        mn, mx = np.floor(np.minimum(a, b) - rm), np.ceil(np.maximum(a, b) + rm)
        P = sdf.eixos((mx - mn).astype(int), mn)
        return sdf.ocupado(sdf.capsula(P, a, b, r0, r1)), mn, mx, None
    tam = op.get("tam")
    if not (isinstance(tam, (list, tuple)) and len(tam) == 3 and all(isinstance(t, (int, float)) for t in tam)):
        raise ErroFicha(f'{onde}: "tam" deve ser [largura, altura, profundidade] em voxels, ex.: "tam": [8, 10, 5].')
    if min(tam) < 1:
        raise ErroFicha(f'{onde}: "tam" {tam} tem dimensao menor que 1 voxel e a forma some. Use no minimo 1.')
    c = esp(_centro_de(op, tam, caixas, peca))
    t = np.asarray(tam, float)
    mn, mx = np.floor(c - t / 2 - 1), np.ceil(c + t / 2 + 1)
    P = sdf.eixos((mx - mn).astype(int), mn)
    if tipo == "caixa":
        fino = min(tam) < 5   # regra de arte: nada de chanfro/raio grande em peca pequena (vira "cruz")
        d = sdf.caixa(P, c, t, raio=min(float(op.get("raio", 0)), 1.0 if fino else 99),
                      chanfro=0.0 if fino else float(op.get("chanfro", 0)))
    elif tipo == "elipsoide":
        d = sdf.elipsoide(P, c, t)
    elif tipo == "cilindro":
        d = sdf.cilindro(P, c, t, eixo=op.get("eixo", "y"))
    else:
        d = sdf.cone(P, c, t, eixo=op.get("eixo", "y"), sentido=int(op.get("sentido", 1)),
                     raio_ponta=float(op.get("raio_ponta", 0)))
    return sdf.ocupado(d), mn, mx, None


def _estampa(op, g, caixas, peca, off, mat_de, onde):
    """Arte em texto aplicada numa face: pinta (profundidade 0), faz relevo (>0) ou cava (<0)."""
    linhas = op.get("linhas") or []
    face = op.get("face", "frente")
    if face not in sdf.FACES:
        raise ErroFicha(f'{onde}: "face": "{face}" invalida; use uma de {list(sdf.FACES)}.')
    if not linhas or len({len(l) for l in linhas}) != 1:
        raise ErroFicha(f'{onde}: "linhas" da estampa precisam ter todas o mesmo comprimento. '
                        f'Ex.: ["B..B", "BPPB"]. Recebi comprimentos {[len(l) for l in linhas]}.')
    leg = op.get("legenda", {})
    F = sdf.FACES[face]
    (en, sn), (eu, su), (ev, sv) = F["n"], F["u"], F["v"]
    ref = op.get("em", face)
    p, _ = caixas.ponto(ref if "." in ref or ref in _NORMAIS or ref == "chao" else f"{ref}.{face}", peca)
    p = p + desloc_semantico(op.get("desloc"))
    h, w = len(linhas), len(linhas[0])
    prof = int(op.get("profundidade", 0))
    G = g
    pts, mats = [], []
    for li, linha in enumerate(linhas):
        for ci, ch in enumerate(linha):
            if ch == ".":
                continue
            if ch not in leg:
                raise ErroFicha(f'{onde}: a letra "{ch}" da estampa nao esta na "legenda" {leg}. '
                                f'Acrescente, ex.: "legenda": {{"{ch}": "olho_pupila"}}.')
            q = np.zeros(3)
            q[eu] = np.floor(p[eu] - su * w / 2.0 + su * (ci + 0.5) + 1e-6)
            q[ev] = np.floor(p[ev] + sv * h / 2.0 - sv * (li + 0.5) + 1e-6)
            # acha a superficie nessa coluna, varrendo de fora para dentro ao longo da normal
            col = [slice(None)] * 3
            i_u, i_v = int(q[eu] + off[eu]), int(q[ev] + off[ev])
            if not (0 <= i_u < _CAMPO and 0 <= i_v < _CAMPO):
                continue
            col[eu], col[ev] = i_u, i_v
            linha_vox = G[tuple(col)]
            oc = np.flatnonzero(linha_vox)
            if len(oc) == 0:
                continue
            sup = oc.max() if sn > 0 else oc.min()
            m = mat_de(leg[ch], onde)
            passos = range(0, 1) if prof == 0 else range(1, prof + 1) if prof > 0 else range(0, -prof)
            for k in passos:
                r = q.copy()
                r[en] = sup - off[en] + (sn * k if prof >= 0 else -sn * k)
                pts.append(r)
                mats.append(0 if prof < 0 else m)
            if prof < 0 and op.get("fundo"):
                r = q.copy()
                r[en] = sup - off[en] - sn * (-prof)
                pts.append(r)
                mats.append(mat_de(op["fundo"], onde))
    if not pts:
        return None, None, None, None
    pts = np.array(pts)
    mn, mx = pts.min(0), pts.max(0) + 1
    forma = (mx - mn).astype(int)
    oc = np.zeros(forma, bool)
    ma = np.zeros(forma, np.uint8)
    for q, m in zip((pts - mn).astype(int), mats):
        oc[tuple(q)] = True
        ma[tuple(q)] = m
    # voxels com material 0 significam "cavar": aplicamos direto e tiramos da uniao
    cav = oc & (ma == 0)
    if cav.any():
        sl = tuple(slice(int(a), int(b)) for a, b in zip(mn + off, mx + off))
        g[sl][cav] = 0
        oc &= ~cav
    return oc, mn, mx, ma
