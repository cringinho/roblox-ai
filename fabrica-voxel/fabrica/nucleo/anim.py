"""Animacao: assa clipes a 30 fps a partir de RECEITAS declarativas por camadas.

Angulos sempre semanticos, em graus: frente (topo vai para a frente), esquerda (vira para o lado _E),
tombar_direita (topo vai para a direita). Translacoes em FRACOES DE H (altura do modelo), entao o mesmo
clipe serve em qualquer tamanho. Tudo e soma de camadas; nada de quaternion na ficha.

Camadas: onda, poses, passos, seguir, tremor, golpe. Ver docs/ARQUITETURA.md, secao 7 e cartoes/animacao.md.
"""
from __future__ import annotations

import fnmatch

import numpy as np

from .contrato import FPS, Clipe, Modelo, matriz_para_quat, quat_conj, quat_mul, quat_para_matriz, quat_semantico

CANAIS_ROT = ("frente", "esquerda", "tombar_direita")
CANAIS_TRANS = {"direita": (0, 1), "esquerda_t": (0, -1), "cima": (1, 1), "baixo": (1, -1),
                "frente_t": (2, -1), "tras": (2, 1)}
CURVAS = ("linear", "suave", "entra", "sai", "entra_sai", "passa_e_volta", "degrau", "golpe")
TIPOS = ("onda", "poses", "passos", "seguir", "tremor", "golpe")


def curva(nome: str, t):
    """Curvas de suavizacao em [0,1]. 'suave' e o minimo jerk (10t3 - 15t4 + 6t5)."""
    t = np.clip(t, 0.0, 1.0)
    if nome == "linear":
        return t
    if nome in ("suave", "entra_sai"):
        return t * t * t * (t * (t * 6 - 15) + 10)
    if nome == "entra":
        return t ** 3
    if nome == "golpe":
        return t ** 4
    if nome == "sai":
        return 1 - (1 - t) ** 3
    if nome == "passa_e_volta":           # ultrapassa ~10% e assenta
        s = 1.70158
        u = t - 1
        return u * u * ((s + 1) * u + s) + 1
    if nome == "degrau":
        return (t >= 1.0).astype(float) if hasattr(t, "astype") else float(t >= 1.0)
    raise ValueError(f'curva "{nome}" nao existe; use uma de {list(CURVAS)}')


class _Acum:
    """Acumulador de um clipe: angulos semanticos [n, nb, 3], translacao em studs [n, nb, 3], escala, e
    rotacao extra por quaternion (so o golpe usa)."""

    def __init__(self, modelo: Modelo, n: int, H: float):
        self.nomes = [o.nome for o in modelo.ossos]
        self.i = {nm: k for k, nm in enumerate(self.nomes)}
        nb = len(self.nomes)
        self.E = np.zeros((n, nb, 3))
        self.T = np.zeros((n, nb, 3))
        self.S = np.ones((n, nb, 3))
        self.Q: dict[int, np.ndarray] = {}
        self.n, self.H = n, H
        self.marc: list[tuple[str, float]] = []
        self.vel = 0.0
        self.modelo = modelo
        self.dirigidos: set[int] = set()      # ossos resolvidos por IK neste clipe (o seguimento automatico nao mexe)
        self.agacho = None                    # quanto o corpo desceu para o joelho ter folga (uma vez por clipe)

    def ossos(self, spec) -> list[int]:
        pads = spec if isinstance(spec, list) else [spec]
        achou = [k for p in pads for k, nm in enumerate(self.nomes) if fnmatch.fnmatchcase(nm, p)]
        if not achou:
            raise ValueError(f'camada cita osso "{spec}" que nao existe. Ossos do modelo: {self.nomes}. '
                             f'Use o nome exato ou um padrao como "Cauda_*".')
        return list(dict.fromkeys(achou))

    def somar(self, k: int, canal: str, valores):
        if canal in CANAIS_ROT:
            self.E[:, k, CANAIS_ROT.index(canal)] += valores
        elif canal in CANAIS_TRANS:
            e, s = CANAIS_TRANS[canal]
            self.T[:, k, e] += s * valores * self.H
        else:
            raise ValueError(f'canal "{canal}" nao existe; rotacao: {list(CANAIS_ROT)}; translacao (fracao de H): '
                             f'{list(CANAIS_TRANS)}')


def _onda(ac: _Acum, c: dict, fase_t):
    """Oscilador: amp * forma(2pi * (harm * t + fase)). 'harm' = ciclos inteiros por laco (fecha sem emenda)."""
    harm = int(c.get("harm", 1))
    amp = float(c["amp"])
    h2 = float(c.get("harm2", 0.0))
    forma = c.get("forma", "seno")
    for j, k in enumerate(ac.ossos(c.get("ossos", c.get("osso")))):
        f = c.get("fase", 0.0) + j * c.get("fase_por_osso", 0.0)
        a = amp * (1 + j * c.get("ganho_por_osso", 0.0))
        x = 2 * np.pi * (harm * fase_t + f)
        if forma == "seno":
            v = np.sin(x) + h2 * np.sin(2 * x + 0.7)
        elif forma == "abs":                      # quica: duas batidas por ciclo, sempre para um lado
            v = np.abs(np.sin(x))
        elif forma == "pulso":                    # pico curto e volta lenta (respiro, bote)
            u = (harm * fase_t + f) % 1.0
            v = np.where(u < 0.25, curva("sai", u / 0.25), 1 - curva("suave", (u - 0.25) / 0.75))
        elif forma == "asa":                      # desce rapido e largo, sobe devagar
            u = (harm * fase_t + f) % 1.0
            v = np.where(u < 0.4, 1 - 2 * curva("entra_sai", u / 0.4), -1 + 2 * curva("suave", (u - 0.4) / 0.6))
        else:
            raise ValueError(f'forma de onda "{forma}" nao existe; use seno, abs, pulso ou asa')
        ac.somar(k, c["canal"], a * v)


def _poses(ac: _Acum, c: dict, fase_t, laco: bool):
    """Poses-chave: [{"t": 0..1, "curva": "suave", "pose": {Osso: {"frente": 10, "cima": 0.02, "escala": [..]}}}]."""
    chaves = sorted(c["chaves"], key=lambda q: q["t"])
    if laco and chaves[0]["t"] > 0:
        chaves = [dict(chaves[-1], t=chaves[-1]["t"] - 1.0)] + chaves
    if laco:
        chaves = chaves + [dict(chaves[0] if chaves[0]["t"] >= 0 else chaves[1], t=1.0 + max(chaves[0]["t"], 0))]
    ossos = sorted({o for q in chaves for o in q.get("pose", {})})
    for nome in ossos:
        for k in ac.ossos(nome):
            canais = sorted({cn for q in chaves for cn in q.get("pose", {}).get(nome, {})})
            for cn in canais:
                if cn == "escala":
                    vals = np.array([q.get("pose", {}).get(nome, {}).get("escala", [1, 1, 1]) for q in chaves], float)
                else:
                    vals = np.array([q.get("pose", {}).get(nome, {}).get(cn, 0.0) for q in chaves], float)
                ts = np.array([q["t"] for q in chaves], float)
                out = np.zeros((ac.n,) + vals.shape[1:])
                for a in range(len(chaves) - 1):
                    t0, t1 = ts[a], ts[a + 1]
                    m = (fase_t >= t0) & (fase_t <= t1) if a == len(chaves) - 2 else (fase_t >= t0) & (fase_t < t1)
                    if not m.any() or t1 <= t0:
                        continue
                    u = curva(chaves[a + 1].get("curva", "suave"), (fase_t[m] - t0) / (t1 - t0))
                    out[m] = vals[a] + (vals[a + 1] - vals[a]) * (u[:, None] if vals.ndim > 1 else u)
                out[fase_t < ts[0]] = vals[0]
                out[fase_t > ts[-1]] = vals[-1]
                if cn == "escala":
                    ac.S[:, k, :] *= out
                else:
                    ac.somar(k, cn, out)


def _passos(ac: _Acum, c: dict, fase_t, duracao: float):
    """Locomocao por formula. Cada pe declara fase; 'apoio' = fracao do ciclo no chao (duty factor).
    Pe SOLTO (modo "solto"): no apoio o pe fica parado no mundo (anda para tras em relacao ao corpo, em
    velocidade constante = velocidade da raiz); no balanco volta pelo ar em arco, acelerando.
    Perna rigida (modo "perna"): a peca gira no quadril para o pe seguir a mesma trajetoria (aproximado)."""
    apoio = float(c.get("apoio", 0.6))
    ciclos = int(c.get("ciclos", 1))
    passada = float(c.get("passada_H", 0.5)) * ac.H          # comprimento da passada em studs
    altura = float(c.get("altura_H", 0.07)) * ac.H
    modo = c.get("modo", "solto")
    ac.vel = passada * ciclos / duracao
    alc = passada * apoio                                     # quanto o pe percorre no chao
    for pe in c["pes"]:
        u = (ciclos * fase_t + pe.get("fase", 0.0)) % 1.0
        no_chao = u < apoio
        s = np.where(no_chao, u / apoio, (u - apoio) / (1 - apoio))
        z = np.where(no_chao, alc * (0.5 - s), alc * (-0.5 + curva("suave", s)))   # + = para a frente
        y = np.where(no_chao, 0.0, altura * np.sin(np.pi * curva("sai", s)) ** 1.0)
        inclina = np.where(no_chao, 0.0, 22 * np.sin(2 * np.pi * s) * (1 - s))     # ponta sobe ao sair
        comp = float(pe.get("comprimento_H", c.get("perna_H", 0.25))) * ac.H
        for k in ac.ossos(pe["osso"]):
            cad = ac.modelo.meta.get("cadeias", {}).get(ac.nomes[k])
            if modo != "solto" and cad and len(cad["ossos"]) >= 2 and cad["eixo"] == 1 and cad["sentido"] < 0 \
                    and cad["dobra"] in ("joelho", "reverso"):
                _perna_ik(ac, c, k, cad, z, y)
                continue
            if modo == "solto":
                ac.T[:, k, 2] += -z
                ac.T[:, k, 1] += y
                ac.E[:, k, 0] += -inclina
            else:
                ac.E[:, k, 0] += -np.degrees(np.arctan2(z, comp))   # "frente" positivo leva a ponta de baixo para tras
                ac.T[:, k, 1] += y * 0.6
        for q in range(ciclos):
            ac.marc.append(("Pisada", ((q + (1 - pe.get("fase", 0.0)) % 1.0) / ciclos % 1.0) * duracao))


def _perna_ik(ac: _Acum, c: dict, k: int, cad: dict, z, y):
    """Perna de dois ossos (IK analitico, lei dos cossenos): o pe segue a trajetoria do passo e o joelho dobra.
    Para o joelho ter folga, tudo que pende da Raiz desce um pouco ("agacho", fracao do comprimento da perna)."""
    L1 = float(cad["comprimentos"][0])
    L2 = float(sum(cad["comprimentos"][1:]))
    L = L1 + L2
    if ac.agacho is None:
        ac.agacho = float(c.get("agacho", 0.07)) * L
        raiz = next(o.nome for o in ac.modelo.ossos if o.pai is None)
        for o in ac.modelo.ossos:
            if o.pai == raiz:
                ac.T[:, ac.i[o.nome], 1] -= ac.agacho
    u = -L + ac.agacho + y                                   # altura do pe em relacao ao quadril
    D = np.clip(np.sqrt(z * z + u * u), abs(L1 - L2) + 1e-4, L * 0.9995)
    phi = np.arctan2(z, -u)                                  # direcao quadril -> pe, a partir de "reto para baixo"
    alfa = np.arccos(np.clip((L1 * L1 + D * D - L2 * L2) / (2 * L1 * D), -1, 1))
    beta = np.pi - np.arccos(np.clip((L1 * L1 + L2 * L2 - D * D) / (2 * L1 * L2), -1, 1))
    s = 1.0 if cad["dobra"] == "joelho" else -1.0            # joelho aponta para a frente; reverso, para tras
    k2 = ac.i[cad["ossos"][1]]
    ac.E[:, k, 0] += -np.degrees(phi + s * alfa)             # "frente" positivo leva a ponta de baixo para tras
    ac.E[:, k2, 0] += np.degrees(s * beta)
    ac.dirigidos |= {k, k2}


def _pernas_acompanham(ac: _Acum):
    """As pernas pendem da Raiz (para o pe ficar parado quando o corpo respira). Quando o corpo TOMBA de verdade
    (morte, queda), perna que nenhuma camada animou passa a ir junto com ele, como se fosse filha do corpo."""
    raiz = next((o.nome for o in ac.modelo.ossos if o.pai is None), None)
    corpo = next((o for o in ac.modelo.ossos if o.pai == raiz and o.papel == "corpo"), None)
    if corpo is None:
        return
    kc = ac.i[corpo.nome]
    qc = np.array([quat_semantico(*ac.E[q, kc]) for q in range(ac.n)])
    if kc in ac.Q:
        qc = np.array([quat_mul(a, b) for a, b in zip(qc, ac.Q[kc])])
    ang = 2 * np.degrees(np.arccos(np.clip(np.abs(qc[:, 3]), 0, 1)))
    w = np.clip((ang - 30.0) / 25.0, 0, 1)
    w = w * w * (3 - 2 * w)
    if w.max() <= 0:
        return
    pC = np.array(corpo.pivo)
    for o in ac.modelo.ossos:
        if o.pai != raiz or o is corpo:
            continue
        k = ac.i[o.nome]
        if k in ac.dirigidos or k in ac.Q or np.abs(ac.E[:, k]).max() > 1e-9 or np.abs(ac.T[:, k]).max() > 1e-9:
            continue
        pL = np.array(o.pivo)
        Q = np.zeros((ac.n, 4))
        for q in range(ac.n):
            Q[q] = _nlerp(np.array([0, 0, 0, 1.0]), qc[q], w[q])
            ac.T[q, k] += w[q] * ac.T[q, kc] + quat_para_matriz(Q[q]) @ (pL - pC) - (pL - pC)
        ac.Q[k] = Q


def _seguir_cadeias(ac: _Acum, laco: bool, antes: np.ndarray):
    """Segmentos de cadeia que nenhuma camada animou acompanham o pai com atraso: antebraco, canela fora do
    andar, cauda, pescoco. E o que da sobreposicao (overlap) sem ninguem escrever camada."""
    seg = ac.modelo.meta.get("seguir", {})
    pai = {o.nome: o.pai for o in ac.modelo.ossos}
    for o in ac.modelo.ossos:                                # pais antes dos filhos: o atraso se propaga na cadeia
        cfg = seg.get(o.nome)
        if not cfg or o.nome not in ac.i or pai[o.nome] not in ac.i:
            continue
        k, kp = ac.i[o.nome], ac.i[pai[o.nome]]
        if k in ac.dirigidos or np.abs(ac.E[:, k] - antes[:, k]).max() > 1e-9:
            continue
        d = max(1, int(round(cfg["atraso_s"] * FPS)))
        src = ac.E[:, kp, :]
        sh = np.roll(src, d, axis=0) if laco else np.concatenate([np.repeat(src[:1], d, 0), src[:-d]])[:ac.n]
        g = cfg["ganho"]
        if cfg["modo"] == "livre":
            ac.E[:, k, :] += g * sh
        else:
            fr = sh[:, 0]                                    # < 0 = o osso de cima foi para a frente
            if cfg["modo"] == "cotovelo":
                ac.E[:, k, 0] += -np.clip(8 + 1.2 * g * np.maximum(-fr, 0) + 0.3 * g * np.abs(fr), 0, 110)
            else:
                flex = np.clip(1.6 * g * np.maximum(-fr, 0) + 0.4 * g * np.maximum(fr, 0), 0, 120)
                ac.E[:, k, 0] += flex if cfg["modo"] == "joelho" else -flex


def _seguir(ac: _Acum, c: dict, laco: bool):
    """Sobreposicao: o osso repete o movimento ja acumulado de outro, com atraso e ganho."""
    fonte = ac.ossos(c["de"])[0]
    d = int(round(float(c.get("atraso_s", 0.08)) * FPS))
    g = float(c.get("ganho", 0.6))
    for j, k in enumerate(ac.ossos(c.get("ossos", c.get("osso")))):
        dj = d * (j + 1) if c.get("em_cadeia") else d
        for arr in ((ac.E,) if c.get("canais", "rot") == "rot" else (ac.E, ac.T)):
            src = arr[:, fonte, :]
            sh = np.roll(src, dj, axis=0) if laco else np.concatenate([np.repeat(src[:1], dj, 0), src[:-dj or None]])[:ac.n]
            arr[:, k, :] += g * sh


def _tremor(ac: _Acum, c: dict, fase_t):
    """Solavancos secos com quadros segurados (terror): senos de frequencias primas entre si, janelados."""
    t0, t1 = c.get("de_t", 0.0), c.get("ate_t", 1.0)
    jan = ((fase_t >= t0) & (fase_t <= t1)).astype(float)
    seg = int(c.get("segurar", 2))
    for j, k in enumerate(ac.ossos(c.get("ossos", c.get("osso")))):
        v = np.sin(2 * np.pi * (11 + 2 * j) * fase_t + j) * np.sin(2 * np.pi * (7 + j) * fase_t) * jan
        v = np.repeat(v[::seg], seg)[:ac.n]
        ac.somar(k, c["canal"], float(c["amp"]) * v)


def _golpe(ac: _Acum, c: dict, fase_t, modelo: Modelo):
    """Golpe por ficha: a PONTA do item percorre um arco num plano inclinado; a mao solta segue o arco e
    gira para o gume ir na frente; o tronco gira (quadril lidera), o corpo desce no contato."""
    f = c["ficha"]
    lado = 1.0 if c.get("mao", "Mao_D").endswith("_D") else -1.0
    k = ac.ossos(c.get("mao", "Mao_D"))[0]
    tp = np.cumsum(f.get("tempos", [0.30, 0.10, 0.05, 0.25, 0.30]))
    tp = tp / tp[-1]
    a0, a1 = np.radians(f["arco"]["inicio_graus"]), np.radians(f["arco"]["fim_graus"])
    passa = a1 + (a1 - a0) * 0.12
    ang = np.zeros(ac.n)
    peso = np.zeros(ac.n)                                    # 0 = mao em repouso, 1 = mao no arco
    for q, t in enumerate(fase_t):
        if t < tp[0]:
            u = curva("suave", t / tp[0]); ang[q] = a0; peso[q] = u
        elif t < tp[2]:
            u = curva("golpe", (t - tp[0]) / (tp[2] - tp[0])); ang[q] = a0 + (a1 - a0) * u; peso[q] = 1
        elif t < tp[3]:
            u = curva("sai", (t - tp[2]) / (tp[3] - tp[2])); ang[q] = a1 + (passa - a1) * u; peso[q] = 1
        else:
            # recuperacao: primeiro a arma volta PELA FRENTE ate a guarda (nunca em linha reta por dentro do corpo),
            # so entao a mao solta para o repouso
            u = (t - tp[3]) / (1 - tp[3])
            guarda = np.radians(f["arco"].get("guarda_graus", 35))
            if u < 0.6:
                ang[q] = passa + (guarda - passa) * curva("suave", u / 0.6); peso[q] = 1
            else:
                ang[q] = guarda; peso[q] = 1 - curva("suave", (u - 0.6) / 0.4)
    p = np.radians(f.get("plano_graus", 35))
    e1 = np.array([0.0, 0.0, -1.0])                                   # frente
    e2 = np.array([lado * np.cos(p), np.sin(p), 0.0])                 # lado da arma, subindo com o plano
    tronco = modelo.osso(c.get("tronco", "Tronco"))
    ctr = f.get("centro_H", {})
    centro = np.array(tronco.pivo) + np.array([lado * float(ctr.get("lado", 0.12)), float(ctr.get("cima", 0.30)),
                                                -float(ctr.get("frente", 0.0))]) * ac.H
    # o item pode ter giro de repouso (empunhadura): a mao desfaz esse giro para a lamina seguir o arco
    item = next((o for o in modelo.ossos if o.pai == ac.nomes[k] and o.papel == "item"), None)
    q_item = quat_conj(item.repouso) if item is not None else np.array([0, 0, 0, 1.0])
    raio_mao = float(f["arco"].get("raio_mao_H", 0.30)) * ac.H
    rep = np.array(modelo.osso(ac.nomes[k]).pivo)
    Q = np.zeros((ac.n, 4)); Q[:, 3] = 1
    for q in range(ac.n):
        u_r = np.cos(ang[q]) * e1 + np.sin(ang[q]) * e2               # radial: da pegada para a ponta
        tg = np.sin(ang[q]) * e1 - np.cos(ang[q]) * e2                # sentido do movimento: gume na frente
        alvo = centro + u_r * raio_mao
        ac.T[q, k] += (alvo - rep) * peso[q]
        x = np.cross(u_r, tg)
        Rm = np.stack([x, u_r, tg], axis=1)                           # colunas = eixos X, Y, Z da mao
        qa = quat_mul(matriz_para_quat(Rm), q_item)
        Q[q] = _nlerp(np.array([0, 0, 0, 1.0]), qa, peso[q])
    ac.Q[k] = Q
    tr = f.get("tronco", {})
    giro = float(tr.get("giro_graus", 35))
    atraso = float(tr.get("atraso_ombro_s", 0.06))
    carga = (ang - a1) / (a0 - a1 + 1e-9)                              # 1 = armado, 0 = no fim do arco
    kt = ac.ossos(c.get("tronco", "Tronco"))[0]
    g = -lado * giro * (np.clip(carga, -0.2, 1) - 0.5) * peso
    d = int(round(atraso * FPS))
    ac.E[:, kt, 1] += np.concatenate([np.repeat(g[:1], d), g[:-d or None]])[:ac.n]
    ac.E[:, kt, 0] += float(tr.get("inclinacao_graus", 10)) * (1 - np.clip(carga, 0, 1)) * peso
    if "Cabeca" in ac.i:
        ac.E[:, ac.i["Cabeca"], 1] -= 0.5 * np.concatenate([np.repeat(g[:1], d), g[:-d or None]])[:ac.n]
    desce = np.exp(-((fase_t - tp[2]) / 0.07) ** 2) * 0.05 * ac.H      # corpo desce ~5% de H no contato
    ac.T[:, kt, 1] -= desce
    dur = f.get("duracao_s", 0.7)
    ac.marc += [("Golpe", tp[0] * dur), ("Impacto", tp[1] * dur)]


def _nlerp(a, b, t):
    if np.dot(a, b) < 0:
        b = -b
    q = a + (b - a) * t
    return q / np.linalg.norm(q)


def assar_clipe(modelo: Modelo, receita: dict, *, H: float | None = None, fator_tempo: float = 1.0) -> Clipe:
    """Assa uma receita em Clipe (30 fps). H = altura de referencia (padrao: altura do modelo).
    fator_tempo multiplica a duracao (use raiz de k para criaturas maiores que o heroi medio)."""
    if H is None:
        mn, mx = modelo.caixa()
        H = float(mx[1] - mn[1])
    laco = bool(receita.get("laco", False))
    dur = float(receita["duracao"]) * (fator_tempo if receita.get("escala_tempo", True) else 1.0)
    n = Clipe.quadros_para(dur, laco)
    fase_t = np.arange(n) / (n if laco else max(n - 1, 1))
    ac = _Acum(modelo, n, H)
    antes = ac.E.copy()
    for i, c in enumerate(receita.get("camadas", [])):
        tipo = c.get("tipo")
        try:
            if tipo == "onda":
                _onda(ac, c, fase_t)
            elif tipo == "poses":
                _poses(ac, c, fase_t, laco)
            elif tipo == "passos":
                _passos(ac, c, fase_t, dur)
            elif tipo == "seguir":
                _seguir(ac, c, laco)
            elif tipo == "tremor":
                _tremor(ac, c, fase_t)
            elif tipo == "golpe":
                _golpe(ac, c, fase_t, modelo)
            else:
                raise ValueError(f'tipo de camada "{tipo}" nao existe; use um de {list(TIPOS)}')
        except (KeyError, ValueError) as e:
            raise ValueError(f'clipe "{receita.get("nome")}", camada {i + 1} ({tipo}): {e}') from None
    _pernas_acompanham(ac)
    _seguir_cadeias(ac, laco, antes)
    cl = Clipe.vazio(receita["nome"], dur, ac.nomes, laco=laco)
    cl.trans[:] = ac.T
    for q in range(n):
        for k in range(len(ac.nomes)):
            e = ac.E[q, k]
            qq = quat_semantico(e[0], e[1], e[2]) if e.any() else np.array([0, 0, 0, 1.0])
            if k in ac.Q:
                qq = quat_mul(qq, ac.Q[k][q])
            cl.rot[q, k] = qq
    if not np.allclose(ac.S, 1.0):
        cl.escala = ac.S.astype(np.float32)
    cl.vel_raiz = float(receita.get("vel_raiz", ac.vel))
    cl.marcadores = sorted([(nm, round(float(t), 3)) for nm, t in ac.marc] +
                           [(nm, round(float(fr) * dur, 3)) for nm, fr in receita.get("marcadores", [])],
                           key=lambda m: m[1])
    cl.meta = {"acerto": receita.get("acerto")} if receita.get("acerto") else {}
    return cl


# --------------------------------------------------------------------------- medidas (para o P1)

def medir(modelo: Modelo, cl: Clipe, papeis: dict | None = None) -> dict:
    """Numeros de naturalidade e seguranca do clipe."""
    w = 2 * np.degrees(np.arccos(np.clip(np.abs((cl.rot[1:] * cl.rot[:-1]).sum(-1)), 0, 1)))   # graus por quadro
    salto = 0.0
    if cl.laco and cl.n_quadros > 2:      # o passo do ultimo quadro para o primeiro deve ser um passo normal
        dt = np.abs(np.diff(cl.trans, axis=0)).max()
        dw = w.max() if w.size else 0.0
        vt = np.abs(cl.trans[0] - cl.trans[-1]).max()
        vw = float(2 * np.degrees(np.arccos(np.clip(np.abs((cl.rot[0] * cl.rot[-1]).sum(-1)), 0, 1))).max())
        salto = max(vt / (dt + 1e-4), vw / (dw + 1e-2))     # 1 = igual aos outros passos; > 2,5 = estalo
    mov = (np.abs(np.diff(cl.trans, axis=0)).sum((0, 2)) > 1e-5) | (w.sum(0) > 0.05)
    if cl.escala is not None:
        mov = mov | (np.abs(np.diff(cl.escala, axis=0)).sum((0, 2)) > 1e-4)
    # "gemeos": correlacao entre um osso _D e o seu par _E (1.0 = espelho perfeito = cara de codigo)
    gemeos = 0.0
    for i, nm in enumerate(cl.ossos):
        if nm.endswith("_D") and nm[:-2] + "_E" in cl.ossos and (papeis or {}).get(nm, "perna") in ("perna", "pe", "mao", "braco"):
            j = cl.ossos.index(nm[:-2] + "_E")
            a = np.concatenate([cl.trans[:, i].ravel(), cl.rot[:, i, :3].ravel()])
            b = np.concatenate([cl.trans[:, j].ravel(), cl.rot[:, j, :3].ravel()])
            if a.std() > 1e-6 and b.std() > 1e-6:
                gemeos = max(gemeos, float(abs(np.corrcoef(np.abs(a), np.abs(b))[0, 1])) if np.allclose(np.abs(a), np.abs(b), atol=1e-4) else 0.0)
    return {"giro_max_graus_quadro": round(float(w.max()) if w.size else 0.0, 2), "salto_no_laco": round(salto, 4),
            "ossos_em_movimento": int(mov.sum()), "gemeos": round(gemeos, 3), "vel_raiz": round(cl.vel_raiz, 3)}
