from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

import os
import random
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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

# Function to send events to Umami API
def send_umami_event(name, referrer, user_agent, additional_data=None):
    try:
        umami_url = "https://analytics.logotypes.dev/api/send"
        payload = {
            "type": "event",
            "payload": {
                "website": "e5291a10-0fea-4aad-9d53-22d3481ada30",  # Verifica este ID
                "url": request.url,
                "referrer": referrer,
                "language": request.headers.get("Accept-Language", "en-US"),
                "title": name,
                "data": additional_data or {}
            }
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": user_agent
        }

        # Log the payload for debugging
        logger.info(f"Sending Umami event: {json.dumps(payload)}")

        response = requests.post(umami_url, json=payload, headers=headers)
        
        # Log response details
        logger.info(f"Umami response: {response.status_code}, {response.text}")
        if response.status_code != 200:
            logger.warning(f"Error sending event: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Umami event for {name}: {e}")


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
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data:
            name = logo_data["name"].lower()
            if name not in json_data:
                json_data[name] = []
            json_data[name].append(logo_data)

    # Send tracking data to Umami
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    send_umami_event("All Logos Access", referrer, user_agent)

    return jsonify({"records": json_data})

@app.route("/random/data")
def get_random_data():
    """
    Endpoint to retrieve data for a random logo.
    Returns raw JSON.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No logos found", 404

    # Retrieve request parameters
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter logos based on parameters
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if logo_data:  # Ensure the logo has valid data
            if (not variant_param or logo_data.get("variant") == variant_param) and \
               (not version_param or logo_data.get("version") == version_param):
                filtered_logos.append(logo_data)

    if not filtered_logos:
        return "No data found with the specified parameters", 404

    # Select random data from filtered logos
    random_data = random.choice(filtered_logos)

    # Send tracking data to Umami
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    send_umami_event("Random Data Access", referrer, user_agent, additional_data={"data": random_data})

    # Return raw JSON data
    return jsonify(random_data)

@app.route("/random")
def get_random_logo():
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No logos found", 404

    random_logo = random.choice(logo_files)
    svg_path = os.path.join(folder_path, random_logo)

    with open(svg_path, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Send tracking data to Umami
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    send_umami_event("Random Logo Access", referrer, user_agent)

    return Response(svg_content, content_type="image/svg+xml")

@app.route("/<name>/data")
def get_name_data(name):
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

    name_data = records.get(name.lower(), [])
    if not name_data:
        return "Name not found", 404

    # Send tracking data to Umami
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    send_umami_event(f"Data Access for {name}", referrer, user_agent)

    return jsonify(name_data)

@app.route("/<name>")
def get_logo(name):
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg') and name.lower() in f.lower()]

    if not logo_files:
        return "Logo not found", 404

    selected_logo = logo_files[0]

    # Send tracking data to Umami
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    send_umami_event(f"Logo Access: {name}", referrer, user_agent)

    return send_from_directory(folder_path, selected_logo)

@app.route('/favicon-list')
def list_favicons():
    logo_dir = 'static/logos'
    try:
        logos = [f for f in os.listdir(logo_dir) if f.endswith('.svg') and "glyph" in f and "color" in f]
        return jsonify(logos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
