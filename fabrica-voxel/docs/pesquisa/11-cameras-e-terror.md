# 11 — As duas câmeras, o movimento em grade e a dungeon em primeira pessoa

As fontes foram lidas pelo resumo da busca, não pela página inteira. O que é medição nossa está marcado como [M] e o que é proposta está marcado como [P].

## Veredito

O medo em primeira pessoa vem de controlar o que o jogador vê. No movimento em grade, a comunidade recomenda guardar a última tecla apertada durante o passo. No Roblox, a primeira pessoa trava e esconde o próprio personagem. Os números de campo de visão, de susto e de passo não têm fonte.

## Terror em primeira pessoa

- O medo vem de controlar a informação. Um campo de visão apertado deixa o jogador ciente do que não vê.
- Exemplo citado: Alien: Isolation, com primeira pessoa restrita, desfoque de profundidade e sem HUD.
- Valores da fábrica [P]: campo de visão 70; salto para 80 em 0,1 s; pausa de 0,08 s no impacto.

## Sustos

- Tensão é o período em que se sabe que algo vem, sem saber quando.
- Construção demais entedia. Alívio demais acostuma. Usar com parcimônia.
- Silent Hill 4 quase não tem sustos.

## Movimento em grade

- Legend of Grimrock: movimento por ladrilho, em primeira pessoa. Os inimigos seguem as mesmas regras: viram, depois andam.
- A comunidade recomenda guardar a última tecla apertada durante o passo (buffer de entrada).
- Acelerar a animação quando há teclas na fila.
- Segurar para andar de forma contínua pareceu "arrastado" a um desenvolvedor.

## Câmera no Roblox

- `CameraMode.LockFirstPerson` trava a primeira pessoa e esconde o próprio personagem, com menos ferramentas equipadas.
- A câmera é sempre controlada no cliente, por um LocalScript.
- O HumanoidRootPart fica 2 studs abaixo da cabeça.

## Orçamento de ossos

- Rigs de jogo típicos têm de 50 a 100 ossos.
- Lionhead citou de 100 a 175 ossos.
- Uma criatura de combate, em um guia de MMORPG feito em Godot, tem de 2 mil a 8 mil triângulos.
- As fontes são blogs e fóruns.

## O que a fábrica faz hoje [M]

- Grade de ladrilhos de 4 studs, com 0,4444 s por ladrilho.
- O herói anda com 2 a 3 ciclos de passo por 2 ladrilhos, conforme o comprimento da perna.
- Arquétipos de monstro com 10 a 24 ossos.
- Chefe importado (Rei Necromante) com 20 a 30 ossos e 269 a 747 blocos.

## O que ficou sem fonte

- Campo de visão publicado, balanço de cabeça e tempo de susto: não achei número.
- Duração do passo no Grimrock: não achei.
- Truque de campo de visão baixo para imitar câmera ortográfica no Roblox: não confirmado por fonte.
- Orçamento de ossos: as fontes são blogs e fóruns.
- Criatura de combate em Godot: o guia não tem link próprio nas notas.
- Valores da fábrica de campo de visão e de susto: são proposta, não fonte.

## Fontes

- https://www.gamedeveloper.com/design/scary-games-why-fear-should-be-easy-in-games-but-it-isn-t-: artigo sobre o medo vir do controle de informação, citando Alien: Isolation.
- https://gamedev.net/blogs/entry/2274395-how-to-use-pacing-and-build-tension-in-a-horror-game: blog sobre ritmo e construção de tensão em jogo de terror.
- https://game-wisdom.com/critical/jumpscare-horror-game-design: texto sobre design de jump scare.
- https://www.superjumpmagazine.com/the-scary-secrets-of-horror-design-from-silent-hill-4/: texto sobre o design de terror de Silent Hill 4, que quase não tem sustos.
- https://www.pcgamer.com/legend-of-grimrock-and-the-value-of-simple-input: artigo sobre entrada simples em Legend of Grimrock.
- https://rpgcodex.net/article.php?id=8470: citado para o movimento em grade do Grimrock.
- https://itch.io/devlog/293172/player-movement.amp: devlog sobre movimento do jogador, citado no trecho sobre grade.
- https://create.roblox.com/docs/workspace/camera: documentação de câmera do Roblox, com `CameraMode.LockFirstPerson`.
- https://create.roblox.com/docs/tutorials/use-case-tutorials/input-and-camera/control-the-users-camera: tutorial sobre controle da câmera do usuário no Roblox, com o LocalScript.
- https://mocaponline.com/blogs/mocap-news/character-rigging-basics-guide: blog sobre fundamentos de rigging, citado no trecho de orçamento de ossos.
- https://www.tech-artists.org/t/next-gen-console-bone-limits/3949: fórum Tech Artists sobre limite de ossos em consoles, citado para o intervalo de 100 a 175 ossos.
