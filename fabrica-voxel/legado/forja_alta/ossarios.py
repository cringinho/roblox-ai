"""Variacoes do Ossario por ficha, e o Esqueleto de susto (corte de susto a 0,0625)."""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import capsula, construir, faces, render, camera_orto, camera_persp, rot_eixo, hex_rgb, malha_gulosa, ruido
import bestiario as B

PAL = B.PAL + [("sangue", "7A1E1E"), ("osso_rubro", "C9A89A"), ("osso_rubro_s", "9C7A6C"), ("musgo_osso", "6E7F4A"), ("fungo_cap", "B5A27A"),
               ("gelo", "A9C4D6"), ("gelo_c", "DCEBF5"), ("gelo_s", "7A93A6"), ("cristal", "8FE3FF"), ("brasa", "FF5A3C")]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
RGB = np.array([hex_rgb(h) for h in ["000000"] + [h for _, h in PAL]])
EMIS = B.EMIS | {K["cristal"], K["brasa"]}
OUT = B.OUT
X, Y, Z = B.X, B.Y, B.Z

FICHAS = [
    dict(id="ossario.rubro", nome="Ossário Rubro", segs=6, esc=1.25, cores=("sangue", "osso_rubro_s", "osso_rubro"), olho="brasa", extra="espinhos"),
    dict(id="ossario.mofado", nome="Ossário Mofado", segs=11, esc=0.9, cores=("osso_e", "musgo_osso", "osso"), olho="alma", extra="fungos"),
    dict(id="ossario.gelido", nome="Ossário Gélido", segs=8, esc=1.05, cores=("gelo_s", "gelo", "gelo_c"), olho="cristal", extra="cristais"),
]

def faixa(cy, ry, c):
    return lambda P: np.where((P[:, 1] - cy) / ry < -0.3, K[c[0]], np.where((P[:, 1] - cy) / ry > 0.4, K[c[2]], K[c[1]]))

def variante(f, vs=0.125):
    e = f["esc"]; c = f["cores"]
    def cranio(P):
        cc = faixa(0.62 * e, 0.42 * e, c)(P)
        for s in (-1, 1):
            o = np.array([s * 0.2 * e, 0.68 * e, -2.25 * e - 0.45 * e])
            cc = np.where(np.linalg.norm((P - o)[:, :2], axis=1) < 0.12 * e, K["buraco"], cc)
            cc = np.where(np.linalg.norm(P - o, axis=1) < 0.08 * e, K[f["olho"]], cc)
        return cc
    pecas = {"Cranio": construir("Cranio", None, vs, (0, 0.5 * e, -2.1 * e), [('U', ('ell', (0, 0.62 * e, -2.25 * e), (0.5 * e, 0.42 * e, 0.52 * e)), cranio)]),
             "Mandibula": construir("Mandibula", "Cranio", vs, (0, 0.42 * e, -2.0 * e), [('U', ('ell', (0, 0.3 * e, -2.3 * e), (0.36 * e, 0.12 * e, 0.38 * e)), K[c[1]])])}
    pai = "Cranio"
    passo = 0.5 * e
    for k in range(f["segs"]):
        z = -1.7 * e + passo * k; r = (0.38 - 0.18 * k / f["segs"]) * e
        ops = [('U', ('ell', (0, 0.45 * e, z), (r, r * 0.85, 0.27 * e)), faixa(0.45 * e, r, c))]
        for s in (-1, 1):
            ops.append(('U', ('cap', (s * r * 0.7, 0.45 * e, z), (s * (r + 0.5 * e), 0.06, z - 0.12 * e), 0.11 * e, 0.09 * e), K[c[1]]))
        if f["extra"] == "espinhos":
            ops.append(('U', ('cone', (0, 0.6 * e, z), (0, 1.15 * e, z + 0.15 * e), 0.13 * e), K["sangue"]))
        elif f["extra"] == "fungos" and k % 2 == 0:
            cc = (0.12 * (-1) ** k, 0.8 * e, z)
            ops.append(('U', ('cap', (cc[0], 0.55 * e, z), cc, 0.1), K["fungo"]))
            ops.append(('U', ('ell', (cc[0], 0.86 * e, z), (0.2, 0.08, 0.2)), K["fungo_cap"]))
        elif f["extra"] == "cristais" and k % 3 != 2:
            ops.append(('U', ('cone', (0.08 * (-1) ** k, 0.55 * e, z), (0.25 * (-1) ** k, 1.2 * e, z - 0.05), 0.14), K["cristal"]))
        else:
            ops.append(('U', ('cone', (0, 0.6 * e, z), (0, 0.85 * e, z + 0.08), 0.07), K[c[2]]))
        n = f"Vertebra_{k + 1}"
        pecas[n] = construir(n, pai, vs, (0, 0.45 * e, z - 0.25 * e), ops)
        pai = n
    if f["extra"] == "espinhos":
        for s in (-1, 1):
            m = capsula(pecas["Cranio"].P, (s * 0.3 * e, 0.88 * e, -2.15 * e), (s * 0.62 * e, 1.5 * e, -1.85 * e), 0.12 * e, 0.03)
            pecas["Cranio"].unir(m, K[c[2]])
    return dict(nome=f["nome"], arq="corrente", pecas=pecas, ficha=f)

def esqueleto(vs_fino=0.0625, vs=0.125):
    """Esqueleto de susto: tronco de costelas sobre a cauda do Ossario, cranio e maos em microvoxel."""
    c = ("osso_e", "osso_s", "osso")
    pecas = {}
    pecas["Base"] = construir("Base", None, vs, (0, 0.35, 0.6), [('U', ('cap', (0, 0.3, 0.2), (0, 0.25, 2.6), 0.32, 0.12), faixa(0.3, 0.3, c))] +
                              [('U', ('cap', (s * 0.15, 0.3, z), (s * 0.7, 0.05, z - 0.1), 0.09), K["osso_s"]) for s in (-1, 1) for z in (0.5, 1.1, 1.7, 2.3)])
    def costelas(P):
        cc = faixa(1.3, 0.6, c)(P)
        vao = (np.floor((P[:, 1] - 0.8) / 0.2) % 2 == 1) & (np.abs(P[:, 0]) > 0.12) & (P[:, 2] < 0.2)
        return cc, vao
    tor = construir("Torax", "Base", vs, (0, 0.55, 0.25), [
        ('U', ('cap', (0, 0.5, 0.25), (0, 2.38, 0.05), 0.15), K["osso_s"]),
        ('U', ('cap', (0, 0.95, -0.47), (0, 1.85, -0.45), 0.09), K["osso"]),
        ('U', ('ell', (0, 1.4, -0.05), (0.62, 0.62, 0.45)), lambda P: costelas(P)[0]),
        ('C', lambda P: (((P - np.array([0, 1.4, -0.05])) / np.array([0.44, 0.46, 0.28])) ** 2).sum(1) <= 1, None),
        ('C', lambda P: costelas(P)[1] & ((((P - np.array([0, 1.4, -0.05])) / np.array([0.62, 0.62, 0.45])) ** 2).sum(1) <= 1), None),
        ('U', ('cap', (-0.55, 1.85, 0.0), (0.55, 1.85, 0.0), 0.1), K["osso"])])
    pecas["Torax"] = tor
    def rosto(P):
        cc = faixa(2.55, 0.42, c)(P)
        for s in (-1, 1):
            o = np.array([s * 0.17, 2.62, -0.4])
            cc = np.where(np.linalg.norm((P - o)[:, :2], axis=1) < 0.12, K["buraco"], cc)
            cc = np.where(np.linalg.norm((P - o)[:, :2], axis=1) < 0.055, K["alma"], cc)
        nariz = (np.abs(P[:, 0]) < 0.05) & (np.abs(P[:, 1] - 2.43) < 0.06) & (P[:, 2] < -0.35)
        dentes = (np.abs(P[:, 1] - 2.27) < 0.035) & (P[:, 2] < -0.3) & (np.floor(P[:, 0] / 0.0625) % 2 == 0)
        return np.where(nariz, K["buraco"], np.where(dentes, K["osso_unha"], cc))
    pecas["Cranio"] = construir("Cranio", "Torax", vs_fino, (0, 2.3, 0.05), [
        ('U', ('ell', (0, 2.66, -0.05), (0.46, 0.48, 0.46)), rosto),
        ('U', ('ell', (0, 2.33, -0.18), (0.3, 0.14, 0.26)), rosto)])
    pecas["Mandibula"] = construir("Mandibula", "Cranio", vs_fino, (0, 2.3, 0.1), [
        ('U', ('ell', (0, 2.18, -0.2), (0.27, 0.08, 0.26)), K["osso_s"]),
        ('U', ('ell', (0, 2.24, -0.4), (0.22, 0.04, 0.06)), lambda P: np.where(np.floor(P[:, 0] / 0.0625) % 2 == 0, K["osso_unha"], K["osso_s"]))])
    for s, L in ((-1, "E"), (1, "D")):
        om, cot, mao = np.array([s * 0.55, 1.85, 0.0]), np.array([s * 0.9, 1.25, -0.2]), np.array([s * 0.85, 0.75, -0.55])
        pecas[f"Umero_{L}"] = construir(f"Umero_{L}", "Torax", vs, om, [('U', ('cap', om, cot, 0.14, 0.12), K["osso"])])
        ops = [('U', ('cap', cot, mao, 0.11, 0.09), K["osso_s"]), ('U', ('ell', mao + np.array([0, -0.08, -0.04]), (0.14, 0.12, 0.08)), K["osso"])]
        for k in (-1.5, -0.5, 0.5, 1.5):
            dedo = mao + np.array([k * 0.07, -0.42, -0.12])
            ops.append(('U', ('cap', mao + np.array([k * 0.05, -0.1, -0.04]), dedo, 0.05, 0.035), K["osso_unha"]))
        pecas[f"Antebraco_{L}"] = construir(f"Antebraco_{L}", f"Umero_{L}", vs_fino, cot, ops)
    return dict(nome="Esqueleto de susto", arq="corrente erguida", pecas=pecas)

def pose_esqueleto(mon, t, dur=1.6):
    """0 a 0,45: pilha de ossos deitada, com tremor. 0,45 a 0,6: ergue de uma vez com sobressalto. Depois: mandibula abre, bracos avancam."""
    f = t / dur
    if f < 0.45:
        ang = math.radians(-82) + 0.03 * math.sin(t * 40) * (f > 0.3)
    elif f < 0.6:
        u = (f - 0.45) / 0.15
        ang = math.radians(-82 + 92 * (1 - (1 - u) ** 3)) + math.radians(6) * math.sin(math.pi * u)
    else:
        ang = math.radians(10 - 4 * min((f - 0.6) / 0.2, 1))
    L = {"Torax": rot_eixo(X, ang)}
    abre = 0 if f < 0.58 else min((f - 0.58) / 0.08, 1)
    L["Mandibula"] = rot_eixo(X, math.radians(58) * abre)
    L["Cranio"] = rot_eixo(Z, math.radians(9) * math.sin(t * 25) * abre) @ rot_eixo(X, math.radians(-8) * abre)
    alc = 0 if f < 0.55 else min((f - 0.55) / 0.12, 1)
    for s, Ln in ((-1, "E"), (1, "D")):
        L[f"Umero_{Ln}"] = rot_eixo(X, math.radians(-75) * alc) @ rot_eixo(Z, s * math.radians(25) * alc)
        L[f"Antebraco_{Ln}"] = rot_eixo(X, math.radians(-35) * alc)
    return B.montar(mon, B.raiz(mon, np.eye(3), np.zeros(3)), L)

def pose_var(mon, clipe, t):
    n = sum(1 for k in mon["pecas"] if k.startswith("Vertebra"))
    w = 2 * math.pi; L = {}
    vel = {"parado": 0.15, "mover": 1.0, "ataque": 0.3}[clipe]
    ph = w * t / 0.9
    Rr, d = np.eye(3), np.array([0, 0, -1.6 * t if clipe == "mover" else 0])
    ergue = 0
    if clipe == "ataque":
        f = (t % 1.2) / 1.2
        ergue = math.sin(math.pi * min(f / 0.6, 1)) if f < 0.6 else 0.0
        Rr = rot_eixo(X, 0.75 * ergue)
        L["Mandibula"] = rot_eixo(X, 0.6 * (math.sin(w * f * 3) > 0) * ergue)
    else:
        L["Mandibula"] = rot_eixo(X, 0.12 * max(0, math.sin(w * t * 1.5)))
    for k in range(n):
        L[f"Vertebra_{k + 1}"] = rot_eixo(Y, 0.32 * vel * math.sin(ph - 0.9 * k) * 8 / n) @ (rot_eixo(X, -0.18 * ergue) if k < 3 else np.eye(3))
    return B.montar(mon, B.raiz(mon, Rr, d), L)

def cena(mon, T, cam, **kw):
    it = [(mon["faces"][n], *T[n]) for n in mon["pecas"]]
    return render(it, cam, RGB, EMIS, **kw)

# ================= esqueleto de elite, redesenhado para assustar =================
def esqueleto(vs_fino=0.0625, vs=0.125):
    def osso_sujo(cy, ry):
        def f(P):
            h = (P[:, 1] - cy) / ry
            c = np.where(h < -0.2, K["osso_e"], np.where(h > 0.5, K["osso"], K["osso_s"]))
            mancha = ruido(P, 3.2, seed=21) > 0.66
            return np.where(mancha, K["sangue"], c)
        return f
    pecas = {}
    pecas["Base"] = construir("Base", None, vs, (0, 1.05, 0.1), [
        ('U', ('ell', (0, 1.05, 0.1), (0.38, 0.2, 0.26)), osso_sujo(1.05, 0.2)),
        ('C', ('ell', (0, 1.0, -0.05), (0.18, 0.12, 0.2)), None),
        ('U', ('cap', (0, 1.0, 0.3), (0, 0.45, 0.9), 0.13, 0.11), K["osso_e"]),
        ('U', ('cap', (0, 0.45, 0.9), (0, 0.12, 1.8), 0.11, 0.09), K["osso_e"]),
        ('U', ('cap', (0, 0.12, 1.8), (0.25, 0.08, 2.7), 0.09, 0.05), K["osso_e"])] +
        [('U', ('ell', (0, y, z), (0.16, 0.1, 0.08)), K["osso_s"]) for y, z in ((0.85, 0.5), (0.6, 0.75), (0.3, 1.25), (0.15, 1.6), (0.12, 2.1))])
    for s, L in ((-1, "E"), (1, "D")):
        q, j, pe = np.array([s * 0.24, 1.0, 0.1]), np.array([s * 0.3, 0.55, -0.12]), np.array([s * 0.3, 0.08, 0.05])
        pecas[f"Perna_{L}"] = construir(f"Perna_{L}", "Base", vs, q, [('U', ('cap', q, j, 0.11, 0.09), K["osso_s"]), ('U', ('cap', j, pe, 0.09, 0.08), K["osso_e"]),
                                                                       ('U', ('ell', j, (0.12, 0.1, 0.1)), K["osso"]), ('U', ('ell', pe + (0, 0, -0.15), (0.11, 0.06, 0.22)), K["osso_s"])])
    def vao(P):
        v = (np.floor((P[:, 1] - 0.9) / 0.2) % 2 == 1) & (np.abs(P[:, 0]) > 0.12) & (P[:, 2] < 0.15)
        quebra = (P[:, 0] > 0.15) & (P[:, 1] > 1.55) & (P[:, 1] < 1.95) & (P[:, 2] < -0.1)
        return v | quebra
    pecas["Torax"] = construir("Torax", "Base", vs, (0, 1.1, 0.15), [
        ('U', ('cap', (0, 1.0, 0.18), (0, 2.55, 0.1), 0.14), K["osso_e"]),
        ('U', ('cap', (0, 1.0, -0.42), (0, 2.1, -0.4), 0.09), K["osso"]),
        ('U', ('ell', (0, 1.6, -0.05), (0.5, 0.78, 0.4)), osso_sujo(1.6, 0.78)),
        ('C', lambda P: (((P - np.array([0, 1.6, -0.05])) / np.array([0.36, 0.64, 0.26])) ** 2).sum(1) <= 1, None),
        ('C', lambda P: vao(P) & ((((P - np.array([0, 1.6, -0.05])) / np.array([0.5, 0.78, 0.4])) ** 2).sum(1) <= 1), None),
        ('U', ('cap', (-0.62, 2.35, 0.05), (0.62, 2.35, 0.05), 0.1), K["osso_s"]),
        ('U', ('cap', (-0.5, 1.8, 0.05), (0.5, 1.8, 0.05), 0.09), K["osso_s"])])
    pecas["Pescoco"] = construir("Pescoco", "Torax", vs, (0, 2.5, 0.08), [
        ('U', ('cap', (0, 2.5, 0.08), (0, 3.05, -0.08), 0.1), K["osso_s"])] +
        [('U', ('ell', (0, y, z), (0.15, 0.06, 0.13)), K["osso_e"]) for y, z in ((2.62, 0.04), (2.78, -0.01), (2.94, -0.05))])
    def rosto(P):
        cc = osso_sujo(3.35, 0.5)(P)
        racha = (np.abs(P[:, 0] - 0.08 * np.sin(P[:, 2] * 9)) < 0.04) & (P[:, 1] > 3.62)
        cc = np.where(racha, K["buraco"], cc)
        for s in (-1, 1):
            o = np.array([s * 0.15, 3.36, -0.5])
            orb = ((P[:, 0] - o[0]) / 0.11) ** 2 + ((P[:, 1] - o[1]) / 0.17) ** 2 < 1
            cc = np.where(orb, K["buraco"], cc)
            cc = np.where(np.linalg.norm((P - (o + np.array([-s * 0.03, -0.06, 0])))[:, :2], axis=1) < 0.035, K["brasa"], cc)
        nariz = (np.abs(P[:, 0]) < 0.05) & (P[:, 1] > 3.1) & (P[:, 1] < 3.2) & (P[:, 2] < -0.4)
        dentes = (P[:, 1] > 2.93) & (P[:, 1] < 3.03) & (P[:, 2] < -0.32) & (np.floor(P[:, 0] / 0.0625) % 2 == 0)
        return np.where(nariz, K["buraco"], np.where(dentes, K["osso_unha"], cc))
    pecas["Cranio"] = construir("Cranio", "Pescoco", vs_fino, (0, 3.05, -0.08), [
        ('U', ('ell', (0, 3.38, -0.15), (0.36, 0.5, 0.46)), rosto),
        ('U', ('ell', (0, 3.05, -0.28), (0.27, 0.14, 0.28)), rosto)])
    def mand(P):
        return np.where((P[:, 1] > 2.96) & (np.floor(P[:, 0] / 0.0625) % 2 == 0), K["osso_unha"], K["osso_s"])
    pecas["Mandibula"] = construir("Mandibula", "Cranio", vs_fino, (0, 3.0, -0.02), [
        ('U', ('ell', (0, 2.82, -0.3), (0.25, 0.1, 0.3)), K["osso_s"]),
        ('U', ('ell', (0, 2.95, -0.5), (0.2, 0.06, 0.07)), mand)])
    bracos = [("E1", -1, 2.35, 1.0), ("D1", 1, 2.35, 1.0), ("E2", -1, 1.8, 0.85), ("D2", 1, 1.8, 0.85)]
    for L, s, y, k in bracos:
        om, cot, mao = np.array([s * 0.6, y, 0.05]), np.array([s * 1.05, y - 0.55 * k, -0.15]), np.array([s * 1.0, y - 1.2 * k, -0.55])
        pecas[f"Umero_{L}"] = construir(f"Umero_{L}", "Torax", vs, om, [('U', ('cap', om, cot, 0.11 * k, 0.09 * k), K["osso_s"])])
        ops = [('U', ('cap', cot, mao, 0.09 * k, 0.07), K["osso_e"]), ('U', ('ell', mao + np.array([0, -0.06, -0.04]), (0.12, 0.1, 0.07)), K["osso"])]
        for j in (-1.5, -0.5, 0.5, 1.5):
            dedo = mao + np.array([j * 0.09, -0.62 * k, -0.2])
            ops.append(('U', ('cap', mao + np.array([j * 0.05, -0.08, -0.04]), dedo, 0.045, 0.03), K["osso_unha"]))
        pecas[f"Antebraco_{L}"] = construir(f"Antebraco_{L}", f"Umero_{L}", vs_fino, cot, ops)
    return dict(nome="Esqueleto de susto", arq="corrente erguida", pecas=pecas)

def pose_esqueleto(mon, t, dur=1.6):
    """0 a 0,45: pilha de ossos com tremor. 0,45 a 0,52: ergue em 0,1 s e avanca. Depois: pescoco estica, cabeca entorta 70 graus, quatro maos fecham a tela."""
    f = t / dur
    if f < 0.45:
        ang, av = math.radians(-82) + 0.04 * math.sin(t * 45) * (f > 0.3), 0.0
    elif f < 0.52:
        u = (f - 0.45) / 0.07
        ang, av = math.radians(-82 + 95 * (1 - (1 - u) ** 3)), 1.3 * u
    else:
        ang, av = math.radians(13 - 3 * min((f - 0.52) / 0.2, 1)), 1.3
    L = {"Torax": rot_eixo(X, ang)}
    abre = 0 if f < 0.55 else min((f - 0.55) / 0.06, 1)
    L["Pescoco"] = rot_eixo(X, math.radians(-35) * abre)
    L["Cranio"] = rot_eixo(Z, math.radians(70) * abre + math.radians(5) * math.sin(t * 31) * abre) @ rot_eixo(X, math.radians(-15) * abre)
    L["Mandibula"] = rot_eixo(X, math.radians(80) * abre) @ rot_eixo(Z, math.radians(-12) * abre)
    alc = 0 if f < 0.5 else min((f - 0.5) / 0.08, 1)
    for Ln, s, cima in (("E1", -1, 1), ("D1", 1, 1), ("E2", -1, 0), ("D2", 1, 0)):
        if cima:
            L[f"Umero_{Ln}"] = rot_eixo(X, math.radians(-115) * alc) @ rot_eixo(Z, s * math.radians(40) * alc)
            L[f"Antebraco_{Ln}"] = rot_eixo(X, math.radians(-50) * alc)
        else:
            L[f"Umero_{Ln}"] = rot_eixo(X, math.radians(-70) * alc) @ rot_eixo(Z, -s * math.radians(10) * alc)
            L[f"Antebraco_{Ln}"] = rot_eixo(X, math.radians(-25) * alc)
    return B.montar(mon, B.raiz(mon, np.eye(3), np.array([0, 0, -av])), L)


def pose_quadro(mon, etapa, t=0.0):
    """Storyboard do susto: 'longe' (parado, curvado), 'avanco' (bracos abertos), 'rosto' (perto, cabeca torta)."""
    L = {}
    if etapa == "longe":
        L["Torax"] = rot_eixo(X, math.radians(18)); L["Pescoco"] = rot_eixo(X, math.radians(-20))
        L["Cranio"] = rot_eixo(Z, math.radians(18))
        for Ln in ("E1", "D1", "E2", "D2"):
            L[f"Umero_{Ln}"] = rot_eixo(X, math.radians(-10))
        d = np.zeros(3)
    elif etapa == "avanco":
        L["Torax"] = rot_eixo(X, math.radians(28)); L["Pescoco"] = rot_eixo(X, math.radians(-30))
        L["Cranio"] = rot_eixo(Z, math.radians(35)); L["Mandibula"] = rot_eixo(X, math.radians(34))
        for Ln, s, cima in (("E1", -1, 1), ("D1", 1, 1), ("E2", -1, 0), ("D2", 1, 0)):
            L[f"Umero_{Ln}"] = rot_eixo(X, math.radians(-100 if cima else -60)) @ rot_eixo(Z, s * math.radians(55 if cima else 30))
            L[f"Antebraco_{Ln}"] = rot_eixo(X, math.radians(-30))
        L["Perna_E"], L["Perna_D"] = rot_eixo(X, math.radians(-30)), rot_eixo(X, math.radians(20))
        d = np.zeros(3)
    else:
        return pose_esqueleto(mon, 1.4)
    return B.montar(mon, B.raiz(mon, np.eye(3), d), L)


if __name__ == "__main__":
    mons = [variante(f) for f in FICHAS] + [esqueleto()]
    rel = {}
    for m in mons:
        sol = sum(p.limpar_soltos() for p in m["pecas"].values())
        m["faces"] = {n: faces(p) for n, p in m["pecas"].items()}
        tris = {n: 2 * len(malha_gulosa(p.g)) for n, p in m["pecas"].items()}
        pts = np.concatenate([p.P[p.solido()] for p in m["pecas"].values()])
        poses = [pose_esqueleto(m, i * 0.1) for i in range(16)] if m["nome"].startswith("Esq") else \
                [pose_var(m, c, i * 0.08) for c in ("parado", "mover", "ataque") for i in range(15)]
        col = max(B.colisoes(m, T) for T in poses)
        rel[m["nome"]] = dict(pecas=len(m["pecas"]), voxels=sum(p.n() for p in m["pecas"].values()), tris=sum(tris.values()),
                              maior_malha=max(tris.values()), tamanho=(pts.max(0) - pts.min(0) + 0.125).round(2).tolist(), soltos=sol, colisao_max=col)
        print(m["nome"], rel[m["nome"]])
    json.dump(rel, open(os.path.join(OUT, "ossarios_relatorio.json"), "w"), indent=1, ensure_ascii=False)
    base = B.ossario(); base["faces"] = {n: faces(p) for n, p in base["pecas"].items()}
    # folha: original + 3 variantes + esqueleto erguido
    W, H = 300, 230
    folha = Image.new("RGB", (W * 2, H * 3), (255, 255, 255))
    linha = [(base, B.pose(base, "parado", 0.0), B.RGB, B.EMIS)] + [(m, pose_var(m, "parado", 0.0), RGB, EMIS) for m in mons[:3]]
    for k, (m, T, rgb, em) in enumerate(linha):
        cam = camera_orto((0.62, -0.32, 0.72), Y, (0, 0.6, -0.2), 40, W, H)
        it = [(m["faces"][n], *T[n]) for n in m["pecas"]]
        folha.paste(render(it, cam, rgb, em, fundo=(0.2, 0.19, 0.22), bloom=0.6, ambiente=0.55), ((k % 2) * W, (k // 2) * H))
    esq = mons[3]
    Te = pose_esqueleto(esq, 1.4)
    folha.paste(cena(esq, Te, camera_orto((0.55, -0.15, 0.83), Y, (0, 1.9, -0.6), 52, W, H), fundo=(0.2, 0.19, 0.22), bloom=0.6, ambiente=0.55), (0, 2 * H))
    folha.paste(cena(esq, pose_esqueleto(esq, 0.2), camera_orto((0.55, -0.4, 0.73), Y, (0, 0.6, 0.6), 50, W, H), fundo=(0.2, 0.19, 0.22), bloom=0.6, ambiente=0.55), (W, 2 * H))
    folha.save(os.path.join(OUT, "ossarios_variacoes.png"))
    # susto em primeira pessoa: camera no olho do heroi, lanterna de baixo
    olho = np.array([0.1, 2.6, -2.6])
    alvo = np.array([0, 2.8, -1.0])
    fr = []
    for i in range(24):
        t = i * 1.6 / 24
        T = pose_esqueleto(esq, t)
        cam = camera_persp(olho, alvo, Y, 70, 640, 360)
        fr.append(cena(esq, T, cam, fundo=(0, 0, 0), lanterna=(olho + np.array([0.4, -0.7, 0.2]), 1.3 * (0.35 if i in (13, 15) else 1.0), 2.4), neblina=((0, 0, 0), 2.5, 6.0), bloom=0.9))
    for _ in range(8):
        fr.append(fr[-1])
    fr[0].save(os.path.join(OUT, "esqueleto_susto.webp"), save_all=True, append_images=fr[1:], duration=67, loop=0, quality=85)
    fr[21].save(os.path.join(OUT, "esqueleto_susto_pico.png"))
    # storyboard do susto em primeira pessoa: tres distancias
    chao = construir("Chao", None, 0.25, (0, 0, 0), [('U', ('ell', (0, -0.15, 0), (6.0, 0.14, 9.0)), K["pedra_s"])])
    fch = faces(chao)
    sb = Image.new("RGB", (3 * 400, 225))
    for k, (etapa, dist) in enumerate((("longe", 7.0), ("avanco", 3.6), ("rosto", 2.6))):
        T = pose_quadro(esq, etapa)
        olho = np.array([0.15, 2.4, -dist]); alvo = np.array([0, 2.0 if etapa != "rosto" else 2.8, 0 if etapa != "rosto" else -1.2])
        cam = camera_persp(olho, alvo, Y, 70, 400, 225)
        it = [(esq["faces"][n], *T[n]) for n in esq["pecas"]] + [(fch, np.eye(3), np.zeros(3))]
        sb.paste(render(it, cam, RGB, EMIS, fundo=(0, 0, 0), lanterna=(olho + np.array([0.4, -0.8, 0.2]), 1.6, 4.0 + dist * 0.4),
                        neblina=((0.01, 0.01, 0.02), 3.0 + dist * 0.5, 9.0 + dist), bloom=0.9), (k * 400, 0))
    sb.save(os.path.join(OUT, "esqueleto_storyboard.png"))
    # variantes animadas 2x2: parado, mover, ataque
    frames = []
    for clipe, dur in (("parado", 1.2), ("mover", 1.2), ("ataque", 1.2)):
        for i in range(int(dur / 0.07)):
            t = i * 0.07; q = Image.new("RGB", (720, 280))
            for k, m in enumerate(mons[:3]):
                T = pose_var(m, clipe, t)
                if clipe == "mover":
                    T = {n: (R, tt + np.array([0, 0, 1.6 * t])) for n, (R, tt) in T.items()}
                q.paste(cena(m, T, camera_orto((0.62, -0.32, 0.72), Y, (0, 0.7, -0.2), 32, 240, 280), fundo=(0.2, 0.19, 0.22), bloom=0.6, ambiente=0.55), (k * 240, 0))
            frames.append(q)
    frames[0].save(os.path.join(OUT, "ossarios_animacoes.webp"), save_all=True, append_images=frames[1:], duration=70, loop=0, quality=82)
    print("ok")




