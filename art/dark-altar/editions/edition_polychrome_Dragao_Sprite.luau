--!strict
-- Gerado pelo PixelForge. Animacao: edition_polychrome_Dragao
-- Coloque em ReplicatedStorage/Shared/Sprites/ e troque 'image' pelo ID enviado.
-- Uso: SpriteAnimator.play(imageLabel, require(este_modulo))

export type Frame = { x: number, y: number, w: number, h: number, ms: number }
export type SpriteData = {
	name: string,
	image: string,
	loop: boolean,
	pivotX: number,
	pivotY: number,
	frames: { Frame },
}

local data: SpriteData = {
	name = "edition_polychrome_Dragao",
	image = "rbxassetid://0",
	loop = true,
	pivotX = 32,
	pivotY = 32,
	frames = {
		{ x = 1, y = 1, w = 64, h = 64, ms = 100 },
		{ x = 67, y = 1, w = 64, h = 64, ms = 100 },
		{ x = 133, y = 1, w = 64, h = 64, ms = 100 },
		{ x = 1, y = 67, w = 64, h = 64, ms = 100 },
		{ x = 67, y = 67, w = 64, h = 64, ms = 100 },
		{ x = 133, y = 67, w = 64, h = 64, ms = 100 },
		{ x = 1, y = 133, w = 64, h = 64, ms = 100 },
		{ x = 67, y = 133, w = 64, h = 64, ms = 100 },
	},
}

return table.freeze(data)
