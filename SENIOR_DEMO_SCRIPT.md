# Senior Engineering Walkthrough: Ige JSON Rule Engine

> **Target Audience:** Principal Systems Engineers, FinTech Architects, Risk & Compliance Engineering Leads.  
> **Key Architecture Highlights:** Declarative Schema (`Pydantic v2`), Nested Dot-Notation Resolution, Sub-Millisecond Execution (&lt;300&mu;s), Fully Auditable Evaluation Trees.

---

## 1. Executive Summary & Problem Space

Modern enterprise systems (such as risk evaluation, anti-money laundering compliance, loan underwriting, and discount calculation) require frequent policy changes. Hardcoding business rules in imperative `if-else` blocks requires code changes, regression testing, and deployment cycles for every minor threshold tweak.

The **Ige JSON Rule Engine** externalizes business logic into declarative JSON structures. It supports:
- Safe dynamic evaluation without using dangerous `eval()` or `exec()`
- Arbitrarily deep dot-notation object graph traversal (e.g. `user.profile.credit_score`)
- 12 atomic comparison operators (including regex and membership checks)
- Granular, explainable audit traces detailing *why* a rule matched or failed.

---

## 2. File & Function Code Architecture

### `engine.py` — Declarative Evaluation Engine
- `class Operator(str, Enum)`: 12 comparison operators (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `contains`, `not_contains`, `regex`, `in`, `not_in`, `starts_with`, `ends_with`).
- `class Condition(BaseModel)`: Atomic condition unit specifying target field path, operator, and expected value.
- `class ConditionEvaluation(BaseModel)`: Audit record holding resolved actual value, pass/fail status, and explanation string.
- `class Rule(BaseModel)`: Rule specification containing ID, conditions array, `match_all` boolean (AND vs OR logic), priority rank, and action string.
- `class JsonRuleEngine`:
  - `get_nested_field(data, path)`: Traverses nested dictionaries and array indexes using dot-notation.
  - `evaluate_condition(condition, data)`: Evaluates a single condition against the payload with type-coercion guards.
  - `evaluate(payload)`: Evaluates payload against all rules sorted by priority, recording sub-millisecond execution duration and detailed audit trails.

### `server.py` — Embedded Zero-Dependency HTTP Gateway (Port 8093)
- `RuleEngineHandler(SimpleHTTPRequestHandler)`:
  - `GET /api/rules`: Returns active rule catalog.
  - `POST /api/evaluate`: Evaluates test payload and responds with audit result tree.
  - `POST /api/rules`: Dynamic rule registration.
- `start_server(port)`: Boots HTTP daemon on port 8093.

### `main.py` — Dual CLI Runner & Server Bootstrap
- `run_cli_demo()`: Runs CLI verification of AML wire transfers and VIP volume upgrades.
- `main()`: Parses `--serve` and `--port` flags.

### `static/` — Modular Frontend Visualizer
- `static/css/styles.css`: Dark indigo aesthetics, responsive workbench grid, pass/fail status badges.
- `static/js/api.js`: REST API client.
- `static/js/components/RuleCatalog.js`: Displays rules with interactive condition chips.
- `static/js/components/PayloadEditor.js`: JSON editor with preset selector (Flagged AML Wire, Approved VIP Settlement, Disposable Domain Check).
- `static/js/components/EvaluationResultView.js`: Step-by-step match explanation tree.
- `static/js/app.js`: Main event orchestrator.

---

## 3. How to Run the Live Demo

### Option A: Interactive Web Mission Control (Port 8093)
```powershell
py server.py
# or: py main.py --serve
```
Open your browser to: **http://127.0.0.1:8093**

**Demo Narrative Walkthrough:**
1. Point to the **Active Business Rules** on the left. Explain that these rules are declarative data schemas, completely decoupled from application code.
2. Under **Test Payload**, select the preset **Flagged AML Wire ($14.5k EUR)** and click **Evaluate Payload Against Rules**.
3. Point to the **Evaluation Audit Trail** on the right:
   - Show the sub-millisecond execution time (e.g. `280μs`).
   - Show how `RULE_FRAUD_HIGH_RISK` triggered, and walk through each condition check (Amount > 10,000, Currency != USD, Risk Score >= 75) showing expected vs actual values.
4. Switch to **Approved VIP Settlement ($75k USD)** and re-evaluate: show `RULE_VIP_INSTANT_CLEARANCE` triggering while the fraud rule safely passes over.

### Option B: Terminal CLI Execution
```powershell
py main.py
```
Runs high-precision performance benchmarks in the console.
