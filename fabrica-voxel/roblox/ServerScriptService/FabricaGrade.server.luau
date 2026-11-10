--!nonstrict
-- Coloque este Script em ServerScriptService, com o nome FabricaGrade
-- SERVIDOR. Dono da verdade do movimento em grade: valida cada pedido de passo (4 direcoes, uma casa por
-- vez, cadencia minima) e publica os atributos que os clientes desenham. Cria o que faltar.
-- Nao testado no Studio: confira no piloto.

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local pastaFabrica = ReplicatedStorage:FindFirstChild("Fabrica")
if not pastaFabrica then
	pastaFabrica = Instance.new("Folder")
	pastaFabrica.Name = "Fabrica"
	pastaFabrica.Parent = ReplicatedStorage
end
local remotos = pastaFabrica:FindFirstChild("Remotos")
if not remotos then
	remotos = Instance.new("Folder")
	remotos.Name = "Remotos"
	remotos.Parent = pastaFabrica
end
local pedir = remotos:FindFirstChild("PedirPasso")
if not pedir then
	pedir = Instance.new("RemoteEvent")
	pedir.Name = "PedirPasso"
	pedir.Parent = remotos
end

local okConfig, Config = pcall(function()
	return require(pastaFabrica:WaitForChild("Config", 10))
end)
local LADRILHO = (okConfig and Config and Config.LADRILHO) or 4
local DURACAO = (okConfig and Config and Config.SEGUNDOS_POR_LADRILHO) or 0.4444

local ocupado: { [Player]: number } = {}

-- Passabilidade plugavel: por padrao bloqueia o que tiver a tag "Bloqueia" na casa de destino.
local function casaLivre(destino: Vector3): boolean
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = CollectionService:GetTagged("Bloqueia")
	local achados = Workspace:GetPartBoundsInBox(CFrame.new(destino + Vector3.new(0, 2, 0)), Vector3.new(LADRILHO - 0.5, 3, LADRILHO - 0.5), params)
	return #achados == 0
end

local function unitaria(d: any): Vector3?
	if typeof(d) ~= "Vector3" then
		return nil
	end
	local x, z = math.round(d.X), math.round(d.Z)
	if math.abs(x) + math.abs(z) ~= 1 then
		return nil -- so as 4 direcoes
	end
	return Vector3.new(x, 0, z)
end

(pedir :: RemoteEvent).OnServerEvent:Connect(function(jogador: Player, direcao: any)
	local d = unitaria(direcao)
	local modelo = jogador.Character
	if not d or not modelo or not modelo.PrimaryPart then
		return
	end
	if jogador:GetAttribute("Modo") == "Dungeon" then
		return
	end
	local agora = Workspace:GetServerTimeNow()
	if (ocupado[jogador] or 0) > agora then
		return -- ainda esta no passo anterior
	end
	local de = modelo:GetAttribute("PassoPara")
	if typeof(de) ~= "Vector3" then
		local p = modelo:GetPivot().Position
		de = Vector3.new(math.round(p.X / LADRILHO) * LADRILHO, p.Y, math.round(p.Z / LADRILHO) * LADRILHO)
	end
	local para = (de :: Vector3) + d * LADRILHO
	local rumo = if d.Z < 0 then 0 elseif d.X > 0 then 90 elseif d.Z > 0 then 180 else 270
	modelo:SetAttribute("Rumo", rumo)
	if not casaLivre(para) then
		return
	end
	ocupado[jogador] = agora + DURACAO
	modelo:SetAttribute("PassoDe", de)
	modelo:SetAttribute("PassoPara", para)
	modelo:SetAttribute("PassoDur", DURACAO)
	modelo:SetAttribute("PassoT0", agora)
	modelo:SetAttribute("Velocidade", LADRILHO / DURACAO)
	modelo:SetAttribute("Estado", "Andar")
	CollectionService:AddTag(modelo, "FabricaGrade")
	task.delay(DURACAO + 0.05, function()
		if modelo.Parent and (ocupado[jogador] or 0) <= Workspace:GetServerTimeNow() then
			modelo:SetAttribute("Estado", "Parado")
		end
	end)
end)

Players.PlayerRemoving:Connect(function(jogador)
	ocupado[jogador] = nil
end)
