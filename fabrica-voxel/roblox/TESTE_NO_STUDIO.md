# Teste no Roblox Studio (passo a passo)

Nada deste runtime foi testado dentro do Studio. Este roteiro é o primeiro teste.

1. `python -m fabrica pacote` gera `saida/FabricaVoxel.rbxmx`.
2. No Studio, arraste o arquivo para a janela 3D. Aparece `Workspace > FabricaVoxel_Instalar`.
3. Clique com o botão direito no Script `INSTALAR` > **Run**. A saída deve dizer `[FabricaVoxel] instalado`.
   - Deve aparecer `ReplicatedStorage > Fabrica` (com `Dados`, `Clipes` e os módulos), dois Scripts em
     `ServerScriptService` e um LocalScript em `StarterPlayer > StarterPlayerScripts`.
   - Se o botão Run não existir, dê Play uma vez: o Script roda sozinho.
4. Dê **Play**. Em `z = 60` deve aparecer uma fileira com todos os modelos, montados por Parts, trocando de
   animação a cada poucos segundos.
   - Não apareceu nada: veja a janela Output. Mensagens começam com `[Fabrica...]` e dizem o que faltou.
   - Apareceu parado: o LocalScript `FabricaCliente` não rodou. Confira se está em `StarterPlayerScripts`.
   - Apareceu de costas: selecione o modelo e ponha o atributo `GiroY = 180`.
5. Teste de malha: `File > Import 3D`, escolha `saida/<id>/modelo.glb`, unidade **Studs**. Ponha o Model
   importado em `ServerStorage > FabricaModelos` com o nome igual ao Id (ex.: `esporinho`). O viveiro passa a
   usar a malha em vez das Parts.
   - Confira: cada peça é um MeshPart com o nome da peça; as cores aparecem sem textura; o tamanho bate.
6. Movimento em grade: no servidor, dê ao jogador o atributo `Modo = "Grade"` e um Character com `PrimaryPart`.
   WASD pede um passo por casa de 4 studs.

O que anotar e me dizer: (a) as cores de vértice aparecem? (b) o modelo vem de frente ou de costas?
(c) as juntas giram no lugar certo? (d) a animação fica lisa a 60 fps com 20 modelos?
