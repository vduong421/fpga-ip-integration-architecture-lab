import json
import sys
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from src.fpga_arch_lab import load_catalog, build_architecture_report

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
SHARED = ROOT.parent / "_shared_project_workbench"

if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

try:
    from local_llm import chat_json
except Exception:
    chat_json = None


catalog, blocks = load_catalog(ROOT / "data" / "ip_catalog.json")
report = build_architecture_report(catalog, blocks)


def enrich_report():
    category_counts = Counter(block["category"] for block in report["blocks"])
    readiness_counts = Counter(block["readiness"] for block in report["blocks"])
    risk_rank = sorted(report["blocks"], key=lambda block: block["risk_score"], reverse=True)
    power_rank = sorted(report["blocks"], key=lambda block: block["power_mw"], reverse=True)
    slack_rank = sorted(report["blocks"], key=lambda block: block["timing_slack_ns"])

    report["deterministic_reasoning"] = {
        "category_counts": dict(category_counts),
        "readiness_counts": dict(readiness_counts),
        "highest_risk": risk_rank[:5],
        "highest_power": power_rank[:5],
        "worst_slack": slack_rank[:5],
        "total_clock_domains": sum(block["clock_domain_count"] for block in report["blocks"]),
        "total_reset_domains": sum(block["reset_domain_count"] for block in report["blocks"]),
    }


enrich_report()


def fallback_ai_insights():
    reasoning = report["deterministic_reasoning"]
    high_risk = reasoning["highest_risk"][:3]
    return {
        "result": f"{report['high_risk_count']} high-risk IP blocks and {report['needs_review_count']} review-needed block detected.",
        "recommendation": "Prioritize timing closure, CDC/RDC review, and constraint completion before integration freeze.",
        "decision": "Proceed with ready IP blocks while gating high-risk IP blocks behind architecture review.",
        "executive_summary": f"{report['ip_count']} IP blocks modeled with {report['total_bandwidth_gbps']} Gbps bandwidth and {report['total_power_mw']} mW total power.",
        "top_risks": [
            "Highest-risk IP blocks: " + ", ".join(block["name"] for block in high_risk),
            "Negative or near-zero timing slack may block integration closure.",
            "Multi-clock and multi-reset IP blocks require CDC/RDC review."
        ],
        "operator_actions": [
            "Open timing closure review for negative-slack IP blocks.",
            "Run CDC/RDC checks for multi-domain IP blocks.",
            "Complete generated-clock and constraint packages before signoff."
        ],
        "resume_signal": "Built FPGA IP integration dashboard with deterministic architecture risk scoring and local-AI triage guidance."
    }


def generate_ai_insights(model="google/gemma-4-e4b"):
    if chat_json is None:
        return fallback_ai_insights()

    prompt = f"""You are a senior FPGA architecture integration copilot.

Return ONLY valid JSON with:
- result
- recommendation
- decision
- executive_summary
- top_risks array of 3
- operator_actions array of 3
- resume_signal

Rules:
- use only deterministic FPGA report data
- do not invent IP names, metrics, or risks
- be concise and engineering-focused

FPGA report:
{json.dumps(report, indent=2)}
"""
    try:
        response = chat_json(prompt, model=model)
        if not isinstance(response, dict):
            return fallback_ai_insights()
        return {
            "result": response.get("result", ""),
            "recommendation": response.get("recommendation", ""),
            "decision": response.get("decision", ""),
            "executive_summary": response.get("executive_summary", ""),
            "top_risks": response.get("top_risks", []),
            "operator_actions": response.get("operator_actions", []),
            "resume_signal": response.get("resume_signal", "")
        }
    except Exception:
        return fallback_ai_insights()


ai_copilot = generate_ai_insights()


def ask(question, model="google/gemma-4-e4b"):
    q = question.lower()
    reasoning = report["deterministic_reasoning"]

    fallback = {
        "answer": f"{report['high_risk_count']} high-risk IP blocks were detected.",
        "evidence": f"Highest risk blocks: {', '.join(block['name'] for block in reasoning['highest_risk'][:3])}.",
        "next_action": "Start timing, CDC/RDC, and constraint reviews for the highest-risk IP blocks.",
        "recommendation": ai_copilot["recommendation"],
        "decision": ai_copilot["decision"],
        "risks": ai_copilot["top_risks"],
        "operator_actions": ai_copilot["operator_actions"],
    }

    if "risk" in q:
        fallback["answer"] = "Highest-risk IP blocks are " + ", ".join(block["name"] for block in reasoning["highest_risk"][:5]) + "."
        fallback["evidence"] = "; ".join(f"{block['name']} risk={block['risk_score']}" for block in reasoning["highest_risk"][:5])
    elif "timing" in q or "slack" in q:
        fallback["answer"] = "Worst timing slack blocks are " + ", ".join(block["name"] for block in reasoning["worst_slack"][:5]) + "."
        fallback["evidence"] = "; ".join(f"{block['name']} slack={block['timing_slack_ns']}ns" for block in reasoning["worst_slack"][:5])
    elif "power" in q:
        fallback["answer"] = "Highest-power IP blocks are " + ", ".join(block["name"] for block in reasoning["highest_power"][:5]) + "."
        fallback["evidence"] = "; ".join(f"{block['name']} power={block['power_mw']}mW" for block in reasoning["highest_power"][:5])
    elif "cdc" in q or "clock" in q:
        fallback["answer"] = f"Total modeled clock-domain count is {reasoning['total_clock_domains']} across all IP blocks."
        fallback["evidence"] = "CDC risk is estimated from clock_domain_count in deterministic report."
    elif "reset" in q or "rdc" in q:
        fallback["answer"] = f"Total modeled reset-domain count is {reasoning['total_reset_domains']} across all IP blocks."
        fallback["evidence"] = "RDC risk is estimated from reset_domain_count in deterministic report."

    if chat_json is None:
        return fallback

    prompt = f"""You are an FPGA architecture integration copilot.

Answer using ONLY this deterministic FPGA report.

Return ONLY valid JSON with:
- answer
- evidence
- next_action
- recommendation
- decision
- risks array
- operator_actions array

Question:
{question}

FPGA report:
{json.dumps(report, indent=2)}

AI analyst:
{json.dumps(ai_copilot, indent=2)}
"""
    try:
        response = chat_json(prompt, model=model)
        if not isinstance(response, dict):
            return fallback
        return {
            "answer": response.get("answer", fallback["answer"]),
            "evidence": response.get("evidence", fallback["evidence"]),
            "next_action": response.get("next_action", fallback["next_action"]),
            "recommendation": response.get("recommendation", fallback["recommendation"]),
            "decision": response.get("decision", fallback["decision"]),
            "risks": response.get("risks", fallback["risks"]),
            "operator_actions": response.get("operator_actions", fallback["operator_actions"]),
        }
    except Exception:
        return fallback


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api":
            self._json({
                **report,
                "ai_copilot": ai_copilot
            })
            return

        p = "index.html" if self.path == "/" else self.path[1:]
        f = WEB / p

        if f.exists():
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f.read_bytes())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/ask":
            length = int(self.headers.get("Content-Length", 0))
            question = self.rfile.read(length).decode()
            self._json(ask(question))
            return
        self.send_error(404)

    def _json(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


print("FPGA Architecture Dashboard running at http://127.0.0.1:8010")
HTTPServer(("127.0.0.1", 8010), H).serve_forever()