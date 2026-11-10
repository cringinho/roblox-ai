--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome MovimentoGrade
-- CLIENTE. Fora das dungeons o mundo e uma grade de casas de 4 studs e so existe passo nas 4 direcoes.
-- O servidor decide o passo e publica atributos no modelo (PassoDe, PassoPara, PassoT0, PassoDur, Rumo).
-- Este modulo le a entrada, pede o passo e DESENHA o deslocamento de todo modelo que tenha esses atributos.
-- Nao testado no Studio: confira no piloto.

local CollectionService = game:GetService("CollectionService")
local ContextActionService = game:GetService("ContextActionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local MovimentoGrade = {}
local conexoes: { RBXScriptConnection } = {}
local direcao: Vector3? = nil
local ACAO = "FabricaPassoGrade"

local DIRECOES = {
	[Enum.KeyCode.W] = Vector3.new(0, 0, -1), [Enum.KeyCode.Up] = Vector3.new(0, 0, -1),
	[Enum.KeyCode.S] = Vector3.new(0, 0, 1), [Enum.KeyCode.Down] = Vector3.new(0, 0, 1),
	[Enum.KeyCode.A] = Vector3.new(-1, 0, 0), [Enum.KeyCode.Left] = Vector3.new(-1, 0, 0),
	[Enum.KeyCode.D] = Vector3.new(1, 0, 0), [Enum.KeyCode.Right] = Vector3.new(1, 0, 0),
}

-- curva do passo: sai devagar, anda, assenta
local function curva(u: number): number
	return u * u * u * (u * (u * 6 - 15) + 10)
end

local function desenhar()
	local agora = Workspace:GetServerTimeNow()
	for _, modelo in ipairs(CollectionService:GetTagged("FabricaGrade")) do
		if modelo:IsA("Model") and modelo.PrimaryPart then
			local de, para = modelo:GetAttribute("PassoDe"), modelo:GetAttribute("PassoPara")
			local t0, dur = modelo:GetAttribute("PassoT0"), modelo:GetAttribute("PassoDur")
			if typeof(de) == "Vector3" and typeof(para) == "Vector3" and typeof(t0) == "number" and typeof(dur) == "number" then
				local u = math.clamp((agora - t0) / math.max(dur, 0.01), 0, 1)
				local pos = (de :: Vector3):Lerp(para :: Vector3, curva(u))
				local rumo = math.rad(-(modelo:GetAttribute("Rumo") or 0))
				local alvo = CFrame.new(pos) * CFrame.Angles(0, rumo, 0)
				local atual = modelo:GetPivot()
				modelo:PivotTo(CFrame.new(pos) * atual.Rotation:Lerp(alvo.Rotation, 0.3))
			end
		end
	end
end

function MovimentoGrade.iniciar()
	MovimentoGrade.parar()
	local pasta = ReplicatedStorage:WaitForChild("Fabrica"):WaitForChild("Remotos", 10)
	local pedir = pasta and pasta:WaitForChild("PedirPasso", 10)
	if not pedir or not pedir:IsA("RemoteEvent") then
		warn("[Fabrica.MovimentoGrade] nao achei o RemoteEvent Fabrica/Remotos/PedirPasso; o script FabricaGrade do servidor esta rodando?")
		return
	end
	ContextActionService:BindAction(ACAO, function(_, estado, entrada)
		local d = DIRECOES[entrada.KeyCode]
		if d and estado == Enum.UserInputState.Begin then
			direcao = d
		elseif d and estado == Enum.UserInputState.End and direcao == d then
			direcao = nil
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.W, Enum.KeyCode.A, Enum.KeyCode.S, Enum.KeyCode.D, Enum.KeyCode.Up, Enum.KeyCode.Down, Enum.KeyCode.Left, Enum.KeyCode.Right)
	local espera = 0
	table.insert(conexoes, RunService.Heartbeat:Connect(function(dt)
		espera -= dt
		if direcao and espera <= 0 then
			espera = 0.1 -- o servidor e quem limita a cadencia de verdade
			(pedir :: RemoteEvent):FireServer(direcao)
		end
	end))
	table.insert(conexoes, RunService.RenderStepped:Connect(desenhar))
end

function MovimentoGrade.parar()
	pcall(function()
		ContextActionService:UnbindAction(ACAO)
	end)
	for _, c in ipairs(conexoes) do
		c:Disconnect()
	end
	table.clear(conexoes)
	direcao = nil
end

return MovimentoGrade
