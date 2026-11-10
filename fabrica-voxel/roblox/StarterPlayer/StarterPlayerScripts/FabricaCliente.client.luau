--!nonstrict
-- Coloque este LocalScript em StarterPlayer > StarterPlayerScripts, com o nome FabricaCliente
-- CLIENTE. Liga tudo: anima todo modelo da fabrica que aparecer e troca camera/movimento pelo atributo
-- "Modo" do jogador ("Grade" ou "Dungeon"; o servidor e quem muda).
-- Nao testado no Studio: confira no piloto.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local pasta = ReplicatedStorage:WaitForChild("Fabrica", 15)
if not pasta then
	warn("[FabricaCliente] nao achei ReplicatedStorage.Fabrica.")
	return
end
local Rig = require(pasta:WaitForChild("Rig"))
local Animador = require(pasta:WaitForChild("Animador"))
local Catalogo = require(pasta:WaitForChild("Catalogo"))
local CameraJogo = require(pasta:WaitForChild("CameraJogo"))
local MovimentoGrade = require(pasta:WaitForChild("MovimentoGrade"))

local registrados: { [Instance]: boolean } = {}

-- anima qualquer modelo que tenha o atributo IdFabrica (posto por Rig.montar no servidor)
local function tentar(inst: Instance)
	if not inst:IsA("Model") or registrados[inst] then
		return
	end
	local id = inst:GetAttribute("IdFabrica")
	if typeof(id) ~= "string" then
		return
	end
	local dados, clipes = Catalogo.dados(id), Catalogo.clipes(id)
	if not dados or not clipes then
		return
	end
	registrados[inst] = true
	task.defer(function()
		local ok, rig = pcall(Rig.ler, inst, dados)
		if ok and rig then
			Animador.registrar(rig, clipes)
		end
	end)
	inst.Destroying:Once(function()
		registrados[inst] = nil
	end)
end

for _, d in ipairs(Workspace:GetDescendants()) do
	tentar(d)
end
Workspace.DescendantAdded:Connect(function(d)
	if d:IsA("Model") then
		task.defer(tentar, d)
		d:GetAttributeChangedSignal("IdFabrica"):Connect(function()
			tentar(d)
		end)
	end
end)

-- modo do jogador: Grade (padrao) ou Dungeon
local jogador = Players.LocalPlayer
local function aplicarModo()
	local m = jogador:GetAttribute("Modo")
	if m == "Dungeon" then
		MovimentoGrade.parar()
		CameraJogo.mergulhar()
	elseif m == "Grade" then
		CameraJogo.modoGrade()
		MovimentoGrade.iniciar()
	end
	-- sem atributo: nao mexe na camera (bom para o viveiro de demonstracao)
end
jogador:GetAttributeChangedSignal("Modo"):Connect(aplicarModo)
aplicarModo()
