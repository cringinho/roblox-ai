# 13. Animação fluida, procedural e por camadas: técnicas e números

Escopo: o passo seguinte ao dossiê 01 (percepção, dois terços, jerk mínimo, 12 princípios, que não se repetem aqui). Foco: técnicas concretas para o gerador de clipes assados a 30 qpf com peças rígidas de voxel.

Legenda de confiança: [LIDO] a página foi aberta e o conteúdo foi lido; [RESUMO] só o resumo da busca ou uma página que não trouxe o detalhe; [PROPOSTA] não há fonte, é número de partida a ser medido no jogo; [CONHECIDO] fórmula padrão de manual, não reaberta nesta sessão.

Aviso de honestidade: as palestras mais importantes (Rosen/GDC 2014, Rain World/GDC 2016, t3ssel8r, Bollo/GDC 2018) estão em vídeo ou atrás de paywall; as ferramentas desta sessão não leem vídeo. Dessas fontes só se obteve o resumo. Os números duros vieram de páginas escritas (Holden, Chou, Juckett, SmashWiki, SonicHurricane, Epic via resumo, mocaponline, ouhsc, PMC).

## Veredito

1. A dureza vem de três causas: interpolação linear/uniforme entre poses, ausência de inércia (nada atrasa nem passa do ponto) e laço perfeitamente periódico. As três se corrigem na camada de curvas e molas, sem mudar o modelo.
2. O que os jogos de referência fazem é o mesmo padrão: pouquíssimas poses-chave (Overgrowth: cerca de 13 poses na locomoção [RESUMO]) mais camadas procedurais reativas (IK de pés, olhar, molas). Fluidez nasce da camada procedural em cima da pose, não de mais quadros.
3. Todo osso secundário (cabeça, cauda, capa, orelha, arma pendurada) deve passar por uma mola de segunda ordem assada, com meia-vida em quadros de 3 a 12 (valores abaixo, [PROPOSTA] calibrada pela fórmula de Holden [LIDO]).
4. Transições: mistura curta e assimétrica (0,05 a 0,1 s para reação, 0,2 s padrão de locomoção, abaixo de 0,4 s sempre [RESUMO]); entrar em ação de combate deve ser quase corte, sair dela pode ser longo. Inertialização (decaimento do deslocamento com velocidade casada) é o padrão da indústria contra estalos [LIDO: Holden].
5. Ataques ganham peso com hit-stop proporcional (fighting games: 7 a 14 quadros a 60 qpf [LIDO]; Smash: fórmula por dano [LIDO]) e com antecipação curta, golpe veloz e recuperação longa. O laço vivo exige camadas de períodos incomensuráveis, não ruído puro.

## Jogos de referência

| Jogo | Técnica | Por que funciona | Fonte |
|---|---|---|---|
| Overgrowth / Receiver / Black Shades (David Rosen, Wolfire) | Poucas poses-chave (cerca de 13 na locomoção) mais camadas procedurais, física e ragdoll; plano inicial 100% procedural foi abandonado por falta de controle, ficou "combinação de keyframe, procedural e física" | Poses dão a intenção; o procedural dá reatividade e variação; a física dá consequência | [RESUMO] gdcvault.com/play/1020583; gamedeveloper.com (resumo); citação de blog Wolfire via ModDB. Talk em vídeo não lida |
| Rain World | Corpo de 2 "pedaços" esféricos a distância fixa; membros e cauda cosméticos animados por código a partir da entrada; mistura de animação clássica e procedural, "macio e dobrável" | O corpo simulado tropeça, gira e cai de verdade; membros reagem ao terreno | [LIDO] unity.com/en/blog/exploring-procedural-design-rain-world; [RESUMO] gamedeveloper.com (talk GDC 2016, sem números) |
| Spore (Hecker) | Clipes nomeados aplicados a qualquer morfologia por retargeting em tempo real com IK | Um clipe vale para qualquer criatura; o IK corrige o que a forma muda | [RESUMO] chrishecker.com (página fora do ar na leitura) |
| Wolfire / Overgrowth ragdoll | Esqueleto de cápsulas com juntas limitadas e mistura com animação | Reação física parcial em vez de animação enlatada | [RESUMO] ModDB (post "why we are not using euphoria") |
| Shadow of the Colossus / ICO | Pés casados a degraus de alturas diferentes, mãos presas; procedural para Agro e colossos de quatro patas e serpentes | Contato com o mundo sem clipes por terreno | [LIDO] deck Google Docs de Team Ico (lista de técnicas, sem números); [RESUMO] Tanaka/Ueda (genDESIGN) |
| The Last Guardian (Trico) | Coluna dobra para seguir curva do caminho com limite de ângulo; pé escolhe pouso ao levantar e reverifica durante o passo; pé "preso" ao chão; postura pelo deslocamento do pé; método "dança do leão" (cabeça primeiro, pescoço resolvido depois); sensores de teto baixam a cabeça | Escolher o pouso no início e corrigir durante dá passo natural; cabeça-primeiro dá olhar expressivo | [LIDO] deck Google Docs (lista, sem números) |
| Monster Hunter | Ataques legíveis só pelo início ("dá para saber o que vem pela animação de partida"); compromisso total (sem cancelar); hit-stop deliberadamente forte em World, reduzido e depois reforçado em Wilds | Legibilidade e peso vêm do tempo, não de detalhe | [LIDO] news.capcomusa.com (Sunbreak); [LIDO] gamingbolt (sem números) |
| Dark Souls | Dados de quadro medidos a 30 qpf (animações em passos de 30 qpf); ataques do jogador na mesma escala de tempo dos inimigos | Comprometimento e leitura justa | [RESUMO] buscas; sem dados de partida oficiais |
| Hollow Knight, Ori, Hades, Celeste, Dead Cells | Dead Cells: poses-chave primeiro, intermediários depois, fácil reequilibrar mudando só a pose; Ori: Mahler defensor de squash e stretch; Hades: pausa de acerto de 30 a 50 ms (blog, não confiável) | Poucas poses fortes, tempo ajustável | [RESUMO] Motion Twin (repost, não aberto: a página aberta era outro conteúdo), RPS/Ori, blogs. Sem contagem oficial de quadros achada |
| Smash Bros (Sakurai) | Hit-stop (hitlag) como função do dano; 8 técnicas de hit-stop em vídeo | Peso do golpe legível em milissegundos | [LIDO] ssbwiki.com/Hitlag; [RESUMO] vídeo de Sakurai (legenda bloqueada, 403) |

## Molas e dinâmica de segunda ordem

### Formulas (todas verificadas, exceto onde indicado)

Mola amortecida contínua, com x o valor, alvo xt, ω = 2πf e ζ a razão de amortecimento:

x'' + 2ζω x' + ω² (x − xt) = 0  [LIDO: Chou; Juckett]

- ζ = 1: crítica, chega o mais rápido sem passar do alvo. ζ < 1: sobe e oscila. ζ > 1: lenta, sem oscilar [LIDO: Juckett].
- Crítica em forma fechada (Holden): y = d/2; j0 = x0 − alvo; j1 = v0 + j0·y; x(t) = e^(−y t)(j0 + j1 t) + alvo; v(t) = e^(−y t)(v0 − j1 y t) [LIDO: theorangeduck.com/page/spring-roll-call].
- Parametrização por meia-vida h (tempo para cair metade da distância): y = 2·ln2 / h. Amortecedor simples sem oscilação: x = lerp(x, alvo, 1 − exp(−ln2·dt/h)) [LIDO: Holden].
- Atraso médio: lag = h / ln2 [LIDO: Holden].
- Integração estável passo a passo (Euler implícito): com h_t o passo, Δ = 1 + 2·h_t·ζω + h_t²ω²; x+ = ((1 + 2h_tζω)x + h_t v + h_t²ω² xt)/Δ; v+ = (v + h_t ω² (xt − x))/Δ [LIDO: allenchou.net]. Como o assado roda uma vez, qualquer das formas fechadas serve; Euler implícito evita explodir se se usar passo grande.
- Decaimento: parte restante após t_d é p_d; ζ = ln(p_d) / (−ω t_d). Exemplo de Chou: 90% de redução a cada 0,5 s a 2 Hz dá ζ ≈ 0,367 [LIDO: Chou]. Demonstração dele: 4 Hz e ζ = 0,23 reduz 99,7% por segundo [LIDO].

Dinâmica de segunda ordem de t3ssel8r (f, ζ, r) [CONHECIDO, o vídeo não pôde ser lido; só o resumo da busca confirmou o papel dos três parâmetros]:

- k1 = ζ/(π f); k2 = 1/(2π f)²; k3 = r·ζ/(2π f). Passo: y += dt·v; v += dt·(x + k3·x' − y − k1·v)/k2, com x' a velocidade estimada da entrada.
- f: rapidez de resposta/oscilação. ζ: amortecimento (0 oscila para sempre, 1 crítico). r: resposta inicial. Resumo confirmado: r < 0 gera antecipação (vai para trás primeiro), r > 1 gera overshoot, r entre 0 e 1 e depois 1 faz a saída acompanhar a entrada [RESUMO: documentação de crux sobre o vídeo, e resumo do Hackaday].
- Estabilidade: passo grande explode; limitar o passo ou desacelerar a dinâmica em vez de arriscar [RESUMO: Hackaday].

### Como assar uma mola em quadros (receita)

1. Escolha o sinal que dirige a mola: o osso-pai (rotação do pai em cada quadro), ou uma pose-alvo por trechos.
2. Itere a 30 qpf com dt = 1/30 (ou subpasso 1/120 por estabilidade se ζ < 0,3).
3. Faça um pré-aquecimento de 2 a 4 laços e grave só o último, para o laço fechar com velocidade contínua (começo igual ao fim). [PROPOSTA, técnica padrão de laço assado].
4. Em clipes não periódicos (golpe) comece a mola em repouso e acrescente 0,3 a 0,5 s de rabo parado para a mola assentar; ou decida que a mola continua viva na mistura de clipes.

### Valores por parte do corpo [PROPOSTA]

Nenhuma fonte dá valores por parte; os números abaixo são partida, derivados das fórmulas lidas (meia-vida h em quadros a 30 qpf; ζ é a razão de amortecimento). Faixa de aceitação: menor h é mais rígido; ζ < 1 dá a sobra de movimento que lemos como peso e vida.

| Parte | f (Hz) | ζ | r | Meia-vida crítica equivalente | Observação |
|---|---|---|---|---|---|
| Cabeça sobre o tronco | 2,0 a 3,0 | 0,7 a 0,9 | 0,5 a 1,0 | 4 a 6 quadros | Atrasar mais que o tronco; nunca ζ < 0,6 |
| Pescoço/olhar (cabeça-primeiro, a la "dança do leão") | 3,0 a 4,0 | 0,8 a 1,0 | 0 a 0,5 | 3 a 5 quadros | Olhar chega antes do corpo |
| Cauda (por segmento, cadeia) | 1,0 a 2,0 | 0,3 a 0,5 | 1,0 | 8 a 14 quadros, +2 a 3 por segmento | Ver dossiê 05 |
| Orelha/pena/franja | 3,0 a 5,0 | 0,25 a 0,4 | 1,5 | 3 a 6 quadros | Sobra de 1 a 2 oscilações visíveis |
| Capa/pano pesado | 0,8 a 1,5 | 0,5 a 0,7 | 1,0 | 10 a 18 quadros | Segue o quadril, com defasagem |
| Arma/escudo pendurado | 2,5 a 3,5 | 0,6 a 0,8 | 1,0 | 4 a 8 quadros | Precisa de limite de ângulo |
| Ombros/braços soltos (balanço passivo) | 1,5 a 2,5 | 0,5 a 0,7 | 1,0 | 6 a 10 quadros | Segue a rotação do tronco |
| Anticipação por mola (r negativo) | f do osso | 0,6 a 0,8 | -0,3 a -0,6 | n/a | Só em golpes e saltos curtos |

Cálculo de apoio: para mola crítica, h = 4·ln2/d e d = 2·ω = 4π f; logo h ≈ 0,22 / f em segundos (por exemplo f = 2 Hz dá h ≈ 0,11 s, cerca de 3,3 quadros). [derivado das fórmulas de Holden, LIDO]

### Observações práticas

- "Seguir" do gerador (osso copia o de cima com atraso e ganho) é uma mola de primeira ordem (amortecedor exponencial) de Holden: use a forma lerp com meia-vida, não um atraso fixo de quadros, para não criar passos visíveis [LIDO].
- Prefira ζ entre 0,5 e 1 na maior parte; abaixo de 0,3 vira "gelatina" e acima de 1 vira arrasto.
- A mola dá overshoot de graça. Não acrescente overshoot em cima de uma mola (dupla contagem).

## Transições

| Tipo | Tempo de mistura | Fonte |
|---|---|---|
| Padrão de locomoção (UE5 e Unity) | 0,2 s | [LIDO] mocaponline.com |
| Reação a dano (flinch) | 0,05 a 0,1 s | [LIDO] mocaponline.com |
| Roblox: Play/AdjustWeight, fadeTime padrão | 0,1 s, fade linear sem escolha de curva | [RESUMO] create.roblox.com; DevForum 2687610 |
| Recomendação da Epic para duração | menor que 0,4 s; evitar inertialização com poses muito diferentes | [RESUMO] docs da Epic |
| Entrada em ataque/golpe | 0 a 0,05 s [PROPOSTA]: cortar para a antecipação | proposta |
| Saída de ataque para parado/andar | 0,15 a 0,3 s [PROPOSTA] | proposta |
| Pouso | 0,05 s [PROPOSTA] | proposta |

Inertialização (Bollo, Gears of War, GDC 2018 [RESUMO: página protegida]; implementação Holden [LIDO]): em vez de misturar duas poses, aplica-se um deslocamento aditivo que decai a zero. Coeficientes cúbicos em t normalizado: w0 = 2t³ − 3t² + 1, w1 = (t³ − 2t² + t)·duração, w2 = (6t² − 6t)/duração, w3 = 3t² − 4t + 1; em t = 0 o deslocamento é total e a velocidade casa; em t = 1 tudo é zero [LIDO: theorangeduck.com]. Por que importa: garante continuidade de posição e de velocidade, que é o que a fusão linear não dá.

Adaptação ao gerador (dois clipes assados que o Roblox mistura): o cliente só faz crossfade linear por peso. Para simular inertialização no assado:

- Termine cada clipe de ação com 2 a 4 quadros de "rabo" cuja velocidade vai a zero (curva de saída suave) para o crossfade começar com velocidade quase nula. [PROPOSTA]
- Comece clipes de ação já na pose de antecipação, sem amanhecer do repouso, para o crossfade ser curto. [PROPOSTA]
- Mantenha todas as camadas de molas e de respiração rodando nos clipes de parado e de andar (não pausar) para que a mistura não revele pausa. [PROPOSTA]

Cancelamento: defina janelas explícitas de cancelamento por quadro ("pode sair entre os quadros 18 e 35") em vez de prioridades; ataques de compromisso rodam até o fim; reação leve é aditiva e reação pesada é de corpo inteiro [LIDO: mocaponline]. Evitar estalo: não usar "tempo de saída" que espera o fim do clipe quando a entrada deve responder [LIDO: mocaponline, resumo Unity].

Regra de piso: velocidade de cada osso no último quadro do clipe de origem e no primeiro do destino deve ser da mesma ordem (derivada contínua). [PROPOSTA]

## Peso e tempo

Convenções (SonicHurricane): inicialização (startup) é o tempo antes da caixa de dano, ativo é o tempo com caixa, recuperação é depois [LIDO: critpoints.net, definição]. Os jogos de luta e Dark Souls medem a 60 e 30 qpf respectivamente.

Hit-stop (quadros, em 60 qpf):

| Contexto | Quadros | Fonte |
|---|---|---|
| Leve / médio / pesado em lutas modernas | 9 / 11 / 13 | [LIDO] sonichurricane.com |
| SF2 antigo, qualquer força | cerca de 14 | [LIDO] sonichurricane.com |
| KOF XIII | 7 (leve) a 11 (pesado) | [RESUMO] SRK wiki |
| Projétil SF4 | 8 (vítima 12 em outro exemplo do mesmo post) | [LIDO] sonichurricane.com |
| Smash Ultimate, golpe de 15% | 15 (Melee 8, Brawl 10); teto 20 em Melee e 30 de Brawl em diante | [LIDO] ssbwiki.com/Hitlag |
| Fórmula Ultimate | floor(d·0,65 + 6)·h·e (d dano, h multiplicador, e elétrico 1,5) | [LIDO] ssbwiki.com/Hitlag |
| Hades (blog) | 30 a 50 ms | [RESUMO], baixa confiança |
| Monster Hunter World/Wilds | sem número, ajuste por feedback | [LIDO] gamingbolt |

Conversão a 30 qpf: 9 a 13 quadros a 60 qpf = 150 a 217 ms = 4,5 a 6,5 quadros a 30 qpf. Para o gerador assado: hit-stop só faz sentido como parada do clipe (pausa da pista na hora do acerto), que o servidor/cliente controla; no clipe assado dá para embutir 2 a 4 quadros de tremor de "congelado" (vibração de 1 a 2 voxels, ver tremor). [PROPOSTA]

Tabela de quadros por fase a 30 qpf [PROPOSTA]: não achei dados oficiais de quadros por fase de Dark Souls ou Monster Hunter; Dark Souls documenta medidas comunitárias com margem de ±3 quadros [RESUMO]. Os valores abaixo são partida para o gerador, coerentes com a ideia de "antecipação curta, golpe rápido, recuperação longa" e com os 30 qpf nativos de Dark Souls.

| Ataque | Antecipação | Golpe (rápido) | Contato (hit-stop) | Recuperação | Total | Notas |
|---|---|---|---|---|---|---|
| Rápido/leve | 3 a 5 | 2 a 3 | 2 a 3 | 6 a 9 | 13 a 20 | Corte rápido, sem repouso na pose |
| Médio | 6 a 9 | 3 a 4 | 3 a 4 | 9 a 14 | 21 a 31 | |
| Pesado | 10 a 18 | 3 a 5 | 4 a 6 | 14 a 24 | 31 a 53 | Antecipação legível, como Monster Hunter |
| Chefe/telégrafo | 18 a 30 | 4 a 6 | 5 a 8 | 20 a 40 | 47 a 84 | Início legível diz o ataque [LIDO: Capcom] |
| Mordida/estocada | 4 a 8 | 2 a 3 | 3 a 4 | 8 a 12 | 17 a 27 | Recuo seguido de salto à frente |

Regras de forma [PROPOSTA com princípio padrão]:

- O golpe é a fase mais rápida e a mais curta; a antecipação e a recuperação não são simétricas.
- Antecipação puxa para o lado contrário em 10 a 25% da amplitude do golpe (pode ser r negativo de mola, ver acima).
- O golpe passa do alvo (overshoot) em 5 a 15% e volta por mola; a ponta da arma desenha arco, não reta.
- Recuperação com saída lenta (curva "sai"), nunca parada em seco.
- Squash e stretch em peça rígida: sem deformar o voxel, simule com: escala vertical/horizontal do osso do tronco entre 0,92 e 1,08, sempre preservando o produto, e deslocamento de osso para efeito de compressão. Se o motor não permite escala por osso, usar compressão por deslocamento (agachar 5 a 10% da altura) e alongamento por inclinação. [PROPOSTA; Ori usa squash e stretch, sem números, RESUMO]
- Smear: um quadro de arco largo ou 2 quadros com a arma esticada. [PROPOSTA]

## Vida no parado

| Item | Valor | Fonte |
|---|---|---|
| Respiração em repouso, adulto | 12 a 20 ciclos por minuto (período 3 a 5 s); alguns textos dão 10 a 20 | [RESUMO] StatPearls NBK537306 via busca; Toronto Metropolitan University |
| Razão inspiração:expiração | cerca de 1:2 (1:1,5 a 1:2; com pausa até 1:3 a 1:4) | [RESUMO] respiratorytherapyzone, paramedicpractice |
| Respiração de personagem (jogo) | 10 a 14 ciclos/min para humanoides calmos; 20 a 30 para pequenos [PROPOSTA]; amplitude de peito 1 a 2% de escala, ombros sobem 0,5 a 1 voxel | proposta |
| Piscar, humano | média 17,6 por minuto (6,9 a 25,5) em 24 min; intervalo médio 4,3 s e mediana 2,7 s; distribuição em lei de potência (muitas piscadas próximas, algumas pausas longas) | [LIDO] PMC3156585 |
| Duração do piscar | 100 a 400 ms; maioria perto de 100 a 150 ms (3 a 5 quadros) | [RESUMO] buscas (Wikipedia mirror, lens.com) |
| Piscar em concentração | cai para 5 a 7 por minuto | [RESUMO] busca |
| Troca de peso, olhar, coçar | a cada 6 a 20 s, aleatório [PROPOSTA] | proposta |

Como evitar o aspecto de laço [PROPOSTA, princípio de somar períodos incomensuráveis]:

1. Camadas com períodos que não se dividem entre si (por exemplo 3,3 s respiração, 7,1 s sutil balanço de peso, 11,7 s inclinação da cabeça): o padrão combinado só repete no mínimo múltiplo, que é longo. Em clipe assado, o laço total precisa de comprimento igual ao m.m.c.; quando não, use vários clipes de parado de comprimentos diferentes e alterne.
2. Um clipe principal de repouso (6 a 10 s) mais clipes ocasionais ("olhar em volta", "coçar", "troca de peso") sorteados com intervalo aleatório de 8 a 25 s.
3. Piscar como evento separado, não assado no laço (intervalo sorteado a partir de uma distribuição assimétrica: mediana 2,7 s, média 4,3 s) [LIDO: PMC].
4. Ruído suave de baixa frequência (valor de ruído com período maior que 3 s) em cabeça e ombros, amplitude 0,5 a 1,5 grau; nunca em todos os ossos na mesma fase.
5. Fase aleatória por instância (cada inimigo começa o laço em um quadro diferente) para evitar coro sincronizado.

## Locomoção

Dados medidos de marcha humana:

| Grandeza | Valor | Fonte |
|---|---|---|
| Deslocamento vertical do centro de massa | cerca de 5 cm de amplitude, 2 oscilações por ciclo completo | [LIDO] ouhsc.edu |
| Deslocamento lateral do centro de gravidade | cerca de 6 cm, 1 oscilação por ciclo | [LIDO] ouhsc.edu |
| Flexão do joelho de apoio em meio apoio | cerca de 5 graus | [LIDO] ouhsc.edu |
| Pelve e tórax em contrarrotação; rotação pélvica aumenta o passo acima de 3 km/h | sim, qualitativo, sem graus no que li | [RESUMO] rug.nl e PMC (busca) |
| Calcanhar levantado reduz cerca de dois terços da oscilação vertical do centro | sim | [RESUMO] J Biomech 2014 |
| Passo de caminhada a corrida (Alexander) | passada/altura do quadril = 2,0 para marcha a trote, 2,9 para trote a corrida; λ/h ≈ 2,3 (v²/(g h))^0,3 | [RESUMO] buscas (Springer, PMC) |

Regras acionáveis (todas [PROPOSTA] salvo indicação):

- Travar o pé: todo pé em apoio fica parado no mundo; a velocidade do pé no chão é a negativa da velocidade do corpo. Isso é o IK de 2 ossos com fase de apoio que o gerador já tem. Comece o apoio com o pé a 0,5 a 1 comprimento de passo à frente do quadril projetado e termine atrás.
- Estimativa de cadência por tamanho: passos por segundo ∝ 1/√(altura do quadril) (pêndulo; Froude). Fr = v²/(g·h) [LIDO: resumo de busca sobre definição]. Para altura de quadril h em metros: cadência de caminhada aproximada f ≈ 1,0 a 1,1 × √(g/h)/(2π) × 2 passos por ciclo. Calibrar em jogo; valor para humano (h ≈ 0,9 m) fica em cerca de 1,8 a 2 passos/s.
- Subida e descida do centro de massa: amplitude vertical do quadril em torno de 2 a 3% da altura do corpo, duas vezes por ciclo; no mínimo no apoio duplo e máximo no apoio simples (arco invertido) conforme o modelo de "pêndulo invertido". [PROPOSTA; ouhsc dá 5 cm absolutos]
- Lateral: o quadril oscila 3 a 4% da largura de passo para o lado do apoio; uma vez por ciclo.
- Contrarrotação: rotação do quadril ±4 a 6 graus no eixo vertical, ombros em fase oposta com 60 a 100% dessa amplitude; aumenta com a velocidade. [PROPOSTA]
- Inclinação com a aceleração: incline o tronco no sentido da aceleração com ângulo ≈ atan(a/g), limitado a 8 a 15 graus; suavizar por mola crítica de meia-vida 4 a 6 quadros. [PROPOSTA com física padrão: a ≈ g tanθ]
- Virar em arco: não girar no lugar; o corpo gira com a velocidade angular limitada (por exemplo 180 a 360 graus/s para humanoide) e o tronco anda atrás da cabeça, o quadril atrás do tronco, cada um com mola de meia-vida crescente (4, 6, 8 quadros). [PROPOSTA, mesma ideia do "cabeça-primeiro" da Trico, LIDO]
- Escolher o pouso do pé ao levantar e corrigir durante o passo [LIDO: deck Team Ico/Last Guardian]. No gerador: o alvo do pé é recalculado no meio do balanço, com mistura nos últimos 30% do balanço.
- Quadrúpedes e aranhas: use sempre ordem de apoio fixa e fase por pata; trote tem diagonais em fase (0, 0,5), andar tem 0, 0,25, 0,5, 0,75; coerente com o dossiê 01/07. Não re-derivei aqui.
- Aceleração e parada: não cortar a velocidade de animação; escalonar a amplitude do passo e o tempo de ciclo com a velocidade real (evita patinar).

## Reações

| Reação | Mistura | Duração | Fonte |
|---|---|---|---|
| Flinch leve | camada aditiva, entrada 0,05 a 0,1 s | 6 a 12 quadros | [LIDO] mocaponline (aditiva e janelas); duração [PROPOSTA] |
| Cambalear pesado/stagger | corpo inteiro sobrepõe, volta | 18 a 36 quadros | [LIDO] mocaponline; duração [PROPOSTA] |
| Empurrão | deslocamento do corpo por mola crítica h = 4 a 6 quadros mais inclinação do tronco no sentido do empurrão (10 a 20 graus) | 10 a 20 quadros | [PROPOSTA] |
| Morte | estágio 1 de golpe e hit-stop; estágio 2 queda com ragdoll parcial, estágio 3 imóvel com respiro final | 30 a 90 quadros | [PROPOSTA]; ragdoll como em Overgrowth [RESUMO] |
| Tropeço | pé trava, tronco passa à frente (mola ζ 0,4), mão toca o chão | 12 a 24 quadros | [PROPOSTA] |

Ragdoll parcial: apenas os ossos fora do núcleo (cabeça, braços, cauda) vão a física; o tronco e os pés continuam animados; o peso da física sobe de 0 a 1 em 0,1 a 0,2 s e desce em 0,3 a 0,6 s. [PROPOSTA; princípio de Overgrowth e Unreal "physical animation", sem números na fonte]. Para peças rígidas de voxel o equivalente barato é "mola de cabo": todos os ossos secundários passam a ter ζ menor por 20 a 30 quadros após o dano.

Dano como gesto, não só tremor: o golpe recebido deve ter hit-stop da vítima (Smash: vítima treme na primeira pose do flinch durante o hitlag [LIDO: ssbwiki]). No assado: repetir o quadro de pico do flinch com tremor de 1 voxel por 2 a 4 quadros.

## Curvas

- Interpolação linear entre poses faz velocidade constante com mudança abrupta no quadro-chave: sem aceleração e desaceleração, o movimento perde a assinatura biológica, que tem perfil de velocidade em sino (mínimo jerk, dossiê 01). Resultado: robô.
- Roblox: o fade entre pistas é linear sem escolha de curva [RESUMO: DevForum]. Isso significa que a suavização deve estar dentro dos próprios quadros assados, não no crossfade.
- Nomes de curvas do gerador (suave, entra, sai, golpe, passa-e-volta) e uso:
  - suave (smoothstep 3t²−2t³ ou quíntico 6t⁵−15t⁴+10t³): pose para pose em repouso. Quíntico tem aceleração zero nas pontas (mínimo jerk) [dossiê 01].
  - entra (começa lento, termina rápido): antecipação para golpe.
  - sai (começa rápido, termina lento): recuperação e pouso.
  - golpe: ease-in curto seguido de snap; 2 a 3 quadros para a fase rápida.
  - passa-e-volta: overshoot de 5 a 15% e retorno por mola (ζ 0,5 a 0,7) em vez de uma curva de bounce de manual.
- Overshoot: usar mola (r > 1 em t3ssel8r [RESUMO], ζ < 1 em Chou [LIDO]) e não somar overshoot à mão.
- Quantos quadros-chave bastam: Overgrowth anima locomoção com cerca de 13 poses [RESUMO]; Dead Cells valida poses-chave primeiro e intermediários depois [RESUMO]. Para o gerador: 2 a 4 poses-chave por laço de andar; 3 a 6 por ataque; a amostragem em 30 qpf é só renderização da curva, não as chaves. [PROPOSTA]
- Redução de chaves: se a curva assada tiver erro máximo menor que 0,5 grau ou 0,25 voxel contra a curva contínua, reduzir chaves (algoritmo de Douglas-Peucker/Ramer em cada canal) e deixar o cliente interpolar. [PROPOSTA] Atenção: o cliente do Roblox interpola linearmente ou pelo estilo de easing da chave; se há perda de suavização, mantenha chaves em todo quadro nas curvas de mola.

## Sintomas e correções

| Sintoma ("parece código") | Causa provável | Correção (camada) |
|---|---|---|
| Robótico, mecânico | Linear ou senoide pura sem atraso | Trocar seno por suave/quíntico, adicionar "seguir" com mola, harmônico 2 de 10 a 25% |
| Tudo move ao mesmo tempo | Fases iguais em todos os ossos | Defasagem proporcional à distância da raiz (onda viajante), 2 a 4 quadros por osso |
| Flutuante, sem peso | Sem antecipação, sem contato, sem hit-stop, sem queda do quadril | Antecipação, hit-stop de 2 a 4 quadros, queda de 2 a 3% da altura no contato |
| Pé escorrega | Velocidade de pé no apoio diferente da do corpo | Travar pé com IK, escalar passo à velocidade |
| Estalo na troca | Crossfade com velocidades diferentes | Rabo de saída suave, pose inicial já em antecipação, mistura mais curta ou rabo comum |
| Parece laço | Período único e fase igual | Camadas incomensuráveis, clipes sorteados, fase aleatória por instância |
| Gelatina | ζ muito baixo ou meia-vida longa demais | ζ ≥ 0,5, meia-vida menor, limites de ângulo |
| Rígido/duro (queixa do dono) | Falta de inércia nos secundários | Molas em cabeça, cauda, orelha, capa, braços com os valores acima |
| Simétrico demais | Esquerda e direita idênticas | Pequena assimetria: 5 a 10% de amplitude e 1 a 2 quadros de fase |
| Tremor feio | Ruído de alta frequência | Ruído só abaixo de 3 Hz; tremor a 6 a 12 Hz só em dor ou medo, com envelope |
| Pausa em pose | Quadros iguais seguidos | Nunca reter pose mais que 6 a 10 quadros sem deriva de 0,3 grau ("moving hold") |
| Ataque sem leitura | Antecipação curta demais para tamanho do inimigo | Escalar antecipação ao tamanho e à ameaça [LIDO: Capcom, legibilidade do início] |
| Olhar morto | Cabeça sem alvo | Olhar-primeiro: cabeça/olhos chegam antes do corpo [LIDO: Last Guardian] |

## REGRAS ACIONÁVEIS

| Situação | Camada do gerador | Parâmetro | Valor | Fonte ou proposta |
|---|---|---|---|---|
| Todo osso secundário | seguir (mola) | forma | amortecedor lerp com meia-vida h: x += (alvo − x)(1 − 2^(−dt/h)) | [LIDO] Holden |
| Cabeça | seguir | f, ζ | 2 a 3 Hz, 0,7 a 0,9 | [PROPOSTA] |
| Cauda | seguir encadeado | f, ζ, +h por segmento | 1 a 2 Hz, 0,3 a 0,5, +2 a 3 quadros | [PROPOSTA] |
| Orelha, pena | seguir | f, ζ, r | 3 a 5 Hz, 0,25 a 0,4, 1,5 | [PROPOSTA] |
| Capa | seguir | f, ζ | 0,8 a 1,5 Hz, 0,5 a 0,7 | [PROPOSTA] |
| Montar mola em quadros | assado | pré-aquecer, gravar último laço | 2 a 4 laços | [PROPOSTA] |
| Atraso médio desejado L | seguir | h = L·ln2 | h em quadros | [LIDO] Holden |
| Quadro de transição locomoção | cliente/Play | fadeTime | 0,2 s | [LIDO] mocaponline |
| Reação a dano | cliente/Play | fadeTime | 0,05 a 0,1 s | [LIDO] mocaponline |
| Entrada em ataque | cliente/Play | fadeTime | 0 a 0,05 s | [PROPOSTA] |
| Qualquer fade | cliente/Play | teto | menor que 0,4 s | [RESUMO] Epic |
| Fim de clipe de ação | curvas | velocidade final | tender a zero em 2 a 4 quadros | [PROPOSTA] |
| Janelas de cancelamento | lógica | formato | "pode sair entre quadro A e B" | [LIDO] mocaponline |
| Hit-stop leve/médio/pesado (60 qpf) | golpe/contato | quadros | 9/11/13 | [LIDO] sonichurricane |
| Hit-stop em 30 qpf | golpe/contato | quadros | 4/5/6 | derivado |
| Hit-stop por dano (Smash) | golpe/contato | quadros | floor(d·0,65+6) | [LIDO] ssbwiki |
| Ataque leve | poses-chave + curvas | antecipação/golpe/recuperação | 3 a 5 / 2 a 3 / 6 a 9 quadros | [PROPOSTA] |
| Ataque pesado | idem | idem | 10 a 18 / 3 a 5 / 14 a 24 quadros | [PROPOSTA] |
| Golpe de arco | golpe por arco | overshoot | 5 a 15% e retorno por mola | [PROPOSTA] |
| Antecipação | poses-chave | recuo | 10 a 25% da amplitude do golpe | [PROPOSTA] |
| Respiração | onda por osso | período | 3 a 5 s (12 a 20 ciclos/min); inspira:expira 1:2 | [RESUMO] StatPearls, outros |
| Piscar | evento | intervalo | mediana 2,7 s, média 4,3 s, longa cauda; duração 3 a 5 quadros | [LIDO] PMC3156585 |
| Piscar em foco | evento | taxa | 5 a 7 por minuto | [RESUMO] |
| Parado vivo | ondas por osso | períodos | 3 períodos incomensuráveis (por exemplo 3,3, 7,1, 11,7 s) | [PROPOSTA] |
| Laço de parado | clipes | variação | 2 a 3 clipes + fase aleatória por instância | [PROPOSTA] |
| Quadril vertical | onda por osso | frequência/amplitude | 2 por ciclo; 5 cm em humano ou 2 a 3% da altura | [LIDO] ouhsc / [PROPOSTA] |
| Quadril lateral | onda por osso | frequência/amplitude | 1 por ciclo; 6 cm em humano ou 3 a 4% da largura de passo | [LIDO] ouhsc / [PROPOSTA] |
| Contrarrotação quadril/ombros | onda por osso | amplitude | ±4 a 6° quadril, ombros oposto 60 a 100% | [PROPOSTA] |
| Inclinação do tronco | seguir | ângulo | atan(a/g) limite 8 a 15°, h 4 a 6 quadros | [PROPOSTA] |
| Pés | passos por fase com IK | travamento | pé em apoio fixo no mundo; alvo recalculado no meio do balanço | [LIDO] deck Last Guardian |
| Virar | seguir | cascata | cabeça h 4, tronco h 6, quadril h 8 quadros | [PROPOSTA] |
| Empurrão | seguir | h, inclinação | 4 a 6 quadros; 10 a 20° | [PROPOSTA] |
| Pós-dano | seguir | ζ temporário | reduzir ζ por 20 a 30 quadros | [PROPOSTA] |
| Reação leve | camada aditiva | duração | 6 a 12 quadros | [PROPOSTA] |
| Reação pesada | corpo inteiro | duração | 18 a 36 quadros | [PROPOSTA] |
| Pose em retenção | poses-chave | deriva | nunca reter pose mais de 6 a 10 quadros sem 0,3° de deriva | [PROPOSTA] |
| Squash/stretch em voxel | tronco | escala | 0,92 a 1,08 preservando volume, ou compressão por deslocamento 5 a 10% | [PROPOSTA] |
| Quadros-chave por laço | poses-chave | quantidade | 2 a 4 (andar), 3 a 6 (ataque); amostrar a 30 qpf | [PROPOSTA]; Overgrowth ≈13 poses [RESUMO] |
| Redução de chaves | exportação | tolerância | 0,5° ou 0,25 voxel | [PROPOSTA] |

## Glossário

- Antecipação: movimento contrário curto antes da ação principal.
- Amortecimento (ζ, razão): 0 não amortece, 1 crítico, maior que 1 lento.
- Crítica: mola que chega mais rápido ao alvo sem passar.
- f: frequência em Hz (ω = 2πf).
- Hit-stop / hitlag / impact freeze: congelamento breve dos dois lados no contato.
- Inertialização: transição por deslocamento aditivo que decai, preservando a velocidade.
- Meia-vida (h): tempo para a distância ao alvo cair pela metade.
- Moving hold: manter pose com deriva sutil.
- Overshoot: passar do alvo e voltar.
- r (t3ssel8r): resposta inicial; r < 0 antecipação, r > 1 overshoot.
- Recuperação: fase após o golpe antes de poder agir.
- Seguir: osso copia o de cima com atraso e ganho.
- Smear: quadro com arco largo para dar sensação de velocidade.
- Startup/ativo/recuperação: fases de dados de quadro.

## Fontes

Lidas (abertas):

- Holden, "Spring-It-On / Spring Roll Call": https://theorangeduck.com/page/spring-roll-call [LIDO]
- Holden, inertialização: https://theorangeduck.com/page/propagating-velocities-through-animation-systems [LIDO]
- Chou, molas numéricas: https://allenchou.net/2015/04/game-math-precise-control-over-numeric-springing [LIDO]
- Juckett, "Damped Springs": https://www.ryanjuckett.com/damped-springs/ [LIDO]
- SmashWiki, Hitlag: https://www.ssbwiki.com/Hitlag [LIDO]
- SonicHurricane, "Impact Freeze": https://sonichurricane.com/?p=1043 [LIDO]
- critpoints, padrões de dados de quadro: https://critpoints.net/2023/02/20/frame-data-patterns-that-game-designers-should-know [LIDO, sem números úteis]
- mocaponline, máquina de estados e tempos de mistura: https://mocaponline.com/blogs/mocap-news/animation-state-machine-guide [LIDO]
- Capcom USA, animando monstros de Sunbreak: https://news.capcomusa.com/2023/04/07/animating-the-monsters-of-sunbreak [LIDO]
- GamingBolt, hitstop de Wilds: https://gamingbolt.com/monster-hunter-wilds-weapon-hitstops-will-be-closer-to-what-people-are-looking-forward-to/amp [LIDO]
- Unity, Rain World The Watcher: https://unity.com/en/blog/exploring-procedural-design-rain-world [LIDO]
- Deck Team Ico / Last Guardian: https://docs.google.com/presentation/d/1cYDabTQGYe09w3PyUU4XLrDn2fHy9X5eJIFUjVDt89U/htmlpresent [LIDO]
- ouhsc, cinemática da marcha: https://ouhsc.edu/bserdac/dthompso/web/gait/knmatics/gait.htm [LIDO]
- PMC, padrões temporais de piscar: https://pmc.ncbi.nlm.nih.gov/articles/PMC3156585 [LIDO]

Apenas resumo ou página sem o conteúdo pedido:

- Rosen, GDC 2014: https://gdcvault.com/play/1020583/Animation-Bootcamp-An-Indie-Approach ; https://gamedeveloper.com/design/video-an-indie-approach-to-procedural-animation ; https://www.gameanim.com/2018/03/04/indie-approach-procedural-animation/ ; https://archive.org/details/GDC2014Rosen [RESUMO]
- Wolfire, "why we are not using euphoria": https://www.moddb.com/news/why-we-are-not-using-euphoria/ [RESUMO]
- Rain World, GDC 2016: https://gamedeveloper.com/art/video-animating-i-rain-world-i-and-its-many-squishy-stretchy-creatures [RESUMO, página só com resumo]
- t3ssel8r, "Giving Personality to Procedural Animations using Math": https://www.youtube.com/watch?v=KPoeNZZ6H4s ; https://hackaday.com/2022/06/30/a-math-based-personality-for-games ; https://chemicalcrux.github.io/vrc-docs/docs/code/best.crux.animator-dynamics/sources/second-order-dynamics [RESUMO]
- Bollo, GDC 2018, inertialização: https://gdcvault.com/play/1025165/Inertialization-High-Performance-Animation-Transitions-in-Gears-of-War [RESUMO]
- Epic, Inertialization e Dead Blending: https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprint-blend-nodes-in-unreal-engine [RESUMO]
- Hecker, Spore: https://www.chrishecker.com/Real-time_Motion_Retargeting_to_Highly_Varied_User-Created_Morphologies [RESUMO, página fora do ar]
- Roblox AnimationTrack: https://create.roblox.com/docs/reference/engine/classes/AnimationTrack ; https://devforum.roblox.com/t/how-to-make-a-smoother-transition-between-two-animations/2687610 [RESUMO]
- StatPearls, frequência respiratória: https://www.ncbi.nlm.nih.gov/books/NBK537306/ [RESUMO]
- Dead Cells, Motion Twin (repost): https://www.jikguard.com/news/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-dead-cells [a página aberta não continha o artigo; só o resumo da busca]
- Marcha: https://research.rug.nl/en/publications/interaction-between-thorax-lumbar-and-pelvis-movements-in-the-tra/ ; https://www.doi.org/10.1016/j.jbiomech.2014.02.002 [RESUMO]
- Froude e Alexander: https://link.springer.com/content/pdf/10.1186/s12983-020-00363-z.pdf ; https://pmc.ncbi.nlm.nih.gov/articles/PMC7220109 [RESUMO]
- Sakurai, hit stop: https://mynintendonews.com/2015/11/12/sakurai-talks-about-the-term-hitstop-used-in-fighting-games/ [RESUMO]

## Lacunas conhecidas

1. Sem transcrição de Rosen, Rain World e t3ssel8r: nenhum número de seus sistemas.
2. Sem dados oficiais de quadros por fase de Dark Souls e Monster Hunter, nem de Hollow Knight, Hades, Celeste, Ori (a tabela de ataques é PROPOSTA).
3. Valores de mola por parte do corpo, cadência por tamanho, contrarrotação em graus e ragdoll parcial são PROPOSTA a validar visualmente.
