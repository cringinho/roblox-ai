--!nonstrict
-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome CameraJogo
-- CLIENTE. As duas cameras do jogo: grade 2.5D (alta, quase ortografica) e dungeon (primeira pessoa),
-- com o mergulho entre elas e o tranco do susto.
-- Nao testado no Studio: confira no piloto.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")

local Config = require(script.Parent:WaitForChild("Config"))

local CameraJogo = {}
local conexao: RBXScriptConnection? = nil
local modo = ""
local tremor = 0

local function camera(): Camera?
	return Workspace.CurrentCamera
end

local function raizDoHeroi(): BasePart?
	local jogador = Players.LocalPlayer
	local ch = jogador and jogador.Character
	if not ch then
		return nil
	end
	local r = ch:FindFirstChild("HumanoidRootPart") or ch.PrimaryPart
	if r and r:IsA("BasePart") then
		return r
	end
	return nil
end

-- distancia para a tela cobrir GRADE_ALTURA_TELA studs com o FOV escolhido
local function distanciaGrade(): number
	return (Config.GRADE_ALTURA_TELA / 2) / math.tan(math.rad(Config.GRADE_FOV / 2))
end

local function cframeGrade(alvo: Vector3): CFrame
	local giro = CFrame.Angles(0, math.rad(Config.GRADE_GUINADA), 0) * CFrame.Angles(math.rad(-Config.GRADE_INCLINACAO), 0, 0)
	return CFrame.new(alvo) * giro * CFrame.new(0, 0, distanciaGrade())
end

local function parar()
	if conexao then
		conexao:Disconnect()
		conexao = nil
	end
end

function CameraJogo.modoGrade()
	local cam = camera()
	local jogador = Players.LocalPlayer
	if not cam or not jogador then
		return
	end
	parar()
	modo = "grade"
	jogador.CameraMode = Enum.CameraMode.Classic
	cam.CameraType = Enum.CameraType.Scriptable
	cam.FieldOfView = Config.GRADE_FOV
	local foco: Vector3? = nil
	conexao = RunService.RenderStepped:Connect(function(dt)
		local r = raizDoHeroi()
		local c = camera()
		if not r or not c then
			return
		end
		local alvo = r.Position
		foco = if foco then foco:Lerp(alvo, math.clamp(dt * Config.GRADE_SUAVIZACAO, 0, 1)) else alvo
		local cf = cframeGrade(foco :: Vector3)
		if tremor > 0 then
			tremor = math.max(0, tremor - dt * 4)
			cf *= CFrame.new((math.noise(os.clock() * 31) * tremor), (math.noise(os.clock() * 37, 5) * tremor), 0)
		end
		c.CFrame = cf
	end)
end

function CameraJogo.modoDungeon()
	local cam = camera()
	local jogador = Players.LocalPlayer
	if not cam or not jogador then
		return
	end
	parar()
	modo = "dungeon"
	cam.CameraType = Enum.CameraType.Custom
	cam.FieldOfView = Config.DUNGEON_FOV
	jogador.CameraMode = Enum.CameraMode.LockFirstPerson
end

-- Mergulho: da vista alta ate a cabeca do heroi, depois troca para primeira pessoa.
function CameraJogo.mergulhar(aoTerminar: (() -> ())?)
	local cam = camera()
	local r = raizDoHeroi()
	if not cam or not r then
		CameraJogo.modoDungeon()
		if aoTerminar then
			aoTerminar()
		end
		return
	end
	parar()
	cam.CameraType = Enum.CameraType.Scriptable
	local destino = CFrame.new(r.Position + Vector3.new(0, 1.5, 0)) * (r.CFrame - r.CFrame.Position)
	local info = TweenInfo.new(Config.MERGULHO_SEGUNDOS, Enum.EasingStyle.Quint, Enum.EasingDirection.In)
	local tw = TweenService:Create(cam, info, { CFrame = destino, FieldOfView = Config.DUNGEON_FOV })
	tw.Completed:Once(function()
		CameraJogo.modoDungeon()
		if aoTerminar then
			aoTerminar()
		end
	end)
	tw:Play()
end

-- Susto: o FOV salta e volta; a camera treme.
function CameraJogo.susto(intensidade: number?)
	local cam = camera()
	if not cam then
		return
	end
	local base = if modo == "dungeon" then Config.DUNGEON_FOV else Config.GRADE_FOV
	local pico = base + (Config.SUSTO_FOV - Config.DUNGEON_FOV) * (intensidade or 1)
	local ida = TweenService:Create(cam, TweenInfo.new(Config.SUSTO_SEGUNDOS, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { FieldOfView = pico })
	ida.Completed:Once(function()
		TweenService:Create(cam, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { FieldOfView = base }):Play()
	end)
	ida:Play()
	tremor = 0.6 * (intensidade or 1)
end

function CameraJogo.tremer(forca: number)
	tremor = math.max(tremor, forca)
end

function CameraJogo.modo(): string
	return modo
end

return CameraJogo
