import os

import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Sequential


def create_datasets(data_dir, config, seed):
    train_ds, val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="both",
        seed=seed,
        image_size=(config["height"], config["width"]),
        batch_size=config["batch_size"],
    )

    return train_ds, val_ds


def create_model(data_dir, train_ds, val_ds, config):
    AUTOTUNE = tf.data.AUTOTUNE

    # Cache and prefetch the datasets
    train_ds = (
        train_ds.cache().shuffle(config["batch_size"]).prefetch(buffer_size=AUTOTUNE)
    )
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # define class names (work around if train_ds.class_names is undefined)
    class_names = [
        item
        for item in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, item))
    ]
    # set up data augmentation
    data_augmentation = keras.Sequential(
        [
            layers.RandomFlip(
                "horizontal", input_shape=(config["height"], config["width"], 3)
            ),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ]
    )

    # create the model
    model = Sequential(
        [
            data_augmentation,
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(16, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Dropout(0.2),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(len(class_names), name="outputs"),
        ]
    )

    # compile the model
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    return model, class_names


def train_model(model, train_ds, val_ds, epochs=10):
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)
    return history
