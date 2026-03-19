// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract InvariantBug {
    uint256 public totalSupply = 1000;
    mapping(address => uint256) public balances;
    function deposit() external payable {
        balances[msg.sender] += msg.value;
        totalSupply += msg.value;
    }
    function burn(uint256 amount) external {
        balances[msg.sender] -= amount;
        // Bug: forgets to reduce totalSupply!
    }
}