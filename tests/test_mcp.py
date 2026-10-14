import app as app_module

from core.config import load_settings


def _make_client(root, monkeypatch):
    logos_dir = root / "static" / "logos"
    logos_dir.mkdir(parents=True)
    (root / "static" / "data").mkdir()
    (root / "static" / "web").mkdir()

    (logos_dir / "airbnb-wordmark-color.svg").write_text("<svg>airbnb-wordmark-color</svg>", encoding="utf-8")
    (logos_dir / "airbnb-glyph-black.svg").write_text("<svg>airbnb-glyph-black</svg>", encoding="utf-8")
    (logos_dir / "spotify-glyph-color.svg").write_text("<svg>spotify-glyph-color</svg>", encoding="utf-8")
    (logos_dir / "mcp-glyph-black.svg").write_text("<svg>mcp-glyph-black</svg>", encoding="utf-8")

    monkeypatch.setenv("UMAMI_ENABLED", "false")
    settings = load_settings(root)
    monkeypatch.setattr(app_module, "load_settings", lambda: settings)
    return app_module.create_app().test_client()


def _rpc(client, method, params=None, request_id=1):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return client.post("/mcp", json=message)


def _call(client, name, arguments=None):
    response = _rpc(client, "tools/call", {"name": name, "arguments": arguments or {}})
    assert response.status_code == 200
    return response.get_json()["result"]


def test_initialize_and_tools_list(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    init = _rpc(client, "initialize", {"protocolVersion": "2025-06-18"}).get_json()["result"]
    assert init["protocolVersion"] == "2025-06-18"
    assert "tools" in init["capabilities"]

    tools = _rpc(client, "tools/list").get_json()["result"]["tools"]
    assert {tool["name"] for tool in tools} == {"search_logos", "get_logo", "random_logo", "list_logos"}


def test_notification_returns_202(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    response = client.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert response.status_code == 202


def test_unknown_method_and_invalid_json(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    assert _rpc(client, "nope").get_json()["error"]["code"] == -32601
    assert client.post("/mcp", data="not json", content_type="application/json").status_code == 400


def test_search_and_filters(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    result = _call(client, "search_logos", {"query": "air"})
    assert result["structuredContent"]["total"] == 2

    result = _call(client, "search_logos", {"query": "air", "variant": "glyph"})
    logos = result["structuredContent"]["logos"]
    assert [logo["variant"] for logo in logos] == ["glyph"]


def test_get_logo(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    result = _call(client, "get_logo", {"name": "Spotify"})
    logo = result["structuredContent"]["logos"][0]
    assert logo["logo"].endswith("static/logos/spotify-glyph-color.svg")
    assert "svg" not in logo

    result = _call(client, "get_logo", {"name": "spotify", "include_svg": True})
    assert result["structuredContent"]["logos"][0]["svg"] == "<svg>spotify-glyph-color</svg>"

    missing = _call(client, "get_logo", {"name": "unknown"})
    assert missing["isError"] is True


def test_random_and_list(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    assert _call(client, "random_logo", {"variant": "wordmark"})["structuredContent"]["name"] == "Airbnb"

    listing = _call(client, "list_logos")["structuredContent"]
    assert listing["total"] == 3
    airbnb = next(item for item in listing["logos"] if item["name"] == "airbnb")
    assert airbnb["variants"] == ["glyph", "wordmark"]


def test_unknown_tool_is_rpc_error(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    response = _rpc(client, "tools/call", {"name": "nope"}).get_json()
    assert response["error"]["code"] == -32602


def test_get_mcp_still_serves_logo(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    response = client.get("/mcp")
    assert response.status_code == 200
    assert b"mcp-glyph-black" in response.data

    sse = client.get("/mcp", headers={"Accept": "text/event-stream"})
    assert sse.status_code == 405
