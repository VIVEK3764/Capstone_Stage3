def extract_signals(contract, function):
    signals = {
        "has_external_call": False,
        "writes_state": False,
        "has_require": False,
        "uses_tx_origin": False,
        "uses_timestamp": False,
        "has_delegatecall": False,
        "has_selfdestruct": False,
        "has_loop": False,
        "writes_after_call": False,
    }

    seen_external = False

    for node in function.nodes:
        expr = str(node.expression)

        # external calls
        if "call" in expr:
            signals["has_external_call"] = True
            seen_external = True

        if "delegatecall" in expr:
            signals["has_delegatecall"] = True

        if "selfdestruct" in expr:
            signals["has_selfdestruct"] = True

        if "tx.origin" in expr:
            signals["uses_tx_origin"] = True

        if "block.timestamp" in expr:
            signals["uses_timestamp"] = True

        if "require" in expr:
            signals["has_require"] = True

        # loop detection
        if node.type.name in ["IFLOOP", "STARTLOOP"]:
            signals["has_loop"] = True

        # state writes
        if node.state_variables_written:
            signals["writes_state"] = True

            if seen_external:
                signals["writes_after_call"] = True

    return signals