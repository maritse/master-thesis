from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Use first Ganache account
account = w3.eth.accounts[0]
print(account)

# Contract ABI and address (from Truffle migration)
contract_abi = [
    {
        "inputs": [{"internalType": "uint256","name":"_value","type":"uint256"}],
        "name":"setValue",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    },
    {
        "inputs": [],
        "name":"getValue",
        "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
        "stateMutability":"view",
        "type":"function"
    }
]
contract_address = "0xe78a0f7e598cc8b0bb87894b0f60dd2a88d6a8ab"
checksum_address = Web3.to_checksum_address(contract_address)


# Instantiate contract
contract = w3.eth.contract(address=checksum_address, abi=contract_abi)

# Set a value
tx_hash = contract.functions.setValue(999).transact({'from': account})
w3.eth.wait_for_transaction_receipt(tx_hash)

# Read the value
value = contract.functions.getValue().call()
print("Stored value:", value)
