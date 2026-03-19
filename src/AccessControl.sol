// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract AccessControl {
    address public owner;
    constructor() { owner = msg.sender; }
    // Bug: Missing require(msg.sender == owner)
    function withdrawAll() external {
        payable(msg.sender).transfer(address(this).balance);
    }
    receive() external payable {}
}