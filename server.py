"""
Zero-dependency HTTP server for the JSON Rule Engine.
Serves static frontend assets and exposes REST endpoints for rule catalog inspection and payload evaluation.
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from engine import JsonRuleEngine, Rule, Condition, Operator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 8093
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Sample Default Rules
DEFAULT_RULES = [
    Rule(
        id="RULE_FRAUD_HIGH_RISK",
        description="Flag international high-velocity transfers over $10,000 for AML review",
        priority=1,
        match_all=True,
        conditions=[
            Condition(field="transaction.amount", operator=Operator.GREATER_THAN, value=10000),
            Condition(field="transaction.currency", operator=Operator.NOT_EQUALS, value="USD"),
            Condition(field="user.risk_score", operator=Operator.GREATER_THAN_OR_EQUAL, value=75),
        ],
        action="HOLD_FOR_MANUAL_AML_REVIEW"
    ),
    Rule(
        id="RULE_VIP_INSTANT_CLEARANCE",
        description="Auto-approve VIP institutional transfers with pristine credit scores",
        priority=2,
        match_all=True,
        conditions=[
            Condition(field="user.tier", operator=Operator.IN, value=["VIP", "INSTITUTIONAL"]),
            Condition(field="user.kyc_status", operator=Operator.EQUALS, value="VERIFIED"),
            Condition(field="user.credit_score", operator=Operator.GREATER_THAN_OR_EQUAL, value=750),
        ],
        action="INSTANT_SETTLEMENT_ZERO_FEE"
    ),
    Rule(
        id="RULE_SUSPICIOUS_DOMAIN_REJECT",
        description="Reject login or withdrawal attempts originating from disposable emails",
        priority=3,
        match_all=False,
        conditions=[
            Condition(field="user.email", operator=Operator.ENDS_WITH, value="@tempmail.com"),
            Condition(field="user.email", operator=Operator.ENDS_WITH, value="@disposable.org"),
            Condition(field="network.is_vpn", operator=Operator.EQUALS, value=True),
        ],
        action="BLOCK_AND_CHALLENGE_2FA"
    )
]

engine = JsonRuleEngine(rules=DEFAULT_RULES)


class RuleEngineHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/rules":
            rules_data = [r.model_dump() for r in engine.rules]
            self._set_headers(200)
            self.wfile.write(json.dumps(rules_data).encode("utf-8"))
        elif parsed.path == "/" or parsed.path == "/index.html":
            root_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
            target = os.path.join(STATIC_DIR, "index.html") if os.path.exists(os.path.join(STATIC_DIR, "index.html")) else root_index
            if os.path.exists(target):
                self._set_headers(200, "text/html")
                with open(target, "rb") as f:
                    self.wfile.write(f.read())
            else:
                super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Malformed JSON payload"}).encode("utf-8"))
            return

        if parsed.path == "/api/evaluate":
            target_data = payload.get("data", payload)
            result = engine.evaluate(target_data)
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode("utf-8"))

        elif parsed.path == "/api/rules":
            try:
                new_rule = Rule(**payload)
                engine.add_rule(new_rule)
                self._set_headers(201)
                self.wfile.write(json.dumps({"success": True, "rule": new_rule.model_dump()}).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": f"Invalid rule schema: {str(e)}"}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))


def start_server(port=PORT):
    server = HTTPServer(("0.0.0.0", port), RuleEngineHandler)
    print(f"[*] JSON Rule Engine Server running at http://127.0.0.1:{port}")
    print(f"    Endpoints: GET /api/rules | POST /api/evaluate | POST /api/rules")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    start_server()
