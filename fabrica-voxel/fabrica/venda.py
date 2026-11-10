"""Pacote de venda: junta os arquivos de um ou mais assets aprovados com LEIA-ME, licenca-modelo e proveniencia."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from . import esteira, revisao
from .nucleo import exporta, render
from .nucleo.montagem import montar
from .nucleo.paleta import Paleta
from .registro import RAIZ

LEIAME = """{nome}
Gerado pela Fabrica de Voxel {versao}.

CONTEUDO (por modelo)
  modelo_studs.glb    1 unidade = 1 stud (Roblox Studio). Frente = -Z, cima = +Y.
  modelo_metros.glb   1 unidade = 1 metro (Unity, Godot, Unreal, Blender). 1 stud = 0,28 m.
  modelo.vox          MagicaVoxel, um objeto por peca rigida.
  vitrine.png         imagem de vitrine
  giro.gif            giro de 360 graus
  anim.gif            animacoes (quando houver)
  ficha_tecnica.json  voxels, triangulos, pecas, ossos, clipes

COMO IMPORTAR
  Roblox Studio: File > Import 3D, escolha modelo_studs.glb, unidade Studs. Cada peca vira um MeshPart com o
    nome da peca. As cores estao no vertice (sem textura). As animacoes do arquivo servem de referencia; no
    Roblox, use os modulos Luau da Fabrica ou anime por conta propria.
  Unity / Godot / Unreal / Blender: importe modelo_metros.glb. O material deve usar a cor de vertice.
  MagicaVoxel: abra modelo.vox.

O modelo usa pecas rigidas (sem pele que dobra): um osso por peca.
"""

LICENCA = """LICENCA DE USO (modelo; preencha os campos entre colchetes; nao substitui orientacao de advogado)

Produto: {nome}        Licenciante: [SEU NOME OU ESTUDIO]        Data: [DATA]

1. O QUE VOCE PODE FAZER
   - Usar os arquivos em quantos jogos, apps, videos e projetos quiser, comerciais ou nao.
   - Modificar os arquivos para os seus projetos.
2. O QUE VOCE NAO PODE FAZER
   - Revender, sublicenciar ou redistribuir os arquivos, modificados ou nao, como asset, pack, modelo
     avulso ou em bibliotecas de assets.
   - Usar os arquivos para treinar modelos de inteligencia artificial.
   - Cunhar NFT ou equivalente a partir dos arquivos.
   - Alegar autoria dos arquivos originais.
3. LICENCA ESTENDIDA [opcional]: permite uso em produtos em que o proprio asset e o conteudo vendido
   (ex.: itens de UGC). Contratada a parte.
4. EXCLUSIVIDADE [opcional]: o licenciante deixa de vender o produto a terceiros a partir de [DATA].
5. ORIGEM: os modelos foram gerados por codigo procedural proprio, a partir de fichas de dados, sob direcao
   de arte humana, com assistencia de IA de texto na escrita do codigo e das fichas. Nao foi usada IA de
   imagem, nem modelos, texturas ou digitalizacoes de terceiros. O arquivo PROVENIENCIA.json registra a
   ficha, a semente e o hash de cada arquivo.
6. SEM OUTRAS GARANTIAS: os arquivos sao fornecidos como estao.

--- ENGLISH SUMMARY ---
Royalty-free license. You may use and modify the files in unlimited commercial and non-commercial projects.
You may not resell or redistribute the files (modified or not) as assets, use them to train AI models, or
mint NFTs. Made with proprietary procedural code from data sheets under human art direction, with
text-AI assistance for code; no image-generation AI and no third-party models were used.
"""


def vender(ids: list[str], nome: str, reg, data: str = "", exigir_p3: bool = True) -> str:
    pal = Paleta.carregar()
    pasta = RAIZ / "saida" / "_venda" / nome
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir(parents=True)
    prov = {"pack": nome, "data": data, "fabrica": exporta.VERSAO_FABRICA, "modelos": []}
    recusados, sem_p3 = [], []
    for ref in ids:
        rel = esteira.construir(ref, registro=reg, data=data, imagens=False, exportar=False)
        if rel["status"] != "aprovado":
            recusados.append(ref)
            continue
        p3 = revisao.publicavel(rel["id"], rel.get("hash_ficha"))
        if not p3:
            sem_p3.append(ref)
            if exigir_p3:
                continue
        ficha = reg.resolver(ref)
        m = montar(ficha, pal)
        d = pasta / m.id
        d.mkdir()
        exporta.escrever_glb(m, d / "modelo_studs.glb")
        exporta.escrever_glb(m, d / "modelo_metros.glb", escala=0.28)
        exporta.escrever_vox(m, d / "modelo.vox")
        mn, mx = m.caixa()
        px = 520 / max(max(mx - mn), 0.5)
        render.render_modelo(m, vista="tres_quartos", px_por_stud=px, fundo=(40, 36, 48)).save(d / "vitrine.png")
        giro = [render.render_modelo(m, vista=(a, 20), px_por_stud=px * 0.5, tamanho=(360, 360), centro=(mn + mx) / 2).quantize(96)
                for a in range(0, 360, 24)]
        giro[0].save(d / "giro.gif", save_all=True, append_images=giro[1:], duration=90, loop=0)
        if m.clipes:
            render.gif_animacao(m, list(m.clipes.values()), d / "anim.gif", px_por_stud=px * 0.5)
        tri = exporta.contar_triangulos(m)
        (d / "ficha_tecnica.json").write_text(json.dumps({
            "id": m.id, "nome": m.nome, "voxels": m.n_voxels(), "triangulos": tri["total"], "pecas": len(m.pecas),
            "ossos": len(m.ossos), "clipes": {k: round(c.duracao, 2) for k, c in m.clipes.items()},
            "tamanho_studs": [round(float(v), 3) for v in (mx - mn)], "nota_p2": rel["p2"]["nota"],
            "revisao_visual": "publicavel" if p3 else "pendente"}, indent=1, ensure_ascii=False), encoding="utf-8")
        prov["modelos"].append({"id": m.id, "hash_ficha": rel.get("hash_ficha"), "semente": 0,
                                "arquivos": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(d.iterdir())}})
    prov["metodo"] = ("Gerado por codigo procedural a partir de fichas de dados, sob direcao de arte humana, com assistencia de IA de "
                      "texto na escrita do codigo e das fichas. Sem IA de imagem, sem modelos de terceiros.")
    prov["declaracao_ia_para_lojas"] = "Assistido por IA (codigo e dados escritos com IA de texto); arte gerada por algoritmo proprio."
    (pasta / "LEIA-ME.txt").write_text(LEIAME.format(nome=nome, versao=exporta.VERSAO_FABRICA), encoding="utf-8")
    (pasta / "LICENCA.txt").write_text(LICENCA.format(nome=nome), encoding="utf-8")
    (pasta / "PROVENIENCIA.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False), encoding="utf-8")
    zp = pasta.with_suffix(".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pasta.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(pasta.parent))
    msg = f"{zp}  ({len(prov['modelos'])} modelos, {zp.stat().st_size // 1024} KB)"
    if recusados:
        msg += f"\nFICARAM DE FORA (nao aprovados): {recusados}. Rode: python -m fabrica construir <id> para ver o conserto."
    if sem_p3:
        msg += (f"\n{'FICARAM DE FORA' if exigir_p3 else 'ENTRARAM SEM REVISAO VISUAL'} (sem P3 valido): {sem_p3}. "
                "Siga cartoes/revisao_visual.md e rode: python -m fabrica revisar <id> <respostas> --por <nome>")
    return msg
