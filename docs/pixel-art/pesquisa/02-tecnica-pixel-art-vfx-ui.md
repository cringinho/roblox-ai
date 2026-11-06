# 02 — Técnica profissional de pixel art para geração programática (VFX, UI, transições, ícones, molduras de carta e cenários góticos)

> Base de conhecimento para um agente que gera pixel art em **Python/Pillow** para um card game **gótico dark-fantasy**.
> Pesquisa compilada em 2026-11-06. Idioma: PT-BR (termos técnicos em inglês quando consagrados).

---

## 0. Como ler este documento

**Formato das regras.** Cada regra tem um ID (`F-03`, `C-12`, `VFX-07`…), um enunciado testável e a **fonte** (URL).
Marcadores:

| Marcador | Significado |
|---|---|
| **[FONTE]** | Regra extraída diretamente da fonte citada (parafraseada; números exatamente como na fonte). |
| **[MEDIDO]** | Medição própria feita sobre arquivos públicos da fonte (ex.: metadados de duração dos GIFs de tutorial do Saint11; cores amostradas por pixel; arquivos `.hex` das paletas do Lospec). Método descrito no texto. |
| **[SÍNTESE]** | Conclusão/algoritmo meu, derivado das fontes indicadas. Não é citação. Use como default ajustável. |
| **[SECUNDÁRIA]** | Fonte de confiabilidade menor (blog/marketing/fórum/wiki comunitária). Use como ponto de partida, não como verdade. |

**Unidades.** H em graus (0–360), S e V em % (modelo HSV). Para "valor perceptual" uso **L do OKLab** (0 = preto, 1 = branco), porque o V do HSV não representa a luminância percebida (azul puro e amarelo puro têm o mesmo V=100 mas luminâncias muito diferentes — ver C-09). Durações em **ms por frame**; "f" = frame; "@60" = frames de jogo a 60 fps.

**Sobre os tutoriais do Saint11 (Pedro Medeiros, artista de Celeste/TowerFall).** São GIFs com texto embutido; os textos foram lidos quadro a quadro e as durações foram extraídas dos metadados dos GIFs (Pillow). Índice: https://saint11.art/blog/pixel-art-tutorials/ — cada GIF está em `https://saint11.art/img/pixel-tutorials/<Nome>.gif`.

---

## 1. Fundamentos: grade, escala, clusters, linhas, AA, outline, dithering

### 1.1 Escala e grade

- **F-01 [FONTE]** Escalar pixel art **somente por múltiplos inteiros** (200%, 300%, 400%) com vizinho-mais-próximo; em escalas não inteiras (ex.: 193,5%) "as unidades de pixel ficam distorcidas e não são todas perfeitamente quadradas". O autor raramente passa de 4x ("chunky demais"). Composições típicas de 128×128 a 256×256 px exibidas a 2x–4x. — https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics
- **F-02 [FONTE]** "Pixel art must be scaled by whole number multiples to avoid distortion of the pixel units"; mockup de jogo exibido a 4x em 1920×1080. — https://www.slynyrd.com/blog/2026/7/26/pixelblog-63-horizontal-shmup
- **F-03 [FONTE]** Resolução-alvo de tela recomendada 480×270, com "faixa de ouro" de 320×180 a 640×360 (todas escalam inteiro para 1080p). — https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design
- **F-04 [SECUNDÁRIA]** Blasphemous (referência gótica) usa arte nativa 640×360; múltiplos inteiros (720p = 2x, 1080p = 3x) ficam pixel-perfect. — https://steamcommunity.com/app/774361/discussions/0/1638669204735629860
- **F-05 [FONTE]** **Não escalar nem rotacionar** arte pronta para gerar o asset final: "não há saída fácil, você precisa redesenhar"; algoritmos automáticos ajudam como rascunho. Procedimento: (1) resize automático → (2) consertar outline e silhueta → downscale: (3) redesenhar informação perdida, (4) escolher detalhes a omitir, (5) consertar dither e sombreamento quebrado; upscale: (3) caçar "quadradões" e arredondar, (4) redesenhar linhas e dither quebrados, (5) achar áreas para detalhe extra. Reduzir de um conceito é "tradução, não reescala": massas grandes primeiro, escolher detalhes fortes, concentrar detalhe/contraste neles. — https://saint11.art/img/pixel-tutorials/Resizing.gif
- **F-06 [FONTE]** "Sempre evito rotacionar pixel art; quando possível, use motion blur para fingir a rotação." — https://saint11.art/img/pixel-tutorials/Hazards.gif
- **F-07 [FONTE]** **Mixels** = pixels de tamanhos diferentes combinados na mesma imagem/tela (inclusive quando cada sprite é consistente mas são exibidos em escalas diferentes); "um dos erros fundamentais que você deve sempre evitar". Exceção aceitável: efeitos (corações, símbolos de raiva, gotas, poeira) em resolução menor para se destacarem. — https://yari-pixels.github.io/Articles/mixels.html
- **F-08 [FONTE]** "Quando não tiver certeza, use tamanhos menores" (exemplo do processo: 48×48). — https://saint11.art/img/pixel-tutorials/Pipeline.gif
- **F-09 [SÍNTESE]** Regra de código: todo asset é gerado **na resolução nativa** e exportado com `Image.resize((w*k, h*k), Image.NEAREST)`, `k ∈ ℕ`. Proibido `rotate()`/`resize()` com filtro bilinear/bicúbico/LANCZOS em qualquer estágio de arte; rotação de efeitos só via frames redesenhados ou rotação em passos de 90° (e espelhamentos), que preservam a grade.

### 1.2 Clusters, ruído, pixels órfãos

- **F-10 [FONTE]** Cluster = "qualquer grupo de pixels que se tocam com a mesma cor"; clusters ditam o visual (angulares = limpo; orgânicos = natural); clusters ambíguos geram "estilo extremamente pobre". — https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics
- **F-11 [FONTE]** Regras do Saint11 para legibilidade e redução de ruído: evitar criar muitos clusters; **pixels diagonais não conectam bem**; **pixel órfão** = pixel que não está em um "chunk"; órfãos demais arruínam a imagem (ruído); órfãos são úteis para **detalhes fortes**; evitar dither quando possível (útil para **textura**); repetir um padrão facilita a leitura; formas regulares são fáceis de reconhecer. Ao animar: acompanhar os clusters e **não quebrá-los**. — https://saint11.art/img/pixel-tutorials/Fundamentals.gif
- **F-12 [FONTE]** "Ruído e pixels órfãos desnecessários é o que você obtém ao tentar enfiar detalhes demais"; agrupar detalhe em "pequenas ilhas de detalhe"; usar 2+ variantes de tile (movimentada e calma). — https://www.androidarts.com/pixtut/pixelart.htm
- **F-13 [FONTE]** Em imagens escuras: "cada cluster de pixels precisa ter um motivo para estar ali"; evitar detalhe demais. — https://saint11.art/img/pixel-tutorials/Darkness.gif
- **F-14 [FONTE]** Sangue/partículas: "só uso pixels órfãos em resolução muito baixa"; "sempre evito órfãos, a menos que seja o último frame de uma partícula". — https://saint11.art/img/pixel-tutorials/Blood.GIF

### 1.3 Linhas e curvas (algoritmizáveis)

- **F-15 [FONTE]** Linhas retas regulares: **todos os degraus com o mesmo número de pixels**; use-as quando possível. Linhas irregulares (não ideais, mas úteis): **repita um padrão com números adjacentes**, ex. `2,2,3,2,2,3`. Curvas: **cada degrau menor que o anterior até a "quina"**, depois o inverso (degraus crescendo). Degraus de linha **sempre se conectam na diagonal**; quinas em "L" criam um ponto mais grosso na linha. **Quadrados não intencionais:** pixels tendem a formar quadrados grandes quando adjacentes — distribua cores em padrão de "tijolo" e procure sempre "quadrados imaginários". — https://saint11.art/img/pixel-tutorials/Fundamentals2.gif
- **F-16 [FONTE]** Curvas em degraus do tipo `1,1,2,3` ou `2,1,2`; formas angulares com degraus de 90° e 45°. — https://www.androidarts.com/pixtut/pixelart.htm
- **F-17 [FONTE]** Fluxo "pixel-perfect": começar com linha suja → limpar quinas indesejadas → corrigir linhas de 2 px → trocar padrões irregulares. Pixels são quadrados e afiados: use isso para pontas; quinas "erradas" às vezes servem para adicionar detalhe em baixa resolução. — https://saint11.art/img/pixel-tutorials/Outlines.gif
- **F-18 [SÍNTESE]** Para linhas geradas por código: use Bresenham e depois aplique (a) remoção de "dobras em L" (em cada bloco 2×2, se houver 3 pixels da linha, remova o do canto que não quebra a conectividade 8-vizinhos); (b) para inclinações próximas de 1:2, 1:3, 2:1… force runs constantes (slopes "limpos": 1:1, 1:2, 2:1, 1:3, 3:1, 1:4); (c) para curvas (círculos/arcos), gere com o algoritmo de ponto-médio e verifique a monotonicidade dos comprimentos de run por octante.

### 1.4 Anti-aliasing (AA)

- **F-19 [FONTE]** **Nunca** AA automático: "certifique-se de que não há anti-aliasing aplicado. Isso vale para todas as operações em pixel art"; pincéis suaves contradizem o conceito. — https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics
- **F-20 [FONTE]** AA manual (Pixel Parmesan):
  1. o **valor percebido** do pixel de AA reflete a **cobertura** da linha no pixel vizinho (≈50% → valor ~a meio caminho; ≈25% → mais perto do fundo);
  2. **não** faça média simples de cor (fica "lamacento", sobretudo com complementares): case o *valor*, puxe o *matiz* para um dos extremos; reutilize cores já existentes no sprite;
  3. "**quanto mais longo o segmento, mais longo o AA**"; segmentos longos aceitam AA empilhado com 2+ tons, mais pixels do tom mais próximo da linha;
  4. evite AA na **borda externa** (fica errado sobre outro fundo) — mantenha o AA **dentro** do sprite; para FX, use pixels semitransparentes;
  5. em sprites muito pequenos AA vira ruído; pergunta-chave: "isso é realmente necessário?";
  6. banding: linhas paralelas de mesmo comprimento reforçam a grade (ver F-29).
  — https://pixelparmesan.com/anti-aliasing-fundamentals-for-pixel-artists
- **F-21 [FONTE]** "AA excessivo deixa a peça borrada e indistinta"; cada pixel deve contar. — https://www.androidarts.com/pixtut/pixelart.htm
- **F-22 [SÍNTESE]** Algoritmo de AA para Pillow: para cada pixel de borda entre a cor A (linha) e B (fundo interno) num degrau de comprimento `n ≥ 2`, adicionar `round(n/2)` pixels de AA no fim do run com a cor da paleta cujo L_OKLab fique mais perto de `L_B + c·(L_A − L_B)`, com `c` = cobertura estimada (0,5 no 1º pixel, 0,25 no 2º). Não aplicar AA: (a) em sprites ≤16 px; (b) na silhueta externa de sprites com fundo transparente; (c) em ícones de UI que precisam de bordas duras.

### 1.5 Outlines e sel-out

- **F-23 [FONTE]** Saint11 (Outlines): outlines **ocupam muito espaço** → evite-os em resolução muito baixa. Use-os para **separar formas**: a borda externa separa do fundo; a interna separa partes entre si e **pode ser mais clara**. **Outline seletivo**: use uma cor escura em vez de preto (outline mais suave); **remova o outline nas áreas claras**; use o outline para **reforçar o sombreamento**. — https://saint11.art/img/pixel-tutorials/Outlines.gif
- **F-24 [FONTE]** Processo: outline no **contorno externo dos objetos importantes**; outline também em coisas na frente do objeto, mesmo que sejam parte do mesmo objeto. — https://saint11.art/img/pixel-tutorials/Pipeline.gif
- **F-25 [FONTE]** Androidarts: preto para outlines inferiores/sombreados e outline mais claro em cima (sobretudo em volta de cor clara); efeitos brilhantes (sóis, plasma) com outline todo colorido ou sem outline; não pôr linha preta sob formas que tocam o chão; linhas internas pretas só onde a separação for necessária (senão separe por contraste de cor); **não fazer outline em volta de outline**, exceto escudos/auras. — https://www.androidarts.com/pixtut/pixelart.htm
- **F-26 [FONTE]** Outline só se o sprite precisar de separação do fundo; comece com uma cor e depois clareie/escureça trechos para casar com as cores adjacentes (= sel-out). — https://www.slynyrd.com/blog/2025/7/28/pixelblog-57-knights-monsters-amp-castles
- **F-27 [FONTE]** Projéteis: outline é quase obrigatório; **outline duplo (claro + escuro)** como "seguro"; outlines **brancos** em projéteis os separam dos sprites (que usam outline escuro) — e por isso os fundos evitam grandes áreas brancas/muito claras. — https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design
- **F-28 [SÍNTESE]** Algoritmo de sel-out: (1) gere a máscara de silhueta; (2) outline = pixels transparentes 4-vizinhos da máscara (1 px); (3) a cor de cada pixel de outline = tom 2 passos mais escuro da rampa do material interno adjacente (ou o tom mais escuro da paleta, se a rampa acabar); (4) no lado iluminado (produto escalar normal-da-borda·direção-da-luz > 0,5) use 1 passo mais escuro ou remova; (5) no lado da sombra/contato com o chão use a cor mais escura da paleta (não `#000`, ver C-10). Espessura: 1 px até 64 px de altura; outline de 2 px só em UI/ícones estilizados ou efeitos que precisam "saltar".

### 1.6 Banding, pillow shading e dithering

- **F-29 [FONTE]** **Banding** (definição operacional, TU Delft "Pixel Fixer", citando *Pixel Logic*, M. Azzi): ocorre quando **dois segmentos de cores diferentes com ≥2 px, adjacentes ao longo da aresta mais longa, têm extremidades alinhadas**. Não é banding: segmento degenerado, segmentos que só compartilham a aresta curta, segmentos desalinhados. **Pillow shading**: sombreamento em camadas concêntricas que seguem o contorno (quase) perfeitamente — "tem banding quase em todo lugar". Correção automática proposta: dividir o objeto em segmentos (horizontais e verticais) → detectar banding → redimensionar segmentos (encolher/expandir); para pillow: extrair camadas de sombra → transladar as camadas para quebrar a iluminação frontal → perturbar estocasticamente cada camada. — https://cse3000-research-project.github.io/static/38fffaaa7e934fdd5d9b8416b1ee386e/poster.pdf
- **F-30 [FONTE]** Banding chama atenção para as bordas entre campos de cor; correções: comprimir a mudança de valor (borda rápida), colocar a borda da banda num terminador de sombra natural, ou quebrar o gradiente em "tufos"; não adicione cores para suavizar gradiente por padrão. Pillow: gradiente radial para o centro deixa a forma desinteressante; construa valor e termine **abruptamente** contra outro gradiente para descrever a forma. — https://www.androidarts.com/pixtut/pixelart.htm
- **F-31 [FONTE]** Saint11 (Shading): "**comprima as bandas de cor** para que seja mais difícil ver os degraus"; evitar gradientes quando possível — faces de um volume são, na maioria, **uma cor sólida**; conceitos: luz principal, highlight, terminador, luz rebatida; **sombra projetada = borda dura; sombra própria = borda suave**. — https://saint11.art/img/pixel-tutorials/Shading.gif
- **F-32 [FONTE]** Dithering (Tsugumo): pixels alternados de duas cores sugerem a cor intermediária; funciona melhor quanto menores os pixels; para suavizar um gradiente, adicione 2 tons intermediários; também serve para textura (2 cores bastam para um piso rochoso); **pisos devem ter baixo contraste** (dither de alto contraste no chão faz o jogador perder o personagem). — https://web.cs.wpi.edu/~claypool/courses/frontiers-06/samples/pixel-artist/chapter6.htm
- **F-33 [FONTE]** Androidarts: dither com parcimônia, quando faz "trabalho duplo" (gradiente + textura); evitar em áreas que deveriam ser lisas. — https://www.androidarts.com/pixtut/pixelart.htm
- **F-34 [FONTE]** Matrizes de Bayer (ordered dithering): `M2 = 1/4·[[0,2],[3,1]]`; `M4 = 1/16·[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]`; `M8` 8×8 (valores 0–63; ver fonte); recursão `M2n = 1/(2n)²·[[4Mn, 4Mn+2],[4Mn+3, 4Mn+1]]`; transformação por pixel `c' = paleta_mais_próxima(c + r·(M(x mod n, y mod n) − 1/2))`, `r ≈ 255/N`. — https://en.wikipedia.org/wiki/Ordered_dithering
- **F-35 [SECUNDÁRIA]** Return of the Obra Dinn (Lucas Pope): o jogo começou com dithering Bayer; Pope criou depois uma variante *blue noise* porque ela "sobrevive muito melhor" a escala de tela e compressão de vídeo; e mapeou o padrão de dither numa esfera em volta da câmera para evitar que ele "se mova erraticamente" (flicker) entre frames. Lição para animação: **padrão de dither deve ficar preso ao mundo/objeto, não à tela**, senão cintila. — https://www.alanzucconi.com/?p=10365
- **F-36 [SÍNTESE]** Quando o gerador deve **dither** vs **cluster**: dither apenas (a) em transições de luz amplas de cenário (feixes, halos, névoa, fade de reflexo) com padrão **ordenado** (Bayer 4×4) entre **tons vizinhos da mesma rampa** (ΔL_OKLab ≤ 0,12); (b) em texturas (pedra, ferrugem) com dither esparso; (c) em transições de tela. Nunca dither em sprites ≤32 px, ícones, texto, bordas de UI, nem entre cores com ΔL > 0,25 (vira ruído). No resto, clusters sólidos com bandas comprimidas.


---

## 2. Cor: rampas, hue shifting, tamanho de paleta, paletas de referência

### 2.1 Rampas (regras de fonte)

- **C-01 [FONTE]** Rampa = conjunto de cores que funcionam juntas, **ordenadas por brilho**, e que **também deslocam o matiz** ao longo do comprimento. Números do Slynyrd: **9 amostras por rampa**; **+20° de matiz entre amostras** ("o máximo que uso"), com deslocamento **positivo** (fica mais quente conforme clareia); brilho sobe da esquerda para a direita, "normalmente nunca começa em 0, a não ser que eu queira preto", com **passos menores perto de 100%**; saturação **atinge o pico perto do meio** e "nunca vai a 100 nem a 0", com passos maiores nas pontas; cores claras perdem saturação, escuras carregam mais saturação; paleta "Mondo": **8 rampas a 45°** umas das outras (360/8) + neutros feitos duplicando o miolo da rampa (sem as colunas extremas), invertido e dessaturado (8×9 + 8×7 = 128 cores). Ajuste fino de S e B é feito no olho ("passos uniformes não dão bom resultado"). — https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes (espelho: https://www.gamedev.net/articles/visual-arts/color-palettes-r4964/)
- **C-02 [FONTE]** Saint11 (Shading): ao sombrear, mude **brilho e matiz**; mova o matiz em direção às regiões **mais escuras** (azul/violeta) ou **mais claras** (amarelo) do círculo cromático. — https://saint11.art/img/pixel-tutorials/Shading.gif
- **C-03 [FONTE]** Androidarts: não faça as pontas da rampa misturando preto e branco puros; desloque o matiz ("uma rampa preto-rosa-branco fica lamacenta e artificial"); evite rampas longas de cores totalmente saturadas; a frequência de cores saturadas na paleta deve casar com o quanto você as usa. — https://www.androidarts.com/pixtut/pixelart.htm
- **C-04 [FONTE]** Pixel Parmesan ("é tudo relativo"): a cor depende da luz e das cores vizinhas; **cinzas parecem o complemento relativo das cores ao redor** e servem de interpoladores neutros entre rampas; "quente/frio" é relativo — se a luz é mais quente que o objeto, as sombras parecem mais frias (e vice-versa); **escolha a cor da luz antes** de deslocar as cores; a sombra nem sempre é menos saturada ("o tom menos saturado pode não ser o mais escuro"); meios-tons têm o maior potencial de saturação; o pico de saturação depende do matiz (**amarelo em valores altos, vermelho no meio, azul em valores baixos**); luminância percebida: **azul a mais baixa, amarelo a mais alta**; na vida real ~5 passos (escala 1–10) entre luz e sombra, pixel art costuma precisar de **menos**; comprimir os fatores de modelagem para evitar banding; **distribuição**: uma cor principal na maior área, **acento em ~10–20% da imagem**, cor secundária de menor contraste no resto; o highlight/branco define o tom geral (amarelo é ótimo highlight; outros matizes precisam de saturação bem menor no highlight). — https://pixelparmesan.com/blog/color-theory-for-pixel-artists-its-all-relative
- **C-05 [FONTE]** Highlights: escolha poucos "sweet spots" e pode o resto; em materiais brilhantes "faço o highlight saltar com poucos pixels"; highlights em excesso puxam um vermelho para rosa e ele perde identidade. — https://www.androidarts.com/pixtut/pixelart.htm

### 2.2 Rampas profissionais medidas **[MEDIDO]**

Método: conversão HSV dos `.hex` oficiais do Lospec (rampas consecutivas da paleta). Apollo é de AdamCYounis (https://lospec.com/palette-list/apollo); Resurrect 64 é de Kerrie Lake (https://lospec.com/palette-list/resurrect-64); Endesga 32: https://lospec.com/palette-list/endesga-32.

| Rampa (escuro → claro) | Matiz H (°) | ΔH total | S (%) | V (%) |
|---|---|---|---|---|
| Apollo azul `#172038 #253a5e #3c5e8b #4f8fba #73bed3 #a4dddb` | 224, 218, 214, 204, 193, 178 | −46 | 59, 61, 57, 58, 45, 26 | 22, 37, 55, 73, 83, 87 |
| Apollo verde `#19332d #25562e #468232 #75a743 #a8ca58 #d0da91` | 166, 131, 105, 90, 78, 68 | −98 | 51, 57, 62, 60, 56, 33 | 20, 34, 51, 65, 79, 85 |
| Apollo marrom `#4d2b32 #7a4841 #ad7757 #c09473 #d7b594 #e7d5b3` | 348, 7, 22, 26, 30, 39 | +51 | 44, 47, 50, 40, 31, 23 | 30, 48, 68, 75, 84, 91 |
| Apollo laranja `#341c27 #602c2c #884b2b #be772b #de9e41 #e8c170` | 332, 0, 21, 31, 36, 40 | +68 | 46, 54, 68, 77, 71, 52 | 20, 38, 53, 75, 87, 91 |
| Apollo vermelho `#241527 #411d31 #752438 #a53030 #cf573c #da863e` | 290, 327, 345, 0, 11, 28 | +98 | 46, 55, 69, 71, 71, 72 | 15, 25, 46, 65, 81, 85 |
| Apollo roxo `#1e1d39 #402751 #7a367b #a23e8c #c65197 #df84a5` | 242, 276, 299, 313, 324, 338 | +96 | 49, 52, 56, 62, 59, 41 | 22, 32, 48, 64, 78, 87 |
| Apollo cinza (10) `#090a14 … #ebede9` | 235 → 158 (frio→neutro) | — | 55 → 2 | 8, 12, 16, 22, 31, 47, 59, 71, 81, 93 |
| Resurrect 64 "fogo" `#ae2334 #e83b3b #fb6b1d #f79617 #f9c22b` | 353, 0, 21, 34, 44 | +51 | 80, 75, 88, 91, 83 | 68, 91, 98, 97, 98 |
| Endesga 32 "fogo" `#a22633 #e43b44 #f77622 #feae34 #fee761` | 354, 357, 24, 36, 51 | +57 | 77, 74, 86, 80, 62 | 64, 89, 97, 100, 100 |
| Endesga 32 "aço frio" `#181425 #262b44 #3a4466 #5a6988 #8b9bb4 #c0cbdc #ffffff` | 254, 230, 226, 220, 217, 216, — | −38 | 46, 44, 43, 34, 23, 13, 0 | 15, 27, 40, 53, 71, 86, 100 |
| Endesga 32 "pele/quente" `#3e2731 #733e39 #b86f50 #e4a672 #ead4aa` | 334, 5, 18, 27, 39 | +65 | 37, 50, 57, 50, 27 | 24, 45, 72, 89, 92 |

**Regras derivadas das medições** (C-06 a C-09):

- **C-06 [MEDIDO]** Rampas de 6 passos de paletas profissionais giram o matiz **45°–100°** do mais escuro ao mais claro (média ≈ 76°; ≈ 15°/passo). O deslocamento por passo é **maior nos escuros** (19°–37° nos 1–2 primeiros passos) e **menor nos claros** (4°–15°).
- **C-07 [MEDIDO]** Direção: ao clarear, o matiz caminha (pelo caminho mais curto) para **amarelo ≈ 40°–70°**; ao escurecer, para **azul-violeta ≈ 220°–290°** (ex.: vermelho começa em 290° e termina em 28°; verde 166° → 68°; azul 224° → 178°).
- **C-08 [MEDIDO]** Saturação: ponta escura **44–59%**, pico **57–77%** no meio/meio-alto, ponta clara **23–52%** (≈ 0,4–0,75 × pico). Rampas de fogo/VFX ficam saturadas até o topo (S 62–91%).
- **C-09 [MEDIDO]** Valor: tom mais escuro **V 15–30%** (nunca 0), mais claro **V 85–91%** (rampas de material) ou 98–100% (rampas de luz/fogo); incrementos de **13–20 pontos** na metade de baixo e **4–10** perto do topo.

### 2.3 Gerador de rampas (algoritmo) **[SÍNTESE]** (calibrado por C-01, C-06–C-09)

```python
import colorsys, math
def lerp_angle(a, b, k, cap):            # anda de a em direção a b pelo caminho mais curto
    d = (b - a + 540) % 360 - 180
    return (a + max(-cap, min(cap, d * k))) % 360

def make_ramp(h_mid, n=6, s_peak=0.66, s_dark=0.50, s_light_ratio=0.45,
              v_min=0.18, v_max=0.90, gamma=1.6,
              k=0.45, cap_light=35, cap_dark=45, hue_light=60, hue_dark=260):
    ramp = []
    for i in range(n):
        t = i / (n - 1)                                   # 0 = mais escuro
        v = v_min + (v_max - v_min) * (1 - (1 - t) ** gamma)   # passos grandes embaixo, pequenos em cima
        if t <= 0.6: s = s_dark + (s_peak - s_dark) * math.sin(math.pi / 2 * t / 0.6)
        else:        s = s_peak * (1 - (1 - s_light_ratio) * ((t - 0.6) / 0.4) ** 1.5)
        if t >= 0.5: h = lerp_angle(h_mid, hue_light, k, cap_light * (t - 0.5) * 2)
        else:        h = lerp_angle(h_mid, hue_dark,  k, cap_dark  * (0.5 - t) * 2)
        r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
        ramp.append((round(r * 255), round(g * 255), round(b * 255)))
    return ramp
```

Saídas de exemplo (verificadas): `h_mid=0` → `#2e1728 #652a45 #943644 #bb4e40 #d88d65 #e5c0a1` (ΔH por passo 18,18,16,14,6; L_OKLab 0,24→0,83); `h_mid=210` → `#171a2e #2a3265 #365794 #408cbb #65c6d8 #a1e5e0`; `h_mid=275` → `#22172e #462a65 #623694 #9640bb #d065d8 #e5a1da`.
**Validação obrigatória** após gerar: (a) |ΔH| entre vizinhos ≤ 22° (C-01); (b) L_OKLab estritamente crescente com **ΔL ≥ 0,06** entre vizinhos (senão dois tons ficam indistinguíveis); (c) S nunca 0 nem 100% (exceto branco puro de núcleo de VFX); (d) V_min ≥ 0,12.
Variações: rampas de **luz/fogo/magia** → `v_max = 1.0`, `s_light_ratio = 0.85`; rampas de **pedra gótica** → `s_peak = 0.25`, `s_dark = 0.30`, `k = 0.25` (matiz quase fixo, fria); **metal** → ver L-10 (claros mais frios/menos saturados, escuros mais quentes/saturados).

### 2.4 Quantas cores / quantos passos

- **C-10 [FONTE]** Cenário de fundo completo: limite autoimposto de **≤16 cores** (Valley/Desert/Forest com 15 cada) num canvas 192×144. — https://www.slynyrd.com/blog/2026/5/27/pixelblog-62-landscape-backgrounds
- **C-11 [FONTE]** Itens 16×16: "cada item tem cerca de **6 cores ou menos**"; tamanho do item = tamanho do tile do jogo (tiles 16×16 → itens 16×16). — https://www.slynyrd.com/blog/2019/12/21/pixelblog-24-items
- **C-12 [FONTE]** Estilo NES: sprites com **3 cores + 1 compartilhada**; ações cabendo em grade 16×16. — https://www.slynyrd.com/blog/2022/3/19/pixelblog-37-classic-castlevania-study
- **C-13 [FONTE]** Resoluções maiores costumam ter **mais cores**; ao reduzir a resolução você escolhe quais detalhes importam. — https://saint11.art/img/pixel-tutorials/Resizing.gif
- **C-14 [FONTE]** Objetos distantes usam **menos cores** (e menos saturação/contraste). — https://www.slynyrd.com/blog/2018/11/16/pixelblog-11-landscape-pixeling
- **C-15 [FONTE]** Rampas de material reais em tutoriais: **gema = 7 papéis** (ponto de highlight, reflexo de highlight, highlight, meio-tom, sombra, refração da sombra, sombra profunda) — https://saint11.art/img/pixel-tutorials/gems.gif ; **metal = rampa de 5** com salto de contraste (vs. plástico de gradiente suave) — https://saint11.art/img/pixel-tutorials/Metal.gif ; **projétil = 4 tons por lado + núcleo** (borda escura fria → núcleo quente/claro) — https://saint11.art/img/pixel-tutorials/Bullets.gif
- **C-16 [SÍNTESE]** Orçamentos default para o gerador:

| Asset | Cores (sem transparência) | Passos por rampa |
|---|---|---|
| Ícone 16×16 | 4–6 | 3 (sombra/base/luz) + outline |
| Ícone 24×24 | 6–8 | 3–4 |
| Ícone 32×32 | 8–12 | 4 |
| Ícone 48×48 | 12–16 | 4–5 |
| Moldura de carta / painel 9-slice | 6–10 | 3–4 por material (metal, madeira, pedra) |
| Botão (todos os estados) | 5–8 | 3 + 1 cor de highlight |
| Efeito (VFX) individual | 4–6 + branco | 4–5 (rampa de luz) + 1–2 de fumaça |
| Cenário (fundo de batalha) | 16–24 | 2–3 para planos distantes; 4–6 para o primeiro plano |
| Paleta mestra do jogo | 32–64 | — |

### 2.5 Paletas de referência (Lospec) — estatística objetiva **[MEDIDO]**

Colunas: `L_min/L_max` = OKLab L da cor mais escura/clara; `esc%` = % de cores com L < 0,35; `roxo%` = % com H 245°–330° e S > 15%; `quente%` = % com H ≤ 60° ou ≥ 342° e S > 35%; `S̄` = saturação média; `contraste` = razão de contraste WCAG entre a mais clara e a mais escura.

| Paleta | n | L_min | L_max | esc% | roxo% | quente% | S̄ | contraste |
|---|---|---|---|---|---|---|---|---|
| Resurrect 64 | 64 | 0.27 | 1.00 | 8 | 17 | 33 | 0.52 | 15.2 |
| Apollo | 46 | 0.15 | 0.94 | 28 | 13 | 28 | 0.48 | 16.7 |
| Endesga 32 | 32 | 0.21 | 1.00 | 12 | 9 | 44 | 0.56 | 18.0 |
| Endesga 64 | 64 | 0.15 | 1.00 | 22 | 17 | 34 | 0.58 | 19.7 |
| Sweetie 16 | 16 | 0.23 | 0.97 | 6 | 6 | 19 | 0.52 | 15.3 |
| DawnBringer 16 | 16 | 0.17 | 0.93 | 12 | 12 | 25 | 0.47 | 15.7 |
| DawnBringer 32 | 32 | 0.00 | 1.00 | 12 | 12 | 31 | 0.45 | 21.0 |
| TwilioQuest 76 | 76 | 0.24 | 1.00 | 9 | 20 | 39 | 0.52 | 16.5 |
| Oil 6 | 6 | 0.29 | 0.97 | 17 | 17 | 0 | 0.28 | 13.3 |
| SLSO8 | 8 | 0.28 | 0.95 | 25 | 12 | 38 | 0.46 | 12.6 |
| AAP-64 | 64 | 0.12 | 1.00 | 17 | 9 | 27 | 0.47 | 20.2 |
| Journey | 64 | 0.14 | 1.00 | 36 | 31 | 28 | 0.69 | 19.7 |
| Gothic Bit | 8 | 0.17 | 0.93 | 38 | 0 | 0 | 0.19 | 15.5 |
| RPGVania | 32 | 0.26 | 0.96 | 16 | 19 | 34 | 0.58 | 14.4 |
| Gothic Temple | 14 | 0.00 | 1.00 | 14 | 14 | 43 | 0.31 | 21.0 |
| Horror Dark | 16 | 0.12 | 1.00 | 31 | 50 | 19 | 0.52 | 20.4 |
| Darkseed 16 | 16 | 0.00 | 0.99 | 38 | 6 | 6 | 0.36 | 20.5 |
| Grim32 | 32 | 0.19 | 0.56 | 41 | 22 | 12 | 0.29 | 4.0 |
| Bloodmoon21 | 9 | 0.14 | 0.64 | 56 | 33 | 56 | 0.86 | 5.3 |
| Midnight Ablaze | 7 | 0.13 | 0.75 | 57 | 29 | 14 | 0.79 | 8.4 |

Paletas com tag "gothic" no Lospec (Gothic Bit, Carver6, RPGVania, Gothic Temple, Dorian_Greenless, Horror Dark, Gotham-30): https://lospec.com/palette-list/tag/gothic

- **C-17 [SÍNTESE]** Recomendação para o jogo:
  - **Paleta mestra: Endesga 64 ou Apollo.** Ambas têm escuros profundos *não pretos* (`#0e071b` / `#090a14`, L 0,15), rampas roxas/violetas completas (Endesga 64: `#3b1443 #622461 #93388f #ca52c9`; Apollo: `#1e1d39 #402751 #7a367b #a23e8c #c65197 #df84a5`), rampa de fogo longa e cinzas frios em 7–10 passos (ideais para pedra).
  - **Resurrect 64**: os melhores roxos/carmins para *mid-tones* (`#45293f #6b3e75 #905ea9 #a884f3 #eaaded`; `#831c5d #c32454 #f04f78`), mas o mais escuro é `#2e222f` (L 0,27) — para noite gótica, acrescente 1–2 escuros (ex.: `#1a1020`, `#0e0a14`).
  - **DB32**: é a paleta das animações de explosão/fogo/magia do Saint11 (ver 2.6) e tem preto real (útil só para *contrast frames*).
  - **Grim32** tem contraste máx. 4:1 → serve só para planos muito distantes/neblina; **Bloodmoon21** (9 vermelhos) e **Midnight Ablaze** (7 carmins) servem como sub-rampas de sangue/magia demoníaca; **Gothic Bit** (8 cinzas frios, S̄ 0,19) como rampa de pedra.
- **C-18 [FONTE]** "Evite fundo 100% preto." — https://saint11.art/img/pixel-tutorials/Stars.gif

Hex completos (para colar no código) — fonte de cada lista: o próprio `.hex` do Lospec (`https://lospec.com/palette-list/<slug>.hex`):

```text
Resurrect 64 (64) — https://lospec.com/palette-list/resurrect-64
  #2e222f #3e3546 #625565 #966c6c #ab947a #694f62 #7f708a #9babb2 #c7dcd0 #ffffff #6e2727 #b33831 #ea4f36 #f57d4a #ae2334 #e83b3b
  #fb6b1d #f79617 #f9c22b #7a3045 #9e4539 #cd683d #e6904e #fbb954 #4c3e24 #676633 #a2a947 #d5e04b #fbff86 #165a4c #239063 #1ebc73
  #91db69 #cddf6c #313638 #374e4a #547e64 #92a984 #b2ba90 #0b5e65 #0b8a8f #0eaf9b #30e1b9 #8ff8e2 #323353 #484a77 #4d65b4 #4d9be6
  #8fd3ff #45293f #6b3e75 #905ea9 #a884f3 #eaaded #753c54 #a24b6f #cf657f #ed8099 #831c5d #c32454 #f04f78 #f68181 #fca790 #fdcbb0
Apollo (46) — https://lospec.com/palette-list/apollo
  #172038 #253a5e #3c5e8b #4f8fba #73bed3 #a4dddb #19332d #25562e #468232 #75a743 #a8ca58 #d0da91 #4d2b32 #7a4841 #ad7757 #c09473
  #d7b594 #e7d5b3 #341c27 #602c2c #884b2b #be772b #de9e41 #e8c170 #241527 #411d31 #752438 #a53030 #cf573c #da863e #1e1d39 #402751
  #7a367b #a23e8c #c65197 #df84a5 #090a14 #10141f #151d28 #202e37 #394a50 #577277 #819796 #a8b5b2 #c7cfcc #ebede9
Endesga 32 (32) — https://lospec.com/palette-list/endesga-32
  #be4a2f #d77643 #ead4aa #e4a672 #b86f50 #733e39 #3e2731 #a22633 #e43b44 #f77622 #feae34 #fee761 #63c74d #3e8948 #265c42 #193c3e
  #124e89 #0099db #2ce8f5 #ffffff #c0cbdc #8b9bb4 #5a6988 #3a4466 #262b44 #181425 #ff0044 #68386c #b55088 #f6757a #e8b796 #c28569
Endesga 64 (64) — https://lospec.com/palette-list/endesga-64
  #ff0040 #131313 #1b1b1b #272727 #3d3d3d #5d5d5d #858585 #b4b4b4 #ffffff #c7cfdd #92a1b9 #657392 #424c6e #2a2f4e #1a1932 #0e071b
  #1c121c #391f21 #5d2c28 #8a4836 #bf6f4a #e69c69 #f6ca9f #f9e6cf #edab50 #e07438 #c64524 #8e251d #ff5000 #ed7614 #ffa214 #ffc825
  #ffeb57 #d3fc7e #99e65f #5ac54f #33984b #1e6f50 #134c4c #0c2e44 #00396d #0069aa #0098dc #00cdf9 #0cf1ff #94fdff #fdd2ed #f389f5
  #db3ffd #7a09fa #3003d9 #0c0293 #03193f #3b1443 #622461 #93388f #ca52c9 #c85086 #f68187 #f5555d #ea323c #c42430 #891e2b #571c27
Sweetie 16 (16) — https://lospec.com/palette-list/sweetie-16
  #1a1c2c #5d275d #b13e53 #ef7d57 #ffcd75 #a7f070 #38b764 #257179 #29366f #3b5dc9 #41a6f6 #73eff7 #f4f4f4 #94b0c2 #566c86 #333c57
DawnBringer 32 (DB32) (32) — https://lospec.com/palette-list/dawnbringer-32
  #000000 #222034 #45283c #663931 #8f563b #df7126 #d9a066 #eec39a #fbf236 #99e550 #6abe30 #37946e #4b692f #524b24 #323c39 #3f3f74
  #306082 #5b6ee1 #639bff #5fcde4 #cbdbfc #ffffff #9badb7 #847e87 #696a6a #595652 #76428a #ac3232 #d95763 #d77bba #8f974a #8a6f30
DawnBringer 16 (16) — https://lospec.com/palette-list/dawnbringer-16
  #140c1c #442434 #30346d #4e4a4e #854c30 #346524 #d04648 #757161 #597dce #d27d2c #8595a1 #6daa2c #d2aa99 #6dc2ca #dad45e #deeed6
TwilioQuest 76 (76) — https://lospec.com/palette-list/twilioquest-76
  #ffffff #eaeae8 #cecac9 #abafb9 #a18897 #756276 #5d4660 #4c3250 #432641 #28192f #fb7575 #fb3b64 #c83157 #8e375c #4f2351 #351544
  #f74a53 #f22f46 #bc1642 #fcc539 #f87b1b #f8401b #bd2709 #7c122b #ffe08b #fac05a #eb8f48 #d17441 #c75239 #b12935 #fdbd8f #f0886b
  #d36853 #ae454a #8c3132 #542323 #a85848 #83404c #67314b #3f2323 #d49577 #9f705a #845750 #633b3f #7bd7a9 #52b281 #148568 #146756
  #22474c #102f34 #ebff8b #b3e363 #4cbd56 #2f8735 #0b5931 #97bf6e #899f66 #61855a #4c6051 #73dff2 #2abbd0 #315dcd #472a9c #a0d8d7
  #7dbefa #668faf #585d81 #45365d #f6bafe #d59ff4 #b070eb #7c3ce1 #dbcfb1 #a9a48d #7b8382 #5f5f6e
Oil 6 (6) — https://lospec.com/palette-list/oil-6
  #fbf5ef #f2d3ab #c69fa5 #8b6d9c #494d7e #272744
SLSO8 (8) — https://lospec.com/palette-list/slso8
  #0d2b45 #203c56 #544e68 #8d697a #d08159 #ffaa5e #ffd4a3 #ffecd6
AAP-64 (64) — https://lospec.com/palette-list/aap-64
  #060608 #141013 #3b1725 #73172d #b4202a #df3e23 #fa6a0a #f9a31b #ffd541 #fffc40 #d6f264 #9cdb43 #59c135 #14a02e #1a7a3e #24523b
  #122020 #143464 #285cc4 #249fde #20d6c7 #a6fcdb #ffffff #fef3c0 #fad6b8 #f5a097 #e86a73 #bc4a9b #793a80 #403353 #242234 #221c1a
  #322b28 #71413b #bb7547 #dba463 #f4d29c #dae0ea #b3b9d1 #8b93af #6d758d #4a5462 #333941 #422433 #5b3138 #8e5252 #ba756a #e9b5a3
  #e3e6ff #b9bffb #849be4 #588dbe #477d85 #23674e #328464 #5daf8d #92dcba #cdf7e2 #e4d2aa #c7b08b #a08662 #796755 #5a4e44 #423934
Journey (64) — https://lospec.com/palette-list/journey
  #050914 #110524 #3b063a #691749 #9c3247 #d46453 #f5a15d #ffcf8e #ff7a7d #ff417d #d61a88 #94007a #42004e #220029 #100726 #25082c
  #3d1132 #73263d #bd4035 #ed7b39 #ffb84a #fff540 #c6d831 #77b02a #429058 #2c645e #153c4a #052137 #0e0421 #0c0b42 #032769 #144491
  #488bd4 #78d7ff #b0fff1 #faffff #c7d4e1 #928fb8 #5b537d #392946 #24142c #0e0f2c #132243 #1a466b #10908e #28c074 #3dff6e #f8ffb8
  #f0c297 #cf968c #8f5765 #52294b #0f022e #35003b #64004c #9b0e3e #d41e3c #ed4c40 #ff9757 #d4662f #9c341a #691b22 #450c28 #2d002e
Gothic Bit (8) — https://lospec.com/palette-list/gothic-bit
  #0e0e12 #1a1a24 #333346 #535373 #8080a4 #a6a6bf #c1c1d2 #e6e6ec
RPGVania (32) — https://lospec.com/palette-list/rpgvania
  #312580 #3b42a1 #435cde #7aa3e6 #cce7ff #9db0cd #7679a0 #574473 #3d2157 #301939 #5e106c #872b59 #b1385c #f09190 #ffbcb8 #ffe7cf
  #f2cba7 #e6b183 #d98d52 #c7723e #9d5019 #3c1904 #78340a #ac4d00 #ffa319 #ffd21c #deffb5 #6ebc51 #4d9655 #3c8051 #27614e #143b3a
Gothic Temple (14) — https://lospec.com/palette-list/gothic-temple
  #ffffff #d6cdd4 #b4a8b6 #8e8496 #676375 #494151 #eeeeb4 #dcbf81 #dda082 #d88282 #c77b51 #7c3b17 #500d06 #000000
Horror Dark (16) — https://lospec.com/palette-list/horror-dark
  #050508 #0d0a12 #150f1e #221830 #352545 #4a3860 #6a5580 #9080a0 #b0ff60 #60dd20 #ff4040 #990000 #cc44ff #ff9900 #d0c8e0 #ffffff
Darkseed 16 (16) — https://lospec.com/palette-list/darkseed-16
  #000000 #001418 #002024 #002c38 #143444 #443444 #583c48 #6c4c44 #806058 #6c706c #888078 #a49484 #c4ac9c #d8b0a8 #ecd4d0 #fcfcfc
Grim32 (32) — https://lospec.com/palette-list/grim32
  #081611 #0f1e1d #162627 #213434 #2c413c #3e4e47 #515f4f #616854 #505641 #474932 #3d3b26 #34311f #231f13 #342d20 #453a2d #56473a
  #6c584d #867069 #6c5e61 #5f4c53 #52414a #382b34 #231921 #2e2430 #362f3d #403c49 #4a4856 #525363 #666875 #4e5763 #3e4852 #222b34
Bloodmoon21 (9) — https://lospec.com/palette-list/bloodmoon21
  #130310 #1d0518 #270721 #3c0921 #520b20 #7d0f1f #a8141d #d3181c #ff252b
Midnight Ablaze (7) — https://lospec.com/palette-list/midnight-ablaze
  #ff8274 #d53c6a #7c183c #460e2b #31051e #1f0510 #130208
Dorian_Greenless (24) — https://lospec.com/palette-list/doriangreenless
  #1c0f10 #2b1102 #4c1302 #660f00 #862102 #c35e26 #fb8b41 #ffb766 #ffda83 #be7b20 #9f7d33 #6f460e #583000 #391f04 #2a2209 #171b15
  #29342e #5e605f #6d7e74 #a2b2a8 #d2d5c6 #ffe7bd #e0b38c #b57b4d```

### 2.6 Cores efetivamente usadas por um profissional em VFX/materiais **[MEDIDO]**

Amostragem por pixel (todas as frames) dos GIFs de tutorial do Saint11. As cores batem com DB32 (explosão/fogo/magia sombria) e Endesga 32 (projéteis/magia de luz/materiais).

| Uso | Cores (escuro/frio → claro/quente, salvo indicado) | Fonte |
|---|---|---|
| Explosão + fogo (DB32) | núcleo `#ffffff` → `#fbf236` (H57 S78 V98) → `#df7126` (H24 S83 V87) → `#ac3232` (H0 S71 V67) → **fumaça** `#3f3f74` (H240 S46 V45) → `#222034` (H246 S38 V20) | https://saint11.art/img/pixel-tutorials/Explosion.gif , https://saint11.art/img/pixel-tutorials/Fire.gif |
| Magia sombria — barra "cold→warm" | `#639bff #99e550 #76428a #c327ff #3f3f74 #000000 #9badb7 #ffffff #fbf236 #ac3232` ("muitas complementares, alto contraste e roxo"); no painel do efeito: fundo `#222034`, efeito `#76428a #d77bba #99e550 #ffffff` + círculo `#000000` | https://saint11.art/img/pixel-tutorials/DarkMagic.gif |
| Magia de luz/sagrada — "cold→warm" | `#3e8948 #63c74d #ffffff #2ce8f5 #0095e9 #124e89 #e43b44 #f77622 #feae34 #fee761` ("análogas, claras e saturadas") | https://saint11.art/img/pixel-tutorials/LightMagic.gif |
| Projétil de fogo (simétrico) | `#9e2835 #f77622 #feae34 [#fee761] #feae34 #f77622 #9e2835` | https://saint11.art/img/pixel-tutorials/Bullets.gif |
| Projétil azul | `#124e89 #0095e9 #2ce8f5 [#ffffff] …` (espelhado) | idem |
| Projétil verde | `#265c42 #3e8948 #63c74d [#fee761] …` (núcleo amarelo = mais quente) | idem |
| Holograma/fantasma ("cores frias") | `#2ce8f5 #0095e9 #124e89 #262b44 #68386c #b55088 #c4686c` | https://saint11.art/img/pixel-tutorials/Holograms-Ghosts.gif |
| Metal (rampa) | `#121a22 #293941 #3a4466 #5a6988 #c0cbdc` | https://saint11.art/img/pixel-tutorials/Metal.gif |
| Gema vermelha | `#3f2832 #9e284b #e43b44 #ff596a #ff97b1 #ffffff` | https://saint11.art/img/pixel-tutorials/gems.gif |
| Arco de espada (smear/slash) | `#cbdbfc` (branco-azulado frio, H220 S19 V98) | https://saint11.art/img/pixel-tutorials/Swords.gif |
| Paredes de interior ("baixa saturação, baixa temperatura") | `#745f7b #615f7b #5f737b #5f7b68 #727b5f #7b5f75` (S ≈ 20–25%, V ≈ 48%) | https://saint11.art/img/pixel-tutorials/indoors.gif |
| Móveis/detalhes de primeiro plano ("alta saturação, cores claras, alto contraste") | `#743f39 #be4a2f #e43b44 #0095e9 #3e8948 #f77622 #ead4aa #b86f50 #f7e022 #63c74d #ffffff` | idem |

- **C-19 [FONTE]** Fundo vs. primeiro plano (interiores): paredes/fundo com **baixa saturação e baixa temperatura**, evitar mudar demais o matiz (esquema de 2 cores complementares), mas **variar levemente o matiz das paredes**; pôsteres/quadros com **baixo contraste e poucas cores**; móveis e detalhes de primeiro plano com **alta saturação, cores claras e alto contraste**; "loops longos e lentos são ótimos para criar clima"; "flicker de luz muito sutil". Processo: bloquear → luz simples → esculpir detalhes → props menores. — https://saint11.art/img/pixel-tutorials/indoors.gif
- **C-20 [FONTE]** Legibilidade por cima de fundo: Slynyrd baixou **saturação −20, contraste −15 e subiu brilho +15** (Aseprite) em todas as camadas de fundo, exceto a grama próxima, e isso melhorou profundidade e legibilidade (cena diurna). — https://www.slynyrd.com/blog/2026/7/26/pixelblog-63-horizontal-shmup
- **C-21 [FONTE]** Em fundos escuros: "uso **só uma cor** para manter contraste baixo" nas coisas do fundo; misture áreas escuras ao fundo para o espectador completar com a imaginação. — https://saint11.art/img/pixel-tutorials/Darkness.gif
- **C-22 [FONTE]** Hyper Light Drifter (Alx Preston): "Eu amava pensar em **cor e silhueta** mais que tudo"; "**contraste e clima** são muito importantes e têm grande efeito na primeira impressão"; "mesmo em baixa resolução, ser **fácil de ver** era o mais importante"; "usar **cores escuras** nos deixou expressar uma sensação irreal". — https://automaton-media.com/articles/interviewsjp/20170525-47328/

### 2.7 Bandas de valor para cenas góticas escuras **[SÍNTESE]**

Baseado em C-04 (acento 10–20%), C-14/C-19/C-20/C-21 (fundo menos saturado/contrastado), C-18 (sem preto puro) e C-22.

| Banda | Uso | L_OKLab | S (HSV) | Matiz |
|---|---|---|---|---|
| B0 "vazio" | céu/abóbadas no escuro, sombras profundas | 0,12–0,20 | 25–50% | azul-violeta 240°–280° (nunca `#000`) |
| B1 "arquitetura distante" | naves laterais, colunas ao fundo | 0,18–0,32 | ≤ 25% | frio (230°–290°) |
| B2 "arquitetura média / piso" | colunas próximas, chão | 0,28–0,45 | 15–35% | frio a neutro |
| B3 "jogo" | personagens, cartas, objetos interativos | 0,35–0,80 (contraste interno alto) | 35–75% | livre |
| B4 "luz e acento" | vitrais, fogo, VFX, runas, highlights | 0,70–1,00 | 60–95% (branco no núcleo) | quente (fogo/ouro) ou joia (vitral) |

Teste: B4 deve ocupar **10–20%** da área (C-04); a silhueta de B3 deve ter **ΔL ≥ 0,20** em relação ao fundo imediato; núcleos de VFX **L ≥ 0,85**.


---

## 3. Luz e sombreamento

- **L-01 [FONTE]** Defina a fonte de luz "logo no início de qualquer ilustração"; luz de cima é a mais natural; o autor costuma pôr a luz principal **no alto à esquerda ou à direita**; pode haver várias fontes com intensidades diferentes; ar enevoado → sombras projetadas suaves; ar limpo → sombras duras e escuras; sem atmosfera → sombras alongadas e "afiadas como navalha". — https://www.slynyrd.com/blog/2018/6/15/pixelblog-6-light-and-shadow
- **L-02 [FONTE]** Iluminação de 3 pontos: **key** (luz principal; projeta a sombra principal), **fill** (suaviza sombras), **rim** (cria um contorno fino que separa o objeto do fundo). **Contre-jour**: contraluz forte esconde detalhes e emoldura o objeto no centro. **De baixo para cima**: ótimo para horror e tensão, forte em rostos, **luzes coloridas** funcionam muito bem. **Contraste de fundo**: escureça o fundo **do lado iluminado** do objeto central; mantenha a contraluz do lado iluminado, senão "a luz parece errada". **Hue shift**: mude o matiz quando mudar a quantidade de luz; use **cores de luz complementares** para contraste forte. **Luz volumétrica**: cones de luz só são visíveis se houver **poeira ou fumaça**; o cone é **mais claro no meio**. "Use fotos de referência quando possível." — https://saint11.art/img/pixel-tutorials/IlluminationTechniques.gif
- **L-03 [FONTE]** Magia sombria: "**luz de baixo** — esse ângulo parece antinatural e estranho, e é exatamente o que queremos". Magia sagrada: "**luz de cima** transmite coisas divinas e celestiais". — https://saint11.art/img/pixel-tutorials/DarkMagic.gif , https://saint11.art/img/pixel-tutorials/LightMagic.gif
- **L-04 [FONTE]** Escuridão (processo): forma geral → luz/sombra → **pontos de luz fortes** → **rim/back light forte**; sombras e silhuetas podem assustar mais que a coisa em si; foque nos detalhes importantes; encontre a sombra traçando **2 linhas imaginárias da fonte de luz até as bordas do objeto**; mantenha a direção da luz **sempre consistente**; use sombras para mostrar profundidade. — https://saint11.art/img/pixel-tutorials/Darkness.gif
- **L-05 [FONTE]** Metal: processo forma geral → luz base → sombra base → contraluz e especular → reflexo/interferência; **claros geralmente mais frios e menos saturados; escuros mais quentes e mais saturados**; metal é muito reflexivo → "espere uma **contraluz forte**"; arranhões contam história; mais ou menos brilhante conforme uso/conservação; metal é rígido (não estica, mas as partes se movem separadas); o brilho/reflexo deve ser animado conforme o ângulo; para reflexos fáceis, faça **várias linhas de luz/sombra**. — https://saint11.art/img/pixel-tutorials/Metal.gif
- **L-06 [FONTE]** Gemas: esboço marcando facetas → remover linhas → sombreamento básico → refração (um pouco aleatória, cuidado com ruído); na animação de brilho, **cada faceta brilha inteira**, a luz nos frames do meio cobre uma área **muito maior**; em superfícies lisas o brilho é arredondado e se move com a **mesma easing**. — https://saint11.art/img/pixel-tutorials/gems.gif
- **L-07 [FONTE]** Falloff de luz pontual com dither (shader 2D "retro dithered lighting"): `falloff = 1 − smoothstep(r·softness, r, d)` com `softness = 0,30`; soma das luzes + ambiente (0,05), `lit = pow(lit, 1.6)`; quantização em **6 níveis** com limiar de **Bayer 8×8**: `banded = floor(lit·6 + bayer)/6`; bloco de dither de 2 px; flicker **só escurece**: `1 − flicker·rand()`; escuridão padrão `(0.02, 0.02, 0.06)` (azulada, não preta). — https://godotshaders.com/shader/2d-retro-dithered-lighting-fog-of-war/
- **L-08 [FONTE]** Luz de tocha "à mão" (PICO-8, *Dank Tomb*, Jakub Wasilewski): multiplicar o raio por um fator aleatório por frame faz a luz inteira "piscar" demais; melhor **um fator aleatório por linha horizontal**; o banding entre níveis de luz foi resolvido com **dither temporal** (bordas mudam a cada frame) + dither espacial só em segmentos verticais; paredes escurecem **1 nível da paleta a cada 2 px** atrás do personagem; o resultado inicial com paleta neutra parecia "luz fluorescente de escritório" → precisou de tons quentes. — https://hackernoon.com/lighting-by-hand-3-breath-of-life-7a775617697e
- **L-09 [SÍNTESE] Algoritmo de poça de luz quente (tocha/forja) em Pillow:**
  1. `d` = distância ao centro da fonte (em px nativos, opcionalmente elíptica: `dy·1.6` para simular perspectiva do chão);
  2. `I = (1 − smoothstep(0.3r, r, d)) ** 1.6` (L-07);
  3. quantizar `I` em **4–6 níveis**; somar o limiar Bayer 4×4 (`M4/16 − 0.5`)·(1/níveis) **só numa faixa de ±1 nível** em torno de cada fronteira (evita banding sem sujar a área toda);
  4. cada nível mapeia para **um passo da rampa** do material (não multiplique RGB): nível 0 = cor base em B1/B2; níveis altos andam na rampa em direção ao laranja/amarelo (C-06/C-07);
  5. flicker por frame: `r_f = r·(1 − 0.06·u)`, `u ~ U(0,1)` (só diminui, L-07) + jitter de ±1 px por linha (L-08); 4–8 frames de 80–120 ms, em loop **não** perfeitamente periódico (sorteie a ordem) para não "pulsar".

---

## 4. Animação: timing, easing, impacto

### 4.1 Princípios com regras explícitas

- **A-01 [FONTE]** Easing (Saint11): "easing é tudo sobre aceleração"; nada se move linearmente na vida real — movimento linear é "chato"; slow in/out (acelera/desacelera) e "gosto de **distorcer o frame do meio**"; back in/out = **antecipação e overshoot**, especialmente útil para ataques e movimentos fortes; "às vezes até **pulo o frame do meio** para deixar o movimento mais forte"; a **distância entre desenhos** dá a sensação de aceleração; rastro (trail) é bom para movimento rápido. — https://saint11.art/img/pixel-tutorials/Easings.gif
- **A-02 [FONTE]** Anatomia de um impacto: **idle → antecipação → movimento → overshoot → repouso**. Exagero: motion blur, partículas de fumaça, estilhaços/debris, coisas afetadas pela gravidade. A antecipação torna o golpe mais forte; o alvo deve **quicar/reagir**; **tremer câmera e alvo**. "Corte esses frames": remova frames entre o repouso e a posição-alvo para um movimento mais rápido e forte, e use **muito motion blur**. **Freeze**: "gosto de pausar **um frame antes do impacto**", sem exagerar a pausa, e só para impactos muito exagerados. — https://saint11.art/img/pixel-tutorials/Impact-export.gif
- **A-03 [FONTE]** Ataques com espada em 3 partes: **wind-up** (melhor para NPCs; normalmente evitado no personagem do jogador), **overshot** (exagerado, motion blur, efeito de vento = o *slash arc*), **recover** (cuidado com pés/pernas; **a parte mais longa e lenta**). — https://saint11.art/img/pixel-tutorials/Swords.gif
- **A-04 [FONTE]** Ataque simples: **3 frames de ataque + 4 frames de volta ao idle**; "é importante que **não haja frame de antecipação**, senão o jogador sente input lag"; o último frame é um **bounce** (vai mais para trás que o frame 1). GIF medido: 300 ms no idle, 100 ms nos demais. — https://saint11.art/img/pixel-tutorials/AttackSheet.gif
- **A-05 [FONTE]** Slynyrd (golpes corpo a corpo): armas pesadas (maça, machado de 2 mãos) têm antecipação e recuperação **mais lentas**; antecipação demais gera "input lag desagradável"; "**normalmente um único smear frame resolve**"; gradação de cor no smear dá suavidade sem frames extras; o follow-through fica "um pouco mais" que os outros frames; overshoot: desloque a base **1 px por 1 frame** (bounce); freeze de "alguns frames extras" só para ações exageradas; espada cobrindo um arco de 90° (de cima da cabeça até a frente). — https://www.slynyrd.com/blog/2018/9/8/pixelblog-9-melee-attacks
- **A-06 [FONTE]** Ataques top-down (Slynyrd 56): **6 frames** em todas as 8 direções; antecipação 1 frame, smear em vários frames curtos, rebound 1 frame (só martelo), follow-through 1, recover 1; **não usar smear em antecipação nem em recover**. Tempos (ms): **espada 100, 50, 50, 50, 100, 50 (= 400)**; **lança 200, 50, 50, 50, 150, 50 (= 550)**; **martelo 250, 50, 50, 50, 300, 100 (= 800)**. — https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation
- **A-07 [FONTE]** Socos e chutes (Slynyrd 53): jab de 5 frames = smear, hit, follow-through, recover, overshoot (sem windup; a pose de golpe "é praticamente atingida no smear"); cross de 7 frames com load + pull antes; o frame de **hit é segurado um pouco mais**; round kick com **delay extra, screen shake e hit effect mais pesado começando no frame de hit**. — https://www.slynyrd.com/blog/2024/11/25/pixelblog-53-punches-and-kicks
- **A-08 [FONTE]** Ciclos: "cada pose do ciclo de 8 frames dura **80 ms**; cada pose do ciclo de 4 frames dura **160 ms**" (mesma energia); "ciclos de **6 frames** funcionam bem na maioria dos casos"; para reduzir frames, remova primeiro os que não são keyframes. — https://www.slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation
- **A-09 [FONTE]** Smear: na TV, 1 frame resolve (2 só para ação "realmente violenta"); em jogos, 1–2 frames; ponha **entre duas poses-chave fortes, não na pose de impacto**; amarre ao **arco** do movimento (smear que ignora o caminho parece glitch); pode distorcer o interior, mas **o contorno externo ainda deve "dizer quem é"**; tipos: in-between alongado, múltiplos (partes duplicadas ao longo do caminho — mais limpo quando a legibilidade importa), drybrush/linhas de movimento. — https://prolificstudio.co/blog/smear-frames/
- **A-10 [FONTE]** Motion blur: deixa o movimento mais fluido e natural (mesmo lento); **cores claras "sangram" sobre as escuras; cores escuras são usadas para o fade**; animação muito rápida → **flash de cores complementares** para misturá-las ("sensação muito dinâmica"); o blur "borra a imagem como se tentasse conectá-la ao frame anterior"; é um jeito barato de mostrar movimento complicado. — https://saint11.art/img/pixel-tutorials/MotionBlur.gif
- **A-11 [FONTE]** Squash & stretch: "massa nunca muda — ao mudar a largura, mude a altura" (regra mais importante); stretch é barato para suavizar animações rápidas; a preparação **achata na direção oposta** à ação; material importa (objetos rígidos deformam pouco); combine com motion blur; ponha tweens de squash/stretch no código. Sequência: prepare (achatado) → salto (esticado) → freio → prepare → recover. — https://saint11.art/img/pixel-tutorials/Squash.gif
- **A-12 [FONTE]** Movimento < 1 px (sub-pixel): mova uma parte primeiro (passos demais deixam o objeto "torto"); crie um pixel extra e deslize-o pela linha; mova o interior antes/depois da silhueta; use cor escura perto das bordas; **faça fade de cores** para ilusão de < 1 px; cuidado: cores demais deixam tudo borrado; **mova principalmente a luz, evite mover formas** (a silhueta quase não muda). — https://saint11.art/img/pixel-tutorials/Subpixel.gif
- **A-13 [FONTE]** Levar dano/morrer: o **primeiro frame é o mais forte** (joga o personagem todo para trás); recupera devagar ao idle; esmaecer sangue e efeitos; "hit animation": o impacto é questão de **easing correta**, **overshoot no primeiro frame**, o impacto usa **um frame só**, recuperação lenta; inimigos pequenos: *squish* conservando massa, *contrast frame* (frame preto para mais contraste), explosão; ao cair: braços atrasam, overshoot no chão (+1 px para baixo), quique do braço, repouso. — https://saint11.art/img/pixel-tutorials/Death.GIF

### 4.2 Hit-stop (hitlag) e "freeze"

- **A-14 [FONTE]** Sakurai (Smash): atacante e vítima congelam **pelo mesmo tempo**; mais dano → hitstop maior (com teto); ataques elétricos têm modificador maior; projéteis têm menos; durante o hitstop a vítima **treme**, **de um lado para o outro se estiver no chão e para cima/baixo se estiver no ar**, com amplitude que **começa grande e diminui até o fim**; o atacante também vibra levemente; a pose de dor é misturada em **4 frames** durante o hitstop. — https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/
- **A-15 [FONTE]** Fórmulas (frames @60): Melee `⌊⌊⌊d/3 + 3⌋·e⌋·c⌋`, teto **20**; Brawl/Smash 4 `⌊⌊(d·0,3846154 + 5)·h·e⌋·c⌋`; Ultimate `⌊⌊⌊(d·0,65 + 6)·h·e·s⌋·p⌋·c⌋`; teto **30** de Brawl em diante; `e` = 1,5 para elétrico; `d` = dano. Ex.: 10 de dano no Ultimate → 12 frames (200 ms). — https://www.ssbwiki.com/Hitlag
- **A-16 [SECUNDÁRIA]** Vlambeer, "The Art of Screenshake" (Jan Willem Nijman): lista de ajustes cronometrada por um espectador inclui *sleep* (pausa momentânea ao acertar o inimigo), *permanence* (cadáveres/cápsulas/fumaça ficam na tela), *camera kick* (câmera no sentido oposto ao tiro), *gun kickback*, *muzzle flash*, *bigger bullets*, *impact effects*, *hit animation*, *enemy knockback*, *screen shake*, *random explosion*. Um comentarista atribui ao autor um `sleep(20)` em cada morte de inimigo (não verificado). — https://theengineeringofconsciousexperience.com/jan-willem-nijman-vlambeer-the-art-of-screenshake/ ; contexto: https://gamedeveloper.com/design/vlambeer-co-founder-shares-advice-on-building-better-action-games

### 4.3 Frame rate e holds

- **A-17 [FONTE]** Dead Cells: animações a **30 FPS** (renderizadas de 3D); personagem com ~**50 px** de altura. — https://habr.com/post/416589 (tradução do artigo de Thomas Vasseur "Art Design Deep Dive: Using a 3D pipeline for 2D animation in Dead Cells", Game Developer/Gamasutra)
- **A-18 [FONTE]** GIF de exemplo com hold de **50 ms (20 fps)** por limitação do formato; num jogo, mire **≥ 60 fps** de renderização. — https://www.slynyrd.com/blog/2026/7/26/pixelblog-63-horizontal-shmup
- **A-19 [SECUNDÁRIA]** 12 fps (≈ 83 ms) é o default de consenso para pixel art; 24 fps raramente compensa o dobro de trabalho. — https://divoom.com/blogs/setup-ideas/pixel-art-animation-frame-rate
- **A-20 [SECUNDÁRIA]** Tabela de referência (ms/frame): idle 2–4 f × 300–500; walk 4–6 f × 100–150; run 6–8 f × 60–100; wind-up 1–2 f × 60–80; **impacto 1–2 f × 120–200 (segurado)**; recovery 1–2 f × 80–100; apex de pulo 1 f × 120–180; "durações uniformes são o erro mais comum". — https://www.sprite-ai.art/guides/animation-principles
- **A-21 [FONTE]** Loops: no fogo, ao chegar ao último frame "continue como se o primeiro frame fosse o próximo" (desenhe o loop pensando na emenda) — https://saint11.art/img/pixel-tutorials/Fire.gif ; elementos em loop sobrepostos precisam ter **contagem de frames que divide** o total do loop maior — https://www.slynyrd.com/blog/2019/11/12/pixelblog-23-parallax-scrolling
- **A-22 [FONTE]** Animações de "idle" para itens: itens flutuantes **oscilam (bob)**, itens no chão **quicam**; moedas **brilham**; power-ups oscilam; rotação é complexa demais, salvo itens simples; feedback ao pegar: brilhos pequenos variados + aleatoriedade; "quanto mais importante o item, mais especial o feedback". — https://www.slynyrd.com/blog/2019/12/21/pixelblog-24-items
- **A-23 [FONTE]** Fantasmas/hologramas flutuam com uma **senóide** aplicada ao objeto inteiro: `y = sin(time)`. — https://saint11.art/img/pixel-tutorials/Holograms-Ghosts.gif

### 4.4 Durações medidas nos tutoriais do Saint11 **[MEDIDO]**

Metadado `duration` de cada frame dos GIFs (Pillow). Representa a cadência escolhida pelo artista para demonstrar o efeito.

| GIF | Frames | ms/frame | Observação |
|---|---|---|---|
| Explosion | 20 | 80 | linha do tempo do tutorial: 14 frames (ver VFX-01) |
| Fire | 30 | 100 | loop de fogo (10 fps) |
| SmokeSheet | 40 | 100 | fumaça |
| Impact-export | 27 | 80 (último 20) | impacto |
| DarkMagic | 34 | 60 | magia sombria (mais rápida/caótica) |
| LightMagic | 30 | 70 | magia de luz |
| Electric | 15 | 80 (um frame de 110) | eletricidade "deve ser rápida" |
| Blood | 27 | 80 | sangue |
| Death | 22 | 100 | dano/morte |
| Glitch | 14 | 60 | glitch |
| Bullets | 20 | 60 | projéteis |
| RocketTrail | 40 | 60 | propulsão |
| MotionBlur | 32 | 80 | blur |
| Squash | 19 | 80 | squash & stretch |
| Shine (UI) | 44 | **500** (pausa) → 9×**80** (varrida) → **200** (hold) | ciclo de brilho de UI ≈ 1,42 s |
| AttackSheet | 36 | 300 (idle) + 100 | ataque |
| indoors | 40 | 140 | loops lentos de ambiente |

### 4.5 Defaults de timing para o jogo **[SÍNTESE]** (de A-04…A-23 e 4.4)

| Ação | Frames | ms/frame | Total |
|---|---|---|---|
| Flash de contraste/branco de VFX | 1 + 1 | 40–60 | ~100 ms |
| Explosão pequena | 6–8 | 60–80 | 0,4–0,6 s |
| Explosão grande | 12–16 | 60–80 (fumaça final 100) | 0,9–1,3 s |
| Slash arc | 3–4 | 40–60 | 0,15–0,25 s |
| Raio/eletricidade | 6–8 (com 1–2 frames em branco) | 50–80 | 0,4–0,6 s |
| Fogo/tocha (loop) | 6–8 | 90–110 | 0,6–0,9 s |
| Brasa/faísca (vida) | 3–8 | 60–100 | — |
| Shine sweep em botão/carta | 6–9 | 50–80 + pausa 1–3 s | — |
| Hit-stop ao acertar carta/unidade | 4–12 frames @60 | 66–200 ms (proporcional ao dano, teto 30 f) | — |
| Hit flash branco | 1–3 frames @60 | 16–50 ms | — |
| Transição de tela | 16–30 frames @60 (ou 8–12 passos de 33–50 ms) | 0,25–0,5 s | — |
| Idle de ícone/carta lendária | 4–8 | 120–200 | loop de 1–2 s |


---

## 5. VFX (sprite sheets de efeitos)

### 5.1 Explosões

- **VFX-01 [FONTE]** Saint11 ("Explosions part 1"): "penso em explosões **em camadas** e animo cada uma separadamente": **FLASH → BLAST → FIRE → SMOKE**. Linha do tempo do tutorial (14 frames): **flash f1–f2; blast f3–f5; fogo f4–f10; fumaça f4–f14** (camadas sobrepostas). Passos: (1) **contrast flash** — um frame escuro (disco quase preto) "faz os outros frames parecerem mais claros"; (2) **white flash** — "às vezes adiciono estilhaços ou linhas de luz"; (3) **sharp blast** — **ângulos agudos, evitar ruído**; (4+) **fade** — **o fogo some rápido, a fumaça some devagar**. "Esse estilo precisa de **pelo menos 4 frames**; mais frames deixam mais suave." "O fogo da explosão é como **bolhas**; **o centro é mais claro e mais quente**." Atenção ao entorno (a forma se adapta a parede/chão); pode-se lançar **pedaços voando depois** da explosão; **várias explosões encadeadas** para um efeito longo. GIF a 80 ms/frame. — https://saint11.art/img/pixel-tutorials/Explosion.gif
- **VFX-02 [FONTE]** Slynyrd (shmup): comece com **círculos que viram anéis mais finos conforme expandem** (define tamanho e ritmo); converta o guia em bolhas orgânicas de fogo; a expansão é **rápida no início e desacelera** ("ar quente expande rápido e desacelera ao esfriar"); cor: **branco incandescente → tons quentes → cinza ao virar fumaça**; as bolhas começam consistentes e ficam mais numerosas/complexas, com áreas escuras invadindo; após a expansão máxima, **sobem devagar e se dissipam** em fumaça; os anéis-guia podem virar uma **onda de choque**. — https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design
- **VFX-03 [MEDIDO]** Paleta da explosão do Saint11 (DB32): `#ffffff → #fbf236 → #df7126 → #ac3232`, fumaça **índigo** `#3f3f74 → #222034` (a fumaça não é cinza neutro: é um roxo-azulado escuro, H≈240°). — https://saint11.art/img/pixel-tutorials/Explosion.gif
- **VFX-04 [SÍNTESE] Gerador de explosão (Pillow), 12 frames, canvas S×S (S = 48–64), 60–80 ms/frame:**

| f | Camada(s) | Forma | Cor |
|---|---|---|---|
| 0 | contraste | disco r = 0,22·S | tom mais escuro da paleta (B0) |
| 1 | flash | disco r = 0,30·S + 4–8 linhas radiais 1 px | branco |
| 2 | blast | estrela de 5–8 pontas (ângulos agudos), núcleo branco | amarelo + branco |
| 3–5 | fogo | 5–9 "bolhas" (círculos) em volta do centro; raio `r(t)=R·easeOutCubic(t)` | temperatura `T = 1 − d/R − idade`; T alto → branco/amarelo, médio → laranja, baixo → vermelho |
| 4–7 | fogo → anéis | subtrair círculos internos (anéis afinando), áreas escuras invadindo | laranja/vermelho + 1º tom de fumaça |
| 5–11 | fumaça | puffs nas bolhas externas; sobem 1 px/frame desacelerando; encolhem e se fragmentam | índigo → índigo escuro; últimos 1–2 frames só fragmentos |
| 3–9 | debris (opcional) | 4–8 partículas 1–2 px com gravidade | amarelo → vermelho |

Validações: f0 é o frame de menor L médio; f1 é o de maior L médio; nenhum frame de fogo com mais de 2 tons de fumaça; erosão por remoção de pixels (sem alpha parcial). Para explosões longas, encadear 2–4 explosões menores com 2–3 frames de defasagem (VFX-01).

- **VFX-05 [FONTE]** Propulsão (ciclo de 5 frames, útil para mísseis/feitiços com rastro): (1) **frame claro, como uma pequena explosão** + clarear a nave nesse frame; (2) chama esticada, alta e fina; (3) massa volta ao propulsor, um pedaço da chama é jogado para trás; (4) chama mais larga e curta, **mais escura**; (5) ainda mais escura e menor. Partículas procedurais se a nave se mover muito; padrões ondulados de fogo também servem. — https://saint11.art/img/pixel-tutorials/RocketTrail.gif

### 5.2 Fogo

- **VFX-06 [FONTE]** Saint11 (Fire): "desenhar fogo é sobre **fluxo**; desenho cada partícula/onda por vez, focando no movimento". **Uma onda**: começa **mais clara e embaixo**; formas onduladas. **Várias ondas**: comece **uma nova onda a cada 2 ou 3 frames**; no último frame continue como se o primeiro fosse o próximo (loop). **Chama simples**: dividir em **base + partículas**; a base muda de forma mas **mantém o volume**; partículas se soltam da base. Truque barato: redesenhar a mesma forma "errando um pouco". **A velocidade da chama é maior no meio**; não quebrar a forma cedo/demais; formas em S; **o topo da onda some numa ponta**; **as cores claras vêm de baixo**; **brasa "pisca" e se move pouco**; faíscas. GIF: 30 frames × 100 ms. — https://saint11.art/img/pixel-tutorials/Fire.gif
- **VFX-07 [FONTE]** Fogo do DOOM (PSX), algoritmo de autômato: grade de "calor" 0–36; linha de baixo = 36 (branco, fonte constante); para cada pixel (de baixo para cima), o pixel acima recebe `valor − (rand & 1)` com deslocamento horizontal aleatório (`randIdx ∈ {0..3}`, destino `src − randIdx + 1`); o resfriamento irregular gera a cintilação. — https://fabiensanglard.net/doom_fire_psx/ . Paleta de 37 entradas (índice 0 → 36), extraída do código de referência https://github.com/fabiensanglard/DoomFirePSX (`flames.html`):

```text
#070707 #1f0707 #2f0f07 #470f07 #571707 #671f07 #771f07 #8f2707 #9f2f07 #af3f07 #bf4707 #c74707 #df4f07
#df5707 #df5707 #d75f07 #d75f07 #d7670f #cf6f0f #cf770f #cf7f0f #cf8717 #c78717 #c78f17 #c7971f #bf9f1f
#bf9f1f #bfa727 #bfa727 #bfaf2f #b7af2f #b7b72f #b7b737 #cfcf6f #dfdf9f #efefc7 #ffffff
```

- **VFX-08 [SÍNTESE] Progressão de cor do fogo pela idade da partícula** (consenso de VFX-02, VFX-03, VFX-06, VFX-07; o matiz desce de ~60° para ~0° enquanto o valor cai; a saturação sobe até o vermelho e despenca na fumaça, que é fria):

| Idade (0–1) | Estado | DB32 (Saint11) | Endesga 64 | Resurrect 64 | DOOM idx |
|---|---|---|---|---|---|
| 0,00–0,12 | branco incandescente | `#ffffff` | `#ffffff` | `#ffffff` | 36–34 |
| 0,12–0,30 | amarelo | `#fbf236` | `#ffeb57` `#ffc825` | `#f9c22b` | 33–26 |
| 0,30–0,55 | laranja | `#df7126` | `#ffa214` `#ed7614` | `#f79617` `#fb6b1d` | 25–15 |
| 0,55–0,75 | vermelho | `#ac3232` | `#c64524` `#8e251d` | `#e83b3b` `#ae2334` | 14–6 |
| 0,75–0,88 | brasa escura / transição | (pular) | `#571c27` | `#6e2727` | 5–1 |
| 0,88–1,00 | fumaça (fria) | `#3f3f74` → `#222034` | `#424c6e` → `#2a2f4e` | `#3e3546` → `#2e222f` | — |

Regras: o tom mais claro fica **embaixo/no centro** (VFX-01, VFX-06); a fumaça é sempre **mais fria e menos saturada** que o último vermelho; em fundo escuro, o último tom de fumaça deve ter ΔL ≥ 0,05 em relação ao fundo, senão a fumaça "some" (ou é eliminada).

### 5.3 Fumaça

- **VFX-09 [FONTE]** Saint11 (Smoke): sistemas de partículas são complicados, mas **partículas individuais são simples**: "anime **uma partícula**, volte e faça outra até a fumaça estar pronta"; o **primeiro frame é um contrast frame** ("deixa o próximo mais claro"); numa explosão minúscula, "**resolvo o blast em 2 frames**"; em sistemas complexos, foque **um elemento por vez**; "não quebre demais a forma, senão vira **ruído**". GIF 100 ms/frame. — https://saint11.art/img/pixel-tutorials/SmokeSheet.gif
- **VFX-10 [FONTE]** Fumaça de magia sombria: **mais fluida que o normal, com mais conexões**; **some em espirais e devagar**. Magia de luz: **evite fumaça**. — https://saint11.art/img/pixel-tutorials/DarkMagic.gif , https://saint11.art/img/pixel-tutorials/LightMagic.gif
- **VFX-11 [SÍNTESE] Puff de fumaça:** cluster de 1–3 círculos sobrepostos; cresce 1 px a cada 1–2 frames; sobe 1 px/frame desacelerando; a cada 2–3 frames desce um passo na rampa (mais escuro e mais frio); ao fim, quebra em 2–3 fragmentos (mantendo-os conectados o máximo possível) e é **erodido de fora para dentro**; 6–10 frames × 80–100 ms. Nunca usar dither para "transparência" de fumaça em sprites pequenos (vira ruído, F-36).

### 5.4 Faíscas, brasas e partículas

- **VFX-12 [FONTE]** Magia de luz: **faíscas pequenas que caem devagar ou até sobem**; "faíscas demais causam ruído"; **rastros de partículas** transmitem ordem/inteligência — **começam rápidos e depois desaceleram**. — https://saint11.art/img/pixel-tutorials/LightMagic.gif
- **VFX-13 [FONTE]** Fogo: "a brasa **pisca** e se move **ligeiramente**" (movimentos pequenos). — https://saint11.art/img/pixel-tutorials/Fire.gif
- **VFX-14 [FONTE]** Eletricidade: "**faíscas podem ser resolvidas em apenas 3 frames**". — https://saint11.art/img/pixel-tutorials/Electric.gif
- **VFX-15 [FONTE]** Fragmentação (fantasmas/hologramas): escolha **um formato de partícula**; simule uma a uma, em loop; as partículas ficam **mais escuras/transparentes e menores**; **começam rápidas e desaceleram**. — https://saint11.art/img/pixel-tutorials/Holograms-Ghosts.gif
- **VFX-16 [SÍNTESE] Brasa de forja/tocha:** 1 px (às vezes 1×2 na direção do movimento); nasce no topo da chama com cor `amarelo`; sobe 0,3–0,8 px/frame (acumular sub-pixel em float e só desenhar `round()`), deriva horizontal senoidal ±1 px; desce na rampa a cada 3–4 frames (amarelo → laranja → vermelho); nos últimos 2–3 frames **pisca** (aceso/apagado); vida 8–20 frames × 60–100 ms; densidade máx. ≈ 1 brasa por 150 px² de área de fogo (evitar ruído, VFX-12).

### 5.5 Eletricidade e raios

- **VFX-17 [FONTE]** Saint11 (Electricity): animações elétricas **devem ser rápidas**; animar em frames alternados **adicionando frames em branco**; misture **arcos, raios e fumaça**; há um **contrast frame**. **Arco** (f1–f6): o arco se move e se dissipa; evitar partículas demais; frames em branco para **piscar**. **Raio**: f7 *primeiro choque*, **ângulos agudos**; f8 **branco ou claro, forma diferente**; f9 **espera 1 frame** (vazio); f10 **fade do raio a partir do 1º frame** (fragmentos dele); f11 espera 1 frame; f12–f13 **dissipar rápido**. — https://saint11.art/img/pixel-tutorials/Electric.gif
- **VFX-18 [FONTE]** Geração de raio por deslocamento do ponto médio: função recursiva recebe o segmento e um deslocamento; desloca o ponto médio por `(rand − 0,5)·displace` em x e y; chama-se nas duas metades com `displace/2`; para quando `displace < detail` (detail maior = menos segmentos). — https://krazydad.com/bestiary/bestiary_lightning.html
- **VFX-19 [FONTE]** Magia sombria: "cores **antinaturais** para relâmpagos dão um ar sinistro"; "relâmpagos e símbolos são sempre ótimos para coisas místicas". — https://saint11.art/img/pixel-tutorials/DarkMagic.gif
- **VFX-20 [SÍNTESE] Raio em pixel:** gerar polilinha (VFX-18) com `detail` = 2–3 px nativos; rasterizar com Bresenham (núcleo 1 px branco/`#cbdbfc`), **brilho de 1 px** de cada lado em tom médio frio (ou violeta/verde-ácido para magia sombria), sem AA; ramificações com prob. 0,2–0,35 por segmento, ângulo ±20°–40°, comprimento 30–60% do restante; sequência VFX-17: `[contraste, choque, branco/forma nova, vazio, fragmentos do choque, vazio, dissipação, dissipação]` a 50–80 ms.

### 5.6 Magia sombria × sagrada (essencial para o tom gótico)

- **VFX-21 [FONTE]** Magia sombria: "é tudo sobre transmitir sentimentos: **antinatural, caótico, místico, fantasmagórico, mórbido**"; muitas cores complementares, alto contraste e roxo; **"uso o círculo preto para criar contraste"**; **formas afiadas** quando possível; **animações sobrepostas** para sensação caótica; **adicione rostos ou caveiras**; luz de baixo; fumaça fluida em espirais. GIF 60 ms/frame. — https://saint11.art/img/pixel-tutorials/DarkMagic.gif
- **VFX-22 [FONTE]** Magia de luz/sagrada: "**ordem, inteligência, limpeza, calma, bem**"; cores **análogas, claras e saturadas**; chuva e efeitos de água funcionam bem; **evite explosões demais**; **formas arredondadas ou quadradas**, evite pontas; **evite fumaça**; as coisas devem acontecer **em sequência** (ex.: chuva > explosão > símbolo); luz de cima. GIF 70 ms/frame. — https://saint11.art/img/pixel-tutorials/LightMagic.gif
- **VFX-23 [SÍNTESE] Tabela de parâmetros para o gerador:**

| Parâmetro | Sombria / profana | Sagrada / divina |
|---|---|---|
| Paleta | complementares, roxo dominante + verde-ácido/rosa; fundo de contraste preto | análogas: ouro/branco/ciano ou ouro/laranja |
| Formas | pontas, espinhos, garras, caveiras, rostos | círculos, quadrados, raios retos, halos |
| Direção de luz | de baixo | de cima |
| Ritmo | camadas sobrepostas, defasadas, "caóticas" | eventos em sequência, simétricos |
| Fumaça | fluida, em espiral, lenta | nenhuma |
| Partículas | sobem e espiralam, aceleram | caem devagar/sobem retas, desaceleram |
| ms/frame | 50–60 | 70–90 |

### 5.7 Arcos de golpe (slash arcs) e smears

- **VFX-24 [FONTE]** O frame de *overshot* do ataque leva o **arco** (crescente claro), exagerado, com motion blur e "wind FX"; cor medida do arco: `#cbdbfc` (branco-azulado frio). — https://saint11.art/img/pixel-tutorials/Swords.gif
- **VFX-25 [FONTE]** Smear: normalmente **1 frame** (A-05); **não** em antecipação/recover (A-06); entre poses-chave fortes e seguindo o arco (A-09).
- **VFX-26 [SÍNTESE] Arco em crescente (algoritmo):** dois arcos concêntricos de raio externo `R` e interno `R − w(θ)`, com espessura `w(θ)` afinando de `w_max` (borda de ataque, ≈ R/4) até 0 na cauda; ângulo varrido 90°–160° (A-05 usa 90°); cores: borda de ataque branca/`#cbdbfc`, corpo em tom claro frio, **cauda nos tons mais escuros** (cores escuras servem para o fade, A-10). Frames (40–60 ms): f0 arco cheio; f1 arco mais fino avançado 10°–20°; f2 só o fragmento da frente + 2–3 linhas de velocidade; f3 restos de 1–2 px. Variantes elementais recolorem a mesma máscara (fogo: núcleo amarelo/borda laranja; sombra: violeta com núcleo branco).

### 5.8 Sangue e gore estilizado

- **VFX-27 [FONTE]** Saint11 (Blood and guts): não exagere nas gotas (fica bagunçado); órfãos só em resolução muito baixa; **use formas redondas** quando possível; respingo grande: **comece com uma forma muito pontuda** e depois **espalhe mantendo as partículas conectadas o máximo possível**; jato: **começa com bordas afiadas**, depois a resistência do ar o curva; **gravidade** — partículas caem antes de sumir; evite órfãos, exceto no último frame de uma partícula; **variações de matiz** para não ficar monótono; vísceras = "tubos e balões de água"; **pequenos pontos de brilho** mostram que é molhado/viscoso. — https://saint11.art/img/pixel-tutorials/Blood.GIF
- **VFX-28 [SÍNTESE]** Para o tom gótico, use rampa de carmim escuro (ex.: Bloodmoon21 `#3c0921 #520b20 #7d0f1f #a8141d #d3181c #ff252b`) com variação de matiz para o roxo nos escuros (C-07); 1 px de highlight quase branco por gota grande; a mancha no chão **permanece** (permanence, A-16).

### 5.9 Projéteis, brilho, fantasmas, glitch

- **VFX-29 [FONTE]** Projéteis (Saint11): rampa com **núcleo mais quente e claro, bordas mais frias e escuras**; considere **projéteis maiores** para serem vistos; projéteis perigosos devem chamar mais atenção — **piscar** é um jeito bom e barato; projéteis rápidos têm menos detalhe e são **alongados na direção do movimento**; **muzzle flash e estilhaços de impacto** são muito importantes (comunicam onde o tiro começa e termina), especialmente se o projétil não é visível. — https://saint11.art/img/pixel-tutorials/Bullets.gif
- **VFX-30 [FONTE]** Projéteis (Slynyrd): visibilidade é o fator mais importante; cores claras e saturadas; formas únicas; outline quase obrigatório (duplo claro+escuro como seguro); piscar entre **2 frames** basta (contraste maior = mais intenso, mas demais atrapalha rastrear tiros rápidos); pulsar (expandir/contrair) ou girar. — https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design
- **VFX-31 [FONTE]** Shine/brilho: "simple shine" = faixa diagonal branca que varre a forma; "extra shine" = flash branco do conteúdo → preenchimento colorido → blob que encolhe → linha fina; "funciona em outras formas" (círculos, lâminas). Tempos medidos: pausa 500 ms, 9 frames × 80 ms, hold 200 ms. — https://saint11.art/img/pixel-tutorials/Shine.gif
- **VFX-32 [FONTE]** Estrelas/brilhos: formas comuns (ponto 1 px, "+" de 5 px, quadrado 2×2); para estrelas de fundo, **2–3 variações de cor**; cintilação com **pequenas mudanças de cor**, **poucos frames**, **nem todas animam**, **fora de sincronia**; pontos brilhantes esporádicos dão ritmo; estrelas grandes: **hue shift e mais saturação em direção ao centro**; evite contraste em planetas de fundo. — https://saint11.art/img/pixel-tutorials/Stars.gif
- **VFX-33 [FONTE]** Fantasmas/hologramas: preferir **cores frias** (quentes só com saturação baixa); **uma cor principal** (monocromático); sem semitransparência → enfatize **outlines, olhos, boca e nariz**; flutuação senoidal; **blend aditivo**. — https://saint11.art/img/pixel-tutorials/Holograms-Ghosts.gif
- **VFX-34 [FONTE]** Glitch: combine vários efeitos — **deslocamento horizontal** de faixas (sem exagero); **V-sync ruim/flicker** (deslocar a imagem verticalmente + barras pretas/brancas aleatórias + frames pretos, brancos e de ruído); **corrupção** (mover seleções quadradas, números, formas pretas, glifos); **scanlines e color bleed** (mover scanlines 1 px, trocar cores, "empurrar as cores para a direita"); inverter cores. — https://saint11.art/img/pixel-tutorials/Glitch.gif

### 5.10 Círculos mágicos **[SÍNTESE]**

Não encontrei tutorial de pixel art específico e confiável; o que segue combina F-05/F-06 (não rotacionar arte pronta), VFX-21/22 e técnicas gerais de círculos (polígonos rotacionados + círculos menores em volta: https://medibangpaint.com/en/use/2022/09/how-to-draw-a-magic-circle).

1. Desenhar cada anel **na resolução final** com o algoritmo de círculo de ponto médio (F-18), anéis de 1 px separados por ≥ 2 px.
2. Simetria que respeita a grade: **4 ou 8 setores** (runas a cada 45°/90°), estrelas de 4/8 pontas ou pentagrama (sombria).
3. "Rotação" sem rotacionar pixels: (a) **mover as runas ao longo do anel** (reposicionar glifos pré-desenhados em ângulos novos, cada glifo sempre "em pé"), ou (b) **ciclar a cor** ao longo do anel (ver TR-10), ou (c) rotação em passos de 90° + espelhamento.
4. Brilho: 1 anel externo 1 px em tom médio + núcleo claro; pulso de 4–6 frames × 80–120 ms; sombria = contraste preto + roxo/verde-ácido; sagrada = ouro/branco com raios retos de cima.

### 5.11 Legibilidade de VFX sobre fundo escuro

- **VFX-35 [FONTE]** Fontes: projéteis claros/saturados com outline (VFX-30), maiores e piscando (VFX-29), *contrast frame* escuro antes do flash (VFX-01, VFX-09, VFX-17), círculo preto atrás de magia sombria (VFX-21), fundos dessaturados/menos contrastados (C-20), blend aditivo para espectros (VFX-33).
- **VFX-36 [SÍNTESE] Checagens numéricas:** núcleo do efeito com **L_OKLab ≥ 0,85** e **ΔL ≥ 0,40** em relação à mediana do fundo sob o efeito; pelo menos 1 tom do efeito com **S ≥ 60%** e matiz a ≥ 60° do matiz dominante do fundo; se o fundo local tiver L > 0,45, contornar o efeito com 1 px do tom mais escuro da rampa; a área do flash branco não deve passar de 1–2 frames (fadiga visual); evitar que um efeito ocupe > 35% da tela por mais de 150 ms.


---

## 6. Efeitos de tela ("juice") e transições

### 6.1 Shake, hit-stop, flash, impact frames

- **TR-01 [FONTE]** Ver A-02 (tremer câmera **e** alvo), A-14/A-15 (hit-stop proporcional ao dano, tremor que decai, horizontal no chão/vertical no ar), A-16 (camera kick oposto ao tiro, *sleep* ao acertar, *permanence*).
- **TR-02 [SECUNDÁRIA]** Shake por "trauma" (implementação de terceiros que credita o vídeo "Math for Game Programmers" da GDC — a sessão de 2016 sobre câmeras é de Squirrel Eiserloh): `trauma ∈ [0,1]` somado a cada impacto e decaindo por frame (`trauma −= dt·taxa`); `offset = shakeMagnitude · trauma² · perlin(seed+eixo, t)` (uma amostra de Perlin por eixo, outra para rotação, também ×trauma²). — https://community.gamedev.tv/t/enhanced-camera-shake-with-perlin-noise/204230
- **TR-03 [SÍNTESE]** Em pixel art, o deslocamento de shake é **inteiro em pixels nativos** (o mundo inteiro desloca junto; a UI não treme), amplitude 1–4 px nativos, decaimento em 4–10 frames @60, direção preferencial = direção do golpe (A-16, "camera kick"), alternando o sinal a cada 1–2 frames.
- **TR-04 [SECUNDÁRIA]** Hit flash: o sprite "vira branco sólido por **0,1 s** e volta ao normal" (implementado com uma camada/efeito que desenha tudo em branco). — https://forum.gdevelop.io/t/sprite-flash-solid-white-when-damaged/29507 . **[SÍNTESE]** Default: 2–4 frames @60 (33–66 ms), até 6 frames (100 ms) em golpes pesados; gere o sprite branco a partir da máscara alfa (todas as cores → branco ou → tom mais claro da paleta).
- **TR-05 [SECUNDÁRIA]** *Impact frames* (animação 2D/anime): 1–3 frames de alto contraste/inversão, formas simplificadas e angulares, reservados para momentos-chave. — https://knowyourmeme.com/memes/cultures/impact-frames . Equivalentes em pixel art com fonte primária: *contrast frame* escuro + *white flash* (VFX-01, VFX-09, VFX-17, A-13).
- **TR-06 [SÍNTESE] Impact frame em Pillow:** silhueta do atacante+alvo em 1 cor (preto ou branco) sobre fundo invertido (2 cores totais), 1 frame (≤ 50 ms) seguido do frame normal com hit-stop; no máximo 1 a cada ~2 s de jogo para não cansar.

### 6.2 Transições de tela

- **TR-07 [SÍNTESE] Dither fade (Bayer), baseado em F-34:** para cada pixel, `limiar = (M4[y%4][x%4] + 0,5)/16`; mostra a cena nova se `progresso > limiar`. 4×4 = 16 passos visíveis (8×8 = 64). Para retro "chunky", aplique sobre blocos de 2×2 px nativos. Duração: 8–16 passos de 33–50 ms. Fade "para o escuro": primeiro a cena → cor B0 (ver 2.7), depois B0 → nova cena. Prenda a matriz à tela inteira (padrão estável) durante a transição.
- **TR-08 [FONTE] Diamond wipe:** grade de células de `diamondPixelSize` px; `xF = fract(x/size)`, `yF = fract(y/size)`; `xD = |xF − 0,5|`, `yD = |yF − 0,5|`; descarte o pixel da cortina se `xD + yD + u + v > progresso·4` (u, v = coordenadas normalizadas 0–1 → varre do canto superior esquerdo ao inferior direito); variante só-grade: `xF + yF > progresso·2`; tween o progresso 0→1. — https://ddrkirby.com/articles/shader-based-transitions/shader-based-transitions.html
- **TR-09 [SÍNTESE] Iris wipe:** `r(t) = easeInOutCubic(t)·R_max` (R_max = distância ao canto mais distante), arredondado para inteiro; visível se `(x−cx)² + (y−cy)² < r²`; métrica de Chebyshev → íris quadrada, Manhattan → losango (combina com TR-08); borda de 1 px na cor de acento; 12–20 frames @60.
- **TR-10 [FONTE] Wipes por máscara:** uma textura-máscara codifica a **ordem** de revelação de cada pixel: `d = r + g/256 + b/65536`; `t' = t·(1 + 2·ramp) − ramp`; `alpha = clamp((t' − d)/ramp + 0,5, 0, 1)` (exemplo `ramp = 4/256`); padrões: wipe, curtain, shutter, **diamond**, box, spiral, random, infect; *delay* pequeno mas não zero; partículas da máscara não devem ser vazadas (estrela ok, crescente não). — https://c.eev.ee/particle-wipe-generator/ . **[SÍNTESE]** Para pixel art use `ramp → 0` (limiar binário, sem alpha parcial).
- **TR-11 [FONTE] Mosaico/pixelate (SNES):** registrador `$2106` — 4 bits altos = tamanho do mosaico **0 = 1×1 … 15 = 16×16**, 4 bits baixos = quais BGs; cada bloco é coberto pelo **pixel superior esquerdo** do bloco. — https://snes.nesdev.org/wiki/PPU_registers ; uso típico: fade para mosaico → troca de cena → revelar (exemplo de ~30 frames). — https://k0b3n4irb.github.io/opensnes/mosaic_8h.html . **[SÍNTESE]** Em Pillow: para `s` em `[1,2,3,4,6,8,12,16]` → `img.resize((w//s, h//s), NEAREST).resize((w, h), NEAREST)` (amostra canto/centro); 2–3 frames @60 por passo.
- **TR-12 [FONTE] Glitch como transição:** ver VFX-34 (deslocamento de faixas, barras, frames de ruído, scanlines deslocadas 1 px). — https://saint11.art/img/pixel-tutorials/Glitch.gif
- **TR-13 [FONTE] CRT (Balatro, shader `CRT.fs` extraído pela comunidade):** coordenadas recentradas em [−1,1] e **abaulamento** `tc += (tc.yx²)·tc·(k − 1)`; **máscara de borda** com `smoothstep` (feather) escurecendo as bordas; **glitch** opcional = deslocamento horizontal por soma de senos em `y` e tempo; **aberração cromática horizontal** (R amostrado ~+0,0005 UV, G ~−0,0005 UV, normalizado a 1600 px de largura ≈ ±0,8 px de tela); **overlay de scanline/abertura** = cada canal RGB modulado por `sin(y·scanlines + fase)` com fases diferentes por canal e máscara de coluna `cos(x·scanlines·4)`; ruído; correção de contraste/brilho; bloom no fim. — https://github.com/balatro-src/balatro-src-reverse-engineering (arquivo `resources/shaders/CRT.fs`) **[SÍNTESE]** Aplicar CRT **depois** do upscale inteiro (na resolução da tela), nunca na resolução nativa; manter um toggle (acessibilidade).
- **TR-14 [FONTE] Palette cycling (Mark Ferrari):** animação por **troca de cores na paleta**, não por redesenho; como lâmpadas de marquise que acendem em sequência — "cada pixel afetado fica completamente parado", vizinhos rodam laços defasados e as faixas de cor parecem se mover; usado para água, lava, luzes. — https://en.wikipedia.org/wiki/Color_cycling ; palestra GDC 2016 "8 Bit & '8 Bitish' Graphics: Outside the Box" — https://gdcvault.com/play/1023586/8-Bit-8-Bitish-Graphics ; demo Canvas Cycle (J. Huckaby, arte de Ferrari), que ainda **mistura linearmente as cores** durante o ciclo ("blend shift") para suavizar — https://experiments.withgoogle.com/canvas-cycle
- **TR-15 [SÍNTESE] Palette cycling em Pillow:** gere a cena em modo `"P"` com faixas de índices reservadas (ex.: 8 índices para o brilho da forja, 6 para o tremeluzir do vitral, 4 para runas); a cada tick, rotacione `palette[lo:hi]`; frames de 80–200 ms; para "blend shift", interpole linearmente cada entrada entre a cor atual e a próxima em 2–4 subpassos e **quantize de volta** para a paleta mestra se o estilo exigir paleta fechada.

---

## 7. UI: 9-slice, botões, barras, molduras de carta

### 7.1 Caixas 9-slice / 3-slice

- **UI-01 [FONTE]** Saint11 (UI 9-Slice): técnica para formas retangulares ("caixas"); **os lados devem ser tileáveis com as bordas e consigo mesmos**; **evite detalhe demais no meio e nas bordas**; **cantos podem ter mais detalhe**; para estender, **repita (tile) as bordas** ou estique — **esticar só funciona em caixas com pouquíssimo detalhe**; variação: randomizar (em código) a borda e o tile do meio; animar a caixa pode ser boa ideia; adicionar headers/footers; caixas servem também para **barras de vida, sliders, divisores**; use **3-slice** para formas só verticais/horizontais. — https://saint11.art/img/pixel-tutorials/UI-9-Slice.gif
- **UI-02 [FONTE]** Kit de UI pixel: para esticar, "mantenha os cantos decorados intactos e estique só o meio liso"; 4 estados (normal, hover, pressed, disabled) gerados por script a partir de um sprite base. — https://gegx.itch.io/pixel-ui-kit
- **UI-03 [SÍNTESE] Regras do gerador 9-slice:** largura do canto `c` = 3–8 px nativos (ornamento gótico cabe no canto); bordas com período de tile que divide o comprimento (ou com tile "coringa" de ajuste); o miolo é cor sólida ou textura de período ≤ 4 px; contorno externo 1 px na cor mais escura; bisel: 1 px de luz no topo/esquerda interna e 1 px de sombra embaixo/direita interna (luz vinda do alto-esquerda, L-01).

### 7.2 Botões e estados

- **UI-04 [FONTE]** Estados: **Normal, Focus, Hover, Active (pressionado)**; desaconselha "Disabled" (melhor mostrar uma mensagem de erro ao clicar); **uma ação principal por tela**, visualmente mais forte; borda visível para ler como botão; **sombra** imita um botão físico que afunda; exemplo base 48×16 px. — https://indieklem.substack.com/p/8-better-designed-buttons
- **UI-05 [FONTE]** Estado pressionado: **remova a sombra e desloque o botão pela mesma distância que a sombra ocupava**. — https://dev.to/nicm42/how-to-make-a-button-looked-like-it-s-staying-pressed-down-58k . Alternativa: pressed nos **mesmos pixels** do normal, mudando só a cor ("hover e press leem como mudança de cor, não como tremida"). — https://gegx.itch.io/pixel-ui-kit
- **UI-06 [FONTE]** UI deve seguir regras consistentes de cor, forma, tamanho, fonte e posição; não misturar estilos de barra; "a função vem primeiro"; legível sempre, sem distrair do jogo; animação de UI é bem-vinda se não distrair. — https://www.slynyrd.com/blog/2020/2/23/pixelblog-26-uxui-design-basics
- **UI-07 [SÍNTESE] Especificação de botão pixel (luz no alto-esquerda):**

| Estado | Face | Bisel/sombra | Conteúdo (ícone/texto) | Animação |
|---|---|---|---|---|
| Normal | tom base da rampa | 1 px luz topo, 1 px sombra base, **sombra projetada 1 px** abaixo | posição base | — |
| Hover/Focus | +1 passo na rampa (ou outline de acento 1 px) | igual | igual | shine sweep (VFX-31) a cada 2–4 s, ou pulso de outline 2 frames × 120 ms |
| Pressed | −1 passo na rampa | bisel invertido (sombra no topo), **sem sombra projetada** | **desloca 1 px para baixo** (= espessura da sombra, UI-05) | 1 frame de squash (A-11) opcional, 40–60 ms |
| Disabled (se usar) | dessaturar para S ≤ 15%, L −0,10 | sem sombra | conteúdo em tom médio, sem acento | nenhuma |

### 7.3 Molduras de carta, raridade e "editions"

- **UI-08 [FONTE]** Slay the Spire: raridade pela **cor do banner e da moldura** — **comum = cinza, incomum = azul, rara = dourada**; tipo pela **forma da moldura** — Ataque: retângulo com borda inferior afunilada; Skill: retangular; Power: oval. — https://slaythespire.wiki.gg/wiki/Cards
- **UI-09 [FONTE]** Convenção MMO de qualidade (WoW): Poor `#9d9d9d`, Common `#ffffff`, Uncommon `#1eff00`, Rare `#0070dd`, Epic `#a335ee`, Legendary `#ff8000`, Artifact `#e6cc80`, Heirloom `#00ccff`. — https://warcraft.wiki.gg/wiki/Quality
- **UI-10 [FONTE]** Inscryption (Daniel Mullins): o design visual das cartas foi acompanhado de "preocupação constante com a **legibilidade**" por causa da **baixa resolução** — detalhes pequenos ficavam difíceis de ver; soluções: **nenhum texto na carta além do nome** e **ícones cobrindo o retrato quando necessário**. — https://www.gamedeveloper.com/design/how-game-jam-sacrifices-became-inscryption
- **UI-11 [FONTE] Editions do Balatro** (shaders extraídos pela comunidade; descrição do mecanismo, não do código): todos avaliam o efeito em **UV "floored" ao texel** (o efeito respeita a grade de pixels do sprite) e usam um campo animado `field(uv, t)` = soma de cossenos/senos das **distâncias a 3 centros que orbitam** no tempo.
  - **Polychrome**: converte para HSL; dessatura levemente R/G de pixels pouco saturados; `hue += res` (res ∈ [0,1] vindo do campo, i.e. **rotação de matiz completa variando em manchas suaves**) e `sat = min(0,6; sat + 0,5)`.
  - **Holographic**: mistura a cor 50% com azul antes do HSL; mesmo campo com escala ~5× mais fina; soma uma **grade diagonal** (picos de `cos` em `x` e em `y·45 ± x·20`, limiarizados) ao matiz; `sat ×1,3`; `light = light·0,6 + 0,4`; mistura com o original por um peso que cresce com a croma; tinge `×(0,9; 0,8; 1,2)` (azul-violeta).
  - **Foil**: máscara de **anéis radiais** + **faixas angulares que giram** + faixas lineares em x/y; onde a máscara é alta, reduz R e G e **aumenta B** (brilho metálico azulado).
  - **Negative**: **inverte a luminosidade** (L → 1 − L), espelha o matiz (`h → −h + 0,2`) e soma um cinza-azulado `0,8·(79, 99, 103)/255`.
  — https://github.com/balatro-src/balatro-src-reverse-engineering (arquivos `resources/shaders/polychrome.fs`, `holo.fs`, `foil.fs`, `negative.fs`); porte do foil para Godot: https://godotshaders.com/shader/balatro-foil-card-effect/
- **UI-12 [SÍNTESE] Editions em Python (frames estáticos/animados):** para cada texel `(x, y)` do sprite nativo calcule `field` com 3 centros orbitando (períodos de 40–150 frames), gere o deslocamento e aplique em HSL; depois **quantize o resultado para a paleta mestra** (ou para uma sub-paleta "holo" de 12–16 cores) para continuar pixel art; aplique só na **arte e na moldura**, nunca no texto/números; gere 8–16 frames em loop (80–100 ms).
- **UI-13 [SÍNTESE] Anatomia de carta gótica (gerador):** (1) moldura 9-slice (UI-03) com cantos ornamentados (arcos ogivais/rosáceas, ver 9.2) e **cor por raridade** (cinza-ferro → prata-azulada → ouro-velho → carmim/roxo para lendária); (2) banner do nome com o mesmo código de cor (UI-08); (3) **forma/selo por tipo** (UI-08); (4) janela do retrato com bisel interno (sombra 1 px no topo/esquerda, luz 1 px embaixo/direita = efeito de "afundado"); (5) custo/atributos em gemas (L-06) com ícones grandes, texto mínimo (UI-10); (6) edição especial = overlay de UI-12 + shine sweep (VFX-31); (7) raridades altas podem ter 1 animação idle (A-22: "quanto mais importante, mais especial o feedback").

---

## 8. Ícones (16/24/32/48 px)

- **IC-01 [FONTE]** Oito regras de ícone: **silhuetas distintas** (reconhecível só pela forma); **baixa complexidade**; **estilo consistente** (projetar lado a lado); **não depender de texto** (se precisar, rótulo abaixo); usar **metáforas estabelecidas**; **um significado por ícone** (e estados ativo/inativo distintos); **projetar para tamanho pequeno**; **forma antes da cor** (cor apoia; ajuda daltônicos). — https://www.gamedeveloper.com/design/icon-design-rules-you-should-know
- **IC-02 [FONTE]** Itens: tamanho relativo ao tile (tiles 16×16 → itens 16×16); ~6 cores ou menos; projeção consistente (top-down: item levemente inclinado para a frente). — https://www.slynyrd.com/blog/2019/12/21/pixelblog-24-items
- **IC-03 [FONTE]** Silhueta: "a silhueta é o prólogo"; formas de cobra, membros longos, **pontas** e formas **complicadas e afiadas** transmitem **perigo**; adicione **elementos fortes** à silhueta (ex.: cabeça achatada, esteiras); processo **silhueta → detalhes → animação**. — https://saint11.art/img/pixel-tutorials/Silhouette.gif
- **IC-04 [FONTE]** Caveiras em baixa resolução (útil para ícones góticos): quando não cabe tudo, prioridade **olhos → maxila → zigomático → dentes → osso nasal → mandíbula → fossa temporal**; nas menores, foque em **olhos e nariz**; há versões para largura par e ímpar; ossos diagonais usam menos pixels; ossos simples em forma de "fita"; pilhas de ossos com formas ruidosas/irregulares; "moscas de 1 px são legais". — https://saint11.art/img/pixel-tutorials/skull.gif
- **IC-05 [FONTE]** Perigo em objetos: um *tell* antes da ação; aparência perigosa; ritmo/previsibilidade; impacto; **vermelho ou verde-claro** são ótimos para zonas de perigo; objetos estáticos podem ter alguma animação (facilita a detecção); **luzes piscando** sinalizam perigo; formas afiadas e movimento espasmódico = perigo. — https://saint11.art/img/pixel-tutorials/Hazards.gif
- **IC-06 [SECUNDÁRIA]** Teste de valor: dessature o sprite; se as formas não se separarem, espalhe mais os valores; a legibilidade vem quase toda do **contraste de valor**, não da cor; posterizar em 2–3 valores mostra se as massas de luz/sombra se sustentam. — https://www.wayline.io/learn/color-palettes/1
- **IC-07 [SÍNTESE] Regras por tamanho:**

| Tamanho | Outline | Cores | AA | Detalhe | Fundo/plate |
|---|---|---|---|---|---|
| 16×16 | 1 px, escuro (sel-out mínimo); nenhum pixel órfão | 4–6 | não | 1 ideia + 1 detalhe forte (IC-04) | plate opcional; ícone ocupa 12–14 px |
| 24×24 | 1 px sel-out | 6–8 | não | 1 ideia + 2 detalhes | plate com borda 1 px; ícone 18–20 px |
| 32×32 | 1 px sel-out | 8–12 | só interno, mínimo | silhueta + volume em 3 tons + 1 highlight | plate com moldura de raridade 1–2 px; ícone 24–28 px |
| 48×48 | 1 px sel-out (2 px só se estilizado) | 12–16 | interno moderado | volume em 4 tons, textura leve | moldura de raridade 2 px + cantos; ícone 36–42 px |

Comuns a todos: luz do alto-esquerda (L-01) igual em todo o conjunto; **ΔL ≥ 0,30** entre a silhueta do ícone e o plate; plate em B1/B2 (2.7) com matiz complementar ao objeto; raridade **na moldura e não no objeto** (para o objeto manter identidade); raridades altas recebem shine sweep periódico (VFX-31) e brilho de 1 px nos cantos; testar sobre fundo claro, médio e escuro.

- **IC-08 [SÍNTESE] Tiers de raridade sugeridos (gótico, compatíveis com UI-08/UI-09):** Comum = ferro `#5d5d5d→#b4b4b4` (Endesga 64 cinzas); Incomum = prata-azulada/aço `#424c6e→#c7cfdd`; Rara = ouro-velho `#8a4836→#edab50→#ffc825`; Épica = ametista `#3b1443→#93388f→#ca52c9`; Lendária = carmim + ouro `#571c27→#c42430→#ffc825` com animação. Cada tier deve diferir também em **valor e forma da moldura** (não só matiz) para daltônicos (IC-01).

