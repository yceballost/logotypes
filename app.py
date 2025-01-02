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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})


# Function to generate JSON from logo file name
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

# Function to wrap SVG content in HTML with Ahrefs tracking
def wrap_with_analytics(name, svg_content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>{name.capitalize()} Logo</title>
        <script
          src="https://analytics.ahrefs.com/analytics.js"
          data-key="NxIL3uTxgf1M7lSfSVpbWA"
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
def generate_json():
    """
    Endpoint to list all logos.
    Returns HTML with Ahrefs tracking or raw JSON.
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

    # Detect if the request is for JSON or HTML
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header:
        # Return raw JSON
        return jsonify({"records": json_data})

    # Format the data as HTML with Ahrefs tracking
    html_content = wrap_with_analytics(
        "All Logos",
        f"<pre>{json.dumps({'records': json_data}, indent=2)}</pre>"
    )
    return Response(html_content, content_type="text/html")

@app.route("/random")
def get_random_logo():
    """
    Endpoint to serve a random logo.
    Returns an HTML with Ahrefs tracking or raw SVG.
    """
    folder_path = "static/logos"
    logo_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    if not logo_files:
        return "No logos found", 404

    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter logos based on parameters
    filtered_logos = []
    for logo_file in logo_files:
        logo_data = generate_json_from_logo_name(logo_file)
        if (not variant_param or logo_data.get("variant") == variant_param) and \
           (not version_param or logo_data.get("version") == version_param):
            filtered_logos.append(logo_file)

    if not filtered_logos:
        return "No logo found with the specified parameters", 404

    # Select a random logo
    random_logo = random.choice(filtered_logos)
    svg_path = os.path.join(folder_path, random_logo)

    # Read the SVG content
    with open(svg_path, "r", encoding="utf-8") as svg_file:
        svg_content = svg_file.read()

    # Detect the type of request
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Serve HTML with tracking
        html_content = wrap_with_analytics("random", svg_content)
        return Response(html_content, content_type="text/html")

    # Serve raw SVG
    return Response(svg_content, content_type="image/svg+xml")


@app.route("/random/data")
def get_random_data():
    """
    Endpoint to retrieve data for a random logo.
    Returns HTML with Ahrefs tracking or raw JSON.
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

    # Detect the type of request
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Format data as HTML with Ahrefs tracking
        html_content = wrap_with_analytics("random data", f"<pre>{json.dumps(random_data, indent=2)}</pre>")
        return Response(html_content, content_type="text/html")

    # Return raw JSON data
    return jsonify(random_data)


@app.route("/<name>/data")
def get_name_data(name):
    """
    Endpoint to retrieve data for a specific logo.
    Returns HTML with Ahrefs tracking or raw JSON.
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

        # Detect the type of request (HTML or raw JSON)
        accept_header = request.headers.get("Accept", "")
        if "text/html" in accept_header:
            # Format data as HTML with Ahrefs tracking
            html_content = wrap_with_analytics(
                name,
                f"<pre>{json.dumps(name_data, indent=2)}</pre>"
            )
            return Response(html_content, content_type="text/html")

        # Return raw JSON data
        return jsonify(name_data)

    except Exception as e:
        logger.error(f"Error fetching data for name '{name}': {e}")
        return "Error fetching data", 500


@app.route("/<name>")
def get_logo(name):
    if name.startswith("umami"):
        return "Not handled by app.py", 404
    
    """
    Main endpoint to serve SVGs or HTML with tracking.
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
    svg_path = os.path.join(folder_path, selected_logo)

    # Log access for tracking
    referrer = request.referrer or "No referrer"
    user_agent = request.headers.get("User-Agent", "Unknown")
    logger.info(f"Accessed logo: {name}, Referrer: {referrer}, User-Agent: {user_agent}")

    # Send tracking data to Ahrefs analytics (or another system)
    try:
        tracking_url = "https://analytics.ahrefs.com/track"
        tracking_data = {
            "name": name,
            "variant": variant_param,
            "version": version_param,
            "referrer": referrer,
            "user_agent": user_agent
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(tracking_url, json=tracking_data, headers=headers)
        if response.status_code != 200:
            logger.warning(f"Tracking failed for logo: {name}. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error tracking logo: {name}. Exception: {str(e)}")

    # Serve raw SVG or HTML based on Accept header
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        # Wrap SVG in HTML with tracking script
        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()
        html_content = wrap_with_analytics(name, svg_content)
        return Response(html_content, content_type="text/html")

    # Serve raw SVG for image requests
    return send_from_directory(folder_path, selected_logo)



@app.route('/favicon-list')
def list_favicons():
    """
    Endpoint to list all available favicons.
    """
    logo_dir = 'static/logos'
    try:
        # Filter only files containing "glyph" and "color"
        logos = [f for f in os.listdir(logo_dir) if f.endswith('.svg') and "glyph" in f and "color" in f]
        return jsonify(logos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test.html')
def serve_test_page():
    return send_from_directory('static/web', 'test.html')

if __name__ == "__main__":
    app.run(debug=False)
