// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
 * ⚠️ INTENTIONALLY VULNERABLE CONTRACT
 * Used only for testing exploit pipelines.
 */

contract Vault {
    mapping(address => uint256) public balances;

    // deposit ETH into vault
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // ❌ VULNERABLE withdraw (reentrancy unsafe)
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");

        // interaction BEFORE effect (bug)
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");

        balances[msg.sender] -= amount;
    }

    // helper
    function getBalance(address user) external view returns (uint256) {
        return balances[user];
    }

    receive() external payable {}
}
