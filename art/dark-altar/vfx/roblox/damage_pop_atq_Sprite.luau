--!strict
-- Gerado pelo PixelForge. Animacao: damage_pop_atq
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
	name = "damage_pop_atq",
	image = "rbxassetid://0",
	loop = false,
	pivotX = 13,
	pivotY = 14,
	frames = {
		{ x = 1, y = 1, w = 26, h = 28, ms = 33 },
		{ x = 29, y = 1, w = 26, h = 28, ms = 33 },
		{ x = 57, y = 1, w = 26, h = 28, ms = 50 },
		{ x = 1, y = 31, w = 26, h = 28, ms = 83 },
		{ x = 29, y = 31, w = 26, h = 28, ms = 100 },
		{ x = 57, y = 31, w = 26, h = 28, ms = 100 },
		{ x = 1, y = 61, w = 26, h = 28, ms = 83 },
		{ x = 29, y = 61, w = 26, h = 28, ms = 83 },
	},
}

return table.freeze(data)
