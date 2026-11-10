# Cartão: animação (camadas de um clipe)

Um clipe é uma lista de camadas que se somam. Ângulos em graus, com nome: `frente` (topo vai para a frente),
`esquerda` (vira para a esquerda), `tombar_direita`. Translações em **fração da altura do modelo**:
`cima`, `baixo`, `frente_t`, `tras`, `direita`, `esquerda_t`.

```json
{"nome": "Parado", "duracao": 8, "laco": true, "camadas": [
  {"tipo": "onda", "osso": "Corpo", "canal": "cima", "amp": 0.012, "harm": 2, "forma": "pulso"},
  {"tipo": "onda", "osso": "Cabeca", "canal": "esquerda", "amp": 7, "harm": 1, "fase": 0.3, "harm2": 0.5}]}
```

| Camada | Para quê | Campos |
| --- | --- | --- |
| `onda` | respiração, balanço, cauda, asa | `osso` ou `ossos` (aceita `"Cauda_*"`), `canal`, `amp`, `harm` (ciclos por laço, **inteiro**), `fase` 0–1, `fase_por_osso` (onda que viaja), `forma`: `seno`, `abs` (quica), `pulso` (respira), `asa` |
| `poses` | ataque, dano, morte | `chaves`: `[{"t": 0.42, "curva": "suave", "pose": {"Corpo": {"frente": -14, "tras": 0.06}}}]` |
| `passos` | andar | `pes`: `[{"osso": "Perna_D", "fase": 0}, ...]`, `apoio` (fração no chão), `passada_H`, `altura_H`, `modo`: `perna` ou `solto` |
| `seguir` | parte que chega atrasada | `osso`, `de`, `atraso_s`, `ganho` |
| `tremor` | espasmo de terror | `osso`, `canal`, `amp`, `de_t`, `ate_t`, `segurar` |
| `golpe` | golpe de arma do herói | `mao`, `ficha` (arco da ponta, plano, tempos) |

Curvas: `suave` (padrão), `entra`, `sai`, `golpe` (acelera forte), `passa_e_volta` (ultrapassa e assenta), `degrau`, `linear`.

Receita de ataque que funciona: `t 0` repouso → `t 0.42` recua (curva `suave`) → `t 0.55` golpeia (`golpe`) →
`t 0.68` segue (`sai`) → `t 1` volta (`suave`). Marque `"marcadores": [["Aviso", 0], ["Impacto", 0.55]]`.

Fases de andadura: bípede `0` e `0.52`; quadrúpede passo TE `0`, DE `0.25`, TD `0.5`, DD `0.75`; trote pares
diagonais `0` e `0.5`; seis pernas em tripé alternado; oito em dois grupos de quatro.

**Perna de dois ossos:** se o osso da perna tem `"segmentos": 2` e `"dobra": "joelho"` ou `"reverso"`, a camada
`passos` em `"modo": "perna"` resolve o joelho sozinha: o pé fica parado no chão durante o apoio e o corpo desce um
pouco (`"agacho": 0.07`, fração do comprimento da perna) para o joelho ter folga. Não escreva camada para `<Perna>_2`.

**Segmentos que ninguém animou** (antebraço, canela fora do andar, ponta de cauda, orelha) acompanham o osso de cima
com atraso. Para a cauda inteira ondular, anime só `Cauda_1`; o resto vem atrás.
