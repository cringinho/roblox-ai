"""Slimes goticos: 8 variantes por ficha (paleta, textura, conteudo, adorno e tamanho), rig e 3 clipes de squash e stretch."""
import sys, os, math, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import construir, faces, render, camera_orto, rot_eixo, hex_rgb, malha_gulosa, ruido
import bestiario as B

X, Y, Z = B.X, B.Y, B.Z
OUT = B.OUT
# paleta: comuns + 5 tons por variante (claro, base, sombra, escuro, brilho)
PAL = list(B.PAL) + [("ferro", "4A4448"), ("ferrugem", "7A3E22"), ("ouro_velho", "A8873A"), ("vidro_r", "B0304A"), ("vidro_a", "D99A2B"), ("vidro_v", "4A2A8A")]
FICHAS = [
 dict(nome="Coágulo", tam=1.0, cores=("9E2B2B", "6E1616", "4A0C0E", "2A0608", "FFB0A0"), textura="bolhas", dentro="dedos", adorno=None, olhos="brasa"),
 dict(nome="Cera Negra", tam=0.7, cores=("4A4448", "2E2A2E", "1E1B1F", "121014", "8A8290"), textura="escorrido", dentro=None, adorno="velas", olhos="buraco"),
 dict(nome="Ectoplasma", tam=1.5, cores=("8FF0B8", "4FC488", "2E8A5E", "1A5440", "E6FFF0"), textura="veias", dentro="cranio", adorno=None, olhos="nenhum"),
 dict(nome="Vitral", tam=1.0, cores=("6E4A9A", "4A2E70", "33204E", "1E1230", "D8C0FF"), textura="cacos", dentro=None, adorno="cacos", olhos="brasa"),
 dict(nome="Tinta de Sepulcro", tam=0.7, cores=("2E3A5E", "1C2440", "11172C", "080B16", "7A90C8"), textura="bolhas", dentro=None, adorno="pena", olhos="ciclope"),
 dict(nome="Bile de Gárgula", tam=1.5, cores=("8A8A70", "5E6048", "40422E", "26281A", "C8C8A8"), textura="crosta", dentro="ossos", adorno=None, olhos="brasa"),
 dict(nome="Vinho Profano", tam=1.0, cores=("8A1E4A", "5E1032", "400822", "240412", "F0A0C8"), textura="veias", dentro="calice", adorno=None, olhos="buraco"),
 dict(nome="Rei Lodo", tam=2.2, cores=("5E5A3A", "403E26", "2A2918", "17160C", "B8B488"), textura="bolhas", dentro="cranio", adorno="coroa", olhos="muitos"),
]
for i, f in enumerate(FICHAS):
    for j, s in enumerate(("c", "b", "s", "e", "h")):
        PAL.append((f"v{i}_{s}", f["cores"][j]))
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
RGB = np.array([hex_rgb(h) for h in ["000000"] + [h for _, h in PAL]])
EMIS = set(B.EMIS)
VS = 0.125

def corpo_cor(i, f, r, cy):
    c = {s: K[f"v{i}_{s}"] for s in "cbseh"}
    def fn(P):
        y = (P[:, 1] - cy) / r
        n = ruido(P, 3.5 / f["tam"], seed=40 + i)
        col = np.where(y > 0.25, c["c"], np.where(y > -0.35, c["b"], c["s"]))
        col = np.where(n > 0.7, c["s"], col)
        col = np.where(P[:, 1] < 0.18, c["e"], col)
        t = f["textura"]
        if t == "bolhas":
            col = np.where(ruido(P, 9.0 / f["tam"], seed=7 + i) > 0.8, c["h"], col)
            col = np.where(ruido(P, 6.0 / f["tam"], seed=11 + i) < 0.12, c["e"], col)
        elif t == "veias":
            v = np.abs(ruido(P, 4.0 / f["tam"], seed=3 + i) - 0.5) < 0.035
            col = np.where(v, c["e"] if i != 2 else c["h"], col)
        elif t == "crosta":
            v = np.abs(ruido(P, 5.0 / f["tam"], seed=9) - 0.5) < 0.04
            col = np.where(y > -0.1, np.where(v, c["e"], c["c"]), col)
        elif t == "escorrido":
            fio = (np.abs(np.sin(np.arctan2(P[:, 2], P[:, 0]) * 7)) > 0.9) & (y > -0.6)
            col = np.where(fio, c["c"], col)
        elif t == "cacos":
            col = np.where(ruido(P, 5.0, seed=5) > 0.74, K["vidro_a"], np.where(ruido(P, 5.0, seed=6) > 0.76, K["vidro_r"], col))
        # brilho especular: mancha clara em cima-frente-esquerda
        esp = ((P[:, 0] + 0.35 * r) ** 2 + (P[:, 1] - cy - 0.55 * r) ** 2 + (P[:, 2] + 0.5 * r) ** 2) < (0.22 * r) ** 2
        return np.where(esp, c["h"], col)
    return fn

FORMA = {  # (raio x, altura, raio z, inclinacao, amplitude do ruido, frequencia, afina no topo)
 "Coágulo": (1.0, 0.8, 0.95, 0.0, 0.28, 2.2, 0.0), "Cera Negra": (0.75, 1.25, 0.75, 0.0, 0.12, 1.5, 0.35),
 "Ectoplasma": (0.85, 1.1, 0.85, 0.18, 0.14, 1.4, 0.3), "Vitral": (0.95, 0.85, 0.9, 0.0, 0.1, 2.0, 0.0),
 "Tinta de Sepulcro": (1.2, 0.55, 1.1, 0.0, 0.2, 2.5, 0.0), "Bile de Gárgula": (1.0, 0.75, 0.95, -0.1, 0.32, 1.6, 0.1),
 "Vinho Profano": (1.0, 0.8, 0.95, 0.08, 0.14, 1.8, 0.1), "Rei Lodo": (1.05, 0.7, 1.0, 0.0, 0.2, 1.3, 0.15)}

def slime(i):
    f = FICHAS[i]; s = f["tam"]; c = {k: K[f"v{i}_{k}"] for k in "cbseh"}
    fx, fy, fz_, lean, amp, fq, afina = FORMA[f["nome"]]
    r = 0.95 * s * fx; ry = 0.82 * s * fy; rz = 0.95 * s * fz_; cy = ry * 0.95
    cc = np.array([0, cy, 0])
    def forma(P):
        q = P - cc
        h = np.clip(q[:, 1] / ry, -1, 1)
        q = q - np.stack([lean * s * np.maximum(h, 0) ** 2, 0 * h, 0 * h], 1)
        esc = 1 - afina * np.maximum(h, 0) ** 1.5
        d = np.sqrt((q[:, 0] / (r * esc)) ** 2 + (q[:, 1] / ry) ** 2 + (q[:, 2] / (rz * esc)) ** 2)
        return d > 1 + amp * (ruido(P, fq / s, seed=60 + i) - 0.5) * 2
    ops = [('U', ('ell', (0, cy, 0), (r * 1.35, ry * 1.35, rz * 1.35)), corpo_cor(i, f, max(r, ry), cy)),
           ('C', forma, None),
           ('U', ('ell', (0, 0.1, 0), (r * 1.2, 0.12, rz * 1.15)), c["e"])]
    ops.append(('C', lambda P: P[:, 1] < 0, None))
    for k in range(7):
        a = k * 2 * math.pi / 7 + 0.4 * i
        x, z = math.sin(a) * r * 0.95, math.cos(a) * rz * 0.95
        ops.append(('U', ('cap', (x * 0.9, cy - 0.15 * ry, z * 0.9), (x * 1.1, 0.12, z * 1.1), 0.08 * s + 0.05), c["s"]))
    fz = -rz * 0.9
    oy = cy + 0.15 * ry
    olhos_pts = []
    if f["olhos"] in ("brasa", "buraco"):
        olhos_pts = [((sx * 0.3 * r, oy, fz), (0.15 * s + 0.05, 0.2 * s + 0.06, 0.25 * s + 0.1)) for sx in (-1, 1)]
    elif f["olhos"] == "ciclope":
        olhos_pts = [((0, oy, fz), (0.3 * s + 0.05, 0.3 * s + 0.05, 0.3 * s + 0.1))]
    elif f["olhos"] == "muitos":
        olhos_pts = [((ox * r, oy + oyy * ry, fz * (1 - 0.15 * abs(ox))), (0.08 * s + 0.04, 0.09 * s + 0.04, 0.2 * s)) for ox, oyy in ((-0.45, 0.25), (0.4, 0.3), (0.0, 0.55), (-0.15, -0.05), (0.6, -0.05), (-0.65, -0.1))]
    boca = ((0.05 * r, cy - 0.32 * ry, fz), (0.45 * r, 0.07 * s + 0.05, 0.3 * s + 0.1))
    for cc_, rr in olhos_pts + [boca]:
        ops.append(('C', ('ell', cc_, rr), None))
    corpo = construir("Corpo", None, VS, (0, 0, 0), ops)
    ilhas_ruido = corpo.limpar_soltos()  # ilhas do ruido de superficie nao sao desenho; o resto da auditoria e sobre o que sobra
    P = corpo.P; vazio = np.zeros(len(P), bool)
    def perto(cc_, rr):
        return (((P - np.array(cc_)) / (np.array(rr) + 0.12)) ** 2).sum(1) <= 1
    for cc_, rr in olhos_pts + [boca]:
        vazio |= perto(cc_, rr)
    corpo.pintar(vazio, K["buraco"])
    if f["olhos"] in ("brasa", "ciclope", "muitos"):
        for cc_, rr in olhos_pts:
            pup = (((P - np.array(cc_) - np.array([0, 0, rr[2] * 0.75])) ** 2).sum(1) <= (0.06 * s + 0.07) ** 2)
            corpo.unir(pup, K["olho_verm"] if f["olhos"] != "muitos" else K["brilho_laranja"])
    for k in (-3, -1, 1, 3):
        x = boca[0][0] + k * 0.12 * r
        y0 = boca[0][1] + boca[1][1] + 0.1; y1 = boca[0][1] - 0.03 - 0.05 * s * (k % 2)
        dente = (np.abs(P[:, 0] - x) < 0.06) & (P[:, 1] < y0) & (P[:, 1] > y1) & (P[:, 2] > fz - 0.02) & (P[:, 2] < fz + 0.3)
        corpo.unir(dente, K["osso_unha"])
    pecas = {"Corpo": corpo}
    d = f["dentro"]; ops = []; top = cy + ry
    if d == "cranio" and f["olhos"] == "nenhum":
        # o cranio engolido E o rosto: aflora pela frente
        cr = np.array([0, cy + 0.1 * ry, fz + 0.15 * s]); rr = 0.42 * s
        ops = [('U', ('ell', cr, (rr * 0.85, rr, rr * 0.9)), K["osso"]), ('U', ('ell', cr + (0, -rr * 0.6, -rr * 0.25), (rr * 0.6, rr * 0.35, rr * 0.6)), K["osso_s"])]
        for sx in (-1, 1):
            ops.append(('C', ('ell', cr + (sx * rr * 0.38, 0.05 * rr, -rr * 0.8), (rr * 0.26, rr * 0.3, rr * 0.45)), None))
        ops.append(('C', ('ell', cr + (0, -rr * 0.35, -rr * 0.85), (rr * 0.12, rr * 0.15, rr * 0.3)), None))
    elif d == "cranio":
        cr = np.array([0.4 * r, top - 0.25 * ry, 0.2 * rz]); rr = 0.36 * s
        ops = [('U', ('ell', cr, (rr * 0.85, rr, rr)), K["osso"]), ('U', ('ell', cr + (0, -rr * 0.5, -rr * 0.35), (rr * 0.6, rr * 0.4, rr * 0.55)), K["osso_s"])]
        for sx in (-1, 1):
            ops.append(('C', ('ell', cr + (sx * rr * 0.38, 0, -rr * 0.8), (rr * 0.25, rr * 0.28, rr * 0.4)), None))
    elif d == "dedos":
        for k, (x, z, inc) in enumerate(((0.35, 0.25, 0.3), (-0.4, 0.3, -0.35), (0.0, 0.45, 0.05))):
            b = np.array([x * r, top - 0.35 * ry, z * rz]); m = b + np.array([inc * 0.5, 0.5 * s + 0.1, 0.1]); e = m + np.array([inc * 0.4 - 0.1, 0.25 * s + 0.1, -0.2])
            ops += [('U', ('cap', b, m, 0.11), K["osso"]), ('U', ('ell', m, (0.12, 0.12, 0.12)), K["osso_s"]), ('U', ('cap', m, e, 0.11, 0.09), K["osso_unha"])]
    elif d == "ossos":
        for a in (0.3, 1.9, 3.6, 5.0):
            b = np.array([math.sin(a) * 0.45 * r, top - 0.4 * ry, math.cos(a) * 0.4 * rz])
            e = b + np.array([math.sin(a) * 0.55, 0.55 * s, math.cos(a) * 0.45])
            ops += [('U', ('cap', b, e, 0.12), K["osso"]), ('U', ('ell', e, (0.17, 0.14, 0.17)), K["osso"])]
    elif d == "calice":
        b = np.array([-0.15 * r, top - 0.3 * ry, 0.15 * rz]); ax = np.array([0.35, 1.0, 0.0]); ax /= np.linalg.norm(ax)
        ops = [('U', ('cap', b, b + ax * 0.4 * s, 0.1), K["ouro_velho"]), ('U', ('cone', b + ax * 0.9 * s, b + ax * 0.4 * s, 0.32 * s), K["ouro_velho"]),
               ('C', ('ell', b + ax * 0.92 * s, (0.21 * s, 0.14 * s, 0.21 * s)), None), ('U', ('ell', b + ax * 0.85 * s, (0.2 * s, 0.1, 0.2 * s)), c["s"])]
        bo = b + ax * 0.9 * s + np.array([0.3 * s, 0, 0])
        ops.append(('U', ('cap', bo, bo + np.array([0.15, -0.6 * s, -0.05]), 0.11), c["b"]))
    nucleo = ('U', ('ell', (0, cy + 0.1 * ry, 0), (0.62 * r, 0.62 * ry, 0.62 * rz)), c["e"])
    if ops:
        ops.append(nucleo)
        pecas["Engolido"] = construir("Engolido", "Corpo", VS, (0, cy, 0), ops)
        if f["olhos"] == "nenhum":
            E = pecas["Engolido"]; EP = E.P
            for sx in (-1, 1):
                o = cr + np.array([sx * rr * 0.38, 0.05 * rr, -rr * 0.55])
                E.unir(((EP - o) ** 2).sum(1) <= (0.09 * s + 0.06) ** 2, K["alma"])
    a = f["adorno"]; ops = []
    if a == "velas":
        for k, (x, z, h) in enumerate(((0, 0, 0.6), (0.33, 0.18, 0.38), (-0.3, 0.12, 0.46), (0.1, -0.35, 0.3))):
            b = np.array([x * r, top - 0.15 - 0.3 * (x * x + z * z) * ry, z * rz])
            ops += [('U', ('cap', b - (0, 0.15, 0), b + (0, h * s, 0), 0.1 * s + 0.04), K["cera"]), ('U', ('cap', b + (0, h * s, 0), b + (0, h * s + 0.1, 0), 0.04), K["pavio"]),
                    ('U', ('ell', b + (0, h * s + 0.22, 0), (0.07, 0.12, 0.07)), K["chama"]),
                    ('U', ('cap', b + (0.1 * s, h * s * 0.8, 0), b + (0.12 * s, h * s * 0.2, -0.03), 0.05), K["cera_s"])]
    elif a == "pena":
        b = np.array([0.2 * r, top - 0.1, 0.15 * rz]); ax = np.array([0.35, 1.0, 0.25])
        ops = [('U', ('cap', b - ax * 0.1, b + ax * 1.6 * s, 0.08), K["osso_unha"])]
        for k in range(1, 9):
            p0 = b + ax * (0.19 * k * s)
            ops.append(('U', ('cap', p0, p0 + np.array([0.18, -0.08, -0.05]) * (1.2 - 0.1 * k) * s * 2.0, 0.07), K["membrana_s"]))
            ops.append(('U', ('cap', p0, p0 + np.array([-0.15, -0.08, 0.08]) * (1.2 - 0.1 * k) * s * 2.0, 0.07), K["membrana_s"]))
    elif a == "cacos":
        for k in range(9):
            ang = k * 0.7 + 0.3; alt = 0.2 + 0.7 * ((k * 5) % 9) / 9
            b = np.array([math.sin(ang) * 0.75 * r * (1 - 0.4 * alt), cy + alt * ry * 0.9, math.cos(ang) * 0.75 * rz * (1 - 0.4 * alt)])
            dirv = np.array([math.sin(ang), 0.8 + alt, math.cos(ang)]); dirv /= np.linalg.norm(dirv)
            ops.append(('U', ('cap', b - dirv * 0.15, b + dirv * (0.45 + 0.2 * (k % 3)) * s, 0.17, 0.09), [K["vidro_r"], K["vidro_a"], K["vidro_v"]][k % 3]))
    elif a == "coroa":
        R0 = 0.42 * r
        ops = [('U', ('cap', (0, top - 0.35, 0), (0, top - 0.05, 0), R0), K["ferro"]), ('C', ('cap', (0, top - 0.55, 0), (0, top + 0.3, 0), R0 - 0.2), None),
               ('C', lambda P: (P[:, 1] > top - 0.02) | (P[:, 1] < top - 0.4), None)]
        for k in range(8):
            ang = k * math.pi / 4; rr2 = R0 - 0.08
            ops.append(('U', ('cap', (math.sin(ang) * rr2, top - 0.1, math.cos(ang) * rr2), (math.sin(ang) * rr2 * 1.1, top + 0.4 + 0.15 * (k % 2), math.cos(ang) * rr2 * 1.1), 0.15, 0.08), K["ferrugem"] if k % 2 else K["ferro"]))
        ops.append(("U", ("ell", (0, top - 0.2, -R0 + 0.06), (0.14, 0.14, 0.12)), K["vidro_r"]))
    if ops:
        ops.append(nucleo)
        pecas["Adorno"] = construir("Adorno", "Corpo", VS, (0, top - 0.1, 0), ops)
    return dict(nome=f["nome"], ficha=f, pecas=pecas, cy=cy, s=s)

def pose(mon, clipe, t):
    s = mon["s"]; w = 2 * math.pi; L = {}
    if clipe == "parado":
        q = 0.05 * math.sin(w * t / 1.4)
        Sc = np.diag([1 + q, 1 - q, 1 + q]); d = np.zeros(3)
        L["Adorno"] = rot_eixo(Z, 0.06 * math.sin(w * (t - 0.2) / 1.4))
        L["Engolido"] = rot_eixo(Y, 0.3 * math.sin(w * t / 2.8))
    elif clipe == "mover":
        dur = 0.9; f = (t % dur) / dur
        if f < 0.25:      # antecipa
            u = f / 0.25; sq = 0.25 * math.sin(math.pi * u * 0.5); h = 0
        elif f < 0.75:    # no ar
            u = (f - 0.25) / 0.5; sq = -0.2 * math.sin(math.pi * u) ; h = 1.1 * s * 4 * u * (1 - u)
        else:             # aterrissa
            u = (f - 0.75) / 0.25; sq = 0.3 * math.sin(math.pi * u) * (1 - u) ; h = 0
        Sc = np.diag([1 + sq * 0.7, 1 - sq, 1 + sq * 0.7]); d = np.array([0, h, -1.2 * s * f])
        L["Adorno"] = rot_eixo(X, -0.25 * sq * 3)
        L["Engolido"] = rot_eixo(X, 0.2 * sq * 3)
    elif clipe == "morte":
        dur = 1.2; f = min(t / dur, 1.0)
        tr = 0.06 * math.sin(t * 60) * (f < 0.25)
        u = 0 if f < 0.25 else (f - 0.25) / 0.75; u = u * u * (3 - 2 * u)
        Sc = np.diag([1 + 0.6 * u + tr, max(0.08, 1 - 0.92 * u), 1 + 0.6 * u - tr]); d = np.zeros(3)
        L["Adorno"] = rot_eixo(Z, 1.2 * u) ; L["Engolido"] = rot_eixo(X, -0.6 * u)
    else:
        dur = 1.0; f = (t % dur) / dur
        inf = math.sin(math.pi * min(f / 0.45, 1)) if f < 0.45 else 0
        bote = math.sin(math.pi * (f - 0.45) / 0.3) if 0.45 <= f < 0.75 else 0
        Sc = np.diag([1 + 0.12 * inf - 0.15 * bote, 1 + 0.18 * inf - 0.25 * bote, 1 + 0.12 * inf + 0.45 * bote])
        d = np.array([0, 0, -0.8 * s * bote])
        L["Adorno"] = rot_eixo(X, 0.35 * bote - 0.1 * inf)
        L["Engolido"] = rot_eixo(X, -0.3 * bote)
    R = rot_eixo(X, -0.12 * (clipe == "ataque") * (Sc[2, 2] - 1)) @ Sc
    return B.montar(mon, (R, d), L)

def auditoria(mon):
    rel = {}
    for n, p in mon["pecas"].items():
        antes = p.n(); rest = p.limpar_soltos(); rest = antes - p.n() if not isinstance(rest, (int, np.integer)) else rest
        rel[n] = dict(voxels=p.n(), soltos=rest, tris=2 * len(malha_gulosa(p.g)))
    mon["faces"] = {n: faces(p) for n, p in mon["pecas"].items()}
    cont = np.zeros(len(RGB))
    for fc in mon["faces"].values():
        cont += np.bincount(fc["cor"], minlength=len(RGB))
    em = np.isin(np.arange(len(RGB)), list(EMIS)); lum = RGB @ np.array([0.2126, 0.7152, 0.0722]); tot = cont.sum()
    # juntas: filhos tem que encostar no corpo
    junta = {}
    for n, p in mon["pecas"].items():
        if p.pai:
            q = mon["pecas"][p.pai]
            A = set(map(tuple, np.round(p.P[p.solido()] / VS).astype(int))); Bc = set(map(tuple, np.round(q.P[q.solido()] / VS).astype(int)))
            junta[n] = len(A & Bc)
    v = dict(escuro=round(100 * cont[(lum < 0.2) & ~em].sum() / tot, 1), brilho=round(100 * cont[em].sum() / tot, 2))
    regras = [("Nenhum voxel solto", all(r["soltos"] == 0 for r in rel.values())),
              ("Adorno e engolido cravados no corpo (8+ voxels)", all(k >= 8 for k in junta.values())),
              ("Malha abaixo de 2.500 triangulos por stud de tamanho", sum(r["tris"] for r in rel.values()) <= 2500 * max(1.0, mon["s"] * 1.6)),
              ("Brilho abaixo de 4%", v["brilho"] < 4)]
    return dict(pecas=rel, juntas=junta, valores=v, regras=[(r, ok) for r, ok in regras])

if __name__ == "__main__":
    mons = [slime(i) for i in range(len(FICHAS))]
    res = {}
    for m in mons:
        a = auditoria(m); res[m["nome"]] = a
        print(m["nome"], m["s"], {n: (r["voxels"], r["tris"]) for n, r in a["pecas"].items()}, a["juntas"], a["valores"], [r for r, ok in a["regras"] if not ok])
    json.dump(res, open(os.path.join(OUT, "slimes_auditoria.json"), "w"), indent=1, ensure_ascii=False, default=str)
    # galeria 4x2 com escala comum
    W, H = 300, 300
    gal = Image.new("RGB", (4 * W, 2 * H))
    for k, m in enumerate(mons):
        T = pose(m, "parado", 0.0)
        it = [(m["faces"][n], *T[n]) for n in m["pecas"]]
        cam = camera_orto((0.55, -0.3, 0.78), Y, (0, 1.2, 0), 54, W, H)
        gal.paste(render(it, cam, RGB, EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.5, ambiente=0.5), ((k % 4) * W, (k // 4) * H))
    gal.save(os.path.join(OUT, "slimes_galeria.png"))
    # animacao: os 8 lado a lado em fila, clipes parado -> mover -> ataque
    fr = []
    xs = np.cumsum([0] + [m["s"] * 2.2 + 0.4 for m in mons[:-1]]); xs = xs - (xs[-1] + mons[-1]["s"] * 1.1) / 2
    cam = camera_orto((-0.3, -0.35, 0.89), Y, (0, 1.3, -0.6), 40, 1200, 360)
    for clipe, dur, n in (("parado", 1.4, 14), ("mover", 0.9, 12), ("ataque", 1.0, 12)):
        for k in range(n):
            t = k / n * dur; it = []
            for m, x in zip(mons, xs):
                T = pose(m, clipe, t)
                dx = np.array([x + m["s"] * 1.1, 0, 0])
                if clipe == "mover":
                    dx = dx + np.array([0, 0, 1.2 * m["s"] * ((t % 0.9) / 0.9)])
                it += [(m["faces"][nn], T[nn][0], T[nn][1] + dx) for nn in m["pecas"]]
            fr.append(render(it, cam, RGB, EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.5, ambiente=0.5))
    clipes = (("parado", 1.4, 14), ("mover", 0.9, 12), ("ataque", 1.0, 12), ("morte", 1.6, 16))
    W2, H2 = 300, 260; fr2 = []
    for clipe, dur, n in clipes:
        for k in range(n):
            t = k / n * dur; tela = Image.new("RGB", (4 * W2, 2 * H2))
            for j, m in enumerate(mons):
                T = pose(m, clipe, t)
                if clipe == "mover":
                    T = {nn: (R_, tt + np.array([0, 0, 1.2 * m["s"] * ((t % 0.9) / 0.9)])) for nn, (R_, tt) in T.items()}
                it = [(m["faces"][nn], *T[nn]) for nn in m["pecas"]]
                cam = camera_orto((-0.45, -0.3, 0.84), Y, (0, 1.0 * m["s"] + 0.3, 0), 62 / max(0.75, m["s"] ** 0.75), W2, H2)
                tela.paste(render(it, cam, RGB, EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.5, ambiente=0.5), ((j % 4) * W2, (j // 4) * H2))
            fr2.append(tela)
    fr2[0].save(os.path.join(OUT, "slimes_grade.webp"), save_all=True, append_images=fr2[1:], duration=75, loop=0, quality=82)
    fr[0].save(os.path.join(OUT, "slimes_animacoes.webp"), save_all=True, append_images=fr[1:], duration=75, loop=0, quality=85)
