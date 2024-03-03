// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract TrainingProcess is Base {
    mapping(uint => uint) public trainers;

    constructor() {
    }

    function startRound(address[] trainersForRound) onlyOwner public {
        // TODO
    }


}