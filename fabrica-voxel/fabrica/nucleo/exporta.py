"""Exportadores: malha gulosa por cor, GLB (um no por osso, uma malha por peca, cor de vertice, animacoes),
.vox do MagicaVoxel (um objeto por peca), caixas para a rota Parts e os ModuleScripts de dados em Luau.

Decisao de cor para o Roblox (docs/pesquisa/03-roblox-tecnico.md): cor de VERTICE, sem textura. MeshPart nao
tem filtro por vizinho mais proximo; cor de vertice nao borra nem vaza. Falta confirmar no Studio.
"""
from __future__ import annotations

import json
import struct

import numpy as np

from . import util_grade as ug
from .contrato import VERSAO_FABRICA, Clipe, Modelo, quat_mul, quat_para_matriz
from .paleta import hex_para_rgb

TETO_TRIANGULOS = 20000
_EIXOS_FACE = [(0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1)]  # dir, esq, topo, base, tras, frente


def _retangulos(mask: np.ndarray):
    """Decomposicao gulosa de uma mascara 2D de rotulos (0 = nada) em retangulos (i, j, h, w, rotulo)."""
    m = mask.copy()
    H, W = m.shape
    out = []
    for i in range(H):
        j = 0
        while j < W:
            r = m[i, j]
            if r == 0:
                j += 1
                continue
            w = 1
            while j + w < W and m[i, j + w] == r:
                w += 1
            h = 1
            while i + h < H and np.all(m[i + h, j:j + w] == r):
                h += 1
            m[i:i + h, j:j + w] = 0
            out.append((i, j, h, w, int(r)))
            j += w
    return out


def malha_da_grade(grade, cores_sel=None):
    """Malha gulosa por cor. Devolve (pos [n,3] studs em repouso, normais [n,3], cor_idx [n], indices [m,3]).
    cores_sel: conjunto de indices de cor a incluir (None = todas)."""
    oc = grade.mat > 0
    fe = ug.faces_expostas(oc)
    P, N, C, I = [], [], [], []
    for f, (eixo, sinal) in enumerate(_EIXOS_FACE):
        rot = np.where(fe[f], grade.cor, 0)
        if cores_sel is not None:
            rot = np.where(np.isin(rot, list(cores_sel)), rot, 0)
        u, v = [e for e in range(3) if e != eixo]
        rot = np.moveaxis(rot, eixo, 0)                       # [n_eixo, n_u, n_v]
        for s in range(rot.shape[0]):
            if not rot[s].any():
                continue
            for (i, j, h, w, r) in _retangulos(rot[s]):
                base = np.zeros(3)
                base[eixo] = s + (1 if sinal > 0 else 0)
                c = []
                for (du, dv) in ((0, 0), (h, 0), (h, w), (0, w)):
                    q = base.copy()
                    q[u] = i + du
                    q[v] = j + dv
                    c.append(q)
                n = np.zeros(3)
                n[eixo] = sinal
                # ordem anti-horaria vista de fora
                if np.dot(np.cross(c[1] - c[0], c[2] - c[0]), n) < 0:
                    c = [c[0], c[3], c[2], c[1]]
                k = len(P)
                P += [grade.origem + q * grade.v for q in c]
                N += [n] * 4
                C += [r] * 4
                I += [(k, k + 1, k + 2), (k, k + 2, k + 3)]
    return (np.array(P, np.float32).reshape(-1, 3), np.array(N, np.float32).reshape(-1, 3),
            np.array(C, np.int32), np.array(I, np.uint32).reshape(-1, 3))


def contar_triangulos(modelo: Modelo) -> dict:
    por_peca = {p.nome: int(len(malha_da_grade(p.grade)[3])) for p in modelo.pecas}
    return {"por_peca": por_peca, "total": sum(por_peca.values()), "maior": max(por_peca.values() or [0])}


def caixas_gulosas(grade) -> list[tuple]:
    """Funde voxels vizinhos de mesma cor em paralelepipedos: [(cx, cy, cz, sx, sy, sz, cor_idx)] em studs."""
    c = grade.cor.copy()
    nx, ny, nz = c.shape
    out = []
    for i, j, k in np.argwhere(c > 0):
        r = c[i, j, k]
        if r == 0:
            continue
        a = 1
        while i + a < nx and c[i + a, j, k] == r:
            a += 1
        b = 1
        while k + b < nz and np.all(c[i:i + a, j, k + b] == r):
            b += 1
        h = 1
        while j + h < ny and np.all(c[i:i + a, j + h, k:k + b] == r):
            h += 1
        c[i:i + a, j:j + h, k:k + b] = 0
        tam = np.array([a, h, b]) * grade.v
        cen = grade.origem + (np.array([i, j, k]) + np.array([a, h, b]) / 2) * grade.v
        out.append((*np.round(cen, 4), *np.round(tam, 4), int(r)))
    return out


# --------------------------------------------------------------------------- GLB

class _Buf:
    def __init__(self):
        self.b = bytearray()
        self.views, self.acc = [], []

    def por(self, arr: np.ndarray, tipo: str, comp: int, alvo=None, minmax=False, norm=False) -> int:
        while len(self.b) % 4:
            self.b.append(0)
        dados = arr.tobytes()
        v = {"buffer": 0, "byteOffset": len(self.b), "byteLength": len(dados)}
        if alvo:
            v["target"] = alvo
        self.b += dados
        self.views.append(v)
        a = {"bufferView": len(self.views) - 1, "componentType": comp, "count": int(arr.shape[0]), "type": tipo}
        if norm:
            a["normalized"] = True
        if minmax:
            a["min"] = [float(x) for x in np.atleast_1d(arr.min(0))]
            a["max"] = [float(x) for x in np.atleast_1d(arr.max(0))]
        self.acc.append(a)
        return len(self.acc) - 1


def _linear(rgb8):
    c = np.asarray(rgb8, float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def escrever_glb(modelo: Modelo, caminho, *, escala: float = 1.0, com_animacao: bool = True) -> dict:
    """Grava o GLB. escala=1 -> studs (Roblox); escala=0.28 -> metros (lojas). Devolve estatisticas."""
    buf = _Buf()
    nos = [{"name": "Modelo", "children": [], "extras": {"id": modelo.id, "fabrica": VERSAO_FABRICA}}]
    malhas, idx_no = [], {}
    tab = np.array([(0, 0, 0)] + [hex_para_rgb(c) for c in modelo.cores], float)
    lin = np.concatenate([_linear(tab), np.ones((len(tab), 1))], 1)
    mats = [{"name": "CorDeVertice", "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
                                                              "roughnessFactor": 1}},
            {"name": "Brilho", "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
                                                        "roughnessFactor": 1}, "emissiveFactor": [1, 1, 1]}]
    for o in modelo.ossos:
        pai = modelo.osso(o.pai).pivo if o.pai else (0, 0, 0)
        nos.append({"name": o.nome if not any(p.nome == o.nome for p in modelo.pecas) else f"Osso_{o.nome}",
                    "translation": [float((a - b) * escala) for a, b in zip(o.pivo, pai)], "children": [],
                    "extras": {"papel": o.papel}})
        if tuple(o.repouso) != (0.0, 0.0, 0.0, 1.0):
            nos[-1]["rotation"] = [float(x) for x in o.repouso]
        idx_no[o.nome] = len(nos) - 1
        nos[idx_no[o.pai] if o.pai else 0]["children"].append(len(nos) - 1)
    tri_total = 0
    brilho = set(modelo.cores_brilho)
    todas = set(range(1, len(modelo.cores) + 1))
    for p in modelo.pecas:
        piv = np.array(modelo.osso(p.osso).pivo)
        for sufixo, sel, mat in (("", todas - brilho, 0), ("_Brilho", brilho, 1)):
            if not sel:
                continue
            pos, nrm, cor, ind = malha_da_grade(p.grade, sel)
            if len(ind) == 0:
                continue
            tri_total += len(ind)
            a_pos = buf.por(((pos - piv) * escala).astype(np.float32), "VEC3", 5126, 34962, minmax=True)
            a_nrm = buf.por(nrm, "VEC3", 5126, 34962)
            a_cor = buf.por((lin[cor] * 255 + 0.5).astype(np.uint8), "VEC4", 5121, 34962, norm=True)
            a_ind = buf.por(ind.reshape(-1).astype(np.uint32), "SCALAR", 5125, 34963)
            malhas.append({"name": p.nome + sufixo, "primitives": [{"attributes": {"POSITION": a_pos, "NORMAL": a_nrm,
                           "COLOR_0": a_cor}, "indices": a_ind, "material": mat}]})
            nos.append({"name": p.nome + sufixo, "mesh": len(malhas) - 1})
            nos[idx_no[p.osso]]["children"].append(len(nos) - 1)
    anims = []
    if com_animacao:
        for cl in modelo.clipes.values():
            tempos = (np.arange(cl.n_quadros) / cl.fps).astype(np.float32)
            a_t = buf.por(tempos, "SCALAR", 5126, minmax=True)
            samp, chan = [], []
            for k, nome in enumerate(cl.ossos):
                o = modelo.osso(nome)
                pai = np.array(modelo.osso(o.pai).pivo) if o.pai else np.zeros(3)
                rep = (np.array(o.pivo) - pai)
                tem_rep = tuple(o.repouso) != (0.0, 0.0, 0.0, 1.0)
                tr_k, rot_k = cl.trans[:, k], cl.rot[:, k]
                if tem_rep:                       # glTF: o canal substitui a rotacao do no, entao inclui o repouso
                    Rr = quat_para_matriz(o.repouso)[:3, :3]
                    tr_k = tr_k @ Rr.T
                    rot_k = np.array([quat_mul(o.repouso, q) for q in rot_k])
                if np.abs(cl.trans[:, k]).max() > 1e-5:
                    a = buf.por(((rep + tr_k) * escala).astype(np.float32), "VEC3", 5126)
                    samp.append({"input": a_t, "output": a, "interpolation": "LINEAR"})
                    chan.append({"sampler": len(samp) - 1, "target": {"node": idx_no[nome], "path": "translation"}})
                if np.abs(cl.rot[:, k, :3]).max() > 1e-5:
                    a = buf.por(rot_k.astype(np.float32), "VEC4", 5126)
                    samp.append({"input": a_t, "output": a, "interpolation": "LINEAR"})
                    chan.append({"sampler": len(samp) - 1, "target": {"node": idx_no[nome], "path": "rotation"}})
                if cl.escala is not None and np.abs(cl.escala[:, k] - 1).max() > 1e-5:
                    a = buf.por(cl.escala[:, k].astype(np.float32), "VEC3", 5126)
                    samp.append({"input": a_t, "output": a, "interpolation": "LINEAR"})
                    chan.append({"sampler": len(samp) - 1, "target": {"node": idx_no[nome], "path": "scale"}})
            if chan:
                anims.append({"name": cl.nome, "samplers": samp, "channels": chan})
    for n in nos:
        if not n.get("children"):
            n.pop("children", None)
    while len(buf.b) % 4:
        buf.b.append(0)
    g = {"asset": {"version": "2.0", "generator": f"Fabrica de Voxel {VERSAO_FABRICA}"}, "scene": 0,
         "scenes": [{"nodes": [0]}], "nodes": nos, "meshes": malhas, "materials": mats,
         "accessors": buf.acc, "bufferViews": buf.views, "buffers": [{"byteLength": len(buf.b)}]}
    if anims:
        g["animations"] = anims
    js = json.dumps(g, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(buf.b)
    with open(caminho, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(buf.b), 0x004E4942) + bytes(buf.b))
    return {"triangulos": tri_total, "malhas": len(malhas), "animacoes": len(anims), "bytes": total}


def ler_glb(caminho) -> dict:
    """Rele o JSON do GLB (para conferencia)."""
    b = open(caminho, "rb").read()
    magic, ver, total = struct.unpack_from("<III", b, 0)
    assert magic == 0x46546C67 and ver == 2 and total == len(b), "cabecalho GLB invalido"
    n, tipo = struct.unpack_from("<II", b, 12)
    assert tipo == 0x4E4F534A
    return json.loads(b[20:20 + n])


# --------------------------------------------------------------------------- .vox (MagicaVoxel)

def _chunk(nome: bytes, conteudo: bytes, filhos: bytes = b"") -> bytes:
    return nome + struct.pack("<II", len(conteudo), len(filhos)) + conteudo + filhos


def _str(s: str) -> bytes:
    b = s.encode()
    return struct.pack("<I", len(b)) + b


def _dic(d: dict) -> bytes:
    return struct.pack("<I", len(d)) + b"".join(_str(k) + _str(str(v)) for k, v in d.items())


def escrever_vox(modelo: Modelo, caminho) -> dict:
    """Um objeto por peca, com nome, na posicao de repouso. Eixos do MagicaVoxel: Z para cima.
    Conversao: (x, y, z) da fabrica -> (x, -z, y), rotacao propria (nao espelha)."""
    if len(modelo.cores) > 255:
        raise ValueError(f"o modelo tem {len(modelo.cores)} cores e o .vox aceita 255; reduza rampas/materiais")
    filhos = b""
    nos = b""
    ids = []
    for i, p in enumerate(modelo.pecas):
        c = p.grade.cor
        nx, ny, nz = c.shape
        if max(nx, ny, nz) > 256:
            raise ValueError(f'peca "{p.nome}" tem {max(nx, ny, nz)} voxels num eixo; o .vox aceita 256. Divida a peca.')
        idx = np.argwhere(c > 0)
        vx = np.stack([idx[:, 0], nz - 1 - idx[:, 2], idx[:, 1], c[c > 0]], 1).astype(np.uint8)
        filhos += _chunk(b"SIZE", struct.pack("<III", nx, nz, ny))
        filhos += _chunk(b"XYZI", struct.pack("<I", len(vx)) + vx.tobytes())
        o = np.round(p.grade.origem / p.grade.v).astype(int)
        t = (int(o[0] + nx // 2), int(-(o[2] + nz) + nz // 2), int(o[1] + ny // 2))
        nt, ns = 2 + 2 * i, 3 + 2 * i
        ids.append(nt)
        nos += _chunk(b"nTRN", struct.pack("<I", nt) + _dic({"_name": p.nome}) + struct.pack("<IiiI", ns, -1, 0, 1)
                      + _dic({"_t": f"{t[0]} {t[1]} {t[2]}"}))
        nos += _chunk(b"nSHP", struct.pack("<I", ns) + _dic({}) + struct.pack("<I", 1) + struct.pack("<I", i) + _dic({}))
    raiz = _chunk(b"nTRN", struct.pack("<I", 0) + _dic({}) + struct.pack("<IiiI", 1, -1, -1, 1) + _dic({}))
    grp = _chunk(b"nGRP", struct.pack("<I", 1) + _dic({}) + struct.pack("<I", len(ids)) + struct.pack(f"<{len(ids)}I", *ids))
    pal = bytearray(1024)
    for i, hx in enumerate(modelo.cores):
        pal[i * 4:i * 4 + 4] = bytes((*hex_para_rgb(hx), 255))
    filhos += raiz + grp + nos + _chunk(b"RGBA", bytes(pal))
    with open(caminho, "wb") as f:
        f.write(b"VOX " + struct.pack("<I", 200) + _chunk(b"MAIN", b"", filhos))
    return {"modelos": len(modelo.pecas)}


# --------------------------------------------------------------------------- Luau (ModuleScripts de dados)

def _n(x) -> str:
    s = f"{float(x):.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _id_luau(s: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in s.replace(".", "_").split("_") if p)


def luau_dados(modelo: Modelo, *, com_caixas: bool = True) -> str:
    v3 = lambda t: "{" + ", ".join(_n(x) for x in t) + "}"
    L = [f"-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_{_id_luau(modelo.id)}",
         "-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.",
         "-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).",
         "return {",
         f'\tId = "{modelo.id}", Nome = "{modelo.nome}", VersaoFabrica = "{VERSAO_FABRICA}",',
         f"\tAltura = {_n(modelo.caixa()[1][1])},",
         "\tOssos = { -- pais antes dos filhos; Repouso = quaternion {x, y, z, w} do giro fixo do osso (vai no C0)"]
    for o in modelo.ossos:
        mola = "nil" if not o.mola else ("{FreqHz = " + _n(o.mola.get("freq_hz", 2.5)) + ", Amort = " +
                                         _n(o.mola.get("amort", 0.6)) + ", MaxGraus = " + _n(o.mola.get("max_graus", 25)) + "}")
        rep = "" if tuple(o.repouso) == (0.0, 0.0, 0.0, 1.0) else ", Repouso = {" + ", ".join(_n(x) for x in o.repouso) + "}"
        L.append(f'\t\t{{Nome = "{o.nome}", Pai = "{o.pai or ""}", Pivo = {v3(o.pivo)}, Papel = "{o.papel}", Mola = {mola}{rep}}},')
    L += ["\t},", "\tPecas = { -- uma malha (MeshPart) por peca; varias pecas podem usar o mesmo osso"]
    for p in modelo.pecas:
        a, b = p.grade.caixa()
        tb = bool(set(np.unique(p.grade.cor).tolist()) & set(modelo.cores_brilho))
        L.append(f'\t\t{{Nome = "{p.nome}", Osso = "{p.osso}", Centro = {v3((a + b) / 2)}, Tamanho = {v3(b - a)}, '
                 f'Corte = {_n(p.grade.v)}, TemBrilho = {"true" if tb else "false"}, '
                 f'EscalaAnimada = {"true" if p.escala_animada else "false"}}},')
    L += ["\t},", "\tSoquetes = {"]
    for s in modelo.soquetes:
        L.append(f'\t\t{{Nome = "{s.nome}", Osso = "{s.osso}", Pos = {v3(s.pos)}}},')
    L.append("\t},")
    if com_caixas:
        L.append("\tCaixas = { -- por peca: {cx, cy, cz, sx, sy, sz, corHex, neon}; monta o modelo com Parts, sem importar malha")
        total = 0
        for p in modelo.pecas:
            cx = caixas_gulosas(p.grade)
            total += len(cx)
            L.append(f"\t\t{p.nome} = {{")
            for c in cx:
                hx = modelo.cores[c[6] - 1].lstrip("#")
                L.append("\t\t\t{" + ", ".join(_n(x) for x in c[:6]) + f', "{hx}", {1 if c[6] in modelo.cores_brilho else 0}}},')
            L.append("\t\t},")
        L += ["\t},", f"\tTotalCaixas = {total},"]
    L += ["}", ""]
    return "\n".join(L)


def luau_clipes(modelo: Modelo, clipes: dict[str, Clipe] | None = None, nome_modulo: str | None = None) -> str:
    clipes = modelo.clipes if clipes is None else clipes
    L = [f"-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Clipes, com o nome "
         f"{nome_modulo or 'Clipes_' + _id_luau(modelo.id)}",
         "-- Quadros assados a 30 fps pela Fabrica de Voxel. T = delta de posicao local (studs), R = quaternion xyzw,",
         "-- E = escala. Osso sem trilha fica em repouso. NAO edite a mao.",
         "return {", "\tFps = 30,", "\tClipes = {"]
    for cl in clipes.values():
        marc = ", ".join(f'{{"{n}", {_n(t)}}}' for n, t in cl.marcadores)
        L.append(f'\t\t{cl.nome} = {{Duracao = {_n(cl.duracao)}, Laco = {"true" if cl.laco else "false"}, '
                 f"N = {cl.n_quadros}, VelRaiz = {_n(cl.vel_raiz)}, Marcadores = {{{marc}}}, Trilhas = {{")
        for k, nome in enumerate(cl.ossos):
            partes = []
            if np.abs(cl.trans[:, k]).max() > 1e-5:
                partes.append("T = {" + ",".join(_n(v) for v in cl.trans[:, k].ravel()) + "}")
            if np.abs(cl.rot[:, k, :3]).max() > 1e-5:
                partes.append("R = {" + ",".join(_n(v) for v in cl.rot[:, k].ravel()) + "}")
            if cl.escala is not None and np.abs(cl.escala[:, k] - 1).max() > 1e-5:
                partes.append("E = {" + ",".join(_n(v) for v in cl.escala[:, k].ravel()) + "}")
            if partes:
                L.append(f"\t\t\t{nome} = {{" + ", ".join(partes) + "},")
        L.append("\t\t}},")
    L += ["\t},", "}", ""]
    return "\n".join(L)
