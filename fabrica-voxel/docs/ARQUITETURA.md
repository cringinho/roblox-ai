# Fábrica de Voxel v4 — Arquitetura e contrato

Este arquivo é o contrato técnico da fábrica. Quem implementa um módulo lê este arquivo inteiro antes.
Quem só vai **produzir assets** não precisa dele: leia `AGENTS.md` e o cartão da tarefa em `cartoes/`.

## 1. O que a fábrica é

Uma esteira em Python (numpy + Pillow, sem Blender, sem IA de imagem) que transforma uma **ficha** JSON
em um asset voxel completo: modelo, rig, animações, arquivos para o Roblox, arquivos para venda, folhas de
conferência e relatório de auditoria.

```
ficha.json ──P0──> forma ──> pintura ──> rig ──> clipes ──P1──> malha/export ──P2──> folha ──P3──> registro
 (dados)   esquema  voxels    cor        ossos    30 fps  geometria  GLB/.vox/Luau  arte    revisão   saídas
```

Princípios que não se negociam:

1. **Tudo é dado.** Raça, item, monstro, estrutura, golpe: um arquivo no `registro/`. A fábrica só lê arquivos.
2. **Classes, nunca pares.** Gera-se por classe de corpo, de cabeça e de pegada. Nada é feito por par raça × item.
3. **Peça rígida.** Nenhum voxel estica. Cada peça gira inteira; junta com sobreposição; corpo longo vira corrente.
4. **Eixos iguais em todo osso.** O repouso de todo osso tem os eixos do modelo. "Inclinar 30° para a frente" é o mesmo número em qualquer junta.
5. **Número antes de gosto.** Tudo que pode ser medido é medido (P1 e P2) antes de alguém olhar.
6. **O que se confere é o que toca.** Os clipes são assados (30 fps) na fábrica, conferidos quadro a quadro, e o jogo toca exatamente esses quadros.
7. **Poucos graus de liberdade.** A ficha usa nomes, âncoras e inteiros de voxel. Nunca coordenada absoluta em studs, nunca sinal de ângulo cru.
8. **Determinismo.** Mesma ficha + mesma semente = mesmos bytes. Sem `random` global, sem relógio.

## 2. Convenções (valem em todo módulo)

| Assunto | Regra |
| --- | --- |
| Unidade | stud. Chão em Y = 0. Origem do modelo no chão, no centro da pegada (footprint). |
| Eixos | +Y cima. **Frente = −Z.** +X = lado direito da criatura (`_D`), −X = esquerdo (`_E`). Destro. |
| Voxel (corte) | `mundo` 0,25 · `grade` 0,125 · `perto` 0,0625 · `susto` 0,03125 stud. Uma peça usa um corte só. |
| Grade | arrays numpy indexados `[x, y, z]`. Centro do voxel `(i,j,k)` = `origem + (i+0.5, j+0.5, k+0.5) * v`. `origem` é múltiplo de `v`. |
| Ladrilho | 4 studs. Classes de herói: P = 3 studs (24 voxels), M = 4 (32), G = 5 (40), no corte `grade`. |
| Nomes de peça/osso/soquete | PascalCase sem acento: `Cabeca`, `Tronco`, `Mao_D`, `Pe_E`, `Cauda_3`. Sufixo `_D`/`_E` do ponto de vista da criatura. |
| Ids do registro | minúsculas com espaço de nome: `linhagem.fada`, `item.espada.lamina_curva`. Versão: `"versao": 2`. O id nunca muda. |
| Ângulo na ficha | graus, com nome semântico: `frente` (topo vai para −Z), `esquerda` (vira para o lado `_E`), `tombar_direita` (topo vai para +X). |
| Composição de rotação | `R = Ry(esquerda) · Rx(−frente) · Rz(−tombar_direita)`. No Roblox: `CFrame.fromEulerAnglesYXZ(rad(-frente), rad(esquerda), rad(-tombar_direita))`. |
| Quaternion | ordem `[x, y, z, w]`, unitário. |
| Tempo | segundos. Clipes assados a 30 fps. |
| Cor | hex `#RRGGBB` maiúsculo. Só cores de rampas declaradas. Nada em preto ou branco puros. |
| Idioma | português sem acento em identificadores; com acento em textos. |

Deslocamentos na ficha são sempre semânticos e em voxels inteiros do corte da peça:
`{"frente": 2, "cima": 1, "direita": -3}` (negativo = sentido oposto). Internamente:
`dx = direita`, `dy = cima`, `dz = −frente`.

## 3. Modelo de dados (em `fabrica/nucleo/contrato.py`)

- `Grade`: `v`, `origem`, `mat` (uint8, 0 = vazio, índice em `Modelo.materiais`), `cor` (uint16, índice em `Modelo.cores`, 0 = sem cor).
- `Peca`: `nome`, `osso`, `grade`. Peças podem se sobrepor no espaço (junta sobreposta): cada peça tem a própria grade em coordenadas de repouso do modelo.
- `Osso`: `nome`, `pai`, `pivo` (studs, repouso, espaço do modelo), `papel`, `limites`, `mola`.
- `Soquete`: `nome`, `osso`, `pos` (studs, repouso).
- `Clipe`: `nome`, `duracao`, `fps`, `laco`, `ossos`, `trans [n,nb,3]`, `rot [n,nb,4]`, `escala [n,nb,3] | None`, `marcadores`, `vel_raiz`.
- `Modelo`: `id`, `nome`, `pecas`, `ossos`, `soquetes`, `materiais`, `cores`, `clipes`, `meta`.

Cinemática direta: a transformação de um osso leva **coordenadas de repouso do modelo** para a pose:

```
M_osso = M_pai · T(pivo) · R(repouso) · T(trans) · R(rot) · S(escala) · T(−pivo)
```

Como o repouso não tem rotação, os voxels de uma peça ficam em coordenadas de repouso e basta aplicar `M_osso`.
No Roblox isso é `Motor6D.C0 = pivô no espaço da peça-mãe`, `C1 = pivô no espaço da peça-filha`, `Transform = CFrame(trans) * rot`.

Quadros de um clipe: `n = round(duracao * fps)` se `laco` (o quadro `n` é o quadro 0), senão `n = round(duracao * fps) + 1`.

## 4. Registro

```
registro/
  paletas/        rampas e materiais
  partes/         macros de forma reutilizáveis (cabeças, chifres, lâminas, ...)
  arquetipos/     20 planos de corpo: esqueleto-modelo, receita padrão, clipes
  classes/        corpo (P1..G3), cabeca (redonda, longa, larga, alta), pegada (uma_mao, ...)
  linhagens/      14 linhagens jogáveis
  tracos/         orelhas, chifres, asas, caudas, antenas (com volume protegido e regras por slot)
  aparencia/      olhos, bocas, sobrancelhas, cabelos, marcas
  itens/          por slot; itens de mão declaram classe de pegada e 3 pontos
  conjuntos/      conjuntos de equipamento
  monstros/       fichas de monstro (herdam de um arquétipo)
  estruturas/     famílias do kit de quartos, marcos, props
  golpes/         fichas de golpe por classe de pegada
  _esquemas/      esquema de cada tipo (gerado do código, para consulta)
```

Regras do registro:

- Todo arquivo tem `id`, `tipo`, `versao`. O nome do arquivo é o id sem o prefixo do tipo.
- `herda`: id de outro arquivo do mesmo tipo (ou de um arquétipo). Só se escreve o que muda. Fusão profunda; lista substitui lista, a não ser com a chave `"+formas"` (acrescenta).
- A fábrica nunca escreve dentro de `registro/`. Saídas vão para `saida/<id>/`, com `relatorio.json` (assetId, hash, status entram ali).
- P0 recusa campo desconhecido. A mensagem diz o campo, os valores aceitos e um exemplo.

## 5. Linguagem de forma

Cada peça é uma lista de operações, executadas em ordem, na grade da peça.
Unidade: voxel inteiro do corte da peça. Posição: âncora + deslocamento semântico.

```json
{ "op": "caixa", "nome": "cranio", "tam": [12, 11, 11], "raio": 3,
  "em": "base", "material": "pele" }
{ "op": "elipsoide", "tam": [14, 6, 13], "em": "cranio.topo", "desloc": {"cima": -2},
  "material": "cabelo", "modo": "uniao" }
{ "op": "estampa", "em": "cranio.frente", "desloc": {"cima": 1}, "profundidade": 1,
  "linhas": ["B.....B", "BP...PB", "BB...BB"], "legenda": {"B": "olho_branco", "P": "olho_pupila"} }
```

- **Primitivas:** `caixa` (com `raio` e `chanfro`), `elipsoide`, `capsula` (afina de `r0` a `r1`), `cilindro`, `cone`, `toro`, `cunha`, `perfil_revolucao`, `perfil_extrusao`, `estampa`, `voxels` (lista explícita, último recurso).
- **Modo:** `uniao` (padrão), `uniao_suave` (com `k` voxels), `cortar`, `intersectar`, `pintar` (só troca o material de voxels que já existem).
- **Âncoras:** `centro`, `topo`, `base`, `frente`, `tras`, `esq`, `dir` e combinações (`topo_frente`), da própria peça (`"em": "topo"`), de uma forma nomeada (`"cranio.topo"`) ou de outra peça (`"Tronco.topo"`). A âncora fica na face; a forma nova é centrada nela e, por padrão, encosta por fora (`"encaixe": "fora" | "dentro" | "centro"`).
- **Simetria:** `"espelhar": true` repete a operação no outro lado. Assimetria proposital é uma operação sem espelho.
- **Parte de biblioteca:** `{ "parte": "chifre.curvo", "em": "Cabeca.topo", "lado": "ambos", "params": {"comprimento": 6} }`. Partes são macros em `registro/partes/`.
- **Formas menores que 1 voxel somem.** O P0 avisa quando `tam` tem dimensão menor que 1 ou espessura menor que a mínima do corte.

## 6. Pintura

A cor nasce de **material + rampa + regra**, nunca de ruído por voxel.

1. Cada material aponta para uma rampa (4 a 7 tons, sombra fria e luz quente) e um perfil (`pele`, `tecido`, `couro`, `metal`, `osso`, `pedra`, `madeira`, `cabelo`, `fungo`, `brilho`).
2. Passes em ordem: degrau de luz pela normal suavizada (não pelo degrau do voxel) → oclusão só nas dobras e contatos → borda clara só em aresta convexa voltada para a luz (na crista, não em toda face de cima) → padrão lógico do material (trama, veio, placa, escama, mecha) → acabamentos pedidos na ficha (`musgo_em_cima`, `sangue_escorrido`, `ferrugem_nas_arestas`, `costura`, `rebites`, `rachadura`, `listras`, `gradiente_vertical`) → limpeza de voxel órfão de cor.
3. Luz de pintura: de cima, da frente e da esquerda da tela (da direita da criatura). É luz de forma, discreta: o Roblox ilumina por cima.
4. Estrutura de valor: três grupos (escuro, médio, claro) mais brilho. Alvo por tipo de asset no perfil de auditoria.
5. Brilho (`Neon`) só em voxels de material `brilho`; vira malha `<Peca>_Brilho`.

## 7. Rig e animação

- **Junta sobreposta:** a peça-filha começa com uma esfera centrada no pivô, 1 voxel mais larga que o osso, e a mãe cobre esse ponto. A esfera não muda quando gira, então a junta não abre em ângulo nenhum.
- **Pivô** em canto da grade (múltiplo de `v`).
- **Camadas do clipe (todas assadas):** poses-chave com curvas → locomoção por fórmula (Froude, fase, apoio, pé travado por IK de 2 ossos com vetor-polo) → regras de tronco (quadril lidera, ombro segue) → molas em ossos soltos, simuladas em laço fechado → respiração e micro-movimento em harmônicos inteiros do laço → squash e stretch em peças marcadas.
- **Estilos de movimento** (modificadores aplicáveis a qualquer arquétipo): `natural`, `pesado`, `eterio`, `manco`, `espasmodico`, `marionete`, `staccato`.
- **Nomes canônicos de clipe:** `Parado`, `Andar`, `Correr`, `Alerta`, `Preparar`, `Ataque`, `Dano`, `Morte`, `Susto`, mais específicos (`Pairar`, `Voar`, `Pulo`, `Golpe_<classe>_<nome>`). Apelidos antigos aceitos na leitura: `Ocioso` → `Parado`, `Passo`/`Mover` → `Andar`.
- **Marcadores:** `Pisada`, `Impacto`, `Golpe`, `Queda`, `FimSopro`, `Aviso`.
- **Herói:** trajetórias medidas em H (altura da classe), então as 14 linhagens e os 3 tamanhos dividem os mesmos clipes.
- **Golpe:** ficha com plano, arco da ponta, tempos `[preparação, ação, contato, seguimento, recuperação]`, regra de tronco e `acerto`. A fábrica anima a ponta do item; a pegada segue.

No jogo: o servidor só publica estado (atributos e eventos); cada cliente toca os quadros assados com transição por inércia, e aplica molas de tempo real e hit-stop só nos personagens próximos.

## 8. Portões

| Portão | Quando | O que mede | Quem decide |
| --- | --- | --- | --- |
| **P0** esquema | ao ler a ficha | campos, tipos, ids que existem, âncoras que existem, tamanhos mínimos | script, recusa com mensagem que ensina |
| **P1** geometria e movimento | após forma e após clipes | voxel solto, espessura mínima, junta coberta em ângulo máximo, colisão entre peças por quadro, deslize de pé, centro de massa sobre o apoio, laço que fecha, giro máximo por quadro, orçamento de triângulos, brilho %, regras de golpe | script, recusa |
| **P2** arte | após pintura | silhueta na câmera da grade, grupos de valor, estrutura da paleta, ruído de cor, hierarquia de detalhe e descanso, assimetria, rosto legível, coesão de densidade | script, nota 0–100 com mínimo por tipo |
| **P3** revisão visual | na folha de conferência | rubrica A1–A10 com âncoras, respondida olhando a folha | humano, ou IA com visão seguindo o cartão |

Um asset só recebe `status: "aprovado"` no relatório com P0, P1 e P2 passando. O P3 muda para `"publicavel"`.

## 9. Saídas por asset (`saida/<id>/`)

| Arquivo | Para quê |
| --- | --- |
| `modelo.glb` | Roblox (3D Importer) e lojas. Um nó por osso, uma malha por peça rígida (`<Peca>`), brilho em `<Peca>_Brilho`. Eixos do Roblox, em studs, sem giro. Animações embutidas para conferência e para lojas. |
| `modelo.vox` | MagicaVoxel: retoque à mão e lojas. Um modelo por peça. |
| `modelo.obj` + `.mtl` + `atlas.png` | lojas. |
| `Dados_<Id>.luau` | ModuleScript: rig (nome, pai, pivô, centro da malha), soquetes, e opcionalmente as caixas para montar com Parts sem importar nada. |
| `Clipes_<Id>.luau` | ModuleScript com os quadros assados (compartilhado por classe quando possível). |
| `folha.png` | folha de conferência: 6 vistas, 3/4, cinza, silhueta, tamanho real na câmera da grade, paleta. |
| `anim_<Clipe>.png`, `anim.gif` | tira de 8 quadros e GIF de cada clipe. |
| `icone_64.png`, `retrato_64.png` | pixel art renderizada do próprio voxel, presa à paleta, contorno de 1 px. |
| `relatorio.json` | P0–P2, métricas, orçamento, hash, semente, versão da fábrica. |
| `proveniencia.json` | ficha, semente, hash de cada saída, data, autor humano responsável: base da garantia de originalidade. |

## 10. Módulos Python

```
fabrica/
  __main__.py          CLI:  python -m fabrica <comando>
  esteira.py           construir(id) de ponta a ponta
  registro.py          carregar, herdar, validar (P0)
  nucleo/
    contrato.py        tipos e matemática comum                 (pronto; não mude assinaturas)
    sdf.py             primitivas e combinações em grade
    forma.py           interpreta a linguagem de forma, âncoras, partes
    paleta.py          rampas, materiais, quantização
    pintura.py         passes de cor
    render.py          rasterizador ortográfico: vistas, folha, tiras, GIF, ícone
    rig.py             esqueleto, FK, IK de 2 ossos, junta sobreposta, soquetes
    anim.py            camadas, curvas, molas, locomoção, assar clipes
    golpe.py           ficha de golpe -> clipe
    malha.py           malha gulosa, cor por vértice e/ou atlas
    glb.py             escrita e releitura de GLB
    vox.py, obj.py     MagicaVoxel e OBJ
    luau.py            emissão dos ModuleScripts de dados
    auditoria.py       P1 e P2
    proveniencia.py    hashes e registro de origem
  heroi/               corpo-base, cabeça, aparência, traços, casca, recorte, matriz de prova
  arquetipos/          código de locomoção e receita padrão de cada arquétipo
  estrutura/           kit de quartos, montagem, corte de um terço, props
```

CLI (todas as saídas em português, erros com o conserto):

```
python -m fabrica validar <id | caminho>          P0
python -m fabrica construir <id> [--so forma|pintura|clipes] [--semente N]
python -m fabrica folha <id>                      regenera só as imagens
python -m fabrica auditar <id>                    P1 + P2, imprime a nota e as 3 piores métricas
python -m fabrica lote <arquivo.txt | padrão>     constrói vários, resume em tabela
python -m fabrica matriz <id-do-item | id-do-traço>   matriz de prova
python -m fabrica listar <tipo>                   o que existe no registro
python -m fabrica novo <tipo> <id> --de <id-modelo>   copia uma ficha-modelo
python -m fabrica explicar <tipo>                 campos, valores aceitos e exemplo
```

## 11. Roblox (`roblox/`)

Runtime genérico, dirigido por dados: nenhum script por criatura.

```
ReplicatedStorage/Fabrica/
  Rig.luau            monta Motor6D a partir de Dados_<Id> (idempotente), cria Attachments dos soquetes
  Animador.luau       cliente: toca clipes assados, inércia, molas, LOD por distância, hit-stop
  ConstrutorParts.luau  monta o modelo com Parts a partir das caixas (rota sem importação)
  Equipar.luau        cascas por classe, itens nos soquetes, mostrar/esconder por slot
  CameraJogo.luau     grade 2.5D (Scriptable, FOV baixo) e dungeon (primeira pessoa), com o mergulho
  MovimentoGrade.luau passo por casa de 4 studs; servidor decide, cliente desenha
  MovimentoLivre.luau dungeon
  Dados/, Clipes/     módulos gerados pela fábrica
ServerScriptService/FabricaServidor.server.luau
StarterPlayer/StarterPlayerScripts/FabricaCliente.client.luau
```

Regras de código: `game:GetService`, `pcall` em tudo que toca asset ou rede, `WaitForChild`/`FindFirstChild`,
instâncias que faltarem são criadas por código, cliente e servidor isolados, comentário no topo dizendo onde colar.


## Adendo 4.1: empunhadura, cadeias e detalhe mínimo

- **Giro de repouso por osso** (`Osso.repouso`, quaternion). A grade continua reta; a peça gira como corpo rígido em
  torno do pivô. No Roblox entra no `C0` do Motor6D (`Rig.luau`); no GLB, na rotação do nó. As trilhas dos clipes
  Luau não o incluem; os canais do GLB incluem, porque no glTF o canal substitui a rotação do nó.
- **`fabrica/nucleo/colisao.py`**: `escolher_empunhadura` (giro de repouso do item por medição),
  `desviar_itens` (afasta a mão nos quadros com contato; uma direção por clipe, alargada e suavizada no tempo).
- **`anim._golpe`**: recuperação pela guarda; `centro_H` na ficha do golpe; a mão desfaz o giro de repouso do item.
  `heroi/cli._ajustar_golpe` procura plano, centro e raio por herói.
- **Cadeias** (`montagem._segmentar`): `"segmentos"` no osso corta a peça; pivôs dos filhos ficam na reta do pivô do
  osso. `anim._perna_ik` (IK analítico de dois ossos na camada `passos`) e `anim._seguir_cadeias`
  (seguimento automático de segmentos sem camada). `modelo.meta["cadeias"]` e `["seguir"]` guardam a estrutura.
- **Forma**: `"repetir"` expande uma forma em n cópias.
- **Portões novos no P1**: `um_tamanho_de_voxel`, `item_atravessa_corpo` (2% dos voxels do item, todo quadro),
  `detalhe_minimo` (monstro: 1000 voxels e 8 ossos).
- **Correção**: no modo `perna` rígido a perna balançava ao contrário (o pé ia para a frente durante o apoio).
- Pesquisa de apoio: `docs/pesquisa/04-empunhadura-e-ossos.md`.
