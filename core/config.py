from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    project_root: Path
    static_dir: Path
    logos_dir: Path
    data_dir: Path
    web_dir: Path
    cors_origins: str | list[str]
    debug: bool
    umami_enabled: bool
    umami_url: str
    umami_website_id: str
    umami_timeout: int
    logo_cache_ttl_seconds: int


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_origins(value: str | None) -> str | list[str]:
    if not value or value.strip() == "*":
        return "*"
    origins = [origin.strip() for origin in value.split(",") if origin.strip()]
    return origins or "*"


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path(__file__).resolve().parent.parent
    static_dir = root / "static"

    return Settings(
        project_root=root,
        static_dir=static_dir,
        logos_dir=static_dir / "logos",
        data_dir=static_dir / "data",
        web_dir=static_dir / "web",
        cors_origins=_parse_origins(os.getenv("CORS_ORIGINS", "*")),
        debug=_parse_bool(os.getenv("DEBUG"), False),
        umami_enabled=_parse_bool(os.getenv("UMAMI_ENABLED"), True),
        umami_url=os.getenv("UMAMI_URL", "https://analytics.logotypes.dev/api/send"),
        umami_website_id=os.getenv("UMAMI_WEBSITE_ID", "e5291a10-0fea-4aad-9d53-22d3481ada30"),
        umami_timeout=int(os.getenv("UMAMI_TIMEOUT", "30")),
        logo_cache_ttl_seconds=int(os.getenv("LOGO_CACHE_TTL_SECONDS", "60")),
    )
