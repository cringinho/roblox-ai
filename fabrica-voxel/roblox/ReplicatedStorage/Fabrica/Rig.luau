--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome Rig
-- Monta as juntas (Motor6D) de um modelo da Fabrica de Voxel a partir do modulo Dados_<Id>.
-- Funciona com MeshParts importados do modelo.glb (uma peca = um MeshPart com o mesmo nome) e com
-- modelos montados por ConstrutorParts. Idempotente: pode rodar duas vezes sem duplicar nada.
-- Nao testado no Studio: confira no piloto.

local Rig = {}

local function v3(t: { number }): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

-- Acha os BaseParts do modelo pelo nome (o importador pode aninhar em Models).
local function indexar(modelo: Model): { [string]: BasePart }
	local mapa = {}
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("BasePart") and mapa[d.Name] == nil then
			mapa[d.Name] = d
		end
	end
	return mapa
end

-- CFrame que leva o espaco do modelo (repouso, da fabrica) para o mundo.
local function origemDoModelo(modelo: Model, dados, partes): CFrame?
	local giro = CFrame.Angles(0, math.rad(modelo:GetAttribute("GiroY") or 0), 0)
	for _, peca in ipairs(dados.Pecas) do
		local p = partes[peca.Nome]
		if p then
			-- o Roblox centraliza cada MeshPart na caixa da malha: Centro (fabrica) -> Position (mundo)
			return CFrame.new(p.Position) * giro * CFrame.new(-v3(peca.Centro))
		end
	end
	return nil
end

function Rig.montar(modelo: Model, dados)
	local partes = indexar(modelo)
	local origem = origemDoModelo(modelo, dados, partes)
	if not origem then
		warn(("[Fabrica.Rig] %s: nenhuma peca de Dados_%s foi achada no modelo. As pecas precisam ter o nome exato (ex.: %s)."):format(
			modelo.Name, tostring(dados.Id), dados.Pecas[1] and dados.Pecas[1].Nome or "?"))
		return nil
	end
	-- 1) peca principal de cada osso; as outras pecas do mesmo osso sao soldadas nela
	local principal: { [string]: BasePart } = {}
	local porOsso: { [string]: { BasePart } } = {}
	for _, peca in ipairs(dados.Pecas) do
		local p = partes[peca.Nome]
		if p then
			porOsso[peca.Osso] = porOsso[peca.Osso] or {}
			table.insert(porOsso[peca.Osso], p)
			if peca.Nome == peca.Osso or principal[peca.Osso] == nil then
				principal[peca.Osso] = p
			end
			local brilho = partes[peca.Nome .. "_Brilho"]
			if brilho then
				brilho.Material = Enum.Material.Neon
				table.insert(porOsso[peca.Osso], brilho)
			end
		else
			warn(("[Fabrica.Rig] %s: peca '%s' esta nos dados mas nao no modelo."):format(modelo.Name, peca.Nome))
		end
	end
	-- 2) osso sem peca (Raiz, juntas vazias): cria uma Part invisivel no pivo
	for _, osso in ipairs(dados.Ossos) do
		if principal[osso.Nome] == nil then
			local p = modelo:FindFirstChild("Osso_" .. osso.Nome)
			if not p then
				p = Instance.new("Part")
				p.Name = "Osso_" .. osso.Nome
				p.Size = Vector3.new(0.2, 0.2, 0.2)
				p.Transparency = 1
				p.CanCollide = false
				p.CanQuery = false
				p.CanTouch = false
				p.Parent = modelo
			end
			(p :: BasePart).CFrame = origem * CFrame.new(v3(osso.Pivo))
			principal[osso.Nome] = p :: BasePart
			porOsso[osso.Nome] = porOsso[osso.Nome] or {}
		end
	end
	-- 3) juntas: C0 = pivo no espaco da mae, C1 = pivo no espaco da filha (repouso sem rotacao)
	local juntas: { [string]: Motor6D } = {}
	local raiz: BasePart? = nil
	for _, osso in ipairs(dados.Ossos) do
		local p1 = principal[osso.Nome]
		p1.CanCollide = false
		for _, extra in ipairs(porOsso[osso.Nome]) do
			if extra ~= p1 then
				local nomeSolda = "Solda_" .. extra.Name
				local solda = extra:FindFirstChild(nomeSolda)
				if not solda then
					solda = Instance.new("WeldConstraint")
					solda.Name = nomeSolda
					solda.Parent = extra
				end
				(solda :: WeldConstraint).Part0 = p1;
				(solda :: WeldConstraint).Part1 = extra
				extra.Anchored = false
				extra.Massless = true
				extra.CanCollide = false
			end
		end
		if osso.Pai == "" then
			raiz = p1
			p1.Anchored = true
		else
			local p0 = principal[osso.Pai]
			local pivo = origem * CFrame.new(v3(osso.Pivo))
			local m = p1:FindFirstChild("J_" .. osso.Nome)
			if not m then
				m = Instance.new("Motor6D")
				m.Name = "J_" .. osso.Nome
				m.Parent = p1
			end
			local motor = m :: Motor6D
			motor.Part0 = p0
			motor.Part1 = p1
			motor.C0 = p0.CFrame:ToObjectSpace(pivo)
			motor.C1 = p1.CFrame:ToObjectSpace(pivo)
			p1.Anchored = false
			p1.Massless = true
			juntas[osso.Nome] = motor
		end
	end
	-- 4) soquetes viram Attachments na peca do osso
	for _, s in ipairs(dados.Soquetes or {}) do
		local p = principal[s.Osso]
		if p then
			local a = p:FindFirstChild(s.Nome)
			if not a then
				a = Instance.new("Attachment")
				a.Name = s.Nome
				a.Parent = p
			end
			(a :: Attachment).WorldCFrame = origem * CFrame.new(v3(s.Pos))
		end
	end
	if raiz then
		modelo.PrimaryPart = raiz
	end
	modelo:SetAttribute("IdFabrica", dados.Id)
	modelo:SetAttribute("VersaoFabrica", dados.VersaoFabrica)
	return { Modelo = modelo, Juntas = juntas, Partes = principal, Raiz = raiz, Dados = dados }
end

-- No cliente: so le as juntas que o servidor ja criou.
function Rig.ler(modelo: Model, dados)
	local juntas, partes = {}, {}
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("Motor6D") and string.sub(d.Name, 1, 2) == "J_" then
			juntas[string.sub(d.Name, 3)] = d
			if d.Part1 then
				partes[string.sub(d.Name, 3)] = d.Part1
			end
		end
	end
	return { Modelo = modelo, Juntas = juntas, Partes = partes, Raiz = modelo.PrimaryPart, Dados = dados }
end

function Rig.soquete(rig, nome: string): Attachment?
	local a = rig.Modelo:FindFirstChild(nome, true)
	if a and a:IsA("Attachment") then
		return a
	end
	return nil
end

return Rig
