"""Ponte com o Roblox: previa instantanea no Studio (EditableImage) e upload Open Cloud.

1) PREVIA SEM UPLOAD  -> editable_image_luau(canvas)
   Gera um trecho Luau que recria a imagem pixel a pixel num EditableImage e mostra
   num ImageLabel (Pixelated) dentro de StarterGui/PixelForgePreview. Rode pelo MCP do
   Studio (execute_luau, datamodel_type = "Edit") ou cole no Command Bar.
   Limites: <= 1024x1024; precisa de "Allow Mesh / Image APIs" se for usado em jogo;
   Content.fromObject NAO replica (e so para previa local).

2) UPLOAD DEFINITIVO -> upload_images(paths)
   Open Cloud Assets API com assetType "Image" (ID de Decal NAO funciona em
   ImageLabel via script). Le ROBLOX_API_KEY + ROBLOX_USER_ID ou ROBLOX_GROUP_ID do
   ambiente. Nunca coloque a chave no codigo nem no chat.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Dict, List

import numpy as np

from .canvas import Canvas

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"


def editable_image_luau(c: Canvas, name: str = "Preview", scale: int = 4) -> str:
    """Luau que desenha 'c' num EditableImage (paleta indexada: 1 caractere por pixel)."""
    px = c.px
    flat = px.reshape(-1, 4)
    cols: Dict[tuple, int] = {}
    idx = []
    for p in flat:
        # transparente = uma unica 'cor' (o RGB de pixels alpha 0 pode vir do alpha-bleed)
        key = (int(p[0]), int(p[1]), int(p[2]), 255) if p[3] > 0 else (0, 0, 0, 0)
        if key not in cols:
            cols[key] = len(cols)
        idx.append(cols[key])
    if len(cols) > len(ALPHABET):
        raise ValueError(f"{len(cols)} cores: quantize para <= 64 antes da previa")
    pal = ", ".join("{%d,%d,%d,%d}" % k for k in cols)
    data = "".join(ALPHABET[i] for i in idx)
    rows = [data[i:i + 120] for i in range(0, len(data), 120)]
    data_lua = "table.concat({\n\t\t\"" + "\",\n\t\t\"".join(rows) + "\",\n\t})"
    return f'''--!strict
-- PixelForge: previa "{name}" ({c.w}x{c.h}) via EditableImage. Rode em Edit (MCP execute_luau
-- com datamodel_type = "Edit") ou no Command Bar. Cria StarterGui > PixelForgePreview.
local AssetService = game:GetService("AssetService")
local StarterGui = game:GetService("StarterGui")
local W, H, SCALE = {c.w}, {c.h}, {scale}
local ALPHABET = "{ALPHABET}"
local PALETTE: {{ {{ number }} }} = {{ {pal} }}
local DATA = {data_lua}

local lookup: {{ [string]: number }} = {{}}
for i = 1, #ALPHABET do
	lookup[string.sub(ALPHABET, i, i)] = i
end

local buf = buffer.create(W * H * 4)
for i = 1, W * H do
	local color = PALETTE[lookup[string.sub(DATA, i, i)]]
	local o = (i - 1) * 4
	buffer.writeu8(buf, o, color[1])
	buffer.writeu8(buf, o + 1, color[2])
	buffer.writeu8(buf, o + 2, color[3])
	buffer.writeu8(buf, o + 3, color[4])
end

local ok, img = pcall(function()
	return AssetService:CreateEditableImage({{ Size = Vector2.new(W, H) }})
end)
if not ok or img == nil then
	warn("[PixelForge] EditableImage indisponivel (memoria ou permissao): " .. tostring(img))
	return
end
img:WritePixelsBuffer(Vector2.zero, Vector2.new(W, H), buf)

local gui = StarterGui:FindFirstChild("PixelForgePreview")
if gui == nil then
	local sg = Instance.new("ScreenGui")
	sg.Name = "PixelForgePreview"
	sg.ResetOnSpawn = false
	sg.Parent = StarterGui
	gui = sg
end
local label = Instance.new("ImageLabel")
label.Name = "{name}"
label.BackgroundColor3 = Color3.fromRGB(30, 30, 36)
label.Size = UDim2.fromOffset(W * SCALE, H * SCALE)
label.Position = UDim2.fromOffset(16, 16 + #(gui :: Instance):GetChildren() * (H * SCALE + 8))
label.ResampleMode = Enum.ResamplerMode.Pixelated
label.ImageContent = Content.fromObject(img)
label.Parent = gui
print("[PixelForge] previa criada:", label:GetFullName())
'''


# ------------------------------------------------------------------ Open Cloud
API = "https://apis.roblox.com/assets/v1"


def _creator() -> Dict[str, str]:
    gid = os.environ.get("ROBLOX_GROUP_ID")
    if gid:
        return {"groupId": gid}
    uid = os.environ.get("ROBLOX_USER_ID")
    if not uid:
        raise RuntimeError("defina ROBLOX_USER_ID (ou ROBLOX_GROUP_ID) no ambiente")
    return {"userId": uid}


def _request(method: str, url: str, key: str, body: bytes = b"", ctype: str = "") -> Dict:
    req = urllib.request.Request(url, data=body if method == "POST" else None, method=method)
    req.add_header("x-api-key", key)
    if ctype:
        req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def _multipart(fields: Dict[str, tuple]) -> tuple:
    boundary = uuid.uuid4().hex
    out = bytearray()
    for name, (filename, content, ctype) in fields.items():
        out += f"--{boundary}\r\n".encode()
        disp = f'form-data; name="{name}"' + (f'; filename="{filename}"' if filename else "")
        out += f"Content-Disposition: {disp}\r\nContent-Type: {ctype}\r\n\r\n".encode()
        out += content if isinstance(content, bytes) else content.encode("utf-8")
        out += b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def upload_image(path: Path, name: str = "", description: str = "PixelForge pixel art") -> int:
    key = os.environ.get("ROBLOX_API_KEY")
    if not key:
        raise RuntimeError("defina ROBLOX_API_KEY no ambiente (escopos asset:read + asset:write)")
    req = {
        "assetType": "Image",  # NAO "Decal"
        "displayName": (name or path.stem)[:50],
        "description": description[:1000],
        "creationContext": {"creator": _creator()},
    }
    body, ctype = _multipart({
        "request": (None, json.dumps(req), "application/json"),
        "fileContent": (path.name, path.read_bytes(), "image/png"),
    })
    op = _request("POST", f"{API}/assets", key, body, ctype)
    delay, waited = 1.0, 0.0
    while not op.get("done"):  # 'done' ausente = em progresso
        if waited > 180:
            raise TimeoutError(f"upload de {path.name} demorou demais")
        time.sleep(delay)
        waited += delay
        delay = min(delay * 2, 15)
        op_id = op.get("operationId") or op["path"].split("/")[-1]
        try:
            op = _request("GET", f"{API}/operations/{op_id}", key)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    if "error" in op:
        raise RuntimeError(f"{path.name}: {op['error']}")
    asset = op["response"]
    return int(asset["assetId"])


def upload_images(paths: List[Path]) -> Dict[str, int]:
    """Envia varios PNGs (respeita 120 uploads/min com pausa curta entre eles)."""
    out: Dict[str, int] = {}
    for p in paths:
        out[p.name] = upload_image(p)
        print(f"{p.name} -> rbxassetid://{out[p.name]}")
        time.sleep(0.6)
    return out
