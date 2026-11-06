# 03 — UI, ícones, molduras de carta e efeitos de tela

Dossiê: `docs/pixel-art/pesquisa/02-tecnica-pixel-art-vfx-ui.md` (seções 6, 7 e 8).

## 1. Caixas 9-slice [UI-01 a UI-03]
- As **bordas devem ser tileáveis** com os cantos e consigo mesmas. Os cantos concentram o detalhe; bordas e miolo ficam calmos.
- Esticar só funciona em caixas com pouquíssimo detalhe. Para bordas detalhadas, use tile.
- Canto de 3–8 px nativos. Contorno externo de 1 px no tom mais escuro. Bisel: 1 px de luz em cima/esquerda, 1 px de sombra embaixo/direita.
- Formas só verticais ou só horizontais usam 3-slice. A mesma técnica serve para barras de vida, sliders e divisores.
- **Roblox:** `ScaleType = Slice`, `SliceCenter = Rect(minX, minY, maxX, maxY)` em px da imagem, `SliceScale` **inteiro** e `ResampleMode = Pixelated`.
- **No motor:** `ui.panel()` e `ui.border_mask()` devolvem `NineSlice(canvas, center)`, com `luau_rect()` pronto para colar.

## 2. Botões [UI-04 a UI-07]

| Estado | Face | Bisel/sombra | Conteúdo | Animação |
|---|---|---|---|---|
| Normal | tom base | luz no topo, sombra na base, sombra projetada de 1 px | posição base | — |
| Hover/Focus | +1 passo (ou outline de acento) | igual | igual | shine sweep a cada 2–4 s |
| Pressed | −1 passo | bisel invertido, **sem sombra projetada** | **desce 1 px** | squash opcional de 40–60 ms |
| Disabled | S ≤ 15%, L −0,10 | sem sombra | tom médio | nenhuma |

- Os 4 estados têm o **mesmo tamanho** (trocar a imagem não muda o layout). Uma ação principal por tela, visualmente mais forte.
- **No motor:** `ui.button_states(pal, w, h, accent)`.
- **Roblox:** `ImageButton.Image`/`HoverImage`/`PressedImage` com uma imagem por estado, ou sheet + `SpriteAnimator.setFrame`.

## 3. Molduras de carta, raridade e "editions" [UI-08 a UI-13]
- Slay the Spire: raridade pela **cor do banner e da moldura** (cinza, azul, dourado); tipo pela **forma** da moldura. [UI-08]
- Inscryption: em baixa resolução, **texto mínimo** e ícones grandes. [UI-10]
- Raridade gótica sugerida [IC-08]: Comum = ferro; Incomum = aço/prata azulada; Rara = ouro velho; Épica = ametista; Lendária = carmim + ouro animado. Cada tier muda também em **valor e forma** (daltonismo). [IC-01]
- **Editions do Balatro** [UI-11]: efeitos calculados em UV **presa ao texel**, com campo animado de 3 centros orbitando.
  - Polychrome: gira o matiz em manchas.
  - Holographic: grade diagonal + azul-violeta.
  - Foil: anéis radiais + faixas angulares girando, mais B.
  - Negative: inverte L.
  - Em Python: calcule por texel, quantize de volta para a paleta e aplique só na arte e na moldura (nunca no texto). [UI-12]
- Anatomia de carta gótica [UI-13]:
  - moldura 9-slice com cantos ornamentados;
  - banner na cor da raridade;
  - selo por tipo;
  - janela do retrato "afundada";
  - custo em gema;
  - edição = overlay + shine;
  - raridade alta com 1 idle.
- **Implementação de referência deste repositório:** `docs/specs/CURRENT_SPEC.md` (Forja +0..+5) e `pipeline/dark_altar/build_forge.py` (ornamentos e mockup).

## 4. Ícones [IC-01 a IC-07]
- Oito regras: silhueta distinta; baixa complexidade; estilo consistente; sem depender de texto; metáfora conhecida; um significado; projetar pequeno; **forma antes da cor**.
- Pontas e formas afiadas = perigo. Prioridade em caveiras pequenas: olhos → maxila → zigomático → dentes. [IC-03, IC-04]
- Teste de valor: dessature. Se as massas não se separam, abra os valores. [IC-06]

| Tamanho | Outline | Cores | AA | Ícone dentro do plate |
|---|---|---|---|---|
| 16 | 1 px escuro, zero órfãos | 4–6 | não | 12–14 px |
| 24 | 1 px sel-out | 6–8 | não | 18–20 px |
| 32 | 1 px sel-out | 8–12 | interno mínimo | 24–28 px |
| 48 | 1 px sel-out | 12–16 | interno moderado | 36–42 px |

Comum a todos:
- Luz no alto-esquerda em todo o conjunto.
- **ΔL ≥ 0,30** entre ícone e plate. O plate fica nas bandas escuras, com matiz complementar ao objeto.
- **Raridade na moldura, não no objeto.**
- Teste sobre fundo claro, médio e escuro.

## 5. Efeitos de tela e transições [TR-01 a TR-15]
- **Dither fade (Bayer 4×4):** mostra a cena nova onde `progresso > (M4[y%4][x%4] + 0,5)/16`, em 16 passos de 33–50 ms. Para o escuro: cena → B0 → cena nova. Gerador: `fx.transition_dither`. [TR-07]
- **Diamond wipe:** `|fract(x/s) − ½| + |fract(y/s) − ½| + u + v < progresso·k`. Gerador: `fx.transition_diamond`. [TR-08]
- **Iris:** raio inteiro com easeInOutCubic e borda de 1 px no acento. Gerador: `fx.transition_iris`. [TR-09]
- **Wipe por máscara** (ordem codificada numa textura; para pixel art, limiar binário). [TR-10]
- **Mosaico** (SNES): blocos 1→16, cada bloco = pixel superior esquerdo. [TR-11]
- **CRT** (Balatro): curvatura, máscara de borda, aberração cromática ±0,8 px, scanlines por canal. Aplique **depois** do upscale e mantenha um toggle de acessibilidade. [TR-13]
- **Palette cycling** (Mark Ferrari): anima girando faixas da paleta, com pixels parados. Ideal para vitral, lava, runas e forja. [TR-14, TR-15]
- **No Roblox:**
  - Transições em baixa resolução (80×45) num `ImageLabel` de tela cheia, Pixelated, tocadas pelo `SpriteAnimator`. Custa 1 instância.
  - Flash de tela = `Frame` de tela cheia por max(20 ms, 1 quadro), com opção "reduzir flashes".
  - **Não** use `CanvasGroup` para fade de pixel art grande: ele reduz a resolução sob pressão de memória e borra.
- **Shine sweep:** faixa diagonal com `UIGradient` (Transparency em degraus) animando **`Offset`**. Pausa 500 ms → varredura 9×80 ms → hold 200 ms. [VFX-31]

## 6. Texto e números
- Fonte bitmap do jogo, em escala inteira. Números de dano: pop com overshoot de 1–2 px e queda.
- Nunca tween de `UIStroke` em texto: o Roblox renderiza e guarda vários tamanhos de glifo por quadro.
- `TextLabel.MaxVisibleGraphemes` faz efeito typewriter. `utf8.graphemes` itera grafemas e só existe no Roblox.
