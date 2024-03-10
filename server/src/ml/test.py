from model_mnist import *
from model import NNWorker, reset


new_mnist = MNISTHandler()
new_mnist.download_mnist()
new_mnist.get_dataset_details()
new_mnist.save_splitted_data(10)

reset()


with open("/tmp/federated_data_0.d", "rb") as f:
    new_mnist.dataset = pickle.load(f)
worker = NNWorker(
    new_mnist.dataset["train_images"],
    new_mnist.dataset["train_labels"],
    new_mnist.dataset["test_images"],
    new_mnist.dataset["test_labels"],
    0,
    "base0")
worker.build_base()
model = dict()
model['model'] = worker.get_model()
model['accuracy'] = worker.evaluate()
worker.close()