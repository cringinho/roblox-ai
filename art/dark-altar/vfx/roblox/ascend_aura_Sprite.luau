--!strict
-- Gerado pelo PixelForge. Animacao: ascend_aura
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
	name = "ascend_aura",
	image = "rbxassetid://0",
	loop = true,
	pivotX = 16,
	pivotY = 24,
	frames = {
		{ x = 1, y = 1, w = 32, h = 48, ms = 83 },
		{ x = 35, y = 1, w = 32, h = 48, ms = 83 },
		{ x = 69, y = 1, w = 32, h = 48, ms = 83 },
		{ x = 103, y = 1, w = 32, h = 48, ms = 83 },
		{ x = 1, y = 51, w = 32, h = 48, ms = 83 },
		{ x = 35, y = 51, w = 32, h = 48, ms = 83 },
		{ x = 69, y = 51, w = 32, h = 48, ms = 83 },
		{ x = 103, y = 51, w = 32, h = 48, ms = 83 },
	},
}

return table.freeze(data)
