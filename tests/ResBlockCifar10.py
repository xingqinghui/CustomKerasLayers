from keras.layers import Input, AveragePooling2D, Dense, Reshape
from keras.models import Model
from keras.datasets import cifar10
from keras.utils.np_utils import to_categorical
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import TensorBoard
from keras.initializers import VarianceScaling
import numpy as np
import os
from time import time

from layers import ResBlock2D


def evaluate_on_cifar10():
    total_depth = 36
    n_blocks = 3
    basic_block_count = total_depth // n_blocks

    # region Model
    input_layer = Input(shape=[32, 32, 3])
    layer = input_layer
    kernel_initializer = VarianceScaling(scale=1.0 / np.sqrt(total_depth), mode="fan_in", distribution="normal")

    for k in range(n_blocks):
        strides = 2 if k < (n_blocks - 1) else 1
        layer = ResBlock2D(filters=16 * (2 ** k), basic_block_count=basic_block_count, strides=strides,
                           kernel_initializer=kernel_initializer, use_bias=True)(layer)

        if k == (n_blocks - 1):
            layer = AveragePooling2D(pool_size=8)(layer)
        # else:
        #     layer = AveragePooling2D(pool_size=2, strides=2)(layer)

    layer = Reshape([-1])(layer)
    layer = Dense(units=10, activation="softmax")(layer)
    model = Model(inputs=input_layer, outputs=layer)
    model.summary()

    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["acc"])
    # endregion

    # region Data
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train = x_train.astype(np.float32) / 255.0
    x_test = x_test.astype(np.float32) / 255.0

    y_train = to_categorical(y_train, num_classes=10)
    y_test = to_categorical(y_test, num_classes=10)

    generator = ImageDataGenerator(rotation_range=15,
                                   width_shift_range=5. / 32,
                                   height_shift_range=5. / 32,
                                   horizontal_flip=True)
    generator.fit(x_train, seed=0)
    # endregion

    log_dir = "../logs/tests/res_block_cifar10/{}".format(int(time()))
    log_dir = os.path.normpath(log_dir)
    tensorboard = TensorBoard(log_dir=log_dir)

    model.fit_generator(generator.flow(x_train, y_train, batch_size=100),
                        steps_per_epoch=100, epochs=300, validation_data=(x_test, y_test),
                        validation_steps=100, verbose=1, callbacks=[tensorboard])


if __name__ == "__main__":
    evaluate_on_cifar10()