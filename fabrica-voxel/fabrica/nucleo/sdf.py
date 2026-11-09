"""Primitivas de distancia com sinal avaliadas em grade, e combinacoes.

Unidade: VOXEL. O centro do voxel (i, j, k) de uma grade que comeca em `origem` fica em
origem + (i + .5, j + .5, k + .5). Um voxel e OCUPADO quando a distancia no centro e < 0 (`ocupado`).

Como usar:
    P = eixos((nx, ny, nz), origem=(0, 0, 0))      # coordenadas dos centros, prontas para broadcast
    d = caixa(P, centro=(6, 6, 6), tam=(12, 12, 12), raio=3)
    d = uniao_suave(d, elipsoide(P, (6, 13, 6), (8, 4, 8)), k=2)
    cheio = ocupado(d)

Regras de voxel que as primitivas respeitam:
  - `tam` e a caixa-limite [X, Y, Z] em voxels; com `centro` na metade exata, uma caixa de tam inteiro
    ocupa exatamente tam voxels (centro em borda de voxel se o tamanho e par, em centro de voxel se impar).
  - Formas que afinam (cone, cunha) sao medidas no centro de cada camada e a ponta nunca some: sobra
    1 voxel (tamanho impar) ou 2 (tamanho par). Assim a forma ocupa o `tam` todo.
  - O elipsoide tem uma folga pequena (ate 0.25 voxel) para que os extremos de elipsoides finos existam.
  - Forma menor que 1 voxel some.

Faces e arte em texto (perfil_extrusao, e a estampa da linguagem de forma) usam `FACES`: a arte e lida
como um observador olhando para aquela face, de cima para baixo e da esquerda para a direita.
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

# Para cada face: n = (eixo, sinal) da normal para fora; u = eixo/sinal do sentido de leitura (esquerda ->
# direita do texto); v = eixo/sinal de baixo -> cima do texto. Frente = -Z; +X = direita da criatura.
FACES: dict[str, dict[str, tuple[int, int]]] = {
    "frente": {"n": (2, -1), "u": (0, -1), "v": (1, +1)},
    "tras": {"n": (2, +1), "u": (0, +1), "v": (1, +1)},
    "dir": {"n": (0, +1), "u": (2, -1), "v": (1, +1)},
    "esq": {"n": (0, -1), "u": (2, +1), "v": (1, +1)},
    "topo": {"n": (1, +1), "u": (0, -1), "v": (2, +1)},
    "base": {"n": (1, -1), "u": (0, -1), "v": (2, -1)},
}
_EIXOS = {"x": 0, "y": 1, "z": 2}


def _eixo(eixo) -> int:
    if eixo in (0, 1, 2):
        return int(eixo)
    if isinstance(eixo, str) and eixo.lower() in _EIXOS:
        return _EIXOS[eixo.lower()]
    raise ValueError(f'eixo={eixo!r} nao existe; use "x" (direita), "y" (cima) ou "z" (tras), ex.: "eixo": "y"')


def eixos(forma: Sequence[int], origem: Sequence[float] = (0, 0, 0)) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Coordenadas dos centros dos voxels de uma grade [nx, ny, nz], em arrays prontos para broadcast."""
    nx, ny, nz = (int(n) for n in forma)
    ox, oy, oz = (float(o) for o in origem)
    x = (ox + np.arange(nx, dtype=np.float32) + 0.5).reshape(nx, 1, 1)
    y = (oy + np.arange(ny, dtype=np.float32) + 0.5).reshape(1, ny, 1)
    z = (oz + np.arange(nz, dtype=np.float32) + 0.5).reshape(1, 1, nz)
    return x, y, z


def ocupado(d: np.ndarray) -> np.ndarray:
    """Regra de ocupacao: distancia no centro do voxel < 0."""
    return np.asarray(d) < 0


def _cheio(P, valor: float = 0.0) -> np.ndarray:
    x, y, z = P
    return np.full(np.broadcast_shapes(x.shape, y.shape, z.shape), valor, dtype=np.float32)


# --------------------------------------------------------------------------- primitivas

def caixa(P, centro, tam, raio: float = 0.0, chanfro: float = 0.0, arredondar: str = "tudo") -> np.ndarray:
    """Caixa de tamanho `tam` centrada em `centro`.

    raio: arredonda os cantos (em voxels; raio 2 ou 3 tira 1 voxel do canto, raio 4 faz a escada 2-1).
    chanfro: corta as arestas a 45 graus (chanfro 1 tira 1 voxel da aresta, 2 tira a escada 2-1).
    arredondar: "tudo" (as 12 arestas) ou "x" | "y" | "z" = so as arestas PARALELAS a esse eixo
    (ex.: "z" arredonda o contorno visto de frente e deixa frente e costas planas: lapide, escudo).
    """
    x, y, z = P
    c = np.asarray(centro, dtype=np.float32)
    h = np.asarray(tam, dtype=np.float32) / 2.0
    q = [np.abs(x - c[0]) - h[0], np.abs(y - c[1]) - h[1], np.abs(z - c[2]) - h[2]]
    if arredondar == "tudo":
        pares = [(0, 1), (0, 2), (1, 2)]
        redondos = (0, 1, 2)
    elif arredondar in ("x", "y", "z"):
        e = _EIXOS[arredondar]
        redondos = tuple(i for i in range(3) if i != e)
        pares = [redondos]
    else:
        raise ValueError(f'arredondar={arredondar!r} nao existe; use "tudo", "x", "y" ou "z", ex.: "arredondar": "z"')
    r = float(min(max(raio, 0.0), min(float(h[i]) for i in redondos)))
    if r > 0:
        qq = [q[i] + r if i in redondos else None for i in range(3)]
        fora2 = sum(np.maximum(qq[i], 0.0) ** 2 for i in redondos)
        dentro = qq[redondos[0]]
        for i in redondos[1:]:
            dentro = np.maximum(dentro, qq[i])
        d = np.sqrt(fora2) + np.minimum(dentro, 0.0) - r
        for i in range(3):
            if i not in redondos:
                d = np.maximum(d, q[i])
    else:
        d = np.maximum(np.maximum(q[0], q[1]), q[2])
    if chanfro > 0:
        for a, b in pares:
            d = np.maximum(d, (q[a] + q[b] + float(chanfro)) / np.sqrt(2.0))
    return (d + _cheio(P)).astype(np.float32)


def elipsoide(P, centro, tam) -> np.ndarray:
    """Elipsoide inscrito na caixa `tam` (distancia aproximada, sinal exato)."""
    x, y, z = P
    c = np.asarray(centro, dtype=np.float32)
    r = np.maximum(np.asarray(tam, dtype=np.float32) / 2.0, 0.25)
    r = r + 0.25 * np.minimum(1.0, 2.0 / r)          # folga: extremos de elipsoide fino nao somem
    px, py, pz = (x - c[0]), (y - c[1]), (z - c[2])
    k0 = np.sqrt((px / r[0]) ** 2 + (py / r[1]) ** 2 + (pz / r[2]) ** 2)
    k1 = np.sqrt((px / r[0] ** 2) ** 2 + (py / r[1] ** 2) ** 2 + (pz / r[2] ** 2) ** 2)
    d = np.where(k1 > 1e-6, k0 * (k0 - 1.0) / np.maximum(k1, 1e-6), -float(r.min()))
    return d.astype(np.float32)


def capsula(P, a, b, r0: float, r1: Optional[float] = None) -> np.ndarray:
    """Capsula do ponto `a` ao ponto `b`, com raio r0 em `a` afinando (ou engrossando) ate r1 em `b`.

    Capsula fina (raio < 1) na diagonal pode sair desconexa pela regra do centro: junte `linha_voxels(a, b)`.
    """
    x, y, z = P
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    r1 = r0 if r1 is None else r1
    ab = b - a
    comp2 = float(ab @ ab)
    px, py, pz = x - a[0], y - a[1], z - a[2]
    if comp2 < 1e-9:
        return (np.sqrt(px * px + py * py + pz * pz) - max(r0, r1)).astype(np.float32)
    t = np.clip((px * ab[0] + py * ab[1] + pz * ab[2]) / comp2, 0.0, 1.0)
    dx, dy, dz = px - ab[0] * t, py - ab[1] * t, pz - ab[2] * t
    return (np.sqrt(dx * dx + dy * dy + dz * dz) - (r0 + (r1 - r0) * t)).astype(np.float32)


def _k_minimo(tam_a: float, tam_b: float) -> float:
    """Menor raio normalizado que ainda pega o(s) voxel(s) central(is): 0 se a secao e impar x impar."""
    ka = 0.0 if int(round(tam_a)) % 2 else 0.5 / max(tam_a / 2.0, 0.25)
    kb = 0.0 if int(round(tam_b)) % 2 else 0.5 / max(tam_b / 2.0, 0.25)
    return float(np.hypot(ka, kb)) + 1e-3


def cilindro(P, centro, tam, eixo="y") -> np.ndarray:
    """Cilindro (secao eliptica) inscrito na caixa `tam`, com o eixo ao longo de `eixo`."""
    e = _eixo(eixo)
    a, b = [i for i in range(3) if i != e]
    c = np.asarray(centro, dtype=np.float32)
    h = np.maximum(np.asarray(tam, dtype=np.float32) / 2.0, 0.25)
    k = np.sqrt(((P[a] - c[a]) / h[a]) ** 2 + ((P[b] - c[b]) / h[b]) ** 2)
    lim = max(1.0, _k_minimo(tam[a], tam[b]))
    d_rad = (k - lim) * float(min(h[a], h[b]))
    d_ax = np.abs(P[e] - c[e]) - h[e]
    return np.maximum(d_rad, d_ax).astype(np.float32)


def cone(P, centro, tam, eixo="y", sentido: int = 1, raio_ponta: float = 0.0) -> np.ndarray:
    """Cone inscrito na caixa `tam`: base cheia no lado -sentido do eixo, ponta no lado +sentido.

    raio_ponta (voxels) > 0 faz um tronco de cone. A ponta sempre sobra com 1 voxel (secao impar) ou 2x2 (par).
    """
    e = _eixo(eixo)
    a, b = [i for i in range(3) if i != e]
    c = np.asarray(centro, dtype=np.float32)
    h = np.maximum(np.asarray(tam, dtype=np.float32) / 2.0, 0.25)
    comp = float(tam[e])
    s = 1 if sentido >= 0 else -1
    u = (P[e] - (c[e] - s * h[e])) * s                    # 0 na base, comp na ponta
    camada = np.clip(np.floor(u), 0, max(comp - 1, 0))
    frac_ponta = float(np.clip(raio_ponta / float(min(h[a], h[b])), 0.0, 1.0))
    escala = 1.0 - ((camada + 0.5) / max(comp, 1e-6)) * (1.0 - frac_ponta) + 1e-4   # raio no centro da camada
    escala = np.maximum(escala, _k_minimo(tam[a], tam[b]))                          # a ponta nunca some
    k = np.sqrt(((P[a] - c[a]) / h[a]) ** 2 + ((P[b] - c[b]) / h[b]) ** 2)
    d_rad = (k - escala) * float(min(h[a], h[b]))
    d_ax = np.abs(P[e] - c[e]) - h[e]
    return np.maximum(d_rad, d_ax).astype(np.float32)


def toro(P, centro, tam, eixo="y", tubo: Optional[float] = None) -> np.ndarray:
    """Toro (rosquinha) inscrito na caixa `tam`, furo ao longo de `eixo`. tubo = raio do tubo em voxels
    (padrao: metade do tamanho ao longo do eixo)."""
    e = _eixo(eixo)
    a, b = [i for i in range(3) if i != e]
    c = np.asarray(centro, dtype=np.float32)
    h = np.asarray(tam, dtype=np.float32) / 2.0
    r = float(h[e] if tubo is None else tubo)
    ra = max(float(h[a]) - r, 0.25)
    rb = max(float(h[b]) - r, 0.25)
    k = np.sqrt(((P[a] - c[a]) / ra) ** 2 + ((P[b] - c[b]) / rb) ** 2)
    d_plano = (k - 1.0) * min(ra, rb)
    d_eixo = P[e] - c[e]
    return (np.sqrt(d_plano ** 2 + d_eixo ** 2) - r).astype(np.float32)


def cunha(P, centro, tam, eixo_ponta="z", sentido: int = -1, eixo_altura="y", simetrica: bool = False) -> np.ndarray:
    """Cunha (prisma triangular) inscrita na caixa `tam`.

    Normal (simetrica=False): rampa. A altura (ao longo de eixo_altura, apoiada no lado de baixo/minimo)
    e cheia no lado -sentido de eixo_ponta e cai ate 1 voxel no lado +sentido.
    simetrica=True: telhado. `eixo_ponta`/`sentido` dizem para onde a cumeeira aponta (ex.: "y", +1 = para
    cima) e `eixo_altura` e o eixo que ESTREITA dos dois lados ate a cumeeira.
    """
    ep = _eixo(eixo_ponta)
    ea = _eixo(eixo_altura)
    if ep == ea:
        raise ValueError('cunha: eixo_ponta e eixo_altura nao podem ser o mesmo eixo; ex.: eixo_ponta="z", eixo_altura="y"')
    c = np.asarray(centro, dtype=np.float32)
    h = np.asarray(tam, dtype=np.float32) / 2.0
    s = 1 if sentido >= 0 else -1
    comp = float(tam[ep])
    alt = float(tam[ea])
    q = [np.abs(P[i] - c[i]) - h[i] for i in range(3)]
    d = np.maximum(np.maximum(q[0], q[1]), q[2])
    u = (P[ep] - (c[ep] - s * h[ep])) * s                 # 0 no lado grosso, comp na ponta
    col = np.clip(np.floor(u), 0, max(comp - 1, 0))
    fator = 1.0 - (col + 0.5) / max(comp, 1e-6)           # medido no centro da coluna
    cos = comp / float(np.hypot(comp, alt))
    if simetrica:
        minimo = 0.25 if int(round(alt)) % 2 else 0.5
        meia = np.maximum((alt / 2.0) * fator, minimo) + 1e-4
        d_rampa = (np.abs(P[ea] - c[ea]) - meia) * cos
    else:
        altura = np.maximum(alt * fator, 0.5) + 1e-4       # a ponta fica com 1 voxel
        d_rampa = ((P[ea] - (c[ea] - h[ea])) - altura) * cos
    return (np.maximum(d, d_rampa) + _cheio(P)).astype(np.float32)


def raios_da_arte(linhas: Sequence[str], vazio: str = ". ") -> list[float]:
    """Arte em texto de um perfil de revolucao -> raios por camada, de BAIXO para CIMA.
    Cada linha (lida de cima para baixo) vale metade da largura entre o primeiro e o ultimo caractere cheio."""
    raios: list[float] = []
    for linha in reversed(list(linhas)):
        cheios = [i for i, ch in enumerate(linha) if ch not in vazio]
        raios.append((cheios[-1] - cheios[0] + 1) / 2.0 if cheios else 0.0)
    return raios


def perfil_revolucao(P, centro_base, raios: Sequence[float], eixo="y") -> np.ndarray:
    """Solido de revolucao: `raios[j]` e o raio (em voxels; x.5 da diametro impar) da camada j,
    contada a partir de `centro_base` no sentido + do eixo. Aceita tambem a arte em texto (lista de str)."""
    if len(raios) and isinstance(raios[0], str):
        raios = raios_da_arte(raios)  # type: ignore[arg-type]
    e = _eixo(eixo)
    a, b = [i for i in range(3) if i != e]
    c = np.asarray(centro_base, dtype=np.float32)
    rr = np.asarray(list(raios), dtype=np.float32)
    n = len(rr)
    if n == 0:
        raise ValueError('perfil_revolucao: "raios" esta vazio; passe um raio por camada, ex.: "raios": [3, 3, 2.5, 1.5]')
    u = P[e] - c[e]
    camada = np.clip(np.floor(u), 0, n - 1).astype(np.int64)
    raio = rr[camada]
    dist = np.sqrt((P[a] - c[a]) ** 2 + (P[b] - c[b]) ** 2)
    d_rad = dist - raio
    d_ax = np.abs(u - n / 2.0) - n / 2.0
    return np.maximum(d_rad, d_ax + _cheio(P)).astype(np.float32)


def ler_arte(linhas: Sequence[str], nome: str = "linhas") -> np.ndarray:
    """Valida a arte em texto e devolve array de caracteres [n_linhas, n_colunas] (linha 0 = a de cima)."""
    if not isinstance(linhas, (list, tuple)) or not linhas or not all(isinstance(l, str) for l in linhas):
        raise ValueError(f'"{nome}" precisa ser uma lista de textos, uma linha por texto, de cima para baixo, '
                         f'ex.: "{nome}": ["#..#", "####"]')
    larg = max(len(l) for l in linhas)
    if larg == 0:
        raise ValueError(f'"{nome}" tem linhas vazias; cada linha precisa de ao menos 1 caractere, ex.: ["##", "##"]')
    curtas = [i for i, l in enumerate(linhas) if len(l) != larg]
    if curtas:
        raise ValueError(f'"{nome}": todas as linhas precisam ter a mesma largura ({larg}); as linhas {curtas} sao '
                         f'mais curtas. Complete com "." (ponto = nao mexe), ex.: "{linhas[curtas[0]].ljust(larg, ".")}"')
    return np.array([list(l) for l in linhas], dtype="<U1")


def bloco_da_arte(linhas: Sequence[str], profundidade: int = 1, face: str = "frente") -> np.ndarray:
    """Arte em texto -> bloco 3D de caracteres ('<U1' [nx, ny, nz]), com a arte lida olhando para `face`
    e repetida `profundidade` voxels ao longo da normal. '.' e ' ' ficam como '.' (vazio)."""
    if face not in FACES:
        raise ValueError(f'face={face!r} nao existe; use uma de {sorted(FACES)}, ex.: "face": "frente"')
    arte = ler_arte(linhas)
    arte = np.where(arte == " ", ".", arte)
    f = FACES[face]
    (eu, su), (ev, sv), (en, _) = f["u"], f["v"], f["n"]
    uv = arte.T                                   # [coluna, linha]
    if su < 0:
        uv = uv[::-1, :]                          # coluna 0 do texto vai para o lado + do eixo u
    if sv > 0:
        uv = uv[:, ::-1]                          # linha 0 do texto (a de cima) vai para o lado + do eixo v
    prof = max(1, int(profundidade))
    bloco = np.repeat(uv[:, :, None], prof, axis=2)       # eixos (u, v, n)
    ordem = [0, 0, 0]
    ordem[eu], ordem[ev], ordem[en] = 0, 1, 2
    return np.ascontiguousarray(np.transpose(bloco, ordem))


def perfil_extrusao(P, canto_min, linhas: Sequence[str], profundidade: int = 1, face: str = "frente") -> np.ndarray:
    """Arte em texto extrudada. `canto_min` e o canto minimo (voxels) do bloco. Devolve -0.5 dentro e +0.5 fora
    (pseudo-distancia: serve para ocupacao, uniao, corte e intersecao; para uniao_suave use a distancia
    de `util_grade.distancia_com_sinal` sobre a ocupacao)."""
    bloco = bloco_da_arte(linhas, profundidade, face) != "."
    o = np.asarray(canto_min, dtype=np.float64)
    idx = [np.floor(P[i] - o[i]).astype(np.int64) for i in range(3)]
    dentro = np.ones(np.broadcast_shapes(*(a.shape for a in idx)), dtype=bool)
    for i in range(3):
        dentro = dentro & (idx[i] >= 0) & (idx[i] < bloco.shape[i])
    ix, iy, iz = (np.clip(idx[i], 0, bloco.shape[i] - 1) for i in range(3))
    cheio = bloco[ix, iy, iz] & dentro
    return np.where(cheio, np.float32(-0.5), np.float32(0.5))


def linha_voxels(a, b) -> np.ndarray:
    """Linha de voxels conexa por FACE do ponto a ao ponto b (coordenadas em voxels). int64 [n, 3]."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    n = int(np.ceil(np.abs(b - a).max() * 4)) + 1
    t = np.linspace(0.0, 1.0, max(n, 2))[:, None]
    pts = np.floor(a + (b - a) * t + 1e-9).astype(np.int64)
    ordem = np.argsort(-np.abs(b - a), kind="stable")
    saida = [pts[0].copy()]
    for p in pts[1:]:
        q = saida[-1].copy()
        for e in ordem:
            while q[e] != p[e]:
                q[e] += 1 if p[e] > q[e] else -1
                saida.append(q.copy())
    return np.array(saida, dtype=np.int64)


# --------------------------------------------------------------------------- combinacoes

def uniao(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.minimum(a, b)


def uniao_suave(a: np.ndarray, b: np.ndarray, k: float = 2.0) -> np.ndarray:
    """Uniao com filete (smin polinomial). k = largura do filete em voxels; k <= 0 vira uniao comum."""
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return (b + (a - b) * h - k * h * (1.0 - h)).astype(np.float32)


def corte(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """a menos b."""
    return np.maximum(a, -b)


def intersecao(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.maximum(a, b)
