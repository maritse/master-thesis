### opis
1. uv jako izolacja zalezności
2. wykorzystanie framework Flower AI jako core implementacji, z właśną implementacją dodatkowych scenariuszy


### SuperLink
run superlink server:
```
flower-superlink --insecure
```
Load the server:
```
flwr run . local-deployment --stream
```

### SuperNode
command 1:
```
flower-supernode \
     --insecure \
     --superlink 127.0.0.1:9092 \
     --clientappio-api-address 127.0.0.1:9094 \
     --node-config "partition-id=0 num-partitions=2"
```
command 2:
```
flower-supernode \
     --insecure \
     --superlink 127.0.0.1:9092 \
     --clientappio-api-address 127.0.0.1:9095 \
     --node-config "partition-id=1 num-partitions=2"
```



### truffle cheat sheet
```
const instance = await TrainOrch.deployed();

const sessionId = await instance.currentSession();
sessionId.toString()
instance.sessions(0)
instance.getTrainers(sessionId);

let accounts = await web3.eth.getAccounts()
web3.eth.getBalance(accounts[0])
```


flow Solidity:
```
Server - createNewSession
Client - regusterForTraining
Client - Funder - fundSessionRewards
Server - startSession
off-chain - learning process
Server - completeTrainingSession
Server - distributeRewwards
Server - createNewSession
```

flow client - register:
```
publish key hash
register for a training
train
wait for reward
```

flow client - funder
```
publish key hash
fund a model
wait for training results
```
