# 02 — Animação e VFX em pixel art

Dossiê com fontes: `docs/pixel-art/pesquisa/02-tecnica-pixel-art-vfx-ui.md`, seções 4 e 5.

## 1. Princípios com números
- **Easing é aceleração.** Nada linear. Antecipação + overshoot em ataques. Às vezes **pule o frame do meio** para dar força. [A-01]
- **Impacto:** idle → antecipação → movimento → overshoot → repouso. Corte frames entre repouso e alvo, use motion blur e "freeze" 1 frame antes do impacto (só em golpes exagerados). [A-02]
- **Espada:** wind-up → overshot (o slash arc) → recover. O recover é a parte mais longa e lenta. [A-03]
- **Input do jogador:** o ataque disparado pelo jogador **não** tem frame de antecipação (sentiria input lag). [A-04]
- **Smear:** 1 frame (2 só se for violento), entre poses-chave e seguindo o arco. O contorno ainda "diz quem é". [A-05, A-09]
- **Ciclos:** 8 frames × 80 ms ≈ 4 frames × 160 ms. Ciclos de 6 frames resolvem quase tudo. [A-08]
- **Squash & stretch:** a massa se conserva (mudou a largura, muda a altura). [A-11]
- **Sub-pixel:** mova a luz, não a forma. [A-12]
- **Dano:** o primeiro frame é o mais forte (overshoot), a recuperação é lenta. "Contrast frame" preto em inimigos pequenos. [A-13]

## 2. Hit-stop, flash e shake
- Atacante e vítima congelam pelo **mesmo tempo**; mais dano, hit-stop maior (teto 20–30 frames @60). A vítima treme com amplitude decrescente. [A-14, A-15]
- Ultimate: `⌊(d·0,65 + 6)·h·e⌋`. Exemplo: 10 de dano → 12 frames (200 ms). [A-15]
- Shake em pixel: deslocamento **inteiro**, 1–4 px nativos, decai em 4–10 frames, na direção do golpe. **A UI não treme.** [TR-03]
- Hit flash branco: 1–3 frames @60 (16–50 ms). [TR-04]
- Impact frame: silhueta em 2 cores invertidas, 1 frame (≤ 50 ms), no máximo 1 a cada ~2 s. [TR-05, TR-06]

## 3. Tabela de timing padrão [4.5]

| Ação | Frames | ms/frame | Total |
|---|---|---|---|
| Flash de contraste/branco | 1 + 1 | 40–60 | ~100 ms |
| Explosão pequena | 6–8 | 60–80 | 0,4–0,6 s |
| Explosão grande | 12–16 | 60–80 (fumaça 100) | 0,9–1,3 s |
| Slash arc | 3–4 | 40–60 | 0,15–0,25 s |
| Raio/eletricidade | 6–8 (1–2 em branco) | 50–80 | 0,4–0,6 s |
| Fogo/tocha (loop) | 6–8 | 90–110 | 0,6–0,9 s |
| Brasa/faísca (vida) | 3–8 | 60–100 | — |
| Shine sweep | 6–9 | 50–80 + pausa 1–3 s | — |
| Hit-stop | 4–12 @60 | 66–200 ms | proporcional ao dano |
| Transição de tela | 8–16 passos | 33–50 | 0,25–0,5 s |
| Idle de carta lendária | 4–8 | 120–200 | loop de 1–2 s |

Medições dos GIFs do Saint11: explosão 80 ms, fogo 100 ms, fumaça 100 ms, magia sombria 60 ms, magia de luz 70 ms, glitch 60 ms, shine de UI = pausa 500 + 9×80 + hold 200 ms. [4.4]

**Regra de loop:** o último frame continua como se o primeiro fosse o próximo. Em loops sobrepostos, a contagem de frames de um deve dividir a do maior. [A-21]
**No motor:** `noise.fbm_loop` (ruído periódico no tempo) e fases inteiras (`p = (f/frames + fase) % 1`) fecham o loop matematicamente.

## 4. Receitas de VFX (e o gerador correspondente)

### Explosão — `fx.explosion` [VFX-01 a VFX-04]
Camadas FLASH → BLAST → FIRE → SMOKE sobrepostas:
- f0 **contrast frame** (disco quase preto);
- f1 flash branco (pode ter linhas radiais);
- blast com ângulos agudos;
- bolhas de fogo com centro mais claro e quente, expansão rápida que desacelera;
- fumaça **índigo** (não cinza) que sobe devagar e é erodida de fora para dentro.

O fogo some rápido; a fumaça, devagar. Mínimo de 4 frames.

### Fogo — `fx.fire_loop`, `fx.embers_rising` [VFX-06 a VFX-08, VFX-16]
- Fogo é fluxo: base que mantém o volume e partículas que se soltam.
- Nova onda a cada 2–3 frames. As cores claras vêm de baixo. O topo some numa ponta. A velocidade é maior no meio.
- Progressão de cor por idade: branco → amarelo → laranja → vermelho → brasa escura → fumaça fria.
- Brasa: 1 px, sobe 0,3–0,8 px/frame com deriva senoidal ±1 px, desce na rampa a cada 3–4 frames e pisca no fim.

### Fumaça — `fx.curse_smoke` [VFX-09 a VFX-11]
- Anime **uma partícula por vez**. O primeiro frame é de contraste.
- Puff = 1–3 círculos, cresce 1 px a cada 1–2 frames, desce na rampa a cada 2–3, quebra em 2–3 fragmentos conectados.
- **Sem dither para fingir transparência** (vira ruído).
- Fumaça de magia sombria é mais fluida, espirala e some devagar.

### Slash — `fx.slash_arc` [VFX-24 a VFX-26]
- Crescente com espessura afinando nas pontas.
- Borda de ataque branca (ou branco-azulado frio `#cbdbfc`), corpo claro e **cauda nos tons escuros** (o escuro faz o fade).
- Varre 90°–160°. Frames de 40–60 ms.
- Recolorir a mesma máscara gera variantes elementais.

### Faísca de impacto — `fx.impact_spark`
- Estrela (segurada = hit-stop) → anel → partículas que se afastam e escurecem.
- Faíscas se resolvem em ~3 frames. [VFX-14]

### Raio [VFX-17, VFX-18, VFX-20]
Sequência:
1. contraste;
2. choque com ângulos agudos;
3. branco com forma nova;
4. vazio;
5. fragmentos;
6. vazio;
7. dissipação.

Polilinha por deslocamento do ponto médio (`detail` 2–3 px), núcleo 1 px claro, brilho de 1 px de cada lado. *(Ainda não há gerador; é um ponto de melhoria.)*

### Magia sombria × sagrada [VFX-21 a VFX-23]

| | Sombria / profana | Sagrada / divina |
|---|---|---|
| Paleta | complementares, roxo + verde-ácido/rosa, círculo preto de contraste | análogas: ouro/branco/ciano |
| Formas | pontas, espinhos, caveiras, rostos | círculos, quadrados, raios retos, halos |
| Luz | de baixo | de cima |
| Ritmo | camadas sobrepostas, caóticas | eventos em sequência, simétricos |
| Fumaça | fluida, em espiral | nenhuma |
| ms/frame | 50–60 | 70–90 |

Geradores: `fx.curse_smoke` [DEB], `fx.magic_circle` (ritual), `fx.holy_pillar` (sagrado), `fx.ascend_aura` [BUF], `fx.ward_shield` [GRD].

### Sangue — `fx.blood_burst` [VFX-27, VFX-28]
- Formas redondas; o respingo começa **pontudo** e se espalha mantendo as partículas conectadas.
- Gravidade (cai antes de sumir), variação de matiz e 1 px de brilho = molhado.
- Órfãos só no último frame.

### Círculo mágico — `fx.magic_circle` [5.10]
- Anéis de 1 px pelo ponto médio, simetria de 4/8 setores.
- **Não gire linhas finas.** Mova as runas ao longo do anel, cicle as cores ou gire em passos de 90°.

### Glitch [VFX-34]
Faixas deslocadas na horizontal (sem exagero), flicker, blocos movidos, scanlines deslocadas 1 px, cores empurradas. Usado nos subtipos `isGlitchy` (fatias de 1–3 px deslocadas ±2–3 px).

## 5. Legibilidade sobre fundo escuro [VFX-35, VFX-36]
- Núcleo com **L ≥ 0,85** e **ΔL ≥ 0,40** em relação ao fundo sob o efeito.
- Pelo menos 1 tom com S ≥ 60% e matiz a ≥ 60° do matiz do fundo.
- Flash branco: no máximo 1–2 frames. Efeito > 35% da tela por mais de 150 ms cansa.
- O último tom de fumaça precisa de ΔL ≥ 0,05 em relação ao fundo, senão remova-o.

## 6. GUI × partícula (decide o formato de export)

| | GUI (`SpriteAnimator`) | ParticleEmitter (`FlipbookVFX`) |
|---|---|---|
| Nitidez | `Pixelated` real | sempre filtrado → **upscale inteiro antes** |
| Timing | ms por frame (holds) | fps fixo ≤ 30 → holds viram frames repetidos |
| Grade | livre (≤ 1024, padding 1 px) | 2×2/4×4/8×8 (Custom em beta), gutter ≥ cell/16 |
| Crossfade | não tem | **desligue `FlipbookBlendFrames`** (padrão true desde mar/2026) |
| Uso | cartas, HUD, transições, VFX de UI | mundo 3D, ambientes, golpes em modelos |
