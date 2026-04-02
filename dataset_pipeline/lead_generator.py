from signal_extractor import extract_signals
from pattern_engine import match_patterns
from scoring import compute_score


def generate_leads(slither):
    leads = []
    idx = 0

    for contract in slither.contracts:
        for f in contract.functions:

            signals = extract_signals(contract, f)
            matches = match_patterns(signals)

            for m in matches:
                confidence, priority = compute_score(signals, m["name"])

                leads.append({
                    "lead_id": f"ld_{idx:03}",
                    "pattern": m["name"],
                    "swc_id": m["swc"],
                    "target": {
                        "contract": contract.name,
                        "function": f.full_name
                    },
                    "evidence": [
                        {"tool": "signals", "note": str(signals)},
                        {"tool": "pattern", "note": m["name"]}
                    ],
                    "confidence": confidence,
                    "priority_score": priority,
                    "notes": "Multi-signal scoring applied"
                })
                idx += 1

    return leads