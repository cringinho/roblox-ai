"""Registro: carrega fichas JSON, resolve heranca e parametros, e valida (P0) com mensagens que ensinam."""
from __future__ import annotations

import ast
import copy
import difflib
import json
import operator
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "registro"
IGNORAR = {"paletas", "config", "_esquemas"}

# Campos aceitos por tipo: nome -> (tipo python, obrigatorio, descricao)
_BASE = {
    "id": (str, True, 'identificador estavel "<tipo>.<nome>", ex.: "monstro.esporinho"'),
    "tipo": (str, True, "tipo da ficha"), "versao": (int, False, "sobe quando a ficha muda"),
    "nome": (str, False, "nome de exibicao"), "herda": (str, False, "id de outra ficha: so escreva o que muda"),
    "params": (dict, False, "valores dos parametros herdados"), "_ajuda": ((str, list, dict), False, "comentario livre"),
    "lore": (str, False, "uma linha de historia"), "meta": (dict, False, "dados de jogo livres"),
}
_MODELO = {
    **_BASE,
    "materiais": (list, True, 'nomes da tabela padrao ("ferro") ou {"nome", "como", "rampa", "perfil", "brilho", "tom"}'),
    "pecas": (list, True, 'lista de {"nome", "osso", "corte", "formas": [...]}'),
    "+pecas": (list, False, "acrescenta pecas as herdadas"),
    "ossos": (list, False, '{"nome", "pai", "pivo": {"em": ancora, "desloc": {...}}, "papel", "junta", "mola", "repouso": {"frente": graus}, '
                     '"segmentos": 2 (corta a peca em coxa e canela), "dobra": joelho|reverso|cotovelo|livre, "seguir_pai": {"modo", "ganho"}}'),
    "+ossos": (list, False, "acrescenta ossos aos herdados"),
    "soquetes": (list, False, '{"nome", "osso", "em": ancora, "desloc": {...}}'),
    "+soquetes": (list, False, "acrescenta soquetes"),
    "acabamentos": (list, False, '{"tipo": "musgo_em_cima" | "sangue_escorrido" | "ferrugem_nas_arestas" | "pintas" | "listras", "forca", "pecas"}'),
    "clipes": (list, False, 'receitas {"nome", "duracao", "laco", "camadas": [...]}'),
    "+clipes": (list, False, "acrescenta clipes aos herdados"),
    "+materiais": (list, False, "acrescenta materiais aos herdados"),
    "extras": (dict, False, "formas a mais por peca: {\"Cabeca\": [formas...]}"),
    "tempo_por_porte": (bool, False, "multiplica as duracoes por raiz de k (padrao true)"),
    "porte_k": ((int, float), False, "altura do quadril relativa ao heroi medio"),
    "altura_ref_H": ((int, float), False, "altura de referencia H, em studs, para as translacoes dos clipes"),
    "perfil_auditoria": (str, False, "monstro, heroi, item, prop ou estrutura (padrao: pelo tipo)"),
    "tier": (int, False, "1 a 10"), "elemento": (str, False, ""), "pegada_ladrilhos": (int, False, "1 = 1x1, 2 = 2x2"),
    "estilo_movimento": (str, False, "natural, pesado, eterio, manco, espasmodico, marionete, staccato"),
    "susto": (dict, False, "dados do susto na dungeon"), "arquetipo": (str, False, "id do arquetipo (atalho de herda)"),
    "slot": (str, False, "slot do item"), "pegada": (str, False, "classe de pegada do item de mao"),
    "parametros": (dict, False, 'declaracao de parametros: {"nome": {"padrao", "min", "max", "descricao"}}'),
    "armadilhas": (list, False, "avisos para quem usa o arquetipo"), "andadura": (dict, False, "descricao da locomocao"),
    "orcamento": (dict, False, "limites de voxels/triangulos"), "portes": (list, False, "portes permitidos"),
}
ESQUEMAS = {"modelo": _MODELO, "monstro": _MODELO, "item": _MODELO, "prop": _MODELO, "arquetipo": _MODELO, "npc": _MODELO,
            "golpe": {**_BASE, "pegada": (str, True, "classe de pegada"), "duracao_s": ((int, float), True, ""),
                      "plano_graus": ((int, float), True, ""), "arco": (dict, True, ""), "tempos": (list, False, ""),
                      "tronco": (dict, False, ""), "peso_pe_frente": ((int, float), False, ""), "rastro": (list, False, ""),
                      "acerto": (dict, False, "")}}
TIPOS_LIVRES = {"linhagem", "traco", "classe_corpo", "classe_cabeca", "aparencia", "conjunto", "estrutura", "clipe"}


class ErroRegistro(ValueError):
    pass


def _fundir(base: dict, novo: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in novo.items():
        if k.startswith("+") and isinstance(v, list):
            out[k[1:]] = list(out.get(k[1:], [])) + copy.deepcopy(v)
        elif isinstance(v, dict) and isinstance(out.get(k), dict) and k not in ("params",):
            out[k] = _fundir(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.USub: operator.neg}


def _calc(expr: str, params: dict):
    """Aritmetica segura com $parametros: "$comprimento * 2 + 1". Sem eval."""
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in params:
                raise ErroRegistro(f'parametro "${n.id}" nao declarado; existem: {sorted(params)}')
            return params[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("max", "min", "round", "int"):
            return {"max": max, "min": min, "round": round, "int": int}[n.func.id](*[ev(a) for a in n.args])
        raise ErroRegistro(f'expressao "{expr}" usa algo nao permitido; so numeros, $parametros e + - * / // max min round int')
    v = ev(ast.parse(expr.replace("$", ""), mode="eval").body)
    return int(v) if isinstance(v, float) and abs(v - round(v)) < 1e-9 else v


def _aplicar(obj, params: dict):
    if isinstance(obj, str) and "$" in obj:
        return _calc(obj, params)
    if isinstance(obj, list):
        return [_aplicar(x, params) for x in obj]
    if isinstance(obj, dict):
        return {k: _aplicar(v, params) for k, v in obj.items()}
    return obj


class Registro:
    def __init__(self, pasta: Path | str = PASTA):
        self.pasta = Path(pasta)
        self.fichas: dict[str, dict] = {}
        self.arquivo: dict[str, Path] = {}
        for arq in sorted(self.pasta.rglob("*.json")):
            if set(arq.relative_to(self.pasta).parts[:-1]) & IGNORAR:
                continue
            try:
                d = json.loads(arq.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise ErroRegistro(f"{arq}: JSON invalido na linha {e.lineno}, coluna {e.colno}: {e.msg}. "
                                   f"Confira virgulas e aspas nessa linha.") from None
            if "id" not in d:
                raise ErroRegistro(f'{arq}: falta o campo "id", ex.: "id": "monstro.{arq.stem}"')
            if d["id"] in self.fichas:
                raise ErroRegistro(f'id repetido "{d["id"]}" em {arq} e {self.arquivo[d["id"]]}')
            self.fichas[d["id"]] = d
            self.arquivo[d["id"]] = arq

    def achar(self, ref: str) -> str:
        """Aceita o id completo ou so o nome ("esporinho")."""
        if ref in self.fichas:
            return ref
        cand = [i for i in self.fichas if i.split(".", 1)[-1] == ref]
        if len(cand) == 1:
            return cand[0]
        perto = difflib.get_close_matches(ref, list(self.fichas) + [i.split(".", 1)[-1] for i in self.fichas], n=4, cutoff=0.5)
        raise ErroRegistro(f'ficha "{ref}" nao existe no registro.' + (f" Parecidas: {perto}." if perto else "") +
                           (f" Ambiguo entre {cand}: use o id completo." if len(cand) > 1 else "") +
                           ' Liste com: python -m fabrica listar')

    def listar(self, tipo: str | None = None) -> list[str]:
        return sorted(i for i, f in self.fichas.items() if tipo is None or f.get("tipo") == tipo)

    def resolver(self, ref: str, _pilha=()) -> dict:
        """Ficha final: heranca fundida e parametros aplicados."""
        i = self.achar(ref)
        if i in _pilha:
            raise ErroRegistro(f"heranca em ciclo: {' -> '.join(_pilha + (i,))}")
        f = self.fichas[i]
        pai = f.get("herda") or (f"arquetipo.{f['arquetipo']}" if f.get("arquetipo") and not f["arquetipo"].startswith("arquetipo.") else f.get("arquetipo"))
        if pai:
            base = self.resolver(pai, _pilha + (i,))
            decl = base.get("parametros", {})
            dados = {k: v for k, v in f.items() if k not in ("herda",)}
            out = _fundir({k: v for k, v in base.items() if k not in ("id", "nome", "tipo", "_ajuda", "lore", "params_resolvidos")}, dados)
            out["parametros"] = {**decl, **f.get("parametros", {})}
            out["_bruto_pai"] = base.get("_bruto", base)
        else:
            out = copy.deepcopy(f)
        if not _pilha:                          # so a ficha final aplica os parametros
            decl = out.get("parametros", {})
            vals = {k: v.get("padrao") for k, v in decl.items()}
            for k, v in (out.get("params") or {}).items():
                if k not in decl:
                    perto = difflib.get_close_matches(k, list(decl), n=3, cutoff=0.4)
                    raise ErroRegistro(f'{i}: parametro "{k}" nao existe' + (f"; voce quis dizer {perto}?" if perto else "") +
                                       f" Parametros aceitos: " + ", ".join(f'{n} ({d.get("min")} a {d.get("max")}, padrao {d.get("padrao")})' for n, d in decl.items()))
                d = decl[k]
                if isinstance(v, (int, float)) and ((d.get("min") is not None and v < d["min"]) or (d.get("max") is not None and v > d["max"])):
                    raise ErroRegistro(f'{i}: parametro "{k}" = {v} fora da faixa {d.get("min")} a {d.get("max")} (padrao {d.get("padrao")}).')
                vals[k] = v
            out.pop("_bruto_pai", None)
            extras = out.pop("extras", None)
            out = _aplicar(out, vals)
            if extras:
                for p in out.get("pecas", []):
                    if p["nome"] in extras:
                        p["formas"] = list(p.get("formas", [])) + _aplicar(extras[p["nome"]], vals)
                desconhecidas = set(extras) - {p["nome"] for p in out.get("pecas", [])}
                if desconhecidas:
                    raise ErroRegistro(f'{i}: "extras" cita pecas que nao existem: {sorted(desconhecidas)}. Pecas: {[p["nome"] for p in out.get("pecas", [])]}')
            out["params_resolvidos"] = vals
        return out

    def validar(self, ref: str) -> list[str]:
        """P0: devolve a lista de TODOS os erros (vazia = passou)."""
        erros = []
        try:
            f = self.resolver(ref)
        except ErroRegistro as e:
            return [str(e)]
        tipo = f.get("tipo")
        if tipo in TIPOS_LIVRES:
            return erros
        if tipo not in ESQUEMAS:
            return [f'{f.get("id")}: "tipo": "{tipo}" desconhecido; use um de {sorted(set(ESQUEMAS) | TIPOS_LIVRES)}']
        esq = ESQUEMAS[tipo]
        for k, v in f.items():
            if k in ("params_resolvidos", "parametros"):
                continue
            if k not in esq:
                perto = difflib.get_close_matches(k, list(esq), n=3, cutoff=0.5)
                erros.append(f'campo "{k}" nao existe em fichas do tipo {tipo}.' + (f" Voce quis dizer {perto}?" if perto else "") +
                             f' Veja os campos com: python -m fabrica explicar {tipo}')
            elif not isinstance(v, esq[k][0]):
                erros.append(f'campo "{k}" deveria ser {esq[k][0]}, veio {type(v).__name__}: {esq[k][2]}')
        for k, (_, obrig, desc) in esq.items():
            if obrig and k not in f and tipo != "arquetipo":
                erros.append(f'falta o campo obrigatorio "{k}": {desc}')
        ids = [p.get("nome") for p in f.get("pecas", []) if isinstance(p, dict)]
        if len(set(ids)) != len(ids):
            erros.append(f"pecas com nome repetido: {ids}")
        for c in f.get("clipes", []):
            if not isinstance(c, dict) or "nome" not in c or "duracao" not in c:
                erros.append(f'clipe sem "nome" ou "duracao": {str(c)[:80]}. Ex.: {{"nome": "Parado", "duracao": 4, "laco": true, "camadas": []}}')
        return erros


def explicar(tipo: str) -> str:
    if tipo not in ESQUEMAS:
        return f'tipo "{tipo}" desconhecido; tipos: {sorted(set(ESQUEMAS) | TIPOS_LIVRES)}'
    linhas = [f"Ficha do tipo {tipo}. Campos (* = obrigatorio):"]
    for k, (t, ob, desc) in ESQUEMAS[tipo].items():
        tn = t.__name__ if isinstance(t, type) else "/".join(x.__name__ for x in t)
        linhas.append(f'  {"*" if ob else " "} {k:<18} {tn:<10} {desc}')
    linhas.append("Exemplo: veja registro/monstros/esporinho.json e cartoes/ para o passo a passo.")
    return "\n".join(linhas)
