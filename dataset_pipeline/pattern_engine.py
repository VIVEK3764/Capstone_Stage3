PATTERNS = [
    {"name": "reentrancy", "swc": "SWC-107", "cond": lambda s: s["has_external_call"] and s["writes_after_call"]},
    {"name": "tx_origin", "swc": "SWC-115", "cond": lambda s: s["uses_tx_origin"]},
    {"name": "timestamp_dependence", "swc": "SWC-116", "cond": lambda s: s["uses_timestamp"]},
    {"name": "delegatecall", "swc": "SWC-112", "cond": lambda s: s["has_delegatecall"]},
    {"name": "selfdestruct", "swc": "SWC-106", "cond": lambda s: s["has_selfdestruct"]},
    {"name": "dos", "swc": "SWC-113", "cond": lambda s: s["has_loop"] and s["has_external_call"]},
    {"name": "access_control", "swc": "SWC-105", "cond": lambda s: s["writes_state"] and not s["has_require"]},
    {"name": "unchecked_call", "swc": "SWC-104", "cond": lambda s: s["has_external_call"] and not s["has_require"]},
]


def match_patterns(signals):
    matches = []
    for p in PATTERNS:
        try:
            if p["cond"](signals):
                matches.append(p)
        except:
            pass
    return matches