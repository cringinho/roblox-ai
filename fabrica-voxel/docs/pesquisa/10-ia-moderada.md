# 10 — Como fazer um modelo de IA moderado acertar

As fontes foram lidas pelo resumo da busca, não pela página inteira. O que é medição nossa está marcado como [M] e o que é proposta está marcado como [P].

## Veredito

A saída de um modelo não deve ser aceita sem checagem. As fontes sugerem devolver o erro ao modelo, validar por fora e dividir fichas grandes em partes. A fábrica já faz boa parte disso. Nenhum teste foi feito com um modelo pequeno de verdade.

## O que a pesquisa diz

| Achado | Fonte | Regra para a fábrica [P] |
|---|---|---|
| Devolver o erro do validador ao modelo funciona melhor que tentar de novo às cegas. Mensagens com o valor aceito servem de correção. | dev.to (pavelespitia) e dev.to (novaelvaris) | Devolver o erro com o valor aceito. No máximo 2 ou 3 tentativas. |
| Saída restrita por esquema garante a forma do JSON, não o conteúdo certo. | dev.to (inferable) | Validar do lado de fora, mesmo com saída restrita. |
| Modelos pequenos (7 a 9 bilhões de parâmetros) falham quase sempre no formato com prompt ingênuo. Otimizar o prompt fecha boa parte da diferença. Outro artigo diz que a estratégia de prompt pesa mais que o tamanho do modelo. | arXiv 2602.14743 e arXiv 2605.02363 | Melhorar o prompt antes de trocar por um modelo maior. |
| Quebrar um esquema grande em pedaços menores funcionou melhor que repetir o esquema inteiro. | dev.to (pavelespitia, segundo artigo) | Dividir fichas grandes em partes menores. |

## Geração de 3D por programa

Estes trabalhos foram lidos só pelos resumos.

- ShapeCraft: grafo de formas com volumes-limite, usando vários agentes.
- Proc3D: grafo compacto de operações, independente de motor, mais compacto que script de Blender.
- ShapeLib: biblioteca de funções de forma reutilizáveis.
- Texto para CadQuery: modelos maiores erram menos.

## O que a fábrica já faz [M]

- A IA só edita fichas JSON.
- Posição por âncora com nome, nunca por coordenada.
- Rotação por nome (frente, esquerda, tombar_direita), nunca por sinal.
- Erro com "você quis dizer".
- Portões P0, P1 e P2 devolvem a regra, o valor medido e o conserto.
- Começar sempre de uma ficha que funciona.
- Cartões de uma página por tarefa.

## O que ficou sem fonte

- Nenhum teste foi feito com um modelo pequeno de verdade operando a fábrica. Esta é a maior lacuna.
- Os trabalhos de 3D por programa foram lidos só pelos resumos.

## Fontes

- https://dev.to/pavelespitia/structured-output-from-local-llms-json-that-never-breaks-ollama-zod-5d09: texto sobre saída estruturada de LLMs locais e o ciclo de correção com o validador.
- https://dev.to/novaelvaris/json-first-prompting-valid-structured-output-plus-a-repair-loop-2hkb: texto sobre JSON primeiro e ciclo de reparo.
- https://dev.to/inferable/adding-structured-outputs-as-a-feature-to-any-llm-4pel: texto sobre saída restrita por esquema, que garante a forma e não o conteúdo.
- https://arxiv.org/pdf/2602.14743: estudo citado para modelos pequenos que falham no formato com prompt simples, e para a otimização de prompt.
- https://arxiv.org/pdf/2605.02363: artigo citado para a tese de que a estratégia de prompt pesa mais que o tamanho do modelo.
- https://dev.to/pavelespitia/structured-security-findings-from-a-7b-model-the-schema-that-stopped-breaking-3n5b: relato sobre um modelo de 7 bilhões de parâmetros e a quebra do esquema em pedaços.
- https://arxiv.org/pdf/2510.17603: ShapeCraft, grafo de formas com volumes-limite e vários agentes.
- https://arxiv.org/html/2601.12234: Proc3D, grafo compacto de operações, independente de motor.
- https://arxiv.org/abs/2502.08884v1: ShapeLib, biblioteca de funções de forma reutilizáveis.
- https://arxiv.org/pdf/2505.06507v1: artigo sobre geração de texto para CadQuery, em que modelos maiores erram menos.
