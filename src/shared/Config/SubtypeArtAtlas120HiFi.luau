--!strict
--[[
	SubtypeArtAtlas120HiFi.luau  (GERADO com --hifi - nao edite a mao)
	Coloque em: ReplicatedStorage > Shared > Config

	Variante x4 para MOBILE: cada pixel da arte vira um bloco 4x4 = um bloco de compressao
	da GPU, entao a compressao com perdas do celular nao mistura cores vizinhas.
	8 paginas de 1024x1024 (16 artes por pagina, celulas de 256px).
	Custo: ~16x a memoria do atlas normal -> use so onde a cor estragar no aparelho.
	Troque cada PAGES[i] pelo rbxassetid da pagina i depois do upload (assetType Image).
]]

export type Entry = { page: number, offset: Vector2 }

local SubtypeArtAtlas120HiFi = {}

SubtypeArtAtlas120HiFi.CELL = 256
SubtypeArtAtlas120HiFi.PAGES = {
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p1.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p2.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p3.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p4.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p5.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p6.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p7.png
	"rbxassetid://0", -- SubtypeArtAtlas120_x4_p8.png
} :: { string }

local ENTRIES: { [string]: Entry } = {
	Treinamento = { page = 1, offset = Vector2.new(0, 0) },
	Mercenario = { page = 1, offset = Vector2.new(256, 0) },
	Veterano = { page = 1, offset = Vector2.new(512, 0) },
	ReliquiaAncestral = { page = 1, offset = Vector2.new(768, 0) },
	Oasis = { page = 1, offset = Vector2.new(0, 256) },
	Cacto = { page = 1, offset = Vector2.new(256, 256) },
	Deserto = { page = 1, offset = Vector2.new(512, 256) },
	Duna = { page = 1, offset = Vector2.new(768, 256) },
	Fossil = { page = 1, offset = Vector2.new(0, 512) },
	Escorpiao = { page = 1, offset = Vector2.new(256, 512) },
	TempestadeAreia = { page = 1, offset = Vector2.new(512, 512) },
	Mumia = { page = 1, offset = Vector2.new(768, 512) },
	Farao = { page = 1, offset = Vector2.new(0, 768) },
	Salada = { page = 1, offset = Vector2.new(256, 768) },
	Floresta = { page = 1, offset = Vector2.new(512, 768) },
	Pinheiro = { page = 1, offset = Vector2.new(768, 768) },
	Inseto = { page = 2, offset = Vector2.new(0, 0) },
	Planicie = { page = 2, offset = Vector2.new(256, 0) },
	Vegetal = { page = 2, offset = Vector2.new(512, 0) },
	Legume = { page = 2, offset = Vector2.new(768, 0) },
	Folha = { page = 2, offset = Vector2.new(0, 256) },
	Ninfa = { page = 2, offset = Vector2.new(256, 256) },
	Natureza = { page = 2, offset = Vector2.new(512, 256) },
	Fruto = { page = 2, offset = Vector2.new(768, 256) },
	Indigena = { page = 2, offset = Vector2.new(0, 512) },
	Vida = { page = 2, offset = Vector2.new(256, 512) },
	Ar = { page = 2, offset = Vector2.new(512, 512) },
	Vapor = { page = 2, offset = Vector2.new(768, 512) },
	Cinzas = { page = 2, offset = Vector2.new(0, 768) },
	Alada = { page = 2, offset = Vector2.new(256, 768) },
	Fantasma = { page = 2, offset = Vector2.new(512, 768) },
	Justica = { page = 2, offset = Vector2.new(768, 768) },
	Anjo = { page = 3, offset = Vector2.new(0, 0) },
	Arcanjo = { page = 3, offset = Vector2.new(256, 0) },
	Divino = { page = 3, offset = Vector2.new(512, 0) },
	Semideus = { page = 3, offset = Vector2.new(768, 0) },
	Serafim = { page = 3, offset = Vector2.new(0, 256) },
	Gelo = { page = 3, offset = Vector2.new(256, 256) },
	Cristal = { page = 3, offset = Vector2.new(512, 256) },
	Peixe = { page = 3, offset = Vector2.new(768, 256) },
	Raio = { page = 3, offset = Vector2.new(0, 512) },
	Geada = { page = 3, offset = Vector2.new(256, 512) },
	Nevasca = { page = 3, offset = Vector2.new(512, 512) },
	Espirito = { page = 3, offset = Vector2.new(768, 512) },
	Diamante = { page = 3, offset = Vector2.new(0, 768) },
	Plasma = { page = 3, offset = Vector2.new(256, 768) },
	Aurora = { page = 3, offset = Vector2.new(512, 768) },
	Oceano = { page = 3, offset = Vector2.new(768, 768) },
	Mar = { page = 4, offset = Vector2.new(0, 0) },
	Onda = { page = 4, offset = Vector2.new(256, 0) },
	Sereia = { page = 4, offset = Vector2.new(512, 0) },
	AbismoMarinho = { page = 4, offset = Vector2.new(768, 0) },
	Espaco = { page = 4, offset = Vector2.new(0, 256) },
	Estrela = { page = 4, offset = Vector2.new(256, 256) },
	Cometa = { page = 4, offset = Vector2.new(512, 256) },
	Profundeza = { page = 4, offset = Vector2.new(768, 256) },
	Leviata = { page = 4, offset = Vector2.new(0, 512) },
	Dimensao = { page = 4, offset = Vector2.new(256, 512) },
	Terra = { page = 4, offset = Vector2.new(512, 512) },
	Lama = { page = 4, offset = Vector2.new(768, 512) },
	Pantano = { page = 4, offset = Vector2.new(0, 768) },
	Madeira = { page = 4, offset = Vector2.new(256, 768) },
	Caranguejo = { page = 4, offset = Vector2.new(512, 768) },
	RaizPetrificada = { page = 4, offset = Vector2.new(768, 768) },
	Desmatamento = { page = 5, offset = Vector2.new(0, 0) },
	Aracnideo = { page = 5, offset = Vector2.new(256, 0) },
	Terremoto = { page = 5, offset = Vector2.new(512, 0) },
	GolemBarro = { page = 5, offset = Vector2.new(768, 0) },
	Obsidiana = { page = 5, offset = Vector2.new(0, 256) },
	Lixo = { page = 5, offset = Vector2.new(256, 256) },
	Petroleo = { page = 5, offset = Vector2.new(512, 256) },
	Pedra = { page = 5, offset = Vector2.new(768, 256) },
	Aco = { page = 5, offset = Vector2.new(0, 512) },
	Montanha = { page = 5, offset = Vector2.new(256, 512) },
	Sombra = { page = 5, offset = Vector2.new(512, 512) },
	AcoNegro = { page = 5, offset = Vector2.new(768, 512) },
	Void = { page = 5, offset = Vector2.new(0, 768) },
	Vulcao = { page = 5, offset = Vector2.new(256, 768) },
	Eclipse = { page = 5, offset = Vector2.new(512, 768) },
	Fada = { page = 5, offset = Vector2.new(768, 768) },
	Fofo = { page = 6, offset = Vector2.new(0, 0) },
	Brilho = { page = 6, offset = Vector2.new(256, 0) },
	Espelho = { page = 6, offset = Vector2.new(512, 0) },
	Fragmentacao = { page = 6, offset = Vector2.new(768, 0) },
	Beleza = { page = 6, offset = Vector2.new(0, 256) },
	Ilusao = { page = 6, offset = Vector2.new(256, 256) },
	Prisma = { page = 6, offset = Vector2.new(512, 256) },
	ArcoIris = { page = 6, offset = Vector2.new(768, 256) },
	MiragemAstral = { page = 6, offset = Vector2.new(0, 512) },
	Fogo = { page = 6, offset = Vector2.new(256, 512) },
	Lava = { page = 6, offset = Vector2.new(512, 512) },
	Dragonoide = { page = 6, offset = Vector2.new(768, 512) },
	Bomba = { page = 6, offset = Vector2.new(0, 768) },
	Forja = { page = 6, offset = Vector2.new(256, 768) },
	Demonio = { page = 6, offset = Vector2.new(512, 768) },
	Inferno = { page = 6, offset = Vector2.new(768, 768) },
	Solar = { page = 7, offset = Vector2.new(0, 0) },
	Destruicao = { page = 7, offset = Vector2.new(256, 0) },
	Supernova = { page = 7, offset = Vector2.new(512, 0) },
	Dragao = { page = 7, offset = Vector2.new(768, 0) },
	Maldicao = { page = 7, offset = Vector2.new(0, 256) },
	Veneno = { page = 7, offset = Vector2.new(256, 256) },
	Peso = { page = 7, offset = Vector2.new(512, 256) },
	Trevas = { page = 7, offset = Vector2.new(768, 256) },
	Hydra = { page = 7, offset = Vector2.new(0, 512) },
	Corrupcao = { page = 7, offset = Vector2.new(256, 512) },
	Micelio = { page = 7, offset = Vector2.new(512, 512) },
	Peste = { page = 7, offset = Vector2.new(768, 512) },
	Necromante = { page = 7, offset = Vector2.new(0, 768) },
	Lich = { page = 7, offset = Vector2.new(256, 768) },
	Vinho = { page = 7, offset = Vector2.new(512, 768) },
	Vampiro = { page = 7, offset = Vector2.new(768, 768) },
	Sangue = { page = 8, offset = Vector2.new(0, 0) },
	Parasita = { page = 8, offset = Vector2.new(256, 0) },
	Controle = { page = 8, offset = Vector2.new(512, 0) },
	Mutacao = { page = 8, offset = Vector2.new(768, 0) },
	Hemorragia = { page = 8, offset = Vector2.new(0, 256) },
	GengivaGotica = { page = 8, offset = Vector2.new(256, 256) },
	PactoSanguineo = { page = 8, offset = Vector2.new(512, 256) },
	Nosferatu = { page = 8, offset = Vector2.new(768, 256) },
}

function SubtypeArtAtlas120HiFi.get(subtypeId: string): Entry?
	return ENTRIES[subtypeId]
end

-- Aplica a arte; retorna false (e nao mexe na label) se o subtipo nao existir.
function SubtypeArtAtlas120HiFi.apply(label: ImageLabel, subtypeId: string): boolean
	local entry = ENTRIES[subtypeId]
	if entry == nil then
		warn(`[SubtypeArtAtlas120HiFi] subtipo desconhecido: {subtypeId}`)
		return false
	end
	label.Image = SubtypeArtAtlas120HiFi.PAGES[entry.page]
	label.ResampleMode = Enum.ResamplerMode.Pixelated
	label.ImageRectSize = Vector2.new(SubtypeArtAtlas120HiFi.CELL, SubtypeArtAtlas120HiFi.CELL)
	label.ImageRectOffset = entry.offset
	return true
end

return table.freeze(SubtypeArtAtlas120HiFi)
