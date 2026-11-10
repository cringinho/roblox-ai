"""Escada de tier: T1 e simples porque e fraco; T10 e grande e complexo porque e o topo.

A mesma ficha de monstro sobe de tier sem ser redesenhada. `elevar(ficha, tier)`:
1. AUMENTA as formas (mais voxels do mesmo tamanho, nunca voxel maior);
2. MULTIPLICA o que se repete (mais dentes, garras e espinhos, em vez de dentes maiores);
3. ARTICULA mais (cauda, pescoco e asa ganham segmentos; perna e braco ganham o terceiro osso a partir do T6);
4. ORNAMENTA (placas no dorso a partir do T4, nas costas a partir do T7, espinhos de coroa a partir do T9).
O portao P1 "detalhe_minimo" cobra o minimo de voxels e de ossos do tier.

Referencia dos numeros: a Forja Alta do dono (T1-T2 em blocos simples; elite com 6 a 12 mil voxels e 32 a 43 ossos).
"""
from __future__ import annotations

import copy

# tier: (voxels minimos, ossos minimos sem contar a Raiz, escala linear das formas)
TABELA = {1: (1000, 8, 1.00), 2: (1500, 10, 1.15), 3: (2200, 12, 1.30), 4: (3200, 16, 1.48), 5: (4500, 20, 1.66),
          6: (6000, 24, 1.83), 7: (8000, 28, 2.02), 8: (10000, 32, 2.18), 9: (13000, 36, 2.38), 10: (16000, 40, 2.55)}
MEMBROS = ("joelho", "reverso", "cotovelo")
CADEIA_LIVRE = ("cauda", "pescoco", "haste", "segmento", "pano", "asa", "antena", "lingua", "folha", "raiz_planta", "barbatana")


def minimos(tier: int) -> dict:
    t = max(1, min(10, int(tier or 1)))
    return {"voxels_min": TABELA[t][0], "ossos_min": TABELA[t][1]}


def _d(desloc, k):
    if not desloc or k == 1.0:
        return desloc
    return {n: (round(v * k * 2) / 2 if isinstance(v, (int, float)) else v) for n, v in desloc.items()}


def _vetor(d):
    """Deslocamento com nomes -> (x, y, z): direita, cima e tras sao os sentidos positivos."""
    import numpy as np
    d = d or {}
    return np.array([d.get("direita", 0) - d.get("esquerda", 0), d.get("cima", 0) - d.get("baixo", 0), d.get("tras", 0) - d.get("frente", 0)], float)


def escalar_formas(pecas: list[dict], k: float, *, repetir: str = "tamanho") -> list[dict]:
    """GERAR, NAO DEFORMAR: as mesmas formas com as medidas multiplicadas por k e arredondadas para voxel inteiro.
    repetir = "tamanho": o que se repete cresce junto (item de mao no porte do heroi).
    repetir = "quantidade": o elemento repetido fica do mesmo tamanho e passa a ter mais copias (tier de monstro)."""
    if k == 1.0:
        return pecas
    out = copy.deepcopy(pecas)
    arte = max(1, int(k + 0.3))                         # estampa (olhos, boca) cresce em fator inteiro
    for p in out:
        for f in p.get("formas", []):
            rep = f.get("repetir") if isinstance(f.get("repetir"), dict) else None
            if rep and repetir == "quantidade":
                # mais copias do mesmo tamanho; a fileira continua centrada onde estava e cresce com o corpo
                n0 = int(rep["n"])
                n1 = max(n0, int(round((n0 - 1) * k)) + 1)
                ini, passo = _vetor(f.get("desloc")), _vetor(rep.get("passo"))
                centro = (ini + passo * (n0 - 1) / 2.0) * k
                novo = centro - passo * (n1 - 1) / 2.0
                rep["n"] = n1
                f["desloc"] = {"direita": round(float(novo[0]) * 2) / 2, "cima": round(float(novo[1]) * 2) / 2, "tras": round(float(novo[2]) * 2) / 2}
                continue
            if f.get("op") == "estampa" and isinstance(f.get("linhas"), list) and arte > 1:
                f["linhas"] = [("".join(c * arte for c in ln)) for ln in f["linhas"] for _ in range(arte)]
            if isinstance(f.get("tam"), list):
                f["tam"] = [max(1, int(round(t * k))) for t in f["tam"]]
            for campo in ("raio", "chanfro", "r0", "r1"):
                if isinstance(f.get(campo), (int, float)) and f[campo] >= 1:
                    f[campo] = max(1, int(round(f[campo] * k)))
            if f.get("desloc"):
                f["desloc"] = _d(f["desloc"], k)
            for campo in ("de", "ate"):
                if isinstance(f.get(campo), dict) and f[campo].get("desloc"):
                    f[campo]["desloc"] = _d(f[campo]["desloc"], k)
            if rep and rep.get("passo"):
                rep["passo"] = {n: max(1, int(round(v * k))) for n, v in rep["passo"].items()}
    return out


def elevar(ficha: dict, tier: int) -> dict:
    """Devolve a ficha no tier pedido. Tier 1 devolve a propria ficha."""
    tier = max(1, min(10, int(tier or 1)))
    if tier == 1:
        return ficha
    k = TABELA[tier][2]
    f = copy.deepcopy(ficha)
    f["pecas"] = escalar_formas(f["pecas"], k, repetir="quantidade")
    for campo in ("soquetes", "ossos"):
        for x in f.get(campo, []):
            if x.get("desloc"):
                x["desloc"] = _d(x["desloc"], k)
            if isinstance(x.get("pivo"), dict) and x["pivo"].get("desloc"):
                x["pivo"]["desloc"] = _d(x["pivo"]["desloc"], k)
            if x.get("junta"):
                x["junta"] = max(1, int(round(x["junta"] * min(k, 1.8))))
    # ---- mais articulacao
    mais = (tier - 1) // 3                               # T4: +1, T7: +2, T10: +3
    for o in f.get("ossos", []):
        seg = o.get("segmentos")
        dobra = o.get("dobra", {"perna": "joelho", "braco": "cotovelo"}.get(o.get("papel", ""), "livre"))
        if isinstance(seg, int):
            if dobra in MEMBROS:
                o["segmentos"] = [0.4, 0.38, 0.22] if tier >= 6 else seg      # terceiro osso: a pata ou a mao
            else:
                o["segmentos"] = seg + mais
        elif seg is None and not o.get("cadeia_com") and o.get("papel") in CADEIA_LIVRE and tier >= 4:
            o["segmentos"] = 2 + (1 if tier >= 8 else 0)
            o.setdefault("dobra", "livre")
            o.setdefault("ganho_seguir", 0.8)
        if o.get("segmentos"):
            o["segmentos_tolerante"] = True              # peca curta demais: usa menos segmentos em vez de reprovar
    # ---- ornamentos: placas no maior volume do corpo
    if tier >= 4:
        corpo = next((o["nome"] for o in f.get("ossos", []) if o.get("papel") == "corpo"), None)
        peca = next((p for p in f["pecas"] if p["nome"] == corpo), None)
        base = next((x for x in (peca or {}).get("formas", []) if x.get("nome") and x.get("op") == "caixa"), None)
        if peca is not None and base is not None:
            mat = next((m.get("nome") if isinstance(m, dict) else m for m in f.get("materiais", []) if (m.get("nome") if isinstance(m, dict) else m) == "detalhe"),
                       base.get("material"))
            lado = 2 + (tier >= 7) + (tier >= 10)
            borda = 2 + int(max(base.get("chanfro", 0), base.get("raio", 0)))        # ja escalado: placa fora do chanfro
            peca["formas"].append({"op": "placas", "em": base["nome"], "face": "topo", "tam": [lado + 1, 1, lado + 1], "vao": 1,
                                   "margem": borda, "material": mat})
            if tier >= 7:
                peca["formas"].append({"op": "placas", "em": base["nome"], "face": "tras", "tam": [lado, lado, 1], "vao": 2,
                                       "margem": borda, "material": mat})
            if tier >= 9:
                peca["formas"].append({"op": "placas", "em": base["nome"], "face": "topo", "tam": [1, 3, 1], "vao": 4,
                                       "margem": borda, "material": mat, "so_borda": True})
    f["tier"] = tier
    return f
