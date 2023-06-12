from flask import Flask, jsonify
import os
import random

app = Flask(__name__)

def generate_json_from_image_name(image_name):
    # Separar el nombre de la imagen en sus componentes
    components = image_name.split('-')
    name = components[0]
    variant = components[1]
    version = components[2].split('.')[0]

    # Crear el diccionario JSON
    data = {
        "image": f"{image_name}",
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    return data

@app.route("/")
def generate_json():
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "img"
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
    folder_path = "img"
    image_files = os.listdir(folder_path)

    # Generar el JSON para un elemento aleatorio
    random_image_file = random.choice(image_files)
    json_data = generate_json_from_image_name(random_image_file)

    # Devolver el elemento aleatorio como respuesta JSON
    return jsonify(json_data)

if __name__ == "__main__":
    app.run(debug=False)
