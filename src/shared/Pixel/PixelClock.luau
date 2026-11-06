--!strict
--[[
	PixelClock.luau
	Coloque em: ReplicatedStorage > Shared > Pixel   (Rojo: src/shared/Pixel/)
	Tipo: ModuleScript (usado SO no cliente: LocalScripts / componentes de UI)

	O que faz: UM unico evento de quadro para TODAS as animacoes de UI em pixel art
	(cartas, sprites, brasas, glifos orbitais...). Em vez de cada carta abrir sua
	propria conexao, todas "assinam" este relogio. Quando ninguem assina, a
	conexao e desligada sozinha (zero custo parado).

	Fluxo:
	  subscribe(fn) -> liga o relogio se estava parado -> fn(agora, dt) todo quadro
	  a funcao devolvida (unsubscribe) -> remove; se foi o ultimo, desliga o relogio
	  Assinaturas feitas DURANTE um quadro entram no quadro seguinte (seguro).

	Evento: RunService.PreRender = substituto oficial do RenderStepped (mesmo momento:
	antes de desenhar o quadro). Mantenha os callbacks LEVES: o render espera por eles.

	Uso com Fusion 0.3 (a limpeza do scope chama o unsubscribe):
	  table.insert(scope, PixelClock.subscribe(function(now, dt) ... end))
]]

local RunService = game:GetService("RunService")

export type Callback = (now: number, dt: number) -> ()

local subscribers: { [number]: Callback } = {}
local pending: { [number]: Callback } = {}
local nextId = 0
local activeCount = 0
local iterating = false
local connection: RBXScriptConnection? = nil

local PixelClock = {}

local function stopIfIdle()
	if activeCount <= 0 and connection ~= nil then
		connection:Disconnect()
		connection = nil
		activeCount = 0
	end
end

local function step(dt: number)
	local now = os.clock()
	iterating = true
	for id, callback in subscribers do
		-- pcall isola erros: um efeito quebrado nao derruba os outros
		local ok, err = pcall(callback, now, dt)
		if not ok then
			warn(`[PixelClock] callback {id} falhou e foi removido: {err}`)
			subscribers[id] = nil
			activeCount -= 1
		end
	end
	iterating = false
	-- novas assinaturas feitas durante o quadro entram agora (nunca durante a iteracao)
	for id, callback in pending do
		subscribers[id] = callback
	end
	table.clear(pending)
	stopIfIdle()
end

-- Assina o relogio. Retorna a funcao que cancela a assinatura (pode chamar varias vezes).
function PixelClock.subscribe(callback: Callback): () -> ()
	if not RunService:IsClient() then
		warn("[PixelClock] use apenas no cliente (LocalScript)")
		return function() end
	end
	nextId += 1
	local id = nextId
	if iterating then
		pending[id] = callback
	else
		subscribers[id] = callback
	end
	activeCount += 1
	if connection == nil then
		connection = RunService.PreRender:Connect(step)
	end
	local alive = true
	return function()
		if not alive then
			return
		end
		alive = false
		if subscribers[id] ~= nil then
			subscribers[id] = nil
			activeCount -= 1
		elseif pending[id] ~= nil then
			pending[id] = nil
			activeCount -= 1
		end
		if not iterating then
			stopIfIdle()
		end
	end
end

-- Quantas animacoes estao ativas (use em debug/perfil).
function PixelClock.activeCount(): number
	return activeCount
end

-- Arredonda uma posicao para a grade de pixels da arte (evita sub-pixel = "tremido").
function PixelClock.snap(value: number, pixelScale: number): number
	local k = math.max(1, pixelScale)
	return math.floor(value / k + 0.5) * k
end

return table.freeze(PixelClock)
