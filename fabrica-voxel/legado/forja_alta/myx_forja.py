"""Esteira da Myxilia: poses, marcha de marionete, testes P1, renders e exportacao."""
import sys, os, json, math, itertools, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import (faces, render, camera_orto, camera_persp, rot_eixo, compor, aplicar, segmento, IDENT, _unit,
                      malha_da_peca, salvar_glb, salvar_vox, paleta_png, Peca)
from myx_modelo import (pecas_myxilia, PERNAS, RGB, EMIS, HEX, FICHA, PAL, ik2, heroi, chao, NO, NUC)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida")
os.makedirs(OUT, exist_ok=True)
G = 196.2
Y = np.array([0, 1.0, 0]); X = np.array([1.0, 0, 0]); Z = np.array([0, 0, 1.0])
FWD = np.array([0, 0, -1.0])
t0 = time.time()
PG, PONTAS, SOLTOS_G = pecas_myxilia(corte="grade")
PS, _, SOLTOS_S = pecas_myxilia(corte="susto")
NOMES = list(PG.keys())
FG = {n: faces(p) for n, p in PG.items()}
FS = {n: faces(p) for n, p in PS.items()}
LEG = {L["nome"]: L for L in PERNAS}
RAIZ = PG["Cefalotorax"].pivo
print("construcao %.1fs" % (time.time() - t0))

def ordem():
    out, feito = [], set()
    def v(n):
        if n in feito:
            return
        if PG[n].pai:
            v(PG[n].pai)
        feito.add(n); out.append(n)
    for n in NOMES:
        v(n)
    return out
ORDEM = ordem()

def perna_de(n):
    for L in PERNAS:
        if n.startswith(L["nome"] + "_") or n == "No_" + L["nome"]:
            return L
    return None

def plano(a, b, c):
    return _unit(np.cross(np.asarray(b) - a, np.asarray(c) - a))

def T_local(R, p):
    return (R, np.asarray(p, float) - R @ np.asarray(p, float))

def montar(T_corpo, pernas, locais):
    T = {}
    for n in ORDEM:
        p = PG[n]
        if n == "Cefalotorax":
            T[n] = T_corpo
            continue
        L = perna_de(n)
        if L is not None and n.endswith(("_Femur", "_Tibia", "_Tarso")):
            a = pernas[L["nome"]]
            N0 = plano(L["quadril"], L["joelho"], L["tornozelo"])
            N1 = plano(a["quadril"], a["joelho"], a["tornozelo"])
            if n.endswith("_Femur"):
                T[n] = segmento(L["quadril"], L["joelho"], N0, a["quadril"], a["joelho"], N1)
            elif n.endswith("_Tibia"):
                T[n] = segmento(L["joelho"], L["tornozelo"], N0, a["joelho"], a["tornozelo"], N1)
            else:
                T[n] = segmento(L["tornozelo"], L["pe"], N0, a["tornozelo"], a["pe"], N1)
            continue
        if n.startswith("No_"):
            T[n] = T[L["nome"] + "_Femur"]
            continue
        R = locais.get(n)
        T[n] = compor(T[p.pai], T_local(R, p.pivo)) if R is not None else T[p.pai]
    return T

def corpo(desloc, R=None):
    R = np.eye(3) if R is None else R
    return (R, RAIZ + np.asarray(desloc, float) - R @ RAIZ)

def perna_agora(L, Tc, pe, dica):
    quad = aplicar(Tc, L["quadril"])
    torn = pe - Tc[0] @ (L["pe"] - L["tornozelo"])
    alc = np.linalg.norm(torn - quad) / (L["Lf"] + L["Lt"])
    return dict(quadril=quad, joelho=ik2(quad, torn, L["Lf"], L["Lt"], dica), tornozelo=torn, pe=pe, alcance=alc)

GRUPO_A = {"Perna1_E", "Perna2_D", "Perna3_E", "Perna4_D"}

def perfil(sig):
    if sig < 0.25:
        return math.sin(math.pi / 2 * sig / 0.25)
    if sig < 0.8:
        return 1.0
    return 1 - ((sig - 0.8) / 0.2) ** 2

def suave(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def marcha(t, v, T, beta=0.6, h=1.1, A=0.55, cortadas=(), tremor=0.0):
    """Marcha de marionete: tetrapode alternado, arrancos sincronizados com o ciclo, pe puxado pelo fio."""
    s = lambda tt: v * (tt - A * T / (2 * math.pi) * math.sin(2 * math.pi * tt / T))
    nE = sum(1 for c in cortadas if c.endswith("_E")); nD = len(cortadas) - nE
    bob = -0.07 * abs(math.sin(2 * math.pi * 2 * t / T))
    R = rot_eixo(Z, -math.radians(4.5) * (nD - nE)) @ rot_eixo(X, math.radians(1.5) * math.sin(2 * math.pi * t / T))
    Tc = corpo(FWD * s(t) + np.array([0, bob - 0.14 * len(cortadas), 0]), R)
    pernas, levant = {}, {"E": [], "D": []}
    for L in PERNAS:
        n = L["nome"]
        if n in cortadas:
            rel = (L["pe"] - np.array([0, 0, -1.4])) * 0.72 + np.array([0, 0, -1.4 + 0.9])
            pe = rel + FWD * s(t)
            pe[1] = 0.0
            dica = Tc[0] @ (0.15 * Y + L["dir"])
            pernas[n] = perna_agora(L, Tc, pe, dica)
            continue
        off = 0.0 if n in GRUPO_A else 0.5
        ph = t / T + off
        c = math.floor(ph); phi = ph - c
        def F(cc):
            ta = (cc - off) * T
            return L["pe"] + FWD * (s(ta) + (s(ta + beta * T) - s(ta)) / 2)
        lift = 0.0
        if phi < beta:
            pe = F(c)
        else:
            sig = (phi - beta) / (1 - beta)
            a0, a1 = F(c), F(c + 1)
            pe = a0 + (a1 - a0) * suave((sig - 0.15) / 0.6)
            lift = h * perfil(sig)
            pe = pe + np.array([0, lift, 0])
        levant[L["lado"]].append(lift / h)
        ponta = aplicar(Tc, PONTAS[n])
        quad = aplicar(Tc, L["quadril"])
        dica = _unit(Tc[0] @ Y + 0.9 * (lift / h) * _unit(ponta - quad))
        pernas[n] = perna_agora(L, Tc, pe, dica)
    loc = {"Abdomen": rot_eixo(X, math.radians(-6) * math.sin(2 * math.pi * t / T + 0.6) + math.radians(2.5) * len(cortadas))}
    for k in range(3):
        loc[f"Esporangio_{k + 1}"] = rot_eixo(X, math.radians(7) * math.sin(2 * math.pi * 2 * t / T + k * 1.7))
    for lado, sgn in (("E", -1), ("D", 1)):
        m = np.mean(levant[lado]) if levant[lado] else 0.0
        loc[f"Titereiro_Braco_{lado}"] = rot_eixo(X, -0.45 * m)
        loc[f"Quelicera_{lado}"] = rot_eixo(Z, sgn * math.radians(4 + 3 * math.sin(2 * math.pi * t / T)))
    return montar(Tc, pernas, loc), pernas, Tc

def pose_susto():
    R = rot_eixo(X, math.radians(16))
    Tc = corpo(np.array([0, 0.35, -1.0]), R)
    pernas = {}
    for L in PERNAS:
        n = L["nome"]
        quad = aplicar(Tc, L["quadril"])
        if L["i"] == 0:
            pe = quad + np.array([L["s"] * 2.3, 3.2, -1.6])
            dica = _unit(Y + 0.6 * L["s"] * X)
        else:
            pe = L["pe"].copy()
            dica = Tc[0] @ Y
        pernas[n] = perna_agora(L, Tc, pe, dica)
    loc = {"Esporangio_1": rot_eixo(X, math.radians(-20)), "Esporangio_2": rot_eixo(X, math.radians(-14)),
           "Esporangio_3": rot_eixo(X, math.radians(-22)), "Abdomen": rot_eixo(X, math.radians(5))}
    for lado, sgn in (("E", -1), ("D", 1)):
        loc[f"Quelicera_{lado}"] = rot_eixo(X, math.radians(20)) @ rot_eixo(Z, sgn * math.radians(28))
        loc[f"Titereiro_Braco_{lado}"] = rot_eixo(X, -0.4)
    return montar(Tc, pernas, loc), pernas, Tc

def itens(T, faces_dict, extras=()):
    out = [(faces_dict[n], T[n][0], T[n][1]) for n in NOMES]
    return out + list(extras)

def fios(T, cortadas=(), cor=(1.0, 0.42, 0.36), larg=1, curva=0.12):
    out = []
    for L in PERNAS:
        if L["nome"] in cortadas:
            continue
        braco = "Titereiro_Braco_" + L["lado"]
        a = aplicar(T[braco], PONTAS[L["nome"]])
        b = aplicar(T[L["nome"] + "_Femur"], L["ancora"])
        out.append((a, b, cor, larg, curva))
    return out

def fundo_escuro(W, H, topo=(34, 28, 38), base=(8, 7, 10)):
    y = np.linspace(0, 1, H)[:, None, None]
    x = np.linspace(-1, 1, W)[None, :, None]
    c = np.array(topo) * (1 - y) + np.array(base) * y
    vin = 1 - 0.35 * (x ** 2) * np.ones((H, 1, 1))
    return Image.fromarray(np.clip(c * vin, 0, 255).astype(np.uint8))

# ================= TESTES P1 =================
rel = {"pecas": {}, "juntas": [], "equilibrio": {}, "froude": {}, "valores": {}, "marcha": {}}
# triangulos e malhas
MALHAS = {}
for corte, PP in (("grade", PG), ("susto", PS)):
    tot = 0
    for n, p in PP.items():
        base = malha_da_peca(p, [c for c in range(1, len(HEX)) if c not in EMIS])
        brilho = malha_da_peca(p, sorted(EMIS))
        MALHAS[(corte, n)] = (base, brilho)
        tb = 0 if base is None else len(base["idx"]) // 3
        tg = 0 if brilho is None else len(brilho["idx"]) // 3
        tot += tb + tg
        rel["pecas"].setdefault(n, {})[corte] = dict(voxels=p.n(), vs=p.vs, tris=tb, tris_brilho=tg)
    rel[f"tris_total_{corte}"] = tot
rel["maior_malha"] = max((max(v[c]["tris"], v[c]["tris_brilho"]), n, c) for n, v in rel["pecas"].items() for c in ("grade", "susto"))
rel["soltos_removidos"] = dict(grade=sum(SOLTOS_G.values()), susto=sum(SOLTOS_S.values()))
# juntas com sobreposicao
for n in NOMES:
    p = PG[n]
    if not p.pai:
        continue
    pai = PG[p.pai]
    r = 0.3
    sp, sf = pai.solido(), p.solido()
    n_pai = int((((pai.P[sp] - p.pivo) ** 2).sum(1) <= r * r).sum())
    n_filho = int((((p.P[sf] - p.pivo) ** 2).sum(1) <= r * r).sum())
    rel["juntas"].append(dict(peca=n, pai=p.pai, voxels_pai=n_pai, voxels_filho=n_filho, ok=bool(n_pai >= 4 and n_filho >= 4)))
# equilibrio
massa = {n: p.massa() for n, p in PG.items()}
com = sum(massa[n] * PG[n].centro_massa() for n in NOMES) / sum(massa.values())
rel["equilibrio"]["massa_rmu"] = round(sum(massa.values()), 1)
rel["equilibrio"]["centro_massa"] = [round(float(x), 2) for x in com]

def casco(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]

def margem(pt, poli):
    if len(poli) < 3:
        return -9.0
    m = 9e9
    for i in range(len(poli)):
        a, b = np.array(poli[i]), np.array(poli[(i + 1) % len(poli)])
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        m = min(m, float((np.asarray(pt) - a) @ -nrm))
    return m

cxz = com[[0, 2]]
pes = {L["nome"]: L["pe"][[0, 2]] for L in PERNAS}
todos = casco(list(pes.values()))
rel["equilibrio"]["margem_8_pernas"] = round(margem(cxz, todos), 2)
quedas = {}
exemplos_cai, exemplos_fica = {}, {}
for k in range(0, 9):
    n_tot = n_cai = 0
    for combo in itertools.combinations(pes.keys(), k):
        resto = [pes[n] for n in pes if n not in combo]
        mg = margem(cxz, casco(resto)) if len(resto) >= 3 else -9
        cai = mg < 0.0
        n_tot += 1; n_cai += cai
        rel["equilibrio"].setdefault("cambaleia_por_cortes", {}).setdefault(k, 0)
        rel["equilibrio"]["cambaleia_por_cortes"][k] += int(0.0 <= mg < 0.3)
        if cai and k not in exemplos_cai:
            exemplos_cai[k] = list(combo)
        if not cai:
            exemplos_fica[k] = list(combo)
    quedas[k] = (n_cai, n_tot)
rel["equilibrio"]["quedas_por_cortes"] = {k: f"{a}/{b}" for k, (a, b) in quedas.items()}
rel["equilibrio"]["menor_corte_que_derruba"] = min((k for k, (a, b) in quedas.items() if a > 0), default=None)
rel["equilibrio"]["exemplo_derruba"] = exemplos_cai
rel["equilibrio"]["exemplo_fica"] = {k: v for k, v in exemplos_fica.items() if k >= 3}
lado_E = [n for n in pes if n.endswith("_E")]
rel["equilibrio"]["4_de_um_lado"] = round(margem(cxz, casco([pes[n] for n in pes if n not in lado_E])), 2)
# froude
L_quadril = float(np.mean([L["quadril"][1] for L in PERNAS]))
for nome, fr in (("espreita", FICHA["marcha"]["fr_espreita"]), ("investida", FICHA["marcha"]["fr_investida"])):
    rel["froude"][nome] = dict(Fr=fr, v_studs_s=round(math.sqrt(fr * G * L_quadril), 2))
rel["froude"]["altura_quadril"] = round(L_quadril, 2)
rel["froude"]["walkspeed_heroi_padrao"] = 16
# valores (faces de superficie por cor)
cont = np.zeros(len(HEX))
for f in FG.values():
    if f is not None:
        cont += np.bincount(f["cor"], minlength=len(HEX))
lum = RGB @ np.array([0.2126, 0.7152, 0.0722])
emis = np.isin(np.arange(len(HEX)), list(EMIS))
tot = cont.sum()
rel["valores"] = dict(escuro=round(100 * cont[(lum < 0.25) & ~emis].sum() / tot, 1),
                      medio=round(100 * cont[(lum >= 0.25) & (lum < 0.55) & ~emis].sum() / tot, 1),
                      claro=round(100 * cont[(lum >= 0.55) & ~emis].sum() / tot, 1),
                      brilho=round(100 * cont[emis].sum() / tot, 1))
# marcha: alcance, joelho, deslizamento
V_ESP = rel["froude"]["espreita"]["v_studs_s"]
PASSO = 2.4
T_CICLO = PASSO / V_ESP
rel["marcha"]["periodo_s"] = round(T_CICLO, 3)
rel["marcha"]["passo_studs"] = PASSO
alc_max, ang_min, ang_max, invertido, desliz = 0, 999, 0, 0, 0.0
pe_ant = {}
for i in range(64):
    t = i / 64 * T_CICLO * 2
    T, pern, Tc = marcha(t, V_ESP, T_CICLO)
    for n, a in pern.items():
        alc_max = max(alc_max, a["alcance"])
        u1, u2 = a["quadril"] - a["joelho"], a["tornozelo"] - a["joelho"]
        ang = math.degrees(math.acos(np.clip(u1 @ u2 / np.linalg.norm(u1) / np.linalg.norm(u2), -1, 1)))
        ang_min, ang_max = min(ang_min, ang), max(ang_max, ang)
        meio = (a["quadril"] + a["tornozelo"]) / 2
        if a["joelho"][1] < meio[1]:
            invertido += 1
        if a["pe"][1] < 1e-6 and n in pe_ant and pe_ant[n][1] < 1e-6:
            desliz = max(desliz, float(np.linalg.norm(a["pe"] - pe_ant[n])) if np.linalg.norm(a["pe"] - pe_ant[n]) < 0.5 else desliz)
        pe_ant[n] = a["pe"]
rel["marcha"].update(alcance_max=round(alc_max, 3), angulo_joelho=[round(ang_min, 1), round(ang_max, 1)],
                     joelho_invertido=invertido, deslizamento_max=round(desliz, 4))
json.dump(rel, open(os.path.join(OUT, "relatorio_p1.json"), "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: v for k, v in rel.items() if k not in ("pecas", "juntas")}, ensure_ascii=False, default=float))
print("juntas ok:", sum(j["ok"] for j in rel["juntas"]), "/", len(rel["juntas"]), " pior:", min(rel["juntas"], key=lambda j: min(j["voxels_pai"], j["voxels_filho"])))
print("testes %.1fs" % (time.time() - t0))

# ================= RENDERS =================
def salvar(img, nome):
    img.save(os.path.join(OUT, nome))
    return nome

T0 = {n: IDENT for n in NOMES}
F0 = fios(T0)
# 1. arte principal
W, H = 1400, 860
cam = camera_orto((0.5, -0.2, 0.85), Y, (0.3, 3.0, -0.9), 54, W, H)
piso_arte = chao(lx=30, lz=30, vs=0.25, centro=(0, 0, -1), micelio_c=(0, 0, 0.5), micelio_r=7.5)
salvar(render(itens(T0, FG, [(faces(piso_arte), np.eye(3), np.zeros(3))]), cam, RGB, EMIS, img_fundo=fundo_escuro(W, H),
              bloom=0.8, fios=F0, ambiente=0.5, neblina=((0.03, 0.025, 0.035), 6.0, 26.0)), "arte.png")
# 2. planta tecnica
vistas = {"frente": ((0, 0, 1), Y, 460, 280), "lado_a": ((1, 0, 0), Y, 460, 280), "costas": ((0, 0, -1), Y, 460, 280),
          "lado_b": ((-1, 0, 0), Y, 460, 280), "topo": ((0, -1, 0), (0, 0, -1), 460, 420)}
for nome, (d, up, w, h) in vistas.items():
    c = (0, 0, -0.6) if nome == "topo" else (0, 4.9, -0.6)
    cam = camera_orto(d, up, c, 21, w, h)
    salvar(render(itens(T0, FG), cam, RGB, EMIS, fundo=(0.94, 0.94, 0.94), bloom=0.35, fios=F0,
                  grade_fundo=4, chao_y=None if nome == "topo" else 0.0), f"vista_{nome}.png")
# 3. cortes: grade x susto no rosto
for nome, F in (("grade", FG), ("susto", FS)):
    cam = camera_orto((0, -0.12, 1), Y, (0, 3.15, -3.9), 96, 440, 330)
    salvar(render(itens(T0, F), cam, RGB, EMIS, fundo=(0.16, 0.15, 0.17), bloom=0.45, ambiente=0.55), f"corte_{nome}.png")
# 4. escala na grade (camera do jogo, 720p, S = 30 studs)
hero = heroi(); FH = faces(hero)
piso = chao(lx=46, lz=38, vs=0.25, centro=(-1, 0, -4), micelio_c=(0, 0, 0.5), micelio_r=7.5); FP_ = faces(piso)
pos_h = np.array([-4.5, 0, -11.0]); Rh = rot_eixo(Y, math.pi)
extras = [(FH, Rh, pos_h), (FP_, np.eye(3), np.zeros(3))]
p, yaw = math.radians(55), math.radians(30)
d = (math.cos(p) * math.sin(yaw), -math.sin(p), math.cos(p) * math.cos(yaw))
cam = camera_orto(d, Y, (-1.6, 2.0, -4.0), 720 / 30, 1280, 720)
esc = render(itens(T0, FG, extras), cam, RGB, EMIS, fundo=(0.04, 0.04, 0.05), bloom=0.6, fios=F0, ambiente=0.48)
salvar(esc, "escala_grade.png")
from voxforja import projetar
hx, hy, _ = projetar(cam, (pos_h + np.array([1.5, 2.5, 3.0]))[None])
x0, y0 = int(hx[0]) - 150, int(hy[0]) - 110
salvar(esc.crop((x0, y0, x0 + 300, y0 + 200)).resize((900, 600), Image.NEAREST), "escala_zoom.png")
# 5. susto em primeira pessoa (corte de susto, lanterna)
Ts, pern_s, Tcs = pose_susto()
rosto = aplicar(Ts["Cefalotorax"], (0, 2.75, -3.95))
olho = rosto + np.array([0.2, -0.25, -2.5])
cam = camera_persp(olho, rosto + np.array([0, 0.45, 0.6]), Y, 70, 1280, 720)
piso2 = chao(lx=40, lz=40, vs=0.25, centro=(0, 0, -4), micelio_c=(0, 0, -1), micelio_r=8)
salvar(render(itens(Ts, FS, [(faces(piso2), np.eye(3), np.zeros(3))]), cam, RGB, EMIS, fundo=(0, 0, 0),
              lanterna=(olho + np.array([0.5, -0.9, 0.3]), 1.25, 2.6), neblina=((0.0, 0.0, 0.0), 3.5, 12.0),
              bloom=0.75, fios=fios(Ts, larg=2)), "susto_fp.png")
# 6. folha de 8 quadros da marcha
quadros = []
for k in range(8):
    t = k * T_CICLO / 8
    T, pern, Tc = marcha(t, V_ESP, T_CICLO)
    cpos = aplicar(Tc, RAIZ)
    a = render(itens(T, FG), camera_orto((1, 0, 0), Y, (0, 4.2, cpos[2]), 15, 300, 200), RGB, EMIS,
               fundo=(0.94, 0.94, 0.94), bloom=0.3, fios=fios(T), grade_fundo=4, chao_y=0.0)
    b = render(itens(T, FG), camera_orto((0, -1, 0), (0, 0, -1), (0, 0, cpos[2] - 0.6), 13, 300, 250), RGB, EMIS,
               fundo=(0.94, 0.94, 0.94), bloom=0.3, fios=fios(T), grade_fundo=4)
    q = Image.new("RGB", (300, 450), (255, 255, 255)); q.paste(a, (0, 0)); q.paste(b, (0, 200))
    quadros.append(q)
folha = Image.new("RGB", (1212, 908), (255, 255, 255))
for k, q in enumerate(quadros):
    folha.paste(q, (4 + (k % 4) * 302, 4 + (k // 4) * 452))
salvar(folha, "marcha_8_quadros.png")
# 7. equilibrio: poligono de apoio e centro de massa
def painel(cortadas, w=330, h=360):
    T, pern, Tc = marcha(0.0, V_ESP, T_CICLO, cortadas=cortadas)
    cam = camera_orto((0, -1, 0), (0, 0, -1), (0, 0, -0.7), 19, w, h)
    img = render(itens(T, FG), cam, RGB, EMIS, fundo=(0.94, 0.94, 0.94), bloom=0.25, fios=fios(T, cortadas), grade_fundo=4)
    resto = [pes[n] for n in pes if n not in cortadas]
    poli = casco(resto)
    mg = margem(cxz, poli) if len(poli) >= 3 else -9
    ok = mg >= 0.3
    meio = 0.0 <= mg < 0.3
    pts3 = np.array([[x, 0.0, z] for x, z in poli])
    px, py, _ = projetar(cam, pts3)
    dr = ImageDraw.Draw(img)
    cor = (30, 150, 70) if ok else ((225, 140, 20) if meio else (200, 40, 40))
    dr.line(list(zip(px, py)) + [(px[0], py[0])], fill=cor, width=3)
    cx_, cy_, _ = projetar(cam, np.array([[com[0], 0, com[2]]]))
    r = 7
    dr.ellipse((cx_[0] - r, cy_[0] - r, cx_[0] + r, cy_[0] + r), fill=cor, outline=(255, 255, 255), width=2)
    return img, mg
paineis = [painel(()), painel(("Perna1_D", "Perna2_D", "Perna4_D")), painel(("Perna3_E", "Perna4_E")),
           painel(("Perna1_E", "Perna2_E", "Perna3_E", "Perna4_E"))]
eq = Image.new("RGB", (4 * 332 + 2, 364), (255, 255, 255))
for k, (im, mg) in enumerate(paineis):
    eq.paste(im, (2 + k * 332, 2))
salvar(eq, "equilibrio.png")
rel["equilibrio"]["margens_paineis"] = [round(m, 2) for _, m in paineis]
# 8. animacao: marionete andando; o fio da Perna2_E arrebenta no meio
frames = []
Wa, Ha = 720, 460
bg = fundo_escuro(Wa, Ha)
for i in range(40):
    t = i / 40 * 4 * T_CICLO
    cort = ("Perna2_E",) if i >= 20 else ()
    T, pern, Tc = marcha(t, V_ESP, T_CICLO, cortadas=cort)
    cpos = aplicar(Tc, RAIZ)
    cam = camera_orto((0.62, -0.34, 0.70), Y, (cpos[0] + 0.3, 4.0, cpos[2] + 0.2), 26, Wa, Ha)
    frames.append(render(itens(T, FG), cam, RGB, EMIS, img_fundo=bg, bloom=0.7, fios=fios(T, cort), ambiente=0.5))
frames[0].save(os.path.join(OUT, "marcha.webp"), save_all=True, append_images=frames[1:], duration=int(1000 * 4 * T_CICLO / 40), loop=0, quality=82)
print("renders %.1fs" % (time.time() - t0))

# ================= EXPORTACAO =================
png = paleta_png(HEX)
open(os.path.join(OUT, "paleta.png"), "wb").write(png)
rig = {"raiz": "Cefalotorax", "unidade": "stud", "frente": "-Z", "pecas": [], "pernas": [], "fios": []}
for corte in ("grade", "susto"):
    nos = []
    for n in NOMES:
        p = (PG if corte == "grade" else PS)[n]
        base, brilho = MALHAS[(corte, n)]
        if base is not None:
            nos.append(dict(nome=n, malha=base, translacao=p.pivo, material=0))
        if brilho is not None:
            nos.append(dict(nome=n + "_Brilho", malha=brilho, translacao=p.pivo, material=1))
    tam = salvar_glb(os.path.join(OUT, f"myxilia_{corte}.glb"), nos, png, "Myxilia")
    rel[f"glb_{corte}_kb"] = round(tam / 1024)
for n in NOMES:
    p = PG[n]
    base, brilho = MALHAS[("grade", n)]
    centro = (base["pos"].min(0) + base["pos"].max(0)) / 2 + p.pivo if base is not None else p.pivo
    rig["pecas"].append(dict(nome=n, pai=p.pai or "", pivo=[round(float(x), 4) for x in p.pivo],
                             centro=[round(float(x), 4) for x in centro], brilho=brilho is not None))
for L in PERNAS:
    rig["pernas"].append(dict(nome=L["nome"], lado=L["lado"], grupo="A" if L["nome"] in GRUPO_A else "B",
                              **{k: [round(float(x), 4) for x in L[k]] for k in ("quadril", "joelho", "tornozelo", "pe", "dir", "ancora")},
                              Lf=L["Lf"], Lt=L["Lt"], ponta=[round(float(x), 4) for x in PONTAS[L["nome"]]]))
rig["marcha"] = dict(v=V_ESP, periodo=round(T_CICLO, 4), apoio=0.6, levante=1.1, arranco=0.55)
json.dump(rig, open(os.path.join(OUT, "myxilia_rig.json"), "w"), indent=1, ensure_ascii=False)
json.dump(FICHA, open(os.path.join(OUT, "myxilia_ficha.json"), "w"), indent=1, ensure_ascii=False)
# vox (pose de repouso, 0,125)
todos_pts, todas_cores = [], []
for n, p in PG.items():
    s = p.solido()
    todos_pts.append(p.P[s]); todas_cores.append(p.g.reshape(-1)[s])
Pt = np.concatenate(todos_pts); Ct = np.concatenate(todas_cores)
gi = np.floor((Pt - Pt.min(0)) / 0.125 + 1e-6).astype(int)
grade = np.zeros(gi.max(0) + 1, np.uint8)
grade[gi[:, 0], gi[:, 1], gi[:, 2]] = Ct
salvar_vox(os.path.join(OUT, "myxilia.vox"), grade, HEX)
rel["vox_dims"] = list(grade.shape)
json.dump(rel, open(os.path.join(OUT, "relatorio_p1.json"), "w"), indent=1, ensure_ascii=False, default=float)
print("exportacao %.1fs" % (time.time() - t0), rel["glb_grade_kb"], rel["glb_susto_kb"], rel["vox_dims"], rel["equilibrio"]["margens_paineis"])
