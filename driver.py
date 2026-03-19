import json
import subprocess
import os
from dotenv import load_dotenv
import re
from generator import generate_foundry_test
from utils import is_safe_call
from crew_boss import crew_boss_decide

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
FORK_BLOCK = "18000000"


def validate_schema(spec):
    required = ["attempt_id", "calls", "assertions"]
    for r in required:
        if r not in spec:
            raise ValueError(f"Missing field: {r}")


def safety_lint(spec):
    for c in spec["calls"]:
        if not is_safe_call(c):
            raise ValueError("Unsafe call detected")


def run_foundry():
    cmd = [
        ".\\forge",
        "test",
        "--match-contract", "ExploitTest",
        "-vvvv"
    ]

    res = subprocess.run(
        cmd,
        capture_output=True,
        cwd=os.getcwd(),
        text=False
    )

    stdout = res.stdout.decode("utf-8", errors="ignore") if res.stdout else ""
    stderr = res.stderr.decode("utf-8", errors="ignore") if res.stderr else ""

    output = stdout + "\n" + stderr

    print("\n================ RAW FORGE OUTPUT ================\n")
    print(output)
    print("\n===================================================\n")

    return output


def parse_result(output: str):
    if "Suite result: ok" in output:
        return "pass"
    if "Suite result: FAILED" in output:
        return "fail"
    return "fail"

def extract_gas(output: str):
    m = re.search(r"\(gas:\s*(\d+)\)", output)
    return int(m.group(1)) if m else 0

def extract_balance_delta(output: str):
    m = re.search(
        r"BalanceSnapshot\(beforeBal:\s*(\d+).*afterBal:\s*(\d+)",
        output
    )
    if not m:
        return 0

    before = int(m.group(1))
    after = int(m.group(2))
    return after - before

def extract_trace(output: str) -> str:
    """🎉 Phase 3: Extract the specific trace for the exploit execution"""
    trace_lines = []
    capture = False
    for line in output.split('\n'):
        if "ExploitTest::testExploit" in line or "ExploitTest:testExploit" in line:
            capture = True
        
        if capture:
            if "Suite result" in line or "Ran " in line:
                break
            trace_lines.append(line.strip('\r'))
            
    return "\n".join(trace_lines).strip()

def main():
    import glob
    attempt_files = sorted(glob.glob("attempt*.json"))
    if not attempt_files:
        print("No attempt files found!")
        return

    print("\n=== Available Exploit Attempts ===")
    for idx, ffile in enumerate(attempt_files):
        print(f"[{idx + 1}] {ffile}")

    choice = input("\nSelect an attempt file to run (enter number): ").strip()
    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(attempt_files):
            raise ValueError
        selected_file = attempt_files[choice_idx]
    except ValueError:
        print("Invalid choice. Exiting.")
        return

    print(f"\n🚀 Running pipeline for: {selected_file}\n")

    with open(selected_file, encoding="utf-8") as f:
        spec = json.load(f)

    validate_schema(spec)
    safety_lint(spec)

    test_path = generate_foundry_test(spec)

    output = run_foundry()

    delta = extract_balance_delta(output)
    res_status = parse_result(output)
    trace_summary = extract_trace(output)

    # (v) Fact-Check Report
    report = {
        "attempt_id": spec["attempt_id"],
        "result": res_status,
        "why": "All assertions natively passed" if res_status == "pass" else "Foundry EVM verification failed (Assertion failed or Reverted)",
        "trace": trace_summary,
        "balance_deltas": {"attacker": delta},
        "storage_deltas": {},
        "gas": extract_gas(output),
        "provenance": {
            "test_file": test_path,
            "rpc": RPC_URL,
            "block": FORK_BLOCK,
        },
    }

    print("\n=== FACT CHECK REPORT ===")
    print(json.dumps(report, indent=2))

    # Crew Boss
    decision = crew_boss_decide(
        report,
        exploit_plan=spec,
        cfa_excerpt=None,
        use_llm=True,
    )

    print("\n=== CREW BOSS DECISION ===")
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
