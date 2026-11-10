"""Myxilia: ficha, paleta, geometria e rig. Gera as pecas voxel nos dois cortes (grade e susto)."""
import math
import numpy as np
from voxforja import (Peca, construir, ruido, capsula, esfera, elipsoide, hex_rgb, _unit)

PAL = [
    ("quitina_escura", "2A2430", 0), ("quitina", "3B3243", 0), ("quitina_clara", "54485C", 0), ("quitina_borda", "75677D", 0),
    ("fungo_sombra", "8A715E", 0), ("fungo", "BDA084", 0), ("fungo_claro", "DFCCAE", 0),
    ("chapeu_escuro", "631818", 0), ("chapeu", "8E2222", 0), ("lamela", "C99A8C", 0),
    ("olho_morto", "B5B0A6", 0), ("presa", "D8D0BF", 0), ("presa_ponta", "6B6155", 0), ("espinho", "141016", 0),
    ("veio", "A3463E", 0), ("no", "FF9A3C", 1), ("nucleo", "FFC46B", 1),
    ("micelio", "D6C7B2", 0), ("micelio_sombra", "A6927B", 0), ("tit_corpo", "D8B8A8", 0), ("tit_sombra", "9E7466", 0),
    ("pinta", "E8DCC8", 0),
    ("heroi_pele", "C99A7C", 0), ("heroi_armadura", "5B6B7A", 0), ("heroi_armadura_clara", "8A9AA8", 0), ("heroi_cabelo", "3B2A20", 0),
    ("pedra", "3A3836", 0), ("pedra_clara", "46423F", 0), ("rejunte", "262422", 0),
]
K = {n: i + 1 for i, (n, h, e) in enumerate(PAL)}
HEX = ["000000"] + [h for _, h, _ in PAL]
RGB = np.array([hex_rgb(h) for h in HEX])
EMIS = {i + 1 for i, (n, h, e) in enumerate(PAL) if e}
Q0, Q1, Q2, Q3 = K["quitina_escura"], K["quitina"], K["quitina_clara"], K["quitina_borda"]
F0, F1, F2 = K["fungo_sombra"], K["fungo"], K["fungo_claro"]
C0, C1, LAM, OM, PR, PRP, ESP = K["chapeu_escuro"], K["chapeu"], K["lamela"], K["olho_morto"], K["presa"], K["presa_ponta"], K["espinho"]
VEIO, NO, NUC, MIC, MIC0, TC, TS, PINTA = K["veio"], K["no"], K["nucleo"], K["micelio"], K["micelio_sombra"], K["tit_corpo"], K["tit_sombra"], K["pinta"]

FICHA = {
    "id": "monstro.chefe.myxilia", "versao": 1, "arquetipo": "octopode@1", "tier": "chefe", "elemento": "fungo",
    "conceito": "Aranha-matriarca morta, movida como marionete por uma colonia de micelio e pelo Titereiro preso no abdomen.",
    "cortes": {"grade": 0.125, "susto": 0.0625,
               "pecas_susto": ["Cefalotorax", "Quelicera_E", "Quelicera_D", "Esporangio_1", "Esporangio_2", "Esporangio_3", "No_*"]},
    "fios": 8, "sustos": ["investida", "teto", "montagem", "periferico"],
    "marcha": {"padrao": "tetrapode_alternado", "apoio": 0.6, "fr_espreita": 0.05, "fr_investida": 0.6, "modo": "marionete"},
    "assimetria": "Perna3_D trocada por um talo de micelio",
    "fases": [
        {"nome": "Marionete", "vida": [1.0, 0.6], "fios": 8},
        {"nome": "Fios cortados", "vida": [0.6, 0.25], "regra": "cada no destruido solta a perna dele"},
        {"nome": "Desabamento", "gatilho": "centro de massa fora do apoio ou vida < 25%", "acao": "o Titereiro arranca as raizes e luta a pe"},
    ],
}

# ---------------- cores ----------------
def faixas(cy, ry, cores=(Q0, Q1, Q2), baixo=-0.35, topo=0.45):
    def f(P):
        h = (P[:, 1] - cy) / ry
        return np.where(h < baixo, cores[0], np.where(h < topo, cores[1], cores[2]))
    return f

def cor_seg(a, b, ra, rb, cores=(Q0, Q1, Q2), anel=Q3, listras=None):
    a = np.asarray(a, float); b = np.asarray(b, float)
    def f(P):
        ab = b - a
        t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
        Q = a + t[:, None] * ab
        r = ra + (rb - ra) * t
        dy = (P[:, 1] - Q[:, 1]) / r
        c = np.where(dy < -0.35, cores[0], np.where(dy > 0.45, cores[2], cores[1]))
        if listras is not None:
            L = np.linalg.norm(ab)
            c = np.where(np.sin(t * L / listras * math.pi) > 0.55, cores[0], c)
        if anel is not None:
            c = np.where(t > 0.9, anel, c)
        return c
    return f

def esfera_bicolor(c, r, frente, tras, pupila=None):
    c = np.asarray(c, float)
    def f(P):
        cor = np.where(P[:, 2] < c[2] + 0.02, frente, tras)
        if pupila is not None:
            m = (np.abs(P[:, 0] - c[0]) < pupila[0]) & (np.abs(P[:, 1] - c[1]) < pupila[1]) & (P[:, 2] < c[2] - 0.55 * r)
            cor = np.where(m, Q0, cor)
        return cor
    return f

def bolha(c, r):
    c = np.asarray(c, float)
    def f(P):
        dy = P[:, 1] - c[1]
        return np.where(dy > 0.22 * r, NO, np.where(dy > -0.2 * r, F2, F1))
    return f

def cogumelo(c, r, cor_cima=C1, cor_borda=C0, cor_baixo=LAM, pintas=()):
    c = np.asarray(c, float)
    def f(P):
        dy = P[:, 1] - c[1]
        cor = np.where(dy > 0.02, cor_cima, np.where(dy > -0.06, cor_borda, cor_baixo))
        for p in pintas:
            cor = np.where(np.linalg.norm(P - np.asarray(p), axis=1) < 0.11, PINTA, cor)
        return cor
    return f

# ---------------- pernas ----------------
def ik2(quadril, tornozelo, Lf, Lt, dica):
    d = np.linalg.norm(tornozelo - quadril)
    d = min(d, (Lf + Lt) * 0.999)
    e = (tornozelo - quadril) / np.linalg.norm(tornozelo - quadril)
    a = (Lf * Lf - Lt * Lt + d * d) / (2 * d)
    h = math.sqrt(max(Lf * Lf - a * a, 1e-6))
    n = np.asarray(dica, float) - (np.asarray(dica, float) @ e) * e
    n = n / np.linalg.norm(n)
    return quadril + a * e + h * n

PERNAS = []
_ANG = [34, 70, 108, 146]
_RPE = [7.3, 7.1, 6.9, 7.5]
_LF = [4.3, 4.1, 4.0, 4.3]
_LT = [6.5, 6.2, 6.0, 6.7]
_LS = [1.5, 1.4, 1.35, 1.5]
CEF_C = np.array([0.0, 2.95, -1.4])
CEF_R = np.array([1.55, 0.95, 1.75])
for lado, s in (("E", -1), ("D", 1)):
    for i in range(4):
        a = math.radians(_ANG[i])
        dirxz = np.array([s * math.sin(a), 0.0, -math.cos(a)])
        base = CEF_C + np.array([s * CEF_R[0] * math.sin(a) * 0.9, -0.2, -CEF_R[2] * math.cos(a) * 0.9])
        quadril = base + dirxz * 0.75 + np.array([0, 0.2, 0])
        pe = np.array([0.0, 0.0, -1.4]) + dirxz * _RPE[i]
        ang_t = math.radians(72)
        tornozelo = pe - dirxz * _LS[i] * math.cos(ang_t) + np.array([0, _LS[i] * math.sin(ang_t), 0])
        joelho = ik2(quadril, tornozelo, _LF[i], _LT[i], np.array([0, 1.0, 0]))
        PERNAS.append(dict(nome=f"Perna{i + 1}_{lado}", lado=lado, s=s, i=i, dir=dirxz, base=base, quadril=quadril,
                           joelho=joelho, tornozelo=tornozelo, pe=pe, Lf=_LF[i], Lt=_LT[i], Ls=_LS[i],
                           protese=(lado == "D" and i == 2)))

def cima_perp(u):
    u = _unit(u); y = np.array([0, 1.0, 0])
    return _unit(y - (y @ u) * u)

# ---------------- pecas ----------------
def caminhar_veios(p, sementes, passos, direcao_fn, seed, ramo=0.07, cor=VEIO):
    """Veios de 1 voxel que andam pela superficie da peca, como micelio."""
    sup = p.superficie().reshape(p.dims)
    pos = set(map(tuple, np.argwhere(sup)))
    rng = np.random.default_rng(seed)
    viz = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dy, dz) != (0, 0, 0)]
    marcados = []
    fila = []
    for sw in sementes:
        q = np.floor((np.asarray(sw) - p.origem) / p.vs).astype(int)
        cand = np.array(list(pos))
        q = tuple(cand[np.argmin(((cand - q) ** 2).sum(1))])
        fila.append((q, direcao_fn(p.origem + (np.array(q) + 0.5) * p.vs), passos))
    while fila:
        q, d, n = fila.pop()
        visit = {q}
        for _ in range(n):
            marcados.append(q)
            melhor, ms = None, -9
            for v in viz:
                c = (q[0] + v[0], q[1] + v[1], q[2] + v[2])
                if c in pos and c not in visit:
                    sc = (np.array(v) @ d) / np.linalg.norm(v) + rng.normal(0, 0.35)
                    if sc > ms:
                        melhor, ms = c, sc
            if melhor is None:
                break
            passo = _unit(np.array(melhor) - np.array(q))
            alvo = direcao_fn(p.origem + (np.array(melhor) + 0.5) * p.vs)
            d = _unit(0.6 * d + 0.25 * passo + 0.15 * alvo + rng.normal(0, 0.12, 3))
            q = melhor
            visit.add(q)
            if rng.random() < ramo and n > 8:
                rot = rng.normal(0, 0.9, 3)
                fila.append((q, _unit(d + rot), int(n * 0.45)))
    for q in marcados:
        if p.g[q] not in (NO, NUC):
            p.g[q] = cor
    return len(marcados)

def veio_linha(p, a, b, r_a, r_b, lado_vec, amplitude=0.06, ondas=9, cor=VEIO, ate=1.0):
    a = np.asarray(a, float); b = np.asarray(b, float)
    u = _unit(b - a); up = cima_perp(u)
    t = np.linspace(0, ate, 160)[:, None]
    pts = a + (b - a) * t + up * (r_a + (r_b - r_a) * t) * 0.95 + np.asarray(lado_vec) * amplitude * np.sin(t * ondas)
    sup = p.superficie()
    S = p.P[sup]
    d = np.full(len(S), 9.0)
    for k in range(0, len(pts), 40):
        d = np.minimum(d, np.sqrt(((S[:, None, :] - pts[None, k:k + 40, :]) ** 2).sum(2)).min(1))
    idx = np.nonzero(sup)[0][d < 0.62 * p.vs]
    flat = p.g.reshape(-1)
    flat[idx] = cor
    return len(idx)

def pecas_myxilia(vs_grade=0.125, vs_susto=0.0625, corte="grade"):
    fino = lambda nome: vs_susto if (corte == "susto" and (nome in ("Cefalotorax", "Quelicera_E", "Quelicera_D") or nome.startswith(("Esporangio", "No_")))) else vs_grade
    pecas = {}

    # --- cefalotorax e cabeca ---
    olhos = [((s * 0.22, 3.0, -3.86), 0.17) for s in (-1, 1)] + [((s * 0.55, 2.95, -3.72), 0.13) for s in (-1, 1)] + \
            [((s * 0.25, 3.35, -3.72), 0.12) for s in (-1, 1)] + [((s * 0.62, 3.3, -3.52), 0.11) for s in (-1, 1)]
    ops = [('U', ('ell', CEF_C, CEF_R), faixas(2.95, 0.95)),
           ('U', ('ell', (0, 2.65, -2.95), (1.15, 0.85, 1.0)), faixas(2.65, 0.85)),
           ('U', ('ell', (0, 3.62, -1.55), (0.42, 0.32, 1.45)), Q2),
           ('U', ('cap', (0, 2.95, -0.2), (0, 3.05, 0.5), 0.42), Q0)]
    ops += [('U', ('esf', c, r), OM) for c, r in olhos]
    vs = fino("Cefalotorax")
    cef = construir("Cefalotorax", None, vs, (0, 2.85, -1.6), ops, "Corpo", 1.1)
    caminhar_veios(cef, [(0, 3.3, -0.1), (-0.4, 3.2, -0.3), (0.45, 3.1, -0.4)], int(22 * 0.125 / vs),
                   lambda P: _unit(np.array([0, 0.1, -1.0])), seed=3, ramo=0.04)
    pecas["Cefalotorax"] = cef

    # --- esporangios (olhos do parasita) ---
    for k, (b, t, r) in enumerate([((-0.45, 3.2, -3.45), (-0.85, 4.25, -4.15), 0.25),
                                    ((0.1, 3.4, -3.3), (0.15, 4.6, -3.95), 0.28),
                                    ((0.5, 3.2, -3.5), (1.0, 4.0, -4.25), 0.22)]):
        nome = f"Esporangio_{k + 1}"
        vs = fino(nome)
        ops = [('U', ('cap', b, t, 0.12, 0.1), lambda P, b=b, t=t: cor_seg(b, t, 0.12, 0.1, (F0, F1, F1), None)(P)),
               ('U', ('esf', t, r), esfera_bicolor(t, r, NO, F2, pupila=(0.04, 0.15)))]
        pecas[nome] = construir(nome, "Cefalotorax", vs, b, ops, "Rosto", 0.6)

    # --- queliceras e presas ---
    for lado, s in (("E", -1), ("D", 1)):
        nome = f"Quelicera_{lado}"
        vs = fino(nome)
        top, bot = (s * 0.42, 2.25, -3.55), (s * 0.5, 1.25, -3.95)
        ops = [('U', ('cap', top, bot, 0.37, 0.3), cor_seg(top, bot, 0.37, 0.3, (Q0, Q0, Q1), None)),
               ('U', ('cone', (s * 0.5, 1.32, -4.05), (s * 0.3, 0.5, -3.66), 0.16),
                lambda P, s=s: np.where(P[:, 1] < 0.72, PRP, PR))]
        pecas[nome] = construir(nome, "Cefalotorax", vs, top, ops, "Rosto", 1.1)
        p1a, p1b, p2b = (s * 0.85, 2.35, -3.45), (s * 1.25, 2.05, -4.25), (s * 1.15, 1.35, -4.6)
        pecas[f"Palpo1_{lado}"] = construir(f"Palpo1_{lado}", "Cefalotorax", vs_grade, p1a,
                                            [('U', ('cap', p1a, p1b, 0.18, 0.16), cor_seg(p1a, p1b, 0.18, 0.16))], "Rosto", 1.1)
        pecas[f"Palpo2_{lado}"] = construir(f"Palpo2_{lado}", f"Palpo1_{lado}", vs_grade, p1b,
                                            [('U', ('cap', p1b, p2b, 0.17, 0.11), cor_seg(p1b, p2b, 0.17, 0.11))], "Rosto", 1.1)

    # --- abdomen rachado com coroa de fungos ---
    def y_topo(x, z):
        return 4.15 + 2.15 * math.sqrt(max(0.0, 1 - (x / 2.55) ** 2 - ((z - 4.05) / 2.45) ** 2))
    def x_lado(y, z):
        return 2.55 * math.sqrt(max(0.0, 1 - ((y - 4.15) / 2.15) ** 2 - ((z - 4.05) / 2.45) ** 2))
    fenda_c, fenda_r = np.array([0, 6.05, 3.35]), np.array([0.95, 1.75, 2.45])
    def fenda(P, inflar=1.0):
        D = (P - fenda_c) / (fenda_r * inflar)
        return (D ** 2).sum(1) <= 1 + 0.35 * (ruido(P, 2.2, seed=11) - 0.5)
    def guelras(P):
        return np.where(np.floor(P[:, 2] / 0.25) % 2 == 0, LAM, F0)
    def nucleo(P):
        D = (P - np.array([0, 4.85, 3.35])) / np.array([0.75, 0.5, 1.75])
        return np.where((D ** 2).sum(1) < 0.45, NUC, NO)
    ops = [('U', ('cap', (0, 3.0, 0.2), (0, 3.2, 0.95), 0.46), Q0),
           ('U', ('ell', (0, 3.75, 2.55), (2.15, 1.85, 2.15)), faixas(3.75, 1.85)),
           ('U', ('ell', (0, 4.15, 4.05), (2.55, 2.15, 2.45)), faixas(4.15, 2.15)),
           ('P', lambda P: (P[:, 1] > 3.3) & (np.mod(P[:, 2] + 0.85 * np.abs(P[:, 0]), 1.05) < 0.2) & (P[:, 2] > 1.2), Q3),
           ('P', lambda P: fenda(P, 1.13), guelras),
           ('C', lambda P: fenda(P), None),
           ('U', ('ell', (0, 4.85, 3.35), (0.75, 0.5, 1.75)), nucleo)]
    prateleiras = [(3.0, 2.3, 1.1, 0.75), (3.6, 3.5, 1.25, 0.85), (4.2, 4.7, 1.05, 0.75), (2.55, 4.2, 0.95, 0.65), (4.75, 5.6, 0.8, 0.55)]
    for s in (-1, 1):
        for k, (y, z, rx, rz) in enumerate(prateleiras):
            if s > 0:
                y, z = y + 0.25 * (k % 2), z - 0.3
            c = (s * (x_lado(y, z) + 0.12), y, z)
            ops.append(('U', ('ell', c, (rx, 0.2, rz)), lambda P, c=c: np.where(P[:, 1] > c[1] + 0.04, F2, np.where(P[:, 1] > c[1] - 0.06, F1, LAM))))
    tubos = [(-0.95, 2.0, 1.3, 0.22, 'cano'), (0.9, 2.35, 2.0, 0.26, 'torre'), (-1.05, 2.9, 2.6, 0.3, 'torre'),
             (1.1, 3.3, 1.7, 0.24, 'cano'), (-0.85, 3.85, 1.9, 0.25, 'cano'), (0.95, 4.2, 3.0, 0.32, 'torre'),
             (-1.0, 4.75, 1.5, 0.22, 'cano'), (0.75, 5.1, 1.1, 0.2, 'cano'), (-0.6, 5.45, 0.9, 0.18, 'cano')]
    for (x, z, h, r, tipo) in tubos:
        yb = y_topo(x, z)
        base, topo = (x, yb - 0.35, z), (x * 1.12, yb + h, z)
        ops.append(('U', ('cap', base, topo, r, r * (0.72 if tipo == 'torre' else 1.0)),
                    cor_seg(base, topo, r, r, (F0, F1, F2), None, listras=0.36)))
        if tipo == 'torre':
            ponta = (x * 1.14, yb + h + 0.75, z)
            ops.append(('U', ('cone', topo, ponta, r * 0.78), lambda P, yb=yb, h=h: np.where(P[:, 1] > yb + h + 0.5, NO, F1)))
        else:
            ops.append(('C', ('cap', (x * 1.12, yb + h - 0.4, z), (x * 1.12, yb + h + 0.3, z), r * 0.55), None))
            ops.append(('U', ('esf', (x * 1.11, yb + h - 0.42, z), r * 0.5), NO))
    for (x, z, alt, r, pin) in [(-1.35, 1.55, 0.75, 0.55, [(-1.5, 0.25, -0.1), (-1.2, 0.3, 0.15)]),
                                 (1.45, 1.85, 0.95, 0.6, [(1.3, 0.3, 0.0), (1.65, 0.25, 0.2)]),
                                 (0.25, 1.05, 0.6, 0.42, [(0.2, 0.25, -0.05)])]:
        yb = y_topo(x, z)
        cc = (x, yb + alt, z)
        ops.append(('U', ('cap', (x, yb - 0.3, z), cc, 0.13), F1))
        ops.append(('U', ('ell', cc, (r, 0.24, r)), cogumelo(cc, r, pintas=[(px, cc[1] + py, z + pz) for px, py, pz in pin])))
    abd = construir("Abdomen", "Cefalotorax", vs_grade, (0, 3.0, 0.35), ops, "Corpo", 0.9)
    def dir_veio_abd(P):
        return _unit(np.array([np.sign(P[0]) * 0.8 + 1e-3, -1.0, 0.15 * math.sin(P[2] * 3)]))
    sementes = [(sx * 0.95, 5.6, z) for sx in (-1, 1) for z in (2.0, 3.3, 4.5, 5.3)]
    caminhar_veios(abd, sementes, 24, dir_veio_abd, seed=7, ramo=0.05)
    pecas["Abdomen"] = abd

    # --- Titereiro preso na fenda ---
    def corpo_tit(P):
        return np.where(P[:, 1] < 5.5, TS, TC)
    pin = [(0.4, 7.45, 2.85), (-0.45, 7.4, 3.3), (0.1, 7.55, 3.55)]
    ops = [('U', ('cap', (0, 4.6, 3.35), (0, 6.45, 3.15), 0.5, 0.38), corpo_tit)]
    ops += [('U', ('cap', (0, 4.9, 3.35), (sx * 0.7, 4.7, sz), 0.12), TS) for sx, sz in ((-1, 2.5), (1, 2.6), (-1, 4.2), (1, 4.3))]
    ops += [('U', ('ell', (0, 6.95, 3.1), (0.95, 0.16, 0.95)), LAM),
            ('U', ('ell', (0, 7.22, 3.1), (1.05, 0.42, 1.05)), cogumelo((0, 7.22, 3.1), 1.05, pintas=pin)),
            ('U', ('ell', (0, 6.62, 2.8), (0.36, 0.3, 0.14)), TS)]
    ops += [('U', ('esf', c, 0.075), NO) for c in ((-0.14, 6.68, 2.67), (0.14, 6.68, 2.67), (0, 6.52, 2.68))]
    ops += [('U', ('ell', (0, 6.05 - 0.45 * k, 3.66), (0.55 - 0.08 * k, 0.12, 0.3)), F1) for k in range(3)]
    pecas["Titereiro"] = construir("Titereiro", "Abdomen", vs_grade, (0, 4.9, 3.35), ops, "Titereiro", 0.6)
    PONTAS = {}
    for lado, s in (("E", -1), ("D", 1)):
        ombro, cotovelo, mao = np.array([s * 0.42, 6.25, 3.2]), np.array([s * 1.15, 7.0, 2.95]), np.array([s * 1.55, 7.9, 2.7])
        ops = [('U', ('cap', ombro, cotovelo, 0.16, 0.14), TC), ('U', ('cap', cotovelo, mao, 0.14, 0.12), TC), ('U', ('esf', mao, 0.18), TS)]
        for k in range(4):
            ponta = mao + np.array([s * 0.32, 0.12 - 0.09 * k, -0.36 + 0.24 * k])
            PONTAS[f"Perna{k + 1}_{lado}"] = ponta
            ops.append(('U', ('cap', mao, ponta, 0.06, 0.045), VEIO))
        pecas[f"Titereiro_Braco_{lado}"] = construir(f"Titereiro_Braco_{lado}", "Titereiro", vs_susto, ombro, ops, "Titereiro", 0.6)

    # --- pernas ---
    for L in PERNAS:
        n, s = L["nome"], L["s"]
        prot = L["protese"]
        cores = (MIC0, MIC, MIC) if prot else (Q0, Q1, Q2)
        anel = MIC0 if prot else Q3
        k_r = 0.8 if prot else 1.0
        rc, rf0, rf1, rt0, rt1, rs0, rs1 = (x * k_r for x in (0.4, 0.38, 0.32, 0.31, 0.23, 0.22, 0.08))
        b, q, j, t, pe = L["base"], L["quadril"], L["joelho"], L["tornozelo"], L["pe"]
        pecas[f"{n}_Coxa"] = construir(f"{n}_Coxa", "Cefalotorax", vs_grade, b,
                                       [('U', ('cap', b, q, rc, rc * 0.95), cor_seg(b, q, rc, rc, cores, anel))], n, 1.1)
        ops = [('U', ('cap', q, j, rf0, rf1), cor_seg(q, j, rf0, rf1, cores, anel, listras=0.3 if prot else None)),
               ('U', ('esf', q, rf0 + vs_grade), cores[1])]
        up, fora = cima_perp(j - q), _unit(np.cross(_unit(j - q), np.array([0, 1.0, 0]))) * -s
        if prot:
            ops += [('U', ('esf', q + (j - q) * tt + up * rf0 * 0.6, 0.2), F1) for tt in (0.3, 0.55, 0.8)]
        else:
            for tt in (0.35, 0.6, 0.85):
                bb = q + (j - q) * tt + up * (rf0 * 0.8)
                ops.append(('U', ('cone', bb, bb + up * 0.45 + fora * 0.12, 0.1), ESP))
        fem = construir(f"{n}_Femur", f"{n}_Coxa", vs_grade, q, ops, n, 0.6 if prot else 1.1)
        veio_linha(fem, q, j, rf0, rf1, fora, ate=0.92)
        pecas[f"{n}_Femur"] = fem
        ops = [('U', ('cap', j, t, rt0, rt1), cor_seg(j, t, rt0, rt1, cores, anel, listras=0.3 if prot else None)),
               ('U', ('esf', j, rt0 + vs_grade), cores[1])]
        upt = cima_perp(t - j)
        if not prot:
            for tt in (0.3, 0.62):
                bb = j + (t - j) * tt + upt * (rt0 * 0.8)
                ops.append(('U', ('cone', bb, bb + upt * 0.32 + fora * 0.1, 0.08), ESP))
        tib = construir(f"{n}_Tibia", f"{n}_Femur", vs_grade, j, ops, n, 0.6 if prot else 1.1)
        if L["lado"] == "E" or prot:
            veio_linha(tib, j, t, rt0, rt1, fora, ate=0.45 if not prot else 0.95)
        pecas[f"{n}_Tibia"] = tib
        garra = pe + L["dir"] * 0.12 + np.array([0, -0.02, 0])
        ops = [('U', ('cap', t, pe, rs0, rs1), cor_seg(t, pe, rs0, rs1, cores, None)),
               ('U', ('esf', t, rs0 + vs_grade), cores[1]),
               ('U', ('cone', pe - L["dir"] * 0.15 + np.array([0, 0.1, 0]), garra, 0.08), ESP if not prot else MIC0)]
        pecas[f"{n}_Tarso"] = construir(f"{n}_Tarso", f"{n}_Tibia", vs_grade, t, ops, n, 0.6 if prot else 1.1)
        vs = fino(f"No_{n}")
        bolhas = [(j + up * 0.28, 0.3), (j + up * 0.18 + fora * 0.26, 0.22), (j + up * 0.4 - _unit(j - q) * 0.22, 0.18), (j + fora * 0.32 - up * 0.04, 0.16)]
        L["ancora"] = j + up * 0.5
        pecas[f"No_{n}"] = construir(f"No_{n}", f"{n}_Femur", vs, j, [('U', ('esf', c, r), bolha(c, r)) for c, r in bolhas], n, 0.7)

    soltos = {nome: p.limpar_soltos() for nome, p in pecas.items()}
    for nome, p in pecas.items():
        if nome in ("Cefalotorax", "Abdomen") or nome.endswith(("_Coxa", "_Femur", "_Tibia")):
            realce_topo(p)
    return pecas, PONTAS, soltos

def realce_topo(p, de=(Q1, Q2), para=Q3):
    """Pintura a mao: so a crista (maximo local do mapa de altura em x ou em z) ganha a borda clara."""
    s = p.g > 0
    ny = s.shape[1]
    ys = np.where(s.any(1), ny - 1 - np.argmax(s[:, ::-1, :], axis=1), -1)
    def maxloc(a, eixo):
        f = np.full_like(a, -1)
        ant = np.roll(a, 1, eixo); pos = np.roll(a, -1, eixo)
        return (a >= ant) & (a >= pos)
    crista = (maxloc(ys, 0) | maxloc(ys, 1)) & (ys >= 0)
    xi, zi = np.nonzero(crista)
    yi = ys[xi, zi]
    m = np.isin(p.g[xi, yi, zi], de)
    p.g[xi[m], yi[m], zi[m]] = para

# ---------------- heroi e chao para escala ----------------
def heroi(origem=(0, 0, 0), vs=0.125):
    o = np.asarray(origem, float)
    A, AC, PE, CA = K["heroi_armadura"], K["heroi_armadura_clara"], K["heroi_pele"], K["heroi_cabelo"]
    def cabeca(P):
        c = np.where(P[:, 1] > o[1] + 3.25, CA, PE)
        olho = (np.abs(np.abs(P[:, 0] - o[0]) - 0.32) < 0.07) & (np.abs(P[:, 1] - (o[1] + 2.85)) < 0.12) & (P[:, 2] < o[2] - 0.7)
        return np.where(olho, Q0, c)
    ops = [('U', ('ell', o + (0, 1.55, 0), (0.55, 0.52, 0.42)), lambda P: np.where(P[:, 1] > o[1] + 1.75, AC, A)),
           ('U', ('ell', o + (0, 2.9, 0), (0.9, 0.85, 0.85)), cabeca)]
    ops += [('U', ('esf', o + (s * 0.85, 1.45, -0.1), 0.26), PE) for s in (-1, 1)]
    ops += [('U', ('ell', o + (s * 0.3, 0.2, -0.05), (0.24, 0.2, 0.33)), A) for s in (-1, 1)]
    ops += [('U', ('cap', o + (0.95, 1.35, -0.35), o + (0.95, 0.85, -0.45), 0.16), NUC)]
    return construir("Heroi", None, vs, o + (0, 1.5, 0), ops, "Heroi", 1.0)

def chao(lx=28, lz=20, vs=0.25, centro=(0, 0, 0), micelio_c=None, micelio_r=6.0):
    c = np.asarray(centro, float)
    p = Peca("Chao", None, vs, c + (-lx / 2, -0.25, -lz / 2), c + (lx / 2, 0.0, lz / 2), c)
    p.g[:] = K["pedra"]
    P = p.P
    tx, tz = np.floor((P[:, 0] + 1000) / 4), np.floor((P[:, 2] + 1000) / 4)
    cor = np.where((tx + tz) % 2 == 0, K["pedra"], K["pedra_clara"])
    borda = (np.abs(((P[:, 0] + 1000) % 4) - 0.125) < 0.13) | (np.abs(((P[:, 2] + 1000) % 4) - 0.125) < 0.13)
    cor = np.where(borda, K["rejunte"], cor)
    if micelio_c is not None:
        d = np.linalg.norm((P - np.asarray(micelio_c))[:, [0, 2]], axis=1)
        nz = ruido(P * np.array([1, 0, 1]), 0.9, seed=5)
        m = d < micelio_r * (0.75 + 0.5 * nz)
        fio = np.abs(ruido(P * np.array([1, 0, 1]), 1.7, seed=9) - 0.5) < 0.035
        fio2 = np.abs(ruido(P * np.array([1, 0, 1]), 3.1, seed=4) - 0.5) < 0.03
        cor = np.where(m, np.where(fio, VEIO, np.where(fio2, MIC0, np.where(nz > 0.6, Q0, Q1))), cor)
    p.g[:] = np.where(P[:, 1] < 0, cor, 0).reshape(p.dims)
    return p
