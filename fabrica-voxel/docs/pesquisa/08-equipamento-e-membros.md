# 08 — Equipamento que serve em vários corpos, e herói com braços e pernas

As fontes foram lidas pelo resumo da busca, não pela página inteira. O que é medição nossa está marcado como [M] e o que é proposta está marcado como [P].

## Veredito

Vários jogos vestem o personagem com uma camada por cima do corpo. O item na mão ganha um ponto de pega próprio. A fábrica segue essas duas ideias e mede a empunhadura por classe. Os detalhes de Hytale e Cube World ficaram sem fonte.

## Como cada jogo veste o personagem

| Jogo | Como funciona | O que virou regra na fábrica |
|---|---|---|
| Minecraft | A armadura é um modelo humanoide separado, desenhado por cima do corpo com um parâmetro de "inflar". Inflar muda só a geometria, não a textura. | Não há ligação registrada nas notas. A fábrica também faz a roupa como casca do corpo (ver [M]). |
| Roblox | A roupa em camadas usa gaiola interna e gaiola externa, presas ao esqueleto R15 de 15 partes. | Não há ligação direta nas notas. A fábrica também faz a roupa como casca do corpo (ver [M]). |
| Hytale | Cosméticos são camadas visuais por cima do personagem, quase sempre um modelo preso por Model Attachment. O jogador pode esconder peças de armadura, e a roupa pode ir por baixo ou por cima. | Nenhuma regra registrada. |
| Cube World | Oito raças, só cosméticas. Todo o progresso fica no equipamento. | Nenhuma regra registrada. |
| Trove | "Costume" é a pele inteira de cada classe. "Style" troca a aparência de uma peça de equipamento. | Nenhuma regra registrada. |

## Item na mão

- Minecraft: o modelo de item na mão fica inclinado 55 graus na terceira pessoa (rotação [0, -90, 55] e translação [0, 4.0, 0.5]).
- Roblox: a pega é um CFrame próprio da ferramenta, com GripForward, GripUp e GripRight.
- Trove: cada item tem um voxel magenta (255, 0, 255) como ponto de pega e uma caixa-limite. Guias mandam testar o item em todas as classes, para ver se ele entra no chão ou no personagem.

## Proporção de personagem cabeçudo e o alcance do braço

- Chibi: a cabeça fica entre 1/3 e 1/2 da altura, ou seja, de 2 a 3 cabeças. Um chibi não consegue tocar o topo da própria cabeça, porque o braço é curto.
- IK de dois ossos: a lei dos cossenos dá o ângulo do cotovelo ou do joelho. Um vetor-polo decide para que lado a junta dobra.
- Colisão de arma: a cápsula de colisão não cobre a malha. As saídas usuais são IK, poses alternativas, ou medir e recolher a arma.

## O que a fábrica faz hoje [M]

- Herói com braços e pernas: Braço + Mão (antebraço com a mão pintada na ponta) e Perna + Pé (canela com o pé).
- Três portes: P com 24 voxels de altura, M com 32 e G com 40. A cabeça tem o mesmo tamanho nos três.
- Roupa nasce do corpo, como casca: tronco dilatado em 1 voxel, com abertura para os membros. Luva cobre o antebraço, bota cobre a canela. Manga e calça recebem a cor da armadura.
- Item de mão gerado no porte do herói: P 0,75; M 1; G 1,2. Nunca é encolhido.
- Empunhadura escolhida por medição, com o antebraço dobrado por classe: espada 20 graus, escudo 80, lanterna 70. Poses de prova com cabeça e tronco inclinados.
- Golpe por IK do braço: corte em pé pelo lado da arma. Para o porte P, estocada baixa.
- Resultado: 15 de 15 linhagens e 24 de 24 combinações de equipamento aprovadas. Zero voxels do item dentro do corpo.

## O que ficou sem fonte

- Minecraft: os valores da edição Java (1.0 externo e 0.5 para as calças) não foram confirmados. A fonte cobre só a edição de console.
- Hytale: não achei fonte sobre ajuste por raça. As fontes são guias de terceiros.
- Cube World: não achei como o equipamento aparece no modelo.
- Roblox: os relatos do fórum sobre gaiola própria em corpo fora do padrão não foram checados.
- Colisão de arma: a fonte é um fórum, sem dado medido.

## Fontes

- https://mappings.dev/1.21.5/net/minecraft/client/model/HumanoidArmorModel.html: mapeamento da classe HumanoidArmorModel da armadura do Minecraft, versão 1.21.5.
- https://coah80.github.io/lce-docs/client/models: documentação da edição de console, com `new HumanoidModel(1.0f)` para a armadura.
- https://mcreator.net/node/73518: modelo de item na mão do Minecraft, com a rotação e a translação da terceira pessoa.
- https://docs.fabricmc.net/develop/items/item-models: documentação de modelos de item do Fabric, citada para o item na mão.
- https://www.g-portal.com/wiki/en/hytale-customization/: guia de terceiros sobre personalização no Hytale.
- https://www.curseforge.com/hytale/mods/wardrobe: mod de guarda-roupa do Hytale, citado para cosméticos em camadas.
- https://allthings.how/hytale-avatar-customization-explained-early-access/: guia de terceiros sobre avatar no Hytale em acesso antecipado.
- https://create.roblox.com/docs/avatar/layered-accessories/specifications: especificação de acessórios em camadas, com gaiolas e o esqueleto R15.
- https://create.roblox.com/docs/art/accessories/caging-best-practices: boas práticas de gaiola para acessórios no Roblox.
- https://devforum.roblox.com/t/layered-clothing-not-respecting-custom-r15-characters-deformation-cage/2185496: relato de fórum sobre roupa em corpo R15 fora do padrão.
- https://create.roblox.com/docs/reference/engine/classes/Tool: referência da classe Tool, com a propriedade Grip.
- https://gamepressure.com/cubeworld/races/z1525e: lista das raças do Cube World.
- https://cubeworld.fandom.com/wiki/Weapons: wiki de armas do Cube World.
- https://trovesaurus.com/page=5553: guia de Trove, citado para costume e style.
- https://trovesaurus.com/page=5632: guia de Trove, citado para o ponto de pega e os testes em classes.
- https://tips.clip-studio.com/en-us/articles/4823: artigo citado para a proporção chibi.
- https://kanamori.cs.tsukuba.ac.jp/publications/nicoint2017/sd.pdf: publicação citada para a proporção de cabeça.
- https://www.ryanjuckett.com/analytic-two-bone-ik-in-2d/: explicação de IK analítico de dois ossos em 2D.
- https://www.gamedeveloper.com/programming/inverse-kinematics-two-joints-for-foot-placement: artigo sobre IK de duas juntas para posicionar os pés.
- https://forums.unrealengine.com/t/how-to-prevent-a-characters-animation-from-clipping-through-objects/2738129: fórum da Unreal sobre animação que atravessa objetos, citado para as saídas de colisão.
