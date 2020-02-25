#!/usr/local/bin/python
import argparse
from os.path import join

import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Dense, Dropout, Flatten, Input
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing import image as KerasImage


parser = argparse.ArgumentParser(description='Image classifier for EA NHL 20')
parser.add_argument('method', action='store', choices=['train', 'predict'])
parser.add_argument('path', action='store')
parser.add_argument('--model', action='store', default='nhl20_image_model.h5')


classes = (
    'game',
    'goal',
    'results',
    'share_end',
    'team_select',
)
class_by_index = {i: c for i, c in enumerate(classes)}

_model_cache = None


def data_gen_for_path(path):
    return KerasImage.ImageDataGenerator().flow_from_directory(
        path,
        target_size=(224, 224),
        classes=classes,
        batch_size=32
    )


def train(path, model_path):
    train_batches = data_gen_for_path(join(path, 'train'))
    valid_batches = data_gen_for_path(join(path, 'val'))
    test_batches = data_gen_for_path(join(path, 'test'))

    vgg16_model = VGG16(
        weights='imagenet',
        include_top=False,
        input_tensor=Input(shape=(224, 224, 3)),
    )

    for layer in vgg16_model.layers[:-4]:
        layer.trainable = False

    # Create the model
    model = Sequential()

    # Add the vgg convolutional base model
    model.add(vgg16_model)

    # Add new layers
    model.add(Flatten())
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(classes), activation='softmax'))

    # Show a summary of the model. Check the number of trainable parameters
    model.summary()

    model.compile(
        loss='categorical_crossentropy',
        optimizer=RMSprop(lr=1e-4),
        metrics=['acc']
    )
    model.fit(
        train_batches,
        steps_per_epoch=train_batches.samples / train_batches.batch_size,
        epochs=5,
        validation_data=valid_batches,
        validation_steps=valid_batches.samples / valid_batches.batch_size,
        verbose=1,
    )

    model.save(model_path)
    test_imgs, test_labels = next(test_batches)
    predictions = model.predict(test_imgs)

    def to_label(value):
        return class_by_index.get(value, 'unknown')

    test_imgs, test_labels = next(test_batches)
    predictions = model.predict(test_imgs)
    print(predictions)


def load_image(img_path):
    return KerasImage.load_img(img_path, target_size=(224, 224))


def _load_model(model_path):
    global _model_cache
    if _model_cache is None:
        print('First load model!')
        _model_cache = load_model(model_path)
    return _model_cache


def predict(image, model_path='nhl20_image_model.h5'):
    if isinstance(image, str):
        image = load_image(image)

    img_tensor = KerasImage.img_to_array(image)  # (height, width, channels)
    # model expects this shape: (batch_size, height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    model = _load_model(model_path)
    prediction = model.predict(img_tensor)[0]
    max_value = np.max(prediction)
    max_index = np.argmax(prediction)
    predicted_class = classes[max_index]
    return predicted_class, max_value


if __name__ == '__main__':
    args = parser.parse_args()
    if args.method == 'predict':
        out = predict(args.path, args.model)
        print(out)
    elif args.method == 'train':
        out = train(args.path, args.model)
