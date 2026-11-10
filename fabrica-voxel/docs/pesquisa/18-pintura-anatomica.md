# 18 - Pintura anatômica para criaturas voxel

Data: 2026-11-10. Escopo: como a cor segue a anatomia (escama, pelo, pena, quitina, osso, gosma, pedra, casca, carne, pano).

Marcas: [LIDO] abri a página e li. [RESUMO] só resumo da busca. [PROPOSTA] dedução minha, não vem de fonte.

## (a) Veredito

1. A fonte forte é a biologia e a regra geral de pixel art. Receita pronta de textura em voxel quase não existe na web aberta.
2. Quase todo número de motivo (tamanho em voxels, tons) abaixo é [PROPOSTA]. Nenhuma fonte lida dá tamanho de escama ou de tufo em pixels.
3. O que as fontes sustentam: poucos clusters repetidos, sem pixel solto, sem faixa paralela, sem sombra de travesseiro, tom claro no lado da luz, hue que esquenta ao clarear.
4. A biologia sustenta quatro lógicas de pintura: dorso escuro/ventre claro, escama sobreposta da cabeça para a cauda, segmento duro escuro com junta mole clara, aviso por anel de alto contraste.
5. Generalizar a hidra é viável: o motivo vira função de (superfície, direção do corpo, ruído suave de baixa frequência), com ruído só para decidir ONDE o motivo muda, nunca para sujar cada voxel.

## 1. Superfícies em baixa resolução

Aviso: nenhuma página lida deu tamanho de motivo em pixels. Onde há número, é [PROPOSTA].

### 1.1 Escamas
- [LIDO] Escama de peixe ósseo se sobrepõe "da cabeça para a cauda, como telhas". Escama de réptil é menor nas juntas, por flexibilidade, e maior onde há esforço. Ventre de cobra tem escamas largas que cobrem de um lado ao outro. (Wikipedia, Scale (anatomy).)
- [RESUMO] Escama e pena são formas de losango/arredondadas que se sobrepõem em deslocamento. (Creative Bloq, busca; página não aberta.)
- [LIDO] Slynyrd: textura boa precisa de "poucos clusters simples", repetidos com distribuição variada; não emphasize o contorno de cada tijolo (fica "muito ocupado"); deixe áreas vazias onde a textura é só sugerida.
- [PROPOSTA] Motivo mínimo: tijolo deslocado meia largura por fileira, 3 a 4 voxels de largura e 2 a 3 de altura. Fileira corre em anel ao redor do corpo. Borda de 1 voxel no tom 1 (ou 0 nas juntas), miolo no tom 2, 1 em 3 no tom 3. Tom 4 só no fio de luz de cima.
- [PROPOSTA] Ventre: placa larga de lado a lado, 1 voxel de altura por 1 de comprimento do corpo, tom 3 a 4 (mais claro que o dorso).
- [PROPOSTA] Perto de articulação, escama menor (2x2) e mais escura nas dobras.

### 1.2 Pelo (curto, longo, juba)
- [LIDO] Em pixel art se "implica" o pelo, não se desenha fio. Em sprite pequeno talvez nem precise de fio. Detalhe médio lê bem; detalhe pesado distrai. (itch.io, post sobre pelo.) A página não fala de tons nem de direção.
- [RESUMO] Pelo prende muita sombra por causa dos fios sobrepostos; pintar em tufos, não em fios. (guia de miniaturas, via busca.)
- [PROPOSTA] Curto: base no tom 2 com manchas alongadas de 2 a 3 voxels no sentido cabeça-cauda em tom 1 e 3; sem tom 0 nem 4 no miolo. Silhueta ganha dentes (voxels fora do corpo), não a cor.
- [PROPOSTA] Longo/juba: mechas de 1 de largura por 4 a 6 de comprimento, empilhadas, com ponta no tom 3 e raiz no tom 0 ou 1 (raiz no escuro porque a luz não chega). Mecha segue a gravidade e a curvatura do pescoço.

### 1.3 Penas
- [RESUMO] Mesma lógica da escama: formas arredondadas sobrepostas. [LIDO] o post do itch.io trata pena como pelo.
- [PROPOSTA] Coberteiras pequenas: escama alongada 2x3 com a ponta livre voltada à cauda. Remiges grandes: faixas de 1 voxel de largura em tom 1 (eixo) e tons 2/3 nos lados, corrida no sentido do comprimento da asa. Ponta da pena em tom 0 ou 3 conforme a espécie. Sem borda escura em toda pena.

### 1.4 Quitina / exoesqueleto
- [LIDO] Placas duras: tergito (dorso), esterno (ventre), pleura (lado). Juntas e membranas são cutícula mole. Membrana recém-formada é pálida. Esclerotização escurece e endurece (presas de aranha "muito endurecidas e escurecidas"); membrana não esclerotizada fica pálida e forma "ilhas" escuras de placa. (Wikipedia, Arthropod exoskeleton.)
- [LIDO] Cor estrutural muda com o ângulo de visão; nem todo besouro é iridescente. (Wikipedia, Structural coloration.) A página não descreve "faixa de brilho".
- [PROPOSTA] Segmento: placa em tom 1 a 2, 1 faixa de brilho no tom 4 de 1 voxel de largura, perpendicular ao eixo do corpo e perto do topo do segmento. Junta entre segmentos: 1 voxel. Para carapaça escura, junta clara (tom 3, membrana mole). Para casco pálido, junta escura (tom 0, sombra).
- [PROPOSTA] Brilho em faixa só em quitina lisa. Perna: anel escuro curto nas juntas (coleira), tubo claro no meio.

### 1.5 Osso
- [PROPOSTA] Tons 2 a 4 de uma rampa quente e bege, nunca branco puro. Cavidades (olho, nariz, entre costelas) no tom 0. Rachadura: linha de 1 voxel em tom 1, curta, nunca reta por mais de 4 voxels. Junta: nó 1 voxel mais claro. Costela: faixa de 1 voxel clara com sombra de 1 abaixo.

### 1.6 Pele úmida / gosma
- [PROPOSTA] Poucos tons (3), quase sem textura. Dois ou três pontos de brilho tom 4, cada um 1 a 2 voxels, sempre no lado da luz e nos topos de curvatura. Sombra em tom frio e saturado. Gosma escorrendo: coluna de 1 voxel mais clara descendo. Sem dither: fica "seco".
- [LIDO] Dithering "com parcimônia", melhor quando faz dois papéis ao mesmo tempo (gradiente e textura). (androidarts, tutorial de pixel art.)

### 1.7 Pedra
- [LIDO] Slynyrd, Rocks: cinza genérico resolve; a cor segue a geologia do lugar; a forma conta a história da pedra. Não dá tamanho de cluster.
- [PROPOSTA] Faces planas: 1 tom por face (3 a 4 voxels de largura mínima), tom 3 no topo, tom 1 nas faces laterais. Rachadura de 1 voxel em tom 0. Liquens em cima (já existe). Aresta clara de 1 voxel só nas arestas voltadas à luz.

### 1.8 Casca de árvore
- [PROPOSTA] Sulcos verticais (acompanhando o tronco) de 1 voxel em tom 0, separados por cristas de 2 a 3 voxels em tom 2. Comprimento do sulco 4 a 10, interrompido e deslocado. Topo da crista em tom 3. Sem anéis horizontais, a não ser em galho cortado.

### 1.9 Carne exposta
- [PROPOSTA] Rampa vermelha de baixo valor, tons 1 a 3. Fibra: veios de 1 voxel no sentido do músculo. Brilho úmido tom 4 em 1 ou 2 voxels. Borda da ferida escura (tom 0) de 1 voxel; pele em volta mais pálida. Tom 4 só no brilho, nunca em área.

### 1.10 Pano
- [PROPOSTA] Dobras como faixas de 1 a 2 voxels que partem de um ponto de tensão (cinto, ombro) e abrem em leque. Tons 1 a 3. Barra com 1 voxel mais escuro. Sem textura de trama.

### 1.11 Resumo de tamanhos em pixel art
- [LIDO] Fonte: androidarts: com tiles pequenos "clareza importa mais"; usar duas variantes de tile (uma cheia, uma quieta) para área grande não ficar uniforme.
- [RESUMO] Criaturas e blocos do Hytale: textura de criatura em torno de 64x64 e bloco 32x32, segundo comunidade, não oficial. Serve só como ordem de grandeza.

## 2. Regras contra ruído

- Cluster. [LIDO] "Grupo de pixels da mesma cor colocados juntos"; reduz pixels soltos e ajuda a evitar banding. (pixnote, glossário.) [LIDO] androidarts: agrupe pixels em ilhas, como se "gravitassem" uns aos outros.
- Tamanho mínimo de cluster. Nenhuma fonte lida dá número. [PROPOSTA] Mínimo 2 voxels conectados por face visível; exceção de 1 voxel só para brilho (tom 4) e para ponto de olho.
- Pixel órfão. [LIDO] Slynyrd: pixel isolado distrai o olho, evite, salvo dentro de textura maior. androidarts: pixel solto vira "ruído"; cada pixel precisa de propósito; órfão deliberado pode servir de textura se controlado.
- Banding. [LIDO] pixnote: cores de valores diferentes em faixas paralelas ao contorno parecem antinaturais; quebre com clusters ou dither. [LIDO] Pixel Parmesan: linhas de mesmo comprimento paralelas reforçam a grade e chamam a atenção. androidarts: compactar a mudança de valor, pôr a borda onde há terminador de sombra natural, ou quebrar o gradiente em tufos.
- Pillow shading. [LIDO] pixnote: sombreamento do contorno para o centro, sem fonte de luz. Pixel Parmesan: banding repetido ao longo do contorno gera pillow shading. [PROPOSTA] Num voxel, o equivalente é escurecer só por distância da borda da peça. A luz tem que vir de cima, não da borda.
- Dithering. [LIDO] pixnote: alterna duas cores em xadrez para sugerir tom intermediário. androidarts: usar com parcimônia. [PROPOSTA] Em voxel visto de cima e pequeno, o xadrez vira ruído. Preferir bloco de 2x2 ou faixa.
- Contorno de cada elemento. [LIDO] Slynyrd: evitar enfatizar o contorno de cada tijolo. Isto vale contra a borda escura em toda escama: a hidra funciona porque a borda é de 1 voxel e 1 em 3 sai mais clara, quebrando a grade.
- Mais cores não ajudam. [LIDO] androidarts: paleta contida costuma ficar melhor.
- Cuidado: [LIDO] "Voxel Art Styles" (Game Developer) diz que o estilo plano evita sombra dura e mostra cores vivas. Reforça poucos tons e luz suave.

## 3. Biologia que dá lógica

- Contra-sombreamento. [LIDO] Thayer (1909): animal mais escuro onde a luz do céu bate mais, mais claro embaixo; achata o volume. Cott corrigiu o exagero de Thayer. Evidência: 114 espécies de ruminantes seguem a previsão (Allen et al., 2012); em camundongo o gene Agouti produz o ventre claro. (Wikipedia, Countershading.)
- Exceções. [LIDO] Defensores (gambá, texugo-do-mel) têm barriga escura e dorso claro, como aviso. Animais que vivem de cabeça para baixo invertem (lagarta da luna, bagre-do-Nilo). Nunca aplicar contra-sombreamento em criatura de aviso.
- Direção de escama. [LIDO] cabeça para cauda, como telhas (Wikipedia, Scale). Pelo: direção cabeça-cauda nas costas, não achei fonte aberta. [PROPOSTA] Seguir o mesmo eixo.
- Anéis e faixas de aviso. [LIDO] Cores mais comuns e eficazes: vermelho, amarelo, preto, branco; sinais visuais de alto contraste, como listras; mais conspícuo, em geral mais tóxico. Abelhas e vespas simpátricas são miméticas Müllerianas. Cobra-coral é o modelo e a falsa-coral é imitadora Batesiana. (Wikipedia, Aposematism; lido só os primeiros 100 mil caracteres.) A ordem dos anéis da coral NÃO consta na página.
- Manchas disruptivas. [LIDO] Quebram o contorno com manchas de alto contraste, não repetitivas; devem tocar a borda do corpo (as "distrativas" ficam longe dela). A máscara disruptiva esconde o olho. (Wikipedia, Disruptive coloration.)
- Ocelos. [LIDO] Foco rodeado de anéis concêntricos; função de intimidar ou desviar o ataque; ficam em asa, em segmentos anteriores de lagarta (aparecem quando recolhe a cabeça), perto da cauda em peixes ("cabeça falsa"), atrás da cabeça em corujas-anãs. (Wikipedia, Eyespot.) Sem tamanhos absolutos.
- Segmentação. [LIDO] Tergito, esterno e pleura são placas duras. A junta é membranosa. Cutícula esclerotizada escurece; a mole fica pálida. Logo: placa escura e junta clara é o padrão fisiológico, mas depende da espécie. [PROPOSTA] Para insetos pálidos, pinte junta mais escura por sombra.
- Cicatriz e desgaste. Não achei fonte de biologia aberta. [PROPOSTA] Desgaste onde há atrito: cotovelo, joelho, ponta de chifre, garra, focinho, ventre rente ao chão. Cicatriz: risco de 3 a 6 voxels, em geral cruzando a escama, em tom 1 com 1 voxel de tom 3 ao lado, e sem repetição simétrica.

## 4. Cor

- Hue shift. [LIDO] Slynyrd: rampa com hue shift ganha interesse; padrão dele é shift positivo (esquenta ao clarear), até 20 graus por swatch; exemplo de 9 swatches por rampa; ao subir o brilho, baixar a saturação. "O maior erro é combinar saturação e brilho altos." Escuros podem carregar mais saturação, mas ficam "pesados" se exagerar.
- [LIDO] androidarts: o hue costuma mudar do claro para o escuro, evite preto e branco puros. Luz de sol amarela, sombra com cinza frio de céu.
- Quantos tons. [RESUMO] Guias falam 3 a 5 tons por rampa para visual compacto (4 a 6 segundo uma autora de skins de Minecraft). Nossa rampa de 5 está na faixa comum. Não encontrei guia de "sprite pequeno" específico.
- [PROPOSTA] Para 5 tons: shift total de 30 a 50 graus entre 0 e 4, sombra tendendo a frio, luz tendendo a quente. Saturação máxima no tom 1 ou 2; tom 4 com menos saturação.
- [PROPOSTA] Materiais emissivos (fendas, olhos) fora da rampa: cor própria, mais saturada, aplicada em poucos voxels.

## 5. Jogos de referência

Pouco foi confirmado. Ver seção (f).

- Warden (Minecraft). [LIDO] A textura é dividida em camadas: base, biolumin., coração, manchas pulsantes; as partes azuis são emissivas (wiki). [PROPOSTA] Lição: brilho como camada separada da pintura base, com poucos pontos. A wiki não dá contraste nem tamanho.
- Armadillo (Minecraft). [LIDO] A página não descreve o casco. Nada aprendido.
- Hytale. [LIDO] Post de 2019 (desatualizado): texturas de folhas cruzam o bloco; tinta RGB por bloco. [RESUMO] Criatura ~64x64, bloco 32x32 (comunidade). Direção artística "pixel art de baixa definição + pintado à mão". Sem tamanho de motivo.
- Estilo voxel plano. [LIDO] Game Developer: pixelado e plano mostra as cores vivas; sombra dura estraga o estilo.
- Trove, Cube World, Dragon Quest Builders, Voxatron, Sniffer: sem análise de textura encontrada.

## (c) TABELA FINAL: superfície -> padrão procedural

Rampa de 5 tons: 0 = mais escuro, 4 = mais claro. Todas as medidas e tons são [PROPOSTA], salvo nota. "Luz" = lado de cima.

| Superfície | Motivo (forma, voxels) | Direção | Tons | Onde NÃO aplicar | Parâmetros sugeridos |
|---|---|---|---|---|---|
| Escama de dorso (cobra, dragão, hidra) | tijolo deslocado 3-4 x 2-3, borda 1 | anel ao redor do corpo, fileira alternada meia largura, ponta livre para a cauda | borda 0/1, miolo 2, 1 em 3 em 3; fio de luz 4 só no topo | cabeça fina (<6 voxels), pés, juntas | escala 3x2 até 4x3 pelo tamanho; borda_prob 1.0; claro_1em3; ruído_borda 0.15 |
| Escama de ventre / placa | faixa larga de lado a lado, 1 de comprimento | perpendicular ao eixo do corpo | 3 e 4 alternados; junta em 2 | dorso, criatura de aviso com ventre escuro | passo 1-2; contra_sombra 1 |
| Escama de peixe | escama arredondada 3x3, sobreposta | cabeça-cauda, fileiras ao longo do corpo | 1 borda, 2 miolo, 3 no centro; 4 no flanco | barbatana, cauda | diâmetro 3; linha lateral em 3 |
| Pelo curto | manchas 2-3 x 1, tufos | cabeça-cauda no dorso; para baixo nas pernas | 1, 2, 3 (sem 0 e 4 no miolo) | cabeça (focinho liso), patas | densidade 0.25; comprimento 2-3; dentes na silhueta |
| Juba / pelo longo | mecha 1 x 4-6 empilhada | segue o pescoço, para trás e para baixo | raiz 0/1, meio 2, ponta 3 | corpo inteiro | largura 1; comprimento 4-6; variação 0.3 |
| Penas | coberteira 2x3 em escama; remige 1 x comprimento | cabeça-cauda; remige ao longo da asa | eixo 1, lados 2/3, ponta 0 ou 3 | pernas com escama | tamanho 2-3; eixo_central sim |
| Quitina segmentada | placa por segmento + faixa de brilho 1 voxel | anel por segmento, perpendicular ao eixo | placa 1/2; brilho 4; junta 3 (se placa escura) ou 0 (se pálida) | corpo mole (larva, abdome inflado) | junta 1 voxel; brilho 1 por segmento; só em quitina lisa |
| Osso | superfície lisa com cavidades e rachaduras 1 x 2-4 | acompanha o osso | 2-4; cavidade 0; rachadura 1 | carne, pelo | rachaduras max 3 por peça; não branco puro |
| Pele úmida / gosma | 2-3 brilhos de 1-2 voxels; coluna de escorrido 1 x 3-5 | brilho no topo da curvatura; escorrido para baixo | 1, 2, 3; brilho 4 | pedra, osso seco, pano | tons 3; brilho_n 2-3 por peça; sem dither |
| Pedra | faces planas, 1 tom por face; rachadura 1 | por face; luz em cima | topo 3, lado 1/2, rachadura 0 | criatura de carne | face min 3 voxels; rachadura max 6 |
| Casca de árvore | sulco 1 x 4-10; crista 2-3 | vertical, ao longo do tronco | sulco 0, crista 2, topo da crista 3 | folha, flor | deslocamento aleatório; interrupção 0.3 |
| Carne exposta | veios 1 x 3-6; brilho 4 em 1-2 voxels | fibra no sentido do músculo | 1, 2, 3; borda ferida 0 | pele intacta | brilho_n 1-2 por ferida; área máx 1/4 da peça |
| Pano | dobra 1-2 largura, em leque | do ponto de tensão (cinto, ombro) para baixo | 1, 2, 3; barra 0 | corpo vivo | n_dobras 3-5; sem trama |
| Ocelo (aviso) | disco 5-7 voxels: foco 1-2 voxels, anel 1-2, borda | no dorso, perto da borda ou da cauda | foco 4, anel 0, aro 2/3 | dorso inteiro (só 1 a 3 por criatura) | raio 2-3; distância à borda < raio |
| Anel / faixa de aviso | faixa de 1-2 voxels perpendicular ao eixo | anel completo | contraste máximo: 0 e 4 | criatura de camuflagem | largura 1-2; passo 3-4; só 1 hue contrastante |
| Cicatriz / desgaste | risco 1 x 3-6 diagonal; ponta clara | cruza o padrão | 1 com vizinho 3 | simétrico em ambos os lados | n 0-3 por criatura; desgaste em cotovelo, joelho, chifre, garra |
| Contra-sombra (geral) | gradiente por altura em 2 degraus | de cima para baixo no corpo | dorso -1 tom; ventre +1 tom | criatura de aviso (barriga escura) | amplitude 1 tom; degrau único |

## (d) Nunca faça

1. Nunca escureça só por distância à borda da peça (pillow shading).
2. Nunca use ruído por voxel. Ruído serve para decidir ONDE o padrão muda (como a fenda da hidra), com frequência baixa.
3. Nunca deixe voxel solto sem função (exceto brilho e olho).
4. Nunca ponha duas faixas paralelas de mesmo comprimento ao longo do contorno.
5. Nunca contorne cada escama, tijolo ou pena com borda contínua. Falhe 1 em 3 ou use variação.
6. Nunca use tom 0 e tom 4 em área grande. Tom 4 é fio de luz e brilho.
7. Nunca use preto ou branco puro. Use o 0 e o 4 da rampa.
8. Nunca aplique contra-sombreamento em criatura de aviso, nem listra de aviso em criatura de camuflagem.
9. Nunca mude a direção do padrão no meio de uma peça sem junta.
10. Nunca aplique brilho de quitina em corpo mole, nem escama em pelo.
11. Nunca repita o mesmo motivo com a mesma fase em todas as peças; varie fase e densidade.
12. Nunca use dither em xadrez 1x1 em peça pequena vista de cima.
13. Nunca combine saturação alta com brilho alto.
14. Nunca encha de detalhe uma peça pequena. Deixe áreas vazias.
15. Nunca simetrize cicatrizes.

## (e) URLs realmente abertas (conteúdo lido)

- https://www.slynyrd.com/blog/2018/2/15/pixelblog-2-texture
- https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes
- https://www.slynyrd.com/blog/2019/1/22/pixelblog-13-rocks (pouco útil)
- https://pixnote.net/en/learn/glossary
- https://pixelparmesan.com/anti-aliasing-fundamentals-for-pixel-artists
- https://www.androidarts.com/pixtut/pixelart.htm (autoria não confirmada na página)
- https://itch.io/post/6047047
- https://gamedeveloper.com/art/voxelart-styles-in-video-games
- https://www.hytale.com/news/2019/2/exploring-hytale-s-block-tech (desatualizada, sem dado útil de textura)
- https://minecraft.wiki/w/Warden (parcial: 100 mil de 166 mil caracteres)
- https://minecraft.wiki/w/Armadillo (parcial; nada sobre textura)
- https://en.wikipedia.org/wiki/Countershading (parcial)
- https://en.wikipedia.org/wiki/Aposematism (parcial)
- https://en.wikipedia.org/wiki/Arthropod_exoskeleton
- https://en.wikipedia.org/wiki/Disruptive_coloration
- https://en.wikipedia.org/wiki/Eyespot_(mimicry)
- https://en.wikipedia.org/wiki/Scale_(anatomy)
- https://en.wikipedia.org/wiki/Structural_coloration (parcial)
- https://saint11.art/blog/pixel-art-tutorials/ (abriu, mas só lista de imagens, sem texto)

Apenas [RESUMO] (não abertas): Creative Bloq (escama e pena), gamedev.net Color Palettes, guia de skins de Minecraft (4 a 6 tons), notícias do Hytale (64x64), 3dbrendang (pillow shading), guias de miniaturas (pelo).

## (f) O que NÃO confirmei

- Não abriu: art.cleberg.net (tutoriais de escama e pelo em pixel art) não resolve neste ambiente; precisa ser liberado na rede da sessão. Medium (pixel-grimoire) deu 403.
- Saint11 (Pedro Medeiros): a página abriu só com imagens. Nenhuma lição dele foi lida. Tutoriais de Rock, Fabric, Wood, Shading e Goo existem pelos nomes, mas não os li.
- Derek Yu: não achei nem abri o tutorial nem a página de erros comuns.
- Lospec: só apareceram listas de paletas; sem artigo lido.
- MagicaVoxel, Qubicle, Blockbench, Mega Voxels, Voxatron, Trove, Cube World, Dragon Quest Builders: nenhum guia de textura de criatura encontrado. O que a seção 5 diz sobre eles é vazio.
- Warden, Armadillo e Sniffer: as páginas abertas não descrevem contraste nem tamanho de motivo. Sniffer não abri.
- Tamanho mínimo de cluster, tamanho de escama e tamanho de tufo em pixels: nenhuma fonte deu número.
- Direção do pelo (cabeça para cauda): sem fonte aberta; só dedução.
- Ordem dos anéis da cobra-coral e a regra "vermelho com amarelo": a página de aposematismo não cobre (lida só em parte).
- Brilho especular em faixa de quitina: Structural coloration não descreve a forma do brilho. A faixa é [PROPOSTA].
- Cicatrizes e desgaste: sem fonte biológica aberta.
- Número de tons para sprite pequeno: só resumos de busca (3-5 e 4-6).
- Thayer no original (1909) e Cott (1940): não li; só via Wikipedia.
