# Cartão: monstro novo

1. Escolha o arquétipo (plano de corpo). `python -m fabrica listar arquetipo` mostra os 20:
   `heroi_solto`, `bipede_articulado`, `bipede_curvado`, `bipede_bruto`, `bipede_digitigrado`, `quadrupede_cursor`,
   `quadrupede_ungulado`, `quadrupede_baixo`, `hexapode`, `aracnideo`, `corrente`, `nadador`, `alado`, `dragao`,
   `multicabeca`, `flutuante`, `gosma`, `enraizado`, `constructo`, `objeto_animado`.
   Veja todos lado a lado em `saida/_arquetipos/galeria.png` (`python -m fabrica arquetipos`).
2. Copie um monstro que usa esse arquétipo, ou comece assim:

```json
{
 "id": "monstro.lobo_de_cinza", "tipo": "monstro", "versao": 1, "nome": "Lobo de Cinza",
 "arquetipo": "quadrupede_cursor", "tier": 2, "pegada_ladrilhos": 1,
 "lore": "Uma linha de historia.",
 "materiais": [
  {"nome": "corpo", "como": "couro", "rampa": "pelo_cinza"},
  {"nome": "detalhe", "como": "osso"},
  {"nome": "escuro", "como": "escuro"},
  {"nome": "olho", "como": "brilho_brasa"}
 ],
 "extras": {
  "Cabeca": [{"op": "caixa", "tam": [1, 3, 2], "em": "cranio.topo", "desloc": {"direita": 2, "baixo": 1}, "material": "corpo"}]
 },
 "acabamentos": [{"tipo": "sangue_escorrido", "forca": 0.3, "pecas": ["Cabeca"]}]
}
```

3. O que cada campo faz:
   - `materiais`: os quatro nomes do arquétipo (`corpo`, `detalhe`, `escuro`, `olho`) com outra cor. `como` = material
     da tabela (`registro/paletas/materiais.json`); `rampa` = outra rampa de cor (`registro/paletas/`).
     A lista **substitui** a do arquétipo: mantenha os quatro nomes. Pode acrescentar outros.
   - `extras`: formas a mais por peça do arquétipo (chifre, placa, relicário). Veja `cartoes/forma.md`.
   - `acabamentos`: `musgo_em_cima`, `sangue_escorrido`, `ferrugem_nas_arestas`, `pintas`, `listras`.
   - `+clipes`: clipes a mais (ex.: `Susto`). Os do arquétipo já vêm: Parado, Andar, Ataque, Dano, Morte.
4. `python -m fabrica construir lobo_de_cinza` e siga os consertos.
5. Dez variantes = dez fichas curtas com `"herda": "monstro.lobo_de_cinza"`, mudando pelo menos 3 de:
   rampa, extras, acabamento, porte.

Erros comuns: esquecer um dos quatro materiais; `extras` numa peça que não existe (a mensagem lista as peças);
detalhe de 1 voxel solto no ar (encoste na peça).

**Detalhe mínimo (portão `detalhe_minimo`):** toda criatura precisa de 1000 voxels ou mais e de 8 ossos ou mais.
Os 20 arquétipos já passam (11 a 25 ossos). Se a sua variante reprovar, veja em `cartoes/forma.md` os campos
`segmentos`, `seguir_pai` e `repetir`.
