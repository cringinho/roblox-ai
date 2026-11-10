"""Galeria: um exemplo por arquetipo, na mesma escala, com a regua do heroi medio (4 studs)."""
from __future__ import annotations

from PIL import Image, ImageDraw

from .nucleo import render
from .nucleo.montagem import montar
from .nucleo.paleta import Paleta
from .registro import RAIZ


def galeria_arquetipos(reg, px=22.0, colunas=5):
    pal = Paleta.carregar()
    cel, quadros = [], []
    for i in reg.listar("arquetipo"):
        f = reg.resolver(i)
        if "pecas" not in f:
            continue
        m = montar(f, pal)
        a = render.render_modelo(m, vista="tres_quartos", px_por_stud=px)
        b = render.render_modelo(m, vista="grade", px_por_stud=24)
        im = Image.new("RGB", (max(a.width + b.width + 6, 170), max(a.height, b.height) + 20), (30, 26, 36))
        im.paste(a, (0, im.height - 20 - a.height)); im.paste(b, (a.width + 6, im.height - 20 - b.height))
        ImageDraw.Draw(im).text((4, im.height - 15), f'{i.split(".")[1]}  ({len(m.ossos)} ossos)', fill=(236, 228, 243))
        cel.append(im)
        if "Andar" in m.clipes:
            quadros.append(render.quadros_animacao(m, m.clipes["Andar"], px_por_stud=px * 0.8, passo=3)[:10])
    lw, lh = max(c.width for c in cel) + 8, max(c.height for c in cel) + 8
    linhas = (len(cel) + colunas - 1) // colunas
    folha = Image.new("RGB", (lw * colunas + 8, lh * linhas + 30), (30, 26, 36))
    ImageDraw.Draw(folha).text((8, 8), f"{len(cel)} arquetipos: 3/4 e camera da grade (1x). Regua: 1 ladrilho = 4 studs = {int(4 * px)} px", fill=(236, 228, 243))
    for k, c in enumerate(cel):
        folha.paste(c, (8 + (k % colunas) * lw, 28 + (k // colunas) * lh + lh - 8 - c.height))
    pasta = RAIZ / "saida" / "_arquetipos"
    pasta.mkdir(parents=True, exist_ok=True)
    folha.save(pasta / "galeria.png")
    n = min(len(q) for q in quadros)
    qw, qh = max(q[0].width for q in quadros) + 4, max(q[0].height for q in quadros) + 4
    fr = []
    for i in range(n):
        f = Image.new("RGB", (qw * colunas, qh * ((len(quadros) + colunas - 1) // colunas)), render.FUNDO)
        for k, q in enumerate(quadros):
            f.paste(q[i], ((k % colunas) * qw, (k // colunas) * qh + qh - 4 - q[i].height))
        fr.append(f.quantize(128, dither=Image.Dither.NONE))
    fr[0].save(pasta / "galeria_andar.gif", save_all=True, append_images=fr[1:], duration=100, loop=0)
    return f"{pasta / 'galeria.png'}\n{pasta / 'galeria_andar.gif'}"
