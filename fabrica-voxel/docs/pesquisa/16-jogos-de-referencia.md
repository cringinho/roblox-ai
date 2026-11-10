# 16. Jogos de referência: como resolvem o movimento de criaturas

Data da pesquisa: 2026-11-10. Escopo: técnica concreta de jogos-referência, traduzida para ossos rígidos + camadas assadas a 30 fps.

Legenda das marcas:
- [LIDO] li na página aberta.
- [RESUMO] veio de resumo de busca (não abri a fonte, ou a fonte não confirmou).
- [PROPOSTA] dedução minha. Não é dado publicado.

Aviso honesto: as palestras primárias (GDC Rain World, GDC Overgrowth, GDC Horizon, paper do Spore) são vídeos ou PDFs que a ferramenta não conseguiu ler. Quase todo número de jogo vem de textos secundários. Onde a fonte não deu número, escrevi isso.

---

## (a) Veredito em 5 linhas

1. O que dá "vida" não é a curva do ciclo. É a **resposta ao movimento**: inclinar com a aceleração, atrasar o corpo em relação ao alvo, e deixar a perna dar o passo quando o pé fica longe demais (Overgrowth, Rain World, Spyder).
2. Todo o suavizado dos jogos citados converge para **mola criticamente amortecida** com tempo de 0,1 a 0,5 s. Dá para assar isso em 30 fps sem perda.
3. Peso de criatura grande vem de **limitar a velocidade de virada**, antecipação longa e passos com pés presos no chão. Não vem de mais ossos (Horizon).
4. Perna que "escolhe onde pisar" (Trico, Rain World) é a diferença entre andar que parece colado e andar que parece vivo. Em animação assada isso vira passos com IK e "pé travado".
5. Para ataque legível: a pose de início já diz qual golpe vem (Monster Hunter). Antecipação proporcional ao porte. Sem número oficial publicado.

---

## (b) Seção por jogo

### 1. Rain World (Joar Jakobsson, James Therrien)

**O que fazem**
- Criaturas são pontos no espaço ligados a distâncias fixas, desenhadas como "boneca de papel" de partes. Corpo mole e dobrável. [LIDO: gamedeveloper.com, matéria "Crafting the complex, chaotic ecosystem"]
- O corpo da Slugcat são duas esferas presas a distância fixa, o que a deixa girar e cair. Membros e cauda são cosméticos, animados por código a partir do input. [LIDO: unity.com/blog]
- Pernas da lagarto/croc (devlog 2012): cada perna alcança um ponto agarrável, segura, o corpo é puxado, solta e repete. Sensação de "se arrastar", não de correr. [LIDO: devlog, updates 46 e 47]
- Velocidade depende de quantas pernas seguram: 4 presas, anda muito rápido; todas no ar, quase não anda. Um pouco de movimento sobra sem pernas tocando, para não travar. [LIDO: devlog, update 49]
- Pé/braço trocam de sprite conforme a distância mão-corpo, em passos de 5 px por frame de animação. Posição vem do alvo, então o pixel continua preciso. [LIDO: devlog, update 59]
- Variação por indivíduo: gordo/magro, cauda curta/longa, velocidade de ronda como atributo. [LIDO: devlog, updates 30 e 62]
- A palestra GDC 2016 "The Rain World Animation Process" separa "estatísticas da criatura" da animação. [RESUMO]

**Números publicados**
- 13 sprites no croc com pés. 8–9 ms por croc nas pernas vetoriais, orçamento de 25 ms por frame (motivo de trocar por pixel). [LIDO: devlog, updates 45 e 56]
- Sem constantes de mola, atrito, contagem de segmentos. Só li até o caractere 300000 do devlog (de 785814).

**Como traduzir para ossos rígidos + camadas assadas**
- [PROPOSTA] Camada "agarra-puxa": cada pé tem fase de alcançar, segurar, soltar. O corpo avança só enquanto algum pé segura. Velocidade do corpo = fração de pés presos. Serve a lagartos, répteis, aranhas.
- [PROPOSTA] Mantenha uma velocidade mínima com zero pés presos (piso de 10–15% da velocidade) para a criatura nunca congelar.
- [PROPOSTA] Atributos por indivíduo (comprimento da cauda, espessura, velocidade) entram como parâmetros da fábrica, não como animações novas.

### 2. Overgrowth / David Rosen (GDC 2014)

**O que fazem**
- Locomoção base com poucas poses-chave e camadas de código por cima. [LIDO: techarthub.com]
- Os 10 passos de Rosen, como listados no artigo: movimento responsivo; pose de repouso girando para a velocidade; inclinação pela aceleração; roda de passada com poses "passa" e "alcança"; velocidades de andar e correr separadas; mistura entre velocidades e poses; salto por gravidade (talvez com balanço); mistura de fase; pose aditiva de agachar; interpolação por mola entre poses aditivas. [LIDO: techarthub.com]
- Receita de inclinação, reimplementada por outro autor em Unreal (Little Polygon, que chama o texto de Rosen de "melhor apresentação sobre o assunto"): eixo = vetor "para cima" x aceleração, ângulo proporcional à aceleração, limitado, suavizado por mola. [LIDO: blog.littlepolygon.com/posts/loco1]

**Números publicados**
- 13 poses-chave na locomoção base. [LIDO: techarthub.com. Também no forum Unity, [RESUMO]]
- Sem constante de mola nem ângulo de Rosen em nenhuma fonte que abri. A página do GDC Vault só tem a descrição; o vídeo estava fechado. [LIDO: gdcvault.com/play/1020049]
- Números da reimplementação Little Polygon (NÃO são de Rosen): LeanMulti = 0,64; ângulo máximo de inclinação 45°; suavização da inclinação 0,25 s; suavização da rotação 0,1 s; amplitude do quadril 0,5 s; aceleração 0,5 s e desaceleração 0,25 s; vai-e-vem vertical do quadril com frequência de fase 2,0 (~2 Hz no balanço vertical, ~1 Hz no balanço lateral, inferência do próprio autor do blog sobre o código); balanço lateral do quadril 8°. [LIDO: Little Polygon]
- Regra prática "4/T" para atrito: aceleração = -(4/T)·v + (4/T)·velocidade_alvo·entrada. [LIDO: Little Polygon]
- Mola de duração: ω = 2/duração, decaimento exponencial exato. [LIDO: Little Polygon]

**Como traduzir**
- [PROPOSTA] Camada "inclina": roll/pitch do tronco em graus a partir da aceleração, teto por porte, suavizada com mola de 0,25 s. Em animação assada, a aceleração vem da curva de velocidade do clipe (partida, parada, curva).
- [PROPOSTA] Pose aditiva + mola é o jeito certo de fazer agachar, receber dano e pousar: pose-alvo somada, mola de 0,1–0,2 s.

### 3. Spore / Chris Hecker

**O que fazem**
- Animações são autoradas sem saber o esqueleto final, em ferramenta própria (Spasm) com keyframe normal. Guardadas de forma independente da morfologia. Em tempo de execução viram "metas de pose" para um solucionador de IK robusto. [LIDO: beyondsims.com, resumo do paper]
- Paper: "Real-time Motion Retargeting to Highly Varied User-Created Morphologies" (SIGGRAPH 2008). [RESUMO: página do paper existe; não li o conteúdo]

**Números publicados**: nenhum lido. O PDF do Chalmers veio binário ilegível. A página chrishecker.com estava fora do ar.

**O que NÃO consegui confirmar**: o agrupamento de pernas por fase (grupos de pernas) é conhecimento geral sobre o paper, mas **não** consegui ler isso. Não afirmo.

**Como traduzir**
- [PROPOSTA] Ideia aproveitável sem ler o paper: autore a marcha uma vez em "grupos de pernas" (par A e par B em contrafase) e deixe a fábrica mapear quantas pernas houver. É dedução minha, a conferir.

### 4. The Last Guardian (Trico) e Shadow of the Colossus

**O que fazem** (fonte: slides do tech talk de Tanaka, Google Slides; o slide não diz que foi GDC) [LIDO]
- Animação procedural em módulos, do principal ao detalhe: corpo, depois pernas, cabeça, dedos.
- Coluna dobra para seguir uma curva Bezier da IA; há limite de ângulo de dobra, e a navegação cria rota alternativa em curvas muito fechadas.
- Passo: o ponto de pouso é escolhido **no instante em que o pé levanta**, considerando altura e ângulo. É reverificado durante o movimento. Locais inválidos: obstáculos, rampa íngreme, perto de parede.
- O ciclo de andar é um laço de 4 movimentos de perna.
- Trajetória mistura o caminho natural de andar com o caminho mais curto até o alvo.
- Pé preso ao chão (sem deslizar). Quando o pé solto volta, interpola de volta à pose normal.
- Deslocamento do pé em relação à posição original ajusta a postura do corpo.
- Sensor acima da cabeça detecta teto baixo; cabeça e corpo abaixam.
- Olhar: método "dança do leão". Define posição e rotação da cabeça primeiro, e o pescoço é derivado depois. Eixo de rotação o mais à frente possível na cabeça, para dar expressão.
- Penas: método "fin" (tiras longas), reagindo ao vento em ondas. Shadow of the Colossus usava o método "shell". [LIDO]
- Nível de interesse por objeto sobe com o tempo e cai ao agir; escolhe a ação (comer, coçar, som). [LIDO]
- Sem mocap: tudo em keyframe. [RESUMO]

**Números publicados**: nenhum (os slides só têm exemplos).

**Como traduzir**
- [PROPOSTA] Olhar com limite: a cabeça vai primeiro ao alvo, o pescoço (cadeia de 2–4 ossos) distribui o ângulo com atraso crescente. Limite de ±60° na cabeça e ±25° por osso de pescoço como ponto de partida.
- [PROPOSTA] "Pé travado": enquanto o pé está em apoio, sua posição mundial é fixa; a camada de passo só decide quando levantar e onde pousar.
- [PROPOSTA] Pouso decidido na saída do pé, igual ao Trico; no assado isso vira posições fixas por passada.

### 5. Monster Hunter (World / Rise / Sunbreak)

**O que fazem**
- Lead animator Ken Yamazaki (Rise/Sunbreak): "Na maioria dos ataques, consigo saber o que vem só olhando a animação de início" e sabe quando o monstro está aberto a contra-ataque. [LIDO: news.capcomusa.com, 2023-04-07]
- Mocap só quando o movimento pode ser "copiado" por humano (ex.: Garangolm). Serve de base; o resultado final fica bem diferente. [LIDO: mesma página]
- Antes do World, toda animação de monstro era keyframe. [RESUMO: entrevista do Wilds]

**Números publicados**: nenhum. A página não fala de peso, viradas, respiração nem idle.

**Como traduzir**
- [PROPOSTA] Cada golpe tem pose de início inconfundível (silhueta própria). A fábrica deve exigir que as poses de início de dois golpes diferentes difiram em pelo menos um osso grande, ≥30°.
- [PROPOSTA] Fases fixas em todo ataque: antecipação, golpe, recuperação aberta. Janela de recuperação é onde o jogador pune.

### 6. Horizon Zero Dawn (Guerrilla)

**O que fazem**
- Peso: a velocidade de virada é limitada ("não dá para virar rápido demais, senão perde o peso"). Peso também vem de som, partículas e tremor de câmera. [LIDO: gamedeveloper.com, "Making Horizon's machines feel like living creatures"]
- Teste de movimento cedo com modelos ZBrush sem acabamento, esqueleto e baixa taxa de quadros. [LIDO: mesma]
- Variação: ciclos extras misturados aleatoriamente para quebrar a repetição. [RESUMO: cobertura da palestra de Richard Oud, GDC 2018; não li]
- Ajuste procedural de pés da Aloy: animação decide **quando**, código decide **onde** (palestra de traversal 2017). [RESUMO]

**Números publicados**: nenhum de animação. Só prazos de produção (Thunderjaw: ~5 modeladores por ~8 meses; ~18 meses até ficar jogável). [LIDO]

**Como traduzir**
- [PROPOSTA] Regra de peso: velocidade angular máxima do corpo por porte (ver tabela). A fábrica deve limitar a virada, não só suavizá-la.
- [PROPOSTA] 2–3 variantes do ciclo com tempos levemente diferentes (±8%) sorteadas por passada para quebrar o laço.

### 7. Hollow Knight, Dead Cells, Hades

**Hollow Knight**: não achei nada da Team Cherry com contagem de quadros. Os números que circulam (antecipação de 0,3–0,5 s em ataques aparáveis) vêm de um guia sem fonte. [RESUMO, baixa confiança]
**Dead Cells**: pipeline 3D para pixel confirmado pelo artista Thomas Vasseur, para ter suavidade sem desenhar cada retake. [RESUMO: jikguard abriu uma página errada; não li o texto]
**Hades**: não pesquisei a fundo; sem fonte lida.

**Como traduzir**
- [PROPOSTA] Do 2D: poucos quadros de antecipação bem marcados e **parada no pico do golpe** (2–4 quadros a 30 fps) leem mais claro que movimento contínuo.

### 8. Deep Rock Galactic, Grounded e aranhas procedurais

Não achei fonte dos dois jogos. Fontes substitutas:
- Godwalker (devlog de Josh Hirshfield): cada pé guarda posição atual e alvo; quando fica longe demais atrás do alvo, dá passo **além** do alvo na direção em que ele vinha. Parâmetros por pé: distância à frente, velocidade de retorno, imprecisão aleatória. Pernas se revezam; ficam juntas só após movimento brusco. Dash mais rápido que a velocidade de retorno parece investida. Sem valores. [LIDO: joshhirshfield.substack.com]
- Spyder (Sumo Digital): tentei abrir, deu 403. Resumo: posições-alvo de pé como curvas por perna e IK "preditivo". [RESUMO]
- Unity spider asset: perna dá passo quando o solucionador não alcança o alvo dentro da tolerância; o corpo sobe e gira com as pernas. [RESUMO]

**Como traduzir**
- [PROPOSTA] Regra "passo por distância": o pé levanta quando a distância ao ponto ideal passa de ~60% do alcance da perna; pousa ~40% do alcance à frente do ponto ideal ("passo além"). Revezamento obrigatório: nunca mais de 1/3 das pernas no ar (aranha de 8: até 2–3).
- [PROPOSTA] Imprecisão aleatória de ±10% no pouso, com semente fixa por passada (o assado é determinístico).

### 9. Jogos de blocos: Hytale, Minecraft

**Hytale** (plugin oficial do Blockbench, about.md) [LIDO]
- Formato `.blockyanim`; interpolação por quaternion; keyframes de posição/rotação no grupo (filhos herdam), escala/visibilidade/UV só na forma.
- Limite de 255 nós por modelo. Sem taxa de quadros e sem outras interpolações documentadas.
- Faixas de tempo "andar 0,8–1,2 s; ataque 0,3–0,8 s" vêm de uma página de skill de terceiros. [RESUMO, comunidade]

**Minecraft (Warden, Sniffer, Camel)**: não achei entrevista nem definição de animação da Mojang. Só notas de comunidade: Warden/Sniffer elogiados como suaves; Camelo criticado por sentar devagar demais; alguns acham a marcha "realista demais" para o estilo. [RESUMO]

**Trove, Cube World**: não pesquisei.

**Como traduzir**
- [PROPOSTA] Interpolação por quaternion (slerp) nos ossos, nunca por Euler, para evitar viradas estranhas. Já bate com o que o Hytale faz.

### 10. Técnicas nomeadas

**Mola criticamente amortecida** (Daniel Holden, theorangeduck.com "Spring Roll Call") [LIDO]
- Amortecimento 1 = crítico, sem oscilar. Parâmetro prático: meia-vida. Atraso em alvo que se move a velocidade constante = meia-vida / ln 2.
- Meia-vida pequena remove tremores. Sem valores recomendados por uso.
- Constante de conversão: 4·ln2 / meia-vida (o "4" é fator empírico).

**Inertialização / dead blending** (Holden) [LIDO]
- Na troca de clipe, guarda o desvio de posição e velocidade e o deixa decair com mola. Sem tempo fixo de mistura, sem overshoot no caso crítico.
- Mistura "normal" usada no artigo: 0,2 s; teste exagerado: 1 s. Sem meia-vida recomendada.

**Foot lock / foot IK, look-at com limite, camada aditiva de respiração**: sem fonte primária lida além do Trico acima.

---

## (c) Tabela: técnica para camada ou regra da fábrica

Valores iniciais. Quase todos são [PROPOSTA]; a coluna Base diz de onde vem o que existe. Portes: P = pequeno (rato, inseto), M = médio (lobo, goblin), G = grande (urso, ogro), XG = gigante (dragão, colosso).

| Técnica | Camada / regra | Valor inicial | Base |
|---|---|---|---|
| Inclinar pela aceleração | roll/pitch do tronco | multiplicador 0,64; teto P 25°, M 30°, G 15°, XG 8°; suavização 0,25 s | 0,64 / 45° / 0,25 s: Little Polygon [LIDO]; tetos por porte [PROPOSTA] |
| Mola crítica de pose | `seguir_pai` com mola | amortecimento 1,0; meia-vida P 0,06 s, M 0,10 s, G 0,18 s, XG 0,30 s (≈ 2,2 / 1,4 / 0,8 / 0,5 Hz natural) | forma: Holden [LIDO]; valores [PROPOSTA] |
| Atraso de cadeia (cauda, orelha, cabelo) | atraso por osso | +0,04 s por osso (P), +0,06 s (M/G), +0,08 s (XG); atraso = meia-vida / 0,69 | fórmula: Holden [LIDO]; valores [PROPOSTA] |
| Antecipação de golpe | pose-chave antes do golpe | P 0,08–0,15 s; M 0,15–0,30 s; G 0,30–0,60 s; XG 0,60–1,10 s. Pico parado 2–4 quadros | Hollow Knight 0,3–0,5 s [RESUMO fraco]; resto [PROPOSTA] |
| Recuperação aberta | pose após golpe | 1,5x a duração da antecipação | [PROPOSTA] |
| Limite de virada (peso) | rotação do corpo | vel. angular máx.: P 720°/s, M 360°/s, G 180°/s, XG 70°/s; suavização 0,1 s no yaw | princípio: Horizon [LIDO]; números [PROPOSTA]; 0,1 s: Little Polygon [LIDO] |
| Passo por distância | `passos` com IK de 2 ossos | pé levanta a 60% do alcance; pousa 40% à frente; máx. 1/3 das pernas no ar; ruído ±10% | princípio: Godwalker/Trico [LIDO]; números [PROPOSTA] |
| Pé travado | regra do pé em apoio | posição mundial fixa durante apoio; volta à pose neutra por interpolação ao soltar | Trico [LIDO] |
| Cadência de passos | frequência do ciclo | P 3,5 Hz, M 2,0 Hz, G 1,2 Hz, XG 0,6 Hz (passadas/s) | [PROPOSTA]; Hytale 0,8–1,2 s por ciclo [RESUMO] |
| Balanço do quadril | seno vertical + roll | roll 8° a 1x a cadência de passada (meia freq. do vertical); amplitude suavizada em 0,5 s | 8° / 0,5 s: Little Polygon [LIDO]; escala por porte [PROPOSTA] |
| Respiração aditiva | seno no tronco/costelas | P 1,2 Hz, M 0,5 Hz, G 0,3 Hz, XG 0,15 Hz; amplitude 1–3° no tronco | [PROPOSTA], sem fonte de jogo |
| Olhar com limite | cadeia pescoço-cabeça | cabeça ±60°, pescoço ±25° por osso, atraso 0,08 s por osso; cabeça primeiro | método: Trico [LIDO]; números [PROPOSTA] |
| Inertialização | troca entre clipes assados | desvio decai com meia-vida 0,08–0,15 s; sem mistura linear | Holden [LIDO]; 0,2 s de mistura normal [LIDO]; meia-vida [PROPOSTA] |
| Agarra-puxa (rastejantes) | velocidade do corpo = pés presos / total | piso de 10–15% da velocidade com zero pés | Rain World [LIDO]; piso [PROPOSTA] |
| Variação de ciclo | 2–3 variantes sorteadas | tempo ±8%, amplitude ±10% | Horizon [RESUMO]; números [PROPOSTA] |
| Tremor (dor/medo) | ruído de alta frequência | 12–18 Hz, 1–2°, decai em 0,3 s | [PROPOSTA] |

Nota: para meia-vida h, a constante de tempo é h / 0,69. Meia-vida 0,10 s dá ≈ 0,145 s, sem oscilação. O "Hz" entre parênteses na linha da mola é só 1/(2π·constante), uma referência de rapidez; mola crítica não oscila.

---

## (d) URLs realmente abertas (conteúdo lido)

- https://blog.littlepolygon.com/posts/loco1/ (números de inclinação e mola)
- https://techarthub.com/first-do-no-harm-to-the-gameplay/ (13 poses, 10 passos de Rosen)
- https://theorangeduck.com/page/spring-roll-call (mola crítica, meia-vida)
- https://theorangeduck.com/page/dead-blending (inertialização)
- https://candlesign.github.io/Rain-World-Devlog/Full%20devlog (lido até o caractere 300000 de 785814)
- https://www.gamedeveloper.com/design/crafting-the-complex-chaotic-ecosystem-of-i-rain-world-i-
- https://unity.com/blog/exploring-procedural-design-rain-world
- https://docs.google.com/presentation/d/1cYDabTQGYe09w3PyUU4XLrDn2fHy9X5eJIFUjVDt89U/htmlpresent (slides do Trico)
- https://news.capcomusa.com/2023/04/07/animating-the-monsters-of-sunbreak
- https://gamedeveloper.com/design/making-i-horizon-zero-dawn-i-s-machines-feel-like-living-creatures
- https://joshhirshfield.substack.com/p/procedural-animation-techniques-in
- https://www.gamedeveloper.com/programming/deep-dive-physics-based-animation-in-gibbon-beyond-the-trees
- https://cdn.jsdelivr.net/gh/JannisX11/blockbench-plugins@master/plugins/hytale_plugin/about.md
- https://beyondsims.com/2008/05/chris-heckler-takes-you-inside-spores-procedural-animation-system/

Abertas, mas só com descrição (sem técnica): https://gdcvault.com/play/1020049/Animation-Bootcamp-An-Indie-Approach, https://www.gamedeveloper.com/design/video-an-indie-approach-to-procedural-animation, https://gamedeveloper.com/art/video-animating-i-rain-world-i-and-its-many-squishy-stretchy-creatures, https://www.gameanim.com/2018/03/04/indie-approach-procedural-animation/.

## (e) O que não consegui confirmar

Não abriram ou vieram sem conteúdo útil:
- Vídeos das palestras GDC (Rain World 2016, Overgrowth 2014, Horizon 2018): YouTube bloqueou; GDC Vault fechado.
- Paper do Spore: PDF do Chalmers veio ilegível; chrishecker.com fora do ar. Agrupamento de pernas do Spore: **não confirmado**.
- Slides/código do Overgrowth (constantes de mola, ângulos): github de Wolfire deu 404 no caminho tentado.
- Sumo Digital (Spyder): 403. 80.lv e gamesradar (Horizon): abriram sem a técnica.
- Dead Cells: a página jikguard devolveu conteúdo errado; sem números de pipeline.
- Hollow Knight: sem fonte da Team Cherry; sem contagem de quadros.
- Mojang (Warden, Sniffer, Camel), Trove, Cube World, Deep Rock Galactic, Grounded, Hades, Shadow of the Colossus: sem fonte primária.
- Monster Hunter World (só Rise/Sunbreak lido); sem dado sobre peso, viradas, respiração.
- Todos os valores de antecipação por porte, cadência por porte e respiração por porte são [PROPOSTA]: precisam de teste visual na fábrica.
