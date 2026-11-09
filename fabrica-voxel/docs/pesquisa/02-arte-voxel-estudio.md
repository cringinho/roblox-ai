# 02 — Arte voxel com qualidade de estúdio (referenciamento)

Pesquisa de 9 de novembro de 2026. Toda fonte citada foi aberta e lida. Legenda: **[Fn]** = tirado da fonte n; **[P]** = limiar proposto por este dossiê (calibrar antes de travar); **[não verificado]** = não consegui confirmar.

## 0. Veredito

1. Estúdio não vence por resolução, vence por restrição: poucas primitivas, uma densidade por classe de asset, paleta curta em rampas com desvio de matiz (hue shift), luz pintada discreta somada à luz do motor, detalhe concentrado e muita área de descanso.
2. O que denuncia arte feita por código: ruído por voxel, rampa reta, curva de SDF sem facetar, detalhe uniforme, densidades misturadas, simetria estéril.
3. **Conflito a decidir.** Hoje a densidade segue a raridade (0,25 stud comum, 0,125 elite). Hytale e Minecraft fixam densidade por **classe** e tratam mistura como defeito (mixels) [F1][F2][F10]. Recomendo: personagens, criaturas, equipamento e VFX em 0,125; estruturas e props em 0,25. É a razão 2:1 do Hytale (64 px/unidade em personagem, 32 em bloco) [F1].
4. Conta que sustenta o item 3: avatar de 2,8 studs tem 11 voxels de altura a 0,25 e 22 a 0,125. O personagem do Veloren tem cerca de 22 [F9]; só a cabeça-base do Trove tem 10 [F7]. E a casa de 4 studs dá 16 voxels a 0,25, o mesmo grão do tile do Staxel e do bloco do Minecraft [F13][F10].

## 1. Tabela comparativa (só o que tem fonte)

| Jogo | Proporção | Tamanho do personagem | Paleta e cor | Luz | Animação |
|---|---|---|---|---|---|
| Hytale [F1][F2] | "small, bulky, cartoony"; cabeças de tamanho quase igual entre personagens normais | 64 px/unidade (personagem) contra 32 (bloco); altura não publicada | sem preto e branco puros; sombra com cor (toque de roxo) | sombra, AO e brilho pintados na textura + luz real; sem PBR; bloom, DoF, AO | ossos nomeados, cubos e quads, sem pintura de pesos |
| Trove [F6][F7][F15] | "blocky before organic"; cabeça-base 10×10×10 | não publicado | cor simples, saturação só em acento; nada abaixo de RGB 10,10,10 | motor + mapas de material (tipo, alfa, especular) | rig de corpo rígido; arco com squash and stretch |
| Veloren [F9] | — | ~22 × 10 voxels; bloco = 11³ voxels pequenos | propriedades pela paleta do MagicaVoxel | — | por código (o projeto chama as de combate de provisórias) |
| Minecraft / Dungeons [F10][F11][F12] | jogador "bulkier than a regular human" | 32 × 16 px; 1 px = 6,25 cm | rampas com hue shift; sem ruído, banding, pillow shading | topo e frente mais claros na textura | Dungeons: VFX na densidade de pixel do cenário |
| Teardown [F14] | realista | voxel ≈ 10 cm; objeto ≤ 256³, recomendado 128³ | 255 materiais indexados por objeto; prop simples usa 1 | do motor; rugosidade e emissivo na paleta | física |
| Staxel [F13] | — | tile 16³; objeto 24³ (até 80³) | — | — | — |
| Dead Cells [F21] | — | 50 px em jogo | — | toon shader com normal map por frame, sem antialiasing | 3D para frames; poses-chave; 30 fps |
| Cube World [F28] | [não verificado] | [não verificado] | `.cub` guarda RGB por voxel | — | — |

Nenhum estúdio publica "quantas cabeças de altura". Base teórica: adulto realista 7,5 cabeças; super deformado (chibi) tem cabeça de 1/3 a 1/2 da altura, isto é, 2 a 3 cabeças [F26].

## 2. O que cada referência ensina

**Hytale** (Thomas Frick, diretor de arte, 22/12/2025) [F1]
- Só duas primitivas: cubo (6 lados) e quad (2 lados). "No spheres allowed". Geometria mínima; só cresce para melhorar a silhueta.
- Texturas em múltiplos de 32 px. Motivo declarado dos 64 px/unidade em personagens: rosto e emoção, câmera próxima e destacar o personagem do cenário.
- Esticar um nó só entre 0,7× e 1,3× por eixo.
- Textura é "ilustração": sombra, AO e brilho pintados. "We avoid noise, too much grain, or perfectly flat surfaces."
- Coesão (2019) [F2]: cabeças, mãos e espessura de dedos e garras parecidas entre criaturas; blocos de espessura semelhante; densidade de pixel constante. Facção compartilha formas e cores (vazio: carne pálida, acento roxo, olho verde, chifre curvo, losango).
- Avatar (2019) [F3]: roupa em camadas; camisa "one-size-fits-all"; chapéu serve em qualquer cabelo; armadura vai por cima do visual. O esqueleto inimigo usa o rig humano e veste qualquer equipamento [F2]. Cor por tema: fantasia mais escura e saturada, moderno mais claro, fofo em pastel [F3].
- Ferramenta: o Hytale Model Maker (2019, cuboides e planos) [F4] deu lugar ao Blockbench com plugin oficial [F1][F5].

**Trove** (guias do Trovesaurus, canal de submissão; "based on information from Trove Team") [F6][F7][F8]
- Caixas-limite em voxels: corpo a corpo 10×10×35; cajado 12×12×35 (mínimo 16 da pega à ponta, 8 a 14 atrás da pega); arma de fogo 5×5×12; arco 1–3 × 9 × 21, sem corda; chapéu 20×20×14; máscara 10×10×5; cabelo 20×20×20; decoração 12×12×12.
- Cabo com 1 voxel de espessura; um único ponto de pega magenta (255,0,255); nada no cubo 3×3 em volta além do exigido.
- Rejeitado: fora da caixa ("no matter how beautiful"), voxel ligado só por canto ou flutuante, ruído de forma e elemento repetitivo, ferramenta de ruído, degradê automático como única pintura, cor de mapa de material como cor base, cópia de outro jogo, recolor, "something-on-a-stick".
- Mapas de material: malhas extras `_t` (sólido, vidro, vidro ladrilhado, sólido brilhante, vidro brilhante), `_a` e `_s`. Valores RGB exatos: [não verificado].
- Cabelo pintado em matiz vermelho com claro e escuro, tingido em jogo; máscara `_m` protege o que não tinge. Padrão pronto para cabelo e pele das 14 linhagens.

**Cube World**: só confirmei o formato `.cub` (dimensões + RGB por voxel) e, por fonte secundária, o editor embutido que cola cubos em armas e armaduras [F28]. Proporções, altura em voxels e montagem do equipamento: [não verificado; wiki inacessível].

**Minecraft, Blockbench e Dungeons** [F10][F12]
- Mixels são, em regra, proibidos. Forma no modelo, detalhe na textura, mínimo de elementos.
- Rampa: começar no meio-tom, criar uma sombra e uma luz, só depois expandir. Rampa reta é "dull".
- Defeitos nomeados: banding, pillow shading, pancake shading, dithering desnecessário, ruído ("adds no information").
- Dungeons: VFX "in the same resolution as the rest of the environment"; esfera de escudo virou hexágono; arrependimento declarado: degradê radial demais.

**Teardown, Cloudpunk** [F14][F30]: voxel de 10 cm, "considerably smaller than typical voxel games"; material (cor, rugosidade, emissivo, refletividade, tipo físico) vive no índice da paleta; voxels precisam se tocar por face. Cloudpunk: voxel sustentou até primeira pessoa.

**Artistas** [F15][F16]
- Sir Carma: escala é o mais importante; não detalhar demais cada asset (cabelo do Goku com "5 or 6 cubes").
- Zach Soares: quatro estilos-base (vetorial, só dobras de 90°; pixelado flat; blocky; greeble de alta resolução). Voxel art precisa ser perfeita na grade. Rig rígido gera z-fighting e clipping nas juntas: o estilo de animação dita o estilo do modelo.
- Thibault Simar: pintar por último, com luz pintada; separar em partes. Gabriel de Laubier: com forma mínima, é a paleta que devolve a leitura. Lucas Rgznsk: silhueta de uma cor antes de tudo.

## 3. Fundamentos aplicados a voxel

- **Silhueta.** Identificável de relance e mostrando para onde o personagem olha; formas simples equilibram formas complicadas [F17]. O guia de Dota 2 foi escrito para câmera alta, o caso do tabuleiro.
- **Grande, médio, pequeno e descanso.** "Detailed areas should comprise a small percentage of the overall character"; "details that are too small simply become noise" [F17]. Detalhe em área calma só com valor próximo ao do fundo [F17]. Proporção numérica entre os três níveis: [não verificado; a aula de Neil Blevins estava inacessível], limiares abaixo são [P].
- **Valor.** Mais escuro nos pés, mais claro em tronco e cabeça; mais contraste em cima. Conferir sempre em tons de cinza [F17]. Medida: luminância relativa L = 0,2126R + 0,7152G + 0,0722B em RGB linear [F27].
- **Saturação.** Cresce de baixo para cima; máxima só em áreas muito pequenas; nenhum canal R, G ou B no teto, para sobrar folga à luz do motor [F17].
- **Rampas.** Hue shift de até 20° por degrau ("20 is about as high as I go"), saturação com pico no meio, queda nos extremos [F18]. Luz puxa para amarelo, sombra para azul [F19]; Hytale põe roxo na sombra [F1].
- **Paleta curta.** Menos cores dão coesão e controle [F19].
- **Clusters.** Pixel isolado expõe a grade e vira ruído; banding é quando as bordas das faixas se alinham; degrau de comprimento irregular vira jaggy [F19].
- **Materiais em voxel** [P, a partir de F1, F6, F14]: metal = rampa de alto contraste, 1 a 2 voxels de brilho e especular do motor; tecido = rampa curta, faixas largas; pele = sombra quente; madeira e pedra = clusters alongados (veio) ou em bloco (fratura); osso = claro dessaturado com sombra fria; brilho = emissivo pequeno cercado de escuro.
- **AO embutida.** AO por vértice com 4 níveis, `3 − (lado1 + lado2 + canto)`, zero quando os dois lados existem; inverter a diagonal do quad quando `a00 + a11 > a01 + a10`; compatível com malha gulosa se só fundir faces de AO igual [F20]. O Hytale soma luz pintada e luz real; a Valve retirou sombras pintadas pesadas de um herói para a luz ficar difusa [F1][F17]. Logo: AO e gradiente leves no atlas, sombra projetada só do motor.

## 4. Micro-voxel

- **Quando usar**: câmera próxima (dungeon), rostos, armas na mão. É o argumento do Hytale para dobrar a densidade [F1].
- **Riscos**: em alta resolução o sombreamento manual some e o serrilhado aparece; usar cores simples e sombra do motor [F15]. Detalhe menor que 1 pixel pisca [F23]. Malha mais pesada [F15].
- **Coesão com voxel normal**: razão inteira 2:1, grades alinhadas, nunca dois tamanhos no mesmo rig [P, de F1, F10]. Na câmera alta, se o voxel projetado ficar abaixo de 2 px, trocar por LOD fundido 2×2×2 [P].

## 5. Pixel art renderizada em 3D

- **Dead Cells** [F21]: modelo 3D básico; render pequeno "without antialiasing"; cada frame sai em PNG com normal map e recebe toon shader; animação em poses-chave, interpolação só antes ou depois da chave, "never in-between"; reuso de rig entre monstros.
- **Linha t3ssel8r** (relato de David Holland, 2024; vídeo original não transcrito) [F22]: contorno de 1 px com núcleo de 4 vizinhos; profundidade dá a silhueta, normais dão vincos; realce só em aresta convexa; câmera presa a grade de texel alinhada à vista, com o erro devolvido em espaço de tela.
- **ProPixelizer** [F23]: o rastejar de pixel (pixel creep) "can only ever be solved for orthographic projections"; contorno por ID, de modo que personagem e equipamento formam uma silhueta só; alinhar a grade de pixel das peças filhas à raiz; paleta por LUT e dither 4×4; animação em degraus com interpolação constante; snap de ângulo.
- **Texel Splatting** (2026) [F24]: em perspectiva nenhum snap único estabiliza todas as profundidades; posterização da luminosidade em OKLab; contorno aplicado como deslocamento de luminosidade.
- **HD-2D** [F25]: errou com pouca profundidade e depois com resolução e saturação demais, "losing the appeal of pixel art".

## 6. Sintomas de arte feita por código

| Sintoma | Correção |
|---|---|
| Ruído por voxel ("estática") | variação só em clusters ≥ 3; zero `random()` por voxel [F6][F19] |
| Rampa reta, sombra cinza | hue shift; sombra fria ou roxa [F18][F1] |
| Sombra concêntrica (pillow) ou degradê liso de ferramenta | luz direcional fixa; degradê em 3 a 5 faixas com borda irregular [F10][F6] |
| "Sabonete" de SDF: tudo arredondado em escadinha | facetar; hexágono no lugar de círculo; "blocky before organic" [F6][F12] |
| Detalhe igual em todo lugar | área de descanso ≥ 55%; detalhe em cabeça, arma e tronco [F17] |
| Chapado: face grande de cor única | gradiente de valor em 2 a 3 faixas [F1] |
| Mixels | uma densidade por classe [F10][F2] |
| Voxel flutuante, ligação por canto, haste de 1 voxel | conectividade por face; espessura mínima [F6][F14] |
| Preto ou branco puros, canal no teto | clamp 10 a 245 [F1][F6][F17] |
| Cinza uniforme em tons de cinza | separar materiais por valor; pés escuros, cabeça clara [F17] |
| Peças se atravessando na junta | desenhar a junta para rig rígido; folga de 1 voxel [F15] |
| Simetria perfeita e limpa demais | 1 a 3 quebras intencionais [P] |
| Membros e cabeças de espessura aleatória entre criaturas | módulos padrão por tier [F2] |

## 7. Orçamentos por classe [P, ancorados em F7, F9, F13, F14]

| Classe | Voxel (stud) | Eixo maior (voxels) | Cores |
|---|---|---|---|
| Avatar e NPC (2,8 studs) | 0,125 | 22–24 de altura, ≤ 12 de largura, cabeça 8–9 (≈ 2,6 cabeças) | 12–20 |
| Arma de uma mão | 0,125 | ≤ 32 × 8 × 8, cabo de 1–2 | 6–12 |
| Chapéu ou elmo | 0,125 | largura ≤ 2× a cabeça, altura ≤ 1,4× | 6–12 |
| Criatura comum (1 casa) | 0,125 | 12–32 | 8–16 |
| Elite (1–2 casas) | 0,125 | 32–64 | 12–24 |
| Chefe (2–4 casas) | 0,125 | 64–128, dividido em partes ≤ 128³ | 16–32 |
| Estrutura (1×1 a 8×8 casas) | 0,25 | 16 por casa, 16 a 128 de lado | 12–32 |

## 8. Rubrica de auditoria (0 a 10)

- **0–2** Falha de portão: mixels, voxel flutuante, preto ou branco puros, escala fora de 0,7–1,3. Ilegível em silhueta.
- **3–4** Legível só de perto. Ruído ou rampa reta visíveis. Detalhe uniforme. Parece saída de ferramenta.
- **5–6** Silhueta lê nas duas câmeras. Rampas com matiz deslocado, mas valor sem hierarquia; materiais não se distinguem em tons de cinza.
- **7–8** Hierarquia grande, médio e pequeno clara; foco em cabeça e arma; materiais reconhecíveis; coeso com a facção. Um ou dois avisos de lint.
- **9–10** Zero aviso. Reconhecível a 48 px de altura. Assimetria com intenção. Sobrevive ao teste do tabuleiro e ao da dungeon, de dia e no escuro. Colocado ao lado de três assets do conjunto-ouro, não destoa.

Qualquer falha nas regras 1, 3, 4 ou 12 limita a nota a 4.

## 9. Regras acionáveis

1. **[P, de F1, F10]** Um rig, um tamanho de voxel (corpo, equipamento, cabelo, VFX). Vértices em múltiplos do voxel no espaço do osso; `mixels = 0`.
2. **[P, razão de F1]** Densidade por classe: 0,125 para personagem, criatura, equipamento e VFX; 0,25 para estrutura e prop. Origens em múltiplos de 0,25.
3. **[F1]** Escala por osso entre 0,7× e 1,3× por eixo.
4. **[F6, F14]** Cada parte rígida é um único componente conexo por faces; flutuantes = 0; ligações só por aresta ou canto = 0.
5. **[P; exceção F7]** Espessura mínima de 2 voxels; 1 voxel só em cabo de arma, olho, dente e gema marcados como `detalhe`.
6. **[F7]** Todo equipamento declara caixa-limite e um único ponto de encaixe; nada invade o cubo 3×3×3 do encaixe; estouro da caixa reprova.
7. **[P, de F17]** Silhueta ortográfica nas duas câmeras a 64 px: ocupação da caixa entre 35% e 70%; IoU frente×lado ≤ 0,85; IoU contra outro arquétipo do mesmo tier ≤ 0,80.
8. **[P, de F17]** Massas: 1–2 primárias somando ≥ 60% do volume; 2–5 secundárias de 5–25% cada; terciárias < 3% cada e ≤ 15% no total.
9. **[P, de F17]** Descanso ≥ 55% da superfície visível; ≥ 60% dos voxels de detalhe na metade superior.
10. **[P, de F1, F6, F12]** Nenhuma esfera ou cilindro de raio > 4 voxels sem facetar; degraus de silhueta com comprimento monotônico, no máximo 1 inversão por arco.
11. **[P]** Chanfro de 1 voxel em caixas com lado ≥ 8; nunca em peças < 4.
12. **[F6, F1, F17; teto P]** Nenhum canal RGB abaixo de 10 nem acima de 245.
13. **[F18; faixa P]** Rampa de 3 a 5 degraus; hue shift de 8° a 15° por degrau, máximo 20°; luz para quente, sombra para frio; saturação com pico no meio; ΔL entre vizinhos de 0,06 a 0,14.
14. **[P, de F19, F14]** 8 a 24 cores por asset (32 em chefe), 3 a 5 materiais, zero cor fora de rampa declarada. Paleta mestre ≤ 128; teto do `.vox`: 255 [F29].
15. **[P, de F17]** Saturação HSV > 0,75 em no máximo 5% da superfície, só em ponto focal; divisão 60/30/10 (±10) entre dominante, secundária e acento.
16. **[F17; números P]** L médio do terço superior ≥ terço inferior + 0,04; desvio-padrão de L maior em cima.
17. **[P, de F6, F19]** Voxels órfãos (cor diferente dos 4 vizinhos no plano) ≤ 1,5% das faces visíveis; variação só em clusters ≥ 3.
18. **[P, de F1]** Nenhuma região plana de cor única > 48 faces: aplicar 2 a 3 faixas.
19. **[P, de F17]** Em tons de cinza, materiais vizinhos diferem ≥ 0,08 em L médio.
20. **[F20; intensidade P]** AO por vértice de 4 níveis com inversão de diagonal; escurecimento máximo de 25%; topo +6–10% de L, faces de baixo −8–12%; nenhuma sombra projetada no atlas.
21. **[P]** Emissivo ≤ 3% da superfície, com vizinhança ≥ 0,3 de L mais escura.
22. **[P]** Voxel projetado ≥ 2 px no tabuleiro e ≥ 3 px na dungeon (1080p); abaixo disso, LOD 2×2×2.
23. **[F21, F23]** Sprite 3D: sem antialiasing, alfa só 0 ou 255, escala inteira, câmera ortográfica com snap à grade de texel.
24. **[F22, F23; cor P]** Contorno de 1 px por ID (personagem + equipamento = um ID); cor = um degrau abaixo da sombra da rampa, nunca preto.
25. **[F24, F23; números P]** Luz em 3 a 4 faixas (posterização de L em OKLab); ≤ 16 cores por sprite, 24 com equipamento; dither só 4×4 ordenado, ≤ 10% da área.
26. **[F21, F23; fps P]** Sprite animado em degraus, interpolação constante, 8 a 12 fps, poses-chave primeiro.

**Calibração**: antes de travar os [P], medir todas as métricas num conjunto-ouro de 20 a 30 assets aprovados à mão e fixar cada limiar no intervalo entre os percentis 10 e 90.

## 10. Glossário

- **Mixels**: elementos de resoluções misturadas no mesmo modelo ou cena [F10].
- **Rampa** (color ramp): tons de um material ordenados por brilho. **Rampa reta**: só o brilho muda.
- **Hue shift**: girar o matiz ao longo da rampa.
- **Cluster**: grupo conexo de voxels ou pixels da mesma cor.
- **Banding, pillow shading, pancake shading**: faixas alinhadas que revelam a grade; sombra concêntrica que ignora a luz; luz de um lado e sombra do outro, ignorando a forma [F10][F19].
- **Jaggy**: degrau fora de ritmo numa linha.
- **AO** (ambient occlusion): escurecimento de cantos e frestas.
- **Área de descanso**: região de pouco detalhe que valoriza o foco.
- **Pixel creep**: tremor de pixels quando objeto ou câmera se movem em render de baixa resolução.
- **Greeble**: estilo voxel de alta resolução com micro-relevo.
- **Rig de corpo rígido**: cada peça presa a um osso, sem deformação.

## 11. Fontes

- **F1** https://hytale.com/news/2025/12/an-introduction-to-making-models-for-hytale — primitivas, densidade de texel, esticamento, luz pintada, cor (22/12/2025).
- **F2** https://hytale.com/news/2019/4/designing-monsters-for-hytale — coesão de escala e facção (2019; o site marca como desatualizado).
- **F3** https://hytale.com/news/2019/2/customizing-your-character-in-hytale — camadas de avatar e cor por tema (2019).
- **F4** https://hytale.com/news/2019/1/take-a-closer-look-at-hytale-model-maker — cuboides, planos, personagens modulares (2019).
- **F5** https://hytalemodding.dev/en/docs/established-information/server/content-categories/art-assets — Blockbench substitui o Model Maker (comunidade).
- **F6** https://trovesaurus.com/page=3976 — guia de estilo do Trove e lista de rejeições (2019).
- **F7** https://trovesaurus.com/page=5631 (também 5629, 5630, 5632, 5634, 5635, 5636, 5633) — dimensões por tipo (2024).
- **F8** https://trovesaurus.com/page=3749 e https://trovesaurus.com/page=1584 — revisão, sufixos `_a _s _t`, tipos de material.
- **F9** https://book.veloren.net/contributors/artists/voxel-models.html e https://book.veloren.net/print.html — 22×10, bloco 11³, animação por código.
- **F10** https://www.blockbench.net/wiki/guides/minecraft-style-guide — mixels, rampas, defeitos de sombreamento, 1 px = 6,25 cm.
- **F11** https://minecraft.wiki/w/Skin — modelo de 32 × 16 px.
- **F12** https://www.vfxapprentice.com/blog/mojang-vfx-of-minecraft-dungeons — VFX do Dungeons, Chris Nordgren (29/08/2023).
- **F13** https://wiki.playstaxel.com/Tile — tile 16³.
- **F14** https://teardowngame.com/modding/ ; https://blog.voxagon.se/2020/12/03/spraycan.html ; https://softwareengineeringdaily.com/wp-content/uploads/2024/12/SED1772-Teardown.txt — limites, paleta de materiais, voxel de 10 cm.
- **F15** https://www.gamedeveloper.com/art/voxelart-styles-in-video-games e https://80.lv/articles/working-with-voxels-in-gamedev — estilos e animação voxel, Zach Soares.
- **F16** https://80.lv/articles/sir-carma-magica-voxel-was-like-having-infinite-legos-in-my-computer ; https://80.lv/articles/voxel-dioramas-tips-and-tricks/ ; https://80.lv/articles/using-voxels-for-simple-dioramas ; https://80.lv/articles/approaching-voxel-pixel-art — conselhos de artistas.
- **F17** https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935 — guia de arte de personagem do Dota 2 (Valve).
- **F18** https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes — rampas, 20° de hue shift.
- **F19** https://pixeljoint.com/forum/forum_posts.asp?TID=11299 — tutorial de pixel art (cure).
- **F20** https://0fps.net/2013/07/03/ambient-occlusion-for-minecraft-like-worlds/ — AO por vértice em voxel.
- **F21** https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i- — pipeline do Dead Cells (25/01/2018).
- **F22** https://davidholland.netlify.app/articles/3d-pixel-art-rendering — contorno e câmera no estilo t3ssel8r (24/09/2024).
- **F23** https://propixelizer.github.io/docs/usage/outlines (e `/eliminate-pixel-creep/`, `/palette-tools/`, `/stepped-animation/`, `/tips/`) — contorno por ID, creep, paleta, degraus.
- **F24** https://arxiv.org/html/2603.14587v1 — Texel Splatting (15/03/2026).
- **F25** https://www.siliconera.com/project-octopath-traveler-developers-answer-project-started-troubles-developing-hd-2d/ e https://nintendoeverything.com/octopath-traveler-devs-on-character-origins-visual-style-initial-hd-rumble-plans-much-more/ — erros do HD-2D.
- **F26** https://en.wikipedia.org/wiki/Body_proportions e https://en.wikipedia.org/wiki/Chibi_(style) — contagem de cabeças.
- **F27** https://www.w3.org/TR/WCAG21/ — fórmula de luminância relativa.
- **F28** https://gist.github.com/Vazkii/6049710 e https://gamersnexus.net/gg/962-everything-about-cube-world — formato `.cub`; cubos nas armas.
- **F29** https://raw.githubusercontent.com/ephtracy/voxel-model/master/MagicaVoxel-file-format-vox.txt — paleta de 256 entradas, índices 1 a 255.
- **F30** https://www.gamedeveloper.com/game-platforms/cloudpunk-creator-marko-dieckmann-on-cyberpunk-voxel-art-and-constant-fight-that-is-indie-development — Cloudpunk (26/08/2020).
