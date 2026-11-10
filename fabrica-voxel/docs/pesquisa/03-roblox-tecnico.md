# 03 — Roblox técnico: limites e APIs para levar voxel ao Studio

Pesquisa de 9 de novembro de 2026. A documentação oficial foi lida no repositório `Roblox/creator-docs` (commit de 7 nov 2026, espelho de create.roblox.com/docs); os anúncios foram lidos no DevForum, post original de funcionário (staff). Legenda: **[Fn]** = fonte n; **[P]** = limiar proposto por este dossiê (calibrar); **[não verificado]** = não consegui confirmar.

## 0. Veredito

1. **GLB é rota oficial e já automatizável.** O Importer aceita `.gltf/.glb` com malha, textura, rig, skinning, animação e cor de vértice [F1][F2]. A Assets API do Open Cloud aceita Model em `.fbx/.gltf/.glb` até 20 MB [F4]. Desde 4 nov 2026 o servidor MCP embutido do Studio sobe e insere o arquivo sozinho (`open_cloud_invoke` + skill `rbx-import-asset`) [F6].
2. **Limites duros:** 20.000 triângulos por malha e 4 influências por vértice [F3]. Não há limite publicado de ossos por malha.
3. **Pixel nítido em malha ainda não existe em produção.** `MeshPart`, `Decal` e `Texture` não têm filtro por vizinho mais próximo. `SurfaceAppearance.ResampleMode = Pixelated` está na referência da API, mas staff disse em 7 jul 2026 que "está demorando para chegar à produção" e em 5 nov 2026 ainda não aparecia no Studio [F19]. Para voxel, **cor de vértice sem textura** é a rota segura.
4. **Animação por dados é a decisão certa.** Clipe criado por script só toca dentro do Studio [F13]; asset de animação é restrito, precisa de permissão por experiência e não pode virar uso aberto [F15]. Um modelo vendido não pode depender de `AnimationId`.
5. **Avatar R15 da plataforma deixou de usar Motor6D** (Avatar Joint Upgrade, fase 2 desde 27 mai 2026, fase 3 prevista para o fim de 2026) [F12]. Rig próprio continua com Motor6D.
6. **Câmera ortográfica nativa chegou, mas só em Studio Beta** (30 out 2026); jogo publicado ainda não usa [F26].
7. **Venda no Roblox:** só `Model` e `Plugin` são vendidos, em dólar. O cadastro de vendedor **não é aceito no Brasil** [F33]. O plano de receita precisa de lojas externas.

## 1. Tabela: fato → valor → fonte/data → impacto na fábrica

| # | Fato | Valor | Fonte / data | Impacto |
|---|---|---|---|---|
| **Importação** | | | | |
| 1 | Formatos de malha | `.fbx`, `.obj`, `.gltf/.glb`; fbx e gltf levam hierarquia, PBR, rig, skinning, animação e cor de vértice | F1, F2 (docs 7 nov 2026; glTF completo em 7 set 2023) | GLB único por asset |
| 2 | Triângulos por malha | 20.000 (acessório rígido: 4.000) | F3, F31 | Lint por peça; dividir acima disso |
| 3 | Vértices | Sem limite publicado no Importer [não verificado]; `EditableMesh`: 60.000 vértices e 20.000 triângulos | F22 | Lint ≤ 60.000 (quad com cor própria = 4 vértices) |
| 4 | Skinning | ≤ 4 influências por vértice; raiz em 0,0,0 sem peso; ossos com escala 1 e rotação 0 | F3 | Voxel rígido: 1 osso, peso 1,0 |
| 5 | Ossos sem influência | Removidos por padrão (`Keep Zero Influence Bones` desligado) | F1 | Soquete não pode ser osso vazio |
| 6 | Animação no arquivo | 1 trilha por arquivo (regra escrita para `.fbx`); via Animation Editor, "Import > From FBX Animation"; o exportador glTF do Studio não exporta animação | F3, F7 | Não depender de clipe embutido |
| 7 | Cor de vértice | Importada; `Ignore Vertex Colors` desligado por padrão; tinge a superfície | F1, F8 | Cor sem textura |
| 8 | Textura | Renderiza até 4096² por streaming (upload até 8k); guia: 256² para 5×5 studs; 1 material e 1 conjunto UV (0 a 1) por malha | F5, F21 | Atlas de 256 a 1024 basta |
| 9 | Unidade | `Scale Unit` padrão = Studs: 1 unidade do arquivo = 1 stud; 1 stud ≈ 28 cm | F1, F9 | Gravar o GLB em studs |
| 10 | Eixos | glTF: destro, +Y cima, frente em +Z, metros. Importer: `World Forward = Front`, `World Up = Top`. Corpo de avatar: frente +Z | F10, F1, F31 | Frente da fábrica é −Z: testar e travar |
| 11 | Hierarquia glTF | `Model` > `Model` por malha > 1 `MeshPart` por primitiva; nome repetido ganha `_Node` | F1 | 1 primitiva por peça; nó ≠ malha |
| 12 | Sufixos reservados | `_Att` vira `Attachment`; `_OuterCage`/`_InnerCage` viram `WrapTarget`/`WrapLayer` | F18 | Proibir nos nomes |
| 13 | Lote | Import Queue (vários arquivos, presets, "Apply settings to all"); Reimport casa por nome de malha | F1, F37 | Nomes estáveis entre versões |
| 14 | Open Cloud Assets | Model `.fbx/.gltf/.glb/.rbxm`, 20 MB por chamada, vira Package; 120 criações/min; sem opções de importação; animação só `.rbxm` | F4, F40 | Upload automático |
| 15 | MCP embutido | Desde 5 mar 2026. `execute_luau`, `insert_asset`, `screen_capture`, `start_stop_play`, `search_game_tree`; `open_cloud_invoke` (4 nov 2026). Sobe só de pasta aprovada, em place publicado | F6 | IA importa, mede e fotografa sem cliques |
| 16 | Duplicatas | O Importer não deduplica malhas iguais | F16 | Subir cada peça uma vez e clonar |
| **Render** | | | | |
| 17 | Draw call | Malhas com o mesmo `MeshContent` e a mesma textura (ou `SurfaceAppearance`, ou material) saem em 1 chamada; decal, textura e partícula agrupam mal | F16 | Peça compartilhada, variação por cor |
| 18 | Orçamento | Exemplo oficial: < 1.000 draw calls e < 1.000.000 triângulos no aparelho-base. ~65% dos jogadores em Android, 60% deles com 2 a 4 GB | F17 | Meta [P]: metade |
| 19 | `RenderFidelity` | Automatic: máximo até 250 studs, médio 250 a 500, mínimo além; Precise é caro | F18 | Automatic; conferir silhueta de longe |
| 20 | `CollisionFidelity` | Box, Hull, Default, PreciseConvexDecomposition, Tunable | F18 | Box nas peças |
| 21 | Filtro de textura | `ResamplerMode` (Default bilinear, Pixelated) vale em `ImageLabel`/`ImageButton`; ausente em `MeshPart`, `Decal`, `Texture`; em `SurfaceAppearance` documentado e não liberado | F19 | Ver §2 |
| 22 | Brilho | `Neon` vale para a peça inteira; máscara emissiva no `SurfaceAppearance` (jogos publicados desde 12 fev 2026) usa só o canal R e a cor do `ColorMap` | F20 | Olho e runa: peça Neon ou máscara |
| 23 | Malha com ossos fora de Humanoid | Ao mover, reconstrói FastCluster; contorno oficial: pôr um `Humanoid` no Model | F16 | Elite: testar |
| 24 | Streaming | Ligado por padrão em place novo; `ModelStreamingMode` Atomic/Persistent | F36 | Criatura = Atomic |
| **Animação** | | | | |
| 25 | `Motor6D.Transform` | Aplicado em lote após `PreSimulation`; o `Animator` sobrescreve entre `PreAnimation` e `PreSimulation`; não replica | F11 | Escrever em `PreSimulation` |
| 26 | `Bone.Transform` | Deslocamento relativo ao `CFrame` do osso; não replica; não afeta colisão | F11 | Mesmo padrão |
| 27 | `C0`/`C1` | Não usar para animar; usar `Transform` | F16 | Lint no Luau |
| 28 | Clipe por script | `RegisterAnimationClip` / `RegisterKeyframeSequence` dão id temporário, só no Studio; `KeyframeSequenceProvider` está deprecado | F13 | Só pré-visualização |
| 29 | Posse de animação | Restrita; a experiência precisa de permissão; nunca uso aberto | F15 (31 jul 2025) | Clipes vão como ModuleScript |
| 30 | Réplica | NPC: animar no cliente; sincronizar por atributo ou `UnreliableRemoteEvent` | F12, F16 | Confirma a arquitetura |
| 31 | LOD de animação | `Animator.PreferLodEnabled`, `EvaluationThrottled` | F14 | Runtime próprio precisa do seu LOD |
| 32 | Juntas do avatar | `AnimationConstraint` no lugar de Motor6D; `C0`/`C1` só leitura | F12 | Nunca `IsA("Motor6D")` em avatar padrão |
| 33 | `IKControl` | Precisa de `Humanoid` ou `AnimationController` com `Animator` | F14 | Só em rig com Animator |
| **Editable\*** | | | | |
| 34 | `EditableMesh` | 60.000 vértices, 20.000 triângulos; ossos e pesos; cor por canto de face | F22 | Dá para montar voxel por script |
| 35 | Permissão | Jogo publicado: dono 13+, identidade verificada e "Allow Mesh / Image APIs"; plugin no Studio dispensa; memória limitada no cliente | F22, F23 | Não usar em jogo |
| 36 | Persistência | Não salva no place. `CreateDataModelContentAsync` fixa por sessão (18 mai 2026). `CreateAssetAsync` (Mesh, Image, Model) só em plugin local ou tarefa Luau do Open Cloud; 30/min | F24, F25 | Rota C (§3) |
| **Câmera e movimento** | | | | |
| 37 | `FieldOfView` | 1 a 120 graus, padrão 70 | F26 | FOV baixo simula ortográfica |
| 38 | Ortográfica | `Camera.ProjectionType = Orthographic`; `OrthographicSize` 0,001 a 100.000 (padrão 35). Studio Beta; sombra do sol incorreta; não vale em ViewportFrame | F26 (30 out 2026) | Deixar atrás de uma chave |
| 39 | `Scriptable` | Desliga os scripts padrão de câmera; atualizar com `BindToRenderStep` | F26, F27 | Dois perfis de câmera |
| 40 | Controles | `Player.DevComputerMovementMode` / `DevTouchMovementMode` = Scriptable; só o servidor escreve | F29 | Troca de modo no servidor |
| 41 | Controladores | `ControllerManager` (29 set 2023); `Humanoid.EvaluateStateMachine`; Character Controller Library em Studio Beta (18 fev 2026) | F28, F29 | Não basear o jogo na beta |
| **Avatar** | | | | |
| 42 | Alturas | Clássico ≈ 5 studs; Rthro 5,75 a 6,5; corpo de Marketplace: 4 a 10 studs de altura | F31 | Avatar de 2,8 studs não vira corpo de Marketplace |
| 43 | Personagem próprio | `Model` chamado `StarterCharacter` em `StarterPlayer`; acessórios por conta do jogo | F30 | Linhagens usam isso |
| 44 | Pontos padrão | 19, de `Hat_Att` a `RightGrip_Att`; no Studio viram `HatAttachment` etc. | F31 | Reusar os nomes |
| 45 | `WrapLayer`/`WrapTarget` | Estica a malha por gaiolas com UV casado | F32 | Contraria "peça rígida"; não usar |
| **Loja** | | | | |
| 46 | Creator Store | Grátis: Model, Plugin, MeshPart, Decal, áudio. Pago: só Model (US$ 2,99 a 49,99) e Plugin (US$ 4,99 a 249,99); 100% do líquido; retenção de 30 dias; Stripe | F33 (10 dez 2025) | Teto de US$ 49,99 por modelo |
| 47 | Requisitos | Conta individual, identidade verificada, verificação em 2 etapas, país suportado. **Brasil, China, Índia e Rússia sem cadastro** | F33 (19 ago 2026) | Bloqueia venda direta |
| 48 | Regras do asset | 200 modelos por 30 dias; < 15.000 dependências; sem `require(id)`, `loadstring`, `getfenv`, código ofuscado | F33 | Lint de pacote |
| 49 | Marketplace de avatar | Em Robux; upload 80 Robux (500 se emissivo); 30% ao criador; exige identidade e Plus/Premium | F34 | Fora do escopo inicial |
| 50 | 2D | AnimatedImage (importa `.ase`) em Early Access, só Studio | F39 (27 out 2026) | Pixel art 2D: acompanhar |

## 2. Cor e pixel: o que fazer hoje

- **Rota 1 (padrão):** cor de vértice (`COLOR_0`), sem textura. Não há filtro, não há vazamento entre texels, e peças iguais agrupam em uma chamada.
- **Rota 2:** atlas em `TextureID`. O filtro é bilinear; o pedido de recurso relata borrão e vazamento mesmo com 1024² e pede 2 a 3 px de margem por ladrilho [F19]. Só com texel ampliado e margem.
- **Rota 3 (futura):** `SurfaceAppearance` com `ColorMap` e `ResampleMode = Pixelated`. Ativar por chave quando o teste no Studio passar.
- Interface 2D: `ImageLabel.ResampleMode = Pixelated` já funciona [F19].

## 3. Três rotas de entrada no Studio

| Rota | Como | Bom para | Limite |
|---|---|---|---|
| A | Import Queue (manual) | Conferir avisos e ajustar eixo/escala | Depende de cliques |
| B | `open_cloud_invoke` ou Assets API → `insert_asset` → `execute_luau` | Produção em massa | Sem opções de importação; asset é permanente; staff não recomenda a API para 3D por não mostrar avisos [F33] |
| C | Luau → `EditableMesh` → `CreateAssetAsync` | Malha gerada por dados, sem arquivo | Só plugin local ou tarefa Luau (5 tarefas/min) [F24][F40] |

Recomendação: B como padrão, com um asset de calibração passando por A uma vez.

## 4. Não confirmado: precisa testar no Studio

1. `ResampleMode = Pixelated` em `SurfaceAppearance`: existe no Studio atual? Vale em jogo publicado?
2. Cor de vértice de GLB aparece em `MeshPart` sem textura? O Roblox trata como linear (o glTF define linear) ou sRGB? Como combina com `MeshPart.Color`?
3. GLB com frente em −Z ou +Z: qual vira `LookVector` com `World Forward = Front`? Pela rota B o resultado é o mesmo?
4. Rota B mantém 1 unidade = 1 stud? (A skill fala em "redimensionar para o tamanho real".)
5. Ossos por malha: 30, 60 e 120 ossos importam e animam? Custo no MicroProfiler.
6. Animação dentro do GLB: onde aparece depois de importar? [não verificado]
7. Rota B preserva ossos e nomes? Remove os sem influência?
8. `Motor6D.Transform` sem `Animator`, com peças ancoradas, no cliente: funciona? Custo de 500 a 2.000 juntas por quadro.
9. `Bone.Transform` segue o mesmo momento do quadro? A documentação só descreve Motor6D.
10. `Humanoid` com `EvaluateStateMachine = false` em malha com ossos: ganho real?
11. `RenderFidelity = Automatic` deforma a silhueta voxel acima de 250 studs?
12. Motor6D: staff prometeu marcar como deprecado (jan 2026); a documentação ainda não marca.
13. Tamanho máximo de `EditableImage`: a classe diz 1024²; a nota da versão 718 sugere mais.

## 5. Regras acionáveis

1. Exportar um `.glb` por asset, ≤ 20 MB.
2. Cada malha ≤ 20.000 triângulos e ≤ 60.000 vértices. Meta [P]: criatura comum ≤ 6.000 no total, elite ≤ 16.000.
3. Uma primitiva por malha. Nome de nó diferente do nome da malha. Nomes únicos.
4. Proibir nomes terminados em `_Att`, `_InnerCage`, `_OuterCage`, `_Node`.
5. Cada vértice com 1 osso e peso 1,0. Raiz na origem, sem peso. Ossos em repouso com rotação 0 e escala 1.
6. Todo osso do GLB influencia ≥ 1 vértice. Soquetes saem do módulo Luau.
7. Uma unidade do GLB = 1 stud. Lint: altura da caixa = altura da ficha ± 1 voxel.
8. Eixo travado por um asset de calibração (seta com "frente" e "cima"). O exportador nunca muda.
9. Cor padrão em `COLOR_0`, sem textura. Proibir textura até o teste 2 passar com outro resultado.
10. Se houver atlas: potência de 2, ≤ 1024, margem ≥ 2 px, texel ≥ 4×4 px por voxel [P].
11. Uma peça igual = um asset. Hash do GLB no registro; upload repetido é erro.
12. Cena no aparelho-base [P]: ≤ 500 draw calls e ≤ 500.000 triângulos (teto de exemplo oficial: 1.000 e 1.000.000).
13. Uma `MeshPart` por peça rígida. Nunca uma `Part` por voxel. Meta [P]: ≤ 16 peças por criatura comum.
14. `Transform` só é escrito dentro de `RunService.PreSimulation`. Atribuir `C0`/`C1` em tempo de jogo é erro de lint.
15. Rig procedural não tem `Animator`. Se tiver, multiplicar sobre o `Transform` e pular o quadro quando `EvaluationThrottled`.
16. Animação roda no cliente. O servidor publica só estado (clipe, início, velocidade) em atributos. Nenhum `LoadAnimation` de NPC no servidor.
17. Asset de venda sem `AnimationId`, `require(id)`, `loadstring`, `getfenv`/`setfenv` e código ofuscado; < 15.000 dependências.
18. Código que procura juntas em avatar padrão aceita `AnimationConstraint` e `Motor6D`.
19. Câmera do tabuleiro: `Scriptable`, FOV de 10 a 20 [P] com distância compensada. Chave `ortografica` desligada até liberação em jogo publicado.
20. Troca de modo: o servidor muda `DevComputerMovementMode` e `DevTouchMovementMode`; o cliente troca o perfil de câmera.
21. Peças de criatura: `CollisionFidelity = Box`, `CanCollide = false`; colisão só na raiz. `RenderFidelity = Automatic`. Model `Atomic`.
22. Nenhum módulo de jogo publicado depende de `EditableMesh`/`EditableImage`.
23. Upload ≤ 120 por minuto, só da pasta `saida/` aprovada; confirmar antes (o asset não se apaga pela API).
24. Preço de Model na Creator Store entre US$ 2,99 e US$ 49,99.

## 6. Glossário

- **Draw call:** uma ordem de desenho enviada à placa de vídeo.
- **Instanciamento (instancing):** juntar cópias da mesma malha em uma ordem de desenho.
- **Skinning:** ligação de vértices a ossos por pesos.
- **FastCluster:** agrupamento interno de malhas que o motor reconstrói quando algo muda.
- **Filtro bilinear / vizinho mais próximo (nearest):** mistura texels vizinhos / mostra o texel cru.
- **Restrito / uso aberto (Restricted / Open Use):** asset que exige permissão / asset livre.
- **Package:** modelo versionado e reutilizável do Roblox.
- **MCP (Model Context Protocol):** protocolo que liga um cliente de IA ao Studio.
- **AJU (Avatar Joint Upgrade):** troca de Motor6D por AnimationConstraint nos avatares.

## 7. Fontes

- **F1** https://create.roblox.com/docs/studio/importer — formatos, hierarquia glTF, opções do Importer, fila (7 nov 2026).
- **F2** https://devforum.roblox.com/t/3d-importer-gltf-file-support-full-release/2584034 — glTF com rig, skinning e animação (7 set 2023).
- **F3** https://create.roblox.com/docs/art/modeling/specifications — 20.000 triângulos, 4 influências, 1 trilha de animação.
- **F4** https://create.roblox.com/docs/cloud/guides/usage-assets — tipos e limites da Assets API.
- **F5** https://create.roblox.com/docs/art/modeling/texture-specifications — resolução e UV.
- **F6** https://create.roblox.com/docs/studio/mcp e https://devforum.roblox.com/t/studio-mcp-server-updates-open-cloud-access-in-your-mcp-client-and-asset-import-workflows/4975849 — ferramentas do MCP e importação (4 nov 2026); MCP embutido: https://devforum.roblox.com/t/assistant-updates-studio-built-in-mcp-server-and-playtest-automation/4474643 (5 mar 2026).
- **F7** https://create.roblox.com/docs/art/modeling/gltf-export e https://create.roblox.com/docs/art/characters/export-avatar-animations-from-maya — exportador sem animação; importação de animação FBX.
- **F8** https://create.roblox.com/docs/art/blender — pintura de vértice, escala.
- **F9** https://create.roblox.com/docs/physics/units — stud ≈ 28 cm.
- **F10** https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html — eixos, metros, `COLOR_0` linear (lido no fonte em github.com/KhronosGroup/glTF).
- **F11** https://create.roblox.com/docs/reference/engine/classes/Motor6D e .../classes/Bone — `Transform`.
- **F12** https://devforum.roblox.com/t/avatar-joint-upgrade-aju-phase-2-rollout-updated-migration-recommendations/4656414 (27 mai 2026) e https://devforum.roblox.com/t/avatar-joint-upgrade-for-physically-simulated-character-movement-is-now-live/4298561 (26 jan 2026).
- **F13** https://create.roblox.com/docs/reference/engine/classes/AnimationClipProvider — id temporário só no Studio.
- **F14** https://create.roblox.com/docs/reference/engine/classes/Animator e .../classes/IKControl.
- **F15** https://devforum.roblox.com/t/improving-animation-asset-permissions/3852101 — animação restrita (31 jul 2025).
- **F16** https://create.roblox.com/docs/performance-optimization/improve — draw calls, FastCluster, NPC no cliente.
- **F17** https://create.roblox.com/docs/performance-optimization/design e .../test-on-hardware — exemplo de orçamento, aparelhos.
- **F18** https://create.roblox.com/docs/parts/meshes — fidelidades, sufixos.
- **F19** https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance ; https://devforum.roblox.com/t/release-notes-for-729/4722823 (staff, post 10, 7 jul 2026); https://devforum.roblox.com/t/release-notes-for-746/4977079 (relato, 5 nov 2026); https://devforum.roblox.com/t/pixelated-resamplemode-for-surfaceappearances-pixel-art-meshes/4028314 (pedido, 27 out 2025).
- **F20** https://devforum.roblox.com/t/emissive-masks-are-now-live-for-published-experiences/4357705 (12 fev 2026).
- **F21** https://devforum.roblox.com/t/4k-texture-rendering/4316229 (30 jan 2026).
- **F22** https://create.roblox.com/docs/reference/engine/classes/EditableMesh e .../classes/EditableImage.
- **F23** https://devforum.roblox.com/t/client-beta-in-experience-mesh-image-apis-now-available-in-published-experiences/3267293 (20 nov 2024).
- **F24** https://devforum.roblox.com/t/beta-lua-asset-creation-for-creator-tooling-with-createassetasync/3294134 (5 dez 2024) e https://devforum.roblox.com/t/creator-store-accepts-plugins-that-use-createassetasync-but-the-api-always-fails-for-users-who-install-them/4955322 (24 out 2026).
- **F25** https://devforum.roblox.com/t/full-release-introducing-createdatamodelcontent-convert-editable-mesh-and-image-data-into-static-content/4541898 (27 mar 2026).
- **F26** https://create.roblox.com/docs/reference/engine/classes/Camera e https://devforum.roblox.com/t/studio-beta-build-2d-isometric-and-top-down-games-with-orthographic-camera/4966772 (30 out 2026).
- **F27** https://create.roblox.com/docs/tutorials/use-case-tutorials/input-and-camera/control-the-users-camera — câmera isométrica com FOV 20.
- **F28** https://create.roblox.com/docs/characters/character-controller-library ; https://devforum.roblox.com/t/studio-beta-avatarabilities-library-for-a-luau-based-character-controller/4403904 ; https://devforum.roblox.com/t/releasing-character-physics-controllers/2623426.
- **F29** https://create.roblox.com/docs/reference/engine/classes/Player e .../classes/Humanoid.
- **F30** https://create.roblox.com/docs/reference/engine/classes/StarterPlayer e https://create.roblox.com/docs/characters.
- **F31** https://create.roblox.com/docs/avatar/character-bodies/specifications ; https://create.roblox.com/docs/avatar/rigid-accessories/specifications ; https://create.roblox.com/docs/studio/avatar-settings.
- **F32** https://create.roblox.com/docs/characters/appearance — gaiolas em modelo não R15.
- **F33** https://create.roblox.com/docs/production/creator-store ; https://devforum.roblox.com/t/buy-and-sell-models-on-the-creator-store/4142112 (10 dez 2025); https://devforum.roblox.com/t/new-requirements-to-publish-to-the-creator-store/4820095 (19 ago 2026).
- **F34** https://create.roblox.com/docs/marketplace/marketplace-fees-and-commissions e .../marketplace/marketplace-policy.
- **F36** https://create.roblox.com/docs/workspace/streaming.
- **F37** https://create.roblox.com/docs/art/modeling/reimport.
- **F39** https://devforum.roblox.com/t/early-access-program-build-2d-games-with-animatedimages/4960734 (27 out 2026).
- **F40** https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/cloud/openapi.json — limites de taxa (120/min Assets; 5/min tarefas Luau).
