# Cartão: linhagem, traço, rosto, cabelo

Uma linhagem **escolhe** entre classes que existem; nunca cria classe.

- Tamanho: `P` (3 studs), `M` (4), `G` (5). Corpo: `1` ombro largo, `2` quadril largo, `3` robusto.
- Cabeça: `redonda`, `longa` (focinho), `larga`, `alta`. A cabeça tem o mesmo tamanho nos três tamanhos.
- Arquivo: `registro/linhagens/<id>.json`. Copie um parecido.

```json
{"id": "linhagem.elfo", "tipo": "linhagem", "nome": "Elfo", "tamanho": "M", "classe_cabeca": "alta",
 "tracos": ["orelhas.longas"],
 "rampas": {"pele": ["pele_marfim", "pele_oliva"], "cabelo": ["cabelo_castanho", "cabelo_prata"], "olhos": ["moss", "abyss"]},
 "cabeca": {"roupa": "moss[1:6]"},
 "predefinicoes": [{"o": 2, "b": 1, "s": 2, "h": 3, "cp": 0, "ch": 0, "co": 0}],
 "jeito": "eterio", "lore": "Uma linha."}
```

- `tracos`: arquivos de `registro/tracos/` (orelhas, chifres, asas, cauda, barba, gorro, gola...). Um de cada tipo.
- `predefinicoes`: 6 rostos prontos. `o` olhos, `b` boca, `s` sobrancelha, `h` cabelo (1 a 10), `cp`/`ch`/`co` índices
  das rampas de pele, cabelo e olhos. As opções estão em `registro/aparencia/`.
- `cabeca`: ajustes da linhagem: `focinho` `[l, a, p]`, `olhos_brilho`, `olho_unico`, `sem_cabelo`, `perfil_pele`
  (`pedra`, `osso`), `corpo_padrao`, `roupa` (rampa da roupa inicial).
- `jeito`: `natural`, `pesado`, `eterio`, `staccato`, `espasmodico`, `manco`.

Comandos: `python -m fabrica heroi elfo --predef 2 --corpo 2 --conjunto placas_de_cripta`;
`python -m fabrica elenco` (todas lado a lado); `python -m fabrica elenco --conjuntos` (vestidas).

Traço novo: copie um de `registro/tracos/`. Formas encadeadas (`"em": "b.topo"`) evitam pedaço flutuando.
`regras` diz o que acontece com cada slot: `esconde`, `recorta`, `abre_embaixo`, `passa_por_cima`, `nada`.
Depois de criar um traço, rode a matriz de todos os conjuntos.
