"""Checagem estatica LEVE de arquivos Luau (rede de seguranca quando o luau-analyze nao roda).

NAO substitui a Script Analysis do Studio / luau-lsp. Pega os erros mais comuns de
codigo gerado ou editado por IA:
  - falta de '--!strict' na primeira linha
  - uso de 'any' em anotacao (': any', ':: any', '<any>')
  - caracteres do bloco U+2600-27BF (emoji/dingbats) - regra do projeto
  - blocos desbalanceados (function/if/for/while/do/repeat vs end/until), ignorando
    if-expressions do Luau ('x = if a then b else c' nao tem 'end')
  - parenteses/chaves/colchetes desbalanceados
Uso: python -m pixelforge luau-check caminho [caminho...]
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

KEYWORDS = re.compile(r"\b(function|if|then|elseif|else|for|while|do|repeat|until|end)\b")


def _strip(code: str) -> str:
    """Remove comentarios e strings (mantendo as quebras de linha para numerar erros)."""
    out = []
    i, n = 0, len(code)
    while i < n:
        if code.startswith("--[[", i) or code.startswith("--[=[", i):
            close = "]]" if code.startswith("--[[", i) else "]=]"
            j = code.find(close, i)
            j = n if j < 0 else j + len(close)
            out.append("\n" * code.count("\n", i, j))
            i = j
        elif code.startswith("--", i):
            j = code.find("\n", i)
            j = n if j < 0 else j
            i = j
        elif code[i] in "\"'`":
            q = code[i]
            j = i + 1
            while j < n and code[j] != q and code[j] != "\n":
                j += 2 if code[j] == "\\" else 1
            out.append('""')
            i = j + 1
        elif code.startswith("[[", i):
            j = code.find("]]", i)
            j = n if j < 0 else j + 2
            out.append('""' + "\n" * code.count("\n", i, j))
            i = j
        else:
            out.append(code[i])
            i += 1
    return "".join(out)


def check_text(code: str, name: str = "<luau>") -> List[str]:
    issues: List[str] = []
    first = code.lstrip("﻿").splitlines()[0] if code.strip() else ""
    if first.strip() != "--!strict":
        issues.append(f"{name}:1: primeira linha deve ser --!strict")
    for ln, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if 0x2600 <= ord(ch) <= 0x27BF:
                issues.append(f"{name}:{ln}: caractere bloqueado U+{ord(ch):04X}")
                break
    s = _strip(code)
    for ln, line in enumerate(s.splitlines(), 1):
        if re.search(r"(:\s*any\b|::\s*any\b|<\s*any\s*>)", line):
            issues.append(f"{name}:{ln}: uso de 'any' (proibido)")
    # blocos
    stack: List[Tuple[str, int]] = []
    tokens = []
    for ln, line in enumerate(s.splitlines(), 1):
        for m in KEYWORDS.finditer(line):
            prev = line[: m.start()].rstrip()
            tokens.append((m.group(1), ln, prev))
    expr_if_depth = 0
    for kw, ln, prev in tokens:
        if kw == "if":
            # if-expression: aparece depois de '=', '(', ',', 'return', 'then', 'else', operador...
            if re.search(r"(=|\(|,|\breturn|\{|\band|\bor|\bnot|\.\.|[+\-*/%<>])$", prev) or prev.endswith("then") \
                    or prev.endswith("else"):
                expr_if_depth += 1
                continue
            stack.append(("if", ln))
        elif kw in ("then", "elseif"):
            continue
        elif kw == "else":
            if expr_if_depth > 0:
                expr_if_depth -= 1
            continue
        elif kw in ("function", "for", "while", "repeat"):
            stack.append((kw, ln))
        elif kw == "do":
            if stack and stack[-1][0] in ("for", "while") and not stack[-1][0].endswith("+do"):
                stack[-1] = (stack[-1][0] + "+do", stack[-1][1])
            else:
                stack.append(("do", ln))
        elif kw == "until":
            if not stack or not stack[-1][0].startswith("repeat"):
                issues.append(f"{name}:{ln}: 'until' sem 'repeat'")
            else:
                stack.pop()
        elif kw == "end":
            if not stack:
                issues.append(f"{name}:{ln}: 'end' sobrando")
            else:
                stack.pop()
    for kw, ln in stack:
        issues.append(f"{name}:{ln}: bloco '{kw.split('+')[0]}' sem 'end'")
    # parenteses / chaves / colchetes
    pairs = {")": "(", "}": "{", "]": "["}
    st: List[Tuple[str, int]] = []
    for ln, line in enumerate(s.splitlines(), 1):
        for ch in line:
            if ch in "({[":
                st.append((ch, ln))
            elif ch in ")}]":
                if not st or st[-1][0] != pairs[ch]:
                    issues.append(f"{name}:{ln}: '{ch}' sem par")
                    break
                st.pop()
    for ch, ln in st:
        issues.append(f"{name}:{ln}: '{ch}' nao fechado")
    return issues


def check_paths(paths: List[Path]) -> List[str]:
    out: List[str] = []
    for p in paths:
        files = sorted(p.rglob("*.luau")) if p.is_dir() else [p]
        for f in files:
            out += check_text(f.read_text(encoding="utf-8"), str(f))
    return out
