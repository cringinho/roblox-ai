# 01 — Animação natural: percepção, ofício e parâmetros para rigs voxel rígidos

Dossiê de pesquisa da Fábrica de Voxel (Sanctum Obscura), fechado em 9 nov 2026.
Escopo: rig de segmentos rígidos (ossos só giram e transladam, sem escala), animação procedural em Luau.

Convenções: `[Fn]` = fonte aberta e lida (lista no fim). **[proposta]** = valor de projeto que derivei das fontes, não medido. **[não verificado]** = não abri a fonte primária.
`h` = altura do quadril. `k` = h da criatura ÷ h do avatar. Quadros a 60 fps.

## 0. Achados centrais

1. O olho julga "vivo" pela cinemática das juntas, sobretudo dos **pés** e da sua aceleração vertical. Voxel rígido não atrapalha; pé mal animado, sim.
2. Uma lei resolve o peso: **todo tempo escala com √k**. Criatura 4× maior, ciclos 2× mais lentos.
3. Marcha = dois números por pé (**fator de apoio** e **fase**) + fase dirigida pela **distância percorrida**, como em Spore e Minecraft Bedrock.
4. O "look de código" são dez defeitos mensuráveis (seção 6); todos viram lint.

## 1. Percepção: o que o olho mede

| Achado | Número | Consequência | Fonte |
|---|---|---|---|
| Movimento biológico (*biological motion*, Johansson 1973, *point-light*): ação reconhecida só com pontos nas juntas, e só em movimento | — | A vida está nas juntas | [F1] |
| "Detector de vida": direção e animacidade vêm do movimento local dos pés e exigem aceleração vertical compatível com a gravidade; sem aceleração o efeito some | direção lida em 100 ms | Pé sobe e desce acelerando | [F2][F3][F4] |
| Lei da potência de dois terços (*two-thirds power law*) | v = g·κ^(−β), β ≈ 0,33 (velocidade ∝ raio^(1/3)) | Frear nas curvas fechadas de mão, arma e cabeça | [F5] |
| A lei vale na percepção: velocidade constante em curva parece **não** uniforme; variação > 200% parece uniforme se obedece à lei | > 200% | Velocidade constante em arco é erro visível | [F6] |
| Mínimo jerk (*minimum jerk*, Flash & Hogan 1985): caminho reto, velocidade em sino | x = x₀+(x_f−x₀)(10τ³−15τ⁴+6τ⁵); pico/média 1,875 | Easing padrão de gesto (é o *smootherstep*) | [F5][F7][F8][F9] |
| Isocronia (*isochrony*): a velocidade média cresce com a extensão do gesto | — | Duração ∝ amplitude^0,3–0,5 **[proposta]** | [F10] |
| Deslize de pé (*foot sliding*) | visível abaixo de 21 mm; corrigir é sempre preferido; alongar o membro venceu IK + suavização | Travar pé em apoio; transladar o osso da perna (≤ 1 voxel) é aceitável | [F11] |
| Latência | tolerância 100 ms (1ª pessoa), 500 ms (3ª pessoa/RPG), 1000 ms (onipresente); reação simples ~200 ms | Resposta local < 100 ms; telégrafo inimigo ≥ 2× reação | [F12][F13] |
| Ruído 1/f | postura: Hurst 0,35 ± 0,06, correlações de segundos a minutos; respiração: período e amplitude flutuam de forma fractal | Ocioso com ruído multi-escala | [F14][F15] |
| Vale da estranheza (*uncanny valley*) | movimento amplifica a resposta; o cérebro reage ao **descompasso** aparência × movimento; estudo paramétrico de caminhada achou só variação monotônica | Boneco estilizado pede movimento estilizado e coerente | [F16][F17][F18] |

Derivação: 21 mm ≈ 1,2% de um adulto de 1,75 m ⇒ no avatar de 2,8 studs, deslize máximo de **0,034 stud** **[proposta]**.

## 2. Ofício: princípios traduzidos para rig rígido

Os 12 princípios (Thomas & Johnston): *squash and stretch, anticipation, staging, straight ahead/pose to pose, follow through and overlapping action, slow in and slow out, arc, secondary action, timing, exaggeration, solid drawing, appeal* [F19].

| Princípio / termo | Tradução sem deformação | Padrão **[proposta]** |
|---|---|---|
| *Squash and stretch* (volume constante [F19]) | Aproximar ou afastar segmentos (tronco–quadril); dobrar juntas | ≤ 1–2 voxels |
| Antecipação | Pose oposta antes do golpe | 2–4× a duração do golpe |
| *Follow-through*, *overlapping*, *drag* [F19][F20] | Atraso por junta distal; molas; ultrapassar e voltar | ultrapassagem 10–20%; ζ 0,3–0,5 |
| *Successive breaking of joints*, *lead and follow* [F20] | Ombro → cotovelo → pulso em sequência | 2–4 quadros por junta |
| *Slow in/slow out* | Mínimo jerk; nunca linear | pico/média ≥ 1,5 |
| Arcos | Só girar juntas; extremidade nunca em reta | — |
| Ação secundária | Camadas aditivas que não roubam a cena [F19] | ≤ 30% da principal |
| *Timing* | Peso = tempo: o leve reage mais rápido [F19] | × √k |
| Exagero | Amplitude acima do real | × 1,3–1,5 na câmera alta |
| *Solid drawing* / "twins" [F19] | Proibido espelhar esquerda e direita | defasagem 3–8%; amplitude ±10% |
| Contraposto [F22] | Quadril inclina para a perna de apoio, ombros ao contrário | 3–6° |
| *Moving hold* [F21] | Pose parada nunca congela ("instant death" em CG) | deriva 1–3% + respiração |
| *Smear* | Peça trocada ou rastro de VFX | ≤ 2 quadros [F24] |

### 2.1 Em degrau (*stepped*, "on twos") ou interpolado

| Obra | O que a fonte afirma | Lição |
|---|---|---|
| Dead Cells (2018) | Modelo 3D renderizado pequeno, sem antialiasing, com normal map e toon shader; poses-chave; quadros de interpolação só antes ou depois da chave, "never in-between"; VFX dá a sensação de movimento [F23] | É o nosso "pixel art renderizada em 3D" |
| Spider-Verse | "Primarily on twos": anima-se em uns, apaga-se uma chave sim, outra não, e põe-se em degrau; smears bons por 1–2 quadros [F24] | 12 poses/s em 24 fps [F25] |
| Minecraft Bedrock | Marcha por fórmula: perna = cos(distância × 38,17°) × 80°, fase pela distância percorrida, peso pela velocidade [F26] | Sem deslize; mas seno puro é o look de código |
| Hytale (2025–2026) | Só cubos e quads, sem *weight painting*; ossos com nome padrão são animados pelo sistema; animação via plugin de Blockbench; em 2026 refez animais buscando "emotion, balance, readable silhouettes" [F27][F28][F29] | Rig rígido + nomes padronizados |
| Overgrowth, Rain World | Pouquíssimas poses-chave + procedural (GDC 2014); procedural (GDC 2016) [F30][F31] | Pose forte, código interpola |
| Guilty Gear Xrd | 3D que imita 2D desenhado (GDC 2015) [F32]; animação limitada sem interpolação **[não verificado]** | — |
| Trove, Cube World, Minecraft Dungeons | Sem fonte primária sobre animação **[não verificado]** | — |

Regra **[proposta]**: locomoção, ocioso e molas interpolados; golpes pose-a-pose com transições de 2–4 quadros e *holds*; sprites de pixel 3D em degrau a 8–12 poses/s (`PoseEasingStyle.Constant` [F33]). Nunca pôr em degrau a translação da raiz.

## 3. Locomoção

### 3.1 Lei de escala

- Froude: Fr = v²/(g·h). Mesmo Fr, andadura semelhante. Bípede passa a correr em Fr ≈ 0,5; teto da caminhada Fr = 1,0; quadrúpede passa a trote ou andadura lateral perto de 1,0; andaduras assimétricas (cânter, galope, salto) entre 2,0 e 3,0 [F34].
- Passada relativa s/h: < 2,0 caminhada; 2,0–2,9 trote; > 2,9 corrida. Equação de Alexander (1976): v = 0,25·s^1,67·h^−1,17, em metros (o original leva g^0,5; conferir) [F35].
- De camundongo a cavalo, velocidades ∝ M^0,2 e frequências ∝ M^−0,15 [F36]. Com M ∝ k³, frequência ∝ k^−0,45 ≈ **1/√k**.
- Fator de apoio (*duty factor*): fração do ciclo com o pé no chão; > 50% caminhada, < 50% corrida. Fase dianteiro–traseiro: 0 = andadura lateral, 50% = trote [F37].

### 3.2 Quadrúpedes (cavalo; diagrama de Hildebrand)

TE/TD = traseiros; DE/DD = dianteiros.

| Andadura | Fator de apoio | Fase de cada pé | Frequência |
|---|---|---|---|
| Passo (*walk*), 4 batidas | ~0,6 | TE 0; DE 0,25; TD 0,5; DD 0,75 | 0,8–1,1 Hz |
| Trote, 2 batidas | 0,35–0,45 | TE+DD 0; TD+DE 0,5 | 1,5–2,0 Hz |
| Andadura lateral (*pace*) | 0,28–0,35 | TE+DE 0; TD+DD 0,5 | 1,8–2,7 Hz |
| Cânter, 3 batidas | — | traseiro 0; diagonal 0,3; dianteiro 0,6 **[proposta]** | — |
| Galope, 4 batidas | 0,2–0,3 | TE 0; TD 0,1; DE 0,4; DD 0,5 **[proposta]** | — |
| Salto (*bound*) | < 0,5 | traseiros 0; dianteiros 0,5 **[proposta]** | — |

Fontes: [F37][F38][F39]. No trote e no galope a respiração trava 1:1 com a passada [F40].

### 3.3 Bípedes

- Ciclo: 60% apoio, 40% balanço, 20% em apoio duplo; ~1,4 m/s; passada de 150–170 cm; 115–120 passos/min ⇒ **~1,0 s por passada** [F41].
- Centro de massa: ~5 cm vertical, **duas** oscilações por ciclo, mínimos no apoio duplo; ~6 cm lateral, **uma** por ciclo [F42]. Joelho flexiona ~15° no apoio [F43].
- Cada braço acompanha a perna oposta; abaixo de ~0,8 m/s bate 2:1 [F45]. Prender os braços custa +12% de energia; fase invertida, +26% [F44].
- Cabeça estabilizada: rotação ≤ 20° e < 140°/s enquanto o corpo translada 1–25 cm [F46].

### 3.4 Outros corpos

- **Hexápode**: tripé alternado E1 0°, D1 180°, E2 180°, D2 0°, E3 0°, D3 180°; com a velocidade passa de onda (≥ 5 pés no chão) a tetrápode (≥ 4) e tripé (≥ 3) [F47].
- **Aracnídeo**: dois grupos de quatro pernas em antifase; ~10 Hz em aranha-lobo [F48]. Grupos {E1, D2, E3, D4} e {D1, E2, D3, E4} **[não verificado]**.
- **Miriápode**: onda metacronal (*metachronal wave*), pernas em sequência formando onda viajante [F49].
- **Serpente**: curvatura κ(s,t) = α·cos(kπ(s+t)); comprimento de onda 0,4 ± 0,1 do corpo; amplitude 0,1 ± 0,03; período de 2 s para 30 cm; avança 0,22 corpo por período; contato nos pontos de curvatura zero; em velocidade ergue as curvas [F50].
- **Alado**: frequência ∝ √massa ÷ área da asa [F51] ⇒ ∝ 1/√k em semelhança geométrica **[derivação]**; a batida para baixo sustenta e a asa dobra na subida [F52].

## 4. Técnicas procedurais

1. **Fase por distância**: φ += Δs ÷ passada [F26]. Spore gera a marcha para que "feet not slip" [F53].
2. **Marcha à la Spore**: por pé, fator de apoio + gatilho de passo (*step trigger*); voo do pé normalizado pelo comprimento da perna; parâmetros interpolados pela velocidade; estilo "lumbering" para grandes [F53].
3. **IK de 2 ossos**: lei dos cossenos com `acos` limitado e vetor de dobra (polo) [F54]. No Roblox, `IKControl`: tipos Transform, Position, Rotation, LookAt; `Pole`; `SmoothTime` 0,05 s, criticamente amortecido [F55].
4. **Trava de pé** (*foot planting*) [F56]: fixar no mundo durante o apoio; soltar em 2–3 quadros; alcance ≤ 97% da perna **[proposta]**.
5. **Molas**: frequência ou meia-vida + razão de amortecimento ζ (1 = crítico; < 1 oscila) [F57]. Referência: pêndulo, T ≈ 2π√(L/g) [F58]. Padrões k = 1 **[proposta]**, f × 1/√k: orelha 4–6 Hz, ζ 0,5; cauda 2–3 Hz, ζ 0,35 por elo; capa 1–2 Hz, ζ 0,6; cabelo 3–4 Hz, ζ 0,45; antena 5–7 Hz, ζ 0,3.
6. **Look-at**: pescoço humano, médias: rotação ~72–74°, flexão 56°, extensão 70°, inclinação 43° [F59]. Usar yaw ±45° na cabeça + ±20° no tronco, pitch ±30°, suavização 0,15–0,3 s **[proposta]**; limite suave quando o alvo passa para trás [F53].
7. **Ruído em laço**: senos em harmônicos inteiros do período do clipe [F60]; amplitude ∝ 1/√n, fase por semente **[proposta]**.
8. **Camadas aditivas**: base + respiração + piscar + micro-ocioso + look-at + molas. O Bedrock soma os canais de várias animações antes de montar a transformação [F26].
9. **Transições**: crossfade padrão do Roblox 0,1 s [F61]; inertialização (*inertialization*) como pós-processo, sem avaliar dois estados [F62]; *dead blending* extrapola pose + velocidade e mistura com smoothstep [F63].
10. **Root motion × in-place**: root motion = a animação move o personagem [F64]. Padrão **[proposta]**: clipe in-place, código move a raiz.
11. **Retargeting**: Spore grava a animação em forma independente da morfologia e gera metas de pose para IK [F53]. Para 14 linhagens: clipes em ângulos e frações do membro, nunca em studs.
12. **Easing** [F65]: gesto → smootherstep; golpe → Quart/Quint In até o impacto; assentamento → Back Out ou mola ζ 0,4–0,6; queda → parábola com `Workspace.Gravity` (196,2 studs/s²; 1 stud = 28 cm [F66]); Linear só em rotação contínua.
13. **Roblox**: `Motor6D.Transform` é o recomendado para animação própria; aplicado em lote após `RunService.PreSimulation`; o `Animator` sobrescreve entre `PreAnimation` e `PreSimulation`; `Bone.Transform` funciona igual; não replica [F67][F68]. Escrever em `PreSimulation`, em cada cliente.

**Duas movimentações [proposta]**. Tabuleiro (casa de 4 studs, câmera alta): 1 casa = número inteiro de passadas (s ≈ 1,7 h andando, ≈ 3,3 h correndo); o pé pousa na chegada; a raiz acelera só na primeira casa e freia só na última. Masmorra: fase por distância com velocidade variável, trava de pé, hit-stop.

## 5. Tempos de referência

| Evento | Referência | Padrão k = 1 **[proposta]** |
|---|---|---|
| Antecipação inimiga | reação simples ~200 ms [F13] | 400–600 ms; piso de 400 ms em todo porte |
| Antecipação do jogador | tolerância 100 ms [F12]; "least amount of frames possible" [F23] | ≤ 100 ms |
| Golpe | — | 80–130 ms |
| Hit-stop | luta 2D: ~9/11/13 quadros (fraco/médio/forte) = 150/183/217 ms; SF2 ~14; contra muitos inimigos, congelar cada golpe trava o jogo [F69][F70] | 50–80 ms; 100–150 ms em crítico; 0–30 ms em horda |
| Recuperação | — | 250–400 ms |
| Reação a dano | — | pico em 50–80 ms, volta em 200–300 ms |
| Morte | — | 600–1200 ms + assentamento em mola |
| Piscar | fechado 100–150 ms (até 400); intervalo 2–10 s; ~17/min; 4–5/min em foco [F71] | 120 ms a cada 2–8 s aleatórios |
| Respiração | 12–15/min; ~2 s inspira, ~3 s expira [F72]; frequência ∝ M^−0,26 [F73] | 4–5 s; 40% entra, 60% sai |
| Crossfade | 0,1 s [F61] | 0,1–0,2 s |

## 6. Erros que denunciam animação "de código"

| Sintoma | Correção | Lint |
|---|---|---|
| Simetria perfeita | Defasar lados 3–8%; amplitude ±10%; ocioso em contraposto | correlação espelhada E/D < 0,98 |
| Tudo começa e para junto | Atraso por profundidade na cadeia; molas | picos de velocidade espalhados ≥ 2 quadros |
| Velocidade constante | Mínimo jerk; lei dos 2/3 | pico/média ≥ 1,5 |
| Seno puro | 2º harmônico de 10–25%; pé sobe rápido, desce acelerando | energia fora do fundamental ≥ 5% |
| Laço curto | Ocioso ≥ 8 s; camadas com períodos primos entre si | ≥ 8 s e ≥ 2 camadas |
| Pé deslizando | Fase por distância + trava | deslize em apoio ≤ 1,2% da altura |
| Cabeça soldada | Compensa 50–80% do tronco, com 2–3 quadros de atraso | rotação no mundo ≤ 0,5× a do tronco |
| Falta de peso | Bob 2×/ciclo, mínimo no apoio duplo; antecipação; × √k | bob ≥ 3% de h; antecipação/golpe ≥ 2 |
| Estalo na transição | Crossfade ou dead blending | ≥ 0,1 s |
| Pose congelada | Moving hold | velocidade zero por ≤ 0,5 s |

## 7. Parâmetros padrão

### 7.1 Por porte **[proposta: médio × √k; respiração × k^0,78]**

| Parâmetro | Pequeno k = 0,5 | Médio k = 1 | Grande k = 2 | Colossal k = 4–8 |
|---|---|---|---|---|
| Fator de tempo | 0,71 | 1,0 | 1,41 | 2,0–2,8 |
| Passada andando (s) | 0,7 | 1,0 | 1,4 | 2,0–2,8 |
| Passada correndo (s) | 0,4 | 0,6 | 0,85 | 1,2–1,7 |
| Respiração (s) | 2,3–2,9 | 4–5 | 7–8,6 | 12–25 |
| Piscar fechado (ms) | 85 | 120 | 170 | 240–340 |
| Antecipação inimiga (ms) | 400 | 400–600 | 600–850 | 800–1700 |
| Golpe (ms) | 55–90 | 80–130 | 110–185 | 160–370 |
| Hit-stop (ms) | 35–55 | 50–80 | 70–110 | 100–160 |
| Recuperação (ms) | 180–280 | 250–400 | 350–570 | 500–1100 |
| Atraso por junta (quadros) | 1–3 | 2–4 | 3–6 | 4–11 |
| Mola de cauda (Hz) | 2,8–4,2 | 2–3 | 1,4–2,1 | 0,7–1,5 |
| Crossfade (s) | 0,1 | 0,1–0,2 | 0,15–0,3 | 0,2–0,55 |
| Laço ocioso mínimo (s) | 8 | 8 | 12 | 16 |

Bob vertical andando: 4–6% de h em todo porte (humano: 5 cm em ~0,9 m de perna [F42]).

### 7.2 Por tipo de corpo **[proposta, salvo valores da seção 3]**

| Corpo | Andadura lenta → rápida | Raiz e tronco | Camadas obrigatórias |
|---|---|---|---|
| Bípede | caminhada: apoio 0,60, pés 0 e 0,5 → corrida: apoio 0,3–0,4, fase aérea | bob 2×/ciclo; lateral 1×/ciclo; quadril ±4–8°, ombros opostos; braço ±20–30° | cabeça estabilizada, respiração, piscar |
| Quadrúpede | passo → trote → galope (3.2); trocar em s/h 2,0 e 2,9 | coluna arfa 1×/ciclo no galope; cabeça acena no passo | cauda e orelhas em mola |
| Hexápode | onda → tripé; apoio 0,7 → 0,5 | corpo baixo, bob ≤ 2% | antenas em mola |
| Aracnídeo | tetrápode alternado; apoio 0,6 → 0,5 | quase sem bob; rajadas com pausas | pedipalpos, abdômen em mola |
| Serpente | onda de 0,4 corpo, amplitude 0,1 | cada segmento repete o caminho do anterior | língua, cabeça estabilizada |
| Alado | batida 2–3 Hz × 1/√k; planar entre séries | corpo sobe na batida para baixo; asa dobra ao subir | cauda como leme |
| Flutuante | bob 0,3–0,6 Hz × 1/√k, 3–6% da altura | inclina 5–15° no sentido da aceleração | ruído 1/f, apêndices em mola |
| Gosma | salto: agacha 40%, voo 35%, assenta 25% | "squash" por translação de segmentos empilhados; mola ζ 0,3 | tremor 1/f, núcleo com atraso |

## 8. Regras acionáveis

1. Todo tempo de ciclo, golpe, recuperação e crossfade = valor do porte médio × √k.
2. Fase de locomoção = distância percorrida ÷ comprimento da passada; proibido marcha dirigida só por tempo.
3. Cada pé declara `fator_de_apoio` e `fase` (tabelas 3.2 e 7.2).
4. Deslize do pé em apoio ≤ 1,2% da altura (0,034 stud no avatar).
5. Trajetória vertical do pé acelerada; proibido perfil triangular.
6. Gesto ponto a ponto usa 10τ³−15τ⁴+6τ⁵; velocidade de pico ÷ média ≥ 1,5 (alvo 1,875).
7. Em curva, velocidade ∝ raio^(1/3).
8. Caminhada bípede: apoio 0,60; 20% de apoio duplo; bob de 4–6% de h, 2×/ciclo; lateral 1×/ciclo.
9. Braço acompanha a perna oposta; fase invertida é erro.
10. Cabeça compensa 50–80% da rotação do tronco; resíduo ≤ 20°.
11. Lados nunca espelhados: defasagem 3–8% e amplitude ±10%.
12. Juntas sucessivas atrasam 2–4 quadros × √k.
13. Osso solto em mola: f da tabela ÷ √k, ζ 0,3–0,6, ultrapassagem 10–20%.
14. Ocioso: laço ≥ 8 s, ≥ 2 camadas, harmônicos inteiros com amplitude ∝ 1/√n; velocidade zero por no máximo 0,5 s.
15. Piscar 100–150 ms a cada 2–8 s; respiração de 4–5 s × k^0,78, 40/60.
16. Antecipação inimiga ≥ 400 ms e 2–4× o golpe; resposta ao jogador < 100 ms.
17. Hit-stop 50–80 ms (teto 150 ms); 0–30 ms contra hordas.
18. Transição entre clipes ≥ 0,1 s.
19. Golpe pose-a-pose (transição de 2–4 quadros); sprite pixel 3D a 8–12 poses/s em degrau; smear ≤ 2 quadros; raiz sempre contínua.
20. Clipes em ângulos e frações do membro; alcance de IK ≤ 97% da perna.
21. No Roblox, escrever `Transform` em `PreSimulation`, no cliente; queda usa `Workspace.Gravity`.
22. No tabuleiro, 1 casa = número inteiro de passadas, pé pousando na chegada.

## 9. Glossário

- **Fator de apoio (duty factor)**: fração do ciclo com o pé no chão.
- **Fase / gatilho de passo**: instante, de 0 a 1, em que o pé começa seu ciclo.
- **Froude**: v²/(g·h); mesmo valor, mesma andadura.
- **Mínimo jerk**: trajetória que minimiza a variação da aceleração.
- **Razão de amortecimento (ζ)**: 1 chega sem oscilar; abaixo de 1 oscila.
- **Overlapping / follow-through / drag**: partes em tempos diferentes; seguem após a parada; arrastam atrás.
- **Moving hold**: pose sustentada com micro-movimento.
- **On twos / em degrau**: uma pose a cada dois quadros, sem interpolar.
- **Inertialização / dead blending**: transição feita como pós-processo.
- **Root motion / in-place**: a animação move o personagem / o código move.

## 10. Fontes

- [F1] https://en.wikipedia.org/wiki/Biological_motion — Johansson 1973, point-light.
- [F2] https://pmc.ncbi.nlm.nih.gov/articles/PMC9975895 — "Life Detection From Biological Motion": pés, gravidade.
- [F3] https://europepmc.org/article/MED/16631591 — Troje & Westhoff 2006.
- [F4] https://europepmc.org/article/MED/19271889 — Chang & Troje 2009: 100 ms, aceleração.
- [F5] https://pmc.ncbi.nlm.nih.gov/articles/PMC6758108 — Richardson & Flash 2002: β 0,33; pico/média 1,875.
- [F6] https://europepmc.org/article/MED/1500865 — Viviani & Stucchi 1992.
- [F7] https://pmc.ncbi.nlm.nih.gov/articles/PMC6565116 — Flash & Hogan 1985.
- [F8] https://github.com/demotu/BMC/blob/master/notebooks/MinimumJerkHypothesis.ipynb — polinômio de mínimo jerk.
- [F9] https://en.wikipedia.org/wiki/Smoothstep — smootherstep.
- [F10] https://europepmc.org/article/MED/1826312 — Viviani & Schneider 1991: isocronia.
- [F11] https://diglib.eg.org/handle/10.2312/SCA.SCA11.287-294 — Pražák, Hoyet & O'Sullivan 2011: 21 mm.
- [F12] https://ftp.cs.wpi.edu/pub/techreports/pdf/06-13.pdf — Claypool & Claypool 2006: latência.
- [F13] https://en.wikipedia.org/wiki/Mental_chronometry — reação ~200 ms.
- [F14] https://europepmc.org/article/MED/10754215 — Duarte & Zatsiorsky 2000: Hurst 0,35.
- [F15] https://europepmc.org/article/MED/15286051 — Fadel et al. 2004: respiração fractal.
- [F16] https://en.wikipedia.org/wiki/Uncanny_valley — movimento amplifica.
- [F17] https://pmc.ncbi.nlm.nih.gov/articles/PMC3324571/ — Saygin et al. 2012: descompasso.
- [F18] https://europepmc.org/article/MED/21936298 — Thompson et al. 2011: sem vale.
- [F19] https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation — os 12 princípios, "twins".
- [F20] https://blog.animschool.edu/?p=645 — drag, lead and follow, breaking of joints.
- [F21] https://newsletters.animationmentor.com/newsletter/0609/feature_geek.html — moving hold.
- [F22] https://en.wikipedia.org/wiki/Contrapposto — contraposto.
- [F23] https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i- — Dead Cells, 25 jan 2018.
- [F24] https://www.cgspectrum.com/blog/spider-man-into-the-spider-verse-how-they-got-that-mind-blowing-look — on twos, smears.
- [F25] https://en.wikipedia.org/wiki/Inbetweening — on ones/twos.
- [F26] https://learn.microsoft.com/en-us/minecraft/creator/documents/animations/animationsoverview — Bedrock (jun 2026).
- [F27] https://hytale.com/news/2025/12/an-introduction-to-making-models-for-hytale — cubos, quads, ossos nomeados.
- [F28] https://hytale.com/news/2025/11/hytale-modding-strategy-and-status — plugin Blockbench.
- [F29] https://hytale.com/news/2026/7/first-look-chapter-1-and-more — animais refeitos.
- [F30] https://gdcvault.com/play/1020583/Animation-Bootcamp-An-Indie-Approach — Rosen, GDC 2014.
- [F31] https://www.gamedeveloper.com/art/video-animating-i-rain-world-i-and-its-many-squishy-stretchy-creatures — Rain World, GDC 2016.
- [F32] https://gdcvault.com/play/1022031/GuiltyGearXrd-s-Art-Style-The — resumo da palestra.
- [F33] https://create.roblox.com/docs/reference/engine/enums/PoseEasingStyle.md — Constant, Linear, CubicV2.
- [F34] https://en.wikipedia.org/wiki/Froude_number — Fr 0,5; 1,0; 2–3.
- [F35] https://www.app.pan.pl/archive/published/app46/app46-235.pdf — Mazzetta & Blanco 2001: Alexander, s/h.
- [F36] https://europepmc.org/article/MED/3193059 — Heglund & Taylor 1988: escala.
- [F37] https://en.wikipedia.org/wiki/Gait — fator de apoio e fase.
- [F38] https://fr.copernicus.org/articles/24/151/2021/ — Vincelette 2021: andaduras do cavalo.
- [F39] https://en.wikipedia.org/wiki/Horse_gait — sequência e batidas.
- [F40] https://europepmc.org/article/MED/6849136 — Bramble & Carrier 1983: 1:1.
- [F41] https://now.aapmr.org/?p=1388 — ciclo, cadência, velocidade.
- [F42] https://ouhsc.edu/bserdac/dthompso/web/gait/knmatics/gait.htm — 5 cm vertical, 6 cm lateral.
- [F43] https://en.wikipedia.org/wiki/Gait_(human) — joelho 15°.
- [F44] https://europepmc.org/article/MED/19640879 — Collins et al. 2009: custo dos braços.
- [F45] https://en.wikipedia.org/wiki/Arm_swing_in_human_locomotion — perna oposta, 2:1.
- [F46] https://europepmc.org/article/MED/2257917 — Pozzo et al. 1990: cabeça.
- [F47] https://pmc.ncbi.nlm.nih.gov/articles/PMC5321742 — Ramdya et al. 2017: tripé.
- [F48] https://journals.biologists.com/jeb/article/221/18/jeb174268/260/Limping-following-limb-loss-increases-locomotor — Wilshin et al. 2018: aranhas.
- [F49] https://en.wikipedia.org/wiki/Metachronal_rhythm — onda metacronal.
- [F50] https://pmc.ncbi.nlm.nih.gov/articles/PMC2700932 — Hu et al. 2009: serpentes.
- [F51] https://physicsworld.com/a/simple-equation-predicts-how-quickly-animals-flap-their-wings/ — f ~ √m/A (jun 2024).
- [F52] https://en.wikipedia.org/wiki/Bird_flight — batida das asas.
- [F53] https://www.cse.chalmers.se/edu/year/2011/course/TDA361/Advanced%20Computer%20Graphics/027-hecker%20copy.pdf — Hecker et al. 2008 (Spore).
- [F54] https://theorangeduck.com/page/simple-two-joint — IK de duas juntas.
- [F55] https://create.roblox.com/docs/reference/engine/classes/IKControl.md — IKControl.
- [F56] https://gleicher.sites.cs.wisc.edu/video/2002_footskate — Kovar et al. 2002.
- [F57] https://theorangeduck.com/page/spring-roll-call — molas, meia-vida, ζ.
- [F58] https://en.wikipedia.org/wiki/Pendulum — período do pêndulo.
- [F59] https://help.neckcare.com/range-of-motion-test — amplitude cervical.
- [F60] https://en.wikipedia.org/wiki/Fourier_series — harmônicos.
- [F61] https://create.roblox.com/docs/reference/engine/classes/AnimationTrack.md — fadeTime 0,1.
- [F62] https://gdcvault.com/play/1025165/Inertialization-High-Performance-Animation-Transitions — Bollo, GDC 2018.
- [F63] https://theorangeduck.com/page/dead-blending — dead blending (2023).
- [F64] https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine — root motion.
- [F65] https://create.roblox.com/docs/reference/engine/enums/EasingStyle.md — estilos de easing.
- [F66] https://create.roblox.com/docs/physics/units.md — stud e gravidade.
- [F67] https://create.roblox.com/docs/reference/engine/classes/Motor6D.md — Transform, ordem de execução.
- [F68] https://create.roblox.com/docs/reference/engine/classes/Bone.md — Bone.Transform.
- [F69] https://sonichurricane.com/?p=1043 — impact freeze 9/11/13.
- [F70] https://mynintendonews.com/2015/11/12/sakurai-talks-about-the-term-hitstop-used-in-fighting-games/ — Sakurai, hit-stop.
- [F71] https://en.wikipedia.org/wiki/Blinking — piscar.
- [F72] https://en.wikipedia.org/wiki/Respiratory_rate — 12–15/min.
- [F73] https://pdodds.w3.uvm.edu/files/papers/others/1966/stahl1966a.pdf — Stahl 1967: expoente −0,26.
