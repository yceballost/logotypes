from flask import Flask, jsonify, request, redirect, send_from_directory
from flask_cors import CORS

import os
import random

app = Flask(__name__, static_folder="../static")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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

    # Create the JSON dictionary
    data = {
        "image": image_url,
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    return data


# def generate_image_path_from_image_name(image_name):
#     return f"logos/{image_name}"

@app.route("/all")
def generate_json():
    # Get the list of files in the "img" folder
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

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
    # Get the list of files in the "img" folder
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

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
        return f"No logo found with the specified parameters", 404


@app.route("/<name>")
def get_logo_variants(name):
    # Get the list of files in the "img" folder
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

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
        return f"No logo found with the specified parameters", 404


if __name__ == "__main__":
    app.run(debug=False)
