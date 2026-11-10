"""Nihilis, a Hidra do Vazio: boss colossal. 7 pescoços em cadeia (5 segmentos), 7 cabeças distintas com mandíbula,
corpo com costelas de catedral, 4 patas, cauda, núcleo exposto e fragmentos de Avalon flutuando."""
import sys, os, math, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import construir, faces, render, camera_orto, rot_eixo, hex_rgb, malha_gulosa, ruido
import bestiario as B

X, Y, Z = B.X, B.Y, B.Z
OUT = B.OUT
VS_C, VS_P, VS_H = 0.25, 0.125, 0.0625   # corpo, pescoços/patas/cauda, cabeças
PAL = list(B.PAL) + [
    ("vazio_e", "0E0A1C"), ("vazio", "211641"), ("vazio_s", "36245E"), ("vazio_c", "5A4390"),
    ("fenda", "B58CFF"), ("fenda_b", "F2E8FF"), ("ouro_av", "B8974A"), ("ouro_av_s", "7E6430"),
    ("pedra_av", "8A8696"), ("pedra_av_s", "5C5868"), ("vit_r", "B0304A"), ("vit_a", "D99A2B"), ("vit_v", "4A2A8A"), ("vit_b", "2E6AA8"),
    ("carne_v", "4A1E52"), ("lingua", "7A2A5E"), ("pele_p", "D8C8BE"), ("pele_ps", "A39690"), ("lagrima", "6E4A9A")]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
RGB = np.array([hex_rgb(h) for h in ["000000"] + [h for _, h in PAL]])
EMIS = {K["fenda"], K["fenda_b"]}
VIT = [K["vit_r"], K["vit_a"], K["vit_v"], K["vit_b"]]

def escamas(P, h, base, alt, borda):
    """Fileiras de escamas em tijolo: borda escura de 1 voxel, 1 escama em 3 mais clara."""
    row = np.floor(P[:, 1] / h).astype(int); fy = P[:, 1] / h - row
    u = (P[:, 0] + 0.6 * P[:, 2]) / h + 0.5 * (row % 2); cu = np.floor(u).astype(int); fx = u - cu
    return np.where((fy < 0.26) | (fx < 0.2), borda, np.where((cu + row) % 3 == 0, alt, base))

def pele(c0, c1, c2, seed, fq=2.0, fenda=0.0, h=0.5):
    liso = c2 in (K["osso"], K["pele_p"], K["pedra_av"])
    def f(P):
        if liso:
            return np.where(ruido(P, fq * 0.45, seed=seed) < 0.3, c1, c2)
        return escamas(P, h, c1, c2, c0)
    return f

def cor_tubo(a, b, ra, h, dorso, ventre, fenda=False):
    """Pescoco/cauda continuos: aneis de escamas com numero inteiro de escamas em volta (sem emenda na volta),
    aneis alinhados nas juntas e uma coleira escura nas pontas, para a junta girar sem emenda de textura."""
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.linalg.norm(b - a); e = (b - a) / L
    nr = max(2, int(round(L / h))); hh = L / nr                       # aneis cabem exatos no segmento
    na = max(6, 3 * int(round(2 * math.pi * ra / h / 3)))              # escamas em volta, multiplo de 3
    side = np.cross(e, Y); side = X if np.linalg.norm(side) < 1e-6 else side / np.linalg.norm(side); up = np.cross(side, e)
    colar = dorso[2]
    def f(P):
        sd = (P - a) @ e; Q = a + np.clip(sd, 0, L)[:, None] * e; r = P - Q
        phi = np.arctan2(r @ side, r @ up)
        ring = np.floor(np.clip(sd, 0, L - 1e-6) / hh).astype(int); fy = np.clip(sd, 0, L) / hh - ring
        u = phi / (2 * math.pi) * na + 0.5 * (ring % 2); cu = np.floor(u).astype(int); fx = u - cu
        col = np.where((fy < 0.25) | (fx < 0.2), dorso[2], np.where((cu + ring) % 3 == 0, dorso[1], dorso[0]))
        col = np.where(np.abs(phi) > 2.25, np.where(fy < 0.25, ventre[1], ventre[0]), col)
        if fenda:
            col = np.where((np.abs(np.abs(phi) - 2.05) < 0.14) & (ring % 2 == 0) & (fy > 0.3), K["fenda"], col)
        return np.where((sd < 0.45 * hh) | (sd > L - 0.45 * hh), colar, col)
    return f

def corpo_cor(P):
    col = escamas(P, 1.0, K["vazio"], K["vazio_s"], K["vazio_e"])
    col = np.where(P[:, 1] > 4.6, escamas(P, 1.0, K["vazio_s"], K["vazio_c"], K["vazio"]), col)
    col = np.where(P[:, 1] < 2.3, np.where((P[:, 2] % 1.0) < 0.25, K["vazio_e"], K["vazio_c"]), col)
    return np.where(np.abs(ruido(P, 0.45, seed=3) - 0.5) < 0.02, K["fenda"], col)

def basis(f):
    f = np.asarray(f, float); f = f / np.linalg.norm(f)
    u = Y - (Y @ f) * f; u /= np.linalg.norm(u)
    return np.stack([np.cross(u, f), u, f], 1)

# ---------------- pescoços ----------------
# nome, x_raiz, z_raiz, spread, L, H, tipo, hs, raio
# nome, x_raiz, z_raiz, alvo da cabeca (x,y,z), tipo, hs, raio na raiz
NECKS = [("Rei", 0.0, -0.4, (0.0, 15.3, -6.5), "rei", 1.95, 0.98), ("Osso", -3.3, -3.0, (-9.8, 6.8, -7.4), "osso", 1.4, 0.74),
         ("Vitral", -1.1, -3.0, (-5.0, 9.0, -9.4), "vitral", 1.43, 0.7), ("Funil", 1.1, -3.0, (5.0, 9.2, -9.4), "funil", 1.56, 0.74),
         ("Ferrao", 3.3, -3.0, (9.8, 6.6, -7.4), "ferrao", 1.23, 0.62), ("Olhos", -2.3, -0.5, (-7.5, 13.4, -3.6), "olhos", 1.56, 0.76),
         ("Costurada", 2.3, -0.5, (7.2, 12.8, -3.4), "costurada", 1.04, 0.52)]
NSEG = 5

def superficie_y(x, z):
    a = 3.1 + 2.5 * math.sqrt(max(0, 1 - (x / 4.2) ** 2 - (z / 5.0) ** 2))
    b = 4.2 + 1.8 * math.sqrt(max(0, 1 - (x / 3.4) ** 2 - ((z + 2.2) / 2.2) ** 2)) if abs(x) < 3.4 and abs(z + 2.2) < 2.2 else 0
    return max(a, b)

def vs_cabeca(hs):
    return 0.0625 * max(1.0, hs / 1.25)

def juntas_pescoco(n):
    nome, x, z, E, tipo, hs, rk = n
    P0 = np.array([x, superficie_y(x, z) - 0.6, z]); E = np.array(E, float)
    sg = 0.0 if abs(E[0]) < 0.5 else math.copysign(1, E[0] - x)
    dirE = np.array([0.25 * sg, -0.38, -0.9]); dirE /= np.linalg.norm(dirE)
    dist = np.linalg.norm(E - P0)
    P1 = P0 + np.array([(E[0] - x) * 0.2, max(3.0, (E[1] - P0[1]) * 0.9 + 1.5), 0.0])
    P2 = E - dirE * 0.38 * dist
    pts = []
    for j in range(NSEG + 1):
        u = j / NSEG
        pts.append((1 - u) ** 3 * P0 + 3 * (1 - u) ** 2 * u * P1 + 3 * (1 - u) * u ** 2 * P2 + u ** 3 * E)
    return pts, [rk * (1 - 0.38 * j / NSEG) for j in range(NSEG + 1)]

def pescoco_pecas(k, n):
    nome = n[0]; pts, rs = juntas_pescoco(n); pecas = {}; ant = "Corpo"
    for j in range(1, NSEG + 1):
        a, b = pts[j - 1], pts[j]; ra, rb = rs[j - 1], rs[j]
        eixo = b - a; ln2 = float(eixo @ eixo)
        cor = cor_tubo(a, b, ra, 0.5, (K["vazio"], K["vazio_s"], K["vazio_e"]), (K["vazio_c"], K["vazio_e"]), fenda=True)
        ops = [('U', ('cap', a, b, ra, rb), cor), ('U', ('ell', a, (ra * 1.02,) * 3), cor), ('U', ('ell', b, (rb * 1.1,) * 3), cor)]
        for q in (0.25, 0.7):  # crista dorsal
            c = a + eixo * q; rr = ra + (rb - ra) * q
            ops.append(('U', ('cone', c + Y * rr * 0.8, c + Y * (rr + 0.38), 0.17), K["vazio_c"]))
        nm = f"P{k}_{j}"
        pecas[nm] = construir(nm, ant, VS_P, a, ops); pecas[nm].rj = ra; ant = nm
    return pecas, pts, rs

# ---------------- cabeças ----------------
def cabeca(k, n, pts, rs):
    nome, x, z, E_, tipo, hs, rk = n
    vsh = vs_cabeca(hs)
    o = pts[-1]; f = pts[-1] - pts[-2]; B_ = basis(f)
    W = lambda p: o + B_ @ (np.asarray(p, float) * hs)
    Rr = lambda r: np.asarray(r, float) * hs
    ell = lambda c, r: ('ell', W(c), Rr(r), B_)
    cap = lambda a, b, ra, rb=None: ('cap', W(a), W(b), max(ra * hs, 0.85 * vsh), None if rb is None else max(rb * hs, 0.6 * vsh))
    hinge = (0.0, -0.2, 0.75)
    pupilas, brilhos, orbs = [], [], []
    def orb(c, r): orbs.append((W(c), Rr(r), B_))
    ouro, osso_ = K["ouro_av"], K["osso"]
    sk = pele(K["vazio_e"], K["vazio_s"], K["vazio_c"], 50 + k, 3.0, 0.015)
    dentes = K["osso_unha"]
    oc, om = [], []   # ops da cabeça, da mandíbula
    # base comum: bola do pescoço
    oc.append(ell((0, 0, 0.15), (0.62, 0.6, 0.6)))
    if tipo in ("rei", "osso", "vitral", "costurada"):
        cc = {"rei": sk, "osso": pele(K["osso_e"], K["osso_s"], K["osso"], 60), "vitral": sk, "costurada": pele(K["pele_ps"], K["pele_p"], K["pele_p"], 61, 3.0)}[tipo]
        cs = 1.0 if tipo != "costurada" else 0.8
        oc = [('U', oc[0], cc), ('U', ell((0, 0.1, 0.95), (0.78 * cs, 0.66 * cs, 1.0)), cc)]
        sn = 1.0 if tipo != "costurada" else 0.3
        if tipo == "osso": sn = 1.25
        oc.append(('U', cap((0, 0.02, 1.5), (0, -0.02, 1.5 + 1.2 * sn), 0.52 * (1 if tipo != "costurada" else 0.7), 0.36), cc))
        for sx in (-1, 1):
            oc.append(('U', cap((sx * 0.2, 0.55, 1.4), (sx * 0.55, 0.45, 0.95), 0.14), cc))
            er = {"osso": 1.45, "costurada": 1.3}.get(tipo, 1.0)
            oc.append(('C', ell((sx * 0.43, 0.3, 1.35), (0.17 * er, 0.2 * er, 0.22)), None)); orb((sx * 0.43, 0.3, 1.3), (0.22 * er, 0.25 * er, 0.27))
            pupilas.append((W((sx * 0.43, 0.3, 1.2)), 0.1 * hs))
            if tipo != "costurada":
                oc.append(('C', ell((sx * 0.15, 0.05, 1.3 + 1.2 * sn), (0.06, 0.06, 0.08)), None))
            om.append(('U', ell((sx * 0.45, -0.2, 0.75), (0.2, 0.2, 0.2)), cc)); oc.append(('U', ell((sx * 0.45, -0.2, 0.75), (0.2, 0.2, 0.2)), cc))
        # dentes de cima
        if tipo != "costurada":
            for i in range(5):
                zz = 1.7 + 0.22 * i * sn
                for sx in (-1, 1):
                    oc.append(('U', cap((sx * (0.38 - 0.02 * i), -0.2, zz), (sx * (0.38 - 0.02 * i), -0.62 - 0.05 * (i % 2), zz), 0.075), dentes))
        # mandibula
        for sx in (-1, 1):
            om.append(('U', cap((sx * 0.42, -0.22, 0.75), (sx * 0.3, -0.28, 1.5 + 0.9 * sn), 0.17), cc))
            if tipo != "costurada":
                for i in range(4):
                    zz = 1.4 + 0.22 * i * sn + 0.1
                    om.append(('U', cap((sx * (0.34 - 0.02 * i), -0.25, zz), (sx * (0.34 - 0.02 * i), 0.12 + 0.04 * (i % 2), zz), 0.075), dentes))
        om.append(('U', cap((-0.3, -0.28, 1.5 + 0.9 * sn), (0.3, -0.28, 1.5 + 0.9 * sn), 0.17), cc))
        om.append(('U', ell((0, -0.15, 1.2 + 0.4 * sn), (0.2, 0.07, 0.5 * sn + 0.2)), K["lingua"]))
        brilhos.append((W((0, -0.3, 1.1)), 0.24 * hs))
        if tipo == "rei":
            for i in range(5):
                a_ = -1.0 + 0.5 * i; alt = 1.7 - 0.25 * abs(i - 2) - (0.8 if i == 4 else 0)
                b0 = (math.sin(a_) * 0.7, 0.5 + 0.12 * math.cos(a_), 0.5); tp = (math.sin(a_) * 1.1, alt, 0.15)
                oc.append(('U', cap(b0, tp, 0.17, 0.03), ouro if i != 4 else K["ouro_av_s"]))
                if i:
                    pa = (math.sin(a_ - 0.5) * 0.7, 0.5 + 0.12 * math.cos(a_ - 0.5), 0.5)
                    oc.append(('U', cap(pa, b0, 0.1), K["ouro_av_s"]))
            for sx in (-1, 1):
                for (ex, ey, ez, er) in ((0.62, 0.52, 0.9, 0.1), (0.3, 0.62, 1.2, 0.09)):
                    oc.append(('C', ell((sx * ex, ey, ez), (er, er, er * 1.2)), None)); orb((sx * ex, ey, ez), (er * 1.3, er * 1.3, er * 1.5)); pupilas.append((W((sx * ex, ey, ez + 0.05)), 0.075 * hs))
        if tipo == "osso":
            for sx in (-1, 1):
                p0, p1, p2 = (sx * 0.35, 0.6, 0.7), (sx * 0.8, 1.5, 0.3), (sx * 1.2, 2.5, 0.0)
                oc += [('U', cap(p0, p1, 0.16, 0.12), osso_), ('U', cap(p1, p2, 0.12, 0.07), osso_),
                       ('U', cap(p1, (sx * 0.55, 2.4, 0.8), 0.1, 0.05), osso_), ('U', cap(p2, (sx * 0.9, 3.2, 0.3), 0.09, 0.05), osso_),
                       ('U', cap(p2, (sx * 1.6, 3.0, -0.2), 0.09, 0.05), osso_)]
        if tipo == "vitral":
            oc.append(('C', ell((0, 0.5, 1.55), (0.3, 0.27, 0.25)), None)); orb((0, 0.5, 1.5), (0.38, 0.34, 0.3)); pupilas.append((W((0, 0.5, 1.4)), 0.16 * hs))
            for i in range(9):
                a_ = -2.4 + 0.6 * i; dd = (math.sin(a_), math.cos(a_))
                tpd = 1.1 + 0.25 * (i % 3)
                oc.append(('U', cap((dd[0] * 0.55, dd[1] * 0.5 + 0.1, 0.4), (dd[0] * tpd, dd[1] * tpd + 0.1, -0.5), 0.25, 0.04), VIT[i % 4]))
        if tipo == "costurada":
            oc.append(('U', ell((0, 0.0, 1.62), (0.11, 0.2, 0.2)), cc))                       # nariz
            for sx in (-1, 1):
                oc.append(('U', ell((sx * 0.38, -0.12, 1.45), (0.2, 0.16, 0.2)), cc))         # macas do rosto
            oc.append(('C', ell((0, -0.3, 1.78), (0.46, 0.035, 0.12)), None)); orb((0, -0.3, 1.74), (0.5, 0.07, 0.16))   # boca selada
            for i in range(7):
                xx = -0.4 + 0.133 * i
                oc.append(('U', cap((xx, -0.1, 1.74), (xx, -0.5, 1.76), 0.055), K["buraco"]))
            for sx in (-1, 1):
                oc.append(('U', cap((sx * 0.43, 0.05, 1.6), (sx * 0.46, -0.55, 1.5), 0.05), K["lagrima"]))
    elif tipo == "funil":
        cc = pele(K["vazio_e"], K["vazio_s"], K["vazio_c"], 70, 3.0, 0.015)
        oc = [('U', ell((0, 0, 0.15), (0.62, 0.6, 0.6)), cc), ('U', cap((0, 0, 0.3), (0, 0, 2.0), 0.64, 0.84), cc),
              ('C', cap((0, 0, 1.7), (0, 0, 3.2), 0.56), None)]
        for i in range(14):
            a_ = i * 2 * math.pi / 14
            oc.append(('U', cap((0.84 * math.cos(a_), 0.84 * math.sin(a_), 2.0), (0.84 * math.cos(a_ + 0.45), 0.84 * math.sin(a_ + 0.45), 2.0), 0.14), K["lingua"]))
            for (rr, zz, ln) in ((0.55, 1.8, 0.4), (0.5, 2.05, 0.35)):
                oc.append(('U', cap((rr * math.cos(a_), rr * math.sin(a_), zz), (0.45 * rr * math.cos(a_), 0.45 * rr * math.sin(a_), zz + ln), 0.075, 0.04), dentes))
        brilhos.append((W((0, 0, 1.3)), 0.36 * hs))
        for sx in (-1, 1):
            for yy in (0.15, 0.35):
                oc.append(('C', ell((sx * 0.62, yy, 0.9), (0.07, 0.07, 0.09)), None))
        om = [('U', cap((0, 0, 0.9), (0, 0, 2.4), 0.16), K["osso_e"]), ('U', ell((0, 0, 1.0), (0.36, 0.36, 0.3)), K["osso_e"])]
        for i in range(6):
            a_ = i * math.pi / 3
            om.append(('U', cap((0, 0, 1.9), (0.44 * math.cos(a_), 0.44 * math.sin(a_), 2.0), 0.1, 0.075), K["osso_s"]))
            om.append(('U', cap((0.44 * math.cos(a_), 0.44 * math.sin(a_), 2.0), (0.4 * math.cos(a_), 0.4 * math.sin(a_), 2.45), 0.085, 0.04), dentes))
        hinge = (0, 0, 1.0)
    elif tipo == "ferrao":
        cc = pele(K["vazio_e"], K["vazio_s"], K["vazio_c"], 80, 3.0, 0.015)
        oc = [('U', ell((0, 0, 0.15), (0.62, 0.6, 0.6)), cc), ('U', ell((0, 0.1, 0.8), (0.6, 0.55, 0.8)), cc),
              ('U', cap((0, 0.08, 1.2), (0, -0.05, 4.4), 0.38, 0.05), K["osso_e"])]
        for i in range(4):
            zz = 1.8 + 0.5 * i
            for sx in (-1, 1):
                oc.append(('U', cap((sx * 0.28 * (1 - 0.1 * i), -0.1, zz), (sx * 0.28 * (1 - 0.1 * i), -0.5, zz - 0.25), 0.075, 0.03), dentes))
        for sx in (-1, 1):
            oc.append(('C', ell((sx * 0.55, 0.2, 0.55), (0.14, 0.17, 0.2)), None)); orb((sx * 0.55, 0.2, 0.5), (0.19, 0.22, 0.25)); pupilas.append((W((sx * 0.56, 0.2, 0.45)), 0.1 * hs))
            oc.append(('U', cap((sx * 0.3, 0.6, 0.3), (sx * 0.5, 1.3, -0.6), 0.14, 0.04), K["osso_e"]))
            om.append(('U', ell((sx * 0.35, -0.2, 0.75), (0.2, 0.2, 0.2)), cc)); oc.append(('U', ell((sx * 0.35, -0.2, 0.75), (0.2, 0.2, 0.2)), cc))
        oc.append(('U', cap((0, 0.45, 0.4), (0, 1.2, -0.7), 0.14, 0.04), K["osso_e"]))
        om += [('U', cap((-0.3, -0.2, 0.75), (0.0, -0.3, 3.6), 0.22, 0.04), K["osso_s"]), ('U', cap((0.3, -0.2, 0.75), (0.0, -0.3, 3.6), 0.22, 0.04), K["osso_s"])]
        for i in range(4):
            om.append(('U', cap((0, -0.28, 1.6 + 0.55 * i), (0, 0.15, 1.35 + 0.55 * i), 0.07, 0.03), dentes))
        brilhos.append((W((0, -0.25, 1.3)), 0.2 * hs))
    elif tipo == "olhos":
        cc = pele(K["vazio_e"], K["vazio"], K["vazio_s"], 90, 3.0, 0.012)
        oc = [('U', ell((0, 0, 0.15), (0.62, 0.6, 0.6)), cc), ('U', ell((0, 0.1, 0.95), (1.0, 0.95, 1.0)), cc)]
        for i in range(11):
            th_ = i * 2.4; rr = math.sqrt((i + 0.5) / 11) * 0.82
            d = np.array([rr * math.cos(th_), rr * math.sin(th_) + 0.12, math.sqrt(max(1 - rr * rr, 0.05))]); d /= np.linalg.norm(d)
            er = 0.13 + 0.12 * (i % 3) / 2
            cen = np.array([0, 0.1, 0.95]) + d * np.array([1.0, 0.95, 1.0])
            oc.append(('C', ell(cen * 0.99, (er, er, er)), None)); orb(cen * 0.97, (er * 1.3,) * 3); pupilas.append((W(cen * 0.88), er * 0.62 * hs))
        oc.append(('C', ell((0, -0.5, 1.6), (0.46, 0.07, 0.3)), None))
        for i in range(7):
            xx = -0.36 + 0.12 * i
            oc.append(('U', cap((xx, -0.45, 1.55), (xx, -0.15, 1.6), 0.07, 0.03), dentes))
        for sx in (-1, 1):
            om.append(('U', ell((sx * 0.45, -0.3, 0.8), (0.2, 0.2, 0.2)), cc)); oc.append(('U', ell((sx * 0.45, -0.3, 0.8), (0.2, 0.2, 0.2)), cc))
            om.append(('U', cap((sx * 0.42, -0.32, 0.8), (sx * 0.34, -0.55, 1.65), 0.17), cc))
        om.append(('U', cap((-0.34, -0.55, 1.65), (0.34, -0.55, 1.65), 0.17), cc))
        for i in range(6):
            xx = -0.28 + 0.112 * i
            om.append(('U', cap((xx, -0.5, 1.65), (xx, -0.18, 1.6), 0.07, 0.03), dentes))
        hinge = (0, -0.3, 0.8)
        brilhos.append((W((0, -0.4, 1.3)), 0.18 * hs))
    return dict(oc=oc, om=om, o=o, B=B_, hs=hs, hinge=W(hinge), pupilas=pupilas, brilhos=brilhos, tipo=tipo, orbs=orbs)

def montar_cabeca(k, n, pts, rs, pai):
    h = cabeca(k, n, pts, rs)
    vsh = vs_cabeca(n[5])
    pc = construir(f"C{k}", pai, vsh, h["o"], h["oc"])
    P = pc.P
    for c, r, Bm in h["orbs"]:
        pc.pintar(((((P - c) @ Bm) / r) ** 2).sum(1) <= 1.0, K["buraco"])
    for c, r in h["pupilas"]:
        pc.unir(((P - c) ** 2).sum(1) <= r * r, K["fenda_b"])
    for c, r in h["brilhos"]:
        pc.unir((((P - c) ** 2).sum(1) <= r * r) & (pc.g.reshape(-1) > 0) | (((P - c) ** 2).sum(1) <= (r * 0.6) ** 2), K["fenda"])
    pm = construir(f"M{k}", f"C{k}", vsh, h["hinge"], h["om"])
    pc.rj = pm.rj = 0.42 * h["hs"]
    return pc, pm, h

# ---------------- corpo, patas, cauda, núcleo, fragmentos ----------------
def corpo():
    ops = [('U', ('ell', (0, 3.1, 0), (4.2, 2.5, 5.0)), corpo_cor), ('U', ('ell', (0, 4.2, -2.2), (3.4, 1.8, 2.2)), corpo_cor),
           ('U', ('ell', (0, 2.6, 3.9), (2.9, 1.7, 2.3)), corpo_cor)]
    ops.append(('C', ('ell', (0, 1.9, -3.5), (1.7, 1.15, 1.5)), None))
    ops.append(('C', lambda P: P[:, 1] < 0.55 + 0.0 * P[:, 0], None))
    for zc, hh, ww in ((1.0, 3.6, 3.2), (2.2, 3.4, 3.0), (3.4, 3.0, 2.7), (4.4, 2.5, 2.2)):   # costelas de catedral (arco gótico)
        ys = superficie_y(0, zc)
        for sx in (-1, 1):
            arco = []
            for t in np.linspace(0, 1, 10):
                xx = sx * ww * (1 - t ** 1.6)
                yy = ys - 0.4 + 2.2 * math.sin(t * math.pi * 0.5) ** 0.8 * (1.1 if zc < 3 else 0.9)
                arco.append((xx * 0.9, min(yy, ys + 2.0), zc))
            for a, b in zip(arco[:-1], arco[1:]):
                ops.append(('U', ('cap', a, b, 0.3), K["pedra_av"] if zc < 3 else K["pedra_av_s"]))
    for x in (-1.3, -0.45, 0.45, 1.3):   # presas da gaiola do nucleo
        ops.append(('U', ('cap', (x, 0.75, -4.1), (x * 0.6, 3.2, -4.55), 0.3, 0.2), K["osso_e"]))
    pc = construir("Corpo", None, VS_C, (0, 3.1, 0), ops)
    P = pc.P
    for d in ((-0.7, 0.62, -0.7), (0.7, 0.62, -0.7), (-0.95, 0.2, -0.3), (0.95, 0.2, -0.3), (-0.5, 0.35, 0.85), (0.55, 0.3, 0.8), (-0.9, 0.1, 0.45), (0.9, 0.05, 0.5)):
        dd = np.array(d); dd /= np.linalg.norm(dd)
        c = np.array([0, 3.1, 0]) + dd * np.array([4.2, 2.5, 5.0]) * 0.97
        pc.unir((((P - c) ** 2).sum(1) <= 0.45 ** 2) & (pc.g.reshape(-1) > 0), K["fenda_b"])
    return pc

PERNAS = [("FE", -3.8, -1.4), ("FD", 3.8, -1.4), ("TE", -3.4, 3.2), ("TD", 3.4, 3.2)]
def perna(nm, x, z):
    s = 1 if x > 0 else -1
    q = pele(K["vazio_e"], K["vazio"], K["vazio_s"], 110, 2.2, 0.02)
    quadril, joelho, pe = np.array([x, 2.8, z]), np.array([x + s * 1.1, 1.35, z]), np.array([x + s * 0.9, 0.2, z])
    cox = construir(f"Coxa_{nm}", "Corpo", VS_P, quadril, [('U', ('cap', quadril, joelho, 0.9, 0.72), q), ('U', ('ell', quadril, (0.95,) * 3), q), ('U', ('ell', joelho, (0.78,) * 3), q),
                                                      ('U', ('cap', quadril + (s * 0.5, 0.8, 0), quadril + (s * 1.0, 1.9, 0), 0.34, 0.15), K["vazio_c"])])
    ops = [('U', ('cap', joelho, pe, 0.7, 0.55), q), ('U', ('ell', joelho, (0.72,) * 3), q), ('U', ('ell', pe, (0.62, 0.45, 0.62)), q)]
    for a_ in (-0.5, 0.0, 0.5):
        tip = pe + np.array([math.sin(a_) * 1.1 + s * 0.15, -0.05, -1.3 * math.cos(a_)])
        ops.append(('U', ('cap', pe + (0, 0.05, -0.2), tip, 0.26, 0.1), K["osso_e"]))
    ops.append(('U', ('cap', pe + (0, 0.1, 0.3), pe + (s * 0.1, 0.5, 1.0), 0.2, 0.06), K["osso_e"]))
    can = construir(f"Canela_{nm}", f"Coxa_{nm}", VS_P, joelho, ops)
    cox.rj = 0.78; can.rj = 0.72
    return cox, can

def cauda():
    pts = [np.array([0, 2.4 - 0.35 * j, 4.8 + 2.6 * j]) for j in range(6)]
    rs = [0.95, 0.85, 0.72, 0.58, 0.45, 0.3]
    pecas = {}; ant = "Corpo"
    for j in range(1, 6):
        a, b = pts[j - 1], pts[j]
        ct = cor_tubo(a, b, rs[j - 1], 0.5, (K["vazio"], K["vazio_s"], K["vazio_e"]), (K["vazio_c"], K["vazio_e"]), fenda=True)
        ops = [('U', ('cap', a, b, rs[j - 1], rs[j]), ct), ('U', ('ell', a, (rs[j - 1],) * 3), ct), ('U', ('ell', b, (rs[j] * 1.1,) * 3), ct)]
        if j < 5:
            c = (a + b) / 2; ops.append(('U', ('cone', c + Y * rs[j] * 0.8, c + Y * (rs[j] + 0.5), 0.2), K["vazio_c"]))
        else:
            for dx in (-1, 0, 1):
                ops.append(('U', ('cap', b, b + np.array([dx * 0.5, 0.2 + 0.4 * (dx == 0), 1.7]), 0.34, 0.16), K["osso_s"]))
        nm = f"Cauda{j}"; pecas[nm] = construir(nm, ant, VS_P, a, ops); pecas[nm].rj = rs[j - 1]; ant = nm
    return pecas

def nucleo():
    c = np.array([0, 1.9, -3.2])
    def cor(P):
        r = np.sqrt(((P - c) ** 2).sum(1))
        return np.where(r < 0.42, K["fenda_b"], np.where(np.abs(ruido(P, 3.0, seed=2) - 0.5) < 0.08, K["fenda_b"], K["fenda"]))
    ops = [('U', ('ell', c, (1.1, 1.0, 1.0)), cor)]
    for d in ((1, 0.2, 0.6), (-1, 0.2, 0.6), (0.6, -0.8, 0.6), (-0.6, -0.8, 0.6), (0.5, 0.3, 1.2), (-0.5, 0.3, 1.2)):
        dd = np.array(d, float); dd /= np.linalg.norm(dd)
        ops.append(('U', ('cap', c, c + dd * 2.2, 0.2, 0.14), K["fenda"]))
    return construir("Nucleo", "Corpo", VS_P, c, ops)

FRAG = [("arco", (-9.0, 6.5, 3.0)), ("arco", (9.5, 7.5, 1.0)), ("arco", (-6.0, 11.0, 6.0)), ("arco", (6.0, 12.5, 4.0)),
        ("vitral", (-11.5, 4.0, 1.5)), ("vitral", (11.5, 4.5, 0.0)), ("vitral", (0.0, 13.5, 7.5)),
        ("pinaculo", (-10.5, 10.0, 4.5)), ("pinaculo", (8.5, 10.5, 5.0)), ("pedra_olho", (0.0, 8.5, 10.0))]
def fragmento(i, tipo, c):
    c = np.array(c, float); ops = []
    if tipo == "arco":
        for sx in (-1, 1):
            pts = [c + np.array([sx * 1.4 * (1 - t ** 1.5), 2.0 * math.sin(t * math.pi / 2) ** 0.8 - 1.0, 0]) for t in np.linspace(0, 1, 9)]
            for a, b in zip(pts[:-1], pts[1:]):
                ops.append(('U', ('cap', a, b, 0.3), K["pedra_av"] if i % 2 else K["pedra_av_s"]))
        ops.append(('U', ('ell', c + (0, 1.0, 0), (0.35, 0.35, 0.3)), K["ouro_av"]))
    elif tipo == "vitral":
        def cor(P, c=c):
            gx = (P[:, 0] - c[0]) / 0.5; gy = (P[:, 1] - c[1]) / 0.5 + 0.3 * np.sin(gx * 2.0)
            lead = (gx % 1 < 0.16) | (gy % 1 < 0.16)
            cell = np.array(VIT)[(np.floor(gx).astype(int) * 3 + np.floor(gy).astype(int) * 5 + i) % 4]
            return np.where(lead, K["ouro_av_s"], cell)
        ops = [('U', ('ell', c, (1.0, 1.4, 0.18)), cor)]
        ops.append(('U', ('cap', c + (-1.0, -1.3, 0), c + (-1.0, 1.3, 0), 0.14), K["ouro_av_s"])); ops.append(('U', ('cap', c + (1.0, -1.3, 0), c + (1.0, 1.3, 0), 0.14), K["ouro_av_s"]))
        ops.append(('U', ('cap', c + (-1.0, 1.3, 0), c + (1.0, 1.3, 0), 0.14), K["ouro_av_s"])); ops.append(('U', ('cap', c + (-1.0, -1.3, 0), c + (1.0, -1.3, 0), 0.14), K["ouro_av_s"]))
    elif tipo == "pinaculo":
        ops = [('U', ('cone', c + (0, -1.8, 0), c + (0, 1.9, 0), 0.7), K["pedra_av"]), ('U', ('cap', c + (0, -1.8, 0), c + (0, -1.2, 0), 0.75), K["pedra_av_s"]),
               ('U', ('cone', c + (0, 1.0, 0), c + (0.2, 2.5, 0), 0.25), K["ouro_av"])]
    else:
        ops = [('U', ('ell', c, (1.1, 0.9, 1.0)), pele(K["pedra_av_s"], K["pedra_av"], K["pedra_av"], 130, 2.5)), ('C', ('ell', c + (0, 0, -0.9), (0.4, 0.3, 0.3)), None)]
    p = construir(f"Frag{i}", "Corpo", VS_P, c, ops)
    if tipo == "pedra_olho":
        p.unir(((p.P - (c + np.array([0, 0, -0.75]))) ** 2).sum(1) <= 0.2 ** 2, K["fenda_b"])
    return p

def hidra():
    P = {"Corpo": corpo()}
    for nm, x, z in PERNAS:
        a, b = perna(nm, x, z); P[a.nome] = a; P[b.nome] = b
    P.update(cauda())
    P["Nucleo"] = nucleo()
    info = {}
    for k, n in enumerate(NECKS):
        pp, pts, rs = pescoco_pecas(k, n); P.update(pp)
        pc, pm, h = montar_cabeca(k, n, pts, rs, f"P{k}_{NSEG}")
        P[pc.nome] = pc; P[pm.nome] = pm; info[k] = dict(h=h, pts=pts, rs=rs)
    for i, (t, c) in enumerate(FRAG):
        P[f"Frag{i}"] = fragmento(i, t, c)
    return dict(nome="Nihilis", pecas=P, info=info)

if __name__ == "__main__":
    import time
    t0 = time.time(); m = hidra(); print("pecas", len(m["pecas"]), "voxels", sum(p.n() for p in m["pecas"].values()), round(time.time() - t0, 1), "s")
