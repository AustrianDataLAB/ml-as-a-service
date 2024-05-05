import os
import imghdr
import requests
import tarfile
import numpy as np
import tensorflow as tf

from argparse import ArgumentParser
from pathlib import Path

from tensorflow import keras
from keras import layers
from keras.models import Sequential


seed = 42
np.random.seed(seed)

data_dir = os.path.abspath("./data")

def clean_data():
    image_extensions = [".png", ".jpg"]
    img_type_accepted_by_tf = ["bmp", "gif", "jpeg", "png"]
    
    cnt_removed = 0
    for filepath in Path(data_dir).rglob("*"):
        if filepath.suffix.lower() in image_extensions:
            img_type = imghdr.what(filepath)
            if img_type is None or img_type not in img_type_accepted_by_tf:
                os.remove(filepath)
                cnt += 1
    print(f"Found and removed {cnt_removed} invalid files")
    
def fetch_data(persistence_url):
    # Download the tar file
    response = requests.get(persistence_url)
    tar_filename = "data.tgz"
    
    with open(tar_filename, "wb") as file:
        file.write(response.content)
    
    # Extract the contents of the tar file
    with tarfile.open(tar_filename, "r:gz") as tar:
        tar.extractall(data_dir)
    
    # Clean the extracted data
    clean_data()
    
    # Remove the tar file
    os.remove(tar_filename)

def transmit_data(persistence_url, model_path):
    with open(model_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(persistence_url, files=files)

    if response.status_code == 200:
        print("File transmitted successfully.")
    else:
        print("Failed to transmit file.")

def create_datasets(img_height, img_width, batch_size):
    train_ds, val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="both",
        seed=seed,
        image_size=(img_height, img_width),
        batch_size=batch_size,
    )
    
    return train_ds, val_ds

def create_model(train_ds, val_ds, img_height, img_width):
    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ])

    # work around if train_ds.class_names is undefined
    class_names = [item for item in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, item))]    
    num_classes = len(class_names)

    model = Sequential([
        # data_augmentation,
        layers.Rescaling(1./255),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, name="outputs")
    ])

    model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

    return model

def train_model(model, train_ds, val_ds, epochs = 10):
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    return history

if __name__ == "__main__":
    parser = ArgumentParser(description="ImageClassifaction")
    parser.add_argument("--img_height", type=int, default=180, help="Height of the images")
    parser.add_argument("--img_width", type=int, default=180, help="Width of the images")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--persistence_url", type=str, default="/no-url" , help="Url to persistence service")
    args = parser.parse_args()

    # fetch data
    fetch_data(args.persistence_url)

    # train model
    train_ds, val_ds = create_datasets(args.img_height, args.img_width, args.batch_size)
    model = create_model(train_ds, val_ds, args.img_height, args.img_width)
    history = train_model(model, train_ds, val_ds, args.epochs)
    model.save_weights('./model.weights.h5')

    # transmit model
    transmit_data(args.persistence_url, './model.weights.h5')

