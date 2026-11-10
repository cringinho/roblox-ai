"""Importa um modelo de blocos da Forja antiga (script Luau com as tabelas PALETA, OSSOS, PECAS, ROTACOES, VFX) e
escreve uma ficha da fabrica. E assim que os chefes desenhados a mao (Rei Necromante) entram na esteira nova.

- Cada bloco da Forja (voxel de 0,25 stud) vira 2 x 2 x 2 voxels da fabrica (0,125): o elenco inteiro fica num so
  tamanho de voxel e o desenho original nao muda.
- Cada osso vira uma peca; os blocos sao formas "bloco" em coordenada absoluta (ficha importada nao usa ancora).
- Espelho (_D -> _E) e escrito por extenso. Peca girada (o cajado) e endireitada e o giro vai para o "repouso" do osso.
- Cores: cada entrada da paleta vira um material com rampa gerada a partir da cor original.

Uso: python -m fabrica importar <arquivo.luau> --id rei_necromante_f1 --tier 7
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from .nucleo.contrato import matriz_para_quat
from .registro import RAIZ

FATOR = 2            # 1 voxel da Forja (0,25 stud) = 2 voxels da fabrica (0,125)
PERFIL = {"Neon": "brilho", "Metal": "metal", "Wood": "madeira", "Fabric": "tecido"}


def _tabela(texto: str, nome: str) -> list[list]:
    m = re.search(r"local " + nome + r"[^=\n]*=\s*\{(.*?)\n\}", texto, re.S)
    if not m:
        return []
    out = []
    for ln in m.group(1).splitlines():
        ln = ln.split("--")[0].strip().rstrip(",")
        if not ln.startswith("{"):
            continue
        campos = [c.strip() for c in ln.strip("{}").split(",")]
        out.append([c.strip('"') if c.startswith('"') else (float(c) if c not in ("nil", "") else None) for c in campos])
    return out


def _paleta(texto: str) -> dict:
    m = re.search(r"local PALETA[^=\n]*=\s*\{(.*?)\n\}", texto, re.S)
    return {k: (h, mat) for k, h, mat in re.findall(r'(\w+)\s*=\s*\{"([0-9A-Fa-f]{6})",\s*"(\w+)"\}', m.group(1))} if m else {}


def _esq(nome: str) -> str:
    return nome[:-2] + "_E" if nome.endswith("_D") else nome.replace("_D_", "_E_")


def _papel(nome: str) -> str:
    n = nome.lower()
    for chave, papel in (("mandibula", "mandibula"), ("cabeca", "cabeca"), ("coroa", "adorno"), ("coxa", "perna"), ("canela", "pe"),
                         ("pe_", "pe"), ("bracosup", "braco"), ("braco", "braco"), ("antebraco", "mao"), ("punho", "mao"), ("mao", "mao"),
                         ("dedos", "mao"), ("manto", "pano"), ("tabardo", "pano"), ("tanga", "pano"), ("nuvem", "pano"),
                         ("pescoco", "pescoco"), ("cajado", "item_fixo")):
        if chave in n:
            return papel
    return "corpo"


def parado_generico(ossos: list[dict]) -> list[dict]:
    """Modelo importado sem animacao ganha um Parado: respira, olha em volta, bate a mandibula, o pano balanca."""
    cam, k = [], 0
    raiz = next((o["nome"] for o in ossos if o["pai"] == "Raiz"), None)
    if raiz:
        cam.append({"tipo": "onda", "osso": raiz, "canal": "cima", "amp": 0.004, "harm": 2, "forma": "pulso"})
    for o in ossos:
        n, papel = o["nome"], o["papel"]
        if o.get("seguir_pai") or n == raiz:
            continue
        k += 1
        fase = round((k * 0.137) % 1.0, 3)
        if papel == "cabeca":
            cam += [{"tipo": "onda", "osso": n, "canal": "esquerda", "amp": 5, "harm": 1, "fase": fase, "harm2": 0.4},
                    {"tipo": "onda", "osso": n, "canal": "frente", "amp": 1.5, "harm": 2, "fase": fase}]
        elif papel == "mandibula":
            cam.append({"tipo": "onda", "osso": n, "canal": "frente", "amp": 3, "harm": 3, "fase": fase, "forma": "pulso"})
        elif papel == "braco":
            cam.append({"tipo": "onda", "osso": n, "canal": "frente", "amp": 2.5, "harm": 2, "fase": fase})
        elif papel == "pano":
            cam += [{"tipo": "onda", "osso": n, "canal": "frente", "amp": 3, "harm": 2, "fase": fase},
                    {"tipo": "onda", "osso": n, "canal": "tombar_direita", "amp": 1.5, "harm": 1, "fase": fase}]
        elif papel == "corpo":
            cam.append({"tipo": "onda", "osso": n, "canal": "tombar_direita", "amp": 0.8, "harm": 1, "fase": fase})
    return [{"nome": "Parado", "duracao": 6.0, "laco": True, "camadas": cam}]


def converter(texto: str, ident: str, nome: str, tier: int, clipes: list | None = None, flutua: bool = False) -> dict:
    pal = _paleta(texto)
    ossos_t, pecas_t, rots, vfx = _tabela(texto, "OSSOS"), _tabela(texto, "PECAS"), _tabela(texto, "ROTACOES"), _tabela(texto, "VFX")
    if not pecas_t or not ossos_t:
        raise ValueError("nao achei as tabelas OSSOS e PECAS no arquivo")
    ossos, piv = [], {}
    declarados = {o[0] for o in ossos_t}
    for o in ossos_t:
        nm, pai, x, y, z = o[0], o[1], o[2], o[3], o[4]
        esp = len(o) > 5 and o[5] == 1
        for lado in ((1, -1) if esp else (1,)):
            n = nm if lado > 0 else _esq(nm)
            p = pai if lado > 0 else (_esq(pai) if _esq(pai) != pai and (pai in declarados) else pai)
            if p == "HumanoidRootPart":
                p = "Raiz"
            piv[n] = np.array([x * lado, y, z], float)
            ossos.append({"nome": n, "pai": p, "pivo": {"abs": [x * lado * FATOR, y * FATOR, z * FATOR]}, "papel": _papel(n)})
    por_osso: dict[str, list] = {o["nome"]: [] for o in ossos}
    giro: dict[str, np.ndarray] = {}
    n_blocos = 0
    for pc in pecas_t:
        _, osso, x, y, z, w, h, d, cor = pc[:9]
        esp = len(pc) > 9 and pc[9] == 1
        rot = int(pc[10]) if len(pc) > 10 and pc[10] else 0
        for lado in ((1, -1) if esp else (1,)):
            o = osso if lado > 0 else _esq(osso)
            c = np.array([x * lado, y, z], float)
            if rot:                                       # desfaz o giro em torno do pivo do osso; o giro vai para o repouso
                R = np.array(rots[rot - 1], float).reshape(3, 3)
                if lado < 0:
                    R = np.diag([-1, 1, 1]) @ R @ np.diag([-1, 1, 1])
                giro[o] = R
                c = piv[o] + R.T @ (c - piv[o])
                c = np.round(c * 2) / 2
            por_osso.setdefault(o, []).append({"op": "bloco", "centro": [float(v * FATOR) for v in c],
                                               "tam": [int(w * FATOR), int(h * FATOR), int(d * FATOR)], "material": cor})
            n_blocos += 1
    for o in ossos:
        if o["nome"] in giro:
            o["repouso_quat"] = [round(float(v), 6) for v in matriz_para_quat(giro[o["nome"]])]
    # articulacao: perna em cadeia (IK no andar) quando o joelho esta reto abaixo do quadril; o resto acompanha o pai
    por_nome = {o["nome"]: o for o in ossos}
    for o in ossos:
        n, pai = o["nome"], por_nome.get(o["pai"])
        baixo = n.lower()
        if "coxa" in baixo:
            filho = next((x for x in ossos if x["pai"] == n and "canela" in x["nome"].lower()), None)
            if filho and abs(piv[n][0] - piv[filho["nome"]][0]) < 1e-6 and abs(piv[n][2] - piv[filho["nome"]][2]) < 1e-6:
                o["cadeia_com"], o["dobra"] = filho["nome"], "joelho"
        elif "antebraco" in baixo:
            o["seguir_pai"] = {"modo": "cotovelo", "ganho": 0.5, "atraso_s": 0.09}
        elif any(k in baixo for k in ("mao", "dedos", "punho")):
            o["seguir_pai"] = {"modo": "livre", "ganho": 0.5, "atraso_s": 0.08}
        elif any(k in baixo for k in ("manto", "nuvem", "tabardo", "tanga")) and pai is not None and pai["papel"] == "pano":
            o["seguir_pai"] = {"modo": "livre", "ganho": 0.9, "atraso_s": 0.14}
        elif "coroa" in baixo:
            o["seguir_pai"] = {"modo": "livre", "ganho": 0.15, "atraso_s": 0.1}
    mats = [{"nome": k, "rampa": "#" + h.upper(), "perfil": ("osso" if k.startswith("osso") else PERFIL.get(m, "chapado")),
             "brilho": m == "Neon"} for k, (h, m) in pal.items()]
    usados = {f["material"] for fs in por_osso.values() for f in fs}
    alt = max((f["centro"][1] + f["tam"][1] / 2) for fs in por_osso.values() for f in fs)
    lado_max = max(max(abs(f["centro"][e]) + f["tam"][e] / 2 for fs in por_osso.values() for f in fs) for e in (0, 2))
    campo = int(max(160, np.ceil((alt + 40) / 32) * 32, np.ceil((2 * lado_max + 40) / 32) * 32))
    soq = []
    for v in vfx:
        for lado in ((1, -1) if len(v) > 5 and v[5] == 1 else (1,)):
            soq.append({"nome": v[0] if lado > 0 else _esq(v[0]), "osso": v[1] if lado > 0 else _esq(v[1]),
                        "abs": [v[2] * lado * FATOR, v[3] * FATOR, v[4] * FATOR]})
    return {"id": f"monstro.{ident}", "tipo": "monstro", "versao": 1, "nome": nome, "tier": tier, "tier_manual": True,
            "origem": f"Importado da Forja de blocos do dono: {n_blocos} blocos, {len(ossos)} ossos. Nao edite a mao; reimporte.",
            "campo": campo, "materiais": [m for m in mats if m["nome"] in usados],
            "pecas": [{"nome": o["nome"], "formas": por_osso[o["nome"]]} for o in ossos if por_osso.get(o["nome"])],
            "ossos": [o for o in ossos if por_osso.get(o["nome"]) or any(x["pai"] == o["nome"] for x in ossos)],
            "soquetes": [s for s in soq if por_osso.get(s["osso"])], "clipes": clipes or parado_generico(ossos),
            "tempo_por_porte": False, "meta": {"blocos_de_origem": n_blocos, **({"flutua": True} if flutua else {})}}


def importar(arquivo: str, ident: str, nome: str | None = None, tier: int = 7, clipes: list | str | None = None,
             flutua: bool = False) -> str:
    texto = Path(arquivo).read_text(encoding="utf-8")
    if isinstance(clipes, str):                               # id de uma ficha de clipe, ex.: "clipe.rei_necromante_f1"
        arq = RAIZ / "registro" / "clipes" / (clipes.split(".", 1)[-1] + ".json")
        clipes = json.loads(arq.read_text(encoding="utf-8"))["clipes"]
    f = converter(texto, ident, nome or ident.replace("_", " ").title(), tier, clipes, flutua)
    # pedacos que ja eram soltos no desenho original (barras de gaiola, por exemplo) ficam registrados: o portao
    # voxels_soltos so reprova o que passar disso
    from .nucleo import auditoria
    from .nucleo.montagem import montar
    from .nucleo.paleta import Paleta
    m = montar({**f, "clipes": []}, Paleta.carregar(), com_clipes=False)
    r = next(x for x in auditoria.p1(m, "prop") if x["regra"] == "voxels_soltos")
    if isinstance(r["valor"], dict) and r["valor"]:
        f["meta"]["soltos_de_origem"] = r["valor"]
    destino = RAIZ / "registro" / "monstros" / f"{ident}.json"
    destino.write_text(json.dumps(f, indent=None, ensure_ascii=False, separators=(",", ":")).replace('},{"op"', '},\n{"op"')
                       .replace('"pecas":[', '"pecas":[\n').replace('"ossos":[', '\n"ossos":[\n').replace('{"nome"', '\n{"nome"'), encoding="utf-8")
    return f"{destino}  ({f['meta']['blocos_de_origem']} blocos, {len(f['ossos'])} ossos, {len(f['materiais'])} materiais)"
