# 06 — Gate de qualidade (antes de entregar ou fazer upload)

## A. Lint automático (`python -m pixelforge lint arquivo.png --kind K`)

| Métrica | O que mede | Falha quando |
|---|---|---|
| alpha parcial | pixels com 0 < alpha < 255 | qualquer um (pixel art usa alpha binário) |
| ampliada | a imagem é k×k de uma menor | trabalhe e faça o lint no nativo |
| cores / fora da paleta | contagem e conformidade | acima do orçamento (`references/01` §8) ou fora da paleta |
| órfãos (ruído) | pixel sem vizinho da mesma cor numa vizinhança de 2+ cores | > px/120 (sprite/UI) ou px/60 (VFX/cenário) |
| dither | órfão cercado por 1 cor (textura plana) | não penaliza (informativo) |
| faíscas | pixel opaco isolado no vazio | só penaliza se `allow_sparks=False` |
| anéis | cores paralelas à borda (banding/pillow) | ≥ 2 faixas |
| faixa de valor | max L − min L | < 0,30 em sprite/UI |
| contraste com o fundo | maior contraste WCAG contra #1E1E24 | < 3 (exceto frames de contraste ou dissipação marcados) |
| animação | pivô do loop, ≤ 64 frames | base oscila > H/8; não cabe em 8×8 |

**Notas mínimas:** sprite, ícone e UI ≥ 90; VFX ≥ 85; cenário ≥ 80.

## B. Rubrica visual (sempre olhe a prévia ×4 sobre o fundo real)
1. **Silhueta:** preencha tudo de preto. Ainda reconhece? (ícones, emblemas, personagens)
2. **Escala de cinza:** dessature. As massas de luz e sombra se separam?
3. **Apertar os olhos:** o ponto focal salta primeiro? Algo compete com ele?
4. **Fundo real:** sobre o #1E1E24 da UI, sobre o cenário e sobre um fundo claro (pior caso).
5. **Escala real:** ×1 na resolução do celular (k = 1 em DPI 3×) e ×2/×3 no PC. Nada de mixels.
6. **Animação:** quadro a quadro. Flash segurado? Dissipação mais lenta que o ataque? Loop sem "pulo"? Nada pisca sem querer?
7. **Consistência:** mesma luz, mesma paleta e mesmo peso de contorno do resto do jogo, lado a lado com 3 assets existentes.
8. **Roblox:** `Pixelated` setado, tamanho inteiro, dentro de 1024, alpha bleed, upload como Image, `FlipbookBlendFrames = false`.

## C. Teste no aparelho
- Celular de entrada (Android) e iPhone: a cor muda (compressão)? Algum tremor de sub-pixel? FPS no MicroProfiler?
- Se a compressão destruir a cor: variante ×4 nos sprites críticos ou paleta com menos cores vizinhas parecidas.

## D. Registro
Salve `lint_report.json`, as prévias (strip/GIF) e uma nota curta "o que mudou" junto do asset. A próxima iteração começa dali.
