"""Empacota o runtime (roblox/) e os dados aprovados (saida/*/Dados_*.luau, Clipes_*.luau) num unico
arquivo .rbxmx que se arrasta para dentro do Studio. Dentro vai um Script INSTALAR que move cada pasta para
o servico certo."""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from .registro import RAIZ

INSTALAR = '''-- INSTALAR: rode UMA vez. Clique com o botao direito neste Script > Run (ou de Play).
-- Move cada pasta de FabricaVoxel_Instalar para o servico certo, substituindo versoes antigas.
local raiz = script.Parent
local destinos = {
	ReplicatedStorage = game:GetService("ReplicatedStorage"),
	ServerScriptService = game:GetService("ServerScriptService"),
	StarterPlayerScripts = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts"),
}
for nome, servico in pairs(destinos) do
	local pasta = raiz:FindFirstChild(nome)
	if pasta then
		for _, item in ipairs(pasta:GetChildren()) do
			local antigo = servico:FindFirstChild(item.Name)
			if antigo and antigo ~= item then
				antigo:Destroy()
			end
			item.Parent = servico
		end
	end
end
print("[FabricaVoxel] instalado. Pode apagar a pasta FabricaVoxel_Instalar.")
raiz:Destroy()
'''


class _X:
    def __init__(self):
        self.n = 0
        self.L = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                  'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">']

    def abrir(self, classe: str, nome: str, fonte: str | None = None):
        self.n += 1
        self.L.append(f'<Item class="{classe}" referent="RBX{self.n}"><Properties><string name="Name">{escape(nome)}</string>')
        if fonte is not None:
            self.L.append('<ProtectedString name="Source"><![CDATA[' + fonte.replace("]]>", "]]]]><![CDATA[>") + "]]></ProtectedString>")
        self.L.append("</Properties>")

    def fechar(self):
        self.L.append("</Item>")

    def texto(self) -> str:
        return "\n".join(self.L + ["</roblox>"])


def _classe(arq: Path) -> tuple[str, str]:
    n = arq.name
    if n.endswith(".server.luau"):
        return "Script", n[:-12]
    if n.endswith(".client.luau"):
        return "LocalScript", n[:-12]
    return "ModuleScript", n[:-5]


def _pasta(x: _X, pasta: Path):
    for f in sorted(pasta.iterdir()):
        if f.is_dir():
            x.abrir("Folder", f.name)
            _pasta(x, f)
            x.fechar()
        elif f.suffix == ".luau":
            c, nome = _classe(f)
            x.abrir(c, nome, f.read_text(encoding="utf-8"))
            x.fechar()


def empacotar(destino: Path | None = None, so_aprovados: bool = True) -> str:
    rb = RAIZ / "roblox"
    x = _X()
    x.abrir("Folder", "FabricaVoxel_Instalar")
    x.abrir("Script", "INSTALAR", INSTALAR)
    x.fechar()
    x.abrir("Folder", "ReplicatedStorage")
    x.abrir("Folder", "Fabrica")
    _pasta(x, rb / "ReplicatedStorage" / "Fabrica")
    dados, clipes = [], []
    for rel in sorted((RAIZ / "saida").glob("*/relatorio.json")):
        try:
            r = json.loads(rel.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if so_aprovados and r.get("status") != "aprovado":
            continue
        dados += sorted(rel.parent.glob("Dados_*.luau"))
        clipes += sorted(rel.parent.glob("Clipes_*.luau"))
    for nome, lista in (("Dados", dados), ("Clipes", clipes)):
        x.abrir("Folder", nome)
        for f in lista:
            x.abrir("ModuleScript", f.stem, f.read_text(encoding="utf-8"))
            x.fechar()
        x.fechar()
    x.fechar()  # Fabrica
    x.fechar()  # ReplicatedStorage
    x.abrir("Folder", "ServerScriptService")
    _pasta(x, rb / "ServerScriptService")
    x.fechar()
    x.abrir("Folder", "StarterPlayerScripts")
    _pasta(x, rb / "StarterPlayer" / "StarterPlayerScripts")
    x.fechar()
    x.fechar()
    destino = destino or RAIZ / "saida" / "FabricaVoxel.rbxmx"
    destino.write_text(x.texto(), encoding="utf-8")
    return f"{destino}  ({len(dados)} modelos, {len(clipes)} conjuntos de clipes, {destino.stat().st_size // 1024} KB)"
