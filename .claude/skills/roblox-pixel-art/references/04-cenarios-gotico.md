# 04 — Cenários góticos (backgrounds)

Fontes: dossiê `02-tecnica...` (seções 2.6–3), análise das referências do usuário (catedral da "torre do arquimago" e forja) e o gerador `scene.cathedral`.

## 1. Bandas de valor para cena gótica escura [2.7]

| Banda | Uso | L_OKLab | Saturação | Matiz |
|---|---|---|---|---|
| B0 vazio | abóbada, sombras profundas | 0,12–0,20 | 25–50% | azul-violeta (nunca #000) |
| B1 arquitetura distante | naves laterais, colunas do fundo | 0,18–0,32 | ≤ 25% | frio |
| B2 arquitetura média/piso | colunas próximas, chão | 0,28–0,45 | 15–35% | frio a neutro |
| B3 jogo | cartas, personagens, interativos | 0,35–0,80 | 35–75% | livre |
| B4 luz e acento | vitrais, fogo, VFX, runas | 0,70–1,00 | 60–95% | quente ou joia |

Testes:
- B4 ocupa **10–20%** da área.
- A silhueta de B3 tem ΔL ≥ 0,20 em relação ao fundo imediato.
- Fundo atrás de UI: baixe a saturação (−20), o contraste (−15) e suba o brilho (+15). Saint11 usa "só uma cor" no fundo escuro. [C-20, C-21]
- Interiores: paredes com baixa saturação e baixa temperatura; móveis e detalhes do primeiro plano saturados e claros; loops longos e lentos dão clima. [C-19]

## 2. Anatomia da referência "catedral / torre do arquimago"
1. **Ponto focal:** dois vitrais em lanceta, o único croma alto da cena (joias: vermelho, ouro, violeta, ciano).
2. **Centro:** porta ogival quase preta. A perspectiva de 1 ponto puxa o olho para o meio, onde fica a UI.
3. **Arquitetura:** tijolos roxo-acinzentados em 2 tons + argamassa. A abóbada some no escuro em dither. Colunas cilíndricas com 3 tons.
4. **Estátuas aladas** em pedestais: silhueta escura com **rim light** colorido do lado do vitral.
5. **Piso polido:** xadrez em perspectiva + **reflexo espelhado** da parede, mais forte perto da linha do piso e sumindo em degraus, com **faixas de luz colorida** do vitral derramadas.
6. **Vinheta** nos cantos. Poeira (motes) no feixe.

Gerador: `pixelforge.scene.cathedral(pal, w=320, h=180)`. Usa ~22 cores da paleta ALTAR e quantiza no fim.

## 3. Anatomia da referência "forja"
- **Fonte de luz quente** (lareira em arco de tijolos) à esquerda. A poça de luz quente cai sobre o **piso de lajotas hexagonais**: intensidade `(1 − smoothstep(0,3r, r, d))^1,6`, 4–6 níveis, cada nível = 1 passo de uma rampa que vai de violeta-escuro a laranja (L-09). A elipse `dy·1,6` simula a perspectiva do chão.
- **Bigorna em primeiro plano:** silhueta escura com **rim light laranja** no lado do fogo (L-02: contraluz no lado iluminado).
- **Parede do fundo** em pedra fria e escura (contraste de temperatura com o fogo). As cartas penduradas são o segundo ponto de interesse.
- **Animação ideal:** palette cycling no fogo e nas brasas (TR-14), `fx.fire_loop` na lareira e `fx.embers_rising` subindo. Flicker que **só escurece** e jitter por linha (L-07, L-08).
- *Ainda não há gerador `scene.forge`.* Siga a estrutura do `cathedral` e as regras acima (ponto de melhoria nº 1).

## 4. Receita geral de cenário (ordem de pintura)
1. **Blocos de valor** (B0–B2) e linha do horizonte. A perspectiva de 1 ponto converge onde a UI fica.
2. **Ponto focal** em B4 (10–20%), com a forma mais simples e reconhecível.
3. **Arquitetura** com textura de baixo contraste (tijolos 2 tons, juntas 1 passo mais escuras).
4. **Luz:** fonte → poça no chão → rim light nos objetos → luz volumétrica só se houver poeira ou fumaça (o cone é mais claro no meio). [L-02]
5. **Piso:** reflexo, sombra de contato e faixas de luz.
6. **Vinheta e atmosfera:** dither estilizado nas áreas amplas.
7. **Quantize** para a paleta e rode o lint (`--kind background`, gate 80).

## 5. Parallax e uso no Roblox
- Separe em camadas (fundo, meio, frente) com PNGs próprios. Elementos em loop precisam de contagem de frames que divida o loop maior. [A-21]
- Exibição: `ImageLabel` de tela cheia com `ResampleMode = Pixelated`, tamanho = k × 320×180 (k inteiro por `PixelScale`) e barras (letterbox) com a cor B0 para sobrar espaço.
- 320×180 cabe em 1024. Para 640×360 também. Acima disso, divida em tiles.
- Mobile: compressão com perdas. Teste no aparelho e, se a cor mudar demais, considere a variante ×2/×4 por tiles.
- Ambiente animado sem custo de CPU: palette cycling pré-renderizado em 4–8 quadros (sheet) tocados pelo `SpriteAnimator`.
