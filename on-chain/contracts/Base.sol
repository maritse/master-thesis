// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

abstract contract Base {

    enum RoundPhase {
        BeforeStart,
        WaitingForClientsRegistration,
        Training,
        WaitingForScores,
        WaitingForTermination,
        Termination
    }
    
    struct ModelDetails {
        uint ID;
        RoundPhase status;
        address[] enteredClients;
        uint maxNumberOfClients;
        uint numberOfRounds;
        uint currentRoundNumber;
    }

    // Events
    event registerClient();

    ModelDetails[] modelsList;
    ModelDetails[] modelsListReadyToRegister;

    modifier onlyOwner() {
    require(
        msg.sender == owner,
        "This function is restricted to the contracts owner"
        );
        _;
    }

    address public owner;

    address[] public aggregators;
    mapping(address => bool) public registeredAggregators;

    address[] public clients;
    mapping(address => bool) public registeredClients;

    constructor() {
        owner = msg.sender;
        aggregators.push(msg.sender);
    }

    function registerClient() public {
        if (registeredClients[msg.sender] == false) {
            clients.push(msg.sender);
            registeredClients[msg.sender] = true;
            emit registerClient();
        }
    }

    function registerClientToModel(uint ID) public {
        // TODO
    }

    function getClients() onlyOwner public view returns (address[] memory) {
        return clients;
    }

    function getClientsByProject(uint ID) onlyOwner public view returns (address[] memory) {
        // TODO
    }

    function getAggregator() public view returns (address[] memory) {
        return aggregators;
    }

    function registerNewModel(uint ID, uint _roundsNumber, uint _maxNumberOfClients) onlyOwner public {
        address[] memory _x;
        modelsList.push(ModelDetails({
            ID: ID,
            status: RoundPhase.BeforeStart,
            enteredClients: _x,
            numberOfRounds: _roundsNumber,
            maxNumberOfClients: _maxNumberOfClients,
            currentRoundNumber: 0
        }));
    }
    function deleteModel(uint ID) onlyOwner public {
        // TODO
    }

    function activateClientRegistrationModel(uint ID) onlyOwner public {
        // TODO - czy potrzebne?
    }
}
