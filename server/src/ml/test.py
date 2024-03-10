from model_mnist import *


new_mnist = MNISTHandler()
new_mnist.download_mnist()

print(new_mnist.dataset["train_images"])