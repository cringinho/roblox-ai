---
name: roblox-pixel-art
description: >-
  Produz pixel art de nível profissional para Roblox, animada ou estática: UI, botões,
  painéis 9-slice, molduras e ornamentos de carta, ícones e arte de carta, sprite sheets de
  VFX para GUI, flipbooks de ParticleEmitter, transições e efeitos de tela, e cenários.
  Usa o motor PixelForge (Python) e integra no Roblox Studio pelo MCP embutido, Open Cloud
  e Luau. Use quando pedirem pixel art, sprite, spritesheet, flipbook, VFX 2D, ícone,
  moldura, botão pixel, background pixel, paleta, animação em pixel ou revisão de
  qualidade de pixel art em Roblox.
---

# Pixel art para Roblox (PixelForge)

Você é o artista, o animador e o integrador ao mesmo tempo. Qualidade aqui significa três coisas:
1. A forma lê em 1 segundo (silhueta e valor).
2. A cor é fechada numa paleta com rampas hue-shifted.
3. Não há ruído (pixels órfãos, banding, mixels).
4. O timing tem peso (holds e contraste).
5. No Roblox, o asset aparece **nítido** (Pixelated, escala inteira) e **leve** (atlas, 1 relógio).

## Mapa da skill

| Caminho | O que é |
|---|---|
| `scripts/pixelforge/` | Motor Python (Pillow + numpy). CLI: `python -m pixelforge --help`, rodando a partir de `scripts/` |
| `luau/` | Runtime Roblox: `PixelClock` (1 relógio), `SpriteAnimator` (GUI), `PixelScale` (escala inteira), `FlipbookVFX` (partículas) |
| `references/01-fundamentos.md` | Grade, clusters, linhas, AA, sel-out, banding, dithering, rampas e paletas, orçamento de cores |
| `references/02-animacao-vfx.md` | Timing, impacto, hit-stop, smear, receitas de explosão, fogo, fumaça, faísca, raio, magia, sangue, slash |
| `references/03-ui-icones-telas.md` | 9-slice, botões, molduras de carta e raridade, ícones por tamanho, transições, shake, flash |
| `references/04-cenarios-gotico.md` | Composição de cenário, bandas de valor, catedral e forja, reflexo, luz, parallax |
| `references/05-roblox-integracao.md` | ResampleMode, limites de imagem, compressão mobile, flipbook, upload, EditableImage, Fusion 0.3, Studio MCP |
| `references/06-qa-checklist.md` | Gate de qualidade: lint, rubrica visual e teste no aparelho |

## Regras de ouro (nunca quebre)

1. **Nativo primeiro.** Desenhe na resolução final pequena (ícone 32–64, VFX 24–64, cenário 320×180). Escale **só por inteiro** com nearest. Nunca rotacione nem redimensione arte pronta com filtro.
2. **Paleta fechada.** Use `altar_palette()` ou outra do projeto. Termine com `Palette.quantize()`. O orçamento de cores está em `references/01` (C-16).
3. **Rampas com hue shift.** Sombra puxa para azul-violeta e luz puxa para amarelo. Nada de rampa preto→cor→branco.
4. **Luz única.** Luz no topo-esquerda para todo o jogo. Sombreie pela direção da luz, nunca do centro para a borda (pillow shading).
5. **Clusters limpos.** Nenhum pixel órfão. Exceções: faísca intencional e último frame de partícula.
6. **Sel-out**, não contorno preto. Borda escura derivada da cor vizinha e mais clara no lado da luz.
7. **Dither com parcimônia.** Só em transições amplas (céu, feixe, névoa, fade) e só no padrão estilizado: 0 / 50% / 100%.
8. **Timing com peso.** Frames de impacto e flash curtos e **segurados**. Dissipação mais lenta que a explosão. Durações uniformes são o erro mais comum.
9. **Contraste antes da cor.** A forma tem de ler em escala de cinza. VFX: núcleo com L ≥ 0,85 sobre o fundo real do jogo.
10. **Roblox:** toda `ImageLabel`/`ImageButton` de arte usa `ResampleMode = Pixelated`, tamanho = k × nativo e `UIScale` inteiro. Imagens ≤ 1024 px. Upload como **Image**, nunca Decal. Partículas e texturas 3D **não** têm nearest: amplie antes do upload.
11. **Sem emoji** em código ou dados (bloco U+2600–27BF). Tags entre colchetes `[ATQ]` e glifos `◆ ◇ ▸ † ‡ ▲ ~ ·`.
12. **Verifique com os olhos.** Gere a prévia (strip/GIF ×4 sobre o fundo escuro do jogo), olhe a imagem e corrija. Rode o lint. Só entregue com gate aprovado (`references/06`).

## Fluxo obrigatório

```
1 BRIEF        o que é, onde aparece (GUI? partícula 3D? cenário?), tamanho na tela, fundo real,
               paleta, sentimento (sombrio/sagrado), tags de jogo, orçamento (cores, frames)
2 SILHUETA     máscara booleana (raster.*): lê sozinha? (teste de silhueta)
3 VALOR        bandas de luz (shade.form_shade / bevel): lê em cinza?
4 COR          rampas da paleta; acento saturado em 10-20% da área
5 ANIMAÇÃO     poses-chave -> timing (tabela em references/02) -> holds -> loop fecha?
6 LINT         python -m pixelforge lint ... (nota >= gate)  + olhar a prévia ×4
7 EXPORT       GUI: sheet.export_gui_sheet (padding + alpha bleed + módulo Luau)
               Partícula: sheet.export_flipbook (1024, 2x2/4x4/8x8, upscale inteiro, BlendFrames=false)
               3D: sheet.upscale_for_3d ; cenário: PNG nativo + cópia ×4 para revisão
8 ROBLOX       upload (Image) -> IDs nos módulos -> montar com luau/* -> conferir no Studio
9 CONFERIR     screen_capture (MCP) ou print no aparelho -> ajustar -> repetir 6-9
```

## PixelForge em 30 segundos

```bash
cd .claude/skills/roblox-pixel-art/scripts
python -m pixelforge list                          # geradores de VFX e transições
python -m pixelforge fx fire_loop --gui --flipbook --out out/fx
python -m pixelforge fx-all --out out/fx           # todos + lint_report.json
python -m pixelforge lint caminho.png --kind sprite|vfx|ui|background
python -m pixelforge preview-luau caminho.png      # Luau p/ prévia instantânea (EditableImage)
python -m pixelforge scene cathedral --out out/cathedral.png
python -m pixelforge upload a.png b.png            # Open Cloud (precisa ROBLOX_API_KEY no ambiente)
```

API Python (para arte nova, escreva um script curto que use os módulos):

```python
import sys; sys.path.insert(0, ".claude/skills/roblox-pixel-art/scripts")
from pixelforge.palette import altar_palette
from pixelforge.canvas import Canvas
from pixelforge.raster import shape_mask, SHAPES, polygon_mask, dilate, edge_inner
from pixelforge.shade import form_shade, selout, outline, gradient_dither
from pixelforge.anim import Animation, ticks
from pixelforge import fx, sheet, lint, preview

pal = altar_palette()
c = Canvas(32, 32)
m = shape_mask(32, 32, SHAPES["DIAMOND"], 16, 16, 9, 13)   # silhueta
form_shade(c, m, pal.ramp("violet").colors)                # valor + cor (luz topo-esquerda)
selout(c, pal)                                             # borda derivada da cor
outline(c, pal["void:0"])                                  # contorno externo (ícones/UI)
print(lint.lint_canvas(c, pal, "gema", max_colors=8).text())
c.save("out/gema_x4.png", scale=4)                         # PRÉVIA: olhe esta imagem
```

Módulos: `color` (OKLab/OKLCH, contraste WCAG), `palette` (rampas hue-shifted, quantize, shift), `canvas` (alpha duro, linhas pixel-perfect), `raster` (formas por SDF, ângulos limpos, máscaras), `shade` (forma, sel-out, rim, dither Bayer estilizado), `noise` (ruído periódico p/ loop perfeito), `fx` (11 VFX + 3 transições), `ui` (9-slice, máscara de borda, estados de botão), `scene` (catedral), `font` (bitmap 5×7 com `† ‡ ◆ ◇ ▲ ▸ ~ ·`), `sheet` (exports Roblox), `lint`, `preview`, `roblox` (prévia EditableImage e upload).

## Receitas rápidas

| Pedido | Como fazer |
|---|---|
| **Ícone / arte de carta** | Silhueta (`raster`) → `form_shade` (3–4 bandas) → `selout` → plate e raridade na moldura. Tamanhos e cores: `references/03` (IC-07). Exemplo completo: `pipeline/dark_altar/subtype_render.py` (120 artes 64×64 com gravura, monograma, emblema e partículas). |
| **Botão** | `ui.button_states()`: 4 estados do mesmo tamanho. Pressed desce 1 px e inverte o bevel. No Roblox: `ImageButton` com `HoverImage`/`PressedImage` ou sheet com `SpriteAnimator.setFrame`. |
| **Painel / moldura 9-slice** | `ui.panel()` / `ui.border_mask()`. No Roblox: `ScaleType.Slice`, `SliceCenter` do retorno, `SliceScale` inteiro. Máscara **branca** + `ImageColor3` serve a várias cores e aceita `UIGradient`. |
| **Ornamentos** (cantoneira, arco, coroa) | Máscara do ornamento + `bevel()` (ver `pipeline/dark_altar/build_forge.py`). Faça um sprite por canto; não rotacione (a luz quebraria). |
| **VFX em GUI** (cartas, HUD) | `fx.*` ou gerador novo no mesmo padrão → `export_gui_sheet` → `SpriteAnimator.play(label, require(Sprite))`. Respeita ms por frame (holds). |
| **VFX no mundo 3D** | `export_flipbook` → `FlipbookVFX.ensure(part, nome, spec)`. Máximo 30 fps, `FlipbookBlendFrames = false`, OneShot com Lifetime = frames/fps. |
| **Transição de tela** | `fx.transition_dither/diamond/iris` em baixa resolução (80×45) → ImageLabel em tela cheia, Pixelated → SpriteAnimator (ida e volta). |
| **Cenário** | `scene.cathedral()` como modelo de composição. Para outro ambiente, copie a estrutura (parede → focal saturado → arquitetura → piso e reflexo → luz → vinheta → quantize). Para parallax, separe camadas em PNGs. |
| **Brilho de carta / foil** | Faixa diagonal (UIGradient com Offset animado) e foil escuro em tile. Veja `docs/specs/CURRENT_SPEC.md` §5. |

## Roblox Studio MCP (fluxo de montagem e verificação)

- **Claude Code local + Studio aberto** (MCP embutido: Assistant > ... > Manage MCP Servers > *Enable Studio as MCP server*; toda chamada leva `studio_id`):
  1. Gere os PNGs com o PixelForge.
  2. **Prévia sem upload:** `python -m pixelforge preview-luau arte.png` → `execute_luau` (datamodel_type `Edit`) cria `StarterGui/PixelForgePreview` via EditableImage.
  3. **Upload:** `upload_image` (aceita só URLs HTTP: por exemplo o raw do GitHub depois do push), ou `open_cloud_invoke` com arquivos de uma pasta aprovada, ou o script `pixelforge upload` (API key no ambiente).
  4. **Montagem:** `execute_luau` (Edit) cria ou ajusta as instâncias. Use `luau/*` e os módulos gerados (`*_Sprite.luau`, atlas).
  5. **Conferência:** `screen_capture` e `get_console_output`. Olhe a captura, corrija e repita.
- **Sessão na nuvem** (sem Studio alcançável): entregue PNG + módulos Luau no repositório e o passo a passo de upload. O MCP do Studio roda só na máquina local.
- Servidores MCP da comunidade sobem imagem como **Decal**, e esse ID não funciona em `ImageLabel` via script. Prefira `upload_image`/Open Cloud com `assetType` Image.

## Gate de qualidade (resumo; detalhes em `references/06`)

| Tipo | Nota mínima do lint | Revisão visual obrigatória |
|---|---|---|
| Sprite, ícone, UI | 90 | silhueta, escala de cinza, sobre o fundo real, ×1 e ×4 |
| VFX | 85 | quadro a quadro + GIF; o flash lê; a dissipação não "pisca"; o loop fecha |
| Cenário | 80 | ponto focal claro; nada compete com a UI; sem preto puro |

## Limites honestos (diga ao usuário quando se aplicarem)

- Formas **orgânicas complexas** (rostos, personagens, estátuas detalhadas) por puro procedimento ficam esquemáticas. Para isso:
  - escreva a máscara à mão em ASCII (`mask_from_rows` em `build_forge.py`) e deixe o motor sombrear; ou
  - peça um rascunho e quantize ou redesenhe sobre ele.
- O lint é heurístico: pega ruído, cores fora da paleta, contraste e banding concêntrico, mas **não substitui** o olhar.
- A compressão do Roblox no mobile altera cores de pixel art nativa. Teste no aparelho. Para sprites críticos, use a variante ×4 (`upscale=4`).
