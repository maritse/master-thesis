import tensorflow as tf
import numpy as np
import sys

class MNISTHandler():
    def __init__(self):
        pass
    
    def download_mnist(self):
        try:
            from tensorflow.examples.tutorials.mnist import input_data
        except:
            print("Failed import the tensorflow.examples.tutorials.mnist library")
            sys.exit(0)

        mnist = input_data.read_data_sets("/tmp/feddata")
        
        self.dataset = dict()

        self.dataset["train_images"] = mnist.train.images
        self.dataset["train_labels"] = mnist.train.labels
        self.dataset["test_images"] = mnist.test.images
        self.dataset["test_labels"] = mnist.test.labels

    def get_dataset_details(self):
        for one in self.dataset.keys():
            print(one, dataset[one].shape)