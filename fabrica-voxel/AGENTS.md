# Fábrica de Voxel — manual de operação para IA

Você vai produzir assets voxel para o jogo Sanctum Obscura (Roblox). Você **não** esculpe à mão nem escreve
código: você edita **fichas JSON** em `registro/` e roda a fábrica. A fábrica mede o resultado e diz o conserto.

Rode tudo de dentro da pasta `fabrica-voxel/`. Só precisa de Python com numpy e Pillow.

## As 7 regras

1. **Nunca edite `fabrica/`, `saida/` nem arquivos `.luau` gerados.** Só `registro/`.
2. **Comece de uma ficha que existe.** `python -m fabrica novo monstro meu_bicho --de mastim_relicario`.
3. **Só inteiros de voxel, âncoras e nomes.** Nada de coordenada em studs. Nada de sinal de ângulo: use
   `frente`, `tras`, `cima`, `baixo`, `direita`, `esquerda` (posição) e `frente`, `esquerda`, `tombar_direita` (rotação).
4. **Rode `construir` depois de cada mudança** e leia a saída inteira. Se reprovou, aplique o conserto que a
   mensagem dá e rode de novo. Não mude três coisas de uma vez.
5. **Não afrouxe limite de auditoria.** Conserte a ficha.
6. **Olhe a folha** (`saida/<id>/folha.png`) antes de dizer que terminou. Se você não enxerga imagens, diga isso.
7. **Diga o que não foi testado.** Nada aqui roda dentro do Roblox Studio; quem testa lá é o dono do jogo.

## O laço de trabalho

```
python -m fabrica listar monstro            # o que existe
python -m fabrica explicar monstro          # campos aceitos
python -m fabrica novo monstro <id> --de <modelo>
# ... edite registro/monstros/<id>.json ...
python -m fabrica validar <id>              # P0: a ficha esta bem formada?
python -m fabrica construir <id>            # P0 -> forma -> pintura -> clipes -> P1 -> exporta -> P2 -> folha
# status APROVADO = terminou.  REPROVADO = leia o conserto, edite, construa de novo.
```

Saídas em `saida/<id>/`: `folha.png` (confira), `anim.gif`, `modelo.glb`, `modelo.vox`, `Dados_*.luau`,
`Clipes_*.luau`, `relatorio.json`.

## Qual cartão ler

| Tarefa | Cartão |
| --- | --- |
| Monstro novo a partir de um arquétipo | `cartoes/monstro.md` |
| Forma: peças, âncoras, estampas | `cartoes/forma.md` |
| Animação: camadas de um clipe | `cartoes/animacao.md` |
| Item de mão ou conjunto de equipamento | `cartoes/equipamento.md` |
| Linhagem, traço, rosto, cabelo | `cartoes/linhagem.md` |
| Produzir muitos de uma vez e empacotar | `cartoes/lote.md` |
| Entender por que reprovou | `cartoes/reprovou.md` |

Leia **só** o cartão da tarefa. Não leia `docs/ARQUITETURA.md` a menos que vá mudar o código da fábrica.

## Barra de arte (o que separa asset de estúdio de asset de código)

- Silhueta primeiro: 1 ou 2 massas grandes, poucas médias, detalhe só na cabeça e na arma.
- Blocos antes de orgânico: prefira `caixa` com `chanfro` a `elipsoide`. Nada de "sabonete".
- 3 a 6 materiais por asset. Cada material vizinho com valor diferente (um escuro, um médio, um claro).
- Brilho só em olhos, núcleos e pontas.
- 1 a 3 assimetrias intencionais (uma ombreira, um chifre quebrado, uma orelha rasgada).
- Nunca ruído: padrão só onde há lógica (musgo em cima, ferrugem na aresta).
- Tudo no mesmo voxel de 0,125 stud (corte `grade`). Só estrutura e prop grande usam 0,25 (`mundo`).

## Barra de movimento

- Nada começa e para junto: defase as camadas (`fase`).
- Esquerda e direita nunca espelhadas: fases e amplitudes um pouco diferentes.
- Ataque: preparação longa (40% do tempo), golpe curto, assentamento. Inimigo avisa por pelo menos 0,4 s.
- Parado dura 6 a 8 s e tem pelo menos duas camadas.
- Criatura maior é mais lenta: a fábrica já multiplica os tempos pela raiz do porte.
