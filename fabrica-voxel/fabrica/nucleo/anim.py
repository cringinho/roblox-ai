"""Animacao: assa clipes a 30 fps a partir de RECEITAS declarativas por camadas.

Angulos sempre semanticos, em graus: frente (topo vai para a frente), esquerda (vira para o lado _E),
tombar_direita (topo vai para a direita). Translacoes em FRACOES DE H (altura do modelo), entao o mesmo
clipe serve em qualquer tamanho. Tudo e soma de camadas; nada de quaternion na ficha.

Camadas: onda, poses, passos, seguir, tremor, golpe, soltar_bracos, vida, impacto. Ver docs/ARQUITETURA.md, secao 7 e cartoes/animacao.md.
"""
from __future__ import annotations

import fnmatch

import numpy as np

from .contrato import (FPS, Clipe, Modelo, matriz_para_quat, matriz_translacao, matriz_trs, quat_conj, quat_mul,
                       quat_para_matriz, quat_semantico)

CANAIS_ROT = ("frente", "esquerda", "tombar_direita")
CANAIS_TRANS = {"direita": (0, 1), "esquerda_t": (0, -1), "cima": (1, 1), "baixo": (1, -1),
                "frente_t": (2, -1), "tras": (2, 1)}
CURVAS = ("linear", "suave", "entra", "sai", "entra_sai", "passa_e_volta", "degrau", "golpe")
TIPOS = ("onda", "poses", "passos", "seguir", "tremor", "golpe", "soltar_bracos", "vida", "impacto", "ondular")


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
        self.ABS: dict[int, np.ndarray] = {}  # rotacao final do osso, ja resolvida (braco no golpe): vale no lugar de E e Q
        self.golpes: list[dict] = []          # golpes de braco articulado, resolvidos depois de todas as camadas
        self.pisadas: list[tuple[float, int]] = []   # (fracao do clipe, osso do pe) de cada pisada, para a camada "impacto"
        self.apoios: list[tuple[int, np.ndarray]] = []   # (osso do pe, quadros em que esta no chao)
        self.vida: dict | None = None         # parametros da camada "vida" para as cadeias, aplicados no fim
        self.patas: list[dict] = []           # patas de varios ossos (artropode), resolvidas no fim com o corpo ja na pose final

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
    q_balanco = (1 - apoio) * ac.n / ciclos                  # passo muito rapido tem poucos quadros no ar: o pe sobe menos
    if q_balanco < 7:
        altura *= max(0.35, (q_balanco / 7.0) ** 1.4)
    ac.vel = passada * ciclos / duracao
    alc = passada * apoio                                     # quanto o pe percorre no chao
    for pe in c["pes"]:
        u = (ciclos * fase_t + pe.get("fase", 0.0)) % 1.0
        no_chao = u < apoio
        s = np.where(no_chao, u / apoio, (u - apoio) / (1 - apoio))
        z = np.where(no_chao, alc * (0.5 - s), alc * (-0.5 + curva("suave", s)))   # + = para a frente
        # o pe passa pelo alto a 44% do balanco e so pousa no fim (antes ele encostava cedo e
        # deslizava para a frente rente ao chao: e o defeito que o olho ve primeiro)
        y = np.where(no_chao, 0.0, altura * np.sin(np.pi * (1 - (1 - s) ** 1.2)))
        inclina = np.where(no_chao, 0.0, 22 * np.sin(2 * np.pi * s) * (1 - s))     # ponta sobe ao sair
        comp = float(pe.get("comprimento_H", c.get("perna_H", 0.25))) * ac.H
        if modo == "perna" and "comprimento_H" not in pe:    # perna rigida: usa o comprimento medido na peca
            o_pe = ac.modelo.osso(ac.nomes[ac.ossos(pe["osso"])[0]])
            medido = float(o_pe.pivo[1] - ponta_da_perna(ac.modelo, o_pe.nome)[1])
            if medido > 0.05:
                comp = medido
        if modo == "patas":                                   # pata de varios ossos em qualquer direcao: resolve no fim
            for k in ac.ossos(pe["osso"]):
                ac.patas.append({"raiz": k, "z": z, "y": y, "abre": float(pe.get("abre_H", 0.0)) * ac.H,
                                 "chao": no_chao, "s": s})
        for k in ([] if modo == "patas" else ac.ossos(pe["osso"])):
            cad = ac.modelo.meta.get("cadeias", {}).get(ac.nomes[k])
            if modo != "solto" and cad and len(cad["ossos"]) >= 2 and cad["eixo"] == 1 and cad["sentido"] < 0 \
                    and cad["dobra"] in ("joelho", "reverso"):
                _perna_ik(ac, c, k, cad, z, y, inclina)
                continue
            if modo == "solto":
                ac.T[:, k, 2] += -z
                ac.T[:, k, 1] += y
                ac.E[:, k, 0] += -inclina
            else:
                ac.E[:, k, 0] += -np.degrees(np.arctan2(z, comp))   # "frente" positivo leva a ponta de baixo para tras
                ac.T[:, k, 1] += y * 0.6
        k_pe = ac.ossos(pe["osso"])[0]
        ac.apoios.append((k_pe, no_chao))
        for q in range(ciclos):
            fr = (q + (1 - pe.get("fase", 0.0)) % 1.0) / ciclos % 1.0
            ac.marc.append(("Pisada", fr * duracao))
            ac.pisadas.append((fr, k_pe))


def _perna_ik(ac: _Acum, c: dict, k: int, cad: dict, z, y, inclina=0.0):
    """Perna de dois ossos (IK analitico, lei dos cossenos): o pe segue a trajetoria do passo e o joelho dobra.
    Para o joelho ter folga, tudo que pende da Raiz desce um pouco ("agacho", fracao do comprimento da perna)."""
    L1 = float(cad["comprimentos"][0])
    tres = len(cad["ossos"]) >= 3                            # terceiro osso = o pe: fica plano no chao
    L2 = float(cad["comprimentos"][1]) if tres else float(sum(cad["comprimentos"][1:]))
    L = L1 + L2
    if ac.agacho is None:
        ac.agacho = float(c.get("agacho", 0.07)) * L
        raiz = next(o.nome for o in ac.modelo.ossos if o.pai is None)
        for o in ac.modelo.ossos:
            if o.pai == raiz:
                ac.T[:, ac.i[o.nome], 1] -= ac.agacho
    u = -L + ac.agacho + y                                   # altura do pe em relacao ao quadril
    D = np.sqrt(z * z + u * u)
    ds = float(c.get("ik_suave", 0.05)) * L                  # IK suave: perto de esticar, a perna chega devagar ao limite
    da = L - ds                                              # (sem isso o joelho estala: a conta e singular com a perna reta)
    D = np.where(D > da, da + ds * (1 - np.exp(-(D - da) / ds)), D)
    D = np.clip(D, abs(L1 - L2) + 1e-4, L * 0.9995)
    phi = np.arctan2(z, -u)                                  # direcao quadril -> pe, a partir de "reto para baixo"
    alfa = np.arccos(np.clip((L1 * L1 + D * D - L2 * L2) / (2 * L1 * D), -1, 1))
    beta = np.pi - np.arccos(np.clip((L1 * L1 + L2 * L2 - D * D) / (2 * L1 * L2), -1, 1))
    s = 1.0 if cad["dobra"] == "joelho" else -1.0            # joelho aponta para a frente; reverso, para tras
    k2 = ac.i[cad["ossos"][1]]
    t1, t2 = -np.degrees(phi + s * alfa), np.degrees(s * beta)   # "frente" positivo leva a ponta de baixo para tras
    ac.E[:, k, 0] += t1
    ac.E[:, k2, 0] += t2
    ac.dirigidos |= {k, k2}
    if tres:                                                 # o pe gira ao contrario da perna e rola na ponta ao sair
        k3 = ac.i[cad["ossos"][2]]
        ac.E[:, k3, 0] += -(t1 + t2) - 0.6 * inclina
        ac.dirigidos.add(k3)


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
        if o.mola and cfg["modo"] == "livre":                # mola assada: atrasa, passa do ponto e assenta
            sh = _mola(src, float(o.mola.get("freq_hz", 2.5)), float(o.mola.get("amort", 0.5)), laco)
            lim = float(o.mola.get("max_graus", 30))
            sh = np.clip(sh, -lim, lim)
        else:
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
    pai_mao = modelo.osso(modelo.osso(ac.nomes[k]).pai) if modelo.osso(ac.nomes[k]).pai else None
    articulado = pai_mao is not None and pai_mao.papel == "braco"
    tp = np.cumsum(f.get("tempos", [0.30, 0.10, 0.05, 0.25, 0.30]))
    tp = tp / tp[-1]
    a0, a1 = np.radians(f["arco"]["inicio_graus"]), np.radians(f["arco"]["fim_graus"])
    passa = a1 + (a1 - a0) * 0.12
    ang = np.zeros(ac.n)
    peso = np.zeros(ac.n)                                    # 0 = mao em repouso, 1 = mao no arco
    for q, t in enumerate(fase_t):
        if t < tp[0]:
            if articulado:           # com braco: sobe PELA GUARDA e depois pelo proprio arco, nunca em linha reta por dentro do corpo
                u = t / tp[0]
                gd = np.radians(f["arco"].get("guarda_graus", 35))
                if u < 0.4:
                    ang[q] = gd; peso[q] = curva("suave", u / 0.4)
                else:
                    ang[q] = gd + (a0 - gd) * curva("suave", (u - 0.4) / 0.6); peso[q] = 1
            else:
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
    if articulado:
        _golpe_tronco(ac, c, f, fase_t, tp, ang, a0, a1, peso, lado)
        ac.golpes.append({"mao": k, "braco": ac.i[pai_mao.nome], "lado": lado, "ang": ang, "peso": peso, "e1": e1, "e2": e2,
                          "ficha": f, "tronco": ac.i[tronco.nome],
                          "carga": np.clip((ang - a1) / (a0 - a1 + 1e-9), 0, 1)})
        return
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
    _golpe_tronco(ac, c, f, fase_t, tp, ang, a0, a1, peso, lado, desce_H=0.05)


def _golpe_tronco(ac: _Acum, c: dict, f: dict, fase_t, tp, ang, a0, a1, peso, lado, desce_H: float = 0.0):
    """Parte do golpe que e do corpo: o tronco gira (quadril lidera, ombro atrasa), inclina no contato, a cabeca
    compensa metade. desce_H so vale para o heroi de pecas soltas (com pernas, o tronco nao pode sair de cima delas)."""
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
    if desce_H:
        ac.T[:, kt, 1] -= np.exp(-((fase_t - tp[2]) / 0.07) ** 2) * desce_H * ac.H   # corpo desce no contato
    dur = f.get("duracao_s", 0.7)
    ac.marc += [("Golpe", tp[0] * dur), ("Impacto", tp[1] * dur)]


def _soltar_bracos(ac: _Acum, c: dict, fase_t):
    """Queda e morte: a mao larga a pose de empunhadura. O antebraco estica (desfaz a dobra de repouso) e o item
    fica ao comprido do braco, apontando para longe do corpo. Entre "de_t" e "ate_t" a mudanca entra suave."""
    t0, t1 = float(c.get("de_t", 0.2)), float(c.get("ate_t", 0.55))
    w = curva("suave", np.clip((fase_t - t0) / max(t1 - t0, 1e-6), 0, 1))
    ident = np.array([0.0, 0.0, 0.0, 1.0])
    vira = np.array([0.0, 0.0, 1.0, 0.0])                      # meia volta: a ponta do item vai para o lado da mao
    for o in ac.modelo.ossos:
        if o.papel != "item" or o.nome not in ac.i:
            continue
        mao = ac.modelo.osso(o.pai)
        ac.ABS[ac.i[o.nome]] = np.array([_nlerp(ident, quat_mul(quat_conj(np.array(o.repouso)), vira), x) for x in w])
        if tuple(mao.repouso) != (0.0, 0.0, 0.0, 1.0) and mao.nome in ac.i:
            ac.ABS[ac.i[mao.nome]] = np.array([_nlerp(ident, quat_conj(np.array(mao.repouso)), x) for x in w])
            ac.dirigidos.add(ac.i[mao.nome])


def _arco_curto(de, para):
    """Matriz da menor rotacao que leva o vetor `de` ao vetor `para` (sem torcer). So e instavel se forem opostos."""
    a, b = de / np.linalg.norm(de), para / np.linalg.norm(para)
    v, c = np.cross(a, b), float(np.dot(a, b))
    if c < -0.9999:                                   # opostos: meia volta em torno de X
        return np.diag([1.0, -1.0, -1.0])
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1.0 + c)


def _resolver_golpes(ac: _Acum):
    """Golpe com braco de dois ossos. A mao segue o arco ate onde o braco alcanca (personagem cabecudo tem braco
    curto: o arco encolhe sozinho); cotovelo por IK analitico com polo para baixo e para fora; o item gira no punho
    para a lamina seguir o arco com o gume na frente. Roda depois de todas as camadas, com o tronco ja na pose final."""
    m = ac.modelo
    for g in ac.golpes:
        kB, kM, kT, lado, f = g["braco"], g["mao"], g["tronco"], g["lado"], g["ficha"]
        oB, oM, oT = m.osso(ac.nomes[kB]), m.osso(ac.nomes[kM]), m.osso(ac.nomes[kT])
        item = next((o for o in m.ossos if o.pai == oM.nome and o.papel == "item"), None)
        pS, pE = np.array(oB.pivo), np.array(oM.pivo)
        soq = next((s for s in m.soquetes if s.osso == oM.nome and s.nome.startswith("Pegada")), None)
        pG = np.array(item.pivo) if item is not None else (np.array(soq.pos) if soq else pE + (pE - pS))
        L1, L2 = float(np.linalg.norm(pE - pS)), float(np.linalg.norm(pG - pE))
        ctr = f.get("centro_H", {})
        centro = pS + np.array([lado * float(ctr.get("lado", 0.0)), float(ctr.get("cima", -0.02)), -float(ctr.get("frente", 0.05))]) * ac.H
        raio = float(f["arco"].get("alcance", 0.92)) * (L1 + L2)
        RrB, RrI = quat_para_matriz(oB.repouso), (quat_para_matriz(item.repouso) if item is not None else np.eye(3))
        RrM = quat_para_matriz(oM.repouso)            # o antebraco pode ter dobra de repouso (empunhadura)
        polo = np.array([lado * 0.5, -0.7, 0.5])
        QB, QM, QI = (np.zeros((ac.n, 4)) for _ in range(3))
        for q in range(ac.n):
            e = ac.E[q, kT]
            qT = quat_semantico(e[0], e[1], e[2])
            if kT in ac.Q:
                qT = quat_mul(qT, ac.Q[kT][q])
            RT = quat_para_matriz(qT)
            S = np.array(oT.pivo) + ac.T[q, kT] + RT @ (pS - np.array(oT.pivo))        # ombro no mundo
            a = g["ang"][q]
            u_r = np.cos(a) * g["e1"] + np.sin(a) * g["e2"]
            tg = np.sin(a) * g["e1"] - np.cos(a) * g["e2"]
            # estocada: o braco recolhe na preparacao ("recuo" = fracao do alcance) e estica no golpe
            d = centro + u_r * raio * (1.0 - float(f["arco"].get("recuo", 0.0)) * g["carga"][q]) - S
            D = float(np.clip(np.linalg.norm(d), abs(L1 - L2) + 1e-4, (L1 + L2) * 0.999))
            dn = d / (np.linalg.norm(d) + 1e-9)
            pp = polo - np.dot(polo, dn) * dn
            pp = pp / (np.linalg.norm(pp) + 1e-9)
            ca = np.clip((L1 * L1 + D * D - L2 * L2) / (2 * L1 * D), -1, 1)
            cot = S + L1 * (ca * dn + np.sqrt(1 - ca * ca) * pp)
            mao = S + D * dn
            R1 = _arco_curto(np.array([0.0, -1.0, 0.0]), cot - S)          # braco em repouso aponta para baixo
            R2 = _arco_curto(cot - S, mao - cot) @ R1
            w = g["peso"][q]
            eb, em = ac.E[q, kB], ac.E[q, kM]
            QB[q] = _nlerp(quat_semantico(eb[0], eb[1], eb[2]), matriz_para_quat(RrB.T @ RT.T @ R1), w)
            QM[q] = _nlerp(quat_semantico(em[0], em[1], em[2]), matriz_para_quat(RrM.T @ R1.T @ R2), w)
            Rt = np.stack([np.cross(u_r, tg), u_r, tg], axis=1)
            QI[q] = _nlerp(np.array([0, 0, 0, 1.0]), matriz_para_quat(RrI.T @ R2.T @ Rt), w)
        ac.ABS[kB], ac.ABS[kM] = QB, QM
        if item is not None and item.nome in ac.i:
            ac.ABS[ac.i[item.nome]] = QI
        ac.dirigidos |= {kB, kM}



# --------------------------------------------------------------------------- vida, impacto e mola (dossies 13 e 15)

def _mola(u: np.ndarray, freq_hz: float, amort: float, laco: bool, sub: int = 4) -> np.ndarray:
    """Passa o sinal u [n, ...] por uma mola amortecida (x'' = w2 (u - x) - 2 z w x'). O resultado segue u com atraso,
    passa do ponto quando u para e assenta. Em laco, roda tres voltas e fica com a ultima (regime periodico)."""
    w = 2 * np.pi * freq_hz
    dt = 1.0 / (FPS * sub)
    x, v = u[0].astype(float).copy(), np.zeros_like(u[0], dtype=float)
    out = np.zeros_like(u, dtype=float)
    n = len(u)
    for volta in range(3 if laco else 1):
        for q in range(n):
            alvo0, alvo1 = u[q], u[(q + 1) % n] if laco else u[min(q + 1, n - 1)]
            out[q] = x
            for i in range(sub):
                alvo = alvo0 + (alvo1 - alvo0) * (i / sub)
                v += (w * w * (alvo - x) - 2 * amort * w * v) * dt
                x += v * dt
    return out


def _harmonicos(dur: float, periodos: list[float]) -> list[int]:
    """Ciclos inteiros por laco para cada periodo pedido, sem repetir quando da (o olho nao acha a emenda)."""
    usados: list[int] = []
    for p in periodos:
        h = max(1, int(round(dur / p)))
        for cand in (h, h + 1, h - 1, h + 2):
            if cand >= 1 and cand not in usados:
                h = cand
                break
        usados.append(h)
    return usados


def _familia(papel: str) -> str:
    return papel[:-4] if papel.endswith("_seg") else papel


PAPEIS_ONDA = {"cauda": 1.0, "pescoco": 0.45, "antena": 2.2, "haste": 0.7, "lingua": 1.2, "tentaculo": 1.3, "segmento": 0.5,
               "barbatana": 0.8, "folha": 0.8, "raiz_planta": 0.5}


def _cadeias_por_papel(modelo: Modelo) -> list[tuple[str, list[str]]]:
    """Fileiras de ossos do mesmo papel, pai e filho (Cauda_1 > Cauda_2 > ...), declaradas osso a osso ou por "segmentos"."""
    por_nome = {o.nome: o for o in modelo.ossos}
    filhos: dict[str, list] = {}
    for o in modelo.ossos:
        filhos.setdefault(o.pai, []).append(o)
    out = []
    for o in modelo.ossos:
        fam = _familia(o.papel)
        if fam not in PAPEIS_ONDA or (o.pai in por_nome and _familia(por_nome[o.pai].papel) == fam):
            continue
        fila, atual = [o.nome], o
        while True:
            prox = next((x for x in filhos.get(atual.nome, []) if _familia(x.papel) == fam), None)
            if prox is None:
                break
            fila.append(prox.nome)
            atual = prox
        out.append((fam, fila))
    return out


def _direcao(modelo: Modelo, fila: list[str]) -> np.ndarray:
    """Para onde a cadeia aponta em repouso: do primeiro pivo ate o centro das pecas do ultimo osso."""
    p0 = np.array(modelo.osso(fila[0]).pivo, float)
    cx = [p.grade.caixa() for p in modelo.pecas if p.osso == fila[-1] and p.grade.n_voxels()]
    p1 = (np.min([c[0] for c in cx], 0) + np.max([c[1] for c in cx], 0)) / 2 if cx else np.array(modelo.osso(fila[-1]).pivo, float)
    d = p1 - p0
    return d / (np.linalg.norm(d) + 1e-9)


def _canais_da_cadeia(d: np.ndarray) -> tuple[str, str, float]:
    """(canal lateral, canal vertical, sinal do vertical para a ponta subir)."""
    e = int(np.argmax(np.abs(d)))
    if e == 1:
        return "tombar_direita", "frente", -1.0
    if e == 0:
        return "esquerda", "tombar_direita", 1.0 if d[0] < 0 else -1.0
    return "esquerda", "frente", 1.0 if d[2] > 0 else -1.0


def _ondular(ac: _Acum, c: dict, fase_t):
    """Onda que VIAJA pelo corpo (centopeia, cobra, peixe, verme). "graus" e o quanto cada segmento se desvia do
    caminho, no mundo; a camada calcula o giro de cada osso em relacao ao pai e desloca a cadeia de lado para o
    corpo ficar sobre o caminho. Com "onda" comum em Seg_*, os giros se somam e a traseira chicoteia como uma vara."""
    ks = ac.ossos(c.get("ossos", c.get("osso")))
    n = len(ks)
    A = float(c.get("graus", 8.0))
    ondas = float(c.get("ondas", 1.0))                       # quantos comprimentos de onda cabem no corpo
    harm = int(c.get("harm", 1))
    cresce = float(c.get("cresce", 0.0))                     # 0.5 = a ponta desvia 50% mais que a base
    canal = c.get("canal", "esquerda")
    if canal not in CANAIS_ROT:
        raise ValueError(f'"ondular": canal deve ser um de {list(CANAIS_ROT)}')
    phi = np.zeros((ac.n, n))
    for j in range(n):
        phi[:, j] = A * (1 + cresce * j / max(n - 1, 1)) * np.sin(2 * np.pi * (harm * fase_t + c.get("fase", 0.0) - ondas * j / n))
    for j, k in enumerate(ks):
        ac.somar(k, canal, phi[:, j] - (phi[:, j - 1] if j else 0.0))
    if canal == "esquerda" and c.get("centrar", True) and n >= 3:
        piv = np.array([ac.modelo.osso(ac.nomes[k]).pivo for k in ks], float)
        L = np.linalg.norm(np.diff(piv, axis=0), axis=1)
        L = np.append(L, L[-1])
        sentido = 1.0 if piv[-1][2] >= piv[0][2] else -1.0  # cadeia que vai para tras: guinada positiva leva a ponta para +X
        x = np.cumsum(sentido * L[None, :] * np.sin(np.radians(phi)), axis=1)
        ac.T[:, ks[0], 0] += -x.mean(axis=1)


def _respiro(u):
    """Inspira em um terco do ciclo, solta em dois tercos (1:2). Devolve -0,5 a 0,5."""
    u = u % 1.0
    return np.where(u < 1 / 3, curva("suave", u * 3), 1 - curva("suave", (u - 1 / 3) * 1.5)) - 0.5


def _vida(ac: _Acum, c: dict, fase_t, dur: float):
    """Camada de vida, para todo Parado (e mais fraca nos outros lacos): o corpo respira, passa o peso de um lado ao
    outro e gira um nada nos tres eixos, cada coisa num periodo diferente; a cabeca compensa atrasada e tem dois
    balancos proprios; a mandibula solta o ar; caudas, pescocos e antenas que nenhuma outra camada animou ganham
    uma onda que viaja da base para a ponta. Nenhuma parte se move sozinha."""
    g = float(c.get("intensidade", 1.0))
    m = ac.modelo
    raiz = next(o.nome for o in m.ossos if o.pai is None)
    corpo = c.get("corpo") or next((o.nome for o in m.ossos if o.papel == "corpo" and o.pai == raiz), None) \
        or next((o.nome for o in m.ossos if o.papel == "corpo"), None)
    if corpo is None:
        raise ValueError('a camada "vida" precisa de um osso com "papel": "corpo" (ou diga qual em "corpo").')
    kc = ac.ossos(corpo)[0]
    pai = {o.nome: o.pai for o in m.ossos}

    def desce_de(nome, anc):
        while nome:
            if nome == anc:
                return True
            nome = pai.get(nome)
        return False
    # pernas presas ao corpo (aranha, inseto): o corpo mexe pouco, senao os pes escorregam
    presa = any(_familia(o.papel) in ("perna", "pe") and desce_de(o.pai, ac.nomes[kc]) for o in m.ossos)
    k_rot, k_tr, k_resp = (0.3, 0.0, 1.0) if presa else (1.0, 1.0, 1.0)
    if presa and c.get("plantar", True):                   # as pontas das patas ficam cravadas e o corpo se move sobre elas
        raizes = [o for o in m.ossos if _familia(o.papel) == "perna" and desce_de(o.pai, ac.nomes[kc])
                  and _familia(m.osso(o.pai).papel) not in ("perna", "pe")]
        raizes = [o for o in raizes if len(cadeia_da_perna(m, o.nome)) >= 2]
        if raizes:
            zero = np.zeros(ac.n)
            ja = {r["raiz"] for r in ac.patas}
            ac.patas += [{"raiz": ac.i[o.nome], "z": zero, "y": zero, "abre": 0.0, "se_livre": True} for o in raizes if ac.i[o.nome] not in ja]
            k_rot, k_tr, k_resp = 0.7, 1.0, 0.4              # artropode nao tem peito que respira: o corpo oscila sobre as patas
    hr, hp, hg, hc1, hc2 = _harmonicos(dur, [float(c.get("respira_s", 3.6)), 6.0, 7.0, 3.0, 2.2])
    f0 = float(c.get("fase", 0.0))
    resp = _respiro(hr * fase_t + f0)
    peso = np.sin(2 * np.pi * (hp * fase_t + f0 + 0.13))
    peso_atr = np.sin(2 * np.pi * (hp * fase_t + f0 + 0.13 - 0.07))
    giro = np.sin(2 * np.pi * (hg * fase_t + f0 + 0.37))
    antes_c = ac.E[:, kc, :].copy()
    ac.somar(kc, "cima", float(c.get("respira_H", 0.012)) * g * k_tr * k_resp * resp)
    ac.somar(kc, "frente", -1.3 * g * k_rot * resp)
    ac.somar(kc, "direita", float(c.get("peso_H", 0.010)) * g * k_tr * peso)
    ac.somar(kc, "tombar_direita", 0.9 * g * k_rot * peso_atr)
    ac.somar(kc, "esquerda", 0.8 * g * k_rot * giro)
    if c.get("escala"):                                     # peito cresce: so em pele (GLB); em Parts a escala nao e tocada
        e = 1 + 0.03 * g * resp
        ac.S[:, kc, 0] *= e
        ac.S[:, kc, 2] *= e
    d_corpo = ac.E[:, kc, :] - antes_c
    # cabecas: compensam 60% do corpo com 0,1 s de atraso e balancam sozinhas em dois periodos
    cabecas = [o for o in m.ossos if o.papel == "cabeca"]
    for j, o in enumerate(cabecas):
        k = ac.i[o.nome]
        fj = f0 + 0.334 * j                                  # vizinhas defasadas de 2,1 rad
        ac.E[:, k, :] += -0.6 * np.roll(d_corpo, 3, axis=0)
        ac.somar(k, "frente", 1.1 * g * np.sin(2 * np.pi * (hc1 * fase_t + fj + 0.2)))
        ac.somar(k, "esquerda", 1.8 * g * np.sin(2 * np.pi * (hc2 * fase_t + fj + 0.55)) * (0.6 + 0.4 * np.sin(2 * np.pi * (hp * fase_t + fj))))
        ac.somar(k, "tombar_direita", 0.7 * g * np.sin(2 * np.pi * (hg * fase_t + fj + 0.8)))
    for j, o in enumerate(o for o in m.ossos if o.papel == "mandibula"):
        ac.somar(ac.i[o.nome], "frente", 2.2 * g * np.maximum(-_respiro(hr * fase_t + f0 + 0.06 + 0.334 * j), 0) * 2)
    ac.vida = {"g": g, "fase": f0, "h1": max(1, int(round(dur / float(c.get("cauda_s", 4.0))))), "hp": hp,
               "cadeias": c.get("cadeias", "auto"), "dur": dur, "ganho": float(c.get("cadeias_ganho", 1.0))}


def _vida_cadeias(ac: _Acum, fase_t, antes: np.ndarray):
    """Onda viajante nas cadeias que ficaram sem camada: guinada que cresce para a ponta, atraso de 0,5 rad por elo,
    arfagem no dobro da frequencia e 90 graus defasada (a ponta desenha uma elipse) e uma segunda onda lenta."""
    v = ac.vida
    if not v or v["cadeias"] in (False, [], "nenhuma"):
        return
    g, f0, h1, hp = v["g"], v["fase"], v["h1"], v["hp"]
    for n_cad, (fam, fila) in enumerate(_cadeias_por_papel(ac.modelo)):
        if isinstance(v["cadeias"], list) and not any(fnmatch.fnmatchcase(fila[0], p) for p in v["cadeias"]):
            continue
        ks = [ac.i[n] for n in fila]
        if any(k in ac.dirigidos or np.abs(ac.E[:, k] - antes[:, k]).max() > 1e-9 for k in ks):
            continue
        lat, ver, sv = _canais_da_cadeia(_direcao(ac.modelo, fila))
        ganho = PAPEIS_ONDA[fam] * g * v.get("ganho", 1.0) * (0.85 if fila[0].endswith("_E") else 1.0)
        h = h1 * (3 if fam == "antena" else 1)               # antena varre mais depressa
        fc = f0 + 0.29 * n_cad + (0.37 if fila[0].endswith("_E") else 0.0)
        n = len(fila)
        base, passo = (1.7, 1.1) if n > 2 else (3.0, 2.0)    # cadeia curta: cada elo precisa girar mais
        for j, k in enumerate(ks):
            a = (base + passo * j) * ganho
            x = 2 * np.pi * (h * fase_t + fc - 0.0796 * j)
            lento = np.sin(2 * np.pi * (hp * fase_t + fc + 0.21 - 0.05 * j))
            ac.somar(k, lat, a * (0.8 * np.sin(x) + 0.6 * lento))
            ac.somar(k, ver, sv * 0.45 * a * np.sin(2 * x + np.pi / 2))
            ac.dirigidos.add(k)                              # ja tem onda propria: o seguimento automatico nao soma


def _resposta(tau, freq_hz: float, amort: float):
    """Tranco amortecido: comeca em zero, afunda, volta passando do ponto e assenta. Pico = 1."""
    pico_t = np.arctan(2 * np.pi * freq_hz / amort) / (2 * np.pi * freq_hz)
    pico = np.exp(-amort * pico_t) * np.sin(2 * np.pi * freq_hz * pico_t)
    return np.where(tau >= 0, np.exp(-amort * np.maximum(tau, 0)) * np.sin(2 * np.pi * freq_hz * np.maximum(tau, 0)), 0.0) / pico


def _impacto(ac: _Acum, c: dict, fase_t, dur: float, laco: bool):
    """Peso: cada pisada (ou cada instante de "em_t") afunda o corpo e ele volta oscilando; a cabeca e as cadeias
    sentem o tranco depois, elo a elo. No andar, o corpo ainda vai para o lado dos pes de apoio.
    Ponha esta camada DEPOIS de "passos"."""
    m = ac.modelo
    raiz = next(o.nome for o in m.ossos if o.pai is None)
    corpo = c.get("corpo") or next((o.nome for o in m.ossos if o.papel == "corpo" and o.pai == raiz), None) \
        or next((o.nome for o in m.ossos if o.papel == "corpo"), None)
    if corpo is None:
        raise ValueError('a camada "impacto" precisa de um osso com "papel": "corpo" (ou diga qual em "corpo").')
    kc = ac.ossos(corpo)[0]
    centro = np.array(m.osso(ac.nomes[kc]).pivo, float)
    golpes = [(float(t), None) for t in c.get("em_t", [])] or list(ac.pisadas)
    if not golpes:
        raise ValueError('"impacto" nao achou pisadas: ponha a camada depois de "passos" ou de os instantes em "em_t": [0.5].')
    intervalo = dur / len(golpes)
    f = float(c.get("freq_hz", min(4.0, max(1.4, 0.8 / intervalo))))
    am = float(c.get("amort", 2.6 * f))
    afunda = float(c.get("afunda_H", 0.015))
    graus = float(c.get("graus", 1.0))
    atraso = float(c.get("atraso_por_elo_s", 0.05))
    t = fase_t * dur
    cadeias = [] if c.get("cadeias") in (False, []) else _cadeias_por_papel(m)
    cabecas = [ac.i[o.nome] for o in m.ossos if o.papel == "cabeca"]

    def bruta(atr, pesos):
        r = np.zeros(ac.n)
        for (fr, _), w in zip(golpes, pesos):
            for volta in range(4 if laco else 1):
                r += w * _resposta(t - fr * dur + volta * dur - atr, f, am)
        return r - (r.mean() if laco else 0.0)
    # pisadas muito juntas somam e achatam: a amplitude pedida vale para o pico da soma, nao para cada pisada
    pico0 = np.abs(bruta(0.0, np.ones(len(golpes)))).max()
    k_norm = 1.0 / pico0 if pico0 > 1e-6 and len(golpes) > 1 else 1.0

    def soma(atr, pesos):
        return k_norm * bruta(atr, pesos)
    frente_pe, lado_pe, pesos = [], [], []
    for fr, k in golpes:
        if k is None:
            frente_pe.append(0.0); lado_pe.append(0.0); pesos.append(1.0)
            continue
        pv = np.array(m.osso(ac.nomes[k]).pivo, float)
        na_frente = pv[2] < centro[2] - 1e-6
        frente_pe.append(1.0 if na_frente else -1.0 if pv[2] > centro[2] + 1e-6 else 0.0)
        lado_pe.append(float(np.sign(pv[0] - centro[0])))
        pesos.append(0.55 if na_frente else 0.4 if pv[2] > centro[2] + 1e-6 else 0.5)
    pesos = np.array(pesos) / max(pesos)
    r0 = soma(0.0, pesos)
    ac.somar(kc, "baixo", afunda * r0)
    ac.somar(kc, "frente", graus * soma(0.0, pesos * np.array(frente_pe)))          # pata da frente: o focinho desce
    ac.somar(kc, "tombar_direita", 0.7 * graus * soma(0.0, pesos * np.array(lado_pe)))
    for k in cabecas:
        ac.somar(k, "frente", 1.2 * graus * soma(0.06, pesos))
    for fam, fila in cadeias:
        _, ver, sv = _canais_da_cadeia(_direcao(m, fila))
        for j, nome in enumerate(fila):
            ac.somar(ac.i[nome], ver, sv * 1.5 * graus * (1 + 0.25 * j) * soma(atraso * (j + 1), pesos))
    # peso para o lado do apoio (so com passos): centro dos pes no chao, alisado
    lateral = float(c.get("lateral_H", 0.015))
    if ac.apoios and lateral:
        num, den = np.zeros(ac.n), np.zeros(ac.n)
        for k, no_chao in ac.apoios:
            lado = float(np.sign(m.osso(ac.nomes[k]).pivo[0] - centro[0]))
            num += lado * no_chao
            den += no_chao
        alvo = num / np.maximum(den, 1e-6)
        alvo = _mola(alvo, max(0.8, 0.5 / intervalo), 1.0, laco)                    # mola critica: sem degrau
        ac.somar(kc, "direita", lateral * alvo)
        ac.somar(kc, "tombar_direita", float(c.get("rolar", 1.2)) * alvo)


# --------------------------------------------------------------------------- patas de artropode (pe travado no mundo)

def ponta_da_perna(modelo: Modelo, osso: str) -> np.ndarray:
    """Onde a perna toca o chao, em coordenadas de autoria. Perna em pe (sem giro de repouso): o centro da sola.
    Pata girada no repouso (aranha, inseto): o centro da face mais longe do pivo, no eixo comprido."""
    piv = np.array(modelo.osso(osso).pivo, float)
    cx = [p.grade.caixa() for p in modelo.pecas if p.osso == osso and p.grade.n_voxels()]
    if not cx:
        return piv
    mn, mx = np.min([c[0] for c in cx], 0), np.max([c[1] for c in cx], 0)
    o, girada = modelo.osso(osso), False
    while o is not None and _familia(o.papel) in ("perna", "pe"):
        girada = girada or tuple(np.round(o.repouso, 6)) != (0.0, 0.0, 0.0, 1.0)
        o = modelo.osso(o.pai) if o.pai else None
    if not girada:
        return np.array([piv[0], mn[1], piv[2]])           # reto abaixo do pivo: a sola
    e = int(np.argmax(mx - mn))
    pt = (mn + mx) / 2
    pt[e] = mn[e] if abs(mn[e] - piv[e]) > abs(mx[e] - piv[e]) else mx[e]
    return pt


def cadeia_da_perna(modelo: Modelo, raiz: str) -> list[str]:
    """Do osso dado ate a ponta, seguindo os filhos que sao perna ou pe."""
    fila = [raiz]
    while True:
        prox = next((o for o in modelo.ossos if o.pai == fila[-1] and _familia(o.papel) in ("perna", "pe")), None)
        if prox is None:
            return fila
        fila.append(prox.nome)


def _R4(e) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = quat_para_matriz(quat_semantico(e[0], e[1], e[2]))
    return m


def _local(ac: _Acum, k: int, q: int) -> np.ndarray:
    """Matriz local do osso k no quadro q, com tudo o que as camadas ja somaram."""
    o = ac.modelo.ossos[k]
    e = ac.E[q, k]
    rot = quat_semantico(e[0], e[1], e[2]) if e.any() else np.array([0, 0, 0, 1.0])
    if k in ac.Q:
        rot = quat_mul(rot, ac.Q[k][q])
    if k in ac.ABS:
        rot = ac.ABS[k][q]
    piv = np.array(o.pivo, float)
    return matriz_translacao(piv) @ matriz_trs((0, 0, 0), o.repouso) @ matriz_trs(ac.T[q, k], rot) @ matriz_translacao(-piv)


def _mundo(ac: _Acum, k: int | None, q: int | None) -> np.ndarray:
    """Matriz no mundo do osso k (q = None: pose de repouso)."""
    M = np.eye(4)
    fila = []
    while k is not None:
        fila.append(k)
        pai = ac.modelo.ossos[k].pai
        k = ac.i[pai] if pai else None
    for kk in reversed(fila):
        if q is None:
            o = ac.modelo.ossos[kk]
            piv = np.array(o.pivo, float)
            M = M @ matriz_translacao(piv) @ matriz_trs((0, 0, 0), o.repouso) @ matriz_translacao(-piv)
        else:
            M = M @ _local(ac, kk, q)
    return M


def _resolver_patas(ac: _Acum, laco: bool):
    """Pata de artropode: a ponta fica PARADA NO MUNDO durante o apoio, mesmo com o corpo subindo, girando e
    ondulando; no balanco ela vai pelo ar ate o proximo ponto. Resolve os angulos de todos os ossos da pata por
    minimos quadrados amortecidos, partindo do quadro anterior (sem pulo) e puxando de leve para o repouso."""
    m = ac.modelo
    if not ac.patas:
        return
    for req in ac.patas:
        nomes = cadeia_da_perna(m, ac.nomes[req["raiz"]])
        ks = [ac.i[n] for n in nomes]
        if req.get("se_livre") and any(np.abs(ac.E[:, k]).max() > 1e-9 or k in ac.dirigidos for k in ks):
            continue                                         # outra camada ja mexe nesta pata (um toque, um ataque)
        ossos = [m.osso(n) for n in nomes]
        A = [matriz_translacao(np.array(o.pivo, float)) @ matriz_trs((0, 0, 0), o.repouso) for o in ossos]
        B = [matriz_translacao(-np.array(o.pivo, float)) for o in ossos]
        ponta = np.append(ponta_da_perna(m, nomes[-1]), 1.0)
        kp = ac.i[ossos[0].pai] if ossos[0].pai else None
        base = (_mundo(ac, ks[-1], None) @ ponta)[:3]        # onde a ponta pisa em repouso
        if not m.meta.get("flutua") and abs(base[1]) < 0.45 * sum(
                float(np.linalg.norm(np.array(a.pivo, float) - np.array(b.pivo, float))) for a, b in zip(ossos[:-1], ossos[1:])) + 1.0:
            base[1] = 0.0                                    # a pata pisa no CHAO, mesmo que a ficha a tenha deixado no ar
        lado = float(np.sign(base[0])) or 1.0
        alvo = base[None, :] + np.stack([lado * req["abre"] * np.ones(ac.n), req["y"], -req["z"]], axis=1)
        if req.get("chao") is not None and kp is not None:
            # o ponto de pisada acompanha o corpo: em cada apoio a pata crava onde ela estaria, em repouso, no MEIO do
            # apoio (o corpo de uma centopeia ondula; o de uma aranha gira). No balanco, vai de um ponto ao outro.
            rel = np.linalg.inv(_mundo(ac, kp, None)) @ np.append(base, 1.0)
            chao = np.asarray(req["chao"], bool)
            janelas = []
            for q0 in [q for q in range(ac.n) if chao[q] and not chao[q - 1 if (laco or q) else 0] or (q == 0 and chao[0] and not laco)]:
                idx, q = [], q0
                while len(idx) < ac.n and (q < ac.n or laco) and chao[q % ac.n]:
                    idx.append(q % ac.n)
                    q += 1
                if idx:
                    qm = idx[len(idx) // 2]
                    nat = (_mundo(ac, kp, qm) @ rel)[:3]
                    janelas.append((idx, np.array([nat[0] - base[0], 0.0, nat[2] - base[2]])))
            if janelas:
                des = np.zeros((ac.n, 3))
                dono = -np.ones(ac.n, int)
                for j, (idx, off) in enumerate(janelas):
                    des[idx] = off
                    dono[idx] = j
                for q in range(ac.n):
                    if dono[q] >= 0:
                        continue
                    a_, b_ = q, q                                # apoio anterior e proximo
                    while dono[a_ % ac.n] < 0 and q - a_ < ac.n and (laco or a_ > 0):
                        a_ -= 1
                    while dono[b_ % ac.n] < 0 and b_ - q < ac.n and (laco or b_ < ac.n - 1):
                        b_ += 1
                    oa = janelas[dono[a_ % ac.n]][1] if dono[a_ % ac.n] >= 0 else None
                    ob = janelas[dono[b_ % ac.n]][1] if dono[b_ % ac.n] >= 0 else None
                    oa, ob = (oa if oa is not None else ob), (ob if ob is not None else oa)
                    des[q] = oa + (ob - oa) * curva("suave", float(req["s"][q]))
                alvo = alvo + des
        nb = len(ks)
        peso = np.ones(nb * 3)
        peso[1::3][1:] = 0.35                                # guinada so na coxa; nos outros ossos vale pouco
        peso[0], peso[2] = 0.35, 0.6                         # a coxa quase nao arfa
        W = np.diag(peso)

        def fk(Mp, th):
            M = Mp
            for i in range(nb):
                M = M @ A[i] @ _R4(th[3 * i:3 * i + 3]) @ B[i]
            return (M @ ponta)[:3]
        th = np.zeros(nb * 3)
        sol = np.zeros((ac.n, nb * 3))
        pior = 0.0
        for volta in range(2 if laco else 1):
            for q in range(ac.n):
                Mp = _mundo(ac, kp, q) if kp is not None else np.eye(4)
                for it in range(14):
                    p0 = fk(Mp, th)
                    err = alvo[q] - p0
                    if np.linalg.norm(err) < 2e-3:
                        break
                    J = np.zeros((3, nb * 3))
                    for j in range(nb * 3):
                        d = th.copy()
                        d[j] += 0.5
                        J[:, j] = (fk(Mp, d) - p0) / 0.5
                    JW = J @ W
                    Jp = W @ JW.T @ np.linalg.inv(JW @ JW.T + 1e-5 * np.eye(3))
                    passo = Jp @ err
                    mx = np.abs(passo).max()
                    if mx > 20:
                        passo *= 20 / mx
                    th = th + passo + (np.eye(nb * 3) - Jp @ J) @ (-0.08 * th)
                sol[q] = th
                if volta == (1 if laco else 0):
                    pior = max(pior, float(np.linalg.norm(alvo[q] - fk(Mp, th))))
        for i, k in enumerate(ks):
            ac.E[:, k, :] = sol[:, 3 * i:3 * i + 3]
            ac.dirigidos.add(k)
        ac.erro_patas = max(getattr(ac, "erro_patas", 0.0), pior)
        if pior > getattr(ac, "pior_pata", ("", 0.0))[1]:
            ac.pior_pata = (nomes[0], pior)


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
            elif tipo == "soltar_bracos":
                _soltar_bracos(ac, c, fase_t)
            elif tipo == "ondular":
                _ondular(ac, c, fase_t)
            elif tipo == "vida":
                _vida(ac, c, fase_t, dur)
            elif tipo == "impacto":
                _impacto(ac, c, fase_t, dur, laco)
            else:
                raise ValueError(f'tipo de camada "{tipo}" nao existe; use um de {list(TIPOS)}')
        except (KeyError, ValueError) as e:
            raise ValueError(f'clipe "{receita.get("nome")}", camada {i + 1} ({tipo}): {e}') from None
    _pernas_acompanham(ac)
    _vida_cadeias(ac, fase_t, antes)
    _seguir_cadeias(ac, laco, antes)
    _resolver_patas(ac, laco)
    _resolver_golpes(ac)
    cl = Clipe.vazio(receita["nome"], dur, ac.nomes, laco=laco)
    cl.trans[:] = ac.T
    for q in range(n):
        for k in range(len(ac.nomes)):
            e = ac.E[q, k]
            qq = quat_semantico(e[0], e[1], e[2]) if e.any() else np.array([0, 0, 0, 1.0])
            if k in ac.Q:
                qq = quat_mul(qq, ac.Q[k][q])
            if k in ac.ABS:
                qq = ac.ABS[k][q]
            cl.rot[q, k] = qq
    if not np.allclose(ac.S, 1.0):
        cl.escala = ac.S.astype(np.float32)
    cl.vel_raiz = float(receita.get("vel_raiz", ac.vel))
    cl.marcadores = sorted([(nm, round(float(t), 3)) for nm, t in ac.marc] +
                           [(nm, round(float(fr) * dur, 3)) for nm, fr in receita.get("marcadores", [])],
                           key=lambda m: m[1])
    cl.meta = {"acerto": receita.get("acerto")} if receita.get("acerto") else {}
    if receita.get("largar_item"):
        cl.meta["largar_item"] = True
    if ac.patas:
        cl.meta["erro_patas_studs"] = round(float(getattr(ac, "erro_patas", 0.0)), 4)
        cl.meta["pior_pata"] = getattr(ac, "pior_pata", ("", 0.0))[0]
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
