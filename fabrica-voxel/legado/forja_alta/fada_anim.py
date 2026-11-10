"""Fada: rig rigido (pecas soltas estilo Trove) e animacoes procedurais pairar, voar e golpe de varinha."""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import faces, render, camera_orto, rot_eixo, IDENT
import herois as H

OUT = H.OUT
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])

def rig_fada(conjunto="mascote", corpo=1):
    ch = H.personagem("P", corpo)
    itens = H.mascote(ch) if conjunto == "mascote" else (H.armadura(ch) if conjunto == "armadura" else {})
    g = H.cor_corpo(ch)
    G = ch["G"]
    cab = ch["cabelo"]
    corcab = np.where(G.Y < ch["cb"][1] - 0.2 * ch["c"]["cab"][1], H.K["cabelo_fada_s"], H.K["cabelo_fada"])
    g[cab] = corcab[cab]
    H.pintar_tracos(ch, g, set(ch["tracos"]) - ch["ocultar"])
    donos = {}
    for n, (m, cor) in itens.items():
        g[m] = cor[m]; donos[n] = m
    rx, ry, rz = ch["c"]["tr"]; cb, tr = ch["cb"], ch["tr"]
    E, D = G.X < 0, G.X >= 0
    pes = ch["pes"] | donos.get("botas", np.zeros(G.dims, bool))
    maos = ch["maos"] | donos.get("luvas", np.zeros(G.dims, bool))
    cabeca = ch["cabeca"] | cab | ch["tracos"].get("orelhas", np.zeros(G.dims, bool)) | donos.get("elmo", np.zeros(G.dims, bool)) | donos.get("gorro", np.zeros(G.dims, bool))
    asas = ch["tracos"]["asas"]
    vara = donos.get("varinha", np.zeros(G.dims, bool))
    partes = {"Cabeca": cabeca, "Mao_E": maos & E, "Mao_D": (maos & D) | vara, "Pe_E": pes & E, "Pe_D": pes & D,
              "Asa_E": asas & E, "Asa_D": asas & D}
    usado = np.zeros(G.dims, bool)
    for m in partes.values():
        usado |= m
    partes["Tronco"] = (g > 0) & ~usado
    mao_y = tr[1] + 0.05 * ry
    raiz = ch["raiz_asa"]
    pivos = {"Tronco": tr, "Cabeca": np.array([0, cb[1] - ch["c"]["cab"][1], cb[2]]),
             "Mao_E": np.array([-(rx + ch["c"]["dmao"]), mao_y, -0.08]), "Mao_D": np.array([rx + ch["c"]["dmao"], mao_y, -0.08]),
             "Pe_E": np.array([-0.48 * rx, ch["c"]["pe"][1] + 0.25, -0.06]), "Pe_D": np.array([0.48 * rx, ch["c"]["pe"][1] + 0.25, -0.06]),
             "Asa_E": np.array([-0.14, raiz[1], rz - 0.05]), "Asa_D": np.array([0.14, raiz[1], rz - 0.05])}
    pecas = {}
    for n, m in partes.items():
        gg = np.where(m, g, 0).astype(np.uint8)
        p = H.peca(G, gg, n)
        pecas[n] = dict(faces=faces(p), centros=G.P[m.reshape(-1)], pivo=pivos[n])
    return pecas, ch

def gira(R, piv):
    return (R, piv - R @ piv)

def compor(A, B):
    return (A[0] @ B[0], A[0] @ B[1] + A[1])

def mola(t, freq, amort=3.0):
    return math.exp(-amort * (t % (1 / freq))) * math.cos(2 * math.pi * freq * t)

def pose(pecas, clipe, t):
    """Devolve (R, t) por peca. Tronco e a raiz; o resto pende dele com atraso."""
    pv = {n: p["pivo"] for n, p in pecas.items()}
    T = {}
    if clipe == "pairar":
        sobe = 0.08 * math.sin(2 * math.pi * t / 1.2)
        Rt = rot_eixo(Z, math.radians(2) * math.sin(2 * math.pi * t / 2.4))
        bater = math.radians(18 + 30 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 3.5)))
        atraso = math.sin(2 * math.pi * (t - 0.12) / 1.2)
        maos, pes, cab = math.radians(6) * atraso, math.radians(10) * atraso, math.radians(4) * math.sin(2 * math.pi * t / 2.4 + 1)
        desl = np.array([0, sobe, 0]); golpe = None
    elif clipe == "voar":
        sobe = 0.25 + 0.05 * math.sin(2 * math.pi * t / 0.6)
        Rt = rot_eixo(X, math.radians(-16))
        bater = math.radians(15 + 45 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 6)))
        maos, pes, cab = math.radians(-25), math.radians(-35) + math.radians(8) * math.sin(2 * math.pi * t / 0.6), math.radians(10)
        desl = np.array([0, sobe, -1.6 * t]); golpe = None
    else:
        dur = 0.7; f = (t % dur) / dur
        marcos = [0.0, 0.30, 0.40, 0.45, 0.70, 1.0]
        ang_arco = [140, 155, -40, -60, -60, 140]
        giro = [0, -25, 30, 35, 20, 0]
        k = max(i for i in range(5) if marcos[i] <= f)
        u = (f - marcos[k]) / (marcos[k + 1] - marcos[k]); u = u * u * (3 - 2 * u)
        a = math.radians(ang_arco[k] + (ang_arco[k + 1] - ang_arco[k]) * u)
        yaw = math.radians(giro[k] + (giro[k + 1] - giro[k]) * u)
        Rt = rot_eixo(Y, yaw) @ rot_eixo(X, math.radians(-6) * math.sin(math.pi * f))
        bater = math.radians(25 + 15 * math.sin(2 * math.pi * t * 3.5))
        maos, pes, cab = 0.0, math.radians(8) * math.sin(math.pi * f), -yaw * 0.5
        desl = np.zeros(3); golpe = a
    Ttr = (Rt, pv["Tronco"] + desl - Rt @ pv["Tronco"])
    T["Tronco"] = Ttr
    T["Cabeca"] = compor(Ttr, gira(rot_eixo(Y, cab) @ rot_eixo(X, cab * 0.5), pv["Cabeca"]))
    for lado, sg in (("E", -1), ("D", 1)):
        T[f"Asa_{lado}"] = compor(Ttr, gira(rot_eixo(Y, -sg * bater), pv[f"Asa_{lado}"]))
        T[f"Pe_{lado}"] = compor(Ttr, gira(rot_eixo(X, pes + sg * 0.03), pv[f"Pe_{lado}"]))
        if lado == "D" and golpe is not None:
            # mao solta = ponta da cadeia: segue um arco no plano do golpe, pulso gira junto (gume a frente)
            c = pv["Tronco"] + np.array([0.75, 0.25, -0.45])
            r = 0.6
            alvo = c + r * np.array([0.35 * math.cos(a), math.sin(a), -0.75 * math.cos(a)])
            Rw = rot_eixo(X, -(a - math.radians(90)))
            T["Mao_D"] = compor(Ttr, (Rw, alvo - Rw @ pv["Mao_D"]))
        else:
            T[f"Mao_{lado}"] = compor(Ttr, gira(rot_eixo(X, maos), pv[f"Mao_{lado}"]))
    return T

def colisao(pecas, T, a, outras):
    """P1 por quadro: voxels de uma peca que caem em celulas ocupadas por outras."""
    cel = set()
    for n in outras:
        R, t = T[n]
        cel.update(map(tuple, np.round((pecas[n]["centros"] @ R.T + t) / H.VS).astype(int)))
    R, t = T[a]
    q = np.round((pecas[a]["centros"] @ R.T + t) / H.VS).astype(int)
    return sum(1 for c in map(tuple, q) if c in cel)

def quadro(pecas, T, cam):
    itens = [(p["faces"], *T[n]) for n, p in pecas.items()]
    return render(itens, cam, H.RGB, set(), fundo=(0.36, 0.35, 0.39), ambiente=0.55)

if __name__ == "__main__":
    rel = {}
    frames = []
    W, Hh = 480, 420
    for conj, clipe, dur, n in (("base", "pairar", 2.4, 24), ("mascote", "voar", 1.2, 16), ("mascote", "golpe", 1.4, 20), ("armadura", "pairar", 1.2, 12)):
        pecas, ch = rig_fada(conj)
        pior = {}
        for i in range(n):
            t = i / n * dur
            T = pose(pecas, clipe, t)
            for a in ("Asa_E", "Asa_D", "Mao_D"):
                outros = [k for k in pecas if k not in (a, "Asa_E", "Asa_D") or k == a and False]
                outros = [k for k in pecas if k != a and not k.startswith("Asa")]
                pior[a] = max(pior.get(a, 0), colisao(pecas, T, a, outros))
            cpos = T["Tronco"][0] @ pecas["Tronco"]["pivo"] + T["Tronco"][1]
            cam = camera_orto((0.55, -0.2, 0.81), Y, (cpos[0], 1.6, cpos[2]), 80, W, Hh)
            frames.append(quadro(pecas, T, cam))
        rel[f"{conj}/{clipe}"] = pior
    frames[0].save(os.path.join(OUT, "fada_animacoes.webp"), save_all=True, append_images=frames[1:], duration=70, loop=0, quality=85)
    pecas, ch = rig_fada("mascote")
    folha = Image.new("RGB", (4 * 240, 2 * 260), (255, 255, 255))
    for k in range(8):
        T = pose(pecas, "golpe", k * 0.7 / 8)
        cam = camera_orto((1, -0.15, 0.0001), Y, (0, 1.6, 0), 62, 240, 260)
        folha.paste(quadro(pecas, T, cam), ((k % 4) * 240, (k // 4) * 260))
    folha.save(os.path.join(OUT, "fada_golpe_8_quadros.png"))
    rig = {n: dict(pivo=[round(float(x), 3) for x in p["pivo"]], pai=None if n == "Tronco" else "Tronco", voxels=len(p["centros"])) for n, p in pecas.items()}
    json.dump(dict(rig=rig, colisao_max_voxels=rel), open(os.path.join(OUT, "fada_rig.json"), "w"), indent=1)
    print(json.dumps(rel))
