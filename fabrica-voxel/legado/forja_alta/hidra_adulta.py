"""Hidra do Vazio adulta: 3 cabecas de dragao com chifres, corpo de escamas, orbe do vazio no peito preso por garras,
ataques (raio convergente, mordida dupla, pisao com onda) e VFX. Auditoria rigida por quadro."""
import sys, os, math, json, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hidra as Hd, hidra_anim as HA, bestiario as B, herois
from hidra import X, Y, Z, basis, escamas, cor_tubo
from voxforja import construir, faces, render, camera_orto, rot_eixo, hex_rgb

OUT = B.OUT
PAL = list(Hd.PAL) + [("placa", "7A68A6"), ("placa_c", "A294CC"), ("rocha", "6A6878"), ("rocha_c", "9694A6"), ("rocha_e", "434158"),
                      ("chifre", "B4B2C2"), ("chifre_c", "DAD8E4"), ("ciano", "5CE8FF"), ("breu", "05030A")]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
RGB = np.array([hex_rgb(h) for h in ["000000"] + [h for _, h in PAL]])
EMIS = {K["fenda"], K["fenda_b"], K["ciano"]}
VC, VH = 0.25, 0.125
VH_T = 0.125
DORSO = (K["vazio_s"], K["vazio_c"], K["vazio"]); VENTRE = (K["placa"], K["vazio_e"])
NSEG = 6
# raiz, alvo da cabeca, escala da cabeca, raio na raiz
NECKS = [("Centro", (0.0, 13.6, -1.2), (0.0, 31.0, -11.0), 2.6, 1.75), ("Esq", (-4.4, 11.8, -2.2), (-13.5, 22.0, -12.5), 2.2, 1.6), ("Dir", (4.4, 11.8, -2.2), (13.5, 24.5, -10.5), 2.2, 1.6)]

def esc_corpo(P):
    col = escamas(P, 1.0, K["vazio_s"], K["vazio_c"], K["vazio"])
    return np.where(P[:, 1] < 7.0, escamas(P, 1.0, K["vazio"], K["vazio_s"], K["vazio_e"]), col)

def juntas(n):
    nome, P0, E, hs, rk = n; P0 = np.array(P0, float); E = np.array(E, float)
    sg = 0.0 if abs(E[0]) < 0.5 else math.copysign(1, E[0])
    dirE = np.array([0.2 * sg, -0.42, -0.9]); dirE /= np.linalg.norm(dirE)
    dist = np.linalg.norm(E - P0)
    P1 = P0 + np.array([(E[0] - P0[0]) * 0.25, (E[1] - P0[1]) * 0.75 + 1.5, 1.0]); P2 = E - dirE * 0.36 * dist
    pts = [(1 - u) ** 3 * P0 + 3 * (1 - u) ** 2 * u * P1 + 3 * (1 - u) * u ** 2 * P2 + u ** 3 * E for u in np.linspace(0, 1, NSEG + 1)]
    return pts, [rk * (1 - 0.4 * j / NSEG) for j in range(NSEG + 1)]

def pescoco(k, n):
    pts, rs = juntas(n); pecas = {}; ant = "Corpo"
    for j in range(1, NSEG + 1):
        a, b = pts[j - 1], pts[j]; ra, rb = rs[j - 1], rs[j]; e = (b - a) / np.linalg.norm(b - a)
        ct = cor_tubo(a, b, ra, 1.0, DORSO, VENTRE)
        ops = [('U', ('cap', a, b, ra, rb), ct), ('U', ('ell', a, (ra * 1.02,) * 3), ct), ('U', ('ell', b, (rb * 1.02,) * 3), ct)]
        side = np.cross(e, Y); side /= np.linalg.norm(side); up = np.cross(side, e)
        for q in (0.3, 0.75):   # espinhos dorsais
            c = a + (b - a) * q; rr = ra + (rb - ra) * q
            ops.append(('U', ('cap', c + up * rr * 0.7, c + up * (rr + 1.4), 0.4, 0.14), K["rocha_c"] if q < 0.5 else K["rocha"]))
        nm = f"N{k}_{j}"; pecas[nm] = construir(nm, ant, VC, a, ops); pecas[nm].rj = ra; ant = nm
    return pecas, pts, rs

def cabeca(k, n, pts, pai):
    hs = n[3]; o = pts[-1]; B_ = basis(pts[-1] - pts[-2])
    W = lambda p: o + B_ @ (np.asarray(p, float) * hs)
    ell = lambda c, r: ('ell', W(c), np.asarray(r, float) * hs, B_)
    cap = lambda a, b, ra, rb=None: ('cap', W(a), W(b), max(ra * hs, 0.85 * VH), None if rb is None else max(rb * hs, 0.7 * VH))
    def cor(P):
        q = ((P - o) @ B_) / hs
        placas = np.where(((q[:, 2] * 2.6) % 1) < 0.16, K["rocha_e"], np.where(q[:, 1] > 0.38, K["rocha_c"], K["rocha"]))
        baixo = np.where(((q[:, 2] * 2.6) % 1) < 0.16, K["vazio_e"], K["vazio_s"])
        return np.where(q[:, 1] > 0.02, placas, baixo)
    def cor_m(P):
        q = ((P - o) @ B_) / hs
        return np.where(((q[:, 2] * 2.6) % 1) < 0.16, K["vazio_e"], K["vazio"])
    ch, chc, dn = K["chifre"], K["chifre_c"], K["osso_unha"]
    oc = [('U', ell((0, 0, 0.1), (0.72, 0.64, 0.62)), cor), ('U', ell((0, 0.1, 0.8), (0.66, 0.52, 0.86)), cor),
          ('U', cap((0, 0.02, 1.3), (0, -0.06, 2.7), 0.46, 0.28), cor)]
    om = []; orbs = []; pup = []
    for sx in (-1, 1):
        oc.append(('U', cap((sx * 0.16, 0.5, 1.7), (sx * 0.64, 0.46, 0.85), 0.16), K["rocha_c"]))                    # sobrancelha
        oc.append(('C', ell((sx * 0.56, 0.22, 1.25), (0.14, 0.1, 0.26)), None)); orbs.append((W((sx * 0.52, 0.22, 1.22)), np.array([0.2, 0.15, 0.32]) * hs))
        pup.append((W((sx * 0.5, 0.22, 1.28)), np.array([0.07, 0.055, 0.2]) * hs))
        oc.append(('C', ell((sx * 0.14, 0.12, 2.72), (0.06, 0.05, 0.1)), None))
        h1, h2 = (sx * 0.72, 1.05, -0.9), (sx * 0.9, 1.35, -2.3)
        oc += [('U', cap((sx * 0.36, 0.48, 0.3), h1, 0.21, 0.13), ch), ('U', cap(h1, h2, 0.13, 0.04), chc),          # chifre grande
               ('U', cap((sx * 0.6, 0.2, 0.15), (sx * 1.1, 0.5, -1.4), 0.16, 0.04), ch),                             # chifre medio
               ('U', cap((sx * 0.62, -0.12, 0.45), (sx * 1.0, -0.3, -0.8), 0.13, 0.04), ch),                         # espinho da bochecha
               ('U', cap((sx * 0.3, 0.42, 1.1), (sx * 0.42, 0.8, 0.55), 0.09, 0.04), ch)]
        for i in range(6):
            z = 1.5 + 0.2 * i; xx = sx * (0.36 - 0.025 * i); comp = 0.34 + 0.12 * (i == 5) + 0.05 * (i % 2)
            oc.append(('U', cap((xx, -0.2, z), (xx, -0.2 - comp, z), 0.062), dn))
        oc.append(('U', ell((sx * 0.45, -0.2, 0.7), (0.2, 0.2, 0.2)), cor)); om.append(('U', ell((sx * 0.45, -0.2, 0.7), (0.2, 0.2, 0.2)), cor_m))
        om.append(('U', cap((sx * 0.44, -0.26, 0.7), (sx * 0.25, -0.38, 2.45), 0.17, 0.13), cor_m))
        om.append(('U', cap((sx * 0.3, -0.42, 1.3), (sx * 0.48, -0.9, 0.7), 0.11, 0.04), ch))                         # barbela
        for i in range(5):
            z = 1.6 + 0.2 * i; xx = sx * (0.3 - 0.02 * i)
            om.append(('U', cap((xx, -0.34, z), (xx, -0.02 + 0.05 * (i % 2), z), 0.062), dn))
    for i in range(3):   # crista
        oc.append(('U', cap((0, 0.52, 0.95 - 0.45 * i), (0, 1.0 + 0.12 * i, 0.45 - 0.6 * i), 0.13, 0.04), ch))
    oc.append(('U', cap((0, 0.26, 2.35), (0, 0.62, 2.05), 0.1, 0.04), ch))
    om += [('U', cap((-0.25, -0.38, 2.45), (0.25, -0.38, 2.45), 0.15), cor_m), ('U', ell((0, -0.36, 1.6), (0.3, 0.09, 0.9)), K["vazio_e"]),
           ('U', ell((0, -0.24, 1.4), (0.18, 0.07, 0.75)), K["lingua"]), ('U', cap((0, -0.45, 2.45), (0, -0.85, 2.2), 0.1, 0.04), ch)]
    pc = construir(f"H{k}", pai, VH, o, oc); P = pc.P
    for c, r in orbs:
        pc.pintar(((((P - c) @ B_) / r) ** 2).sum(1) <= 1, K["breu"])
    for c, r in pup:
        pc.unir(((((P - c) @ B_) / r) ** 2).sum(1) <= 1, K["ciano"])
    g = W((0, -0.16, 0.95)); pc.unir((((P - g) ** 2).sum(1) <= (0.3 * hs) ** 2) & (pc.g.reshape(-1) > 0), K["fenda"])
    pm = construir(f"J{k}", f"H{k}", VH, W((0, -0.2, 0.7)), om)
    pc.rj = pm.rj = 0.42 * hs
    return pc, pm, dict(o=o, B=B_, hs=hs, boca=W((0, -0.55, 3.1)))

def corpo():
    ops = [('U', ('ell', (0, 9.5, -1.0), (5.2, 5.0, 4.6)), esc_corpo), ('U', ('ell', (0, 8.0, 2.4), (4.6, 4.2, 3.6)), esc_corpo),
           ('C', ('ell', (0, 9.0, -5.6), (2.7, 2.7, 2.5)), None)]
    P0 = None
    for a_ in (0.6, 1.57 + 0.55, 3.14 + 0.6, 4.71 + 0.55, 1.57 - 0.5, 4.71 - 0.5):   # garras que prendem o orbe
        base = np.array([3.3 * math.cos(a_), 9.0 + 3.3 * math.sin(a_), -4.4]); mid = np.array([2.9 * math.cos(a_), 9.0 + 2.9 * math.sin(a_), -6.6]); tip = np.array([1.5 * math.cos(a_), 9.0 + 1.5 * math.sin(a_), -7.3])
        ops += [('U', ('cap', base, mid, 0.55, 0.42), K["rocha"]), ('U', ('cap', mid, tip, 0.42, 0.16), K["chifre"])]
    for z, hgt in ((-2.5, 2.6), (-0.3, 3.0), (1.9, 2.6), (4.0, 2.0)):   # espinhos das costas
        y0 = 13.2 - 0.25 * (z + 1) ** 2 * 0.2
        for x in (-1.6, 1.6):
            ops.append(('U', ('cap', (x, y0 - 1.0, z), (x * 1.5, y0 + hgt, z + 1.2), 0.6, 0.16), K["rocha_c"] if z < 1 else K["rocha"]))
    for sx in (-1, 1):   # ombreiras de rocha
        ops.append(('U', ('ell', (sx * 4.6, 11.2, -1.0), (1.6, 1.3, 2.0)), K["rocha"]))
        for i in range(3):
            ops.append(('U', ('cap', (sx * 5.0, 11.6, -2.0 + 1.2 * i), (sx * 7.0, 13.4 + 0.3 * i, -1.6 + 1.3 * i), 0.5, 0.14), K["chifre"]))
    pc = construir("Corpo", None, VC, (0, 6.5, 4.0), ops); P = pc.P
    ventre = (P[:, 1] < 6.2) | ((P[:, 2] < -3.6) & (np.abs(P[:, 0]) < 3.2) & (P[:, 1] < 12.2))
    faixa = np.where(((P[:, 1] * 0.9 + P[:, 2] * 0.5) % 1.5) < 0.3, K["vazio_e"], np.where(P[:, 1] > 9, K["placa_c"], K["placa"]))
    esc = pc.g.reshape(-1); ehesc = np.isin(esc, [K["vazio"], K["vazio_s"], K["vazio_e"], K["vazio_c"]])
    pc.pintar(ventre & ehesc, faixa)
    return pc

def lombo():
    def cor(P):
        col = escamas(P, 1.0, K["vazio_s"], K["vazio_c"], K["vazio"])
        return np.where(P[:, 1] < 3.6, np.where((P[:, 2] % 1.5) < 0.3, K["vazio_e"], K["placa"]), col)
    ops = [('U', ('ell', (0, 6.6, 5.0), (4.4, 4.0, 4.2)), cor), ('U', ('ell', (0, 5.4, 9.6), (4.0, 3.5, 4.6)), cor)]
    for z, hgt in ((6.0, 1.8), (8.2, 1.5), (10.4, 1.2)):
        ops.append(('U', ('cap', (0, 9.6 - 0.25 * (z - 6), z), (0, 10.8 - 0.25 * (z - 6) + hgt, z + 1.2), 0.6, 0.16), K["rocha"]))
    p = construir("Lombo", "Corpo", VC, (0, 6.5, 4.0), ops); p.rj = 3.0
    return p

PERNAS = [("FE", -1, (5.4, 8.3, -0.6), (7.6, 4.3, -0.6), (7.2, 0.95, -2.4), "Corpo"), ("FD", 1, (5.4, 8.3, -0.6), (7.6, 4.3, -0.6), (7.2, 0.95, -2.4), "Corpo"),
          ("TE", -1, (4.2, 6.3, 9.4), (6.6, 3.8, 10.5), (6.2, 0.95, 9.1), "Lombo"), ("TD", 1, (4.2, 6.3, 9.4), (6.6, 3.8, 10.5), (6.2, 0.95, 9.1), "Lombo")]
def perna(nm, s, q, j, p, pai):
    q, j, p = [np.array([s * v[0], v[1], v[2]]) for v in (q, j, p)]
    cq = lambda P: np.where(P[:, 1] > 4.0, escamas(P, 1.0, K["vazio_s"], K["vazio_c"], K["vazio"]), escamas(P, 1.0, K["vazio"], K["vazio_s"], K["vazio_e"]))
    cox = construir(f"Coxa_{nm}", pai, VC, q, [('U', ('cap', q, j, 2.0, 1.5), cq), ('U', ('ell', q, (2.1,) * 3), cq), ('U', ('ell', j, ((1.25 if pai == 'Corpo' else 1.0),) * 3), cq),
                                             ('U', ('cap', j, j + np.array([s * 1.4, 1.6, 0.8]), 0.6, 0.15), K["chifre"])])
    can = construir(f"Canela_{nm}", f"Coxa_{nm}", VC, j, [('U', ('cap', j, p, 1.5, 1.15), cq), ('U', ('ell', j, (1.3,) * 3), cq), ('U', ('ell', p, (1.1,) * 3), K["rocha"])])
    ops = [('U', ('ell', p + (0, -0.15, 0), (1.4, 0.9, 1.5)), K["rocha"]), ('U', ('ell', p, (1.1,) * 3), K["rocha"])]
    for a_ in (-0.55, 0.0, 0.55):
        ops.append(('U', ('cap', p + (0, -0.1, -0.8), p + np.array([math.sin(a_) * 2.4 + s * 0.2, -0.3, -3.0 * math.cos(a_)]), 0.6, 0.2), K["chifre"]))
    ops.append(('U', ('cap', p + (0, 0.0, 0.8), p + np.array([s * 0.2, 0.7, 2.4]), 0.45, 0.15), K["chifre"]))
    pe = construir(f"Pe_{nm}", f"Canela_{nm}", VC, p, ops)
    cox.rj = 1.7; can.rj = 1.2; pe.rj = 1.0
    return cox, pe, can

def cauda():
    N = 12; ang = 0.22
    rs = [1.6 * (1 - j / N) ** 1.2 + 0.25 for j in range(N + 1)]
    pts = [np.array([0.0, max(rs[j] + 0.35, 4.6 - 0.2 * j), 13.2 + 3.6 * j]) for j in range(N + 1)]   # reta no eixo: o rabo varre os dois lados
    pecas = {}; ant = "Lombo"
    for j in range(1, N + 1):
        a, b = pts[j - 1], pts[j]; ct = cor_tubo(a, b, rs[j - 1], 1.0, DORSO, VENTRE)
        ops = [('U', ('cap', a, b, rs[j - 1], rs[j]), ct), ('U', ('ell', a, (rs[j - 1],) * 3), ct), ('U', ('ell', b, (rs[j] * 1.02,) * 3), ct)]
        c = (a + b) / 2
        if j < N:
            ops.append(('U', ('cap', c + Y * rs[j] * 0.7, c + Y * (rs[j] + 1.2) + np.array([0, 0, 0.5]), 0.36, 0.14), K["rocha"]))
        else:
            e = (b - a) / np.linalg.norm(b - a)
            for d in ((0, 0.25), (0.9, 0.5), (-0.9, 0.5)):
                lado = np.cross(e, Y)
                ops.append(('U', ('cap', b, b + e * 2.6 + lado * d[0] * 1.2 + Y * d[1], 0.5, 0.16), K["chifre"]))
        nm = f"Cauda{j}"; pecas[nm] = construir(nm, ant, VC if rs[j - 1] > 0.9 else VH_T, a, ops); pecas[nm].rj = rs[j - 1]; ant = nm
    return pecas

NUC = np.array([0, 9.0, -5.9])
def nucleo():
    def cor(P):
        r = np.sqrt(((P - NUC) ** 2).sum(1)); d = P - NUC
        aro = (np.abs(r - 2.0) < 0.3) & (np.abs(d[:, 2] + 0.5) < 0.4)
        return np.where(aro, K["fenda_b"], np.where(np.abs(np.sin(np.arctan2(d[:, 1], d[:, 0]) * 3 + r * 2.5)) < 0.12, K["vazio_c"], K["breu"]))
    ops = [('U', ('ell', NUC, (2.15, 2.15, 2.15)), cor), ('U', ('cap', NUC, NUC + (0, 0, 2.4), 0.8), K["breu"]),
           ('U', ('ell', NUC + (0, 0, -0.5), (2.5, 2.5, 0.3)), K["fenda"]), ('C', ('ell', NUC + (0, 0, -0.5), (2.05, 2.05, 0.6)), None),
           ('U', ('ell', NUC, (2.15, 2.15, 2.15)), cor)]
    return construir("Nucleo", "Corpo", VC, NUC, ops)

def vfx():
    raio = lambda P: np.where((P[:, 0] ** 2 + P[:, 1] ** 2) < 0.3 ** 2, K["fenda_b"], K["fenda"])
    orbe = lambda P: np.where((P ** 2).sum(1) < 0.62 ** 2, K["fenda_b"], K["fenda"])
    V = {"Raio": construir("Raio", None, VH, (0, 0, 0), [('U', ('cap', (0, 0, -0.7), (0, 0, 2.7), 0.62), raio), ('C', lambda P: (P[:, 2] < 0) | (P[:, 2] > 2.0), None)]),
         "Orbe": construir("Orbe", None, VH, (0, 0, 0), [('U', ('ell', (0, 0, 0), (1, 1, 1)), orbe)]),
         "Onda": construir("Onda", None, VC, (0, 0, 0), [('U', ('ell', (0, 0.3, 0), (4.0, 0.45, 4.0)), K["fenda"]), ('C', ('ell', (0, 0.3, 0), (3.3, 1.0, 3.3)), None)])}
    ops = [('U', ('ell', (0, 0, 0), (1, 1, 1)), orbe)]
    for i in range(10):
        a_ = i * 0.628; ops.append(('U', ('cap', (0, 0, 0), (1.9 * math.cos(a_), 0.7 + 0.8 * (i % 2), 1.9 * math.sin(a_)), 0.4, 0.1), K["fenda_b"] if i % 2 else K["fenda"]))
    V["Impacto"] = construir("Impacto", None, VH, (0, 0, 0), ops)
    return {n: faces(p) for n, p in V.items()}

def hidra():
    P = {"Corpo": corpo(), "Lombo": lombo(), "Nucleo": nucleo()}
    for nm, s, q, j, p, pai in PERNAS:
        a, b, c = perna(nm, s, q, j, p, pai); P[a.nome] = a; P[b.nome] = b; P[c.nome] = c
    P.update(cauda()); info = {}
    for k, n in enumerate(NECKS):
        pp, pts, rs = pescoco(k, n); P.update(pp)
        pc, pm, h = cabeca(k, n, pts, f"N{k}_{NSEG}"); P[pc.nome] = pc; P[pm.nome] = pm; info[k] = h
    return dict(nome="Hidra do Vazio adulta", pecas=P, info=info)

# ---------------- animacao ----------------
W2 = 2 * math.pi
def ease(a, b, f):
    u = min(max((f - a) / (b - a), 0.0), 1.0); return u * u * (3 - 2 * u)
def mj(q):
    return q * q * q * (10 - 15 * q + 6 * q * q)
def bump(dt, f=1.4, k=3.6):
    return math.exp(-k * dt) * math.sin(W2 * f * dt) if dt >= 0 else 0.0
def wrap(a):
    return (a + math.pi) % W2 - math.pi

CLIPES = (("parado", 4.0, 24), ("andar", 2.0, 24), ("raio", 3.6, 30), ("mordida", 2.6, 26), ("pisao", 2.8, 28), ("rugido", 3.0, 24))
# marcha de animal pesado: sequencia lateral (TE, FE, TD, FD), 70% de apoio, passo curto, pe quase rente ao chao
PER_ANDAR, BETA, PASSO = 2.0, 0.70, 4.0
VEL = PASSO / (BETA * PER_ANDAR)          # o chao anda exatamente na velocidade do apoio: pe travado, sem deslizar
FASES = {"TE": 0.0, "FE": 0.25, "TD": 0.5, "FD": 0.75}
Y_PE = 0.95; LEVANTE = 0.8
ALVO = np.array([0.0, 0.6, -24.0])

def ik(Hyz, Fyz, t0, s0):
    L1, L2 = math.hypot(*t0), math.hypot(*s0)
    D = np.array(Fyz) - np.array(Hyz); d = float(np.linalg.norm(D)); d = min(max(d, abs(L1 - L2) * 1.02), (L1 + L2) * 0.995)
    ang = lambda v: math.atan2(v[1], v[0])
    psi0 = wrap(ang(s0) - ang(t0)); c = (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    psi = math.copysign(math.acos(max(-1.0, min(1.0, c))), psi0)
    A1 = ang(D) - math.atan2(L2 * math.sin(psi), L1 + L2 * math.cos(psi))
    return wrap(A1 - ang(t0)), wrap(psi - psi0)

def impacto(t, clipe):
    """Soma das pisadas: cada pe que toca o chao dá um tranco que decai (o peso chega, o corpo afunda e volta)."""
    if clipe != "andar":
        return 0.0
    return sum((0.55 if nm[0] == "F" else 0.4) * bump(((t / PER_ANDAR + ph) % 1.0) * PER_ANDAR) for nm, ph in FASES.items())

def pe_alvo(clipe, nm, t, p, f_clip):
    """Alvo do pe no mundo (x, y, z) e o quanto o calcanhar sobe. Padrao: plantado onde estava."""
    x, y, z = p[0], Y_PE, p[2]; toe = 0.0
    if clipe == "andar":
        u = (t / PER_ANDAR + FASES[nm]) % 1.0
        if u < BETA:
            ps = u / BETA; z = p[2] + PASSO * (ps - 0.5); toe = -0.32 * ease(0.78, 1.0, ps)
        else:
            q = (u - BETA) / (1 - BETA); z = p[2] + PASSO / 2 - PASSO * mj(q); y = Y_PE + LEVANTE * math.sin(math.pi * q) ** 1.3; toe = 0.22 * math.sin(math.pi * q)
    elif clipe == "pisao" and nm[0] == "F":
        sobe, desce = f_clip
        y = Y_PE + 3.2 * sobe * (1 - desce); z = p[2] - 1.5 * sobe * (1 - desce); toe = 0.3 * sobe * (1 - desce)
    return np.array([x, y, z]), toe

def pose(m, clipe, t, com_vfx=False):
    L = {}; nk = 3
    atk = np.zeros((nk, NSEG)); yawk = np.zeros((nk, NSEG)); jaw = np.full(nk, 0.08); core = 1.0; fx = []
    d = np.zeros(3); pit = rol = yaw = 0.0; rear = 0.0; f_clip = (0.0, 0.0); frag_burst = 0.0
    anda = clipe == "andar"; ph = W2 * t / PER_ANDAR
    # ---- camada viva (sempre ligada): respiracao, peso que passa de um lado a outro, lombo que defasa
    resp = math.sin(W2 * t / 3.6); vida = 1.0 if not anda else 0.5
    d += np.array([0.28 * vida * math.sin(W2 * t / 6.0), 0.1 * vida * resp, 0.0])
    rol += 0.012 * vida * math.sin(W2 * t / 6.0 - 0.5); yaw += 0.015 * vida * math.sin(W2 * t / 7.0); pit += 0.008 * vida * math.sin(W2 * t / 3.6 + 0.8)
    lom = [0.02 * vida * math.sin(W2 * t / 4.4 - 0.9), 0.012 * vida * math.sin(W2 * t / 3.6 - 1.2), 0.014 * vida * math.sin(W2 * t / 6.0 - 1.4)]   # yaw, pitch, roll do lombo
    imp = impacto(t, clipe)
    sway = lambda k, j: (0.04 * math.sin(W2 * t / 4 + k * 2.1 - 0.5 * j), 0.025 * math.sin(2 * W2 * t / 4 + k * 1.3 - 0.6 * j))
    tail_w, tail_a, tail_v = W2 / 5.0, 1.0, 0.0
    if clipe == "parado":
        for k in range(nk):
            jaw[k] = 0.1 + 0.12 * max(0, math.sin(W2 * t / 4 + 2 * k))
        core = 1 + 0.06 * math.sin(W2 * t / 2)
    elif anda:
        sway = lambda k, j: (0.045 * math.sin(ph + k * 2.1 - 0.5 * j) - 0.012 * math.sin(ph), 0.03 * math.sin(2 * ph - 0.6 * j + 0.3 * k))
        d += np.array([0.5 * math.sin(ph), -0.55 * max(imp, -0.04), 0.0])                      # peso passa para o lado do apoio; cada pisada afunda o corpo
        rol += 0.03 * math.sin(ph - 0.3); yaw += 0.035 * math.sin(ph + 0.4); pit += 0.9 * 0.05 * (bump(((t / PER_ANDAR + FASES["FE"]) % 1) * PER_ANDAR) + bump(((t / PER_ANDAR + FASES["FD"]) % 1) * PER_ANDAR))
        lom = [-0.05 * math.sin(ph + 0.4), 0.02 * math.sin(2 * ph + 1.0), -0.028 * math.sin(ph - 0.3)]   # lombo gira contra os ombros
        for k in range(nk):
            jaw[k] = 0.12 + 0.08 * math.sin(2 * ph + k)
        core = 1 + 0.07 * math.sin(2 * ph); tail_w, tail_a = ph, 1.5
    elif clipe == "raio":
        f = (t % 3.6) / 3.6
        carga = ease(0.0, 0.38, f); fogo = ease(0.42, 0.48, f) * (1 - ease(0.8, 0.86, f)); volta = ease(0.86, 1.0, f)
        for k in range(nk):
            for j in range(NSEG):
                atk[k, j] = 0.05 * carga * (1 - ease(0.38, 0.46, f)) - 0.045 * ease(0.38, 0.46, f) * (1 - volta)
            jaw[k] = 0.25 * carga + 0.55 * fogo
        core = 1 + 0.1 * carga + 0.08 * fogo * math.sin(t * 40)
        d += np.array([0, -0.2 * fogo, 0.5 * fogo + 0.05 * fogo * math.sin(t * 50)]); pit += 0.03 * fogo
        varre = 7.0 * math.sin(W2 * (f - 0.45) / 0.4 * 0.5) if fogo > 0 else 0.0
        fx = [("carga", carga * (1 - fogo) if f < 0.5 else 0.0), ("fogo", fogo, ALVO + np.array([varre, 0, 0]))]
        tail_a = 1.0 + 1.2 * fogo; lom[1] += 0.03 * fogo
    elif clipe == "mordida":
        f = (t % 2.6) / 2.6
        for k, (t0, sg) in ((1, (0.0, 1)), (2, (0.22, -1))):
            arma = ease(t0, t0 + 0.2, f); bote = ease(t0 + 0.2, t0 + 0.29, f); vol = ease(t0 + 0.42, t0 + 0.75, f)
            for j in range(NSEG):
                atk[k, j] = 0.07 * arma * (1 - bote) - 0.13 * bote * (1 - vol)
                yawk[k, j] = sg * 0.05 * bote * (1 - vol)
            jaw[k] = 0.75 * ease(t0 + 0.08, t0 + 0.2, f) * (1 - ease(t0 + 0.28, t0 + 0.32, f)) + 0.08
        tot = ease(0.2, 0.29, f) * (1 - ease(0.6, 0.9, f))
        d += np.array([0, -0.25 * tot, -0.8 * tot]); jaw[0] = 0.3 * tot + 0.08; pit += 0.05 * tot; tail_a = 1.0 + 1.0 * tot
    elif clipe == "pisao":
        f = (t % 2.8) / 2.8
        sobe = ease(0.0, 0.38, f); desce = ease(0.38, 0.47, f); vol = ease(0.7, 1.0, f)
        rear = 0.2 * sobe * (1 - desce) - 0.03 * desce * (1 - vol); f_clip = (sobe, ease(0.38, 0.47, f) * (1 - vol) if f > 0.38 else 0.0)
        f_clip = (sobe * (1 - (desce if f > 0.38 else 0.0)), 0.0) if f < 0.7 else (0.0, 0.0)
        for k in range(nk):
            for j in range(NSEG):
                atk[k, j] = -0.03 * sobe * (1 - desce)
            jaw[k] = 0.5 * desce * (1 - vol) + 0.08
        d += np.array([0, 0.25 * math.sin(t * 45) * desce * (1 - ease(0.47, 0.6, f)), 0]); core = 1 + 0.12 * desce * (1 - vol)
        fx = [("onda", ease(0.46, 0.95, f) if f > 0.46 else 0.0)]; tail_a = 1.0 + 1.4 * desce * (1 - vol); tail_v = 0.5 * desce * (1 - vol)
    else:
        f = (t % 3.0) / 3.0
        insp = ease(0.0, 0.3, f); roar = ease(0.3, 0.4, f) * (1 - ease(0.85, 1.0, f))
        for k in range(nk):
            for j in range(NSEG):
                atk[k, j] = 0.035 * insp * (1 - roar) + 0.05 * roar
                yawk[k, j] = 0.012 * math.sin(t * 30 + k) * roar
            jaw[k] = 0.85 * roar + 0.06 * insp
        d += np.array([0, 0.3 * insp + 0.08 * math.sin(t * 50) * roar, 0]); rear = 0.05 * roar; resp = resp + 2.0 * insp
        core = 1 + 0.12 * roar + 0.03 * math.sin(t * 40) * roar; fx = [("pulso", roar, f)]; frag_burst = roar; tail_a = 1.0 + 1.3 * roar
    # ---- corpo: matriz do peito (rotacao e respiracao) e lombo (corrente de 2 elos) ----
    Rc = rot_eixo(X, rear + pit) @ rot_eixo(Z, rol) @ rot_eixo(Y, yaw) @ np.diag([1 + 0.012 * resp, 1 + 0.02 * resp, 1 + 0.012 * resp])
    L["Lombo"] = rot_eixo(Y, lom[0]) @ rot_eixo(X, lom[1] - rear * 0.85 - pit * 0.6) @ rot_eixo(Z, lom[2])
    # ---- pescoços: sway + atraso do tranco das pisadas (o pescoço sente o corpo afundar com um pouco de atraso) ----
    for k in range(nk):
        for j in range(1, NSEG + 1):
            yw, pt = sway(k, j - 1)
            seg = 0.02 * j * impacto(t - 0.05 * j - 0.04 * k, clipe) if anda else 0.0
            L[f"N{k}_{j}"] = rot_eixo(Y, yw + yawk[k, j - 1]) @ rot_eixo(X, pt + atk[k, j - 1] - rear / NSEG + seg)
        h = m["info"][k]
        L[f"H{k}"] = rot_eixo(Y, 0.05 * math.sin(W2 * t / 3 + 2 * k)) @ rot_eixo(X, 0.03 * math.sin(W2 * t / 2.2 + k) - 0.35 * jaw[k])
        L[f"J{k}"] = rot_eixo(h["B"][:, 0], jaw[k])
    # ---- rabo: corrente de 12 elos. Onda que viaja da base à ponta e cresce, atraso em cada elo,
    #      contrapeso do quadril (gira contra o lombo), levantar/abaixar com o tranco das pisadas e peso (a ponta cai)
    NT = 12
    for j in range(1, NT + 1):
        a_y = (0.03 + 0.02 * j) * tail_a; a_p = (0.006 + 0.0065 * j) * min(tail_a, 1.15)
        if anda:
            yaw_j = a_y * math.sin(tail_w - 0.5 * j + 0.4) - 0.5 * lom[0] / NT * j * 0.4
            pit_j = a_p * (0.5 * math.sin(2 * tail_w - 0.45 * j + 0.5) - 0.25)
            pit_j += 0.005 * j * impacto(t - 0.05 * j, clipe)
        else:   # a ponta desenha uma elipse (yaw e pitch defasados 90 graus) e uma 2a onda mais lenta a desloca: varre direita, esquerda, cima e baixo
            yaw_j = a_y * math.sin(tail_w * t - 0.5 * j) + 0.6 * a_y * math.sin(W2 * t / 3.1 - 0.35 * j + 1.0)
            pit_j = a_p * (0.55 * math.sin(tail_w * t - 0.5 * j + 1.57) - 0.2) + 0.15 * a_p * math.sin(W2 * t / 4.3 - 0.4 * j) - 0.012 * tail_v * j
        rol_j = 0.02 * math.sin(tail_w * t - 0.5 * j + 0.8) * j / NT if not anda else 0.02 * math.sin(tail_w - 0.5 * j) * j / NT
        L[f"Cauda{j}"] = rot_eixo(Y, yaw_j) @ rot_eixo(X, pit_j) @ rot_eixo(Z, rol_j)
    L["Nucleo"] = np.diag([core] * 3)
    # ---- pernas: IK de duas juntas, pe travado no chao ----
    T0 = B.montar(m, B.raiz(m, Rc, d), L)
    for nm, s_, q, j, p, pai in PERNAS:
        Tp = T0[pai]; p_w = np.array([s_ * p[0], p[1], p[2]])
        Fw, toe = pe_alvo(clipe, nm, t, p_w, f_clip)
        Fl = Tp[0].T @ (Fw - Tp[1])
        qv, jv = np.array([s_ * q[0], q[1], q[2]]), np.array([s_ * j[0], j[1], j[2]])
        th1, th2 = ik((qv[1], qv[2]), (Fl[1], Fl[2]), (jv[1] - qv[1], jv[2] - qv[2]), (p_w[1] - jv[1], p_w[2] - jv[2]))
        L[f"Coxa_{nm}"] = rot_eixo(X, th1); L[f"Canela_{nm}"] = rot_eixo(X, th2); L[f"Pe_{nm}"] = rot_eixo(X, -(th1 + th2) + toe)
    T = B.montar(m, B.raiz(m, Rc, d), L)
    if not com_vfx:
        return T
    itens = []
    bocas = [T[f"H{k}"][0] @ m["info"][k]["boca"] + T[f"H{k}"][1] for k in range(nk)]
    for e in fx:
        if e[0] == "carga" and e[1] > 0.02:
            for bq in bocas:
                s_ = 0.4 + 1.5 * e[1] + 0.12 * math.sin(t * 40); itens.append(("Orbe", np.eye(3) * s_, bq))
        if e[0] == "fogo" and e[1] > 0.02:
            alvo = e[2]
            for bq in bocas:
                v = alvo - bq; ln = np.linalg.norm(v); Bz = basis(v); w = (0.75 + 0.12 * math.sin(t * 60)) * e[1]
                itens.append(("Raio", Bz @ np.diag([w, w, ln / 2.0]), bq)); itens.append(("Orbe", np.eye(3) * 1.7, bq))
            itens.append(("Impacto", rot_eixo(Y, t * 9) * (2.2 + 0.5 * math.sin(t * 45)) * e[1], alvo))
        if e[0] == "onda" and e[1] > 0.0 and e[1] < 1.0:
            s_ = 1.5 + 7.0 * e[1]; itens.append(("Onda", np.diag([s_, 1 - 0.7 * e[1], s_]), np.array([0, 0, -3.0])))
            if e[1] > 0.3:
                s2 = 1.5 + 7.0 * (e[1] - 0.3); itens.append(("Onda", np.diag([s2, 1 - 0.7 * e[1], s2]), np.array([0, 0, -3.0])))
        if e[0] == "pulso" and e[1] > 0.05:
            nu = T["Nucleo"][0] @ NUC + T["Nucleo"][1]
            for q in (0.0, 0.5):
                u = ((e[2] * 4 + q) % 1.0); s_ = 0.7 + 2.2 * u
                itens.append(("Onda", rot_eixo(X, math.pi / 2) @ np.diag([s_, 0.8, s_]), nu + np.array([0, 0, -2.6 - 5 * u])))
    return T, itens

if __name__ == "__main__":
    t0 = time.time(); m = hidra()
    rel = HA.auditoria(m, rapido="--rapido" in sys.argv, pose=pose, CLIPES=CLIPES, RGB=RGB, EMIS=EMIS)
    json.dump(rel, open(os.path.join(OUT, "hidra_adulta_auditoria.json"), "w"), indent=1, ensure_ascii=False, default=float)
    for r in rel["regras"]:
        print(r)
    print("pecas", len(m["pecas"]), "voxels", rel["total_voxels"], "tris", rel["total_tris"], rel["valores"], "colisao", rel["colisao"], "nucleo", rel["nucleo_cravado"], round(time.time() - t0), "s")
    print("fracas", [j for j in rel["juntas"] if min(j[1], j[2]) < 8]); print("soltos", {n: v["soltos"] for n, v in rel["pecas"].items() if v["soltos"]})
    print("tris>20k", {n: v["tris"] for n, v in rel["pecas"].items() if v["tris"] > 20000})
    for c, v in rel["colisao_pares"].items():
        if v: print(c, v)
    if "--render" in sys.argv:
        V = vfx(); FUNDO = (0.13, 0.11, 0.17)
        cor_p = lambda P: np.where((np.floor(P[:, 0] / 6) + np.floor(P[:, 2] / 6)) % 2 == 0, K["pedra_av_s"], K["rocha_e"])
        PISO = faces(construir("Piso", None, 0.5, (0, 0, 0), [('U', ('ell', (0, -0.3, -8), (52, 0.3, 52)), cor_p)]))
        def itens(T, extra=(), zp=0.0):
            return [(m["faces"][n], *T[n]) for n in m["pecas"]] + [(PISO, np.eye(3), np.array([0, 0, zp % 12.0]))] + [(V[n], M, tt) for n, M, tt in extra]
        def cena(T, dv, c, esc, W, H, extra=(), zp=0.0):
            return render(itens(T, extra, zp), camera_orto(dv, Y, c, esc, W, H), RGB, EMIS, fundo=FUNDO, bloom=0.6, ambiente=0.5)
        T0 = pose(m, "parado", 0.0)
        Q = np.concatenate([m["faces"][n]["c"] @ T0[n][0].T + T0[n][1] for n in m["pecas"]]); dim = Q.max(0) - Q.min(0); print("dimensoes", dim.round(1))
        v = Image.new("RGB", (3 * 640, 720))
        for k, dv in enumerate(((0.0001, -0.1, 1), (0.55, -0.2, 0.81), (1, -0.12, 0.0001))):
            v.paste(cena(T0, dv, (0, 14.5, 4.0), 14.5, 640, 720), (k * 640, 0))
        v.save(os.path.join(OUT, "hidra_adulta_vistas.png"))
        # escala: heroi (4 studs) e Nihilis
        cam = camera_orto((0.4, -0.18, 0.9), Y, (-6, 14.0, 0), 13.5, 1300, 700)
        ch, g, _ = herois.montar("M", 1, "base"); fh = faces(herois.peca(ch["G"], g))
        img = render([(fh, np.eye(3), np.array([-27.0, 0, -8.0]))], cam, herois.RGB, set(), fundo=FUNDO, ambiente=0.55)
        nh = Hd.hidra()
        for p in nh["pecas"].values(): p.limpar_soltos()
        Tn = HA.pose(nh, "parado", 0.0)
        img = render([(faces(p), Tn[n][0], Tn[n][1] + np.array([-38.0, 0, 6.0])) for n, p in nh["pecas"].items()], cam, Hd.RGB, Hd.EMIS, img_fundo=img, bloom=0.5, ambiente=0.5)
        esc = render([(m["faces"][n], *T0[n]) for n in m["pecas"]], cam, RGB, EMIS, img_fundo=img, bloom=0.6, ambiente=0.5)
        ImageDraw.Draw(esc).text((12, 12), f"Nihilis (18 studs)  |  heroi (4 studs)  |  Hidra adulta: {dim[1]:.0f} de altura, {dim[0]:.0f} de largura, {dim[2]:.0f} de comprimento", fill=(235, 235, 235))
        esc.save(os.path.join(OUT, "hidra_adulta_escala.png"))
        # close de uma cabeca
        h = m["info"][0]; fz, up, ld = h["B"][:, 2], h["B"][:, 1], h["B"][:, 0]
        cl = Image.new("RGB", (2 * 560, 460))
        for i, dv in enumerate((-(fz * 0.75 + ld * 0.6 + up * 0.15), -(ld * 1.0 + fz * 0.1 + up * 0.05))):
            its = [(m["faces"][n], *T0[n]) for n in ("H0", "J0")]
            cl.paste(render(its, camera_orto(tuple(dv), Y, tuple(h["o"] + fz * 0.4 * h["hs"] + up * 0.5 * h["hs"]), 36, 560, 460), RGB, EMIS, fundo=FUNDO, bloom=0.6, ambiente=0.5), (i * 560, 0))
        cl.save(os.path.join(OUT, "hidra_adulta_cabeca.png"))
        fr = []; Wf, Hf = 760, 620; folha = Image.new("RGB", (6 * 250, 6 * 204))
        for r, (c, dur, n) in enumerate(CLIPES):
            for i in range(n):
                tt = i / n * dur; T, ex = pose(m, c, tt, com_vfx=True)
                im = cena(T, (0.55, -0.2, 0.81), (0, 14.5, -5.0), 15.0, Wf, Hf, ex, VEL * tt if c == "andar" else 0.0); fr.append(im)
                if i % (n // 6) == 0 and i // (n // 6) < 6:
                    folha.paste(im.resize((250, 204)), ((i // (n // 6)) * 250, r * 204))
        fr[0].save(os.path.join(OUT, "hidra_adulta_animacoes.webp"), save_all=True, append_images=fr[1:], duration=75, loop=0, quality=70)
        folha.save(os.path.join(OUT, "hidra_adulta_clipes.png")); print(len(fr), "quadros")
