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
        "image": f"logos/{image_name}",
        "name": name.capitalize(),
        "variant": variant,
        "version": version
    }

    return data

@app.route("/")
def generate_json():
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "src"
    image_files = os.listdir(folder_path)

    # Generar el JSON para cada imagen encontrada
    json_data = []
    for image_file in image_files:
        json_data.append(generate_json_from_image_name(image_file))

    # Devolver el JSON como respuesta
    return jsonify(records=json_data)

@app.route("/random")
def get_random_logo():
    # Obtener la lista de archivos en la carpeta "img"
    folder_path = "src"
    image_files = os.listdir(folder_path)

    # Seleccionar un logotipo aleatorio
    random_image_file = random.choice(image_files)
    random_logo = generate_json_from_image_name(random_image_file)

    # Devolver el logotipo aleatorio como respuesta JSON
    return jsonify(random_logo)

if __name__ == "__main__":
    app.run(debug=False)
