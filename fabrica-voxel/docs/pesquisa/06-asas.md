# 06 - Asas: anatomia, voo e regras para o gerador (Sanctum Obscura)

Data da pesquisa: 2026-11-10. Autor: pesquisador (Claude). Idioma: pt-BR.

Legenda de confiança usada em todo o texto:
- **[LIDO]** abri a página e extraí o dado do texto.
- **[RESUMO]** só vi o resumo da busca (a página não foi aberta, ou o PDF veio ilegível/503).
- **[PROPOSTA]** número ou regra meus, sem fonte; a justificativa vem junto.

Aviso geral: nenhuma fonte que consegui abrir deu razões de comprimento úmero:antebraço:metacarpo:dedo para pterossauros ou morcegos (os PDFs de osteologia vieram ilegíveis). As proporções de segmento abaixo são, portanto, **[PROPOSTA]** ancorada em afirmações qualitativas lidas (por exemplo "dedo-asa é metade ou mais da asa").

---

## 1. Veredito (5 linhas)

1. Asa de porta é erro de anatomia: toda asa real tem pelo menos duas articulações que se movem com atraso entre si (ombro e punho), e a ponta sempre chega atrasada em relação à base. Use no mínimo 2 ossos em qualquer asa, 4 em morcego/dragão.
2. Descida e subida reais são quase iguais em duração (razão de descida 0,45 a 0,56 em pombo e morcegos [LIDO/RESUMO]); o que muda é a **forma** da asa: na subida ela dobra (morcego: envergadura 30-40% da descida [LIDO]). Use o seno "asa" (rápido/lento) só como exagero de estilo, com razão visual 0,40/0,60 (proposta).
3. Insetos são o oposto das aves: não têm articulação de cotovelo; a asa é uma lâmina rígida que gira (supina/prona) na ponta de uma batida; dois ossos (base = batida, lâmina = torção atrasada) bastam. Libélula: par traseiro adiantado 77 a 102 graus no voo para frente, 180 graus (oposição) no pairar [LIDO/RESUMO].
4. Acima de 15 Hz o jogo (30 qps) não consegue mostrar a batida: renderizar "leque translúcido + tremor de 2 poses", nunca a frequência real (seção 6.3).
5. O corpo precisa reagir: subir/descer em fase com a batida, cabeça e cauda compensando em contrafase. Sem isso a asa parece colada.

---

## 2. Asa de membrana (morcego e pterossauro: base da asa de dragão)

### 2.1 Morcego
- Esqueleto da asa: úmero, rádio (a ulna é reduzida/fundida; o rádio é o osso longo do antebraço), carpo, metacarpos e falanges alongadas dos dedos II a V. A legenda da Wikipédia lista úmero, rádio, ulna, carpos e falanges [LIDO, Bat flight]. A membrana (patágio) é feita de fibras de elastina e tecido conjuntivo (durável e flexível) [LIDO]. O "plagiopatágio" cobre o antebraço, e há dactilopatágio (entre dedos) e uropatágio (entre as pernas) [LIDO apenas como nomes em legenda; a descrição detalhada dos 4 patágios não foi lida, está no meu conhecimento prévio].
- Massa da asa em seis morcegos pteropodídeos: úmero + antebraço + punho = 60% da massa da asa; dedos (metacarpos e falanges) = 12,1% da massa, mas respondem por ~44% do custo inercial; braço, 38%; membranas, ~16%; pernas ~1,9% [LIDO, PMC3385481]. Leitura útil: a ponta (dedos) é leve, mas o que mais custa balançar; por isso, na subida, ela fecha.
- Razão de descida (tempo de descida / ciclo): Cynopterus 0,48; Rousettus 0,50; Pteropus pumilus 0,52; Eidolon 0,51; Pteropus hypomelanus 0,56; P. vampyrus 0,56; média 0,52 [LIDO, tabela]. Ou seja, descida e subida têm praticamente a mesma duração.
- Dobra na subida (razão de envergadura = envergadura na subida / na descida): média ~0,3 a 0,4, com ciclos até 0,16 [LIDO]. Dobrar e desdobrar acontece sobretudo durante a subida; o custo inercial da subida não é menor que o da descida [RESUMO, mesma linha de pesquisa].
- Proporção do corpo: envergaduras 0,36 m (34 g) a 1,45 m (1,08 kg) [LIDO]. Razão de aspecto de morcegos 5 a 11; carga alar 4 a 35 N/m2 [LIDO, Wikipédia].
- A subida de morcegos sustenta peso, e em baixa velocidade "faz um flick para trás" que gera empuxo (Glossophaga) [RESUMO].

### 2.2 Pterossauro
- Dedo IV (dedo-asa) enorme, normalmente 4 falanges; o conjunto "braço + dedo" é uma viga que sustenta a membrana [LIDO, Wikipédia Pterosaur; RESUMO da busca].
- Em pterodactilóides avançados o 4o metacarpo é muito alongado, igual ou maior que o antebraço; dedo-asa = cerca de metade ou mais do comprimento total da asa; a última falange é curta e sem garra, dando ponta arredondada (reduz arrasto induzido) [LIDO].
- Úmero curto e robusto com crista deltopeitoral grande; rádio/ulna bem mais longos que o úmero [LIDO].
- Pteroide: osso do punho que sustenta o propatágio; em ornitoquerídeos mede ~47% da ulna [RESUMO].
- Membrana: propatágio (frente, entre punho e ombro), braquiopatágio (do dedo-asa até a perna; chega ao tornozelo/perna inferior em todos os espécimes completos) e cruropatágio/uropatágio entre as pernas (possivelmente com a cauda). O braquiopatágio divide-se em actinopatágio (distal, denso em fibras) e tenopatágio (proximal, poucas fibras) [LIDO, PMC2842671 e Wikipédia]. Actinofibrilas de ~0,1 mm, 4 a 9 por mm, ao menos 3 camadas; músculo fino e vasos podem ajustar folga/curvatura [LIDO].
- Repouso/solo: asa dobrada para trás, pterodactilóides andavam sobre os metacarpos com os dedos pequenos apontando para trás; o dedo-asa varre até ~175 graus e a asa dobra quase automaticamente quando se dobra o cotovelo [LIDO, Wikipédia].
- Pteranodon: razão de aspecto ~9:1 (albatroz ~8:1), planador dinâmico com rajadas de batida; decolava de quatro, com impulso dos membros anteriores (subida enquanto sai do chão, depois descida rápida) [LIDO, Wikipédia Pteranodon]. Envergaduras: anurognatídeos ~0,4 m; típicos do Jurássico até 2 m; Pteranodon macho 5,6 m (média); azdarquídeos 10-11 m [LIDO].
- Ciclo de batida de pterossauro: não há medição (não existe animal vivo). Tudo é inferência; trate como morcego grande e mais lento.

### 2.3 Cadeia de ossos recomendada (morcego, pterossauro, dragão) - [PROPOSTA]
| Osso | Papel | % do comprimento da asa | Observação |
|---|---|---|---|
| A: úmero | ombro, bate | 15 | curto e forte; gira pouco |
| B: antebraço | cotovelo | 25 | rádio/ulna; mais longo que o úmero (LIDO) |
| C: metacarpo + punho | punho | 15 | em pterodactilóide pode chegar a 20-25 (LIDO: igual ou maior que antebraço) |
| D: dedo-asa | ponta | 45 | >= 50% se quiser pterossauro "puro" (LIDO) |
Dedos II-III-IV podem ser três ripas finas (varetas de voxel) saindo do osso C e D, com membrana entre elas; dactilopatágio vira um "leque" de 2 a 3 quadriláteros. Membrana do corpo (plagiopatágio) vai do osso B/D até a coxa (osso do corpo), ancorada no "tornozelo".

---

## 3. Asa de ave

Fontes: [LIDO, Wikipédia Bird flight], [RESUMO, estudos de pombo].
- A descida produz a maior parte do empuxo; os músculos giram o vetor de sustentação para frente [LIDO].
- Na subida a asa dobra levemente para dentro (reduz custo) e as penas giram nos folículos, deixando o ar passar; a integridade da asa é restaurada na descida. Isso importa mais em decolagem e baixa velocidade [LIDO].
- Primárias: ligadas à mão reduzida (3 dedos); formam o aerofólio de ponta. Secundárias: ligadas à ulna, atrás do punho [LIDO]. Em termos de esqueleto: úmero, antebraço (rádio+ulna), mão (carpometacarpo). Regras de proporção: [PROPOSTA] úmero 30%, antebraço 30%, mão com primárias 40% do comprimento total de asa estendida (penas incluídas na mão). Não tenho fonte de números para as razões.
- Pombo em voo lento: 6,67 Hz, descida 0,067 s e subida 0,083 s, razão de descida 0,45 (um indivíduo, filmagem) [RESUMO]. Em curva, a subida gerou ~50% das forças aerodinâmicas da descida [RESUMO]. "Reversão de ponta" (tip-reversal): em baixa velocidade a mão gira (supinação) na subida [RESUMO].
- Voo saltitante (bounding): asas fechadas junto ao corpo entre rajadas de batida; trajetória balística [LIDO]. Planeio: asa aberta e quase parada; úteis como pose-chave "planar".
- Beija-flor: exceção, asa estendida o tempo todo, trajetória em 8, sustentação em ambas as fases; ~12 Hz (maior espécie) até 99 Hz (Chaetocercus bombus) [LIDO, Wikipédia Hummingbird e Bird flight]. (A mesma página também cita 52 Hz para o beija-flor-de-garganta-rubi e 43 Hz como geral: inconsistência da fonte.)

---

## 4. Asas de inseto (seção maior)

### 4.1 Tórax e músculos [LIDO, Wikipédia Insect flight]
- **Direto (Odonata)**: músculos presos direto na base da asa; um pequeno movimento para baixo da base levanta a asa; asas da frente e de trás operam de forma independente. Isso permite o atraso de fase entre pares.
- **Indireto (todos os outros)**: músculos deformam o tórax; longitudinais fazem a asa descer e dorsoventrais fazem subir. Músculos diretos auxiliares dão controle fino.
- **Síncrono**: um impulso nervoso = uma contração; vale para < 100 Hz (faixa geral ~5 a 200 Hz); menos potente. **Assíncrono** (besouros, moscas, himenópteros): várias contrações por impulso; passa de 1000 Hz em pequenos.
- Implicação de design: insetos "lentos" (borboleta, libélula, mariposa) têm batida visível e legível a 30 qps; insetos "assíncronos" (mosca, abelha, vespa) nunca são legíveis.

### 4.2 Articulação, nervuras
- A asa é uma lâmina rígida e fina com nervuras que a enrijecem; borboletas: asas da frente com nervuras grossas no bordo de ataque, traseiras menores e mais redondas com menos nervuras [LIDO, Wikipédia Butterfly]. A asa é articulada na base (axila); girar a lâmina (pronação/supinação) acontece na virada da batida; não há cotovelo.
- O dado que usarei: a torção é o movimento principal. Número de amplitude de torção: sem fonte lida. [PROPOSTA] 40 a 70 graus de rotação do bordo de ataque entre o meio da descida e o meio da subida.

### 4.3 Trajetória da ponta
- Wikipédia (Insect flight): nos voos com sustentação suficiente a ponta da asa descreve uma elipse; outros insetos têm formas que não se cruzam [LIDO]. Beija-flor: trajetória em 8 [LIDO]. Não achei fonte lida que afirme "trajetória em 8" para insetos em geral; muita literatura chama de "figura-de-oito" para pairar de mosca/abelha, mas não confirmei (o resumo de busca sobre abelha disse explicitamente que não achou).
- Abelha em pairar: amplitude ~90 graus e ~230 Hz, baixa amplitude/alta frequência; moscas-das-frutas e outros usam ~145 a 165 graus [RESUMO, PNAS Altshuler et al. 2005]. Em ar rarefeito, amplitude +30 a 50% sem mudar a frequência [RESUMO].
- Para o jogo [PROPOSTA]: elipse = osso A bate no plano (amplitude A) e osso B (lâmina) torce com atraso de um quarto de ciclo (~90 graus, 7-8 quadros a 7,5 Hz); se o motor suportar um segundo eixo, adicionar um balanço vertical de 2x frequência com amplitude ~10-15 graus para um "8".

### 4.4 Libélula (4 asas) [LIDO Frontiers 2022 Pantala; RESUMO Purdue/outros]
- Pantala flavescens, voo ascendente: frequência asa dianteira 28,5 Hz e traseira 28,4 Hz (subida íngreme, ângulo de subida 67,5 graus); 27,2/27,4 Hz (subida suave 22,4 graus). Amplitude de batida: ~65/66 graus (íngreme); dianteira ~61-62 graus e traseira ~36-38 graus (suave). Ângulo do plano de batida -2,5 graus (íngreme) ou ~42 graus (suave). Diferença de fase (traseira adiantada) ~77 graus (íngreme) e ~102 graus (suave). Ângulo do corpo 65 e 13,5 graus [LIDO]. A fonte tem pequenas inconsistências internas (61,3 vs 62; 41,6 vs 43,6) e não dá tempos de descida/subida nem o comprimento da asa.
- Pairar: ~180 graus de defasagem (oposição); voo para frente: 54 a 100 graus; manobras/aceleração: perto de 0 (em fase) [RESUMO].
- Aeshnid (libélula grande): 38 Hz a 7 m/s; zigoptera (donzelinha): 16 Hz a 1,5 m/s [LIDO, tabela Wikipédia]. Resumo geral: libélulas batem ~29 Hz, acima da frequência de ressonância (20 Hz) [RESUMO, Biology Letters via busca].
- Design: 2 pares independentes com a mesma onda mas fase diferente (traseiro = dianteiro + 90 graus para voo, 180 graus para pairar, 0 para disparo).

### 4.5 Borboleta e mariposa
- 4 asas escamosas; em borboletas as asas da frente e de trás não são presas por gancho (como em mariposas) e se coordenam pelo atrito da área sobreposta [LIDO, Wikipédia Butterfly]. Vanessa atalanta usa sustentação por vórtices, captura de esteira, mecanismos rotacionais e "clap and fling" (Weis-Fogh) alternando rapidamente [LIDO].
- Repouso: borboletas mantêm asas verticais acima do corpo; mariposas planas ou dobradas sobre o corpo [LIDO].
- Frequência: borboleta-branca-grande (Pieris brassicae) 12 Hz a 2,5 m/s [LIDO, tabela]. Mariposas-esfinge: Manduca sexta 22 Hz; Sphinx ligustri 25-27 Hz; Deilephila elpenor 41 Hz; Hyles euphorbiae 42-44 Hz; Macroglossum stellatarum 48-55 Hz; Hemaris fuciformis 46-65 Hz (livre) [LIDO, PMC3673148, em gramas: 1,5; 1,48; 0,85; 0,89; 0,32; 0,20]. Mariposa-beija-flor "hummingbird hawkmoth" 85 Hz na tabela da Wikipédia (valor divergente dos 48-55 Hz medidos por PMC; fontes diferentes, não conciliado) [LIDO].
- "Clap and fling" de verdade só é essencial em insetos < 1 mm (tripés a 254 Hz); reduz arrasto até 50% com asa flexível [LIDO]. Em borboleta, a versão "palmas" visual (asas se tocando no ápice da subida) é um recurso de animação válido: [PROPOSTA] pose-chave com asas fechadas por 1-2 quadros no topo da subida.
- Amplitude de borboleta: não achei fonte lida; [PROPOSTA] 100-140 graus, batida lenta e ampla (conforme o pedido).

### 4.6 Abelha, mosca, halteres
- Frequências [LIDO tabela]: abelha 250 Hz; mosca-doméstica 190 Hz; mosca-das-flores 120 Hz; mamangaba 130 Hz; vespão 100 Hz; mutuca 96 Hz. Outros: abelha pairando ~230 Hz, ~90 graus [RESUMO]; Hemaris diffinis ~60 Hz vs. mamangaba ~180 Hz com tamanho similar [RESUMO, preprint Sponberg]: tamanho prediz fraco a frequência entre espécies; o tipo de músculo (síncrono x assíncrono) prediz melhor.
- Halteres (moscas): asas posteriores reduzidas, giroscópio. Batem na mesma frequência da asa, quase 180 graus fora de fase em Brachycera; offset de ~90 graus entre direito e esquerdo; detectam rotação > ~50 graus/s [LIDO, Wikipédia Halteres]. No jogo: dois pinos de 1 voxel batendo em contrafase da asa; só aparecem visuais se a mosca é grande e lenta.

### 4.7 Besouro (élitros + asa membranosa)
- Os élitros (asas dianteiras endurecidas) não voam; ficam levantados para soltar as asas traseiras; as asas membranosas dobram sob os élitros após o pouso [LIDO, Wikipédia Beetle].
- Besouro-rinoceronte (Allomyrina dichotoma): desdobramento em 2 fases e **passivo**: (1) élitros abrem e liberam as asas até ~48,5 graus do abdômen com a ponta ainda dobrada; (2) o batimento levanta as bases e desdobra as pontas, impulsionado por energia elástica dos élitros e forças de batida; a ~38 Hz o mecanismo se repete em robô [RESUMO, EPFL/Nature 2024; o arXiv veio ilegível].
- Design: pose-chave "preparar" (élitros +60 a 80 graus; PROPOSTA), "liberar" (asa a 48 graus e ponta dobrada, valor LIDO), "voar" (asa aberta, batida). Reverso no pouso.

### 4.8 Tabela de frequências por espécie (resumo; cuidado com a fonte)
| Espécie/grupo | Hz | Fonte | Status |
|---|---|---|---|
| Borboleta-branca-grande (Pieris brassicae) | 12 | Wikipédia Insect flight (tabela) | LIDO |
| Donzelinha (damselfly) | 16 | idem | LIDO |
| Manduca sexta (esfinge, 1,5 g) | 22 | PMC3673148 | LIDO |
| Sphinx ligustri (1,48 g) | 25-27 | idem | LIDO |
| Escorpião-mosca | 28 | Wikipédia tabela | LIDO |
| Pantala flavescens (libélula) | 27-28,5 | Frontiers 2022 | LIDO |
| Libélula aeshnid | 38 | Wikipédia tabela | LIDO |
| Deilephila elpenor / Hyles euphorbiae (0,85-0,89 g) | 41-44 | PMC3673148 | LIDO |
| Macroglossum stellatarum (0,32 g) | 48-55 | idem | LIDO |
| Hemaris fuciformis (0,20 g) | 46-65 | idem | LIDO |
| Hemaris diffinis | ~60 | preprint Sponberg 2025 | RESUMO |
| Mariposa-beija-flor (tabela) | 85 | Wikipédia tabela | LIDO |
| Mutuca | 96 | idem | LIDO |
| Vespão | 100 | idem | LIDO |
| Mosca-das-flores | 120 | idem | LIDO |
| Mamangaba | 130 (180 no preprint) | Wikipédia / preprint | LIDO/RESUMO |
| Mosca-doméstica | 190 | Wikipédia | LIDO |
| Abelha | 230-250 | PNAS 2005 / Wikipédia | RESUMO/LIDO |
| Tripés (clap-and-fling) | 254 | Wikipédia | LIDO |
| Mosquito-pólvora/mosquito pequeno | ~1000 | resumo de busca (fonte secundária) | RESUMO (fraco) |
| Besouro-rinoceronte | ~38 (robô reproduzindo) | EPFL | RESUMO |
Regra geral lida: insetos maiores batem mais lentamente; mas a relação por espécie é fraca [RESUMO preprint]. [PROPOSTA] para o gerador: f(Hz) = 22 * (tamanho_em_voxels/ 10)^-0.5 limitado em 8 a 250, só como semente; trocar por frequência de design (seção 7).

---

## 5. Fadas

- Asas são uma adição moderna: no folclore as fadas voavam por magia ou "montadas em hastes de ragwort e costas de aves" [LIDO, Wikipédia Fairy]. As asas ficaram comuns na pintura vitoriana; ilustrações modernas usam asas de borboleta ou de libélula (exemplo: Falero, 1888, asas de borboleta); o imaginário tornou-se "mais bonito e menor" com Cicely Mary Barker (flower fairies, 1923-48) [LIDO].
- Número de pares e ponto de nascimento nas costas: a página não diz nada. [PROPOSTA] convenção visual (observação de arte popular, sem fonte): 1 par (borboleta/libélula estilizada) ou 2 pares (libélula/borboleta de 4 asas); nascimento entre as omoplatas, um pouco acima da cintura escapular; o par traseiro ligeiramente mais baixo e menor. Cigarra: 2 pares transparentes, 'telhado' sobre o corpo em repouso (conhecimento prévio, sem fonte lida).
- Animação [PROPOSTA]: a fada voxel deve usar a lógica de inseto (lâmina rígida + torção), baixa frequência visual (6 a 10 Hz percebidos), amplitude 50-70 graus, e corpo ereto com balanço (fada leve = corpo balança mais, vertical 1 voxel).

---

## 6. Dragões

### 6.1 Anatomia especulativa e design
- Dragão ocidental padrão: 4 pernas + par de asas (6 membros), problema anatômico: vertebrados têm 4 membros; sustenta-se com "asas = membros anteriores modificados" (wyvern/dragão-morcego) ou com seis membros (hexápode, como inseto) [RESUMO, fontes de fãs/TVTropes; sem fonte acadêmica].
- Wyvern: heráldica britânica a partir do século XVI distingue wyvern (2 pernas + 2 asas) de dragão (4 pernas) [LIDO, Wikipédia Wyvern]. A página não diz que as asas são membros anteriores.
- Para o gerador, a solução bioanatômica mais coerente: **wyvern = asa-membro anterior** (como morcego/pterossauro: 4 ossos de asa), e que ele anda sobre os "punhos" (como pterossauro: metacarpos no solo, dedo-asa dobrado para trás) [LIDO, Wikipédia Pterosaur]. Dragão de 6 membros: asa nasce nas costas, atrás da escápula, com ossos próprios (não é membro). Cada caso tem custo: seis membros precisam de ombro dedicado (um osso-raiz "escápula alada").
- Asa de morcego vs. de ave: dragões de asa de pássaro (penas) têm menos tradição e mais complexidade (penas = mais peças). Asa de membrana tem a vantagem de dobrar bem e ter "dedos" visíveis.
- Envergadura em relação ao corpo [PROPOSTA]: para voar de forma crível, envergadura ~2,5 a 3,5x o comprimento do tronco (pescoço e cauda fora). Âncoras: Pteranodon macho 5,6 m e razão de aspecto 9:1 [LIDO]; morcegos de 0,36 m com 34 g a 1,45 m com 1 kg [LIDO]; as proporções do tronco do pterossauro não foram lidas.
- Dragão de ficção é tão grande que a física não suporta (carga alar); por isso a convenção: batidas **lentas e amplas** (2 a 3 Hz) em dragões enormes (PROPOSTA), pairar com pequenas rajadas.

### 6.2 Dobra de repouso
- Pterossauro: asa dobra para trás, dedo-asa varre ~175 graus; metacarpos no solo [LIDO]. Morcego: dedos dobram junto ao antebraço e a membrana pende. Ave: asa em "Z" (úmero, antebraço, mão).
- Regra [PROPOSTA] para repouso de dragão: osso A = -20 graus (para trás); B = +140 (dobra sobre A); C = -120 (dobra de volta); D = +160 (dedo paralelo ao corpo).

### 6.3 Frequência de batida do dragão
- Sem dado real. Pterossauro como morcego grande: Pteranodon provavelmente planava e batia em rajadas [LIDO]. Pteropus vampyrus (1 kg) é o maior morcego medido; frequência não tabulada no artigo lido. [PROPOSTA]: 3-4 Hz para dragão grande, 5-6 Hz para wyvern médio, 7-9 Hz para dragãozinho.

---

## 7. Ciclo de batida com números

### 7.1 Medido [LIDO/RESUMO]
- Razão de descida real: morcegos 0,48 a 0,56 (média 0,52) [LIDO]; pombo 0,45 [RESUMO]. Hawkmoth/dragonfly: não achei valores de tempo de descida/subida lidos.
- Dobra: morcego, envergadura na subida 30-40% da descida [LIDO]; ave, dobra "leve" [LIDO].
- Fase de libélula: 77 a 102 graus (voo), 180 (pairar), ~0 (manobra) [LIDO/RESUMO].
- Amplitude: libélula 61-66 graus [LIDO]; abelha ~90 graus [RESUMO]; mosca-das-frutas 145-165 graus [RESUMO].

### 7.2 Resultado para o jogo [PROPOSTA]
- A descida real é ~50% do ciclo, então a forma "asa" (descida rápida, subida lenta) não tem base biológica forte; ela ajuda a leitura (silhueta) mas cria impressão de "bater pesado". Uso recomendado: razão de descida (tempo) de 0,42 para dragão grande (subida levemente mais longa porque a dobra e o desdobrar tomam tempo), 0,45 para ave, 0,50 para inseto e morcego (seno puro).
- Atraso base-ponta: nos dados lidos não há número direto. Para articular, o atraso entre ossos adjacentes: [PROPOSTA] 2 a 4 quadros por osso a 30 qps em batida ~3 Hz (ou 20-40 graus de fase por osso, dependendo da frequência). Em inseto, 90 graus entre batida e torção. Em dragão grande, fase acumulada total 60-110 graus entre úmero e ponta do dedo-asa.
- Amplitude por osso [PROPOSTA]: ver tabela de regras.

---

## 8. Sintomas de asa feita por código e correção

| Sintoma | Causa | Correção [PROPOSTA salvo indicação] |
|---|---|---|
| Asa de porta (placa que gira em torno de um eixo) | 1 osso, 1 articulação, sem torção | >= 2 ossos; osso de ponta com atraso e ganho 0,4-0,7 (camada "seguir") |
| Asa sem dobra | subida simétrica à descida | na subida, dobrar B e C (morcego: envergadura 30-40% da descida, LIDO); adicionar pose-chave "tucked" |
| Corpo parado enquanto bate | só os ossos da asa animados | tronco sobe na descida (ou no fim dela) e desce na subida; amplitude 3-8% do tamanho do corpo; cabeça e cauda em contrafase 60-90 graus |
| Ponta chega junto com a base | fase zero entre ossos | defasar 20-40 graus por osso |
| Asa em leque / piscando | frequência > 15 Hz a 30 qps | ver 6.3 abaixo (leque translúcido) |
| Roda de carroça (asa parece girar ao contrário ou parada) | aliasing: ciclos por laço não inteiros, frequência perto de 30 Hz/N | número inteiro de ciclos por laço; evitar frequências entre 12 e 18 Hz; usar a regra de leque |
| Inseto com batida de pássaro | cotovelo em asa de inseto | só torção (pitch) na ponta; sem dobra |
| Libélula com 4 asas em fase | par traseiro igual ao dianteiro | par traseiro +90 graus (voo), +180 (pairar) [LIDO/RESUMO] |
| Dragão pairando sem esforço | só os 4 ossos e 1 Hz | dragão grande: batidas amplas, corpo sobe forte, cauda cai |

### 8.1 Como mostrar a 30 quadros (limite de Nyquist)
- 30 qps só representa até 15 Hz como "dois quadros por ciclo" (descida em 1 quadro, subida em 1 quadro) - isso já é um tremor. Para ler como batida, o ciclo precisa de >= 4 quadros (7,5 Hz) e idealmente >= 8 quadros (3,75 Hz). [PROPOSTA]
- Regra do jogo [PROPOSTA]:
  - f_real <= 7 Hz: usar a frequência real, ciclos inteiros por laço, 4 a 12 quadros por ciclo.
  - 7 Hz < f_real <= 15 Hz: **reduzir a frequência exibida** para 6-7,5 Hz (quase sempre mais bonito) e aumentar amplitude +10%. Não reproduzir a frequência real; a borboleta (12 Hz) e a donzelinha (16 Hz) caem aqui.
  - f_real > 15 Hz (libélula, esfinge, abelha, mosca): não animar a batida real. Mostrar (1) um leque translúcido (peça de asa em duas poses sobrepostas, alpha ~0,35) que cobre o arco de batida real; (2) tremor leve de 2 poses (quadros alternados A/B) com amplitude pequena (1/3), para que a asa pareça "borrada"; (3) opcional: alternar a cada 2-3 ciclos uma pose "congelada" mais legível (libélula em pairar). Sem Transparency em peças? usar Transparency=0.6 na peça "borrão" e opaca na peça do osso.
  - A fase entre pares de asas (libélula) deve ser mantida no leque.

---

## 9. REGRAS ACIONÁVEIS

Convenções: ângulos em graus, pivô em cada junta. "Amplitude" = pico a pico do osso quando o campo é "onda". "Descida/subida" é a razão do tempo de descida sobre o ciclo (0,5 = igual). "Atraso" é fase entre um osso e seu pai. "Qps" = quadros por segundo. Todos os números de campo são **[PROPOSTA]** ancorados nos dados citados (referência na última coluna do bloco abaixo).

| Tipo de asa | Ossos | Proporções (% do comprimento) | Juntas | Amplitude por osso (graus) | Razão desc./sub. | Atraso base-ponta | Frequência (visível) | Como mostrar a 30 qps | Reação do corpo |
|---|---|---|---|---|---|---|---|---|---|
| Dragão ocidental / asa de morcego | 4 (úmero, antebraço, metacarpo, dedo-asa) + 2-3 ripas de dedo | 15 / 25 / 15 / 45 (dedo >= 50 em pterossauro puro) | ombro na escápula (alto nas costas), cotovelo a 40% do vão, punho a 55% | A 70, B 45, C 30, D 25 | 0,45 (sub. mais longa por dobra) | 2-4 quadros/osso (fase 20-35 graus) | 2-4 Hz (grande); 5-7 (médio) | frequência real; dobra na subida (B e C fechando) | tronco sobe 0,5-1 voxel na descida; cabeça -6 graus em contrafase; cauda +10 graus em contrafase |
| Wyvern (asa = membro anterior) | 4 como acima | 15 / 25 / 20 / 40 | idem, mais pose de solo "apoiado em punho" | A 60, B 45, C 30, D 25 | 0,45 | idem | 3-5 Hz | idem + decolagem: subida curta, descida forte | corpo se projeta para frente (pitch -8 graus) na descida |
| Ave (águia, corvo) | 3 (úmero, antebraço, mão) | 30 / 30 / 40 (mão com primárias) | ombro, cotovelo (Z), punho | A 55, B 40, C 30 | 0,45 (pombo 0,45) | 2 quadros/osso | 2-5 Hz | frequência real; subida com B dobrado | corpo sobe na descida 0,5 voxel; cauda abre e compensa |
| Beija-flor / ave pequena | 2 (braço, mão) | 40 / 60 | ombro e punho (rotação em torno do eixo longo) | A 80, B torção 50 | 0,5 | 90 graus entre A e torção | real 12-99 Hz (grande a pequeno) | exibir 7 Hz + leque translúcido | corpo quase parado (hover), pitch 5 graus |
| Libélula / donzelinha | 2 pares x 2 ossos (base + lâmina) | base 20 / lâmina 80 | raiz fixa no tórax; lâmina torce | A 65 (dianteira) e 40-65 (traseira); lâmina 35 | 0,50 | fase traseira-frente 90 (voo), 180 (pairar), 0 (disparo); torção +90 | real 16-38 Hz | leque + tremor; 4 asas em 2 camadas | tórax levemente inclinado; abdome (cauda) balança em contrafase 10 |
| Borboleta | 2 pares acoplados x 2 ossos | dianteira 55 / traseira 45 do vão; lâmina 100 | raiz; torção leve | A 110, torção 25 | 0,50 | traseira segue dianteira (ganho 0,8, atraso 2 quadros) | real 12 Hz -> exibir 3-6 Hz | batida lenta e ampla; pose "palmas" no topo (1 quadro) | corpo sobe e desce 1-2 voxel; trajetória oscilante |
| Mariposa (esfinge) | 2 pares acoplados (gancho) x 1-2 ossos | idem | idem | A 90, torção 40 | 0,50 | traseira = dianteira (acopladas) | real 22-65 Hz | leque + tremor | corpo parado, pairar |
| Abelha / mosca / vespa | 1 par x 2 ossos (base + lâmina) + 2 halteres (mosca) | 25 / 75 | raiz, torção | A 90 (abelha, RESUMO) a 150 (mosca-da-fruta), torção 60 | 0,50 | torção +90 | real 100-250 Hz | leque translúcido fixo + tremor 2 poses (1/3 da amplitude); halteres em oposição de fase | corpo estável; vibra 0,1-0,2 voxel (zumbido visual) |
| Besouro | élitro (1 osso) + asa membranosa (2 ossos: base e ponta dobrável) | élitro 100 do abdômen; asa base 55 / ponta 45 | élitro: dobradiça na base; asa: dobra a 45% | élitro +70; asa A 70, ponta 30 | 0,50 | ponta após base 3 quadros | real ~38 Hz | pose "abrir -> liberar (48 graus) -> voar", batida em leque | corpo sobe, abdome em contrafase |
| Fada (asas de borboleta ou libélula) | 1-2 pares x 1-2 ossos | 60 / 40 (dianteira/traseira) | nasce entre omoplatas | A 50-70, torção 25 | 0,50 | traseira +2 quadros | exibido 6-10 Hz | frequência real | corpo balança 1 voxel; pernas e cabelo atrasam |

Fontes de ancoragem: razão de descida morcego 0,48-0,56 [LIDO]; envergadura de subida morcego 30-40% [LIDO]; pombo 0,45 [RESUMO]; pterossauro dedo-asa >= metade [LIDO]; libélula 61-66 graus, 77-102 graus fase [LIDO]; abelha ~90 graus/230 Hz [RESUMO]; besouro 48,5 graus de liberação [RESUMO]; halteres 180 graus fora de fase [LIDO]. O resto (ossos, %) é proposta.

Receita no motor (camadas):
- Onda: osso A seno ou "asa" (amp acima, ciclos/laço inteiro), osso B/C/D com "seguir" (ganho 0,7/0,6/0,5; atraso 2/4/6 quadros a 3 Hz) em vez de onda independente, para que a dobra emerja.
- Poses-chave: "repouso" (dobrado), "decolar" (abertura máxima), "planar" (asa quase reta, amplitude 8), "pouso".
- Corpo: osso do tronco com onda senoidal de mesma frequência, fase -10 a +30 graus em relação a A, amplitude 3-5 graus (pitch) e 0,5-1 voxel (altura); cabeça e cauda ossos em contrafase.

---

## 10. Glossário
- **Úmero**: osso do braço. **Rádio/ulna**: antebraço. **Carpo/punho**: articulação mão-antebraço. **Metacarpo**: ossos da palma. **Falange**: ossos dos dedos.
- **Patágio**: membrana de voo. **Propatágio**: frente do braço. **Plagiopatágio/braquiopatágio**: membrana principal do braço à perna. **Actinopatágio/tenopatágio**: zona distal com fibras / zona proximal. **Dactilopatágio**: entre dedos. **Uropatágio/cruropatágio**: entre as pernas.
- **Actinofibrilas**: fibras que enrijecem a membrana do pterossauro.
- **Pteroide**: osso do punho do pterossauro.
- **Primárias/secundárias**: penas de voo da mão / do antebraço.
- **Músculo de voo direto/indireto**: ligado à base da asa / ao tórax. **Síncrono/assíncrono**: uma contração por impulso / várias.
- **Clap and fling (Weis-Fogh)**: asas batem uma na outra e se abrem como livro.
- **Halteres**: asa posterior reduzida das moscas (giroscópio).
- **Élitros**: asas dianteiras endurecidas do besouro.
- **Pronação/supinação**: torção da asa em torno do eixo longo.
- **Razão de descida**: tempo de descida / ciclo. **Razão de envergadura**: vão na subida / vão na descida.
- **Plano de batida**: plano onde a ponta se move. **Defasagem**: diferença de fase em graus entre pares.
- **Nyquist**: máximo representável = metade da taxa de quadros (15 Hz a 30 qps).

---

## 11. Fontes (com status de leitura)

LIDAS (página aberta e extraída):
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3385481 - morcegos pteropodídeos: custo inercial, razão de descida, razão de envergadura (título completo não confirmado na extração)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3673148 - esfinges: frequências por espécie e massa
- https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2022.795063/full - libélula Pantala em subida (frequência, amplitude, fase)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2842671 - membrana de pterossauro (partes, fibras, repouso)
- https://en.wikipedia.org/wiki/Insect_flight - músculos, tabela de frequências, clap and fling (primeiros 100k caracteres)
- https://en.wikipedia.org/wiki/Bird_flight (primeiros 100k)
- https://en.wikipedia.org/wiki/Pterosaur (primeiros 100k)
- https://en.wikipedia.org/wiki/Pteranodon (primeiros 100k)
- https://en.wikipedia.org/wiki/Butterfly (primeiros 100k)
- https://en.wikipedia.org/wiki/Halteres
- https://en.wikipedia.org/wiki/Beetle (primeiros 100k)
- https://en.wikipedia.org/wiki/Fairy (primeiros 100k)
- https://en.wikipedia.org/wiki/Wyvern
- https://en.wikipedia.org/wiki/Bat_flight (pouco conteúdo útil)
- https://en.wikipedia.org/wiki/Hummingbird (primeiros 100k; seção de voo não alcançada)

SÓ RESUMO DA BUSCA (não abertas, ou PDF ilegível/503):
- https://engineering.purdue.edu/~xdeng/Dragonfly_journal.pdf (503 ao abrir) - fase de libélula
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3350744 e https://scholars.csus.edu/esploro/outputs/journalArticle/How-wing-kinematics-affect-power-requirements/99257876774301671 - efeito da dobra na potência (morcego)
- https://www.app.pan.pl/archive/published/app56/app20090145.pdf - pterossauro (PDF ilegível)
- https://arxiv.org/pdf/2407.18180 e https://ai.epfl.ch/flying-like-a-beetle - desdobramento passivo do besouro (arXiv ilegível; usei o resumo da busca)
- https://agris.fao.org/search/en/records/65df524f4c5aef494fe1b70b - abelha, amplitude curta/alta frequência (PNAS 2005)
- https://sponberg.gatech.edu/wp-content/uploads/2025/06/2025.05.07.652680.full_.pdf - batidas supra-ressonantes
- https://typeset.io/pdf/momentum-and-energy-in-the-wake-of-a-pigeon-columba-livia-in-4nt38b6vbe.pdf - pombo, razão de descida 0,45
- https://TVTropes.org/pmwiki/pmwiki.php/Main/OurDragonsAreDifferent e https://blackdrago.com/science/anatomy_west.htm - dragões (fontes de fãs, usadas só para convenção de design)
- https://cob.silverchair.com/jeb/article/210/10/1663/9473/Sailing-the-skies-the-improbable-aeronautical - pterossauros (só resumo)

---

## 12. Lacunas (o que não consegui obter)
1. Razões de comprimento úmero:antebraço:metacarpo:dedo para morcego e pterossauro (PDFs ilegíveis); as proporções da seção 2.3 são proposta.
2. Tempos de descida/subida e amplitudes de inseto (esfinge, abelha, borboleta) e frequências de morcegos/aves grandes por massa; "trajetória em 8" de insetos não confirmada.
3. Atraso de fase entre articulações (ombro-punho-ponta) de morcego/ave, que é o número que mais controla a "organicidade"; os 20-40 graus por osso são minha proposta e precisam de teste visual no jogo.
