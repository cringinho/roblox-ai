--!strict
--[[
	PixelScale.luau
	Coloque em: ReplicatedStorage > Shared > Pixel   (Rojo: src/shared/Pixel/)

	O que faz: escolhe um fator de escala INTEIRO (1x, 2x, 3x...) para a UI em
	pixel art e aplica num UIScale. Escala fracionada (1.5x) cria "mixels"
	(pixels de tamanhos diferentes) - e o erro mais comum de pixel art no Roblox.

	Como montar a UI:
	  1. Desenhe tudo em "pixels da arte" (ex.: carta 72x104) usando Offset.
	  2. Coloque um UIScale no Frame raiz e chame PixelScale.bind(uiScale, ...).
	  3. Todas as ImageLabels com ResampleMode = Pixelated.
	Observacao: em celulares com DPI 2x/3x, mesmo k = 1 fica nitido (cada pixel da
	arte vira 2x2 ou 3x3 pixels fisicos).
]]

local PixelScale = {}

-- Maior fator inteiro em que 'nativeSize' cabe em 'fraction' da tela.
function PixelScale.compute(viewport: Vector2, nativeSize: Vector2, fraction: number?, minScale: number?, maxScale: number?): number
	local f = fraction or 1
	local kx = math.floor((viewport.X * f) / math.max(1, nativeSize.X))
	local ky = math.floor((viewport.Y * f) / math.max(1, nativeSize.Y))
	return math.clamp(math.min(kx, ky), minScale or 1, maxScale or 8)
end

-- Liga o UIScale ao tamanho da tela (atualiza ao girar o celular / redimensionar).
-- Retorna a funcao de desligar (coloque no scope do Fusion ou chame no Destroy).
function PixelScale.bind(uiScale: UIScale, nativeSize: Vector2, fraction: number?, minScale: number?, maxScale: number?): () -> ()
	local camera = workspace.CurrentCamera
	if camera == nil then
		warn("[PixelScale] sem CurrentCamera; usando escala 1")
		uiScale.Scale = 1
		return function() end
	end
	local cam: Camera = camera
	local function update()
		uiScale.Scale = PixelScale.compute(cam.ViewportSize, nativeSize, fraction, minScale, maxScale)
	end
	update()
	local connection = cam:GetPropertyChangedSignal("ViewportSize"):Connect(update)
	return function()
		connection:Disconnect()
	end
end

-- Arredonda um valor para multiplo do fator (posicoes animadas sem sub-pixel).
function PixelScale.snap(value: number, scale: number): number
	local k = math.max(1, scale)
	return math.floor(value / k + 0.5) * k
end

return table.freeze(PixelScale)
