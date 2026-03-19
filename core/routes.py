from __future__ import annotations

from flask import Response, jsonify, request, send_from_directory

from core.config import Settings
from core.logo_repository import LogoRecord, LogoRepository
from core.tracking import UmamiTracker


def _record_to_public_data(record: LogoRecord, host_url: str) -> dict:
    data = {
        "logo": f"{host_url}static/logos/{record.filename}",
        "name": record.slug.capitalize(),
        "variant": record.variant,
        "version": record.version,
    }

    if record.example_title:
        data["example_title"] = record.example_title
    if record.example_description:
        data["example_description"] = record.example_description
    return data


def register_routes(app, repository: LogoRepository, tracker: UmamiTracker, settings: Settings) -> None:
    @app.route("/")
    def landing_page():
        return send_from_directory(str(settings.web_dir), "index.html")

    @app.route("/style.css")
    def style_file():
        return send_from_directory(str(settings.web_dir), "style.css")

    @app.route("/all")
    def generate_json():
        grouped = repository.grouped_records()
        json_data = {
            name: [_record_to_public_data(record, request.host_url) for record in records]
            for name, records in grouped.items()
        }

        exclude_tracking = request.args.get("example") == "true" or request.referrer == "Direct Access"
        if not exclude_tracking:
            tracker.send_event(
                request=request,
                name="All Logos Access",
                title="All Logos",
                data={"total_logos": len(repository.all_records())},
            )

        return jsonify({"records": json_data})

    @app.route("/random/data")
    def get_random_data():
        variant_param = request.args.get("variant")
        version_param = request.args.get("version")
        random_record = repository.random_record(variant=variant_param, version=version_param)

        if not random_record:
            return "No data found with the specified parameters", 404

        response_data = _record_to_public_data(random_record, request.host_url)
        tracker.send_event(
            request=request,
            name="Random Data Access",
            title="Random Logo Data",
            data=response_data,
        )

        return jsonify(response_data)

    @app.route("/random")
    def get_random_logo():
        variant_param = request.args.get("variant")
        version_param = request.args.get("version")
        random_record = repository.random_record(variant=variant_param, version=version_param)

        if not random_record:
            return "No logos found", 404

        svg_path = settings.logos_dir / random_record.filename
        svg_content = svg_path.read_text(encoding="utf-8")

        referrer = request.referrer or "Direct Access"
        origin = request.headers.get("Origin", "Unknown")
        exclude_tracking = request.args.get("example") == "true" or referrer == "Direct Access"

        if not exclude_tracking:
            tracker.send_event(
                request=request,
                name="Random Logo Access",
                title="Random Logo",
                data={"file": random_record.filename, "origin": origin},
            )

        return Response(svg_content, content_type="image/svg+xml")

    @app.route("/<name>/data")
    def get_name_data(name):
        try:
            name_records = repository.records_by_name(name)
            if not name_records:
                return "Name not found", 404

            response_data = [_record_to_public_data(record, request.host_url) for record in name_records]

            origin = request.headers.get("Origin", "Unknown")
            tracker.send_event(
                request=request,
                name=f"{name} Data Access",
                title=f"{name} Data",
                data={"records": len(name_records), "origin": origin},
            )

            return jsonify(response_data)
        except Exception:
            return "Error fetching data", 500

    @app.route("/<name>")
    def get_logo(name):
        name_records = repository.records_by_name(name)
        if not name_records:
            return "Logo not found", 404

        variant_param = request.args.get("variant")
        version_param = request.args.get("version")
        filtered_records = repository.filter_records(name_records, variant=variant_param, version=version_param)

        if not filtered_records:
            return "No logo found with the specified parameters", 404

        selected_logo = filtered_records[0].filename

        referrer_url = request.referrer or "Unknown"
        origin = request.headers.get("Origin", "Unknown")
        exclude_tracking = "/name" in request.path or request.args.get("example") == "true"
        if not exclude_tracking:
            tracker.send_event(
                request=request,
                name=f"{name} (image access)",
                title="Logo Image Access",
                data={
                    "variant": variant_param,
                    "version": version_param,
                    "referrer_url": referrer_url,
                    "origin": origin,
                },
            )

        return send_from_directory(str(settings.logos_dir), selected_logo)

    @app.route("/favicon-list")
    def list_favicons():
        try:
            return jsonify(repository.favicon_records())
        except Exception as error:
            return jsonify({"error": str(error)}), 500

    @app.route("/test.html")
    def serve_test_page():
        return send_from_directory(str(settings.web_dir), "test.html")
