import json, os
from llm import complete

def run_agent(system: str, payload: dict, provider: str | None = None) -> dict:
    system += "\nReturn ONLY valid JSON. No markdown fences, no commentary."
    user = json.dumps(payload, default=str)
    for _ in range(2):  # one retry: smaller local models sometimes break JSON
        t = complete(system, user, provider)
        try:
            return json.loads(t[t.find("{"): t.rfind("}") + 1])
        except json.JSONDecodeError:
            user += "\n\nYour previous reply was not valid JSON. Reply again with ONLY the JSON object."
    raise ValueError("Model did not return valid JSON")

ANALYST = """You are a Data Quality Analyst Agent. You receive a statistical profile of a CSV.
Identify issues in 4 categories: missing_values, duplicates, inconsistent_types, suspicious_values.
Rules: use ONLY numbers present in the profile; never invent values; flag domain-implausible
values (e.g. age > 120, negative order values). Output:
{"findings":[{"id":"F1","category":"...","column":"... or null","description":"...",
"evidence":"numbers from profile","affected_rows":<int or null>}],
"overall_summary":"2-3 sentences"}"""

REMEDIATOR = """You are a Remediation and Reporting Agent. Given findings and the profile, assign each
finding a severity (Critical/High/Medium/Low) with a one-line rationale, and recommend a concrete
corrective action (specific, e.g. 'standardise country to ISO-3166 via mapping table').
Order by priority. If reviewer_feedback is supplied, address it. Output:
{"prioritized_actions":[{"priority":1,"finding_id":"F1","severity":"...","rationale":"...",
"action":"...","effort":"Low|Medium|High"}],
"executive_summary":"3-4 sentences","data_quality_score":<0-100>}"""

REVIEWER = """You are a Quality Review Agent. Verify the findings and recommendations against the raw
profile. Check: (1) every cited number matches the profile, (2) no major issue in the profile is
missed, (3) actions are specific and match severity,(4) conclude verdict as revise if severity is medium. Output:
{"verdict":"approve|revise","verified_findings":["F1"],"incorrect_or_unsupported":[{"finding_id":"..","issue":".."}],
"missed_issues":["..."],"feedback_for_remediator":"..."}"""

def analyst(profile):            return run_agent(ANALYST, {"profile": profile})
def remediator(profile, findings, feedback=None):
    return run_agent(REMEDIATOR, {"profile": profile, "findings": findings, "reviewer_feedback": feedback})
def reviewer(profile, findings, plan):
    # REVIEWER_PROVIDER lets a different model audit the work (empty = same as LLM_PROVIDER)
    return run_agent(REVIEWER, {"profile": profile, "findings": findings, "plan": plan},
                     provider=os.getenv("REVIEWER_PROVIDER") or None)