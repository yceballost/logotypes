from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging
import random
import time

from core.config import Settings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LogoRecord:
    slug: str
    variant: str
    version: str
    filename: str
    example_title: str | None = None
    example_description: str | None = None


class LogoRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._records_cache: list[LogoRecord] = []
        self._records_by_slug_cache: dict[str, list[LogoRecord]] = {}
        self._cache_expiration = 0.0

    @staticmethod
    def _parse_logo_filename(filename: str) -> tuple[str, str, str] | None:
        stem = Path(filename).stem
        try:
            slug, variant, version = stem.rsplit("-", 2)
        except ValueError:
            logger.warning("Invalid logo filename: %s", filename)
            return None

        if not slug or not variant or not version:
            logger.warning("Invalid logo filename: %s", filename)
            return None

        return slug.lower(), variant.lower(), version.lower()

    def _metadata_candidates(self, slug: str) -> list[Path]:
        compact = slug.replace("-", "").replace("_", "")
        return [
            self.settings.data_dir / f"{slug}.txt",
            self.settings.data_dir / f"{slug.replace('-', '_')}.txt",
            self.settings.data_dir / f"{slug.replace('_', '-')}.txt",
            self.settings.data_dir / f"{compact}.txt",
        ]

    def _read_metadata(self, slug: str) -> tuple[str | None, str | None]:
        for candidate in self._metadata_candidates(slug):
            if not candidate.exists():
                continue

            title = None
            description = None
            with candidate.open("r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("Title:"):
                        title = line[len("Title:"):].strip()
                    elif line.startswith("Description:"):
                        description = line[len("Description:"):].strip()
            return title, description

        return None, None

    def _refresh_if_stale(self) -> None:
        now = time.monotonic()
        if self._records_cache and now < self._cache_expiration:
            return

        logos_dir = self.settings.logos_dir
        if not logos_dir.exists():
            self._records_cache = []
            self._records_by_slug_cache = {}
            self._cache_expiration = now + self.settings.logo_cache_ttl_seconds
            return

        records: list[LogoRecord] = []
        for logo_file in sorted(logos_dir.iterdir()):
            if logo_file.suffix.lower() != ".svg":
                continue

            parsed = self._parse_logo_filename(logo_file.name)
            if not parsed:
                continue

            slug, variant, version = parsed
            title, description = self._read_metadata(slug)
            records.append(
                LogoRecord(
                    slug=slug,
                    variant=variant,
                    version=version,
                    filename=logo_file.name,
                    example_title=title,
                    example_description=description,
                )
            )

        by_slug: dict[str, list[LogoRecord]] = {}
        for record in records:
            by_slug.setdefault(record.slug, []).append(record)

        self._records_cache = records
        self._records_by_slug_cache = by_slug
        self._cache_expiration = now + self.settings.logo_cache_ttl_seconds

    @staticmethod
    def _canonical_name(value: str) -> str:
        return value.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

    def all_records(self) -> list[LogoRecord]:
        self._refresh_if_stale()
        return self._records_cache

    def grouped_records(self) -> dict[str, list[LogoRecord]]:
        self._refresh_if_stale()
        return self._records_by_slug_cache

    def records_by_name(self, name: str) -> list[LogoRecord]:
        self._refresh_if_stale()
        canonical = self._canonical_name(name)
        return [
            record
            for record in self._records_cache
            if self._canonical_name(record.slug) == canonical
        ]

    def filter_records(
        self,
        records: list[LogoRecord],
        variant: str | None = None,
        version: str | None = None,
    ) -> list[LogoRecord]:
        variant_value = variant.lower() if variant else None
        version_value = version.lower() if version else None
        return [
            record
            for record in records
            if (not variant_value or record.variant == variant_value)
            and (not version_value or record.version == version_value)
        ]

    def random_record(
        self,
        variant: str | None = None,
        version: str | None = None,
    ) -> LogoRecord | None:
        records = self.filter_records(self.all_records(), variant=variant, version=version)
        if not records:
            return None
        return random.choice(records)

    def favicon_records(self) -> list[str]:
        records = self.filter_records(self.all_records(), variant="glyph", version="color")
        return [record.filename for record in records]
