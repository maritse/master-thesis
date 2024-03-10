import tensorflow as tf
import numpy as np
import sys
import pickle

class MNISTHandler():
    def __init__(self):
        pass
    
    def download_mnist(self):
        self.dataset = dict()
        (self.dataset["train_images"], self.dataset["train_labels"]), (self.dataset["test_images"], self.dataset["test_labels"]) = tf.keras.datasets.mnist.load_data()

    def get_dataset_details(self):
        for one in self.dataset.keys():
            print(one, self.dataset[one].shape)

    def save_data(self, name = "/tmp/mnist.data"):
        # move it to the database?
        with open(name, "wb") as file:
            pickle.dump(self.dataset, file)

    def save_part_data(self, dataset, name):
        with open(name, "wb") as file:
            pickle.dump(dataset, file)

    def load_data(self, name = "/tmp/mnist.data"):
        with open(name, "rb") as file:
            return pickle.load(file)

    def split_dataset(self, number_of_parts):
        self.datasets_splitted = []
        split_data_length = len(self.dataset["train_images"]) // number_of_parts
        for one in range(number_of_parts):
            d = dict()
            d["train_images"] = self.dataset["train_images"][one * split_data_length: (one + 1) * split_data_length]
            d["train_labels"] = self.dataset["train_labels"][one * split_data_length: (one + 1) * split_data_length]
            d["test_images"] = self.dataset["test_images"][:]
            d["test_labels"] = self.dataset["test_labels"][:]
            self.datasets_splitted.append(d)
        return self.datasets_splitted

    def save_splitted_data(self, number_of_parts):
        splitted_data = self.split_dataset(number_of_parts)
        for n, d in enumerate(splitted_data):
            self.save_part_data(d, "/tmp/federated_data_" + str(n) + ".d")
        