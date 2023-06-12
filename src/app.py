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
    image_url = f"{request.base_url.rsplit('/', 1)[0]}/{image_name}"

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
    folder_path = "public/images"
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
    folder_path = "public/images"
    image_files = os.listdir(folder_path)

    # Generar el JSON para un elemento aleatorio
    random_image_file = random.choice(image_files)
    json_data = generate_json_from_image_name(random_image_file)

    # Devolver el elemento aleatorio como respuesta JSON
    return jsonify(json_data)

@app.route("/<name>")
def get_logo_variants(name):
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "public/images"
    image_files = os.listdir(folder_path)

    # Filtrar los resultados según el nombre del logo
    variants = []
    for image_file in image_files:
        logo_name = image_file.split('-')[0]
        if logo_name.lower() == name.lower():
            variant = generate_json_from_image_name(image_file)
            variants.append(variant)

    if variants:
        if len(variants) == 1:
            return jsonify(variants[0])
        else:
            return jsonify(variants)
    else:
        return f"No se encontró ningún logo con el nombre '{name}'", 404



if __name__ == "__main__":
    app.run(debug=False)
