--!strict
--[[
	SpriteAnimator.luau
	Coloque em: ReplicatedStorage > Shared > Pixel   (Rojo: src/shared/Pixel/)
	Depende de: PixelClock (mesma pasta)

	O que faz: toca animacoes em pixel art dentro de ImageLabel/ImageButton usando
	o modulo gerado pelo PixelForge (<nome>_Sprite.luau). Respeita a duracao de
	CADA quadro (holds de impacto) - coisa que o ParticleEmitter nao faz.

	Fluxo:
	  play(label, data) -> aplica Image + ResampleMode Pixelated -> quadro 1
	    -> a cada quadro do relogio soma o tempo -> passou 'ms'? avanca o quadro
	    -> fim: loop volta ao 1; one-shot chama onFinished e para sozinho
	  play() devolve stop(): chame para interromper (ou coloque no scope do Fusion)
]]

local PixelClock = require(script.Parent:WaitForChild("PixelClock"))

export type Frame = { x: number, y: number, w: number, h: number, ms: number }
export type SpriteData = {
	name: string,
	image: string,
	loop: boolean,
	pivotX: number,
	pivotY: number,
	frames: { Frame },
}
export type PlayOptions = {
	speed: number?, -- 1 = normal; 2 = dobro da velocidade
	startFrame: number?,
	onFinished: (() -> ())?,
	hideOnFinish: boolean?,
}

local SpriteAnimator = {}

-- Mostra um quadro especifico (util para estados de botao feitos em sprite sheet).
function SpriteAnimator.setFrame(label: ImageLabel | ImageButton, data: SpriteData, index: number)
	local frame = data.frames[index]
	if frame == nil then
		warn(`[SpriteAnimator] {data.name}: quadro {index} inexistente`)
		return
	end
	label.ImageRectOffset = Vector2.new(frame.x, frame.y)
	label.ImageRectSize = Vector2.new(frame.w, frame.h)
end

-- Toca a animacao. Retorna stop().
function SpriteAnimator.play(label: ImageLabel | ImageButton, data: SpriteData, options: PlayOptions?): () -> ()
	local opts: PlayOptions = options or {}
	local frames = data.frames
	if #frames == 0 then
		warn(`[SpriteAnimator] {data.name}: sem quadros`)
		return function() end
	end
	label.Image = data.image
	label.ResampleMode = Enum.ResamplerMode.Pixelated

	local speed = math.max(0.01, opts.speed or 1)
	local index = math.clamp(opts.startFrame or 1, 1, #frames)
	local elapsedMs = 0
	SpriteAnimator.setFrame(label, data, index)

	local unsubscribe: (() -> ())? = nil
	local stopped = false

	local function stop()
		if stopped then
			return
		end
		stopped = true
		if unsubscribe ~= nil then
			unsubscribe()
			unsubscribe = nil
		end
	end

	unsubscribe = PixelClock.subscribe(function(_now: number, dt: number)
		if stopped then
			return
		end
		-- a label pode ter sido destruida por outro sistema: para com seguranca
		if label.Parent == nil then
			stop()
			return
		end
		elapsedMs += dt * 1000 * speed
		local advanced = false
		-- while: se o jogo travar, pula quadros em vez de atrasar a animacao
		-- math.max(1, ...) protege contra quadro com ms = 0 (loop infinito)
		while elapsedMs >= math.max(1, frames[index].ms) do
			elapsedMs -= math.max(1, frames[index].ms)
			index += 1
			advanced = true
			if index > #frames then
				if data.loop then
					index = 1
				else
					index = #frames
					stop()
					if opts.hideOnFinish then
						label.Visible = false
					end
					if opts.onFinished then
						-- defer: roda depois do quadro atual (evita reentrar no PixelClock)
						task.defer(opts.onFinished)
					end
					return
				end
			end
		end
		if advanced then
			SpriteAnimator.setFrame(label, data, index)
		end
	end)

	return stop
end

return table.freeze(SpriteAnimator)
