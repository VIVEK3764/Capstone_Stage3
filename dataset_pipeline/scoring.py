SEVERITY = {
    "reentrancy": 1.0,
    "access_control": 0.9,
    "delegatecall": 0.85,
    "selfdestruct": 0.9,
    "dos": 0.7,
    "unchecked_call": 0.75,
    "tx_origin": 0.6,
    "timestamp_dependence": 0.5,
}


def compute_score(signals, pattern):
    score = 0.0

    # signal contributions
    if signals.get("has_external_call"): score += 0.2
    if signals.get("writes_after_call"): score += 0.25
    if signals.get("writes_state"): score += 0.15
    if signals.get("has_delegatecall"): score += 0.2
    if signals.get("uses_tx_origin"): score += 0.1
    if signals.get("has_selfdestruct"): score += 0.2
    if signals.get("has_loop"): score += 0.1

    # severity boost
    score *= SEVERITY.get(pattern, 0.6)

    # normalize
    score = min(score, 1.0)

    priority = 0.6 * score + 0.4 * SEVERITY.get(pattern, 0.6)

    return round(score, 2), round(priority, 2)