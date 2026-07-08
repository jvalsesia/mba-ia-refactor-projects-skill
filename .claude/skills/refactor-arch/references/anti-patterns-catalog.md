# Anti-Patterns Catalog

The knowledge Phase 2 (Audit) cross-references code against. Each entry has a
**Name**, **Severity** (one of CRITICAL / HIGH / MEDIUM / LOW), a concrete
**Detection signal**, an **Impact**, and a **Recommendation** that names the
playbook pattern used to fix it.

**Severity scale:**
- **CRITICAL** — security failures and architecture failures (data exposure,
  injection, hardcoded secrets).
- **HIGH** — MVC / SOLID violations (God Class, business logic in the wrong
  layer, no separation of concerns).
- **MEDIUM** — standardization, duplication, moderate performance (N+1
  queries, copy-pasted logic, missing error handling).
- **LOW** — readability, naming, magic numbers.

This catalog contains **12** entries, covers **all four** severities, and
includes **deprecated-API detection** (entry AP-11).

---

### AP-01 — Hardcoded Credentials / Secrets
- **Severity:** CRITICAL
- **Detection signal:** literal passwords, API keys, tokens, or connection
  strings in source — e.g. `SECRET_KEY = "hunter2"`, `password="admin"`,
  `mongodb://user:pass@host` embedded in a `.py`/`.js` file.
- **Impact:** secrets leak through version control; rotation requires a code
  change and redeploy; a repo leak is an immediate breach.
- **Recommendation:** extract into a config module backed by environment
  variables. See playbook **P-01 (Extract Config & Secrets)**.

### AP-02 — SQL Injection via String Interpolation
- **Severity:** CRITICAL
- **Detection signal:** a query string built with f-strings / template
  literals / concatenation inside a handler — e.g.
  `cursor.execute(f"SELECT * FROM users WHERE id={uid}")` or
  `` db.query(`... WHERE name='${name}'`) ``.
- **Impact:** attacker-controlled input reaches the database verbatim; enables
  data theft, deletion, and privilege escalation.
- **Recommendation:** use parameterized queries / an ORM. See playbook **P-02
  (Parameterize Queries)**.

### AP-03 — Missing Authentication / Authorization on Sensitive Routes
- **Severity:** CRITICAL
- **Detection signal:** a route mutating or exposing sensitive data (e.g.
  `/admin`, `/users/<id>/delete`, `/orders`) with no auth check/decorator/
  middleware guarding it.
- **Impact:** any anonymous caller can read or destroy protected data.
- **Recommendation:** introduce an auth middleware/decorator applied centrally.
  See playbook **P-08 (Centralize Auth Middleware)**.

### AP-04 — God Class / God File
- **Severity:** HIGH
- **Detection signal:** a single file or class holding routing, DB access,
  business logic, and config together, often > ~300 lines with many unrelated
  responsibilities.
- **Impact:** untestable, high-churn, high-merge-conflict; violates single
  responsibility; every change risks unrelated breakage.
- **Recommendation:** split by responsibility into models/controllers/routes.
  See playbook **P-03 (Split God Class into MVC layers)**.

### AP-05 — Business Logic in Route Handlers / Views
- **Severity:** HIGH
- **Detection signal:** validation, calculations, and DB orchestration written
  directly inside a route/view function instead of a controller/service.
- **Impact:** logic can't be reused or unit-tested; the view layer becomes fat
  and the app hard to reason about.
- **Recommendation:** move logic into controllers/services; keep routes thin.
  See playbook **P-04 (Move Business Logic to Controllers)**.

### AP-06 — Tight Coupling / No Dependency Injection
- **Severity:** HIGH
- **Detection signal:** modules instantiate their own DB connections, clients,
  or config at import time (`db = sqlite3.connect('app.db')` at module top),
  making substitution impossible.
- **Impact:** cannot swap implementations or mock in tests; hidden global
  state; brittle startup ordering.
- **Recommendation:** inject dependencies through a composition root. See
  playbook **P-05 (Introduce Dependency Injection)**.

### AP-07 — N+1 Query
- **Severity:** MEDIUM
- **Detection signal:** a loop issuing one query per iteration — e.g. fetching
  a list, then querying details for each item inside a `for` loop.
- **Impact:** database round-trips scale linearly with result size; latency and
  load balloon under real data.
- **Recommendation:** batch with a join / `IN` query / eager loading. See
  playbook **P-06 (Fix N+1 with Batched Query)**.

### AP-08 — Duplicated Logic (Copy-Paste)
- **Severity:** MEDIUM
- **Detection signal:** the same block (validation, response shaping, DB
  access) repeated across ≥2 handlers with minor edits.
- **Impact:** fixes and changes must be applied in many places; drift causes
  inconsistent behavior and bugs.
- **Recommendation:** extract a shared helper/service function. See playbook
  **P-07 (Extract Shared Helper)**.

### AP-09 — Missing / Inconsistent Error Handling
- **Severity:** MEDIUM
- **Detection signal:** handlers with no try/except or try/catch, or each
  handler formatting its own ad-hoc error response; unhandled exceptions leak
  stack traces to clients.
- **Impact:** inconsistent API responses, leaked internals, hard-to-debug
  failures.
- **Recommendation:** centralize error handling in one handler/middleware. See
  playbook **P-09 (Centralize Error Handling)**.

### AP-10 — Magic Numbers / Hardcoded Literals
- **Severity:** LOW
- **Detection signal:** unexplained numeric or string literals in logic — e.g.
  `if role == 2`, `timeout = 3600`, `page[:10]` with no named constant.
- **Impact:** intent is opaque; the same literal changed in one place but not
  another causes subtle bugs.
- **Recommendation:** extract into named constants/config. See playbook **P-10
  (Extract Magic Numbers to Constants)**.

### AP-11 — Deprecated API Usage
- **Severity:** MEDIUM
- **Detection signal:** calls to APIs marked deprecated for the detected stack
  — e.g. Flask `@app.before_first_request`, `flask.Markup`, Python
  `datetime.utcnow()`; Node.js `new Buffer()`, `url.parse()`, `crypto.createCipher`,
  `require('domain')`; or any dependency pinned to an end-of-life major version.
- **Impact:** breaks on the next runtime/library upgrade; may carry known
  security advisories; blocks maintenance.
- **Recommendation:** replace with the current supported API. See playbook
  **P-11 (Replace Deprecated API)**.

### AP-12 — Poor / Misleading Naming
- **Severity:** LOW
- **Detection signal:** single-letter or meaningless identifiers for non-trivial
  values (`d`, `tmp`, `data2`, `func1`), or names that contradict behavior.
- **Impact:** raises the cost of reading and safely changing the code.
- **Recommendation:** rename to intention-revealing identifiers. See playbook
  **P-12 (Rename for Intent)**.

---

**Coverage summary:** CRITICAL — AP-01, AP-02, AP-03 · HIGH — AP-04, AP-05,
AP-06 · MEDIUM — AP-07, AP-08, AP-09, AP-11 · LOW — AP-10, AP-12. Deprecated-API
detection: AP-11.
