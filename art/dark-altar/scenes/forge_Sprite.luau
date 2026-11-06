--!strict
-- Gerado pelo PixelForge. Animacao: forge
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
	name = "forge",
	image = "rbxassetid://0",
	loop = true,
	pivotX = 160,
	pivotY = 90,
	frames = {
		{ x = 1, y = 1, w = 320, h = 180, ms = 100 },
		{ x = 323, y = 1, w = 320, h = 180, ms = 100 },
		{ x = 1, y = 183, w = 320, h = 180, ms = 100 },
		{ x = 323, y = 183, w = 320, h = 180, ms = 100 },
		{ x = 1, y = 365, w = 320, h = 180, ms = 100 },
		{ x = 323, y = 365, w = 320, h = 180, ms = 100 },
	},
}

return table.freeze(data)
