from flask import Flask, jsonify, request
from flask_cors import CORS

import os
import random

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def generate_json_from_image_name(image_name):
    # Separar el nombre de la imagen en sus componentes
    components = image_name.split('-')
    name = components[0]
    variant = components[1]
    version = components[2].split('.')[0]

    # Crear la URL absoluta de la imagen
    image_url = f"{request.host_url}static/images/{image_name}"

    # Crear el diccionario JSON
    data = {
        "image": image_url,
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    return data


def generate_image_path_from_image_name(image_name):
    return f"logos/{image_name}"


@app.route("/")
def generate_json():
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

    # Generar el JSON para cada imagen encontrada
    json_data = {}
    for image_file in image_files:
        name = image_file.split('-')[0]
        if name not in json_data:
            json_data[name] = []
        json_data[name].append(generate_json_from_image_name(image_file))

    # Crear el diccionario final con la estructura deseada
    data_final = {
        "records": json_data
    }

    # Devolver el diccionario final como respuesta JSON
    return jsonify(data_final)

@app.route("/random")
def get_random_json():
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

    # Obtener los parámetros de la URL
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filtrar los resultados según los parámetros especificados
    filtered_images = []
    for image_file in image_files:
        image_data = generate_json_from_image_name(image_file)
        if (variant_param and image_data.get("variant") != variant_param) or \
           (version_param and image_data.get("version") != version_param):
            continue
        filtered_images.append(image_data)

    if filtered_images:
        # Generar el JSON para un elemento aleatorio entre los filtrados
        random_image_data = random.choice(filtered_images)
        return jsonify(random_image_data)
    else:
        return f"No se encontró ningún logo con los parámetros especificados", 404


@app.route("/<name>")
def get_logo_variants(name):
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "static/images"
    image_files = os.listdir(folder_path)

    # Obtener los parámetros de la URL
    variant_param = request.args.get("variant")
    version_param = request.args.get("version")

    # Filtrar los resultados según el nombre y los parámetros especificados
    filtered_images = []
    for image_file in image_files:
        image_data = generate_json_from_image_name(image_file)
        if image_data.get("name").lower() == name.lower():
            if (variant_param and image_data.get("variant") != variant_param) or \
               (version_param and image_data.get("version") != version_param):
                continue
            filtered_images.append(image_data)

    if filtered_images:
        if len(filtered_images) == 1:
            return jsonify(filtered_images[0])
        else:
            return jsonify(filtered_images)
    else:
        return f"No se encontró ningún logo con los parámetros especificados", 404


if __name__ == "__main__":
    app.run(debug=False)
