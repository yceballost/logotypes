from flask import Flask, jsonify
import os
import json

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
    json_list = []
    for image_file in image_files:
        json_data = generate_json_from_image_name(image_file)
        json_list.append(json_data)

    # Crear el diccionario final con la estructura deseada
    data_final = {
        "records": json_list
    }

    # Convertir el diccionario final a JSON y devolverlo como respuesta
    return jsonify(data_final)

if __name__ == "__main__":
    app.run(debug=False)
