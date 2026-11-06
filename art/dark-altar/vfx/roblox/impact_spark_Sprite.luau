--!strict
-- Gerado pelo PixelForge. Animacao: impact_spark
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
	name = "impact_spark",
	image = "rbxassetid://0",
	loop = false,
	pivotX = 16,
	pivotY = 16,
	frames = {
		{ x = 1, y = 1, w = 32, h = 32, ms = 67 },
		{ x = 35, y = 1, w = 32, h = 32, ms = 33 },
		{ x = 1, y = 35, w = 32, h = 32, ms = 50 },
		{ x = 35, y = 35, w = 32, h = 32, ms = 50 },
		{ x = 1, y = 69, w = 32, h = 32, ms = 67 },
		{ x = 35, y = 69, w = 32, h = 32, ms = 67 },
	},
}

return table.freeze(data)
