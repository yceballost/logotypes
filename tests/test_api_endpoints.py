import app as app_module

from core.config import load_settings


def _prepare_dataset(root):
    static_dir = root / "static"
    logos_dir = static_dir / "logos"
    data_dir = static_dir / "data"
    web_dir = static_dir / "web"

    logos_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)
    web_dir.mkdir(parents=True)

    (logos_dir / "airbnb-wordmark-color.svg").write_text("<svg>airbnb-wordmark-color</svg>", encoding="utf-8")
    (logos_dir / "airbnb-glyph-black.svg").write_text("<svg>airbnb-glyph-black</svg>", encoding="utf-8")

    (data_dir / "airbnb.txt").write_text(
        "Title: Airbnb title\nDescription: Airbnb description\n",
        encoding="utf-8",
    )

    (web_dir / "index.html").write_text("<html>home</html>", encoding="utf-8")
    (web_dir / "style.css").write_text("body { color: red; }", encoding="utf-8")
    (web_dir / "test.html").write_text("<html>test</html>", encoding="utf-8")


def test_endpoints_return_expected_responses(tmp_path, monkeypatch):
    monkeypatch.setenv("UMAMI_ENABLED", "false")
    _prepare_dataset(tmp_path)

    settings = load_settings(tmp_path)
    monkeypatch.setattr(app_module, "load_settings", lambda: settings)
    flask_app = app_module.create_app()

    client = flask_app.test_client()

    all_response = client.get("/all")
    assert all_response.status_code == 200
    all_payload = all_response.get_json()
    assert "records" in all_payload
    assert "airbnb" in all_payload["records"]

    random_logo_response = client.get("/random?variant=wordmark&version=color")
    assert random_logo_response.status_code == 200
    assert random_logo_response.content_type == "image/svg+xml"

    name_data_response = client.get("/airbnb/data")
    assert name_data_response.status_code == 200
    assert isinstance(name_data_response.get_json(), list)

    not_found_response = client.get("/unknown")
    assert not_found_response.status_code == 404
