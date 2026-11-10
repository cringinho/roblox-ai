# 05 - Caudas: anatomia, cinemática e regras para o gerador

Legenda de confiança usada em todo o documento:
- **[LIDO]** = abri a página e li o texto.
- **[RESUMO]** = só vi o resumo da busca (não abri a página).
- **[PROPOSTA]** = proposta minha, sem fonte; o raciocínio vem junto.
- Um PDF (Ringma & Salisbury 2014) foi aberto mas veio binário/ilegível: **NÃO lido**.

## 1. Veredito

1. Cauda real é uma cadeia longa (cerca de 20 a 50 vértebras) que se afina da base para a ponta; o gerador pode usar 4 a 8 ossos por cauda, agrupando vértebras. Isso é escolha de projeto, não dado biológico.
2. As fontes que li dão poucos números de animação. Os números de amplitude, atraso e frequência das regras abaixo são em grande parte PROPOSTA MINHA, ancorados em princípios qualitativos (onda viajante, amplitude crescente, atraso por junta).
3. Dados duros que consegui: contagens de vértebras (faixas), ankilossaurídeo (flexão 5-10° por junta, ~100° de varredura lateral total), guepardo (cauda 0,75 m, 0,66 kg, velocidade angular até 18 rad/s), crocodilo (frequência sobe com a velocidade, amplitude quase constante), escorpião (5 segmentos + télson).
4. Os erros típicos de cauda procedural (bastão, bloco, tudo em fase) se resolvem com três coisas: atraso de fase por osso, ganho crescente para a ponta e uma camada "seguir" com atraso que reaja ao corpo.
5. Maior lacuna: faltam medições abertas de atraso de fase e amplitude por segmento para cauda terrestre (gato, cão, lagarto). Veja lacunas no fim.

## 2. Anatomia real

| Animal | Vértebras caudais | Fonte / leitura |
|---|---|---|
| Cão | 20-23 | tabela veterinária citada em busca [RESUMO]. https://knowt.com/note/b234fc9d-7fcc-4340-8467-53c87fd21453/Vertebral-Formula |
| Gato | 18-23 (fontes divergem: 18-20, 20-23); menos em raças de cauda curta (Manx) | [RESUMO] mesma busca |
| Cavalo | 15-21 | [RESUMO] |
| Canguru-vermelho | 21 | [LIDO] https://carnegiemnh.org/what-is-in-a-tail/ |
| Mamíferos com cauda em geral | 2 a 49 | [LIDO] Carnegie |
| Pangolim-de-cauda-longa | 49 (maior entre mamíferos vivos), cauda preênsil | [LIDO] Carnegie |
| Humano (cóccix) | 3-5, reduzidas | [LIDO] Carnegie |
| Lagarto (geral) | 20 a 50+, muito variável | [RESUMO] |
| Crocodilo (monografia de 1915, espécie não especificada) | ~39 (total ~65-68 vértebras) | [RESUMO] https://www.miketaylor.org.uk/dino/out-of-copyright/Reese1915-the-alligator-and-its-allies-02-chapter-2-skeleton.pdf |
| Rato | NÃO ENCONTREI fonte | lacuna |
| Tyrannosaurus (espécime Sue) | 47 (pelo menos ~40 provável); fonte é wiki, fraca | [RESUMO] https://prehistoric-wiki.fandom.com/wiki/Tyrannosaurus |
| Allosaurus | contagem total não encontrada; sulco do músculo caudofemoral some entre as caudais 24 e 32 | [RESUMO] Cau & Serventi 2017, https://www.app.pan.pl/article/item/app003622017.html?pdf=39 |
| Anquilossaurídeo (Dyoplosaurus, ROM 784) | 11 caudais livres + 1 transicional + ~11 do "cabo" do clube (modelo com 13 segmentos) | [LIDO parcial, 100k de 145k caracteres] https://pmc.ncbi.nlm.nih.gov/articles/PMC2726940 |
| Anquilossaurídeos, cabo do clube | Pinacosaurus >=16; Euoplocephalus ~9-11 | [RESUMO] |
| Escorpião | metassoma de 5 segmentos + télson (vesícula + aculeus); Orkin conta 6 incluindo o télson | [RESUMO] Britannica, https://www.britannica.com/animal/scorpion/Ecology-and-habitats |

**Afilamento, musculatura, onde dobra.** O que tenho com fonte:
- Em terópodes, o músculo caudofemoral (motor da perna, preso à cauda) era muito grande; no T. rex os arcos hemais longos aumentavam sua massa. O músculo se concentra na base e some em direção à ponta (Allosaurus: some entre caudais 24-32). Isso implica base grossa e muscular, ponta fina. [RESUMO]
- Em anquilossaurídeos, a base da cauda dobra lateralmente (5-10° por junta, quase certamente <20°; modelo usa 15°), com pouca flexão vertical, e a ponta (cabo do clube) é rígida por processos entrelaçados e tendões ossificados. Ou seja: aqui a flexibilidade fica na BASE e a ponta é rígida. [LIDO]
- Em lagartos correndo, a coluna forma uma onda estacionária no tronco que vira onda viajante em direção à cauda. [RESUMO] https://www.nature.com/articles/s41598-020-64140-y (link do conjunto de resultados; não confirmei qual artigo traz a frase)
- Onde a cauda "dobra mais" em geral (base ou ponta): para caudas flexíveis, NÃO achei fonte numérica. PROPOSTA: a curvatura visível cresce para a ponta porque as vértebras ficam menores e mais numerosas por comprimento; o ângulo por junta tende a ser parecido, mas o deslocamento angular acumulado da ponta é maior.

## 3. Função

| Função | Animal | O que a fonte diz |
|---|---|---|
| Contrapeso / estabilização inercial | guepardo, canguru-rato, anolis, canguru | Cauda funciona como apêndice inercial; efeito aerodinâmico é pequeno em velocidade do guepardo. [LIDO] https://pmc.ncbi.nlm.nih.gov/articles/PMC8633431/ |
| Contrapeso | gato (saltos) | Contrabalança em saltos. [LIDO] Carnegie |
| Comunicação | cão | [LIDO] Carnegie |
| Mosca | vaca, cavalo | [LIDO] Carnegie |
| Preensão | macaco-aranha, pangolim | [LIDO] Carnegie |
| Propulsão | baleia, foca, morsa; crocodilo | [LIDO] Carnegie; crocodilo [RESUMO] |
| Arma | escorpião (golpe 66-130 cm/s conforme a espécie) | [RESUMO] https://britishecologicalsociety.org/press-sting-tail-high-speed-video-captures-death-stalker-scorpions-strike |
| Arma | anquilossaurídeo (clube) | [LIDO] PMC2726940 |

## 4. Cinemática com números

Dados com fonte:
- **Guepardo** (captura de movimento, 65 passadas): velocidade máx. 29 m/s; velocidade angular de pico da cauda até 18 rad/s (~1030°/s); cauda virtual 0,75 m e 0,66 kg. Na desaceleração a cauda sobe no plano sagital e depois sai do plano; o torque para trás coincide com a fase de só patas dianteiras apoiadas. [LIDO] PMC8633431
- **Canguru-rato:** em saltos altos a cauda balança para cima e por cima das costas para contrariar a rotação para trás do impulso; sem cauda, o bicho capota. Sem magnitudes. [LIDO]
- **Anolis:** cauda sobe na aceleração antes do salto e é mantida fixa no ar. [LIDO]
- **Robô-lagarto:** cauda ativa reduziu rotação em 72% frente à cauda fixa. [RESUMO] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8633431/ (resultado de busca)
- **Crocodilo-de-água-salgada juvenil (Seebacher et al. 2003):** a amplitude da batida não muda com a velocidade; a frequência sobe com a velocidade; amplitude relativa ao comprimento diminui com o tamanho. Números absolutos NÃO obtidos. [RESUMO] https://publish.csiro.au/zo/ZO02036
- **Nadadores ondulatórios em geral:** amplitude da cauda A ~ 0,2 L (L = comprimento do corpo), velocidade de onda = frequência x comprimento de onda. [RESUMO] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10492801/
- **Modelo de crocodilo biônico:** 0,7 Hz, 0,2 m, comprimento de onda 1,2 m dá 64% de eficiência. É modelo, não animal. [RESUMO]
- **Lagarto bípede (simulação):** aumentar ângulos de cintura e cauda alonga a passada e baixa a frequência de passos na mesma velocidade; a rotação da pelve é sincronizada com a marcha. [RESUMO] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7775063/
- **Lagarto com cauda restrita:** comprimento de passo cai. [RESUMO]
- **Anquilossaurídeo:** velocidade angular do clube 4,75-9,38 rad/s; varredura lateral total ~100°. [LIDO]
- **Escorpião:** golpes "abertos" (reto) atingem maior velocidade que "fechados". [RESUMO]

Relação cauda x passada (frequência): NÃO achei número publicado. PROPOSTA: para caudas que respondem à marcha (cão, lagarto), a cauda oscila em 1 ciclo por ciclo de passada completa (ou 2 por ciclo, se o osso vertical acompanha o quique de cada passo). Raciocínio: lagartos têm onda de coluna ligada ao ciclo de passada.

Contra-rotação: a cauda deve se mover em oposição ao que o corpo gira (conservação do momento angular, [LIDO] PMC8633431 mostra a cauda do guepardo torquando contra a rotação do corpo; os braços do biped simulado giram 180° fora de fase com o tronco). Regra: sinal do ganho da cauda é oposto ao da pelve/guinada.

## 5. Princípios de animação

Fontes: tutoriais de animação, nível de confiança moderado.
- Sucessão de quebra de juntas ("successive breaking"): junta 1 dobra, depois a 2, depois a 3. [LIDO] https://blog.animschool.edu/?p=645 (a página é curta e não traz números)
- Follow-through: a cauda continua depois que o corpo para, oscilando como um batente de porta. [LIDO] mesma página
- Atraso por nível da hierarquia: sugestão de 2-4 quadros a 24 fps, ou 1-2 a 60 fps (guia comunitário, "ponto de partida"). [RESUMO] https://playbooks.com/skills/dylantarre/animation-principles/follow-through-overlapping
- Atraso demais fica óbvio e atrapalha a ação principal. [RESUMO] https://brianlemay.com/Pages/animationschool/animation/lipsyncbook/followthrough.html
- Spring bones: parâmetros típicos são rigidez (volta à pose), arrasto/amortecimento (0 sem arrasto, 1 para) e gravidade; são configurados por grupo de ossos, não por osso individual. Nenhuma fonte diz que rigidez deva cair para a ponta. [RESUMO] https://wiki.virtualcast.jp/wiki/en/vrm/setting/spring
- Conversão: 2-4 quadros a 24 fps = 83-167 ms; a 30 fps isso é 2,5-5 quadros. Atraso por osso entre 0,04 e 0,08 s é coerente com isso. (Cálculo meu.)

## 6. Sintomas de cauda feita por código e correção

Estes são diagnósticos meus (PROPOSTA), baseados nos princípios acima.

| Sintoma | Causa provável | Correção |
|---|---|---|
| Cauda dura como bastão | poucos ossos, amplitude baixa, ou todos com o mesmo ângulo | >=5 ossos; ganho crescente para a ponta; ângulo por osso 8-20° |
| Cauda se move em bloco | todos os ossos com a mesma fase | fase por osso = i x (0,5 a 0,9 rad) |
| Todos em fase | idem; onda estacionária em vez de viajante | defasagem por osso somando 1/2 a 1 ciclo ao longo da cauda |
| Ponta parada, base mexe | ganho constante | ganho 0,4 na base, 1,0 na ponta |
| Cauda ignora o corpo | só camada onda, sem camada seguir | camada seguir copiando o osso do quadril com atraso crescente |
| Movimento robótico, regular | seno puro de uma só frequência | somar segundo harmônico pequeno (~15-25%) e 1 pose-chave por laço |
| Cauda atravessa o chão/corpo | amplitude vertical alta | limitar vertical a metade da lateral |
| Laço visível | ciclos fracionários | usar ciclos inteiros por laço |

## 7. Caudas de fantasia

- Dragões ocidentais: cauda geralmente mais longa que o corpo, base grossa e muscular afinando até a ponta; escamas grandes (escudos) ao longo da cauda; ancoragem tipo dinossauro no quadril. [RESUMO] https://design.tutsplus.com/articles/rawr-how-to-draw-an-anatomically-correct-dragon--vector-16561 (fonte de tutorial, qualidade média)
- Dragões orientais: movimento de enguia/serpente, mais ondulatório; ocidentais, caudas mais rígidas e com espinhos. [RESUMO]
- Emoção pela cauda: balanço suave = nobreza; chicoteada com farpas = agressão. [RESUMO] (fonte fraca)
- Cauda como clava: copiar o anquilossaurídeo. Base flexível (12 segmentos livres, 5-15° cada), cabo rígido (um osso só ou dois, sem onda) e massa pesada na ponta. A massa na ponta dá inércia: usar atraso MAIOR e amplitude MENOR na clava. [LIDO] PMC2726940 para o desenho; a leitura de atraso/amplitude é PROPOSTA.
- Cauda com ferrão: copiar o escorpião. 5 segmentos grossos e curtos + télson curvo; repouso enrolado sobre o dorso; golpe aberto e rápido (fonte: 66-130 cm/s). [RESUMO]
- Cauda com lâmina (arraia, wyvern): PROPOSTA: tratar como a de ferrão, mas reta e rígida na ponta (último osso com ganho 0 na onda).
- Wyvern: as asas servem de membros dianteiros, o que altera a relação cauda x corpo. [RESUMO]

## 8. REGRAS ACIONÁVEIS

Convenções: osso 1 = base. "Prop." = proposta minha (sem fonte direta); o raciocínio está em 2-6. Amplitude = pico do seno em graus ao redor do repouso, no eixo lateral (guinada); vertical = ~0,4x lateral salvo indicação. Atraso de fase por osso em fração de ciclo. Frequência em ciclos por segundo, assumindo laço de 1,0 a 2,0 s.

| Tipo | Nº de ossos | Proporções (comprimento por osso / espessura) | Amplitude por osso (graus) | Atraso de fase | Frequência | Repouso | Reação ao corpo |
|---|---|---|---|---|---|---|---|
| Cauda de mamífero comprida (cão, gato, lobo) | 5-6 (real 18-23 vértebras, agrupadas) | comprimentos iguais, ou 1,0 a 0,8 do 1º ao último; espessura 100% -> 35% linear. Cauda total ~0,6-1,0x comprimento do tronco (prop.) | 6, 9, 13, 17, 20, 22 (cresce; ganho base 0,3 -> ponta 1,0) | 0,08-0,12 de ciclo por osso (onda viajante) | 0,5-1 Hz parada; 1 ciclo por passada em andar/corrida | pendente 20-40° abaixo da horizontal (cão), ponta curva para cima 10° (prop.) | seguir: copia a guinada do quadril com atraso 0,05 s por osso, ganho -0,5 (contra-rotação); sobe no salto/aceleração, desce na freada |
| Cauda de lagarto / réptil terrestre | 6-8 | comprimento total ~1,0-1,5x tronco (prop.); espessura 100% -> 20%; ossos ligeiramente mais longos na ponta | 5, 8, 12, 16, 20, 24, 26, 28 | 0,10-0,14 por osso; onda estacionária no tronco virando viajante na cauda (fonte qualitativa) | 1 ciclo por passada | rente ao chão, apoiada em curva suave de 10° | guinada do tronco em fase com a cauda atrasada; ao correr, cauda levantada |
| Cauda de crocodilo / propulsão aquática | 6-8 | corpo + cauda ~50% do comprimento total (prop.); comprimento por osso igual; espessura 100% -> 25%, achatada lateralmente | amplitude do último osso até 0,2 L de deslocamento (fonte geral); por osso 4, 7, 11, 15, 19, 23 | comprimento de onda ~1 corpo => 1/N de ciclo por osso (N ossos); ~0,12-0,17 | frequência sobe com a velocidade, amplitude fica quase constante (Seebacher) | reta, alinhada ao eixo do corpo | ao nadar a onda começa no tronco; em terra, balanço menor (30%) |
| Cauda de terópode / balanço de dinossauro | 6-8 | longa e grossa na base, afina até 15%; cauda ~1,0x tronco+pescoço (prop.); base com arco hemal alto | mais rígida: 3, 4, 6, 8, 10, 12 (lateral); vertical quase 0 | 0,06-0,08 por osso; quase em fase na base | 1 ciclo por passada, 0,6-1,2 Hz | quase horizontal, equilibrando o tronco (contrapeso do pescoço) | contra-rotação ao quadril; o peso da base resiste (amplitude pequena na base) |
| Cauda de contrapeso de salto / guepardo, canguru, canguru-rato | 4-6 | espessa na base (100% -> 30%); comprimento ~0,8-1,2x tronco | grande na base e média na ponta; varredura total até 60-90° (prop.) em manobras | pequeno, 0,03-0,06 por osso (a cauda gira quase como corpo único para dar torque inercial) | evento (não cíclico): 1 volta rápida na decolagem ou freada | 10-20° sobre a horizontal | gira em direção oposta à rotação do corpo; sobe na desaceleração (guepardo) |
| Cauda preênsil (macaco, pangolim) | 6-8 | afina 100% -> 40%, ossos curtos e finos para enrolar | curva até 35-40° por osso no enrolar; sem onda | atraso 0,05-0,08 em transição | baixo, 0,3 Hz | enrolada em espiral na ponta, ou pendente | segue o osso do quadril lentamente |
| Cauda de escorpião (ferrão) | 5 + télson (6) | segmentos curtos, grossos, quase iguais (1,0 a 0,85); télson bulboso + aculeus curvo | repouso curvado 20-30° por segmento sobre o dorso; golpe: sequência 40°, 30°, 30°, 20°, 20° | golpe aberto e rápido: 0,02-0,04 s por osso (prop.), seguinte à pose-chave de golpe | 0,3 Hz parada; golpe evento ~0,4-0,6 s (fonte: 66-130 cm/s) | arqueada sobre o dorso, ponta apontando à frente | ao golpear, o corpo recua 5° e o ferrão aponta ao alvo |
| Cauda com clava (anquilossauro) | 8-10 livres + 2 rígidas (cabo) + clava | livres: ossos iguais, 100% -> 70%; cabo rígido (1-2 ossos sem onda); clava com espessura 300-400% do cabo | livres: 5-10° por osso (fonte), total ~100°; cabo 0 | 0,02-0,04 por osso (golpe quase simultâneo, a inércia da clava atrasa) | golpe evento 0,5-0,8 s; parada: quase imóvel | horizontal, em linha com o corpo | golpe é guiado pela guinada do quadril com atraso |
| Cauda de dragão / serpente | 8-12 | comprimento 1,0-1,6x corpo (prop.); 100% -> 10% | 5 até 30 (crescendo); soma total >120° | 0,08-0,10 por osso (comprimento de onda ~1 cauda) | 0,4-0,8 Hz; 1 ciclo por 2 passos em voo/caminhada | baixa, ponta levemente erguida | contra-rotação ao quadril; em voo atua de leme (ganho +) |
| Cauda de lâmina / arraia | 4-6 | fina e longa, 100% -> 15%, lâmina rígida na ponta | 5, 8, 12, 18; lâmina 0 | 0,10 por osso | 0,5 Hz | reta para trás | chicoteia no golpe com pose-chave |

Todos os valores de amplitude, atraso e frequência acima são PROPOSTA MINHA, exceto os explicitamente atribuídos (anquilossaurídeo 5-10° por junta; ~100° total; amplitude do nadador ~0,2 L; frequência sobe com a velocidade no crocodilo; guepardo até 18 rad/s). Valide visualmente antes de fixar.

Como mapear para as camadas do gerador:
- **onda:** amplitude por osso da tabela; fase_i = (i-1) x atraso x 2pi; ganho_i = 0,3 + 0,7 x (i-1)/(N-1) em caudas flexíveis.
- **seguir:** o osso 1 copia a guinada/arfagem do quadril com atraso 0,03-0,06 s e ganho -0,3 a -0,6; cada osso seguinte copia o anterior com atraso +0,03-0,05 s e ganho 0,8 (cadeia de decaimento; equivalente a spring bone).
- **pose-chave:** golpe (ferrão, clava, lâmina), salto (contrapeso sobe), freada (sobe), e repouso.
- **laço:** ciclos inteiros por laço; frequência em Hz = ciclos / duração do laço.

## 9. Glossário

- **Caudal:** da região da cauda. **Hemal arch (arco hemal):** osso em V sob as vértebras caudais, ancora músculo.
- **Caudofemoral:** músculo da cauda ao fêmur; motor principal da perna em répteis e terópodes.
- **Metassoma:** "cauda" do escorpião (5 segmentos). **Télson:** último segmento com o ferrão. **Aculeus:** a agulha do ferrão.
- **Cabo e clava (handle/knob):** parte rígida e parte pesada da cauda do anquilossaurídeo.
- **Onda viajante:** a curvatura caminha da base para a ponta; **onda estacionária:** nós fixos, tudo em fase ou antifase.
- **Follow-through / overlapping action:** partes secundárias continuam e atrasam em relação ao movimento principal.
- **Spring bone / jiggle bone:** osso simulado por mola e amortecedor. **Contra-rotação:** cauda gira ao contrário do corpo para conservar momento angular.
- **Apêndice inercial:** parte que muda a rotação do corpo por troca de momento angular.

## 10. Lacunas desta pesquisa

1. Não achei medidas publicadas de atraso de fase e amplitude por segmento em cauda terrestre (cão, gato, lagarto): os valores dessas colunas são propostas.
2. Contagem de vértebras do rato e de terópodes (exceto Sue) sem fonte forte; crocodilo só em monografia de 1915 lida só pelo resumo da busca.
3. Números de crocodilo (Hz, amplitude em comprimentos de corpo) estão no artigo de Seebacher et al. 2003, que não consegui abrir; o PDF de Ringma & Salisbury veio ilegível.

## 11. Fontes (URL)

Lidas (abri a página):
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8633431/ (Tails, Flails, and Sails; li 100k de 107k caracteres)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2726940 (cauda de anquilossaurídeo; li 100k de 145k)
- https://carnegiemnh.org/what-is-in-a-tail/
- https://blog.animschool.edu/?p=645 (pouco conteúdo útil)

Só resumo da busca (não abri):
- https://knowt.com/note/b234fc9d-7fcc-4340-8467-53c87fd21453/Vertebral-Formula
- https://www.miketaylor.org.uk/dino/out-of-copyright/Reese1915-the-alligator-and-its-allies-02-chapter-2-skeleton.pdf
- https://prehistoric-wiki.fandom.com/wiki/Tyrannosaurus
- https://www.app.pan.pl/article/item/app003622017.html?pdf=39
- https://publish.csiro.au/zo/ZO02036
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10492801/
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7775063/
- https://www.nature.com/articles/s41598-020-64140-y
- https://www.britannica.com/animal/scorpion/Ecology-and-habitats
- https://britishecologicalsociety.org/press-sting-tail-high-speed-video-captures-death-stalker-scorpions-strike
- https://playbooks.com/skills/dylantarre/animation-principles/follow-through-overlapping
- https://brianlemay.com/Pages/animationschool/animation/lipsyncbook/followthrough.html
- https://wiki.virtualcast.jp/wiki/en/vrm/setting/spring
- https://design.tutsplus.com/articles/rawr-how-to-draw-an-anatomically-correct-dragon--vector-16561

Não lido (PDF ilegível): https://dinosaurs.group.uq.edu.au/files/2245/Ringma_Salisbury_2014%20%281%29.pdf
