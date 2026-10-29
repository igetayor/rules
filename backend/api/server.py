"""
HTTP server bootstrap for the JSON Rule Engine.

Wires together: RuleService (business logic) → RuleController (HTTP adapter)
→ HTTP request handler → HTTPServer. Frontend assets are served from frontend/.
"""

import os
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from backend.core.engine import Rule, Condition, Operator
from backend.api.services.rule_service import RuleService
from backend.api.controllers.rule_controller import RuleController

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 8093
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend")

# ------------------------------------------------------------------ #
#  Default rules — seeded at startup                                  #
# ------------------------------------------------------------------ #
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

_service = RuleService(initial_rules=DEFAULT_RULES)
_controller = RuleController(service=_service)


class RuleEngineHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status: int, data):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_json_body(self) -> dict | None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/rules":
            status, data = _controller.list_rules()
            self._send_json(status, data)
        else:
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "Malformed JSON payload"})
            return

        if path == "/api/evaluate":
            status, data = _controller.evaluate(body)
            self._send_json(status, data)
        elif path == "/api/rules":
            status, data = _controller.create_rule(body)
            self._send_json(status, data)
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, fmt, *args):
        pass  # Suppress noisy access logs; use structured logging in production


def start_server(port: int = PORT):
    server = HTTPServer(("0.0.0.0", port), RuleEngineHandler)
    print(f"[*] JSON Rule Engine Server  →  http://127.0.0.1:{port}")
    print(f"    API: GET /api/rules | POST /api/rules | POST /api/evaluate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGraceful shutdown.")
        server.server_close()
