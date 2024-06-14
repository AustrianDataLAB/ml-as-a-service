import os
import json
import shutil
import sys
import zipfile
import imghdr
import requests
import logging

from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from model import create_datasets, create_model, train_model

# Define the required environment variables
REQUIRED_ENV_VARS = ["PERSISTENCE_SERVICE_URI", "TENANT"]
OPTINAL_ENV_VARS = ["IMG_HEIGHT", "IMG_WIDTH", "BATCH_SIZE", "EPOCHS"]

# Define global variables
seed = 42

# ---------------------------------------------------------------------
# -----------------------------functions-------------------------------
# ---------------------------------------------------------------------


def clean_data(data_dir):
    image_extensions = [".png", ".jpg"]
    img_type_accepted_by_tf = ["bmp", "gif", "jpeg", "png"]

    cnt_removed = 0
    for filepath in Path(data_dir).rglob("*"):
        # MACOS specific requierements
        if filepath.is_dir() and "__MACOSX" in filepath.name:
            logging.info(f"Found and removed __MACOSX artefact")
            shutil.rmtree(filepath)
            continue

        if ".DS_Store" in filepath.name:
            logging.info(f"Found and removed .DS_Store artefact")
            os.remove(filepath)
            continue

        if filepath.suffix.lower() in image_extensions:
            img_type = imghdr.what(filepath)
            if img_type is None or img_type not in img_type_accepted_by_tf:
                os.remove(filepath)
                cnt_removed += 1

    logging.info(f"Found and removed {cnt_removed} invalid files")


def fetch_data(persistence_url, tenant, extract_path):
    try:
        response = requests.get(
            f"{persistence_url}/data", headers={"Authorization": tenant}, stream=True
        )
        print(response.status_code, persistence_url, tenant)
        if response.status_code == 200:
            # Use BytesIO for in-memory bytes buffer to store the zip content
            zip_file_bytes = BytesIO(response.content)

            # Extract the zip file contents
            with zipfile.ZipFile(zip_file_bytes, "r") as zip_ref:
                zip_ref.extractall(extract_path)

            # Load the TensorFlow model
            clean_data(extract_path)
        else:
            logging.error(
                f"Unexpected response from persictence service: {str(response.status_code)}"
            )
            sys.exit(f"Unexpected response from persictence service")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        sys.exit(f"Unexpected error occurred when loading model")


def transmit_data(persistence_url, tenant, config, model_path):
    try: 
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add model file to zip
            zip_file.write(model_path, arcname=os.path.basename(model_path))

            # Serialize config dictionary to JSON and write directly to the zip
            with zip_file.open("config.json", "w") as config_file:
                config_file.write(json.dumps(config).encode("utf-8"))

        # Prepare the buffer to be used as a file-like object for the HTTP request
        zip_buffer.seek(0)

        # Set the name of the zip file you are sending
        zip_filename = "model_and_config.zip"

        # Prepare the files dictionary to send via requests
        files = {"file": (zip_filename, zip_buffer, "application/zip")}

        response = requests.post(f"{persistence_url}/model", headers={"Authorization": tenant}, files=files,)

        if response.status_code == 200:
            logging.info("File transmitted successfully")
        else:
            logging.error("Failed to transmit file")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        sys.exit(f"Unexpected error occurred when loading model")


def setup():
    # Check if all required environment variables are set
    for var in REQUIRED_ENV_VARS:
        if var not in os.environ:
            logging.error(f"Error: Environment variable {var} is not set")
            sys.exit(f"Error: Environment variable {var} is not set")

    persistence_service_uri = os.getenv("PERSISTENCE_SERVICE_URI")
    tenant = os.getenv("TENANT")

    # default config
    config = {
        "height": 180,
        "width": 180,
        "batch_size": 128,
        "epochs": 10,
    }

    for var in REQUIRED_ENV_VARS:
        if var in os.environ:
            logging.info(f"Environment variable {var} is set")
            if var == "IMG_HEIGHT":
                config["height"] = os.getenv(int(var))
            elif var == "IMG_WIDTH":
                config["width"] = os.getenv(int(var))
            elif var == "BATCH_SIZE":
                config["batch_size"] = os.getenv(int(var))
            elif var == "EPOCHS":
                config["epochs"] = os.getenv(int(var))

    return persistence_service_uri, tenant, config


# ---------------------------------------------------------------------
# -------------------------Training-Service----------------------------
# ---------------------------------------------------------------------


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    # Load environment variables
    load_dotenv()

    # define variables
    persistence_service_uri, tenant, config = setup()
    data_dir = os.path.abspath("./data")

    # fetch data
    fetch_data(persistence_service_uri, tenant, data_dir)

    # train model
    train_ds, val_ds = create_datasets(data_dir, config, seed)
    model, class_names = create_model(data_dir, train_ds, val_ds, config)
    _ = train_model(model, train_ds, val_ds, config["epochs"])
    model.save("./my_model.keras")

    config["class_names"] = class_names

    # transmit model
    transmit_data(persistence_service_uri, tenant, config, "./my_model.keras")


if __name__ == "__main__":
    main()