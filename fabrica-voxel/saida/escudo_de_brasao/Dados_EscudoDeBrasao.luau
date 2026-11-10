-- Coloque este ModuleScript em ReplicatedStorage > Fabrica > Dados, com o nome Dados_EscudoDeBrasao
-- Gerado pela Fabrica de Voxel. NAO edite a mao: mude a ficha e construa de novo.
-- Studs, repouso, chao em Y = 0, frente = -Z, +X = lado direito (_D).
return {
	Id = "escudo_de_brasao", Nome = "Escudo de brasao", VersaoFabrica = "4.0.0",
	Altura = 1.375,
	Ossos = { -- pais antes dos filhos; Repouso = quaternion {x, y, z, w} do giro fixo do osso (vai no C0)
		{Nome = "Raiz", Pai = "", Pivo = {0, 0, 0}, Papel = "raiz", Mola = nil},
		{Nome = "Item", Pai = "Raiz", Pivo = {0.0625, -0.125, 0}, Papel = "corpo", Mola = nil},
	},
	Pecas = { -- uma malha (MeshPart) por peca; varias pecas podem usar o mesmo osso
		{Nome = "Item", Osso = "Item", Centro = {0.0625, 0.625, 0}, Tamanho = {1.125, 1.5, 0.25}, Corte = 0.125, TemBrilho = false, EscalaAnimada = false},
	},
	Soquetes = {
		{Nome = "Pegada", Osso = "Item", Pos = {0.0625, 0.6875, 0.125}},
		{Nome = "Ponta", Osso = "Item", Pos = {0.0625, 1.375, 0.0625}},
		{Nome = "Base", Osso = "Item", Pos = {0.0625, 0, 0.0625}},
	},
	Caixas = { -- por peca: {cx, cy, cz, sx, sy, sz, corHex, neon}; monta o modelo com Parts, sem importar malha
		Item = {
			{0.0625, 0.0625, 0.0625, 1.125, 0.125, 0.125, "38354B", 0},
			{0, 0.1875, 0.0625, 1, 0.125, 0.125, "38354B", 0},
			{-0.4375, 0.5625, 0.0625, 0.125, 0.625, 0.125, "38354B", 0},
			{-0.4375, 1.0625, 0.0625, 0.125, 0.375, 0.125, "505264", 0},
			{-0.4375, 1.3125, 0.0625, 0.125, 0.125, 0.125, "878D97", 0},
			{0.0625, 0.3125, 0.0625, 0.875, 0.125, 0.125, "550A29", 0},
			{0, 0.5625, 0.0625, 0.75, 0.375, 0.125, "550A29", 0},
			{-0.0625, 0.8125, 0.0625, 0.625, 0.125, 0.125, "550A29", 0},
			{-0.125, 0.9375, 0.0625, 0.5, 0.125, 0.125, "550A29", 0},
			{-0.3125, 1.0625, 0.0625, 0.125, 0.125, 0.125, "550A29", 0},
			{0.0625, 1.1875, 0.0625, 0.875, 0.125, 0.125, "7A2436", 0},
			{0.125, 1.3125, 0.0625, 1, 0.125, 0.125, "A6ACB4", 0},
			{0.125, 1.0625, 0.0625, 0.75, 0.125, 0.125, "7A2436", 0},
			{0.0625, -0.0625, 0.0625, 0.375, 0.125, 0.125, "38354B", 0},
			{0.0625, 0.8125, -0.0625, 0.375, 0.125, 0.125, "F5F3C4", 0},
			{0.0625, 0.5625, -0.0625, 0.125, 0.375, 0.125, "CB9126", 0},
			{0.0625, 0.9375, -0.0625, 0.125, 0.125, 0.125, "F5F3C4", 0},
			{0.3125, 0.9375, 0.0625, 0.375, 0.125, 0.125, "7A2436", 0},
			{0.375, 0.8125, 0.0625, 0.25, 0.125, 0.125, "7A2436", 0},
			{0.4375, 0.5625, 0.0625, 0.125, 0.375, 0.125, "7A2436", 0},
			{0.5625, 0.5625, 0.0625, 0.125, 0.875, 0.125, "6B6F7C", 0},
			{0.5625, 1.125, 0.0625, 0.125, 0.25, 0.125, "878D97", 0},
		},
	},
	TotalCaixas = 22,
}
