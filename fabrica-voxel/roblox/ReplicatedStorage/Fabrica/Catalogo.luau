--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome Catalogo
-- Acha os modulos gerados (Dados_<Id>, Clipes_<Id>) com require protegido e cache.
-- Nao testado no Studio: confira no piloto.

local Catalogo = {}
local cache = {}

local function idLuau(id: string): string
	local out = ""
	for parte in string.gmatch(id, "[^_%.]+") do
		out ..= string.upper(string.sub(parte, 1, 1)) .. string.sub(parte, 2)
	end
	return out
end

local function carregar(pasta: string, prefixo: string, id: string)
	local chave = prefixo .. id
	if cache[chave] ~= nil then
		return cache[chave] or nil
	end
	local dir = script.Parent:FindFirstChild(pasta)
	local modulo = dir and dir:FindFirstChild(prefixo .. idLuau(id))
	if not modulo or not modulo:IsA("ModuleScript") then
		cache[chave] = false
		return nil
	end
	local ok, dados = pcall(require, modulo)
	if not ok then
		warn(("[Fabrica.Catalogo] erro ao carregar %s: %s"):format(modulo.Name, tostring(dados)))
		cache[chave] = false
		return nil
	end
	cache[chave] = dados
	return dados
end

function Catalogo.dados(id: string)
	return carregar("Dados", "Dados_", id)
end

function Catalogo.clipes(id: string)
	return carregar("Clipes", "Clipes_", id)
end

function Catalogo.ids(): { string }
	local lista = {}
	local dir = script.Parent:FindFirstChild("Dados")
	if dir then
		for _, m in ipairs(dir:GetChildren()) do
			if m:IsA("ModuleScript") then
				local ok, d = pcall(require, m)
				if ok and type(d) == "table" and d.Id then
					table.insert(lista, d.Id)
				end
			end
		end
	end
	table.sort(lista)
	return lista
end

return Catalogo
