"""Estrutura de animacao + utilitarios de timing.

Timing em pixel art (ver references/02-animacao-vfx.md):
- 'tick' = 1/60 s. VFX costuma rodar 'on twos/threes' (2-3 ticks por quadro ~ 30-20 fps)
  e segurar (hold) os quadros-chave: flash de impacto, pose de antecipacao.
- GUI (ImageRectOffset) aceita duracao por quadro -> use 'durations_ms'.
- ParticleEmitter Flipbook tem framerate FIXO -> holds precisam ser 'assados'
  duplicando quadros (ver sheet.flipbook_frames()).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .canvas import Canvas

TICK_MS = 1000.0 / 60.0


def ticks(n: float) -> int:
    """Converte ticks de 60 Hz em ms inteiros (2 ticks = 33 ms, 3 = 50 ms, 4 = 67 ms, 5 = 83 ms)."""
    return int(round(n * TICK_MS))


@dataclass
class Animation:
    name: str
    frames: List[Canvas]
    durations_ms: List[int]
    loop: bool = False
    pivot: Tuple[int, int] = (0, 0)
    tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.frames) != len(self.durations_ms):
            raise ValueError(f"{self.name}: {len(self.frames)} quadros e {len(self.durations_ms)} duracoes")
        ws = {f.w for f in self.frames}
        hs = {f.h for f in self.frames}
        if len(ws) != 1 or len(hs) != 1:
            raise ValueError(f"{self.name}: todos os quadros devem ter o mesmo tamanho")
        if self.pivot == (0, 0):
            self.pivot = (self.w // 2, self.h // 2)

    @property
    def w(self) -> int:
        return self.frames[0].w

    @property
    def h(self) -> int:
        return self.frames[0].h

    @property
    def total_ms(self) -> int:
        return int(sum(self.durations_ms))

    def resample_fixed(self, fps: float, max_frames: Optional[int] = None) -> List[Canvas]:
        """Amostra a animacao numa taxa fixa (para Flipbook). Holds viram quadros repetidos."""
        step = 1000.0 / fps
        out: List[Canvas] = []
        t = 0.0
        total = self.total_ms
        while t < total - 1e-6:
            acc = 0.0
            for f, d in zip(self.frames, self.durations_ms):
                if t < acc + d:
                    out.append(f)
                    break
                acc += d
            t += step
            if max_frames and len(out) >= max_frames:
                break
        return out


def uniform(frames: Sequence[Canvas], ms: int) -> List[int]:
    return [ms] * len(frames)
