import networkx as nx


BAD_STATE_MAP = {
    "reentrancy": "balance_drain",
    "access_control": "unauthorized_access",
    "delegatecall": "logic_hijack",
    "selfdestruct": "contract_destroyed",
    "dos": "service_unavailable",
    "unchecked_call": "silent_failure",
    "tx_origin": "auth_bypass",
    "timestamp_dependence": "time_manipulation",
}


def generate_witnesses(leads, graph):
    witnesses = []

    for i, lead in enumerate(leads):
        target = lead["target"]["function"]

        path = []

        # try cycle detection (reentrancy)
        try:
            cycles = list(nx.simple_cycles(graph))
            for c in cycles:
                if target in c:
                    path = c
                    break
        except:
            pass

        # fallback path
        if not path:
            path = ["entry()", target, "external_call()", target]

        witnesses.append({
            "witness_id": f"w_{i:03}",
            "lead_id": lead["lead_id"],
            "path": path,
            "bad_state": BAD_STATE_MAP.get(lead["pattern"], "state_violation"),
            "precondition_cost": "low",
            "confidence": round(lead["confidence"] - 0.1, 2)
        })

    return witnesses