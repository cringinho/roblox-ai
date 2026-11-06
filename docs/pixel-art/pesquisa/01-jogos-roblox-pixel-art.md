# Pixel art em experiências Roblox: 10 estudos de caso e arquitetura de integração

> Pesquisa de apoio ao guia de produção de **The Dark Altar** (jogo de cartas por turnos, gótico, com menus, fundos e VFX em pixel art dentro de `ScreenGui`).
> Coleta: 06/11/2026. Fontes: DevForum, Creator Hub (documentação oficial), páginas de jogos no roblox.com, rastreadores (RoTrends/RoWatcher), GitHub, guias de terceiros.

## Convenções de confiabilidade

- **Verificado**: confirmado em fonte primária (documentação oficial, post do próprio desenvolvedor, código-fonte, página oficial do jogo).
- **Parcial**: fonte secundária ou de terceiros (guias, rastreadores, wikis de fãs, trechos de resultado de busca) ou inferência minha, sempre explicitada como tal.
- **não verificado**: não encontrei fonte. Não usar como fato.

Notas de método:

- Wikis do Fandom (Doodle World, Loomian Legacy, Roblox Wiki) e TVTropes bloquearam o acesso direto (HTTP 402/403). Quando uso algo delas, vem de trecho de resultado de busca e está marcado como Parcial.
- Visitas e CCU de rastreadores variam conforme a data de captura. Use como ordem de grandeza.
- O código de *Pokémon Brick Bronze* analisado vem de um arquivo público mantido por fãs (não oficial, com conteúdo adicionado depois de 2018). Serve só para entender a arquitetura. **Não reutilize código nem arte de terceiros.**
- Nenhum jogo de cartas popular do Roblox com pixel art foi encontrado (ver tabela 1.2). As referências de arquitetura vêm de RPGs de batalha por turnos, jogos 2D em GUI e ferramentas da comunidade.

---

## 0. Achados mais acionáveis (resumo)

1. **Para UI, a nitidez de pixel art está resolvida**: `ImageLabel`/`ImageButton` têm `ResampleMode = Enum.ResamplerMode.Pixelated` (vizinho mais próximo) desde ago/2021. **Em 3D não está**: Decal, Texture, ParticleEmitter, Beam e MaterialVariant continuam com filtragem bilinear. O `ResampleMode` de SurfaceAppearance aparece na API, mas consta como "Pending" em out/2026.
2. **Arquitetura de sprite sheet orientada a dados** (padrão observado no código arquivado de Brick Bronze): uma tabela por animação com `sheets = {{id, rows}}`, `nFrames`, `fWidth`, `fHeight`, `framesPerRow`, `border = 1`. Cada folha fica com até 1024 px e a animação é dividida em várias folhas quando necessário. O quadro atual é calculado pelo **tempo de parede**, com uma única conexão `Stepped` para todos os sprites, e a **próxima folha é pré-carregada** num `ImageLabel` oculto.
3. **Limites que mordem**: imagens acima de 1024 px eram reduzidas silenciosamente no upload. Em jan/2026 o 4K chegou para MeshPart, SurfaceAppearance, Texture, Decal e MaterialVariant, mas não para UI: "2D UI textures" aparecem como "coming next" no Texture Streaming. Para `ScreenGui`, trate **1024×1024 como teto efetivo**.
4. **Mobile é o maior risco**: a Roblox confirmou (jul/2025) que a "texture block compression" é com perda e inevitável em algumas plataformas, e ela estraga pixel art de cores chapadas em `ImageLabel` Pixelated. `CanvasGroup` também reduz a resolução do conteúdo sob pressão de memória ou em níveis gráficos baixos.
5. **VFX em `ScreenGui` não usam `ParticleEmitter`**: partículas são objetos 3D e não renderizam em `ViewportFrame` (consenso da comunidade). O caminho é sprite sheet animado em `ImageLabel` ou um módulo de partículas 2D de UI. Flipbooks de `ParticleEmitter` (3D) têm limite de 30 fps, não aceitam `ResampleMode`, devem usar `FlipbookBlendFrames = false` em pixel art e podem ser desligados pelo cliente quando falta memória.
6. **Pipeline de arte citado pela comunidade**: Aseprite, Pixilart, Piskel, paint.net e GIMP (redimensionar com "Interpolation: None"), RPG Maker para bases de personagens, Blender com compositor de pixelização, After Effects exportando PNGs para impact frames, e Free Tex Packer ou Contact Sheet do Photoshop para montar flipbooks. Antes do upload, aplique **alpha bleed** (PixelFix e similares) para evitar contornos claros ou escuros.
7. **Raster por pixel** (EditableImage/CanvasDraw) já sustenta jogos com mais de 100 M de visitas (*The Powder Box*). Ainda assim tem custo: máximo de 1024×1024, orçamento de memória, a API precisa ser habilitada, `WritePixelsBuffer` é lento no mobile e só uma EditableImage é atualizada por frame no display. Use para efeitos dinâmicos (troca de paleta, dissolve), não para animar tudo.

---

## 1. Tabelas-resumo

### 1.1 Os 10 casos estudados

| # | Experiência | Criador | Popularidade (aprox.) | Onde há pixel art | Integração no Roblox (observada) | Confiabilidade |
|---|---|---|---|---|---|---|
| 1 | Pokémon Brick Bronze (histórico, 2016–2018) | Llama Train Studio (direção Lando64000, programação Tbradm) | cerca de 20 mil CCU nos fins de semana no auge; encerrado em 19/04/2018 | sprites animados de batalha (low-res, estilo Gen 6), menus | sprite sheets em várias folhas num `ImageLabel` com `ImageRectOffset/Size`; GUI (provável `SurfaceGui`) em Parts que olham para a câmera na cena 3D de batalha | Verificado (código arquivado por fãs) / Parcial (números) |
| 2 | Pixel Quest! | grupo "Pixel Quest!" (dev provável: majordev5) | 25,9 M visitas; pico de 8,4 mil CCU | mundo 2D inteiro (bullet hell), personagens, UI | jogo 2D completo; framework próprio "Forge2D" citado pelo dev; renderização não documentada | Parcial |
| 3 | The Powder Box (+ versão All Ages) | Ethanthegrand14 | 54,5 M + 122,5 M visitas; pico de 4 mil CCU (All Ages) | simulação inteira em pixels | raster por pixel com o módulo CanvasDraw (hoje sobre `EditableImage`) | Verificado |
| 4 | Starving Artists | Double Bandit Studios | cerca de 462,7 M visitas (terceiros) | quadros de pixel art pintados pelos jogadores | canvas em grade de pixels (implementação não verificada) | Parcial |
| 5 | The Campgrounds 2 | Ha1wen | pequeno (jogo de concurso, depois privado) | personagens, mapas, batalhas estilo Undertale | 100% `ScreenGui` | Verificado (post do dev) |
| 6 | "UNDERTALE UI-based game" | 1DiamondBor ("Bor") | pequeno (showcase) | overworld e menus estilo Undertale | 100% UI; mapa do Tiled exportado em Lua e desenhado em tiles de GUI; colisão com Frames | Verificado (post do dev) |
| 7 | GLOOM (horror 2D) | MorbidalDev | não lançado (demo cogitada) | tudo | "pequeno engine 2D com física" próprio; uso de sprite sheets perguntado e não respondido | Parcial |
| 8 | Pixle Platform [2D] e Don't Look (tutoriais) | violet_angxl | protótipos | tiles 18×18, sprites 30×30, fundo 144×72 | Parts invisíveis com `SurfaceGui`/`BillboardGui`, `ResampleMode` Pixelated e câmera lateral scriptada | Verificado (tutorial) |
| 9 | Engine de pixels e sprites estilo Mario Maker | PotatoVampire7797 | protótipo | sprites criados pelo jogador | Frames como pixels em `SurfaceGui` (1 a 64 Frames por Part), depois greedy meshing | Verificado (post do dev) |
| 10 | Pixel Game Project (devlogs) | MischieRaven | protótipo | tiles, personagem, árvores | Aseprite e Blender pixelizado; grid de Parts; tileset dual-grid | Verificado (devlogs) |

> Por que há protótipos na lista: dos *leads* populares sugeridos, vários **não usam pixel art** ou **não têm fonte** que confirme (tabela 1.2). Mantive os jogos populares confirmados (1 a 4) e completei com showcases do DevForum que **documentam a técnica**. Era o critério secundário pedido.

### 1.2 Leads investigados que ficaram de fora (ou só como referência)

| Lead | Achado | Status | Fonte |
|---|---|---|---|
| **Pixel Blade** (Frost Blade Games) | 267,9 M visitas, pico de 22,8 mil CCU, criado em 23/06/2024. Roguelite de ação em **3D com avatar Roblox** (legenda de screenshot: "Roblox guy holding a long flaming Katana in the main lobby"). Guias o descrevem como de visual "Minecraft-inspired" e "pixel-art universe" (trechos de busca, sem confirmação primária). Nenhum detalhe técnico encontrado. | estética pixel/voxel **não verificada**; técnica **não verificada** | [RoTrends](https://rotrends.com/game/6161049307/Pixel-Blade), [allthings.how](https://allthings.how/?p=285688), [Pocket Tactics](https://www.pockettactics.com/pixel-blade-weapons) |
| **Doodle World** (Doodle World Studios / wish_z) | cerca de 135 M visitas (rastreadores). Monstros 2D em batalhas por turnos, mas a página oficial diz "all the creatures are **hand-drawn**". | não é pixel art (2D desenhado à mão) | [roblox.com](https://www.roblox.com/games/5116869569), [créditos no DevForum](https://devforum.roblox.com/t/doodle-world-credits/1657176) |
| **Loomian Legacy** (Llama Train Studio) | cerca de 909,6 M visitas, pico de 23,3 mil CCU (RoTrends). Há indícios de **modelos 3D** para os Loomians: log de update cita "models... updated"; um artista se apresenta como "3D Generalist" do jogo. É o sucessor de Brick Bronze. | pixel art **não verificada**; provável migração de sprites para 3D | [RoTrends](https://rotrends.com/game/117307972/Loomian-Legacy) (trecho de busca), log no Fandom (trecho de busca) |
| **Undertale Test Place Reborn** | 185,9 M visitas, pico de 6,3 mil CCU, battlegrounds de luta. Estilo de arte não documentado. | não verificado | [RoTrends](https://rotrends.com/game/2916593387) |
| **Undertale: Last Corridor** / **Sans Multiversal Battles** | ULC: cerca de 39,3 M visitas. Nada sobre sprites ou pixel art. SMB: nada encontrado. | não verificado | [Bloxodes](https://bloxodes.com/stats/games/undertale-last-corridor-3958291198) |
| **Sol's RNG** | nenhuma fonte sobre VFX de auras com flipbook ou pixel art | não verificado | — |
| **Funky Friday** (Lyte Interactive) | ritmo com setas 2D na UI; nada sobre skins em pixel ou sprites | não verificado | [Roblox Wiki](https://roblox.fandom.com/wiki/Lyte_Interactive/Funky_Friday) (trecho) |
| **Literally FNF** (Dungeon Arcade) | cerca de 205 M visitas. Um dev no DevForum o cita como exemplo de "2D sprites on GUI instead of 3D models". Pixel art (Week 6) não verificada. | referência de sprites 2D em GUI | [RoTrends](https://www.rotrends.com/game/2422985977/Literally-FNF), [DevForum](https://devforum.roblox.com/t/how-to-do-2d-sprites-easily/3193539) |
| **Arcane Lineage** | RPG por turnos; nenhuma fonte sobre pixel art na UI | não verificado | — |
| **The Strongest Battlegrounds / Jujutsu Shenanigans** | não é pixel art. A técnica de *impact frames* aparece em §4.14. | só técnica | threads do DevForum (§4.14) |
| **Anime Card Battle / Anime Card Clash** | jogos de cartas (TCG); nenhuma evidência de pixel art | não verificado | [Sportskeeda](https://sportskeeda.com/roblox-news/anime-card-battle-ranked-guide) |
| **Pixel Pets!** (Pixy Palace) | "All 645 Pixel Art made by hand from me!". Batalha de criaturas em pixel art, popularidade desconhecida | pixel art confirmada; técnica e números não verificados | [roblox.com](https://www.roblox.com/games/90486354692269) |
| **Draw & Donate** (Bidaz; programação PondazYeah) | canvas de desenho feito com o módulo CanvasDraw (pixel-based); mais de 8 M de visitas (snapshot de perfil) | referência para canvas por pixel | [CanvasDraw](https://devforum.roblox.com/t/canvasdraw-a-custom-pixel-based-game-engine/1624633), [roblox.com](https://www.roblox.com/games/17070253881/Draw-Donate) |
| **2D PIXEL RPG** (BlockByte Studio), **Pix-art** (Quincy's Games) | RPG 2D em pixel e jogo de desenho em grade de pixels; sem números nem técnica | pequeno / não verificado | [2D PIXEL RPG](https://www.roblox.com/games/18893183789/2D-PIXEL-RPG), [Pix-art](https://www.roblox.com/games/71053628284433) |

---

## 2. Fichas por jogo

### 2.1 Pokémon Brick Bronze (histórico): sprites de batalha por sprite sheet

**Identificação**

- Criador: Llama Train Studio. Diretor Lando64000; scripting principal de Tbradm ([namu.moe](https://namu.moe/w/pbb), Parcial; créditos também em espelho da Wikipedia via trecho de busca).
- Popularidade: cerca de 20 mil jogadores simultâneos nos fins de semana no início, caindo para a faixa dos 6 mil em 2017–2018 ([namu.moe](https://namu.moe/w/pbb), Parcial).
- Encerrado em 19/04/2018, após reclamações de copyright da Nintendo e da The Pokémon Company ([namu.moe](https://namu.moe/w/pbb), Parcial). Sucessor: Loomian Legacy (2019).
- Link: o jogo original não existe mais.

**Onde há pixel art**

- Sprites animados das criaturas em batalha, de frente, de costas e shiny.
- Um usuário do DevForum descreve: "Pokemon Brick Bronze had the pokemon's pixel art in the game when fight scenes..." ([DevForum, 2023](https://devforum.roblox.com/t/putting-2d-character-sprites-in-a-game/2481297), Parcial).
- Um agregador de sprites feito por fãs descreve o acervo como "Gen 6 (XY/ORAS) style" ([GitHub](https://github.com/AmexOfficial24/PokemonBrickBronzeSpriteScraper), Parcial).
- Nos dados, os quadros têm cerca de 40 a 140 px de lado: sprites de baixa resolução.

**Pipeline de produção**

- Origem e ferramenta dos sprites: não verificado.
- Os dados mostram animações frame a frame com **muitos quadros**: Abra 79, Litten 29, Snorlax 28. Isso é compatível com GIFs convertidos em folhas (inferência).
- Não há indício de upscale. Os quadros são usados no tamanho nativo e escalados no motor.

**Integração no Roblox (código arquivado por fãs, [OpenBronze](https://github.com/singharaj-usai/OpenBronze), descrito como "port do codebase de Brick Bronze para Rojo")**

- **Módulo `AnimatedSprite`** ([fonte](https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/AnimatedSprite.lua), Verificado como código, não como original de 2016):
  - Anima um `ImageLabel` (ou `ImageButton`) trocando `Image`, `ImageRectOffset` e `ImageRectSize`.
  - Posição do quadro: `col, row = frame % framesPerRow, floor(frame / framesPerRow)`. O offset é `col*(fWidth+border), row*(fHeight+border) + startPixelY`.
  - **`border` padrão = 1 px** entre quadros.
  - **Várias folhas por animação**: cada folha cobre `rows*framesPerRow` quadros, e o índice global é convertido em folha mais posição local.
  - **Timing por relógio**: `frame = floor((tick()-startTime)/speed*relativeSpeed) % nFrames + 1`. O padrão é `speed = 0.03` s por quadro (cerca de 33 fps). Se houver lag, quadros são **pulados** em vez de a animação ficar lenta. O quadro só é reatribuído quando muda.
  - **Uma única conexão `Stepped`** atualiza todos os sprites ativos e é desconectada quando não há nenhum. Sprites invisíveis são ignorados (`if not Visible then return`). O sprite se remove sozinho quando `Parent == nil`.
  - **Pré-carregamento**: quando há mais de uma folha, cria um `ImageLabel` filho de 1×1 px com `ImageTransparency = 0.9`, que carrega antecipadamente a **próxima** folha.
  - Não há suporte a espelhamento (flip).
- **Tabela de dados `Spritesheets`** ([fonte](https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Data/Spritesheets.lua)). Exemplos reais:
  - `['Litten']={sheets={{id=620436374,rows=2},},nFrames=29,fWidth=55,fHeight=58,framesPerRow=18}`
  - `['Unown-b']={sheets={{id=606623397,rows=5},},nFrames=79,fWidth=63,fHeight=63,framesPerRow=16,inAir=.6}`
  - Campos opcionais: `speed`, `scale`, `inAir`. A maioria usa de 1 a 4 folhas; animações longas chegam a 13–17 folhas.
  - *Análise minha*: com `border = 1`, Litten ocupa 18×(55+1) = **1008 px** de largura e Unown-b 16×(63+1) = **1024 px**. O `framesPerRow` foi escolhido para caber em 1024 px.
- **Sprite na cena de batalha** ([fonte](https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/Battle/Sprite.lua)):
  - A batalha é uma **cena 3D**. Cada criatura é uma Part com GUI filha cujo `CanvasSize` é o tamanho do quadro. O fato de ser uma `SurfaceGui` é inferência.
  - Tamanho em studs: `fWidth/25*scale`, ou seja **25 px por stud**.
  - Em `RenderStep` (prioridade Last), a Part é reorientada para a câmera **apenas no plano XZ**, um billboard que só gira em yaw.
  - A chave do sprite combina `_SHINY` com `_BACK`/`_FRONT`. **Variantes de cor são folhas separadas, não troca de paleta em runtime.**

**Técnicas que valem copiar**

- Entrada do monstro: o tamanho cresce de 0 enquanto `ImageColor3` vai de preto a branco.
- Desmaio: o sprite encolhe, escurece (`ImageColor3`) e desce.
- "Drag out": desliza e some com `ImageTransparency`.
- Mega evolução: tinta preta e depois volta ao normal.
- Câmera com tremor senoidal: `CFrame.new(0, math.sin(et*50)*mag, 0)`.
- HP bar animada com `animateHP` e tempos mínimos por golpe (cerca de 1 s em multi-hit) ([Actions.lua](https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/Battle/Actions.lua)).

**Lacunas**

- Não sei se o código arquivado é idêntico ao de 2016–2018. Há IDs de assets de 2021 a 2023 e formas regionais posteriores, sinal de continuação por fãs.
- `ResampleMode` não aparece (é anterior a 2021, então era provavelmente bilinear).
- O código de piscar ou flash ao levar dano não foi encontrado nos arquivos lidos.

---

### 2.2 Pixel Quest!: MMORPG 2D bullet hell em pixel art

**Identificação**

- Grupo "Pixel Quest!" ([página](https://www.roblox.com/games/80003276594057/Pixel-Quest), comunidade 35806564).
- Popularidade: 25,9 M visitas, pico de 8,4 mil CCU, 361,6 mil favoritos, criado em 30/03/2025 ([RoTrends](https://www.rotrends.com/game/7458874788/Pixel-Quest-GUILDS), Parcial).
- Lançamento amplo em 22/10/2025, para PC e mobile, com console planejado ([allthings.how](https://allthings.how/pixel-quest-on-roblox-bullet-hell-mmo-basics-permadeath-early-tips), Parcial). A página atual exibe a tag "[CONSOLE]".

**Onde há pixel art**

- O jogo inteiro. Descrição oficial: "Pixel Quest is a 2D Open World RPG focusing on Bullet Hell combat with Roguelike elements" e "pixelated world".

**Pipeline e integração**

- Um thread do DevForum de 2023, de majordev5, intitulado "Pixel Quest - 2D RPG Game", diz que o jogo é inspirado sobretudo em *Realm of the Mad God*.
- O autor credita o próprio framework 2D, **"Forge2D"**: "made making this game so much easier". Ele pretende liberá-lo, e em nov/2025 houve um pedido de atualização do plugin ([DevForum](https://devforum.roblox.com/t/pixel-quest-2d-rpg-game/2310608)).
- *Ressalva*: a ligação entre esse thread e o jogo publicado não é oficial. O nome e a inspiração coincidem com a descrição de bullet hell (Parcial).
- Feedback técnico no thread: desativar a playerlist padrão, já que o jogo tem uma própria; não deixar o painel de item "pular", pois isso atrapalha os botões.
- Não verificado: render em `ScreenGui` ou em 3D com câmera ortográfica, resolução nativa, uso de `ResampleMode`, sprite sheets, paleta.

**Técnicas que valem copiar**

- Escala multiplataforma: WASD e mouse no PC; toque para mover e mirar no mobile, com tutorial de gestos ([allthings.how](https://allthings.how/pixel-quest-on-roblox-bullet-hell-mmo-basics-permadeath-early-tips)).
- Investir num framework 2D próprio antes do conteúdo.

---

### 2.3 The Powder Box (e All Ages): simulação em pixels com CanvasDraw/EditableImage

**Identificação**

- Criador: Ethanthegrand14.
- Versão principal: 54,5 M visitas, pico de 674 CCU (mai/2026), lançada em mar/2022 ([RoWatcher](https://rowatcher.com/games/3458415923/the-powder-box)).
- Versão All Ages: 122,5 M visitas, pico de 4 mil CCU (ago/2025), lançada em nov/2024 ([RoWatcher](https://rowatcher.com/games/6787644864/the-powder-box-all-ages)).
- Tem um port para PC no itch.io ([itch](https://ethanthegrand.itch.io/the-powder-box-pc-edition)).

**Onde há pixel art**

- Toda a área de jogo é uma grade de pixels simulada no estilo *falling sand*, inspirada em Powder Game e Noita.

**Pipeline e integração**

- O autor construiu o jogo para testar o próprio módulo de canvas: "my performant canvas module" que permite "high-resolution pixel-based games" ([DevForum, 2022](https://devforum.roblox.com/t/feedback-on-2d-powder-and-fluid-simulation-sandbox-game/1736128)).
- Na época do post, alegava 700 a 1,3 mil CCU médios e mais de 18 M de visitas. Disse não ter visto antes "a 2D game on roblox reach over 1000 players".
- Simulação simples: "no forces... no velocity or even momentum", e cada partícula desce 1 pixel por frame. Houve otimizações grandes em 31/03/2022. Suporte a mobile e tablet chegou em 10/04/2022.
- **CanvasDraw** ([DevForum](https://devforum.roblox.com/t/canvasdraw-a-custom-pixel-based-game-engine/1624633), versão 4.20.2, atualizado em 10/2026):
  - Hoje é "the largest and fastest custom graphics library in roblox utilising **EditableImage**".
  - Na versão 2.0 deixou de representar pixels como Frames: "A pixel is no longer represented as a physical frame object".
  - Canvas de até 1024×1024 (2048 em plugins). Tem primitivas, `DrawImage`, fonte bitmap e saída para Gui, SurfaceGui, BillboardGui, Decal, Texture e MeshPart.
  - Limites citados:
    - Usuários sem certos requisitos não podem usar `EditableImage` em experiências publicadas.
    - Há orçamento de memória.
    - `AutoRender` vem ligado e atualiza a cada frame; desligue quando houver vários canvases.
    - `CreateImageContent()` gera saída estática sem custo contínuo.
  - Outros jogos listados com CanvasDraw: *Draw and Donate* (PondazYeah), um jogo de pesca 3D, raytracer e player de GIF.

**Técnicas que valem copiar**

- Use canvas por pixel só quando o conteúdo **precisa** ser gerado ou alterado por pixel (simulação, desenho, troca de paleta).
- Para arte estática, gere o resultado uma vez e congele.

---

### 2.4 Starving Artists: pixel art criada pelos jogadores

**Identificação**

- Double Bandit Studios ([página](https://www.roblox.com/games/8916037983/starving-artists)).
- Cerca de 462,7 M visitas e 1,3 M favoritos, lançado em fev/2022 (game.guide via trecho de busca, Parcial).
- Recebeu integração de marca da Gamefam ("PixoBitz"), com mais de 108 M de "engagements" ([Gamefam](https://www.gamefam.com/case-study-pixobitz)).

**Onde há pixel art**

- Jogadores pintam pixel art em canvases de grade e vendem as obras, ligadas a itens de roupa. Fontes: guia da earnaldo (trecho de busca) e a ferramenta de terceiros "PhantomCanvas", que se anuncia como "pixel art tracer for Starving Artists" e aceita PNG de 50×50 ([itch.io](https://brainjoose.itch.io/phantomcanvas)).
- O tamanho exato do canvas **não foi verificado**.

**Integração no Roblox**

- **Não verificada**: Frames por pixel, EditableImage ou outra coisa.
- Existem bots de pintura que "simulates mouse clicks" sobre o canvas, com risco de banimento ([GitHub](https://github.com/Luois45/roblox-starving-artists-bot/blob/main/README.md)). Isso indica que a pintura é feita célula a célula via UI.

**O que tirar daqui**

- Pixel art como **conteúdo gerado pelo usuário** sustenta um dos maiores jogos de "donation". A grade de pixels em si é uma mecânica.

---

### 2.5 The Campgrounds 2: RPG 2D feito só com ScreenGuis

**Identificação**

- Ha1wen, jan/2023, feito para um concurso organizado por Jackeryz. Depois ficou privado por causa de bugs ([DevForum](https://devforum.roblox.com/t/the-campgrounds-2d-rpg-story-game-roblox-undertale/2131536)).

**Onde há pixel art**

- Personagens, mapas e batalhas com esquiva no estilo Undertale.

**Pipeline**

- "I used RPG Maker's character generator and map maker for the pixel art."
- "most of the sprites and maps were made with RPGMaker and then slightly altered in paint.net". A GUI também foi feita no paint.net.
- Áudio possivelmente no Beepbox (suposição de um avaliador).

**Integração**

- "made entirely with ScreenGuis". Estrutura interna, `ImageRectOffset` e `ResampleMode` não são descritos.

**Lições do feedback**

- Os avaliadores elogiaram o polimento ("doesn't even look like a ROBLOX game").
- Também apontaram que a **UI não combinava com a pixel art**; o próprio dev concordou que a GUI parecia "sloppy and out of place".
- Pediram: prompt de interação, NPCs virando para o jogador, autosave, opções de velocidade de texto e controles que funcionem com mouse e teclado no input de nome.
- Lição: **a UI precisa ser desenhada na mesma grade e paleta da arte**.

---

### 2.6 "UNDERTALE UI-based game" (1DiamondBor): pipeline Tiled → Lua → GUI

**Identificação**

- Bor (1DiamondBor). Post de 18/02/2025, grande update em 13/03/2025 ([DevForum](https://devforum.roblox.com/t/undertale-ui-based-game-in-roblox/3484839)).

**Onde há pixel art**

- Overworld, caixas de texto e menus de batalha no estilo Undertale.

**Pipeline e integração**

- Mapas feitos no **Tiled**, que exporta arquivos Lua lidos por um ModuleScript.
- O desenho "loops through the width and height of the map, gets the specific tile that belongs in that spot".
- Camadas de tile atualizam a camada do objeto do jogador.
- Colisão com "half-transparent frames with their size and position set to the size & position of the objects in the tiled map, in pixels". Só retângulos.
- Stats enviados ao cliente "every frame using an UnreliableRemoteEvent".
- Texto tremido: posição com `UDim2.fromOffset(base.X + offset_x, base.Y + offset_y)`.
- Sugestão de um comentarista: normalizar o movimento diagonal com `Vector2.Unit`.
- `ResampleMode`: não mencionado.

**Técnicas que valem copiar**

- Usar um editor de níveis externo (Tiled) e **importar dados**, não montar a tela à mão.
- Fazer o *shaky text* com offsets inteiros.

---

### 2.7 GLOOM (MorbidalDev): horror 2D em pixel art

**Identificação**

- MorbidalDev. Primeiro post em nov/2022 ([DevForum](https://devforum.roblox.com/t/ive-been-working-on-a-2d-horror-game-in-roblox-what-do-you-guys-think/2066090)). Retomado como "GLOOM" em nov/2024 ([DevForum](https://devforum.roblox.com/t/2d-horror-game-in-roblox-pixel-art/3246131)).
- Cogitou liberar cerca de 20 minutos de demo.

**Pipeline e integração**

- "Made a little 2D Engine with some physics and Made the pixel art for the game."
- Alguém perguntou "did you only used sprite sheets for those animations?" e não houve resposta.
- Comentaristas acharam que era Godot, Unity ou Unreal.
- Ferramentas, resolução e `ResampleMode`: não verificado.

**O que tirar daqui**

- Prova de que a pixel art 2D, com iluminação e atmosfera de horror, **pode não parecer "Roblox"**. Isso interessa à direção gótica de The Dark Altar.

---

### 2.8 Pixle Platform [2D] e Don't Look (violet_angxl): tutoriais de 2D pixelado

**Identificação**

- violet_angxl, out/2023.
- [Tutorial de plataforma](https://devforum.roblox.com/t/how-to-make-a-roblox-game-2d-pixlated-pixel-platformer/2630038) e [tutorial de horror](https://devforum.roblox.com/t/how-to-make-a-roblox-game-2d-pixlated-horror-game/2628506). Os jogos de exemplo não foram concluídos.

**Pipeline**

- Arte em **Pixilart**.
- Tiles de **18×18**, personagens de **30×30**, fundo de **144×72**.
- Upload em resolução nativa, sem upscale prévio.

**Integração (2D falso dentro do mundo 3D)**

- Tiles são Parts de 4×4×4, invisíveis e com colisão, com uma `SurfaceGui` e um `ImageLabel` (`ScaleType` Crop).
- O jogador usa uma `BillboardGui` (`ScaleType` Fit). No horror, `AlwaysInFront`.
- O fundo é uma `BillboardGui` grande sobre uma Part.
- **`ResampleMode = Pixelated`** em todos os `ImageLabel`.
- Câmera `Scriptable`, seguindo com lerp e offset fixo (0, 0, −35) ou (0, 0, −17).
- `PlayerModule` reduzido a esquerda e direita.
- Aviso do autor: muitas `BillboardGui` "will make your game laggy!"; para jogos grandes, prefira `SurfaceGui`.

**Relevância para The Dark Altar**

- Baixa para menus, que são `ScreenGui`.
- Útil se houver cenas com personagens 2D num diorama 3D, à maneira de Brick Bronze.

---

### 2.9 Engine de pixels e sprites estilo Mario Maker (PotatoVampire7797)

**Identificação**

- PotatoVampire7797, jun–jul/2022 ([DevForum](https://devforum.roblox.com/t/working-on-a-pixelsprite-engine-for-roblox/1852195)).

**Integração**

- "Each part has a surface gui with 1-64 frames on it depending on the shape of the sprite": cada Frame é um pixel.
- Problemas:
  - Elementos fora da tela somem conforme `AbsolutePosition`, o que causa flicker nas bordas.
  - Debate sobre limite de objetos de UI. Um participante lembrou que já houve limite para impedir "pixels de Frame" que burlassem a moderação de decals.
  - "Roblox's UI isn't very performant."
- Solução adotada: **greedy meshing** por linhas, que reduziu cerca de 60% dos assets e roda a cada tick.

**Lição**

- A técnica "Frame como pixel" é **legado**. Hoje `EditableImage` (via CanvasDraw ou similar) substitui esse uso.

---

### 2.10 Pixel Game Project (MischieRaven): Aseprite + Blender pixelizado

**Identificação**

- MischieRaven, 11 devlogs entre set e out/2024 ([DevForum](https://devforum.roblox.com/t/pixel-game-project-dev-logs/3142416)).

**Pipeline**

- **Aseprite** para os tilesets à mão.
- Tileset de 128×128, depois 128×160: tiles de 32 px num **dual-grid de 16 tiles** ("only have to make a few tile maps instead of hundreds").
- Personagem com tamanho real de **96×96**, cerca de "three tiles tall".
- **Blender** para modelos 3D pixelizados via nós do compositor (adaptado de um tutorial do CBaileyFilm). Geometry nodes deixam as folhas sempre viradas para a câmera.
- Migrou parte da produção para o Blender porque iterar cores à mão era lento.

**Integração**

- Grid scriptado de Parts de 4×0,001×4.
- O autor alerta que um jogo em pixel "is not very optimized for Roblox Studios".

**Lição**

- Separar a produção em **tiles autotile (dual-grid)** reduz a quantidade de arte.
- Pré-renderizar 3D como pixel art (Blender) é uma via de produção para fundos e VFX.

---

## 3. Padrões de arquitetura recorrentes

### 3.1 Quatro formas de colocar pixel art no Roblox

| Modo | Exemplos | Nitidez | Custos e riscos |
|---|---|---|---|
| **A. `ImageLabel`/`ImageButton` em `ScreenGui`** | Campgrounds, Bor, UI em geral | `ResampleMode` Pixelated, nativo | compressão no mobile; `CanvasGroup` reduz resolução; 1024 px; flicker de carregamento |
| **B. GUI em Part (`SurfaceGui`/`BillboardGui`)** | Brick Bronze (batalha), tutoriais da violet_angxl | Pixelated funciona porque continua sendo `ImageLabel` | muitas Billboard ou SurfaceGui pesam; uma `SurfaceGui` fica "weird" a cerca de 20 studs ([thread](https://devforum.roblox.com/t/add-a-resamplemode-to-decals-textures-surfaceappearance/4399698)) |
| **C. Raster por pixel (`EditableImage`/CanvasDraw)** | The Powder Box, Draw & Donate | controlado pelo código (`SamplingMode` Pixelated em `DrawImageTransformed`) | máximo de 1024×1024; orçamento de memória; API precisa ser habilitada; `WritePixelsBuffer` lento e não thread-safe; uma atualização por frame no display |
| **D. Textura 3D (Decal, Texture, MeshPart, SurfaceAppearance, ParticleEmitter, Beam)** | voxel e Minecraft-like; flipbooks de partículas | **bilinear forçado**; o workaround é upscale com vizinho mais próximo (10×) | memória alta, ainda com leve blur, seams de mipmap; `ResampleMode` de SurfaceAppearance "Pending" |

### 3.2 Sprite sheet orientado a dados (o "padrão Brick Bronze")

- Um registro por animação, por exemplo `{sheets = {{id, rows}, ...}, nFrames, fWidth, fHeight, framesPerRow, border, speed, scale}`.
- Um módulo genérico converte o índice global em folha e (col, row), depois em `ImageRectOffset`, com `ImageRectSize = (fWidth, fHeight)`.
- Variantes (shiny, costas, formas) são **chaves diferentes** que apontam para folhas diferentes.
- Ferramentas da comunidade fazem a mesma conta: SpriteClip/SpriteClip2 (`spriteSize`, `spriteCount`, `columnCount`, `frameRate`), EasySprite (`textureSize`, `cellSize`, `flip()`), SimpleSprite e LUASprites (gera folha e código Lua a partir de PNGs ou GIFs). Ver §4.15.

### 3.3 Relógio único e tempo de parede

- O índice do quadro vem de `(agora − início)/duração_do_quadro`. Com lag, pula quadros em vez de desacelerar (Brick Bronze).
- Use **um** loop para todos os sprites: um `Stepped` em Brick Bronze; o Scheduler do SpriteClip2, com `Pause/Resume` global ("e.g. pause menus").
- Pule sprites invisíveis e destrua os órfãos. O SpriteClip original iterava todos os clips; o SpriteClip2 corrigiu isso. Um teste com 250 labels deu cerca de 3–4% de CPU.
- Taxas usadas:
  - Brick Bronze: cerca de 33 fps (0,03 s) por padrão, alguns a 25 fps.
  - SpriteClip: `FrameRate` precisa ser divisor de 60.
  - SpriteClip2: padrão 30, limitado pelo `RenderStepped`.
  - Flipbook de `ParticleEmitter`: máximo de 30 fps.

### 3.4 Como contornar o limite de 1024 px

- Escolher `framesPerRow` para caber em 1024 px. Litten: 18×56 = 1008. Unown-b: 16×64 = 1024.
- **Dividir em várias folhas** (Brick Bronze chega a 17) e pré-carregar a próxima.
- Separar folhas grandes por animação (plano citado num thread de fan-game de FNF com folhas de 6660×832 e 8192×4096).
- Conferir a resolução real do asset depois do upload: `https://assetdelivery.roblox.com/v1/asset/?id=<id>` (dica do autor do SpriteClip).
- Em partículas: layouts `Custom` de flipbook permitem folhas não quadradas e sem potência de 2. O FAQ do anúncio dá o exemplo de uma textura de 4096×4096 com uma grade de 32×8 quadros de 128×512 (ver §4.8).

### 3.5 Nitidez: Pixelated, escala inteira e DPI

- `ResampleMode = Pixelated` só existe em GUI (e VideoDisplay).
- Em 3D, faça upscale com vizinho mais próximo antes do upload: GIMP com "Interpolation: None" até 1024; Aseprite cerca de 10×; voxel de 32×32 para 320×320.
- Escala **inteira** de quadros na tela evita "mixels". Converta Scale em pixels com `AbsoluteSize` e `math.round` ([thread](https://devforum.roblox.com/t/integer-scaling/3924311)).
- **DPI**: o `AbsoluteSize` da UI está em pontos lógicos (iPhone X: 812×375 em vez de 2436×1125), e o motor renderiza a UI cerca de 3× maior ([post de 2018](https://devforum.roblox.com/t/ui-is-really-really-really-weird-on-mobile/95626)). *Inferência minha*: a escala inteira deve ser calculada em pontos lógicos; em aparelhos com fator de DPI fracionário, pode haver pequenas irregularidades. Teste no Device Emulator e em aparelho real.

### 3.6 VFX: flipbook em UI versus `ParticleEmitter`

- Em `ScreenGui`, os VFX são **sprite sheets animados em `ImageLabel`**, com o mesmo módulo de 3.2 e 3.3. Partículas de UI usam módulos 2D (rParticle, EmitYourParticle, Emitter2D, UI Particle); o UI Particle ainda **não suporta flipbook** ([thread](https://devforum.roblox.com/t/ui-particle-an-unoptimized-module-to-integrate-particleemitters-into-your-ui-with-minimal-coding/4004649)).
- `ParticleEmitter` (3D) tem flipbook nativo: Grid2x2, 4x4, 8x8 ou Custom; modos Loop, OneShot, PingPong e Random; `FlipbookStartRandom`; `FlipbookBlendFrames`. Para pixel art, desligue o crossfade.
  - Precisa de espaçamento entre quadros, e mais ainda por causa do mip filtering.
  - Não aceita `ResampleMode`.
  - Não aparece em `ViewportFrame`.
  - Pode ser desativado pelo cliente quando falta memória.
- *Impact frames* para cutscenes: a comunidade gera sequências de PNG (por exemplo no After Effects) e toca como vídeo. Problema relatado: buffering na primeira execução; ver §4.12.

### 3.7 2D "puro" em GUI exige framework próprio

- Os casos com mais ambição (Pixel Quest, GLOOM, Bor) escreveram engine ou framework próprio: Forge2D, "little 2D engine", leitor de mapas do Tiled.
- Opções públicas: Nature2D (física para elementos de UI, Verlet), Upside Engine (engine 2D, lançado em abr/2023), CanvasDraw e OSGL (raster). Ver §4.15.
- Comentário típico (dez/2021): "working with GUI objects is a pain" e "loading images are really technical". A sugestão no mesmo post é fazer o jogo em 3D com câmera que pareça 2D. Outro participante (jan/2024) alerta que atualizações do Roblox podem quebrar UIs complexas ([thread](https://devforum.roblox.com/t/is-it-possible-to-make-a-fully-2d-game-on-roblox/1529211)).

### 3.8 Pré-carregamento e cache

- Brick Bronze mantém um `ImageLabel` oculto (1×1, transparência 0,9) com a **próxima** folha.
- A comunidade relata que `PreloadAsync` não garante a carga e que a imagem precisa ser **exibida uma vez** antes de `IsLoaded`/`Loaded` virar true ([feedback de doc, 2026](https://devforum.roblox.com/t/feedback-on-contentproviderpreloadasync/4350350)).
- Use folhas em vez de dezenas de imagens soltas: 1 carga em vez de 40 ([thread](https://devforum.roblox.com/t/putting-2d-character-sprites-in-a-game/2481297)).

### 3.9 Feedback de combate ("juice") observado

- Brick Bronze:
  - Entrada com escala crescente e tinta preta clareando (`ImageColor3`).
  - Desmaio encolhendo, escurecendo e descendo.
  - Câmera com tremor senoidal (`sin(t*50)*mag`).
  - Tempos mínimos entre golpes.
- Bor: *shaky text* por offset.
- Campgrounds: esquiva em caixa (bullet hell) estilo Undertale.
- Combate 3D (TSB/JJS e similares): *impact frames* com ColorCorrection de contraste extremo, Highlight e partículas, e *hit-stop* via `AnimationTrack:AdjustSpeed(0)`. Ver §4.14.

### 3.10 Variações de cor e paleta

- Brick Bronze e Loomian Legacy tratam variantes raras (shiny, gleam) como **assets separados**. Em Brick Bronze, são folhas `_SHINY`.
- `ImageColor3` só tinge de forma multiplicativa (não clareia além da cor original). Serve para escurecer ou tingir, não para "flash branco".
- Troca de paleta em runtime: só via `EditableImage`, lendo o buffer, remapeando e escrevendo. **Não encontrei jogo que faça isso**; é viável segundo a API (§4.10).

### 3.11 Implicações práticas para *The Dark Altar* (recomendações derivadas, não fatos de fonte)

1. **Toda pixel art de menu, fundo, carta e VFX em `ImageLabel`/`ImageButton` com `ResampleMode = Enum.ResamplerMode.Pixelated`.** Não dependa de Decal, Texture ou `ParticleEmitter` para arte que precisa ser nítida.
2. **Resolução base virtual e escala inteira.** Desenhe na resolução nativa e calcule `escala = floor(min(AbsoluteSize.X/baseW, AbsoluteSize.Y/baseH))` a partir do `AbsoluteSize` do `ScreenGui` raiz (em pontos lógicos). Arredonde posições e tamanhos em Offset e use letterbox. Para molduras e painéis, use 9-slice (`ScaleType = Slice`, `SliceCenter`) com `SliceScale` inteiro.
3. **Pipeline de sprite sheet no padrão Brick Bronze**:
   - Tabela de metadados por animação; folhas de até 1024×1024.
   - Gutter de pelo menos 1 px; dimensões exatas, porque uma folha de 799 px em vez de 800 causou tremor de cerca de 0,25 px por quadro.
   - Relógio único; pausa global (serve para hit-stop e menus); pré-carregar a próxima folha.
4. **Mobile primeiro.**
   - Teste em aparelho real cedo: a compressão de bloco é com perda e "unavoidable" (Roblox, 2025).
   - Se a arte chapada degradar, teste upscale com vizinho mais próximo de 2× ou 4× nos assets críticos, pesando a memória. *Hipótese não verificada*: alinhar cada pixel de arte a blocos 4×4 de compressão reduz artefatos. Pelo mesmo motivo, alinhe quadros a múltiplos de 4 px.
5. **Evite `CanvasGroup` grande** em telas de pixel art, porque ele reduz a resolução do conteúdo. Use só em fades curtos e pequenos, ou faça o fade por elemento.
6. **VFX de UI como flipbook em `ImageLabel`.**
   - Flash branco: desenhe quadros "silhueta branca" na folha, já que `ImageColor3` não clareia.
   - Shake: offsets inteiros num Frame raiz.
   - Hit-stop: pausar o scheduler por alguns quadros.
   - Partículas de UI: módulo 2D com `ImageLabel`s Pixelated.
7. **PNG de 32 bits com alpha bleed** (PixelFix e similares). Não passe por otimizadores que convertem para 8 bits/paleta.
8. **Moderação**: suba cedo; não ponha texto minúsculo dentro das imagens (prefira `TextLabel`); guarde os fontes. Relatos de pixel art recusada por engano existem, e o caminho é apelar, não reenviar em massa.
9. **Paletas e variações** (cartas raras, maldições, estados): prefira folhas pré-renderizadas. Use `EditableImage` só para poucos efeitos dinâmicos, com a API habilitada e de olho no orçamento de memória.
10. **Fundos góticos com profundidade**: considere pré-renderizar 3D como pixel art no Blender (compositor de pixelização) e em camadas para parallax em `ScreenGui`. O padrão vem do Pixel Game Project.

---

## 4. Lições gerais da comunidade (com URLs)

### 4.1 Nitidez e `ResampleMode`

- **Anúncio (16/08/2021)**: propriedade `ResampleMode` em `ImageLabel` e `ImageButton`; `Default` é bilinear e `Pixelated` é vizinho mais próximo. A própria Roblox avisa que o vizinho mais próximo causa aliasing e "shimmering" ao **reduzir**, então use Pixelated para **ampliar** ([anúncio](https://devforum.roblox.com/t/resamplemode-new-property-for-image-gui-objects/1418681)). A doc confirma: "the image preserves the sharp edges of pixels" ([ImageLabel](https://create.roblox.com/docs/reference/engine/classes/ImageLabel)).
- **Instâncias com e sem suporte (jul–out/2026)**: só `ImageButton`, `ImageLabel` e `VideoDisplay`. `ParticleEmitter`, `ViewportFrame`, `MaterialVariant`, `Texture` e `Decal` ficam "stuck as the default bilinear" ([pedido](https://devforum.roblox.com/t/add-resamplemode-for-all-instances-that-render-images/4751910)). Um comentário de out/2026 diz que Decal e Texture já teriam ganhado suporte, mas é **não verificado**.
- **SurfaceAppearance**: pedido de out/2025. Um staff já disse que Decal e Texture legados não podem ganhar o recurso por compatibilidade, e um engenheiro explicou que SurfaceAppearance usa outro pipeline ([thread](https://devforum.roblox.com/t/pixelated-resamplemode-for-surfaceappearances-pixel-art-meshes/4028314)). A referência da API registra `SurfaceAppearance.ResampleMode` desde a release 716 ([robloxapi](https://robloxapi.github.io/ref/class/SurfaceAppearance.html)). Fóruns de ago/2026 ainda a descrevem como "Pending".
- **Workarounds em 3D**:
  - Upscale com vizinho mais próximo antes do upload, até 1024 ([solução](https://devforum.roblox.com/t/how-to-make-pixel-art-less-blurry-solution/3140843); [thread de 2021](https://devforum.roblox.com/t/how-would-i-go-about-making-a-pixelart-game-in-roblox/1416335), onde o autor fazia cerca de 10× no Aseprite ou paint.net).
  - `SurfaceGui` com `ImageLabel` Pixelated ([thread](https://devforum.roblox.com/t/pixel-style-textures-being-blurred/2790436)).
  - Custos: um jogo voxel precisou levar texturas de 32×32 para 320×320. O upscale "consumes excessive amounts of memory and the textures still have a slight blur", e há seams de mipmap que exigem dilatação de borda ([pedido de 2026](https://devforum.roblox.com/t/add-a-resamplemode-to-decals-textures-surfaceappearance/4399698)).
- **Regressão**: em jan/2026, Pixelated passou a aparecer borrado no Studio 0.702. A correção foi um rollback de configuração, bastando reiniciar ([bug](https://devforum.roblox.com/t/resample-mode-enumresamplermode-pixelated-appears-blurry/4227459)). Se a arte borrar de repente, verifique a versão do Studio antes de mexer nos assets.
- **Tutorial (nov/2025)**: Pixelated com `ScaleType` Fit; exportar na resolução que vai aparecer na tela; checar no Device Emulator ([tutorial](https://devforum.roblox.com/t/how-to-make-pixel-art-look-less-blurry/4051703)).

### 4.2 Limite de resolução e redução silenciosa

- Historicamente, o upload máximo era 1024×1024 e imagens maiores eram reduzidas sem aviso ([thread SpriteClip](https://devforum.roblox.com/t/spriteclip-sprite-sheet-animation-module/294195); [thread SpriteClip2](https://devforum.roblox.com/t/spriteclip2-a-free-versatile-spritesheet-animation-module/3184892); [discussão](https://devforum.roblox.com/t/why-is-the-max-image-resolution-1024x1024/1679078)).
- **Jan/2026**: "4K Texture Rendering" via Texture Streaming para MeshPart, SurfaceAppearance, Texture, Decal e MaterialVariant. Importações até 8K ficam guardadas no original e são transcodificadas para 4K. Quem pediu 4K em GUI não teve resposta ([anúncio](https://devforum.roblox.com/t/4k-texture-rendering/4316229)).
- **Texture Streaming (dez/2025, atualizado em 23/03/2026)**: inclui MeshPart, SurfaceAppearance, Texture, Decal, MaterialVariant e, desde a atualização, Beam e ParticleEmitter. **"2D UI Textures" e "SurfaceGUI textures" aparecem como "coming next"**. EditableImage não tem plano. Em atlas, a folha inteira vai para o mip que o uso mais exigente pede ([anúncio](https://devforum.roblox.com/t/introducing-texture-streaming/4144855)).
- A doc de especificações hoje fala em suporte até 4096×4096 e que "the engine automatically starts with lower quality versions of the texture and ramps up quality" ([Texture specifications](https://create.roblox.com/docs/art/modeling/texture-specifications)).
- `EditableImage` tem máximo de 1024×1024 ([doc](https://create.roblox.com/docs/reference/engine/classes/EditableImage)).

### 4.3 Sprite sheets: alinhamento, bleeding, padding e flip

- **Tremor de cerca de 1 px**: a folha tinha 799×999 em vez de 800×1000, e "each frame [moved] ~0.25 pixels". Reexportar com o grid exato resolveu ([thread](https://devforum.roblox.com/t/need-help-to-fix-shaking-in-sprite-sheet-using-imagerectoffset/1603967)).
- **Bleeding de quadros vizinhos** (antes do Pixelated): "the linear blending will cause bleeding from surrounding pixels when rendered upscaled or downscaled". Solução: "gutters of 1 pixel around each of your tiles... [filled with] the nearest edge color", ou mostrar em 1:1 ([thread de 2019](https://devforum.roblox.com/t/imagerectoffsetsize-issues/224476)).
- Caso de tile esticado: o alpha bleed não resolveu; `ScaleType = Slice` com `SliceCenter` 1,1,1,1 resolveu para um usuário e não para outro ([thread](https://devforum.roblox.com/t/strange-bleeding-using-tiles/513951)).
- Erro comum: passar o tamanho da **folha** onde o módulo espera o tamanho do **sprite** ([SpriteClip2](https://devforum.roblox.com/t/spriteclip2-a-free-versatile-spritesheet-animation-module/3184892)).
- **Flip horizontal**: `ImageRectSize` negativo "não funciona de forma confiável", segundo o autor do SpriteClip ([thread](https://devforum.roblox.com/t/spriteclip-sprite-sheet-animation-module/294195)). O EasySprite oferece `flip()` ([GitHub](https://github.com/dev-alastair/EasySprite)). Alternativa segura: quadros espelhados na própria folha (recomendação).
- Folhas de FNF chegam a 6660×832 e 8192×4096 e precisam ser divididas. Um participante avisou que alguns sprites "may not be Roblox friendly" ([thread](https://devforum.roblox.com/t/need-help-with-scripting-an-animation-with-sprite-sheets/1056519)).

### 4.4 Contornos claros ou escuros (alpha bleed) e formato PNG

- **Causa**: pixels transparentes guardam RGB, e a filtragem bilinear mistura essa cor nas bordas. Staff (fev/2024): o problema "stems from the limitations inherent to the bilinear rescaling algorithm we use for Alpha blended textures". A Roblox espera que os devs usem ferramentas de *color bleeding* de terceiros ([thread](https://devforum.roblox.com/t/fix-image-upload-adding-outlines-to-transparent-images/604835)).
- **Ferramentas**:
  - Automated PixelFix for UI (ago/2026): watcher em Python que aplica bleed de 4 px sem alterar o alpha ([thread](https://devforum.roblox.com/t/automated-pixelfix-for-ui-run-and-forget/4812286)).
  - Alpha Bleeder Discord Bot ([thread](https://devforum.roblox.com/t/alpha-bleeder-discord-bot-fix-your-images-for-free/2798249)).
  - chipng (citado [aqui](https://devforum.roblox.com/t/how-would-i-go-about-making-a-pixelart-game-in-roblox/1416335)).
- **PNG 8 bits e otimizadores** (TinyPNG etc.) já fizeram a transparência virar cor sólida; PNG de 32 bits salvo pelo Photoshop funcionava ([thread](https://devforum.roblox.com/t/unable-to-upload-some-images-to-roblox-without-failing-or-mangled-results/226675), Parcial via trecho). Há também relato de pixels com alpha 0 convertidos para (0,0,0,0) ([thread](https://devforum.roblox.com/t/uploading-a-decal-converts-the-color-of-all-transparent-pixels-to-black/348995), Parcial).

### 4.5 Compressão de textura (mobile) e qualidade

- **Thread-chave** ([link](https://devforum.roblox.com/t/compression-of-pixelated-imagelabels-on-mobile-unavoidably-ruins-our-games-aesthetic-graphics/2506241)):
  - Sprite sheets em `ImageLabel` Pixelated ficam "a JPEG mess" no mobile (Pixel 7, iPhone 14 e outros). Depois houve relatos em PC e laptops.
  - Staff (01/07/2025): "texture block compression is inherently lossy and, in its current implementation, unavoidable for performance on certain platforms". Sem trabalho planejado.
  - Staff (23/07/2025): explorando formas de os criadores controlarem a qualidade.
  - Workarounds que o autor recusou por custo: upscale de 4–8× (memória e tempo de carga) e Frames por pixel (CPU). EditableImage também é comprimida no mobile.
- Seams e "grão" em texturas 3D pequenas: um usuário resolveu os seams com 1 px de gap no UV; o grão no rosto continuou ([thread](https://devforum.roblox.com/t/roblox-compressing-this-texture-when-it-does-not-need-compression/3672084)).

### 4.6 `CanvasGroup` reduz a resolução do conteúdo

- Doc: o grupo vira uma textura única ("consumes extra texture memory"), limitada pelo `QualityLevel` do cliente. Acima do limite, renderiza em branco ([CanvasGroup](https://create.roblox.com/docs/reference/engine/classes/CanvasGroup)).
- Conteúdo de `CanvasGroup` perde qualidade em nível gráfico 3 ou menos quando o grupo é grande. O staff abriu ticket em 04/2024, sem correção ([bug](https://devforum.roblox.com/t/canvasgroup-makes-its-content-low-quality-at-certain-sizes-and-graphics-level-3-or-below/2946471)).
- Staff (jul/2025): é o motor "running into the limits and rescaling to remain under them". Texto borrado é "the expected result" ([thread](https://devforum.roblox.com/t/canvasgroup-images-fast-flag-uitexture-use-dynamic-render-settings-more-canvasgroup-blurriness-on-everything-instead-of-just-images/3826627)).
- Posição absoluta com casa decimal também borra ([trecho de busca](https://devforum.roblox.com/t/canvasgroups-content-is-blurred/3817152), Parcial).

### 4.7 Escala de UI, DPI e "mixels"

- Integer scaling: converter Scale em pixels com `AbsoluteSize` e arredondar ("Offset only works with whole numbers") ([thread](https://devforum.roblox.com/t/integer-scaling/3924311)).
- High-DPI: o `AbsoluteSize` é reportado em pontos, e a UI é renderizada cerca de 3× maior para ficar nítida ([post de 2018](https://devforum.roblox.com/t/ui-is-really-really-really-weird-on-mobile/95626)).
- Densidade de pixel consistente entre sprites de tamanhos diferentes: o thread não chegou a uma solução para `ParticleEmitter` ([thread](https://devforum.roblox.com/t/how-do-i-keep-pixel-size-consistent-in-my-pixel-art-game/4035701)).

### 4.8 Flipbooks de partículas: workflow, limites e armadilhas

- **Beta (18/03/2022)**:
  - Exigia textura de 1024×1024: quadros de 512 px em 2×2, 256 px em 4×4 ou 128 px em 8×8.
  - Montagem com Contact Sheet do Photoshop, ferramentas web ou **Free Tex Packer**, com tamanho fixo de 1024×1024 e trim e rotate desligados.
  - Animações com mais quadros precisam ser reduzidas: de 128 para 64 quadros ([beta](https://devforum.roblox.com/t/animated-particles-with-the-particle-flipbooks-beta/1718023)).
- **Release (21/10/2022)**:
  - Texturas quadradas em potência de 2, de 8 a 1024. Texturas menores economizam memória.
  - Enums renomeados para `Grid2x2`, `Grid4x4` e `Grid8x8`.
  - Recomenda "a little spacing around your frames".
  - Usuários pediram para desligar o fade entre quadros, porque ele fica ruim em sprites cartunescos ([release](https://devforum.roblox.com/t/particles’-flipbook-release/2029388)).
- **Custom layouts (beta de cliente, 13/10/2025)**: `FlipbookLayout = Custom` com `FlipbookSizeX/Y` de 1 a 64. Folhas não quadradas e sem potência de 2 são aceitas, por exemplo 4096×4096 com 32×8 quadros de 128×512 ([anúncio](https://devforum.roblox.com/t/client-beta-optimize-your-particle-animations-with-custom-flipbook-layouts/4005128)).
- **Documentação atual** ([ParticleEmitter](https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter); [guia](https://create.roblox.com/docs/effects/particle-emitters)):
  - `FlipbookFramerate` tem máximo de 30 fps. Em `OneShot`, a taxa é a duração da partícula dividida pelo número de quadros.
  - `FlipbookBlendFrames` escolhe entre crossfade e troca seca.
  - As dimensões da textura devem ser múltiplo exato do grid.
  - "include spacing between each of the particle frames", e o mip filtering pode exigir mais.
  - "clients automatically deactivate flipbooks when they are low on memory". Para economizar, reutilize texturas e use texturas menores.
- Flicker em flipbook (mai/2026, mesmo com `FlipbookBlendFrames = false`): o thread está marcado como resolvido, mas a solução não aparece na página capturada ([thread](https://devforum.roblox.com/t/solved-particleemitter-flipbook-flickering/4657545)).
- EmberGen para flipbook: **não encontrei** thread do DevForum. Exporte uma grade 8×8 ou Custom com espaçamento, conforme as regras acima.

### 4.9 Partículas em UI e em `ViewportFrame`

- Consenso da comunidade: `ParticleEmitter`, Beam e Trail **não renderizam em `ViewportFrame`**. Workarounds:
  - Sprite sheet num `ImageLabel`.
  - Uma Part com emissores no mundo, na frente da câmera, sob a GUI.
  - Fontes: [thread](https://devforum.roblox.com/t/particle-emitter-in-viewportframe/3262784), [thread](https://devforum.roblox.com/t/trail-in-a-viewport/2133446). A doc oficial do `ViewportFrame` não menciona partículas.
- Módulos de partículas 2D: [rParticle](https://devforum.roblox.com/t/rparticle-the-light-weight-open-source-gui-particle-system/680038), [EmitYourParticle](https://devforum.roblox.com/t/emityourparticle-a-faster-and-better-2d-particle-emitter-v101/2842247), [Emitter2D](https://devforum.roblox.com/t/emitter2d-convert-any-particleemitter-to-2d-with-the-click-of-a-button/3742009) (partículas são `ImageLabel`s, "noticeably slower" que 3D) e [UI Particle](https://devforum.roblox.com/t/ui-particle-an-unoptimized-module-to-integrate-particleemitters-into-your-ui-with-minimal-coding/4004649) (sem flipbook).
- Nature2D sugere "custom 2D Particle Emitters instead of RigidBodies due to frame drops" ([thread](https://devforum.roblox.com/t/nature2d-2d-physics-engine-for-ui-elements/1510935)).

### 4.10 `EditableImage`: limites e desempenho

- Doc ([EditableImage](https://create.roblox.com/docs/reference/engine/classes/EditableImage)):
  - Criar com `AssetService:CreateEditableImage()` ou `CreateEditableImageAsync()`.
  - Exibir com `Content.fromObject` em `ImageLabel.ImageContent`.
  - Máximo de 1024×1024.
  - "Editable assets are currently expensive for memory usage", com orçamento rígido no cliente.
  - **Desligado por padrão em jogos publicados**: habilite "Allow Mesh / Image APIs".
  - "Only a single `EditableImage` can be updated per frame on the display side".
  - `DrawImageTransformed` aceita `SamplingMode` Pixelated.
- `WritePixelsBuffer` é lento e não é thread-safe. Com 112×63 px a 10 desenhos por segundo, houve quedas de frame, piores no mobile ([thread](https://devforum.roblox.com/t/how-to-write-to-an-editableimage-in-parallel/3638723)).
- Animação frame a frame redesenhada em `EditableImage` atrasa porque o próprio tempo de escrita não é contabilizado ([thread](https://devforum.roblox.com/t/how-to-properly-draw-frames-of-animation-to-editableimage/2835825), Parcial).

### 4.11 Moderação de imagens

- Pixel art de um ovo (600×640, feita no pixelartmaker.com) foi recusada duas vezes. A hipótese da comunidade é que o bot confunde pixel art com sprites de Minecraft; não há confirmação oficial ([thread](https://devforum.roblox.com/t/egg-sprite-repeatedly-moderated/1823041)).
- Tiles de 18×18 enviados em lote falharam parcialmente na moderação ([thread](https://devforum.roblox.com/t/asset-failed-moderation-review-bulk-importing-images/2082704), Parcial via trecho).
- O LUASprites alerta para texto pequeno dentro das imagens ([thread](https://devforum.roblox.com/t/luasprites-spritesheet-generator-with-lua-output/1932127)).
- Doc: "Images declined by moderation will never load" ([ImageLabel](https://create.roblox.com/docs/reference/engine/classes/ImageLabel)).

### 4.12 Pré-carregamento e flicker

- `PreloadAsync` não impede o flicker na primeira exibição. Uma imagem precisa ser mostrada uma vez ([feedback de doc, fev/2026](https://devforum.roblox.com/t/feedback-on-contentproviderpreloadasync/4350350); [thread](https://devforum.roblox.com/t/preloadasync-doesnt-fix-the-issue-of-decalsimagelabels-flickering/3353512)).
- Player de impact frames com PNGs separados travava nas 3 primeiras execuções e voltava a travar depois de 5 a 10 minutos sem uso. Ideias: um `ImageLabel` por quadro alternando ZIndex, ou pré-exibir com transparência 0,999 ([thread](https://devforum.roblox.com/t/feedback-on-impact-frame-player-andor-frameplayer/3537568)).

### 4.13 2D dentro do mundo 3D: custo de BillboardGui e SurfaceGui

- "500 surface guis in one area can destroy performance"; algo entre 25 e 50 é aceitável. Há opiniões divergentes e nenhuma medição ([thread](https://devforum.roblox.com/t/are-surfaceguis-goodperformant-for-textures/2276029)).
- Muitas `BillboardGui` "will make your game laggy" ([tutorial](https://devforum.roblox.com/t/how-to-make-a-roblox-game-2d-pixlated-horror-game/2628506)).
- Frames como pixels: flicker por culling fora da tela; greedy meshing reduziu os assets em cerca de 60% ([thread](https://devforum.roblox.com/t/working-on-a-pixelsprite-engine-for-roblox/1852195)).

### 4.14 Impact frames, hit-stop e shake (referência dos battlegrounds)

- **Impact Frame Module** (mai/2024):
  - `ColorCorrectionEffect` com Contrast de +25000 ("White") ou −25000 ("Black"), Saturation −1, duração padrão de 0,1 s.
  - Parts atingidas viram Neon tingido.
  - O autor evitou Highlight alegando falta de suporte no mobile; não verificado ([thread](https://devforum.roblox.com/t/open-source-impactframe-module/2963136)).
- **Sequência observada em vídeos** (2023): speedlines → ColorCorrection preta → Highlight branco no jogador → mais partículas. Métodos alternativos: quadros desenhados à mão (Photopea), captura editada com filtros, ou pack da Creator Store ([thread](https://devforum.roblox.com/t/advanced-impact-frames/2468478)).
- **Cutscene em PNGs**: quadros feitos no After Effects, exportados em PNG e tocados por um módulo com FPS e duração ([thread](https://devforum.roblox.com/t/feedback-on-impact-frame-player-andor-frameplayer/3537568)).
- **Hit-stop**: `AnimationTrack:AdjustSpeed(0)` seguido de volta a 1. Só afeta as animações, não a física ([thread](https://devforum.roblox.com/t/slow-motion-effect-or-other-effects-like-slow-mo/2046601)).
- **Em UI** (recomendação): ColorCorrection não afeta `ScreenGui`. Faça inversão e flash com quadros pré-desenhados ou overlays em `ImageLabel`; pause o scheduler de sprites para o hit-stop.

### 4.15 Módulos e frameworks citados

| Recurso | O que é | Observações | Link |
|---|---|---|---|
| SpriteClip (2019, obsoleto) | animador de sprite sheet | `SpriteSizePixel`, `SpriteOffsetPixel` (espaçamento), `EdgeOffsetPixel`, `SpriteCountX`; `FrameRate` divisor de 60 | [DevForum](https://devforum.roblox.com/t/spriteclip-sprite-sheet-animation-module/294195) |
| SpriteClip2 (2024) | sucessor | `ImageSprite`, `EditableSprite`, `Scripted*` (callback por frame); Scheduler com Pause/Resume; sinais `FrameLast`, `Looped`, `FrameChanged` | [DevForum](https://devforum.roblox.com/t/spriteclip2-a-free-versatile-spritesheet-animation-module/3184892) |
| EasySprite (Luau, tipado) | matemática de `ImageRectOffset/Size` + `SpriteSequencer` | `flip()`, `fromRange`, `play(fps, loop)` | [GitHub](https://github.com/dev-alastair/EasySprite) |
| SimpleSprite | helper de sprite sheet para `ImageLabel`/`ImageButton` | Parcial (trecho) | [DevForum](https://devforum.roblox.com/t/simplesprite-create-spritesheets-for-uis-easily/1208693) |
| LUASprites (Python) | gera sprite sheet e código Lua a partir de PNGs ou quadros de GIF | aviso sobre moderação de texto pequeno | [DevForum](https://devforum.roblox.com/t/luasprites-spritesheet-generator-with-lua-output/1932127), [GitHub](https://github.com/AJSteinhauser/LUASprites) |
| CanvasDraw | biblioteca de raster por pixel sobre EditableImage | usada em The Powder Box e Draw & Donate | [DevForum](https://devforum.roblox.com/t/canvasdraw-a-custom-pixel-based-game-engine/1624633) |
| OSGL | biblioteca gráfica sobre EditableImage | Parcial (trecho) | [DevForum](https://devforum.roblox.com/t/osgl-editableimage-graphics-library/3066757) |
| Nature2D | física 2D para elementos de UI (Verlet, convex hull) | cerca de 60 fps com cerca de 100 colisões por frame, segundo o autor | [DevForum](https://devforum.roblox.com/t/nature2d-2d-physics-engine-for-ui-elements/1510935) |
| Upside Engine | engine 2D para Roblox (abr/2023) | iluminação "can consume quite a lot of resources" | [DevForum](https://devforum.roblox.com/t/2d-game-engine-upside-engine/2289749) |
| rParticle, EmitYourParticle, Emitter2D, UI Particle | partículas em UI | ver §4.9 | links em §4.9 |
| Impactframe Module | impact frames via ColorCorrection | ver §4.14 | [DevForum](https://devforum.roblox.com/t/open-source-impactframe-module/2963136) |

---

## 5. Lista de fontes

### Documentação oficial (Creator Hub)

- ImageLabel (ResampleMode, ImageRectOffset/Size, ScaleType, SliceCenter/SliceScale, ImageContent, IsLoaded): https://create.roblox.com/docs/reference/engine/classes/ImageLabel
- ParticleEmitter (Flipbook*, LightEmission, Orientation): https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
- Guia de Particle emitters (flipbooks, espaçamento, memória): https://create.roblox.com/docs/effects/particle-emitters
- Enum ParticleFlipbookLayout: https://create.roblox.com/docs/reference/engine/enums/ParticleFlipbookLayout
- EditableImage: https://create.roblox.com/docs/reference/engine/classes/EditableImage
- CanvasGroup: https://create.roblox.com/docs/reference/engine/classes/CanvasGroup
- ViewportFrame: https://create.roblox.com/docs/reference/engine/classes/ViewportFrame
- Texture specifications: https://create.roblox.com/docs/art/modeling/texture-specifications
- Referência de API de terceiros (histórico de SurfaceAppearance.ResampleMode): https://robloxapi.github.io/ref/class/SurfaceAppearance.html

### Anúncios no DevForum

- ResampleMode (2021): https://devforum.roblox.com/t/resamplemode-new-property-for-image-gui-objects/1418681
- Particle Flipbooks Beta (2022): https://devforum.roblox.com/t/animated-particles-with-the-particle-flipbooks-beta/1718023
- Particles' Flipbook Release (2022): https://devforum.roblox.com/t/particles’-flipbook-release/2029388
- Custom flipbook layouts (2025): https://devforum.roblox.com/t/client-beta-optimize-your-particle-animations-with-custom-flipbook-layouts/4005128
- Introducing Texture Streaming (2025/2026): https://devforum.roblox.com/t/introducing-texture-streaming/4144855
- 4K Texture Rendering (2026): https://devforum.roblox.com/t/4k-texture-rendering/4316229

### Threads do DevForum (técnica e armadilhas)

- https://devforum.roblox.com/t/how-to-make-pixel-art-less-blurry-solution/3140843
- https://devforum.roblox.com/t/how-to-make-pixel-art-look-less-blurry/4051703
- https://devforum.roblox.com/t/how-would-i-go-about-making-a-pixelart-game-in-roblox/1416335
- https://devforum.roblox.com/t/pixel-style-textures-being-blurred/2790436
- https://devforum.roblox.com/t/pixelated-resamplemode-for-surfaceappearances-pixel-art-meshes/4028314
- https://devforum.roblox.com/t/add-a-resamplemode-to-decals-textures-surfaceappearance/4399698
- https://devforum.roblox.com/t/add-resamplemode-for-all-instances-that-render-images/4751910
- https://devforum.roblox.com/t/resample-mode-enumresamplermode-pixelated-appears-blurry/4227459
- https://devforum.roblox.com/t/are-surfaceguis-goodperformant-for-textures/2276029
- https://devforum.roblox.com/t/spriteclip-sprite-sheet-animation-module/294195
- https://devforum.roblox.com/t/spriteclip2-a-free-versatile-spritesheet-animation-module/3184892
- https://devforum.roblox.com/t/need-help-to-fix-shaking-in-sprite-sheet-using-imagerectoffset/1603967
- https://devforum.roblox.com/t/imagerectoffsetsize-issues/224476
- https://devforum.roblox.com/t/strange-bleeding-using-tiles/513951
- https://devforum.roblox.com/t/putting-2d-character-sprites-in-a-game/2481297
- https://devforum.roblox.com/t/need-help-with-scripting-an-animation-with-sprite-sheets/1056519
- https://devforum.roblox.com/t/how-to-make-friday-night-funkin-in-roblox-part-1/2177738 (tutorial removido; só a descrição "Starling-formatted SpriteSheet and XML pairs" sobreviveu)
- https://devforum.roblox.com/t/how-to-do-2d-sprites-easily/3193539
- https://devforum.roblox.com/t/luasprites-spritesheet-generator-with-lua-output/1932127
- https://devforum.roblox.com/t/simplesprite-create-spritesheets-for-uis-easily/1208693
- https://devforum.roblox.com/t/fix-image-upload-adding-outlines-to-transparent-images/604835
- https://devforum.roblox.com/t/automated-pixelfix-for-ui-run-and-forget/4812286
- https://devforum.roblox.com/t/alpha-bleeder-discord-bot-fix-your-images-for-free/2798249
- https://devforum.roblox.com/t/unable-to-upload-some-images-to-roblox-without-failing-or-mangled-results/226675
- https://devforum.roblox.com/t/uploading-a-decal-converts-the-color-of-all-transparent-pixels-to-black/348995
- https://devforum.roblox.com/t/compression-of-pixelated-imagelabels-on-mobile-unavoidably-ruins-our-games-aesthetic-graphics/2506241
- https://devforum.roblox.com/t/roblox-compressing-this-texture-when-it-does-not-need-compression/3672084
- https://devforum.roblox.com/t/why-is-the-max-image-resolution-1024x1024/1679078
- https://devforum.roblox.com/t/canvasgroup-makes-its-content-low-quality-at-certain-sizes-and-graphics-level-3-or-below/2946471
- https://devforum.roblox.com/t/canvasgroup-images-fast-flag-uitexture-use-dynamic-render-settings-more-canvasgroup-blurriness-on-everything-instead-of-just-images/3826627
- https://devforum.roblox.com/t/canvasgroups-content-is-blurred/3817152
- https://devforum.roblox.com/t/integer-scaling/3924311
- https://devforum.roblox.com/t/ui-is-really-really-really-weird-on-mobile/95626
- https://devforum.roblox.com/t/how-do-i-keep-pixel-size-consistent-in-my-pixel-art-game/4035701
- https://devforum.roblox.com/t/solved-particleemitter-flipbook-flickering/4657545
- https://devforum.roblox.com/t/particle-emitter-in-viewportframe/3262784
- https://devforum.roblox.com/t/trail-in-a-viewport/2133446
- https://devforum.roblox.com/t/rparticle-the-light-weight-open-source-gui-particle-system/680038
- https://devforum.roblox.com/t/emityourparticle-a-faster-and-better-2d-particle-emitter-v101/2842247
- https://devforum.roblox.com/t/emitter2d-convert-any-particleemitter-to-2d-with-the-click-of-a-button/3742009
- https://devforum.roblox.com/t/ui-particle-an-unoptimized-module-to-integrate-particleemitters-into-your-ui-with-minimal-coding/4004649
- https://devforum.roblox.com/t/canvasdraw-a-custom-pixel-based-game-engine/1624633
- https://devforum.roblox.com/t/osgl-editableimage-graphics-library/3066757
- https://devforum.roblox.com/t/how-to-write-to-an-editableimage-in-parallel/3638723
- https://devforum.roblox.com/t/how-to-properly-draw-frames-of-animation-to-editableimage/2835825
- https://devforum.roblox.com/t/nature2d-2d-physics-engine-for-ui-elements/1510935
- https://devforum.roblox.com/t/2d-game-engine-upside-engine/2289749
- https://devforum.roblox.com/t/is-it-possible-to-make-a-fully-2d-game-on-roblox/1529211
- https://devforum.roblox.com/t/egg-sprite-repeatedly-moderated/1823041
- https://devforum.roblox.com/t/asset-failed-moderation-review-bulk-importing-images/2082704
- https://devforum.roblox.com/t/feedback-on-contentproviderpreloadasync/4350350
- https://devforum.roblox.com/t/preloadasync-doesnt-fix-the-issue-of-decalsimagelabels-flickering/3353512
- https://devforum.roblox.com/t/open-source-impactframe-module/2963136
- https://devforum.roblox.com/t/advanced-impact-frames/2468478
- https://devforum.roblox.com/t/feedback-on-impact-frame-player-andor-frameplayer/3537568
- https://devforum.roblox.com/t/slow-motion-effect-or-other-effects-like-slow-mo/2046601
- Tag "pixelate" (índice de threads): https://devforum.roblox.com/tag/pixelate

### Showcases e devlogs (casos 2.5 a 2.10 e Pixel Quest/Powder Box)

- https://devforum.roblox.com/t/pixel-quest-2d-rpg-game/2310608
- https://devforum.roblox.com/t/feedback-on-2d-powder-and-fluid-simulation-sandbox-game/1736128
- https://devforum.roblox.com/t/the-campgrounds-2d-rpg-story-game-roblox-undertale/2131536
- https://devforum.roblox.com/t/undertale-ui-based-game-in-roblox/3484839
- https://devforum.roblox.com/t/ive-been-working-on-a-2d-horror-game-in-roblox-what-do-you-guys-think/2066090
- https://devforum.roblox.com/t/2d-horror-game-in-roblox-pixel-art/3246131
- https://devforum.roblox.com/t/how-to-make-a-roblox-game-2d-pixlated-pixel-platformer/2630038
- https://devforum.roblox.com/t/how-to-make-a-roblox-game-2d-pixlated-horror-game/2628506
- https://devforum.roblox.com/t/working-on-a-pixelsprite-engine-for-roblox/1852195
- https://devforum.roblox.com/t/pixel-game-project-dev-logs/3142416
- https://devforum.roblox.com/t/doodle-world-credits/1657176

### Código e repositórios

- OpenBronze (arquivo de fãs do codebase de Brick Bronze): https://github.com/singharaj-usai/OpenBronze
  - AnimatedSprite.lua: https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/AnimatedSprite.lua
  - Battle/Sprite.lua: https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/Battle/Sprite.lua
  - Battle/Actions.lua: https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Plugins/Battle/Actions.lua
  - Data/Spritesheets.lua: https://raw.githubusercontent.com/singharaj-usai/OpenBronze/main/src/ServerStorage/Data/Spritesheets.lua
- PokemonBrickBronzeSpriteScraper: https://github.com/AmexOfficial24/PokemonBrickBronzeSpriteScraper
- EasySprite: https://github.com/dev-alastair/EasySprite
- LUASprites: https://github.com/AJSteinhauser/LUASprites
- Bot de Starving Artists (README): https://github.com/Luois45/roblox-starving-artists-bot/blob/main/README.md

### Páginas de jogos, rastreadores e terceiros

- Pixel Quest!: https://www.roblox.com/games/80003276594057/Pixel-Quest · https://www.rotrends.com/game/7458874788/Pixel-Quest-GUILDS · https://allthings.how/pixel-quest-on-roblox-bullet-hell-mmo-basics-permadeath-early-tips
- The Powder Box: https://rowatcher.com/games/3458415923/the-powder-box · https://rowatcher.com/games/6787644864/the-powder-box-all-ages · https://ethanthegrand.itch.io/the-powder-box-pc-edition
- Starving Artists: https://www.roblox.com/games/8916037983/starving-artists · https://www.gamefam.com/case-study-pixobitz · https://brainjoose.itch.io/phantomcanvas
- Draw & Donate: https://www.roblox.com/games/17070253881/Draw-Donate
- Pokémon Brick Bronze: https://namu.moe/w/pbb
- Pixel Blade: https://rotrends.com/game/6161049307/Pixel-Blade · https://allthings.how/?p=285688 · https://www.pockettactics.com/pixel-blade-weapons
- Doodle World: https://www.roblox.com/games/5116869569
- Loomian Legacy: https://rotrends.com/game/117307972/Loomian-Legacy
- Undertale Test Place Reborn: https://rotrends.com/game/2916593387
- Undertale: Last Corridor: https://bloxodes.com/stats/games/undertale-last-corridor-3958291198
- Literally FNF: https://www.rotrends.com/game/2422985977/Literally-FNF
- Pixel Pets!: https://www.roblox.com/games/90486354692269
- 2D PIXEL RPG: https://www.roblox.com/games/18893183789/2D-PIXEL-RPG
- Pix-art: https://www.roblox.com/games/71053628284433
