--!strict
--[[
	ForgeOrnamentAtlas.luau  (GERADO por pipeline/dark_altar/build_forge.py - nao edite a mao)
	Coloque em: ReplicatedStorage > Shared > Config
	Atlas: art/dark-altar/forge/ForgeOrnamentAtlas.png
	Use sempre com ResampleMode = Enum.ResamplerMode.Pixelated e tamanho = multiplo inteiro do sprite.
]]

export type Sprite = { offset: Vector2, size: Vector2 }

local ForgeOrnamentAtlas = {}

ForgeOrnamentAtlas.IMAGE = "rbxassetid://0" -- troque pelo ID apos o upload

local SPRITES: { [string]: Sprite } = {
	arch_top = { offset = Vector2.new(166, 1), size = Vector2.new(41, 18) },
	border_1px = { offset = Vector2.new(31, 107), size = Vector2.new(12, 12) },
	border_2px = { offset = Vector2.new(45, 107), size = Vector2.new(12, 12) },
	corner_bl = { offset = Vector2.new(1, 107), size = Vector2.new(13, 13) },
	corner_br = { offset = Vector2.new(16, 107), size = Vector2.new(13, 13) },
	corner_tl = { offset = Vector2.new(226, 1), size = Vector2.new(13, 13) },
	corner_tr = { offset = Vector2.new(241, 1), size = Vector2.new(13, 13) },
	crown_triple = { offset = Vector2.new(131, 1), size = Vector2.new(33, 19) },
	ember_0 = { offset = Vector2.new(80, 107), size = Vector2.new(3, 3) },
	ember_1 = { offset = Vector2.new(85, 107), size = Vector2.new(3, 3) },
	ember_2 = { offset = Vector2.new(90, 107), size = Vector2.new(3, 3) },
	filigree_l = { offset = Vector2.new(75, 1), size = Vector2.new(9, 64) },
	filigree_r = { offset = Vector2.new(86, 1), size = Vector2.new(9, 64) },
	foil_tile = { offset = Vector2.new(97, 1), size = Vector2.new(32, 32) },
	glyph_dagger = { offset = Vector2.new(66, 107), size = Vector2.new(5, 7) },
	glyph_diamond = { offset = Vector2.new(59, 107), size = Vector2.new(5, 7) },
	glyph_hollow = { offset = Vector2.new(73, 107), size = Vector2.new(5, 7) },
	relic_frame = { offset = Vector2.new(1, 1), size = Vector2.new(72, 104) },
	rune_seal = { offset = Vector2.new(209, 1), size = Vector2.new(15, 15) },
}

function ForgeOrnamentAtlas.get(name: string): Sprite?
	return SPRITES[name]
end

-- Aplica o sprite num ImageLabel. scale = fator inteiro (pixel art nunca usa escala fracionada).
function ForgeOrnamentAtlas.apply(label: ImageLabel, name: string, scale: number): boolean
	local sprite = SPRITES[name]
	if sprite == nil then
		warn(`[ForgeOrnamentAtlas] sprite inexistente: {name}`)
		return false
	end
	local k = math.max(1, math.floor(scale))
	label.Image = ForgeOrnamentAtlas.IMAGE
	label.ResampleMode = Enum.ResamplerMode.Pixelated
	label.ImageRectOffset = sprite.offset
	label.ImageRectSize = sprite.size
	label.Size = UDim2.fromOffset(sprite.size.X * k, sprite.size.Y * k)
	return true
end

-- SliceCenter das mascaras de borda (ScaleType = Slice, SliceScale = fator inteiro)
ForgeOrnamentAtlas.SLICE_1PX = Rect.new(3, 3, 9, 9)
ForgeOrnamentAtlas.SLICE_2PX = Rect.new(4, 4, 8, 8)

return table.freeze(ForgeOrnamentAtlas)
