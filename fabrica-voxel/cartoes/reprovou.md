# Cartão: reprovou, e agora?

| Mensagem | Causa | Conserto |
| --- | --- | --- |
| P0: `campo "x" nao existe` | nome errado | use a sugestão da mensagem; `python -m fabrica explicar <tipo>` |
| P0: `ancora "..." nao existe` | a forma ou peça citada vem depois, ou o nome está errado | a mensagem lista as âncoras que existem |
| P0: `material "x" nao foi declarado` | faltou em `materiais` | acrescente o nome na lista |
| P1 `voxels_soltos` | pedaço da peça não encosta em nada | encadeie as formas (`"em": "<forma>.topo"`), engrosse para 2 voxels, ou encoste no corpo |
| P1 `pe_no_chao` | o modelo flutua ou entra no chão | primeira forma com `"em": "chao"`; se flutua de propósito, `"meta": {"flutua": true}` |
| P1 `brilho` | material de brilho em área grande | brilho só em olhos, núcleos, pontas |
| P1 `clipe_X_laco` | o laço dá um tranco | `harm` inteiro nas ondas; última pose igual à primeira |
| P1 `clipe_X_giro` | um osso gira demais num quadro | aumente a duração ou reduza a amplitude |
| P1 `clipe_X_gemeos` | esquerda e direita espelhadas | mude `fase` de um lado em 0.03 a 0.08 |
| P1 `um_tamanho_de_voxel` | peças com `corte` diferente no mesmo modelo | o mesmo `corte` em todas as peças |
| P1 `item_atravessa_corpo` | a arma ou o escudo entra no corpo em algum quadro | confira `pegada`, soquetes `Pegada` e `Ponta` do item; em golpe novo, `centro_H.frente` maior ou `arco.raio_mao_H` maior |
| P1 `triangulos_por_malha` | peça com cor demais ou grande demais | divida a peça; simplifique o padrão |
| P2 `grupos_de_valor` | tudo no mesmo tom | materiais vizinhos com rampas de claridade diferente |
| P2 `silhueta` | caixote ou esfiapado | acrescente 1 ou 2 formas que saiam do corpo, ou engrosse |
| P2 `voxels_orfaos` | ruído de cor | tire estampa de 1 voxel isolado |
| P2 `area_de_descanso` | detalhe em tudo | concentre o detalhe na cabeça; deixe o resto liso |
| P2 `assimetria` | simetria perfeita | uma forma sem `espelhar` |

Se a mesma regra reprovar três vezes, pare e descreva o problema para o dono em vez de tentar de novo.
