from __future__ import annotations

import logging
from urllib.parse import urlparse

import requests

from core.config import Settings


logger = logging.getLogger(__name__)


class UmamiTracker:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_event(self, request, name: str, title: str, data: dict | None = None) -> None:
        if not self.settings.umami_enabled:
            return

        try:
            referrer_url = request.referrer or "Unknown"
            parsed_referrer = urlparse(referrer_url)
            referrer_host = parsed_referrer.netloc
            origin = request.headers.get("Origin", "Unknown")

            payload = {
                "type": "event",
                "payload": {
                    "hostname": request.host,
                    "language": request.headers.get("Accept-Language", "en-US"),
                    "referrer": referrer_url,
                    "screen": request.headers.get("Screen-Resolution", "Unknown"),
                    "title": title,
                    "url": request.url,
                    "website": self.settings.umami_website_id,
                    "name": name,
                    "data": data
                    or {
                        "referrer_url": referrer_url,
                        "referrer_host": referrer_host,
                        "origin": origin,
                    },
                },
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": request.headers.get("User-Agent", "Unknown"),
            }

            response = requests.post(
                self.settings.umami_url,
                json=payload,
                headers=headers,
                timeout=self.settings.umami_timeout,
            )

            if response.status_code != 200:
                logger.warning("Umami tracking error (%s): %s", response.status_code, response.text)
        except requests.exceptions.Timeout:
            logger.error("Timeout error while sending Umami event: %s", name)
        except Exception as error:
            logger.error("Error sending Umami event %s: %s", name, error)
