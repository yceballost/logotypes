from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import random
import requests
import urllib.parse
import http.client

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})

GA_TRACKING_ID = 'G-KQCFQFWW6V'

def track_pageview(page_title, page_path):
    """Send pageview to Google Analytics with optional page title"""
    params = {
        'v': 1,                # API version
        'tid': GA_TRACKING_ID, # Tracking ID
        'cid': '555',          # Client ID
        't': 'pageview',       # Pageview hit type
        'dp': page_path,       # Document path (URL)
        'dt': page_title       # Document title
    }
    encoded_params = urllib.parse.urlencode(params)

    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = http.client.HTTPSConnection("www.google-analytics.com")
    
    try:
        conn.request("POST", "/collect", encoded_params, headers)
        response = conn.getresponse()
        response_status = response.status
        response_data = response.read()

        if response_status == 200:
            print(f"GA Response: {response_data.decode('utf-8', errors='ignore')}")
        else:
            print(f"GA Error {response_status}: {response_data.decode('utf-8', errors='ignore')}")
    
    except Exception as e:
        print(f"Error tracking pageview: {e}")
    
    finally:
        conn.close()

@app.route('/')
def landing_page():
    return send_from_directory(app.static_folder, 'web/index.html')

@app.route('/style.css')
def style_file():
    return send_from_directory(app.static_folder, 'web/style.css')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    return jsonify(data_final)

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
        logo_data = generate_json_from_logo_name(random_logo)
        # Send a pageview with the logo name as the page title
        track_pageview(page_title=logo_data['name'], page_path=f'/random/{random_logo}')
        return send_from_directory(app.static_folder, f"logos/{random_logo}")
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
            return jsonify(random_item)
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
            return jsonify(name_data)
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
        return send_from_directory(app.static_folder, f"logos/{logo_name}")
    else:
        return "No logo found with the specified parameters", 404

if __name__ == "__main__":
    app.run(debug=False)
