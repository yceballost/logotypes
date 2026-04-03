from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS

from core.config import load_settings
from core.logo_repository import LogoRepository
from core.routes import register_routes
from core.tracking import UmamiTracker


logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    settings = load_settings()

    app = Flask(__name__, static_folder=str(settings.static_dir))
    CORS(app, resources={r"/*": {"origins": settings.cors_origins}})

    repository = LogoRepository(settings)
    tracker = UmamiTracker(settings)
    register_routes(app, repository, tracker, settings)

    return app


app = create_app()


if __name__ == "__main__":
    settings = load_settings()
    app.run(debug=settings.debug)
