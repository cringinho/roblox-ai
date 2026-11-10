# 15 — Lições da Forja Alta (a Hidra adulta do dono)

Fonte: o código do próprio dono, em `legado/forja_alta/` (`hidra.py`, `hidra_adulta.py`, `voxforja.py`, `herois.py`).
Li as funções de forma, de cor e de pose. É a referência de qualidade do projeto: tudo aqui já foi aprovado por ele.
O que a Fábrica v4 ainda não fazia está marcado **[FALTAVA]**; o que já faz, **[JÁ FAZ]**.

## Veredito

1. A Hidra não é melhor por ter mais voxels. É melhor porque **forma, cor e movimento seguem a anatomia**.
2. A forma é orgânica: cápsulas que afinam ao longo de uma curva, com uma esfera em cada junta.
3. A cor é um padrão com lógica (escamas em tijolo, anéis por segmento, ventre, fendas), não um degradê de luz.
4. O movimento é uma soma de muitas ondas pequenas, cada uma com período e atraso próprios, e de trancos amortecidos.
5. Os meus arquétipos de caixa perdem nos quatro pontos. O conserto é no motor, não modelo a modelo.

## Forma

| Técnica da Forja Alta | Número no código | Estado na v4 |
| --- | --- | --- |
| Pescoço e cauda seguem uma curva de Bézier cúbica, cortada em elos | 6 elos por pescoço, 12 na cauda | [FALTAVA] não havia forma em curva |
| Cada elo é uma cápsula que afina, mais uma esfera em cada ponta | raio cai 40% da base à cabeça; esfera com 1,02 do raio | [FALTAVA] só caixa cortada em segmentos |
| A esfera da junta pertence aos dois elos | a junta gira sem abrir fresta | [JÁ FAZ] em parte (campo `junta`) |
| Espinhos dorsais nascem de cada elo, não do corpo | 2 por elo, a 30% e 75% do comprimento | [FALTAVA] |
| Cabeça do herói é elipsoide; corpo é cápsula | `ell` e `cap` em `herois.py` | [FALTAVA] até hoje; cabeça agora tem raio alto |
| Olho escuro com um ponto de brilho no canto de cima | cor `olho` e `olho_brilho` | [JÁ FAZ] desde a atualização dos rostos |
| Limpeza: só fica o que está ligado ao pivô | `limpar_soltos` | [JÁ FAZ] portão `voxels_soltos` |

## Cor

| Técnica | Como é feita | Estado na v4 |
| --- | --- | --- |
| Escamas em tijolo | fileiras de altura `h`; borda escura de 1 voxel; 1 escama em 3 mais clara; fileiras alternadas deslocadas meia escama | [FALTAVA] |
| Anéis de tubo | número inteiro de anéis no elo e de escamas em volta (múltiplo de 3), para não haver emenda | [FALTAVA] |
| Coleira escura nas pontas do elo | 45% de um anel em cada ponta | [FALTAVA] é o que esconde a junta girando |
| Ventre | faixa de placas de outra cor na parte de baixo do tubo | [FALTAVA] |
| Dorso mais claro que os flancos | troca de trio de cores acima de certa altura | [JÁ FAZ] em parte (luz por cima) |
| Fendas que brilham | linha fina onde um ruído suave cruza 0,5 | [FALTAVA] |

## Movimento

Todas as amplitudes abaixo estão em radianos no código; converti para graus.

| Camada | O que faz | Números | Estado na v4 |
| --- | --- | --- | --- |
| Vida, sempre ligada | respira, passa o peso de um lado ao outro, gira um nada em três eixos | respiração 3,6 s com o peito crescendo 1,2 a 2%; peso 6 s e 0,28 stud; giros de 0,5 a 0,9 grau com períodos 6, 7 e 3,6 s | [FALTAVA] como camada; o Parado tinha 2 ondas |
| Lombo contra os ombros | a parte de trás gira ao contrário do peito, atrasada | 1,1 a 2,9 graus; atraso de 0,9 a 1,4 rad | [FALTAVA] |
| Peso no andar | o corpo vai para o lado do pé de apoio | 0,5 stud por ciclo | [FALTAVA] |
| Tranco da pisada | cada pisada afunda o corpo e ele volta oscilando | mola: frequência 1,4 Hz, amortecimento 3,6; pata da frente pesa 0,55, a de trás 0,4 | [FALTAVA] |
| Tranco que viaja | pescoço e cauda sentem a pisada depois do corpo | atraso de 0,05 s por elo; ganho cresce com o elo | [FALTAVA] |
| Pescoço | onda que viaja, mais uma segunda onda no dobro da frequência | atraso de 0,5 rad por elo; cada pescoço 2,1 rad defasado do vizinho | [JÁ FAZ] em parte (`fase_por_osso`) |
| Cabeça | balança sozinha em dois períodos e baixa quando a boca abre | períodos 3 s e 2,2 s; cabeça desce 0,35 do ângulo da mandíbula | [FALTAVA] o acoplamento com a mandíbula |
| Cauda de 12 elos | onda da base à ponta, crescendo; a ponta desenha uma elipse | guinada de 1,7 grau mais 1,1 por elo; atraso 0,5 rad por elo; arfagem no dobro da frequência, 90 graus defasada; a ponta cai | [JÁ FAZ] em parte; faltavam a elipse e a segunda onda lenta |
| Cauda contra o quadril | a cauda gira ao contrário do lombo | proporcional ao elo | [FALTAVA] |
| Pernas | IK de duas juntas, pé travado; o pé gira ao contrário para ficar plano e rola na ponta ao sair | o chão anda exatamente na velocidade do apoio | [JÁ FAZ] o IK; [FALTAVA] o pé plano |
| Núcleo | pulsa no ritmo do passo | 6 a 7% de escala, no dobro da frequência do passo | [JÁ FAZ] (escala em poses) |
| Ataque | inspira, segura, solta; treme em alta frequência durante a carga | tremor a cerca de 7 Hz; a cauda abre mais durante o rugido | [JÁ FAZ] (`poses` e `tremor`) |

## O que isso muda na fábrica

1. **Forma em curva**: uma operação `tubo` que recebe pontos de controle e raios e já devolve os elos com os ossos em cadeia.
2. **Padrões anatômicos na pintura**: `escamas`, `aneis` (com coleira nas juntas), `ventre` e `fendas`, aplicados por peça.
3. **Camadas novas de animação**:
   - `vida`: respiração por escala, troca de peso e três giros pequenos com períodos diferentes;
   - `impacto`: tranco amortecido a cada pisada, que viaja pelas cadeias com atraso por elo;
   - `passos` com pé plano, peso para o lado do apoio e afundar na pisada;
   - cauda com a ponta em elipse e segunda onda lenta.
4. **Laço longo com vários períodos**: num laço de 12 s cabem ondas de 6, 4, 3 e 2,4 s. O olho não acha a repetição.
5. **Regra de autoria**: nenhuma parte se move sozinha. Toda onda tem um vizinho que responde atrasado ou ao contrário.

## O que não aprendi daqui

- O código não mede nada sobre percepção; os números são escolhas do dono que deram certo nesta criatura.
- Não há regra para criaturas pequenas ou rápidas. Para elas valem os dossiês 01, 05, 06, 07, 13 e 14.
- Nada disso foi visto dentro do Roblox Studio.
