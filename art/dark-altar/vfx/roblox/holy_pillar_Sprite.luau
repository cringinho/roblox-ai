--!strict
-- Gerado pelo PixelForge. Animacao: holy_pillar
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
	name = "holy_pillar",
	image = "rbxassetid://0",
	loop = true,
	pivotX = 12,
	pivotY = 32,
	frames = {
		{ x = 1, y = 1, w = 24, h = 64, ms = 83 },
		{ x = 27, y = 1, w = 24, h = 64, ms = 83 },
		{ x = 53, y = 1, w = 24, h = 64, ms = 83 },
		{ x = 79, y = 1, w = 24, h = 64, ms = 83 },
		{ x = 105, y = 1, w = 24, h = 64, ms = 83 },
		{ x = 1, y = 67, w = 24, h = 64, ms = 83 },
		{ x = 27, y = 67, w = 24, h = 64, ms = 83 },
		{ x = 53, y = 67, w = 24, h = 64, ms = 83 },
	},
}

return table.freeze(data)
