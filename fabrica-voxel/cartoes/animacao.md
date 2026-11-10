# Cartão: animação (camadas de um clipe)

Um clipe é uma lista de camadas que se somam. Ângulos em graus, com nome: `frente` (topo vai para a frente),
`esquerda` (vira para a esquerda), `tombar_direita`. Translações em **fração da altura do modelo**:
`cima`, `baixo`, `frente_t`, `tras`, `direita`, `esquerda_t`.

```json
{"nome": "Parado", "duracao": 8, "laco": true, "camadas": [
  {"tipo": "vida"},
  {"tipo": "onda", "osso": "Cabeca", "canal": "esquerda", "amp": 7, "harm": 1, "fase": 0.3, "harm2": 0.5}]}
{"nome": "Andar", "duracao": 0.9, "laco": true, "camadas": [
  {"tipo": "passos", "modo": "perna", "apoio": 0.6, "passada_H": 0.5, "pes": [{"osso": "Perna_D", "fase": 0}, {"osso": "Perna_E", "fase": 0.52}]},
  {"tipo": "impacto"}]}
```

| Camada | Para quê | Campos |
| --- | --- | --- |
| `onda` | respiração, balanço, cauda, asa | `osso` ou `ossos` (aceita `"Cauda_*"`), `canal`, `amp`, `harm` (ciclos por laço, **inteiro**), `fase` 0–1, `fase_por_osso` (onda que viaja), `forma`: `seno`, `abs` (quica), `pulso` (respira), `asa` |
| `poses` | ataque, dano, morte | `chaves`: `[{"t": 0.42, "curva": "suave", "pose": {"Corpo": {"frente": -14, "tras": 0.06}}}]` |
| `passos` | andar | `pes`: `[{"osso": "Perna_D", "fase": 0}, ...]`, `apoio` (fração no chão), `passada_H`, `altura_H`, `modo`: `perna`, `solto` ou `patas` (aranha, inseto, centopeia) |
| `seguir` | parte que chega atrasada | `osso`, `de`, `atraso_s`, `ganho` |
| `tremor` | espasmo de terror | `osso`, `canal`, `amp`, `de_t`, `ate_t`, `segurar` |
| `golpe` | golpe de arma do herói | `mao`, `ficha` (arco da ponta, plano, tempos) |
| `vida` | **todo Parado começa com esta**: respira, troca o peso, gira um nada em três eixos, a cabeça compensa atrasada, a mandíbula solta o ar, e caudas, pescoços e antenas sem camada ganham uma onda que viaja | nenhum campo é obrigatório. `intensidade` (padrão 1), `cadeias_ganho` (padrão 1), `corpo` (se o osso do corpo não for filho da `Raiz`) |
| `impacto` | peso no andar: cada pisada afunda o corpo e ele volta; cabeça e cauda sentem depois, elo a elo; o corpo vai para o lado do pé de apoio | ponha **logo depois de `passos`**. `afunda_H` (padrão 0.015), `lateral_H` (0.015). Sem passos: `"em_t": [0.55]` dá um tranco naquele instante (pouso, pancada) |
| `ondular` | corpo de centopeia, cobra, peixe, verme | `ossos`: `["Cabeca", "Seg_*"]`, `graus` (desvio de cada segmento, 4 a 12), `ondas` (quantas ondas cabem no corpo, 1), `harm`. **Não** use `onda` em `Seg_*`: os giros se somam e a traseira chicoteia |

Curvas: `suave` (padrão), `entra`, `sai`, `golpe` (acelera forte), `passa_e_volta` (ultrapassa e assenta), `degrau`, `linear`.

Receita de ataque que funciona: `t 0` repouso → `t 0.42` recua (curva `suave`) → `t 0.55` golpeia (`golpe`) →
`t 0.68` segue (`sai`) → `t 1` volta (`suave`). Marque `"marcadores": [["Aviso", 0], ["Impacto", 0.55]]`.

Fases de andadura: bípede `0` e `0.52`; quadrúpede passo TE `0`, DE `0.25`, TD `0.5`, DD `0.75`; trote pares
diagonais `0` e `0.5`; seis pernas em tripé alternado; oito em dois grupos de quatro.

**Perna de dois ossos:** se o osso da perna tem `"segmentos": 2` e `"dobra": "joelho"` ou `"reverso"`, a camada
`passos` em `"modo": "perna"` resolve o joelho sozinha: o pé fica parado no chão durante o apoio e o corpo desce um
pouco (`"agacho": 0.07`, fração do comprimento da perna) para o joelho ter folga. Não escreva camada para `<Perna>_2`.

**Perna de três ossos** (tier 6 ou mais): o terceiro osso é o pé e fica plano no chão sozinho.

**Aranha, inseto, escorpião, centopeia:** use `passos` com `"modo": "patas"` e cite só o primeiro osso de cada pata
(`"osso": "Coxa_1_D"`). A fábrica dobra coxa, fêmur e tíbia para a ponta ficar **parada no chão** durante o apoio,
mesmo com o corpo subindo e ondulando. Fases: aranha e escorpião em dois grupos (`0` e `0.5`, alternando lado e par);
inseto em tripé (`0` e `0.5`); centopeia com `0.12` de atraso por par e os lados em contra-fase. No Parado, a camada
`vida` crava as patas e mexe o corpo sobre elas.

**Segmentos que ninguém animou** (antebraço, canela fora do andar, orelha) acompanham o osso de cima com atraso.
Osso com `"mola": {"freq_hz": 2.5, "amort": 0.35}` segue como mola: atrasa, passa do ponto e assenta.
Cauda, pescoço e antena: no Parado, deixe para a `vida`. No Andar, use `onda` em `"Cauda*"` com
`"fase_por_osso": -0.08` e `"ganho_por_osso": 0.5`. Nunca anime só o primeiro osso: a cauda vira uma vara.

## O que o P1 mede no movimento (e reprova)

| Medida | Limite | Por quê |
| --- | --- | --- |
| Pé desliza no apoio | 2,5% do comprimento da perna (8% em perna rígida de um osso) | é o defeito que o olho vê primeiro |
| Pata alcança o ponto de pisada | 0,03 stud | pata curta com passada longa fica no ar |
| Peso no andar | o corpo sobe e desce, ou vai de lado, 3% do comprimento da perna ou mais | sem isso a criatura desliza como um carrinho |
| Parado não repete | a pose inteira não volta a ser a mesma em menos de 5 s | o olho acha a emenda do laço |
| Cadeia em onda | cada elo atrasa 0,5 quadro ou mais em relação ao anterior | cauda que gira em bloco parece vara |

Passo muito rápido (menos de 7 quadros no ar) levanta menos o pé, sozinho. Perna que quase estica chega devagar ao
limite (`"ik_suave": 0.05`), para o joelho não estalar.
