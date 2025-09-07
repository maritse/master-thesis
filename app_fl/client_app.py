import torch

from flwr.client import ClientApp, Client
from flwr.common import (
    Code,
    Config,
    Context,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    GetParametersIns,
    GetParametersRes,
    GetPropertiesRes,
    Scalar,
    Status,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)
from flwr_datasets import FederatedDataset
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from typing import Dict

from app_fl.task import Net, get_weights, load_data, set_weights, test, train, get_parameters, set_parameters
from app_fl.crypto_utils import decrypt_data_privkey_client, encrypt_data_pubkey_server

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#def deserialize_and_decrypt(parameters_enc):
#    parameters_original = decrypt_client_pub_key(str(parameters_enc))
#    ndarrays_original = parameters_to_ndarrays(parameters_original)
#    return ndarrays_original


def load_datasets(partition_id: int, num_partitions: int):
    fds = FederatedDataset(dataset="cifar10", partitioners={"train": num_partitions})
    partition = fds.load_partition(partition_id)
    # Divide data on each node: 80% train, 20% test
    partition_train_test = partition.train_test_split(test_size=0.2, seed=42)
    pytorch_transforms = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    def apply_transforms(batch):
        # Instead of passing transforms to CIFAR10(..., transform=transform)
        # we will use this function to dataset.with_transform(apply_transforms)
        # The transforms object is exactly the same
        batch["img"] = [pytorch_transforms(img) for img in batch["img"]]
        return batch

    partition_train_test = partition_train_test.with_transform(apply_transforms)
    trainloader = DataLoader(partition_train_test["train"], batch_size=32, shuffle=True)
    valloader = DataLoader(partition_train_test["test"], batch_size=32)
    testset = fds.load_split("test").with_transform(apply_transforms)
    testloader = DataLoader(testset, batch_size=32)
    return trainloader, valloader, testloader


# Define Flower Client and client_fn
class FlowerClient(Client):
    def __init__(self, partition_id, net, trainloader, valloader, local_epochs):
        self.partition_id = partition_id
        self.net = net
        self.trainloader = trainloader
        self.valloader = valloader
        self.local_epochs = local_epochs
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def get_properties(self, config: Config) -> Dict[str, Scalar]:
        props: Dict[str, Scalar] = {
            "client_id": "client1"
        }
        return GetPropertiesRes(
            status=Status(code=Code.OK, message="Success"),
            properties=props
        )

    def get_parameters(self, ins: GetParametersIns) -> GetParametersRes:
        print(f"[Client {self.partition_id}] get_parameters")

        ndarrays: List[np.ndarray] = get_parameters(self.net)
        
        parameters = ndarrays_to_parameters(ndarrays)

        status = Status(code=Code.OK, message="Success")
        return GetParametersRes(
            status=status,
            parameters=parameters,
        )

    def fit(self, ins: FitIns) -> FitRes:
        ndarrays_original = decrypt_data_privkey_client(ins.parameters)
        #ndarrays_original = parameters_to_ndarrays(parameters_original)

        # Update local model, train, get updated parameters
        set_parameters(self.net, ndarrays_original)
        epochs_num = 1
        train(self.net, self.trainloader, epochs_num, self.device)
        ndarrays_updated = get_parameters(self.net)

        # Serialize ndarray's into a Parameters object
        #parameters_updated = ndarrays_to_parameters(ndarrays_updated)
        parameters_updated = encrypt_data_pubkey_server(ndarrays_updated)

        # Build and return response
        status = Status(code=Code.OK, message="Success")
        return FitRes(
            status=status,
            parameters=parameters_updated,
            num_examples=len(self.trainloader),
            metrics={},
        )

    def evaluate(self, ins: EvaluateIns) -> EvaluateRes:
        print(f"[Client {self.partition_id}] evaluate, config: {ins.config}")

        # Deserialize parameters to NumPy ndarray's
        #parameters_original = ins.parameters
        ndarrays_original = decrypt_data_privkey_client(ins.parameters)
        #ndarrays_original = parameters_to_ndarrays(parameters_original)
        set_parameters(self.net, ndarrays_original)
        loss, accuracy = test(self.net, self.valloader, self.device)
        print("loss: " + str(loss))
        print("accuracy: " + str(accuracy))

        # Build and return response
        status = Status(code=Code.OK, message="Success")
        return EvaluateRes(
            status=status,
            loss=float(loss),
            num_examples=len(self.valloader),
            metrics={"accuracy": float(accuracy)},
        )

def client_fn(context: Context) -> Client:
    net = Net().to(DEVICE)
    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config["num-partitions"]
    trainloader, valloader, _ = load_datasets(partition_id, num_partitions)
    return FlowerClient(partition_id, net, trainloader, valloader, 3).to_client()


# Create the ClientApp
app = ClientApp(client_fn=client_fn)