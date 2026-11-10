"""Forja voxel: nucleo generico (ruido, primitivas, pecas, malha gulosa, GLB, VOX, render).
Unidades em studs. Y para cima, frente do modelo em -Z (convencao do Roblox)."""
import json, struct, io, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------------- ruido ----------------
def _hash(ix, iy, iz, seed):
    u = np.uint64
    h = (ix.astype(u) * u(73856093)) ^ (iy.astype(u) * u(19349663)) ^ (iz.astype(u) * u(83492791)) ^ u((seed * 2654435761) % 2**32)
    h = (h ^ (h >> u(13))) * u(1274126177)
    h = h ^ (h >> u(16))
    return (h & u(0xFFFF)).astype(np.float64) / 65535.0

def ruido(P, freq=1.0, seed=0):
    Q = P * freq
    i0 = np.floor(Q).astype(np.int64)
    f = Q - i0
    s = f * f * (3 - 2 * f)
    out = np.zeros(len(P))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (s[:, 0] if dx else 1 - s[:, 0]) * (s[:, 1] if dy else 1 - s[:, 1]) * (s[:, 2] if dz else 1 - s[:, 2])
                out += w * _hash(i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz, seed)
    return out

# ---------------- primitivas (mascaras sobre pontos Nx3) ----------------
def esfera(P, c, r):
    return ((P - c) ** 2).sum(1) <= r * r

def elipsoide(P, c, r, R=None):
    D = P - np.asarray(c, float)
    if R is not None:
        D = D @ R
    return ((D / np.asarray(r, float)) ** 2).sum(1) <= 1.0

def capsula(P, a, b, ra, rb=None, pontas=True):
    a = np.asarray(a, float); b = np.asarray(b, float)
    rb = ra if rb is None else rb
    ab = b - a
    t = ((P - a) @ ab) / max((ab * ab).sum(), 1e-9)
    tc = np.clip(t, 0, 1)
    Q = a + tc[:, None] * ab
    r = ra + (rb - ra) * tc
    m = ((P - Q) ** 2).sum(1) <= r * r
    if not pontas:
        m &= (t >= 0) & (t <= 1)
    return m

def cone(P, base, ponta, r):
    return capsula(P, base, ponta, r, 0.0, pontas=False)

def caixa_prim(spec):
    """Caixa envolvente de uma primitiva declarativa."""
    k = spec[0]
    if k == 'esf':
        c, r = np.asarray(spec[1], float), spec[2]
        return c - r, c + r
    if k == 'ell':
        c, r = np.asarray(spec[1], float), np.asarray(spec[2], float)
        m = r.max() if len(spec) > 3 and spec[3] is not None else r
        return c - m, c + m
    if k in ('cap', 'cone'):
        a, b = np.asarray(spec[1], float), np.asarray(spec[2], float)
        r = max(spec[3], spec[4] if (k == 'cap' and len(spec) > 4 and spec[4] is not None) else spec[3])
        return np.minimum(a, b) - r, np.maximum(a, b) + r
    raise ValueError(k)

def avaliar(P, spec):
    k = spec[0]
    if k == 'esf':
        return esfera(P, np.asarray(spec[1], float), spec[2])
    if k == 'ell':
        return elipsoide(P, spec[1], spec[2], spec[3] if len(spec) > 3 else None)
    if k == 'cap':
        return capsula(P, spec[1], spec[2], spec[3], spec[4] if len(spec) > 4 else None)
    if k == 'cone':
        return cone(P, spec[1], spec[2], spec[3])
    raise ValueError(k)

# ---------------- peca ----------------
VIZ6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

class Peca:
    def __init__(self, nome, pai, vs, lo, hi, pivo, grupo='', densidade=1.0):
        self.nome, self.pai, self.vs, self.grupo, self.densidade = nome, pai, vs, grupo, densidade
        lo = np.floor(np.asarray(lo, float) / vs - 1) * vs
        hi = np.ceil(np.asarray(hi, float) / vs + 1) * vs
        self.origem = lo
        self.dims = tuple(int(x) for x in np.maximum(1, np.round((hi - lo) / vs)))
        self.g = np.zeros(self.dims, np.uint8)
        self.pivo = np.asarray(pivo, float)
        idx = np.indices(self.dims).reshape(3, -1).T
        self.P = self.origem + (idx + 0.5) * vs

    def unir(self, mascara, cor):
        m = mascara.reshape(self.dims)
        if np.isscalar(cor):
            self.g[m] = cor
        else:
            self.g[m] = np.asarray(cor).reshape(self.dims)[m]

    def cavar(self, mascara):
        self.g[mascara.reshape(self.dims)] = 0

    def pintar(self, mascara, cor):
        m = mascara.reshape(self.dims) & (self.g > 0)
        if np.isscalar(cor):
            self.g[m] = cor
        else:
            self.g[m] = np.asarray(cor).reshape(self.dims)[m]

    def solido(self):
        return (self.g > 0).reshape(-1)

    def superficie(self):
        s = self.g > 0
        G = np.pad(s, 1)
        viz_vazio = np.zeros_like(s)
        for d in VIZ6:
            viz_vazio |= ~G[1 + d[0]:G.shape[0] - 1 + d[0], 1 + d[1]:G.shape[1] - 1 + d[1], 1 + d[2]:G.shape[2] - 1 + d[2]]
        return (s & viz_vazio).reshape(-1)

    def topo_livre(self):
        s = self.g > 0
        cima = np.zeros_like(s)
        cima[:, :-1, :] = s[:, 1:, :]
        return (s & ~cima).reshape(-1)

    def limpar_soltos(self):
        """Regra do Trove: nada solto. Mantem so o componente ligado ao pivo (vizinhos de face)."""
        s = self.g > 0
        if not s.any():
            return 0
        idx = np.argwhere(s)
        centros = self.origem + (idx + 0.5) * self.vs
        semente = idx[np.argmin(((centros - self.pivo) ** 2).sum(1))]
        cur = np.zeros_like(s)
        cur[tuple(semente)] = True
        while True:
            nxt = cur.copy()
            nxt[1:] |= cur[:-1]; nxt[:-1] |= cur[1:]
            nxt[:, 1:] |= cur[:, :-1]; nxt[:, :-1] |= cur[:, 1:]
            nxt[:, :, 1:] |= cur[:, :, :-1]; nxt[:, :, :-1] |= cur[:, :, 1:]
            nxt &= s
            if np.array_equal(nxt, cur):
                break
            cur = nxt
        soltos = int(s.sum() - cur.sum())
        self.g[s & ~cur] = 0
        return soltos

    def n(self):
        return int((self.g > 0).sum())

    def centro_massa(self):
        s = self.solido()
        return self.P[s].mean(0) if s.any() else self.pivo

    def massa(self):
        return self.n() * self.vs ** 3 * self.densidade

def construir(nome, pai, vs, pivo, ops, grupo='', densidade=1.0, margem=0.0):
    """ops: lista de (modo, spec, cor). modo: 'U' unir, 'C' cavar, 'P' pintar.
    cor: int ou funcao(P) -> array de indices."""
    los, his = [], []
    for modo, spec, _ in ops:
        if modo == 'U':
            lo, hi = caixa_prim(spec)
            los.append(lo); his.append(hi)
    lo = np.min(los, 0) - margem; hi = np.max(his, 0) + margem
    p = Peca(nome, pai, vs, lo, hi, pivo, grupo, densidade)
    for modo, spec, cor in ops:
        m = avaliar(p.P, spec) if not callable(spec) else spec(p.P)
        c = cor(p.P) if callable(cor) else cor
        if modo == 'U':
            p.unir(m, c)
        elif modo == 'C':
            p.cavar(m)
        else:
            p.pintar(m, c)
    return p

# ---------------- malha gulosa ----------------
def _gulosa2d(C):
    H, W = C.shape
    rows = C.tolist()
    used = [[False] * W for _ in range(H)]
    out = []
    for i in range(H):
        ri, ui = rows[i], used[i]
        if not any(ri):
            continue
        j = 0
        while j < W:
            c = ri[j]
            if c == 0 or ui[j]:
                j += 1
                continue
            w = 1
            while j + w < W and ri[j + w] == c and not ui[j + w]:
                w += 1
            h = 1
            while i + h < H:
                r2, u2 = rows[i + h], used[i + h]
                if all(r2[x] == c and not u2[x] for x in range(j, j + w)):
                    h += 1
                else:
                    break
            for y in range(i, i + h):
                uy = used[y]
                for x in range(j, j + w):
                    uy[x] = True
            out.append((i, j, h, w, c))
            j += w
    return out

def malha_gulosa(g):
    """Quads (eixo, sinal, plano, u0, v0, du, dv, cor) em unidades de voxel."""
    quads = []
    G = np.pad(g, 1)
    for ax in range(3):
        A = np.moveaxis(G, ax, 0)
        for k in range(1, A.shape[0]):
            prev, cur = A[k - 1], A[k]
            for sinal, C in ((1, np.where((prev > 0) & (cur == 0), prev, 0)), (-1, np.where((cur > 0) & (prev == 0), cur, 0))):
                if not C.any():
                    continue
                for (i, j, h, w, c) in _gulosa2d(C):
                    quads.append((ax, sinal, k - 1, i - 1, j - 1, h, w, c))
    return quads

def triangulos(g):
    return 2 * len(malha_gulosa(g))

# ---------------- faces para render ----------------
def faces(p):
    s = p.g
    G = np.pad(s, 1)
    cs, ns, cols, tans = [], [], [], []
    X, Y, Z = s.shape
    for ax in range(3):
        for sinal in (1, -1):
            sl = [slice(1, X + 1), slice(1, Y + 1), slice(1, Z + 1)]
            sl[ax] = slice(1 + sinal, (X, Y, Z)[ax] + 1 + sinal)
            viz = G[tuple(sl)]
            m = (s > 0) & (viz == 0)
            idx = np.argwhere(m)
            if len(idx) == 0:
                continue
            n = np.zeros(3); n[ax] = sinal
            c = p.origem + (idx + 0.5) * p.vs + n * p.vs / 2
            cs.append(c); ns.append(np.repeat(n[None], len(idx), 0)); cols.append(s[m])
            a1, a2 = [a for a in range(3) if a != ax]
            t1 = np.zeros(3); t1[a1] = p.vs / 2
            t2 = np.zeros(3); t2[a2] = p.vs / 2
            tans.append(np.repeat(np.concatenate([t1, t2])[None], len(idx), 0))
    if not cs:
        return None
    return dict(c=np.concatenate(cs), n=np.concatenate(ns), cor=np.concatenate(cols), tan=np.concatenate(tans))

# ---------------- camera e render ----------------
def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)

def camera_orto(direcao, cima, centro, escala, W, H):
    d = _unit(direcao); r = _unit(np.cross(d, cima)); u = np.cross(r, d)
    return dict(tipo='orto', d=d, r=r, u=u, c=np.asarray(centro, float), s=escala, W=W, H=H)

def camera_persp(olho, alvo, cima, fov_graus, W, H):
    olho = np.asarray(olho, float)
    d = _unit(np.asarray(alvo, float) - olho); r = _unit(np.cross(d, cima)); u = np.cross(r, d)
    f = (H / 2) / math.tan(math.radians(fov_graus) / 2)
    return dict(tipo='persp', d=d, r=r, u=u, e=olho, f=f, W=W, H=H)

def projetar(cam, P):
    if cam['tipo'] == 'orto':
        D = P - cam['c']
        x = cam['W'] / 2 + cam['s'] * (D @ cam['r'])
        y = cam['H'] / 2 - cam['s'] * (D @ cam['u'])
        z = D @ cam['d']
    else:
        D = P - cam['e']
        z = D @ cam['d']
        zz = np.maximum(z, 1e-3)
        x = cam['W'] / 2 + cam['f'] * (D @ cam['r']) / zz
        y = cam['H'] / 2 - cam['f'] * (D @ cam['u']) / zz
    return x, y, z

def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0

def render(itens, cam, paleta, emissivos, fundo=(0.93, 0.93, 0.93), luzes=None, ambiente=0.42,
           lanterna=None, neblina=None, bloom=0.0, fios=(), grade_fundo=None, chao_y=None, img_fundo=None):
    """itens: lista de (faces_dict, R, t). paleta: Nx3 em 0..1 (indice 0 sem uso)."""
    W, H = cam['W'], cam['H']
    luzes = luzes or [(_unit((-0.5, -1.0, -0.35)), 0.62), (_unit((0.7, -0.2, 0.6)), 0.18)]
    Cs, Ns, Cols, T1, T2 = [], [], [], [], []
    for f, R, t in itens:
        if f is None:
            continue
        Cs.append(f['c'] @ R.T + t); Ns.append(f['n'] @ R.T)
        T1.append(f['tan'][:, :3] @ R.T); T2.append(f['tan'][:, 3:] @ R.T); Cols.append(f['cor'])
    C = np.concatenate(Cs); N = np.concatenate(Ns); cor = np.concatenate(Cols); t1 = np.concatenate(T1); t2 = np.concatenate(T2)
    if cam['tipo'] == 'orto':
        vis = (N @ cam['d']) < -1e-6
    else:
        vis = ((C - cam['e']) * N).sum(1) < 0
    C, N, cor, t1, t2 = C[vis], N[vis], cor[vis], t1[vis], t2[vis]
    cantos = [C - t1 - t2, C + t1 - t2, C + t1 + t2, C - t1 + t2]
    xs, ys, zs = [], [], []
    for k in cantos:
        x, y, z = projetar(cam, k)
        xs.append(x); ys.append(y); zs.append(z)
    xs = np.stack(xs, 1); ys = np.stack(ys, 1); zs = np.stack(zs, 1)
    _, _, zc = projetar(cam, C)
    ok = np.ones(len(C), bool)
    if cam['tipo'] == 'persp':
        ok = zs.min(1) > 0.05
    base = paleta[cor]
    emis = np.isin(cor, list(emissivos))
    luz = np.full(len(C), ambiente)
    for dl, it in luzes:
        luz += it * np.clip(-(N @ dl), 0, None)
    luz *= np.where(N[:, 1] < -0.5, 0.78, 1.0)
    if lanterna is not None:
        pos, it, alcance = lanterna
        V = pos - C
        dist = np.linalg.norm(V, axis=1)
        lam = np.clip((N * V).sum(1) / np.maximum(dist, 1e-6), 0, None)
        luz = 0.06 + it * lam / (1 + (dist / alcance) ** 2) + (luz - ambiente) * 0.08
    rgb = base * luz[:, None]
    if neblina is not None:
        cor_n, d0, d1 = neblina
        fz = np.clip((zc - d0) / (d1 - d0), 0, 1)[:, None]
        rgb = rgb * (1 - fz) + np.asarray(cor_n) * fz
    rgb[emis] = base[emis]
    rgb = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    ordem = np.argsort(-zc)
    if img_fundo is not None:
        img = img_fundo.copy()
    else:
        img = Image.new('RGB', (W, H), tuple(int(255 * v) for v in fundo))
    dr = ImageDraw.Draw(img)
    if grade_fundo is not None:
        _grade(dr, cam, grade_fundo, chao_y)
    glow = Image.new('RGB', (W, H), (0, 0, 0)) if bloom > 0 else None
    dg = ImageDraw.Draw(glow) if glow is not None else None
    xs_l, ys_l, rgb_l, emis_l, ok_l = xs.tolist(), ys.tolist(), rgb.tolist(), emis.tolist(), ok.tolist()
    for i in ordem.tolist():
        if not ok_l[i]:
            continue
        pts = list(zip(xs_l[i], ys_l[i]))
        c = tuple(rgb_l[i])
        dr.polygon(pts, fill=c, outline=c)
        if dg is not None:
            gc = c if emis_l[i] else (0, 0, 0)
            dg.polygon(pts, fill=gc, outline=gc)
    for p0, p1, corf, larg, curva in fios:
        tt = np.linspace(0, 1, 16)[:, None]
        pts3 = p0 + (p1 - p0) * tt + np.array([0, -1.0, 0]) * (curva * 4 * tt * (1 - tt))
        x, y, z = projetar(cam, pts3)
        pl = list(zip(x.tolist(), y.tolist()))
        c = tuple(int(255 * v) for v in corf)
        dr.line(pl, fill=c, width=larg)
        if dg is not None:
            dg.line(pl, fill=c, width=larg + 2)
    if glow is not None:
        raio = max(2, int(min(W, H) / 90))
        b1 = np.asarray(glow.filter(ImageFilter.GaussianBlur(raio)), float)
        b2 = np.asarray(glow.filter(ImageFilter.GaussianBlur(raio * 4)), float)
        a = np.asarray(img, float) + bloom * (0.9 * b1 + 0.7 * b2)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img

def _grade(dr, cam, passo, chao_y):
    if cam['tipo'] != 'orto':
        return
    W, H, s = cam['W'], cam['H'], cam['s']
    cr, cu = cam['c'] @ cam['r'], cam['c'] @ cam['u']
    for eixo, centro, n, horiz in ((cam['r'], cr, W, False), (cam['u'], cu, H, True)):
        if np.abs(eixo).max() < 0.99:
            continue
        sgn = eixo[np.argmax(np.abs(eixo))]
        lo, hi = centro - n / (2 * s), centro + n / (2 * s)
        for k in range(int(math.floor(lo)), int(math.ceil(hi)) + 1):
            pix = n / 2 + s * (k - centro) if not horiz else n / 2 - s * (k - centro)
            mundo = k * sgn
            forte = abs(round(mundo)) % passo == 0
            cor = (178, 178, 178) if forte else (214, 214, 214)
            larg = 2 if forte else 1
            if horiz:
                dr.line([(0, pix), (W, pix)], fill=cor, width=larg)
            else:
                dr.line([(pix, 0), (pix, H)], fill=cor, width=larg)
    if chao_y is not None and abs(cam['u'][1]) > 0.99:
        pix = H / 2 - s * (chao_y - cu)
        dr.line([(0, pix), (W, pix)], fill=(70, 70, 70), width=3)

# ---------------- transformacoes ----------------
def rot_eixo(eixo, ang):
    k = _unit(eixo); x, y, z = k
    c, s = math.cos(ang), math.sin(ang); C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])

def em_torno(R, pivo, novo_pivo=None):
    """Transformacao que gira R em torno de pivo e o leva a novo_pivo."""
    pivo = np.asarray(pivo, float)
    novo = pivo if novo_pivo is None else np.asarray(novo_pivo, float)
    return R, novo - R @ pivo

def compor(A, B):
    """A apos B: x -> A(B(x))."""
    Ra, ta = A; Rb, tb = B
    return Ra @ Rb, Ra @ tb + ta

def aplicar(T, p):
    return T[0] @ np.asarray(p, float) + T[1]

def quadro(u, n):
    u = _unit(u); n = _unit(n - (n @ u) * u); w = np.cross(u, n)
    return np.stack([u, n, w], 1)

def segmento(P0, P1, N0, Q0, Q1, N1):
    """Transformacao rigida que leva o segmento P0->P1 (plano N0) a Q0->Q1 (plano N1)."""
    F0 = quadro(np.asarray(P1) - P0, N0); F1 = quadro(np.asarray(Q1) - Q0, N1)
    R = F1 @ F0.T
    return R, np.asarray(Q0, float) - R @ np.asarray(P0, float)

IDENT = (np.eye(3), np.zeros(3))

# ---------------- exportacao ----------------
def paleta_png(paleta_hex, lado=16):
    img = Image.new('RGB', (lado, lado), (255, 0, 255))
    px = img.load()
    for i, h in enumerate(paleta_hex):
        if i == 0:
            continue
        px[i % lado, i // lado] = tuple(int(h[k:k + 2], 16) for k in (0, 2, 4))
    b = io.BytesIO(); img.save(b, 'PNG')
    return b.getvalue()

def malha_da_peca(p, cores_filtro, lado=16):
    g = np.where(np.isin(p.g, list(cores_filtro)), p.g, 0).astype(np.uint8)
    quads = malha_gulosa(g)
    if not quads:
        return None
    pos, nor, uv, idx = [], [], [], []
    for (ax, sinal, k, u0, v0, du, dv, c) in quads:
        a1, a2 = [a for a in range(3) if a != ax]
        cs = []
        for (uu, vv) in ((u0, v0), (u0 + du, v0), (u0 + du, v0 + dv), (u0, v0 + dv)):
            q = np.zeros(3); q[ax] = k + 1 if False else k; q[a1] = uu; q[a2] = vv
            cs.append(p.origem + q * p.vs - p.pivo)
        n = np.zeros(3); n[ax] = sinal
        if np.cross(cs[1] - cs[0], cs[3] - cs[0]) @ n < 0:
            cs = [cs[0], cs[3], cs[2], cs[1]]
        b = len(pos)
        pos += cs; nor += [n] * 4
        uvc = ((c % lado + 0.5) / lado, (c // lado + 0.5) / lado)
        uv += [uvc] * 4
        idx += [b, b + 1, b + 2, b, b + 2, b + 3]
    return dict(pos=np.array(pos, np.float32), nor=np.array(nor, np.float32), uv=np.array(uv, np.float32), idx=np.array(idx, np.uint32))

def salvar_glb(caminho, nos, png, nome_raiz):
    """nos: lista de dict(nome, malha, translacao, material 0/1)."""
    bin_ = bytearray(); views = []; acc = []; meshes = []; nodes = []

    def add_view(data, target=None):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_); bin_.extend(data)
        v = dict(buffer=0, byteOffset=off, byteLength=len(data))
        if target:
            v['target'] = target
        views.append(v)
        return len(views) - 1

    for no in nos:
        m = no['malha']
        a_pos = len(acc)
        acc.append(dict(bufferView=add_view(m['pos'].tobytes(), 34962), componentType=5126, count=len(m['pos']), type='VEC3',
                        min=m['pos'].min(0).tolist(), max=m['pos'].max(0).tolist()))
        acc.append(dict(bufferView=add_view(m['nor'].tobytes(), 34962), componentType=5126, count=len(m['nor']), type='VEC3'))
        acc.append(dict(bufferView=add_view(m['uv'].tobytes(), 34962), componentType=5126, count=len(m['uv']), type='VEC2'))
        acc.append(dict(bufferView=add_view(m['idx'].tobytes(), 34963), componentType=5125, count=len(m['idx']), type='SCALAR'))
        meshes.append(dict(name=no['nome'], primitives=[dict(attributes=dict(POSITION=a_pos, NORMAL=a_pos + 1, TEXCOORD_0=a_pos + 2),
                                                             indices=a_pos + 3, material=no['material'])]))
        nodes.append(dict(name=no['nome'], mesh=len(meshes) - 1, translation=[float(x) for x in no['translacao']]))
    img_view = add_view(png)
    raiz = dict(name=nome_raiz, children=list(range(len(nodes))))
    nodes.append(raiz)
    gltf = dict(asset=dict(version='2.0', generator='forja-voxel'), scene=0, scenes=[dict(nodes=[len(nodes) - 1])], nodes=nodes,
                meshes=meshes, accessors=acc, bufferViews=views, buffers=[dict(byteLength=0)],
                images=[dict(bufferView=img_view, mimeType='image/png')],
                samplers=[dict(magFilter=9728, minFilter=9728, wrapS=33071, wrapT=33071)],
                textures=[dict(sampler=0, source=0)],
                materials=[dict(name='voxel', pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=0.0, roughnessFactor=1.0)),
                           dict(name='brilho', pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=0.0, roughnessFactor=1.0),
                                emissiveTexture=dict(index=0), emissiveFactor=[1.0, 1.0, 1.0])])
    while len(bin_) % 4:
        bin_.append(0)
    gltf['buffers'][0]['byteLength'] = len(bin_)
    js = json.dumps(gltf, separators=(',', ':')).encode()
    while len(js) % 4:
        js += b' '
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(caminho, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(bin_), 0x004E4942)); f.write(bytes(bin_))
    return total

def salvar_vox(caminho, grade, paleta_hex):
    """grade: array (x, y, z) com Y para cima. MagicaVoxel usa Z para cima."""
    xs, ys, zs = np.nonzero(grade)
    nx, ny, nz = grade.shape
    assert max(nx, ny, nz) <= 256, grade.shape
    def chunk(cid, conteudo, filhos=b''):
        return cid + struct.pack('<ii', len(conteudo), len(filhos)) + conteudo + filhos
    size = chunk(b'SIZE', struct.pack('<iii', nx, nz, ny))
    dados = struct.pack('<i', len(xs)) + b''.join(struct.pack('<BBBB', x, nz - 1 - z, y, grade[x, y, z]) for x, y, z in zip(xs, ys, zs))
    xyzi = chunk(b'XYZI', dados)
    rgba = b''
    for i in range(1, 257):
        h = paleta_hex[i] if i < len(paleta_hex) else '000000'
        rgba += bytes([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255])
    pal = chunk(b'RGBA', rgba)
    main = chunk(b'MAIN', b'', size + xyzi + pal)
    with open(caminho, 'wb') as f:
        f.write(b'VOX ' + struct.pack('<i', 150) + main)
