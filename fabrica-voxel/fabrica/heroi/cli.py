"""Comandos do heroi: heroi, elenco, matriz. E o JEITO de cada linhagem (camadas por cima dos clipes base)."""
from __future__ import annotations

import copy
import json

import numpy as np

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
                cam.append({"tipo": "tremor", "ossos": ["Braco_D", "Braco_E"], "canal": "frente", "amp": 7, "de_t": 0.44, "ate_t": 0.55, "segurar": 2})
            if est == "pesado":
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": {}}, {"t": 0.55, "curva": "linear", "pose": {}},
                            {"t": 0.62, "curva": "golpe", "pose": {"Tronco": {"tombar_direita": 4}}},
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
            if voa and laco:                    # pairar: corpo e pernas sobem juntos; as pernas pendem um pouco para tras
                h = modelo.meta.get("H", 3.0)
                sobe = {"Tronco": {"cima": 0.25 / h}, "Perna_D": {"cima": 0.25 / h, "frente": 24}, "Perna_E": {"cima": 0.25 / h, "frente": 16}}
                cam[:] = [c for c in cam if c.get("tipo") != "passos"]     # voando nao pisa
                if nome == "Andar":
                    r["vel_raiz"] = 8.0 / r["duracao"]
                cam.append({"tipo": "onda", "ossos": ["Tronco", "Perna_D", "Perna_E"], "canal": "cima", "amp": 0.08 / h, "harm": 5})
                cam.append({"tipo": "onda", "osso": "Perna_D", "canal": "frente", "amp": 6, "harm": 2, "fase": 0.1})
                cam.append({"tipo": "onda", "osso": "Perna_E", "canal": "frente", "amp": 5, "harm": 2, "fase": 0.4})
                cam.append({"tipo": "poses", "chaves": [{"t": 0, "pose": sobe}, {"t": 1, "pose": sobe}]})
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


def _ajustar_golpe(m, receita, cam, H) -> dict:
    """O mesmo golpe serve em corpos de larguras diferentes: abaixa o plano, leva o centro para a frente e abre o
    raio ate o arco passar por fora deste corpo. Fica com o primeiro candidato limpo (o mais perto da ficha)."""
    from ..nucleo import colisao
    from ..nucleo.anim import assar_clipe
    base = cam["ficha"]
    cenas = [colisao._Cena(m, it) for it in colisao.itens(m)]

    def pior(cl):
        from ..nucleo.contrato import matrizes_do_quadro
        return max(c.dentro(matrizes_do_quadro(m, cl, q)) for q in range(0, cl.n_quadros, 2) for c in cenas)

    melhor = (pior(m.clipes[receita["nome"]]), None, m.clipes[receita["nome"]])
    if melhor[0] > 0:
        # primeiro o corte em pe, cada vez mais aberto; se a cabeca for grande demais para o braco (porte P), o corte
        # deita: varre na horizontal, abaixo da cabeca
        for plano in (base.get("plano_graus", 70), 60, 50, 80, 12, 4):
            for frente in (base.get("centro_H", {}).get("frente", 0.05), 0.10, 0.16):
                for raio in (-0.02, -0.08, -0.14, -0.2):           # com braco: "raio" = altura do centro do arco (mais baixo livra a cabeca)
                    f = copy.deepcopy(base)
                    f["plano_graus"] = plano
                    f.setdefault("centro_H", {})["frente"] = frente
                    f["centro_H"]["cima"] = raio
                    cam["ficha"] = f
                    cl = assar_clipe(m, receita, H=H)
                    d = pior(cl)
                    if d < melhor[0] - 1e-9:
                        melhor = (d, {"plano_graus": plano, "centro_frente_H": frente, "centro_cima_H": raio}, cl)
                    if d == 0:
                        break
                if melhor[0] == 0:
                    break
            if melhor[0] == 0:
                break
        if melhor[0] > 0:          # nenhum corte livra (cabeca grande, braco curto): estocada baixa, pelo lado da arma
            for lado_c in (0.06, 0.10, 0.14):
                for cima in (-0.14, -0.2, -0.1):
                    f = copy.deepcopy(base)
                    f["plano_graus"] = 0
                    f["arco"].update({"inicio_graus": 22, "fim_graus": -6, "guarda_graus": 8, "recuo": 0.55})
                    f["centro_H"] = {"lado": lado_c, "cima": cima, "frente": 0.0}
                    f.setdefault("tronco", {})["giro_graus"] = 10
                    cam["ficha"] = f
                    cl = assar_clipe(m, receita, H=H)
                    d = pior(cl)
                    if d < melhor[0] - 1e-9:
                        melhor = (d, {"estocada": True, "centro_lado_H": lado_c, "centro_cima_H": cima}, cl)
                    if d == 0:
                        break
                if melhor[0] == 0:
                    break
        cam["ficha"] = base
        m.clipes[receita["nome"]] = melhor[2]
    return {"dentro_antes_do_desvio": round(melhor[0], 4), "mudou": melhor[1]}


def clipes_do_heroi(reg, modelo) -> list[dict]:
    base = copy.deepcopy(reg.fichas["clipe.heroi"]["clipes"])
    cad = modelo.meta.get("cadeias", {}).get("Perna_D")
    armado = {o.pai for o in modelo.ossos if o.papel == "item"}
    for mao in armado:               # antebraco que segura item fica na dobra escolhida pela empunhadura; nao balanca sozinho
        modelo.meta.get("seguir", {}).pop(mao, None)
    # morte: o tronco deita para a frente em torno do quadril; desce so o bastante para encostar no chao, sem afundar
    tr = modelo.osso("Tronco")
    pt = next((p for p in modelo.pecas if p.nome == "Tronco"), None)
    if pt is not None:
        a, b = pt.grade.caixa()
        queda = max(0.0, (tr.pivo[1] - (b[2] - a[2]) / 2 - 0.0625) / modelo.meta.get("H", 4.0))
        for r in base:
            if r["nome"] == "Morte":
                for c in r["camadas"]:
                    if c["tipo"] == "poses":
                        for ch in c["chaves"]:
                            if "baixo" in ch.get("pose", {}).get("Tronco", {}):
                                ch["pose"]["Tronco"]["baixo"] = round(queda * min(1.0, ch["pose"]["Tronco"]["baixo"] / 0.2), 4)
    for r in base:
        if r["nome"] == "Andar" and cad:
            # a grade manda na velocidade (8 studs por ciclo do clipe); perna curta da mais passos no mesmo tempo
            L = sum(cad["comprimentos"])
            ciclos = int(np.clip(round(8.0 / (3.3 * L)), 2, 3))
            modelo.meta["passos_por_clipe"] = ciclos
            for c in r["camadas"]:
                if c["tipo"] == "passos":
                    c["ciclos"], c["passada_H"] = ciclos, c["passada_H"] / ciclos
                    c["altura_H"] = min(c.get("altura_H", 0.05), 0.2 * L / modelo.meta.get("H", 4.0))
                elif c["tipo"] == "onda":
                    c["harm"] = int(c.get("harm", 1)) * ciclos
        for c in r["camadas"]:                                   # mao que segura item balanca menos e fica um pouco a frente
            if c["tipo"] == "onda" and f'Mao_{c.get("osso", "")[-1:]}' in armado and c.get("osso", "").startswith("Braco_"):
                c["amp"] *= 0.35
        if armado and r["nome"] != "Morte":
            for c in r["camadas"]:
                if c["tipo"] == "poses":
                    for ch in c["chaves"]:
                        for osso, pose in ch.get("pose", {}).items():
                            if osso.startswith("Braco_") and f"Mao_{osso[-1]}" in armado:
                                for canal in ("frente", "esquerda", "tombar_direita"):
                                    if canal in pose:
                                        pose[canal] *= 0.3
    return jeito(base, modelo)


def construir_heroi(reg, pal, linhagem, *, corpo=None, predef=1, conjunto=None, com_clipes=True):
    from ..nucleo.anim import assar_clipe
    m = montar_heroi(reg, pal, linhagem, corpo=corpo, predef=predef, conjunto=conjunto)
    H = {"P": 3.0, "M": 4.0, "G": 5.0}[m.meta["tamanho"]]
    m.meta["H"] = H
    if com_clipes:
        from ..nucleo import colisao
        for r in clipes_do_heroi(reg, m):
            m.clipes[r["nome"]] = assar_clipe(m, r, H=H)
            cam = next((c for c in r["camadas"] if c.get("tipo") == "golpe"), None)
            if cam is not None and colisao.itens(m):
                m.meta["golpe_ajustado"] = _ajustar_golpe(m, r, cam, H)

        m.meta["desvios"] = colisao.desviar_itens(m)      # mao sai da frente onde o item ainda tocaria o corpo
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
