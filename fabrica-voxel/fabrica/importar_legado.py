"""Roda os modelos da forja antiga (legado/forja_alta, codigo do dono) e entrega cada um como Modelo da fabrica.

A forja antiga esculpe e pinta as pecas em codigo (campos de distancia, escamas, faixas) e anima por uma funcao
pose(modelo, clipe, t). Aqui nada e redesenhado: as grades de voxel e as cores saem como estao, os pivos viram ossos e
cada pose e amostrada a 30 quadros por segundo e assada em Clipe. Dai em diante vale a esteira normal: auditoria,
folha, GLB, .vox e os modulos Luau que o Roblox toca (a forja antiga nao gerava Luau para estes modelos).

Ficha: {"id": "monstro.forja_hidra_adulta", "tipo": "monstro", "tier": 9, "tier_manual": true,
        "legado": {"modulo": "hidra_adulta", "construtor": "hidra", "pose": "hidra_adulta.pose", "clipes": [...]}}
"""
from __future__ import annotations

import importlib
import sys

import numpy as np

from .nucleo.contrato import FPS, Clipe, Grade, Material, Modelo, Osso, Peca, matriz_para_quat
from .registro import RAIZ

PASTA = RAIZ / "legado" / "forja_alta"
NOMES = {"parado": "Parado", "andar": "Andar", "mover": "Andar", "ataque": "Ataque", "bote": "Ataque", "mordida": "Ataque",
         "morte": "Morte", "susto": "Susto", "rugido": "Rugido", "raio": "Raio", "pisao": "Pisao"}
PAPEL = (("mandib", "mandibula"), ("cabec", "cabeca"), ("cranio", "cabeca"), ("cauda", "cauda"), ("perna", "perna"), ("coxa", "perna"),
         ("canela", "pe"), ("pe_", "pe"), ("braco", "braco"), ("mao", "mao"), ("asa", "asa"), ("adorno", "adorno"), ("vertebra", "segmento"))


def _mod(nome):
    if str(PASTA) not in sys.path:
        sys.path.insert(0, str(PASTA))
    return importlib.import_module(nome)


def _papel(nome: str) -> str:
    n = nome.lower()
    for chave, p in PAPEL:
        if chave in n:
            return p
    return "corpo"


def _pose(fn, m, clipe, t):
    T = fn(m, clipe, t)
    return T[0] if isinstance(T, tuple) and isinstance(T[0], dict) else T


def _periodo(fn, m, clipe, pecas, laco: bool, dur) -> tuple[float, np.ndarray]:
    """Para clipe em laco sem duracao declarada: acha o menor periodo em que a pose volta ao comeco. Devolve tambem a
    velocidade de deriva da raiz (a forja antiga anda de verdade no 'mover'; a fabrica quer o laco no lugar)."""
    raiz = next(n for n, p in pecas.items() if getattr(p, "pai", None) is None)
    T0 = _pose(fn, m, clipe, 0.0)

    def dif(d):
        # mede logo ANTES do fim do ciclo: quem anda de verdade (slime que pula, esqueleto que avanca) volta ao
        # ponto de partida no instante exato do laco, e a deriva sumiria da conta
        fim = d * 0.999
        Tf = _pose(fn, m, clipe, fim)
        deriva = (Tf[raiz][1] - T0[raiz][1]) / fim
        Td = Tf
        e = 0.0
        for n in pecas:
            e = max(e, float(np.abs(Td[n][0] - T0[n][0]).max()), float(np.abs((Td[n][1] - deriva * fim) - T0[n][1]).max()))
        return e, deriva

    if dur:
        return float(dur), (dif(float(dur))[1] if laco else np.zeros(3))
    if not laco:
        return 1.2, np.zeros(3)
    melhor = None
    for d in np.arange(0.6, 8.05, 0.1):
        e, deriva = dif(float(d))
        if melhor is None or e < melhor[0] - 1e-6:
            melhor = (e, float(d), deriva)
        if e < 2e-3:
            break
    return melhor[1], melhor[2]


def montar_legado(ficha: dict) -> Modelo:
    L = ficha["legado"]
    mod = _mod(L["modulo"])
    args = L.get("args", [])
    m = getattr(mod, L["construtor"])(*args)
    pecas = m["pecas"]
    if L.get("ligar_soltos"):                                  # relicario: tendao liga o que ficaria solto
        for p in pecas.values():
            mod.ligar_soltos(p, mod.K[L["ligar_soltos"]])
    for p in pecas.values():
        p.limpar_soltos()
    pecas = {n: p for n, p in pecas.items() if (p.g > 0).any()}
    m["pecas"] = pecas
    if hasattr(_mod("voxforja"), "faces") and L.get("faces", True):
        try:
            m["faces"] = {n: _mod("voxforja").faces(p) for n, p in pecas.items()}
        except Exception:                                      # so e usado pelo render antigo
            pass
    RGB = np.asarray(mod.RGB, float)
    usados = sorted({int(c) for p in pecas.values() for c in np.unique(p.g[p.g > 0])})
    mapa = np.zeros(int(max(usados)) + 1, np.uint16)
    cores = []
    for k, c in enumerate(usados, 1):
        mapa[c] = k
        cores.append("#%02X%02X%02X" % tuple(int(round(float(np.clip(v, 0, 1)) * 255)) for v in RGB[c]))
    modelo = Modelo(id=ficha["id"].split(".", 1)[-1], nome=ficha.get("nome", m.get("nome", ficha["id"])))
    modelo.cores = cores
    modelo.cores_brilho = {int(mapa[c]) for c in getattr(mod, "EMIS", set()) if c in usados}
    modelo.materiais = [Material(nome="legado", rampa="bone", perfil="chapado")]
    modelo.ossos.append(Osso("Raiz", None, (0.0, 0.0, 0.0), "raiz"))
    for n, p in pecas.items():
        g = Grade(v=float(p.vs), origem=np.asarray(p.origem, float), mat=(p.g > 0).astype(np.uint8), cor=mapa[p.g].astype(np.uint16))
        modelo.pecas.append(Peca(nome=n, osso=n, grade=g, escala_animada=True))
        pai = getattr(p, "pai", None)
        modelo.ossos.append(Osso(n, pai if pai in pecas else "Raiz", tuple(float(x) for x in p.pivo), _papel(n)))
    from .nucleo.contrato import ordem_topologica
    modelo.ossos[:] = ordem_topologica(modelo.ossos)
    modelo.meta.update({"tier": int(ficha.get("tier", 1)), "legado": L["modulo"], "voxel_misto_de_origem": True,
                        **dict(ficha.get("meta", {}))})
    # ---- clipes: amostra a pose antiga e converte transformacao do mundo em translacao e rotacao locais do osso
    nome_pose = L.get("pose")
    if nome_pose:
        pm, pf = nome_pose.rsplit(".", 1)
        fn = getattr(_mod(pm), pf)
        nomes = [o.nome for o in modelo.ossos]
        pai = {o.nome: o.pai for o in modelo.ossos}
        piv = {o.nome: np.array(o.pivo) for o in modelo.ossos}
        usados_n = set()
        for c in L.get("clipes", []):
            cn, dur, laco = c["nome"], c.get("duracao"), bool(c.get("laco", False))
            dur, deriva = _periodo(fn, m, cn, pecas, laco, dur)
            canon = NOMES.get(cn, cn.capitalize())
            if canon in usados_n:
                canon = cn.capitalize()
            usados_n.add(canon)
            cl = Clipe.vazio(canon, dur, nomes, laco=laco)
            esc = np.ones((cl.n_quadros, len(nomes), 3), np.float32)
            def amostra(t):
                """Pose antiga no instante t -> (rotacao, translacao, escala) locais de cada osso."""
                T = _pose(fn, m, cn, t)
                W = {"Raiz": (np.eye(3), np.zeros(3))}
                for n in pecas:
                    W[n] = (np.asarray(T[n][0], float), np.asarray(T[n][1], float) - deriva * t)
                r_, t_, e_ = np.tile(np.array([0, 0, 0, 1.0]), (len(nomes), 1)), np.zeros((len(nomes), 3)), np.ones((len(nomes), 3))
                for k, n in enumerate(nomes):
                    if n == "Raiz":
                        continue
                    Rp, tp = W[pai[n]]
                    Rb, tb = W[n]
                    A = np.linalg.inv(Rp) @ Rb                      # rotacao (e escala) local
                    s = np.linalg.norm(A, axis=0)
                    s = np.where(s < 1e-6, 1.0, s)
                    Rl = A / s
                    if np.linalg.det(Rl) < 0:
                        Rl[:, 0] *= -1
                        s[0] *= -1
                    r_[k] = matriz_para_quat(Rl)
                    e_[k] = s
                    pos = Rb @ piv[n] + tb                          # onde o pivo esta no mundo
                    loc = np.linalg.inv(Rp) @ (pos - tp)            # no espaco do pai
                    t_[k] = loc - piv[n]
                return r_, t_, e_
            for q in range(cl.n_quadros):
                cl.rot[q], cl.trans[q], esc[q] = amostra(q / FPS)
            if laco and cl.n_quadros > 12:
                # o laco antigo pode nao fechar (ondas de periodos que nao dividem a duracao): nos ultimos quadros,
                # mistura com a pose de "antes do comeco" (t - duracao). No fim do laco a pose e exatamente a do quadro 0.
                rf, tf, ef = amostra(cl.n_quadros / FPS)
                fecha = max(float(np.abs(tf - cl.trans[0]).max()),
                            float(2 * np.degrees(np.arccos(np.clip(np.abs((rf * cl.rot[0]).sum(-1)), 0, 1))).max()) / 30.0)
                passo = max(float(np.abs(cl.trans[1] - cl.trans[0]).max()),
                            float(2 * np.degrees(np.arccos(np.clip(np.abs((cl.rot[1] * cl.rot[0]).sum(-1)), 0, 1))).max()) / 30.0, 1e-4)
                if fecha > 2.0 * passo:
                    guarda = (cl.rot.copy(), cl.trans.copy(), esc.copy())
                    nb = int(min(cl.n_quadros // 3, FPS * 1.5))
                    for i in range(nb):
                        q = cl.n_quadros - nb + i
                        w = (i + 1) / (nb + 1)
                        w = w * w * w * (w * (w * 6 - 15) + 10)
                        r2, t2, e2 = amostra(q / FPS - cl.n_quadros / FPS)
                        for k in range(len(nomes)):
                            a_, b_ = cl.rot[q, k].astype(float), r2[k]
                            if float(np.dot(a_, b_)) < 0:
                                b_ = -b_
                            qq = a_ + (b_ - a_) * w
                            cl.rot[q, k] = qq / np.linalg.norm(qq)
                        cl.trans[q] = cl.trans[q] + (t2 - cl.trans[q]) * w
                        esc[q] = esc[q] + (e2 - esc[q]) * w
                    # so vale se melhorou: a pose antiga pode nao estar definida antes de t = 0 (um pulo, por exemplo)
                    emenda = float(np.abs(cl.trans[0] - cl.trans[-1]).max())
                    antes_ = float(np.abs(guarda[1][0] - guarda[1][-1]).max())
                    salto_meio = float(np.abs(np.diff(cl.trans[-nb - 1:], axis=0)).max())
                    if emenda > antes_ or salto_meio > 3 * max(float(np.abs(np.diff(guarda[1], axis=0)).max()), 1e-4):
                        cl.rot[:], cl.trans[:], esc[:] = guarda
                    else:
                        modelo.meta.setdefault("lacos_fechados_por_mistura", []).append(canon)
            for k in range(len(nomes)):                             # continuidade do quaternion
                for q in range(1, cl.n_quadros):
                    if float(np.dot(cl.rot[q, k], cl.rot[q - 1, k])) < 0:
                        cl.rot[q, k] = -cl.rot[q, k]
            if np.abs(esc - 1).max() > 1e-4:
                cl.escala = esc
            cl.vel_raiz = float(np.linalg.norm(deriva))
            cl.marcadores = [(nm, round(float(fr) * dur, 3)) for nm, fr in c.get("marcadores", [])]
            modelo.clipes[canon] = cl
    return modelo
