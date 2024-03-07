// // SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

contract Communication {
    event BCEvenet(
        uint256 timestamp,
        bool is_encrypted,
        bytes event_type,
        bytes body
    );

    function publish(
        uint256 timestamp,
        bool is_encrypted,
        bytes memory event_type,
        bytes memory body
    ) public returns (uint ack) {}
}
