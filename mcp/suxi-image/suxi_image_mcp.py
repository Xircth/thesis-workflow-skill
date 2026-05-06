#!/usr/bin/env python3
"""
Minimal stdio MCP server for Suxi gpt-image-2-vip.

This implementation follows the provided OpenAPI pages exactly:
- POST https://new.suxi.ai/v1/images/generations
  JSON: {model, prompt, size, quality}
- POST https://new.suxi.ai/api/upload
  multipart/form-data: file

Secrets are read from environment variables only:
- SUXI_API_KEY
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SERVER_NAME = "suxi-image-mcp"
SERVER_VERSION = "1.1.0"
SUXI_BASE_URL = "https://new.suxi.ai"
SUXI_IMAGE_MODEL = "gpt-image-2-vip"
DEFAULT_SIZE = "3840x2160"
DEFAULT_QUALITY = "low"


def _json_response(request_id: Any, result: Any = None, error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response: Dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    return response


def _tool_text(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": False}


def _tool_error(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def _get_api_key() -> Optional[str]:
    return os.environ.get("SUXI_API_KEY")


def _require_api_key() -> str:
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "SUXI_API_KEY is not configured. If the user needs image generation, ask them to register/top up at "
            "https://new.suxi.ai/console/topup, create an API key at https://new.suxi.ai/console/token, then provide "
            "the key for local MCP configuration. If they do not need image generation, skip this step."
        )
    return api_key


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _http_json(url: str, api_key: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1200]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc


def _http_multipart_upload(url: str, api_key: str, file_path: Path, timeout: int) -> Dict[str, Any]:
    if not file_path.exists() or not file_path.is_file():
        raise RuntimeError(f"File not found: {file_path}")

    boundary = f"----suxi-mcp-{int(time.time() * 1000)}"
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    filename = file_path.name
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    body = b"".join(parts)

    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1200]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc


def _download_url(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"Accept": "image/*,*/*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _iter_possible_image_items(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        if "url" in value or "b64_json" in value:
            yield value
        for child in value.values():
            yield from _iter_possible_image_items(child)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_possible_image_items(item)


def _save_images_from_response(result: Dict[str, Any], output_dir: Path, filename: str, timeout: int) -> List[str]:
    saved: List[str] = []
    suffix = Path(filename).suffix or ".png"
    stem = Path(filename).stem or f"suxi-gpt-image-2-vip-{int(time.time())}"

    for index, item in enumerate(_iter_possible_image_items(result), start=1):
        target = output_dir / (f"{stem}{suffix}" if index == 1 else f"{stem}-{index}{suffix}")
        if item.get("b64_json"):
            _write_bytes(target, base64.b64decode(item["b64_json"]))
            saved.append(str(target.resolve()))
        elif item.get("url"):
            _write_bytes(target, _download_url(str(item["url"]), timeout))
            saved.append(str(target.resolve()))

    return saved


def tool_check_config(_: Dict[str, Any]) -> Dict[str, Any]:
    data = {
        "configured": bool(_get_api_key()),
        "api_key_env": "SUXI_API_KEY" if _get_api_key() else "",
        "base_url": SUXI_BASE_URL,
        "image_generation": {
            "method": "POST",
            "path": "/v1/images/generations",
            "model": SUXI_IMAGE_MODEL,
            "default_size": DEFAULT_SIZE,
            "default_quality": DEFAULT_QUALITY,
            "request_fields": ["model", "prompt", "size", "quality"],
        },
        "image_upload": {
            "method": "POST",
            "path": "/api/upload",
            "content_type": "multipart/form-data",
            "field": "file",
        },
        "cost_note": "User-provided workflow: recharge 1 CNY = 1 USD credit; each generation consumes 0.12 USD credit, approximately 0.12 CNY.",
        "setup": [
            "Register and top up at https://new.suxi.ai/console/topup",
            "Create an API key at https://new.suxi.ai/console/token",
            "Inject the key into the active agent's local MCP config as SUXI_API_KEY; never commit it into this skill.",
            "If the user does not need image generation, skip this MCP setup.",
        ],
    }
    return _tool_text(json.dumps(data, ensure_ascii=False, indent=2))


def tool_create_gpt_image_2_vip(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        api_key = _require_api_key()
        prompt = str(arguments.get("prompt", "")).strip()
        if not prompt:
            return _tool_error("Missing required argument: prompt")

        size = str(arguments.get("size") or DEFAULT_SIZE)
        quality = str(arguments.get("quality") or DEFAULT_QUALITY)
        timeout = int(arguments.get("timeout_seconds") or 180)
        output_dir = Path(str(arguments.get("output_dir", "images/generated"))).expanduser()
        filename = str(arguments.get("filename") or f"suxi-gpt-image-2-vip-{int(time.time())}.png")

        payload = {
            "model": SUXI_IMAGE_MODEL,
            "prompt": prompt,
            "size": size,
            "quality": quality,
        }
        endpoint = f"{SUXI_BASE_URL}/v1/images/generations"
        result = _http_json(endpoint, api_key, payload, timeout)
        saved = _save_images_from_response(result, output_dir, filename, timeout)
        response = {
            "endpoint": endpoint,
            "request": payload,
            "saved_files": saved,
            "raw_response": result,
            "note": "If saved_files is empty, inspect raw_response for the provider's returned image URL or task result shape.",
        }
        return _tool_text(json.dumps(response, ensure_ascii=False, indent=2))
    except Exception as exc:
        return _tool_error(str(exc))


def tool_upload_image(arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        api_key = _require_api_key()
        file_path = Path(str(arguments.get("file_path", ""))).expanduser()
        timeout = int(arguments.get("timeout_seconds") or 120)
        endpoint = f"{SUXI_BASE_URL}/api/upload"
        result = _http_multipart_upload(endpoint, api_key, file_path, timeout)
        response = {
            "endpoint": endpoint,
            "file_path": str(file_path.resolve()),
            "raw_response": result,
        }
        return _tool_text(json.dumps(response, ensure_ascii=False, indent=2))
    except Exception as exc:
        return _tool_error(str(exc))


TOOLS = {
    "suxi_check_config": {
        "description": "Check whether Suxi gpt-image-2-vip MCP is configured without revealing the API key.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "handler": tool_check_config,
    },
    "suxi_create_gpt_image_2_vip": {
        "description": "Create an image through POST https://new.suxi.ai/v1/images/generations using model gpt-image-2-vip.",
        "inputSchema": {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "prompt": {"type": "string", "description": "Image prompt."},
                "size": {"type": "string", "default": DEFAULT_SIZE, "description": "Example from API page: 3840x2160."},
                "quality": {"type": "string", "default": DEFAULT_QUALITY, "description": "Example from API page: low."},
                "output_dir": {"type": "string", "default": "images/generated"},
                "filename": {"type": "string", "description": "Local filename for saving returned image data when present."},
                "timeout_seconds": {"type": "integer", "default": 180},
            },
            "additionalProperties": False,
        },
        "handler": tool_create_gpt_image_2_vip,
    },
    "suxi_upload_image": {
        "description": "Upload an image through POST https://new.suxi.ai/api/upload multipart/form-data field file.",
        "inputSchema": {
            "type": "object",
            "required": ["file_path"],
            "properties": {
                "file_path": {"type": "string", "description": "Local image file path."},
                "timeout_seconds": {"type": "integer", "default": 120},
            },
            "additionalProperties": False,
        },
        "handler": tool_upload_image,
    },
}


def handle_request(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = message.get("method")
    request_id = message.get("id")

    if method == "initialize":
        return _json_response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return _json_response(
            request_id,
            {
                "tools": [
                    {
                        "name": name,
                        "description": spec["description"],
                        "inputSchema": spec["inputSchema"],
                    }
                    for name, spec in TOOLS.items()
                ]
            },
        )
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        spec = TOOLS.get(name)
        if not spec:
            return _json_response(request_id, error={"code": -32602, "message": f"Unknown tool: {name}"})
        return _json_response(request_id, spec["handler"](arguments))

    if request_id is None:
        return None
    return _json_response(request_id, error={"code": -32601, "message": f"Method not found: {method}"})


def serve_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            response = handle_request(message)
        except Exception as exc:
            response = _json_response(None, error={"code": -32700, "message": str(exc)})
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def self_test() -> int:
    init = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    tools = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    config = tool_check_config({})
    serialized_tools = json.dumps(tools, ensure_ascii=False)
    ok = bool(init and tools and config and "suxi_create_gpt_image_2_vip" in serialized_tools and "suxi_upload_image" in serialized_tools)
    print(json.dumps({"ok": ok, "server": SERVER_NAME, "tools": list(TOOLS.keys())}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Suxi gpt-image-2-vip stdio MCP server")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    serve_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
