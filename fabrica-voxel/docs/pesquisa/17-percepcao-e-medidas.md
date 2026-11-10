# 17 - Percepção de movimento e medidas automáticas de naturalidade

Data da pesquisa: 2026-11-10.

Legenda: **[LIDO]** abri a página/arquivo e li o trecho. **[RESUMO]** só resumo de busca, sem abrir o texto completo. **[PROPOSTA]** dedução minha, sem fonte direta.

Aviso: várias páginas primárias não abriram (ver seção f). Onde faltou fonte, não há número inventado. O que é limiar inicial é [PROPOSTA] e precisa de calibração com criaturas reais da fábrica.

---

## (a) Veredito em 5 linhas

1. O olho lê "vivo" principalmente pelo movimento local dos pés (aceleração vertical sob gravidade) e pela fase coerente entre membros. [LIDO: Troje & Chang 2023]
2. O defeito mais barato de medir e mais fácil de ver é o pé deslizando: já aparece abaixo de ~21 mm. [RESUMO: Pražák et al. 2011]
3. Movimento "morto" é: velocidade constante, tudo em fase, esquerda e direita espelho exato, ruído branco, sem subir e descer de massa. [PROPOSTA apoiada em Williams, LIDO, e em 1/f, RESUMO]
4. Dá para medir tudo isso só com trilhas: suavidade (SPARC/jerk), correlação cruzada de fase, razão de apoio, frequência de passada por tamanho, espectro do ruído.
5. Em 30 fps, "twos" (15 fps) é escolha de estilo, não correção de defeito. Use só se o estilo pedir; nunca para esconder deslize.

---

## 1. Percepção de movimento biológico

**1.1 Pés são o detector de vida.** Em pontos de luz (point-light), caminhante embaralhado ainda mostra a direção quando está de pé, mas não de cabeça para baixo. Como embaralhar destrói a configuração do corpo, o efeito vem do movimento local dos pés. Troje & Westhoff (2006) propuseram um "detector de vida". [LIDO: PMC9975895, Troje & Chang 2023]

**1.2 A pista é o "roda rolando".** Pés em sentido horário ao longo da trajetória leem como andar para a direita; anti-horário, para a esquerda. [LIDO: PMC9975895]

**1.3 Gravidade e aceleração.** A pista só funciona com movimento vertical que acelera e desacelera de acordo com a gravidade. O texto diz que só a aceleração para baixo valida a pista, não a para cima. Invertido, perde o sentido. [LIDO: PMC9975895] Chang & Troje (2009) apontaram a aceleração vertical dos pés como o sinal. [RESUMO: página do laboratório yorku.ca]

**1.4 Animacy.** A sensibilidade à direção por movimento dos pés se correlacionou com o quanto os observadores achavam o estímulo animado. [LIDO: PMC9975895]

**1.5 Inato e periférico.** Recém-nascidos e pintinhos respondem a movimento tipo passo; a visão periférica também. Cerca de 50% da variação entre pessoas no processamento de movimento local é genética. [LIDO: PMC9975895]

**1.6 Ressalvas.** O sinal local dos pés não é totalmente independente da configuração global (Saunders, Suchan & Troje 2009). A interpretação "detector de vida" é debatida. [RESUMO]

**1.7 Ordem de importância (para a fábrica).** [PROPOSTA]
1. Pé: trajetória em arco, subida e queda com aceleração tipo gravidade, contato com parada clara.
2. Fase entre membros: pés em contra-fase (~0,5 do ciclo em bípedes), braços contra pernas; onda atrasada na coluna e cauda.
3. Periodicidade: ciclo regular, mas com pequena variação ciclo a ciclo (ver seção 5).
Não achei estudo que ordene esses três fatores. A ordem acima é dedução.

---

## 2. Defeitos que o olho vê primeiro

| Defeito | O que se sabe | Marca |
|---|---|---|
| Pé deslizando | Pessoas percebem deslize pequeno: "<21 mm na maioria das condições". Animações corrigidas foram sempre preferidas às com deslize. Encurtar/alongar membros foi preferido a IK complexo com suavização de trajetória. | [RESUMO] Pražák, Hoyet, O'Sullivan, SCA 2011 (abstract via busca; página 403/redirect) |
| Pé deslizando e câmera | Estudo separado "Perceptual thresholds for foot slipping in animated characters" usa método clássico de limiar e relata que movimento simples de câmera pode subir o limiar. Valor numérico não obtido. | [RESUMO] core.ac.uk (403) |
| Limiar em % da passada | Não encontrei. | não confirmado |
| Deslize como produto de edição | Kovar et al. 2002 corrige restrições de apoio com mudanças suaves, permitindo pequena variação do comprimento da perna. Não traz teste perceptual. | [RESUMO] |
| Suavidade humana | McDonnell, Newell, O'Sullivan 2007: taxa de ciclo, velocidade linear, complexidade do movimento e tamanho do grupo afetam o limiar de suavidade aceitável. | [RESUMO] |
| Anomalias de física | O'Sullivan et al. 2003: limiares de sensibilidade a distorções angulares, de momento e espaço-tempo. | [RESUMO] |
| Estalos (pops) | Sem estudo perceptual direto achado. | não confirmado |
| Peso ausente | Williams: andar rotoscopiado com precisão "flutua"; é preciso exagerar o sobe-e-desce. "É a posição para cima e para baixo das massas que dá a sensação de peso." Peso entra logo depois do contato e sai logo depois da passagem. | [LIDO] Animator's Survival Kit (texto extraído do PDF) |
| Movimento linear / sem peso | Williams: peso não vem de movimento liso e nivelado. | [LIDO] |
| Tudo em sincronia | Williams: "as coisas não começam nem terminam ao mesmo tempo"; partes do corpo se sobrepõem (overlapping). | [LIDO] |
| Passo repetido igual | Williams pede mudar levemente a silhueta para "não parecer um passo repetindo". | [LIDO] |
| Simetria perfeita | Sem estudo perceptual achado. Dedução: ritmo e fase perfeitamente idênticos entre lados lembram máquina. | [PROPOSTA] |
| Repetição do laço (idle) | Não achei estudo que diga em quantos segundos o olho nota a repetição. | não confirmado |

---

## 3. Métricas quantitativas

**3.1 Mínimo jerk (Flash & Hogan 1985).** Movimento voluntário de alcance tende a minimizar a integral do jerk ao quadrado. Não abri o artigo original. Há debate: Viviani & Flash (1995) concluíram que a relação velocidade-curvatura não decorre do mínimo jerk. [RESUMO]

**3.2 Lei da potência (dois-terços).** Viviani & Terzuolo (1982); Lacquaniti et al. (1983). Velocidade angular proporcional à curvatura^(2/3), ou velocidade tangencial v = K·κ^(-1/3). Vale para traços de mão (desenho, escrita); não está provada para pés ou criaturas. [RESUMO] Uso na fábrica: só como checagem fraca de pontas de membros em trajetória curva. [PROPOSTA]

**3.3 Jerk adimensional.** [LIDO: monalysa]
DJ = -(T^5 / V^2) · ∫ ||d²v/dt²||² dt, com T = duração, V = velocidade de pico. LDLJ = -ln(valor positivo). Mais negativo = menos suave. Aqui "v" é a velocidade; a integral é do jerk ao quadrado.

**3.4 SPARC (Balasubramanian et al. 2012/2015).** [LIDO: fórmula em monalysa; contexto em RESUMO]
SPARC = -∫₀^ωc sqrt( (1/ωc)² + (dV̂/dω)² ) dω, onde V̂(ω) = V(ω)/V(0) é o espectro de magnitude da velocidade normalizado. ωc vem de um teto máximo e de um limiar de amplitude. Mais negativo = menos suave. A página lida não dá valores recomendados de corte; a busca cita faixa de 0 a 20 Hz e limiar 0,05 como exemplo gráfico, o que não é recomendação. Resumo de busca: SPARC é menos sensível a ruído de medida que LDLJ. [RESUMO]
Dependência de segmentação: o valor depende de onde se corta o movimento. [RESUMO]

**3.5 Razão de apoio (duty factor) e Froude.** Froude Fr = v²/(g·L), L = comprimento da perna; duty factor = fração do ciclo com o pé no chão. Animais em mesmo Fr têm movimento dinamicamente semelhante (mesmo comprimento relativo de passada e duty factor, Alexander & Jayes). Duty factor < 0,5 implica fase aérea. Humanos trocam de andar para correr perto de Fr ≈ 0,5. [RESUMO: busca; o PDF sfu.ca não abriu]
Cálculo meu: Fr = 0,5, L = 1 m, g = 9,81 dá v ≈ 2,2 m/s. [PROPOSTA]
Não obtive tabela duty factor por Fr; usarei valores de projeto (seção c) marcados como PROPOSTA.

**3.6 Frequência de passada por tamanho.** Heglund & Taylor 1988 (J. Exp. Biol. 138:301):
- Trote preferido: f ≈ 3,35 · M^(-0,130) (M em kg; unidade de f não declarada na página; provavelmente Hz). [LIDO]
- Transição trote-galope: f cai com M^(-0,150), sem coeficiente na página. [LIDO]
- Velocidade de trote preferida ≈ 1,09 · M^0,222 m/s. [LIDO]
- Mesma conclusão no resumo de busca: expoente −0,15 nas velocidades equivalentes. [RESUMO]
Uso: criatura maior = passada mais lenta. Regra "f ∝ massa^-0,14" do enunciado cai entre −0,13 e −0,15, coerente. Escala por comprimento de perna (f ∝ L^-0,5 por pêndulo) é [PROPOSTA]; não verifiquei fonte.

**3.7 Respiração por massa.** Stahl (1966): f = 0,89 · M^(-0,26) Hz (M em kg). A teoria dá −0,25. Reanálise de 2025 dá −0,303 para mamíferos terrestres. [RESUMO]
Exemplo calculado por mim com Stahl: M = 70 kg dá ~0,29 Hz (~17 resp/min); M = 0,03 kg dá ~2,2 Hz; M = 5000 kg dá ~0,098 Hz (~6 resp/min). [PROPOSTA - aritmética sobre fórmula RESUMO]

**3.8 Piscadas.** Adulto em repouso ~15-20 por minuto (Tsubota et al. 1996, via Frontiers); outro estudo: 19/min mulheres e 11/min homens; lendo cai para 4-5/min. [RESUMO] Piscada em animação: intervalo irregular de ~3-6 s. [PROPOSTA derivada]

**3.9 Fase-atraso em cadeias (ondas viajantes).** Não achei limiar perceptual. Williams descreve sobreposição e arrasto como princípio. [LIDO, qualitativo] A medida (atraso do pico ao longo da cadeia, correlação cruzada) é [PROPOSTA].

---

## 4. Tempo de animação por porte

Fontes lidas: Animator's Survival Kit, texto extraído do PDF (Internet Archive). Frames do livro são a 24 fps; converto a 30 fps por regra de três, o que é [PROPOSTA].

**Fatos lidos (24 fps):**
- Meio segundo = 12 quadros ("tempo de marcha"). Um pé = 16 quadros = 2/3 s. [LIDO]
- Exemplo de personagem que anda: passos lentos de 16 quadros, mais rápidos de 14 e 12. [LIDO]
- Variantes de passo: média 24 quadros por passo; rápida 16 quadros; outra 22 quadros; furtiva 10 a 14. [LIDO, leitura de OCR ruidoso, confiança média]
- "Take" (susto) de 8 quadros: cabeça sobe em 3 quadros, depois "cushion back" e segura. [LIDO]
- Regra de twos: twos para ações normais, ones para ações muito rápidas; corridas sempre em ones; "andar funciona bem em twos, mas fica melhor em ones". [LIDO]
- Ação ampla e rápida em twos "brilha"; ones mecânicos matam a vitalidade. Mas Williams diz que, se se planeja para ones, o resultado costuma ser superior. [LIDO]
- Câmera panorâmica em ones sobre personagem em twos causa tremor estroboscópico: panoramizar também em twos. [LIDO]
- Tytla: só há três coisas em animação: antecipação, ação e reação. [LIDO]
- Moving hold: resumo de busca diz que mantém movimento sutil no corpo enquanto expressa a pose. [RESUMO: anim.works] Não achei a frase no livro.

**Não encontrei** tabelas de quadros de antecipação/golpe/recuperação por porte em fonte primária, nem dados de Monster Hunter. Os números abaixo são [PROPOSTA] de partida, a calibrar. Lógica: tempo de ação cresce com a raiz do comprimento (pêndulo, t ∝ sqrt(L/g)); antecipação e recuperação são mais longas que o golpe; criatura grande segura mais.

### (d) Tabela de tempos em quadros a 30 fps [PROPOSTA]

| Porte | Altura típica | Antecipação | Golpe | Recuperação | Hold na pose-chave | Ciclo de andar (2 passos) | Respiração idle (período) |
|---|---|---|---|---|---|---|---|
| Pequena | 0,3-0,8 m | 3-5 | 2-3 | 5-8 | 1-2 | 12-18 | 0,6-1,2 s (18-36 q) |
| Média | 1-2 m | 6-10 | 3-5 | 9-14 | 2-4 | 24-36 | 2-3 s (60-90 q) |
| Grande | 3-5 m | 10-16 | 4-7 | 16-24 | 4-8 | 42-60 | 3-5 s (90-150 q) |
| Colossal | 8 m ou mais | 18-30 | 6-10 | 30-48 | 8-14 | 72-108 | 5-8 s (150-240 q) |

Notas: ciclo de andar usa f do trote Heglund (3,35·M^-0,13) como ordem de grandeza e raiz do comprimento; respiração usa Stahl. A fábrica deve preferir derivar de massa/perna a usar a tabela fixa.

---

## 5. Ruído

**5.1 1/f em movimento humano.** Flutuações de variabilidade saudável têm espectro ~1/f (ruído rosa); marcha patológica de idosos perde essa escala; postura em pé (centro de pressão) lembra 1/f; atividade humana segue 1/f acima da frequência circadiana (Sci. Rep. 2024). [RESUMO]

**5.2 Perlin.** Cinemachine (Unity) descreve Perlin como "movimento pseudoaleatório de comportamento natural". Patente de câmera usa 6 oitavas em 1D por eixo, com amplitude e frequência ligadas à velocidade. Perlin não é rosa por definição; o espectro depende de oitavas e persistência. [RESUMO]

**5.3 Por que branco parece tremor.** Ruído branco muda de um quadro para o outro com igual energia em todas as frequências; adjacentes não se parecem. Perlin/1/f têm valores vizinhos semelhantes (transição suave). [RESUMO para o segundo; o primeiro é propriedade matemática, PROPOSTA]

**5.4 Amplitudes de idle.** Não achei números de fonte. Valores de projeto [PROPOSTA]: balanço de tronco 0,2-0,6° de rotação; cabeça 0,3-1°; respiração do peito 0,3-0,8% do comprimento do tronco; deriva de peso 0,5-1,5% da altura. Frequência dominante abaixo de ~2 Hz, com 1/f.

**5.5 Lacuna.** Nenhum estudo achado testa se idle 1/f é percebido como mais natural que branco ou Perlin em personagem. Só há evidência de variabilidade biológica 1/f em dados humanos.

---

## 6. Taxa de quadros

**6.1 30 fps assado, interpolado no motor.** Não achei fonte sobre perda. Dedução [PROPOSTA]: amostrar a 30 Hz e interpolar linear/slerp entre chaves de 30 Hz perde conteúdo acima de 15 Hz (Nyquist); movimentos rápidos (golpe de 2-3 quadros) ficam suavizados. Interpolação de rotação linear entre quadros subestima giro rápido. Motor a 60 Hz entre chaves de 30 Hz repete ou interpola: se interpola, aparece leve borrão de movimento, aceitável.

**6.2 Twos / stepped.**
- Williams: twos para ação normal, ones para muito rápido; aparência "brilha" em ação ampla em twos. [LIDO]
- Spider-Verse: twos como escolha estilística para dar leitura de quadro desenhado, em performance; câmera frequentemente em ones; cabelo/pano simulados em ones, senão "pulam"; alterna ones/twos por plano; Miles em twos contrastando com Peter fluido. [RESUMO: Imageworks via Creative Bloq/AWN, fxguide etc.]
- Guilty Gear Xrd: equipe cortou quadros de propósito para imitar sprites 2D; sem interpolação entre quadros. Valor "15 fps" não confirmado. [RESUMO] Palestra de Motomura (GDC 2015) existe, não abri.
- Dead Cells: não pesquisado (sem fonte).
- Quando ajuda [PROPOSTA]: estilo voxel/stop-motion, ações curtas e fortes (golpes), quando se quer legibilidade de poses. Quando prejudica: andar contínuo e câmera em ones (tremor estroboscópico, Williams, LIDO), e qualquer coisa que dependa de aceleração suave do pé (1.3).
- Regra prática: se a fábrica usar twos, aplicar em todas as camadas esqueléticas do mesmo personagem e nunca nas molas de cauda/pano.

---

## (c) TABELA FINAL: medidas automáticas

Convenções [PROPOSTA]: q = quadro a 30 fps; T = período do ciclo; v(t) = velocidade escalar do osso; ω = velocidade angular; "ponta" = osso terminal do membro; contato = pé com y abaixo de limiar e velocidade horizontal baixa. Todos os limiares iniciais são PROPOSTA, exceto onde dito.

| # | Medida | Como calcular com as trilhas | Limiar inicial | O que o conserto deve dizer |
|---|---|---|---|---|
| 1 | Deslize do pé no apoio | Em cada janela de contato, desvio horizontal máximo da posição mundial do pé; dividir pela altura da perna. | Falha > 0,02 m escalado à humana (~1,5% do comprimento de perna); aviso > 0,01 m. Âncora: percebem <21 mm [RESUMO]. | "Pé desliza X cm no passo N: reduzir velocidade do tronco ou alongar a passada para casar com a velocidade de deslocamento." |
| 2 | Aceleração vertical do pé em balanço | Segunda derivada de y da ponta; razão pico de descida / pico de subida; presença de desaceleração antes do contato. | Existe pico de subida e queda com assimetria (queda mais aguda) ; falha se y(t) é rampa constante (R² linear > 0,98). Fundamento: pista de gravidade [LIDO]. | "Pé sobe e desce em rampa: usar arco com aceleração (parábola), toque com parada curta." |
| 3 | Fase entre pés (bípede/quadrúpede) | Correlação cruzada ou ângulo de fase entre y (ou ângulo da coxa) de esquerdo e direito. | Andar alternado: fase 0,5 ± 0,08 do ciclo. Falha se < 0,35 ou > 0,65 sem ser salto proposital. | "Pernas fora de contra-fase: atrasar o lado direito meio ciclo." |
| 4 | Duty factor por velocidade | Fração do ciclo com contato / velocidade em Fr = v²/(gL). | Andar: duty ≥ 0,5; correr: < 0,5; transição perto de Fr 0,5 [RESUMO]. Falha se duty < 0,5 com Fr < 0,3 ou duty > 0,6 com Fr > 1. | "Tempo de apoio incompatível com a velocidade: aumentar/diminuir o apoio ou a velocidade." |
| 5 | Frequência de passada vs. massa | Contar ciclos por segundo; comparar com f_alvo = 3,35·M^(-0,13) como ordem de grandeza [LIDO] ajustada à escala voxel. | Dentro de 0,6x a 1,6x de f_alvo; fora = falha. | "Criatura grande passa rápido demais: reduzir frequência, aumentar apoio e hold." |
| 6 | Suavidade (SPARC e LDLJ) | Velocidade escalar por osso; SPARC no espectro de v; LDLJ por segmento entre contatos. | Comparar com baseline da própria criatura; marcar osso se SPARC cair > 30% abaixo da mediana do conjunto. Limiar absoluto: não há fonte; calibrar. | "Osso X tem energia em alta frequência: suavizar a curva ou remover chave extra." |
| 7 | Pop / estalo | Pico de jerk (3ª derivada) por osso > k·MAD; ou aceleração angular de 1 quadro > 6x mediana. | Falha se jerk de pico > 8x mediana em osso que não é golpe/impacto marcado. | "Estalo no quadro N, osso X: inserir chave intermediária ou limitar mudança angular." |
| 8 | Velocidade constante / linearidade | Por segmento entre poses-chave: variância de v / v médio; ou R² de rotação linear no tempo. | Falha se coeficiente de variação de v < 0,10 em segmento > 6 q, sem ser rotação contínua (roda, hélice). | "Movimento linear: aplicar ease-in/out ou overshoot." |
| 9 | Atraso em cadeia (onda viajante) | Para cadeias (coluna, cauda): atraso do pico de ω entre ossos vizinhos por correlação cruzada; monotonicidade. | Atraso por elo ≥ 1 q e ≤ 0,15·T; monotônico; falha se todos os atrasos < 0,5 q (tudo em sincronia). | "Cauda gira junto com o corpo: acrescentar 2-4 quadros de atraso por segmento, com amortecimento." |
| 10 | Simetria exata esquerda/direita | Já existe espelho perfeito. Acrescentar: diferença de fase (medida 3) e de amplitude entre lados em movimento. | Falha se |amplitude E-D|/amplitude < 0,02 E fase exata 0,5 E ruído idêntico. Esperado 3-10% de diferença. | "Lados idênticos: variar amplitude 3-8% e fase 0,02-0,05 ciclos entre lados." |
| 11 | Variação ciclo-a-ciclo / repetição do laço | Compara ciclos consecutivos de uma variável (ex.: pico de y do pé); coeficiente de variação; autocorrelação de espectro. | Para laços > 2 s: CV de amplitude de pico entre 2% e 8%. Falha se 0% ou > 15%. Janela de repetição visível: sem fonte. | "Laço exato demais: sobrepor camada de idle com período não múltiplo (ex.: 1,37 vs 2,0 s)." |
| 12 | Sobe-e-desce de massa (peso) | Amplitude vertical do osso da pelve/tronco por passo ÷ altura do corpo; fase vs. contato (queda após contato, subida após passagem) [LIDO Williams]. | Amplitude ≥ 1,5% da altura em andar; ≥ 3% em corrida; mínimo no apoio central é de passagem alta. Falha se desvio padrão do y da pelve < 0,3% da altura. | "Corpo desliza nivelado: aumentar curva vertical da pelve; mínimo logo após contato." |
| 13 | Espectro do ruído de idle | PSD (Welch) da rotação do osso em idle; inclinação em log-log. | Esperado inclinação -0,7 a -1,3 (1/f) [RESUMO conceito]. Falha se plano (±0,3 = branco) ou se pico estreito único (senoide pura). | "Ruído branco: trocar por ruído Perlin/1/f de baixa frequência (< 2 Hz)." |
| 14 | Respiração e piscada | Período dominante do osso do peito; intervalo entre piscadas. | Período dentro de 0,5x a 2x de 1/(0,89·M^-0,26) [RESUMO]; piscada intervalo 2-8 s com jitter > 20%. | "Respira rápido/lento para o porte: ajustar período de respiração ao peso." |
| 15 | Antecipação e hold | Quadros entre início de recuo e início do golpe; duração do golpe; recuperação; quadros com pose parada (ω < ε). | Antecipação ≥ valor da tabela (d) -30%; recuperação ≥ 1,5x golpe; hold em pose-chave ≥ 1 q; sem "hold morto": ω de ossos livres não deve ser exatamente 0 por > 12 q (moving hold). | "Golpe sem aviso: adicionar N quadros de antecipação conforme porte." |
| 16 | Giro e salto de emenda (existentes) | Manter portão atual. | Manter. | Manter. |

---

## (e) URLs realmente abertas

Abriram e li (WebFetch): 
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9975895 (Troje & Chang, Current Directions in Psych. Science, 2023) [LIDO]
- https://monalysa.readthedocs.io/en/latest/smoothness.html (fórmulas DJ, LDLJ, SPARC) [LIDO]
- https://www.originalwisdom.com/wp-content/uploads/bsk-pdf-manager/2019/10/Heglund-and-Taylor_1988_Speed-and-stride-frequency-and-energy-cost-per-stride-how-do-they-change-with-body-size-and-gait.pdf (Heglund & Taylor 1988; extração limitada a poucas equações) [LIDO]
- https://dn721807.ca.archive.org/0/items/taskav-01/The__Animator%27s_Survival_Kit%5B1%5D_text.pdf (Williams; li o PDF extraído localmente com pdftotext, OCR ruidoso) [LIDO]

Só apareceram em busca (resumo, não abertas por mim):
- https://unpaywall.org/10.2312%2FSCA%2FSCA11%2F287-294 (Pražák et al.; redirecionou, não completei)
- https://www.yorku.ca/research/biomotionlab/?p=536
- https://monalysa.readthedocs.io/en/latest/smoothness.html (também usada em RESUMO para SPARC)
- https://par.nsf.gov/servlets/purl/10048743, https://arxiv.org/pdf/2012.01732, https://www.bohrium.com/paper-details/a-robust-and-sensitive-metric-for-quantifying-movement-smoothness/813347964939403264-3906
- https://www.ece.uvic.ca/~bctill/papers/mocap/Lacquaniti_etal_1983.pdf, https://pmc.ncbi.nlm.nih.gov/articles/PMC6758108
- https://cob.silverchair.com/jeb/article/200/4/821/7425/Effect-of-reduced-gravity-on-the-preferred-walk e PMC1617162 (Froude/duty)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12400827/ (respiração alométrica), https://pdodds.w3.uvm.edu/files/papers/others/1966/stahl1966a.pdf (Stahl)
- https://pubmed.ncbi.nlm.nih.gov/18565090/, https://www.frontiersin.org/articles/10.3389/fnhum.2017.00489/full (piscadas)
- https://www.nature.com/articles/s41598-024-52905-8.pdf (1/f em atividade)
- https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBasicMultiChannelPerlin.html
- https://creativebloq.com/features/how-into-the-spider-verse-got-its-mind-blowing-look, https://www.fxguide.com/?p=244678
- https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf (palestra GDC, não aberta)
- https://anim.works/?p=25924 (moving hold)

## (f) O que não confirmei

- Texto completo de Pražák et al. 2011: abstract via busca só; diglib.eg.org retornou 403. Só o "<21 mm" é citado, sem número de participantes, condições ou unidade de escala (cm do mundo real ou do boneco).
- Valor numérico de "Perceptual thresholds for foot slipping in animated characters" (core.ac.uk 403).
- Limiar de deslize em % da passada: não achado.
- Flash & Hogan 1985, Viviani & Terzuolo 1982 e Troje & Westhoff 2006 originais: não abertos.
- Duty factor por Froude (Alexander) com números: o PDF sfu.ca veio ilegível; só definições de busca.
- Expoentes de respiração e passada no arXiv 2105.01540: PDF ilegível; usei Stahl via busca.
- Frequência de passada por comprimento de perna: sem fonte.
- Tempo em que o olho percebe repetição de laço idle: sem fonte.
- Estudo de estalos (pops) e de simetria perfeita: sem fonte.
- Tabela de quadros por porte (antecipação, golpe, recuperação) em Williams, Disney 12 princípios ou Monster Hunter: não achei. A tabela (d) é proposta minha.
- Dead Cells e taxa exata do Guilty Gear Xrd: não confirmados.
- Perda real ao assar a 30 fps e interpolar no motor: apenas dedução (seção 6.1).
- Amplitudes de idle em graus ou % : sem fonte; valores de projeto.
- Se 1/f parece mais natural que branco/Perlin em personagens: nenhum estudo achado.
