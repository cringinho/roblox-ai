--!strict
--[[
	FlipbookVFX.luau
	Coloque em: ReplicatedStorage > Shared > Pixel   (Rojo: src/shared/Pixel/)

	O que faz: configura um ParticleEmitter para tocar um flipbook gerado pelo
	PixelForge (arquivo <nome>_flipbook.json traz os valores). Tambem cria o
	emissor sozinho se ele nao existir (Instance.new) - menos montagem manual.

	Regras que este modulo aplica:
	  - textura quadrada 1024 com grade 2x2/4x4/8x8 (celulas ja ampliadas por fator inteiro)
	  - OneShot: Lifetime = quadros / fps (a particula morre no ultimo quadro)
	  - fogo/luz: LightEmission 1 ; fumaca/sangue: LightEmission 0
	  - pixel art nao "cresce": Size constante (sem curva) para nao virar mixel borrado
	  - FlipbookBlendFrames = false: o padrao (true, desde mar/2026) faz crossfade entre
	    quadros e destroi a troca seca da pixel art
	  - FlipbookFramerate maximo = 30 fps (limite do Roblox)
	  - OneShot ignora FlipbookFramerate: a velocidade vem de Lifetime / numero de quadros
]]

export type Layout = "Grid2x2" | "Grid4x4" | "Grid8x8"
export type Mode = "Loop" | "OneShot" | "PingPong" | "Random"
export type FlipbookSpec = {
	texture: string, -- rbxassetid://...
	layout: Layout,
	mode: Mode,
	fps: number,
	sizeStuds: number, -- tamanho da particula no mundo
	lightEmission: number?, -- 0..1
	rate: number?, -- particulas por segundo (0 = so Emit manual)
	speed: number?,
}

local LAYOUT_ENUM: { [Layout]: Enum.ParticleFlipbookLayout } = {
	Grid2x2 = Enum.ParticleFlipbookLayout.Grid2x2,
	Grid4x4 = Enum.ParticleFlipbookLayout.Grid4x4,
	Grid8x8 = Enum.ParticleFlipbookLayout.Grid8x8,
}
local MODE_ENUM: { [Mode]: Enum.ParticleFlipbookMode } = {
	Loop = Enum.ParticleFlipbookMode.Loop,
	OneShot = Enum.ParticleFlipbookMode.OneShot,
	PingPong = Enum.ParticleFlipbookMode.PingPong,
	Random = Enum.ParticleFlipbookMode.Random,
}
local FRAMES: { [Layout]: number } = { Grid2x2 = 4, Grid4x4 = 16, Grid8x8 = 64 }

local FlipbookVFX = {}

function FlipbookVFX.apply(emitter: ParticleEmitter, spec: FlipbookSpec)
	emitter.Texture = spec.texture
	emitter.FlipbookLayout = LAYOUT_ENUM[spec.layout]
	emitter.FlipbookMode = MODE_ENUM[spec.mode]
	local fps = math.clamp(spec.fps, 1, 30)
	emitter.FlipbookFramerate = NumberRange.new(fps)
	emitter.FlipbookBlendFrames = false
	emitter.FlipbookStartRandom = spec.mode == "Loop"
	emitter.Size = NumberSequence.new(spec.sizeStuds)
	emitter.LightEmission = spec.lightEmission or 0
	emitter.Orientation = Enum.ParticleOrientation.FacingCamera
	emitter.Rotation = NumberRange.new(0)
	emitter.RotSpeed = NumberRange.new(0)
	emitter.Speed = NumberRange.new(spec.speed or 0)
	emitter.Rate = spec.rate or 0
	if spec.mode == "OneShot" then
		local lifetime = FRAMES[spec.layout] / fps
		emitter.Lifetime = NumberRange.new(lifetime)
	end
end

-- Busca (ou cria) o emissor dentro de 'parent' e aplica o flipbook.
function FlipbookVFX.ensure(parent: Instance, name: string, spec: FlipbookSpec): ParticleEmitter
	local existing = parent:FindFirstChild(name)
	local emitter: ParticleEmitter
	if existing ~= nil and existing:IsA("ParticleEmitter") then
		emitter = existing
	else
		local rate = spec.rate or 0
		emitter = Instance.new("ParticleEmitter")
		emitter.Name = name
		emitter.Enabled = rate > 0
		emitter.Parent = parent
	end
	local ok, err = pcall(FlipbookVFX.apply, emitter, spec)
	if not ok then
		warn(`[FlipbookVFX] falha ao configurar {name}: {err}`)
	end
	return emitter
end

-- Dispara N particulas (efeitos de impacto one-shot).
function FlipbookVFX.burst(emitter: ParticleEmitter, count: number?)
	emitter:Emit(count or 1)
end

return table.freeze(FlipbookVFX)
