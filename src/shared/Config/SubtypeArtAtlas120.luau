--!strict
--[[
	SubtypeArtAtlas120.luau  (GERADO - nao edite a mao)
	Coloque em: ReplicatedStorage > Shared > Config

	Modo B (recomendado para mobile): 1 ImageLabel por carta usando o atlas
	SubtypeArtAtlas120.png (1024x512, celulas de 64x64). Configure no ImageLabel:
	  ResampleMode = Enum.ResamplerMode.Pixelated
	  ImageRectSize = Vector2.new(64, 64)
	  ImageRectOffset = SubtypeArtAtlas120.offsetOf(subtypeId)
	Troque IMAGE pelo rbxassetid do atlas depois do upload.
]]

local SubtypeArtAtlas120 = {}

SubtypeArtAtlas120.IMAGE = "rbxassetid://0"
SubtypeArtAtlas120.CELL = 64

local OFFSETS: { [string]: Vector2 } = {
	Treinamento = Vector2.new(0, 0),
	Mercenario = Vector2.new(64, 0),
	Veterano = Vector2.new(128, 0),
	ReliquiaAncestral = Vector2.new(192, 0),
	Oasis = Vector2.new(256, 0),
	Cacto = Vector2.new(320, 0),
	Deserto = Vector2.new(384, 0),
	Duna = Vector2.new(448, 0),
	Fossil = Vector2.new(512, 0),
	Escorpiao = Vector2.new(576, 0),
	TempestadeAreia = Vector2.new(640, 0),
	Mumia = Vector2.new(704, 0),
	Farao = Vector2.new(768, 0),
	Salada = Vector2.new(832, 0),
	Floresta = Vector2.new(896, 0),
	Pinheiro = Vector2.new(960, 0),
	Inseto = Vector2.new(0, 64),
	Planicie = Vector2.new(64, 64),
	Vegetal = Vector2.new(128, 64),
	Legume = Vector2.new(192, 64),
	Folha = Vector2.new(256, 64),
	Ninfa = Vector2.new(320, 64),
	Natureza = Vector2.new(384, 64),
	Fruto = Vector2.new(448, 64),
	Indigena = Vector2.new(512, 64),
	Vida = Vector2.new(576, 64),
	Ar = Vector2.new(640, 64),
	Vapor = Vector2.new(704, 64),
	Cinzas = Vector2.new(768, 64),
	Alada = Vector2.new(832, 64),
	Fantasma = Vector2.new(896, 64),
	Justica = Vector2.new(960, 64),
	Anjo = Vector2.new(0, 128),
	Arcanjo = Vector2.new(64, 128),
	Divino = Vector2.new(128, 128),
	Semideus = Vector2.new(192, 128),
	Serafim = Vector2.new(256, 128),
	Gelo = Vector2.new(320, 128),
	Cristal = Vector2.new(384, 128),
	Peixe = Vector2.new(448, 128),
	Raio = Vector2.new(512, 128),
	Geada = Vector2.new(576, 128),
	Nevasca = Vector2.new(640, 128),
	Espirito = Vector2.new(704, 128),
	Diamante = Vector2.new(768, 128),
	Plasma = Vector2.new(832, 128),
	Aurora = Vector2.new(896, 128),
	Oceano = Vector2.new(960, 128),
	Mar = Vector2.new(0, 192),
	Onda = Vector2.new(64, 192),
	Sereia = Vector2.new(128, 192),
	AbismoMarinho = Vector2.new(192, 192),
	Espaco = Vector2.new(256, 192),
	Estrela = Vector2.new(320, 192),
	Cometa = Vector2.new(384, 192),
	Profundeza = Vector2.new(448, 192),
	Leviata = Vector2.new(512, 192),
	Dimensao = Vector2.new(576, 192),
	Terra = Vector2.new(640, 192),
	Lama = Vector2.new(704, 192),
	Pantano = Vector2.new(768, 192),
	Madeira = Vector2.new(832, 192),
	Caranguejo = Vector2.new(896, 192),
	RaizPetrificada = Vector2.new(960, 192),
	Desmatamento = Vector2.new(0, 256),
	Aracnideo = Vector2.new(64, 256),
	Terremoto = Vector2.new(128, 256),
	GolemBarro = Vector2.new(192, 256),
	Obsidiana = Vector2.new(256, 256),
	Lixo = Vector2.new(320, 256),
	Petroleo = Vector2.new(384, 256),
	Pedra = Vector2.new(448, 256),
	Aco = Vector2.new(512, 256),
	Montanha = Vector2.new(576, 256),
	Sombra = Vector2.new(640, 256),
	AcoNegro = Vector2.new(704, 256),
	Void = Vector2.new(768, 256),
	Vulcao = Vector2.new(832, 256),
	Eclipse = Vector2.new(896, 256),
	Fada = Vector2.new(960, 256),
	Fofo = Vector2.new(0, 320),
	Brilho = Vector2.new(64, 320),
	Espelho = Vector2.new(128, 320),
	Fragmentacao = Vector2.new(192, 320),
	Beleza = Vector2.new(256, 320),
	Ilusao = Vector2.new(320, 320),
	Prisma = Vector2.new(384, 320),
	ArcoIris = Vector2.new(448, 320),
	MiragemAstral = Vector2.new(512, 320),
	Fogo = Vector2.new(576, 320),
	Lava = Vector2.new(640, 320),
	Dragonoide = Vector2.new(704, 320),
	Bomba = Vector2.new(768, 320),
	Forja = Vector2.new(832, 320),
	Demonio = Vector2.new(896, 320),
	Inferno = Vector2.new(960, 320),
	Solar = Vector2.new(0, 384),
	Destruicao = Vector2.new(64, 384),
	Supernova = Vector2.new(128, 384),
	Dragao = Vector2.new(192, 384),
	Maldicao = Vector2.new(256, 384),
	Veneno = Vector2.new(320, 384),
	Peso = Vector2.new(384, 384),
	Trevas = Vector2.new(448, 384),
	Hydra = Vector2.new(512, 384),
	Corrupcao = Vector2.new(576, 384),
	Micelio = Vector2.new(640, 384),
	Peste = Vector2.new(704, 384),
	Necromante = Vector2.new(768, 384),
	Lich = Vector2.new(832, 384),
	Vinho = Vector2.new(896, 384),
	Vampiro = Vector2.new(960, 384),
	Sangue = Vector2.new(0, 448),
	Parasita = Vector2.new(64, 448),
	Controle = Vector2.new(128, 448),
	Mutacao = Vector2.new(192, 448),
	Hemorragia = Vector2.new(256, 448),
	GengivaGotica = Vector2.new(320, 448),
	PactoSanguineo = Vector2.new(384, 448),
	Nosferatu = Vector2.new(448, 448),
}

-- Offset do subtipo no atlas; Vector2.zero se nao existir (mostra o primeiro).
function SubtypeArtAtlas120.offsetOf(subtypeId: string): Vector2
	return OFFSETS[subtypeId] or Vector2.zero
end

function SubtypeArtAtlas120.apply(label: ImageLabel, subtypeId: string)
	label.Image = SubtypeArtAtlas120.IMAGE
	label.ResampleMode = Enum.ResamplerMode.Pixelated
	label.ImageRectSize = Vector2.new(SubtypeArtAtlas120.CELL, SubtypeArtAtlas120.CELL)
	label.ImageRectOffset = SubtypeArtAtlas120.offsetOf(subtypeId)
end

return table.freeze(SubtypeArtAtlas120)
