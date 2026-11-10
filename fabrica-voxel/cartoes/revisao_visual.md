# Cartão: revisão visual (P3)

O P3 é o único portão que precisa de olho: humano, ou IA com visão. Só rode depois de P0, P1 e P2 passarem.
Abra `saida/<id>/folha.png` (vistas em cor, cinza e silhueta), `saida/<id>/anim.gif` e as tiras `saida/<id>/anim_<Clipe>.png`.

## Como responder

Para cada pergunta, responda **sim**, **quase** ou **não**. Na dúvida, é **não**.

| # | Pergunta | Onde olhar | Âncora do "sim" |
| --- | --- | --- | --- |
| A1 | Dá para dizer o que é só pela silhueta preta? | quadro de silhueta, vista de frente e da câmera do jogo | uma pessoa de fora acerta a categoria (lobo, cavaleiro, baú) em 2 segundos |
| A2 | Dá para dizer para onde ele olha? | silhueta de lado e de três quartos | a frente é óbvia sem ver o rosto |
| A3 | O olho vai primeiro para a cabeça ou para a arma? | folha em cor, olhando de longe | o ponto mais claro ou mais saturado está no foco, não no pé |
| A4 | Em tons de cinza, os materiais se separam? | quadro em cinza | pelo menos 3 tons distintos; pele, roupa e metal não viram a mesma mancha |
| A5 | Existe área calma? | folha em cor | pelo menos metade da superfície sem detalhe; detalhe junto, não espalhado |
| A6 | Algum voxel parece sujeira? | folha em cor, ampliada | nenhum ponto isolado de cor; nenhum padrão que pareça estática |
| A7 | Ele parece da mesma família dos outros? | ao lado de 3 modelos aprovados (`saida/_elenco`, `saida/_arquetipos`) | mesmo tamanho de voxel, mesma espessura de membro, mesma paleta de mundo |
| A8 | Há uma quebra de simetria com intenção? | vista de frente | 1 a 3 diferenças entre os lados que contam uma história (remendo, chifre quebrado) |
| A9 | Parado, ele parece vivo? | `anim.gif` e `anim_Parado.png` | respira e tem um segundo movimento fora de fase; não parece um pêndulo |
| A10 | Andando, o pé pisa? | `anim.gif` e `anim_Andar.png` | o pé para no chão no apoio e não desliza; o corpo sobe e desce com o passo |

Modelo estático (item, prop, estrutura): pule A9 e A10. Item de mão: A2 vira "dá para ver qual é a ponta e qual é o cabo?".

## Resultado

- **Publicável**: nenhum "não" e no máximo dois "quase".
- **Volta para a ficha**: qualquer "não". Diga qual pergunta reprovou e aplique o conserto abaixo.
- A1, A4 ou A6 com "não": o modelo não sai, mesmo com nota P2 alta.

## Conserto por pergunta

| Reprovou | Mexa em |
| --- | --- |
| A1, A2 | forma: acrescente o que sai do corpo (focinho, chifre, cauda, arma); engrosse o que some |
| A3 | paleta: clareie o foco, escureça pés e base |
| A4 | materiais: troque a rampa de um dos vizinhos por outra mais clara ou mais escura |
| A5, A6 | tire estampas; deixe o padrão só no foco |
| A7 | confira o `corte` da ficha e a paleta; nunca dois tamanhos de voxel no mesmo modelo |
| A8 | uma forma sem `espelhar` |
| A9, A10 | `cartoes/animacao.md`: camada `onda` com fase diferente; camada `passos` com `apoio` maior |

## Registro

```
python -m fabrica revisar <id> <respostas> --por <quem revisou>
```

`<respostas>` são 10 letras na ordem A1 a A10: `s` (sim), `q` (quase), `n` (não), `-` (pulou).
Exemplo para um item estático aprovado: `python -m fabrica revisar espada_longa ssssssss-- --por dono`.

A revisão fica em `revisoes/<id>.json`, presa à ficha: se a ficha mudar, a revisão deixa de valer e precisa ser
refeita. `python -m fabrica vender` deixa de fora todo modelo sem revisão válida.
