// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AccessControlBug {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    //  no access control
    function withdrawAll() external {
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}