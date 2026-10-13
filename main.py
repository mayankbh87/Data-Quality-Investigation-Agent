import sys, os, json
from profiler import profile_csv
import agents

def render(path, profile, findings, plan, review):
    L = [f"# Data Quality Report: `{os.path.basename(path)}`", "",
         f"**Rows:** {profile['rows']}  |  **Columns:** {profile['columns']}  |  "
         f"**Quality score:** {plan.get('data_quality_score','n/a')}/100", "",
         "## Executive summary", plan["executive_summary"], "",
         "## Prioritized actions", "| # | Severity | Finding | Action | Effort |", "|---|---|---|---|---|"]
    fmap = {f["id"]: f for f in findings["findings"]}
    for a in plan["prioritized_actions"]:
        f = fmap.get(a["finding_id"], {})
        L.append(f"| {a['priority']} | {a['severity']} | {f.get('description','')} "
                 f"({f.get('evidence','')}) | {a['action']} | {a['effort']} |")
    L += ["", "## Detailed findings"]
    for f in findings["findings"]:
        L.append(f"- **{f['id']} [{f['category']}] {f.get('column') or 'dataset'}**: {f['description']}")
    L += ["", "## Quality review", f"**Verdict:** {review['verdict']}"]
    for m in review.get("missed_issues", []): L.append(f"- Missed: {m}")
    for i in review.get("incorrect_or_unsupported", []): L.append(f"- Questioned {i['finding_id']}: {i['issue']}")
    return "\n".join(L)

def main(path):
    print("1/4 Profiling..."); profile = profile_csv(path)
    print("2/4 Analyst agent..."); findings = agents.analyst(profile)
    print("3/4 Remediation agent..."); plan = agents.remediator(profile, findings)
    print("4/4 Review agent..."); review = agents.reviewer(profile, findings, plan)
    if review["verdict"] == "revise":
        print("   Reviewer requested revision, re-running remediation once...")
        plan = agents.remediator(profile, findings, review["feedback_for_remediator"])
        review = agents.reviewer(profile, findings, plan)
    os.makedirs("output", exist_ok=True)
    with open("output/report.md", "w", encoding="utf-8") as f:
        f.write(render(path, profile, findings, plan, review))
    json.dump({"profile": profile, "findings": findings, "plan": plan, "review": review},
              open("output/trace.json", "w"), indent=2, default=str)
    print("Done: output/report.md")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="?", default="data/customers.csv")
    ap.add_argument("--provider", choices=["anthropic", "gemini", "ollama"])
    ap.add_argument("--model", help="override the model for the chosen provider")
    ap.add_argument("--reviewer-provider", choices=["anthropic", "gemini", "ollama"])
    a = ap.parse_args()
    if a.provider: os.environ["LLM_PROVIDER"] = a.provider
    if a.model:
        os.environ[f"{os.environ.get('LLM_PROVIDER', 'anthropic').upper()}_MODEL"] = a.model
    if a.reviewer_provider: os.environ["REVIEWER_PROVIDER"] = a.reviewer_provider
    print(f"Provider: {os.getenv('LLM_PROVIDER', 'anthropic')}")
    main(a.csv)