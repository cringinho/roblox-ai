# Cartão: item de mão e conjunto de equipamento

**Item de mão** (`registro/itens/`): um modelo em pé, com três soquetes obrigatórios.

```json
{"id": "item.machado", "tipo": "item", "versao": 1, "nome": "Machado", "slot": "mao", "pegada": "uma_mao",
 "materiais": ["madeira_escura", "ferro"],
 "pecas": [{"nome": "Item", "formas": [
   {"op": "caixa", "nome": "cabo", "tam": [1, 16, 1], "em": "chao", "material": "madeira_escura"},
   {"op": "caixa", "nome": "lamina", "tam": [1, 5, 4], "em": "cabo.topo", "encaixe": "dentro", "desloc": {"frente": 2}, "material": "ferro"}]}],
 "soquetes": [{"nome": "Pegada", "osso": "Item", "em": "cabo.base", "desloc": {"cima": 4}},
              {"nome": "Ponta", "osso": "Item", "em": "cabo.topo"}, {"nome": "Base", "osso": "Item", "em": "cabo.base"}]}
```

`pegada`: `uma_mao`, `duas_maos`, `haste`, `escudo`, `luz`, `arremesso`, `arco`. O item cresce para cima da pegada
até a ponta. Se a pegada ficar alta demais, o item entra no chão e o P1 avisa.

**Conjunto** (`registro/conjuntos/`): não se modela peça de roupa. Declara-se material por slot e a fábrica gera
a casca a partir do corpo, para os 3 tamanhos e os 3 corpos.

```json
{"id": "conjunto.guarda", "tipo": "conjunto", "versao": 1, "nome": "Guarda do Adro",
 "materiais": ["ferro", "aco", "ouro", "tecido_vinho", "couro_escuro"],
 "elmo": {"tipo": "fechado", "material": "ferro", "detalhe": "ouro", "crista": true},
 "tronco": {"faixas": [{"ate": 0.25, "material": "couro_escuro"}, {"ate": 1, "material": "ferro"}],
            "emblema": {"linhas": [".A.", "AAA", ".A."], "material": "ouro"}},
 "luvas": {"material": "ferro", "detalhe": "aco"}, "botas": {"material": "ferro", "detalhe": "couro_escuro"},
 "ombreiras": {"material": "aco", "detalhe": "ouro", "so_uma": "D"},
 "capa": {"material": "tecido_vinho"}, "mao_principal": "item.espada_longa"}
```

Slots: `elmo` (`fechado` ou `aberto`) **ou** `chapeu`, `tronco` (`faixas` por altura, de baixo para cima), `luvas`,
`botas`, `ombreiras`, `capa`, `mao_principal`, `mao_secundaria`.

**Sempre rode a matriz de prova:** `python -m fabrica matriz guarda`. Ela veste o conjunto em 6 corpos de teste
(fada P, gnomo P, elfo M, demônio M, draconato G, gigante G) e mede: voxel solto, item partido pelo recorte,
item no chão. Olhe `saida/_matriz/guarda.png`. Orelha, chifre, asa e cauda abrem o próprio furo sozinhos.
