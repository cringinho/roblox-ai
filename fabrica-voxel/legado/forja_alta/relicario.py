"""Relicario: esqueleto de susto grotesco, feito dos ossos das vitimas do Ossario, com auditoria rigida."""
import sys, os, math, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxforja import construir, faces, render, camera_orto, camera_persp, rot_eixo, ruido, malha_gulosa, hex_rgb, capsula
import bestiario as B
import ossarios as O

PAL = O.PAL + [("carne_seca", "5E2A22"), ("tendao", "8A3A2E"), ("pele_podre", "8C7A5C"), ("pele_podre_s", "5E5240"), ("medula", "3A1A14")]
_TROCA = {"osso": "C2B48F", "osso_s": "8E8160", "osso_e": "554B3A", "sangue": "561512", "osso_unha": "D8CBA8"}
PAL = [(n, _TROCA.get(n, h)) for n, h in PAL]
K = {n: i + 1 for i, (n, h) in enumerate(PAL)}
RGB = np.array([hex_rgb(h) for h in ["000000"] + [h for _, h in PAL]])
EMIS = O.EMIS
X, Y, Z = O.X, O.Y, O.Z
VS, VSC = 0.0625, 0.03125

def osso(cy=1.5, ry=1.5, sangue=0.72):
    def f(P):
        n = ruido(P, 7.0, seed=5)
        c = np.where(n < 0.33, K["osso_e"], np.where(n > 0.63, K["osso"], K["osso_s"]))
        c = np.where((P[:, 1] - cy) / ry < -0.85, K["osso_e"], c)
        return np.where(ruido(P, 3.0, seed=21) > sangue, K["sangue"], c)
    return f

def arco(c, a, b, y, t0, t1, r, n, ops, cor):
    pts = [np.array([c[0] + a * math.sin(t), y - 0.06 * math.sin(t) ** 2, c[2] + b * math.cos(t)]) for t in np.linspace(t0, t1, n)]
    for p, q in zip(pts[:-1], pts[1:]):
        ops.append(('U', ('cap', p, q, r), cor))
    return pts

def ligar_soltos(p, cor):
    """Auditoria: nada solto. Cada pedaco separado ganha um tendao ate o corpo principal."""
    s = p.g > 0
    tendoes = 0
    for _ in range(40):
        idx = np.argwhere(s)
        if len(idx) == 0:
            return tendoes
        semente = idx[np.argmin(((p.origem + (idx + 0.5) * p.vs - p.pivo) ** 2).sum(1))]
        cur = np.zeros_like(s); cur[tuple(semente)] = True
        while True:
            nxt = cur.copy()
            nxt[1:] |= cur[:-1]; nxt[:-1] |= cur[1:]; nxt[:, 1:] |= cur[:, :-1]; nxt[:, :-1] |= cur[:, 1:]; nxt[:, :, 1:] |= cur[:, :, :-1]; nxt[:, :, :-1] |= cur[:, :, 1:]
            nxt &= s
            if np.array_equal(nxt, cur):
                break
            cur = nxt
        resto = s & ~cur
        if not resto.any():
            return tendoes
        A = p.origem + (np.argwhere(cur) + 0.5) * p.vs
        Bp = p.origem + (np.argwhere(resto) + 0.5) * p.vs
        a_s = A[:: max(1, len(A) // 1500)]; b_s = Bp[:: max(1, len(Bp) // 600)]
        d = ((a_s[:, None, :] - b_s[None, :, :]) ** 2).sum(2)
        i, j = np.unravel_index(np.argmin(d), d.shape)
        m = capsula(p.P, a_s[i], b_s[j], p.vs * 1.1).reshape(p.dims) & ~s
        p.g[m] = cor
        s = p.g > 0
        tendoes += 1
    return tendoes

def relicario():
    P = {}
    sinew = K["tendao"]
    ops = [('U', ('ell', (s * 0.2, 1.08, 0.12), (0.18, 0.21, 0.09)), osso()) for s in (-1, 1)]
    ops += [('C', ('ell', (s * 0.2, 1.06, 0.05), (0.09, 0.1, 0.05)), None) for s in (-1, 1)]
    ops += [('U', ('ell', (0, 1.02, 0.18), (0.11, 0.15, 0.08)), osso()), ('U', ('cap', (-0.26, 0.92, 0.05), (0.26, 0.92, 0.05), 0.055), osso())]
    cauda = [(0, 1.0, 0.25), (0, 0.8, 0.55), (0, 0.5, 0.85), (0, 0.25, 1.25), (0, 0.12, 1.75), (0.15, 0.08, 2.25), (0.3, 0.06, 2.7)]
    for k in range(len(cauda) - 1):
        a, b = np.array(cauda[k]), np.array(cauda[k + 1])
        for u in np.linspace(0, 1, 5, endpoint=False):
            p = a + (b - a) * u; r = max(0.06, 0.12 - 0.01 * k)
            ops += [('U', ('ell', p, (r, r * 0.8, 0.065)), osso()), ('U', ('cone', p, p + np.array([0, 0.1, 0.02]), 0.035), osso())]
        ops.append(('U', ('cap', a + (0, -0.02, 0), b + (0, -0.02, 0), 0.05), K["medula"]))
    trapo = lambda Q: np.where(ruido(Q, 6.0, seed=8) > 0.55, K["membrana_s"], K["carne_seca"])
    ops += [('U', ('ell', (s * 0.13, 0.72, -0.12), (0.13, 0.3, 0.035)), trapo) for s in (-1, 1)]
    ops += [('C', lambda Q: (Q[:, 1] < 0.6) & (ruido(Q, 9.0, seed=3) > 0.45) & (Q[:, 2] < -0.08), None)]
    P["Base"] = construir("Base", None, VS, (0, 1.05, 0.1), ops)
    for s, L in ((-1, "E"), (1, "D")):
        q, j, pe = np.array([s * 0.24, 1.0, 0.1]), np.array([s * 0.3, 0.55, -0.12]), np.array([s * 0.3, 0.1, 0.05])
        ops = [('U', ('ell', q, (0.09, 0.09, 0.09)), osso()), ('U', ('cap', q, j, 0.07, 0.055), osso()), ('U', ('ell', j + (0, 0.01, -0.08), (0.065, 0.065, 0.045)), osso()),
               ('U', ('ell', j, (0.085, 0.07, 0.075)), osso()), ('U', ('cap', j + (s * 0.03, 0, 0), pe + (s * 0.03, 0, 0), 0.05, 0.045), osso()),
               ('U', ('cap', j + (-s * 0.035, -0.02, 0.03), pe + (-s * 0.03, 0.02, 0.04), 0.035), osso()),
               ('U', ('cap', j + (0, 0.02, 0.06), pe + (0, 0.1, 0.06), 0.03), sinew), ('U', ('ell', pe, (0.07, 0.055, 0.07)), osso())]
        for k in (-1, 0, 1):
            ops.append(('U', ('cap', pe + (k * 0.045, -0.02, 0), pe + (k * 0.065, -0.05, -0.3), 0.032, 0.022), osso()))
        P[f"Perna_{L}"] = construir(f"Perna_{L}", "Base", VS, q, ops)
    ops = []
    for y in np.arange(1.05, 2.52, 0.085):
        z = 0.15 - 0.05 * math.sin((y - 1.05) / 1.45 * math.pi)
        ops += [('U', ('ell', (0, y, z), (0.09, 0.055, 0.08)), osso()), ('U', ('cone', (0, y, z + 0.05), (0, y - 0.05, z + 0.17), 0.035), osso())]
    ops.append(('U', ('cap', (0, 1.05, 0.21), (0, 2.5, 0.18), 0.04), K["medula"]))
    for i, y in enumerate((2.22, 2.07, 1.92, 1.77, 1.62, 1.47)):
        a = 0.36 + 0.05 * math.sin(i / 5 * math.pi)
        fim = 0.62 * math.pi if i == 2 else 0.97 * math.pi
        pts = arco((0, 0, -0.05), a, 0.3, y, 0.05 * math.pi, fim, 0.045, 16, ops, osso())
        if i == 2:
            ops.append(('U', ('cone', pts[-1], pts[-1] + np.array([0.28, 0.05, -0.18]), 0.05), K["osso_unha"]))
        arco((0, 0, -0.05), -a, 0.3, y, 0.05 * math.pi, 0.97 * math.pi, 0.045, 16, ops, osso())
        ops.append(('U', ('cap', (s_ := 0.0, y, 0.12), (0.0, y - 0.05, -0.32), 0.0), sinew)) if False else None
    ops += [('U', ('cap', (0, 2.24, -0.36), (0, 1.55, -0.35), 0.05, 0.04), osso()),
            ('U', ('cap', (-0.42, 2.38, -0.14), (-0.04, 2.32, -0.3), 0.045), osso()), ('U', ('cap', (0.42, 2.38, -0.14), (0.04, 2.32, -0.3), 0.045), osso())]
    ops += [('U', ('ell', (s * 0.25, 2.12, 0.22), (0.17, 0.21, 0.035)), osso()) for s in (-1, 1)]
    ops += [('U', ('cap', (-0.64, 2.35, 0.05), (0.64, 2.35, 0.05), 0.055), osso()), ('U', ('cap', (-0.64, 1.8, 0.05), (0.64, 1.8, 0.05), 0.05), osso())]
    ops += [('U', ('ell', (s * 0.62, y, 0.05), (0.1, 0.1, 0.1)), osso()) for s in (-1, 1) for y in (2.35, 1.8)]
    for (cx, cy, cz, r, aceso) in ((-0.1, 1.85, -0.08, 0.13, False), (0.12, 1.58, -0.05, 0.12, True)):
        def cr(Q, cx=cx, cy=cy, cz=cz, r=r, aceso=aceso):
            c = osso(cy, r)(Q)
            for s in (-1, 1):
                o = np.array([cx + s * 0.05 * r / 0.13, cy + 0.02, cz - r * 0.8])
                c = np.where(np.linalg.norm((Q - o)[:, :2], axis=1) < 0.035 * r / 0.13, K["buraco"], c)
                if aceso:
                    c = np.where(np.linalg.norm((Q - o)[:, :2], axis=1) < 0.015, K["brasa"], c)
            boca = (np.abs(Q[:, 0] - cx) < 0.04) & (Q[:, 1] < cy - 0.05) & (Q[:, 1] > cy - 0.11) & (Q[:, 2] < cz - 0.05)
            return np.where(boca, K["buraco"], c)
        ops.append(('U', ('ell', (cx, cy, cz), (r * 0.85, r, r * 0.9)), cr))
        ops.append(('U', ('cap', (cx, cy, cz + r * 0.5), (0, cy, 0.15), 0.035), sinew))
    for y in (2.15, 1.85, 1.55):
        ops.append(('U', ('cap', (0.35, y, -0.05), (0.0, y - 0.12, 0.15), 0.025), sinew))
        ops.append(('U', ('cap', (-0.33, y + 0.05, -0.12), (0.0, y - 0.05, 0.15), 0.025), sinew))
    P["Torax"] = construir("Torax", "Base", VS, (0, 1.1, 0.15), ops)
    ops = []
    for y in np.arange(2.5, 3.06, 0.07):
        z = 0.17 - (y - 2.5) * 0.12
        ops += [('U', ('ell', (0, y, z), (0.085, 0.045, 0.075)), osso()), ('U', ('cone', (0, y, z + 0.04), (0, y - 0.03, z + 0.13), 0.03), osso())]
    ops += [('U', ('cap', (0, 2.5, 0.21), (0, 3.0, 0.15), 0.03), K["medula"]),
            ('U', ('cap', (-0.07, 2.92, 0.15), (-0.3, 2.42, 0.1), 0.03), sinew), ('U', ('cap', (0.07, 2.92, 0.15), (0.3, 2.42, 0.1), 0.03), sinew)]
    ops.append(('U', ('ell', (0, 2.5, 0.13), (0.09, 0.07, 0.08)), osso()))
    ops.append(('U', ('ell', (0, 3.05, 0.0), (0.1, 0.08, 0.085)), osso()))
    P["Pescoco"] = construir("Pescoco", "Torax", VS, (0, 2.5, 0.13), ops)
    def rosto(Q):
        c = osso(3.35, 0.5)(Q)
        racha = (np.abs(Q[:, 0] - 0.06 * np.sin(Q[:, 2] * 11)) < 0.022) & (Q[:, 1] > 3.58)
        c = np.where(racha, K["buraco"], c)
        pele = (Q[:, 0] > 0.04 + 0.08 * ruido(Q, 5.0, seed=12)) & (Q[:, 1] < 3.55) & (Q[:, 1] > 3.0) & ((((Q - np.array([0, 3.4, -0.1])) / np.array([0.37, 0.44, 0.46])) ** 2).sum(1) > 0.82)
        c = np.where(pele, np.where(ruido(Q, 9.0, seed=13) > 0.5, K["pele_podre"], K["pele_podre_s"]), c)
        for s in (-1, 1):
            c = np.where(np.linalg.norm((Q - np.array([s * 0.13, 3.31, -0.42]))[:, :2], axis=1) < 0.026, K["brasa"], c)
        return c
    ops = [('U', ('ell', (0, 3.44, -0.08), (0.31, 0.4, 0.42)), rosto), ('U', ('ell', (0, 3.16, -0.32), (0.25, 0.24, 0.25)), rosto),
           ('U', ('ell', (0.08, 3.3, -0.05), (0.38, 0.4, 0.45)), lambda Q: np.where(ruido(Q, 9.0, seed=13) > 0.5, K["pele_podre"], K["pele_podre_s"])),
           ('C', lambda Q: (Q[:, 0] < 0.06 + 0.08 * ruido(Q, 5.0, seed=12)) | (Q[:, 1] > 3.55) | (ruido(Q, 6.0, seed=31) > 0.68), None)]
    ops += [('U', ('ell', (0, 3.44, -0.08), (0.31, 0.4, 0.42)), rosto), ('U', ('ell', (0, 3.16, -0.32), (0.25, 0.24, 0.25)), rosto)]
    ops += [('U', ('cap', (-0.29, 3.47, -0.47), (0.29, 3.47, -0.47), 0.05), osso(3.35, 0.5)),
            ('U', ('ell', (-0.27, 3.22, -0.38), (0.09, 0.065, 0.12)), osso(3.35, 0.5)), ('U', ('ell', (0.27, 3.22, -0.38), (0.09, 0.065, 0.12)), osso(3.35, 0.5))]
    for s in (-1, 1):
        ops.append(('C', ('ell', (s * 0.14, 3.34, -0.5), (0.11, 0.135, 0.16)), None))
    ops.append(('C', ('cone', (0, 3.11, -0.56), (0, 3.27, -0.5), 0.075), None))
    for k in range(-5, 6):
        x = k * 0.04; zz = -0.5 + 0.005 * k * k; comp = 0.07 + 0.03 * ((k * 7) % 3 == 0)
        ops.append(('U', ('cap', (x, 3.06, zz), (x, 3.06 - comp, zz - 0.01), 0.016), K["osso_unha"]))
    ops.append(('C', ('ell', (0.2, 3.12, -0.42), (0.1, 0.07, 0.12)), None))
    P["Cranio"] = construir("Cranio", "Pescoco", VSC, (0, 3.05, -0.03), ops)
    cr = P["Cranio"]
    fundo = np.zeros(len(cr.P), bool)
    for s in (-1, 1):
        fundo |= (((cr.P - np.array([s * 0.14, 3.34, -0.48])) / np.array([0.15, 0.175, 0.2])) ** 2).sum(1) <= 1
    fundo |= (((cr.P - np.array([0, 3.18, -0.5])) / np.array([0.1, 0.13, 0.12])) ** 2).sum(1) <= 1
    fundo |= (((cr.P - np.array([0.2, 3.12, -0.42])) / np.array([0.13, 0.1, 0.15])) ** 2).sum(1) <= 1
    cr.pintar(fundo & (cr.g.reshape(-1) != K["osso_unha"]), K["buraco"])
    for s in (-1, 1):
        m = np.linalg.norm(cr.P - np.array([s * 0.13, 3.31, -0.4]), axis=1) < 0.024
        cr.unir(m, K["brasa"])
    ops = [('U', ('cap', (-0.22, 2.95, -0.1), (-0.12, 2.85, -0.45), 0.05), osso(3.0, 0.3)), ('U', ('cap', (0.22, 2.95, -0.1), (0.12, 2.85, -0.45), 0.05), osso(3.0, 0.3)),
           ('U', ('cap', (-0.12, 2.85, -0.45), (0.12, 2.85, -0.45), 0.05), osso(3.0, 0.3)), ('U', ('cap', (0.2, 2.95, -0.1), (0.25, 3.1, -0.3), 0.025), K["tendao"])]
    for k in range(-4, 5):
        ops.append(('U', ('cap', (k * 0.04, 2.88, -0.45), (k * 0.04, 2.97 + 0.02 * (k % 2), -0.45), 0.016), K["osso_unha"]))
    ops += [('U', ('ell', (sx * 0.22, 2.97, -0.12), (0.05, 0.05, 0.05)), osso(3.0, 0.3)) for sx in (-1, 1)]
    ops.append(('U', ('cap', (-0.2, 2.97, -0.16), (0.2, 2.97, -0.16), 0.025), K["tendao"]))
    P["Mandibula"] = construir("Mandibula", "Cranio", VSC, (0, 2.97, -0.15), ops)
    for L, s, y, k in (("E1", -1, 2.35, 1.0), ("D1", 1, 2.35, 1.0), ("E2", -1, 1.8, 0.85), ("D2", 1, 1.8, 0.6)):
        om = np.array([s * 0.62, y, 0.05])
        cot, mao = (np.array([s * 1.2, y - 0.5, 0.0]), np.array([s * 1.45, y - 1.1, -0.2])) if L.endswith('1') else (np.array([s * 0.85, y - 0.45 * k, -0.35]), np.array([s * 0.7, y - 0.95 * k, -0.85]))
        P[f"Umero_{L}"] = construir(f"Umero_{L}", "Torax", VS, om, [('U', ('ell', om, (0.09, 0.09, 0.09)), osso()), ('U', ('cap', om, cot, 0.06 * max(k, 0.8), 0.05 * max(k, 0.8)), osso()),
                                                                     ('U', ('ell', cot, (0.1, 0.095, 0.095)), osso()), ('U', ('cap', om + (0, 0.04, 0.05), cot + (0, 0.04, 0.05), 0.025), K["tendao"])])
        ops = [('U', ('ell', cot, (0.095, 0.09, 0.09)), osso()), ('U', ('cap', cot + (0.035, 0, 0), mao + (0.035, 0, 0), 0.042), osso()),
               ('U', ('cap', cot + (-0.035, -0.02, 0.02), mao + (-0.035, 0, 0.02), 0.036), osso()), ('U', ('ell', mao + (0, -0.05, -0.03), (0.1, 0.08, 0.06)), osso())]
        for j in (-1.5, -0.5, 0.5, 1.5):
            b0 = mao + np.array([j * 0.05, -0.08, -0.05]); b1 = b0 + np.array([j * 0.03, -0.28 * k, -0.1]); b2 = b1 + np.array([j * 0.02, -0.26 * k, -0.14])
            ops += [('U', ('cap', mao + (j * 0.03, -0.04, -0.03), b0, 0.035), osso()), ('U', ('cap', b0, b1, 0.035), osso()),
                    ('U', ('ell', b1, (0.042, 0.042, 0.042)), osso()), ('U', ('cap', b1, b2, 0.032, 0.02), K["osso_unha"])]
        P[f"Antebraco_{L}"] = construir(f"Antebraco_{L}", f"Umero_{L}", VS, cot, ops)
    return dict(nome="Relicário", arq="esqueleto composto", pecas=P)

def colisoes_finas(mon, T, grade=0.0625):
    cel = {n: set(map(tuple, np.round((p.P[p.solido()] @ T[n][0].T + T[n][1]) / grade).astype(int))) for n, p in mon["pecas"].items()}
    ns = list(mon["pecas"]); pior = 0
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            if mon["pecas"][a].pai == b or mon["pecas"][b].pai == a:
                continue
            pior = max(pior, len(cel[a] & cel[b]))
    return pior

def auditoria(mon):
    rel = {"pecas": {}}
    for n, p in mon["pecas"].items():
        t = ligar_soltos(p, K["tendao"])
        restos = p.limpar_soltos()
        tri = 2 * len(malha_gulosa(p.g))
        rel["pecas"][n] = dict(vs=p.vs, voxels=p.n(), tendoes_de_ligacao=t, soltos_finais=restos, tris=tri)
    mon["faces"] = {n: faces(p) for n, p in mon["pecas"].items()}
    juntas = []
    for n, p in mon["pecas"].items():
        if p.pai:
            q = mon["pecas"][p.pai]
            juntas.append((n, int((((q.P[q.solido()] - p.pivo) ** 2).sum(1) <= 0.12 ** 2).sum()), int((((p.P[p.solido()] - p.pivo) ** 2).sum(1) <= 0.12 ** 2).sum())))
    col = {}
    for etapa in ("longe", "avanco"):
        col[etapa] = colisoes_finas(mon, O.pose_quadro(mon, etapa))
    col["susto"] = max(colisoes_finas(mon, O.pose_esqueleto(mon, i * 0.1)) for i in range(16))
    cont = np.zeros(len(RGB))
    for f in mon["faces"].values():
        cont += np.bincount(f["cor"], minlength=len(RGB))
    lum = RGB @ np.array([0.2126, 0.7152, 0.0722]); em = np.isin(np.arange(len(RGB)), list(EMIS)); tot = cont.sum()
    rel["valores"] = dict(escuro=round(100 * cont[(lum < 0.25) & ~em].sum() / tot, 1), medio=round(100 * cont[(lum >= 0.25) & (lum < 0.55) & ~em].sum() / tot, 1),
                          claro=round(100 * cont[(lum >= 0.55) & ~em].sum() / tot, 1), brilho=round(100 * cont[em].sum() / tot, 2))
    rel["juntas"] = juntas
    rel["colisao"] = col
    rel["total_voxels"] = sum(v["voxels"] for v in rel["pecas"].values())
    rel["total_tris"] = sum(v["tris"] for v in rel["pecas"].values())
    regras = [("Nenhum voxel solto", all(v["soltos_finais"] == 0 for v in rel["pecas"].values())),
              ("Juntas com pelo menos 8 voxels de cada lado", all(a >= 8 and b >= 8 for _, a, b in juntas)),
              ("Malha abaixo de 20 mil triangulos", all(v["tris"] <= 20000 for v in rel["pecas"].values())),
              ("Nenhuma colisao em quadro nenhum", all(v == 0 for v in col.values())),
              ("Brilho so nos olhos (abaixo de 1%)", rel["valores"]["brilho"] < 1.0)]
    rel["regras"] = [(r, "passa" if ok else "falha") for r, ok in regras]
    return rel

if __name__ == "__main__":
    mon = relicario()
    rel = auditoria(mon)
    json.dump(rel, open(os.path.join(B.OUT, "relicario_auditoria.json"), "w"), indent=1, ensure_ascii=False, default=float)
    for r in rel["regras"]:
        print(r)
    print("voxels", rel["total_voxels"], "tris", rel["total_tris"], "valores", rel["valores"], "colisao", rel["colisao"])
    print("ligacoes", {n: v["tendoes_de_ligacao"] for n, v in rel["pecas"].items() if v["tendoes_de_ligacao"]})
    print("juntas fracas", [j for j in rel["juntas"] if min(j[1], j[2]) < 8])
    out = B.OUT
    T = O.pose_quadro(mon, "longe")
    it = [(mon["faces"][n], *T[n]) for n in mon["pecas"]]
    vis = Image.new("RGB", (3 * 400, 500))
    for k, d in enumerate(((0.0001, -0.08, 1), (1, -0.08, 0.0001), (0.55, -0.2, 0.83))):
        vis.paste(render(it, camera_orto(d, Y, (0, 1.9, 0.3), 118, 400, 500), RGB, EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.5, ambiente=0.5), (k * 400, 0))
    vis.save(os.path.join(out, "relicario_vistas.png"))
    cr = Image.new("RGB", (2 * 450, 420))
    for k, d in enumerate(((0.25, -0.05, 1), (-0.6, -0.1, 0.8))):
        cr.paste(render(it, camera_orto(d, Y, (0, 3.2, -0.3), 360, 450, 420), RGB, EMIS, fundo=(0.2, 0.19, 0.22), bloom=0.6, ambiente=0.5), (k * 450, 0))
    cr.save(os.path.join(out, "relicario_cranio.png"))
    chao = construir("Chao", None, 0.25, (0, 0, 0), [('U', ('ell', (0, -0.15, 0), (6.0, 0.14, 9.0)), K["pedra_s"])])
    fch = faces(chao)
    sb = Image.new("RGB", (3 * 420, 236))
    for k, (etapa, dist) in enumerate((("longe", 6.0), ("avanco", 3.4), ("rosto", 2.6))):
        T = O.pose_quadro(mon, etapa)
        olho = np.array([0.15, 2.4, -dist]); alvo = np.array([0, 2.0 if etapa != "rosto" else 2.8, 0 if etapa != "rosto" else -1.2])
        it = [(mon["faces"][n], *T[n]) for n in mon["pecas"]] + [(fch, np.eye(3), np.zeros(3))]
        sb.paste(render(it, camera_persp(olho, alvo, Y, 70, 420, 236), RGB, EMIS, fundo=(0, 0, 0), lanterna=(olho + np.array([0.4, -0.8, 0.2]), 1.7, 4.0 + dist * 0.4),
                        neblina=((0.01, 0.01, 0.02), 3.0 + dist * 0.5, 9.0 + dist), bloom=0.9), (k * 420, 0))
    sb.save(os.path.join(out, "relicario_storyboard.png"))
