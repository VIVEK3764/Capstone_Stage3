import re

WEI = 10**18


def to_wei(val: str) -> int:
    """Canonicalize ETH units → wei."""
    if val is None:
        return 0

    val = str(val).strip().lower()

    if "ether" in val or "eth" in val:
        num = float(re.findall(r"[\d.]+", val)[0])
        return int(num * WEI)

    return int(val)


def is_safe_call(call: dict) -> bool:
    """Safety lint: block dangerous patterns."""
    forbidden = ["delegatecall(", "selfdestruct", "callcode"]

    fn = call.get("function", "").lower()
    for bad in forbidden:
        if bad in fn:
            return False
    return True
