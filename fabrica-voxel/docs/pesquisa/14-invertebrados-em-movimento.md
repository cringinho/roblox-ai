# 14 - Invertebrados em movimento (locomoção, comportamento, ataque e rig)

Escopo: MOVIMENTO e RIG de invertebrados para o gerador procedural de monstros (peças rígidas de voxel, ossos, clipes assados a 30 quadros por segundo). A anatomia está em `07-anatomia-artropodes-e-fantasia.md` e não se repete aqui.

Convenção das fontes: **[LIDO]** = a página foi aberta e lida (ou o trecho que a ferramenta devolveu). **[RESUMO]** = só o resumo da busca. **[PROPOSTA]** = número ou regra nossa, sem fonte; a justificativa vem junto. Nenhum número abaixo foi inventado: o que não tem fonte está marcado.

Limite honesto da pesquisa: muitos artigos de biomecânica (JEB, Journal of Arachnology) devolveram 403/503 ou PDF ilegível, então vários números vêm de resumos. Onde isso pesa, está dito.

---

## 1. Veredito

1. Em artrópodes de muitas pernas o corpo quase não sobe e desce: numa aranha em corrida (Cupiennius) a oscilação vertical mediana do centro de massa foi 1,7 mm para um animal de ~32 mm (cerca de 5 por cento do tamanho), sem fase aérea [LIDO]. Logo, bob de corpo pequeno e guinada leve valem mais que balanço grande.
2. A velocidade é carregada sobretudo pela FREQUÊNCIA de passada, e a fração de apoio cai abaixo de 0,5 em alta velocidade (aranha, barata, formiga) [LIDO/RESUMO]. A 30 quadros não dá para mostrar 25 a 47 Hz: tem de ser um ciclo simbólico lento, com "borrão" (ver seção 8).
3. Quase tudo que lê como "inseto" é: tripé alternado em dois grupos de fase 0 e 0,5, corpo rígido e estável, pausas e arrancos, antenas sempre se mexendo e independentes. O que lê como "aranha" é: pernas finas de ciclo rápido porém curto, dianteiras tateando, e postura de ameaça com as pernas da frente erguidas.
4. Para invertebrados sem perna (minhoca, lesma, lagarta, polvo, água-viva) a regra é uma ONDA que viaja pela cadeia de ossos (fase por osso), não poses: minhoca e lagarta têm onda contraindo de trás para a frente do corpo; a água-viva tem contração curta e relaxamento 3 a 4 vezes mais longo [LIDO].
5. Ataques reais são mais rápidos que um quadro a 30 fps (golpe de mantis 50 a 290 ms; ferrão de escorpião ~128 cm/s). O jogo precisa de antecipação MAIS LONGA que a real (PROPOSTA: 0,4 a 0,8 s de armar) e um golpe de 2 a 4 quadros.

---

## 2. Locomoção com pernas

Tabela principal. "Fonte" traz o rótulo de leitura. Células sem dado ficam como "sem fonte".

| Animal | Frequência de passada / velocidade | Fração de apoio | O que o corpo faz | Fonte |
|---|---|---|---|---|
| Aranha de corrida Cupiennius (4 pares) | Mediana ~0,32 m/s (~10 comprimentos de corpo/s); pico 0,6 m/s (~18); acima de 0,5 m/s: perna 1 = 6,3 /s, perna 2 = 7,2, perna 3 = 8,6, perna 4 = 8,3 | Pernas 1, 2 e 4 abaixo de 0,5 em alta velocidade; perna 3 raramente abaixo | Altura do CM ~10 mm constante; oscilação vertical 1,7 mm, lateral 2,1 mm; guinada ~5,4 graus, arfagem ~4,6, rolagem ~6,6 (nenhuma >15); sem fase aérea; NÃO é tetrápode alternado limpo (dois grupos fracamente acoplados, pernas de trás ciclam mais rápido, segundas pernas às vezes pulam o apoio) | PMC3689776 [LIDO] |
| Aranha Hololena (tetrápode alternado) | Picos >70 comprimentos de corpo/s (~50 cm/s); a ~54 comp./s começa fase aérea | Cai quase linearmente com a velocidade | Frequência e comprimento de passo sobem com a velocidade | Agelenids of the World [RESUMO] |
| Tarântula | 4 a 10 comp./s conforme temperatura (3,97 a 10,11 de 16,8 a 37,9 graus C); em Brachypelma a velocidade vem só da frequência | sem fonte | Marcha "walk-trot" em Eupalaestrus | resumo da busca (JEB/J. Arachnol.) [RESUMO] |
| Barata (Periplaneta/Blaberus) | Recorde ~5,4 km/h = ~50 comp./s; freq. de passada 25 a 27 Hz (Delcomyn 1971, citado) | Tripé alternado em quase todas as velocidades; fração cai a 0,5 ou menos com a velocidade | Em ~1,0 a 1,5 m/s passa a correr em 4 e depois 2 patas (bípede); ~25 curvas de corpo por segundo ao seguir parede | Wikipedia + typeset/JEB [RESUMO]; Ting, Blickhan, Full 1994 [RESUMO] |
| Barata Nauphoeta | Em alta velocidade a marcha deixa o tripé e vira mais "metacrônica" | sem fonte | sem fonte | Frontiers in Zoology 2017 [RESUMO] |
| Formiga Cataglyphis (prateada) | Até 855 mm/s (~106 a 108 comp./s); passada até ~47 /s (C. fortis ~36); acima de ~370 mm/s a frequência estabiliza e surge fase aérea | Cai abaixo de 0,5 acima desse ponto | Tripé forte (coordenação ~0,8) de 60 a 855 mm/s; passo cresce de 4,7 a 20,8 mm | Cosmos / Science News / Springer [RESUMO] |
| Formigas em geral | Algumas espécies até ~40 Hz | sem fonte | Tripé nas rápidas | revisão citada [RESUMO] |
| Drosófila / inseto-vareta | Mosca: velocidade controlada quase só por frequência; mosca usa onda (uma perna por vez) em lento e tripé em rápido; inseto-vareta usa tetrápode; barata, tripé | Frequência muda sobretudo encurtando o APOIO | Coordenação é contínua, não marchas discretas | arXiv 2112.12227 [LIDO] |
| Inseto-vareta/barata (regra) | Acima de ~7 Hz de passo (15 a 20 cm/s) a marcha tende a tripé rígido | sem fonte | sem fonte | busca (J. Exp. Biol.) [RESUMO] |
| Besouro | **Sem fonte útil encontrada.** Usar parâmetros de barata | - | - | [PROPOSTA] |
| Louva-a-deus (andar) | **Sem número.** Caça por emboscada: imóvel ou persegue em movimento lento e furtivo; balança o corpo de lado a lado ritmicamente (imitar vegetação ao vento; ajuda a perceber profundidade) | - | Balanço rítmico lateral | Wikipedia Praying mantis [LIDO] |
| Gafanhoto (salto) | Fase de co-contração do extensor da tíbia dura até ~0,5 s; depois solta; aceleração de pico ~20 g; salto de ~1 m (~20 comp. de corpo) | n/a | Preparar agachando (0,3 a 0,5 s) e liberar rápido | Wikipedia Grasshopper [LIDO] |
| Centopeia (Scolopendra) | Onda metacrônica de pernas; velocidade do CM medida em comprimentos de segmento por período de atuação: 9,14 ± 1,26 (comprimento de onda de 11 segmentos); períodos menores com mais velocidade; corrida de ~0,5 comp. de corpo por ciclo em outra fonte | Cada perna toca ~9 a 19 por cento do ciclo (derivado: 1/(λ/ℓs) para λ/ℓs 11 a 5,3) | Ondulação lateral do corpo (onda de flexão com defasagem constante de -0,10 π) que acompanha a onda de pernas; o modelo prevê rigidez intersegmentar crescendo ~7 vezes com a velocidade (modelo, não medição) | arXiv 2603.08409 [LIDO]; Georgia Tech / SICB [RESUMO] |
| Piolho-de-cobra (diplópode) | Em geral lento; dois pares de pernas por segmento visível; ondas metacrônicas (não confirmadas nesta leitura); defesa: enrolar em espiral (volvação) | sem fonte | Empurra com a cabeça baixa ao escavar (bulldozing) | Wikipedia Millipede [LIDO] |
| Escorpião | **Sem frequência de passada encontrada.** Cauda carregada curvada para a frente sobre o dorso; pectines varrem o chão | sem fonte | - | Wikipedia Scorpion [LIDO]; passada [PROPOSTA]: tetrápode alternado como aranha |
| Caranguejo-fantasma (lateral) | Em passo lento usa as 4 pernas de cada lado, às vezes trocando o lado que lidera; mais rápido, o 4o par sai do chão; no máximo corre só com o 1o e 2o pares (quase bípede) | sem fonte | Foge direto à toca ou ao mar | Wikipedia Ghost crab [LIDO] |
| Lagosta | **Sem fonte encontrada.** | - | - | [PROPOSTA]: passada lenta de 4 pares, pinças à frente |

Notas de aplicação (cada uma ligada a uma fonte acima):
- A mesma aranha mostra que a oscilação de corpo tem frequência menor que a passada (CM vertical ~5 /s contra pernas 6 a 8,6 /s) [LIDO].
- Fases aéreas aparecem só em velocidades extremas (Hololena >54 comp./s; Cataglyphis >370 mm/s) [RESUMO]; em jogo, ignorar.

---

## 3. Sem pernas articuladas

| Animal | Mecanismo | Números | Fonte |
|---|---|---|---|
| Minhoca | Peristalse: músculo circular (alonga e afina) e longitudinal (encurta e engrossa) em cada segmento; segmento encurtado se ancora com cerdas (sedas); a onda de contração anda em sentido OPOSTO ao movimento; volume do segmento constante | Mais velocidade = passadas mais longas e mais frequentes; velocidade absoluta da onda **sem fonte** | Wikipedia Earthworm [LIDO]; arXiv 1707.04084 [RESUMO] |
| Sanguessuga | Dois ventosas (anterior e posterior) alternando fixação com alongamento/encurtamento ("mede-palmos" de ventosas) | **Sem fonte lida** | [PROPOSTA] |
| Lesma e caracol | Ondas no pé (musculares); lesma/caracol terrestre usam ondas DIRETAS (da cauda para a cabeça); retrógradas são de gastrópodes marinhos; velocidade proporcional à velocidade das ondas e à frequência delas | Hz do pé **sem fonte lida**; tentáculos/antenas recolhem por retração: **sem fonte lida** | busca (Crozier & Pilz 1924 via artigos) [RESUMO] |
| Lagarta (Manduca, 5 pares de falsas pernas) | Ondas anterógradas: levanta, balança para a frente e repousa falsas pernas sucessivas, de trás para a frente; ganchos (crochets) soltos por um músculo retrator no início do balanço | Duração do passo ~1,28 ± 0,36 s (horizontal) e 1,02 ± 0,23 s (vertical), resumo de congresso | SICB / Woods, van Griethuijsen, Trimmer [RESUMO] |
| Mede-palmos (Geometridae) | Só 2 a 3 pares de falsas pernas na ponta; prende as patas da frente, puxa a traseira para junto, prende a traseira, estica a frente; laço de "medir" | **Sem tempos** | Wikipedia Inchworm [LIDO] |
| Polvo | Braços são hidrostatos musculares: encurtam, esticam, enrolam, enrijecem; alcance = uma curva (bend) que viaja da base à ponta com perfil de velocidade em sino, invariante; rastejar = ventosas pegam e soltam; jato pelo sifão é o modo mais rápido (fuga, caro) | ~2/3 dos neurônios nos braços (movimentos semi-independentes); sem números de tempo do jato | Wikipedia Octopus [LIDO]; JEB/PMC (Sumbre) [RESUMO] |
| Lula | Jato por contração do manto; barbatanas para ajuste | **Sem fonte lida** (busca não cobriu) | [PROPOSTA] |
| Água-viva (Aurelia) | Sino contrai (ejeta água) e relaxa (reabastece pelo recuo elástico da mesogleia); a pausa entre fases cria dois anéis de vórtice; tentáculos pendem como linhas de deriva | Contração ~0,4 s e relaxamento ~1,4 s (entradas do modelo, razão ~3,5); natural 0,24 ± 0,11 Hz; acima de ~0,56 Hz o músculo não relaxa; velocidade ~3 a 3,5 cm/s no robô híbrido | Xu & Dabiri 2020, PMC6989144 [LIDO]; Wikipedia Jellyfish [LIDO] |
| Estrela-do-mar | Pés ambulacrais (centenas de pés tubulares) com cada braço liderando; **sem fonte lida** | - | [PROPOSTA] |
| Larvas | **Sem fonte lida.** Tratar como lagarta sem pernas (onda de contração de trás para a frente) | - | [PROPOSTA] |

Regra de rig para cadeia (todos): ver seção 9, onda por osso com fase = índice vezes defasagem; minhoca e lagarta: onda de trás para a frente; água-viva: sino com assimetria 1:3 a 1:4 (contrai rápido, relaxa devagar).

---

## 4. Comportamento e pausas (vida e medo)

| Comportamento | O que se sabe | Tempo | Fonte |
|---|---|---|---|
| Movimento intermitente (arrancos e pausas) | Animais intercalam deslocamento com pausas de ms a minutos; em gafanhoto-do-deserto, pausas <6 s = descanso entre deslocamentos e >100 s = reorientação; aranhas de espreita (Pardosa) seguem regras matemáticas (pausas em lei de potência) | Pausa curta <6 s; longa >100 s (gafanhoto) | PMC3349720 e Toft et al. 2021 [RESUMO] |
| Congelar | **Sem tempo medido.** Louva-a-deus fica imóvel como emboscada | - | Wikipedia Praying mantis [LIDO]; tempo [PROPOSTA]: 1 a 3 s |
| Ameaça da tarântula | Encara a ameaça, ergue-se nas patas traseiras e estica as da frente; algumas inclinam para trás expondo as presas | **Sem tempo** | Texas Parks (TXPUB 00235) e ypte.org.uk [RESUMO] |
| Ameaça do louva-a-deus (deimática) | Empina, abre as pernas dianteiras e as asas para parecer maior; algumas espécies chiam | Sem tempo | Wikipedia Praying mantis [LIDO] |
| Ameaça do escorpião | Ergue as pinças e a cauda em postura defensiva; alguns estridulam; algumas espécies esguicham veneno até 1 m | Sem tempo | Wikipedia Scorpion [LIDO] |
| Polvo deimático | Muda de cor, estica braços, barbatanas ou teias para parecer maior | Sem tempo | Wikipedia Octopus [LIDO] |
| Aranha-lobo (agitar de perna, cortejo) | Ergue e balança uma perna da frente; taxa de agitar maior com mais sucesso; depois bate a perna no chão (vibração) | Sem Hz lido | Frontiers Ecol Evol 2022; UNL [RESUMO] |
| Balanço do louva-a-deus e do inseto-vareta | Movimento rítmico lateral | Sem Hz lido | Wikipedia Praying mantis [LIDO] |
| Limpeza de antenas e pernas, tremor, pulsar de abdome, reação ao toque | **Sem fonte lida nesta pesquisa.** | - | [PROPOSTA] ver seção 9 |

Truque de design (PROPOSTA, lógica de leitura): o medo vem do contraste entre quase-imobilidade e arrancos. Quanto mais longo o congelamento, mais forte o arranco seguinte.

---

## 5. Antenas e palpos

| Fato | Dado | Fonte |
|---|---|---|
| Inseto-vareta move as duas antenas de forma rítmica e contínua ao andar; ao tocar, passa a movimento mais estreito e mais rápido (frequência de ciclo maior, amplitude menor) | Contato com parede médio ~134 ms; com borda ~115 ms; contatos acontecem mais no movimento de abaixar | Frontiers Behav Neurosci 2012 (fnbeh.2012.00030) [LIDO] |
| Duas antenas: sem preferência de lado; zonas de contato quase não se sobrepõem; juntas análogas esquerda/direita ficam coordenadas na parede, juntas homólogas contralaterais sem defasagem consistente | Acoplamento fraco | mesma fonte [LIDO] |
| Barata seguindo parede: a base da antena fica relativamente parada e o flagelo dobra; a ressonância passiva do flagelo é ~18 Hz (isto é a mecânica passiva, NÃO a taxa de varredura) | 18 ± 3 Hz; até 25 curvas de corpo/s | JEB 1999 (pubmed 9929464) e outros [RESUMO] |
| Frequência de varredura de antena em formiga/barata | **Sem fonte encontrada** | lacuna |
| Escorpião: pectines varrem o chão (machos procuram feromônio) | Sem Hz | Wikipedia Scorpion [LIDO] |

[PROPOSTA] para o jogo: antena esquerda e direita com ondas senoidais de fases independentes (diferença de fase aleatória fixa por criatura), 1,5 a 2,5 Hz exibidos em marcha e vira 2 vezes mais rápida e curta ao detectar o jogador (espelha "mais rápido e mais estreito após contato").

---

## 6. Ataques e telegrafia

| Ataque | Dado | Fonte |
|---|---|---|
| Louva-a-deus (Madagascar marbled) | Extensão da tíbia 60 a 290 ms, mais lenta com presa mais lenta; a probabilidade de pausa durante o golpe também depende da velocidade da presa | Biology Letters / Sussex [RESUMO] |
| Louva-a-deus gigante da floresta | Golpe a toda velocidade ~50 a 100 ms | Science News [RESUMO] |
| Escorpião (Leiurus, deathstalker) | Cauda até 128 a 130 cm/s; espécie mais lenta (spitting) 66 cm/s; golpe aberto mais rápido e mais preciso; alguns golpes diretos, outros circulares (podem repetir); ângulo ótimo ~30 graus | Coelho et al. 2017 (resumo) [RESUMO]; Wikipedia Scorpion [LIDO] |
| Duração do golpe de ferrão em ms | **Não obtida** (filmado a 500 quadros/s, mas valores só no artigo completo, DOI 10.1111/1365-2435.12855) | lacuna |
| Aranha-chicote (Charon) | Golpe completo 30 a 180 ms | J. Arachnology 47(2) [RESUMO] |
| Aranha caçadora de formiga (fase acrobática) | ~74 ± 4 ms, pico 25 cm/s | busca [RESUMO] |
| Armadilha-mandíbula (Mecysmaucheniidae) | Fechamento 0,049 a 8,5 m/s | sci.news [RESUMO] |
| Bote da aranha-lobo / Cupiennius, pinça de lagosta/caranguejo, mandíbula de formiga/besouro | **Sem fonte** | lacuna |
| Centopeia | Forcípulas (patas modificadas) agarram e injetam veneno; sem tempo | Wikipedia Centipede [LIDO] |
| Limbo | A ilusão de inteligência vem de UMA perna dinâmica separada do resto da animação; se o menino chega perto, a animação acelera quase imperceptivelmente para alinhar a perna com o corpo | GamesRadar [RESUMO] |
| Rakna-Kadaki | Há telégrafo visível antes dos feixes de seda: ela apenas aponta os feixes perto de si por um momento | guia de jogo [RESUMO] |

Telegrafia em jogo (PROPOSTA, derivada: a 30 fps o golpe real cabe em 1 a 3 quadros e é ilegível):
1. Armar longo e legível: 0,4 a 0,8 s (12 a 24 quadros) recolhendo/erguendo o membro de ataque; pico de pose mantido 2 a 4 quadros.
2. Golpe curto: 3 a 5 quadros (100 a 170 ms, na faixa lenta do mantis e do ferrão).
3. Recuperação mais longa que o golpe: 10 a 20 quadros (janela de punição).
4. Congelar antes do bote: imobilidade de 0,3 a 0,6 s aumenta o medo (ver seção 4).

---

## 7. Jogos de referência

Pouco foi achado de bastidor. A tabela diz o que está sustentado e o que não foi achado.

| Jogo | Criatura | Técnica | Fonte |
|---|---|---|---|
| Limbo | Aranha gigante | Animação quase toda pré-feita, com UMA perna física/dinâmica que ajusta a mira ao jogador; animação "acelera" para alinhar | GamesRadar [RESUMO] |
| Subnautica 2 | Collector Leviathan (tentáculos) | Tentáculos em física da Unreal + physical animation + Control Rig; procedurais, não golpes pré-roteirizados | Dev vlog #3 e PC Gamer [RESUMO] |
| Monster Hunter Rise / Stories | Rakna-Kadaki | Telégrafo de seda; pernas são ponto fraco (quebrar derruba) | guias [RESUMO]; bastidor de animação NÃO achado |
| Jogos com IK procedural (técnica geral) | Aranha-mecha de 6 pernas (UE5) | Sem timeline; passos por intervalos de tempo em array com módulo (evita pernas emboladas); ~0,3 ms/quadro | 80.lv [LIDO] |
| Godwalker | Quadro-aranha | Cada perna com IK independente; pé passa do alvo quando se afasta demais; parâmetros por pé: distância de passo, velocidade de retorno, imprecisão aleatória; pernas se revezam; se o inimigo anda mais rápido que o retorno parece "dash" | joshhirshfield.substack.com [LIDO] |
| Overgrowth (talk de David Rosen, GDC 2014) | Humanoides, não aranhas | Poucas poses-chave + procedural; **não cobre IK de aranha** | GDC Vault via buscas [RESUMO] |
| Grounded | Aranhas e insetos | Só achado: aranhas têm opção de acessibilidade (nº de olhos, pernas, pelo, som); **nada achado de técnica de animação** | GamesRadar/GameSpot [RESUMO] |
| Deep Rock Galactic | Glyphids | Nada achado de técnica; só variantes compartilham o mesmo corpo base | wiki [RESUMO] |
| Hollow Knight | Insetos 2D | Arte à mão no Photoshop, centenas de insetos animados; nada de técnica de marcha | PC Gamer / Team Cherry [RESUMO] |
| Minecraft | Aranha | Modelo de 8 pernas de 1 osso cada; mods mostram que a perna "walking" vanilla quase não muda; mod/pack usa pernas de 2 segmentos | Fresh Animations, Webs [RESUMO] |
| Earth Defense Force, Dark Souls / Elden Ring, Resident Evil, Half-Life (headcrab), Starship Troopers | - | **Nenhuma fonte de bastidor encontrada** | lacuna |

Bones por perna: IK procedural geralmente usa 2 a 3 segmentos; nossa perna de 3 ossos (coxa, fêmur, tíbia) é compatível. Sem fonte comparando contagens entre jogos.

---

## 8. O que simplificar a 30 quadros

1. **Frequência exibida máxima** [PROPOSTA]: a 30 fps o limite de Nyquist é 15 Hz, mas a leitura clara pede ao menos 8 quadros por ciclo, então ciclo de perna de no máximo ~3,5 Hz. Aranha real faz 6 a 8,6 /s e barata 25 a 47 /s (formigas) [LIDO/RESUMO]: nunca reproduzir, só sugerir. Evita efeito "roda de carroça".
2. **Quantas pernas em fase certa** [PROPOSTA]: apenas dois grupos. Hexápode: tripé (L1, R2, L3 contra R1, L2, R3, defasagem 0,5). Aranha/escorpião de 8: grupos alternados A (L1, R2, L3, R4) e B (R1, L2, R3, L4), defasagem 0,5. Cupiennius real é só frouxamente tetrápode [LIDO], logo um pouco de jitter de fase por perna (±0,05) é mais natural que sincronia perfeita.
3. **Corpo**: bob vertical ~5 por cento do tamanho do corpo [LIDO, derivado], guinada e rolagem ≤6 graus, com frequência = metade da passada (o CM oscila menos que as pernas) [LIDO].
4. **Truques baratos que leem como inseto** [PROPOSTA]: (a) tripé rígido com corpo estável; (b) arranque-pausa: andar 0,3 a 1,2 s, parar 0,2 a 1,5 s; (c) antenas sempre vibrando, independentes; (d) cabeça reorienta antes do corpo; (e) um tremor de pernas dianteiras em parada ("tatear"); (f) pernas da frente maiores em amplitude, de trás em empurrão; (g) rotação do tronco na fase de cada tripé (arfagem/rolagem ligeiras que seguem a passada).
5. **Centopeia** [PROPOSTA a partir de arXiv 2603.08409 LIDO]: onda de pernas (fase = índice de segmento vezes constante) + onda de flexão lateral de fase fixa atrás da onda de pernas; amplitude lateral cresce com a velocidade.
6. **Salto** [LIDO: Wikipedia Grasshopper]: agachar (co-contração, até ~0,5 s), liberar em 2 a 3 quadros, aterrissar. O atraso de armar é o que faz parecer inseto.

---

## 9. REGRAS ACIONÁVEIS

Valores de amplitude, frequência e fase são **[PROPOSTA]**, calibrados sobre os dados das seções 2 a 8 (a coluna "Base" cita a fonte quando existe). Convenção: "ciclo" = 1 período do clipe; fase em fração do ciclo; perna 1 = frontal. Os ossos são os 3 já existentes por perna: coxa (gira frente/trás), fêmur (sobe), tíbia (desce).

### 9.1 Aranha (8 pernas, grupos A e B)

| Clipe | O que cada osso faz | Amplitude | Frequência / duração | Fase | Base |
|---|---|---|---|---|---|
| Parado | Corpo respira (osso do abdome ±1 por cento de escala em Y), uma perna da frente tateia (coxa ±8 graus, aleatória), pernas travadas | coxa ±8 graus em 1 perna; abdome 1 por cento | respiração 0,3 Hz; tato a cada 1,5 a 4 s | tato sem fase fixa | pausas: PMC3349720 [RESUMO] |
| Andar | Coxa balança ±20 graus; fêmur sobe 25 graus na fase de balanço; tíbia compensa descendo 20 graus no apoio; corpo bob vertical ~5 por cento do corpo e guinada ±5 graus | ver à esquerda | 2,5 a 3,5 Hz exibido (ciclo 8 a 12 quadros) | Grupo A fase 0; B fase 0,5; jitter ±0,05; apoio 55 a 65 por cento | Cupiennius: bob 1,7 mm, guinada 5,4 graus, apoio <0,5 em rápido [LIDO] |
| Ataque | Arma: corpo recua e ergue as 2 pernas da frente (fêmur +45 graus, coxa para trás) 0,5 s; congela 0,2 s; bote: coxa dianteira e corpo +1,2 comprimentos de corpo em 3 a 4 quadros; recupera em 15 quadros | fêmur +45 graus; coxa -25 para +30 | arma 0,5 s, golpe 0,13 s, recuperação 0,5 s | pernas dianteiras antecipam o tronco em 2 quadros | ameaça tarântula [RESUMO]; telegrafia seção 6 |
| Ameaça | Ergue-se nas pernas traseiras: pares 1 e 2 para cima (fêmur +60 graus, tíbia aberta), presas (quelíceras) abertas, tremor de ±3 graus nas pernas erguidas | fêmur +60; tremor ±3 | segura 1 a 3 s, tremor 6 Hz exibido | tremor sem fase entre pernas | TXPUB 00235, ypte [RESUMO] |
| Dano | Corpo se contrai: todas as coxas puxam para dentro 15 graus em 2 quadros, volta em 6 | 15 graus | 0,27 s | simultâneo | [PROPOSTA] |
| Morte | Pernas dobram para dentro e sobem (tíbia fecha, fêmur +80 graus) em onda de fase 0,04 por perna de fora para dentro, corpo cai | fêmur +80 | 1,2 s | 0,04 por perna | comum em aranhas mortas (pernas enrolam) [PROPOSTA] |

### 9.2 Inseto hexápode (barata, besouro, formiga)

| Clipe | Ossos | Amplitude | Frequência / duração | Fase | Base |
|---|---|---|---|---|---|
| Parado | Antenas varrem (±20 graus, 1,5 a 2,5 Hz, fase independente); pernas dianteiras limpam antena a cada 4 a 8 s | antena ±20 | ver à esquerda | esq e dir independentes | antenas: fnbeh.2012.00030 [LIDO] |
| Andar | Tripé: coxa ±25 graus, fêmur +20 no balanço, tíbia compensa; corpo bob 3 por cento, balanço lateral ±3 graus | ±25 | 3 a 3,5 Hz exibido (corrida: salto para 4 Hz com antenas para trás) | Tripé A (L1, R2, L3) fase 0; B (R1, L2, R3) fase 0,5; apoio 50 a 60 por cento | tripé: arXiv 2112.12227 [LIDO]; barata [RESUMO] |
| Ataque | Mandíbula (osso da cabeça) abre 40 graus e fecha; corpo avança com 1 arrancada de 4 quadros | mandíbula 40 graus | arma 0,3 s, golpe 0,1 s | pernas travadas em tripé durante o golpe | mandíbula sem fonte [PROPOSTA] |
| Ameaça | Levanta a parte da frente (pernas 1 e 2 abertas), asas/élitros abrem se houver; chiado | ver à esquerda | 1 a 2 s | simétrico | deimática do louva-a-deus [LIDO] |
| Dano | Encolhe: pernas contraem 12 graus, antenas recuam | 12 | 0,25 s | simultâneo | [PROPOSTA] |
| Morte | Capota de costas (corpo gira 180 graus em Z) e pernas tremem 4 Hz, fecham | giro 180 | 1,5 s | tremor sem fase | comportamento comum de insetos mortos [PROPOSTA] |

### 9.3 Louva-a-deus

| Clipe | Ossos | Amplitude | Duração | Fase | Base |
|---|---|---|---|---|---|
| Parado | Balanço lateral do corpo ±4 graus, patas raptoriais dobradas | ±4 | 0,5 Hz | - | balanço: Wikipedia [LIDO] |
| Andar | Furtivo: passos lentos e pausas | ver 9.2, 1,5 Hz | pausas longas | tripé | Wikipedia [LIDO] |
| Ataque | Arma: abre patas raptoriais 0,4 s, congela; golpe: extensão de fêmur/tíbia 3 a 5 quadros (real 50 a 290 ms) | extensão 90 graus | arma 0,4 s, golpe 0,13 s, recuperação 0,5 s | par de patas simultâneo | Biology Letters [RESUMO]; Science News [RESUMO] |
| Ameaça | Empina o tórax, abre pernas dianteiras e asas, balança | asas abertas | 1,5 s | simétrico | Wikipedia [LIDO] |
| Dano, Morte | como 9.2 | - | - | - | [PROPOSTA] |

### 9.4 Escorpião

| Clipe | Ossos | Amplitude | Duração | Fase | Base |
|---|---|---|---|---|---|
| Parado | Cauda curvada sobre o dorso, ponta balança ±3 graus; pinças semiabertas | ±3 | respiração 0,3 Hz | - | Wikipedia [LIDO] |
| Andar | Mesmo de aranha 9.1 (grupos A/B), pinças à frente, cauda curvada estável | ver 9.1 | 2 a 2,5 Hz exibido | A 0, B 0,5 | passada sem fonte [PROPOSTA] |
| Ataque | Arma: cauda arqueia para trás (segmentos 1 a 5 em cascata, 0,03 de fase por osso) 0,5 s; golpe: cauda dobra para a frente em 3 a 4 quadros (real ~128 cm/s); recuperação | arco ~120 graus | arma 0,5 s, golpe 0,13 s, recup. 0,6 s | cascata de fase da base à ponta | Wikipedia [LIDO] |
| Ameaça | Ergue pinças e cauda | cauda alta | 1 a 3 s | - | Wikipedia [LIDO] |
| Dano, Morte | como 9.1; morte: cauda enrola | - | - | - | [PROPOSTA] |

### 9.5 Centopeia / piolho-de-cobra (cadeia de segmentos)

| Clipe | Ossos | Amplitude | Frequência | Fase | Base |
|---|---|---|---|---|---|
| Parado | Antenas varrem; segmentos quase imóveis; ondulação mínima | - | - | - | [PROPOSTA] |
| Andar | Cada segmento: perna balança ±25 graus com FASE = índice vezes 0,09 a 0,19 do ciclo (comprimento de onda 5 a 11 segmentos); corpo ondula lateral ±8 graus, atrasado -0,05 ciclo em relação à onda de pernas; amplitude da ondulação sobe com a velocidade | ±25 / ±8 | 2 a 3 Hz exibido | ver | arXiv 2603.08409 [LIDO] |
| Ataque | Cabeça recua 3 quadros e morde; forcípulas fecham | - | arma 0,5 s, golpe 0,13 s | - | Wikipedia Centipede [LIDO]; tempos [PROPOSTA] |
| Ameaça | Ergue a frente do corpo e abre forcípulas; piolho-de-cobra enrola em espiral (volvação) | - | 1 a 2 s | - | Wikipedia Millipede [LIDO] |
| Dano, Morte | Segmentos contraem em onda da cabeça para a cauda; morte: enrola e para | - | 1 s | 0,04 por osso | [PROPOSTA] |

### 9.6 Sem perna articulada (cadeia de ossos)

| Criatura | Ossos | Amplitude | Frequência | Fase | Base |
|---|---|---|---|---|---|
| Minhoca / larva | Escala Z (comprimento) de cada segmento: contrai 25 por cento e engrossa XY em compensação (volume constante); onda de TRÁS PARA A FRENTE, deslocando-se para trás | 25 por cento | 0,6 a 1 Hz | 1/n por segmento | Wikipedia Earthworm [LIDO] |
| Lagarta | Onda anterógrada: cada segmento ergue o meio ~30 por cento e avança; ritmo de passo ~1 a 1,3 s | 30 por cento | ~0,8 a 1 Hz | da traseira para a frente | SICB (Manduca) [RESUMO] |
| Mede-palmos | Arco: ponta traseira se junta à frente, depois estica | arco 90 graus | ciclo 1,5 a 2 s | 2 fases (prende-puxa-prende-estica) | Wikipedia Inchworm [LIDO]; tempo [PROPOSTA] |
| Lesma / caracol | Onda direta no pé (cauda para cabeça); olhos/antenas recolhem ao toque | pé ±5 por cento | 1 a 2 Hz (valor [PROPOSTA]) | direta | busca [RESUMO] |
| Polvo / lula | Cadeia de 6 a 8 ossos por braço; curva viaja da base à ponta com velocidade em sino; segue o osso de cima com atraso (fase 0,08 por osso) | curva 40 a 70 graus | alcance 0,6 a 1,2 s | base para ponta | Wikipedia Octopus [LIDO]; JEB [RESUMO] |
| Água-viva | Sino: contração 0,4 s, relaxamento ~1,4 s; tentáculos seguem com atraso e balançam; leve subida na contração | sino ±25 por cento | 0,25 a 0,55 Hz | tentáculos 0,1 por osso | Xu & Dabiri [LIDO] |
| Estrela-do-mar | 5 braços ondulam ±15 graus lentos, braço líder alterna | ±15 | 0,3 Hz | - | [PROPOSTA] |

### 9.7 Nota sobre "Dano" e "Morte" em geral
Sem literatura lida sobre reação ao toque, tremor ou pulsar do abdome; os valores de Dano (0,25 a 0,3 s de encolher) e Morte (1 a 1,5 s) são [PROPOSTA] de design. Calibrar por teste visual.

---

## 10. Glossário

- **Tripé alternado (alternating tripod)**: três pernas apoiam (L1, R2, L3) enquanto as outras três balançam (R1, L2, R3); defasagem de meio ciclo.
- **Tetrápode alternado**: quatro pernas apoiam por vez; usado por aranhas de corrida e inseto-vareta.
- **Fração de apoio (duty factor)**: fração do ciclo em que a perna está no chão; abaixo de 0,5 o animal começa a ter instantes sem apoio suficiente.
- **Fase aérea**: instante em que nenhum pé toca o chão (só em velocidades extremas).
- **Marcha metacrônica**: pernas de um mesmo lado entram em fase em onda sequencial (centopeia, piolho-de-cobra).
- **Comprimento de corpo por segundo**: velocidade normalizada pelo tamanho do animal.
- **Peristalse**: onda de contração que atravessa o corpo (minhoca).
- **Hidrostato muscular**: órgão sem esqueleto, que se move variando o volume (braço de polvo).
- **Deimático**: exibição de susto/ameaça que blefa tamanho ou perigo.
- **Co-contração**: dois músculos opostos contraem juntos para armazenar energia antes de soltar (salto do gafanhoto).
- **IK (cinemática inversa)**: calcula ângulos de juntas para o pé alcançar um alvo.
- **Alvo de passo**: ponto onde o pé pousa; salta adiante quando o corpo se afasta demais do pé.
- **Telegrafia**: antecipação visual do ataque que dá ao jogador tempo de reagir.

---

## 11. Fontes

[LIDO] = aberta e lida; [RESUMO] = só resumo da busca.

1. Crawling at High Speeds: Steady Level Locomotion in the Spider Cupiennius salei, PMC3689776 [LIDO]. https://pmc.ncbi.nlm.nih.gov/articles/PMC3689776
2. Embodied intelligence solves the centipede's dilemma, arXiv 2603.08409v2 [LIDO]. https://arxiv.org/html/2603.08409v2
3. Parallel locomotor control strategies in mice and flies, arXiv 2112.12227 [LIDO]. https://ar5iv.arxiv.org/html/2112.12227
4. Stick insect antennal sampling, Frontiers Behav Neurosci 2012 [LIDO]. https://www.frontiersin.org/articles/10.3389/fnbeh.2012.00030/full
5. Xu & Dabiri 2020, Aurelia swimming (Science Advances), PMC6989144 [LIDO]. https://pmc.ncbi.nlm.nih.gov/articles/PMC6989144
6. 80.lv, procedural IK spider mech UE5 [LIDO]. https://80.lv/articles/developer-shows-procedural-ik-system-for-animating-six-legged-spider-mech-in-ue5
7. Procedural Animation Techniques in Godwalker [LIDO]. https://joshhirshfield.substack.com/p/procedural-animation-techniques-in
8. Wikipedia (todas [LIDO]): Praying mantis https://en.wikipedia.org/wiki/Praying_mantis; Grasshopper https://en.wikipedia.org/wiki/Grasshopper; Scorpion https://en.wikipedia.org/wiki/Scorpion; Octopus https://en.wikipedia.org/wiki/Octopus; Jellyfish https://en.wikipedia.org/wiki/Jellyfish; Earthworm https://en.wikipedia.org/wiki/Earthworm; Inchworm https://en.wikipedia.org/wiki/Inchworm; Millipede https://en.wikipedia.org/wiki/Millipede; Centipede https://en.wikipedia.org/wiki/Centipede; Ghost crab https://en.wikipedia.org/wiki/Ghost_crab; Hexapod (robotics) https://en.wikipedia.org/wiki/Hexapod_(robotics)
9. Hololena gait (Agelenids of the World) [RESUMO; página retornou 403]. https://agelenidsoftheworld.myspecies.info/content/gait-characteristics-two-fast-running-spider-species-hololena-adnexa-and-hololena-curta
10. Ting, Blickhan, Full 1994, Dynamic and static stability in hexapedal runners [RESUMO]. https://cob.silverchair.com/jeb/article/197/1/251/33602/Dynamic-and-static-stability-in-hexapedal-runners
11. Nauphoeta cinerea gait, Frontiers in Zoology 2017 [RESUMO]. https://frontiersinzoology.biomedcentral.com/articles/10.1186/s12983-017-0232-y
12. Mechanics of a rapid running insect (Full & Tu) / American cockroach [RESUMO]. https://en.wikipedia.org/wiki/American_cockroach ; https://typeset.io/pdf/mechanics-of-a-rapid-running-insect-two-four-and-six-legged-qwjvyshv8z.pdf
13. Cataglyphis silver ant speed (Science News / Cosmos) [RESUMO]. https://sciencenews.org/article/sahara-silver-ants-world-fastest-despite-relatively-short-legs
14. Strike mechanics of an ambush predator, the praying mantis (JEB 215) [RESUMO]. https://cob.silverchair.com/jeb/article-split/215/24/4374/11185/Strike-mechanics-of-an-ambush-predator-the
15. Female giant rainforest mantises (Science News) [RESUMO]. https://www.sciencenews.org/article/female-mantises-strike-harder-strike
16. Coelho et al. 2017, scorpion defensive strike (Functional Ecology) [RESUMO]. https://ui.adsabs.harvard.edu/abs/2017FuEco..31.1390C
17. Strike kinematics in the whip spider Charon (J. Arachnology 47) [RESUMO]. https://www.americanarachnology.org/journal-joa/joa-all-articles/article/download/arac-47-02-260.pdf/?no_cache=1
18. Trap-jaw spiders (sci.news) [RESUMO]. https://www.sci.news/biology/mecysmaucheniid-spiders-strike-prey-lightning-speed-03767.html
19. Intermittent motion in desert locusts, PMC3349720 [RESUMO]. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3349720/
20. Caterpillar step durations (SICB) [RESUMO]. https://sicb.org/?p=27699
21. Snail pedal waves (Pembury Smith 2021, JZool) [RESUMO; PDF 403]. https://research-repository.st-andrews.ac.uk/bitstream/10023/24786/1/Pembury_Smith_2021_How_fast_is_a_snail_JZool_AAM.pdf
22. Earthworm-inspired soft crawling robot, arXiv 1707.04084 [RESUMO]. https://arxiv.org/pdf/1707.04084
23. Octopus arm movements (JEB 218) [RESUMO]. https://cob.silverchair.com/jeb/article-split/218/7/1069/14549/Octopus-arm-movements-under-constrained-conditions
24. Tarantula threat posture (Texas Parks; YPTE) [RESUMO]. https://texashistory.unt.edu/ark:/67531/metapth661996/m2/1/high_res_d/TXPUB_00235.pdf ; https://ypte.org.uk/factsheets/tarantulas/defences
25. Wolf spider leg waving, Frontiers Ecol Evol 2022 [RESUMO]. https://www.frontiersin.org/articles/10.3389/fevo.2022.939133
26. Cockroach antennal wall-following [RESUMO]. https://pubmed.ncbi.nlm.nih.gov/9929464/
27. Limbo spider (GamesRadar) [RESUMO]. https://www.gamesradar.com/why-making-limbos-terrifying-giant-spider-was-nightmare
28. Subnautica 2 Collector Leviathan (PC Gamer) [RESUMO]. https://www.pcgamer.com/games/survival-crafting/subnautica-2-devs-reveal-the-latest-horrifying-leviathan-to-grace-the-deep-sea-it-has-4-tentacles-to-grab-crush-swat-and-terrify-players/
29. Sumo Digital, Spyder animation (Unreal tech blog) [RESUMO; página 403]. https://www.unrealengine.com/tech-blog/sumo-digital-shares-how-it-created-spyder-s-sophisticated-animation-systems
30. Rakna-Kadaki guias [RESUMO]. https://gamerguides.com/monster-hunter-rise/guide/monster-hunts/large-monsters/rakna-kadaki
31. Wolfire / GDC 2014, An Indie Approach to Procedural Animation [RESUMO]. https://gamedeveloper.com/design/video-an-indie-approach-to-procedural-animation
32. Minecraft spider mods [RESUMO]. https://modrinth.com/resourcepack/fresh-animations-spiders

## 12. Lacunas (resumo)

1. Duração real do golpe de ferrão do escorpião (Coelho 2017, texto completo) e do bote de aranha-lobo/tarântula.
2. Frequência de varredura das antenas (barata/formiga) e Hz dos pés de caracol/lesma; ondas da minhoca e sanguessuga em números.
3. Bastidores de animação de Grounded, Deep Rock Galactic, Hollow Knight, Elden Ring, Resident Evil, Half-Life, Starship Troopers, EDF e Monster Hunter. Besouro, lagosta, lula e estrela-do-mar também sem número.
