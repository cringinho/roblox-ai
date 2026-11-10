"""Montagem: ficha resolvida -> Modelo (pecas, ossos, soquetes, pintura, clipes)."""
from __future__ import annotations

import numpy as np

from . import sdf
from .anim import assar_clipe
from .contrato import CORTES, Material, Modelo, Osso, Soquete
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
    mats = materiais_da_ficha(ficha.get("materiais"), paleta)
    pecas, anc = construir_pecas(ficha["pecas"], [m.nome for m in mats])
    res = anc["resolver"]
    nomes_pecas = [p.nome for p in pecas]
    ossos: list[Osso] = []
    declarados = {o["nome"]: o for o in ficha.get("ossos", [])}
    if "Raiz" not in declarados:
        ossos.append(Osso("Raiz", None, (0.0, 0.0, 0.0), "raiz"))
    for o in ficha.get("ossos", []):
        peca_ref = o["nome"] if o["nome"] in nomes_pecas else (nomes_pecas[0] if nomes_pecas else "")
        piv = res(o.get("pivo", "base"), peca_ref) if o.get("pivo") != "origem" else np.zeros(3)
        v = CORTES["grade"]
        piv = np.round(np.asarray(piv) / (v / 2)) * (v / 2)
        ossos.append(Osso(o["nome"], o.get("pai", "Raiz") if o["nome"] != "Raiz" else None, tuple(float(x) for x in piv),
                          o.get("papel", "corpo"), o.get("limites"), o.get("mola")))
    for p in pecas:                       # peca sem osso declarado: osso proprio, pivo na base, filho da Raiz
        if p.osso not in {o.nome for o in ossos}:
            a, b = p.grade.caixa()
            ossos.append(Osso(p.osso, "Raiz", (float((a[0] + b[0]) / 2), float(a[1]), float((a[2] + b[2]) / 2)), "corpo"))
    nomes = {o.nome for o in ossos}
    for o in ossos:
        if o.pai and o.pai not in nomes:
            raise ErroFicha(f'osso "{o.nome}" tem "pai": "{o.pai}", que nao existe. Ossos: {sorted(nomes)}.')
    modelo = Modelo(id=ficha["id"].split(".", 1)[-1], nome=ficha.get("nome", ficha["id"]), pecas=pecas,
                    ossos=_ordenar(ossos), materiais=mats, meta=dict(ficha.get("meta", {})))
    _juntas(modelo, ficha)
    for s in ficha.get("soquetes", []):
        if s["osso"] not in nomes:
            raise ErroFicha(f'soquete "{s["nome"]}": osso "{s["osso"]}" nao existe. Ossos: {sorted(nomes)}.')
        pos = res({"em": s.get("em", "centro"), "desloc": s.get("desloc")}, s["osso"] if s["osso"] in nomes_pecas else nomes_pecas[0])
        modelo.soquetes.append(Soquete(s["nome"], s["osso"], tuple(float(x) for x in pos)))
    modelo.meta["pintura"] = pintar(modelo, paleta, acabamentos=ficha.get("acabamentos"), semente=semente)
    if com_clipes:
        mn, mx = modelo.caixa()
        H = float(ficha.get("altura_ref_H", mx[1] - mn[1]))
        k = float(ficha.get("porte_k", max(H / 4.0, 0.25)))
        for r in ficha.get("clipes", []):
            cl = assar_clipe(modelo, r, H=H, fator_tempo=float(np.sqrt(k)) if ficha.get("tempo_por_porte", True) else 1.0)
            modelo.clipes[cl.nome] = cl
    return modelo


def _ordenar(ossos):
    from .contrato import ordem_topologica
    return ordem_topologica(ossos)


def _juntas(modelo: Modelo, ficha: dict):
    """Junta sobreposta: osso com "junta": r ganha, na peca-filha, uma esfera de raio r voxels centrada no pivo
    (a esfera nao muda quando gira, entao a junta nao abre). Material = o mais comum da peca perto do pivo."""
    por_nome = {o["nome"]: o for o in ficha.get("ossos", [])}
    for p in modelo.pecas:
        o = por_nome.get(p.osso)
        if not o or not o.get("junta"):
            continue
        r = float(o["junta"])
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
