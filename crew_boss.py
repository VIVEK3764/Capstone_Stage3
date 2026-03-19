import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -------------------------------------------------
# Deterministic core logic (paper faithful)
# -------------------------------------------------
def deterministic_decide(report, exploit_plan):
    if report["result"] == "pass":
        delta = report["balance_deltas"].get("attacker", 0)

        if delta > 0:
            return "confirm", "High"
        else:
            return "retry", None
    else:
        return "drop", None


# -------------------------------------------------
# Optional LLM refinement (research mode)
# -------------------------------------------------
def llm_refine_decision(report, exploit_plan, cfa_excerpt):
    prompt = f"""
You are CREW BOSS.

Decide exploit outcome.

FACT REPORT:
{report}

EXPLOIT PLAN:
{exploit_plan}

CFA:
{cfa_excerpt}

Return STRICT JSON:
{{
  "verdict": "...",
  "severity": "...",
  "rationale": "..."
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    return resp.choices[0].message.content


# -------------------------------------------------
# Main Crew Boss entry
# -------------------------------------------------
def crew_boss_decide(report, exploit_plan, cfa_excerpt=None, use_llm=False):
    verdict, severity = deterministic_decide(report, exploit_plan)

    decision = {
        "attempt_id": report["attempt_id"],
        "verdict": verdict,
        "severity": severity,
        "next_lead_idx": None,
        "include_patch": verdict == "confirm",
        "rationale": "deterministic decision",
    }

    # optional LLM adjudication
    if use_llm:
        try:
            llm_out = llm_refine_decision(report, exploit_plan, cfa_excerpt)
            decision["llm_review"] = llm_out
        except Exception as e:
            decision["llm_error"] = str(e)

    return decision
