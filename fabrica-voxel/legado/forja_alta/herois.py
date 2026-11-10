"""Forja de herois: corpos-base, linhagens, tracos e conjuntos, com a matriz de prova."""
import sys, os, json, math, itertools
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import faces, render, camera_orto, IDENT, hex_rgb, malha_gulosa, capsula

VS = 0.125
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida_herois")
os.makedirs(OUT, exist_ok=True)
PAL = [("pele_fada", "C9C2D6"), ("pele_fada_s", "A39CB5"), ("pele_humano", "C99A7C"), ("pele_humano_s", "A67A5E"),
       ("pele_g", "8A8F9E"), ("pele_g_s", "6C7080"), ("cabelo_fada", "6B8A5E"), ("cabelo_fada_s", "4F6845"),
       ("cabelo_humano", "4A3326"), ("cabelo_humano_s", "33231A"), ("cabelo_g", "2C2632"), ("cabelo_g_s", "1E1A22"),
       ("olho", "1E1A22"), ("olho_brilho", "F2EEE6"), ("boca", "7A4A4A"), ("roupa", "8C8278"), ("roupa_s", "6E655C"),
       ("asa", "D8CDB4"), ("asa_s", "AA9E84"), ("asa_olho", "5A4A3A"), ("asa_veia", "8E8068"), ("chifre", "D8D0BF"), ("chifre_ponta", "9C9384"),
       ("m_preto", "201C26"), ("m_preto_l", "363040"), ("m_roxo", "7A4FBF"), ("m_lilas", "B48DE8"), ("m_branco", "E8E4EE"), ("m_prata", "C9C9D6"),
       ("aco_e", "434952"), ("aco", "6B737D"), ("aco_c", "A3ABB5"), ("couro", "5A3E2B"), ("capa", "6B2430"), ("capa_s", "4A1820"),
       ("acab", "2B2E33"), ("base", "3A3836"), ("musgo", "4E6338")]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
HEX = ["000000"] + [h for _, h in PAL]
RGB = np.array([hex_rgb(h) for h in HEX])

class Grade:
    def __init__(self, lo, hi):
        lo = np.floor(np.asarray(lo, float) / VS) * VS; hi = np.ceil(np.asarray(hi, float) / VS) * VS
        self.origem = lo
        self.dims = tuple(int(x) for x in np.round((hi - lo) / VS))
        idx = np.indices(self.dims).reshape(3, -1).T
        self.P = self.origem + (idx + 0.5) * VS
        self.X, self.Y, self.Z = (self.P[:, k].reshape(self.dims) for k in range(3))

def ell(G, c, r):
    return ((G.X - c[0]) / r[0]) ** 2 + ((G.Y - c[1]) / r[1]) ** 2 + ((G.Z - c[2]) / r[2]) ** 2 <= 1

def cap(G, a, b, ra, rb=None):
    return capsula(G.P, a, b, ra, rb).reshape(G.dims)

def desl(m, d):
    out = np.zeros_like(m)
    s = tuple(slice(max(k, 0), n + min(k, 0)) for k, n in zip(d, m.shape))
    t = tuple(slice(max(-k, 0), n + min(-k, 0)) for k, n in zip(d, m.shape))
    out[s] = m[t]
    return out

VIZ26 = [d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0)]
VIZ6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

def dil(m, n=1, viz=VIZ26):
    for _ in range(n):
        o = m.copy()
        for d in viz:
            o |= desl(m, d)
        m = o
    return m

def componentes(m):
    m = m.copy(); n = 0
    while m.any():
        cur = np.zeros_like(m); cur[tuple(np.argwhere(m)[0])] = True
        while True:
            nxt = dil(cur, 1, VIZ6) & m
            if np.array_equal(nxt, cur):
                break
            cur = nxt
        m &= ~cur; n += 1
    return n

CLASSE = {"P": dict(H=3.0, s=0.8, cab=(0.78, 0.74, 0.70), tr=(0.46, 0.44, 0.31), mao=0.19, pe=(0.19, 0.13, 0.25), gap=0.2, dmao=0.30),
          "M": dict(H=4.0, s=1.0, cab=(0.88, 0.84, 0.78), tr=(0.60, 0.70, 0.40), mao=0.24, pe=(0.24, 0.16, 0.32), gap=0.26, dmao=0.36),
          "G": dict(H=5.0, s=1.15, cab=(0.98, 0.95, 0.88), tr=(0.82, 0.95, 0.54), mao=0.30, pe=(0.30, 0.20, 0.40), gap=0.3, dmao=0.42)}
LINHAGEM = {"P": dict(nome="fada", pele=("pele_fada", "pele_fada_s"), cabelo=("cabelo_fada", "cabelo_fada_s"), estilo="longo",
                      tracos=("asas", "orelhas"), olho=(0.13, 0.17), elev=0.25),
            "M": dict(nome="humano", pele=("pele_humano", "pele_humano_s"), cabelo=("cabelo_humano", "cabelo_humano_s"), estilo="curto",
                      tracos=(), olho=(0.09, 0.12), elev=0.0),
            "G": dict(nome="chifres", pele=("pele_g", "pele_g_s"), cabelo=("cabelo_g", "cabelo_g_s"), estilo="longo",
                      tracos=("chifres",), olho=(0.1, 0.12), elev=0.0)}

def personagem(tam, corpo):
    c, L = CLASSE[tam], LINHAGEM[tam]
    rx, ry, rz = c["tr"]; hx, hy, hz = c["cab"]; s = c["s"]
    pe_y = c["pe"][1] + L["elev"]
    tr = np.array([0, pe_y + c["pe"][1] + c["gap"] + ry, 0.0])
    cb = np.array([0, tr[1] + ry + 0.04 + hy, -0.02])
    G = Grade((-2.2, -0.3, -1.5), (2.2, cb[1] + hy + 1.4, 1.7))
    ch = dict(tam=tam, corpo=corpo, G=G, tr=tr, cb=cb, c=c, L=L, ocultar=set(), regras=[])
    wc, wh = (1.0, 0.78) if corpo == 1 else (0.8, 0.98)
    ch["tronco"] = ell(G, tr + (0, 0.3 * ry, 0), (wc * rx, 0.62 * ry, rz)) | ell(G, tr - (0, 0.35 * ry, 0), (wh * rx, 0.6 * ry, 0.95 * rz))
    ch["cabeca"] = ell(G, cb, c["cab"])
    ch["maos"] = ell(G, (-(rx + c["dmao"]), tr[1] + 0.05 * ry, -0.08), (c["mao"],) * 3) | ell(G, (rx + c["dmao"], tr[1] + 0.05 * ry, -0.08), (c["mao"],) * 3)
    ch["pes"] = ell(G, (-0.48 * rx, pe_y, -0.06), c["pe"]) | ell(G, (0.48 * rx, pe_y, -0.06), c["pe"])
    ch["ye"] = cb[1] - 0.08 * hy
    base_cab = ell(G, cb + (0, 0.06, 0.04), (hx + 0.15, hy + 0.15, hz + 0.15)) & ~ch["cabeca"]
    frente = G.Z < cb[2] - 0.35 * hz
    franja = cb[1] + 0.34 * hy - 0.14 * np.abs(np.sin(G.X * math.pi / (3 * VS)))
    cab = base_cab & ((G.Y > cb[1] - 0.1 * hy) | (G.Z > cb[2] + 0.2 * hz)) & ~(frente & (G.Y < franja))
    for sg in (-1, 1):
        cab |= cap(G, (sg * 0.86 * hx, cb[1] + 0.2 * hy, cb[2] - 0.3 * hz), (sg * 0.92 * hx, cb[1] - 0.72 * hy, cb[2] - 0.34 * hz), 0.14, 0.08) & ~ch["cabeca"]
    if L["estilo"] == "longo":
        cab |= ell(G, (0, cb[1] - 0.75 * hy, cb[2] + 0.62 * hz), (0.92 * hx, 1.25 * hy, 0.34 * hz)) & (G.Z > cb[2] + 0.2 * hz) & ~ch["cabeca"] & ~dil(ch["tronco"])
    ch["cabelo"] = cab & ~dil(ch["tronco"])
    tr_ = {}
    if "asas" in L["tracos"]:
        k = s / 0.8
        raiz = np.array([0, tr[1] + 0.35 * ry, rz + 0.5])
        asas = np.zeros(G.dims, bool)
        def lobo(cx, cy, a, b, ang):
            dx, dy = G.X - cx, G.Y - cy
            u = dx * math.cos(ang) + dy * math.sin(ang); v = -dx * math.sin(ang) + dy * math.cos(ang)
            return ((u / a) ** 2 + (v / b) ** 2 <= 1) & (np.abs(G.Z - raiz[2]) <= 0.09)
        for sg in (-1, 1):
            asas |= lobo(sg * 1.0 * k, raiz[1] + 0.78 * k, 1.05 * k, 0.62 * k, sg * math.radians(38))
            asas |= lobo(sg * 0.72 * k, raiz[1] - 0.42 * k, 0.62 * k, 0.4 * k, -sg * math.radians(28))
            asas |= cap(G, (sg * 0.14, raiz[1], raiz[2]), (sg * 0.55 * k, raiz[1] + 0.15 * k, raiz[2]), 0.1)
            asas |= cap(G, (sg * 0.14, raiz[1], rz - 0.05), (sg * 0.14, raiz[1], raiz[2]), 0.08)
        tr_["asas"] = asas & ~dil(ch["tronco"], 1) & ~dil(ch["cabeca"], 3)
        ch["centros_asa"] = [np.array([sg * 1.0 * k, raiz[1] + 0.78 * k]) for sg in (-1, 1)]
        ch["raiz_asa"] = raiz
    if "orelhas" in L["tracos"]:
        o = np.zeros(G.dims, bool)
        for sg in (-1, 1):
            o |= cap(G, (sg * 0.85 * hx, cb[1] + 0.02, cb[2] + 0.05), (sg * (hx + 0.66 * s / 0.8), cb[1] + 0.52 * s / 0.8, cb[2] + 0.14), 0.15, 0.05)
        tr_["orelhas"] = o & ~ch["cabeca"]
    if "chifres" in L["tracos"]:
        o = np.zeros(G.dims, bool)
        for sg in (-1, 1):
            a = np.array([sg * 0.45 * hx, cb[1] + 0.7 * hy, cb[2] + 0.05])
            b = a + np.array([sg * 0.32, 0.45, 0.12]) * s
            d = b + np.array([-sg * 0.05, 0.42, 0.22]) * s
            o |= cap(G, a, b, 0.17 * s, 0.12 * s) | cap(G, b, d, 0.12 * s, 0.05)
        tr_["chifres"] = o & ~ch["cabeca"]
    ch["tracos"] = tr_
    return ch

def cor_corpo(ch):
    G, L, cb, c = ch["G"], ch["L"], ch["cb"], ch["c"]
    hx, hy, hz = c["cab"]
    g = np.zeros(G.dims, np.uint8)
    pele, pele_s = K[L["pele"][0]], K[L["pele"][1]]
    g[ch["tronco"]] = np.where(G.Y < ch["tr"][1] - 0.4 * c["tr"][1], K["roupa_s"], K["roupa"])[ch["tronco"]]
    g[ch["pes"]] = K["roupa_s"]
    g[ch["maos"]] = pele
    cab = np.where(G.Y < cb[1] - 0.55 * hy, pele_s, pele)
    ew, eh = (x * c["s"] / 0.8 if ch["tam"] != "P" else x for x in L["olho"])
    frente = G.Z < cb[2] - 0.6 * hz
    for sg in (-1, 1):
        ex = sg * 0.36 * hx
        olho = frente & (np.abs(G.X - ex) < ew) & (np.abs(G.Y - ch["ye"]) < eh)
        cab = np.where(olho, K["olho"], cab)
        brilho = olho & (G.X < ex - ew * 0.2) & (G.Y > ch["ye"] + eh * 0.35)
        cab = np.where(brilho, K["olho_brilho"], cab)
    boca = frente & (np.abs(G.X) < 0.07 * c["s"] / 0.8) & (np.abs(G.Y - (cb[1] - 0.42 * hy)) < 0.04)
    cab = np.where(boca, K["boca"], cab)
    g[ch["cabeca"]] = cab[ch["cabeca"]]
    return g

def pintar_tracos(ch, g, visiveis):
    G, L = ch["G"], ch["L"]
    t = ch["tracos"]
    if "asas" in t and "asas" in visiveis:
        k = CLASSE[ch["tam"]]["s"] / 0.8
        raiz = ch["raiz_asa"]
        cor = np.full(G.dims, K["asa"], np.uint8)
        for cc in ch["centros_asa"]:
            d = np.sqrt((G.X - cc[0]) ** 2 + (G.Y - cc[1]) ** 2)
            cor = np.where((d > 0.17 * k) & (d < 0.28 * k), K["asa_olho"], cor)
            cor = np.where(d <= 0.1 * k, K["asa_olho"], cor)
        ang = np.arctan2(G.Y - raiz[1], np.abs(G.X) + 1e-6)
        cor = np.where((np.abs(np.sin(ang * 5)) < 0.12) & (np.abs(G.X) > 0.35), K["asa_veia"], cor)
        cor = np.where(dil(~t["asas"], 1, [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]) & t["asas"], K["asa_s"], cor)
        g[t["asas"]] = cor[t["asas"]]
    if "orelhas" in t and "orelhas" in visiveis:
        g[t["orelhas"]] = K[L["pele"][0]]
    if "chifres" in t and "chifres" in visiveis:
        g[t["chifres"]] = np.where(G.Y > ch["cb"][1] + 1.25 * ch["c"]["cab"][1], K["chifre_ponta"], K["chifre"])[t["chifres"]]

def protegido(ch, nomes):
    m = np.zeros(ch["G"].dims, bool)
    for n in nomes:
        if n in ch["tracos"]:
            m |= dil(ch["tracos"][n], 1)
    return m

# ---------------- conjuntos ----------------
def armadura(ch):
    G, cb, c, tr = ch["G"], ch["cb"], ch["c"], ch["tr"]
    hx, hy, hz = c["cab"]; rx, ry, rz = c["tr"]; s = c["s"]
    it = {}
    d1, d2 = dil(ch["cabeca"], 1), dil(ch["cabeca"], 2)
    elmo = d2 & ~d1 & (G.Y > cb[1] - 0.72 * hy)
    frente = G.Z < cb[2] - 0.45 * hz
    visor = frente & (((np.abs(G.Y - ch["ye"]) < 0.08 * s) & (np.abs(G.X) < 0.62 * hx)) |
                      ((np.abs(G.X) < 0.08 * s) & (G.Y < ch["ye"]) & (G.Y > ch["ye"] - 0.45 * hy)))
    elmo &= ~visor
    elmo |= ell(G, (0, cb[1] + hy + 0.08, cb[2] + 0.05), (VS * 0.9, 0.22 * s, 0.55 * hz)) & ~d1
    prot = protegido(ch, ["chifres"])
    elmo &= ~prot
    cor = np.where(G.Y > cb[1] + 0.55 * hy, K["aco_c"], K["aco"])
    cor = np.where(dil(visor & frente, 1) | dil(prot, 1), K["acab"], cor)
    it["elmo"] = (elmo, cor)
    ch["ocultar"].add("orelhas")
    ch["cabelo"] = ch["cabelo"] & ~d2
    asas = protegido(ch, ["asas"])
    peit = dil(ch["tronco"], 1) & ~ch["tronco"] & ~asas
    yb = tr[1] - 0.95 * ry
    cor = np.where(np.abs(G.X) < VS, K["aco_c"], K["aco"])
    cor = np.where(G.Y < yb + 0.18, K["acab"], cor)
    it["peitoral"] = (peit, cor)
    colar = dil(ch["tronco"], 2) & ~dil(ch["tronco"], 1) & (G.Y > tr[1] + 0.55 * ry) & (G.Z > -0.1)
    zb = float(G.Z[dil(ch["tronco"], 1)].max()) + VS / 2
    largura = rx * (1.0 + 0.45 * np.clip((tr[1] + 0.3 * ry - G.Y) / (tr[1] + 0.3 * ry), 0, 1))
    placa = (G.Z > zb) & (G.Z < zb + 0.2) & (np.abs(G.X) < largura) & (G.Y > 0.12) & (G.Y < tr[1] + 0.55 * ry)
    capa = (colar | placa) & ~dil(ch["tronco"], 1) & ~asas & ~dil(ch["cabeca"], 1)
    if componentes(capa & ~ch["cabelo"]) == 1:
        capa = capa & ~ch["cabelo"]
        ch["regras"].append("cabelo longo por cima da capa")
    else:
        ch["cabelo"] = ch["cabelo"] & ~dil(capa, 1)
        ch["regras"].append("cabelo longo por baixo da capa (recuo do P1)")
    cor = np.where(G.Z < zb + 0.06, K["capa_s"], K["capa"])
    cor = np.where(G.Y < 0.3, K["acab"], cor)
    it["capa"] = (capa, cor)
    luvas = dil(ch["maos"], 1) & ~ch["maos"]
    it["luvas"] = (luvas, np.where(G.Y > tr[1] + 0.05 * ry + 0.4 * c["mao"], K["aco"], K["couro"]))
    pes = ch["pes"]
    topo_pe = c["pe"][1] * 2 + ch["L"]["elev"]
    cano = dil(pes, 1) & ~pes
    cano |= (dil(pes, 1) & (G.Y > topo_pe - 0.05) & (G.Y < topo_pe + 0.25 * s)) | (dil(desl(pes, (0, 2, 0)), 1) & ~pes & (G.Y < topo_pe + 0.25 * s))
    it["botas"] = (cano & ~pes, np.where(G.Y > topo_pe, K["aco_e"], K["couro"]))
    return it

def mascote(ch):
    G, cb, c, tr = ch["G"], ch["cb"], ch["c"], ch["tr"]
    hx, hy, hz = c["cab"]; rx, ry, rz = c["tr"]; s = c["s"]
    it = {}
    d1, d2, d3 = dil(ch["cabeca"], 1), dil(ch["cabeca"], 2), dil(ch["cabeca"], 3)
    corte = ch["ye"] + 0.17 * s
    gorro = d2 & ~d1 & (G.Y > corte)
    aba = d3 & ~d1 & (G.Y > corte) & (G.Y < corte + 0.22 * s)
    topo = cb[1] + hy
    orelhas = (ell(G, (-0.58 * hx, topo - 0.1, cb[2]), (0.27 * s,) * 3) | ell(G, (0.58 * hx, topo - 0.1, cb[2]), (0.27 * s,) * 3)) & ~d1
    laco = (ell(G, (-0.58 * hx - 0.16 * s, topo + 0.12, cb[2] - 0.2), (0.14 * s, 0.09 * s, 0.07)) |
            ell(G, (-0.58 * hx + 0.1 * s, topo + 0.12, cb[2] - 0.2), (0.14 * s, 0.09 * s, 0.07))) & ~d1
    prot = protegido(ch, ["chifres", "orelhas"])
    g_m = (gorro | aba | orelhas) & ~prot
    cor = np.where(np.floor(G.X / VS) % 2 == 0, K["m_preto"], K["m_preto_l"])
    dentro = (G.Z < cb[2] - 0.08) & ((np.sqrt((np.abs(G.X) - 0.58 * hx) ** 2 + (G.Y - (topo - 0.1)) ** 2)) < 0.16 * s)
    cor = np.where(orelhas & dentro, K["m_lilas"], cor)
    cor = np.where(aba & (np.abs(G.X) < 0.12 * s) & (G.Z < cb[2] - 0.5 * hz), K["m_lilas"], cor)
    cor = np.where(dil(prot, 1), K["m_preto_l"], cor)
    it["gorro"] = (g_m | laco, np.where(laco, K["m_roxo"], cor))
    ch["cabelo"] = ch["cabelo"] & ~(d2 & (G.Y > corte - VS))
    asas = protegido(ch, ["asas"])
    jaq = dil(ch["tronco"], 1) & ~ch["tronco"] & ~asas
    cor = np.full(G.dims, K["m_preto"], np.uint8)
    frente = G.Z < -0.3 * rz
    cor = np.where(frente & (np.abs(G.X) < 0.24 * rx), K["m_branco"], cor)
    px, py = 0.55 * rx, tr[1] - 0.05 * ry
    xm = frente & (np.minimum(np.abs((G.X + px) - (G.Y - py)), np.abs((G.X + px) + (G.Y - py))) < VS * 0.8) & (np.abs(G.X + px) < 0.16 * s)
    cor = np.where(xm, K["m_roxo"], cor)
    cor_ = frente & (np.sqrt((G.X - px) ** 2 + (G.Y - py) ** 2) < 0.14 * s)
    cor = np.where(cor_, K["m_roxo"], cor)
    cor = np.where(frente & (np.sqrt(G.X ** 2 + (G.Y - (tr[1] + 0.35 * ry)) ** 2) < 0.07 * s + VS * 0.5), K["m_prata"], cor)
    it["jaqueta"] = (jaq, cor)
    y_top, y_bot = min(tr[1] - 0.25 * ry, tr[1] + 0.05 * ry - c["mao"] - VS), tr[1] - 0.95 * ry - 0.08
    raio = rx * 1.0 + 2.5 * VS + 0.22 * s * np.clip((y_top - G.Y) / max(y_top - y_bot, 1e-3), 0, 1)
    rr = np.sqrt(G.X ** 2 + (G.Z * rx / rz) ** 2)
    saia = (G.Y > y_bot) & (G.Y < y_top) & (rr < raio) & (rr > raio - 0.22) & ~dil(ch["tronco"], 1) & ~asas
    plis = (np.floor(np.arctan2(G.Z, G.X) * 8 / math.pi) % 2 == 0)
    it["saia"] = (saia, np.where(plis, K["m_roxo"], K["m_lilas"]))
    pes = ch["pes"]
    topo_pe = c["pe"][1] * 2 + ch["L"]["elev"]
    bota = (dil(pes, 1) & ~pes) | (dil(desl(pes, (0, 2, 0)), 1) & ~pes & (G.Y < topo_pe + 0.32 * s))
    listra = np.floor((G.Y - topo_pe) / (2 * VS)) % 2 == 0
    it["botas"] = (bota, np.where((G.Y > topo_pe) & listra, K["m_roxo"], K["m_preto"]))
    mao = np.array([rx + c["dmao"], tr[1] + 0.05 * ry, -0.08])
    topo_v = mao + np.array([0.05, 0.9 * s, -0.25])
    vara = cap(G, mao + (0, -0.15, -0.12), topo_v, 0.06)
    cabeca_v = ell(G, topo_v + (0, 0.1, 0), (0.16 * s, 0.2 * s, 0.07))
    gema = ell(G, topo_v + (0, 0.1, -0.05), (0.06, 0.08, 0.07))
    vv = (vara | cabeca_v | gema) & ~dil(ch["maos"], 0)
    it["varinha"] = (vv & ~ch["maos"], np.where(gema, K["m_roxo"], np.where(cabeca_v, K["m_lilas"], K["m_prata"])))
    return it

# ---------------- montagem e checagens ----------------
def montar(tam, corpo, conjunto):
    ch = personagem(tam, corpo)
    itens = {}
    if conjunto == "armadura":
        itens = armadura(ch)
    elif conjunto == "mascote":
        itens = mascote(ch)
    g = cor_corpo(ch)
    Gq, cbq, hyq = ch["G"], ch["cb"], ch["c"]["cab"][1]
    fio = (np.floor(Gq.X / VS) % 3 == 0) & (Gq.Y < cbq[1] + 0.6 * hyq)
    corcab = np.where((Gq.Y < cbq[1] - 0.2 * hyq) | fio, K[ch["L"]["cabelo"][1]], K[ch["L"]["cabelo"][0]])
    g[ch["cabelo"]] = corcab[ch["cabelo"]]
    vis = set(ch["tracos"]) - ch["ocultar"]
    pintar_tracos(ch, g, vis)
    ocupado = g > 0
    rel = {}
    for n, (m, cor) in itens.items():
        sobre = int((m & ocupado).sum())
        rel["_regras"] = list(ch["regras"])
        rel[n] = dict(voxels=int(m.sum()), sobreposicao=sobre, pecas=componentes(m),
                      tris=2 * len(malha_gulosa(np.where(m, cor, 0).astype(np.uint8))))
        g[m] = cor[m]
    return ch, g, rel

class _P:
    pass

def peca(G, g, nome="x"):
    p = _P(); p.g, p.origem, p.vs, p.nome = g, G.origem, VS, nome
    return p

def disco(raio):
    G = Grade((-raio - 0.2, -0.3, -raio - 0.2), (raio + 0.2, 0.0, raio + 0.2))
    m = (G.X ** 2 + G.Z ** 2 <= raio ** 2) & (G.Y < 0)
    g = np.where(m, np.where((G.Y > -0.13) & (G.X ** 2 + G.Z ** 2 > (raio - 0.25) ** 2), K["musgo"], K["base"]), 0).astype(np.uint8)
    return faces(peca(G, g))

DISCOS = {t: disco(0.75 + 0.35 * CLASSE[t]["H"] / 3) for t in "PMG"}

def cena(tam, g, G, d, W, H, escala, centro_y):
    cam = camera_orto(d, (0, 1, 0), (0, centro_y, 0), escala, W, H)
    itens = [(faces(peca(G, g)), *IDENT), (DISCOS[tam], *IDENT)]
    return render(itens, cam, RGB, set(), fundo=(0.36, 0.35, 0.39), ambiente=0.55)

if __name__ == "__main__":
    relatorio = {}
    linhas = []
    W, H, ESC = 250, 300, 44
    FR, TR = (0.5, -0.22, 0.84), (0.5, -0.22, -0.84)
    for tam in "PMG":
        for corpo in (1, 2):
            celulas = []
            for conj, d in (("base", FR), ("mascote", FR), ("armadura", FR), ("armadura", TR)):
                ch, g, rel = montar(tam, corpo, conj)
                if d is FR:
                    relatorio[f"{tam}{corpo}_{conj}"] = rel
                celulas.append(cena(tam, g, ch["G"], d, W, H, ESC, 2.55))
            linha = Image.new("RGB", (W * 4, H), (255, 255, 255))
            for k, im in enumerate(celulas):
                linha.paste(im, (k * W, 0))
            linhas.append(linha)
    folha = Image.new("RGB", (W * 4, H * 6), (255, 255, 255))
    for k, l in enumerate(linhas):
        folha.paste(l, (0, k * H))
    folha.save(os.path.join(OUT, "matriz_de_prova.png"))
    vistas = []
    for corpo in (1, 2):
        ch, g, rel = montar("P", corpo, "base")
        for d in ((0.0001, -0.08, 1), (1, -0.08, 0.0001), (0.0001, -0.08, -1)):
            vistas.append(cena("P", g, ch["G"], d, 340, 340, 92, 1.55))
    fada = Image.new("RGB", (340 * 3, 340 * 2), (255, 255, 255))
    for k, im in enumerate(vistas):
        fada.paste(im, ((k % 3) * 340, (k // 3) * 340))
    fada.save(os.path.join(OUT, "fada_base.png"))
    json.dump(relatorio, open(os.path.join(OUT, "relatorio_herois.json"), "w"), indent=1)
    for k, v in relatorio.items():
        print(k, {n: (r["sobreposicao"], r["pecas"], r["tris"]) for n, r in v.items() if n != "_regras"}, v.get("_regras", ""))
