"""Comandos do heroi: heroi, elenco, matriz. E o JEITO de cada linhagem (camadas por cima dos clipes base)."""
from __future__ import annotations

import copy
import json

from PIL import Image, ImageDraw

from .. import esteira
from ..nucleo import render
from ..nucleo.paleta import Paleta
from ..registro import RAIZ
from .montar import montar_heroi

# O que cada estilo muda nos clipes base (multiplicadores) e que gesto acrescenta ao Parado.
ESTILOS = {
    "natural": dict(amp=1.0, dur=1.0),
    "pesado": dict(amp=0.7, dur=1.25),       # tempos longos, pouca oscilacao, assenta
    "eterio": dict(amp=1.3, dur=1.2),        # flutua, atrasos longos, sem impacto
    "staccato": dict(amp=0.9, dur=0.9),      # estalos com pausa
    "espasmodico": dict(amp=0.8, dur=1.0),   # tiques secos
    "manco": dict(amp=1.0, dur=1.1),         # um pe arrasta
    "marionete": dict(amp=1.1, dur=1.1),
}


def jeito(receitas: list[dict], modelo) -> list[dict]:
    """Aplica o jeito da linhagem e liga os ossos de tracos (asas, cauda, gorro, capa)."""
    est = modelo.meta.get("jeito", "natural")
    cfg = ESTILOS.get(est, ESTILOS["natural"])
    ossos = {o.nome for o in modelo.ossos}
    out = []
    for r in copy.deepcopy(receitas):
        nome = r["nome"]
        if nome in ("Parado",):
            r["duracao"] *= cfg["dur"]
            for c in r["camadas"]:
                if c["tipo"] == "onda":
                    c["amp"] *= cfg["amp"]
        cam = r["camadas"]
        laco = r.get("laco")
        if nome == "Parado":
            if est == "staccato":
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {}}, {"t": 0.30, "curva": "degrau", "pose": {"Cabeca": {"esquerda": 18}}},
                            {"t": 0.34, "curva": "golpe", "pose": {"Cabeca": {"esquerda": 18, "tombar_direita": 12}}},
                            {"t": 0.62, "curva": "degrau", "pose": {"Cabeca": {"esquerda": 18, "tombar_direita": 12}}},
                            {"t": 0.66, "curva": "golpe", "pose": {"Cabeca": {"esquerda": -14}}}, {"t": 0.9, "curva": "degrau", "pose": {"Cabeca": {"esquerda": -14}}},
                            {"t": 0.94, "curva": "golpe", "pose": {}}]})
            if est == "espasmodico":
                cam.append({"tipo": "tremor", "osso": "Cabeca", "canal": "tombar_direita", "amp": 9, "de_t": 0.42, "ate_t": 0.5, "segurar": 2})
                cam.append({"tipo": "tremor", "ossos": ["Mao_D", "Mao_E"], "canal": "cima", "amp": 0.02, "de_t": 0.44, "ate_t": 0.55, "segurar": 2})
            if est == "pesado":
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {}}, {"t": 0.55, "curva": "linear", "pose": {}},
                            {"t": 0.62, "curva": "golpe", "pose": {"Tronco": {"tombar_direita": 4, "baixo": 0.012}, "Pe_D": {"cima": 0.0}}},
                            {"t": 0.72, "curva": "passa_e_volta", "pose": {"Tronco": {"tombar_direita": -3}}}, {"t": 0.95, "curva": "suave", "pose": {}}]})
            if est == "manco":
                cam.append({"tipo": "onda", "osso": "Tronco", "canal": "tombar_direita", "amp": 3, "harm": 1, "fase": 0.4})
        if nome == "Andar" and est == "manco":
            for c in cam:
                if c["tipo"] == "passos":
                    c["pes"][1]["fase"] = 0.62
                    c["altura_H"] = 0.05
            cam.append({"tipo": "onda", "osso": "Tronco", "canal": "tombar_direita", "amp": 6, "harm": 1, "fase": 0.1})
        if nome == "Andar" and est == "pesado":
            for c in cam:
                if c["tipo"] == "onda" and c["osso"] == "Tronco" and c["canal"] == "cima":
                    c["amp"] *= 1.5
        # ---- ossos de tracos e de equipamento
        if {"Asa_D", "Asa_E"} <= ossos:
            voa = modelo.meta.get("pose_descanso") == "pairar"
            bat = (21 if nome == "Parado" else 5) if voa else (1 if nome == "Parado" else 2)
            if laco:
                cam.append({"tipo": "onda", "osso": "Asa_D", "canal": "esquerda", "amp": 15 if voa else 5, "harm": bat, "forma": "asa"})
                cam.append({"tipo": "onda", "osso": "Asa_E", "canal": "esquerda", "amp": -15 if voa else -5, "harm": bat, "forma": "asa", "fase": 0.03})
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {"Asa_D": {"esquerda": 33 if voa else 8}, "Asa_E": {"esquerda": -33 if voa else -8}}},
                                                         {"t": 1, "pose": {"Asa_D": {"esquerda": 33 if voa else 8}, "Asa_E": {"esquerda": -33 if voa else -8}}}]})
            if voa and nome == "Parado":       # pairar: o corpo inteiro sobe e desce 0,08 stud a cada 1,2 s
                h = modelo.meta.get("H", 3.0)
                cam.append({"tipo": "onda", "ossos": ["Tronco", "Pe_D", "Pe_E"], "canal": "cima", "amp": 0.08 / h, "harm": 5, "fase_por_osso": 0.02})
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {"Tronco": {"cima": 0.25 / h}, "Pe_D": {"cima": 0.25 / h, "frente": -25}, "Pe_E": {"cima": 0.25 / h, "frente": -18}}},
                                                         {"t": 1, "pose": {"Tronco": {"cima": 0.25 / h}, "Pe_D": {"cima": 0.25 / h, "frente": -25}, "Pe_E": {"cima": 0.25 / h, "frente": -18}}}]})
        if "Cauda" in ossos and laco:
            cam.append({"tipo": "onda", "osso": "Cauda", "canal": "esquerda", "amp": 14 if est != "pesado" else 6, "harm": 2 if nome == "Parado" else 1, "fase": 0.2, "harm2": 0.3})
            cam.append({"tipo": "onda", "osso": "Cauda", "canal": "frente", "amp": 5, "harm": 2, "fase": 0.45})
        for mole in ("Gorro", "Chapeu", "Capa"):
            if mole in ossos and laco:
                cam.append({"tipo": "onda", "osso": mole, "canal": "frente", "amp": -7 if mole == "Capa" and nome == "Andar" else 3, "harm": 2, "fase": 0.35})
                cam.append({"tipo": "onda", "osso": mole, "canal": "tombar_direita", "amp": 3, "harm": 1, "fase": 0.2})
        if "Capa" in ossos and nome == "Andar":
            cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {"Capa": {"frente": -16}}}, {"t": 1, "pose": {"Capa": {"frente": -16}}}]})
        if nome == "Golpe" and "Item_D" not in ossos:
            pass
        out.append(r)
    return out


def clipes_do_heroi(reg, modelo) -> list[dict]:
    base = reg.fichas["clipe.heroi"]["clipes"]
    return jeito(base, modelo)


def construir_heroi(reg, pal, linhagem, *, corpo=None, predef=1, conjunto=None, com_clipes=True):
    from ..nucleo.anim import assar_clipe
    m = montar_heroi(reg, pal, linhagem, corpo=corpo, predef=predef, conjunto=conjunto)
    H = {"P": 3.0, "M": 4.0, "G": 5.0}[m.meta["tamanho"]]
    m.meta["H"] = H
    if com_clipes:
        for r in clipes_do_heroi(reg, m):
            m.clipes[r["nome"]] = assar_clipe(m, r, H=H)
    return m


def _celula(m, nome, px=34):
    a = render.render_modelo(m, vista="tres_quartos", px_por_stud=px)
    b = render.render_modelo(m, vista="grade", px_por_stud=24)
    b = b.resize((b.width * 2, b.height * 2), Image.NEAREST)
    w, h = max(a.width + b.width + 8, 150), max(a.height, b.height) + 22
    im = Image.new("RGB", (w, h), (30, 26, 36))
    im.paste(a, (0, h - 22 - a.height))
    im.paste(b, (a.width + 8, h - 22 - b.height))
    ImageDraw.Draw(im).text((4, h - 16), nome, fill=(236, 228, 243))
    return im


def _grade(celulas, colunas, caminho, titulo):
    lw = max(c.width for c in celulas) + 10
    lh = max(c.height for c in celulas) + 10
    linhas = (len(celulas) + colunas - 1) // colunas
    f = Image.new("RGB", (lw * colunas + 10, lh * linhas + 34), (30, 26, 36))
    ImageDraw.Draw(f).text((10, 8), titulo, fill=(236, 228, 243))
    for i, c in enumerate(celulas):
        f.paste(c, (10 + (i % colunas) * lw, 30 + (i // colunas) * lh + (lh - 10 - c.height)))
    f.save(caminho)
    return caminho


ORDEM = ["peregrino_nobre", "peregrino_corrompido", "peregrino_mutacao", "elfo", "anao", "demonio", "meio_elfo", "gigante",
         "ciclope", "draconato", "fada", "ninfa", "gnomo", "lobisomem", "vampiro"]


def rodar(a, reg) -> int:
    pal = Paleta.carregar()
    pasta = RAIZ / "saida" / "_elenco"
    pasta.mkdir(parents=True, exist_ok=True)
    lins = [l for l in ORDEM if f"linhagem.{l}" in reg.fichas] + sorted(
        i.split(".", 1)[1] for i in reg.listar("linhagem") if i.split(".", 1)[1] not in ORDEM)
    if a.cmd == "heroi":
        m = construir_heroi(reg, pal, a.linhagem, corpo=a.corpo if a.corpo != "1" else None, predef=a.predef, conjunto=a.conjunto)
        rel = esteira.finalizar(m, "heroi", {"fabrica": "4", "id": "heroi." + m.id, "p0": {"passou": True, "erros": []}}, perfil="heroi")
        print(esteira.resumo(rel))
        if m.meta.get("equipamento"):
            print("  equipamento:", json.dumps(m.meta["equipamento"], ensure_ascii=False))
        return 0 if rel["status"] == "aprovado" else 1
    if a.cmd == "elenco":
        conj = [i.split(".", 1)[1] for i in reg.listar("conjunto")] if a.conjuntos else []
        cel, quadros = [], []
        for k, l in enumerate(lins):
            m = construir_heroi(reg, pal, l, conjunto=conj[k % len(conj)] if conj else None)
            cel.append(_celula(m, reg.fichas[f"linhagem.{l}"]["nome"]))
            quadros.append(render.quadros_animacao(m, m.clipes["Parado"], px_por_stud=26, passo=6)[:30])
        nome = "elenco_vestido" if conj else "elenco"
        print(_grade(cel, 5, pasta / f"{nome}.png", f"As {len(lins)} linhagens" + (" vestidas" if conj else "") + ": 3/4 e camera da grade (2x)"))
        # GIF do Parado, todas lado a lado
        n = min(len(q) for q in quadros)
        lw, lh = max(q[0].width for q in quadros) + 6, max(q[0].height for q in quadros) + 6
        cols = 5
        fr = []
        for i in range(n):
            f = Image.new("RGB", (lw * cols, lh * ((len(quadros) + cols - 1) // cols)), render.FUNDO)
            for k, q in enumerate(quadros):
                f.paste(q[i], ((k % cols) * lw, (k // cols) * lh + lh - 6 - q[i].height))
            fr.append(f.quantize(128, dither=Image.Dither.NONE))
        fr[0].save(pasta / f"{nome}_parado.gif", save_all=True, append_images=fr[1:], duration=200, loop=0)
        print(pasta / f"{nome}_parado.gif")
        return 0
    if a.cmd == "matriz":
        from ..nucleo import auditoria
        casos = [("fada", "1"), ("gnomo", "2"), ("elfo", "1"), ("demonio", "2"), ("draconato", "1"), ("gigante", "3")]
        cel, ruim, linhas = [], 0, []
        for l, c in casos:
            if f"linhagem.{l}" not in reg.fichas:
                continue
            m = construir_heroi(reg, pal, l, corpo=c, conjunto=a.conjunto, com_clipes=False)
            r1 = auditoria.p1(m, "heroi")
            falhas = [r["regra"] for r in r1 if not r["passou"]]
            eq = m.meta.get("equipamento", {})
            ruim += bool(falhas)
            linhas.append(f'  {l:<12} corpo {c} ({m.meta["tamanho"]}): ' + ("ok" if not falhas else f"REPROVOU {falhas}") +
                          f'  recortes {[(x["item"], x["traco"]) for x in eq.get("recortes", [])]}  escondidos {eq.get("escondidos", [])}')
            fr = render.render_modelo(m, vista="tres_quartos", px_por_stud=34)
            co = render.render_modelo(m, vista="tres_quartos_costas", px_por_stud=34)
            im = Image.new("RGB", (fr.width + co.width + 6, max(fr.height, co.height) + 22), (30, 26, 36))
            im.paste(fr, (0, 0)); im.paste(co, (fr.width + 6, 0))
            ImageDraw.Draw(im).text((4, im.height - 16), f'{l} {m.meta["tamanho"]}{c}' + ("  REPROVOU" if falhas else ""), fill=(236, 228, 243))
            cel.append(im)
        (RAIZ / "saida" / "_matriz").mkdir(parents=True, exist_ok=True)
        print(_grade(cel, 3, RAIZ / "saida" / "_matriz" / f"{a.conjunto}.png", f"Matriz de prova: {a.conjunto} (frente e costas)"))
        print("\n".join(linhas))
        return 1 if ruim else 0
    return 1
