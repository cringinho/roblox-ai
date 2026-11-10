"""P3: registro da revisao visual (cartoes/revisao_visual.md).

A revisao fica em revisoes/<id>.json, presa ao hash da ficha: se a ficha mudar, a revisao deixa de valer.
"""
from __future__ import annotations

import json

from . import esteira
from .registro import RAIZ, ErroRegistro

PERGUNTAS = ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10")
BLOQUEIAM = ("A1", "A4", "A6")                  # um "nao" aqui reprova mesmo com nota P2 alta
LETRAS = {"s": "sim", "q": "quase", "n": "nao", "-": "pulou"}
PASTA = RAIZ / "revisoes"


def veredito(respostas: dict) -> str:
    v = list(respostas.values())
    if "nao" in v:
        return "volta"
    return "publicavel" if v.count("quase") <= 2 else "volta"


def registrar(ref: str, letras: str, por: str, reg, data: str = "") -> str:
    """letras: 10 caracteres na ordem A1..A10 (s = sim, q = quase, n = nao, - = pulou)."""
    letras = letras.strip().lower()
    if len(letras) != 10 or any(c not in LETRAS for c in letras):
        raise ErroRegistro('respostas: escreva 10 letras na ordem A1..A10, usando s (sim), q (quase), n (nao) ou - (pulou). '
                           'Exemplo: ssqsssss--')
    rel = esteira.construir(ref, registro=reg, data=data, imagens=False, exportar=False)
    if rel.get("status") != "aprovado":
        raise ErroRegistro(f'{ref}: P0, P1 e P2 precisam passar antes do P3. Rode: python -m fabrica construir {ref}')
    resp = {p: LETRAS[c] for p, c in zip(PERGUNTAS, letras)}
    v = veredito(resp)
    PASTA.mkdir(exist_ok=True)
    (PASTA / f'{rel["id"]}.json').write_text(json.dumps(
        {"id": rel["id"], "hash_ficha": rel["hash_ficha"], "por": por, "data": data, "respostas": resp, "veredito": v},
        indent=1, ensure_ascii=False), encoding="utf-8")
    ruins = [p for p, r in resp.items() if r == "nao"]
    if v == "publicavel":
        return f'{rel["id"]}: PUBLICAVEL (revisado por {por}).'
    aviso = f' {[p for p in ruins if p in BLOQUEIAM]} bloqueiam sempre.' if any(p in BLOQUEIAM for p in ruins) else ""
    return (f'{rel["id"]}: VOLTA PARA A FICHA. Reprovou em {ruins or "mais de dois quase"}.{aviso} '
            f'Veja o conserto por pergunta em cartoes/revisao_visual.md.')


def ler(idc: str, hash_ficha: str | None) -> dict | None:
    """Devolve a revisao se existir e ainda valer para esta ficha."""
    f = PASTA / f"{idc}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if d.get("hash_ficha") == hash_ficha else None


def publicavel(idc: str, hash_ficha: str | None) -> bool:
    d = ler(idc, hash_ficha)
    return bool(d and d.get("veredito") == "publicavel")
