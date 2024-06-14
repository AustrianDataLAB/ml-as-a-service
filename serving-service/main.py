from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import zipfile
import os
import sys
import io
import json
import logging
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename

# Create a Flask app
app = Flask(__name__)

persistence_service_uri = None
auth_header = None
model = None
config = None

# ---------------------------------------------------------------------
# -----------------------------functions-------------------------------
# ---------------------------------------------------------------------


def setup():
    # Define the required environment variables
    REQUIRED_ENV_VARS = ["PERSISTENCE_SERVICE_URI", "TENANT"]

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    # Check if all required environment variables are set
    for var in REQUIRED_ENV_VARS:
        if var not in os.environ:
            logging.error(f"Error: Environment variable {var} is not set")
            sys.exit(f"Error: Environment variable {var} is not set")

    # Set Persistence Service URL
    global persistence_service_uri
    persistence_service_uri = os.getenv("PERSISTENCE_SERVICE_URI")

    # Set auth header
    global auth_header
    auth_header = os.getenv("TENANT")


def load_model():
    try:
        headers = {"Authorization": auth_header}
        response = requests.get(persistence_service_uri, headers=headers, stream=True)
        if response.status_code == 200:
            # Use BytesIO for in-memory bytes buffer to store the zip content
            zip_file_bytes = io.BytesIO(response.content)

            # Extract the zip file contents
            with zipfile.ZipFile(zip_file_bytes, "r") as zip_ref:
                # Optionally specify a path where to extract
                extract_path = "./model"
                zip_ref.extractall(extract_path)

            # Load the TensorFlow model
            global model
            model_directory = os.path.join(extract_path, "my_model.keras")
            model = tf.keras.models.load_model(model_directory)

            # Load the configuration JSON
            config_path = os.path.join(extract_path, "config.json")
            with open(config_path, "r") as json_file:
                global config
                config = json.load(json_file)
        else:
            logging.error(
                f"Unexpected response from persictence service: {str(response.status_code)}"
            )
            sys.exit(f"Unexpected response from persictence service")

    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        sys.exit(f"Unexpected error occurred when loading model")


def _inference(image):
    try:
        predictions = model.predict(image)
        score = tf.nn.softmax(predictions[0])
        return (
            "This image most likely belongs to {} with a {:.2f} percent confidence.".format(
                config["class_names"][np.argmax(score)], 100 * np.max(score)
            )
        ), 200
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def _parse_and_infer(request):
    if "file" not in request.files:
        logging.error("No file part in infer request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logging.error("Infer request has empty file")
        return jsonify({"error": "Infer request has empty file"}), 400

    try:
        # Save file
        filename = secure_filename(file.filename)
        save_path = os.path.join("uploads", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        # Load and preprocess image
        image = tf.keras.preprocessing.image.load_img(
            save_path, target_size=(config["img_height"], config["img_width"])
        )
        img_array = tf.keras.utils.img_to_array(image)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        # Remove file
        if os.path.exists(save_path):
            os.remove(save_path)

        return _inference(img_array)
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({"error": "Error processing image"}), 500


# ---------------------------------------------------------------------
# ---------------------------------API---------------------------------
# ---------------------------------------------------------------------


@app.route("/infer", methods=["POST"])
def inference():
    return _parse_and_infer(request)


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello, World!"


def create_app(config):
    setup()
    load_model()
    app.config.from_object(config)
    return app


if __name__ == "__main__":
    setup()
    load_model()
    app.run(host="0.0.0.0", port=5001, debug=True)
