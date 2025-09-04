from flwr.common import (
    Context, 
    ndarrays_to_parameters,
    parameters_to_ndarrays,
    FitIns,
    GetPropertiesIns,
    EvaluateIns,
    EvaluateRes
)
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg
from app_fl.task import Net, get_weights
from typing import Dict

from app_fl.crypto_utils import encrypt_data_pubkey_client, decrypt_data_privkey_server


class CustomFedAvg(FedAvg):
    def __init__(self, custom_number_of_rounds, **kwargs):
        self.custom_number_of_rounds = custom_number_of_rounds
        super().__init__(**kwargs)

    def configure_fit(self, server_round, parameters, client_manager):
        fit_ins_list = []
        ins = GetPropertiesIns({})

        config = {"learning_rate": 0.01, "batch_size": 32}
        
        for client in client_manager.all().values():
            prop = client.get_properties(ins, timeout=30, group_id="default")
            client_id = prop.properties["client_id"]
            print(client_id)

            parameters_enc = encrypt_data_pubkey_client(parameters, client_id)
            
            fit_ins_list.append((client, FitIns(parameters_enc, config)))

        return fit_ins_list

    def configure_evaluate(self, server_round, client_manager, parameters):
        eval_ins_list = []
        ins = GetPropertiesIns({})
        config = {}  # or any evaluation config
        for client in client_manager.all().values():
            prop = client.get_properties(ins, timeout=30, group_id="default")
            client_id = prop.properties["client_id"]

            parameters_enc = encrypt_data_pubkey_client(parameters, client_id)
            
            eval_ins_list.append((client, EvaluateIns(parameters_enc, config)))
        
        return eval_ins_list

    def aggregate_fit(self, server_round, results, failures):
        decrypted_results = []
        for client_proxy, fit_res in results:
            ndarrays = decrypt_data_privkey_server(fit_res.parameters)
            #parameters = ndarrays_to_parameters(ndarrays)
            #decrypted_results.append((parameters, fit_res.num_examples))
            fit_res.parameters = ndarrays_to_parameters(ndarrays)  # patch in place
            decrypted_results.append((client_proxy, fit_res))  # keep original tuple structure
        return super().aggregate_fit(server_round, decrypted_results, failures)

    def aggregate_evaluate(self, server_round, results, failures):
        # TODO encryption - decryptio - like fit evaluate???
        aggregated_loss = super().aggregate_evaluate(server_round, results, failures)
        ins = GetPropertiesIns({})
        if server_round == self.custom_number_of_rounds:
            for client_proxy, evaluate_res in results:
                prop = client_proxy.get_properties(ins, timeout=30, group_id="default")
                client_id = prop.properties["client_id"]
                loss = evaluate_res.loss
                print("client-id: {} - loss: {}".format(client_id, loss))
        return super().aggregate_evaluate(server_round, results, failures)


def server_fn(context: Context):
    # Read from config
    num_rounds = context.run_config["num-server-rounds"]
    fraction_fit = context.run_config["fraction-fit"]

    # Initialize model parameters
    ndarrays = get_weights(Net())
    parameters = ndarrays_to_parameters(ndarrays)

    # Define strategy
    strategy = CustomFedAvg(
        custom_number_of_rounds=num_rounds,
        fraction_fit=fraction_fit,
        fraction_evaluate=1.0,
        min_available_clients=2,
        initial_parameters=parameters,
    )
    """
    strategy = FedAvg(
        fraction_fit=fraction_fit,
        fraction_evaluate=1.0,
        min_available_clients=2,
        initial_parameters=parameters,
    )
    """
    
    config = ServerConfig(num_rounds=num_rounds)
    return ServerAppComponents(strategy=strategy, config=config)


# Create ServerApp
app = ServerApp(server_fn=server_fn)
