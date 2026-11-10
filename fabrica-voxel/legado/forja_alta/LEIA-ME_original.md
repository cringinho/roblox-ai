# Pacote da Fábrica de Voxel (9 e 10/11/2026)

Pasta `modelos/`: cada modelo em pose de repouso.
- `<modelo>.glb`: uma malha por peça rígida, já posicionada no pivô (translation = pivô no mundo). A peça `X_Brilho` é a parte emissiva.
- `<modelo>_rig.json`: peça, pai, pivô (studs), tamanho do voxel e quantidade de voxels. Use para montar os Motor6D.
- `<modelo>_paleta.png`: textura de paleta usada pelo GLB (sem filtro, cada voxel mapeia um pixel).
- Unidade: stud. Frente: -Z. Cima: +Y.

`modelos/myxilia/`: GLBs de grade e de susto, .vox, rig, ficha e os scripts Luau da Myxilia.
`animacoes/`: as animações em WebP.
`codigo/`: o gerador (voxforja.py) e os scripts de cada modelo. Para regerar: `python3 exportar.py <pasta>`.

Não incluso: scripts Luau dos demais modelos (ainda não foram feitos) e as animações em dados; os clipes são procedurais, em hidra_anim.py, hidra_adulta.py, relicario_anim.py, slimes.py e bestiario.py.
Os GLBs não foram testados no Roblox Studio.
