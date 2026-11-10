-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_Varinha
-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.
-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).
return {
	Id = "varinha", Nome = "Varinha de estrela", VersaoFabrica = "4.0.0",
	Altura = 1.5,
	Rig = {
		{Nome = "Raiz", Pai = "", Peca = false, Pivo = {0, 0, 0}, Centro = {0, 0, 0}, Tamanho = {0, 0, 0}, Papel = "raiz", Corte = 0, TemBrilho = false, EscalaAnimada = false, Mola = nil},
		{Nome = "Item", Pai = "Raiz", Peca = true, Pivo = {0.0625, 0, 0.0625}, Centro = {0.0625, 0.75, 0.0625}, Tamanho = {0.125, 1.5, 0.625}, Papel = "corpo", Corte = 0.125, TemBrilho = true, EscalaAnimada = false, Mola = nil},
	},
	Soquetes = {
		{Nome = "Pegada", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
		{Nome = "Ponta", Osso = "Item", Pos = {0.0625, 1.5, 0.0625}},
		{Nome = "Base", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
	},
	Caixas = { -- {cx, cy, cz, sx, sy, sz, corHex, neon} para montar com Parts, sem importar malha
		Item = {
			{0.0625, 0.0625, 0.0625, 0.125, 0.125, 0.125, "48230A", 0},
			{0.0625, 0.625, 0.0625, 0.125, 1, 0.125, "190B0A", 0},
			{0.0625, 1.3125, 0.0625, 0.125, 0.375, 0.375, "B388F5", 1},
			{0.0625, 1.3125, -0.1875, 0.125, 0.125, 0.125, "B388F5", 1},
			{0.0625, 1.3125, 0.3125, 0.125, 0.125, 0.125, "B388F5", 1},
		},
	},
	TotalCaixas = 5,
}
