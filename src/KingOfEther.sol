// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract KingOfEther {
    address public king;
    uint256 public highestBid;
    function claim() external payable {
        require(msg.value > highestBid, "Bid too low");
        if(king != address(0)) {
            (bool ok,) = king.call{value: highestBid}("");
            require(ok, "Transfer failed"); // DoS vector!
        }
        king = msg.sender;
        highestBid = msg.value;
    }
}