-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_CajadoDeCirio
-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.
-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).
return {
	Id = "cajado_de_cirio", Nome = "Cajado de cirio", VersaoFabrica = "4.0.0",
	Altura = 4.25,
	Rig = {
		{Nome = "Raiz", Pai = "", Peca = false, Pivo = {0, 0, 0}, Centro = {0, 0, 0}, Tamanho = {0, 0, 0}, Papel = "raiz", Corte = 0, TemBrilho = false, EscalaAnimada = false, Mola = nil},
		{Nome = "Item", Pai = "Raiz", Peca = true, Pivo = {0.0625, 0, 0.0625}, Centro = {0.0625, 2.125, 0.0625}, Tamanho = {0.375, 4.25, 0.375}, Papel = "corpo", Corte = 0.125, TemBrilho = true, EscalaAnimada = false, Mola = nil},
	},
	Soquetes = {
		{Nome = "Pegada", Osso = "Item", Pos = {0.0625, 0.625, 0.0625}},
		{Nome = "Ponta", Osso = "Item", Pos = {0.0625, 4.25, 0.0625}},
		{Nome = "Base", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
	},
	Caixas = { -- {cx, cy, cz, sx, sy, sz, corHex, neon} para montar com Parts, sem importar malha
		Item = {
			{0, 2.6875, 0.0625, 0.25, 0.125, 0.125, "6B6F7C", 0},
			{-0.0625, 3.5625, -0.0625, 0.125, 0.125, 0.125, "878D97", 0},
			{-0.0625, 3.5625, 0.125, 0.125, 0.125, 0.25, "38354B", 0},
			{0.0625, 0.375, 0.0625, 0.125, 0.75, 0.125, "190B0A", 0},
			{0.0625, 1.375, 0.0625, 0.125, 1.25, 0.125, "3A1E15", 0},
			{0.0625, 2.3125, 0.0625, 0.125, 0.625, 0.125, "190B0A", 0},
			{0.0625, 2.8125, 0.0625, 0.125, 0.125, 0.125, "52392C", 0},
			{0.0625, 3.1875, 0.0625, 0.125, 0.625, 0.125, "190B0A", 0},
			{0.125, 3.5625, -0.0625, 0.25, 0.125, 0.125, "A6ACB4", 0},
			{0.0625, 3.5625, 0.0625, 0.125, 0.125, 0.125, "6B6F7C", 0},
			{0.0625, 3.5625, 0.1875, 0.125, 0.125, 0.125, "38354B", 0},
			{0.0625, 3.8125, 0.0625, 0.125, 0.375, 0.125, "D6CEAF", 0},
			{0.0625, 4.125, 0.0625, 0.125, 0.25, 0.125, "F59341", 1},
			{0.1875, 2.6875, 0.0625, 0.125, 0.125, 0.125, "A6ACB4", 0},
			{0.1875, 3.5625, 0.0625, 0.125, 0.125, 0.125, "A6ACB4", 0},
			{0.1875, 3.5625, 0.1875, 0.125, 0.125, 0.125, "878D97", 0},
		},
	},
	TotalCaixas = 16,
}
