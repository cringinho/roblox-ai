--!strict
-- Gerado pelo PixelForge. Animacao: blood_burst
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
	name = "blood_burst",
	image = "rbxassetid://0",
	loop = false,
	pivotX = 20,
	pivotY = 20,
	frames = {
		{ x = 1, y = 1, w = 40, h = 40, ms = 33 },
		{ x = 43, y = 1, w = 40, h = 40, ms = 50 },
		{ x = 85, y = 1, w = 40, h = 40, ms = 50 },
		{ x = 1, y = 43, w = 40, h = 40, ms = 50 },
		{ x = 43, y = 43, w = 40, h = 40, ms = 50 },
		{ x = 85, y = 43, w = 40, h = 40, ms = 67 },
		{ x = 1, y = 85, w = 40, h = 40, ms = 67 },
		{ x = 43, y = 85, w = 40, h = 40, ms = 67 },
	},
}

return table.freeze(data)
