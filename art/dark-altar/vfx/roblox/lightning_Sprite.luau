--!strict
-- Gerado pelo PixelForge. Animacao: lightning
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
	name = "lightning",
	image = "rbxassetid://0",
	loop = false,
	pivotX = 16,
	pivotY = 32,
	frames = {
		{ x = 1, y = 1, w = 32, h = 64, ms = 33 },
		{ x = 35, y = 1, w = 32, h = 64, ms = 50 },
		{ x = 69, y = 1, w = 32, h = 64, ms = 50 },
		{ x = 103, y = 1, w = 32, h = 64, ms = 33 },
		{ x = 1, y = 67, w = 32, h = 64, ms = 50 },
		{ x = 35, y = 67, w = 32, h = 64, ms = 33 },
		{ x = 69, y = 67, w = 32, h = 64, ms = 67 },
		{ x = 103, y = 67, w = 32, h = 64, ms = 67 },
	},
}

return table.freeze(data)
