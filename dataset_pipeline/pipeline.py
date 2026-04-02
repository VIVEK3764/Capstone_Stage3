import json
import sys

from slither_runner import run_slither
from lead_generator import generate_leads
from witness_generator import generate_witnesses
from graph_builder import build_graph


def build_pipeline(sol_file, output_file, label):
    slither = run_slither(sol_file)

    graph = build_graph(slither)
    leads = generate_leads(slither)
    witnesses = generate_witnesses(leads, graph)

    contract_name = slither.contracts[0].name if slither.contracts else "unknown"

    
    final_output = {
    "example_id": sol_file.split("/")[-1].replace(".sol", ""),
    "split": "train",
    "source": "smartbugs",

    "ground_truth": label,   #  NEW FIELD

    "contract_id": contract_name,

    "metadata": {
        "num_contracts": len(slither.contracts),
        "num_functions": sum(len(c.functions) for c in slither.contracts),
        "num_leads": len(leads),
    },

    "target_output": {
        "leads": leads,
        "witnesses": witnesses
    }
}

    with open(output_file, "w") as f:
        json.dump(final_output, f, indent=2)

    print(" Research dataset entry created:", output_file)


if __name__ == "__main__":
    import sys
    build_pipeline(sys.argv[1], sys.argv[2], sys.argv[3])