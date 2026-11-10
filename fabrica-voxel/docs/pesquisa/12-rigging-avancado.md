# 12 - Rigging avançado de criaturas e personagens (peças rígidas)

Data da pesquisa: 2026-11-10. Marcas: **[LIDO]** = abri a página (ou o PDF) e li o conteúdo; **[RESUMO]** = só vi o resumo da busca, ou a página aberta não trazia o dado; **[PROPOSTA]** = sem fonte, raciocínio meu, precisa de teste no gerador.

Aviso de honestidade: a busca na web achou pouquíssimos números oficiais de contagem de ossos por jogo. Estúdios quase não publicam isso. Onde a tabela diz "sem número público", é isso mesmo. Várias páginas importantes (site do Hecker, GDC Vault, Epic, 80.lv da Horizon) estavam fora do ar, bloqueadas (403) ou não traziam o dado. Os números das REGRAS ACIONÁVEIS são, em sua maioria, [PROPOSTA] ancorada em poucos dados duros.

---

## 1. Veredito

1. Não existe "número mágico" de ossos publicado por jogo. O que existe de duro: R15 = 15 peças, Unity humanoide = 15 obrigatórios de 55 possíveis [RESUMO], Mixamo = 65 [RESUMO], VRChat classifica avatar em 75 / 150 / 256 / 400 ossos [LIDO]. Humanoide de jogo fica entre 50 e 100 ossos com dedos e auxiliares [RESUMO].
2. Os seus 10 ossos de herói estão abaixo do piso de qualquer padrão: faltam mão, pé, ombro, pescoço, quadril separado do tronco. O ganho de "articulação" vem de subir para 18-22 ossos e de pôr ossos de **transmissão** (ombro, quadril, peito, pescoço), não de pôr mais blocos.
3. O que faz criatura parecer viva não é a contagem: é o **acoplamento entre ossos** (quadril comanda perna, peito compensa, cabeça estabiliza, cauda contrabalança) e a **cadeia com atraso** em tudo que é longo. O Spore resolve criaturas arbitrárias com só espinha + membros + gait + IK [LIDO].
4. Para peça rígida: esconder junta com esfera/peça intermediária, usar poucos ossos de torção falsos (peça-luva), e squash por escala só em peça sem filhos rígidos (no Hytale a escala de um grupo não afeta os filhos [LIDO]).
5. Teto prático: 255 nós no Hytale/Blockbench [LIDO]; 75 ossos é o "Excelente" do VRChat [LIDO]. Para chefe sugiro 36-48 ossos animados e até 12 secundários; ver tabela de regras. Roblox não publica limite de Motor6D [RESUMO]; medir com MicroProfiler.

---

## 2. Quantos ossos (tabela)

Separação: D = deformação (move malha), A = auxiliar (twist, corretivo, IK/controle), F = física (mola/jiggle).

| Jogo / padrão | Personagem ou criatura | Ossos | D / A / F | Fonte |
|---|---|---|---|---|
| Roblox R6 | humanoide blocado | 6 peças / 6 juntas | só D | [RESUMO] HumanoidRigDescription: "R6 (6-joint)" e "R15 (15-joint)" subconjuntos de 22 juntas. https://create.roblox.com/docs/en-us/reference/engine/classes/HumanoidRigDescription.md |
| Roblox R15 | humanoide blocado | 15 peças / 15 meshes | só D (peças rígidas; skinning opcional) | [LIDO] https://create.roblox.com/docs/art/modeling/rigging |
| Unity Humanoid Avatar | genérico | 55 mapeáveis, 15 obrigatórios (hips, spine, head, 2x coxa/canela/pé, 2x braço/antebraço/mão); 30 dos opcionais são dedos | D | [RESUMO] a página oficial não trazia os números; vêm de conhecimento geral. https://docs.unity.com/en-us/engine/current/manual/animation-section/animation-mecanim/avatar-creationand-setup |
| Mixamo | humanoide | 65 | D (inclui dedos) | [RESUMO] https://mocaponline.com/blogs/mocap-news/character-rigging-game-dev-guide |
| Humanoide de jogo, faixa típica | humanoide | 50-100; ~50 básico + 30-40 de dedos | D+A | [RESUMO] mesmo link acima |
| Unreal UE5 Manny/Quinn | humanoide | sem número oficial achado; relato de fórum: 161 em perto, 91 em longe (LOD) | D+A (2 twist por segmento de membro, ossos corretivos, ossos IK) | [LIDO, anedótico] https://forums.unrealengine.com/t/unreal-engine-5s-new-mannequin/558026 ; twist/corretivos [RESUMO] https://forums.unrealengine.com/t/any-docs-about-ue4-and-ue5-mannequins/519131 |
| VRChat | avatar de jogador | limite PC: 75 Excelente / 150 Bom / 256 Médio / 400 Ruim; física: 4/8/16/32 componentes PhysBone, 16/64/128/256 transforms afetados, 4/8/16/32 colisores | D+F | [LIDO] https://creators.vrchat.com/avatars/avatar-performance-ranking-system/ |
| Hytale (Blockbench) | modelo/personagem | máx. 255 nós (cada grupo conta, cada cubo conta, exceto o 1º cubo do grupo) | nós = D (peça rígida) | [LIDO] https://cdn.jsdelivr.net/gh/JannisX11/blockbench-plugins@master/plugins/hytale_plugin/about.md |
| Minecraft Bedrock | mobs | sem limite documentado; hierarquia "arbitrariamente funda", um osso raiz recomendado; cubos dentro de ossos; osso "head" recebe look_at | D (peça rígida) | [LIDO] https://learn.microsoft.com/en-us/minecraft/creator/documents/entitymodelingandanimation |
| Monster Hunter World | monstros | sem número público; esqueleto é compartilhado por classe (brutos, leviatãs, piscinas); asas ou cauda extra mudam a contagem e viram esqueleto próprio | D+A | [RESUMO] fórum/wiki de mod, não oficial. https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Mod3-Structure-Notes |
| Dark Souls / Elden Ring | humanoides e chefes | sem número achado | - | [RESUMO] busca sem resultado útil; contar importando FLVER (Soulstruct) |
| Horizon Zero Dawn | máquinas | sem número público; equipe de 6 só em animação das máquinas; Thunderjaw ~5 modeladores por ~8 meses, ~18 meses até "divertido no jogo" | - | [LIDO] https://gamedeveloper.com/design/making-i-horizon-zero-dawn-i-s-machines-feel-like-living-creatures |
| God of War, WoW, Hades, Hollow Knight, Spore (ossos), Cube World, Trove, Deep Rock Galactic, Grounded | - | **sem número público achado** | - | Não encontrado. Hollow Knight: nenhuma fonte confiável sobre o pipeline. Dead Cells usa pipeline 3D para sprites 2D [RESUMO] https://www.jikguard.com/news/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-dead-cells (a página abriu errada, só o resumo da busca vale) |
| Spore | criatura do jogador | não é contagem fixa: árvore de "corpos" com espinha + membros; sem ossos pré-definidos | D | [LIDO] PDF do SIGGRAPH 2008 (texto extraído) https://www.cse.chalmers.se/edu/year/2011/course/TDA361/Advanced%20Computer%20Graphics/027-hecker%20copy.pdf |

Correção honesta: na linha do Unity, o que a página oficial confirmou foi só o conceito de Avatar; 15 obrigatórios / 55 total vêm do meu conhecimento prévio e batem com o que se conhece, mas não foram verificados na fonte.

---

## 3. Rig de peças rígidas (como esconder as juntas e dar vida com poucas peças)

O que as fontes abertas sustentam:

- **Bedrock**: modelo = ossos (invisíveis, em hierarquia funda) contendo cubos; um osso raiz permite animar o conjunto; "pense em qual ponto a peça deve girar" e ajuste o pivô [LIDO, Microsoft Learn]. Cada cubo ainda pode ter pivô e rotação próprios [RESUMO, Mcblend].
- **Hytale**: nó = grupo + cubo/quad; chaves de posição e rotação no grupo; chave de **escala** anima o "stretch" do cubo e **não afeta filhos**; para escalar a partir de um lado, contra-anima a posição [LIDO]. Isso é o squash por escala em peça rígida, com a regra: escalar só folhas ou compensar filhos.
- **Roblox**: ossos (Bone) deformam a malha mas não mudam a forma física de colisão [LIDO]. Para peça rígida, o par Motor6D/AnimationConstraint move a peça inteira.

Técnicas de esconder junta (PROPOSTA, prática comum de brinquedo/LEGO/mecha; não achei artigo aberto que as quantifique):

| Truque | Como | Custo em ossos |
|---|---|---|
| Esfera na junta | esfera de diâmetro ~ 1,1x a largura do membro, filha do osso de cima, centrada no pivô | 0 (é peça do osso pai) |
| Sobreposição de extremidades | cada peça avança 15-25% dentro da vizinha; no giro máximo o vão não aparece | 0 |
| Peça intermediária (cotovelo, joelho, pescoço) | bloco pequeno de cor de "junta" (cinza, couro, osso) | 0 a 1 |
| Luva de torção falsa | peça-luva entre braço e antebraço que recebe 50% da rotação de rolamento | +1 por segmento |
| Squash por escala | escala Y 0,9-1,1 no tronco/cabeça no impacto, com filhos compensados | 0 |
| Cobertura por costura | ombreira/pelve/coxote cobrem a junta (armadura) | 0 |

---

## 4. Técnicas avançadas

| Técnica | O que resolve | Como fazer com peça rígida assada a 30 quadros |
|---|---|---|
| FK | pose direta, arcos de membro | rotação por osso nas chaves; base de tudo |
| IK 2 ossos + vetor-polo | pé fixo no chão, joelho aponta certo | já existe; garantir polo (joelho para frente, cotovelo para trás) por perna; no Roblox existe IKControl com ChainRoot, EndEffector, Target, Pole, Weight, SmoothTime [LIDO, só estrutura] https://create.roblox.com/docs/reference/engine/classes/IKControl |
| Troca IK/FK | pé preso no apoio, solto no balanço | gerar por fase da passada: IK na fase de apoio, FK/arco na fase de voo; assar já o resultado |
| IK de coluna / spline IK | corpo ondulante, cobra, cauda, tentáculo | posicionar 3-5 pontos de controle ao longo da curva; o número de controles não precisa casar com o de ossos [RESUMO, doc Epic Control Rig splines https://dev.epicgames.com/documentation/unreal-engine/control-rig-spline-rigging-in-unreal-engine]; assar posição/rotação de cada segmento |
| Spline/partículas no Spore | tronco com muitos segmentos | o Spore resolve a espinha como curva com UMA restrição de comprimento entre pontos de ramificação, depois resolve os membros com a espinha fixa (duas fases) [LIDO PDF] |
| Cadeia com atraso (follow-through) | cauda, capa, antena, cabelo | já existe; usar atraso de 2-4 quadros por elo e ganho decrescente (PROPOSTA) |
| Osso de torção | antebraço/coxa torcem sem "embrulhar" a pele | UE5 usa 2 ossos de torção por segmento de membro [RESUMO, fórum]; em peça rígida vira luva (ver seção 3) |
| Osso corretivo | ombro/quadril quebram em pose extrema | em peça rígida: peça de ombreira que gira em 40-60% do braço; sem malha deformável não há colapso, então só para cobertura de vão |
| Restrições aim / look-at | cabeça segue alvo, olho segue alvo | o Spore tem controlador lookat que alinha o vetor frontal do osso da cabeça ao alvo [LIDO]; Bedrock tem animação look_at no osso "head" [LIDO]. Horizon trocou IK total por rotação **aditiva** de look-at porque ficava artificial [RESUMO, slides GDC 2017 via busca] |
| Mola / jiggle com colisão | rabo, peitoral, pele solta | não rodar física no jogo: simular offline e assar. Em VRChat a física é limitada a 4-32 componentes [LIDO]: ordem de grandeza útil para orçamento de secundários |
| Tentáculo | cadeia longa | spline IK + atraso + onda senoidal com fase por elo (PROPOSTA) |
| Pé com rolamento (heel roll / toe pivot) | passo plausível | 3 ossos de pé: calcanhar, planta, ponta; rolamento = rotação sequencial por fase do passo (PROPOSTA; não achei fonte aberta) |
| Dedos | garra, mão | mínimo 1 osso por garra; 2-3 por dedo só em herói de perto. Unity: 30 dos 55 ossos humanoides são dedos [RESUMO] |
| Mandíbula e rosto | rugido, fala | 1 osso de mandíbula; olhos 2 ossos só se houver look-at (Unity lista eye e jaw como opcionais) [RESUMO] |
| Espaço de controle | animar em espaço de mundo, de pai ou do tronco | para cauda e cabeça: rotações em espaço de mundo (estabiliza); para membros: espaço local. PROPOSTA |
| Rig modular por partes | reutilizar perna, cauda, asa | Monster Hunter reutiliza esqueleto por classe e muda a contagem com asa/cauda [RESUMO fórum]; fazer módulos "pernaN", "caudaN", "asa" e montar |
| Retargeting entre proporções | mesma animação em criaturas diferentes | Spore: movimento guardado independente de morfologia; pose em termos de "corpos" e alvos; escala do movimento pelo comprimento do membro até o segmento da espinha mais próximo (modo LimbLength); gait por grupos de pernas com razões de comprimento aproximadas por racionais pequenas [LIDO] |
| Criatura sem pé | cobra, verme | Spore converte segmentos da espinha em "pseudo-pés" e gera marcha de lagarta [LIDO] |

---

## 5. Interações entre partes (o que move o quê)

Princípios sustentados:

- Hierarquia do Spore: **espinha** (cadeia de corpos) na raiz, membros presos a segmentos da espinha; modificador "SpineSegment" sobe pelos membros até a cintura (clavícula/quadril) [LIDO]. Ou seja, a espinha é o centro; ombro/quadril são o elo membro-espinha.
- Horizon: peso vem de animação + som + partículas + câmera, e máquina grande não vira rápido [LIDO].

Regras de acoplamento (PROPOSTA, derivadas de biomecânica geral; calibrar no gerador):

| Origem | Efeito sobre | Fração sugerida |
|---|---|---|
| Quadril (pelve) gira em Y no passo | peito gira contrário | 30-50% do giro da pelve, sentido oposto |
| Pelve sobe/desce (bob) | peito e cabeça | peito 60%, cabeça 30% do deslocamento vertical, com 2-3 quadros de atraso |
| Peito inclina | cabeça compensa (olhar horizontal) | cabeça contra-gira 50-70% |
| Braço levanta | ombro (clavícula) sobe junto | 20-30% |
| Perna avança | quadril do mesmo lado avança | pelve inclina 3-6 graus |
| Corpo acelera ou freia | cauda contrabalança | cauda oposta ao movimento, cadeia com atraso 2-4 quadros por elo |
| Pouso/impacto | squash em tronco, recuo na cabeça | escala Y 0,9 por 3-4 quadros |

Onde pôr a raiz: osso raiz **no chão**, sob o centro de massa projetado (translação do corpo); osso "centro de massa/pelve" filho dele (balanço e bob); pernas filhas da pelve, espinha filha da pelve. Em quadrúpedes, centro de massa entre as patas dianteiras e traseiras. PROPOSTA coerente com a recomendação de "osso raiz único" do Bedrock [LIDO] e com a árvore de espinha do Spore [LIDO].

---

## 6. Orçamento no Roblox

| Item | Dado | Fonte |
|---|---|---|
| Motor6D vs AnimationConstraint | Motor6D está sendo substituído por AnimationConstraint em rigs de avatar; equipe disse que o impacto é pequeno; relatos de que o modo cinemático é igual ou pouco melhor. Sem benchmark oficial | [RESUMO] https://devforum.roblox.com/t/studio-beta-avatar-joint-upgrade-enabling-physically-simulated-characters/3266099 |
| Limite de peças/ossos por modelo | **não achei limite oficial** | [LIDO] doc de rigging não cita |
| Referência de teto por avatar | VRChat: 75 / 150 / 256 / 400 ossos; 1 / 2 / 8 / 16 skinned meshes | [LIDO] |
| Referência de teto por modelo de blocos | Hytale: 255 nós | [LIDO] |
| LOD de esqueleto | UE5: 161 em perto, 91 em longe (relato de fórum, não oficial); regra geral "LOD de malha remove ossos" | [LIDO anedótico] |
| Custo por junta | sem número público | - |

Orçamento proposto (PROPOSTA, validar com MicroProfiler com 20 inimigos na tela):

| Classe | Ossos animados | Peças | Secundários (mola) |
|---|---|---|---|
| Herói | 18-22 | 40-120 | até 6 |
| Comum | 12-24 | 30-100 | até 4 |
| Elite | 24-32 | 80-250 | até 8 |
| Chefe | 36-48 | 270-750 (hoje 269-747) | até 12 |

LOD de esqueleto (PROPOSTA): perto = tudo; médio (>40 studs) = tirar dedos, mandíbula, ossos de torção falsos, esferas de junta; longe (>100 studs) = só raiz, pelve, tronco, cabeça e membros inteiros (corte de ~45%, coerente com 161 para 91).

---

## 7. Jogos de referência (e por quê)

| Jogo | Por que é referência | Fonte / status |
|---|---|---|
| Spore | única solução publicada que anima morfologias arbitrárias: movimento independente de forma, IK por partículas com restrições de comprimento, espinha como curva, gait por grupos de pernas | [LIDO] PDF SIGGRAPH 2008 |
| Horizon Zero Dawn (máquinas) | animação inspirada em animais reais (consultoria anatômica), peso por animação+som+câmera, look-at aditivo; processo de prototipar com esqueleto cru no jogo cedo | [LIDO] Game Developer; GDC 2018 do Richard Oud [RESUMO, não abri o vídeo] |
| Monster Hunter | esqueleto por classe de monstro, reaproveitado, com ossos extras para asa/cauda | [RESUMO] fórum de mod |
| Minecraft Bedrock / Hytale | exatamente o seu caso: peças rígidas em ossos, animação por chave de posição/rotação/escala, look-at no osso da cabeça | [LIDO] |
| Dead Cells | animação desenhada em quadros-chave, com poucos quadros e interpolação depois; rig 3D | [RESUMO] |
| Dark Souls/Elden Ring, God of War, Hades, Hollow Knight | reputação de qualidade de animação, mas **nenhum artigo técnico aberto sobre ossos foi lido nesta pesquisa** | lacuna |

---

## 8. REGRAS ACIONÁVEIS

Todos os números abaixo são [PROPOSTA], exceto onde citam fonte. Nomes de osso em português para o gerador. "Mín" = abaixo disso fica rígido; "ideal" = alvo.

| Classe | Mín | Ideal | Quais ossos | O que cada um faz | Interações obrigatórias |
|---|---|---|---|---|---|
| Herói | 14 | 18-22 (+ até 6 secundários: capa 3, cabelo/pluma 2, bainha 1) | raiz, pelve, abdômen, peito, pescoço, cabeça, 2 ombros, 2x(braço, antebraço, mão), 2x(coxa, canela, pé) [+ ponta do pé] | raiz = translação; pelve = bob e giro; abdômen+peito = torção da coluna; ombro = eleva com o braço; pé = rolamento; mão = pega arma | pelve gira, peito contra-gira 30-50%; cabeça estabiliza 50-70%; ombro 20-30% do braço; IK 2 ossos + polo nas pernas; arma presa à mão |
| Criatura comum (humanoide/besta pequena) | 10 | 14-18 | raiz, pelve, tronco, pescoço, cabeça, 2 braços (2 segmentos), 2 pernas (2 segmentos), cauda 1-3 | corpo balança; cabeça olha; cauda segue | cabeça look-at; cauda em cadeia com atraso; tronco inclina contra o passo |
| Elite | 20 | 24-32 | comum + ombros, mãos/garras, mandíbula, 2-4 ossos de armadura/chifre (secundários), cauda 3-5 | mais teatro: antecipação, rugido, peso | todas as do comum + mandíbula abre no ataque; ombreiras seguem braço; esfera nas juntas grandes |
| Chefe | 30 | 36-48 (até 12 secundários) | elite + espinha de 3-5 segmentos, pescoço 2-3, cauda 5-8, 4-8 ossos de apêndice (asas/tentáculos/chifres), olhos, 2 mandíbulas | presença: peso lento, partes que reagem, fase de ataque legível | espinha em spline com atraso; pescoço e cauda em cadeia; recuo e squash no impacto; cabeça lidera o giro (cabeça, pescoço, peito, pelve, com atraso crescente); controle de fase (enrage) troca conjunto de apêndices |
| Artrópode (aranha 8 pernas, besouro 6) | 16 | 30-44 | raiz, abdômen, cefalotórax, cabeça, 2 quelíceras (2 segmentos cada), 2 pedipalpos, pernas 3-4 segmentos x 6 ou 8, 2 antenas x 2 | perna = coxa/fêmur/tíbia/tarso; abdômen balança | gait em grupos alternados (tripé em 6 pernas, 4+4 alternado em 8) como no Spore, que alterna grupos de pernas por razões de comprimento [LIDO]; IK por perna com polo para cima; abdômen contra-balança; quelíceras abrem no ataque |
| Serpente / verme | 10 | 16-24 | raiz, cabeça, mandíbula, 12-20 segmentos de corpo, 2-3 de cauda | onda viaja da cabeça à cauda | spline IK com 3-5 controles [RESUMO Epic]; onda senoidal com fase por elo; cabeça look-at; sem pé: marcha de lagarta como "pseudo-pés" do Spore [LIDO] quando em terra |
| Alado (dragão, morcego, ave) | 20 | 28-40 | base (comum/elite/chefe) + por asa: ombro, braço, antebraço, mão, 2-3 dedos de membrana; cauda 4-6; pescoço 3 | batida de asa dobra em 3 níveis | batida em onda (ombro, cotovelo, mão com atraso 2-3 quadros); corpo sobe/desce oposto à batida; cauda contrabalança; asa recolhe dobrando a cadeia; peito "respira" com a batida |

Regras de implementação transversais:
1. Um osso raiz no chão, pelve como filho (seção 5).
2. Toda cadeia com 3+ elos usa atraso e ganho decrescente.
3. Toda junta com giro > 45 graus recebe esfera ou sobreposição de 15-25%.
4. Squash/escala só em folhas, ou com contra-escala nos filhos (comportamento do Hytale [LIDO]).
5. Pelo menos 2 secundários por criatura "viva" (cauda, orelha, pluma, capa).
6. Se há 4+ pernas ou pernas em grupos, gait por grupos de pernas com razão de comprimento (Spore [LIDO]).

---

## 9. Glossário

- **Osso (bone)**: transformada hierárquica; aqui, pivô de uma ou mais peças rígidas.
- **Motor6D**: junta do Roblox que liga duas peças com transformada animável; sucedida por AnimationConstraint em avatares [RESUMO].
- **FK / IK**: cinemática direta (gira cada osso) / inversa (dado o alvo da ponta, calcula os ossos).
- **Vetor-polo (pole vector)**: ponto que define para onde aponta o joelho/cotovelo no IK.
- **Spline IK**: IK que encaixa uma cadeia numa curva; para cauda, coluna, tentáculo.
- **Osso de torção (twist)**: osso que absorve parte do rolamento do membro para evitar "embrulho" da pele.
- **Osso corretivo**: osso extra que corrige a deformação em poses extremas.
- **Aim / look-at**: restrição que aponta um eixo ao alvo.
- **Jiggle / osso de mola**: secundário simulado (cabelo, cauda, tecido).
- **Heel roll / toe pivot**: rolamento do pé do calcanhar à ponta.
- **Retargeting**: reaplicar uma animação em esqueleto de proporções diferentes.
- **Squash e stretch**: achatar/alongar por escala para dar peso.
- **Nó (Hytale)**: grupo + cubo; limite de 255 [LIDO].
- **LOD de esqueleto**: remover ossos conforme a distância.

---

## 10. Fontes (com status)

1. [LIDO] Hecker et al., "Real-time Motion Retargeting to Highly Varied User-Created Morphologies" (SIGGRAPH 2008), PDF: https://www.cse.chalmers.se/edu/year/2011/course/TDA361/Advanced%20Computer%20Graphics/027-hecker%20copy.pdf (leitura por busca de trechos no texto extraído, não integral). Página do autor fora do ar: https://www.chrishecker.com/Real-time_Motion_Retargeting_to_Highly_Varied_User-Created_Morphologies
2. [LIDO] VRChat, Performance Ranks: https://creators.vrchat.com/avatars/avatar-performance-ranking-system/
3. [LIDO] Roblox, Rigging and skinning: https://create.roblox.com/docs/art/modeling/rigging
4. [LIDO, parcial] Roblox, IKControl: https://create.roblox.com/docs/reference/engine/classes/IKControl
5. [LIDO] Plugin Hytale para Blockbench (limite de 255 nós, escala): https://cdn.jsdelivr.net/gh/JannisX11/blockbench-plugins@master/plugins/hytale_plugin/about.md
6. [LIDO] Microsoft Learn, Entity Modeling and Animation (Bedrock): https://learn.microsoft.com/en-us/minecraft/creator/documents/entitymodelingandanimation
7. [LIDO] Game Developer, máquinas de Horizon Zero Dawn: https://gamedeveloper.com/design/making-i-horizon-zero-dawn-i-s-machines-feel-like-living-creatures
8. [LIDO, anedótico] Fórum Unreal, novo mannequin (161 para 91 ossos): https://forums.unrealengine.com/t/unreal-engine-5s-new-mannequin/558026
9. [RESUMO] Roblox HumanoidRigDescription: https://create.roblox.com/docs/en-us/reference/engine/classes/HumanoidRigDescription.md
10. [RESUMO] DevForum, Avatar Joint Upgrade: https://devforum.roblox.com/t/studio-beta-avatar-joint-upgrade-enabling-physically-simulated-characters/3266099
11. [RESUMO] Unity, Avatar: https://docs.unity.com/en-us/engine/current/manual/animation-section/animation-mecanim/avatar-creationand-setup (números 15/55 não confirmados na página)
12. [RESUMO] Mocap Online, rigs para jogos: https://mocaponline.com/blogs/mocap-news/character-rigging-game-dev-guide
13. [RESUMO] Epic, Control Rig spline: https://dev.epicgames.com/documentation/unreal-engine/control-rig-spline-rigging-in-unreal-engine
14. [RESUMO] Fórum Unreal, mannequins/twist: https://forums.unrealengine.com/t/any-docs-about-ue4-and-ue5-mannequins/519131
15. [RESUMO] Wiki de mod do Monster Hunter World: https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Mod3-Structure-Notes
16. [RESUMO] Dead Cells, pipeline 3D para 2D: https://www.jikguard.com/news/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-dead-cells
17. [RESUMO] GDC Vault, talks de Guerrilla (Horizon): https://gdcvault.com/play/1025040/AI-and-Narrative-Design ; Epic GDC 2024 "Dragons & Robots": https://forums.unrealengine.com/t/talks-and-demos-dragons-robots-adding-life-to-giant-creatures-gdc-2024/1811391 ; Epic, Full Body IK dragão (403 ao abrir): https://www.unrealengine.com/en-US/blog/full-body-ik-procedural-dragon-animations

## Lacunas desta pesquisa

- Sem contagem de ossos publicada para Monster Hunter, Souls, Horizon, God of War, WoW, Hades, Hollow Knight, Cube World, Trove, DRG, Grounded.
- Sem limite oficial de Motor6D/peças por modelo no Roblox e sem custo por junta; precisa de medição própria.
- Frações de acoplamento (pelve/peito/cabeça) e atrasos de cadeia são [PROPOSTA]; nenhuma fonte aberta lida as quantifica. Próximos passos: GDC Vault (Horizon "Bringing Life to the Machines", Epic "Dragons & Robots"), e medir com captura de movimento ou animação de referência.
