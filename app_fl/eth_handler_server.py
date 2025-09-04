from web3 import Web3
from Crypto.PublicKey import RSA
from eth_account import Account
import hashlib
import json
import argparse

def load_abi():
    with open("../on-chain/build/contracts/TrainOrch.json") as f:
        contract_json = json.load(f)
        contract_abi = contract_json["abi"]
    return contract_abi

parser = argparse.ArgumentParser(description="'start' - create a session, 'continue' - go with session flow, 'trainers' - list trainers")
parser.add_argument("action", choices=["start", "continue", "trainers"], help="Action must be 'start' or 'continue'")
args = parser.parse_args()
print(f"You chose action: {args.action}")



PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d" # 0
ACCOUNT = Account.from_key(PRIVATE_KEY)
CONTRACT_ABI = load_abi()
ACCOUNT = Account.from_key(PRIVATE_KEY)


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

CONTRACT_ADDRESS = Web3.to_checksum_address("0xe78a0f7e598cc8b0bb87894b0f60dd2a88d6a8ab")
CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


def get_key_hash(user_address):
    user_address = w3.to_checksum_address(user_address)
    key_hash = CONTRACT.functions.getKeyHash(user_address).call()
    print("Key hash for user:", key_hash.hex())
    return key_hash

# TODO helper???


def test():
    

    # ABI kontraktu (skopiuj po kompilacji w Truffle/Hardhat)
    contract_abi = [
        {
            "inputs": [{"internalType": "bytes32","name":"keyHash","type":"bytes32"}],
            "name":"submitKeyHash",
            "outputs":[],
            "stateMutability":"nonpayable",
            "type":"function"
        },
        {
            "inputs":[{"internalType":"address","name":"user","type":"address"}],
            "name":"getKeyHash",
            "outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],
            "stateMutability":"view",
            "type":"function"
        }
    ]

    contract_address = Web3.to_checksum_address("0xe982e462b094850f12af94d21d470e21be9d0e9c")
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # --- Odczytanie RSA ---
    with open("./public_key.pem", "rb") as f:
        pub_key_bytes = f.read()

    # --- Hash klucza ---
    key_hash = Web3.keccak(pub_key_bytes)  # keccak256 tak jak w Solidity
    print("Key hash:", key_hash.hex())

    # --- Wysyłanie transakcji ---
    tx = contract.functions.submitKeyHash(key_hash).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 500000,
        "gasPrice": w3.eth.gas_price,
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("Transaction mined:", receipt.transactionHash.hex())


    user_address = Web3.to_checksum_address("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1")
    key_hash = contract.functions.getKeyHash(user_address).call()
    print("Key hash for user:", key_hash.hex())


def create_new_session(max_participants):
    owner_address = w3.eth.account.from_key(PRIVATE_KEY).address
    tx = CONTRACT.functions.createNewSession(max_participants).build_transaction({
        'from': owner_address,
        'nonce': w3.eth.get_transaction_count(owner_address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def start_session():
    owner_address = w3.eth.account.from_key(PRIVATE_KEY).address
    tx = CONTRACT.functions.startSession().build_transaction({
        'from': owner_address,
        'nonce': w3.eth.get_transaction_count(owner_address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

# --- Server completes the training session ---
def complete_training_session():
    owner_address = w3.eth.account.from_key(PRIVATE_KEY).address
    tx = CONTRACT.functions.completeTrainingSession().build_transaction({
        'from': owner_address,
        'nonce': w3.eth.get_transaction_count(owner_address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

# --- Server distributes rewards ---
def distribute_rewards(current_session_trainers, amounts):
    """
    trainers: list of trainer addresses to distribute rewards to
    """
    print(amounts)
    print(len(current_session_trainers))
    print(len(amounts))
    assert len(current_session_trainers) == len(amounts), "Arrays must match"
    current_trainers = [w3.to_checksum_address(addr) for addr in current_session_trainers]

    owner_address = w3.eth.account.from_key(PRIVATE_KEY).address

    tx = CONTRACT.functions.distributeRewards(current_trainers, amounts).build_transaction({
        'from': owner_address,
        'nonce': w3.eth.get_transaction_count(owner_address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def get_current_session_trainers():
    owner_address = w3.eth.account.from_key(PRIVATE_KEY).address
    current_session_id = CONTRACT.functions.currentSession().call()
    trainers = CONTRACT.functions.getTrainers(current_session_id).call({'from': owner_address})
    return trainers


def simulation_create_session():
    print("create session")
    print(create_new_session(2))

def simulation_therest():
    print("start session")
    print(start_session())
    print("complete training session")
    print(complete_training_session())
    print("distribute rewards")
    print(distribute_rewards(get_current_session_trainers(), [5000000000000000, 5000000000000000]))


def simulate_run():
    if args.action == 'start':
        simulation_create_session()
    elif args.action == 'continue':
        simulation_therest()
    elif args.action == 'trainers':
        print(get_current_session_trainers())
    else:
        pass

def main():

    
    #print(create_new_session(2))
    #print(start_session())
    #print(complete_training_session())
    #print(distribute_rewards(get_current_session_trainers(), ["5000000000000000, 5000000000000000"]))

    #print(get_current_session_trainers())
    pass
simulate_run()
#simulation_therest()