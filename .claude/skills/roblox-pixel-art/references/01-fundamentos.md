# 01 — Fundamentos de pixel art (regras testáveis)

IDs entre colchetes apontam para o dossiê completo, com fontes, em `docs/pixel-art/pesquisa/02-tecnica-pixel-art-vfx-ui.md`.
Principais fontes: Saint11 (Pedro Medeiros, Celeste), Slynyrd Pixelblog, Androidarts, Pixel Parmesan, Lospec.

## 1. Escala e grade
- **Só escala inteira** (2×, 3×, 4×) com nearest. Escala fracionada deforma os pixels: "mixels". [F-01, F-02, F-07]
- **Mixels** (pixels de tamanhos diferentes na mesma tela) são erro fundamental. A exceção são efeitos menores de propósito (corações, gotas). [F-07]
- **Nunca rotacione nem redimensione arte pronta** como asset final: redesenhe. Para "rotação" de efeito, use quadros redesenhados ou passos de 90° com espelho. [F-05, F-06, F-09]
- Faixa de ouro de resolução de cena: **320×180 a 640×360** (escalam inteiro para 1080p). Blasphemous usa 640×360. [F-03, F-04]
- Na dúvida, menor. [F-08]
- **No motor:** `Canvas.scaled(k)` é a única ampliação. `raster.snap_angle()` força ângulos limpos (0°, 18,43°, 26,57°, 45°…).

## 2. Clusters e ruído
- Cluster = pixels da mesma cor que se tocam. Clusters ambíguos geram estilo pobre. [F-10]
- **Pixel órfão** (sem vizinho da mesma cor) é ruído. Use só como detalhe forte, faísca ou último quadro de partícula. [F-11, F-14]
- Em cenas escuras, cada cluster precisa de motivo para existir. [F-13]
- Agrupe detalhe em "ilhas"; o resto fica calmo. [F-12]
- **No motor:** `shade.clean_index_map()` absorve órfãos e `raster.remove_specks()` limpa máscaras. O lint conta órfãos e separa ruído (vizinhança com 2+ cores) de dither (vizinhança de 1 cor).

## 3. Linhas e curvas
- Reta regular: **todos os degraus com o mesmo comprimento**. Se precisar de irregular, repita um padrão (`2,2,3,2,2,3`). [F-15]
- Curva: degraus diminuem até a "quina" e depois crescem. Degraus conectam **na diagonal**. Quinas em "L" engrossam a linha e devem ser removidas. [F-15, F-17]
- **No motor:** `canvas.line_points()` = Bresenham + remoção de L. Círculos usam ponto médio (`fx.circle_pts`).

## 4. Anti-aliasing
- **Nunca AA automático.** [F-19]
- AA manual só por dentro do sprite. O valor do pixel de AA segue a cobertura (50% → meio caminho). Reaproveite cores da paleta. Não faça AA na borda externa sobre transparente. Em sprites ≤ 16 px, AA vira ruído. [F-20, F-22]

## 5. Outline e sel-out
- Outline separa a forma do fundo. A linha interna separa partes e pode ser mais clara. **Sel-out**: cor escura derivada do material vizinho, mais clara (ou ausente) no lado iluminado. [F-23, F-26]
- Efeitos luminosos (fogo, plasma, luz) **não têm outline escuro**: o outline é colorido ou não existe. [F-25]
- Projéteis e VFX que precisam "saltar" podem usar outline duplo (claro + escuro). [F-27]
- Espessura: 1 px até ~64 px de altura. 2 px só em UI estilizada. [F-28]
- **No motor:** `shade.selout()` (2 passos mais escuro na sombra, 1 na luz), `shade.outline()` (externo 4-conexo) e `shade.rim_light()`.

## 6. Banding, pillow e dithering
- **Banding:** dois segmentos de cores diferentes, ≥ 2 px, paralelos e com extremidades alinhadas reforçam a grade. **Pillow shading:** camadas concêntricas seguindo o contorno. [F-29]
- Correção: sombreie pela **direção da luz**, comprima as bandas e termine o gradiente abruptamente contra outro. As faces de um volume são quase uma cor sólida. [F-30, F-31]
- **Dither:** só onde faz "trabalho duplo" (gradiente + textura): céu, feixe, névoa, fade. Nunca em sprites ≤ 32 px, ícones, texto ou bordas de UI. Nunca entre cores com ΔL > 0,25. O padrão fica **preso ao mundo/tela**, senão cintila. [F-32 a F-36]
- **No motor:**
  - `form_shade` usa campo de altura + luz, e não distância à borda, por isso não gera pillow.
  - `sphere_lit` (fx) cria terminador curvo.
  - `dither_mix(..., levels=(0, .25, .5, .75, 1))` é o dither estilizado.

## 7. Cor: rampas e hue shift (números medidos em paletas profissionais)
- Rampa = cores ordenadas por brilho que também **giram o matiz**. [C-01]
- Rampas de 6 passos (Apollo, Endesga, Resurrect) giram **45°–100°** no total (≈ 15° por passo). O giro é **maior nos escuros**. [C-06]
- Direção: clareando, o matiz vai para **amarelo (40°–70°)**; escurecendo, vai para **azul-violeta (220°–290°)**. [C-07]
- Saturação: ponta escura 44–59%, **pico 57–77% no meio**, ponta clara ≈ 0,4–0,75 do pico. Rampas de fogo e luz ficam saturadas até o topo. [C-08]
- Valor: tom mais escuro V 15–30% (**nunca preto puro**), mais claro V 85–91% (material) ou 98–100% (luz/fogo). [C-09, C-18]
- **Validação de rampa:** |ΔH| entre vizinhos ≤ 22°; **ΔL_OKLab ≥ 0,06** entre vizinhos. [2.3]
- **No motor:**
  - `palette.make_ramp(anchor, hue_shift, cool_hue, warm_hue, ...)` gera em OKLCH, com passos de luz perceptualmente iguais e croma com pico no meio.
  - `altar_palette()` tem 14 rampas e 86 cores. Os tokens da Forja estão fixados: #1E1E24, #2C2E35, #4DD0E1, #B388FF, #E5A93C.
  - Pedra gótica usa pouco giro (10–16°); fogo e magia, muito (40°+).

## 8. Orçamento de cores [C-16]

| Asset | Cores | Passos por rampa |
|---|---|---|
| Ícone 16×16 | 4–6 | 3 + outline |
| Ícone 32×32 | 8–12 | 4 |
| Ícone 48–64 | 12–16 | 4–5 |
| Moldura de carta / 9-slice | 6–10 | 3–4 por material |
| Botão (todos os estados) | 5–8 | 3 + highlight |
| VFX individual | 4–6 + branco | 4–5 de luz + 1–2 de fumaça |
| Cenário | 16–24 | 2–3 (longe) / 4–6 (perto) |
| Paleta mestra | 32–64 | — |

## 9. Luz
- Defina a luz no início. A principal fica no **alto-esquerda** (padrão do jogo inteiro). [L-01]
- Três pontos: key, fill e **rim** (separa do fundo). Para **magia sombria, luz de baixo**; para **sagrada, luz de cima**. [L-02, L-03]
- Metal: claros mais frios e menos saturados, escuros mais quentes e saturados, contraluz forte. [L-05]
- Gema: cada faceta brilha inteira; 7 papéis de cor. [L-06, C-15]
- Poça de luz quente (tocha/forja): `I = (1 − smoothstep(0,3r, r, d))^1,6`, quantizada em 4–6 níveis, cada nível = 1 passo da rampa, dither só em ±1 nível da fronteira. **Flicker só escurece**, jitter por linha. [L-07 a L-09]

## 10. Paletas de referência úteis
- **Endesga 64 / Apollo**: escuros profundos não pretos, roxos completos, fogo longo. São as recomendadas para gótico. [C-17]
- **Bloodmoon21 / Midnight Ablaze**: sub-rampas de sangue. **Gothic Bit**: pedra fria. [C-17]
- Hex completos no dossiê (seção 2.5).
