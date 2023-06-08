from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Dummy database of brand logos with variants
logos = [
    {
        "name": "Nike",
        "variants": {
            "normal": "logos/nike.png",
            "bleeded": "logos/nike.png",
            "squared": "logos/nike.png"
        }
    },
    {
        "name": "Mailchimp",
        "variants": {
            "normal": "logos/mailchimp.png",
            "bleeded": "logos/mailchimp.png",
            "squared": "logos/mailchimp.png"
        }
    }
]

@app.route('/logo/random', methods=['GET'])
def get_random_logo():
    logo = random.choice(logos)
    variant = random.choice(list(logo["variants"].keys()))
    image = logo["variants"][variant]
    return jsonify({"name": logo["name"], "variant": variant, "image": image})

@app.route('/logo/<name>', methods=['GET'])
def get_logo_by_name(name):
    variant = request.args.get('variant')
    for logo in logos:
        if logo["name"].lower() == name.lower():
            if variant and variant in logo["variants"]:
                image = logo["variants"][variant]
                return jsonify({"name": logo["name"], "variant": variant, "image": image})
            else:
                variant = random.choice(list(logo["variants"].keys()))
                image = logo["variants"][variant]
                return jsonify({"name": logo["name"], "variant": variant, "image": image})
    return jsonify({"error": "Logo not found"})

@app.route('/logo/random/<variant>', methods=['GET'])
def get_random_logo_with_variant(variant):
    logo = random.choice(logos)
    if variant and variant in logo["variants"]:
        image = logo["variants"][variant]
        return jsonify({"name": logo["name"], "variant": variant, "image": image})
    else:
        variant = random.choice(list(logo["variants"].keys()))
        image = logo["variants"][variant]
        return jsonify({"name": logo["name"], "variant": variant, "image": image})

if __name__ == '__main__':
    app.run()