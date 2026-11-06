# 05 — Integração com Roblox (fatos verificados em nov/2026)

Dossiê com URLs: `docs/pixel-art/pesquisa/03-roblox-tecnico-fusion-mcp.md`. Jogos e padrões: `docs/pixel-art/pesquisa/01-jogos-roblox-pixel-art.md`.

## 1. Nitidez
- `ResampleMode = Enum.ResamplerMode.Pixelated` (nearest) funciona **só** em `ImageLabel`/`ImageButton`, em qualquer container (ScreenGui, SurfaceGui, BillboardGui).
- **Decal, Texture, MaterialVariant, ParticleEmitter, Beam e Trail não têm filtro configurável:** são bilinear com mipmap e streaming.
- `SurfaceAppearance.ResampleMode` está na API desde abr/2026, mas ainda aparecia como "Pending" em ago/2026.
- Contorno para 3D/partículas: **upscale inteiro com nearest antes do upload** (16→256, 32→512) ou `SurfaceGui` + `ImageLabel` Pixelated em superfícies planas.
- Reduzir uma imagem Pixelated gera shimmering. Exiba sempre ≥ 1× nativo.

## 2. Tamanho, compressão, transparência
- **GUI: trate 1024×1024 como limite** (o limite de 4K anunciado em jan/2026 vale só para texturas 3D com streaming). Atlas maiores vão em páginas.
- Recomendação oficial de memória: a maioria das imagens ≤ 256², no máximo 512². Uma de 1024² consome 4× uma de 512².
- **Mobile comprime UI com perdas** (staff, jul/2025: "unavoidable", sem correção planejada). Pixel art nativa perde cor.
  - Mitigação: upscale ×4, com cada pixel = 1 bloco 4×4 de compressão (`export_gui_sheet(upscale=4)`).
  - Teste em aparelho real.
- **O upload troca o RGB dos pixels transparentes por preto** e a filtragem cria franja escura. Todo export do PixelForge aplica `alpha_bleed`.
- Sprite sheet: padding de 1–2 px. As dimensões devem ser **exatas** (uma folha de 799 px em vez de 800 causou tremor). Alinhar a múltiplos de 4 ajuda a compressão.
- Moderação: horas. Recusada = nunca carrega. Já houve recusa por engano de pixel art simples.

## 3. Upload (Open Cloud)
- `POST https://apis.roblox.com/assets/v1/assets` multipart (`request` JSON + `fileContent`), header `x-api-key`, escopos `asset:read` + `asset:write`.
- Faça polling em `GET /assets/v1/operations/{id}` e leia `response.assetId`.
- **`assetType: "Image"`**. O ID de **Decal não funciona** em `ImageLabel.Image` via script.
- Limites: 120 creates/min e 300 polls/min, arquivo de até 20 MB. A chave expira após 60 dias sem uso.
- `pixelforge.roblox.upload_image()` lê `ROBLOX_API_KEY` e `ROBLOX_USER_ID`/`ROBLOX_GROUP_ID` do ambiente. **Nunca** cole a chave no chat ou no código.

## 4. ParticleEmitter flipbook
- `FlipbookLayout` aceita `Grid2x2` (4), `Grid4x4` (16), `Grid8x8` (64) e `Custom` (`FlipbookSizeX/Y` 1–64, textura não quadrada; Client Beta desde out/2025).
- Modos:
  - `Loop`;
  - `OneShot` (**ignora o framerate**: velocidade = Lifetime/frames);
  - `PingPong`;
  - `Random`.
- **Máximo 30 fps.**
- **`FlipbookBlendFrames` (mar/2026) vem `true` e faz crossfade:** use `false` em pixel art.
- Deixe espaço entre os frames (mipmap). Clientes com pouca memória **desligam** flipbooks: tenha um fallback estático.
- Partículas **não aparecem em ViewportFrame** e não servem para VFX dentro de ScreenGui. Para isso use sprite sheet no `ImageLabel` (`SpriteAnimator`).

## 5. EditableImage
- Criação: `AssetService:CreateEditableImage({ Size = Vector2.new(w, h) })`. Máximo 1024², padrão 512². Retorna `nil` sem orçamento de memória.
- `WritePixelsBuffer` recebe RGBA em 4 bytes por pixel.
- Exibição: `label.ImageContent = Content.fromObject(img)`.
- Só **1 EditableImage exibida atualiza por quadro**. **Não replica**: para levar do servidor ao cliente, use `CreateDataModelContentAsync`.
- Exige "Allow Mesh / Image APIs" e dono 13+ com ID verificado.
- **Usos bons:** prévia no Studio (`pixelforge preview-luau`), palette swap, dissolve, minimapa. Para animação em massa, use sprite sheet.

## 6. Performance de GUI
- Use **um relógio** (`PixelClock`). `RunService.PreRender` é o substituto oficial do `RenderStepped`; mantenha o callback leve.
- **UIGradient** (upgrade de 29/out/2026):
  - interpola em espaço linear;
  - no máximo ~6 paradas de cor e ~1000 gradientes;
  - anime **`Offset`/`Rotation`**, não `Color`/`Transparency`.
- **CanvasGroup:** precisa de `ZIndexBehavior = Sibling`. Gasta memória e, sob pressão, reduz a resolução ou fica em branco. Evite em pixel art.
- **UIStroke:** `Thickness` inteiro (FixedSize) escala com o `UIScale`, mas `BorderOffset` não.
- Faça pooling de instâncias (nada de `Instance.new` por quadro) e reaproveite o mesmo atlas para batching.
- Meça no MicroProfiler (`Perform/Scene/UI`) no aparelho alvo. Não há números oficiais de limite.
- Escala de UI: inteira sobre `AbsoluteSize` em pontos lógicos. Em aparelhos de DPI 2×/3×, k = 1 já é nítido.

## 7. Padrão "Brick Bronze" de sprite sheet (provado em produção)
- **Uma tabela de dados por animação:** ids das folhas, nº de frames, tamanho, frames por linha e borda de 1 px.
- Linhas cabem em 1024. Animações longas são divididas em várias folhas.
- O frame é escolhido pelo **tempo decorrido** (não por contador), num **loop único compartilhado**.
- A **próxima folha é pré-carregada** num ImageLabel escondido. `PreloadAsync` não basta: a imagem precisa aparecer uma vez.
- Variantes (shiny/costas) são folhas separadas, não palette swap em runtime.
- O `SpriteAnimator` + módulo `*_Sprite.luau` do PixelForge seguem esse padrão.

## 8. Fusion 0.3 (UI declarativa)
- A última versão é **0.3.0**; `main` é 0.4-dev.
- Anote `Fusion.Scope<typeof(Fusion)>`: o padrão do código-fonte é `any` e desliga a checagem.
- `scope:New "Classe" {...}` devolve `Instance`: faça cast (`:: ImageLabel`).
- `scope:Computed(function(use, scope) ... end)`: o 2º argumento é um escopo interno, limpo a cada recálculo. Instâncias criadas ali morrem junto.
- Limpeza: `table.insert(scope, conexaoOuFuncao)` e depois `Fusion.doCleanup(scope)`. **`scope:insert` não existe na 0.3.**
- Para sprite animado, prefira **uma** `ImageLabel` com `ImageRectOffset` dirigido por estado ou por callback do relógio. Não recrie a instância.

## 9. Luau
- Para tagged unions em `--!strict`, **anote no ponto de criação** (`local x: Tipo = {...}`) ou use cast (`"A" :: Kind`). Scripts strict seguem no solver antigo, a menos que `Workspace.UseNewLuauTypeSolver` esteja ligado.
- `Color3.fromHex("#RRGGBB")` existe, assim como `Color3:GetContrastRatio`.
- `utf8.graphemes(s)` só existe no Roblox e devolve faixas de bytes `(first, last)`.
- `table.freeze` é raso.

## 10. Roblox Studio MCP
- **Embutido no Studio** (o recomendado; o `studio-rust-mcp-server` foi descontinuado):
  - Ativação: Assistant > ... > Manage MCP Servers > *Enable Studio as MCP server*. Tem quick connect para Claude Code.
  - O processo é **local** (stdio, Windows/macOS).
- Ferramentas úteis (toda chamada leva `studio_id`):
  - `execute_luau` (datamodel_type `Edit`/`Client`/`Server`);
  - `upload_image` (só **URLs HTTP**);
  - `store_image`;
  - `insert_asset`;
  - `inspect_instance`, `search_game_tree`;
  - `screen_capture`, `get_console_output`, `start_stop_play`;
  - `open_cloud_invoke` (nov/2026: permissões por jogo e uploads só de **pastas aprovadas**; place publicado).
- **Não há ferramenta de "setar propriedade"** no MCP embutido: use `execute_luau` em Edit.
- `screen_capture` pode estourar o limite de 1 MB do resultado; capture regiões menores.
- Servidores da comunidade (`robloxstudio-mcp` e fork do Chrrxs) têm `set_property`/`capture_screenshot`, mas sobem imagem como **Decal**.
