"""Rasterizador ortografico por software (numpy + PIL): vistas, folha de conferencia, tiras e GIF.

Desenha so faces expostas, do fundo para a frente (pintor). Sombreamento chapado por face, por cima da cor
pintada, parecido com o que o Roblox faz com a luz de cima.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from . import util_grade as ug
from .contrato import Clipe, Modelo, matrizes_do_quadro
from .paleta import hex_para_rgb

FUNDO = (46, 40, 54)
# (guinada, inclinacao) em graus. guinada 0 = camera na frente da criatura olhando para +Z.
VISTAS = {"frente": (0, 0), "costas": (180, 0), "lado_d": (90, 0), "lado_e": (-90, 0), "topo": (0, 89.9),
          "tres_quartos": (32, 22), "tres_quartos_costas": (148, 22), "grade": (35, 55)}
_NORMAIS = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)], float)
_LUZ_FACE = np.array([0.80, 0.66, 1.0, 0.5, 0.6, 0.88])  # dir, esq, topo, base, tras, frente
# cantos de cada face (em unidades de voxel a partir do canto minimo)
_CANTOS = np.array([
    [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
    [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)], [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]], float)


def _camera(guinada, inclinacao):
    """Matriz 3x3 mundo -> (direita da tela, cima da tela, profundidade para longe)."""
    g, p = np.radians(guinada), np.radians(inclinacao)
    olho = np.array([np.sin(g) * np.cos(p), np.sin(p), -np.cos(g) * np.cos(p)])  # posicao da camera (direcao)
    longe = -olho
    dire = np.cross([0, 1, 0], longe)
    dire = dire / np.linalg.norm(dire)
    cima = np.cross(longe, dire)
    return np.stack([dire, cima, longe])


def _faces(modelo: Modelo, matrizes=None):
    """Junta todas as faces expostas: cantos [n,4,3] em studs, cor idx [n], indice de face [n], normal no mundo."""
    cs, cores, luzes, nrms = [], [], [], []
    for peca in modelo.pecas:
        g = peca.grade
        oc = g.mat > 0
        fe = ug.faces_expostas(oc)
        M = None if matrizes is None else matrizes.get(peca.osso)
        for f in range(6):
            idx = np.argwhere(fe[f])
            if len(idx) == 0:
                continue
            pts = g.origem + (idx[:, None, :] + _CANTOS[f][None]) * g.v
            n = _NORMAIS[f]
            if M is not None:
                pts = pts @ M[:3, :3].T + M[:3, 3]
                n = M[:3, :3] @ n
                n = n / max(np.linalg.norm(n), 1e-9)
            cs.append(pts)
            cores.append(g.cor[fe[f]] if g.cor is not None else g.mat[fe[f]])
            # luz por face a partir da normal no mundo (interpola as 6 direcoes)
            l = 0.62 + 0.38 * max(n[1], 0) - 0.14 * max(-n[1], 0) + 0.16 * max(-n[2], 0) * (1 - abs(n[1])) \
                + 0.06 * max(n[0], 0) - 0.06 * max(n[2], 0)
            luzes.append(np.full(len(idx), l))
            nrms.append(np.tile(n, (len(idx), 1)))
    if not cs:
        return np.zeros((0, 4, 3)), np.zeros(0, int), np.zeros(0), np.zeros((0, 3))
    return np.concatenate(cs), np.concatenate(cores), np.concatenate(luzes), np.concatenate(nrms)


def render_modelo(modelo: Modelo, *, vista="tres_quartos", px_por_stud=48.0, matrizes=None, modo="cor",
                  fundo=FUNDO, tamanho=None, centro=None, extras: list[Modelo] | None = None) -> Image.Image:
    """Renderiza o modelo. modo: cor, cinza, silhueta, valor. `tamanho` (w, h) fixa a tela; `centro` (studs)
    fixa o ponto central (use nos quadros de animacao para a camera nao tremer)."""
    g, p = VISTAS[vista] if isinstance(vista, str) else vista
    C = _camera(g, p)
    pts, cor, luz, nrm = _faces(modelo, matrizes)
    if len(pts) == 0:
        return Image.new("RGB", tamanho or (8, 8), fundo)
    vis = (nrm @ C[2]) < -1e-6           # so faces voltadas para a camera
    pts, cor, luz = pts[vis], cor[vis], luz[vis]
    tela = pts @ C.T                      # [n,4,3]: x, y, profundidade
    if centro is None:
        mn, mx = tela[..., :2].reshape(-1, 2).min(0), tela[..., :2].reshape(-1, 2).max(0)
        c2 = (mn + mx) / 2
        if tamanho is None:
            tamanho = tuple(int(np.ceil((mx - mn)[i] * px_por_stud)) + 16 for i in (0, 1))
    else:
        c2 = (np.asarray(centro, float) @ C.T)[:2]
    w, h = tamanho
    xy = (tela[..., :2] - c2) * px_por_stud
    xy[..., 0] += w / 2
    xy[..., 1] = h / 2 - xy[..., 1]
    ordem = np.argsort(-tela[..., 2].mean(1))
    tab = np.array([(0, 0, 0)] + [hex_para_rgb(c) for c in modelo.cores], float)
    eb = np.zeros(len(tab), bool)
    for i in modelo.cores_brilho:
        eb[i] = True
    rgb = tab[cor]
    if modo == "silhueta":
        rgb = np.full_like(rgb, 16.0)
    else:
        f = np.where(eb[cor], 1.0, luz)[:, None]
        rgb = rgb * f
        if modo in ("cinza", "valor"):
            L = (rgb @ [0.2126, 0.7152, 0.0722])[:, None]
            if modo == "valor":
                L = np.where(L < 80, 50, np.where(L < 150, 125, 215))
            rgb = np.repeat(L, 3, 1)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    img = Image.new("RGB", (w, h), (235, 232, 226) if modo == "silhueta" else fundo)
    d = ImageDraw.Draw(img)
    for i in ordem:
        d.polygon([tuple(q) for q in xy[i]], fill=tuple(int(v) for v in rgb[i]))
    return img


def _rotulo(img: Image.Image, texto: str) -> Image.Image:
    d = ImageDraw.Draw(img)
    d.text((5, 3), texto, fill=(200, 192, 210))
    return img


def folha_conferencia(modelo: Modelo, caminho, *, titulo=None, metricas: dict | None = None) -> Image.Image:
    """Folha: 3/4 frente e costas, 4 vistas ortograficas, topo, cinza, silhueta e tamanho real na camera da grade."""
    mn, mx = modelo.caixa()
    maior = max(mx - mn)
    esc = float(np.clip(300 / max(maior, 0.5), 14, 140))
    grandes = [_rotulo(render_modelo(modelo, vista=v, px_por_stud=esc), v.replace("_", " ")) for v in ("tres_quartos", "tres_quartos_costas")]
    orto = [_rotulo(render_modelo(modelo, vista=v, px_por_stud=esc * 0.62), v.replace("_", " ")) for v in ("frente", "lado_d", "costas", "topo")]
    extra = [_rotulo(render_modelo(modelo, vista="tres_quartos", px_por_stud=esc * 0.62, modo="cinza"), "cinza"),
             _rotulo(render_modelo(modelo, vista="frente", px_por_stud=esc * 0.62, modo="silhueta"), ""),
             _rotulo(render_modelo(modelo, vista="tres_quartos", px_por_stud=esc * 0.62, modo="valor"), "valor em 3 faixas")]
    # tamanho real: 3 px por voxel de 0,125 = 24 px por stud, na camera do jogo; 1x e 4x
    real = render_modelo(modelo, vista="grade", px_por_stud=24)
    real4 = real.resize((real.width * 4, real.height * 4), Image.NEAREST)
    linhas = [grandes, orto, extra + [_rotulo(real, "jogo 1x"), _rotulo(real4, "jogo 4x")]]
    larg = max(sum(i.width for i in l) + 12 * (len(l) + 1) for l in linhas)
    alt = sum(max(i.height for i in l) for l in linhas) + 12 * (len(linhas) + 1) + 54
    folha = Image.new("RGB", (larg, alt), (30, 26, 36))
    d = ImageDraw.Draw(folha)
    d.text((12, 8), titulo or f"{modelo.nome}  ({modelo.id})", fill=(236, 228, 243))
    n_tri = modelo.meta.get("triangulos", "?")
    info = f"{modelo.n_voxels()} voxels  {len(modelo.pecas)} pecas  {len(modelo.cores)} cores  {n_tri} tri  " \
           f"{'x'.join(f'{v:.2f}' for v in (mx - mn))} studs"
    if metricas:
        info += "   " + "  ".join(f"{k} {v}" for k, v in metricas.items())
    d.text((12, 24), info, fill=(169, 156, 184))
    x0 = 12
    for i, hx in enumerate(modelo.cores[:64]):
        d.rectangle([x0 + i * 13, 40, x0 + i * 13 + 11, 50], fill=hex_para_rgb(hx))
    y = 60
    for l in linhas:
        x = 12
        hmax = max(i.height for i in l)
        for im in l:
            folha.paste(im, (x, y + (hmax - im.height) // 2))
            x += im.width + 12
        y += hmax + 12
    folha.save(caminho)
    return folha


def _enquadrar(modelo, clipe, vista, px):
    """Caixa de tela que cabe todos os quadros do clipe (para a camera nao tremer)."""
    g, p = VISTAS[vista]
    C = _camera(g, p)
    mn, mx = np.full(2, 1e9), np.full(2, -1e9)
    for q in range(0, clipe.n_quadros, max(1, clipe.n_quadros // 12)):
        M = matrizes_do_quadro(modelo, clipe, q)
        for peca in modelo.pecas:
            a, b = peca.grade.caixa()
            cant = np.array([[x, y, z] for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])])
            m = M.get(peca.osso)
            if m is not None:
                cant = cant @ m[:3, :3].T + m[:3, 3]
            t = (cant @ C.T)[:, :2]
            mn, mx = np.minimum(mn, t.min(0)), np.maximum(mx, t.max(0))
    c2 = (mn + mx) / 2
    centro = C.T[:, 0] * c2[0] + C.T[:, 1] * c2[1]
    return centro, (int((mx - mn)[0] * px) + 20, int((mx - mn)[1] * px) + 20)


def quadros_animacao(modelo: Modelo, clipe: Clipe, *, vista="tres_quartos", px_por_stud=40.0, passo=1):
    centro, tam = _enquadrar(modelo, clipe, vista, px_por_stud)
    return [render_modelo(modelo, vista=vista, px_por_stud=px_por_stud, tamanho=tam, centro=centro,
                          matrizes=matrizes_do_quadro(modelo, clipe, q))
            for q in range(0, clipe.n_quadros, passo)]


def tira_animacao(modelo: Modelo, clipe: Clipe, caminho, *, n=8, vista="tres_quartos", px_por_stud=40.0):
    passo = max(1, clipe.n_quadros // n)
    qs = quadros_animacao(modelo, clipe, vista=vista, px_por_stud=px_por_stud, passo=passo)[:n]
    tira = Image.new("RGB", (sum(q.width for q in qs), qs[0].height + 14), (30, 26, 36))
    x = 0
    for q in qs:
        tira.paste(q, (x, 14))
        x += q.width
    ImageDraw.Draw(tira).text((4, 1), f"{modelo.id} / {clipe.nome}  {clipe.duracao:.2f}s", fill=(220, 210, 230))
    tira.save(caminho)
    return tira


def gif_animacao(modelo: Modelo, clipes: list[Clipe], caminho, *, vista="tres_quartos", px_por_stud=40.0, passo=2):
    """GIF com os clipes em sequencia (15 fps com passo=2)."""
    quadros = []
    for c in clipes:
        quadros += quadros_animacao(modelo, c, vista=vista, px_por_stud=px_por_stud, passo=passo)
    w, h = max(q.width for q in quadros), max(q.height for q in quadros)
    norm = []
    for q in quadros:
        t = Image.new("RGB", (w, h), FUNDO)
        t.paste(q, ((w - q.width) // 2, h - q.height))
        norm.append(t.quantize(96, dither=Image.Dither.NONE))
    norm[0].save(caminho, save_all=True, append_images=norm[1:], duration=int(1000 * passo / 30), loop=0)
    return caminho


def icone_pixel(modelo: Modelo, tamanho=64, *, vista="tres_quartos") -> Image.Image:
    """Icone em pixel art renderizado do proprio voxel: sem antialiasing, cores do modelo, contorno de 1 px."""
    mn, mx = modelo.caixa()
    px = (tamanho - 6) / max(max(mx - mn) * 1.25, 0.2)
    img = render_modelo(modelo, vista=vista, px_por_stud=px, fundo=(255, 0, 255))
    a = np.array(img)
    solido = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
    ys, xs = np.nonzero(solido)
    if len(ys) == 0:
        return Image.new("RGBA", (tamanho, tamanho))
    a, solido = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], solido[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((tamanho, tamanho, 4), np.uint8)
    oy, ox = (tamanho - a.shape[0]) // 2, (tamanho - a.shape[1]) // 2
    a, solido = a[:tamanho - 2, :tamanho - 2], solido[:tamanho - 2, :tamanho - 2]
    oy, ox = max(oy, 1), max(ox, 1)
    out[oy:oy + a.shape[0], ox:ox + a.shape[1], :3] = a
    out[oy:oy + a.shape[0], ox:ox + a.shape[1], 3] = solido * 255
    alfa = out[..., 3] > 0
    borda = np.zeros_like(alfa)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        borda |= np.roll(alfa, (dy, dx), (0, 1))
    borda &= ~alfa
    escuro = (np.array(hex_para_rgb(min(modelo.cores, key=lambda c: sum(hex_para_rgb(c))))) * 0.6).astype(np.uint8)
    out[borda, :3] = escuro
    out[borda, 3] = 255
    return Image.fromarray(out, "RGBA")
