# Relatório — Motor de produção de pixel art (The Dark Altar)

Sessão de 06/11/2026. Branch `ccr-24eeea0e-bbc14z` do repositório `cringinho/roblox-ai`.
Escrito para que **outra sessão** consiga entender, reproduzir e continuar o trabalho sem esta conversa.

---

## 1. Resumo do que foi entregue

| # | Pedido | Entrega | Caminho |
|---|---|---|---|
| 1–3 | Estudar pixel art, VFX, UI, jogos Roblox e fontes | 3 dossiês com ~2.500 linhas e centenas de URLs | `docs/pixel-art/pesquisa/01..03-*.md` |
| 4 | Relatório + artefato de repertório | este arquivo + página "Grimório PixelForge" | `docs/pixel-art/RELATORIO.md` · https://claude.ai/artifact/VJvCqN1kBP1Ky7gYY8ttmT |
| 5 | Skill de pixel art para Roblox Studio MCP | skill `roblox-pixel-art` (SKILL.md + 6 referências + motor Python + runtime Luau) | `.claude/skills/roblox-pixel-art/` |
| 6a | Módulo de dados das 120 artes de subtipo | `--!strict`, 120 entradas, API e autoteste | `src/shared/Config/SubtypeArtCatalog120.luau` |
| 6b | Arte das 120 artes de subtipo | atlas 1024×512 + prévias por família | `art/dark-altar/subtypes/` + `src/shared/Config/SubtypeArtAtlas120.luau` |
| 6c | Spec da Forja +0..+5 (Fusion 0.3) | árvore de componentes, Tipo Dominante, níveis, performance, aceite | `docs/specs/CURRENT_SPEC.md` |
| 6d | Ornamentos da Forja em pixel art | atlas de 19 sprites + máscaras + mockup dos 6 níveis | `art/dark-altar/forge/` + `src/shared/Config/ForgeOrnamentAtlas.luau` |
| extra | VFX e transições | 11 VFX + 3 transições (GIF, folha de GUI, flipbook 1024, módulo Luau) | `art/dark-altar/vfx/` |
| extra | Cenário de referência | nave de catedral 320×180 | `art/dark-altar/scenes/` |
| extra | Runtime Luau | `PixelClock`, `SpriteAnimator`, `PixelScale`, `FlipbookVFX` | `src/shared/Pixel/` |
| 7 | Pontos de melhoria | seção 9 deste relatório | — |

---

## 2. O que a pesquisa mostrou (síntese)

### 2.1 Técnica (dossiê 02, 202 regras numeradas)
- **Escala inteira e nada de rotação** de arte pronta. A faixa de resolução de cena é 320×180 a 640×360.
- **Rampas profissionais**, medidas em Apollo, Endesga e Resurrect:
  - 4–6 passos;
  - o matiz gira 45–100° no total, para o amarelo ao clarear e para o azul-violeta ao escurecer;
  - saturação com pico no meio;
  - nunca preto puro;
  - ΔL ≥ 0,06 entre passos vizinhos.
- **Cena gótica:** 5 bandas de valor. O acento saturado (vitral, fogo, VFX) ocupa só 10–20% da área.
- **VFX (Saint11):**
  - Explosão em camadas: contrast frame escuro → flash → blast → fogo → fumaça **índigo**. O fogo some rápido e a fumaça devagar.
  - Fogo é fluxo, com uma onda nova a cada 2–3 frames.
  - Smear dura 1 frame.
  - Hit-stop proporcional ao dano, com tremor que decai.
- **UI:**
  - 9-slice com bordas tileáveis e detalhe nos cantos.
  - Botão pressionado desce 1 px e perde a sombra.
  - Raridade por cor **e** forma.
  - Editions do Balatro (foil/holo/polychrome) calculadas por texel e quantizadas de volta.
- **QA:** 19 detectores automáticos (órfão, banding, pillow, mixel, alpha parcial, contraste, flicker…). Parte deles virou o `pixelforge.lint`.

### 2.2 Roblox técnico (dossiê 03)
- **Só `ImageLabel`/`ImageButton` têm nearest** (`ResampleMode = Pixelated`). Decal, Texture, partícula e Beam são sempre filtrados, então faça upscale inteiro antes do upload.
- **Mobile comprime UI com perdas.** É confirmado pela Roblox, sem correção prevista. A mitigação é a variante ×4.
- O upload troca o RGB transparente por preto. Por isso o motor aplica **alpha bleed** em tudo.
- **Flipbook:**
  - `FlipbookBlendFrames` vem `true` desde mar/2026 e precisa ser desligado;
  - máximo 30 fps;
  - grade 2×2/4×4/8×8;
  - layout Custom em beta.
- **Upload Open Cloud com `assetType: "Image"`.** O ID de Decal não funciona em `ImageLabel` via script.
- **Studio MCP embutido** é o caminho oficial (o servidor em Rust foi descontinuado):
  - ferramentas: `execute_luau`, `upload_image` (só URL HTTP), `screen_capture`, `open_cloud_invoke` (nov/2026);
  - roda **localmente** com o Studio.
- **Fusion 0.3:**
  - anotar `Fusion.Scope<typeof(Fusion)>`;
  - `scope:New` precisa de cast;
  - `scope:insert` não existe (use `table.insert(scope, ...)`);
  - o Computed recebe `(use, scope)`.
- `RunService.PreRender` é o substituto oficial do `RenderStepped`.

### 2.3 Jogos Roblox com pixel art (dossiê 01): o resultado honesto
**Quase nenhum jogo famoso do Roblox usa pixel art de verdade em VFX e cenário:**
- Doodle World é desenhado à mão.
- Loomian Legacy e Pixel Blade são 3D.
- Não há card game em pixel art popular na plataforma.

Os 10 casos estudados:
- **4 populares confirmados:** Pokémon Brick Bronze, Pixel Quest!, The Powder Box e Starving Artists.
- **6 showcases do DevForum que documentam a técnica:** Campgrounds 2, um jogo de UI estilo Undertale, GLOOM, os tutoriais da violet_angxl, uma engine estilo Mario Maker e os devlogs da MischieRaven.

O padrão mais valioso é o do **Brick Bronze**:
- um módulo de dados por animação;
- folhas ≤ 1024 divididas;
- frame escolhido por tempo decorrido;
- **um loop único** compartilhado;
- pré-carregamento da folha seguinte.

O `SpriteAnimator` + `*_Sprite.luau` do motor seguem esse padrão.

**Conclusão estratégica:** o espaço de "card game gótico em pixel art" no Roblox está praticamente vazio. Se a arte for consistente, é um diferencial visual.

---

## 3. Diagnóstico das artes atuais (pelas capturas enviadas)

| Observação | Regra quebrada | Como o sistema novo resolve |
|---|---|---|
| Artes das cartas em estilos e densidades de pixel diferentes (cenoura lisa ao lado de cogumelos e sol pixelados) | Mixels / consistência (F-07, IC-01) | 120 artes de subtipo do mesmo gerador: mesma grade de 64 px, mesma luz e mesma linguagem de xilogravura |
| Assunto da arte nem sempre conversa com o nome ou a família da carta | Leitura em 1 s (IC-01) | A arte vem do **subtipo** (família de cor + emblema temático), não de um desenho avulso |
| Arte escurecida sob o texto disputa a leitura com o título e a regra | Hierarquia de valor (C-04, UI-10) | Arte em janela própria 64×64, texto fora dela (`CURRENT_SPEC` §3); fundos de subtipo com etching de baixo contraste |
| Bordas de raridade variando entre sólido e tracejado sem progressão clara | Raridade por cor **e** forma (UI-08, IC-08) | Forja +0..+5 com tokens fixos e ornamentos acumulativos (mockup em `art/dark-altar/forge/mock_forge_levels.png`) |
| Traço do ataque é uma linha fina e lisa entre os painéis | Linhas pixel-perfect, sem AA automático (F-15, F-19) | Use `slash_arc`/`impact_spark` em GUI (Pixelated) ou um raio por ponto médio em pixel (melhoria nº 3) |
| Impacto com pouco peso: sem contrast frame, sem hold, efeito pequeno perto do painel | Timing com peso (A-02, VFX-01, TR-04) | Geradores com contrast frame, flash segurado e dissipação lenta; tabela de timing na skill |
| Tingimento bege/marrom do painel no golpe | VFX legível sobre fundo escuro (VFX-36) | Flash branco de 1–3 frames + faísca de alto contraste; hit-stop proporcional ao dano |

Pontos fortes atuais que vale manter: painéis escuros com fonte pixel nítida, a lógica de tags `[ATQ]`/`[GRD]` e a paleta escura geral. O sistema novo foi desenhado em cima disso.

---

## 4. Arquitetura

```
  pipeline/dark_altar/subtypes.py  (FONTE DE VERDADE: 120 subtipos)
            |                                   \
            v                                    v
  build_subtypes.py --valida (120, emoji, contraste 5.5:1, glifos)
            |-- emite --> src/shared/Config/SubtypeArtCatalog120.luau  (modo PROCEDURAL / dados)
            |-- renderiza via PixelForge --> SubtypeArtAtlas120.png + SubtypeArtAtlas120.luau (modo ATLAS)
            '-- lint de cada arte (media 99,9)

  build_forge.py --> ForgeOrnamentAtlas.png (+ .luau), ShapeMaskAtlas.png, EtchingAtlas.png, mockup +0..+5

  .claude/skills/roblox-pixel-art/scripts/pixelforge  (MOTOR)
     color -> palette -> canvas/raster -> shade -> fx/ui/scene -> lint -> preview -> sheet -> roblox
                                                                      |
  Roblox:  upload (Image) -> IDs nos módulos -> src/shared/Pixel/* (PixelClock, SpriteAnimator,
           PixelScale, FlipbookVFX) -> CardView/CardForgeOrnaments (spec) -> conferir (MCP screen_capture)
```

**Por que um motor em código e não "gerar imagem":**
- toda decisão vira regra testável (rampa, luz, timing, contraste);
- o resultado é **determinístico** (a mesma entrada gera o mesmo PNG);
- o lint pega regressão;
- a arte e os dados Luau saem da **mesma fonte**, sem divergir.

---

## 5. Como reproduzir (passo a passo)

Requisitos: Python 3.10+ com `Pillow` e `numpy` (`pip install pillow numpy`). Nada mais.

```bash
git clone https://github.com/cringinho/roblox-ai && cd roblox-ai && git checkout ccr-24eeea0e-bbc14z

# 1. catálogo + atlas dos 120 subtipos (imprime ajustes de contraste, lint médio ~99,9)
python pipeline/dark_altar/build_subtypes.py
#    saídas: src/shared/Config/SubtypeArtCatalog120.luau, SubtypeArtAtlas120.luau,
#            art/dark-altar/subtypes/SubtypeArtAtlas120.png e preview_*.png

# 2. ornamentos da Forja + máscaras + mockup
python pipeline/dark_altar/build_forge.py

# 3. VFX, transições e cenário (a partir da pasta do motor)
cd .claude/skills/roblox-pixel-art/scripts
python -m pixelforge fx-all --out ../../../../art/dark-altar/vfx      # notas 90-100
python -m pixelforge scene cathedral --out ../../../../art/dark-altar/scenes/cathedral_320x180.png
python -m pixelforge palette --out ../assets/palettes/altar.png
```

Verificação esperada:
- `build_subtypes.py` imprime `OK: 120 subtipos validos em 12 familias` e o `.luau` sai **idêntico** ao commitado (o processo é determinístico; confira com `git diff --stat`).
- Varredura anti-emoji em `src/`: `0` (comando na §10 da spec).

### Plugar no Roblox Studio
1. **Rojo** (ou copie à mão): `src/shared/Config/*.luau` e `src/shared/Pixel/*.luau` vão para `ReplicatedStorage > Shared`.
2. **Upload como Image** dos PNGs:
   - `SubtypeArtAtlas120.png`;
   - `ForgeOrnamentAtlas.png`;
   - `ShapeMaskAtlas.png` e `EtchingAtlas.png`, se usar o modo procedural;
   - os `*_gui.png` dos VFX.

   Caminhos para o upload:
   - `python -m pixelforge upload ...`, com `ROBLOX_API_KEY` e `ROBLOX_USER_ID` no ambiente; ou
   - Asset Manager, copiando o **Image ID**; ou
   - `upload_image` do MCP com a URL raw do GitHub.
3. Troque `IMAGE = "rbxassetid://0"` pelos IDs em `SubtypeArtAtlas120.luau`, `ForgeOrnamentAtlas.luau` e nos `*_Sprite.luau`.
4. No Command Bar: `require(game.ReplicatedStorage.Shared.Config.SubtypeArtCatalog120).validate()` deve retornar `{}`.
5. Implemente `CardView`/`CardForgeOrnaments` seguindo `docs/specs/CURRENT_SPEC.md`. Ajuste **só** o adaptador `CardTokens` ao `DesignTokens`/`HudView` reais.
6. Confira em aparelho real (compressão mobile) e no MicroProfiler.

---

## 6. Detalhes das entregas

### 6.1 Catálogo das 120 artes de subtipo
- **Famílias e contagens** exatamente como pedido: 4 + 9 + 13 + 11 + 10 + 11 + 10 + 11 + 10 + 11 + 10 + 10 = **120**.
- **Cores:**
  - `bgHex` = cor-base da família + 10% do acento, o que dá identidade de família com variação por subtipo.
  - O gerador garante **contraste WCAG ≥ 5,5:1** entre acento e fundo.
  - **19 acentos foram clareados** em OKLCH (mesmo matiz e croma) para passar. Exemplos: Profundeza `#2F5BC4 → #5687F4`, Vinho `#C0384F → #E3596B`. A lista completa sai no console do gerador.
- **`etchingPattern` por semântica:**
  - WAVES: água, ar, areia, sangue;
  - RAYS: luz, sol, sagrado, energia;
  - ABYSS: vazio, profundeza, sombra;
  - ROOTS: natureza, terra, corrupção;
  - FRACTAL: cristal, espelho, ilusão;
  - SCALES: dragão, peixe, armadura;
  - SPIKES: perigo, espinho, demônio;
  - ARCHES: sagrado, tumba, ritual.
- **`centerSilhouettes`:** emblemas **concêntricos** de 1–5 formas (DIAMOND, PILLAR, RING, BLADE, CRESCENT, CROWN), com escala em fração da arte e rotação em graus horários, como `GuiObject.Rotation`. No atlas, as rotações são ajustadas a ângulos limpos.
- **`watermarkGlyph`:** monograma de 1–2 caracteres, únicos por família, todos com glifo na fonte bitmap. **`particleGlyph`:** só `·` `†` `◆` `~`.
- **`isGlitchy = true` (19 subtipos):** Fantasma, AbismoMarinho, Profundeza, Leviata, Dimensao, Sombra, Void, Eclipse, Fragmentacao, Ilusao, MiragemAstral, Demonio, Trevas, Corrupcao, Necromante, Lich, Controle, Mutacao, Nosferatu.
- **Campos extras** (não quebram o contrato pedido): `displayName` com acentos, `family` e `order`. API: `get`, `getOrDefault` (nunca falha), `byFamily`, `resolveColors` (mesma fórmula do atlas) e `validate` (autoteste).
- **Para editar:** mude `pipeline/dark_altar/subtypes.py` e rode o gerador. Nunca edite o `.luau` gerado à mão.

### 6.2 Spec da Forja (`docs/specs/CURRENT_SPEC.md`)
- **Tipo Dominante:** maior valor entre ATQ/GRD/BUF/DEB, desempate na ordem ATQ → GRD → BUF → DEB, `NEUTRO` se tudo ≤ 0. Valores NaN ou negativos contam como 0. `[SAC]` é modificador. Inclui código de referência e tabela de testes.
- **Níveis:**
  - os tokens pedidos estão exatos (#1E1E24, #2C2E35, #4DD0E1, #B388FF, #E5A93C);
  - os ornamentos acumulam e a borda é substituída;
  - gradiente violeta em degraus (≤ 6 paradas) girando por `Rotation`;
  - whiteout com **max(20 ms, 1 quadro)**, para não sumir a 30 FPS, e opção de reduzir flashes.
- **Performance:**
  - um único relógio (`PixelClock` em PreRender);
  - pools fixos;
  - modo `LOW` para mobile;
  - orçamento de instâncias;
  - nada de CanvasGroup.

### 6.3 VFX (lint: gate 85)

| VFX | Quadros | Total | Lint | Uso |
|---|---|---|---|---|
| fire_loop | 8 | 664 ms (loop) | 100 | forja, tocha |
| explosion | 11 | 800 ms | 93 | bomba, supernova |
| slash_arc `[ATQ]` | 7 | 433 ms | 100 | ataque |
| impact_spark | 6 | 334 ms | 100 | acerto |
| magic_circle | 8 | 664 ms (loop) | 100 | ritual |
| ward_shield `[GRD]` | 8 | 517 ms | 100 | defesa |
| ascend_aura `[BUF]` | 8 | 664 ms (loop) | 100 | buff |
| curse_smoke `[DEB]` | 8 | 600 ms | 93 | debuff |
| blood_burst `[SAC]` | 8 | 434 ms | 96 | sacrifício |
| embers_rising | 12 | 996 ms (loop) | 95 | forja, carta +4 |
| holy_pillar | 8 | 664 ms (loop) | 100 | carta +5, sagrado |
| transition_dither / diamond / iris | 16 / 16 / 14 | 528 / 528 / 462 ms | 90 | troca de tela |

### 6.4 Cenário
`scene.cathedral` (320×180, 22 cores) reproduz a composição da referência:
- vitrais como único croma alto, com padrão desenhado (faixas simétricas + medalhão);
- porta ogival;
- colunas;
- estátuas aladas com rim light violeta;
- piso xadrez em perspectiva com reflexo em degraus e faixas de luz colorida;
- vinheta.

### 6.5 Skill `roblox-pixel-art`
- `SKILL.md` com:
  - regras de ouro;
  - fluxo obrigatório (com portão de lint e prévia);
  - API e CLI do motor;
  - receitas por tipo de asset;
  - fluxo com o Studio MCP (local) e o caminho alternativo na nuvem;
  - limites honestos.
- Seis referências: fundamentos, animação/VFX, UI/ícones/telas, cenários, integração Roblox e QA.
- Para usar no claude.ai: compacte a pasta `.claude/skills/roblox-pixel-art/` em zip e envie em Configurações > Skills. Em sessões do Claude Code neste repositório ela é carregada sozinha.

---

## 7. O que NÃO foi verificado (e por quê)
- **Type-check Luau:** baixar e rodar `luau-lsp`/`luau-analyze` foi bloqueado pela política do ambiente. Os módulos foram revisados linha a linha contra as regras do solver antigo (anotação no ponto de criação, sem `any`, refinamentos simples), mas **rode a Script Analysis do Studio** antes de dar por aprovado.
- **Execução no Studio:** esta sessão roda na nuvem e não alcança o MCP local do Studio. `SpriteAnimator`, `PixelClock`, `FlipbookVFX` e o snippet de EditableImage não foram executados no Roblox.
- **`HudView`/`DesignTokens`/Gate RT2:** não encontrei o código do jogo em nenhum repositório acessível (`MyRobloxJunkie` só tem arquivos vazios). A compatibilidade ficou isolada no adaptador `CardTokens` (spec §9).
- **Upload Open Cloud:** o script segue a documentação, mas não foi testado (sem chave, como deve ser).
- **Compressão mobile:** a variante ×4 é mitigação recomendada pela comunidade, ainda não medida no aparelho.

---

## 8. Limitações conhecidas do motor
- Figuras **orgânicas** (estátuas, criaturas, rostos) feitas por procedimento ficam esquemáticas. As asas das estátuas da catedral precisaram de 3 iterações. Solução: máscara ASCII desenhada + sombreamento do motor, ou rascunho do usuário quantizado.
- O lint é heurístico. Ele detecta banding concêntrico, mas não banding por segmentos alinhados (o critério do *Pixel Logic*).
- Os VFX seguem receitas boas, mas ainda não chegam ao nível de um animador sênior em fluidez de fumaça e fogo: são 8–12 quadros procedurais, contra 20–30 desenhados à mão.

---

## 9. Pontos de melhoria (prioridade)
1. **`scene.forge`:** a segunda referência pedida. Poça de luz quente (L-09), lajotas hexagonais iluminadas por laje, bigorna com rim light, lareira com `fire_loop` e palette cycling.
2. **Máscaras desenhadas + sombreamento automático:** um formato `.txt`/ASCII de silhueta por sprite (personagens, estátuas, ícones de carta específicos), com o motor fazendo rampa, sel-out, rim e lint.
3. **Mais geradores:**
   - raio por deslocamento do ponto médio;
   - editions do Balatro por texel (foil/holo/polychrome quantizados);
   - número de dano pop;
   - "contrast frame + impact frame" para golpes críticos.
4. **Lint de nível 2:**
   - detector de banding por segmentos alinhados;
   - validação de rampa (ΔL ≥ 0,06 e |ΔH| ≤ 22°);
   - checagem de linha pixel-perfect;
   - flicker entre quadros;
   - calibração dos limiares contra sprites aprovados por você.
5. **Palette cycling exportado:** sheets de 4–8 quadros por troca de cor para vitral, lava e runas (animação sem custo de CPU no Roblox).
6. **Teste automático no Studio (MCP local):** script que monta a carta +0..+5, faz `screen_capture` e compara com o mockup, para pegar regressão visual.
7. **Variante ×4 paginada do atlas de subtipos** (8 páginas de 1024²), caso a compressão mobile se confirme no seu aparelho.
8. **Implementar `CardView`/`CardForgeOrnaments`** no repositório do jogo seguindo a spec, com uma story por nível.

---

## 10. Avaliação técnica final (nota 0–10)

| Critério | Nota | Comentário |
|---|---:|---|
| Performance (memória e conexões) | 8,5 | 1 relógio para toda a UI, atlas compartilhados, pools fixos, modo LOW, alpha bleed e limites do Roblox respeitados. Falta medir no aparelho. |
| Organização da hierarquia de arquivos | 9,0 | Fonte única → gerador → `.luau` + PNG. Skill portátil separada do projeto. Spec e relatório para outra sessão. |
| Legibilidade de fluxo para não programador | 8,5 | Comentários em PT-BR com "onde colar", fluxos em passos, CLI curta. A spec é longa, mas tem tabelas por nível. |
| Qualidade visual alcançada | 7,0 | Subtipos, ornamentos, VFX e catedral coerentes e limpos (lint 90–100). Ainda abaixo do acabamento à mão das referências em fumaça, fogo e figuras orgânicas. |
| Robustez anti-erro | 8,0 | `getOrDefault`, `validate`, pcall nos relógios, guarda contra ms = 0 e reentrância. Falta o type-check real do Luau. |

**Nota geral: 8,2 / 10.** Como sistema de produção, o motor está sólido: determinístico, testável e documentado. Para chegar a 9+, faltam três coisas: o gerador da forja, as máscaras desenhadas para figuras orgânicas e a validação no Studio e no aparelho.
