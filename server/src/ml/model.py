import numpy as np
import random
import cv2
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend as K
import tensorflowjs as tfjs

from model_mnist import MNISTHandler


class SimpleMLP:
    def __init__(self, id, default_path = "/tmp/federated/", number_of_rounds=10):
        self.default_path = default_path
        self.id = id
        self.number_of_rounds = number_of_rounds

        self.loss_function = "categorical_crossentropy"
        self.learning_rate = 0.01
        self.weight_decay = 0.01 / number_of_rounds
        self.momentum = 0.09
        self.metrics = ['accuracy']
        self.optimizer = SGD(
            learning_rate = self.learning_rate,
            weight_decay = self.weight_decay,
            momentum = self.momentum
        )

    def build(self, shape, classes):
        model = Sequential()
        model.add(Dense(200, input_shape=(shape,)))
        model.add(Activation("relu"))
        model.add(Dense(200))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        
        # czy to dawać? czy dopiero po 1 rundzie

        model.compile(
            loss = self.loss_function,
            optimizer = self.optimizer,
            metrics = self.metrics
        )

        self.model = model
        self.global_initial_weights = self.get_model_weights()

    def get_model_weights(self):
        return self.model.weights
    
    def set_global_weights(self, average_weights):
        self.model.set_weights(average_weights)

    def save_current_model_state_keras_form(self):
        self.model.save(self.default_path + str(self.id))
        return self.default_path + str(self.id)
    
    def save_current_model_state_tfjs_form(self):
        tfjs.converters.save_keras_model(self.model, self.default_path + str(self.id))
        return self.default_path + str(self.id)

    def load_current_model_state(self):
        self.model = keras.saving.load_model(self.default_path + str(self.id))

    def calculate_average_weights(self, weights):
        pass

    def test_global_model(self):
        pass

def func_test():
    new_model = SimpleMLP(id = 124, number_of_rounds = 10)

    new_data = MNISTHandler()
    new_data.download_mnist()
    new_data.prepare_data_for_training()

    new_model.build(784, 10)
    #print(new_model.get_model_weights())
    new_model.model.fit(
        new_data.dataset_flattened["train_images"],
        new_data.dataset_flattened["train_labels"]
    )
    print(new_model.get_model_weights())

func_test()