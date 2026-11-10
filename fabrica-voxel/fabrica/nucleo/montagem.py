"""Montagem: ficha resolvida -> Modelo (pecas, ossos, soquetes, pintura, clipes)."""
from __future__ import annotations

import numpy as np

from . import sdf
from .anim import assar_clipe
from .contrato import CORTES, Grade, Material, Modelo, Osso, Peca, Soquete, quat_semantico
from .forma import ErroFicha, construir_pecas
from .paleta import Paleta
from .pintura import pintar


def materiais_da_ficha(lista, paleta: Paleta) -> list[Material]:
    """Cada item e um nome da tabela padrao ("ferro") ou {"nome", "como"|"rampa", "perfil", "brilho", "tom"}."""
    out = []
    for m in lista or []:
        try:
            if isinstance(m, str):
                out.append(paleta.material(m))
            elif "como" in m:
                out.append(paleta.material(m["como"], como=m["nome"], rampa=m.get("rampa"), perfil=m.get("perfil"),
                                           brilho=m.get("brilho"), tom=m.get("tom")))
            else:
                mat = Material(nome=m["nome"], rampa=m["rampa"], perfil=m.get("perfil", "tecido"),
                               brilho=bool(m.get("brilho", False)), tom=int(m.get("tom", -1)))
                paleta.conferir_material(mat)
                out.append(mat)
        except KeyError as e:
            raise ErroFicha(f'material {m!r}: {e.args[0] if e.args else e}. Formato: "ferro" (da tabela) ou '
                            f'{{"nome": "manto", "como": "tecido", "rampa": "tecido_vinho"}}.') from None
    if len({m.nome for m in out}) != len(out):
        raise ErroFicha(f"materiais com nome repetido: {[m.nome for m in out]}. De um \"nome\" unico a cada um.")
    return out


def montar(ficha: dict, paleta: Paleta, *, semente: int = 0, com_clipes: bool = True) -> Modelo:
    tier = int(ficha.get("tier", 1) or 1)
    if tier > 1 and ficha.get("tipo") in ("monstro", "arquetipo", "npc") and not ficha.get("tier_manual"):
        from .tier import elevar
        ficha = elevar(ficha, tier)                       # T2..T10: maior, mais repeticoes, mais ossos, mais ornamento
    mats = materiais_da_ficha(ficha.get("materiais"), paleta)
    pecas, anc = construir_pecas(ficha["pecas"], [m.nome for m in mats], campo=ficha.get("campo"))
    if tier > 1:
        for p in pecas:
            _colar_soltos(p)
    res = anc["resolver"]
    nomes_pecas = [p.nome for p in pecas]
    ossos: list[Osso] = []
    declarados = {o["nome"]: o for o in ficha.get("ossos", [])}
    if "Raiz" not in declarados:
        ossos.append(Osso("Raiz", None, (0.0, 0.0, 0.0), "raiz"))
    for o in ficha.get("ossos", []):
        peca_ref = o["nome"] if o["nome"] in nomes_pecas else (nomes_pecas[0] if nomes_pecas else "")
        v = CORTES["grade"]
        if isinstance(o.get("pivo"), dict) and "abs" in o["pivo"]:        # ficha importada: pivo em voxels do modelo
            piv = np.array(o["pivo"]["abs"], float) * v
        else:
            piv = res(o.get("pivo", "base"), peca_ref) if o.get("pivo") != "origem" else np.zeros(3)
        piv = np.round(np.asarray(piv) / (v / 2)) * (v / 2)
        ossos.append(Osso(o["nome"], o.get("pai", "Raiz") if o["nome"] != "Raiz" else None, tuple(float(x) for x in piv),
                          o.get("papel", "corpo"), o.get("limites"), o.get("mola"), _repouso(o)))
    for p in pecas:                       # peca sem osso declarado: osso proprio, pivo na base, filho da Raiz
        if p.osso not in {o.nome for o in ossos}:
            a, b = p.grade.caixa()
            ossos.append(Osso(p.osso, "Raiz", (float((a[0] + b[0]) / 2), float(a[1]), float((a[2] + b[2]) / 2)), "corpo"))
    modelo = Modelo(id=ficha["id"].split(".", 1)[-1], nome=ficha.get("nome", ficha["id"]), pecas=pecas,
                    ossos=ossos, materiais=mats, meta={**dict(ficha.get("meta", {})), "tier": tier})
    juntas = {o["nome"]: float(o["junta"]) for o in ficha.get("ossos", []) if o.get("junta")}
    _segmentar(modelo, ficha, juntas)
    _juntas(modelo, juntas)
    nomes = {o.nome for o in modelo.ossos}
    for s in ficha.get("soquetes", []):
        if s["osso"] not in nomes:
            raise ErroFicha(f'soquete "{s["nome"]}": osso "{s["osso"]}" nao existe. Ossos: {sorted(nomes)}.')
        if "abs" in s:
            pos = np.array(s["abs"], float) * CORTES["grade"]
        else:
            pos = res({"em": s.get("em", "centro"), "desloc": s.get("desloc")}, s["osso"] if s["osso"] in nomes_pecas else nomes_pecas[0])
        modelo.soquetes.append(Soquete(s["nome"], _osso_do_ponto(modelo, s["osso"], pos), tuple(float(x) for x in pos)))
    modelo.meta["pintura"] = pintar(modelo, paleta, acabamentos=ficha.get("acabamentos"), semente=semente)
    if com_clipes:
        mn, mx = modelo.caixa()
        H = float(ficha.get("altura_ref_H", mx[1] - mn[1]))
        k = float(ficha.get("porte_k", max(H / 4.0, 0.25)))
        for r in ficha.get("clipes", []):
            cl = assar_clipe(modelo, r, H=H, fator_tempo=float(np.sqrt(k)) if ficha.get("tempo_por_porte", True) else 1.0)
            modelo.clipes[cl.nome] = cl
    return modelo


def _colar_soltos(p: Peca, alcance: int = 4):
    """Ao subir de tier, as medidas sao arredondadas e um detalhe pequeno (garra, presa, placa de borda) pode ficar a
    1 ou 2 voxels do corpo. Cada pedaco solto anda o minimo, numa das 6 direcoes, ate encostar no maior pedaco."""
    from . import util_grade as ug
    g = p.grade
    rot, n = ug.componentes(g.mat > 0)
    if n <= 1:
        return
    mat = np.pad(g.mat, alcance)
    rot = np.pad(rot, alcance)
    maior = int(np.bincount(rot[rot > 0]).argmax())
    corpo = rot == maior
    for k in range(1, n + 1):
        if k == maior:
            continue
        comp = rot == k
        feito = False
        for d in range(1, alcance + 1):
            for eixo in range(3):
                for s in (1, -1):
                    mv = np.roll(comp, s * d, axis=eixo)
                    if (ug.dilatar(mv, 1, 6) & corpo).any():
                        vals = np.roll(np.where(comp, mat, 0), s * d, axis=eixo)
                        mat[comp] = 0
                        mat[mv & (mat == 0)] = vals[mv & (mat == 0)]
                        corpo = corpo | mv
                        feito = True
                        break
                if feito:
                    break
            if feito:
                break
    idx = np.argwhere(mat > 0)
    a, b = idx.min(0), idx.max(0) + 1
    g.origem = g.origem + (a - alcance) * g.v
    g.mat = mat[a[0]:b[0], a[1]:b[1], a[2]:b[2]].copy()


def _repouso(o: dict):
    """"repouso": {"frente": 12, "esquerda": 0, "tombar_direita": 0} -> quaternion. Sem o campo, osso reto."""
    if o.get("repouso_quat"):                              # ficha importada: giro ja em quaternion
        return tuple(float(x) for x in o["repouso_quat"])
    r = o.get("repouso")
    if not r or not isinstance(r, dict):
        return (0.0, 0.0, 0.0, 1.0)
    ruins = set(r) - {"frente", "esquerda", "tombar_direita"}
    if ruins:
        raise ErroFicha(f'osso "{o["nome"]}": "repouso" aceita frente, esquerda e tombar_direita (graus); nao {sorted(ruins)}.')
    return tuple(float(x) for x in quat_semantico(r.get("frente", 0), r.get("esquerda", 0), r.get("tombar_direita", 0)))


def _ordenar(ossos):
    from .contrato import ordem_topologica
    return ordem_topologica(ossos)


MODOS_SEGUIR = ("livre", "cotovelo", "joelho", "reverso")


def _segmentar(modelo: Modelo, ficha: dict, juntas: dict):
    """Osso com "segmentos": 2 (ou [0.55, 0.45]) tem a peca cortada ao longo do eixo mais comprido, do pivo para
    a ponta. Nascem as pecas e os ossos <Nome>_2, <Nome>_3..., em cadeia. O primeiro pedaco fica com o nome
    original, entao os clipes que citam o osso continuam valendo. "dobra" diz como a cadeia se comporta:
    joelho (perna), reverso (perna de ave ou de cao), cotovelo (braco), livre (cauda, pescoco, tentaculo).
    Qualquer osso tambem pode declarar "seguir_pai": {"modo", "ganho", "atraso_s"} para acompanhar o pai."""
    cadeias: dict = {}
    seguir: dict = {}
    for o in ficha.get("ossos", []):
        if o.get("seguir_pai"):
            sp = dict(o["seguir_pai"]) if isinstance(o["seguir_pai"], dict) else {}
            if sp.get("modo", "livre") not in MODOS_SEGUIR:
                raise ErroFicha(f'osso "{o["nome"]}": "seguir_pai.modo" deve ser um de {list(MODOS_SEGUIR)}.')
            seguir[o["nome"]] = {"modo": sp.get("modo", "livre"), "ganho": float(sp.get("ganho", 0.5)),
                                 "atraso_s": float(sp.get("atraso_s", 0.07))}
        if o.get("cadeia_com"):                              # cadeia entre dois ossos ja declarados (heroi: Perna + Pe)
            filho = o["cadeia_com"]
            if filho not in {x.nome for x in modelo.ossos}:
                raise ErroFicha(f'osso "{o["nome"]}": "cadeia_com": "{filho}" nao existe.')
            pr, pf = np.array(modelo.osso(o["nome"]).pivo), np.array(modelo.osso(filho).pivo)
            if abs(pr[0] - pf[0]) > 1e-6 or abs(pr[2] - pf[2]) > 1e-6 or pf[1] >= pr[1]:
                raise ErroFicha(f'osso "{o["nome"]}": para "cadeia_com", o pivo de "{filho}" precisa estar reto abaixo do pivo de '
                                f'"{o["nome"]}" (mesmo x e z). Use a mesma coluna para as duas pecas.')
            desc, cresceu = {filho}, True
            while cresceu:
                cresceu = False
                for x in modelo.ossos:
                    if x.pai in desc and x.nome not in desc:
                        desc.add(x.nome)
                        cresceu = True
            base = min(p.grade.caixa()[0][1] for p in modelo.pecas if p.osso in desc)
            dobra = o.get("dobra", {"perna": "joelho", "braco": "cotovelo"}.get(o.get("papel", ""), "livre"))
            cadeias[o["nome"]] = {"ossos": [o["nome"], filho], "comprimentos": [round(float(pr[1] - pf[1]), 4), round(float(pf[1] - base), 4)],
                                  "eixo": 1, "sentido": -1.0, "dobra": dobra}
            seguir[filho] = {"modo": dobra, "ganho": float(o.get("ganho_seguir", 0.5)), "atraso_s": float(o.get("atraso_seguir_s", 0.07))}
            continue
        seg = o.get("segmentos")
        if not seg:
            continue
        nome = o["nome"]
        fr = [1.0] * int(seg) if isinstance(seg, int) else [float(x) for x in seg]
        if len(fr) < 2 or min(fr) <= 0:
            raise ErroFicha(f'osso "{nome}": "segmentos" deve ser 2, 3 ou 4, ou uma lista de proporcoes como [0.55, 0.45].')
        fr = np.array(fr) / sum(fr)
        dobra = o.get("dobra", {"perna": "joelho", "braco": "cotovelo"}.get(o.get("papel", ""), "livre"))
        if dobra not in MODOS_SEGUIR:
            raise ErroFicha(f'osso "{nome}": "dobra" deve ser um de {list(MODOS_SEGUIR)}.')
        pcs = [p for p in modelo.pecas if p.osso == nome]
        if not pcs:
            raise ErroFicha(f'osso "{nome}" tem "segmentos" mas nenhuma peca usa esse osso.')
        osso = modelo.osso(nome)
        piv = np.array(osso.pivo)
        cx = [p.grade.caixa() for p in pcs]
        mn, mx = np.min([c[0] for c in cx], 0), np.max([c[1] for c in cx], 0)
        eixo = {"x": 0, "y": 1, "z": 2}[o["eixo"]] if o.get("eixo") in ("x", "y", "z") else int(np.argmax(mx - mn))
        sentido = 1.0 if abs(piv[eixo] - mn[eixo]) <= abs(piv[eixo] - mx[eixo]) else -1.0
        ini, comp, v = (mn[eixo] if sentido > 0 else mx[eixo]), float(mx[eixo] - mn[eixo]), pcs[0].grade.v
        lim = [0.0] + [float(round(c * comp / v) * v) for c in np.cumsum(fr)[:-1]] + [comp]
        while o.get("segmentos_tolerante") and len(fr) > 1 and any(b - a < 2 * v for a, b in zip(lim[:-1], lim[1:])):
            fr = np.ones(len(fr) - 1) / (len(fr) - 1)     # peca curta: um segmento a menos, ate caber
            lim = [0.0] + [float(round(c * comp / v) * v) for c in np.cumsum(fr)[:-1]] + [comp]
        if len(fr) < 2:
            continue
        if any(b - a < v for a, b in zip(lim[:-1], lim[1:])):
            raise ErroFicha(f'osso "{nome}": a peca tem {int(round(comp / v))} voxels no eixo comprido; e pouco para '
                            f'{len(fr)} segmentos. Use menos segmentos ou alongue a peca.')
        nomes = [nome] + [f"{nome}_{i + 2}" for i in range(len(fr) - 1)]
        novas = {n: [] for n in nomes}
        for p in pcs:
            g = p.grade
            dist = (g.origem[eixo] + (np.arange(g.mat.shape[eixo]) + 0.5) * g.v - ini) * sentido
            for i, (a, b) in enumerate(zip(lim[:-1], lim[1:])):
                idx = np.nonzero((dist >= a) & (dist < b + (1e-6 if i == len(fr) - 1 else 0)))[0]
                if not len(idx):
                    continue
                sl = [slice(None)] * 3
                sl[eixo] = slice(int(idx[0]), int(idx[-1]) + 1)
                mat = g.mat[tuple(sl)].copy()
                if not mat.any():
                    continue
                org = np.array(g.origem, float)
                org[eixo] += idx[0] * g.v
                novas[nomes[i]].append(Peca(nome=(nomes[i] if p is pcs[0] else f"{p.nome}_{i + 1}" if i else p.nome),
                                            osso=nomes[i], grade=Grade(v=g.v, origem=org, mat=mat), escala_animada=p.escala_animada))
        pos = modelo.pecas.index(pcs[0])
        modelo.pecas[:] = [p for p in modelo.pecas if p not in pcs]
        compr, ossos_cadeia = [], [nome]
        for i, n in enumerate(nomes):
            for q in novas[n]:
                modelo.pecas.insert(pos, q)
                pos += 1
            compr.append(lim[i + 1] - lim[i])
            if i == 0 or not novas[n]:
                continue
            c = np.array(piv, float)                         # pivo na reta que desce do pivo do osso: a cadeia fica
            c[eixo] = ini + sentido * lim[i]                 # reta em repouso, que e o que o IK de dois ossos supoe
            c = np.round(c / (v / 2)) * (v / 2)
            modelo.ossos.append(Osso(n, nomes[i - 1], tuple(float(x) for x in c), f'{osso.papel}_seg', None, osso.mola,
                                     _repouso({"nome": n, "repouso": (o.get("repouso_segmentos") or [None] * 9)[i - 1]})))
            ossos_cadeia.append(n)
            if o.get("junta"):
                juntas[n] = float(o["junta"])
            seguir[n] = {"modo": dobra, "ganho": float(o.get("ganho_seguir", 0.5)), "atraso_s": float(o.get("atraso_seguir_s", 0.07))}
        cadeias[nome] = {"ossos": ossos_cadeia, "comprimentos": [round(c, 4) for c in compr[:len(ossos_cadeia)]],
                         "eixo": eixo, "sentido": sentido, "dobra": dobra}
    nomes = {x.nome for x in modelo.ossos}
    for x in modelo.ossos:                                   # so agora: o pai pode ser um segmento (ex.: "Braco_D_2")
        if x.pai and x.pai not in nomes:
            raise ErroFicha(f'osso "{x.nome}" tem "pai": "{x.pai}", que nao existe. Ossos: {sorted(nomes)}.')
    modelo.ossos[:] = _ordenar(modelo.ossos)
    modelo.meta["cadeias"] = cadeias
    modelo.meta["seguir"] = seguir


def _osso_do_ponto(modelo: Modelo, osso: str, pos) -> str:
    """Soquete declarado num osso que foi segmentado vai para o segmento que contem o ponto (ex.: a mao na ponta)."""
    cad = modelo.meta.get("cadeias", {}).get(osso)
    if not cad:
        return osso
    melhor, dmin = osso, 1e9
    for n in cad["ossos"]:
        for p in modelo.pecas:
            if p.osso == n and p.grade.n_voxels():
                a, b = p.grade.caixa()
                d = float(np.linalg.norm(np.maximum(a - pos, 0) + np.maximum(pos - b, 0)))
                if d < dmin - 1e-9:
                    melhor, dmin = n, d
    return melhor


def _juntas(modelo: Modelo, raios: dict):
    """Junta sobreposta: osso com "junta": r ganha, na peca-filha, uma esfera de raio r voxels centrada no pivo
    (a esfera nao muda quando gira, entao a junta nao abre). Material = o mais comum da peca perto do pivo."""
    for p in modelo.pecas:
        if p.osso not in raios or p.nome != next(q.nome for q in modelo.pecas if q.osso == p.osso):
            continue
        r = float(raios[p.osso])
        g = p.grade
        c = (np.array(modelo.osso(p.osso).pivo) - g.origem) / g.v
        mn = np.floor(np.minimum(c - r - 1, 0)).astype(int)
        mx = np.ceil(np.maximum(c + r + 1, g.mat.shape)).astype(int)
        novo = np.zeros(mx - mn, np.uint8)
        novo[tuple(slice(-mn[i], -mn[i] + g.mat.shape[i]) for i in range(3))] = g.mat
        P = sdf.eixos(novo.shape, mn)
        esf = sdf.ocupado(sdf.elipsoide(P, c, (2 * r, 2 * r, 2 * r))) & (novo == 0)
        vals, cont = np.unique(g.mat[g.mat > 0], return_counts=True)
        novo[esf] = vals[cont.argmax()]
        g.mat, g.origem = novo, g.origem + mn * g.v
