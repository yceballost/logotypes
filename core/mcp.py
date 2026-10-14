from __future__ import annotations

import json
import logging

from flask import Response, jsonify, request

from core.config import Settings
from core.logo_repository import LogoRepository
from core.routes import _record_to_public_data
from core.tracking import UmamiTracker


logger = logging.getLogger(__name__)

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
SERVER_INFO = {"name": "logotypes", "title": "Logotypes.dev", "version": "1.0.0"}

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

_VARIANT_SCHEMA = {"type": "string", "enum": ["wordmark", "glyph"], "description": "Logo variant."}
_VERSION_SCHEMA = {"type": "string", "enum": ["color", "black", "white"], "description": "Logo colour version."}

TOOLS = [
    {
        "name": "search_logos",
        "description": "Search brand logos by name (case-insensitive substring match). Returns logo URLs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to look for in the brand name."},
                "variant": _VARIANT_SCHEMA,
                "version": _VERSION_SCHEMA,
                "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": DEFAULT_LIMIT},
            },
            "required": ["query"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "get_logo",
        "description": "Get the logo files of one brand by exact name. Optionally include the SVG source.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Brand name, for example 'spotify'."},
                "variant": _VARIANT_SCHEMA,
                "version": _VERSION_SCHEMA,
                "include_svg": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include the SVG markup of each logo. Can be large; leave off unless needed.",
                },
            },
            "required": ["name"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "random_logo",
        "description": "Get a random logo, optionally filtered by variant and version.",
        "inputSchema": {
            "type": "object",
            "properties": {"variant": _VARIANT_SCHEMA, "version": _VERSION_SCHEMA},
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "list_logos",
        "description": "List every available brand name with its available variants and versions.",
        "inputSchema": {
            "type": "object",
            "properties": {"variant": _VARIANT_SCHEMA, "version": _VERSION_SCHEMA},
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
]


class _ToolError(Exception):
    pass


def _rpc_result(request_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _rpc_error(request_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_result(payload: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
    }


def _tool_failure(message: str) -> dict:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def register_mcp(app, repository: LogoRepository, tracker: UmamiTracker, settings: Settings) -> None:
    def _origin_allowed() -> bool:
        origin = request.headers.get("Origin")
        if not origin or settings.cors_origins == "*":
            return True
        return origin in settings.cors_origins

    def _filtered(variant, version):
        return repository.filter_records(repository.all_records(), variant=variant, version=version)

    def _search_logos(args: dict) -> dict:
        query = str(args.get("query", "")).strip()
        if not query:
            raise _ToolError("'query' is required.")
        limit = max(1, min(int(args.get("limit", DEFAULT_LIMIT)), MAX_LIMIT))
        canonical = repository._canonical_name(query)
        matches = [
            record
            for record in _filtered(args.get("variant"), args.get("version"))
            if canonical in repository._canonical_name(record.slug)
        ]
        return {
            "total": len(matches),
            "logos": [_record_to_public_data(record, request.host_url) for record in matches[:limit]],
        }

    def _get_logo(args: dict) -> dict:
        name = str(args.get("name", "")).strip()
        if not name:
            raise _ToolError("'name' is required.")
        records = repository.filter_records(
            repository.records_by_name(name), variant=args.get("variant"), version=args.get("version")
        )
        if not records:
            raise _ToolError(f"No logo found for '{name}' with the given filters. Try search_logos.")

        logos = []
        for record in records:
            item = _record_to_public_data(record, request.host_url)
            if args.get("include_svg"):
                item["svg"] = (settings.logos_dir / record.filename).read_text(encoding="utf-8")
            logos.append(item)
        return {"logos": logos}

    def _random_logo(args: dict) -> dict:
        record = repository.random_record(variant=args.get("variant"), version=args.get("version"))
        if not record:
            raise _ToolError("No logos found with the given filters.")
        return _record_to_public_data(record, request.host_url)

    def _list_logos(args: dict) -> dict:
        grouped: dict[str, dict[str, set[str]]] = {}
        for record in _filtered(args.get("variant"), args.get("version")):
            entry = grouped.setdefault(record.slug, {"variants": set(), "versions": set()})
            entry["variants"].add(record.variant)
            entry["versions"].add(record.version)
        names = [
            {"name": slug, "variants": sorted(entry["variants"]), "versions": sorted(entry["versions"])}
            for slug, entry in sorted(grouped.items())
        ]
        return {"total": len(names), "logos": names}

    handlers = {
        "search_logos": _search_logos,
        "get_logo": _get_logo,
        "random_logo": _random_logo,
        "list_logos": _list_logos,
    }

    def _call_tool(params: dict) -> dict:
        name = params.get("name")
        handler = handlers.get(name)
        if not handler:
            raise KeyError(name)
        arguments = params.get("arguments") or {}

        tracker.send_event(request=request, name="MCP Tool Call", title=f"MCP {name}", data={"tool": name})
        try:
            return _tool_result(handler(arguments))
        except _ToolError as error:
            return _tool_failure(str(error))
        except (TypeError, ValueError):
            return _tool_failure("Invalid arguments.")

    def _handle(message) -> dict | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return _rpc_error(None, -32600, "Invalid request")

        method = message.get("method")
        request_id = message.get("id")
        params = message.get("params") or {}

        if request_id is None:
            return None  # notification, e.g. notifications/initialized

        if method == "initialize":
            requested = params.get("protocolVersion")
            version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            return _rpc_result(
                request_id,
                {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                    "instructions": "Search and fetch brand logos (SVG) from logotypes.dev.",
                },
            )
        if method == "ping":
            return _rpc_result(request_id, {})
        if method == "tools/list":
            return _rpc_result(request_id, {"tools": TOOLS})
        if method == "tools/call":
            try:
                return _rpc_result(request_id, _call_tool(params))
            except KeyError:
                return _rpc_error(request_id, -32602, f"Unknown tool: {params.get('name')}")
        return _rpc_error(request_id, -32601, f"Method not found: {method}")

    @app.route("/mcp", methods=["GET", "POST"])
    def mcp_endpoint():
        if request.method == "GET":
            # No server-initiated stream (SSE) is offered. Plain browser requests
            # keep getting the "mcp" logo, as before this endpoint existed.
            if "text/event-stream" in request.headers.get("Accept", ""):
                return Response(status=405, headers={"Allow": "POST"})
            return app.view_functions["get_logo"]("mcp")

        if not _origin_allowed():
            return Response("Forbidden origin", status=403)

        body = request.get_json(silent=True)
        if body is None:
            return jsonify(_rpc_error(None, -32700, "Parse error")), 400

        if isinstance(body, list):
            responses = [r for r in (_handle(m) for m in body) if r is not None]
            if not responses:
                return Response(status=202)
            return jsonify(responses)

        response = _handle(body)
        if response is None:
            return Response(status=202)
        return jsonify(response)
