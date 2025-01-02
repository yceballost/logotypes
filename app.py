from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

import os
import random
import json
import requests
import logging

# Configura el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Función para envolver contenido SVG o JSON en HTML
def wrap_with_html(content, title="Content"):
    """
    Envuelve un contenido (SVG o JSON) en un HTML.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>{title}</title>
        <script
          src="https://analytics.ahrefs.com/analytics.js"
          data-key="NxIL3uTxgf1M7lSfSVpbWA"
          async
        ></script>
      </head>
      <body>
        {content}
      </body>
    </html>
    """

def generate_json_from_logo_name(logo_name):
    components = logo_name.split('-')
    if len(components) < 3:
        logger.warning(f"Invalid logo name format: {logo_name}")
        return None

    name = components[0]
    variant = components[1]
    version = components[2].split('.')[0]
    logo_url = f"{request.host_url}static/logos/{logo_name}"
    metadata_filename = f"{name}.txt"
    metadata_path = os.path.join('static/data', metadata_filename)
    data = {
        "logo": logo_url,
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as file:
            for line in file:
                if line.startswith('Title:'):
                    data["example_title"] = line[len('Title:'):].strip()
                elif line.startswith('Description:'):
                    data["example_description"] = line[len('Description:'):].strip()

    return data

@app.route('/')
def landing_page():
    return send_from_directory(app.static_folder, 'web/index.html')

@app.route('/style.css')
def style_file():
    return send_from_directory(app.static_folder, 'web/style.css')

@app.route("/all")
def generate_json():
    try:
        folder_path = "static/logos"
        logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
        json_data = {}
        for logo_file in logo_files:
            name = logo_file.split('-')[0]
            if name not in json_data:
                json_data[name] = []
            json_data[name].append(generate_json_from_logo_name(logo_file))

        data_final = {"records": json_data}
        html_content = wrap_with_html(
            f"<pre>{json.dumps(data_final, indent=2)}</pre>",
            title="All Logos Data"
        )
        return Response(html_content, content_type='text/html')

    except Exception as e:
        logger.error(f"Error in /all: {e}")
        return "Error generating data", 500

@app.route("/random")
def get_random_logo():
    try:
        folder_path = "static/logos"
        logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
        if not logo_files:
            return "No logo found", 404

        random_logo = random.choice(logo_files)
        svg_path = os.path.join(folder_path, random_logo)

        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        html_content = wrap_with_html(svg_content, title="Random Logo")
        return Response(html_content, content_type='text/html')

    except Exception as e:
        logger.error(f"Error in /random: {e}")
        return "Error fetching random logo", 500

@app.route("/random/data")
def get_random_data():
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()
        data = response.json()
        all_items = [item for sublist in data.get("records", {}).values() for item in sublist]

        variant_param = request.args.get("variant")
        version_param = request.args.get("version")

        if variant_param:
            all_items = [item for item in all_items if item.get("variant") == variant_param]
        if version_param:
            all_items = [item for item in all_items if item.get("version") == version_param]

        if all_items:
            random_item = random.choice(all_items)
            html_content = wrap_with_html(
                f"<pre>{json.dumps(random_item, indent=2)}</pre>",
                title="Random Data"
            )
            return Response(html_content, content_type='text/html')
        else:
            return "No matching data found", 404

    except Exception as e:
        logger.error(f"Error in /random/data: {e}")
        return "Error fetching random data", 500

@app.route("/<name>/data")
def get_name_data(name):
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()
        records = response.json().get("records", {})
        name_data = records.get(name.lower(), [])

        if name_data:
            html_content = wrap_with_html(
                f"<pre>{json.dumps(name_data, indent=2)}</pre>",
                title=f"{name.capitalize()} Data"
            )
            return Response(html_content, content_type='text/html')
        else:
            return "Name not found", 404

    except Exception as e:
        logger.error(f"Error in /<name>/data: {e}")
        return "Error fetching name data", 500

@app.route("/<name>")
def get_logo_variants(name):
    try:
        folder_path = "static/logos"
        logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg') and name.lower() in f.lower()]
        if not logo_files:
            return "No logo found", 404

        random_logo = random.choice(logo_files)
        svg_path = os.path.join(folder_path, random_logo)

        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        html_content = wrap_with_html(svg_content, title=f"{name.capitalize()} Logo")
        return Response(html_content, content_type='text/html')

    except Exception as e:
        logger.error(f"Error in /<name>: {e}")
        return "Error fetching logo variants", 500

@app.route('/favicon-list')
def list_favicons():
    logo_dir = 'static/logos'
    try:
        logos = [f for f in os.listdir(logo_dir) if f.endswith('.svg') and "glyph" in f and "color" in f]
        return jsonify(logos)
    except Exception as e:
        logger.error(f"Error in /favicon-list: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
