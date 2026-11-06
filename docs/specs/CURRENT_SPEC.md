# CURRENT_SPEC — CardView + CardForgeOrnaments (Fusion 0.3)

| Campo | Valor |
|---|---|
| Projeto | The Dark Altar (card game gótico, Roblox) |
| Escopo | `CardView.luau`, `CardForgeOrnaments.luau`, `SubtypeArtView.luau`, `CardTyping.luau` |
| Dados | `src/shared/Config/SubtypeArtCatalog120.luau` (120 artes de subtipo, gerado) |
| Assets | `art/dark-altar/forge/*`, `art/dark-altar/subtypes/*` (gerados pelo PixelForge) |
| Runtime | `src/shared/Pixel/` (`PixelClock`, `SpriteAnimator`, `PixelScale`, `FlipbookVFX`) |
| UI lib | Fusion **0.3** (API com `scope`) |
| Integração | `HudView.panel` (Gate RT2) e `DesignTokens` (ver §9: contrato assumido) |
| Status | Pronto para implementação |

> Esta sessão **não teve acesso** ao código de `HudView` e `DesignTokens`. Tudo o que depende deles está isolado no adaptador `CardTokens` (§9). Antes de implementar, o Claude Code deve abrir os dois módulos reais e ajustar **só** o adaptador.

---

## 0. Regras inegociáveis (valem para todo arquivo desta spec)

1. **Luau `--!strict`** na primeira linha. **Proibido `any`** (inclusive implícito). Todo tipo público usa `export type`.
2. **Proibido emoji.** Nenhum caractere do bloco **U+2600–27BF** em código, strings ou dados. Tags só entre colchetes: `[ATQ]`, `[GRD]`, `[BUF]`, `[DEB]`, `[SAC]`. Glifos permitidos: `◆ ◇ ▸ † ‡ ▲ ~ ·`.
   - Armadilhas comuns, todas **bloqueadas**: estrela de 4 pontas (U+2726), estrela cheia (U+2605), caveira (U+2620) e espadas cruzadas (U+2694). Use `◆`, `†` ou tags.
3. **Pixel art nunca escala fracionado.** Toda `ImageLabel`/`ImageButton` de arte usa `ResampleMode = Enum.ResamplerMode.Pixelated`. O tamanho na tela é sempre `k × nativo`, com `k` inteiro vindo do `UIScale` (`PixelScale`).
4. **Um único relógio de animação.** Nenhum componente abre `RenderStepped`/`Heartbeat` próprio. Tudo assina `PixelClock.subscribe` e devolve o *unsubscribe* ao `scope`.
   - O `PixelClock` usa `RunService.PreRender`, que a documentação oficial apresenta como substituto do `RenderStepped` (mesmo momento: antes de desenhar o quadro). O requisito "girar via RenderStepped" fica atendido com o nome atual da API e sem warning de API legada.
5. **Isolamento Client/Server.** Todos os arquivos desta spec rodam **só no cliente**. O servidor nunca cria UI. O servidor só envia o estado da carta (`CardData`) por `RemoteEvent` ou atributo.
6. **Anti-erro.** Todo `require` de asset e config usa `WaitForChild` com timeout e fallback. Dados desconhecidos (subtipo inexistente, `forgeLevel` fora de 0..5) **degradam** para um visual neutro e geram `warn`, nunca `error`.

---

## 1. Modelo de dados

```lua
--!strict
-- src/shared/Cards/CardTypes.luau  (ReplicatedStorage > Shared > Cards)

export type DominantType = "ATQ" | "GRD" | "BUF" | "DEB" | "NEUTRO"
export type ForgeLevel = number -- inteiro 0..5 (validado por CardTyping.clampForge)

export type CardStats = {
	damage: number, -- [ATQ]
	defense: number, -- [GRD]
	buff: number, -- [BUF]
	debuff: number, -- [DEB]
	sacrifice: number?, -- [SAC] (modificador; NAO disputa o tipo dominante)
}

export type CardData = {
	id: string,
	name: string, -- ja em MAIUSCULAS ou como o jogo exibir
	subtypeId: string, -- chave do SubtypeArtCatalog120 (ex.: "Fogo")
	cost: number,
	stats: CardStats,
	rulesText: string, -- texto curto; tags so entre colchetes
	forgeLevel: ForgeLevel,
}
```

---

## 2. Tipo Dominante (`CardTyping.luau`)

**Regra:** o tipo dominante é o **maior valor numérico** entre Dano `[ATQ]`, Defesa `[GRD]`, Buff `[BUF]` e Debuff `[DEB]`.

- **Desempate:** fica com quem vem primeiro na ordem fixa **ATQ → GRD → BUF → DEB** (comparação `>` estrita).
- **Todos ≤ 0:** o resultado é `"NEUTRO"`, sem chip de tipo.
- **Saneamento:** `NaN`, valores negativos e `nil` contam como `0`.
- `[SAC]` é modificador. Aparece como selo extra quando `sacrifice > 0` e **não** disputa o dominante.

Implementação de referência (pura, testável, sem Instances):

```lua
--!strict
-- src/shared/Cards/CardTyping.luau  (ReplicatedStorage > Shared > Cards)
local CardTypes = require(script.Parent:WaitForChild("CardTypes"))

type DominantType = CardTypes.DominantType
type CardStats = CardTypes.CardStats

local ORDER: { DominantType } = { "ATQ", "GRD", "BUF", "DEB" } -- ordem = desempate

local CardTyping = {}

CardTyping.TAG = table.freeze({
	ATQ = "[ATQ]",
	GRD = "[GRD]",
	BUF = "[BUF]",
	DEB = "[DEB]",
	NEUTRO = "",
})

local function sane(v: number?): number
	if v == nil or v ~= v or v < 0 then -- nil, NaN ou negativo
		return 0
	end
	return v
end

function CardTyping.dominant(stats: CardStats): DominantType
	local values: { [DominantType]: number } = {
		ATQ = sane(stats.damage),
		GRD = sane(stats.defense),
		BUF = sane(stats.buff),
		DEB = sane(stats.debuff),
	}
	local best: DominantType = "NEUTRO"
	local bestValue = 0
	for _, kind in ORDER do
		local v = values[kind] or 0
		if v > bestValue then -- '>' estrito: empate fica com quem vem antes
			best = kind
			bestValue = v
		end
	end
	return best
end

function CardTyping.clampForge(level: number?): number
	local n = math.floor(sane(level))
	return math.clamp(n, 0, 5)
end

return table.freeze(CardTyping)
```

**Tabela de testes obrigatória** (rodar no Command Bar ou num TestEZ/Jest-Lua):

| damage | defense | buff | debuff | esperado |
|---:|---:|---:|---:|---|
| 6 | 0 | 0 | 0 | ATQ |
| 4 | 12 | 0 | 0 | GRD |
| 0 | 0 | 2 | 2 | BUF (empate BUF×DEB → BUF) |
| 5 | 5 | 0 | 0 | ATQ (empate → ATQ) |
| 0 | 0 | 0 | 0 | NEUTRO |
| -3 | 0/0 (NaN) | 0 | 1 | DEB |

**Estilo por tipo**, consumido via `CardTokens` (§9). Cores de tipo são **diferentes** das cores de raridade da Forja para não confundir:

| Tipo | Chip | Cor do texto (fallback) | Glifo |
|---|---|---|---|
| ATQ | `[ATQ]` | `#F28A2E` | `†` |
| GRD | `[GRD]` | `#7FA6C9` | `◆` |
| BUF | `[BUF]` | `#9FBB74` | `▲` |
| DEB | `[DEB]` | `#C25BFF` | `~` |
| NEUTRO | (sem chip) | — | `·` |

---

## 3. Grade de pixels da carta

Tudo é desenhado em **pixels da arte** e ampliado por `UIScale` inteiro (`k`). Medidas abaixo em px nativos:

```
Carta: 72 x 104
 ┌──────────────────────────────┐ y=0
 │ ◆2   TÍTULO (fonte 5x7)      │ y=4..11   (cabeçalho: custo + nome)
 │ ┌──────────────────────────┐ │ y=14
 │ │  ARTE DO SUBTIPO 64x64   │ │ x=4..67
 │ │  (SubtypeArtView)        │ │
 │ └──────────────────────────┘ │ y=78
 │ [ATQ]                  6     │ y=84..91  (chip do tipo + valor dominante)
 │ texto de regra (1-2 linhas)  │ y=93..101
 └──────────────────────────────┘ y=104
```

- `k` = `PixelScale.compute(viewport, Vector2.new(72*colunas + gaps, 104), fração)`, limitado a 1..4.
- Em celulares com DPI 2x/3x, `k = 1` já fica nítido. Não force `k = 2` se não couber.
- Ornamentos que **saem** da carta (arco, coroa, coluna de luz, glifos orbitais) ficam num `Frame` irmão com `ClipsDescendants = false`, para não serem cortados pelo corpo.

---

## 4. Árvore de componentes — `CardView`

```
CardView (ImageButton)                        -- raiz: input, AutoButtonColor=false, BG transparente
├─ UIScale                                    -- k inteiro (PixelScale.bind)
├─ BackFx (Frame, ZIndex 1)                   -- atrás da carta, NÃO recorta
│  ├─ LightColumn (+5)                        -- ImageLabel + SpriteAnimator(holy_pillar)
│  └─ EchoGhosts (+5) x3                      -- rastro ecoante (Springs com atraso)
├─ Body (Frame 72x104, ZIndex 2, ClipsDescendants=true)
│  ├─ Fill (Frame)                            -- #1E1E24 (ardósia)
│  ├─ SubtypeArtView (64x64 em 4,14)          -- §6 (modo ATLAS ou PROCEDURAL)
│  ├─ Foil (+4) (ImageLabel tile)             -- foil holográfico escuro sobre a arte
│  ├─ Sheen (+2) (Frame + UIGradient)         -- varredura diagonal de reflexo
│  ├─ Header (Frame)
│  │  ├─ CostGem (TextLabel "◆" + número)
│  │  └─ Title (TextLabel)
│  ├─ TypeChip (TextLabel "[ATQ]")            -- só se dominante ~= NEUTRO
│  ├─ DominantValue (TextLabel)
│  ├─ SacSeal (+ se sacrifice>0) "[SAC]"
│  └─ RulesText (TextLabel, TextWrapped)
├─ CardForgeOrnaments (Frame 72x104, ZIndex 3) -- §5: bordas e ornamentos por nível
└─ FrontFx (Frame, ZIndex 4, sem recorte)     -- glifos orbitais da frente, brasas, flash local
```

### 4.1 Props (tipadas)

```lua
--!strict
export type ArtMode = "ATLAS" | "PROCEDURAL"
export type Quality = "HIGH" | "LOW"

export type CardViewProps = {
	card: Fusion.UsedAs<CardTypes.CardData>,
	forgeLevel: Fusion.UsedAs<number>?, -- se nil, usa card.forgeLevel
	artMode: ArtMode?, -- padrão "ATLAS" (recomendado mobile)
	quality: Fusion.UsedAs<Quality>?, -- "LOW" desliga foil/eco/orbitais/brasas
	pixelScale: Fusion.UsedAs<number>?, -- k; se nil o componente cria UIScale com PixelScale.bind
	dragPosition: Fusion.UsedAs<UDim2?>?, -- quando arrastada (alimenta o rastro +5)
	Position: Fusion.UsedAs<UDim2>?,
	AnchorPoint: Fusion.UsedAs<Vector2>?,
	LayoutOrder: number?,
	overlayParent: Instance?, -- camada de topo p/ whiteout (HudView fornece)
	onPlay: ((cardId: string) -> ())?,
	onHover: ((cardId: string, hovering: boolean) -> ())?,
}
```

### 4.2 Esqueleto Fusion 0.3

```lua
--!strict
-- src/client/UI/Cards/CardView.luau  (StarterPlayerScripts ou ReplicatedStorage > Client > UI)
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Fusion = require(ReplicatedStorage:WaitForChild("Packages"):WaitForChild("Fusion"))
local Shared = ReplicatedStorage:WaitForChild("Shared")
local CardTypes = require(Shared:WaitForChild("Cards"):WaitForChild("CardTypes"))
local CardTyping = require(Shared.Cards:WaitForChild("CardTyping"))
local CardTokens = require(script.Parent:WaitForChild("CardTokens"))
local SubtypeArtView = require(script.Parent:WaitForChild("SubtypeArtView"))
local CardForgeOrnaments = require(script.Parent:WaitForChild("CardForgeOrnaments"))

local Children, OnEvent = Fusion.Children, Fusion.OnEvent
type Scope = Fusion.Scope<typeof(Fusion)>
type UsedAs<T> = Fusion.UsedAs<T>

local function CardView(scope: Scope, props: CardViewProps): ImageButton
	-- estado derivado (recalcula só quando 'card' muda)
	local dominant = scope:Computed(function(use)
		return CardTyping.dominant(use(props.card).stats)
	end)
	local level = scope:Computed(function(use)
		local explicit = props.forgeLevel
		local raw = if explicit ~= nil then use(explicit) else use(props.card).forgeLevel
		return CardTyping.clampForge(raw)
	end)
	local hovering = scope:Value(false)
	local hoverLift = scope:Spring(scope:Computed(function(use)
		return if use(hovering) then -2 else 0 -- sobe 2 px nativos (k aplicado pelo UIScale)
	end), 40, 0.9)

	return scope:New "ImageButton" {
		Name = "CardView",
		AutoButtonColor = false,
		BackgroundTransparency = 1,
		Size = UDim2.fromOffset(72, 104),
		Position = props.Position,
		AnchorPoint = props.AnchorPoint,
		LayoutOrder = props.LayoutOrder,
		[OnEvent "MouseEnter"] = function() hovering:set(true) end,
		[OnEvent "MouseLeave"] = function() hovering:set(false) end,
		[OnEvent "Activated"] = function()
			local data = Fusion.peek(props.card)
			if props.onPlay then props.onPlay(data.id) end
		end,
		[Children] = {
			-- UIScale + Body + CardForgeOrnaments + Fx (ver árvore 4)
			-- Body usa Position = UDim2.fromOffset(0, use(hoverLift)) arredondado:
			--   math.round(use(hoverLift)) para nunca ficar em sub-pixel
		},
	} :: ImageButton -- scope:New devolve Instance no Fusion 0.3: o cast é obrigatório
end

return CardView
```

Notas do Fusion 0.3 (confirmadas no código da tag 0.3.0):
- Anote sempre `Fusion.Scope<typeof(Fusion)>`. O tipo padrão no código-fonte é `any` e isso desliga a checagem.
- `scope:New` devolve `Instance`. Faça cast para a classe (`:: Frame`, `:: ImageLabel`).
- `scope:insert` **não existe** na 0.3 (é da 0.4-dev). Para tarefas de limpeza, use `table.insert(scope, tarefa)`.
- O `New` do Fusion já aplica `AutoButtonColor = false` em botões e `BorderSizePixel = 0`. Ainda assim, declare `BackgroundTransparency = 1` onde a arte é só imagem.
- Prop opcional é `UsedAs<T>?`. Prop que aceita nil é `UsedAs<T?>`. Não confunda os dois.

Regras do esqueleto:
- **Componentes condicionais por nível** usam o padrão "booleano estável + Computed com scope interno". Assim nada é recriado quando o nível muda de 2 para 3 nos itens que já existiam:
  ```lua
  local hasL2 = scope:Computed(function(use) return use(level) >= 2 end)
  local arch = scope:Computed(function(use, innerScope)
      if not use(hasL2) then return nil end
      return OgivalArch(innerScope, { scale = props.pixelScale }) -- destruído junto com innerScope
  end)
  ```
- **Animações por quadro não passam por `Value:set`.** Elas escrevem direto na propriedade da Instance dentro do callback do `PixelClock`, para não disparar Computeds 60 vezes por segundo. O *unsubscribe* vai para o `scope`.

---

## 5. `CardForgeOrnaments` — evolução +0 a +5

**Princípio:** os ornamentos **acumulam** (o +3 tem tudo do +1 e do +2). A **borda** (cor e espessura) é **substituída** pela do nível mais alto. Todos os sprites vêm de `ForgeOrnamentAtlas.png` (`ForgeOrnamentAtlas.luau` tem os retângulos). Mockup de referência: `art/dark-altar/forge/mock_forge_levels.png`.

Para ver o visual esperado de cada nível, abra `art/dark-altar/forge/mock_forge_levels.png`.

| Nível | Nome | Borda | Ornamentos adicionados | Animação |
|---|---|---|---|---|
| **+0** | `.0 Comum` | fundo ardósia **#1E1E24** + contorno **1 px ferro #2C2E35** | — | nenhuma |
| **+1** | `.1 Incomum` | contorno **2 px Ciano #4DD0E1** | **4 cantoneiras** de ferro forjado (`corner_tl/tr/bl/br`, 11×11) | nenhuma (estático = barato) |
| **+2** | `.2 Raro` | ciano 2 px | **Arco ogival** no topo (`arch_top` 41×18, sobrepõe 4 px) + **Selo rúnico** no rodapé (`rune_seal` 15×15, centrado na borda inferior) | **Sheen**: faixa diagonal de reflexo metálico atravessa a carta em 0,45 s a cada 3,5 s (+ atraso aleatório 0–1,5 s por carta) |
| **+3** | `.3 Épico` | **gradiente Violeta #B388FF** em 2 px | **Filigrana espinhosa dupla** nas laterais (`filigree_l/r` 9×64, a partir de y=20) + **3 glifos orbitais** (`◆ † ◇`) | gradiente gira **360° em 4 s** via `PixelClock` (RenderStepped). Glifos orbitam numa elipse (rx = 0,62·W, ry = 0,56·H) com período de 6 s e ZIndex trocando frente/trás |
| **+4** | `.4 Mítico` | **Âmbar #E5A93C** 2 px | **Coroa Tripla do Altar** (`crown_triple` 33×19, acima do arco) + **Foil holográfico escuro** sobre a arte do subtipo (`foil_tile` 32×32 em Tile) | foil rola 8 px/s na diagonal (pixel-snap). **Brasas ascendentes**: pool fixo de 6 sprites `ember_0..2`, ciclo 1,8 s |
| **+5** | `[†] Relíquia Forjada em Sangue` | **Moldura viva de Gengiva Gótica & Osso** (`relic_frame` 72×104 cobre a borda) | **Coluna de luz** atrás da carta (sprite `holy_pillar` 24×64, 8 quadros) + **Rastro Ecoante** (3 fantasmas) + **Whiteout Flash 20 ms** ao jogar | moldura "respira" alternando `ImageColor3` (branco ↔ #FFE3E7) a cada 1,2 s. Coluna em loop pelo SpriteAnimator. Eco: 3 cópias seguem `dragPosition` com Springs (velocidades 28/20/14, transparência 0,55/0,70/0,85) |

### 5.1 Detalhes de implementação por elemento

**Borda (todos os níveis).** Use uma `ImageLabel` com a máscara branca `border_1px`/`border_2px`:
- `ScaleType = Slice`, `SliceCenter = ForgeOrnamentAtlas.SLICE_1PX/_2PX`, `SliceScale = 1`.
- O `UIScale` da carta já amplia; não multiplique `SliceScale` de novo.
- `ImageColor3` recebe a cor do nível. Assim a mesma imagem serve a todos os níveis.
- No **+3** a borda usa `ImageColor3 = branco` com um `UIGradient` filho.
- **Gradiente "pixel-friendly"** (+3): use `ColorSequence` com **degraus duros**. Repita a cor em dois keypoints vizinhos para evitar degradê liso:
  ```lua
  ColorSequence.new({
      ColorSequenceKeypoint.new(0.00, Color3.fromHex("#513199")),
      ColorSequenceKeypoint.new(0.32, Color3.fromHex("#513199")),
      ColorSequenceKeypoint.new(0.33, Color3.fromHex("#B388FF")),
      ColorSequenceKeypoint.new(0.65, Color3.fromHex("#B388FF")),
      ColorSequenceKeypoint.new(0.66, Color3.fromHex("#F6D9FF")),
      ColorSequenceKeypoint.new(1.00, Color3.fromHex("#F6D9FF")),
  })
  ```
  Rotação: `gradient.Rotation = (now * 90) % 360` dentro do callback do `PixelClock`.
  - Desde 29/out/2026 o `UIGradient` interpola em espaço **linear**. Com degraus duros isso não muda o visual.
  - Orientação oficial: no máximo **6 paradas de cor**; anime **`Rotation`/`Offset`**, nunca `Color`/`Transparency` (que reconstroem o gradiente a cada quadro).

**Cantoneiras (+1).** São 4 `ImageLabel` com sprites próprios. **Não** rotacione um único sprite, porque a luz (topo-esquerda) ficaria errada nos outros cantos. Posições: `(-2,-2)`, `(W-9,-2)`, `(-2,H-9)`, `(W-9,H-9)`.

**Sheen (+2).** Um `Frame` branco do tamanho do `Body` com `UIGradient`:
- `Transparency` em degraus: 1 → 0,55 numa faixa de 6% → 1. `Rotation = 45`.
- Anima `Offset.X` de −1 a 1 em 0,45 s com `Enum.EasingStyle.Quad` e `TweenService`, disparado pelo `PixelClock` no intervalo.

**Selo rúnico e arco (+2).** O selo é centralizado na borda inferior (metade para fora). O arco fica centralizado no topo, com a soleira sobrepondo 4 px. Os dois ficam no `Frame` de ornamentos sem recorte.

**Glifos orbitais (+3).** São 3 `ImageLabel` (`glyph_diamond/dagger/hollow`, 5×7, tintados `#D6A5F4`). Cálculo a cada quadro:
- Ângulo: `θ = now·(2π/6) + i·2π/3`.
- Posição: `(cx + cos θ·rx, cy + sin θ·ry)`, arredondada com `PixelClock.snap(v, k)`.
- **Profundidade:** se `sin θ < 0`, o glifo vai para `BackFx` (ZIndex 1); caso contrário, para `FrontFx` (ZIndex 4). Trocar o `Parent` só quando o sinal muda.

**Foil (+4).** `ImageLabel` `foil_tile` com:
- `ScaleType = Tile`, `TileSize = UDim2.fromOffset(32, 32)`, `ImageTransparency = 0.72`.
- Fica dentro de um `Frame` 64×64 com `ClipsDescendants`, por cima da arte e abaixo do texto.
- Movimento: `Position = ((t·8) % 32, (t·8) % 32)` com pixel-snap.

**Brasas (+4).** Pool **fixo** de 6 `ImageLabel` criadas uma vez. Nada de `Instance.new` por quadro.
- Fase `p = (now/1.8 + i/6) % 1`.
- Posição: `y = H − p·(H+12)`, `x = baseX_i + round(sin(2π(p + i·0.37))·2)`.
- Quadro: `ember_0` se `p < .3`, `ember_1` se `p < .7`, senão `ember_2`.

**Coluna de luz (+5).** `ImageLabel` de 48×128 (sprite 24×64 em 2×, inteiro) atrás da carta, centrada, tocada por `SpriteAnimator.play` com o módulo gerado `holy_pillar_Sprite.luau` (`loop = true`).

**Rastro Ecoante (+5).**
- São 3 `ImageLabel` com o sprite `relic_frame`, tintados `#A02F3C`.
- Cada um segue `dragPosition` por `scope:Spring(target, speed_i, 1)`.
- Só ficam visíveis enquanto `dragPosition ~= nil` ou nos 300 ms seguintes a jogar a carta.

**Whiteout Flash 20 ms (+5).**
- Ao jogar, um `Frame` em `overlayParent` (tela cheia, `#FFF8EC`, `BackgroundTransparency = 0`) fica visível por **max(20 ms, 1 quadro renderizado)** e depois some.
- Implementação: guardar `t0` e contar quadros no `PixelClock`. Esconder quando `now − t0 ≥ 0.02` **e** `quadros ≥ 1`. Assim o flash é garantido mesmo a 30 FPS.
- **Acessibilidade:** pular o flash se a opção do jogo "Reduzir flashes" estiver ativa. Se o projeto usar a configuração de movimento reduzido do Roblox, ler também (verificar o nome atual da API na documentação).

**Moldura viva (+5).** `ImageLabel` `relic_frame` 72×104 com ZIndex acima da arte e abaixo do texto. Título e chip ficam em ZIndex maior. A respiração alterna `ImageColor3` (sem escalar: escala fracionada quebra o pixel).

### 5.2 Esqueleto `CardForgeOrnaments`

```lua
--!strict
-- src/client/UI/Cards/CardForgeOrnaments.luau
export type CardForgeOrnamentsProps = {
	level: Fusion.UsedAs<number>, -- 0..5 já validado
	quality: Fusion.UsedAs<"HIGH" | "LOW">,
	pixelScale: Fusion.UsedAs<number>,
	backFx: Frame, -- camadas criadas pelo CardView
	frontFx: Frame,
	overlayParent: Instance?,
	dragPosition: Fusion.UsedAs<UDim2?>?,
}

-- Retorna o Frame de ornamentos + uma função 'flash()' para o CardView chamar ao jogar.
export type CardForgeOrnamentsResult = { root: Frame, flash: () -> () }
```

Fluxo interno:
1. `borderColor = Computed(level → token)`, `borderThickness = Computed(level → 1|2)`, `borderImage = Computed(level → "border_1px"|"border_2px")`.
2. Para cada faixa de nível (`>=1`, `>=2`, `>=3`, `>=4`, `==5`), um `Computed` booleano estável.
3. Um `Computed(use, innerScope)` por faixa cria os sprites daquela faixa. As assinaturas do `PixelClock` vão para o `innerScope`, então descer de nível limpa tudo sozinho.
4. `quality == "LOW"` desliga: foil animado (fica estático), glifos orbitais (ficam fixos), brasas, eco e coluna (vira sprite estático, quadro 1). Bordas e ornamentos estáticos permanecem.

---

## 6. `SubtypeArtView` — arte de fundo do subtipo

Entrada: `subtypeId` → `SubtypeArtCatalog120.getOrDefault(id)` (nunca falha) → `resolveColors(entry)`.

### Modo `ATLAS` (padrão, recomendado para mão e campo no mobile)

- **1 `ImageLabel`** com `SubtypeArtAtlas120.apply(label, subtypeId)`. O atlas tem 1024×512 px, com células de 64×64 já desenhadas em pixel art pelo PixelForge.
- Custo: 1 instância por carta, 1 textura compartilhada por todas.
- Para glitch (`isGlitchy`), um overlay de 2 `Frame` finos (1–2 px) com cópia deslocada (±2 px) aparece por 1 quadro a cada 1,2–2,4 s (aleatório por carta).

### Modo `PROCEDURAL` ("xilogravura em Fusion Frames": telas de detalhe, coleção, carta ampliada)

Ordem das camadas (ZIndex crescente):
1. **Fundo:** `Frame` com `BackgroundColor3 = colors.bg`.
2. **Gravura:** `ImageLabel` da `EtchingAtlas.png` (64×64 por padrão, ordem `SPIKES, ARCHES, WAVES, RAYS, ABYSS, ROOTS, FRACTAL, SCALES` → `ImageRectOffset = (índice·64, 0)`), `ImageColor3 = colors.etch`.
3. **Monograma:** `TextLabel` com `watermarkGlyph`, `FontFace = Font.fromEnum(Enum.Font.GrenzeGotisch)` (blackletter), `TextColor3 = colors.watermark`, `TextScaled = true`, tamanho de 70% da arte.
4. **Emblema** (`centerSilhouettes`, todas centradas). Para **cada** silhueta são 3 `ImageLabel` da `ShapeMaskAtlas.png` (coluna = forma na ordem `DIAMOND, PILLAR, RING, BLADE, CRESCENT, CROWN`; linha 0 = fill, 1 = shade, 2 = ink):
   - `ink` → `ImageColor3 = colors.ink`; `fill` → `colors.accent`; `shade` → `colors.accentShadow`.
   - `Size = UDim2.fromScale(scaleX, scaleY)`, `AnchorPoint = (0.5, 0.5)`, `Position = (0.5, 0.5)`, `Rotation = rotation`.
   - Ordem de desenho = ordem da lista (a próxima silhueta cobre a anterior, com o ink separando).
5. **Partículas:** 5–7 `TextLabel` com `particleGlyph`, posições determinísticas por hash do `subtypeId` num anel de raio 30–46% da arte, cor `accent` ou `accent:Lerp(bg, 0.45)`.
   - Se a fonte não tiver o glifo, use os sprites `glyph_*` do `ForgeOrnamentAtlas`.
6. **Glitch** (`isGlitchy = true`): o monograma é quebrado com `utf8.graphemes`, um `TextLabel` por grafema:
   ```lua
   for first, last in utf8.graphemes(entry.watermarkGlyph) do
       local grapheme = string.sub(entry.watermarkGlyph, first, last)
       -- cria um TextLabel por grafema; o PixelClock aplica tremor
   end
   ```
   A cada 90–160 ms (aleatório por carta), **um** grafema recebe offset de ±1 px nativo por 1 quadro. Raramente (a cada 1,2–2,4 s), uma "fatia" horizontal da arte é deslocada 2 px.

**Rotação em pixel art:** rotacionar `ImageLabel` gera serrilhado (o Roblox amostra o pixel rotacionado). Por isso o modo ATLAS já vem com as rotações "assadas" e ajustadas a ângulos limpos (0°, 26,57°, 45°...). No modo PROCEDURAL, aceite o serrilhado ou restrinja `rotation` a múltiplos de 45° nas telas de detalhe.

---

## 7. Performance (orçamento para mobile)

| Item | Orçamento |
|---|---|
| Conexões de frame | **1** (`PixelClock`) para todas as cartas |
| Instâncias por carta (ATLAS, +0) | ≤ 12 |
| Instâncias por carta (+5, HIGH) | ≤ 40 (pool fixo, nada criado por quadro) |
| Cartas animadas ao mesmo tempo | ≤ 8 (cartas fora da tela → `quality = LOW` ou desassinar) |
| Texturas | 3 atlas compartilhados (subtipos, ornamentos, máscaras) + sprites de VFX |
| `CanvasGroup` | **evitar** na carta (render offscreen custa memória e borra pixel art) |
| Tamanho de imagem | ≤ 1024×1024 (acima disso o Roblox reduz e destrói o pixel) |

**Compressão no mobile (confirmado pela equipe Roblox, sem correção prevista):**
- Imagens de UI sofrem compressão de bloco com perdas no celular, e pixel art nativa perde cor.
- Para sprites críticos (ornamentos da Forja, chips), exporte a variante **×4** do PixelForge (`export_gui_sheet(..., upscale=4)`): cada pixel da arte vira exatamente um bloco 4×4 de compressão.
- Os retângulos do atlas mudam junto (o gerador já multiplica). Teste em aparelho real antes de decidir; a variante ×4 custa 16× mais memória.
- Todo PNG exportado já sai com **alpha bleed**. O upload troca o RGB transparente por preto, e sem o bleed aparece franja escura.
- **Upload:** use `assetType = "Image"`, não Decal. O ID de Decal não funciona em `ImageLabel.Image` via script.

Faça tudo isso:
- Pré-carregue os atlas com `ContentProvider:PreloadAsync({...})` na tela de loading.
- Pause as animações de cartas invisíveis: quando `Visible`/`AbsolutePosition` sair da tela, chame o *unsubscribe*.
- Desligue o eco e as brasas em `quality = LOW`, que é o padrão em dispositivos com `UserInputService.TouchEnabled` e sem teclado.

---

## 8. Critérios de aceite (Gate RT2)

> Ajuste os nomes dos itens ao checklist oficial do seu Gate RT2.

- [ ] Todos os arquivos com `--!strict` passam na Script Analysis do Studio (ou `luau-lsp analyze`) **sem warnings**, sem `any`.
- [ ] Varredura de caracteres: nenhum code point em **U+2600–27BF** no repositório (comando na §10).
- [ ] `CardTyping.dominant` passa na tabela de testes da §2.
- [ ] `SubtypeArtCatalog120.validate()` retorna lista vazia no Command Bar.
- [ ] Visual: cada nível +0..+5 bate com `mock_forge_levels.png` (história/storybook por nível).
- [ ] Trocar o nível ao vivo (0→5→0) não deixa instâncias órfãs: `PixelClock.activeCount()` volta ao valor inicial.
- [ ] Whiteout aparece **pelo menos 1 quadro** e some em ≤ 50 ms; desligado com "Reduzir flashes".
- [ ] Nenhuma `ImageLabel` de arte sem `ResampleMode = Pixelated`; nenhum `UIScale` fracionado.
- [ ] Em celular de entrada: mão com 5 cartas +5 em HIGH mantém 60 FPS no MicroProfiler (frame de UI < 2 ms).

---

## 9. Adaptador `CardTokens` (contrato assumido com `DesignTokens` / `HudView`)

`CardTokens.luau` é o **único** arquivo que conhece `DesignTokens`. Ele lê os nomes abaixo e, se algum não existir, usa o fallback e emite `warn` uma vez.

| Token lógico | Uso | Fallback |
|---|---|---|
| `card.bg` | fundo da carta | `#1E1E24` |
| `card.iron` | borda +0 | `#2C2E35` |
| `forge.uncommon` | borda +1/+2 | `#4DD0E1` |
| `forge.epic` | gradiente +3 | `#B388FF` |
| `forge.mythic` | borda +4 | `#E5A93C` |
| `forge.relic` | eco/acentos +5 | `#A02F3C` |
| `text.primary` | título | `#F4EEDD` |
| `text.muted` | regra | `#AC9978` |
| `type.ATQ/GRD/BUF/DEB` | chip do tipo | ver §2 |
| `font.title` / `font.body` | fontes | `Enum.Font.Arcade` / `Enum.Font.Arimo` |

**`HudView.panel`:**
- O `CardView` não depende do `HudView`. Ele é um filho comum: `HudView.panel(scope, { ..., [Children] = { CardView(scope, props) } })`.
- O `HudView` só precisa fornecer `overlayParent` (camada de topo) para o whiteout.
- Se o `HudView.panel` exigir props específicas, adapte na tela que monta a mão, **não** no `CardView`.

---

## 10. Comandos úteis

```bash
# regenerar dados e arte dos subtipos (Python 3 + Pillow + numpy)
python pipeline/dark_altar/build_subtypes.py
# regenerar ornamentos da forja, máscaras e mockup
python pipeline/dark_altar/build_forge.py
# varredura anti-emoji (deve imprimir 0)
python -c "import pathlib;print(sum(1 for p in pathlib.Path('src').rglob('*.luau') for ch in p.read_text(encoding='utf-8') if 0x2600<=ord(ch)<=0x27BF))"
```

## 11. Arquivos entregues nesta etapa

| Arquivo | O que é |
|---|---|
| `src/shared/Config/SubtypeArtCatalog120.luau` | 120 entradas tipadas + API (`get`, `getOrDefault`, `byFamily`, `resolveColors`, `validate`) |
| `src/shared/Config/SubtypeArtAtlas120.luau` | offsets do atlas (modo ATLAS) |
| `src/shared/Config/ForgeOrnamentAtlas.luau` | retângulos dos ornamentos, `SLICE_1PX/2PX`, `apply()` |
| `src/shared/Pixel/*.luau` | `PixelClock`, `SpriteAnimator`, `PixelScale`, `FlipbookVFX` |
| `art/dark-altar/subtypes/SubtypeArtAtlas120.png` | atlas 1024×512 para upload |
| `art/dark-altar/forge/ForgeOrnamentAtlas.png` | ornamentos +0..+5 |
| `art/dark-altar/forge/ShapeMaskAtlas.png`, `EtchingAtlas.png` | máscaras brancas do modo PROCEDURAL |
| `art/dark-altar/forge/mock_forge_levels.png` | referência visual dos 6 níveis |
| `src/shared/Dev/ForgePreviewBuilder.luau` | ferramenta: monta os 6 níveis no Studio a partir dos atlas (`require(...).build()` no Command Bar ou via MCP) para conferir antes do Fusion |
| `src/shared/Config/SubtypeArtAtlas120HiFi.luau` + `art/dark-altar/subtypes/SubtypeArtAtlas120_x4_p1..p8.png` | variante ×4 para mobile (8 páginas de 1024², `apply(label, id)`); use só se a compressão estragar a cor no aparelho |
| `art/dark-altar/editions/*` | editions estilo Balatro (foil/holo/polychrome/negative) para a carta ampliada/coleção |

**Próximos arquivos a criar** (pelo Claude Code, seguindo esta spec): `CardTypes.luau`, `CardTyping.luau`, `CardTokens.luau`, `SubtypeArtView.luau`, `CardForgeOrnaments.luau`, `CardView.luau` e uma story por nível.
