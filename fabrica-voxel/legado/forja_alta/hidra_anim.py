"""Nihilis: clipes (parado, andar, bote, rugido), P1 quadro a quadro e auditoria rigida."""
import sys, os, math, json, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hidra as Hd
from hidra import K, RGB, EMIS, X, Y, Z, NSEG, NECKS, FRAG, PERNAS
from voxforja import faces, render, camera_orto, rot_eixo, malha_gulosa
import bestiario as B

W2 = 2 * math.pi
def ease(a, b, f):
    u = min(max((f - a) / (b - a), 0.0), 1.0); return u * u * (3 - 2 * u)
def tique(t, per, dur=0.1, seed=0):
    f = (t + seed * 0.37) % per
    return math.sin(math.pi * f / dur) if f < dur else 0.0

def pose(m, clipe, t):
    L = {}; info = m["info"]
    d = np.zeros(3); Rc = np.eye(3)
    nk = len(NECKS)
    # parametros por clipe
    pitch_extra = np.zeros(nk); jaw = np.zeros(nk); core = 1.0; frag_burst = 0.0; frag_spin = 1.0; tremor = 0.0
    atk = np.zeros((nk, NSEG))     # pitch adicional por junta (negativo = para a frente)
    if clipe == "parado":
        per = 3.0
        sway = lambda k, j: (0.07 * math.sin(W2 * t / per + k * 0.9 - 0.55 * j), 0.05 * math.sin(2 * W2 * t / per + k * 1.3 - 0.7 * j))
        d = np.array([0, 0.08 * math.sin(W2 * t / per), 0]); Rc = rot_eixo(X, 0.008 * math.sin(W2 * t / per))
        core = 1 + 0.12 * math.sin(W2 * t / 1.5)
        for k in range(nk):
            jaw[k] = 0.35 * tique(t, 1.5 + 0.2 * k, 0.5, k) + 0.08
        leg = lambda nm: (0.0, 0.0)
        tail = lambda j: 0.12 * math.sin(W2 * t / per - 0.8 * j)
    elif clipe == "andar":
        per = 2.4; ph = W2 * t / per
        sway = lambda k, j: (0.06 * math.sin(ph + k * 0.9 - 0.55 * j) - 0.012 * math.sin(ph), 0.05 * math.sin(2 * ph - 0.5 * j + 0.3 * k))
        d = np.array([0.22 * math.sin(ph), 0.2 * abs(math.sin(ph)) - 0.1, 0])
        Rc = rot_eixo(Z, 0.035 * math.sin(ph)) @ rot_eixo(Y, 0.04 * math.sin(ph)) @ rot_eixo(X, 0.015 * math.sin(2 * ph))
        core = 1 + 0.08 * math.sin(2 * ph)
        for k in range(nk):
            jaw[k] = 0.15 + 0.12 * math.sin(2 * ph + k)
        def leg(nm):
            p = ph + (0 if nm in ("FE", "TD") else math.pi)
            return (0.36 * math.sin(p), -0.75 * max(0.0, math.cos(p)) ** 0.8)
        tail = lambda j: 0.2 * math.sin(ph - 0.8 * j)
    elif clipe == "bote":
        per = 2.4; f = (t % per) / per
        base = lambda k, j: (0.04 * math.sin(W2 * t / 3 + k * 0.9 - 0.55 * j), 0.04 * math.sin(2 * W2 * t / 3 + k * 1.3 - 0.7 * j))
        sway = base
        arma = ease(0.0, 0.32, f); golpe = ease(0.32, 0.46, f); volta = ease(0.62, 1.0, f)
        a_rei = arma * (1 - golpe) * (1 - volta) * 0.17 - golpe * (1 - volta) * 0.18
        for j in range(NSEG):
            atk[0, j] = a_rei
        # Ferrao (4) estoca logo depois; Olhos (5) e Costurada (6) recuam
        fe = ease(0.5, 0.58, f) * (1 - ease(0.72, 1.0, f)); fe0 = ease(0.4, 0.5, f) * (1 - ease(0.5, 0.52, f))
        for j in range(NSEG):
            atk[4, j] = 0.08 * ease(0.35, 0.5, f) * (1 - ease(0.5, 0.52, f)) * (1 - volta) - 0.19 * fe
            atk[5, j] = 0.06 * golpe * (1 - volta); atk[6, j] = 0.07 * golpe * (1 - volta)
        jaw[0] = 0.85 * ease(0.2, 0.34, f) * (1 - ease(0.52, 0.6, f)) + 0.1
        jaw[4] = 0.5 * ease(0.52, 0.58, f) * (1 - ease(0.7, 0.8, f)); jaw[1] = 0.25 * golpe * (1 - volta); jaw[3] = 0.3 * golpe * (1 - volta)
        d = np.array([0, -0.12 * golpe * (1 - volta), -0.35 * golpe * (1 - volta)]); Rc = rot_eixo(X, -0.03 * golpe * (1 - volta))
        core = 1 + 0.35 * golpe * (1 - volta)
        leg = lambda nm: (-0.1 * golpe * (1 - volta) * (1 if nm[0] == "F" else -1), 0.0)
        tail = lambda j: 0.12 * math.sin(W2 * t / 3 - 0.8 * j) + 0.25 * golpe * (1 - volta) * (j % 2 * 2 - 1) * 0.5
    else:  # rugido
        per = 3.0; f = (t % per) / per
        insp = ease(0.0, 0.3, f); roar = ease(0.3, 0.4, f) * (1 - ease(0.85, 1.0, f)); sai = ease(0.85, 1.0, f)
        base = lambda k, j: (0.05 * math.sin(W2 * t / 2 + k * 0.9 - 0.55 * j) * (0.4 + roar), 0.04 * math.sin(2 * W2 * t / 2 + k * 1.3 - 0.7 * j))
        sway = base
        arq = 0.10 * insp * (1 - roar) + 0.14 * roar
        for k in range(nk):
            for j in range(NSEG):
                atk[k, j] = arq * (0.6 + 0.2 * (k % 3))
            jaw[k] = (0.9 if k != 6 else 1.25) * roar + 0.06 * insp
        tremor = 0.012 * roar
        d = np.array([0, 0.18 * insp * (1 - roar) + 0.1 * roar + tremor * 8 * math.sin(t * 53), 0]); Rc = rot_eixo(X, 0.07 * insp * (1 - roar) + 0.05 * roar)
        core = 0.9 + 0.4 * roar - 0.2 * insp * (1 - roar)
        frag_burst = 1.0 * roar; frag_spin = 1 + 3 * roar
        leg = lambda nm: ((-0.1 * insp + 0.05 * roar) * (1 if nm[0] == "F" else -1), 0.0)
        tail = lambda j: 0.2 * math.sin(W2 * t / 1.2 - 0.8 * j) * roar + 0.1 * math.sin(W2 * t / 3 - 0.8 * j)
    # ---- pescoços e cabeças
    for k in range(nk):
        for j in range(1, NSEG + 1):
            yaw, pit = sway(k, j - 1)
            L[f"P{k}_{j}"] = rot_eixo(Y, yaw) @ rot_eixo(X, pit + atk[k, j - 1] + (pitch_extra[k] / NSEG))
        h = info[k]["h"]
        gl = tique(t, 2.3 + 0.4 * k, 0.07, k) * 0.12
        L[f"C{k}"] = rot_eixo(Y, 0.05 * math.sin(W2 * t / 3 + k) + gl) @ rot_eixo(X, 0.03 * math.sin(W2 * t / 2.4 + 2 * k))
        if h["tipo"] == "funil":
            L[f"M{k}"] = rot_eixo(h["B"][:, 2], W2 * (0.6 + 1.5 * (jaw[k] > 0.4)) * t)
        else:
            L[f"M{k}"] = rot_eixo(h["B"][:, 0], jaw[k])
    for nm, x, z in PERNAS:
        a, b = leg(nm)
        L[f"Coxa_{nm}"] = rot_eixo(X, a); L[f"Canela_{nm}"] = rot_eixo(X, b)
    for j in range(1, 6):
        L[f"Cauda{j}"] = rot_eixo(Y, tail(j))
    c = m["pecas"]["Nucleo"].pivo
    L["Nucleo"] = np.diag([core, core, core])
    T = B.montar(m, B.raiz(m, Rc, d), L)
    # fragmentos: balancam em torno do eixo vertical, giram e boiam
    for i, (tp, c0) in enumerate(FRAG):
        c0 = np.array(c0, float); fase = i * 1.3
        orb = rot_eixo(Y, 0.16 * math.sin(W2 * t / 6 + fase) * (1 + 1.5 * frag_burst))
        auto = rot_eixo(Y, 0.35 * math.sin(W2 * t / 4 * frag_spin + fase)) @ rot_eixo(Z, 0.12 * math.sin(W2 * t / 5 + fase))
        boia = np.array([0, 0.35 * math.sin(W2 * t / 3 + fase), 0]) + frag_burst * 1.2 * np.array([c0[0], 0, c0[2]]) / max(np.linalg.norm([c0[0], c0[2]]), 1)
        Tl = (orb @ auto, orb @ (c0 + boia - auto @ c0))
        Tb = T["Corpo"]
        T[f"Frag{i}"] = (Tb[0] @ Tl[0], Tb[0] @ Tl[1] + Tb[1])
    return T

# ---------------- P1: colisao por quadro ----------------
def _cod(ix):
    return ((ix[:, 0] + 4096).astype(np.int64) << 26) | ((ix[:, 1] + 4096).astype(np.int64) << 13) | (ix[:, 2] + 4096).astype(np.int64)

class Colisor:
    def __init__(self, m):
        self.m = m; self.pts = {n: p.P[p.solido()] for n, p in m["pecas"].items()}
    def quadro(self, T):
        m = self.m; pos = {}; box = {}
        for n, P in self.pts.items():
            Q = P @ T[n][0].T + T[n][1]; pos[n] = Q; box[n] = (Q.min(0), Q.max(0))
        ns = list(m["pecas"]); cache = {}; hits = []
        def codes(n, g):
            if (n, g) not in cache:
                cache[(n, g)] = np.unique(_cod(np.round(pos[n] / g).astype(int)))
            return cache[(n, g)]
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                pa, pb = m["pecas"][a], m["pecas"][b]
                if pa.pai == b or pb.pai == a:
                    continue
                if a.startswith("Frag") and b.startswith("Frag"):
                    continue
                la, ha = box[a]; lb, hb = box[b]
                if (la > hb + 0.3).any() or (lb > ha + 0.3).any():
                    continue
                g = max(pa.vs, pb.vs)
                k = len(np.intersect1d(codes(a, g), codes(b, g), assume_unique=True))
                if k:
                    hits.append((a, b, k))
        return hits

PALN = {i + 1: n for i, (n, h) in enumerate(Hd.PAL)}
CLIPES = (("parado", 3.0, 24), ("andar", 2.4, 24), ("bote", 2.4, 28), ("rugido", 3.0, 28))

VEL_ANDAR = 1.5
def auditoria(m, rapido=False, pose=None, CLIPES=None, RGB=None, EMIS=None):
    RGB = globals()['RGB'] if RGB is None else RGB; EMIS = globals()['EMIS'] if EMIS is None else EMIS
    pose = pose or globals()['pose']; CLIPES = CLIPES or globals()['CLIPES']
    rel = {"pecas": {}}
    for n, p in m["pecas"].items():
        antes = p.n(); p.limpar_soltos(); soltos = antes - p.n()
        rel["pecas"][n] = dict(vs=p.vs, voxels=p.n(), soltos=soltos, tris=2 * len(malha_gulosa(p.g)))
    m["faces"] = {n: faces(p) for n, p in m["pecas"].items()}
    juntas = []
    for n, p in m["pecas"].items():
        if p.pai and hasattr(p, "rj"):
            q = m["pecas"][p.pai]; r = 0.8 * p.rj
            ca = int((((q.P[q.solido()] - p.pivo) ** 2).sum(1) <= r * r).sum()); cb = int((((p.P[p.solido()] - p.pivo) ** 2).sum(1) <= r * r).sum())
            juntas.append((n, ca, cb))
    # nucleo cravado no corpo (veias entram na parede)
    nu, co = m["pecas"]["Nucleo"], m["pecas"]["Corpo"]
    gq = max(nu.vs, co.vs)
    cn = len(np.intersect1d(np.unique(_cod(np.round(nu.P[nu.solido()] / gq).astype(int))), np.unique(_cod(np.round(co.P[co.solido()] / gq).astype(int)))))
    rel["nucleo_cravado"] = cn
    col = {}; pior = {}
    cl = Colisor(m)
    for c, dur, n in CLIPES:
        mx = 0; quem = {}
        for i in range(n if not rapido else 6):
            hits = cl.quadro(pose(m, c, i / n * dur))
            for a, b, k in hits:
                quem[(a, b)] = max(quem.get((a, b), 0), k)
            mx = max([mx] + [k for _, _, k in hits])
        col[c] = mx; pior[c] = sorted(quem.items(), key=lambda kv: -kv[1])[:6]
    cont = np.zeros(len(RGB))
    for f in m["faces"].values():
        cont += np.bincount(f["cor"], minlength=len(RGB))
    lum = RGB @ np.array([0.2126, 0.7152, 0.0722]); em = np.isin(np.arange(len(RGB)), list(EMIS)); tot = cont.sum()
    rel["valores"] = dict(escuro=round(100 * cont[(lum < 0.25) & ~em].sum() / tot, 1), medio=round(100 * cont[(lum >= 0.25) & (lum < 0.55) & ~em].sum() / tot, 1),
                          claro=round(100 * cont[(lum >= 0.55) & ~em].sum() / tot, 1), brilho=round(100 * cont[em].sum() / tot, 2))
    rel["juntas"] = juntas; rel["colisao"] = col; rel["colisao_pares"] = {c: [[a, b, k] for (a, b), k in v] for c, v in pior.items()}
    rel["total_voxels"] = sum(v["voxels"] for v in rel["pecas"].values()); rel["total_tris"] = sum(v["tris"] for v in rel["pecas"].values())
    regras = [("Limpeza da forja apaga no maximo 0,1% de cada peca (so detritos de corte)", all(v["soltos"] <= max(8, 0.001 * (v["voxels"] + v["soltos"])) for v in rel["pecas"].values())),
              ("Juntas com pelo menos 8 voxels de cada lado", all(a >= 8 and b >= 8 for _, a, b in juntas)),
              ("Nucleo cravado no corpo (8+ voxels)", cn >= 8),
              ("Cada peca abaixo de 20 mil triangulos", all(v["tris"] <= 20000 for v in rel["pecas"].values())),
              ("Nenhuma colisao em quadro nenhum de nenhum clipe", all(v == 0 for v in col.values())),
              ("Brilho abaixo de 6% (so fendas, olhos e nucleo)", rel["valores"]["brilho"] < 6.0)]
    rel["regras"] = [(r, "passa" if ok else "falha") for r, ok in regras]
    return rel

if __name__ == "__main__":
    t0 = time.time()
    m = Hd.hidra(); rel = auditoria(m, rapido="--rapido" in sys.argv)
    json.dump(rel, open(os.path.join(OUT := B.OUT, "hidra_auditoria.json"), "w"), indent=1, ensure_ascii=False, default=float)
    for r in rel["regras"]:
        print(r)
    print("pecas", len(m["pecas"]), "voxels", rel["total_voxels"], "tris", rel["total_tris"], rel["valores"], "colisao", rel["colisao"], "nucleo", rel["nucleo_cravado"], round(time.time() - t0), "s")
    print("fracas", [j for j in rel["juntas"] if min(j[1], j[2]) < 8])
    print("soltos", {n: v["soltos"] for n, v in rel["pecas"].items() if v["soltos"]})
    for n, p in m["pecas"].items():
        if rel["pecas"][n]["soltos"] and "--solto" in sys.argv:
            q = Hd.hidra()["pecas"][n]; g0 = q.g.copy(); q.limpar_soltos(); perd = (g0 > 0) & (q.g == 0)
            print(n, "cores", {PALN[c]: int((g0[perd] == c).sum()) for c in set(g0[perd].tolist())}, "centro", q.P[perd.reshape(-1)].mean(0).round(1))
    print("tris>20k", {n: v["tris"] for n, v in rel["pecas"].items() if v["tris"] > 20000})
    for c, v in rel["colisao_pares"].items():
        if v: print(c, v)
