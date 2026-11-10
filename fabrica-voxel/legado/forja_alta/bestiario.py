"""Bestiario: 4 monstros comuns em voxel, com rig rigido, 3 clipes procedurais e P1 por quadro."""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import construir, faces, render, camera_orto, rot_eixo, hex_rgb, malha_gulosa, ruido

VS = 0.125
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida_bestiario")
os.makedirs(OUT, exist_ok=True)
PAL = [("fungo", "D8C4A8"), ("fungo_s", "A8917A"), ("chapeu", "8E2222"), ("chapeu_e", "631818"), ("lamela", "C99A8C"), ("pinta", "E8DCC8"),
       ("raiz", "5A4034"), ("raiz_s", "3E2C24"), ("brilho_laranja", "FF9A3C"), ("cera", "D9CDB0"), ("cera_s", "A89A7C"), ("cera_e", "7A6E58"),
       ("pavio", "2A2420"), ("chama", "FFD36B"), ("chama_n", "FF7A2E"), ("osso_unha", "E6DDC8"), ("buraco", "141016"),
       ("pedra", "6E6A72"), ("pedra_s", "4C4952"), ("pedra_c", "908B94"), ("membrana", "4A3B4E"), ("membrana_s", "33283A"), ("olho_verm", "FF3B3B"),
       ("osso", "D6CCB4"), ("osso_s", "A89E86"), ("osso_e", "7C735F"), ("alma", "7CFFB0"), ("base", "3A3836"), ("musgo", "4E6338")]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
HEX = ["000000"] + [h for _, h in PAL]
RGB = np.array([hex_rgb(h) for h in HEX])
EMIS = {K["brilho_laranja"], K["chama"], K["chama_n"], K["olho_verm"], K["alma"]}
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])

def faixa(cy, ry, cores):
    return lambda P: np.where((P[:, 1] - cy) / ry < -0.3, cores[0], np.where((P[:, 1] - cy) / ry > 0.4, cores[2], cores[1]))

# ---------------- os 4 monstros ----------------
def esporinho():
    pin = [(0.5, 2.0, 0.3), (-0.55, 2.0, -0.2), (0.1, 2.05, -0.65), (-0.2, 2.02, 0.6), (0.75, 1.92, -0.45)]
    def chapeu(P):
        c = np.where(P[:, 1] > 1.78, K["chapeu"], np.where(P[:, 1] > 1.66, K["chapeu_e"], K["lamela"]))
        for p in pin:
            c = np.where(np.linalg.norm(P - np.array(p), axis=1) < 0.14, K["pinta"], c)
        return c
    def saco(P):
        return np.where(ruido(P, 5.0, seed=2) > 0.68, K["brilho_laranja"], K["fungo_s"])
    corpo = construir("Corpo", None, VS, (0, 1.0, 0), [
        ('U', ('ell', (0, 1.15, 0), (0.5, 0.48, 0.44)), faixa(1.15, 0.48, (K["fungo_s"], K["fungo"], K["fungo"]))),
        ('U', ('ell', (0, 1.25, 0.48), (0.32, 0.3, 0.22)), saco)])
    chap = construir("Chapeu", "Corpo", VS, (0, 1.55, 0), [
        ('U', ('ell', (0, 1.78, 0), (1.15, 0.34, 1.15)), chapeu),
        ('U', ('ell', (0, 1.58, 0), (0.95, 0.12, 0.95)), K["lamela"])])
    pecas = {"Corpo": corpo, "Chapeu": chap}
    for s in (-1, 1):
        pecas[f"Olho_{'E' if s < 0 else 'D'}"] = None
    del pecas["Olho_E"], pecas["Olho_D"]
    for p in (corpo,):
        for s in (-1, 1):
            m = np.linalg.norm(p.P - np.array([s * 0.2, 1.22, -0.42]), axis=1) < 0.11
            p.unir(m, K["brilho_laranja"])
    for nome, sx, sz in (("Pata_FE", -1, -1), ("Pata_FD", 1, -1), ("Pata_TE", -1, 1), ("Pata_TD", 1, 1)):
        q = np.array([sx * 0.3, 0.88, sz * 0.28]); pe = np.array([sx * 0.62, 0.06, sz * 0.58])
        pecas[nome] = construir(nome, "Corpo", VS, q, [('U', ('cap', q, pe, 0.13, 0.09), faixa(0.5, 0.5, (K["raiz_s"], K["raiz"], K["raiz"])))])
    return dict(nome="Esporinho", arq="quadrupede de raizes", pecas=pecas)

def cirio():
    def cera(P):
        escorre = (np.floor(P[:, 0] / VS) % 3 == 0) & (ruido(P * np.array([4, 0.6, 4]), 1.0, seed=4) > 0.55)
        return np.where(escorre, K["cera_s"], np.where(P[:, 1] < 1.25, K["cera_s"], K["cera"]))
    tronco = construir("Tronco", None, VS, (0, 1.55, 0.1), [
        ('U', ('ell', (0, 1.6, 0.12), (0.56, 0.66, 0.46)), cera),
        ('U', ('ell', (0, 1.98, 0.32), (0.42, 0.3, 0.3)), cera)])
    def rosto(P):
        c = cera(P)
        for s in (-1, 1):
            c = np.where(np.linalg.norm((P - np.array([s * 0.15, 2.36, -0.68]))[:, :2], axis=1) < 0.1, K["buraco"], c)
            c = np.where(np.linalg.norm(P - np.array([s * 0.15, 2.36, -0.66]), axis=1) < 0.045, K["chama_n"], c)
        c = np.where((np.abs(P[:, 0]) < 0.16) & (np.abs(P[:, 1] - 2.08) < 0.05) & (P[:, 2] < -0.55), K["buraco"], c)
        return c
    cab = construir("Cabeca", "Tronco", VS, (0, 2.05, -0.2), [
        ('U', ('ell', (0, 2.33, -0.35), (0.4, 0.42, 0.36)), rosto),
        ('U', ('cap', (0, 2.7, -0.3), (0, 3.2, -0.28), 0.12), K["cera"]),
        ('U', ('cap', (0, 3.2, -0.28), (0, 3.3, -0.28), 0.03), K["pavio"])])
    chama = construir("Chama", "Cabeca", VS, (0, 3.28, -0.28), [
        ('U', ('cone', (0, 3.25, -0.28), (0, 3.62, -0.28), 0.13), lambda P: np.where(P[:, 1] > 3.42, K["chama"], K["chama_n"]))])
    pecas = {"Tronco": tronco, "Cabeca": cab, "Chama": chama}
    for s, L in ((-1, "E"), (1, "D")):
        om, mao = np.array([s * 0.55, 1.98, -0.02]), np.array([s * 0.78, 0.78, -0.45])
        ops = [('U', ('cap', om, mao, 0.14, 0.11), faixa(1.4, 0.6, (K["cera_s"], K["cera"], K["cera"])))]
        for k in (-1, 0, 1):
            ops.append(('U', ('cone', mao + (k * 0.07, -0.02, 0), mao + (k * 0.1 + s * 0.03, -0.32, -0.08), 0.045), K["osso_unha"]))
        pecas[f"Braco_{L}"] = construir(f"Braco_{L}", "Tronco", VS, om, ops)
        q, pe = np.array([s * 0.26, 1.05, 0.12]), np.array([s * 0.32, 0.1, 0.05])
        pecas[f"Perna_{L}"] = construir(f"Perna_{L}", "Tronco", VS, q, [('U', ('cap', q, pe, 0.17, 0.14), K["cera_s"]),
                                                                          ('U', ('ell', pe + (0, -0.02, -0.08), (0.17, 0.09, 0.24)), K["cera_e"])])
    return dict(nome="Círio", arq="bipede curvado", pecas=pecas)

def gargulho():
    def rosto(P):
        c = faixa(2.9, 0.32, (K["pedra_s"], K["pedra"], K["pedra_c"]))(P)
        for s in (-1, 1):
            c = np.where(np.linalg.norm(P - np.array([s * 0.17, 3.1, -0.57]), axis=1) < 0.09, K["olho_verm"], c)
        return c
    corpo = construir("Corpo", None, VS, (0, 2.35, 0), [
        ('U', ('ell', (0, 2.3, 0.05), (0.55, 0.66, 0.48)), faixa(2.3, 0.5, (K["pedra_s"], K["pedra"], K["pedra_c"]))),
        ('U', ('ell', (0, 3.05, -0.18), (0.46, 0.4, 0.42)), rosto),
        ('U', ('cone', (-0.22, 3.12, -0.1), (-0.38, 3.55, 0.0), 0.11), K["pedra_s"]),
        ('U', ('cone', (0.22, 3.12, -0.1), (0.38, 3.55, 0.0), 0.11), K["pedra_s"]),
        ('U', ('cone', (-0.08, 2.72, -0.42), (-0.07, 2.52, -0.42), 0.05), K["osso_unha"]),
        ('U', ('cone', (0.08, 2.72, -0.42), (0.07, 2.52, -0.42), 0.05), K["osso_unha"]),
        ('U', ('cap', (-0.18, 1.85, 0.0), (-0.22, 1.5, -0.08), 0.08), K["pedra_s"]),
        ('U', ('cap', (0.18, 1.85, 0.0), (0.22, 1.5, -0.08), 0.08), K["pedra_s"])])
    pecas = {"Corpo": corpo}
    for s, L in ((-1, "E"), (1, "D")):
        om = np.array([s * 0.48, 2.6, 0.08])
        def memb(P, s=s):
            borda = np.zeros(len(P), bool)
            for k in range(4):
                borda |= np.linalg.norm((P - np.array([s * (0.55 + 0.42 * k), 1.92, 0.1]))[:, :2], axis=1) < 0.26
            return borda
        ops = [('U', ('ell', (s * 1.45, 2.45, 0.12), (1.2, 0.72, 0.1)), lambda P: np.where(P[:, 1] > 2.6, K["membrana"], K["membrana_s"])),
               ('C', memb, None)]
        for ang in (0.25, -0.1, -0.45, -0.8):
            ponta = om + np.array([s * 1.9 * math.cos(ang), 1.2 * math.sin(ang) + 0.1, 0.05])
            ops.append(('U', ('cap', om, ponta * np.array([1.15, 1, 1]) + np.array([0, 0.1, 0]), 0.1, 0.08), K["pedra_s"]))
        pecas[f"Asa_{L}"] = construir(f"Asa_{L}", "Corpo", VS, om, ops)
    pecas["Cauda"] = construir("Cauda", "Corpo", VS, (0, 2.0, 0.35), [
        ('U', ('cap', (0, 2.0, 0.35), (0, 1.45, 0.95), 0.08, 0.06), K["pedra_s"]),
        ('U', ('cone', (0, 1.5, 0.9), (0, 1.3, 1.2), 0.16), K["pedra"])])
    return dict(nome="Gargulho", arq="voador", pecas=pecas)

def ossario():
    def cranio(P):
        c = faixa(0.55, 0.36, (K["osso_s"], K["osso"], K["osso"]))(P)
        for s in (-1, 1):
            c = np.where(np.linalg.norm((P - np.array([s * 0.17, 0.62, -2.6]))[:, [0, 1]], axis=1) < 0.11, K["buraco"], c)
            c = np.where(np.linalg.norm(P - np.array([s * 0.17, 0.62, -2.6]), axis=1) < 0.07, K["alma"], c)
        return c
    pecas = {"Cranio": construir("Cranio", None, VS, (0, 0.5, -2.1), [('U', ('ell', (0, 0.62, -2.25), (0.5, 0.42, 0.52)), cranio)]),
             "Mandibula": construir("Mandibula", "Cranio", VS, (0, 0.4, -2.0), [('U', ('ell', (0, 0.3, -2.3), (0.34, 0.12, 0.36)), K["osso_s"]),
                                                                               ('U', ('cone', (-0.2, 0.36, -2.6), (-0.18, 0.55, -2.62), 0.05), K["osso_unha"]),
                                                                               ('U', ('cone', (0.2, 0.36, -2.6), (0.18, 0.55, -2.62), 0.05), K["osso_unha"])])}
    pai = "Cranio"
    for k in range(8):
        z = -1.7 + 0.5 * k; r = 0.38 - 0.02 * k
        ops = [('U', ('ell', (0, 0.45, z), (r, r * 0.85, 0.27)), faixa(0.45, r, (K["osso_e"], K["osso_s"], K["osso"]))),
               ('U', ('cone', (0, 0.6, z), (0, 0.85, z + 0.08), 0.07), K["osso"])]
        for s in (-1, 1):
            ops.append(('U', ('cap', (s * r * 0.7, 0.45, z), (s * (r + 0.5), 0.06, z - 0.12), 0.11, 0.09), K["osso_s"]))
        nome = f"Vertebra_{k + 1}"
        pecas[nome] = construir(nome, pai, VS, (0, 0.45, z - 0.25), ops)
        pai = nome
    return dict(nome="Ossário", arq="corrente", pecas=pecas)

# ---------------- poses ----------------
def T_local(R, p):
    return (R, p - R @ p)

def comp(A, B):
    return (A[0] @ B[0], A[0] @ B[1] + A[1])

def montar(mon, raiz_T, locais):
    T = {}
    for n, p in mon["pecas"].items():
        if p.pai is None:
            T[n] = raiz_T
    pend = [n for n in mon["pecas"] if n not in T]
    while pend:
        for n in list(pend):
            p = mon["pecas"][n]
            if p.pai in T:
                R = locais.get(n, np.eye(3))
                T[n] = comp(T[p.pai], T_local(R, p.pivo))
                pend.remove(n)
    return T

def raiz(mon, R, desl):
    p = next(p for p in mon["pecas"].values() if p.pai is None)
    return (R, p.pivo + desl - R @ p.pivo)

def S(sx, sy, sz):
    return np.diag([sx, sy, sz])

def pose(mon, clipe, t):
    n = mon["nome"]; L = {}
    w = 2 * math.pi
    if n == "Esporinho":
        if clipe == "parado":
            Rr, d = rot_eixo(Z, 0.04 * math.sin(w * t / 1.6)), np.array([0, 0.03 * math.sin(w * t / 0.8), 0])
            L["Chapeu"] = rot_eixo(X, 0.05 * math.sin(w * t / 1.6 + 1))
        elif clipe == "mover":
            ph = w * t / 0.5
            Rr, d = rot_eixo(Z, 0.06 * math.sin(ph)), np.array([0, 0.06 * abs(math.sin(ph)), -2.0 * t])
            for nome, fase in (("Pata_FE", 0), ("Pata_TD", 0), ("Pata_FD", math.pi), ("Pata_TE", math.pi)):
                L[nome] = rot_eixo(X, 0.45 * math.sin(ph + fase))
            L["Chapeu"] = rot_eixo(X, 0.08 * math.sin(ph + 0.8))
        else:
            f = (t % 1.2) / 1.2
            a = -0.35 * math.sin(math.pi * min(f / 0.35, 1)) if f < 0.35 else 0.5 * math.sin(math.pi * min((f - 0.35) / 0.25, 1))
            Rr, d = rot_eixo(X, a), np.array([0, 0, -0.5 * max(0, a)])
            esm = 1 + 0.25 * math.sin(math.pi * min(max(f - 0.35, 0) / 0.25, 1))
            L["Chapeu"] = S(esm, 1 / esm, esm)
    elif n == "Círio":
        if clipe == "parado":
            Rr, d = rot_eixo(Z, 0.03 * math.sin(w * t / 2)), np.zeros(3)
            for s, nome in ((-1, "Braco_E"), (1, "Braco_D")):
                L[nome] = rot_eixo(X, 0.08 * math.sin(w * t / 2 + s))
            L["Chama"] = S(1 + 0.12 * math.sin(w * t * 3), 1 + 0.2 * math.sin(w * t * 5), 1)
        elif clipe == "mover":
            ph = w * t / 1.0
            Rr, d = rot_eixo(Z, 0.08 * math.sin(ph)) @ rot_eixo(X, -0.12), np.array([0, 0.05 * abs(math.sin(ph)), -1.3 * t])
            L["Perna_E"], L["Perna_D"] = rot_eixo(X, 0.4 * math.sin(ph)), rot_eixo(X, -0.4 * math.sin(ph))
            L["Braco_E"], L["Braco_D"] = rot_eixo(X, -0.3 * math.sin(ph - 0.6)), rot_eixo(X, 0.3 * math.sin(ph - 0.6))
            L["Cabeca"] = rot_eixo(Z, 0.1 * math.sin(ph + 1))
            L["Chama"] = S(1, 1 + 0.25 * math.sin(w * t * 4), 1) @ rot_eixo(X, 0.3)
        else:
            f = (t % 1.2) / 1.2
            if f < 0.3:
                a = -2.2 * (f / 0.3) ** 2
            elif f < 0.42:
                a = -2.2 + 3.0 * ((f - 0.3) / 0.12)
            else:
                a = 0.8 * (1 - (f - 0.42) / 0.58)
            Rr, d = rot_eixo(Y, -0.25 * math.sin(math.pi * f)), np.zeros(3)
            L["Braco_D"] = rot_eixo(X, a)
            L["Cabeca"] = rot_eixo(X, 0.15 * math.sin(math.pi * f))
    elif n == "Gargulho":
        if clipe == "parado":
            fl = 0.5 * math.sin(w * t / 0.7)
            Rr, d = np.eye(3), np.array([0, 0.12 * math.sin(w * t / 0.7 + 1.2), 0])
        elif clipe == "mover":
            fl = 0.7 * math.sin(w * t / 0.35)
            Rr, d = rot_eixo(X, -0.35), np.array([0, 0.05 * math.sin(w * t / 0.35), -3.0 * t])
        else:
            f = (t % 1.2) / 1.2
            fl = -0.6 if f < 0.5 else 0.6 * math.sin(w * f * 2)
            mergulho = math.sin(math.pi * min(f / 0.5, 1)) if f < 0.5 else math.sin(math.pi * (1 - (f - 0.5) / 0.5)) * 0.3
            Rr, d = rot_eixo(X, -0.9 * mergulho), np.array([0, -1.0 * mergulho, -1.2 * mergulho])
        L["Asa_E"], L["Asa_D"] = rot_eixo(Z, -fl), rot_eixo(Z, fl)
        L["Cauda"] = rot_eixo(X, 0.25 * math.sin(w * t / 0.9))
    else:
        f_ataque = clipe == "ataque"
        vel = {"parado": 0.15, "mover": 1.0, "ataque": 0.3}[clipe]
        ph = w * t / 0.9
        Rr, d = np.eye(3), np.array([0, 0, -1.6 * t if clipe == "mover" else 0])
        if f_ataque:
            f = (t % 1.2) / 1.2
            ergue = math.sin(math.pi * min(f / 0.6, 1)) if f < 0.6 else 0.0
            Rr = rot_eixo(X, 0.75 * ergue)
            L["Mandibula"] = rot_eixo(X, 0.6 * (math.sin(w * f * 3) > 0) * ergue)
        else:
            L["Mandibula"] = rot_eixo(X, 0.12 * max(0, math.sin(w * t * 1.5)))
        for k in range(8):
            L[f"Vertebra_{k + 1}"] = rot_eixo(Y, 0.32 * vel * math.sin(ph - 0.9 * k)) @ (rot_eixo(X, -0.18 * ergue) if f_ataque and k < 3 else np.eye(3))
    return montar(mon, raiz(mon, Rr, d), L)

# ---------------- P1 ----------------
def colisoes(mon, T):
    cel = {}
    for n, p in mon["pecas"].items():
        R, t = T[n]
        q = np.round((p.P[p.solido()] @ R.T + t) / VS).astype(int)
        cel[n] = set(map(tuple, q))
    pior = 0
    nomes = list(mon["pecas"])
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            pa, pb = mon["pecas"][a], mon["pecas"][b]
            if pa.pai == b or pb.pai == a:
                continue
            pior = max(pior, len(cel[a] & cel[b]))
    return pior

if __name__ == "__main__":
    import herois
    mons = [esporinho(), cirio(), gargulho(), ossario()]
    rel = {}
    for m in mons:
        m["faces"] = {n: faces(p) for n, p in m["pecas"].items()}
        soltos = {n: p.limpar_soltos() for n, p in m["pecas"].items()}
        m["faces"] = {n: faces(p) for n, p in m["pecas"].items()}
        vox = sum(p.n() for p in m["pecas"].values())
        tris = {n: 2 * len(malha_gulosa(p.g)) for n, p in m["pecas"].items()}
        pts = np.concatenate([p.P[p.solido()] for p in m["pecas"].values()])
        tam = (pts.max(0) - pts.min(0) + VS).round(2).tolist()
        juntas = [int((((m["pecas"][p.pai].P[m["pecas"][p.pai].solido()] - p.pivo) ** 2).sum(1) <= 0.3 ** 2).sum()) for p in m["pecas"].values() if p.pai]
        col = {c: max(colisoes(m, pose(m, c, i * 0.08)) for i in range(15)) for c in ("parado", "mover", "ataque")}
        rel[m["nome"]] = dict(arquetipo=m["arq"], pecas=len(m["pecas"]), voxels=vox, tris_total=sum(tris.values()), maior_malha=max(tris.values()),
                              tamanho_studs=tam, soltos_removidos=sum(soltos.values()), junta_min_voxels_pai=min(juntas), colisao_max=col)
    json.dump(rel, open(os.path.join(OUT, "relatorio.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in rel.items():
        print(k, v)

    def cena(m, T, d, W, H, esc, cy, extra=()):
        cam = camera_orto(d, Y, (0, cy, -0.4 if m["nome"] == "Ossário" else 0), esc, W, H)
        it = [(m["faces"][n], *T[n]) for n in m["pecas"]] + list(extra)
        return render(it, cam, RGB, EMIS, fundo=(0.20, 0.19, 0.22), bloom=0.6, ambiente=0.55)
    # folha de vistas
    W, H = 300, 280
    folha = Image.new("RGB", (W * 3, H * 4), (255, 255, 255))
    for r, m in enumerate(mons):
        T = pose(m, "parado", 0.0)
        for c, d in enumerate(((0.5, -0.22, 0.84), (1, -0.12, 0.0001), (0.5, -0.22, -0.84))):
            folha.paste(cena(m, T, d, W, H, 52, 1.6), (c * W, r * H))
    folha.save(os.path.join(OUT, "bestiario_vistas.png"))
    # escala com o heroi humano medio
    ch, g, _ = herois.montar("M", 1, "base")
    fh = faces(herois.peca(ch["G"], g))
    lin = Image.new("RGB", (1200, 340), (255, 255, 255))
    xs = [-6.2, -2.6, 1.1, 4.8]
    cam = camera_orto((0.35, -0.2, 0.92), Y, (0, 1.9, 0), 34, 1200, 340)
    it = [(fh, np.eye(3), np.array([-8.6, 0, 0]))]
    for m, x in zip(mons, xs):
        T = pose(m, "parado", 0.0)
        it += [(m["faces"][n], T[n][0], T[n][1] + np.array([x, 0, 0])) for n in m["pecas"]]
    escala = render(it, cam, np.vstack([RGB, herois.RGB]), EMIS, fundo=(0.20, 0.19, 0.22), bloom=0.5, ambiente=0.55) if False else None
    # o heroi usa outra paleta: renderiza em duas passadas e junta
    img_h = render([(fh, np.eye(3), np.array([-8.6, 0, 0]))], cam, herois.RGB, set(), fundo=(0.20, 0.19, 0.22), ambiente=0.55)
    escala = render(it[1:], cam, RGB, EMIS, img_fundo=img_h, bloom=0.5, ambiente=0.55)
    escala.save(os.path.join(OUT, "bestiario_escala.png"))
    # animacao: 2x2, cada painel passa por parado, mover e ataque
    frames = []
    duracoes = (("parado", 1.6), ("mover", 1.6), ("ataque", 1.2))
    for clipe, dur in duracoes:
        for i in range(int(dur / 0.07)):
            t = i * 0.07
            quad = Image.new("RGB", (720, 560))
            for k, m in enumerate(mons):
                T = pose(m, clipe, t)
                if clipe == "mover":
                    raiz_n = next(n for n, p in m["pecas"].items() if p.pai is None)
                    off = T[raiz_n][1] - (np.eye(3) - T[raiz_n][0]) @ np.zeros(3)
                    desl = np.array([0, 0, (T[raiz_n][0] @ m["pecas"][raiz_n].pivo + T[raiz_n][1])[2] - m["pecas"][raiz_n].pivo[2]])
                    T = {n: (R, tt - desl) for n, (R, tt) in T.items()}
                quad.paste(cena(m, T, (0.62, -0.3, 0.72), 360, 280, 46, 1.5), ((k % 2) * 360, (k // 2) * 280))
            frames.append(quad)
    frames[0].save(os.path.join(OUT, "bestiario_animacoes.webp"), save_all=True, append_images=frames[1:], duration=70, loop=0, quality=82)
    print("ok", len(frames))
