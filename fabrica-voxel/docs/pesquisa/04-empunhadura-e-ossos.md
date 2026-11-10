# 04 — Empunhadura sem atravessar o corpo, e mais ossos

Escrito depois do retorno do dono: a espada atravessava o corpo, e os arquétipos tinham poucos ossos e pouco detalhe.
As fontes abaixo foram lidas pelo resultado da busca, não pela página inteira. O que é medição nossa está marcado [M].

## 1. O defeito, medido [M]

Antes da correção, nas 15 linhagens com o conjunto padrão, de 30% a 78% dos voxels de superfície do item ficavam
dentro de outra peça em algum quadro do Golpe; em repouso, até 44% (anão). Causa: cabeça com meia-largura de até
0,4 H, mão colada no tronco, item em pé, arco do golpe com raio de 0,3 H (por dentro da cabeça) e volta ao repouso
em linha reta, por dentro do tronco.

## 2. Como os jogos seguram o item

| Fonte | O que diz | O que virou regra |
| --- | --- | --- |
| Minecraft, modelo `item/handheld` [F1] | Na terceira pessoa o item da mão direita tem rotação `[0, -90, 55]` e translação `[0, 4.0, 0.5]`: fica inclinado 55 graus, nunca em pé | Pose preferida da classe `uma_mao`: 50 graus para a frente |
| Trove, guias do Trovesaurus [F2] | O item tem um ponto de pega (voxel magenta), caixa-limite em volta dele (espada 9 × 9 × 35), 3 a 4 voxels atrás da pega; "teste em todas as classes para pegar item entrando no chão ou no personagem" | Caixa por classe de pegada; matriz de prova; portão `item_atravessa_corpo` |
| Roblox `Tool.Grip` [F3] | A orientação do item na mão é um CFrame próprio (GripForward, GripUp, GripRight), separado da animação | Giro de repouso por osso, gravado no `C0` da junta |
| Fóruns de Unreal [F4] | A cápsula de colisão não cobre a malha; a saída usual é pose alternativa ou IK; outra é medir e recolher a arma quando há contato | Medir por quadro e afastar a mão (desvio) |

Não achei fonte que trate de personagem de cabeça grande (chibi) em particular. A regra abaixo é nossa.

## 3. O que a fábrica faz agora

1. **Empunhadura por medição.** Parte da pose preferida da classe e testa inclinações (frente de 0 a 90, para fora
   de 0 a 40) até o item não tocar o corpo. Escudo pode virar de lado (preso ao braço). Lanterna quase não inclina:
   escorrega até 4 voxels para fora.
2. **Golpe pela frente.** O arco tem centro no tronco; a lâmina aponta para fora do centro. A recuperação volta pelo
   arco até a guarda e só então solta a mão. Por herói, a fábrica procura plano (35, 25, 15, 5 graus), centro à frente
   (0 a 0,18 H) e raio (0,30 a 0,50 H) e fica com o primeiro candidato limpo.
3. **Desvio.** O que sobrar empurra a mão para fora: uma direção por clipe, alargada 3 quadros para cada lado e
   borrada no tempo. Se o contato dura mais de 30% do clipe (asa batendo), afasta de vez.
4. **Portão.** 2% dos voxels do item, em todo quadro de todo clipe.

Resultado [M]: 60 combinações (15 linhagens × 4 conjuntos) com 0% de voxels do item dentro do corpo.

## 4. Mais ossos

- **IK analítico de dois ossos** [F5][F6]: os comprimentos dos ossos e a distância até o alvo formam um triângulo; a
  lei dos cossenos dá o ângulo do joelho; um "polo" decide para que lado a junta dobra. Barato e exato, por isso
  serve para assar a 30 quadros por segundo. Aqui o polo é fixo: `joelho` (para a frente) ou `reverso` (para trás).
- **Medição [M]:** com a perna em dois ossos, a ponta da perna fica em y = 0,000 durante o apoio e sobe até a altura
  pedida no balanço, em bípede, quadrúpede (frente e trás), dragão e digitígrado.
- **Seguimento automático:** segmento sem camada copia o osso de cima com atraso (sobreposição). É o que os 12
  princípios chamam de overlapping action, sem custo de autoria.
- **Limite honesto:** o quadril não sabe do balanço do corpo. As pernas pendem da Raiz, não do tronco; se um dia
  penderem do tronco, o IK precisa compensar o movimento do quadril.

## 5. Números depois da reforma [M]

| | Antes | Depois |
| --- | --- | --- |
| Ossos por arquétipo, sem contar a Raiz | 2 a 13 | 10 a 24 |
| Voxels por arquétipo | 630 a 3916 (7 abaixo de 1000) | 1142 a 4503 |
| Arquétipos aprovados | 20 | 20 |

## Fontes

- **F1** https://mcreator.net/node/73518 e https://docs.fabricmc.net/develop/items/item-models — valores de `handheld` e ordem das transformações.
- **F2** https://trovesaurus.com/page=5632 e páginas de revisão de criações do Trovesaurus — ponto de pega, caixas, teste por classe.
- **F3** https://create.roblox.com/docs/reference/engine/classes/Tool — `Grip`, `GripForward`, `GripUp`.
- **F4** https://forums.unrealengine.com/t/how-to-prevent-a-characters-animation-from-clipping-through-objects/2738129 — cápsula, IK, poses alternativas.
- **F5** https://www.ryanjuckett.com/analytic-two-bone-ik-in-2d/ — derivação do IK de dois ossos.
- **F6** https://www.gamedeveloper.com/programming/inverse-kinematics-two-joints-for-foot-placement — IK de duas juntas para apoio do pé.
