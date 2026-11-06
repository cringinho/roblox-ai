# Roblox técnico para pipeline de pixel art: renderização, flipbooks, EditableImage, GUI, upload, Studio MCP, Fusion 0.3 e Luau

**Data da pesquisa:** 2026-11-06
**Fontes principais:**
- Referência da engine e guias: `create.roblox.com/docs`, lidos no repositório-fonte `github.com/Roblox/creator-docs` (commit `031a0e3`, de 2026-11-06, ou seja, o estado do dia). Os arquivos YAML de referência são gerados automaticamente a partir da engine.
- Anúncios e respostas da equipe no `devforum.roblox.com`.
- `github.com/Roblox/studio-rust-mcp-server` (clonado).
- `github.com/dphfox/Fusion` na tag `v0.3-beta`, que é o release 0.3.0 de 2024-08-30, e no `main`.
- `luau.org` e `github.com/luau-lang/luau`.

**Legenda:**
- [OK] confirmado em fonte primária.
- [CONFLITO] fontes conflitantes, ou estado de rollout incerto.
- [NAO CONFIRMADO] **não confirmado**.
- [DICA] recomendação minha, sem fonte direta.

---

## 0. Resumo executivo: o que muda decisões de implementação

1. [OK] **Filtragem nearest (`ResampleMode = Pixelated`) só funciona de fato em `ImageLabel`/`ImageButton`**, em qualquer `LayerCollector`, inclusive `SurfaceGui` e `BillboardGui`.
   - `Decal`, `Texture`, `MaterialVariant`, `ParticleEmitter`, `Beam` e `Trail` **não têm** propriedade de filtragem. Usam bilinear com mipmaps e streaming.
   - `SurfaceAppearance.ResampleMode` existe na API desde a v716 (abr/2026), mas em ago/2026 ainda aparecia como **"Pending"/não funcional** [CONFLITO].
2. [OK] **Pixel art de UI sofre compressão de bloco com perdas no mobile.** A equipe Roblox (jul/2025) disse que é "unavoidable for performance on certain platforms" e que não há trabalho planejado para resolver.
   - Pixels transparentes viram preto no upload, o que causa franjas escuras com filtragem bilinear.
   - [DICA] Faça upscale inteiro (4–8×) antes do upload, aplique alpha-bleed e teste em aparelho real.
3. [OK] **Flipbooks de partículas:**
   - `FlipbookBlendFrames` foi adicionado em mar/2026 e tem **default `true`** (crossfade). Use `false` para troca seca de frames em pixel art.
   - Layout `Custom` (`FlipbookSizeX/Y` de 1–64, texturas não quadradas e não potência de 2) saiu em Client Beta em out/2025.
   - Limite de 30 fps.
   - Clientes com pouca memória **desativam** flipbooks.
4. [OK] **EditableImage:**
   - Máximo de 1024×1024; default 512×512.
   - Criação retorna `nil` se o orçamento de memória do dispositivo acabar.
   - **Só 1 EditableImage exibida é atualizada por frame.**
   - Exige o toggle "Allow Mesh / Image APIs" e, segundo o anúncio, dono 13+ com ID verificado.
   - `Content.fromObject(editableImage)` **não replica** (vira tabuleiro ciano/magenta). Para levar do servidor ao cliente, use `AssetService:CreateDataModelContentAsync` (GA em mai/2026, conteúdo opaco, sem moderação, 200 MB no servidor).
5. [OK] **Upload via Open Cloud:**
   - `POST https://apis.roblox.com/assets/v1/assets` (multipart: `request` + `fileContent`), header `x-api-key`, escopos `asset:read` + `asset:write`.
   - Faça polling de `GET /assets/v1/operations/{id}`.
   - **Use `assetType: "Image"`** (a doc oficial de ícones usa). `"Decal"` devolve um ID de Decal que **não funciona** em `ImageLabel.Image` via script.
   - Limites: 120 req/min (create) e 300 req/min (operations).
6. [OK] **Studio MCP:**
   - O `Roblox/studio-rust-mcp-server` **não é mais desenvolvido**.
   - O recomendado é o **MCP embutido no Studio**: Assistant ⟩ … ⟩ Manage MCP Servers ⟩ "Enable Studio as MCP server". Conecta por stdio, com quick connect para Claude Code e Claude Desktop.
   - São 26 ferramentas documentadas, mais `open_cloud_invoke` (adicionada em 4–5/nov/2026). Entre elas: `execute_luau` (com `datamodel_type` Edit, Client ou Server), `upload_image` (a partir de URLs HTTP), `store_image`, `screen_capture` e `inspect_instance`.
   - Toda chamada exige `studio_id` (desde ago/2026).
   - Roda como processo **local** junto ao Studio (Windows/macOS). Um container na nuvem não o alcança diretamente.
7. [OK] **UIGradient "upgraded"** (Type Radial/Conical/Elliptical, `Scale`, `TileMode`) virou **full release em 29/out/2026**.
   - A interpolação de cor passou a ser em espaço linear.
   - A equipe recomenda não passar de ~1000 gradientes e animar `Offset`/`Rotation`, não `Color`/`Transparency`.
   - Melhorias de UIStroke (`StrokeSizingMode`, `BorderStrokePosition`) estão em full release desde dez/2025.
8. [OK] **Fusion:**
   - O release estável continua sendo **0.3** (2024-08-30). O `main` é 0.4-dev, não lançado.
   - No código-fonte, `Scope<Constructors = any>`, então anote `Fusion.Scope<typeof(Fusion)>`.
   - `scope:New` devolve `Instance`; faça cast com `:: ImageLabel`.
   - O agendador do Fusion no cliente usa `BindToRenderStep(RenderPriority.First)`.
9. [OK] **Luau:**
   - `utf8.graphemes` é extensão **só do Roblox** (não está no Luau padrão) e retorna pares `(first, last)` de bytes.
   - O novo type solver está em GA desde nov/2025 para nonstrict. Scripts `--!strict` continuam no solver antigo, a menos que `Workspace.UseNewLuauTypeSolver = Enabled`.
   - `table.freeze` só tem tipagem read-only no solver novo.

---

## 1. Renderização de imagens

### 1.1 `ResampleMode` / `Enum.ResamplerMode`

- [OK] **Enum `ResamplerMode`:**
  - `Default = 0`: "Bilinear filtering of the four near pixels in the image".
  - `Pixelated = 1`: "Nearest neighbor filtering of the closest pixel in the image".
  - Fonte: https://create.roblox.com/docs/reference/engine/enums/ResamplerMode
- [OK] **Classes e lugares que usam o enum** (busca por `ResamplerMode` no `creator-docs` de 2026-11-06):

  | Onde | Estado |
  |---|---|
  | `ImageLabel.ResampleMode` | [OK] funcional. Lançado em 16/ago/2021 (https://devforum.roblox.com/t/resamplemode-new-property-for-image-gui-objects/1418681). Doc: https://create.roblox.com/docs/reference/engine/classes/ImageLabel |
  | `ImageButton.ResampleMode` | [OK] funcional (https://create.roblox.com/docs/reference/engine/classes/ImageButton) |
  | `SurfaceAppearance.ResampleMode` | [CONFLITO] documentado ("When set to `Pixelated`, the textures preserve the sharp edges of pixels using nearest-neighbor filtering", https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance). Adicionado na v716 em 2026-04-07 (https://robloxapi.github.io/ref/class/SurfaceAppearance.html). **Em 26–28/ago/2026 ainda "Pending" nas release notes**; usuário relatou que setar via script "doesn't seem to work"; tnavarts (Roblox): "Can confirm that ResampleMode is not forgotten", atrasado por "infrastructure changes" (https://devforum.roblox.com/t/release-notes-for-736/4833635?page=2, https://devforum.roblox.com/t/pixelated-resamplemode-for-surfaceappearances-pixel-art-meshes/4028314?page=4). [NAO CONFIRMADO] **Não confirmado se já funciona em nov/2026.** |
  | `VideoDisplay.ResampleMode` | Classe `VideoDisplay` está com tag `NotBrowsable`, ou seja, não lançada (https://create.roblox.com/docs/reference/engine/classes/VideoDisplay) |
  | `EditableImage:DrawImageTransformed(..., {SamplingMode = Enum.ResamplerMode.Pixelated})` | [OK] nearest ao escalar ou rotacionar dentro do EditableImage (seção 3) |
  | `StudioCaptureService:CaptureScreenshot({ResampleMode = ...})` | [OK] só para plugins (PluginSecurity); útil para preview e QA (https://create.roblox.com/docs/reference/engine/classes/StudioCaptureService) |

- [OK] **Aviso do anúncio de 2021:** "The nearest neighbor filtering can result in aliasing and shimmering during size reduction". Com Pixelated, reduzir a imagem gera shimmering.
- [OK]/[NAO CONFIRMADO] **`SurfaceGui`/`BillboardGui`:** `ResampleMode` é propriedade do `ImageLabel`/`ImageButton`, então vale em qualquer container.
  - Há tutorial da comunidade (fev/2025) de "pixel-perfect 3D objects" com `SurfaceGui` + `ImageLabel` Pixelated: "corners of each pixel are crisp and sharp".
  - Contra: a part não aparece corretamente em `ViewportFrame`.
  - Fonte: https://devforum.roblox.com/t/cool-pixel-perfectnearest-neighborpixel-perfect-3d-objects/3479864
  - Em BillboardGui, o borrão com a distância costuma vir de escala/`PixelsPerStud`, não do resample. [NAO CONFIRMADO] Não há confirmação oficial específica para BillboardGui.

### 1.2 Texturas 3D e partículas: dá para usar nearest?

- [OK] **Nenhuma propriedade de filtragem** em `Decal`, `Texture`, `MaterialVariant`, `ParticleEmitter`, `Beam` e `Trail` (listas de propriedades no `creator-docs` de 2026-11-06).
  - O `Decal` ganhou mapas PBR: `ColorMapContent`, `NormalMapContent` etc.
  - Fontes: https://create.roblox.com/docs/reference/engine/classes/Decal, https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
- [OK] **Motivo citado:** a staff disse que adicionar ResampleMode a Textures/Decals legados "isn't possible due to backwards compatibility". É informação de segunda mão: os posts da staff foram apagados e o relato é de usuário.
  - Fonte: https://devforum.roblox.com/t/pixelated-resamplemode-for-surfaceappearances-pixel-art-meshes/4028314
- [OK] **Partículas usam mip filtering:** "In some cases, mip filtering might require even more spacing" (https://create.roblox.com/docs/effects/particle-emitters).
- [OK] **Texture streaming** carrega mips progressivamente e abrange MeshPart, SurfaceAppearance, Texture, Decal, MaterialVariant, Beam, ParticleEmitter e materiais base.
  - Fonte: https://create.roblox.com/docs/parts/textures-decals
  - Em dispositivos com pouca memória, cair para mips menores foi descrito pela staff como "not a bug" (citado em https://devforum.roblox.com/t/compression-of-pixelated-imagelabels-on-mobile-unavoidably-ruins-our-games-aesthetic-graphics/2506241).
- [OK] **4K:** "4k Texture Rendering" foi anunciado em 30/jan/2026 para MeshPart, SurfaceAppearance, Texture, Decal e MaterialVariant via streaming. GUI não é mencionada.
  - Fonte: https://devforum.roblox.com/t/4k-texture-rendering/4316229
- [NAO CONFIRMADO] **`ParticleEmitter2D`** foi adicionada na v744 (2026-10-19) com tag `NotBrowsable`, ou seja, não lançada. Tem `FlipbookBlendFrames` etc., mas não tem ResampleMode.
  - Fonte: https://robloxapi.github.io/ref/class/ParticleEmitter2D.html
- [DICA] **Workarounds para pixel art em 3D e partículas:**
  - Upload com upscale inteiro por nearest (por exemplo 16→256 ou 32→512), para que o bilinear e o mip atuem em blocos grandes.
  - `SurfaceGui` + `ImageLabel` Pixelated em superfícies planas.
  - Upscale em runtime com `EditableImage:DrawImageTransformed` e `SamplingMode = Pixelated` (≤1024; sugerido no tutorial acima).

### 1.3 `ScaleType`, `SliceCenter`, `SliceScale`, `TileSize`

- [OK] **`Enum.ScaleType`** (https://create.roblox.com/docs/reference/engine/enums/ScaleType):
  - `Stretch=0`: estica até preencher.
  - `Slice=1`: 9-slice, com limites em `SliceCenter`.
  - `Tile=2`: repete; "if the element is twice the X dimension of the image, the image will appear twice".
  - `Fit=3`: escala até caber no eixo que "fits first".
  - `Crop=4`: recorta para cobrir.
- [OK] **`SliceCenter` (`Rect`):**
  - Define a região central do 9-slice e só aparece no Properties quando `ScaleType = Slice`.
  - Cantos não escalam, bordas escalam em 1 eixo e o centro escala nos 2.
  - No editor 9-slice, os offsets são distâncias até cada borda, **diferentes** dos valores de `SliceCenter` (que são `Rect(minX, minY, maxX, maxY)` em pixels da imagem).
  - Fontes: https://create.roblox.com/docs/reference/engine/classes/ImageLabel, https://create.roblox.com/docs/ui/9-slice
- [OK] **`SliceScale`** (float, default `1.0`): "Scales the 9-slice edges by the specified ratio… as if you'd uploaded a new version of the texture upscaled".
  - [DICA] Para pixel art, use `SliceScale` inteiro (2, 3, 4…) junto com `ResampleMode = Pixelated`.
- [OK] **`TileSize`** (`UDim2`, default `UDim2.new(1,0,1,0)`): o tiling começa no canto superior esquerdo e só vale com `ScaleType = Tile`.
- [NAO CONFIRMADO] **SliceCenter com ImageRectOffset:** relatos da comunidade dizem que 9-slice funciona combinado com `ImageRectOffset`/`ImageRectSize` e que `SliceCenter` é relativo ao sub-retângulo. Não está na doc oficial.
  - Fonte: https://devforum.roblox.com/t/how-to-use-slicecenter-robloxs-9-slice-gui-property/18313

### 1.4 `ImageRectOffset` / `ImageRectSize` (sprite sheets) e bleeding

- [OK] `ImageRectOffset` é o offset em pixels a partir do canto superior esquerdo.
- [OK] `ImageRectSize` é o tamanho em pixels. "If either dimension is set to 0, the entire image is displayed instead".
- [OK] A doc recomenda sprite sheets: "Packing multiple images into one… can make your experience's image assets load much quicker".
- Fontes: https://create.roblox.com/docs/reference/engine/classes/ImageLabel e "consider using sprite sheets… `ImageRectOffset` and `ImageRectSize`" em https://create.roblox.com/docs/performance-optimization/improve
- [OK]/[CONFLITO] **Bleeding:** com escala e filtragem bilinear, amostras na borda puxam pixels vizinhos do atlas. A comunidade recomenda gutters ou extrusão de cerca de 2 px por tile, ou renderizar na resolução nativa.
  - Fontes: https://devforum.roblox.com/t/imagerectoffsetsize-issues/224476, https://devforum.roblox.com/t/strange-bleeding-using-tiles/513951. Não há doc oficial sobre isso.
- [DICA] Mesmo com Pixelated, use 1–2 px de padding com borda extrudada. Alinhe sprites a uma grade múltipla de 4 px, porque a compressão de bloco do mobile trabalha em blocos e mistura cores dentro de cada bloco. Isso é inferência sobre formatos de GPU, [NAO CONFIRMADO] não documentado pela Roblox.

### 1.5 Upload: dimensões, formatos, compressão, transparência e moderação

- [OK] **Formatos:**
  - Importer e Asset Manager: `.png`, `.jpg`, `.gif`, `.tga`, `.bmp` (https://create.roblox.com/docs/studio/importer).
  - Open Cloud, para Decal/Image: `.png`, `.jpeg`, `.bmp`, `.tga` (`image/png`, `image/jpeg`, `image/bmp`, `image/tga`) (https://create.roblox.com/docs/cloud/guides/usage-assets).
- [OK] **Dimensões no Open Cloud:**
  - Decal/Image "Must be smaller than 8000x8000 pixels", com arquivo de até 20 MB por chamada.
  - "Not available for updating": não dá para criar nova versão de imagem.
  - Fonte: https://create.roblox.com/docs/cloud/guides/usage-assets
- [OK]/[CONFLITO] **Resolução efetiva:**
  - texture-specifications: "Roblox supports up to 4096×4096 pixel texture resolutions (4K)… engine automatically starts with lower quality versions… and ramps up" (https://create.roblox.com/docs/art/modeling/texture-specifications).
  - Anúncio 4K (30/jan/2026): imagens de até 8K são armazenadas e transcodificadas para até 4K em instâncias com streaming.
  - **Para GUI (`ImageLabel`)** não há confirmação de nada acima de 1024. O limite prático citado pela comunidade é 1024 no maior eixo.
  - Bug report de mar/2026: a página de upload de Decal ainda diz "downsized to 1024x1024", e um usuário em 30/jun/2026 disse que "decals are still getting downsized" (https://devforum.roblox.com/t/decal-upload-page-still-mentions-1024x1024-limit-instead-of-4096x4096/4526770).
  - [NAO CONFIRMADO] **Limite para GUI em nov/2026: não confirmado.** [DICA] Mantenha atlases de UI em ≤1024×1024.
- [OK] **Transcodificação e memória:**
  - "Images uploaded to Roblox are transcoded to a fixed format, so there is no memory benefit to uploading images in a color model associated with fewer bytes per pixel".
  - "a 1024x1024 pixel texture consumes four times the graphics memory of a 512x512".
  - Recomendação oficial: "at most 512x512… Most minor images should be smaller than 256x256".
  - Fonte: https://create.roblox.com/docs/performance-optimization/improve
- [OK] **Compressão com perdas no mobile (crítico para pixel art):**
  - Report de ago/2023 sobre ImageLabels Pixelated.
  - Staff m0bsterlobster (1/jul/2025): a compressão é "unavoidable for performance on certain platforms" e "we currently do not have specific work planned to directly address this particular artifact".
  - Workaround relatado: upscale dos sprites de 4× a 8×.
  - Fontes: https://devforum.roblox.com/t/compression-of-pixelated-imagelabels-on-mobile-unavoidably-ruins-our-games-aesthetic-graphics/2506241, https://devforum.roblox.com/t/ui-pixel-art-affected-by-heavy-color-compression-on-mobile-devices/3245665
- [OK] **Transparência:** "Since transparent pixels are set to black when uploading to Roblox, transparent images should apply alpha blending to avoid a blackish outline around scaled images".
  - Fonte: `ImageLabel.ScaleType` em https://create.roblox.com/docs/reference/engine/classes/ImageLabel
  - [DICA] Faça alpha-bleed: copie a cor das bordas para os pixels com alpha 0.
- [OK] **Moderação:**
  - É humana e automática, "generally happens within a few hours".
  - Enquanto o asset está na fila, "users cannot see or interact with the asset until Roblox approves it".
  - `ImageLabel.IsLoaded`: "Images declined by moderation will never load".
  - Fontes: https://create.roblox.com/docs/projects/assets, https://create.roblox.com/docs/reference/engine/classes/ImageLabel
- [OK] **Preload:** `ContentProvider:PreloadAsync` funciona com `ImageLabel`/`Decal`. Se a instância não estiver visível, a engine "may reduce memory consumption by unloading the textures after preloading". Não suporta `SurfaceAppearance`/`MaterialVariant`.
  - Fonte: https://create.roblox.com/docs/reference/engine/classes/ContentProvider

---

## 2. Flipbooks de `ParticleEmitter`

- [OK] **`FlipbookLayout`** (`Enum.ParticleFlipbookLayout`):
  - `None=0`, `Grid2x2=1` (4 frames), `Grid4x4=2` (16), `Grid8x8=3` (64).
  - `Custom=4`, com `FlipbookSizeX` (colunas) e `FlipbookSizeY` (linhas), que só valem em Custom.
  - Fontes: https://create.roblox.com/docs/reference/engine/enums/ParticleFlipbookLayout, https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
- [OK] **`FlipbookMode`** (`Enum.ParticleFlipbookMode`):
  - `Loop=0`.
  - `OneShot=1`: ignora `FlipbookFramerate`; o fps é `Lifetime / nº de frames`.
  - `PingPong=2`.
  - `Random=3`: ordem aleatória "blending/crossfading".
  - Fonte: https://create.roblox.com/docs/reference/engine/enums/ParticleFlipbookMode
- [OK] **`FlipbookFramerate`:** `NumberRange` (min/max aleatório), com "a maximum of 30 frames per second".
- [OK] **`FlipbookStartRandom`:** cada partícula começa num frame aleatório. Com `FlipbookFramerate = 0`, cada partícula vira um frame estático aleatório, o que é útil para variações de sprite.
- [OK] **`FlipbookBlendFrames` (bool):**
  - "whether the frames… are blended between using a linear crossfade, or swapped instantly".
  - Adicionado na v711 (2026-03-02) com **default `true`** (https://robloxapi.github.io/ref/class/ParticleEmitter.html).
  - [DICA] Para pixel art, **defina `false`**.
  - Contexto: em 2022 a comunidade pedia uma opção para desligar o fade entre sprites (https://devforum.roblox.com/t/particles’-flipbook-release/2029388).
- [OK] **Requisitos de textura, em ordem cronológica:**
  1. Beta (18/mar/2022): textura 1024×1024 com grade 2x2, 4x4 ou 8x8 (https://devforum.roblox.com/t/animated-particles-with-the-particle-flipbooks-beta/1718023).
  2. Release (21/out/2022): "any resolution that is squared and a power of two", de 8×8 a 1024×1024. Layouts renomeados (`TwoByTwo` → `Grid2x2` etc.). Recomenda "a little spacing around your frames" (https://devforum.roblox.com/t/particles’-flipbook-release/2029388).
  3. **Client Beta (13/out/2025):** "the square texture size requirement has been removed". Aceita não potência de 2 (por exemplo 512×256 em Grid4x4). `FlipbookSizeX/Y` inteiros de 1 a 64. Pode mudar a aparência de emissores antigos com textura incompatível (https://devforum.roblox.com/t/client-beta-optimize-your-particle-animations-with-custom-flipbook-layouts/4005128). [CONFLITO] GA não confirmado, embora o enum já esteja documentado sem aviso de beta.
- [CONFLITO] **Conflito na própria referência:**
  - `FlipbookIncompatible` diz "texture size must be an exact multiple of the flipbook layout size". O valor default da string é o legado "Particle texture must be 1024 by 1024 to use flipbooks.".
  - O enum `ParticleFlipbookTextureCompatible` diz "Flipbook playback requires a 1024×1024 texture", o que parece desatualizado.
  - Fontes: https://create.roblox.com/docs/reference/engine/enums/ParticleFlipbookTextureCompatible, https://robloxapi.github.io/ref/class/ParticleEmitter.html
  - [DICA] Para o caminho mais seguro, use dimensões múltiplas exatas da grade e, se possível, quadradas e potência de 2.
- [OK] **Guia oficial de textura:**
  - "include spacing between each of the particle frames. In some cases, mip filtering might require even more spacing".
  - "clients automatically deactivate flipbooks when they are low on memory, which is likely for older mobile phones".
  - "Reusing textures costs less memory than using unique textures".
  - Para textura sem alpha, use `LightEmission = 1` "to hide the darker regions"; o formato recomendado é PNG com fundo transparente.
  - Fonte: https://create.roblox.com/docs/effects/particle-emitters
- [DICA] **Pixel art em partículas:** nearest não existe aqui (seção 1.2). Faça upscale nearest de cada frame antes de montar a folha (por exemplo frames de 16 px → 128 px numa folha 1024 em 8x8) e mantenha gutters transparentes.

---

## 3. `EditableImage`: API atual e disponibilidade

Fontes: https://create.roblox.com/docs/reference/engine/classes/EditableImage, https://create.roblox.com/docs/reference/engine/classes/AssetService

- [OK] **Criação:**
  - `AssetService:CreateEditableImage({ Size = Vector2.new(w, h) })`. "By default, the resolution is set at 512×512". Retorna `nil` "if the device-specific editable memory budget is exhausted".
  - `AssetService:CreateEditableImageAsync(content: Content, options?)` carrega uma imagem existente (aceita `rbxthumb://`). A imagem precisa ser do dono, do usuário do Studio ou do jogador (no cliente), compartilhada com eles, ou de grupo com permissão de edição. Caso contrário, erro.
  - Classe `NotCreatable`; herda de `Object`, não de `Instance`.
- [OK] **Tamanho:** `EditableImage.Size` é read-only. "The maximum size is 1024×1024". Para redimensionar, crie outra e use `DrawImageTransformed`.
- [OK] **Métodos (2026-11-06):**
  - `DrawCircle(center, radius, color, transparency, combineType, antiAliasing = Enabled, alphaBlendType = Default)`.
  - `DrawLine(p1, p2, color, transparency, combineType, antiAliasing = Enabled, alphaBlendType)`.
  - `DrawRectangle(position, size, color, transparency, combineType, alphaBlendType)`. A posição não pode sair do canvas.
  - `DrawImage(position, image: EditableImage, combineType, alphaBlendType)`.
  - `DrawImageTransformed(position, scale: Vector2, rotation (graus), image, options?)`. `options` aceita:
    - `CombineType`, com default `AlphaBlend`.
    - `SamplingMode`: `Enum.ResamplerMode.Default`/**`Pixelated`**.
    - `PivotPoint`, com default `Size/2`.
    - `AlphaBlendType`.
  - `DrawImageProjected`, `SampleImageProjected`.
  - `ReadPixelsBuffer(position, size) -> buffer` e `WritePixelsBuffer(position, size, buffer)`: RGBA, 4 bytes por pixel, `Size.X*Size.Y*4` bytes, **usando alpha e não transparency**.
  - `Destroy()` libera a memória imediatamente.
  - `alphaBlendType` diferente de `Default` "is not yet available".
  - [DICA] Para pixel art gerada, desenhe com `antiAliasing = Enum.AntiAliasing.Disabled` e escale com `SamplingMode = Pixelated`.
- [OK] **Exibição:** "`EditableImage` can be used in any `Content` property which takes an image, such as `ImageLabel.ImageContent` or `MeshPart.TextureContent`… by setting the content property to `Content.fromObject(editableImage)`".
  - `Content.fromObject` mantém uma referência forte.
  - Fonte: https://create.roblox.com/docs/reference/engine/datatypes/Content
- [OK] **Limite de atualização:** "Only a single `EditableImage` can be updated per frame on the display side… three objects… three frames".
  - [DICA] Isso derruba a ideia de animar muitos sprites via EditableImage. Para animação, use sprite sheet com `ImageRectOffset`.
- [OK] **Replicação:**
  - "Replication is not yet supported for `Content.Object` values". O cliente recebe um placeholder que renderiza "as a cyan and magenta checkerboard pattern".
  - "do not use `EditableImage`… as `Content` on the server on an Instance that can replicate". Fonte: https://create.roblox.com/docs/reference/engine/datatypes/Content
- [OK] **`AssetService:CreateDataModelContentAsync(content, options?) -> (Enum.CreateContentResult, Content)`:**
  - Recebe EditableImage ou EditableMesh e gera `Content` com `SourceType = Opaque`, com escopo da sessão do DataModel.
  - Anúncio de 27/mar/2026, disponível em experiências publicadas desde 18/mai/2026.
  - Replica **do servidor para o cliente**; "do not need to go through moderation first".
  - Não consome orçamento Editable; vai para disco.
  - Servidor limitado a 200 MB; falha com `StorageLimitExceeded`.
  - Fontes: https://devforum.roblox.com/t/full-release-introducing-createdatamodelcontent-convert-editable-mesh-and-image-data-into-static-content/4541898, https://create.roblox.com/docs/reference/engine/classes/AssetService
- [OK] **Memória:** "strict client-side memory budgets, although the server, Studio, and plugins operate with unlimited memory". Reutilizar um EditableImage em vários `Content` ajuda.
  - O orçamento é dinâmico e sem números públicos. "one 1k x 1k image uses the same budget as four 512 x 512 images" (https://devforum.roblox.com/t/client-beta-in-experience-mesh-image-apis-now-available-in-published-experiences/3267293).
- [OK]/[CONFLITO] **Publicação:**
  - "using `EditableImage` fails by default in published games". Ative em Creator Dashboard ⟩ Configure ⟩ Settings ⟩ **Enable Mesh / Image APIs**, ou em Studio ⟩ Experience Settings ⟩ Security ⟩ **Allow Mesh / Image APIs** (doc EditableImage).
  - O anúncio de nov/2024 exige que o dono da experiência (ou o dono do grupo) seja "13+, ID-verified, and explicitly opted-in".
  - Em 18/mai/2026 a equipe ainda dizia trabalhar em soluções para "strict permissions and ID verification requirements", ou seja, o requisito continuava.
  - [CONFLITO] A doc atual não menciona ID verification.
  - [NAO CONFIRMADO] **Não há restrição documentada por idade do jogador.** A restrição é sobre o dono/criador.
- [OK] **Plugins e Studio:**
  - "Plugins using these APIs in Edit Mode are not subject to the memory budget" e não precisam do toggle (exceto um known issue com Team Create em 2024; [NAO CONFIRMADO] não confirmado se foi corrigido).
  - [DICA] Um plugin, e provavelmente a command bar, que roda com permissões de plugin em Edit, pode criar EditableImage para preview. [NAO CONFIRMADO] Para a command bar, não confirmado explicitamente.
- [OK] **Publicar EditableImage como asset:**
  - `AssetService:PromptCreatePlatformContentAsync(player, editableImage, Enum.AssetType.Image)`: só no servidor, com place publicado, toggle ligado e prompt ao jogador (https://create.roblox.com/docs/projects/assets/in-experience-asset-creation).
  - `AssetService:CreateAssetAsync(editableImage, Enum.AssetType.Image, {Name=…, Description=…, CreatorId=…, CreatorType=…})`: "can only be used in locally loaded plugins and uploads assets without prompting first". Também roda no contexto Open Cloud Luau Execution, exigindo CreatorId/CreatorType.
  - [DICA] É uma rota de upload de sprites gerados a partir do Studio.

---

## 4. Performance de GUI

- [OK] **`CanvasGroup`** (https://create.roblox.com/docs/reference/engine/classes/CanvasGroup):
  - Achata os descendentes numa textura e aplica `GroupColor3`/`GroupTransparency`.
  - `ClipsDescendants` é sempre `true`.
  - **Só achata se o `LayerCollector` tiver `ZIndexBehavior = Sibling`.**
  - "consumes extra texture memory… limited by the `QualityLevel`… When exceeding the memory cap, `CanvasGroup` will render as a blank texture".
  - Recomenda "static sizes", senão a textura é recriada.
  - Anúncio beta (19/mai/2022): textura extra de `AbsoluteSize.x * AbsoluteSize.y` (com DPI); "down-res fallbacks when the system is high on texture memory pressure"; em gráficos baixos, "display result downscaled as well as animations getting throttled"; "Text is blurry under CanvasGroups" como known issue (https://devforum.roblox.com/t/canvasgroup-beta-group-transparency-on-ui-groups/1797885).
  - MicroProfiler `Perform/Scene/UI`: "Reduce the number of visible UI elements. Using CanvasGroups can help at the expense of increased memory use" (https://create.roblox.com/docs/performance-optimization/microprofiler/tag-table).
  - [DICA] Para pixel art, evite CanvasGroup em telas grandes; o down-res borra os pixels. Use-o só para fades curtos.
- [OK] **`UIGradient`** (https://create.roblox.com/docs/reference/engine/classes/UIGradient):
  - Propriedades: `Color` (ColorSequence), `Transparency` (NumberSequence; "envelope values… are ignored"), `Offset` (escalar, relativo a `AbsoluteSize`), `Rotation` (graus, horário), `Scale`, `TileMode` (`Clamp`/`Repeat`/`Mirror`) e `Type` (`Linear`/`Radial`/`Conical`/`Elliptical`).
  - Não se aplica a descendentes nem a `ScrollingFrame`/`TextBox`.
  - Guia de performance:
    - "Avoid using more than 6 color stops".
    - Evite gradiente sobre texto com `TextStrokeColor3`.
    - "Avoid setting `Color` and `Transparency` frequently… rebuild… expensive… animate the `Offset` or `Rotation`".
    - Tradeoff entre UIGradient (CPU) e imagem estática (memória).
  - **"Upgraded UI Gradients"** (Studio Beta em 2/set/2026, **full release em 29/out/2026**, Elliptical incluído):
    - "Avoid using more than 1000 gradients at a time".
    - "Animating gradient scale, tile mode, type, offset, rotation is cheaper than animating color or transparency".
    - Gradientes iguais são deduplicados.
    - **Cores agora interpolam em espaço linear**, não em sRGB.
    - Known issue de banding em gradientes escuros.
    - Fonte: https://devforum.roblox.com/t/studio-beta-upgraded-ui-gradients/4846594
  - [CONFLITO] A página https://create.roblox.com/docs/ui/appearance-modifiers ainda mostra aviso de beta (doc defasada).
- [OK] **`UIStroke`** (https://create.roblox.com/docs/reference/engine/classes/UIStroke):
  - `Thickness` em pixels (`StrokeSizingMode.FixedSize`, o padrão) ou relativo ao menor eixo do pai (`ScaledSize`; em texto, relativo ao tamanho da fonte).
  - `BorderStrokePosition` (`Outer`/`Center`/`Inner`), `BorderOffset` (UDim), `LineJoinMode`, `ZIndex`, e múltiplos strokes de borda.
  - "Be mindful of tweening this `UIStroke` property when applied to text objects. This renders and stores many glyph sizes each frame".
  - Melhorias: Studio Beta em 25/set/2025, Client Beta em 6/nov/2025, **Full Release em 4/dez/2025** (https://devforum.roblox.com/t/studio-beta-uistroke-improvements-scaling-offsets-and-more/3958036).
  - Relato da comunidade: `Thickness` em FixedSize escala com `UIScale`, mas `BorderOffset` não (https://devforum.roblox.com/t/uistrokeborderoffset-does-not-respect-uiscale/4025794).
  - [NAO CONFIRMADO] Nitidez de traço fino e fracionário não está documentada.
  - [DICA] Para pixel art, prefira contorno "assado" no sprite ou `Thickness` inteiro em FixedSize.
- [OK] **`ZIndexBehavior`:**
  - `Sibling` (o default em `LayerCollector`): filhos sempre acima do pai; `ZIndex` ordena irmãos.
  - `Global`: ordena todos por `ZIndex`.
  - Fonte: https://create.roblox.com/docs/reference/engine/classes/LayerCollector
  - O `New` do Fusion 0.3 define `ZIndexBehavior = Sibling` e `ResetOnSpawn = false` em ScreenGui (seção 7).
- [OK] **Loop de frame:**
  - `PreRender` é o "replacement for `RenderStepped`". Roda antes do render, só no cliente, e deve ser "used sparingly as the engine cannot start to render the frame until code running in this event has finished".
  - `Heartbeat` roda depois da física, no fim do frame, onde "most scripts run".
  - `RenderStepped` e `Stepped` são legados.
  - Fonte: https://create.roblox.com/docs/reference/engine/classes/RunService
  - Boas práticas: "Don't connect/bind functions to the render step unless absolutely necessary… For strict control over order, use `BindToRenderStep()` instead of `PreRender`" (https://create.roblox.com/docs/performance-optimization/microprofiler/task-scheduler).
  - [DICA] Animação de sprite (troca de `ImageRectOffset` a 8–12 fps) pode rodar em `Heartbeat` ou num acumulador em `PreRender`. Não faça trabalho pesado em PreRender.
- [OK] **TweenService:** interpola number, bool, CFrame, Rect, Color3, UDim, UDim2, Vector2, Vector2int16, Vector3 e EnumItem. Dois tweens na mesma propriedade fazem o primeiro ser cancelado (https://create.roblox.com/docs/reference/engine/classes/TweenService). [NAO CONFIRMADO] Não há números oficiais de custo por tween.
- [OK] **Layouts:** flex em `UIListLayout` "adds a slight performance cost… especially when resizing the layout or dynamically adding/removing flex items" (https://create.roblox.com/docs/ui/list-flex-layouts).
- [NAO CONFIRMADO] **Pooling de GuiObject e limite de objetos animados no mobile:** **não há número nem guia oficial.** A doc oficial fala de pooling só para NPCs (https://create.roblox.com/docs/performance-optimization/improve). Um guia de terceiros cita queda de 10–20 FPS com centenas de GuiObjects mudando, sem benchmark e sem confiabilidade.
  - [DICA] Meça com o MicroProfiler (`Perform/Scene/UI` e Id_Screen, que mostra contagem de batches) em aparelho alvo. Reuse instâncias em vez de criar e destruir por frame. Reutilize o mesmo asset (atlas) para batching.

---

## 5. Automação de upload (Open Cloud Assets API) e importação em massa

### 5.1 Fatos da API

- [OK] **Endpoint de criação:** `POST https://apis.roblox.com/assets/v1/assets`, com corpo `multipart/form-data`:
  - campo `request`: JSON do `Asset`;
  - campo `fileContent`: binário com content-type.
  - O header `x-api-key` é obrigatório em todos os endpoints.
  - Estabilidade marcada como **BETA** no OpenAPI.
  - Fontes: https://create.roblox.com/docs/cloud/guides/usage-assets, https://create.roblox.com/docs/cloud/reference/features/assets
- [OK] **JSON `request`:**
  - `assetType`, `displayName` e `description` são obrigatórios no Create; `description` aceita até 1000 caracteres.
  - `creationContext.creator.userId` ou `creationContext.creator.groupId`.
  - Opcionais: `creationContext.expectedPrice` (se o preço real for maior, falha com 400) e `assetPrivacy`.
  - Fonte: schema `Asset`/`CreationContext` em https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/cloud/assets/v1.json
- [OK] **`assetType: "Image"`:** é usado na doc oficial atual para ícones e thumbnails, com o pedido "Read `response.assetId`" (https://create.roblox.com/docs/cloud/guides/experience-icons-and-thumbnails).
  - Evidência da comunidade (PR de 27/set/2026): ícones reenviados como `Image` passaram a renderizar em `ImageButton.Image`, enquanto IDs de `Decal` "don't resolve" (https://github.com/Vsad-Laboratories/Party-Panic/pull/22).
  - [OK] Com `"Decal"`, a API devolve o ID do **Decal**, e não há API estável para obter o Image ID (https://devforum.roblox.com/t/provide-a-stable-open-cloud-api-to-get-an-image-id-from-a-decal-id/3594046).
- [OK] **Escopos:** `asset:read` + `asset:write` no Create; `asset:read` no Get Operation.
  - API key: Creator Dashboard ⟩ API Keys ⟩ adicionar o sistema **assets** com Read/Write.
  - Para assets de grupo, é preciso permissão no grupo.
  - Restrição de IP (CIDR) e expiração são opcionais.
  - **Chave sem uso por 60 dias expira.**
  - Fontes: https://create.roblox.com/docs/cloud/guides/usage-assets, https://create.roblox.com/docs/cloud/auth/api-keys
- [OK] **Resposta do Create:** `Operation` no formato `{ "path": "operations/{operationId}" }`.
- [OK] **Polling:** `GET https://apis.roblox.com/assets/v1/operations/{operationId}`.
  - `done=false` significa em progresso; com `done=true`, vem `response` (Asset) ou `error`.
  - O exemplo de resposta traz `assetId`, `revisionId`, `assetType: "ASSET_TYPE_DECAL"` e `moderationResult.moderationState: "MODERATION_STATE_APPROVED"`. O schema descreve os estados como `Reviewing`/`Rejected`/`Approved`.
  - [DICA] Trate `done` ausente como `false`: é JSON estilo proto3, e isso não está documentado.
- [OK] **Rate limits** (OpenAPI `x-roblox-rate-limits`): Create = 120/min por dono da API key; Get Operation = 300/min.
  - Fonte: https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/cloud/openapi.json
- [OK] **Uso no jogo:** use `rbxassetid://<assetId>` no Properties ou `Content.fromAssetId(assetId)` em propriedades `Content` (https://create.roblox.com/docs/cloud/guides/usage-assets).
- [OK] **Studio:**
  - O Asset Manager faz "bulk import" de imagens, malhas, áudio etc. Os assets "enter the moderation queue and, upon approval, are added to the inventory".
  - O Importer tem fila para vários arquivos.
  - O Asset Manager filtra por tipos `Decal` e `Image` separadamente.
  - Fontes: https://create.roblox.com/docs/projects/assets/manager, https://create.roblox.com/docs/studio/importer
  - [NAO CONFIRMADO] Se o bulk import gera Image ou Decal em cada caso: não confirmado oficialmente. A comunidade recomenda copiar o **Image ID** no Asset Manager.

### 5.2 Esqueleto Python ([DICA] baseado nos fatos acima; requer `pip install requests`)

```python
#!/usr/bin/env python3
"""Envia PNGs como assets 'Image' via Open Cloud. Lê ROBLOX_API_KEY e ROBLOX_USER_ID (ou ROBLOX_GROUP_ID) do ambiente."""
import json, os, sys, time, pathlib
import requests

API = "https://apis.roblox.com/assets/v1"
API_KEY = os.environ["ROBLOX_API_KEY"]
CREATOR = ({"groupId": os.environ["ROBLOX_GROUP_ID"]} if os.environ.get("ROBLOX_GROUP_ID")
           else {"userId": os.environ["ROBLOX_USER_ID"]})
HEADERS = {"x-api-key": API_KEY}

def _poll(op_id: str, max_wait: float = 180.0) -> dict:
    delay, waited = 1.0, 0.0
    while waited < max_wait:
        r = requests.get(f"{API}/operations/{op_id}", headers=HEADERS, timeout=30)
        if r.status_code == 429:                      # 300 req/min nesta rota
            time.sleep(delay); waited += delay; delay = min(delay * 2, 15); continue
        r.raise_for_status()
        op = r.json()
        if op.get("done"):                            # 'done' pode vir ausente enquanto em progresso
            if "error" in op:
                raise RuntimeError(op["error"])
            return op["response"]
        time.sleep(delay); waited += delay; delay = min(delay * 2, 15)
    raise TimeoutError(op_id)

def upload_png(path: pathlib.Path, name: str, description: str = "pixel art sprite") -> int:
    req = {
        "assetType": "Image",                         # NÃO "Decal": ID de Decal não serve em ImageLabel via script
        "displayName": name,
        "description": description,                   # obrigatório; máx. 1000 caracteres
        "creationContext": {"creator": CREATOR},
    }
    with path.open("rb") as fh:
        r = requests.post(
            f"{API}/assets",
            headers=HEADERS,
            files={
                "request": (None, json.dumps(req), "application/json"),
                "fileContent": (path.name, fh, "image/png"),
            },
            timeout=120,
        )
    if r.status_code == 429:                          # 120 req/min nesta rota
        raise RuntimeError("rate limited; aguarde e tente de novo")
    r.raise_for_status()
    op = r.json()
    asset = op["response"] if op.get("done") else _poll(op["path"].split("/")[-1])
    state = asset.get("moderationResult", {}).get("moderationState")
    print(f"{path.name}: assetId={asset['assetId']} moderation={state}", file=sys.stderr)
    return int(asset["assetId"])

if __name__ == "__main__":
    for p in map(pathlib.Path, sys.argv[1:]):
        print(json.dumps({"file": p.name, "assetId": upload_png(p, p.stem)}))
```

[NAO CONFIRMADO] O formato exato de `assetType` na resposta para Image (provavelmente `ASSET_TYPE_IMAGE`) e a ausência ou presença de `done` não estão confirmados.

---

## 6. Roblox Studio MCP

### 6.1 MCP embutido no Studio (caminho recomendado)

- [OK] **Status:**
  - O README do `Roblox/studio-rust-mcp-server` diz: "**This MCP Server is no longer being actively developed.** We've shifted ongoing engineering investment to the built-in MCP Server included with Roblox Studio". O último commit é de 2026-04-03 (https://github.com/Roblox/studio-rust-mcp-server).
  - O anúncio de 5/mar/2026 diz "the recommended way to connect external AI tools to Studio" (https://devforum.roblox.com/t/assistant-updates-studio-built-in-mcp-server-and-playtest-automation/4474643).
- [OK] **Instalação e conexão** (https://create.roblox.com/docs/studio/mcp):
  - No Studio: Assistant ⟩ **…** ⟩ **Manage MCP Servers** ⟩ **Enable Studio as MCP server**.
  - **Quick connect** para Antigravity, Codex CLI, **Claude Code**, **Claude Desktop**, Cursor, Gemini CLI e VS Code.
  - Transporte: **stdio**, com processo local.
  - JSON no macOS: `{"mcpServers":{"Roblox_Studio":{"command":"/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"}}}`.
  - JSON no Windows: `{"command":"cmd.exe","args":["/c","%LOCALAPPDATA%\\Roblox\\mcp.bat"]}`.
  - Uma luz verde no Studio indica cliente conectado.
  - [DICA] No Claude Code: `claude mcp add Roblox_Studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` no macOS, ou `-- cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat` no Windows. É derivado do "CLI command" da doc.
- [OK] **Ferramentas documentadas** (26) + `open_cloud_invoke`:

  | Grupo | Ferramenta e descrição oficial resumida |
  |---|---|
  | Scripts | `script_read` (caminho em dot-notation, faixa de linhas), `multi_edit` (várias edições, cria o script se não existir; `datamodel_type` Edit), `script_search` (fuzzy, até 10), `script_grep` (até 50) |
  | Assets/geração | `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `search_asset` (Creator Store e inventário), `insert_asset` (por ID: models, meshes, **images**, audio, video, animations, packages), **`upload_image`** ("Uploads a batch of images **from HTTP URLs**… returning an image path to asset ID map"), **`store_image`** (lê arquivo local e devolve URI para outras tools) |
  | Exploração | `subagent` (`explore`, `playtest`), `search_game_tree`, `inspect_instance` (todas as propriedades legíveis e atributos) |
  | Luau | **`execute_luau`**, que "Requires specifying a `datamodel_type` (Edit, Client, or Server)" |
  | Playtest | `get_studio_state`, `start_stop_play`, `get_console_output`, **`screen_capture`** (viewport; câmera opcional) |
  | Input | `character_navigation`, `user_keyboard_input`, `user_mouse_input` |
  | Docs/skills | `http_get` (só URLs de docs Roblox permitidas), `skill` |
  | Sessão | `list_roblox_studios`. "Every tool call takes a `studio_id` parameter" |
  | Open Cloud | `open_cloud_invoke(method, endpoint, body, scopes, files)` (https://create.roblox.com/docs/studio/mcp-open-cloud) |

- [OK] **Histórico:**
  - 19/mar/2026: chegaram `generate_mesh`, `generate_material` e `screen_capture` (https://devforum.roblox.com/t/assistant-updates-mesh-generation-new-mcp-server-tools-screenshot-tool-and-more/4527258).
  - 19/ago/2026: `set_active_studio` foi **removido**; `studio_id` passou a ser obrigatório. "tools targeting the Edit datamodel fail during a playtest" (https://devforum.roblox.com/t/studio-mcp-multi-agent-improvements-and-connected-ai-clients/4820583).
- [OK] **Open Cloud via MCP** (anúncio de 4/nov/2026, atualizado em 5/nov/2026: https://devforum.roblox.com/t/studio-mcp-server-updates-open-cloud-access-in-your-mcp-client-and-asset-import-workflows/4975849; doc https://create.roblox.com/docs/studio/mcp-open-cloud):
  - Sem API key: o Studio injeta o token.
  - Permissões **por jogo e por pessoa** (níveis Safe, Balanced (o default), Full access e Custom). Exige place **publicado**.
  - "Publish & manage assets" corresponde a `asset:*`.
  - Uploads só a partir de **pastas aprovadas** ("The client can't copy or move files into an approved folder").
  - Uploads são permanentes e pertencem ao dono do jogo; "Open Cloud can't archive or delete them".
  - Alguns endpoints rejeitam o token do Studio (HTTP 401/403).
  - `execute_luau` com HttpService exige a permissão "Connect to the internet" (capability `Network`) e allowlist de domínios. "**Other capabilities can't be granted**".
  - DataStores via `execute_luau` exigem o escopo e "Enable Studio Access to API Services". Isso usa **dados vivos**.
  - Skills novas: `rbx-open-cloud-usage`, `rbx-permissions`, `rbx-import-asset`.
- [OK]/[NAO CONFIRMADO] **Respostas às dúvidas de limitação:**
  - **Faz upload de imagens?** Sim, por `upload_image` (só de URLs HTTP) ou `open_cloud_invoke` com `files` de pasta aprovada. [NAO CONFIRMADO] Não confirmado se `upload_image` gera Image ou Decal (a descrição diz "image path to asset ID map", o que sugere Image).
  - **Seta propriedades?** Não há ferramenta dedicada no built-in (`multi_edit` é só para scripts). Faça via `execute_luau` com `datamodel_type = "Edit"`.
  - **Segurança do `execute_luau`:** [NAO CONFIRMADO] o nível de identidade e permissões não está documentado. O fato de haver capabilities "que não podem ser concedidas" sugere sandbox. Portanto [NAO CONFIRMADO] não está confirmado que APIs de plugin como `AssetService:CreateAssetAsync` (capability `AssetCreateUpdate`, https://create.roblox.com/docs/scripting/capabilities) funcionem por ele.
  - **Screenshots:** usuários relataram que `screen_capture` pode passar do limite de 1 MB de resultado de tool do Claude, e um comentário disse que JPEG estava sendo implantado (thread de 19/mar/2026, relato de usuários).
- [DICA] **Implicação:** o servidor MCP é local (stdio, ao lado do Studio em Windows/macOS). Um agente rodando num container Linux remoto não o alcança sem ponte. Planeje o pipeline para que geração e upload (Python + Open Cloud) rodem em qualquer lugar e só a etapa de montagem e verificação no Studio use MCP.

### 6.2 Servidor legado `Roblox/studio-rust-mcp-server` (referência)

- [OK] **Ferramentas** (README e `src/rbx_studio_server.rs`):
  - `run_code`: "Runs a command in Roblox Studio and returns the printed output".
  - `insert_model`: busca no Creator Store via `InsertService:GetFreeModels` e insere.
  - `get_console_output`.
  - `start_stop_play`: `start_play`, `stop` ou `run_server`.
  - `run_script_in_play_mode`: com timeout e parada automática.
  - `get_studio_mode`.
- [OK] **Arquitetura:**
  - Binário Rust (`rmcp` por stdio, mais um servidor HTTP `axum`) e um plugin que faz long-poll em `http://localhost:44755`.
  - `run_code` executa com **`loadstring` dentro do plugin**, ou seja, permissões de plugin, no DataModel de **Edit**: o plugin sai se `RunService:IsRunning()`.
  - Cada chamada é gravada via `ChangeHistoryService`, então é desfazível.
  - Não tem ferramenta de upload.
  - Fonte: `plugin/src/Main.server.luau`, `plugin/src/Tools/RunCode.luau` em https://github.com/Roblox/studio-rust-mcp-server
- [OK] **Configuração no Claude Code** (README): `claude mcp add --transport stdio Roblox_Studio -- '/Applications/RobloxStudioMCP.app/Contents/MacOS/rbx-studio-mcp' --stdio`.

### 6.3 Servidores da comunidade

- [OK] **`boshyxd/robloxstudio-mcp`:**
  - **Arquivado em 6/jun/2026**; recomenda o fork do Chrrxs.
  - Node/TS com plugin Luau por HTTP local. Exige "Allow HTTP Requests".
  - Instalação: `claude mcp add robloxstudio -- npx -y robloxstudio-mcp@latest`.
  - Ferramentas (fonte v2.7.x): `get_file_tree`, `search_files`, `get_place_info`, `get_services`, `search_objects`, `get_instance_properties`, `get_instance_children`, `search_by_property`, `get_class_info`, `get_project_structure`, `set_property`, `set_properties`, `mass_set_property`, `mass_get_property`, `create_object`, `mass_create_objects`, `delete_object`, `clone_object`, `smart_duplicate`, `mass_duplicate`, `get_script_source`, `set_script_source`, `edit_script_lines`, `insert_script_lines`, `delete_script_lines`, `grep_scripts`, `find_and_replace_in_scripts`, `get_attributes`, `set_attribute`, `bulk_set_attributes`, `delete_attribute`, `get_tags`, `add_tag`, `remove_tag`, `get_tagged`, `get_selection`, `execute_luau`, `start_playtest`, `stop_playtest`, `get_playtest_output`, `get_output_log`, `capture_screenshot`, `simulate_keyboard_input`, `simulate_mouse_input`, `character_navigation`, `undo`, `redo`, `search_assets`, `get_asset_details`, `get_asset_thumbnail`, `preview_asset`, `insert_asset`, `upload_asset`, builds/scenes e outros.
  - `upload_asset` aceita Audio, **Decal**, Model, Animation e Video, com `ROBLOX_OPEN_CLOUD_API_KEY` ou cookie para Decal.
  - Fonte: https://github.com/boshyxd/robloxstudio-mcp
- [OK] **`Chrrxs/robloxstudio-mcp`** (fork ativo; commits em 2/nov/2026; npm `@chrrxs/robloxstudio-mcp`):
  - `execute_luau` (Edit), `eval_server_runtime`/`eval_client_runtime`, `solo_playtest`/`multiplayer_playtest`, `breakpoints`, `get_runtime_logs`, `capture_screenshot`, `capture_micro_profiler`/`capture_script_profiler`, `get_memory_breakdown`, `get_scene_analysis`, `set_properties`, `find_and_replace_in_scripts`, `selection`, `search_assets`/`preview_asset`/`insert_asset`, `upload_asset` (Audio/**Decal**/Model/Animation/Video), `manage_monetization`, `manage_experience`, `get_roblox_docs`, `get_roblox_skills` e outros.
  - Fonte: https://github.com/Chrrxs/robloxstudio-mcp
  - [CONFLITO] Os dois sobem imagens como **Decal**, então os IDs não servem direto em `ImageLabel` via script.

---

## 7. Fusion 0.3

### 7.1 Versão e estado

- [OK] O último release é **0.3.0** (tag `v0.3-beta`, 2024-08-30; `version = {major = 0, minor = 3, isRelease = true}`).
- [OK] O `main` está em `0.4.0-dev1` (`isRelease = false`). O último commit é de 2026-02-01, e inclui coisas **que não existem na 0.3**, como `scope:insert()` e cleanup chamando `:disconnect()`/`:Disconnect()` de objetos genéricos.
- Fontes: https://github.com/dphfox/Fusion (tags e `src/init.luau`); docs https://elttob.uk/Fusion/0.3/

### 7.2 Assinaturas (0.3)

Fonte: `src/Types.luau` da tag e https://elttob.uk/Fusion/0.3/api-reference/

| API | Assinatura / comportamento |
|---|---|
| `Fusion.scoped(...methods)` | `-> Scope<merge(Methods)>`; métodos passados viram `__index` (https://elttob.uk/Fusion/0.3/api-reference/memory/members/scoped/) |
| `scope:innerScope(...methods)` | escopo interno: vive até `doCleanup` nele **ou** até o escopo pai ser limpo |
| `scope:deriveScope(...methods)` | mesmos métodos, **ciclo de vida independente** |
| `Fusion.doCleanup(task)` | `Instance` → `:Destroy()`; `RBXScriptConnection` → `:Disconnect()`; função → chamada; tabela com `destroy`/`Destroy` → chamado; array → limpa itens **do último para o primeiro**; depois o escopo é "envenenado" (não reutilize). "Scopes are not unique" (são reciclados) |
| `scope:Value(initial)` | `Value<T>`; `:set(newValue, force?)` |
| `scope:Computed(function(use, scope) ... end)` | o 2º argumento é um escopo **limpo automaticamente quando o computed recalcula** (https://elttob.uk/Fusion/0.3/api-reference/state/members/computed/, https://elttob.uk/Fusion/0.3/tutorials/fundamentals/computeds/) |
| `scope:ForValues(tbl, function(use, scope, value) -> VO)` | `For<K, VO>` |
| `scope:ForPairs(tbl, function(use, scope, key, value) -> (KO, VO))` | `For<KO, VO>` |
| `scope:ForKeys(tbl, function(use, scope, key) -> KO)` | `For<KO, V>` |
| `scope:Spring(goal, speed?, damping?)` | defaults `speed = 10`, `damping = 1` (crítico); métodos `:setPosition`, `:setVelocity`, `:addVelocity`; animáveis: number, CFrame, Color3, UDim, UDim2, Vector2, Vector3, Rect etc. |
| `scope:Tween(goal, tweenInfo?)` | `Tween<T>` |
| `scope:Observer(watching)` | `:onChange(cb)` e `:onBind(cb)` (roda já e a cada mudança), ambos retornam função de desconexão (https://elttob.uk/Fusion/0.3/tutorials/fundamentals/observers/) |
| `Fusion.peek(x)` | lê `UsedAs<T>` fora de contexto reativo |
| `scope:New "Class" { props }` | código: `New(scope, className) -> (PropertyTable) -> Instance` (a página da API omite `scope`). Aplica defaults "sensatos": Frame, ImageLabel e outros com `BackgroundColor3` branco e `BorderSizePixel = 0`; `ScreenGui` com `ResetOnSpawn = false` e `ZIndexBehavior = Sibling`; `TextButton`/`ImageButton` com `AutoButtonColor = false` (`src/Instances/defaultProps.luau`). `Parent` é aplicado por último |
| `scope:Hydrate(instance) { props }` | `Hydrate(scope, target) -> (PropertyTable) -> Instance` |
| Chaves especiais | `[Children]`, `[OnEvent "Activated"] = fn`, `[OnChange "Text"] = fn(new)`, `[Out "AbsoluteSize"] = valueObj`, `[Attribute "X"] = v`, `[AttributeChange "X"] = fn`, `[AttributeOut "X"] = valueObj`; `Child {…}` para listas mistas tipadas |
| `Fusion.Contextual(default)` | `:now()`, `:is(v):during(fn, ...)` |
| `Fusion.Safe { try = fn, fallback = fn(err) }` | `Success \| Fail` |
| Tipos | `UsedAs<T> = StateObject<T> \| T`; `Use = <T>(UsedAs<T>) -> T`; `Value<T, S = T>`; `Computed<T>`; `Spring<T>`; `Scope<Constructors = any> = {Task} & Constructors` |

- [CONFLITO] A página `Scope` diz que o default é `typeof(Fusion)`, mas **o código-fonte usa `any`**. Anote `Fusion.Scope<typeof(Fusion)>` para ter checagem real.
- [OK] **Agendador:** no cliente, `RunService:BindToRenderStep("FusionUpdateStep_<GUID>", Enum.RenderPriority.First.Value, ...)`; no servidor, `Heartbeat` (`src/RobloxExternal.luau`).
- [OK] **Dicas de strict:**
  - "Remember… `UsedAs<Vector3>?` (propriedade opcional) vs `UsedAs<Vector3?>` (aceita nil)" (https://elttob.uk/Fusion/0.3/tutorials/best-practices/components/).
  - Mistura de tipos em `[Children]` pode dar falso erro; use `Child {…}` (https://elttob.uk/Fusion/0.3/tutorials/roblox/parenting/).
  - Repetir o nome `scope` no callback é intencional; use `--!nolint LocalShadow`.

### 7.3 Snippets mínimos (Fusion 0.3, `--!strict`)

**a) Componente `(scope, props)` com `UsedAs`:**
```lua
--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Fusion = require(ReplicatedStorage.Packages.Fusion)

type UsedAs<T> = Fusion.UsedAs<T>
type Scope = Fusion.Scope<typeof(Fusion)>
local OnEvent = Fusion.OnEvent

export type PixelButtonProps = {
	Image: UsedAs<string>,
	RectOffset: UsedAs<Vector2>?,
	Position: UsedAs<UDim2>?,
	OnClick: (() -> ())?,
}

local function PixelButton(scope: Scope, props: PixelButtonProps): ImageButton
	return scope:New "ImageButton" {
		BackgroundTransparency = 1,
		Image = props.Image,
		ImageRectOffset = props.RectOffset,
		ImageRectSize = Vector2.new(16, 16),
		ResampleMode = Enum.ResamplerMode.Pixelated,
		Size = UDim2.fromOffset(64, 64), -- escala inteira 4x
		Position = props.Position,
		[OnEvent "Activated"] = function()
			if props.OnClick then props.OnClick() end
		end,
	} :: ImageButton -- New retorna Instance
end

return PixelButton
```

**b) `Computed` que cria instâncias no escopo interno** (a instância anterior é destruída a cada recálculo):
```lua
--!strict
--!nolint LocalShadow
local scope = Fusion.scoped(Fusion)
local Children = Fusion.Children
local frameIndex = scope:Value(0)

local sprite = scope:Computed(function(use, scope): Instance
	local i = use(frameIndex)
	return scope:New "ImageLabel" { -- criado no escopo INTERNO
		BackgroundTransparency = 1,
		Image = "rbxassetid://0000000", -- placeholder
		ImageRectOffset = Vector2.new(i * 16, 0),
		ImageRectSize = Vector2.new(16, 16),
		ResampleMode = Enum.ResamplerMode.Pixelated,
		Size = UDim2.fromOffset(48, 48),
	}
end)

scope:New "Frame" { [Children] = sprite }
```
[DICA] Para animação de sprite, **prefira** um único `ImageLabel` com `ImageRectOffset = scope:Computed(...)`. Recriar a instância a cada frame é caro. O padrão acima serve para conteúdo que muda de estrutura.

**c) Posição dirigida por `Spring`:**
```lua
local isOpen = scope:Value(false)
local target = scope:Computed(function(use, _)
	return if use(isOpen) then UDim2.fromScale(0.5, 0.5) else UDim2.fromScale(0.5, 1.5)
end)
local animated = scope:Spring(target, 25, 0.8) -- speed, damping

scope:New "Frame" {
	AnchorPoint = Vector2.new(0.5, 0.5),
	Position = animated,
}
isOpen:set(true)
```
[DICA] Para manter os pixels "presos" à grade, derive com `Computed` e arredonde os offsets. Só funciona com posição em Offset; Scale gera frações.

**d) Limpar conexão de `RunService` com o escopo:**
```lua
local RunService = game:GetService("RunService")
local peek = Fusion.peek
local frame = scope:Value(0)
local acc = 0

table.insert(scope, RunService.PreRender:Connect(function(dt: number)
	acc += dt
	if acc >= 1 / 12 then -- 12 fps
		acc -= 1 / 12
		frame:set((peek(frame) + 1) % 8)
	end
end))

-- mais tarde: desconecta (RBXScriptConnection -> :Disconnect()) e destrói tudo do escopo
Fusion.doCleanup(scope)
```
Num componente, crie `local scope = outerScope:innerScope()` e insira a conexão nele. Dentro de um `Computed`, insira no escopo do callback para desconectar a cada recálculo. Na 0.3, `scope:insert()` **não existe**; ele é 0.4-dev.

---

## 8. Luau

### 8.1 `utf8.graphemes`

- [OK] `utf8.graphemes(str, i?, j?)` retorna um iterador `for first, last in utf8.graphemes(str) do local g = str:sub(first, last) end`, com as **posições de byte** de cada cluster.
  - `i`/`j` aceitam negativos, contando do fim.
  - Também existem `utf8.nfcnormalize` e `utf8.nfdnormalize`.
  - Fonte: https://create.roblox.com/docs/reference/engine/libraries/utf8. O exemplo da doc usa `s:sub` com variável `str`, um erro de digitação.
- [OK] **É extensão do Roblox:** o Luau padrão só tem `offset`, `codepoint`, `char`, `len`, `codes` e `charpattern` (https://luau.org/library). Não funciona em runtimes Luau fora do Roblox.
- [OK] `utf8.len` conta **codepoints**, não grafemas.
- [OK] Para efeito typewriter, use `TextLabel.MaxVisibleGraphemes` (`-1` sem limite; o layout é calculado como se tudo estivesse visível).
  - A doc oficial combina com `utf8.graphemes` e **remove tags RichText** antes de animar.
  - Fontes: https://create.roblox.com/docs/reference/engine/classes/TextLabel, https://create.roblox.com/docs/ui/animation

### 8.2 `--!strict` e uniões de strings literais (singletons)

- [OK] **Singletons de string e boolean:** `local foo: "Foo" = "Foo"` é ok; `local bar: "Bar" = foo` não; `string = foo` é ok. Números como tipo literal não são suportados.
  - Fonte: https://luau.org/types/basic-types/; RFC https://github.com/luau-lang/rfcs/blob/master/docs/syntax-singleton-types.md
- [OK] **Comportamento testado** (`tests/TypeInfer.singletons.test.cpp`, https://github.com/luau-lang/luau/blob/master/tests/TypeInfer.singletons.test.cpp):
  - Literal de tabela **com tipo esperado** (anotação) infere singletons e tagged unions sem erro: `local b: Animal = { tag = "Cat", meows = true }`.
  - Anotações de dicionário `{[string]: "a" | "b"}` funcionam.
  - **No solver antigo** há *widening*: `local foo: "foo" = "foo"; local copy = foo` dá `copy: string`. No novo, dá `"foo"`.
  - Passar singleton por função identidade genérica (`id("hello")` retornando `"hello"`) **falha no solver antigo** e passa no novo.
- [CONFLITO]/[NAO CONFIRMADO] Que `local t = { kind = "SPIKES" }` sem anotação vire `{kind: string}` e quebre ao passar para `{kind: Kind}` é comportamento amplamente relatado no solver antigo. [NAO CONFIRMADO] Não verifiquei empiricamente (rodar `luau-analyze` foi bloqueado aqui). O comportamento exato no solver novo também não foi confirmado; o anúncio só diz que "singleton handling" melhorou.
- [DICA] **Padrão portátil**, que funciona nos dois solvers:
```lua
--!strict
export type TileKind = "EMPTY" | "WALL" | "SPIKES"
export type Tile = { kind: TileKind, x: number, y: number }

local t: Tile = { kind = "SPIKES", x = 1, y = 2 }      -- anote no ponto de criação
local level: { Tile } = {
	{ kind = "WALL", x = 0, y = 0 },
	{ kind = "SPIKES", x = 1, y = 0 },
}
local k = "SPIKES" :: TileKind                           -- cast explícito quando não há anotação
-- Fusion: o valor genérico não herda o tipo esperado no solver antigo → faça o cast do argumento
-- local kindState = scope:Value("EMPTY" :: TileKind)

-- "enum" congelado mantendo singletons
local Kind = table.freeze({
	EMPTY = "EMPTY" :: "EMPTY",
	WALL = "WALL" :: "WALL",
	SPIKES = "SPIKES" :: "SPIKES",
})
```

### 8.3 `Color3.fromHex`

- [OK] Existe e está documentado. Aceita 6 ou 3 caracteres hexadecimais, sem diferenciar maiúsculas, com `#` opcional (por exemplo `Color3.fromHex("#FA0")`). Não há canal alfa.
- [OK] `Color3:ToHex()` retorna `RRGGBB` minúsculo e sem `#`.
- Também existem `GetLuminance`, `GetContrastRatio` e `GetContrastingColor`.
- Fonte: https://create.roblox.com/docs/reference/engine/datatypes/Color3

### 8.4 `table.freeze`

- [OK] Congela no lugar e de forma **rasa**. Erro se a tabela já estiver congelada ou tiver metatable protegida. Tentativas de modificar, ou de trocar a metatable, levantam erro em runtime.
  - Fontes: https://luau.org/library, https://create.roblox.com/docs/reference/engine/libraries/table
- [OK] **Tipagem:**
  - No **solver antigo**, `table.freeze` é uma identidade sobre tabela, sem propriedades read-only no tipo. A escrita só falha em runtime.
  - No **solver novo**, a função mágica `MagicFreeze` devolve uma cópia do tipo **selada e com todas as propriedades read-only**: "accepts any subtype of `table` and returns a read-only version of that table".
  - Fonte: `Analysis/src/BuiltinDefinitions.cpp` em https://github.com/luau-lang/luau/blob/master/Analysis/src/BuiltinDefinitions.cpp
  - [DICA] Anote antes de congelar, por exemplo `local DATA: {Tile} = {...}; table.freeze(DATA)`, para não depender de inferência através da chamada genérica no solver antigo.

### 8.5 Estado do type solver

- [OK] **GA em 20/nov/2025:**
  - Scripts `nocheck` e `nonstrict` foram movidos para o novo solver.
  - **Projetos com scripts strict ficam no solver antigo por padrão**. Para usar o novo, `Workspace.UseNewLuauTypeSolver = Enabled` (RolloutState).
  - `Workspace.LuauTypeCheckMode` define o modo padrão.
  - O beta do Studio foi removido em 7/jan/2026.
  - O solver antigo é mantido "through 2026".
  - Fontes: https://devforum.roblox.com/t/general-release-luau%E2%80%99s-new-type-solver/4084991, https://create.roblox.com/docs/reference/engine/classes/Workspace
  - [NAO CONFIRMADO] Não está confirmado se o default de strict mudou depois.

---

## 9. Lista consolidada de itens [NAO CONFIRMADO] não confirmados / [CONFLITO] conflitantes

1. `SurfaceAppearance.ResampleMode` funcionando de fato em nov/2026: era "Pending" em ago/2026.
2. Resolução máxima efetiva de imagens de **GUI** em 2026: 1024 é o limite prático segundo a comunidade, não documentado.
3. `ResampleMode` em `BillboardGui`: deve funcionar por ser propriedade do ImageLabel, mas não há confirmação específica.
4. `SliceCenter` relativo a `ImageRectOffset` (relato da comunidade).
5. Requisito de textura de flipbook: a doc tem textos conflitantes (1024×1024, "multiple of layout" e não quadrado no beta de 2025). O GA do layout Custom não foi confirmado.
6. Requisito atual de ID verification para EditableImage: o anúncio de 2024 e o post de mai/2026 indicam que continua; a doc não menciona.
7. Command bar criando EditableImage sem orçamento: inferido do comportamento de plugins.
8. Nível de segurança e capabilities do `execute_luau` no MCP embutido. Se `upload_image` gera Image ou Decal.
9. Bulk import do Asset Manager: se gera Image ou Decal.
10. Formato `assetType` na resposta da Operation para Image; ausência de `done`.
11. Inferência de literal sem anotação no **solver novo** em tabelas; verificação empírica com `luau-analyze` não realizada.
12. Números oficiais de custo de tweens, de pooling e de limites de GuiObjects animados no mobile: **não existem**.
