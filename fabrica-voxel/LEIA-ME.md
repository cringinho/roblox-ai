# Fábrica de Voxel v4

Uma ficha JSON entra; saem modelo voxel, rig, animações, arquivos do Roblox, arquivos de venda e auditoria.
Sem Blender e sem IA de imagem: só Python (numpy, Pillow).

```
pip install numpy pillow
cd fabrica-voxel
python -m fabrica listar
python -m fabrica construir esporinho      # saida/esporinho/folha.png
python -m fabrica elenco                   # saida/_elenco/elenco.png
```

- **Vai produzir assets (humano ou IA):** leia `AGENTS.md` e o cartão da tarefa em `cartoes/`.
- **Vai levar para o Studio:** `roblox/TESTE_NO_STUDIO.md`.
- **Vai mudar o código:** `docs/ARQUITETURA.md`.
- **Pesquisa que embasou as regras:** `docs/pesquisa/`.

| Pasta | O que tem |
| --- | --- |
| `registro/` | os dados: paletas, 20 arquétipos, 15 linhagens, traços, aparência, itens, conjuntos, monstros, clipes |
| `fabrica/` | o código da esteira |
| `roblox/` | runtime Luau genérico (rig, animador, câmera, grade) |
| `saida/` | o que a fábrica gera |
| `cartoes/` | um cartão de uma página por tarefa |

Estado: 20 arquétipos, 15 linhagens, 4 conjuntos, 5 itens e 5 monstros constroem e passam nos portões.
Nada foi testado dentro do Roblox Studio.
