--!strict
--[[
	ForgePreviewBuilder.luau
	Coloque em: ReplicatedStorage > Shared > Dev   (Rojo: src/shared/Dev/)
	Tipo: ModuleScript de FERRAMENTA (não vai para o jogo final)

	O que faz: monta no Studio uma prévia das 6 cartas da Forja (+0 a +5) e de uma família de
	artes de subtipo, usando os atlas gerados pelo PixelForge. Serve para você CONFERIR a arte
	no Studio antes de implementar o CardView em Fusion (a posição de cada ornamento é a mesma
	da spec e do mockup art/dark-altar/forge/mock_forge_levels.png).

	Como rodar (Command Bar do Studio, ou MCP execute_luau com datamodel_type = "Edit"):
	    require(game.ReplicatedStorage.Shared.Dev.ForgePreviewBuilder).build()
	Para limpar:
	    require(game.ReplicatedStorage.Shared.Dev.ForgePreviewBuilder).clear()

	Antes: faça upload dos atlas (assetType Image) e troque os "rbxassetid://0" em
	SubtypeArtAtlas120.luau e ForgeOrnamentAtlas.luau. Sem isso a prévia aparece só com as
	formas (Frames) e um aviso no Output.

	Fluxo:
	  build() -> ScreenGui "DarkAltarForgePreview" em StarterGui
	          -> 6 colunas (uma por nível) com UIScale inteiro (pixel nítido)
	          -> cada carta: corpo 72x104 + arte 64x64 + borda + ornamentos do nível
	          -> fileira de baixo: 12 artes da família escolhida
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")

local PREVIEW_NAME = "DarkAltarForgePreview"
local CARD_W, CARD_H = 72, 104
local SLOT_W, SLOT_H = 100, 140 -- carta + folga para ornamentos que saem da borda
local CARD_X, CARD_Y = 14, 22

-- ------------------------------------------------------------------ carregamento seguro
local function findModule(path: { string }): ModuleScript?
	local node: Instance? = ReplicatedStorage
	for _, name in path do
		if node == nil then
			return nil
		end
		node = node:FindFirstChild(name)
	end
	if node ~= nil and node:IsA("ModuleScript") then
		return node
	end
	return nil
end

type Sprite = { offset: Vector2, size: Vector2 }
type OrnamentAtlas = {
	IMAGE: string,
	get: (name: string) -> Sprite?,
	SLICE_1PX: Rect,
	SLICE_2PX: Rect,
}
type SubtypeAtlas = {
	IMAGE: string,
	CELL: number,
	offsetOf: (subtypeId: string) -> Vector2,
}

local function loadAtlases(): (OrnamentAtlas?, SubtypeAtlas?)
	local ornModule = findModule({ "Shared", "Config", "ForgeOrnamentAtlas" })
	local subModule = findModule({ "Shared", "Config", "SubtypeArtAtlas120" })
	local orn: OrnamentAtlas? = nil
	local sub: SubtypeAtlas? = nil
	if ornModule ~= nil then
		local ok, result = pcall(require, ornModule)
		if ok then
			orn = result :: OrnamentAtlas
		else
			warn("[ForgePreview] falha ao carregar ForgeOrnamentAtlas: " .. tostring(result))
		end
	end
	if subModule ~= nil then
		local ok, result = pcall(require, subModule)
		if ok then
			sub = result :: SubtypeAtlas
		else
			warn("[ForgePreview] falha ao carregar SubtypeArtAtlas120: " .. tostring(result))
		end
	end
	return orn, sub
end

-- ------------------------------------------------------------------ helpers de instância
local function frame(parent: Instance, name: string, x: number, y: number, w: number, h: number, color: Color3): Frame
	local f = Instance.new("Frame")
	f.Name = name
	f.BorderSizePixel = 0
	f.BackgroundColor3 = color
	f.Position = UDim2.fromOffset(x, y)
	f.Size = UDim2.fromOffset(w, h)
	f.Parent = parent
	return f
end

local function sprite(parent: Instance, orn: OrnamentAtlas?, name: string, x: number, y: number): ImageLabel?
	if orn == nil then
		return nil
	end
	local s = orn.get(name)
	if s == nil then
		warn("[ForgePreview] sprite inexistente: " .. name)
		return nil
	end
	local label = Instance.new("ImageLabel")
	label.Name = name
	label.BackgroundTransparency = 1
	label.Image = orn.IMAGE
	label.ResampleMode = Enum.ResamplerMode.Pixelated
	label.ImageRectOffset = s.offset
	label.ImageRectSize = s.size
	label.Size = UDim2.fromOffset(s.size.X, s.size.Y)
	label.Position = UDim2.fromOffset(x, y)
	label.Parent = parent
	return label
end

local function border(parent: Instance, orn: OrnamentAtlas?, thickness: number, color: Color3): ImageLabel?
	if orn == nil then
		return nil
	end
	local name = if thickness >= 2 then "border_2px" else "border_1px"
	local label = sprite(parent, orn, name, 0, 0)
	if label == nil then
		return nil
	end
	label.ScaleType = Enum.ScaleType.Slice
	label.SliceCenter = if thickness >= 2 then orn.SLICE_2PX else orn.SLICE_1PX
	label.Size = UDim2.fromOffset(CARD_W, CARD_H)
	label.ImageColor3 = color
	label.ZIndex = 5
	return label
end

local function text(parent: Instance, value: string, x: number, y: number, w: number, color: Color3): TextLabel
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Text = value
	t.Font = Enum.Font.Arcade
	t.TextSize = 8
	t.TextColor3 = color
	t.TextXAlignment = Enum.TextXAlignment.Left
	t.Position = UDim2.fromOffset(x, y)
	t.Size = UDim2.fromOffset(w, 9)
	t.ZIndex = 8
	t.Parent = parent
	return t
end

-- ------------------------------------------------------------------ cores da spec
local SLATE = Color3.fromHex("#1E1E24")
local IRON = Color3.fromHex("#2C2E35")
local CYAN = Color3.fromHex("#4DD0E1")
local VIOLET = Color3.fromHex("#B388FF")
local AMBER = Color3.fromHex("#E5A93C")
local RELIC = Color3.fromHex("#A02F3C")
local BONE = Color3.fromHex("#CFC3A5")
local EMBER = Color3.fromHex("#F59341")

local LEVEL_BORDER: { [number]: { color: Color3, thickness: number } } = {
	[0] = { color = IRON, thickness = 1 },
	[1] = { color = CYAN, thickness = 2 },
	[2] = { color = CYAN, thickness = 2 },
	[3] = { color = VIOLET, thickness = 2 },
	[4] = { color = AMBER, thickness = 2 },
	[5] = { color = RELIC, thickness = 2 },
}

-- ------------------------------------------------------------------ uma carta
local function buildCard(slot: Frame, level: number, orn: OrnamentAtlas?, sub: SubtypeAtlas?, subtypeId: string)
	local card = frame(slot, "Card", CARD_X, CARD_Y, CARD_W, CARD_H, SLATE)
	card.ZIndex = 2

	local art = Instance.new("ImageLabel")
	art.Name = "SubtypeArt"
	art.BackgroundColor3 = Color3.fromHex("#130E25")
	art.BorderSizePixel = 0
	art.Position = UDim2.fromOffset(4, 14)
	art.Size = UDim2.fromOffset(64, 64)
	art.ZIndex = 3
	if sub ~= nil then
		art.Image = sub.IMAGE
		art.ResampleMode = Enum.ResamplerMode.Pixelated
		art.ImageRectSize = Vector2.new(sub.CELL, sub.CELL)
		art.ImageRectOffset = sub.offsetOf(subtypeId)
	end
	art.Parent = card

	text(card, "GOLPE", 20, 4, 48, BONE)
	text(card, "[ATQ]", 5, 84, 40, EMBER)
	text(card, "6", CARD_W - 11, 84, 8, BONE)

	local style = LEVEL_BORDER[level] or LEVEL_BORDER[0]
	border(card, orn, style.thickness, style.color)

	if level >= 4 then
		local foil = sprite(card, orn, "foil_tile", 4, 14)
		if foil ~= nil then
			foil.ScaleType = Enum.ScaleType.Tile
			foil.TileSize = UDim2.fromOffset(32, 32)
			foil.Size = UDim2.fromOffset(64, 64)
			foil.ImageTransparency = 0.72
			foil.ZIndex = 4
		end
	end
	if level >= 5 then
		local relic = sprite(card, orn, "relic_frame", 0, 0)
		if relic ~= nil then
			relic.ZIndex = 6
		end
	end

	-- ornamentos que saem da carta ficam no slot (sem recorte)
	if level >= 1 then
		sprite(slot, orn, "corner_tl", CARD_X - 2, CARD_Y - 2)
		sprite(slot, orn, "corner_tr", CARD_X + CARD_W - 11, CARD_Y - 2)
		sprite(slot, orn, "corner_bl", CARD_X - 2, CARD_Y + CARD_H - 11)
		sprite(slot, orn, "corner_br", CARD_X + CARD_W - 11, CARD_Y + CARD_H - 11)
	end
	if level >= 2 then
		sprite(slot, orn, "arch_top", CARD_X + math.floor((CARD_W - 41) / 2), CARD_Y - 18 + 4)
		sprite(slot, orn, "rune_seal", CARD_X + math.floor((CARD_W - 15) / 2), CARD_Y + CARD_H - 8)
	end
	if level >= 3 then
		sprite(slot, orn, "filigree_l", CARD_X - 9 + 3, CARD_Y + 20)
		sprite(slot, orn, "filigree_r", CARD_X + CARD_W - 3, CARD_Y + 20)
	end
	if level >= 4 then
		sprite(slot, orn, "crown_triple", CARD_X + math.floor((CARD_W - 33) / 2), CARD_Y - 19 - 8)
	end
	for _, child in slot:GetChildren() do
		if child:IsA("GuiObject") and child ~= card then
			child.ZIndex = 9
		end
	end
end

-- ------------------------------------------------------------------ API
local ForgePreviewBuilder = {}

function ForgePreviewBuilder.clear()
	local old = StarterGui:FindFirstChild(PREVIEW_NAME)
	if old ~= nil then
		old:Destroy()
	end
end

export type BuildOptions = {
	scale: number?, -- fator inteiro (padrão 3)
	subtypeId: string?, -- arte das cartas (padrão "Fogo")
	familyIds: { string }?, -- fileira de baixo (padrão: família Vermelho)
}

function ForgePreviewBuilder.build(options: BuildOptions?): ScreenGui
	ForgePreviewBuilder.clear()
	local opts: BuildOptions = options or {}
	local k = math.max(1, math.floor(opts.scale or 3))
	local subtypeId = opts.subtypeId or "Fogo"
	local family = opts.familyIds
		or { "Fogo", "Lava", "Dragonoide", "Bomba", "Forja", "Demonio", "Inferno", "Solar", "Destruicao", "Supernova", "Dragao" }

	local orn, sub = loadAtlases()
	if orn == nil or orn.IMAGE == "rbxassetid://0" then
		warn("[ForgePreview] ForgeOrnamentAtlas sem ID de imagem: faça o upload e troque IMAGE")
	end
	if sub == nil or sub.IMAGE == "rbxassetid://0" then
		warn("[ForgePreview] SubtypeArtAtlas120 sem ID de imagem: faça o upload e troque IMAGE")
	end

	local gui = Instance.new("ScreenGui")
	gui.Name = PREVIEW_NAME
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

	local cellStep = 68
	local rootW = math.max(SLOT_W * 6, 8 + #family * cellStep)
	local root = frame(gui, "Root", 8, 8, rootW, SLOT_H + 84, Color3.fromHex("#0E0B14"))
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = k -- inteiro: pixel nítido
	uiScale.Parent = root

	for level = 0, 5 do
		local slot = frame(root, "Level" .. level, level * SLOT_W, 0, SLOT_W, SLOT_H, Color3.fromHex("#0E0B14"))
		slot.BackgroundTransparency = 1
		buildCard(slot, level, orn, sub, subtypeId)
		text(slot, "+" .. level, 4, 2, 30, BONE)
	end

	for i, id in family do
		local cell = Instance.new("ImageLabel")
		cell.Name = id
		cell.BackgroundColor3 = SLATE
		cell.BorderSizePixel = 0
		cell.Position = UDim2.fromOffset(4 + (i - 1) * cellStep, SLOT_H + 12)
		cell.Size = UDim2.fromOffset(64, 64) -- tamanho nativo da arte: nunca reduza pixel art
		if sub ~= nil then
			cell.Image = sub.IMAGE
			cell.ResampleMode = Enum.ResamplerMode.Pixelated
			cell.ImageRectSize = Vector2.new(sub.CELL, sub.CELL)
			cell.ImageRectOffset = sub.offsetOf(id)
		end
		cell.Parent = root
	end

	gui.Parent = StarterGui
	print(`[ForgePreview] prévia criada em StarterGui.{PREVIEW_NAME} (escala {k}x)`)
	return gui
end

return table.freeze(ForgePreviewBuilder)
