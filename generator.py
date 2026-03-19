import os
from utils import to_wei

TEMPLATE_TOP = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
{IMPORTS}

contract ExploitTest is Test {
{DECLARATIONS}
    address attacker = address(0x123);

    event BalanceSnapshot(uint256 beforeBal, uint256 afterBal);

    function setUp() public {
{INSTANTIATIONS}

{PRESTATE}
    }

    function testExploit() public {
        uint256 beforeBal = attacker.balance;

{CALLS}
        uint256 afterBal = attacker.balance;
        emit BalanceSnapshot(beforeBal, afterBal);

{ASSERTIONS}
    }
}
"""

def generate_foundry_test(spec: dict):
    os.makedirs("test", exist_ok=True)

    # ---------------- DYNAMIC DEPLOYMENTS (V2 Universal Engine) ----------------
    setup_info = spec.get("setup", {})
    deployments = setup_info.get("deployments", {})

    # Fallback to Phase 2 schema if 'deployments' block is missing
    if not deployments and "target" in setup_info:
        deployments["target"] = setup_info["target"]
        if "attacker_contract" in setup_info:
            deployments["attacker_contract"] = setup_info["attacker_contract"]

    # Absolute ultimate fallback
    if not deployments:
        deployments["target"] = {"file": "Vault.sol", "contract": "Vault", "args": []}

    imports_list = []
    decls_list = []
    insts_list = []

    for alias, info in deployments.items():
        fname = info["file"]
        cname = info["contract"]
        
        # 1. Imports
        imp = f'import "../src/{fname}";'
        if imp not in imports_list:
            imports_list.append(imp)
            
        # 2. Declarations
        decls_list.append(f"    {cname} {alias};")
        
        # 3. Resolve constructor args
        c_args = []
        for a in info.get("args", []):
            if a in deployments:
                c_args.append(f"address({a})")
            else:
                c_args.append(str(a))
        args_str = ", ".join(c_args)

        # 4. Instantiation
        if info.get("prank") == "attacker" or "attacker" in alias.lower():
            insts_list.append(f"        vm.prank(attacker);\n        {alias} = new {cname}({args_str});")
            insts_list.append(f"        vm.deal(address({alias}), 5 ether);")
        else:
            insts_list.append(f"        {alias} = new {cname}({args_str});")
            if alias == "target":
                insts_list.append(f"        vm.deal(address({alias}), 10 ether);")

    imports_code = "\n".join(imports_list)
    declarations_code = "\n".join(decls_list)
    instantiations_code = "\n".join(insts_list)

    # ---------------- PRESTATE (Temporal & State) ----------------
    pre_lines = []
    prestate_info = spec.get("prestate", {})
    
    if "block_timestamp" in prestate_info:
        pre_lines.append(f"        vm.warp({prestate_info['block_timestamp']});")
    if "block_number" in prestate_info:
        pre_lines.append(f"        vm.roll({prestate_info['block_number']});")

    for d in prestate_info.get("deals", []):
        pre_lines.append(f"        vm.deal({d['address']}, {to_wei(d['amount_wei'])});")

    for s in prestate_info.get("storage_writes", []):
        # Resolve address
        addr = s['address']
        if addr in deployments:
            addr = f"address({addr})"
        pre_lines.append(f"        vm.store({addr}, bytes32(uint256({s['slot']})), bytes32(uint256({s['value']})));")

    prestate_code = "\n".join(pre_lines)

    # ---------------- REVERTS ----------------
    revert_assertions = {}
    for a in spec.get("assertions", []):
        if a["type"] == "call_reverts":
            revert_assertions[a.get("call_index", -1)] = a.get("reason", "")

    # ---------------- CALLS ----------------
    call_lines = []

    for i, c in enumerate(spec.get("calls", [])):
        value = to_wei(c.get("value", 0))
        
        # Resolve function args dynamically!
        args_list = []
        for a in c.get("args", []):
            if a in deployments:
                args_list.append(f"address({a})")
            else:
                args_list.append(str(a))
        args = ", ".join(args_list)

        target_alias = c.get("contract", "target")

        call_lines.append("        vm.startPrank(attacker);")

        if i in revert_assertions:
            reason = revert_assertions[i]
            if reason:
                call_lines.append(f'        vm.expectRevert("{reason}");')
            else:
                call_lines.append('        vm.expectRevert();')

        if value > 0:
            call_lines.append(f"        {target_alias}.{c['function']}{{value:{value}}}({args});")
        else:
            call_lines.append(f"        {target_alias}.{c['function']}({args});")

        call_lines.append("        vm.stopPrank();\n")

    calls_code = "\n".join(call_lines)

    # ---------------- ASSERTIONS ----------------
    assert_lines = []
    for a in spec.get("assertions", []):
        t = a["type"]
        if t == "balance_gt":
            addr = a['address']
            balance_target = "attacker" if addr == "attacker" else f"address({addr})"
            assert_lines.append(f"        assertGt({balance_target}.balance, {to_wei(a['value'])});")
        elif t == "balance_gt_before":
            assert_lines.append(f"        assertGt(afterBal, beforeBal);")
        elif t == "storage_eq":
            tgt = a.get("target", "target")
            tgt_addr = f"address({tgt})" if tgt in deployments else tgt
            slot = a["slot"]
            val = a["value"]
            assert_lines.append(f"        assertEq(vm.load({tgt_addr}, bytes32(uint256({slot}))), bytes32(uint256({val})));")

    if not assert_lines:
        assert_lines.append("        assertGt(afterBal, beforeBal);")

    assertions_code = "\n".join(assert_lines)

    # ---------------- FINAL FILE ----------------
    full_code = (
        TEMPLATE_TOP
        .replace("{IMPORTS}", imports_code)
        .replace("{DECLARATIONS}", declarations_code)
        .replace("{INSTANTIATIONS}", instantiations_code)
        .replace("{PRESTATE}", prestate_code)
        .replace("{CALLS}", calls_code)
        .replace("{ASSERTIONS}", assertions_code)
    )

    path = "test/ExploitTest.t.sol"
    with open(path, "w") as f:
        f.write(full_code)

    return path
