from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

import os
import random
import json
import requests
import urllib.parse
import http.client
from functools import wraps
import logging



# Configura el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')

# Función para enviar eventos a Google Analytics
def send_to_ga(endpoint, full_url, referrer):
    measurement_id = GA_TRACKING_ID
    api_secret = os.environ.get('GA_API_SECRET')
    
    ga_endpoint = f'https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}'
    
    payload = {
        'client_id': '555', 
        'events': [{
            'name': 'api_call',
            'params': {
                'endpoint': endpoint,
                'full_url': full_url,
                'referrer': referrer
            }
        }]
    }
    
    logger.info(f"Sending event to GA for endpoint: {endpoint}")
    logger.info(f"GA Endpoint: {ga_endpoint}")
    logger.info(f"Payload: {json.dumps(payload)}")
    
    try:
        response = requests.post(ga_endpoint, json=payload, timeout=10)
        logger.info(f"GA Response: {response.status_code}")
        
        if response.status_code == 204:
            logger.info("Successfully sent event to GA (204 No Content)")
        elif response.status_code != 200:
            logger.error(f"Error sending to GA. Status code: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            logger.error(f"Response headers: {response.headers}")
        else:
            logger.info("Successfully sent event to GA")
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception occurred while sending to GA: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while sending to GA: {str(e)}")

# Decorador para rastrear llamadas API
def track_api_call(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = request.path
        full_url = request.url
        referrer = request.referrer or 'No referrer'
        
        logger.info(f"API call to endpoint: {endpoint}")
        logger.info(f"Full URL: {full_url}")
        logger.info(f"Referrer: {referrer}")
        
        send_to_ga(endpoint, full_url, referrer)
        return f(*args, **kwargs)
    return decorated_function

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

def wrap_with_analytics(name, svg_content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>{name.capitalize()} Logo</title>
        <script
          src="https://analytics.ahrefs.com/analytics.js"
          data-key="TU_CLAVE_AHREFS"
          async
        ></script>
      </head>
      <body>
        <div>
          {svg_content}
        </div>
      </body>
    </html>
    """

@app.route('/')
def landing_page():
    return send_from_directory(app.static_folder, 'web/index.html')

@app.route('/style.css')
def style_file():
    return send_from_directory(app.static_folder, 'web/style.css')

@app.route("/all")
@track_api_call
def generate_json():
    """
    Endpoint para listar todos los logos.
    Devuelve HTML con rastreo de Ahrefs o JSON crudo.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
    json_data = {}

    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data:
            name = logo_data["name"].lower()
            if name not in json_data:
                json_data[name] = []
            json_data[name].append(logo_data)

    # Detectar si la solicitud es para JSON o HTML
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header:
        # Devolver JSON crudo
        return jsonify({"records": json_data})

    # Formatear los datos como HTML con rastreo de Ahrefs
    html_content = wrap_with_analytics(
        "All Logos",
        f"<pre>{json.dumps({'records': json_data}, indent=2)}</pre>"
    )
    return Response(html_content, content_type="text/html")


@app.route("/random")
@track_api_call
def get_random_logo():
    """
    Endpoint para servir un logo aleatorio.
    Puede devolver un HTML con rastreo de Ahrefs o SVG crudo.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No se encontraron logos", 404

    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filtrar los logos según los parámetros
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if (not variant_param or logo_data.get("variant") == variant_param) and \
           (not version_param or logo_data.get("version") == version_param):
            filtered_logos.append(logo_file)

    if not filtered_logos:
        return "No se encontró un logo con los parámetros especificados", 404

    # Seleccionar un logo aleatorio
    random_logo = random.choice(filtered_logos)
    svg_path = os.path.join(folder_path, random_logo)

    # Leer el contenido del SVG
    with open(svg_path, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Detectar el tipo de solicitud
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Servir HTML con rastreo
        html_content = wrap_with_analytics("random", svg_content)
        return Response(html_content, content_type="text/html")

    # Servir SVG crudo
    return Response(svg_content, content_type="image/svg+xml")

@app.route("/random/data")
@track_api_call
def get_random_data():
    """
    Endpoint para obtener los datos de un logo aleatorio.
    Devuelve HTML con rastreo de Ahrefs o JSON crudo.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No se encontraron logos", 404

    # Obtener los parámetros de la solicitud
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filtrar los logos según los parámetros
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data:  # Asegurarnos de que el logo tenga datos válidos
            if (not variant_param or logo_data.get("variant") == variant_param) and \
               (not version_param or logo_data.get("version") == version_param):
                filtered_logos.append(logo_data)

    if not filtered_logos:
        return "No se encontraron datos con los parámetros especificados", 404

    # Seleccionar un logo aleatorio de los filtrados
    random_data = random.choice(filtered_logos)

    # Detectar el tipo de solicitud
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Formatear los datos como HTML con el rastreo de Ahrefs
        html_content = wrap_with_analytics("random data", f"<pre>{json.dumps(random_data, indent=2)}</pre>")
        return Response(html_content, content_type="text/html")

    # Devolver los datos en formato JSON crudo
    return jsonify(random_data)


@app.route("/<name>/data")
@track_api_call
def get_name_data(name):
    """
    Endpoint para obtener los datos de un logo específico.
    Devuelve HTML con rastreo de Ahrefs o JSON crudo.
    """
    try:
        # Cargar los datos directamente desde el sistema de archivos
        folder_path = "static/logos"
        logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
        records = {}

        for logo_file in logo_files:
            logo_data = generate_json_from_logo_name(logo_file)
            if logo_data:
                logo_name = logo_data["name"].lower()
                if logo_name not in records:
                    records[logo_name] = []
                records[logo_name].append(logo_data)

        # Obtener los datos del logo solicitado
        name_data = records.get(name.lower(), [])

        if not name_data:
            return "Name not found", 404

        # Detectar el tipo de solicitud (HTML o JSON crudo)
        accept_header = request.headers.get("Accept", "")
        if "text/html" in accept_header:
            # Formatear los datos como HTML con rastreo de Ahrefs
            html_content = wrap_with_analytics(
                name,
                f"<pre>{json.dumps(name_data, indent=2)}</pre>"
            )
            return Response(html_content, content_type="text/html")

        # Devolver los datos en formato JSON crudo
        return jsonify(name_data)

    except Exception as e:
        logger.error(f"Error fetching data for name '{name}': {e}")
        return "Error fetching data", 500


@app.route("/<name>")
def get_logo(name):
    """
    Endpoint principal para servir SVGs o HTML con rastreo de Ahrefs.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg') and name.lower() in f.lower()]

    if not logo_files:
        return "No se encontró el logo", 404

    # Obtener los parámetros opcionales
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filtrar logos según los parámetros proporcionados
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if (not variant_param or logo_data.get("variant") == variant_param) and \
           (not version_param or logo_data.get("version") == version_param):
            filtered_logos.append(logo_file)

    if not filtered_logos:
        return "No se encontró un logo con los parámetros especificados", 404

    # Seleccionar el primer logo filtrado
    selected_logo = filtered_logos[0]
    svg_path = os.path.join(folder_path, selected_logo)

    # Leer el contenido del SVG
    with open(svg_path, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Registrar acceso para rastreo adicional
    logger.info(f"Acceso al logo: {name}, Variant: {variant_param}, Version: {version_param}")

    # Detectar el tipo de solicitud (HTML o SVG crudo)
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Servir HTML con el rastreo de Ahrefs
        svg_url = f"{request.host_url}{name}?variant={variant_param}&version={version_param}"
        html_content = wrap_with_analytics(name, svg_content)
        return Response(html_content, content_type="text/html")

    # Servir SVG crudo si el navegador lo solicita explícitamente
    return Response(svg_content, content_type="image/svg+xml")


@app.route('/api/datos')
@track_api_call
def get_datos():
    # Tu lógica aquí
    return {"mensaje": "Datos obtenidos"}

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
