# Síntese: movimento natural (dossiês 12 a 17)

Números marcados como proposta não foram medidos em jogo. Teste antes de dar como certo.

## O que aprendemos em 10 linhas

1. O movimento parece vivo pelo acoplamento entre as partes, não pelo número de ossos. (dossiê 12)
2. Peça rígida parece contínua com esfera, peça intermediária ou sobreposição na junta. (dossiê 12)
3. Osso secundário, como cauda, orelha ou capa, precisa de mola de segunda ordem. (dossiê 13)
4. Jogos de referência usam poucas poses-chave e camadas procedurais por cima. (dossiês 13 e 16)
5. Invertebrado sem perna anda por uma onda nos ossos, de trás para a frente em minhoca e lagarta. (dossiê 14)
6. O olho lê vida pelos pés, que sobem e descem em arco e quase não deslizam. (dossiê 17)
7. Ataque precisa de aviso longo e legível, mostrado pela pose de início. (dossiês 14 e 16)
8. O golpe real dura menos de um quadro a 30 fps, então a antecipação do jogo deve ser mais longa. (dossiê 14)
9. Criatura maior passa mais devagar, e o ritmo deve vir do porte. (dossiê 17)
10. O laço fica vivo com períodos que não se dividem e variação entre ciclos. (dossiês 13 e 16)

## Quantos ossos um bom modelo tem

São propostas, ancoradas em poucos dados publicados (dossiê 12). Mín é o piso; ideal é o alvo.

| Classe | Mín | Ideal | Ossos que não podem faltar |
|---|---|---|---|
| Herói | 14 | 18-22 (+ até 6 secundários: capa 3, cabelo/pluma 2, bainha 1) | raiz, pelve, abdômen, peito, pescoço, cabeça, 2 ombros, 2x(braço, antebraço, mão), 2x(coxa, canela, pé) [+ ponta do pé] |
| Comum | 10 | 14-18 | raiz, pelve, tronco, pescoço, cabeça, 2 braços (2 segmentos), 2 pernas (2 segmentos), cauda 1-3 |
| Elite | 20 | 24-32 | comum + ombros, mãos/garras, mandíbula, 2-4 ossos de armadura/chifre (secundários), cauda 3-5 |
| Chefe | 30 | 36-48 (até 12 secundários) | elite + espinha de 3-5 segmentos, pescoço 2-3, cauda 5-8, 4-8 ossos de apêndice, olhos, 2 mandíbulas |
| Artrópode | 16 | 30-44 | raiz, abdômen, cefalotórax, cabeça, 2 quelíceras (2 segmentos cada), 2 pedipalpos, pernas 3-4 segmentos x 6 ou 8, 2 antenas x 2 |
| Serpente/verme | 10 | 16-24 | raiz, cabeça, mandíbula, 12-20 segmentos de corpo, 2-3 de cauda |
| Alado | 20 | 28-40 | base (comum/elite/chefe) + por asa: ombro, braço, antebraço, mão, 2-3 dedos de membrana; cauda 4-6; pescoço 3 |

## As 12 regras de movimento natural

1. O pé de apoio não desliza: o olho percebe deslize acima de cerca de 21 mm. Dossiê 17 (resumo de busca).
2. Pé longe do ponto ideal levanta a 60% do alcance e pousa 40% à frente. Dossiê 16 (proposta).
3. O peito contra-gira 30 a 50% do giro da pelve. Dossiê 12 (proposta).
4. A cabeça contra-gira 50 a 70% da inclinação do peito. Dossiê 12 (proposta).
5. O ombro sobe 20 a 30% junto com o braço. Dossiê 12 (proposta).
6. O corpo sobe e desce duas vezes por passada, em 2 a 3% da altura. Dossiê 13 (proposta).
7. Cada segmento de cauda segue o anterior com 2 a 3 quadros de atraso. Dossiê 13 (proposta).
8. Oito pernas em dois grupos, A e B, defasados em 0,5 do ciclo. Dossiê 14 (proposta).
9. Frequência de passada: f = 3,35 x M^-0,130, com M em kg. A unidade não é declarada, provavelmente Hz. Dossiê 17.
10. Giro máximo do corpo: 720 graus/s (pequeno), 360 (médio), 180 (grande), 70 (gigante). Dossiê 16 (proposta).
11. Camadas de repouso com períodos que não se dividem, como 3,3 s, 7,1 s e 11,7 s. Dossiê 13 (proposta).
12. O ataque arma por 0,4 a 0,8 s e golpeia em 3 a 5 quadros. Dossiê 14 (proposta).

## Invertebrados

Dossiê 14, seção 9. "Sem dado": o dossiê não traz o valor.

| Tipo | Andar | Ataque | Ameaça |
|---|---|---|---|
| Aranha e escorpião | Grupos A e B em contrafase de 0,5; 2,5 a 3,5 Hz exibido (escorpião 2 a 2,5) | Arma 0,5 s; golpe 0,13 s; recuperação 0,5 s | Ergue-se por 1 a 3 s (aranha) ou ergue pinças e cauda (escorpião) |
| Inseto de 6 patas | Tripé, fases 0 e 0,5; 3 a 3,5 Hz exibido | Mandíbula abre 40 graus; arma 0,3 s; golpe 0,1 s | Levanta a frente por 1 a 2 s |
| Louva-a-deus | Passos lentos e pausas longas; 1,5 Hz exibido | Abre as patas 0,4 s; extensão de 90 graus em 0,13 s | Empina e abre asas por 1,5 s |
| Centopeia | Fase por segmento de 0,09 a 0,19 do ciclo; 2 a 3 Hz exibido | Cabeça recua 3 quadros e morde; golpe 0,13 s | Ergue a frente por 1 a 2 s |
| Minhoca e lagarta | Onda de trás para a frente; minhoca contrai 25%, 0,6 a 1 Hz; lagarta ergue 30%, 0,8 a 1 Hz | Sem dado | Sem dado |
| Polvo | Curva de 40 a 70 graus da base à ponta; alcance de 0,6 a 1,2 s | Sem dado | Muda de cor, estica os braços |
| Água-viva | Sino contrai 0,4 s e relaxa 1,4 s; 0,25 a 0,55 Hz | Sem dado | Sem dado |

## Tempos de ataque por porte

Os três dossiês marcam estes valores como proposta. O dossiê 13 separa por tipo de ataque, então liguei leve, médio, pesado e chefe a pequeno, médio, grande e colossal. Essa correspondência é minha.

| Porte | Antecipação | Golpe | Recuperação |
|---|---|---|---|
| Pequeno | 3 a 5 quadros (17 e 13); 0,08 a 0,15 s (16) | 2 a 3 quadros (17 e 13) | 5 a 8 quadros (17); 6 a 9 quadros (13) |
| Médio | 6 a 10 quadros (17); 6 a 9 quadros (13); 0,15 a 0,30 s (16) | 3 a 5 quadros (17); 3 a 4 quadros (13) | 9 a 14 quadros (17 e 13) |
| Grande | 10 a 16 quadros (17); 10 a 18 quadros (13); 0,30 a 0,60 s (16) | 4 a 7 quadros (17); 3 a 5 quadros (13) | 16 a 24 quadros (17); 14 a 24 quadros (13) |
| Colossal | 18 a 30 quadros (17 e 13); 0,60 a 1,10 s (16) | 6 a 10 quadros (17); 4 a 6 quadros (13) | 30 a 48 quadros (17); 20 a 40 quadros (13) |

## O que o olho vê primeiro quando está errado

Ordem minha, pelos vereditos do dossiê 17; nenhum estudo a ordenou. Medidas da tabela (c); limiares são propostas.

1. Pé desliza no apoio. Medida 1: falha acima de 0,02 m, escalado à humana.
2. Pé sobe e desce em reta. Medida 2: falha se a reta linear tem R² acima de 0,98.
3. Pernas fora de contra-fase. Medida 3: falha se a fase entre pés sai de 0,35 a 0,65.
4. Corpo sem peso. Medida 12: a pelve deve subir e descer ao menos 1,5% da altura.
5. Tudo em sincronia. Medida 9: falha se todos os atrasos entre elos ficam abaixo de 0,5 quadro.
6. Movimento linear. Medida 8: falha se a velocidade varia menos de 10%.
7. Estalo. Medida 7: falha se o jerk de pico passa de 8 vezes a mediana.
8. Simetria exata. Medida 10: falha se os dois lados diferem menos de 2%.
9. Tremor de ruído branco. Medida 13: falha se o espectro é plano.
10. Laço exato demais. Medida 11: falha se a variação entre ciclos é 0% ou acima de 15%.
11. Ataque sem aviso. Medida 15: falha se a antecipação fica 30% abaixo da tabela.

## O que ninguém conseguiu confirmar

- Ossos publicados de Monster Hunter, Dark Souls, Horizon e outros jogos. (dossiê 12)
- Limite oficial de peças por modelo no Roblox, e custo por junta. (dossiê 12)
- Acoplamento entre partes e mola por parte do corpo: só propostas. (dossiês 12 e 13)
- Palestras primárias não lidas: Rosen, Rain World, Overgrowth, Horizon e t3ssel8r. (dossiês 13 e 16)
- Spore: o dossiê 12 diz que leu o paper; o dossiê 16 diz que o PDF veio ilegível. (dossiês 12 e 16)
- Quadros oficiais por fase de ataque de Dark Souls, Monster Hunter, Hollow Knight, Hades e Ori. (dossiês 13 e 16)
- Varredura das antenas de barata e formiga; Hz dos pés de lesma e caracol. (dossiê 14)
- Duração do golpe de ferrão do escorpião e do bote de aranha-lobo e tarântula. (dossiê 14)
- Passada de besouro, lagosta, lula e estrela-do-mar. (dossiê 14)
- Limiar de deslize em porcentagem da passada; estudos de estalos e de simetria. (dossiê 17)
- Tempo até o olho notar o laço; se ruído 1/f parece mais natural que branco ou Perlin. (dossiê 17)
- Perda real ao assar a 30 fps e interpolar no motor: só dedução. (dossiê 17)
