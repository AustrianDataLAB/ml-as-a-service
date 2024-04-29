import os
import numpy as np
import tensorflow as tf

from tensorflow import keras
from keras import layers
from keras.models import Sequential

seed = 42
np.random.seed(seed)

data_dir = "data"

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
    batch_size = 128
    img_height = 180
    img_width = 180

    # data_dir = load_data()
    train_ds, val_ds = create_datasets(img_height, img_width, batch_size)
    model = create_model(train_ds, val_ds, img_height, img_width)
    history = train_model(model, train_ds, val_ds)
    model.save_weights('./model.weights.keras')

