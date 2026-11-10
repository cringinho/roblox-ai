-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_EspadaLonga
-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.
-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).
return {
	Id = "espada_longa", Nome = "Espada longa", VersaoFabrica = "4.0.0",
	Altura = 3.5,
	Rig = {
		{Nome = "Raiz", Pai = "", Peca = false, Pivo = {0, 0, 0}, Centro = {0, 0, 0}, Tamanho = {0, 0, 0}, Papel = "raiz", Corte = 0, TemBrilho = false, EscalaAnimada = false, Mola = nil},
		{Nome = "Item", Pai = "Raiz", Peca = true, Pivo = {0, 0, 0.0625}, Centro = {0, 1.75, 0.0625}, Tamanho = {0.25, 3.5, 0.875}, Papel = "corpo", Corte = 0.125, TemBrilho = false, EscalaAnimada = false, Mola = nil},
	},
	Soquetes = {
		{Nome = "Pegada", Osso = "Item", Pos = {0.0625, 0.5625, 0.0625}},
		{Nome = "Ponta", Osso = "Item", Pos = {0.0625, 3.5, 0.0625}},
		{Nome = "Base", Osso = "Item", Pos = {0, 0, 0}},
	},
	Caixas = { -- {cx, cy, cz, sx, sy, sz, corHex, neon} para montar com Parts, sem importar malha
		Item = {
			{0, 0.125, 0, 0.25, 0.25, 0.25, "48230A", 0},
			{0.0625, 0.3125, 0.0625, 0.125, 0.125, 0.125, "3A1E16", 0},
			{0.0625, 0.625, 0.0625, 0.125, 0.5, 0.125, "52392D", 0},
			{0.0625, 0.75, -0.3125, 0.125, 0.25, 0.125, "878D97", 0},
			{0.0625, 0.9375, -0.125, 0.125, 0.125, 0.5, "A6ACB4", 0},
			{0.0625, 0.9375, 0.1875, 0.125, 0.125, 0.125, "9AA1B0", 0},
			{0.0625, 0.9375, 0.3125, 0.125, 0.125, 0.125, "878D97", 0},
			{0.0625, 0.9375, 0.4375, 0.125, 0.125, 0.125, "6B6F7C", 0},
			{0.0625, 1.1875, 0.0625, 0.125, 0.375, 0.375, "B9C1CD", 0},
			{0.0625, 1.5, -0.0625, 0.125, 0.25, 0.125, "D9E2EA", 0},
			{0.0625, 1.5625, 0.125, 0.125, 0.375, 0.25, "B9C1CD", 0},
			{0.0625, 1.6875, -0.0625, 0.125, 0.125, 0.125, "B9C1CD", 0},
			{0.0625, 1.8125, 0.0625, 0.125, 0.125, 0.375, "D9E2EA", 0},
			{0.0625, 2.25, 0.0625, 0.125, 0.75, 0.375, "B9C1CD", 0},
			{0.0625, 2.6875, 0.0625, 0.125, 0.125, 0.375, "D9E2EA", 0},
			{0.0625, 3, -0.0625, 0.125, 0.5, 0.125, "D9E2EA", 0},
			{0.0625, 2.875, 0.125, 0.125, 0.25, 0.25, "B9C1CD", 0},
			{0.0625, 3.25, 0.0625, 0.125, 0.5, 0.125, "D9E2EA", 0},
			{0.0625, 3.0625, 0.1875, 0.125, 0.125, 0.125, "B9C1CD", 0},
			{0.0625, 3.1875, 0.1875, 0.125, 0.125, 0.125, "D9E2EA", 0},
		},
	},
	TotalCaixas = 20,
}
