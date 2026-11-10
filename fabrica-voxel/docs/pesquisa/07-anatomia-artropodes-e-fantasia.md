# 07 - Anatomia de artrópodes e criaturas fantásticas (dossiê para o gerador)

Convenções: **[F]** = número com fonte lida. **[PM]** = proposta minha, sem fonte, com a justificativa ao lado. "Li" = abri a página e li o trecho que o extrator devolveu. "Só resumo" = apenas o resumo da busca. Observação honesta: as páginas da Wikipédia foram lidas por um extrator que devolveu só os trechos pedidos, e algumas páginas longas foram lidas só nos primeiros 100 mil caracteres.

## Veredito (5 linhas)

1. O arco da perna de aranha vem de **7 segmentos com dobradiças de um eixo só**; dois ossos retos não têm como imitar isso. Mínimo viável: coxa curta + fêmur + patela curta + tíbia + metatarso/tarso = 5 ossos, com o fêmur subindo e a tíbia descendo.
2. Insetos têm 3 pares de pernas no tórax, de 3 segmentos; marcha em tripé alternado (3 pés no chão). Aranhas andam em tetrápode alternado (4 pés no chão, fração de apoio medida ~0,63-0,70 [F]).
3. Centopeia = 1 par por segmento, número ímpar de pares, onda de pernas que viaja; piolho-de-cobra = 2 pares por diplossegmento, lento e enrolável [F].
4. Dragão de 6 membros não existe em vertebrados; a base crível é o **wyvern** (asas = braços) [fonte fraca, ver lacunas]. Esqueleto lê-se com crânio, caixa torácica, pelve e ossos longos de pontas alargadas [PM, ver seção].
5. O medo vem de pernas longas e angulosas, movimento errático e simetria [Davey 1991 / May, só resumo]; o jogo deve usar arrancos + imobilidade.

---

## 1. Insetos

**Fontes:** Wikipédia "Insect morphology" (li), "Mantis" (li, 100k primeiros caracteres), "Cockroach" (li, idem), "Arthropod leg" (li).

- **Tagmas [F]:** cabeça, tórax, abdome.
- **Tórax [F]:** 3 segmentos: protórax (1º par de pernas e pronoto), mesotórax (2º par + asa anterior), metatórax (3º par + asa posterior).
- **Perna [F]:** coxa, trocânter (geralmente um só segmento), fêmur, tíbia, tarso (2-5 tarsômeros) e pré-tarso. Cinco componentes principais.
- **Juntas [F]:** coxa-corpo é dobradiça com dois pontos articulares; trocânter-coxa é dobradiça horizontal; trocânter-fêmur é dobradiça num plano vertical/oblíquo com movimento pequeno; tíbia dobra contra a face inferior do fêmur; tarsômeros só flexionam passivamente (sem músculo próprio). Conclusão para o gerador: coxa balança para frente/trás (eixo vertical do corpo), fêmur-tíbia é o joelho, o tarso quase não se mexe.
- **Abdome [F]:** plano básico 11-12 segmentos; gafanhoto 11; baratas têm 10 visíveis (Cockroach, li). Para voxel: 5 a 7 blocos já leem como abdome segmentado [PM].
- **Antenas e boca:** a página lida não deu número de segmentos de antena nem detalhe das peças bucais. Antena fica como "chicote de 3-4 ossos com atraso" [PM]. Peças bucais: mandíbulas laterais que abrem em V (besouro, formiga) ou probóscide enrolada (borboleta) [conhecimento geral, sem fonte aberta].
- **Barata [F, Cockroach]:** corpo achatado, cabeça pequena, antenas longas e flexíveis, pernas robustas com coxas grandes, **pernas dianteiras as mais curtas e as traseiras as mais longas, e as traseiras dão a propulsão**; espinhos na tíbia.
- **Louva-a-deus [F, Mantis]:** coxa+trocânter fundidos num segmento "tão longo quanto o fêmur" (parece um fêmur comprido); fêmur com ~4 espinhos discoides na base (0-5 conforme a espécie), tíbia com tubérculos e garra apical; **protórax muito mais longo que meso e metatórax**; cabeça triangular que gira quase 180 graus; abdome com 10 tergitos; emboscada imóvel e balanço lateral rítmico; ameaça: ergue-se, abre as patas dianteiras e as asas.
- **Gafanhoto (saltador) e besouro/formiga:** sem página aberta com números. Gafanhoto: fêmur traseiro muito engrossado e comprido, tíbia fina dobrando sobre ele [conhecimento geral]. Proporções em [PM] na tabela final.
- **Marcha [F parcial]:** a página "Hexapod (robotics)" (li) confirma tripé alternado = 3 pés no chão por vez. Os números de fase (cada tripé 50% do ciclo, fração de apoio acima de 0,5 em baixa velocidade) não vieram de fonte aberta por mim; usarei [PM] com a lógica "dois tripés em contrafase = fase 0 e 0,5". A busca por Wilson 1966 **não** achou a fonte primária.

## 2. Aracnídeos

**Fontes:** Wikipédia "Spider anatomy" (li), "Scorpion" (li, 100k primeiros), "Arthropod leg" (li), artigo PMC6935789 sobre cinemática de articulações de tarântula (li, com ressalva: o próprio texto tem contradições internas), busca sobre hidráulica (só resumo; links: ETH thesis Goettler, JEB 218:977, RSC Soft Matter 2021).

### Aranha
- **Corpo [F]:** cefalotórax (prossoma) e abdome (opistossoma) ligados por **pedicelo** fino e flexível, que deixa o abdome virar em várias direções.
- **Perna [F]:** 7 segmentos: coxa, trocânter, fêmur, patela, tíbia, metatarso, tarso (garras na ponta). Pedipalpo tem 6 (sem metatarso).
- **Quelíceras [F]:** peças bucais com presas que injetam veneno. **Fiandeiras [F]:** 1 a 4 pares, geralmente 3, móveis e telescópicas, na ponta do abdome. **Olhos [F]:** em geral 8, simples; caçadores (saltadoras, lobo) enxergam bem.
- **Hidráulica [F, só resumo de busca + PMC lido]:** as juntas **fêmur-patela** e **tíbia-metatarso** não têm músculo extensor; a extensão vem da pressão da hemolinfa gerada pela compressão do prossoma; músculos flexores fazem o contrário. **Por que a aranha morta encolhe as pernas:** isto é inferência minha a partir dessas duas afirmações (sem pressão, só os flexores atuam, e a perna dobra). Nenhuma fonte aberta disse isso literalmente. Marcado como [PM-inferência forte].
- **Marcha [F, PMC6935789]:** tetrápode alternado: grupos L1+L3+R2+R4 contra L2+L4+R1+R3 (pernas vizinhas do mesmo lado em estados opostos; pernas diagonais no mesmo estado). Sequências possíveis 4-2-3-1 etc. **Fração de apoio (duty factor): 0,683 piso duro, 0,668 piso mole, 0,630 inclinado**; por perna em piso duro 0,68 / 0,69 / 0,70 / 0,66 (L1..L4). Em aranhas de teia-funil, quanto mais rápido, menor a fração de apoio (só resumo de busca). O artigo não dá offsets numéricos de fase; entre os dois grupos de 4 a fase é 0,5 [PM, decorre da definição de tetrápode alternado].
- **Ângulos medidos [F, PMC, Tabela 3, médias das faixas de movimento, em graus]:** fêmur-patela 19-53 de excursão; tíbia-metatarso 16-53; patela-tíbia 7-31; metatarso-tarso 9-28. O texto diz que a perna varia entre ~90 e ~170 graus em cada junta, mas o autor também se contradiz. Use como ordem de grandeza: **a excursão por junta num passo é pequena (20-50 graus); o arco vem do repouso dobrado**.
- **Comprimento [F, Tabela 1]:** perna 1 de 57-62 mm para corpo de 62-75 mm (tarântula), ou seja perna ~0,73-1,0 do comprimento do corpo; a perna 4 e a 1 são as mais longas, as 2 e 3 as mais curtas (nos dados).
- **Postura de ameaça:** tarântulas erguem as patas dianteiras e as presas; sem fonte aberta, [PM].

### Escorpião [F, Scorpion]
- Prossoma (carapaça, olhos, quelíceras de 3 segmentos, pedipalpos, 4 pares de pernas de 8 segmentos segundo o texto) + mesossoma de **7 segmentos** visíveis + **metassoma de 5 segmentos + télson** (ferrão/acúleo).
- Pedipalpo: coxa, trocânter, fêmur, patela, tíbia (com dedo fixo da pinça), tarso (dedo móvel). Pectines no esternito 2.
- Ameaça: ergue as pinças e a cauda. Marcha: o artigo não descreve; supor tetrápode alternado como em outros aracnídeos [PM].

## 3. Miriápodes

**Fontes:** Wikipédia "Centipede" (li, 100k primeiros), "Millipede" (li, idem), busca sobre onda metacrônica (só resumo; links: Diaz et al. 2023 JEB, SICB, Frontiers).

- **Centopeia [F]:** pelo menos 15 segmentos pós-cabeça; Scolopendromorpha 21 ou 23 pares de pernas, Geophilomorpha 27-191, Lithobiomorpha 15. **Um par por segmento**, primeiro par virou **forcípulas** (pinças com veneno, perto da cabeça); os dois últimos segmentos são pequenos e sem perna; último par ("pernas ultimas") não anda, pode ter até 2x o comprimento do primeiro; cada par é um pouco maior que o anterior (não se atropelam); número de pares **sempre ímpar**.
- **Onda [só resumo]:** a locomoção é uma onda de flexão de pernas passando ao longo do corpo (Manton 1952/1977); espécies de passo "retrógrado" ondulam o corpo quando rápidas; Chong et al. acharam melhor deslocamento quando a ondulação do corpo está adiantada ~2,51 rad da onda de pernas, com ~2 ondas de perna no corpo. Para o gerador: **2 cristas de onda visíveis ao mesmo tempo** [PM, apoiado nesse número de 2 ondas].
- **Piolho-de-cobra [F]:** diplossegmentos (do 5º segmento para trás) com **2 pares de pernas por segmento**; de 11 a mais de 300 segmentos; lento; defesa = enrolar em espiral ou bola (volvação).

## 4. Crustáceos

**Fontes:** Wikipédia "Arthropod leg" (li), "Decapoda" (li), "Crab" (li).

- **Perna de crustáceo [F]:** 7 segmentos: coxa, base, ísquio, mero, carpo, própodo, dáctilo; em muitos decápodes ísquio e mero se fundem. Pinça (quela) = dáctilo fechando contra um prolongamento do própodo.
- **Decápodes [F]:** 5 pares de pereópodes (10 "pernas"); em muitos um par é de quelípodes (quelas). 5 pares de pleópodes no abdome; urópodes + télson formam o leque da cauda.
- **Caranguejo [F parcial]:** carapaça mais larga que comprida, com margens laterais; abdome dobrado e escondido sob o corpo; corre de lado ("de caranguejo"), alguns andam de frente ou nadam; machos de muitas espécies têm quelas maiores. A página não deu contagem de pernas de caminhada: são 4 pares de pernas + 1 par de quelas = 5 pares (consistente com "5 pares de pereópodes" de Decapoda).
- **Marcha lateral, fases:** sem fonte aberta; [PM]: as pernas do lado "para onde vai" empurram, as do lado oposto puxam.
- **Lagosta:** abdome (pleon) comprido e musculoso, em vez de dobrado. Número de segmentos não verificado em fonte; [PM] 6 + télson.

## 5. Vertebrados em resumo

**Fonte:** Wikipédia "Digitigrade" (li), "Quadrupedalism" (li, pobre em detalhes).

- Plano tetrápode: 4 membros; cintura escapular e pélvica; cada membro tem 3 segmentos principais mais mão/pé com dígitos (conhecimento geral, sem página lida sobre osteologia).
- **Plantígrado [F]:** sola inteira no chão (humano). **Digitígrado [F]:** anda sobre os dedos, punho e tornozelo altos (gato, cão, maioria das aves). **Ungulígrado [F]:** só na ponta do dedo (cavalo, boi). Em digitígrados o tornozelo fica alto e dá a perna "dobrada em gancho" típica do cão.
- Diferença-chave para artrópodes [F, Arthropod leg]: vertebrados têm articulação esférica na base do membro; artrópodes só dobradiças de um plano, por isso precisam de mais segmentos.

## 6. Seres fantásticos e esqueletos

**Fontes:** apenas a busca (só resumo), fontes de fóruns e arte; **nenhuma fonte acadêmica aberta**. Tratar tudo abaixo como [PM] apoiado em consenso de design.

- **Regra do animal-base:** pegue um animal real e altere 1-2 coisas. Convence porque o espectador reconhece a mecânica (onde dobra, onde o peso cai).
- **Dragão de seis membros:** vertebrados não têm 6 membros; asa como terceiro par exige um segundo conjunto de músculos peitorais. Solução comum: **wyvern** (asas = braços, como morcego) dá um centro de gravidade verossímil (resumo de busca, fórum). Aviso do mesmo resumo: asas pequenas demais para a massa parecem ridículas.
- **Centro de massa [PM]:** em bípede, sobre os pés (cauda de contrapeso); em quadrúpede, entre os membros, mais perto dos dianteiros (cabeça pesada); em dragão-wyvern, sob a base das asas.
- **Ancoragem de músculo [PM]:** volume muscular grande só onde há osso largo para prender (omoplata, pelve, crista do crânio); sem isso a silhueta parece inchada.
- **Grifo/quimera/hidra [PM]:** grifo = leão (4 patas) + águia (asa = braço extra: seis membros de novo, tolerado porque asa de ave é lida como "capa"); hidra = 1 corpo, N pescoços saindo da mesma cintura escapular; quimera = o corpo de um animal com cabeças e cauda de outros, dividido em zonas bem separadas. Número de pescoços ≤ 5 para ainda ler cada cabeça [PM].
- **Esqueleto com poucas peças [PM]:** crânio com mandíbula separada (articula!), coluna (3-5 blocos), caixa torácica (4-6 arcos/pares de costelas finos), pelve (bloco largo com dois buracos), ossos longos (úmero/rádio/fêmur/tíbia) com **pontas alargadas** em forma de haltere. Mãos com 3-5 blocos pequenos. Desproporção: crânio e tórax grandes, ossos finos. Sem sombra aberta: o que vale é o vazio entre as costelas, então use peças finas com espaço.

## 7. O que assusta

**Fonte:** busca (só resumo): Davey 1991 e Jon May (2015, 252 voluntários, só resumo); a página do Frontiers 2021 com 1.015 eslovacos adultos associa pernas mais longas a mais medo. Fontes populares de baixa qualidade foram ignoradas.

- Pernas **longas e angulosas**, cor escura, movimento **imprevisível/errático** (Davey, May).
- A partir disso, regras do gerador [PM]: (a) mais pernas e mais compridas que o animal real (+15-30%); (b) movimento em **arrancos**: 0,3-0,5 s de corrida e 0,5-2 s de imobilidade total; (c) imobilidade com **uma perna tremendo** (jitter pequeno) mais assustadora que parar tudo; (d) simetria perfeita bilateral nas pernas; quebrar com 1 elemento assimétrico (uma perna a mais longa, olho extra, mandíbula torta) para "errado".
- Louva-a-deus e aranha: balanço lateral lento enquanto parados [F, Mantis].

---

## REGRAS ACIONÁVEIS

Ângulos: 0 = perna esticada reta, valores positivos = dobra. "Elevação" = ângulo da coxa/fêmur acima do plano horizontal do corpo. Fases em fração de ciclo (0 a 1). Tudo marcado [F] tem fonte acima; o restante é [PM].

| Arquétipo | Segmentos do corpo | Segmentos da perna e proporções (% do comprimento total da perna) | Eixo de cada junta | Ângulos de repouso (arco) | Fases da marcha e fração de apoio | Parado, o que mexe | Detalhes que dão a leitura |
|---|---|---|---|---|---|---|---|
| **Aracnídeo (aranha)** | 2 tagmas: cefalotórax (1 bloco grande) + pedicelo (bloco mínimo) + abdome (1 bloco oval) [F]. Opcional: 2 quelíceras, 2 pedipalpos, fiandeiras (3, na ponta) | 8 pernas x 5 ossos mínimos (7 ideal [F]): coxa 6%, trocanter 4%, fêmur 28%, patela 8%, tíbia 26%, metatarso 20%, tarso 8% [PM; ordem e nomes F]. Pernas 1 e 4 as mais longas, 2 e 3 as mais curtas [F-dados da tarântula]. Perna total 0,75-1,0 x corpo [F]; para medo, 1,2-1,6x [PM] | Coxa: balanço horizontal (eixo vertical do corpo). Fêmur-patela: dobradiça vertical (sobe/desce) [hidráulica F]. Patela-tíbia: dobradiça vertical. Tíbia-metatarso: dobradiça vertical (hidráulica F). Todas no mesmo plano vertical da perna, o plano gira com o balanço da coxa | Fêmur sobe 40-60 graus acima do corpo; patela dobra 60-90 para baixo; tíbia desce quase vertical (10-20 da vertical); metatarso 20-30 para dentro até o pé tocar. Forma "M/joelho acima do corpo" [PM, baseado nas faixas 90-170 da tabela F] | **Tetrápode alternado [F]:** grupo A = L1, R2, L3, R4 em fase 0; grupo B = R1, L2, R3, L4 em fase 0,5. Apoio **0,65-0,70** [F]; mais rápido = menor apoio, até 0,55 [PM, tendência F]. Excursão de cada junta num passo 20-50 graus [F] | Tremor curto nas pernas 1 e pedipalpos; abdome bobe 2-3 graus; ocasionalmente ergue e abre pernas 1 e 2 | Pedicelo fino visível; 8 olhos em 2 fileiras; quelíceras com presa curva; fiandeiras; pernas com cerdas (blocos finos) |
| **Hexápode (inseto)** | 3 tagmas: cabeça + tórax (3 blocos: pro, meso, metatórax) + abdome (5-7 blocos) [F: 3 e 11-12 no plano básico; blocos = PM] | 6 pernas x 4-5 ossos: coxa 10%, trocanter 3% (pode fundir), fêmur 32%, tíbia 35%, tarso 20% (pode partir em 2 ossos) [PM; nomes F]. Par 1 curto, par 3 o mais longo (barata F). Besouro: pernas curtas e grossas, 0,6x corpo. Gafanhoto: fêmur 3 com 45% e grosso, salta [PM]. Mantis: fêmur 1 com 40% e coxa longa ~ igual ao fêmur [F]; protórax longo [F] | Coxa: balanço frente/trás (eixo vertical). Trocanter-fêmur: dobradiça vertical pequena. Fêmur-tíbia: dobradiça vertical (joelho). Tarso: sem músculo, só flexão passiva [F] | Fêmur 30-50 graus para fora e para cima do plano do corpo, tíbia dobrada 70-100 para baixo; joelho acima do corpo (besouro, barata) ou na altura (formiga) [PM] | **Tripé alternado [F confirmado como conceito]:** tripé A = L1, R2, L3 em fase 0; tripé B = R1, L2, R3 em fase 0,5 [PM, decorre]. Apoio 0,55-0,65 [PM; sem fonte aberta] | Antenas varrem (2-3 ossos com atraso); palpos bucais; abdome respira (±1-2 graus); mantis: balanço lateral lento [F]; barata: antenas ativas | Antenas longas; elitros (besouro) separados do abdome; mandíbulas em V; espinhos na tíbia (barata F); cabeça menor que o tórax |
| **Corrente (centopeia/piolho-de-cobra)** | Cabeça + 15-23 segmentos com par de pernas [F: 15, 21, 23; geófilas 27-191]. Usar 15, 21 ou 23 (ímpar [F]); 2 últimos segmentos pequenos e sem perna [F]; piolho-de-cobra 11 a 300+ com 2 pares por segmento [F] | Cada perna: 3 ossos (coxa curta, fêmur/tíbia longo, tarso curto) [PM]. Cada par ligeiramente maior que o anterior [F]; último par vira antena-garra, até 2x o primeiro [F]. Primeiro par = forcípulas, em pinça, com veneno [F] | Pernas: dobradiça vertical no joelho, balanço lateral de baixa amplitude. Corpo: cada segmento guina (eixo vertical) e ondula (centopeia rápida [só resumo]) | Pernas abertas para o lado, com 45 graus do plano do corpo, joelho dobrado 60; corpo reto | **Onda metacrônica:** fase de cada par = (i/N) x 2 ondas [PM; "2 ondas visíveis" apoiado em Chong et al., só resumo]. Piolho-de-cobra: ondas mais curtas e lentas, 3-4 ondas [PM]. Apoio 0,6-0,7 [PM] | Antenas; forcípulas abrem e fecham; a onda de pernas continua pequena mesmo parado | Forcípulas visíveis; corpo achatado (centopeia) vs cilíndrico (piolho); segmentos com placas | Último par longo e para trás; cabeça com par de antenas |
| **Escorpião** | Prossoma (1 bloco) + mesossoma (7 segmentos [F], usar 3-4 blocos) + metassoma 5 segmentos + télson [F] | 4 pares de pernas (8 segmentos [F, texto Scorpion]; usar 5 ossos [PM]); pedipalpos = coxa, trocanter, fêmur, patela, tíbia + dedo fixo, tarso = dedo móvel [F]. Pinça ~35% do comprimento do corpo [PM] | Pernas: como aranha. Pinça: dedo móvel dobra no plano horizontal (abre/fecha). Metassoma: cada junta dobradiça vertical, sobe curvando para frente | Cauda levantada em S: segmentos 1-2 sobem 20-40, 3-5 dobram 30-40 cada, télson aponta para a frente. Pinças abertas à frente [F: postura de ameaça] | Tetrápode alternado como aranha [PM; artigo não descreve marcha]. Apoio 0,65 [PM] | Cauda balança de leve; dedos da pinça abrem e fecham; pedipalpos testam o ar | Cauda curva com ferrão; pinças grandes; pectines sob a barriga [F] |
| **Caranguejo** | Carapaça larga (1-2 blocos, mais larga que comprida [F]) + abdome dobrado sob o corpo [F]; olhos em pedúnculo [PM] | 4 pares de pernas + 1 par de quelípodes [F; 5 pereópodes]. Perna: coxa/base curtos, ísquio+mero (fundidos [F]) 30%, carpo 20%, própodo 30%, dáctilo 20% [PM; nomes F]. Quela: própodo grosso e dáctilo móvel [F] | Juntas coxa e base nos pés do lado; mero-carpo e carpo-própodo: dobradiça vertical; dáctilo: dobradiça. A perna dobra para o lado e para baixo | Pernas abertas para o lado, joelho (mero-carpo) alto, ~100 graus; quelas à frente dobradas em L | Marcha lateral [F]. Lado da frente empurra, lado de trás puxa [PM]. Pares de pernas em ondas de 4 passos defasadas 0,25 cada [PM]. Apoio 0,6 [PM] | Quelas se abrem e fecham devagar; olhos em pedúnculo giram; pernas pequenas (maxilípedes) fazem bolhas | Carapaça achatada com bordas laterais; quelas assimétricas (macho) [F]; abdome escondido |
| **Esqueleto bípede** | Crânio + mandíbula + coluna (3-4 blocos) + caixa torácica (4-6 arcos) + pelve (1 bloco) [PM] | Braço: úmero 45%, antebraço 40% (rádio+ulna), mão 15%; perna: fêmur 45%, tíbia 42%, pé 13% [PM, proporções humanas aproximadas, sem fonte aberta]. Pontas dos ossos longos alargadas, haltere [PM] | Ombro: esférico (2-3 eixos). Cotovelo: dobradiça. Quadril: esférico. Joelho: dobradiça. Mandíbula: dobradiça | Postura meio curvada: joelhos 10-20 graus, cotovelos 20-30, cabeça adiantada [PM] | Marcha bípede: pés em fase 0 e 0,5; apoio 0,6 [PM, caminhada humana típica; sem fonte lida]. Braços em contrafase | Mandíbula abre/fecha de leve; costelas não mexem; dedos tremem; cabeça inclina | Caixa torácica com vão entre costelas; pelve aberta; crânio grande; ossos finos; pontas alargadas |
| **Dragão (wyvern)** | Crânio + pescoço (5-8) + tronco (3-4) + cauda (8-12) + asas como braços [PM]. Sem 6 membros (problema dos seis membros [fonte fraca]) | Perna traseira digitígrada: fêmur 25%, tíbia 30%, metatarso 30%, dedos 15%. Asa: úmero, antebraço, dedos longos com membrana [PM]. Cintura escapular reforçada | Pescoço/cauda: guinada + arfada. Asa: ombro esférico, cotovelo dobradiça, dedos dobradiça. Pernas: dobradiças verticais | Pernas traseiras: joelho 40-60 graus para frente, "zigue-zague" digitígrado. Asa dobrada ao lado do corpo, punho para cima | Quadrúpede em terra (asas apoiadas nos punhos) ou bípede; caminhada lenta, patas traseiras em fase 0 e 0,5; apoio 0,7 [PM] | Pescoço ondula devagar; cauda balança com atraso; respira (tronco); asas se ajustam | Asas grandes proporcionalmente à massa (aviso de [fonte fraca]); centro de massa sob a base das asas |

## Regras de implementação sugeridas (PM)

1. **Perna de aranha com arco:** use 5 ossos mínimo (coxa, fêmur, patela, tíbia, metatarso+tarso). Repouso: fêmur sobe, tíbia desce, formando um joelho acima do corpo.
2. **Passo:** levante o pé 15-25% do tamanho da perna, durante a fase de balanço (1 menos fração de apoio).
3. **Excursão do passo:** só 20-50 graus por junta [F], movendo mais a coxa (balanço) do que o joelho.
4. **Arrancos:** gerar a fase de movimento com dois estados (corre 0,3-0,5 s, para 0,5-2 s).
5. **Vida parada:** sempre um micro-movimento em ao menos 2 partes do corpo.

## Glossário

- **Tagma:** região do corpo de artrópode (cabeça, tórax, abdome).
- **Coxa, trocânter, fêmur, tíbia, tarso:** segmentos de perna de inseto; aracnídeos acrescentam patela e metatarso.
- **Pedicelo:** cintura fina entre cefalotórax e abdome de aranha.
- **Quelícera / pedipalpo:** peças bucais / apêndices sensoriais de aracnídeos.
- **Fiandeira:** órgão que produz fio de seda.
- **Metassoma / télson:** cauda de 5 segmentos do escorpião / ferrão na ponta.
- **Forcípula:** primeiro par de pernas da centopeia, convertido em pinça com veneno.
- **Diplossegmento:** segmento duplo do piolho-de-cobra, com 2 pares de pernas.
- **Pereópode / quela:** perna de decápode / pinça.
- **Duty factor (fração de apoio):** fração do ciclo em que o pé está no chão.
- **Tripé / tetrápode alternado:** 3 ou 4 pés apoiando ao mesmo tempo, em dois grupos em contrafase.
- **Onda metacrônica:** onda de passo que viaja ao longo de uma fileira de pernas.
- **Plantígrado / digitígrado / ungulígrado:** anda na sola / nos dedos / na ponta do dedo.

## Fontes (com URL e status de leitura)

Lidas (extrato da página):
- https://en.wikipedia.org/wiki/Insect_morphology (primeiros 100k caracteres)
- https://en.wikipedia.org/wiki/Spider_anatomy
- https://en.wikipedia.org/wiki/Hexapod_(robotics)
- https://en.wikipedia.org/wiki/Scorpion (primeiros 100k)
- https://en.wikipedia.org/wiki/Centipede (primeiros 100k)
- https://en.wikipedia.org/wiki/Millipede (primeiros 100k)
- https://en.wikipedia.org/wiki/Crab (nada sobre contagem de pernas)
- https://en.wikipedia.org/wiki/Arthropod_leg
- https://en.wikipedia.org/wiki/Digitigrade
- https://en.wikipedia.org/wiki/Mantis (primeiros 100k)
- https://en.wikipedia.org/wiki/Cockroach (primeiros 100k)
- https://en.wikipedia.org/wiki/Decapoda
- https://en.wikipedia.org/wiki/Quadrupedalism (sem detalhe útil)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6935789/ (cinemática de tarântula; tem contradições internas entre texto e tabela)

Só resumo da busca (não abri):
- https://research-collection.ethz.ch/bitstream/handle/20.500.11850/502395/1/thesis_ChantalGoettler.pdf (hidráulica)
- https://cob.silverchair.com/jeb/article-pdf/218/7/977/2076054/jeb111922.pdf (cinemática e temperatura)
- https://pubs.rsc.org/en/content/articlehtml/2021/sm/d1sm00338k (hemolinfa shear-thinning)
- https://crablab.gatech.edu/pages/publications/pdf/Diaz_et_al_2023_JEB.pdf (centopeia)
- https://sicb.org/?p=39562 (onda de corpo e pernas de centopeia)
- https://theconversation.com:443/explainer-why-are-we-afraid-of-spiders-26405 e https://www.zmescience.com/science/biology/arachnophobia-evolution-spider-08042015 (medo de aranhas; Davey, May)
- https://www.frontiersin.org/articles/10.3389/fevo.2021.694569/endNote
- Resultados de fórum e tutorial de desenho sobre dragões (baixa qualidade; usados só para a ideia do wyvern e de peso/asa)

## Lacunas

1. Sem fonte aberta para **fases e fração de apoio do tripé de insetos** (Wilson 1966, Full/Cruse) nem do caranguejo; todos os números de inseto e crustáceo são [PM].
2. Sem fonte para **proporções numéricas dos segmentos** de perna (% de coxa, fêmur, tíbia) em insetos, aranhas e crustáceos; só os nomes, a ordem e alguns comprimentos totais da tarântula.
3. **Criaturas fantásticas e esqueleto:** nenhuma fonte acadêmica ou de anatomia comparada lida; tudo é consenso de design e proposta minha. Também falta fonte para "aranha morta encolhe as pernas" (só inferência a partir da hidráulica).
