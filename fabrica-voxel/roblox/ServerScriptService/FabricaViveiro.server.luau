--!nonstrict
-- Coloque este Script em ServerScriptService, com o nome FabricaViveiro
-- SERVIDOR, demonstracao. Monta no Workspace uma fileira com todo modelo que tiver Dados_<Id> em
-- ReplicatedStorage > Fabrica > Dados e troca o atributo Estado para voce ver os clipes.
-- Usa o modelo importado (Workspace ou ServerStorage > FabricaModelos, com o nome igual ao Id) se existir;
-- senao monta por Parts. Apague este script quando nao precisar mais da demonstracao.
-- Nao testado no Studio: confira no piloto.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local Workspace = game:GetService("Workspace")

local pasta = ReplicatedStorage:WaitForChild("Fabrica", 15)
if not pasta then
	warn("[FabricaViveiro] nao achei ReplicatedStorage.Fabrica. Rode o instalador do pacote FabricaVoxel primeiro.")
	return
end
local Rig = require(pasta:WaitForChild("Rig"))
local ConstrutorParts = require(pasta:WaitForChild("ConstrutorParts"))
local Catalogo = require(pasta:WaitForChild("Catalogo"))

local viveiro = Workspace:FindFirstChild("FabricaViveiro")
if viveiro then
	viveiro:Destroy()
end
viveiro = Instance.new("Folder")
viveiro.Name = "FabricaViveiro"
viveiro.Parent = Workspace

local modelosImportados = ServerStorage:FindFirstChild("FabricaModelos")
local x = 0
for _, id in ipairs(Catalogo.ids()) do
	local dados = Catalogo.dados(id)
	local clipes = Catalogo.clipes(id)
	if dados then
		local onde = CFrame.new(x, 0.5, 60)
		local modelo: Model? = nil
		local importado = modelosImportados and modelosImportados:FindFirstChild(id)
		if importado and importado:IsA("Model") then
			modelo = importado:Clone()
			if modelo then
				modelo:PivotTo(onde)
			end
		else
			local ok, m = pcall(ConstrutorParts.construir, dados, onde)
			if ok then
				modelo = m
			else
				warn(("[FabricaViveiro] nao consegui montar %s: %s"):format(id, tostring(m)))
			end
		end
		if modelo then
			modelo.Parent = viveiro
			local ok, erro = pcall(Rig.montar, modelo, dados)
			if not ok then
				warn(("[FabricaViveiro] rig de %s falhou: %s"):format(id, tostring(erro)))
			end
			-- alterna os clipes para a demonstracao
			if clipes then
				local nomes = {}
				for nome in pairs(clipes.Clipes) do
					table.insert(nomes, nome)
				end
				table.sort(nomes)
				task.spawn(function()
					local i = 0
					while modelo.Parent do
						i = i % #nomes + 1
						modelo:SetAttribute("Estado", nomes[i])
						task.wait(math.max(2.5, clipes.Clipes[nomes[i]].Duracao + 0.6))
					end
				end)
			end
			x += 8
		end
	end
end
