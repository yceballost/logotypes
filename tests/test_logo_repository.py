from core.config import load_settings
from core.logo_repository import LogoRepository


def _prepare_dataset(root):
    static_dir = root / "static"
    logos_dir = static_dir / "logos"
    data_dir = static_dir / "data"
    logos_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    (logos_dir / "airbnb-wordmark-color.svg").write_text("<svg></svg>", encoding="utf-8")
    (logos_dir / "airbnb-glyph-black.svg").write_text("<svg></svg>", encoding="utf-8")
    (logos_dir / "my-brand-pro-wordmark-color.svg").write_text("<svg></svg>", encoding="utf-8")

    (data_dir / "airbnb.txt").write_text(
        "Title: Airbnb title\nDescription: Airbnb description\n",
        encoding="utf-8",
    )


def test_repository_loads_and_groups_records(tmp_path):
    _prepare_dataset(tmp_path)
    settings = load_settings(tmp_path)
    repository = LogoRepository(settings)

    all_records = repository.all_records()
    assert len(all_records) == 3

    grouped = repository.grouped_records()
    assert "airbnb" in grouped
    assert len(grouped["airbnb"]) == 2


def test_repository_supports_hyphenated_slug_and_filters(tmp_path):
    _prepare_dataset(tmp_path)
    settings = load_settings(tmp_path)
    repository = LogoRepository(settings)

    records = repository.records_by_name("my-brand-pro")
    assert len(records) == 1
    assert records[0].variant == "wordmark"

    filtered = repository.filter_records(repository.all_records(), variant="glyph", version="black")
    assert len(filtered) == 1
    assert filtered[0].slug == "airbnb"
