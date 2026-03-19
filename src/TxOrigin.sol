// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract TxOrigin {
    address public owner;
    constructor() { owner = msg.sender; }
    function transferOwnership(address newOwner) external {
        require(tx.origin == owner, "Not owner"); // Bug!
        owner = newOwner;
    }
}