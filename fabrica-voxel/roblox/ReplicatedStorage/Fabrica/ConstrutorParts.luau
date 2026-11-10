--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome ConstrutorParts
-- Monta um modelo da Fabrica SEM importar malha: usa a tabela Caixas do modulo Dados_<Id>.
-- Bom para testar e para props; para muitos personagens na tela prefira o modelo.glb importado.
-- Nao testado no Studio: confira no piloto.

local Config = require(script.Parent:WaitForChild("Config"))

local ConstrutorParts = {}

function ConstrutorParts.construir(dados, onde: CFrame?): Model?
	if not dados.Caixas then
		warn(("[Fabrica.ConstrutorParts] Dados_%s nao tem a tabela Caixas."):format(tostring(dados.Id)))
		return nil
	end
	if (dados.TotalCaixas or 0) > Config.MAX_CAIXAS then
		warn(("[Fabrica.ConstrutorParts] %s tem %d caixas (teto %d). Importe o modelo.glb em vez de montar por Parts."):format(
			dados.Id, dados.TotalCaixas, Config.MAX_CAIXAS))
	end
	local base = onde or CFrame.new()
	local modelo = Instance.new("Model")
	modelo.Name = dados.Nome or dados.Id
	local feitas = 0
	for _, peca in ipairs(dados.Pecas) do
		local caixas = dados.Caixas[peca.Nome]
		if caixas then
			-- peca principal invisivel com o nome da peca: e nela que o Rig prende as juntas
			local principal = Instance.new("Part")
			principal.Name = peca.Nome
			principal.Size = Vector3.new(peca.Tamanho[1], peca.Tamanho[2], peca.Tamanho[3])
			principal.CFrame = base * CFrame.new(peca.Centro[1], peca.Centro[2], peca.Centro[3])
			principal.Transparency = 1
			principal.CanCollide = false
			principal.Anchored = true
			principal.Parent = modelo
			local pasta = Instance.new("Folder")
			pasta.Name = "Blocos_" .. peca.Nome
			pasta.Parent = modelo
			for _, c in ipairs(caixas) do
				local b = Instance.new("Part")
				b.Name = "b"
				b.Size = Vector3.new(c[4], c[5], c[6])
				b.CFrame = base * CFrame.new(c[1], c[2], c[3])
				b.Color = Color3.fromHex(c[7])
				b.Material = if c[8] == 1 then Enum.Material.Neon else Enum.Material.SmoothPlastic
				b.TopSurface = Enum.SurfaceType.Smooth
				b.BottomSurface = Enum.SurfaceType.Smooth
				b.CanCollide = false
				b.CanQuery = false
				b.CanTouch = false
				b.Massless = true
				b.Anchored = false
				b.CastShadow = c[8] ~= 1
				local solda = Instance.new("WeldConstraint")
				solda.Part0 = principal
				solda.Part1 = b
				solda.Parent = b
				b.Parent = pasta
				feitas += 1
				if feitas % 200 == 0 then
					task.wait() -- cede o quadro em modelos grandes
				end
			end
		end
	end
	return modelo
end

return ConstrutorParts
