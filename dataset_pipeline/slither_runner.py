import re
import os
from slither.slither import Slither
from solcx import install_solc, set_solc_version


def extract_solc_version(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'pragma solidity\s+([^;]+);', content)

    if not match:
        return "0.8.20"

    numbers = re.findall(r'\d+\.\d+\.\d+', match.group(1))
    return numbers[0] if numbers else "0.8.20"


def normalize_version(version):
    if version.startswith("0.4"):
        return "0.4.26"
    elif version.startswith("0.5"):
        return "0.5.17"
    elif version.startswith("0.6"):
        return "0.6.12"
    elif version.startswith("0.7"):
        return "0.7.6"
    else:
        return "0.8.20"


def run_slither(file_path):
    raw_version = extract_solc_version(file_path)
    version = normalize_version(raw_version)

    print(f"[SOLC] {version} -> {file_path}")

    try:
        install_solc(version)
    except:
        pass

    # ✅ Set version globally
    set_solc_version(version)

    # ✅ IMPORTANT: tell Slither to use solc from solcx
    os.environ["SOLC_VERSION"] = version

    return Slither(file_path)

# def run_slither(file_path):
#     try:
#         slither = Slither(file_path)
#     except Exception as e:
#         print("❌ Slither failed")
#         print("Error:", e)
#         raise e

#     contracts_out = []

#     for contract in slither.contracts:
#         c_data = {
#             "name": contract.name,
#             "functions": [],
#             "state_variables": [],
#             "special_functions": [],
#             "naming_cues": [],
#             "capability_cues": []
#         }

#         # ✅ State variables
#         for var in contract.state_variables:
#             c_data["state_variables"].append(str(var))

#         # ✅ Functions
#         for f in contract.functions:
#             func_data = {
#                 "name": f.name,
#                 "signature": f.full_name,
#                 "visibility": str(f.visibility) if hasattr(f, "visibility") else "public",
#                 "state_mutability": get_state_mutability(f),
#                 "modifiers": [m.name for m in f.modifiers] if hasattr(f, "modifiers") else [],
#                 "guards": [],
#                 "effects": [],
#                 "external_calls": []
#             }

#             # ✅ Guards (require)
#             if hasattr(f, "nodes"):
#                 for node in f.nodes:
#                     try:
#                         if node.expression and "require" in str(node.expression):
#                             func_data["guards"].append(str(node.expression))
#                     except:
#                         pass

#             # ✅ External calls
#             if hasattr(f, "external_calls_as_expressions"):
#                 for call in f.external_calls_as_expressions:
#                     func_data["external_calls"].append(str(call))

#             # ✅ State changes
#             if hasattr(f, "state_variables_written"):
#                 for var_written in f.state_variables_written:
#                     func_data["effects"].append(str(var_written))

#             c_data["functions"].append(func_data)

#         # ✅ Special functions
#         for f in contract.functions:
#             if f.name in ["receive", "fallback"]:
#                 c_data["special_functions"].append(f.name)

#         # ✅ Naming cues
#         for f in c_data["functions"]:
#             if "withdraw" in f["name"].lower():
#                 c_data["naming_cues"].append("withdraw")

#         # ✅ Capability cues
#         c_data["capability_cues"].append("can_transfer_eth")

#         contracts_out.append(c_data)

#     return {
#     "results": {"contracts": contracts_out},
#     "slither_obj": slither
#     }