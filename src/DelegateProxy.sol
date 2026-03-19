// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DelegateProxy {
    address public owner;
    constructor() { owner = msg.sender; }
    function execute(address target, bytes calldata data) external payable {
        // Bug: Arbitrary delegatecall
        (bool ok, ) = target.delegatecall(data);
        require(ok, "Delegatecall failed");
    }
}