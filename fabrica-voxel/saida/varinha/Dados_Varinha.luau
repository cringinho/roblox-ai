-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_Varinha
-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.
-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).
return {
	Id = "varinha", Nome = "Varinha de estrela", VersaoFabrica = "4.0.0",
	Altura = 1.875,
	Ossos = { -- pais antes dos filhos
		{Nome = "Raiz", Pai = "", Pivo = {0, 0, 0}, Papel = "raiz", Mola = nil},
		{Nome = "Item", Pai = "Raiz", Pivo = {0.0625, 0, 0.0625}, Papel = "corpo", Mola = nil},
	},
	Pecas = { -- uma malha (MeshPart) por peca; varias pecas podem usar o mesmo osso
		{Nome = "Item", Osso = "Item", Centro = {0.0625, 0.9375, 0.0625}, Tamanho = {0.125, 1.875, 0.625}, Corte = 0.125, TemBrilho = true, EscalaAnimada = false},
	},
	Soquetes = {
		{Nome = "Pegada", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
		{Nome = "Ponta", Osso = "Item", Pos = {0.0625, 1.875, 0.0625}},
		{Nome = "Base", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
	},
	Caixas = { -- por peca: {cx, cy, cz, sx, sy, sz, corHex, neon}; monta o modelo com Parts, sem importar malha
		Item = {
			{0.0625, 0.0625, 0.0625, 0.125, 0.125, 0.125, "48230A", 0},
			{0.0625, 0.375, 0.0625, 0.125, 0.5, 0.125, "190B0A", 0},
			{0.0625, 0.75, 0.0625, 0.125, 0.25, 0.125, "3A1E15", 0},
			{0.0625, 1.1875, 0.0625, 0.125, 0.625, 0.125, "190B0A", 0},
			{0.0625, 1.6875, 0.0625, 0.125, 0.375, 0.375, "B388F5", 1},
			{0.0625, 1.6875, -0.1875, 0.125, 0.125, 0.125, "B388F5", 1},
			{0.0625, 1.6875, 0.3125, 0.125, 0.125, 0.125, "B388F5", 1},
		},
	},
	TotalCaixas = 7,
}
