-- Coloque este ModuleScript em ReplicatedStorage > Fabrica, com o nome Config
-- Todos os numeros ajustaveis do runtime ficam aqui. Nao testado no Studio: confira no piloto.
return {
	LADRILHO = 4, -- studs por casa da grade
	SEGUNDOS_POR_LADRILHO = 0.4444, -- 9 studs/s a pe
	-- camera da grade (2.5D): Scriptable, FOV baixo para parecer ortografica
	GRADE_ALTURA_TELA = 30, -- studs que a tela cobre na vertical, na distancia do heroi
	GRADE_INCLINACAO = 55, -- graus abaixo do horizonte
	GRADE_GUINADA = 35, -- graus em volta do eixo vertical
	GRADE_FOV = 15,
	GRADE_SUAVIZACAO = 8, -- quanto maior, mais rapido a camera alcanca o heroi
	-- dungeon: primeira pessoa
	DUNGEON_FOV = 70,
	MERGULHO_SEGUNDOS = 1.2,
	SUSTO_FOV = 80,
	SUSTO_SEGUNDOS = 0.1,
	HIT_STOP = 0.08,
	-- animacao
	TRANSICAO = 0.15, -- segundos de mistura entre clipes
	LOD_PERTO = 60, -- ate aqui anima todo quadro
	LOD_LONGE = 160, -- alem daqui nao anima
	MAX_CAIXAS = 600, -- teto de Parts por criatura na rota sem importacao
}
