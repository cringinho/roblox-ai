"""Gera os scripts Luau da Myxilia a partir de saida/myxilia_rig.json."""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
rig = json.load(open(os.path.join(BASE, "saida", "myxilia_rig.json")))
f3 = lambda v: ", ".join("%.3f" % x for x in v)
pecas = rig["pecas"]
# ordem topologica
ordem, feito = [], set()
idx = {p["nome"]: p for p in pecas}
def visita(n):
    if n in feito:
        return
    if idx[n]["pai"]:
        visita(idx[n]["pai"])
    feito.add(n); ordem.append(idx[n])
for p in pecas:
    visita(p["nome"])
raiz = idx[rig["raiz"]]
linhas_rig = "\n".join('\t{"%s", "%s", %s, %s},' % (p["nome"], p["pai"], f3(p["pivo"]), f3(p["centro"])) for p in ordem)
linhas_fios = "\n".join('\t{"%s", "%s", %s, %s},' % (L["nome"], L["lado"], f3(L["ponta"]), f3(L["ancora"])) for L in rig["pernas"])
linhas_pecas = "\n".join('\t{"%s", "%s", %s},' % (p["nome"], p["pai"], f3(p["pivo"])) for p in ordem)
linhas_pernas = "\n".join('\t{"%s", "%s", %s, %s, %s, %s, %s, %s, %.3f, %.3f, %s},' % (
    L["nome"], L["lado"], "true" if L["grupo"] == "A" else "false", f3(L["quadril"]), f3(L["joelho"]), f3(L["tornozelo"]),
    f3(L["pe"]), f3(L["dir"]), L["Lf"], L["Lt"], f3(L["ponta"])) for L in rig["pernas"])
m = rig["marcha"]

MONTAR = '''-- Myxilia: montagem do rig (cole na barra de comando do Roblox Studio e aperte Enter)
-- Antes: importe myxilia_grade.glb (ou myxilia_susto.glb) pelo 3D Importer com unidade em studs,
-- sem girar o modelo, e renomeie o Model importado para "Myxilia".
-- O script liga as pecas com Motor6D nos pivos da forja, solda as malhas _Brilho em Neon
-- e cria os 8 fios (Beams) dos dedos do Titereiro ate os nos dos joelhos.
-- Gerado pela forja a partir de myxilia_rig.json. Nao testado no Studio: confira no piloto.
local NOME = "Myxilia"
local COR_FIO = Color3.fromHex("FF6B5B")

-- {nome, pai, pivo x,y,z, centro da malha x,y,z} em studs, na pose de repouso
local RIG = {
%s
}
-- {perna, lado, ponta do dedo x,y,z, ancora no joelho x,y,z}
local FIOS = {
%s
}

local modelo = workspace:FindFirstChild(NOME) :: Model
assert(modelo, "Importe o GLB e renomeie o Model para " .. NOME)
local partes: {[string]: BasePart} = {}
for _, d in modelo:GetDescendants() do
	if d:IsA("BasePart") then
		partes[d.Name] = d
	end
end
local raiz = partes[RIG[1][1]]
assert(raiz, "Nao achei a peca " .. RIG[1][1])
-- o Roblox centraliza cada MeshPart na caixa da malha: o deslocamento sai da raiz
local OFFSET = raiz.Position - Vector3.new(RIG[1][6], RIG[1][7], RIG[1][8])
modelo:SetAttribute("Offset", OFFSET)

for _, d in RIG do
	local p = partes[d[1]]
	if not p then
		warn("[Myxilia] falta a peca " .. d[1])
		continue
	end
	local velho = p:FindFirstChild("J_" .. d[1])
	if velho then
		velho:Destroy()
	end
	p.CanCollide = false
	p.Anchored = d[2] == ""
	p.Massless = d[2] ~= ""
	local b = partes[d[1] .. "_Brilho"]
	if b then
		b.Material = Enum.Material.Neon
		b.CanCollide = false
		b.Anchored = false
		b.Massless = true
		for _, w in b:GetChildren() do
			if w:IsA("WeldConstraint") then
				w:Destroy()
			end
		end
		local w = Instance.new("WeldConstraint")
		w.Part0 = p
		w.Part1 = b
		w.Parent = b
	end
	if d[2] ~= "" then
		local pai = partes[d[2]]
		local piv = CFrame.new(Vector3.new(d[3], d[4], d[5]) + OFFSET)
		local m = Instance.new("Motor6D")
		m.Name = "J_" .. d[1]
		m.Part0 = pai
		m.Part1 = p
		m.C0 = pai.CFrame:Inverse() * piv
		m.C1 = p.CFrame:Inverse() * piv
		m.Parent = p
	end
end

local pasta = modelo:FindFirstChild("Fios") or Instance.new("Folder")
pasta.Name = "Fios"
pasta.Parent = modelo
pasta:ClearAllChildren()
for _, f in FIOS do
	local braco = partes["Titereiro_Braco_" .. f[2]]
	local femur = partes[f[1] .. "_Femur"]
	if braco and femur then
		for _, parte in {braco, femur} do
			local velho = parte:FindFirstChild("Fio_" .. f[1])
			if velho then
				velho:Destroy()
			end
		end
		local a0 = Instance.new("Attachment")
		a0.Name = "Fio_" .. f[1]
		a0.Parent = braco
		a0.WorldPosition = Vector3.new(f[3], f[4], f[5]) + OFFSET
		local a1 = Instance.new("Attachment")
		a1.Name = "Fio_" .. f[1]
		a1.Parent = femur
		a1.WorldPosition = Vector3.new(f[6], f[7], f[8]) + OFFSET
		local fio = Instance.new("Beam")
		fio.Name = "Fio_" .. f[1]
		fio.Attachment0 = a0
		fio.Attachment1 = a1
		fio.Color = ColorSequence.new(COR_FIO)
		fio.LightEmission = 1
		fio.LightInfluence = 0
		fio.Width0 = 0.08
		fio.Width1 = 0.06
		fio.FaceCamera = true
		fio.Parent = pasta
	end
end
modelo.PrimaryPart = raiz
print(("[Myxilia] rig montado: %%d pecas, %%d fios"):format(#RIG, #pasta:GetChildren()))
''' % (linhas_rig, linhas_fios)

MARIONETE = '''-- Myxilia: marcha de marionete (Script dentro do Model Myxilia, depois de rodar MontarMyxilia)
-- Atributos do Model: Andar (bool), Velocidade (studs/s), Cortadas (ex.: "Perna4_E,Perna4_D").
-- Cada fio cortado solta a perna dela: a perna arrasta, o corpo afunda e inclina para o lado sem apoio.
-- Para teste no Studio roda no servidor e escreve Motor6D.C0; no jogo, rode no cliente a partir de eventos.
-- Gerado pela forja (mesma matematica da previa em Python). Nao testado no Studio: confira no piloto.
local RunService = game:GetService("RunService")
local modelo = script.Parent
local OFFSET: Vector3 = modelo:GetAttribute("Offset") or Vector3.zero
local V0, PERIODO, APOIO, LEVANTE, ARRANCO = %.3f, %.4f, %.2f, %.2f, %.2f
local RAIZ = Vector3.new(%s) + OFFSET
local CHAO = OFFSET.Y
local FWD = Vector3.new(0, 0, -1)
local Y = Vector3.yAxis

-- {nome, pai, pivo x,y,z} em ordem: pai antes do filho
local PECAS = {
%s
}
-- {perna, lado, grupoA, quadril xyz, joelho xyz, tornozelo xyz, pe xyz, direcao xyz, Lf, Lt, ponta do dedo xyz}
local PERNAS = {
%s
}

local function V(d, i)
	return Vector3.new(d[i], d[i + 1], d[i + 2]) + OFFSET
end
local partes, motores, c0, pivo = {}, {}, {}, {}
for _, d in PECAS do
	local p = modelo:FindFirstChild(d[1], true)
	partes[d[1]] = p
	pivo[d[1]] = V(d, 3)
	if d[2] ~= "" and p then
		local m = p:FindFirstChild("J_" .. d[1])
		if m then
			motores[d[1]] = m
			c0[d[1]] = m.C0
		end
	end
end
local L = {}
for _, d in PERNAS do
	L[d[1]] = {lado = d[2], A = d[3], quadril = V(d, 4), joelho = V(d, 7), tornozelo = V(d, 10), pe = V(d, 13),
		dir = Vector3.new(d[16], d[17], d[18]), Lf = d[19], Lt = d[20], ponta = V(d, 21)}
end
local raiz = partes["Cefalotorax"]
local raizRepouso = raiz.CFrame
local fios = modelo:FindFirstChild("Fios")

local function ik2(q, alvo, Lf, Lt, dica)
	local v = alvo - q
	local d = math.min(v.Magnitude, (Lf + Lt) * 0.999)
	local e = v.Unit
	local a = (Lf * Lf - Lt * Lt + d * d) / (2 * d)
	local h = math.sqrt(math.max(Lf * Lf - a * a, 1e-6))
	local n = (dica - e * dica:Dot(e)).Unit
	return q + e * a + n * h
end
local function quadro(u, n)
	u = u.Unit
	n = (n - u * n:Dot(u)).Unit
	return CFrame.fromMatrix(Vector3.zero, u, n, u:Cross(n))
end
local function segmento(P0, P1, N0, Q0, Q1, N1)
	return CFrame.new(Q0) * (quadro(Q1 - Q0, N1) * quadro(P1 - P0, N0):Inverse()) * CFrame.new(-P0)
end
local function plano(a, b, c)
	return (b - a):Cross(c - a).Unit
end
local function perfil(s)
	if s < 0.25 then
		return math.sin(math.pi / 2 * s / 0.25)
	elseif s < 0.8 then
		return 1
	end
	return 1 - ((s - 0.8) / 0.2) ^ 2
end
local function suave(x)
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

local t = 0
RunService.Heartbeat:Connect(function(dt)
	if modelo:GetAttribute("Andar") ~= false then
		t += dt
	end
	local v = modelo:GetAttribute("Velocidade") or V0
	local T = PERIODO * V0 / math.max(v, 0.1)
	local function s(tt)
		return v * (tt - ARRANCO * T / (2 * math.pi) * math.sin(2 * math.pi * tt / T))
	end
	if s(t) > 40 then
		t = 0
	end
	local cortadas, nE, nD = {}, 0, 0
	for nome in string.gmatch(modelo:GetAttribute("Cortadas") or "", "[^,%%s]+") do
		if L[nome] and not cortadas[nome] then
			cortadas[nome] = true
			if L[nome].lado == "E" then nE += 1 else nD += 1 end
		end
	end
	local bob = -0.07 * math.abs(math.sin(2 * math.pi * 2 * t / T))
	local R = CFrame.fromAxisAngle(Vector3.zAxis, -math.rad(4.5) * (nD - nE))
		* CFrame.fromAxisAngle(Vector3.xAxis, math.rad(1.5) * math.sin(2 * math.pi * t / T))
	local Tc = CFrame.new(RAIZ + FWD * s(t) + Vector3.new(0, bob - 0.14 * (nE + nD), 0)) * R * CFrame.new(-RAIZ)
	local Rc = Tc.Rotation
	local Tseg, levant = {}, {E = {}, D = {}}
	for nome, l in L do
		local quad = Tc * l.quadril
		local pe, dica
		if cortadas[nome] then
			local centro = Vector3.new(0, 0, -1.4) + OFFSET
			pe = (l.pe - centro) * 0.72 + centro + Vector3.new(0, 0, 0.9) + FWD * s(t)
			pe = Vector3.new(pe.X, CHAO, pe.Z)
			dica = Rc * (Y * 0.15 + l.dir)
		else
			local off = if l.A then 0 else 0.5
			local ph = t / T + off
			local c = math.floor(ph)
			local phi = ph - c
			local function F(cc)
				local ta = (cc - off) * T
				return l.pe + FWD * (s(ta) + (s(ta + APOIO * T) - s(ta)) / 2)
			end
			local lift = 0
			if phi < APOIO then
				pe = F(c)
			else
				local sig = (phi - APOIO) / (1 - APOIO)
				pe = F(c):Lerp(F(c + 1), suave((sig - 0.15) / 0.6))
				lift = LEVANTE * perfil(sig)
				pe += Vector3.new(0, lift, 0)
			end
			table.insert(levant[l.lado], lift / LEVANTE)
			local ponta = Tc * l.ponta
			dica = (Rc * Y + (ponta - quad).Unit * (0.9 * lift / LEVANTE)).Unit
		end
		local torn = pe - Rc * (l.pe - l.tornozelo)
		local joel = ik2(quad, torn, l.Lf, l.Lt, dica)
		local N0 = plano(l.quadril, l.joelho, l.tornozelo)
		local N1 = plano(quad, joel, torn)
		Tseg[nome .. "_Femur"] = segmento(l.quadril, l.joelho, N0, quad, joel, N1)
		Tseg[nome .. "_Tibia"] = segmento(l.joelho, l.tornozelo, N0, joel, torn, N1)
		Tseg[nome .. "_Tarso"] = segmento(l.tornozelo, l.pe, N0, torn, pe, N1)
		Tseg["No_" .. nome] = Tseg[nome .. "_Femur"]
		local fio = fios and fios:FindFirstChild("Fio_" .. nome)
		if fio then
			fio.Enabled = not cortadas[nome]
		end
	end
	local loc = {}
	loc["Abdomen"] = CFrame.fromAxisAngle(Vector3.xAxis, math.rad(-6) * math.sin(2 * math.pi * t / T + 0.6) + math.rad(2.5) * (nE + nD))
	for k = 1, 3 do
		loc["Esporangio_" .. k] = CFrame.fromAxisAngle(Vector3.xAxis, math.rad(7) * math.sin(2 * math.pi * 2 * t / T + (k - 1) * 1.7))
	end
	for _, lado in {"E", "D"} do
		local soma, n = 0, 0
		for _, x in levant[lado] do
			soma += x
			n += 1
		end
		local media = if n > 0 then soma / n else 0
		loc["Titereiro_Braco_" .. lado] = CFrame.fromAxisAngle(Vector3.xAxis, -0.45 * media)
		local sgn = if lado == "E" then -1 else 1
		loc["Quelicera_" .. lado] = CFrame.fromAxisAngle(Vector3.zAxis, sgn * math.rad(4 + 3 * math.sin(2 * math.pi * t / T)))
	end
	local T_ = {Cefalotorax = Tc}
	for _, d in PECAS do
		local nome, pai = d[1], d[2]
		if nome ~= "Cefalotorax" then
			if Tseg[nome] then
				T_[nome] = Tseg[nome]
			elseif loc[nome] then
				local p = pivo[nome]
				T_[nome] = T_[pai] * CFrame.new(p) * loc[nome] * CFrame.new(-p)
			else
				T_[nome] = T_[pai]
			end
		end
	end
	raiz.CFrame = Tc * raizRepouso
	for nome, m in motores do
		local p = pivo[nome]
		local X = CFrame.new(-p) * T_[m.Part0.Name]:Inverse() * T_[nome] * CFrame.new(p)
		m.C0 = c0[nome] * X
	end
end)
''' % (m["v"], m["periodo"], m["apoio"], m["levante"], m["arranco"], f3(raiz["pivo"]), linhas_pecas, linhas_pernas)

open(os.path.join(BASE, "saida", "MontarMyxilia.luau"), "w").write(MONTAR)
open(os.path.join(BASE, "saida", "MarioneteMyxilia.luau"), "w").write(MARIONETE)
print(len(MONTAR), len(MARIONETE))
