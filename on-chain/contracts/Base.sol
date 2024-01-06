// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

abstract contract Base {
    enum RoundPhase {
        Stopped,
        WaitingForUpdates,
        WaitingForScores,
        WaitingForAggregations,
        WaitingForTermination,
        WaitingForBackpropagation
    }

    address public owner;
    address public model;

    RoundPhase afterUpdate;

    // TODO - decide if we want to support multiple aggregators
    address[] public aggregators;
    mapping(address => bool) public registeredAggregators;
    address[] public clients;
    mapping(address => bool) public registeredClients;

    // Round details
    uint public round = 0;
    RoundPhase public roundPhase = RoundPhase.Stopped;
    mapping(uint => address[]) public selectedClients;

    // Aggregations details - TODO decide if we want to support multiple aggregators

    constructor() {
        owner = msg.sender;
    }

    function registerClient() public {
        if (registeredClients[msg.sender] == false) {
            clients.push(msg.sender);
            registeredClients[msg.sender] = true;
        }
    }

    function getClients() public view returns (address[] memory) {
        return clients;
    }
}
