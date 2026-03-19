// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DoubleWithdraw {
    mapping(address => uint256) public deposits;
    function deposit() external payable { deposits[msg.sender] += msg.value; }
    function withdraw() external {
        uint256 amt = deposits[msg.sender];
        require(amt > 0, "No balance");
        payable(msg.sender).transfer(amt);
        // Bug: forgets to set deposits[msg.sender] = 0;
    }
    receive() external payable {}
}