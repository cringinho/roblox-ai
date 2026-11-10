--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome Animador
-- CLIENTE. Toca os clipes assados pela fabrica (modulos Clipes_<Id>) escrevendo Motor6D.Transform.
-- Uma conexao so para todas as criaturas. O servidor so publica o atributo "Estado" no modelo.
-- Motor6D.Transform nao replica e deve ser escrito em RunService.PreSimulation (fonte: documentacao do Motor6D).
-- Nao testado no Studio: confira no piloto.

local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Config = require(script.Parent:WaitForChild("Config"))

local Animador = {}
local ativos = {} -- [Model] = estado
local conexao: RBXScriptConnection? = nil

local APELIDOS = { Ocioso = "Parado", Passo = "Andar", Mover = "Andar" }

-- quaternion (x, y, z, w) -> CFrame, com interpolacao simples entre dois quadros
local function amostrar(trilha, i0: number, i1: number, a: number, centro: Vector3?): CFrame
	local x, y, z = 0, 0, 0
	local T = trilha.T
	if T then
		local b0, b1 = i0 * 3, i1 * 3
		x = T[b0 + 1] + (T[b1 + 1] - T[b0 + 1]) * a
		y = T[b0 + 2] + (T[b1 + 2] - T[b0 + 2]) * a
		z = T[b0 + 3] + (T[b1 + 3] - T[b0 + 3]) * a
	end
	local R = trilha.R
	if R then
		local b0, b1 = i0 * 4, i1 * 4
		local qx0, qy0, qz0, qw0 = R[b0 + 1], R[b0 + 2], R[b0 + 3], R[b0 + 4]
		local qx1, qy1, qz1, qw1 = R[b1 + 1], R[b1 + 2], R[b1 + 3], R[b1 + 4]
		if qx0 * qx1 + qy0 * qy1 + qz0 * qz1 + qw0 * qw1 < 0 then
			qx1, qy1, qz1, qw1 = -qx1, -qy1, -qz1, -qw1
		end
		return CFrame.new(x, y, z, qx0 + (qx1 - qx0) * a, qy0 + (qy1 - qy0) * a, qz0 + (qz1 - qz0) * a, qw0 + (qw1 - qw0) * a)
	end
	return CFrame.new(x, y, z)
end

local function passo(dtQuadro: number)
	local cam = Workspace.CurrentCamera
	local olho = if cam then cam.CFrame.Position else Vector3.zero
	for modelo, e in pairs(ativos) do
		local dt = dtQuadro
		if not modelo.Parent then
			ativos[modelo] = nil
			continue
		end
		if e.congelado > 0 then
			e.congelado -= dt
			continue
		end
		local raiz = e.rig.Raiz
		local dist = if raiz then (raiz.Position - olho).Magnitude else 0
		if dist > Config.LOD_LONGE then
			continue
		end
		e.saltar = not e.saltar
		if dist > Config.LOD_PERTO and e.saltar then
			e.acumulado += dt
			continue
		end
		dt += e.acumulado
		e.acumulado = 0
		local clipe = e.clipe
		if not clipe then
			continue
		end
		-- fase por distancia: clipes de locomocao andam na velocidade real do modelo
		local vel = e.velocidade
		if clipe.VelRaiz > 0 then
			local v = modelo:GetAttribute("Velocidade")
			if typeof(v) == "number" and v > 0 then
				vel = v / clipe.VelRaiz
			end
		end
		local antes = e.t
		e.t += dt * vel
		local dur = clipe.Duracao
		if clipe.Laco then
			e.t %= dur
		elseif e.t >= dur then
			e.t = dur
			if e.aoTerminar then
				local f = e.aoTerminar
				e.aoTerminar = nil
				task.spawn(f)
			end
		end
		-- marcadores: uma vez por passagem
		for _, m in ipairs(clipe.Marcadores) do
			local tm = m[2]
			if (antes < tm and e.t >= tm) or (clipe.Laco and e.t < antes and (tm > antes or tm <= e.t)) then
				e.marcador:Fire(m[1], e.nome)
			end
		end
		local n = clipe.N
		local f = e.t * 30
		local i0 = math.floor(f)
		local a = f - i0
		local i1 = i0 + 1
		if clipe.Laco then
			i0 %= n
			i1 %= n
		else
			i0 = math.min(i0, n - 1)
			i1 = math.min(i1, n - 1)
		end
		e.mistura = math.min(1, e.mistura + dt / Config.TRANSICAO)
		local k = e.mistura
		for nome, motor in pairs(e.rig.Juntas) do
			local trilha = clipe.Trilhas[nome]
			local alvo = if trilha then amostrar(trilha, i0, i1, a) else CFrame.identity
			if k < 1 then
				local de = e.de[nome] or CFrame.identity
				alvo = de:Lerp(alvo, k * k * (3 - 2 * k))
			end
			motor.Transform = alvo
			e.atual[nome] = alvo
		end
	end
end

function Animador.registrar(rig, clipes)
	if not rig or not clipes then
		return
	end
	local marcador = Instance.new("BindableEvent")
	local e = {
		rig = rig, clipes = clipes.Clipes, clipe = nil, nome = "", t = 0, velocidade = 1, mistura = 1,
		de = {}, atual = {}, congelado = 0, saltar = false, acumulado = 0, marcador = marcador, aoTerminar = nil,
	}
	ativos[rig.Modelo] = e
	if not conexao then
		conexao = RunService.PreSimulation:Connect(passo)
	end
	-- o servidor manda o estado por atributo; o cliente troca de clipe sozinho
	local modelo = rig.Modelo
	local function aplicar()
		local estado = modelo:GetAttribute("Estado")
		if typeof(estado) == "string" then
			Animador.tocar(rig, estado)
		end
	end
	e.sinal = modelo:GetAttributeChangedSignal("Estado"):Connect(aplicar)
	modelo.Destroying:Connect(function()
		Animador.remover(rig)
	end)
	if modelo:GetAttribute("Estado") then
		aplicar()
	else
		Animador.tocar(rig, "Parado")
	end
	return marcador.Event
end

function Animador.tocar(rig, nome: string, opcoes)
	local e = ativos[rig.Modelo]
	if not e then
		return false
	end
	nome = APELIDOS[nome] or nome
	local clipe = e.clipes[nome]
	if not clipe then
		warn(("[Fabrica.Animador] %s nao tem o clipe '%s'."):format(rig.Modelo.Name, nome))
		return false
	end
	if e.clipe == clipe and clipe.Laco then
		return true
	end
	for osso, cf in pairs(e.atual) do
		e.de[osso] = cf
	end
	e.clipe, e.nome, e.t, e.mistura = clipe, nome, 0, 0
	e.velocidade = (opcoes and opcoes.velocidade) or 1
	e.aoTerminar = opcoes and opcoes.aoTerminar or nil
	return true
end

function Animador.congelar(rig, segundos: number) -- hit-stop
	local e = ativos[rig.Modelo]
	if e then
		e.congelado = segundos
	end
end

function Animador.remover(rig)
	local e = ativos[rig.Modelo]
	if e then
		if e.sinal then
			e.sinal:Disconnect()
		end
		e.marcador:Destroy()
		ativos[rig.Modelo] = nil
	end
	if next(ativos) == nil and conexao then
		conexao:Disconnect()
		conexao = nil
	end
end

return Animador
