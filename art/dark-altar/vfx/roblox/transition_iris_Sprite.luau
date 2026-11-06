--!strict
-- Gerado pelo PixelForge. Animacao: transition_iris
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
	name = "transition_iris",
	image = "rbxassetid://0",
	loop = false,
	pivotX = 40,
	pivotY = 22,
	frames = {
		{ x = 1, y = 1, w = 80, h = 45, ms = 33 },
		{ x = 83, y = 1, w = 80, h = 45, ms = 33 },
		{ x = 165, y = 1, w = 80, h = 45, ms = 33 },
		{ x = 1, y = 48, w = 80, h = 45, ms = 33 },
		{ x = 83, y = 48, w = 80, h = 45, ms = 33 },
		{ x = 165, y = 48, w = 80, h = 45, ms = 33 },
		{ x = 1, y = 95, w = 80, h = 45, ms = 33 },
		{ x = 83, y = 95, w = 80, h = 45, ms = 33 },
		{ x = 165, y = 95, w = 80, h = 45, ms = 33 },
		{ x = 1, y = 142, w = 80, h = 45, ms = 33 },
		{ x = 83, y = 142, w = 80, h = 45, ms = 33 },
		{ x = 165, y = 142, w = 80, h = 45, ms = 33 },
		{ x = 1, y = 189, w = 80, h = 45, ms = 33 },
		{ x = 83, y = 189, w = 80, h = 45, ms = 33 },
	},
}

return table.freeze(data)
