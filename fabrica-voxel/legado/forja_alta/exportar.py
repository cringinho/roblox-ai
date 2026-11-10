"""Exporta cada modelo em pose de repouso: GLB (uma malha por peca, no pivo), rig em JSON, paleta PNG."""
import sys, os, json, shutil, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import malha_da_peca, salvar_glb, paleta_png, hex_rgb
DEST = sys.argv[1]; os.makedirs(DEST, exist_ok=True)

def hexs(RGB):
    return ["%02X%02X%02X" % tuple(int(round(float(v) * 255)) for v in c) for c in RGB]

def exportar(slug, nome, pecas, RGB, emis):
    HEX = hexs(RGB); png = paleta_png(HEX)
    nos = []; rig = dict(modelo=nome, unidade="stud", frente="-Z", cima="+Y", pecas=[])
    for n, p in pecas.items():
        cores = np.unique(p.g[p.g > 0]).tolist()
        base = malha_da_peca(p, [c for c in cores if c not in emis]); brilho = malha_da_peca(p, [c for c in cores if c in emis])
        pivo = np.asarray(p.pivo, float)
        if base is not None: nos.append(dict(nome=n, malha=base, translacao=pivo, material=0))
        if brilho is not None: nos.append(dict(nome=n + "_Brilho", malha=brilho, translacao=pivo, material=1))
        rig["pecas"].append(dict(nome=n, pai=getattr(p, "pai", None), pivo=[round(float(x), 4) for x in pivo], voxel_stud=float(p.vs), voxels=int((p.g > 0).sum())))
    tam = salvar_glb(os.path.join(DEST, f"{slug}.glb"), nos, png, slug)
    json.dump(rig, open(os.path.join(DEST, f"{slug}_rig.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(DEST, f"{slug}_paleta.png"), "wb").write(png)
    print(slug, len(pecas), "pecas", round(tam / 1024), "KB")

# ---- bestiario
import bestiario as B
for mk in (B.esporinho, B.cirio, B.gargulho, B.ossario):
    m = mk(); exportar(m["nome"].lower().replace("á", "a").replace("í", "i").replace("é", "e"), m["nome"], m["pecas"], B.RGB, B.EMIS)
# ---- variantes do ossario
import ossarios as O
for f in O.FICHAS:
    m = O.variante(f); exportar(m["nome"].lower().replace(" ", "_").replace("á", "a").replace("é", "e"), m["nome"], m["pecas"], O.RGB, O.EMIS)
# ---- relicario
import relicario as R
m = R.relicario()
for p in m["pecas"].values():
    R.ligar_soltos(p, R.K["tendao"]); p.limpar_soltos()
exportar("relicario", "Relicário", m["pecas"], R.RGB, R.EMIS)
# ---- slimes
import slimes as S
for i in range(len(S.FICHAS)):
    m = S.slime(i)
    for p in m["pecas"].values(): p.limpar_soltos()
    exportar("slime_" + m["nome"].lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("ó", "o"), "Slime " + m["nome"], m["pecas"], S.RGB, S.EMIS)
# ---- hidras
import hidra as Hd, hidra_adulta as HA
m = Hd.hidra()
for p in m["pecas"].values(): p.limpar_soltos()
exportar("hidra_nihilis", "Nihilis, a Hidra do Vazio", m["pecas"], Hd.RGB, Hd.EMIS)
m = HA.hidra()
for p in m["pecas"].values(): p.limpar_soltos()
exportar("hidra_adulta", "Hidra do Vazio adulta", m["pecas"], HA.RGB, HA.EMIS)
# ---- fada (mascote)
import herois as H, fada_anim as FA
criadas = []; orig = H.peca
def gravar(G, g, nome="x"):
    p = orig(G, g, nome); criadas.append(p); return p
H.peca = gravar
pc, ch = FA.rig_fada("mascote"); H.peca = orig
objs = {p.nome: p for p in criadas}
for n, d in pc.items():
    p = objs[n]; p.pivo = np.asarray(d["pivo"], float); p.pai = None if n == "Tronco" else "Tronco"
exportar("fada_mascote", "Fada com o Conjunto da Mascote", {n: objs[n] for n in pc}, H.RGB, set())
