from flask import Flask, jsonify, request, send_from_directory, send_file, Response
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

# Función para envolver contenido SVG en HTML con Ahrefs script
def analytics_wrapper(svg_content, title="Logo"):
    """
    Envuelve un contenido SVG en un HTML con el script de Ahrefs.
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
        {svg_content}
      </body>
    </html>
    """

def generate_json_from_logo_name(logo_name):
    components = logo_name.split('-')
    if len(components) < 3:
        print(f"Not valid: {logo_name}")
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
        example_title = None
        example_description = None
        with open(metadata_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('Title:'):
                    example_title = line[len('Title:'):].strip()
                elif line.startswith('Description:'):
                    example_description = line[len('Description:'):].strip()
        if example_title:
            data["example_title"] = example_title
        if example_description:
            data["example_description"] = example_description

    return data

@app.route('/')
def landing_page():
    return send_from_directory(app.static_folder, 'web/index.html')

@app.route('/style.css')
def style_file():
    return send_from_directory(app.static_folder, 'web/style.css')

@app.route("/all")
def generate_json():
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
    json_data = {}
    for logo_file in logo_files:
        name = logo_file.split('-')[0]
        if name not in json_data:
            json_data[name] = []
        json_data[name].append(generate_json_from_logo_name(logo_file))

    data_final = {
        "records": json_data
    }
    json_data_formatted = json.dumps(data_final, indent=2)

    # Envolver en HTML
    html_content = analytics_wrapper(
        f"<pre>{json_data_formatted}</pre>",
        title="All Logos Data"
    )
    return Response(html_content, content_type='text/html')

@app.route("/random")
def get_random_logo():
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if (variant_param and logo_data.get("variant") != variant_param) or \
           (version_param and logo_data.get("version") != version_param):
            continue
        filtered_logos.append(logo_file)

    if filtered_logos:
        random_logo = random.choice(filtered_logos)
        svg_path = os.path.join(folder_path, random_logo)

        # Leer el contenido del archivo SVG
        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        # Usar la función para envolver el SVG
        html_content = analytics_wrapper(svg_content, title="Random Logo")
        return Response(html_content, content_type='text/html')
    else:
        return "No logo found with the specified parameters", 404

@app.route("/random/data")
def get_random_data():
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()
        data = response.json()
        records = data.get("records", {})
        all_items = [item for sublist in records.values() for item in sublist]

        if variant_param:
            all_items = [item for item in all_items if item.get("variant") == variant_param]
        if version_param:
            all_items = [item for item in all_items if item.get("version") == version_param]

        if all_items:
            random_item = random.choice(all_items)
            json_data = json.dumps(random_item, indent=2)

            # Envolver en HTML
            html_content = analytics_wrapper(
                f"<pre>{json_data}</pre>",
                title="Random Data"
            )
            return Response(html_content, content_type='text/html')
        else:
            return "No data available with the specified parameters", 404

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return "Error fetching data", 500

@app.route("/<name>/data")
def get_name_data(name):
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()
        data = response.json()
        records = data.get("records", {})
        name_data = records.get(name.lower(), [])

        if name_data:
            json_data = json.dumps(name_data, indent=2)
            html_content = analytics_wrapper(
                f"<pre>{json_data}</pre>", 
                title=f"{name.capitalize()} Data"
            )
            return Response(html_content, content_type='text/html')
        else:
            return "Name not found", 404

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return "Error fetching data", 500

@app.route("/<name>")
def get_logo_variants(name):
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data.get("name").lower() == name.lower():
            if (variant_param and logo_data.get("variant") != variant_param) or \
               (version_param and logo_data.get("version") != version_param):
                continue
            filtered_logos.append(logo_data)

    if filtered_logos:
        sorted_logos = sorted(filtered_logos, key=lambda x: x['version'], reverse=True)
        logo_name = sorted_logos[0]['logo'].split('/')[-1]
        svg_path = os.path.join(folder_path, logo_name)

        # Leer el contenido del archivo SVG
        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        # Usar la función para envolver el SVG
        html_content = analytics_wrapper(svg_content, title=f"{name.capitalize()} Logo")
        return Response(html_content, content_type='text/html')
    else:
        return "No logo found with the specified parameters", 404

@app.route('/favicon-list')
def list_favicons():
    logo_dir = 'static/logos'
    try:
        # Filtrar solo los archivos que contienen "glyph" y "color"
        logos = [f for f in os.listdir(logo_dir) if f.endswith('.svg') and "glyph" in f and "color" in f]
        return jsonify(logos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
