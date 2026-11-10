# Cartão: forma (peças, âncoras, estampas)

Uma peça é uma lista de formas, executadas em ordem. Unidade: **voxel inteiro**.

```json
{"op": "caixa", "nome": "cranio", "tam": [12, 11, 11], "raio": 3, "em": "Tronco.t.topo", "desloc": {"baixo": 1}, "material": "pele"}
```

| Campo | Valores |
| --- | --- |
| `op` | `caixa` (com `raio` ou `chanfro`), `elipsoide`, `cilindro`, `cone`, `capsula` (`de`, `ate`, `r0`, `r1`), `estampa`, `voxels` |
| `tam` | `[largura, altura, profundidade]` em voxels, mínimo 1 |
| `em` | âncora: `chao`, ou `topo` `base` `frente` `tras` `dir` `esq` `centro` (e combinações como `topo_frente`) da própria peça, de uma forma nomeada (`cranio.topo`) ou de outra peça (`Tronco.topo`) |
| `encaixe` | `fora` (padrão: encosta por fora da face), `dentro`, `centro` |
| `desloc` | `{"frente": 2, "cima": 1, "direita": 3}`; também `tras`, `baixo`, `esquerda` |
| `modo` | `uniao` (padrão), `so_vazio`, `cortar`, `pintar` (só troca a cor do que já existe) |
| `espelhar` | `true` repete do outro lado. Sem isso a forma é uma assimetria intencional |
| `nome` | dá nome à forma para outras se apoiarem nela |

A primeira forma do modelo usa `"em": "chao"`. Frente da criatura = para onde ela olha.

**Estampa** (olhos, boca, brasão): arte em texto numa face. Cada letra é um material; `.` não mexe.

```json
{"op": "estampa", "em": "cranio", "face": "frente", "desloc": {"cima": 1},
 "linhas": ["BP....PB", "BP....PB"], "legenda": {"B": "olho_branco", "P": "olho_pupila"}}
```

`"profundidade": -1` cava (órbita, boca); com `"fundo": "brilho_brasa"` o fundo do buraco acende.

**Ossos**: cada peça gira em torno do pivô do seu osso.
```json
{"nome": "Cabeca", "pai": "Corpo", "pivo": {"em": "Cabeca.cranio.base"}, "papel": "cabeca", "junta": 2}
```
`junta: 2` põe uma esfera de raio 2 no pivô, para a junta não abrir fresta quando gira.

Regras: nada menor que 1 voxel; detalhe fino com 2 voxels de espessura; peça pequena (lado < 5) não leva chanfro.

**Repetir** (dentes, garras, espinhos, costelas, placas): uma forma vira várias, cada uma um passo adiante.
```json
{"op": "caixa", "tam": [1, 2, 1], "em": "t.topo", "desloc": {"frente": 4}, "material": "detalhe",
 "repetir": {"n": 4, "passo": {"tras": 3}}}
```

**Mais ossos sem redesenhar** (no osso, não na peça):

| Campo do osso | O que faz |
| --- | --- |
| `"segmentos": 2` | corta a peça em dois ossos em cadeia (coxa e canela, braço e antebraço). Nascem `<Nome>_2`, `<Nome>_3`. Use `"eixo": "y"` em braço e perna |
| `"dobra"` | `joelho` (perna), `reverso` (perna de trás de quadrúpede, perna de ave), `cotovelo` (braço), `livre` (cauda, pescoço, asa, tentáculo) |
| `"seguir_pai": {"modo": "livre", "ganho": 0.8, "atraso_s": 0.1}` | o osso acompanha o pai com atraso, sem camada no clipe: orelha, chifre, bolsa, pano |
| `"repouso": {"frente": 12}` | giro fixo do osso em graus (a grade continua reta) |

Uma peça pode pender de um segmento: `"pai": "Braco_D_2"` (a mão na ponta do antebraço).
