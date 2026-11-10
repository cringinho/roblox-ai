# Cartão: produzir muitos de uma vez e empacotar

```
python -m fabrica lote tipo:monstro                 # todos os monstros
python -m fabrica lote lista.txt                    # um id por linha
python -m fabrica lote lobo_a lobo_b lobo_c
```
A tabela mostra status, nota P2, voxels, triângulos e a pior métrica de cada um. Conserte os reprovados um a um
com `python -m fabrica construir <id>`.

Variação controlada: uma ficha-mãe e várias filhas com `"herda"`. Cada filha muda pelo menos 3 de: rampa de cor,
`extras`, `acabamentos`, porte. Menos que isso é recolor, e recolor não vende nem engana o jogador.

Levar para o Roblox:
```
python -m fabrica pacote        # gera saida/FabricaVoxel.rbxmx com o runtime e todos os aprovados
```
Arraste o arquivo para o Studio, rode o Script INSTALAR uma vez. Veja `roblox/TESTE_NO_STUDIO.md`.

Vender:
```
python -m fabrica vender lobo_a lobo_b --nome pack_lobos_01 --data 2026-11-10
```
Gera `saida/_venda/pack_lobos_01.zip` com GLB em studs e em metros, .vox, vitrine, giro, animações, ficha técnica,
LEIA-ME, licença-modelo e PROVENIENCIA.json. Só entra asset aprovado.
