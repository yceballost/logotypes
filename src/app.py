from flask import Flask, jsonify, request, redirect, send_from_directory
from flask_cors import CORS
import os
import random
from middleware import log_request_info

app = Flask(__name__, static_folder="../static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def before_request():
    log_request_info()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def generate_json_from_image_name(image_name):
    # Split the image name into its components
    components = image_name.split('-')

    if len(components) < 3:
        print(f"Not valid: {image_name}")
        return None

    name = components[0]
    variant = components[1]
    version = components[2].split('.')[0]

    # Create the absolute URL of the image
    image_url = f"{request.host_url}static/images/{image_name}"

    # Define the path for the metadata file
    metadata_filename = f"{name}.txt"
    metadata_path = os.path.join('static/data', metadata_filename)

    # Initialize the JSON dictionary
    data = {
        "image": image_url,
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    # Read the metadata file if it exists
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
        
        # Add the title and description to the JSON dictionary if available
        if example_title:
            data["example_title"] = example_title
        if example_description:
            data["example_description"] = example_description

    return data

@app.route("/all")
def generate_json():
    # Get the list of files in the "images" folder
    folder_path = "static/images"
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    # Generate JSON for each found image
    json_data = {}
    for image_file in image_files:
        name = image_file.split('-')[0]
        if name not in json_data:
            json_data[name] = []
        json_data[name].append(generate_json_from_image_name(image_file))

    # Create the final dictionary with the desired structure
    data_final = {
        "records": json_data
    }

    # Return the final dictionary as JSON response
    return jsonify(data_final)

@app.route("/random")
def get_random_json():
    # Get the list of files in the "images" folder
    folder_path = "static/images"
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    # Get the URL parameters
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter the results based on the specified parameters
    filtered_images = []
    for image_file in image_files:
        image_data = generate_json_from_image_name(image_file)
        if (variant_param and image_data.get("variant") != variant_param) or \
           (version_param and image_data.get("version") != version_param):
            continue
        filtered_images.append(image_data)

    if filtered_images:
        # Generate JSON for a random element among the filtered images
        random_image_data = random.choice(filtered_images)
        image_url = random_image_data['image']
        return redirect(image_url)

    else:
        return "No logo found with the specified parameters", 404

@app.route("/<name>")
def get_logo_variants(name):
    # Get the list of files in the "images" folder
    folder_path = "static/images"
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

    # Get the URL parameters
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filter the results based on the name and specified parameters
    filtered_images = []
    for image_file in image_files:
        image_data = generate_json_from_image_name(image_file)
        if image_data.get("name").lower() == name.lower():
            if (variant_param and image_data.get("variant") != variant_param) or \
               (version_param and image_data.get("version") != version_param):
                continue
            filtered_images.append(image_data)

    if filtered_images:
        # Sort the images by version, so that the color version appears first
        sorted_images = sorted(filtered_images, key=lambda x: x['version'], reverse=True)

        image_name = sorted_images[0]['image'].split('/')[-1]
        return send_from_directory(app.static_folder, f"images/{image_name}")
    else:
        return "No logo found with the specified parameters", 404

@app.route("/random/data")
def get_random_data():
    # Fetch the data from the "/all" endpoint
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Flatten the data structure
        records = data.get("records", {})
        all_items = [item for sublist in records.values() for item in sublist]

        if all_items:
            # Select a random item
            random_item = random.choice(all_items)
            return jsonify(random_item)
        else:
            return "No data available", 404

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return "Error fetching data", 500

@app.route("/<name>/data")
def get_name_data(name):
    # Fetch the data from the "/all" endpoint
    try:
        response = requests.get(f"{request.host_url}all")
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Retrieve the brand-specific data
        records = data.get("records", {})
        name_data = records.get(name.lower(), [])

        if name_data:
            return jsonify(name_data)
        else:
            return "Name not found", 404

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return "Error fetching data", 500

if __name__ == "__main__":
    app.run(debug=False)