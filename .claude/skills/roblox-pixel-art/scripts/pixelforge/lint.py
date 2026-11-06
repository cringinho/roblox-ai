"""Lint de pixel art: detecta automaticamente os erros classicos.

Cada regra devolve (ok, mensagem, penalidade). A nota final (0-100) serve de
'gate': assets abaixo de 80 nao devem ser enviados ao Roblox sem revisao.

Limitacoes honestas: heuristicas nao substituem olho humano. 'banding' e
'pillow shading' sao estimados pela distribuicao das cores em relacao a borda.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .anim import Animation
from .canvas import Canvas
from .color import RGB, contrast_ratio, luma
from .palette import Palette
from .raster import N8, distance_inside, shift


@dataclass
class LintResult:
    name: str
    score: int
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def text(self) -> str:
        head = f"[{self.score:3d}/100] {self.name}"
        body = "\n".join(f"   - {i}" for i in self.issues) or "   - sem problemas detectados"
        mets = ", ".join(f"{k}={v}" for k, v in self.metrics.items())
        return f"{head}\n{body}\n   ({mets})"


def _neighbors_same(px: np.ndarray, opaque: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Conta vizinhos (8) opacos e vizinhos com a MESMA cor."""
    h, w = opaque.shape
    rgb = px[..., :3].astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    key = np.where(opaque, key, -1)
    any_n = np.zeros((h, w), dtype=np.int32)
    same_n = np.zeros((h, w), dtype=np.int32)
    for dx, dy in N8:
        sk = np.full((h, w), -2, dtype=np.int64)
        ys0, ys1 = max(0, dy), min(h, h + dy)
        xs0, xs1 = max(0, dx), min(w, w + dx)
        sk[ys0:ys1, xs0:xs1] = key[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        any_n += (sk >= 0)
        same_n += (sk == key) & opaque
    return any_n, same_n


def detect_upscale(c: Canvas) -> int:
    """Se a imagem for pixel art ampliada (blocos kxk), devolve k (>1). Senao 1."""
    a = c.px
    for k in (8, 6, 5, 4, 3, 2):
        if c.w % k or c.h % k:
            continue
        small = a[::k, ::k]
        if np.array_equal(np.repeat(np.repeat(small, k, 0), k, 1), a):
            return k
    return 1


def lint_canvas(c: Canvas, pal: Optional[Palette] = None, name: str = "asset",
                max_colors: int = 24, bg: RGB = (30, 30, 36), kind: str = "sprite",
                allow_sparks: bool = True, check_contrast: bool = True) -> LintResult:
    """kind: 'sprite' (icone/personagem), 'vfx', 'ui', 'background'."""
    res = LintResult(name, 100)
    px = c.px
    alpha = px[..., 3]
    opaque = alpha > 0
    n_op = int(opaque.sum())
    res.metrics["px"] = n_op
    if n_op == 0:
        res.issues.append("imagem vazia")
        res.score = 0
        return res

    # 1. alpha duro
    soft = int(((alpha > 0) & (alpha < 255)).sum())
    if soft:
        res.issues.append(f"{soft} pixels com alpha parcial (pixel art usa so 0 ou 255)")
        res.score -= min(20, 5 + soft // 10)

    # 2. escala nativa
    k = detect_upscale(c)
    if k > 1:
        res.issues.append(f"imagem parece ampliada {k}x: trabalhe/lint na resolucao nativa ({c.w // k}x{c.h // k})")
        res.score -= 5

    # 3. paleta
    cols = c.unique_colors()
    res.metrics["cores"] = len(cols)
    if len(cols) > max_colors:
        res.issues.append(f"{len(cols)} cores (limite sugerido {max_colors} para '{kind}')")
        res.score -= min(15, (len(cols) - max_colors))
    if pal is not None:
        palset = set(pal.colors())
        off = [col for col in cols if tuple(col) not in palset]
        if off:
            res.issues.append(f"{len(off)} cores fora da paleta (quantize com Palette.quantize)")
            res.score -= min(20, 4 + 2 * len(off))

    # 4. pixels orfaos / faiscas
    #    - faisca: pixel opaco sem nenhum vizinho opaco (intencional em VFX)
    #    - ponto de dither: orfao cercado por UMA unica cor (textura plana) -> aceito
    #    - ruido: orfao numa vizinhanca com 2+ cores diferentes -> penaliza
    any_n, same_n = _neighbors_same(px, opaque)
    sparks = opaque & (any_n == 0)
    orphan_all = opaque & (any_n > 0) & (same_n == 0)
    rgbk = (px[..., 0].astype(np.int64) << 16) | (px[..., 1].astype(np.int64) << 8) | px[..., 2]
    orphans = np.zeros_like(orphan_all)
    hh, ww = opaque.shape
    for y, x in zip(*np.where(orphan_all)):
        cols_n = set()
        for dx, dy in N8:
            xx, yy = x + dx, y + dy
            if 0 <= xx < ww and 0 <= yy < hh and opaque[yy, xx]:
                cols_n.add(int(rgbk[yy, xx]))
        if len(cols_n) >= 2:
            orphans[y, x] = True
    n_orph, n_spark = int(orphans.sum()), int(sparks.sum())
    res.metrics["orfaos"] = n_orph
    res.metrics["dither"] = int(orphan_all.sum()) - n_orph
    res.metrics["faiscas"] = n_spark
    lim = max(2, n_op // (60 if kind in ("vfx", "background") else 120))
    if n_orph > lim:
        res.issues.append(f"{n_orph} pixels orfaos (cor sem vizinho igual) -> ruido; limpe clusters")
        res.score -= min(20, (n_orph - lim) // 2 + 3)
    if not allow_sparks and n_spark:
        res.issues.append(f"{n_spark} pixels soltos no vazio")
        res.score -= min(10, n_spark)

    # 5. banding / pillow (cores que formam aneis paralelos a borda)
    if kind in ("sprite", "ui") and n_op > 64:
        d = distance_inside(opaque)
        rgb = px[..., :3].astype(np.int32)
        key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
        ring_like = 0
        for col_key in np.unique(key[opaque]):
            m = opaque & (key == col_key)
            cnt = int(m.sum())
            if cnt < 12:
                continue
            dv = d[m]
            if dv.min() <= 1.0:  # contorno: pode ser paralelo a borda por definicao
                continue
            if dv.std() < 0.55 and cnt > 0.25 * n_op ** 0.5 * 4:
                ring_like += 1
        res.metrics["aneis"] = ring_like
        if ring_like >= 2:
            res.issues.append(f"{ring_like} faixas de cor paralelas a borda (banding/pillow shading): sombreie pela direcao da luz")
            res.score -= 8 * (ring_like - 1)

    # 6. contraste de valor com o fundo do jogo
    lum = np.array([luma(tuple(col)) for col in cols])
    vrange = float(lum.max() - lum.min()) if len(lum) else 0.0
    res.metrics["faixa_valor"] = round(vrange, 2)
    if kind in ("sprite", "ui") and vrange < 0.30:
        res.issues.append(f"faixa de valor curta ({vrange:.2f}): forma sem leitura em escala de cinza (alvo >= 0.30)")
        res.score -= 10
    best_contrast = max(contrast_ratio(tuple(col), bg) for col in cols)
    res.metrics["contraste_max_bg"] = round(best_contrast, 2)
    if check_contrast and best_contrast < 3.0:
        res.issues.append(f"contraste maximo com o fundo {best_contrast:.2f} (< 3): some na UI escura")
        res.score -= 12

    res.score = max(0, min(100, res.score))
    return res


def lint_animation(anim: Animation, pal: Optional[Palette] = None, kind: str = "vfx",
                   max_colors: int = 16) -> LintResult:
    res = LintResult(anim.name, 100)
    scores = []
    # quadros onde baixo contraste e INTENCIONAL: contrast frame declarado na tag e
    # a cauda de dissipacao (ultimos 30%) de efeitos one-shot
    intentional = {int(x) for x in anim.tags.get("contrast_frames", "").split(",") if x.strip().isdigit()}
    tail_start = int(len(anim.frames) * 0.7) if not anim.loop else len(anim.frames)
    for i, f in enumerate(anim.frames):
        if f.bbox() is None:
            continue
        r = lint_canvas(f, pal, f"{anim.name}#{i}", max_colors, kind=kind,
                        check_contrast=(i not in intentional and i < tail_start))
        scores.append(r.score)
        for iss in r.issues:
            res.issues.append(f"q{i}: {iss}")
    if scores:
        res.score = int(round(min(scores) * 0.5 + np.mean(scores) * 0.5))
    # estabilidade do pivo em loops (pulo = 'boiling' indesejado)
    if anim.loop:
        boxes = [f.bbox() for f in anim.frames if f.bbox()]
        if boxes:
            bys = [b[3] for b in boxes]
            if max(bys) - min(bys) > max(2, anim.h // 8):
                res.issues.append("base do loop oscila muito entre quadros (pivo instavel)")
                res.score -= 5
    if anim.w * anim.h > 0 and len(anim.frames) > 64:
        res.issues.append("mais de 64 quadros: nao cabe em Flipbook 8x8")
        res.score -= 5
    res.metrics["quadros"] = len(anim.frames)
    res.metrics["duracao_ms"] = anim.total_ms
    res.score = max(0, min(100, res.score))
    # dedup de mensagens repetidas
    seen, uniq = set(), []
    for i in res.issues:
        k = i.split(": ", 1)[-1]
        if k not in seen:
            seen.add(k)
            uniq.append(i)
    res.issues = uniq[:12]
    return res
