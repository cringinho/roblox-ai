"""Relicario: clipes parado, andar, ataque e susto, com colisao fina por quadro."""
import sys, os, math, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relicario as R, ossarios as O, bestiario as B
from voxforja import render, camera_orto, rot_eixo, faces
X, Y, Z = R.X, R.Y, R.Z
rad = math.radians
BR = (("E1", -1, 1), ("D1", 1, 1), ("E2", -1, 0), ("D2", 1, 0))

def tique(t, periodo, dur=0.08, seed=0):
    """Espasmo: 0 quase sempre, pulo seco por 'dur' segundos uma vez por periodo."""
    f = (t + seed * 0.37) % periodo
    return math.sin(math.pi * f / dur) if f < dur else 0.0

def pose(mon, clipe, t):
    L = {}; d = np.zeros(3); Rr = np.eye(3)
    if clipe == "parado":
        resp = math.sin(2 * math.pi * t / 2.2)
        L["Torax"] = rot_eixo(X, rad(16 + 3 * resp))
        L["Pescoco"] = rot_eixo(X, rad(-18 - 2 * resp))
        L["Cranio"] = rot_eixo(Z, rad(14 + 22 * tique(t, 1.1, 0.1))) @ rot_eixo(Y, rad(10 * math.sin(t * 1.3)))
        L["Mandibula"] = rot_eixo(X, rad(8 + 18 * tique(t, 0.7, 0.06, 2)))
        for Ln, s, cima in BR:
            a = math.sin(2 * math.pi * (t - 0.15 * (not cima)) / 2.2)
            L[f"Umero_{Ln}"] = rot_eixo(X, rad(-8 + 4 * a)) @ rot_eixo(Z, s * rad(4 * a))
            L[f"Antebraco_{Ln}"] = rot_eixo(X, rad(-12 - 20 * tique(t, 1.7, 0.08, 1 + cima + s)))
        d = np.array([0, 0.02 * resp, 0])
    elif clipe == "andar":
        per = 1.4; w = 2 * math.pi * t / per
        L["Torax"] = rot_eixo(X, rad(24)) @ rot_eixo(Z, rad(7 * math.sin(w)))
        L["Pescoco"] = rot_eixo(X, rad(-22))
        L["Cranio"] = rot_eixo(Z, rad(20 - 10 * math.sin(w))) @ rot_eixo(X, rad(6 * math.sin(2 * w)))
        L["Mandibula"] = rot_eixo(X, rad(14 + 10 * max(0, math.sin(2 * w))))
        # perna esquerda firme, direita manca e arrasta
        L["Perna_E"] = rot_eixo(X, rad(26 * math.sin(w)))
        L["Perna_D"] = rot_eixo(X, rad(-12 * math.sin(w) - 8)) @ rot_eixo(Z, rad(6))
        for Ln, s, cima in BR:
            ph = w + (math.pi if s > 0 else 0) + (0.6 if not cima else 0)
            L[f"Umero_{Ln}"] = rot_eixo(X, rad(-14 + 16 * math.sin(ph))) @ rot_eixo(Z, s * rad(6))
            L[f"Antebraco_{Ln}"] = rot_eixo(X, rad(-18 + 8 * math.sin(ph - 0.5)))
        d = np.array([0, -0.06 * abs(math.sin(w)), 0])
        Rr = rot_eixo(Z, rad(4 * math.sin(w)))
    elif clipe == "ataque":
        dur = 1.2; f = (t % dur) / dur
        def ease(a, b):
            u = min(max((f - a) / (b - a), 0), 1); return u * u * (3 - 2 * u)
        prep, bote, volta = ease(0.0, 0.35), ease(0.35, 0.47), ease(0.75, 1.0)
        k = prep * (1 - bote) - 0.0; g = bote * (1 - volta)
        L["Torax"] = rot_eixo(X, rad(16 - 14 * k + 26 * g))
        L["Pescoco"] = rot_eixo(X, rad(-18 + 10 * k - 22 * g))
        L["Cranio"] = rot_eixo(Z, rad(14 + 30 * g + 4 * math.sin(t * 40) * g))
        L["Mandibula"] = rot_eixo(X, rad(8 + 30 * k + 40 * g * (1 - ease(0.55, 0.62))))
        for Ln, s, cima in BR:
            L[f"Umero_{Ln}"] = rot_eixo(X, rad(-8 - (30 if cima else 20) * k - (95 if cima else 60) * g)) @ rot_eixo(Z, s * rad((60 if cima else 35) * k - (15 if cima else 5) * g))
            L[f"Antebraco_{Ln}"] = rot_eixo(X, rad(-12 - 40 * k + 10 * g - 30 * ease(0.5, 0.6) * (1 - volta)))
        L["Perna_E"] = rot_eixo(X, rad(-25 * g)); L["Perna_D"] = rot_eixo(X, rad(18 * g))
        d = np.array([0, -0.1 * k, -0.6 * g])
    else:
        T = O.pose_esqueleto(mon, t)
        return T
    return B.montar(mon, B.raiz(mon, Rr, d), L)

CLIPES = (("parado", 2.2, 22), ("andar", 1.4, 16), ("ataque", 1.2, 18), ("susto", 1.6, 24))

if __name__ == "__main__":
    mon = R.relicario()
    rel = R.auditoria(mon)
    col = {}
    for c, dur, n in CLIPES:
        col[c] = max(R.colisoes_finas(mon, pose(mon, c, i / n * dur)) for i in range(n))
    print("colisao por clipe", col)
    fr = []; W, H = 360, 420
    cam = camera_orto((0.6, -0.12, 0.8), Y, (0, 1.8, -0.2), 104, W, H)
    for c, dur, n in CLIPES:
        for i in range(n):
            T = pose(mon, c, i / n * dur)
            it = [(mon["faces"][k], *T[k]) for k in mon["pecas"]]
            im = render(it, cam, R.RGB, R.EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.5, ambiente=0.5)
            fr.append(im)
    big = [Image.new("RGB", (W, H)) for _ in fr]
    fr[0].save(os.path.join(B.OUT, "relicario_animacoes.webp"), save_all=True, append_images=fr[1:], duration=int(1000 * 1.6 / 24), loop=0, quality=85)
    # folha: 4 clipes x 6 quadros
    fo = Image.new("RGB", (6 * 180, 4 * 210)); idx = 0
    for r, (c, dur, n) in enumerate(CLIPES):
        for j in range(6):
            fo.paste(fr[idx + j * n // 6].resize((180, 210)), (j * 180, r * 210))
        idx += n
    fo.save(os.path.join(B.OUT, "relicario_clipes.png"))
    json.dump(dict(colisao_por_clipe=col), open(os.path.join(B.OUT, "relicario_anim.json"), "w"))
