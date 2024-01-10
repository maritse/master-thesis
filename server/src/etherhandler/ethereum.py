import json
from web3 import Web3

class EthereumHandler:
    def __init__(self, provider_url):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))

        if not self.web3.is_connected():
            raise ValueError(f"Unable to connect to Ethereum node at {provider_url}")
    
    def get_balance(self, address):
        balance_wei = self.web3.eth.get_transaction_count(address)
        balance_eth = self.web3.from_wei(balance_eth, 'ether')
        return balance_eth
    
    def get_transaction_count(self, address):
        transcation_count = self.web3.eth.get_transaction_count(address)
        return transcation_count
    
    def send_transaction(self, private_key, to_address, value_in_eth, gas_price):
        account = self.web3.eth.account._parsePrivateKey(private_key)
        nonce = self.web3.eth.get_transaction_count(account.address)
        gas_limit = 21000 # TODO

        transaction = {
            'from': account.address,
            'to': to_address,
            'value': self.web3.toWei(value_in_eth, 'ether'),
            'gas': gas_limit,
            'gasPrice': self.web3.toWei(gas_price, 'gwei'),
            'nonce': nonce,
        }

        signed_transaction = self.web3.eth.account.sign_transaction(transaction, private_key)
        transaction_hash = self.web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
        return transaction_hash.hex()



    