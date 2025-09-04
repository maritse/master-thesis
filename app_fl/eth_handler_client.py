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

parser = argparse.ArgumentParser(description="Choose client ID (1 or 2)")
parser.add_argument("ID", type=int, choices=[0, 1, 2], help="Session ID (must be 1 or 2)")
args = parser.parse_args()
print(f"You passed ID = {args.ID}")


# ID = 0 - funder
# ID = 1 - 1 client
# ID = 2 - 2 client
if args.ID == 0:
    PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
elif args.ID == 1:
    PRIVATE_KEY = "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"
else:
    PRIVATE_KEY = "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c"

ACCOUNT = Account.from_key(PRIVATE_KEY)

"""
# server and (for testing) funder
#PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
# client 1
PRIVATE_KEY = "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"
# client 2
#PRIVATE_KEY = "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c"
ACCOUNT = Account.from_key(PRIVATE_KEY)
"""

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
CONTRACT_ABI = load_abi()
CONTRACT_ADDRESS = w3.to_checksum_address("0xe78a0f7e598cc8b0bb87894b0f60dd2a88d6a8ab")
CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


def register_for_training():
    client_address = w3.eth.account.from_key(PRIVATE_KEY).address
    tx = CONTRACT.functions.registerForTraining().build_transaction({
        'from': client_address,
        'nonce': w3.eth.get_transaction_count(client_address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def fund_session_rewards(amount_wei):
    funder_address = w3.eth.account.from_key(PRIVATE_KEY).address
    tx = CONTRACT.functions.fundSessionRewards().build_transaction({
        'from': funder_address,
        'value': amount_wei,
        'nonce': w3.eth.get_transaction_count(funder_address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def print_my_balance():
    try:
        account_address = ACCOUNT.address
        # get_balance
        balance_wei = w3.eth.get_balance(account_address)
        print(f"Balance for {account_address}: {balance_wei} wei")
        # Konwertowanie do ETH
        balance_eth = w3.from_wei(balance_wei, "ether")
        print(f"Balance in ETH: {balance_eth}")
    except Exception as e:
        print("Error reading balance:", e)


def simulation_run_client_registration():
    print(register_for_training())

def simulation_run_client_funding():
    # server and (for testing) funder
    print(fund_session_rewards(10000000000000000))

def simulation_run():
    if args.ID == 0:
        print("client funding")
        simulation_run_client_funding()
    elif args.ID == 1:
        print("client 1 registration")
        simulation_run_client_registration()
    else:
        print("client 2 registration")
        simulation_run_client_registration()
    print("done")
    

def main():
    pass


    #print(fund_session_rewards(10000000000000000))
    #print(register_for_training())
#main()
simulation_run()