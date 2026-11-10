"""CLI da Fabrica de Voxel.  Uso:  python -m fabrica <comando> ...   (rode a partir da pasta fabrica-voxel)"""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from . import esteira
from .registro import ErroRegistro, Registro, explicar


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m fabrica", description="Fabrica de Voxel: ficha -> asset voxel para o Roblox")
    sub = ap.add_subparsers(dest="cmd")
    for nome, ajuda in (("validar", "P0: confere a ficha"), ("construir", "esteira completa"), ("auditar", "P1 + P2 sem imagens")):
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("ids", nargs="+")
        s.add_argument("--semente", type=int, default=0)
        s.add_argument("--data", default="")
    s = sub.add_parser("lote", help="constroi varios: ids, 'tipo:monstro' ou arquivo .txt com um id por linha")
    s.add_argument("alvos", nargs="+")
    s.add_argument("--data", default="")
    s = sub.add_parser("listar", help="lista o registro")
    s.add_argument("tipo", nargs="?")
    s = sub.add_parser("explicar", help="campos de um tipo de ficha")
    s.add_argument("tipo")
    s = sub.add_parser("novo", help="cria uma ficha copiando outra")
    s.add_argument("tipo"); s.add_argument("id"); s.add_argument("--de", required=True)
    s = sub.add_parser("heroi", help="constroi um heroi de uma linhagem")
    s.add_argument("linhagem"); s.add_argument("--corpo", default="1"); s.add_argument("--predef", type=int, default=1)
    s.add_argument("--conjunto", default=None); s.add_argument("--mao", default=None)
    s = sub.add_parser("elenco", help="folha e GIF com as 14 linhagens")
    s.add_argument("--conjuntos", action="store_true")
    s = sub.add_parser("matriz", help="matriz de prova de um conjunto de equipamento em todos os corpos")
    s.add_argument("conjunto")
    s = sub.add_parser("arquetipos", help="galeria com um exemplo por arquetipo")
    s = sub.add_parser("pacote", help="gera saida/FabricaVoxel.rbxmx com o runtime e os dados aprovados")
    s = sub.add_parser("vender", help="monta o pacote de venda de um ou mais assets")
    s.add_argument("ids", nargs="+"); s.add_argument("--nome", required=True); s.add_argument("--data", default="")
    s.add_argument("--sem-p3", action="store_true", help="aceita modelos sem revisao visual (so para teste)")
    s = sub.add_parser("revisar", help="P3: registra a revisao visual (cartoes/revisao_visual.md)")
    s.add_argument("id"); s.add_argument("respostas", help="10 letras A1..A10: s, q, n ou -")
    s.add_argument("--por", required=True, help="quem revisou"); s.add_argument("--data", default="")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help()
        return 1
    try:
        reg = Registro()
        if a.cmd == "listar":
            for i in reg.listar(a.tipo):
                print(f'{i:<44} {reg.fichas[i].get("nome", "")}')
            return 0
        if a.cmd == "explicar":
            print(explicar(a.tipo))
            return 0
        if a.cmd == "validar":
            ruim = 0
            for i in a.ids:
                e = reg.validar(i)
                print(f"{i}: " + ("P0 passou" if not e else "P0 REPROVOU\n" + "\n".join(f"  - {x}" for x in e)))
                ruim += bool(e)
            return 1 if ruim else 0
        if a.cmd in ("construir", "auditar"):
            ruim = 0
            for i in a.ids:
                rel = esteira.construir(i, registro=reg, semente=a.semente, data=a.data, imagens=a.cmd == "construir",
                                        exportar=a.cmd == "construir")
                print(esteira.resumo(rel))
                ruim += rel["status"] != "aprovado"
            return 1 if ruim else 0
        if a.cmd == "lote":
            ids = []
            for alvo in a.alvos:
                if alvo.startswith("tipo:"):
                    ids += reg.listar(alvo[5:])
                elif alvo.endswith(".txt"):
                    ids += [l.strip() for l in open(alvo, encoding="utf-8") if l.strip() and not l.startswith("#")]
                else:
                    ids.append(alvo)
            print(f'{"id":<40} {"status":<10} {"P2":>5} {"voxels":>7} {"tri":>6} {"s":>5}  pior metrica')
            ruim = 0
            for i in ids:
                rel = esteira.construir(i, registro=reg, data=a.data)
                n, p2 = rel.get("numeros", {}), rel.get("p2", {})
                pior = (p2.get("piores") or [{}])[0].get("metrica", "") if rel["p0"]["passou"] else rel["p0"]["erros"][0][:60]
                print(f'{rel.get("id", i):<40} {rel["status"]:<10} {p2.get("nota", "-"):>5} {n.get("voxels", "-"):>7} '
                      f'{str(n.get("triangulos", "-")):>6} {n.get("segundos", "-"):>5}  {pior}')
                ruim += rel["status"] != "aprovado"
            print(f"{len(ids) - ruim} aprovados, {ruim} reprovados")
            return 1 if ruim else 0
        if a.cmd == "novo":
            origem = reg.achar(a.de)
            pasta = reg.arquivo[origem].parent
            destino = pasta / f"{a.id}.json"
            if destino.exists():
                print(f"ja existe {destino}; escolha outro id")
                return 1
            d = json.loads(reg.arquivo[origem].read_text(encoding="utf-8"))
            d["id"], d["nome"] = f"{a.tipo}.{a.id}", a.id.replace("_", " ").title()
            destino.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"criei {destino} a partir de {origem}. Edite e rode: python -m fabrica construir {a.id}")
            return 0
        if a.cmd in ("heroi", "elenco", "matriz"):
            from .heroi import cli as hcli
            return hcli.rodar(a, reg)
        if a.cmd == "arquetipos":
            from .galeria import galeria_arquetipos
            print(galeria_arquetipos(reg))
            return 0
        if a.cmd == "pacote":
            from .pacote_roblox import empacotar
            print(empacotar())
            return 0
        if a.cmd == "vender":
            from .venda import vender
            print(vender(a.ids, a.nome, reg, data=a.data, exigir_p3=not a.sem_p3))
            return 0
        if a.cmd == "revisar":
            from .revisao import registrar
            print(registrar(a.id, a.respostas, a.por, reg, data=a.data))
            return 0
    except ErroRegistro as e:
        print(f"ERRO: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
