"""Esteira: ficha -> P0 -> forma -> pintura -> clipes -> P1 -> exporta -> P2 -> folha -> relatorio."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .nucleo import auditoria, exporta, render
from .nucleo.contrato import VERSAO_FABRICA
from .nucleo.forma import ErroFicha
from .nucleo.montagem import montar
from .nucleo.paleta import Paleta
from .registro import RAIZ, ErroRegistro, Registro

SAIDA = RAIZ / "saida"
_TIPO_PERFIL = {"monstro": "monstro", "npc": "monstro", "item": "item", "prop": "prop", "modelo": "monstro", "arquetipo": "monstro"}


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def construir(ref: str, *, registro: Registro | None = None, paleta: Paleta | None = None, saida: Path | None = None,
              semente: int = 0, data: str = "", imagens: bool = True, exportar: bool = True, tier: int | None = None) -> dict:
    """Constroi um asset de ponta a ponta. Devolve o relatorio (tambem gravado em saida/<id>/relatorio.json)."""
    t0 = time.time()
    registro = registro or Registro()
    paleta = paleta or Paleta.carregar()
    rel: dict = {"fabrica": VERSAO_FABRICA, "semente": semente, "data": data, "status": "reprovado", "etapas": {}}
    try:
        idc = registro.achar(ref)
        erros = registro.validar(idc)
        rel["id"] = idc
        rel["p0"] = {"passou": not erros, "erros": erros}
        if erros:
            return rel
        ficha = registro.resolver(idc)
        if tier:                                          # construir a mesma ficha noutro tier (prova da escada)
            ficha = {**ficha, "tier": int(tier)}
        rel["hash_ficha"] = _hash(ficha)
        modelo = montar(ficha, paleta, semente=semente)
        if tier:
            modelo.id = f"{modelo.id}_t{int(tier)}"
    except (ErroFicha, ErroRegistro, ValueError, KeyError) as e:
        rel.setdefault("id", ref)
        rel["p0"] = {"passou": False, "erros": [str(e)]}
        return rel
    return finalizar(modelo, ficha.get("tipo", "monstro"), rel, perfil=ficha.get("perfil_auditoria"), saida=saida, imagens=imagens, exportar=exportar, t0=t0)


def finalizar(modelo, tipo: str, rel: dict | None = None, *, saida: Path | None = None, imagens: bool = True,
              exportar: bool = True, t0: float | None = None, perfil: str | None = None) -> dict:
    """P1, exportacao, P2, imagens e relatorio para um Modelo ja montado (usado tambem pelo heroi)."""
    t0 = t0 or time.time()
    rel = rel if rel is not None else {"fabrica": VERSAO_FABRICA, "id": modelo.id, "p0": {"passou": True, "erros": []}}
    pasta = Path(saida) if saida else SAIDA / modelo.id
    pasta.mkdir(parents=True, exist_ok=True)
    pf = perfil or _TIPO_PERFIL.get(tipo, "monstro")
    r1 = auditoria.p1(modelo, pf)
    rel["p1"] = {"passou": all(r["passou"] for r in r1), "regras": r1}
    arquivos = {}
    if exportar:
        idl = exporta._id_luau(modelo.id)
        est = exporta.escrever_glb(modelo, pasta / "modelo.glb")
        exporta.escrever_vox(modelo, pasta / "modelo.vox")
        (pasta / f"Dados_{idl}.luau").write_text(exporta.luau_dados(modelo), encoding="utf-8")
        if modelo.clipes:
            (pasta / f"Clipes_{idl}.luau").write_text(exporta.luau_clipes(modelo), encoding="utf-8")
        rel["malha"] = est
    r2 = auditoria.p2(modelo, pf)
    rel["p2"] = r2
    if imagens:
        render.folha_conferencia(modelo, pasta / "folha.png", metricas={"P2": r2["nota"]})
        render.icone_pixel(modelo, 64).save(pasta / "icone_64.png")
        if modelo.clipes:
            for nome, cl in modelo.clipes.items():
                render.tira_animacao(modelo, cl, pasta / f"anim_{nome}.png")
            render.gif_animacao(modelo, list(modelo.clipes.values()), pasta / "anim.gif")
    for arq in sorted(pasta.iterdir()):
        if arq.name not in ("relatorio.json", "proveniencia.json") and arq.is_file():
            arquivos[arq.name] = hashlib.sha256(arq.read_bytes()).hexdigest()
    rel["status"] = "aprovado" if rel["p0"]["passou"] and rel["p1"]["passou"] and r2["passou"] else "reprovado"
    rel["numeros"] = {"voxels": modelo.n_voxels(), "pecas": len(modelo.pecas), "ossos": len(modelo.ossos),
                      "cores": len(modelo.cores), "triangulos": modelo.meta.get("triangulos"),
                      "clipes": list(modelo.clipes), "segundos": round(time.time() - t0, 2)}
    (pasta / "relatorio.json").write_text(json.dumps(rel, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    prov = {"id": rel.get("id", modelo.id), "hash_ficha": rel.get("hash_ficha"), "semente": rel.get("semente", 0),
            "fabrica": VERSAO_FABRICA, "data": rel.get("data", ""), "arquivos": arquivos,
            "metodo": "Gerado por codigo procedural a partir de uma ficha de dados. Sem IA de imagem, sem modelos de "
                      "terceiros, sem digitalizacao. A ficha e o codigo foram escritos com assistencia de IA de texto, "
                      "sob direcao de arte humana.",
            "responsavel": ""}
    (pasta / "proveniencia.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False), encoding="utf-8")
    rel["pasta"] = str(pasta)
    return rel


def resumo(rel: dict) -> str:
    """Texto curto para a CLI: status, o que reprovou e o conserto."""
    L = [f'{rel.get("id")}: {rel["status"].upper()}']
    if not rel["p0"]["passou"]:
        L += ["  P0 (ficha) reprovou:"] + [f"   - {e}" for e in rel["p0"]["erros"]]
        return "\n".join(L)
    n = rel.get("numeros", {})
    L.append(f'  {n.get("voxels")} voxels, {n.get("pecas")} pecas, {n.get("triangulos")} triangulos, {n.get("cores")} cores, '
             f'clipes {n.get("clipes")}, {n.get("segundos")} s')
    ruins = [r for r in rel["p1"]["regras"] if not r["passou"]]
    L.append("  P1 passou" if not ruins else "  P1 reprovou:")
    L += [f'   - {r["regra"]}: {r["valor"]} (limite {r["limite"]}). {r["conserto"]}' for r in ruins]
    p2 = rel["p2"]
    L.append(f'  P2 nota {p2["nota"]} (minimo {p2["minimo"]})' + ("" if p2["passou"] else "  REPROVOU"))
    for x in p2["piores"]:
        if x["nota"] < 0.999:
            L.append(f'   - {x["metrica"]} ({x["nota"]}): {x["conserto"]}')
    L.append(f'  arquivos em {rel.get("pasta")}')
    return "\n".join(L)
