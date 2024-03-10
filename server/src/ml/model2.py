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


class SimpleMLP:
    def __init__(self, id, defaut_path = "/tmp/federated/", number_of_rounds=10):
        self.defaut_path = defaut_path
        self.id = id
        self.number_of_rounds = number_of_rounds

    def build(self, shape, classes):
        model = Sequential()
        model.add(Dense(200, input_shape=(shape,)))
        model.add(Activation("relu"))
        model.add(Dense(200))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        
        model.compile(
            loss = "caterogical_crossentropy",
            optimizer = SGD(
                learning_rate = 0.01,
                weight_decay = 0.01 / self.number_of_rounds,
                momentum = 0.9
            ),
            metrics = ['accuracy']
        )

        self.model = model
        self.global_initial_weights = self.get_model_weights()

    def get_model_weights(self):
        return self.model.weights
    
    def set_global_weights(self, average_weights):
        self.model.set_weights(average_weights)

    def save_current_model_state_keras_form(self):
        self.model.save(self.defaut_path + str(self.id))
    
    def save_current_model_state_tfjs_form(self):
        tfjs.converters.save_keras_model(self.model, self.defaut_path + str(self.id))

    def load_current_model_state(self):
        self.model = keras.saving.load_model(self.default_path + str(self.id))

    def calculate_average_weights(self, weights):
        pass

    def test_global_model(self):
        pass


new_model = SimpleMLP(id = 123, number_of_rounds = 10)
new_model.build(784, 10)
new_model.save_current_model_state_tfjs_form()