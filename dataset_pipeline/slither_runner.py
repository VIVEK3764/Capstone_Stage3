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

    #  Set version globally
    set_solc_version(version)

    #  IMPORTANT: tell Slither to use solc from solcx
    os.environ["SOLC_VERSION"] = version

    return Slither(file_path)

