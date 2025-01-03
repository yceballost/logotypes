from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

import os
import random
import requests
import logging



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['COMPRESS_MIN_SIZE'] = 1024 

UMAMI_TIMEOUT = 30

# Function to generate JSON from logo file name
def generate_json_from_logo_name(logo_name):
    components = logo_name.split('-')
    if len(components) < 3:
        logger.warning(f"Invalid logo name: {logo_name}")
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
            lines = file.readlines()
            for line in lines:
                if line.startswith('Title:'):
                    data["example_title"] = line[len('Title:'):].strip()
                elif line.startswith('Description:'):
                    data["example_description"] = line[len('Description:'):].strip()

    return data

def send_umami_event(name, title, data=None):
    """
    Sends a tracking event to Umami with the given parameters.
    """
    try:
        umami_url = "https://analytics.logotypes.dev/api/send"
        payload = {
            "type": "event",  # Specify that this is a custom event
            "payload": {
                "website": "e5291a10-0fea-4aad-9d53-22d3481ada30",  # Site ID
                "url": request.url,  # Current request URL
                "name": name,  # Custom event name
                "title": title,  # Event title
                "language": request.headers.get("Accept-Language", "en-US"),
                "referrer": request.referrer or "Direct Access",  # Include referrer or "Direct Access"
                "origin": request.headers.get("Origin", "Unknown"),  # Include Origin if available
                "data": data or {}  # Additional metadata
            }
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": request.headers.get("User-Agent", "Unknown")
        }

        response = requests.post(umami_url, json=payload, headers=headers, timeout=UMAMI_TIMEOUT)
        logger.info(f"Umami response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logger.warning(f"Error tracking event: {response.text}")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while sending event: {name}")
    except Exception as e:
        logger.error(f"Error sending event {name}. Exception: {str(e)}")



@app.route('/')
def landing_page():
    return send_from_directory(app.static_folder, 'web/index.html')

@app.route('/style.css')
def style_file():
    return send_from_directory(app.static_folder, 'web/style.css')

@app.route("/all")
def generate_json():
    """
    Endpoint to list all logos.
    Returns raw JSON and sends a tracking event to Umami.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
    json_data = {}

    # Generate JSON data for all logos
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data:
            name = logo_data["name"].lower()
            if name not in json_data:
                json_data[name] = []
            json_data[name].append(logo_data)

    # Send tracking event
    send_umami_event(
        name="All Logos Access",
        title="All Logos",
        data={"total_logos": len(logo_files)}
    )

    # Return raw JSON
    return jsonify({"records": json_data})


@app.route("/random/data")
def get_random_data():
    """
    Endpoint to retrieve data for a random logo.
    Returns raw JSON and sends a tracking event to Umami.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No logos found", 404

    # Retrieve optional parameters
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter logos based on parameters
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data and \
           (not variant_param or logo_data.get("variant") == variant_param) and \
           (not version_param or logo_data.get("version") == version_param):
            filtered_logos.append(logo_data)

    if not filtered_logos:
        return "No data found with the specified parameters", 404

    # Select random data from filtered logos
    random_data = random.choice(filtered_logos)

    # Send tracking data to Umami
    send_umami_event(
        name="Random Data Access",
        title="Random Logo Data",
        data=random_data
    )

    # Return raw JSON data
    return jsonify(random_data)

@app.route("/random")
def get_random_logo():
    """
    Endpoint to serve a random logo.
    Returns raw SVG and sends a tracking event to Umami.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No logos found", 404

    random_logo = random.choice(logo_files)
    svg_path = os.path.join(folder_path, random_logo)

    # Read the SVG content
    with open(svg_path, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Get referrer and origin
    referrer = request.referrer or "Direct Access"
    origin = request.headers.get("Origin", "Unknown")
    
    # Send tracking event
    send_umami_event(
        name="Random Logo Access",
        title="Random Logo",
        data={
            "file": random_logo,
             "referrer": referrer,
            "origin": origin
        }
    )

    # Serve raw SVG
    return Response(svg_content, content_type="image/svg+xml")


@app.route("/<name>/data")
def get_name_data(name):
    """
    Endpoint to retrieve data for a specific logo.
    Returns raw JSON and sends a tracking event to Umami.
    """
    try:
        # Load data directly from the file system
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

        # Retrieve data for the requested logo
        name_data = records.get(name.lower(), [])

        if not name_data:
            return "Name not found", 404

        # Get referrer and origin
        referrer = request.referrer or "Direct Access"
        origin = request.headers.get("Origin", "Unknown")

        # Send tracking data to Umami
        send_umami_event(
            name=f"{name} Data Access",
            title=f"{name} Data",
            data={
                "records": len(name_data), 
                "referrer": referrer,
                "origin": origin
            }  
        )

        # Return raw JSON data
        return jsonify(name_data)

    except Exception as e:
        logger.error(f"Error fetching data for name '{name}': {e}")
        return "Error fetching data", 500


@app.route("/<name>")
def get_logo(name):
    """
    Endpoint to serve a specific logo by name and send a custom event to Umami.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg') and name.lower() in f.lower()]

    if not logo_files:
        return "Logo not found", 404

    # Retrieve optional parameters
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter logos based on provided parameters
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if (not variant_param or logo_data.get("variant") == variant_param) and \
           (not version_param or logo_data.get("version") == version_param):
            filtered_logos.append(logo_file)

    if not filtered_logos:
        return "No logo found with the specified parameters", 404

    # Select the first filtered logo
    selected_logo = filtered_logos[0]

     # Get referrer and origin
    referrer = request.referrer or "Direct Access"
    origin = request.headers.get("Origin", "Unknown")

    # Send tracking data to Umami
    send_umami_event(
        name=f"{name} (image access)",
        title="Logo Image Access",
        data={
            "variant": variant_param,
            "version": version_param,
            "referrer": referrer,
            "origin": origin
        }
    )

    # Serve the SVG
    return send_from_directory(folder_path, selected_logo)

@app.route('/favicon-list')
def list_favicons():
    logo_dir = 'static/logos'
    try:
        logos = [f for f in os.listdir(logo_dir) if f.endswith('.svg') and "glyph" in f and "color" in f]
        return jsonify(logos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/test.html')
def serve_test_page():
    return send_from_directory('static/web', 'test.html')

if __name__ == "__main__":
    app.run(debug=False)
