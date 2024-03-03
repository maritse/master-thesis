// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;


abstract contract Base {
    
    // fazy rundy
    enum RoundPhase {
        Stopped,
        WaitingForUpdates,
        WaitingForScores,
        WaitingForTermination,
        WaitingForBackpropagation
    }
    // fazy rundy draft
    /*
    enum RoundPhase {
        BeforeStart,
        WaitingForClientsRegistration.
        WaitingForScores,
        WaitingForTermination,
        TODO
    }
    */

    modifier onlyOwner() {
    require(
        msg.sender == owner,
        "This function is restricted to the contract's owner"
        );
        _;
    }

    address public owner;
    address public model;

    RoundPhase BeforeStart;

    // TODO - decide if we want to support multiple aggregators
    // for now, the only aggregators is the owner of the contract
    address[] public aggregators;
    mapping(address => bool) public registeredAggregators;

    // clients
    address[] public clients;
    mapping(address => bool) public registeredClients;

    // Round details
    uint public round = 0;
    RoundPhase public roundPhase = RoundPhase.Stopped;
    mapping(uint => address[]) public selectedClients;

    // Aggregations details - TODO decide if we want to support multiple aggregators

    constructor() {
        owner = msg.sender;
        aggregators.push(msg.sender);
    }

    function registerClient() public {
        if (registeredClients[msg.sender] == false) {
            clients.push(msg.sender);
            registeredClients[msg.sender] = true;
        }
    }

    function getClients() onlyOwner public view returns (address[] memory) {
        return clients;
    }

    // TODO if needed - aggregator leak
    function returnAggregator() public view returns (address[] memory) {
        return aggregators;
    }

    function setNewModel() onlyOwner public {

    }
}
